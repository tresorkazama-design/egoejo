// Configuration de l'API (DEV -> localhost, PROD -> VITE_API_URL ou domaine fourni)
export const api = {
  base: () => (
    import.meta.env.DEV
      ? "http://localhost:8000/api"
      : (import.meta.env.VITE_API_URL || "https://TON-DOMAIN-API/api")
  ),
  rejoindre: () => `${api.base()}/intents/rejoindre/`,
  adminData: () => `${api.base()}/intents/admin/`,
  exportIntents: () => `${api.base()}/intents/export/`,
  projets: () => `${api.base()}/projets/`,
  cagnottes: () => `${api.base()}/cagnottes/`,
};

