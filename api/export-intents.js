const { Pool } = require("pg");
module.exports = async function handler(req, res) {
  if (req.headers.authorization !== `Bearer ${process.env.ADMIN_TOKEN}`) {
    return res.status(401).end("Unauthorized");
  }
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false },
  });
  try {
    const r = await pool.query(
      "SELECT id, nom, email, profil, message, created_at, ip, user_agent, document_url FROM intents ORDER BY created_at DESC"
    );
    const header = "id,nom,email,profil,message,created_at,ip,user_agent,document_url\n";
    const rows = r.rows.map((x) =>
      [x.id, x.nom, x.email, x.profil, (x.message || "").replaceAll('"', '""'), x.created_at.toISOString(), x.ip, x.user_agent, x.document_url]
        .map((v) => `"${String(v)}"`).join(",")
    ).join("\n");
    res.setHeader("Content-Type", "text/csv; charset=utf-8");
    res.setHeader("Content-Disposition", "attachment; filename=intents.csv");
    res.status(200).end(header + rows + "\n");
  } catch (err) {
    console.error("Erreur API /export-intents:", err);
    return res.status(500).json({ ok: false, error: "Erreur serveur BDD." });
  }
};