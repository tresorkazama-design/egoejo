import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../../../config/api.js";

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

export function useChatThreads() {
  return useQuery({
    queryKey: ["chat", "threads"],
    queryFn: () => fetchJSON(api.chatThreads()),
  });
}

export function useChatThread(threadId, enabled = true) {
  return useQuery({
    queryKey: ["chat", "threads", threadId],
    queryFn: () => fetchJSON(api.chatThreadDetail(threadId)),
    enabled: Boolean(threadId) && enabled,
  });
}

export function useChatMessages(threadId, enabled = true) {
  return useQuery({
    queryKey: ["chat", "messages", threadId],
    queryFn: () => fetchJSON(api.chatMessages(`thread=${threadId}`)),
    enabled: Boolean(threadId) && enabled,
  });
}

export function useCreateThread() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (payload) =>
      fetchJSON(api.chatThreads(), {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: (data) => {
      client.invalidateQueries({ queryKey: ["chat", "threads"] });
      client.setQueryData(["chat", "threads", data.id], data);
    },
  });
}

export function useSendMessage(threadId) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (payload) =>
      fetchJSON(api.chatMessages(), {
        method: "POST",
        body: JSON.stringify({ ...payload, thread: threadId }),
      }),
    onMutate: async (payload) => {
      await client.cancelQueries({ queryKey: ["chat", "messages", threadId] });
      const previous = client.getQueryData(["chat", "messages", threadId]) || [];
      const optimistic = {
        id: `temp-${Date.now()}`,
        thread: threadId,
        content: payload.content,
        author: null,
        created_at: new Date().toISOString(),
        metadata: {},
        is_deleted: false,
      };
      client.setQueryData(["chat", "messages", threadId], [...previous, optimistic]);
      return { previous };
    },
    onError: (_err, _payload, context) => {
      if (context?.previous) {
        client.setQueryData(["chat", "messages", threadId], context.previous);
      }
    },
    onSuccess: (data) => {
      client.invalidateQueries({ queryKey: ["chat", "messages", threadId] });
      client.setQueryData(["chat", "messages", threadId], (current = []) =>
        current.map((msg) => (msg.id?.toString().startsWith("temp-") ? data : msg))
      );
      client.invalidateQueries({ queryKey: ["chat", "threads"] });
    },
  });
}

