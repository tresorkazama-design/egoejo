import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../../../config/api.js";

async function fetchJSON(url, options) {
  const response = await fetch(url, {
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `HTTP ${response.status}`);
  }
  return response.json();
}

export function useModerationReports(params) {
  const search = params ? `?${new URLSearchParams(params).toString()}` : "";
  return useQuery({
    queryKey: ["moderation", "reports", params || null],
    queryFn: () => fetchJSON(`${api.moderationReports()}${search}`),
  });
}

export function useModerationReport(reportId, enabled = true) {
  return useQuery({
    queryKey: ["moderation", "report", reportId],
    queryFn: () => fetchJSON(api.moderationReportDetail(reportId)),
    enabled: Boolean(reportId) && enabled,
  });
}

export function useCreateModerationReport() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (payload) =>
      fetchJSON(api.moderationReports(), {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["moderation", "reports"] });
    },
  });
}

export function useUpdateModerationReport(reportId) {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (payload) =>
      fetchJSON(api.moderationReportDetail(reportId), {
        method: "PATCH",
        body: JSON.stringify(payload),
      }),
    onSuccess: (data) => {
      client.setQueryData(["moderation", "report", reportId], data);
      client.invalidateQueries({ queryKey: ["moderation", "reports"] });
    },
  });
}

export function useDeleteModerationReport() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (reportId) => fetchJSON(api.moderationReportDetail(reportId), { method: "DELETE" }),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["moderation", "reports"] });
    },
  });
}

export function useAuditLogs() {
  return useQuery({
    queryKey: ["audit", "logs"],
    queryFn: () => fetchJSON(api.auditLogs()),
  });
}

