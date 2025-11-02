const { Pool } = require("pg");

// Initialise le pool de connexion (réutilisé par Vercel)
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false,
  },
});

export default async function handler(req, res) {
  // --- SÉCURITÉ ---
  // 1. On vérifie le token Bearer
  const authHeader = req.headers.authorization || "";
  const token = authHeader.split(" ")[1]; // Récupère le token après "Bearer "

  // 2. On compare au secret de Vercel
  if (!token || token !== process.env.ADMIN_TOKEN) {
    // 401 Unauthorized si le token est manquant ou mauvais
    return res.status(401).json({ ok: false, error: "Token invalide." });
  }

  // --- LOGIQUE MÉTIER ---
  // Si le token est bon :
  if (req.method === "GET") {
    try {
      // 3. On lit la table "intents"
      const result = await pool.query(
        "SELECT id, created_at, nom, email, profil, message, ip, user_agent, document_url FROM intents ORDER BY created_at DESC"
      );
      
      // 4. On renvoie les données en JSON
      return res.status(200).json({
        ok: true,
        intents: result.rows, // Envoie toutes les lignes
      });

    } catch (err) {
      console.error("Erreur API /admin-data:", err);
      return res.status(500).json({ ok: false, error: "Erreur serveur BDD." });
    }
  }

  // Si ce n'est pas GET (ex: POST, PUT...)
  return res.status(405).json({ ok: false, error: "Méthode non autorisée (GET seulement)." });
}