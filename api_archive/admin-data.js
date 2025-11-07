export const runtime = 'nodejs';
const { Pool } = require("pg");
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
});
export default async function handler(req, res) {
  // SÃ©curitÃ© : VÃ©rification du Token
  const authHeader = req.headers.authorization || "";
  const token = authHeader.split(" ")[1];
  if (!token || token !== process.env.ADMIN_TOKEN) {
    return res.status(401).json({ ok: false, error: "Token invalide." });
  }
  // Logique : GET
  if (req.method === "GET") {
    try {
      const result = await pool.query(
        "SELECT id, created_at, nom, email, profil, message, ip, user_agent, document_url FROM intents ORDER BY created_at DESC"
      );
      return res.status(200).json({
        ok: true,
        intents: result.rows,
      });
    } catch (err) {
      console.error("Erreur API /admin-data:", err);
      return res.status(500).json({ ok: false, error: "Erreur serveur BDD." });
    }
  }
  return res.status(405).json({ ok: false, error: "MÃ©thode non autorisÃ©e (GET seulement)." });
}
