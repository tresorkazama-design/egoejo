export const runtime = 'nodejs';
const { Pool } = require('pg');
const { checkRate } = require('./_rate-limit'); // RATE_LIMIT

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
    if (!nom || !email || !profil) {
      return res.status(400).json({ ok: false, error: 'Champs requis manquants' });
    }

    const ip = (req.headers['x-forwarded-for'] || req.socket?.remoteAddress || '')
      .toString().split(',')[0].trim();
    const ua = (req.headers['user-agent'] || '').toString();

    // --- RATE LIMIT: 10 req / 60s par IP ---
    const rlKey = `rejoindre:${ip || 'unknown'}`;
    const rl = await checkRate({ key: rlKey, limit: 10, window: 60 });
    if (!rl.allowed) {
      res.setHeader('Retry-After', Math.ceil(rl.reset / 1000).toString());
      return res.status(429).json({ ok: false, error: 'Trop de requêtes, réessayez plus tard', retry_after: rl.reset });
    }

    const client = await pool.connect();
    try {
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
