const { Client } = require("pg");
(async () => {
  const ssl = process.env.DATABASE_URL?.includes("localhost") ? false : { rejectUnauthorized: false };
  const c = new Client({ connectionString: process.env.DATABASE_URL, ssl });
  await c.connect();
  const dup = await c.query(`
    SELECT email, created_day, COUNT(*) AS c
    FROM intents
    GROUP BY email, created_day
    HAVING COUNT(*) > 1
    ORDER BY c DESC
    LIMIT 10
  `);
  console.table(dup.rows);
  await c.end();
})();
