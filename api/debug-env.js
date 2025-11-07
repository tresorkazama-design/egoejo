require("./_sentry");
export const runtime = 'nodejs';

export default async function handler(req, res) {
  try {
    const safeEnv = {
      DATABASE_URL: !!process.env.DATABASE_URL,
      ADMIN_TOKEN: process.env.ADMIN_TOKEN ? process.env.ADMIN_TOKEN.slice(0,4) + "***" : null,
      FRONTEND_URL: process.env.FRONTEND_URL || null
    };
    res.setHeader('Content-Type', 'application/json; charset=utf-8');
    res.status(200).json({ node: process.version, env: safeEnv });
  } catch (e) {
    res.status(500).json({ ok: false, error: e?.message || String(e) });
  }
}

