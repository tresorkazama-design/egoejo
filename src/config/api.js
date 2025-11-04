// Configuration de l'API (DEV -> localhost, PROD -> VITE_API_URL ou domaine fourni)
const API_SUFFIX = "/api";

export const api = {
  base: () => {
    if (import.meta.env.DEV) {
      return "http://localhost:5000/api";
    }

    if (import.meta.env.VITE_API_URL) {
      return import.meta.env.VITE_API_URL.replace(/\/$/, "");
    }

    return `${window.location.origin}${API_SUFFIX}`;
  },
  rejoindre: () => `${api.base()}/rejoindre`,
  adminData: () => `${api.base()}/export-intents?format=json`,
  exportIntents: () => `${api.base()}/export-intents`,
};

