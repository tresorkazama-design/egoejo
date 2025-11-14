const API_PREFIX = "/api";
const WS_PREFIX = "/ws";

export const api = {
  base: () => {
    const raw = import.meta.env.VITE_API_URL;
    if (!raw) return "";
    return raw.endsWith("/") ? raw.slice(0, -1) : raw;
  },
  rejoindre: () => `${api.base()}${API_PREFIX}/intents/rejoindre/`,
  adminData: (params = "") => {
    const baseUrl = `${api.base()}${API_PREFIX}/intents/admin/`;
    return params ? `${baseUrl}?${params}` : baseUrl;
  },
  exportIntents: (params = "") => {
    const baseUrl = `${api.base()}${API_PREFIX}/intents/export/`;
    return params ? `${baseUrl}?${params}` : baseUrl;
  },
  deleteIntent: (id) => `${api.base()}${API_PREFIX}/intents/${id}/delete/`,
  chatThreads: () => `${api.base()}${API_PREFIX}/chat/threads/`,
  chatThreadDetail: (id) => `${api.base()}${API_PREFIX}/chat/threads/${id}/`,
  chatMessages: (params = "") => {
    const baseUrl = `${api.base()}${API_PREFIX}/chat/messages/`;
    return params ? `${baseUrl}?${params}` : baseUrl;
  },
  polls: () => `${api.base()}${API_PREFIX}/polls/`,
  pollDetail: (id) => `${api.base()}${API_PREFIX}/polls/${id}/`,
  pollAction: (id, action) => `${api.base()}${API_PREFIX}/polls/${id}/${action}/`,
  moderationReports: () => `${api.base()}${API_PREFIX}/moderation/reports/`,
  moderationReportDetail: (id) => `${api.base()}${API_PREFIX}/moderation/reports/${id}/`,
  auditLogs: () => `${api.base()}${API_PREFIX}/audit/logs/`,
  wsChat: (threadId) => `${api.base().replace(/^http/, "ws")}${WS_PREFIX}/chat/${threadId}/`,
  wsPoll: (pollId) => `${api.base().replace(/^http/, "ws")}${WS_PREFIX}/polls/${pollId}/`,
};

