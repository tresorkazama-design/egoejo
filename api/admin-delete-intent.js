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
  if (badAuth(req)) return res.status(401).json({ ok:false, error:'Unauthorized' });

  if (req.method !== 'DELETE' && req.method !== 'POST') {
    res.setHeader('Allow', 'DELETE, POST');
    return res.status(405).json({ ok:false, error:'Method Not Allowed' });
  }

  const id = req.query?.id || req.body?.id;
  if (!id) return res.status(400).json({ ok:false, error:'id requis' });

  const client = await pool.connect();
  try {
    const r = await client.query('DELETE FROM intents WHERE id = $1', [id]);
    return res.status(200).json({ ok:true, deleted:r.rowCount });
  } catch (e) {
    console.error('Erreur /api/admin-delete-intent:', e);
    return res.status(500).json({ ok:false, error:'Erreur serveur BDD.' });
  } finally {
    client.release();
  }
}

