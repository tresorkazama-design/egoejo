const { Client } = require("pg");

(async () => {
  const ssl = process.env.DATABASE_URL?.includes("localhost")
    ? false
    : { rejectUnauthorized: false };

  const c = new Client({ connectionString: process.env.DATABASE_URL, ssl });
  await c.connect();

  // Crée l’index UNIQUE (email + jour) uniquement si absent, et uniquement si email IS NOT NULL
  await c.query(`
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM pg_indexes
        WHERE schemaname = 'public' AND indexname = 'intents_email_per_day'
      ) THEN
        EXECUTE 'CREATE UNIQUE INDEX intents_email_per_day
                 ON intents (email, (date(created_at)))
                 WHERE email IS NOT NULL';
      END IF;
    END
    $$;
  `);

  // Vérif
  const r = await c.query(`
    SELECT indexname, indexdef
    FROM pg_indexes
    WHERE tablename='intents'
    ORDER BY indexname
  `);
  console.table(r.rows);

  await c.end();
  console.log("✅ Unique index ready");
})().catch(e => { console.error("❌", e.message); process.exit(1); });
