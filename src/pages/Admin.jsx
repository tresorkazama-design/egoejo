import { useEffect, useMemo, useState } from "react";

const PROFILS = ["je-decouvre", "je-protege", "je-soutiens"];

export default function Admin() {
  const [baseUrl] = useState(window.location.origin);
  const [token, setToken] = useState(localStorage.getItem("ADMIN_TOKEN") || "");
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [profil, setProfil] = useState("");            // pas de filtre par défaut
  const [q, setQ] = useState("");
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [limit, setLimit] = useState(200);
  const [offset, setOffset] = useState(0);

  // Lire le token depuis l'URL (#token= ou ?token=), mémoriser & autoload
  useEffect(() => {
    try {
      const hp = new URLSearchParams(location.hash.slice(1));
      const sp = new URLSearchParams(location.search);
      const t = hp.get("token") || sp.get("token");
      if (t && t !== token) {
        setToken(t);
        localStorage.setItem("ADMIN_TOKEN", t);
      }
    } catch (e) { console.warn("token-from-url failed", e); }
    // si déjà en localStorage, on gardera le state initial
  }, []);

  // Sauvegarder le token dans le storage
  useEffect(() => {
    if (token) localStorage.setItem("ADMIN_TOKEN", token);
  }, [token]);

  // Construire la query-string à partir des filtres
  const qs = useMemo(() => {
    const u = new URLSearchParams();
    if (from) u.set("from", from);
    if (to) u.set("to", to);
    if (profil) u.set("profil", profil);
    if (q) u.set("q", q);
    u.set("limit", String(limit));
    u.set("offset", String(offset));
    return u.toString();
  }, [from, to, profil, q, limit, offset]);

  async function load() {
    if (!token) return;                 // pas d'alerte : simplement ne rien faire
    setLoading(true);
    try {
      const r = await fetch(`${baseUrl}/api/admin-intents?${qs}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const json = await r.json();
      setRows(json.rows || []);
    } catch (e) {
      console.error(e);
      // Optionnel: message non bloquant
      // alert("Erreur chargement admin-intents.");
    } finally {
      setLoading(false);
    }
  }

  // Auto-load : au montage (si token déjà présent) ET à chaque fois que le token change
  useEffect(() => { if (token) load(); }, [token]);   // charge dès que le token est connu
  useEffect(() => { if (token) load(); }, [qs]);      // recharge quand les filtres changent

  return (
    <div style={{ minHeight:"100vh", padding: 16, maxWidth: 1200, margin: "0 auto", fontFamily: "system-ui, sans-serif", background:"#fff", color:"#111" }}>
      <h1 style={{ marginBottom: 8 }}>Admin — Intents</h1>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 8, marginBottom: 8 }}>
        <input placeholder="ADMIN_TOKEN" value={token} onChange={e => setToken(e.target.value)} />
        <input type="date" value={from} onChange={e => setFrom(e.target.value)} />
        <input type="date" value={to} onChange={e => setTo(e.target.value)} />
        <select value={profil} onChange={e => setProfil(e.target.value)}>
          <option value="">Tous profils</option>
          {PROFILS.map(p => <option key={p} value={p}>{p}</option>)}
        </select>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr 1fr 1fr", gap: 8, alignItems: "center", marginBottom: 12 }}>
        <input placeholder="Recherche (nom/email/message)" value={q} onChange={e => setQ(e.target.value)} />
        <input type="number" min={10} max={1000} value={limit} onChange={e => setLimit(Number(e.target.value))} />
        <input type="number" min={0} step={limit} value={offset} onChange={e => setOffset(Number(e.target.value))} />
        <button onClick={load} disabled={loading}>{loading ? "Chargement..." : "Actualiser"}</button>
        <button onClick={async () => {
          try {
            const r = await fetch(`${baseUrl}/api/export-intents?${qs}`, { headers: { Authorization: `Bearer ${token}` } });
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            const blob = await r.blob();
            const a = document.createElement("a");
            a.href = URL.createObjectURL(blob);
            a.download = "intents.csv";
            document.body.appendChild(a); a.click(); a.remove();
          } catch (e) { console.error(e); }
        }}>Export CSV</button>
      </div>

      <div style={{ overflowX: "auto", border: "1px solid #eee", borderRadius: 8 }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
          <thead style={{ background: "#fafafa" }}>
            <tr>
              <th style={th}>ID</th>
              <th style={th}>Nom</th>
              <th style={th}>Email</th>
              <th style={th}>Profil</th>
              <th style={th}>Message</th>
              <th style={th}>Créé</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td style={td}><code>{String(r.id).slice(0,8)}…</code></td>
                <td style={td}>{r.nom}</td>
                <td style={td}>{r.email}</td>
                <td style={td}>{r.profil}</td>
                <td style={td}>{r.message}</td>
                <td style={td}>{new Date(r.created_at).toLocaleString()}</td>
              </tr>
            ))}
            {!rows.length && <tr><td style={td} colSpan={6}>Saisir le token (ou passer `?token=` dans l'URL) puis cliquer "Actualiser".</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
const th = { textAlign: "left", padding: "8px 10px", borderBottom: "1px solid #eee" };
const td = { padding: "8px 10px", borderBottom: "1px solid #f2f2f2", verticalAlign: "top" };
