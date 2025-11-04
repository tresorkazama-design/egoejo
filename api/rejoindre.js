const { Resend } = require("resend");
const { getPool } = require("./db.js");
const { prepareCors } = require("./cors.js");

module.exports = async function handler(req, res) {
  // 1) CORS
  const cors = prepareCors(req, res, { methods: ["POST", "OPTIONS"] });
  if (!cors.allowed) {
    return res.status(403).json({ ok: false, error: "Forbidden origin" });
  }

  // 2) Préflight (navigateur)
  if (req.method === "OPTIONS") {
    return res.status(204).end();
  }

  // 3) Vérification méthode
  if (req.method !== "POST") {
    return res.status(405).json({ ok: false, error: "Use POST" });
  }
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
    const result = await getPool().query(query, values);
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
