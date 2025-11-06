const {Client}=require("pg");
(async()=>{
  const c = new Client({
    connectionString: process.env.DATABASE_URL,
    ssl: process.env.DATABASE_URL.includes("localhost") ? false : {rejectUnauthorized:false}
  });
  await c.connect();
  await c.query(`CREATE TABLE IF NOT EXISTS intents(
    id SERIAL PRIMARY KEY,
    nom TEXT NOT NULL,
    email TEXT NOT NULL,
    profil TEXT NOT NULL,
    message TEXT,
    ip TEXT,
    user_agent TEXT,
    document_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
  )`);
  const r = await c.query("SELECT COUNT(*)::int AS n FROM intents");
  console.log("intents en base =", r.rows[0].n);
  await c.end();
})().catch(e=>{ console.error(e); process.exit(1); });
