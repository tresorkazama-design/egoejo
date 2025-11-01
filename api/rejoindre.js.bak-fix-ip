const { Pool } = require("pg");
const { Resend } = require("resend");

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
});

module.exports = async function handler(req, res) {
  // CORS basique
  const allowed = new Set([
    "http://localhost:5173",
    process.env.FRONTEND_URL || ""
  ]);
  const origin = req.headers.origin || "";
  if (origin && !allowed.has(origin)) {
    res.statusCode = 403;
    return res.json({ ok: false, error: "Forbidden origin" });
  }

  if (req.method !== "POST") {
    res.statusCode = 405;
    return res.json({ ok: false, error: "Use POST" });
  }

  try {
    // lecture du corps
    let body = "";
    await new Promise((resolve, reject) => {
      req.on("data", (c) => (body += c.toString()));
      req.on("end", resolve);
      req.on("error", reject);
    });
    const data = JSON.parse(body || "{}");
    const { nom, email, profil, message, website } = data;

    // honeypot anti-spam : si rempli -> on dit OK mais on ne stocke pas
    if (website) {
      res.statusCode = 200;
      return res.json({ ok: true, id: null, created_at: null });
    }

    // validations basiques
    if (!nom || !email || !profil) {
      res.statusCode = 400;
      return res.json({ ok: false, error: "Champs manquants" });
    }
    const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    if (!emailOk) {
      res.statusCode = 400;
      return res.json({ ok: false, error: "Email invalide" });
    }
    if (message && message.length > 2000) {
      res.statusCode = 413;
      return res.json({ ok: false, error: "Message trop long" });
    }

    const ip = (req.headers["x-forwarded-for"] || "").split(",")[0].trim();
    const ua = req.headers["user-agent"] || "";

    const query = `
      INSERT INTO intents (nom, email, profil, message, ip, user_agent)
      VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING id, created_at
    `;
    const values = [nom, email, profil, message || null, ip || null, ua || null];
    const result = await pool.query(query, values);

    // notif email (best-effort)
    try {
      if (process.env.RESEND_API_KEY) {
        const resend = new Resend(process.env.RESEND_API_KEY);
        await resend.emails.send({
          from: "EGOEJO <noreply@egoejo.com>",
          to: process.env.NOTIFY_EMAIL || "tresor.kazama@gmail.com",
          subject: "Nouvelle intention reçue",
          text:
            `Nom: ${nom}\nEmail: ${email}\nProfil: ${profil}\nMessage:\n${message || "(vide)"}\n` +
            `IP: ${ip}\nUA: ${ua}`
        });
      }
    } catch (e) {
      console.error("Resend error", e);
    }

    res.statusCode = 200;
    return res.json({
      ok: true,
      id: result.rows[0].id,
      created_at: result.rows[0].created_at,
    });
  } catch (err) {
    console.error("Erreur API /rejoindre:", err);
    res.statusCode = 500;
    return res.json({ ok: false, error: "Erreur serveur" });
  }
};