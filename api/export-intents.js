export const runtime = 'nodejs';
const { getPool } = require("./db.js");
const { prepareCors } = require("./cors.js");

function maskIp(ip) {
  if (!ip) return null;
  const value = ip.split(",")[0].trim();
  if (!value) return null;
  if (value.includes(":")) {
    const segments = value.split(":");
    if (segments.length > 1) segments[segments.length - 1] = "****";
    return segments.join(":");
  }
  const parts = value.split(".");
  if (parts.length === 4) { parts[3] = "***"; return parts.join("."); }
  return value;
}

module.exports = async function handler(req, res) {
  const cors = prepareCors(req, res, { methods: ["GET","OPTIONS"] });
  if (!cors.allowed) return res.status(403).json({ ok:false, error:"Forbidden origin" });
  if (req.method === "OPTIONS") return res.status(200).end();

  const token = process.env.ADMIN_TOKEN;
  if (!token) return res.status(500).json({ ok:false, error:"ADMIN_TOKEN manquant sur le serveur." });
  if (req.headers.authorization !== `Bearer ${token}`) return res.status(401).json({ ok:false, error:"Unauthorized" });

  try {
    const r = await getPool().query(
      "SELECT id, nom, email, profil, message, created_at, ip, user_agent, document_url FROM intents ORDER BY created_at DESC"
    );

    const wantsJson =
      (req.headers.accept && req.headers.accept.includes("application/json")) ||
      (req.query && req.query.format === "json");

    if (wantsJson) {
      const intents = r.rows.map(({ user_agent, ...rest }) => ({
        ...rest,
        ip: maskIp(rest.ip),
      }));
      return res.status(200).json({ ok:true, intents });
    }

    const header = "id,nom,email,profil,message,created_at,ip,user_agent,document_url\n";
    const rows = r.rows.map((x) => {
      const msg = (x.message || "").replace(/"/g, '""');
      return [
        x.id, x.nom, x.email, x.profil, msg,
        x.created_at.toISOString(), x.ip || "", x.user_agent || "", x.document_url || ""
      ].map((v) => `"${String(v)}"`).join(",");
    }).join("\n");

    res.setHeader("Content-Type", "text/csv; charset=utf-8");
    res.setHeader("Content-Disposition", "attachment; filename=intents.csv");
    return res.status(200).send(header + rows + "\n");
  } catch (err) {
    console.error("Erreur API /export-intents:", err);
    return res.status(500).json({ ok:false, error:"Erreur serveur BDD." });
  }
};

