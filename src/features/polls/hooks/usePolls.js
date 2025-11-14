import { useMemo } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../../../config/api.js";
import { createWebSocket } from "../../../utils/realtime.js";

async function fetchJSON(url, options) {
  const response = await fetch(url, {
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export function usePolls(params) {
  const queryString = useMemo(() => {
    if (!params) return "";
    const entries = Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== "");
    if (entries.length === 0) return "";
    return `?${new URLSearchParams(Object.fromEntries(entries)).toString()}`;
  }, [params]);

  return useQuery({
    queryKey: ["polls", params || null],
    queryFn: () => fetchJSON(`${api.polls()}${queryString}`),
  });
}

export function usePoll(pollId, enabled = true) {
  return useQuery({
    queryKey: ["poll", pollId],
    queryFn: () => fetchJSON(api.pollDetail(pollId)),
    enabled: Boolean(pollId) && enabled,
  });
}

export function useCreatePoll() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (payload) =>
      fetchJSON(api.polls(), {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: (data) => {
      client.invalidateQueries({ queryKey: ["polls"] });
      client.setQueryData(["poll", data.id], data);
    },
  });
}

export function usePollAction(pollId, action) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: () => fetchJSON(api.pollAction(pollId, action), { method: "POST" }),
    onSuccess: (data) => {
      client.setQueryData(["poll", pollId], data);
      client.invalidateQueries({ queryKey: ["polls"] });
    },
  });
}

export function useVote(pollId) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (payload) =>
      fetchJSON(api.pollAction(pollId, "vote"), {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: (data) => {
      client.setQueryData(["poll", pollId], data);
      client.invalidateQueries({ queryKey: ["polls"] });
    },
  });
}

export function subscribePollUpdates(pollId, callback) {
  const url = api.wsPoll(pollId);
  return createWebSocket(url, {
    onMessage: ({ type, payload }) => {
      if (type === "poll_update") {
        callback(payload);
      }
    },
  });
}

