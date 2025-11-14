const { Client } = require('pg');
const conn = process.env.DATABASE_URL;
if (!conn) { console.error('DATABASE_URL missing'); process.exit(1); }
const ssl = conn.includes('localhost') ? false : { rejectUnauthorized: false };
const client = new Client({ connectionString: conn, ssl });
const sql = `
CREATE TABLE IF NOT EXISTS intents (
  id SERIAL PRIMARY KEY,
  nom TEXT NOT NULL,
  email TEXT NOT NULL,
  profil TEXT NOT NULL,
  message TEXT,
  ip TEXT,
  user_agent TEXT,
  document_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
`;
(async () => {
  try {
    await client.connect();
    await client.query(sql);
    console.log('OK: intents table ready.');
  } catch (e) {
    console.error(e);
    process.exitCode = 1;
  } finally {
    await client.end();
  }
})();
