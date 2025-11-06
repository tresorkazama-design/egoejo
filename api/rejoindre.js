export const runtime = 'nodejs';
const { Pool } = require('pg');

const ssl = process.env.DATABASE_URL?.includes('localhost')
  ? false
  : { rejectUnauthorized: false };
const pool = new Pool({ connectionString: process.env.DATABASE_URL, ssl });

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, error: 'Method Not Allowed' });
  }

  try {
    const { nom, email, profil, message, website } = req.body || {};
    if (website) return res.status(200).json({ ok: true, id: null, created_at: null }); // honeypot
    if (!nom || !email || !profil) return res.status(400).json({ ok: false, error: 'Champs requis manquants' });

    const ip = (req.headers['x-forwarded-for'] || req.socket?.remoteAddress || '').toString().split(',')[0].trim();
    const ua = (req.headers['user-agent'] || '').toString();

    const client = await pool.connect();
    try {
      // Idempotent : un seul enregistrement par (email, created_day)
      const q = `
        INSERT INTO intents (nom, email, profil, message, ip, user_agent, created_at)
        VALUES ($1,$2,$3,$4,$5,$6, NOW())
        ON CONFLICT ON CONSTRAINT intents_email_day_uniq
        DO UPDATE SET
          message = COALESCE(EXCLUDED.message, intents.message),
          profil  = COALESCE(EXCLUDED.profil, intents.profil)
        RETURNING id, created_at
      `;
      const r = await client.query(q, [nom, email, profil, message || null, ip || null, ua || null]);
      const row = r.rows[0] || null;
      return res.status(200).json({ ok: true, id: row?.id ?? null, created_at: row?.created_at ?? null });
    } finally {
      client.release();
    }
  } catch (e) {
    console.error('Erreur API /rejoindre:', e);
    return res.status(500).json({ ok: false, error: 'Erreur serveur' });
  }
}
