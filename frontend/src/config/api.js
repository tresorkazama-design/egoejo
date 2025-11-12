const API_PREFIX = "/api";
export const api = {
  base: () => {
    const configured = import.meta.env.VITE_API_URL && import.meta.env.VITE_API_URL.replace(/\/$/, "");
    return configured || "";
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
  chatMessages: (threadId) => `${api.base()}${API_PREFIX}/chat/messages/?thread=${threadId}`,
  polls: () => `${api.base()}${API_PREFIX}/polls/`,
  pollDetail: (id) => `${api.base()}${API_PREFIX}/polls/${id}/`,
  pollVote: (id) => `${api.base()}${API_PREFIX}/polls/${id}/vote/`,
};
