const { Client } = require("pg");
(async () => {
  const ssl = process.env.DATABASE_URL?.includes("localhost") ? false : { rejectUnauthorized:false };
  const c = new Client({ connectionString: process.env.DATABASE_URL, ssl });
  await c.connect();
  const r = await c.query(`delete from rate_limits where reset_at < now() - interval '1 day' returning count`);
  console.log("🧹 cleaned rows:", r.rowCount);
  await c.end();
})();
