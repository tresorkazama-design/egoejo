const { Client } = require("pg");

(async () => {
  const ssl = process.env.DATABASE_URL?.includes("localhost")
    ? false
    : { rejectUnauthorized: false };

  const c = new Client({ connectionString: process.env.DATABASE_URL, ssl });
  await c.connect();

  // 1) index trié sur la date (pour export/tri récents)
  await c.query(`CREATE INDEX IF NOT EXISTS intents_created_at_idx ON intents (created_at DESC)`);

  // 2) (optionnel) unicity email + jour — échoue s'il existe déjà des doublons
  try {
    await c.query(`CREATE UNIQUE INDEX IF NOT EXISTS intents_email_per_day ON intents (email, (date(created_at)))`);
  } catch (e) {
    console.warn("⚠️ Impossible de créer l'index unique (probables doublons).");
    console.warn("Top doublons (email, date, count) :");
    const dup = await c.query(`
      SELECT email, DATE(created_at) AS day, COUNT(*) AS c
      FROM intents
      GROUP BY email, DATE(created_at)
      HAVING COUNT(*) > 1
      ORDER BY c DESC
      LIMIT 10
    `);
    console.table(dup.rows);
  }

  // Vérif des index présents
  const r = await c.query(`
    SELECT indexname, indexdef
    FROM pg_indexes
    WHERE tablename='intents'
    ORDER BY indexname
  `);
  console.table(r.rows);
  await c.end();
  console.log("✅ Indexes applied/verified");
})().catch(e => { console.error("❌", e.message); process.exit(1); });
