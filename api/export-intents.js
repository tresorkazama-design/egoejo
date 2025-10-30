const { Pool } = require("pg");

module.exports = async function handler(req, res) {
  if (req.headers.authorization !== `Bearer ${process.env.ADMIN_TOKEN}`) {
    res.statusCode = 401;
    return res.end("Unauthorized");
  }
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: false },
  });

  const r = await pool.query(
    "SELECT id, nom, email, profil, message, created_at FROM intents ORDER BY created_at DESC"
  );

  const header = "id,nom,email,profil,message,created_at\n";
  const rows = r.rows
    .map((x) =>
      [x.id, x.nom, x.email, x.profil, (x.message || "").replaceAll('"', '""'), x.created_at.toISOString()]
        .map((v) => `"${String(v)}"`).join(",")
    )
    .join("\n");

  res.setHeader("Content-Type", "text/csv; charset=utf-8");
  res.setHeader("Content-Disposition", "attachment; filename=intents.csv");
  res.end(header + rows + "\n");
};