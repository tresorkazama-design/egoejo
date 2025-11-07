const { Client } = require("pg");
(async () => {
  const ssl = process.env.DATABASE_URL?.includes("localhost") ? false : { rejectUnauthorized:false };
  const c = new Client({ connectionString: process.env.DATABASE_URL, ssl });
  await c.connect();
  await c.query(`
    create table if not exists rate_limits (
      key text primary key,
      count integer not null default 0,
      reset_at timestamptz not null
    );
    create index if not exists idx_rate_limits_reset on rate_limits (reset_at);
  `);
  await c.end();
  console.log("✅ rate_limits table ready");
})().catch(e => { console.error("❌", e); process.exit(1); });
