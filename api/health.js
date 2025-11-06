export const runtime = 'nodejs';
export default async function handler(req, res) {
  res.status(200).json({
    ok: true,
    node: process.version,
    frontend: process.env.FRONTEND_URL || null,
    db: !!process.env.DATABASE_URL
  });
}
