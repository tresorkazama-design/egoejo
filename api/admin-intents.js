require("./_sentry");
export const runtime = 'nodejs';
const { Pool } = require('pg');

const ssl = process.env.DATABASE_URL?.includes('localhost')
  ? false
  : { rejectUnauthorized: false };

const pool = new Pool({ connectionString: process.env.DATABASE_URL, ssl });

function badAuth(req) {
  const h = req.headers?.authorization || '';
  const token = h.startsWith('Bearer ') ? h.slice(7) : '';
  return !token || token !== process.env.ADMIN_TOKEN;
}

export default async function handler(req, res) {
  if (badAuth(req)) return res.status(401).json({ ok: false, error: 'Unauthorized' });
  if (req.method !== 'GET') {
    res.setHeader('Allow', 'GET');
    return res.status(405).json({ ok: false, error: 'Method Not Allowed' });
  }

  try {
    const { from, to, profil, q, limit = '100', offset = '0' } = req.query || {};
    const where = [];
    const params = [];

    if (from)  { params.push(from);   where.push(`created_day >= $${params.length}`); }
    if (to)    { params.push(to);     where.push(`created_day <= $${params.length}`); }
    if (profil){ params.push(profil); where.push(`profil = $${params.length}`); }
    if (q) {
      params.push(`%${q}%`);
      where.push(`(nom ILIKE $${params.length} OR email ILIKE $${params.length} OR profil ILIKE $${params.length} OR message ILIKE $${params.length})`);
    }

    const lim = Math.min(parseInt(limit, 10) || 100, 1000);
    const off = Math.max(parseInt(offset, 10) || 0, 0);

    const sql = `
      SELECT id, nom, email, profil, message, created_at
      FROM intents
      ${where.length ? 'WHERE ' + where.join(' AND ') : ''}
      ORDER BY created_at DESC
      LIMIT ${lim} OFFSET ${off}
    `;

    const client = await pool.connect();
    try {
      const r = await client.query(sql, params);
      return res.status(200).json({ ok: true, count: r.rows.length, rows: r.rows });
    } finally {
      client.release();
    }
  } catch (e) {
    console.error('Erreur /api/admin-intents:', e);
    return res.status(500).json({ ok: false, error: 'Erreur serveur' });
  }
}

