// api/export-intents.js
const { Pool } = require("pg");

module.exports = async function handler(req, res) {
  // 1) CORS
  const origin = req.headers.origin || "*";
  res.setHeader("Access-Control-Allow-Origin", origin);
  res.setHeader("Access-Control-Allow-Methods", "GET,OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
  res.setHeader("Access-Control-Allow-Credentials", "true");

  // 2) Préflight (requête OPTIONS envoyée par le navigateur)
  if (req.method === "OPTIONS") {
    return res.status(200).end();
  }

  // 3) Auth admin
  const token = process.env.ADMIN_TOKEN;
  if (!token) {
    return res.status(500).json({ ok: false, error: "ADMIN_TOKEN manquant sur le serveur." });
  }

  if (req.headers.authorization !== `Bearer ${token}`) {
    return res.status(401).json({ ok: false, error: "Unauthorized" });
  }

  // 4) Connexion DB
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false },
  });

  try {
    const r = await pool.query(
      "SELECT id, nom, email, profil, message, created_at, ip, user_agent, document_url FROM intents ORDER BY created_at DESC"
    );

    const header = "id,nom,email,profil,message,created_at,ip,user_agent,document_url\n";
    const rows = r.rows
      .map((x) => {
        // sécuriser les guillemets
        const msg = (x.message || "").replace(/"/g, '""');
        return [
          x.id,
          x.nom,
          x.email,
          x.profil,
          msg,
          x.created_at.toISOString(),
          x.ip || "",
          x.user_agent || "",
          x.document_url || "",
        ]
          .map((v) => `"${String(v)}"`)
          .join(",");
      })
      .join("\n");

    res.setHeader("Content-Type", "text/csv; charset=utf-8");
    res.setHeader("Content-Disposition", "attachment; filename=intents.csv");
    return res.status(200).send(header + rows + "\n");
  } catch (err) {
    console.error("Erreur API /export-intents:", err);
    return res.status(500).json({ ok: false, error: "Erreur serveur BDD." });
  }
};
