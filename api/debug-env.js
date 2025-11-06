export const runtime = 'nodejs';
module.exports = (req,res) => {
  res.setHeader("Content-Type","application/json");
  res.end(JSON.stringify({
    node: process.version,
    env: {
      DATABASE_URL: !!process.env.DATABASE_URL,
      ADMIN_TOKEN: process.env.ADMIN_TOKEN ? (process.env.ADMIN_TOKEN.slice(0,4)+"***") : null,
      FRONTEND_URL: process.env.FRONTEND_URL || null
    }
  }));
}

