const {Client}=require("pg");
const conn=process.env.DATABASE_URL;
const ssl = conn.includes("localhost") ? false : {rejectUnauthorized:false};
(async()=>{
  const c=new Client({connectionString:conn,ssl});
  await c.connect();
  const r=await c.query("SELECT COUNT(*)::int AS n FROM intents");
  console.log("intents en base =", r.rows[0].n);
  await c.end();
})().catch(e=>{console.error(e);process.exit(1);});
