import React, { useState, useEffect } from "react";
import { api } from "../config/api.js";

// (Copie des styles ici pour garder le fichier autonome)
const styles = {
  adminContainer: {
    color: "#dffdf5", backgroundColor: "#060b0a", padding: "clamp(2rem, 5vw, 4rem) 6vw",
    maxWidth: "1400px", margin: "0 auto", fontFamily: "system-ui, sans-serif", minHeight: "80vh"
  },
  adminTitle: { color: "#74ffd7", textShadow: "0 0 20px rgba(0,255,170,.4)", marginBottom: "0.5rem" },
  adminSubtitle: { fontSize: "1rem", opacity: 0.9, marginBottom: "2rem" },
  adminInput: {
    backgroundColor: "#000", border: "1px solid rgba(116,255,215,.4)", borderRadius: "8px",
    padding: ".6rem .75rem", color: "#dffdf5", fontSize: ".9rem", outline: "none", minWidth: "300px"
  },
  adminButton: {
    background: "linear-gradient(90deg,#00ffa3 0%,#008061 100%)", border: "0", borderRadius: "10px",
    padding: ".7rem 1rem", fontSize: ".9rem", fontWeight: 600, color: "#001710", cursor: "pointer"
  },
  adminError: { color: "#FF8A8A", marginTop: "1rem" },
  table: { width: "100%", borderCollapse: "collapse", marginTop: "2rem", fontSize: "0.9rem" },
  th: {
    backgroundColor: "rgba(6,11,10,.6)", border: "1px solid rgba(255,255,255,.07)",
    padding: "10px 12px", textAlign: "left", color: "#74ffd7"
  },
  td: {
    border: "1px solid rgba(255,255,255,.07)", padding: "10px 12px",
    verticalAlign: "top", opacity: 0.9, maxWidth: "300px"
  },
  pre: { whiteSpace: "pre-wrap", wordBreak: "break-word", margin: 0, fontFamily: "inherit" },
  link: { color: "#74ffd7", textDecoration: "underline" }
};

// --- Composant 1 : Page Admin ---
export default function AdminPage() {
  const [token, setToken] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [intents, setIntents] = useState([]);

  const fetchData = async (adminToken) => {
    setIsLoading(true); setError(null);
    try {
      const response = await fetch(api.adminData(), {
        headers: { Authorization: `Bearer ${adminToken}` },
      });
      if (response.status === 401) throw new Error("Token invalide ou expiré.");
      if (!response.ok) throw new Error(`Erreur HTTP : ${response.status}`);
      const data = await response.json();
      if (data.ok) {
        setIntents(data.intents || []);
        setIsAuthenticated(true);
        sessionStorage.setItem("admin_token", adminToken); 
      } else {
        throw new Error(data.error || "Réponse invalide de l'API.");
      }
    } catch (err) {
      setError(err.message);
      setIsAuthenticated(false);
      sessionStorage.removeItem("admin_token");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const savedToken = sessionStorage.getItem("admin_token");
    if (savedToken) {
      setToken(savedToken);
      fetchData(savedToken);
    }
  }, []);

  if (!isAuthenticated) {
    return (
      <LoginView
        token={token} setToken={setToken}
        onSubmit={() => fetchData(token)}
        isLoading={isLoading} error={error}
      />
    );
  }
  return <IntentsTable intents={intents} />;
}

// --- Composant 2 : Connexion ---
function LoginView({ token, setToken, onSubmit, isLoading, error }) {
  const handleSubmit = (e) => { e.preventDefault(); onSubmit(); };
  return (
    <div style={styles.adminContainer}>
      <h1 style={styles.adminTitle}>Accès Administrateur</h1>
      <p style={styles.adminSubtitle}>Entrez le Token Admin pour voir les intentions.</p>
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '10px' }}>
        <input type="password" value={token} onChange={(e) => setToken(e.target.value)} placeholder="ADMIN_TOKEN" style={styles.adminInput} />
        <button type="submit" disabled={isLoading} style={styles.adminButton}>
          {isLoading ? "Vérification..." : "Entrer"}
        </button>
      </form>
      {error && <p style={styles.adminError}>{error}</p>}
    </div>
  );
}

// --- Composant 3 : Tableau ---
function IntentsTable({ intents }) {
  return (
    <div style={styles.adminContainer}>
      <h1 style={styles.adminTitle}>Table des Intentions ({intents.length})</h1>
      <p style={styles.adminSubtitle}>Voici les soumissions reçues via le formulaire "Rejoindre".</p>
      <div style={{ overflowX: 'auto', width: '100%' }}>
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Date</th>
              <th style={styles.th}>Nom</th>
              <th style={styles.th}>Email</th>
              <th style={styles.th}>Profil</th>
              <th style={styles.th}>Message</th>
              <th style={styles.th}>Document URL</th>
              <th style={styles.th}>IP</th>
            </tr>
          </thead>
          <tbody>
            {intents.length > 0 ? (
              intents.map((intent) => (
                <tr key={intent.id}>
                  <td style={styles.td}>{new Date(intent.created_at).toLocaleString('fr-FR')}</td>
                  <td style={styles.td}>{intent.nom}</td>
                  <td style={styles.td}>{intent.email}</td>
                  <td style={styles.td}>{intent.profil}</td>
                  <td style={styles.td}><pre style={styles.pre}>{intent.message || "(vide)"}</pre></td>
                  <td style={styles.td}>
                    {intent.document_url ? (
                      <a href={intent.document_url} target="_blank" rel="noopener noreferrer" style={styles.link}>Voir Fichier</a>
                    ) : ( "N/A" )}
                  </td>
                  <td style={styles.td}>{intent.ip || "N/A"}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7" style={{ ...styles.td, textAlign: 'center', padding: '20px' }}>
                  Aucune intention reçue pour le moment.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}