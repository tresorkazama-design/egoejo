export const runtime = 'nodejs';
const { Client } = require("pg");

const ssl = process.env.DATABASE_URL?.includes("localhost") ? false : { rejectUnauthorized:false };

async function withClient(fn){
  const c = new (require("pg").Client)({ connectionString: process.env.DATABASE_URL, ssl });
  await c.connect();
  try { return await fn(c); } finally { await c.end(); }
}

/**
 * checkRate({ key, limit: 10, window: 60 })
 * Retourne { allowed:boolean, remaining:number, reset:number(ms) }
 */
async function checkRate({ key, limit = 10, window = 60 }) {
  const now = new Date();
  const res = await withClient(async (c) => {
    const q = `
      insert into rate_limits(key, count, reset_at)
      values ($1, 1, now() + ($2 || ' seconds')::interval)
      on conflict (key)
      do update set
        count = CASE WHEN rate_limits.reset_at > now() THEN rate_limits.count + 1 ELSE 1 END,
        reset_at = CASE WHEN rate_limits.reset_at > now() THEN rate_limits.reset_at ELSE now() + ($2 || ' seconds')::interval END
      returning count, extract(epoch from (reset_at - now()))::int as ttl
    `;
    const r = await c.query(q, [key, String(window)]);
    const count = r.rows[0].count;
    const ttl = Math.max(0, r.rows[0].ttl);
    return { count, ttl };
  });
  return { allowed: res.count <= limit, remaining: Math.max(0, limit - res.count), reset: res.ttl * 1000 };
}

module.exports = { checkRate };
