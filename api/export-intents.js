require("./_sentry");
export const runtime = 'nodejs';
const { Pool } = require('pg');

const ssl = process.env.DATABASE_URL?.includes('localhost')
  ? false
  : { rejectUnauthorized: false };
const pool = new Pool({ connectionString: process.env.DATABASE_URL, ssl });

function toCSV(rows) {
  if (!rows?.length) return 'id,nom,email,profil,message,created_at\n';
  const headers = Object.keys(rows[0]);
  const esc = (v) => {
    if (v == null) return '';
    const s = String(v).replace(/"/g, '""');
    return /[",\n]/.test(s) ? `"${s}"` : s;
  };
  return [headers.join(','), ...rows.map(r => headers.map(h => esc(r[h])).join(','))].join('\n');
}

export default async function handler(req, res) {
  try {
    const auth = req.headers.authorization || '';
    const token = auth.startsWith('Bearer ') ? auth.slice(7) : '';
    if (!token || token !== process.env.ADMIN_TOKEN) {
      return res.status(401).json({ ok: false, error: 'Unauthorized' });
    }

    const { from, to, profil } = req.query || {};
    const params = [];
    const where = [];

    if (from) { params.push(from); where.push(`created_day >= $${params.length}`); }
    if (to)   { params.push(to);   where.push(`created_day <= $${params.length}`); }
    if (profil) { params.push(profil); where.push(`profil = $${params.length}`); }

    const sql = `
      SELECT id, nom, email, profil, message, created_at
      FROM intents
      ${where.length ? 'WHERE ' + where.join(' AND ') : ''}
      ORDER BY created_at DESC
      LIMIT 10000
    `;

    const client = await pool.connect();
    try {
      const r = await client.query(sql, params);
      const csv = toCSV(r.rows);
      res.setHeader('Content-Type', 'text/csv; charset=utf-8');
      res.setHeader('Content-Disposition', 'attachment; filename="intents.csv"');
      return res.status(200).send(csv);
    } finally {
      client.release();
    }
  } catch (e) {
    console.error('Erreur export-intents:', e);
    return res.status(500).json({ ok: false, error: 'Erreur serveur BDD.' });
  }
}

