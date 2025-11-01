const { Pool } = require("pg");
const { Resend } = require("resend");
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
});
module.exports = async function handler(req, res) {
  const allowed = new Set(["http://localhost:5173", process.env.FRONTEND_URL || ""]);
  const origin = req.headers.origin || "";
  if (origin && !allowed.has(origin)) {
    return res.status(403).json({ ok: false, error: "Forbidden origin" });
  }
  if (req.method === "OPTIONS") { return res.status(200).end(); }
  if (req.method !== "POST") { return res.status(405).json({ ok: false, error: "Use POST" }); }
  try {
    const { nom, email, profil, message, website, document_url } = req.body || {};
    if (website) { return res.status(200).json({ ok: true, id: null }); }
    if (!nom || !email || !profil) { return res.status(400).json({ ok: false, error: "Champs manquants" }); }
    const ip = (req.headers["x-forwarded-for"] || "").split(",")[0].trim();
    const ua = req.headers["user-agent"] || "";
    const query = `
      INSERT INTO intents (nom, email, profil, message, ip, user_agent, document_url)
      VALUES ($1, $2, $3, $4, $5, $6, $7)
      RETURNING id, created_at
    `;
    const values = [nom, email, profil, message || null, ip ? ip : null, ua || null, document_url || null];
    const result = await pool.query(query, values);
    try {
      if (process.env.RESEND_API_KEY) {
        const resend = new Resend(process.env.RESEND_API_KEY);
        await resend.emails.send({
          from: "EGOEJO <noreply@egoejo.com>",
          to: process.env.NOTIFY_EMAIL || "tresor.kazama@gmail.com",
          subject: "Nouvelle intention reçue (EGOEJO)",
          text: `Nom: ${nom}\nEmail: ${email}\nProfil: ${profil}\nMessage:\n${message || "(vide)"}`
        });
      }
    } catch (e) { console.error("Resend error", e); }
    return res.status(200).json({
      ok: true,
      id: result.rows[0].id,
      created_at: result.rows[0].created_at,
    });
  } catch (err) {
    console.error("Erreur API /rejoindre:", err);
    return res.status(500).json({ ok: false, error: "Erreur serveur" });
  }
};