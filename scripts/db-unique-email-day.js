const { Client } = require("pg");

(async () => {
  const ssl = process.env.DATABASE_URL?.includes("localhost")
    ? false
    : { rejectUnauthorized: false };
  const c = new Client({ connectionString: process.env.DATABASE_URL, ssl });
  await c.connect();

  // 1) Ajouter la colonne générée (UTC) si absente
  await c.query(`
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name='intents' AND column_name='created_day'
      ) THEN
        ALTER TABLE intents
        ADD COLUMN created_day date
        GENERATED ALWAYS AS ( (created_at AT TIME ZONE 'UTC')::date ) STORED;
      END IF;
    END
    $$;
  `);

  // 2) Ajouter la contrainte UNIQUE (email, created_day) si absente
  await c.query(`
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conrelid = 'intents'::regclass
          AND contype = 'u'
          AND conname = 'intents_email_day_uniq'
      ) THEN
        ALTER TABLE intents
        ADD CONSTRAINT intents_email_day_uniq UNIQUE (email, created_day);
      END IF;
    END
    $$;
  `);

  // 3) Afficher colonnes & index pour vérif
  const cols = await c.query(`
    SELECT column_name, data_type, is_generated, generation_expression
    FROM information_schema.columns
    WHERE table_name='intents'
    ORDER BY ordinal_position
  `);
  console.table(cols.rows);

  const idx = await c.query(`
    SELECT indexname, indexdef
    FROM pg_indexes
    WHERE tablename='intents'
    ORDER BY indexname
  `);
  console.table(idx.rows);

  await c.end();
  console.log("✅ created_day + UNIQUE(email, created_day) OK");
})().catch(e => { console.error("❌", e.stack || e.message); process.exit(1); });
