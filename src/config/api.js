const API_PREFIX = "/api";
export const api = {
  base: () => {
    const configured = import.meta.env.VITE_API_URL && import.meta.env.VITE_API_URL.replace(/\/$/,'');
    return configured || ""; // en dev: mÃªme origine (http://localhost:3000)
  },
  rejoindre: () => `${api.base()}${API_PREFIX}/rejoindre`,
  adminData: () => `${api.base()}${API_PREFIX}/export-intents?format=json`,
  exportIntents: () => `${api.base()}${API_PREFIX}/export-intents`,
};
