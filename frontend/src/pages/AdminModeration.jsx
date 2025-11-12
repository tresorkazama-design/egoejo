export default function AdminModerationPage() {
  return (
    <div className="page">
      <div className="container" style={{ display: "grid", gap: 32 }}>
        <header className="grid" style={{ gap: 12 }}>
          <span className="tag">Modération</span>
          <h1 className="heading-l">Surveillance & Journal</h1>
          <p className="lead">
            Cette page servira de tableau de bord pour gérer les signalements, les audits et les actions de
            modération.
          </p>
        </header>

        <section className="glass" style={{ padding: 24 }}>
          <h2 style={{ marginTop: 0 }}>Signalements récents</h2>
          <p className="muted">
            En attente d’implémentation. Ici s’afficheront les signalements en cours avec les détails nécessaires
            pour les traiter.
          </p>
        </section>

        <section className="glass" style={{ padding: 24 }}>
          <h2 style={{ marginTop: 0 }}>Historique des actions</h2>
          <p className="muted">
            En attente d’implémentation. Cette section listera les actions effectuées par l’équipe de modération
            pour assurer la traçabilité.
          </p>
        </section>
      </div>
    </div>
  );
}
import { useEffect, useState } from "react";
import { api } from "../config/api.js";
import { LoadingState, EmptyState, ErrorState } from "../components/Feedback.jsx";

function useFetch(url, options) {
  const [state, setState] = useState({ data: null, error: null, loading: true });

  useEffect(() => {
    let active = true;
    setState({ data: null, error: null, loading: true });
    fetch(url, { credentials: "include", ...options })
      .then(async (response) => {
        if (!response.ok) {
          const detail = await response.text();
          throw new Error(detail || response.statusText);
        }
        return response.json();
      })
      .then((data) => {
        if (active) setState({ data, error: null, loading: false });
      })
      .catch((error) => {
        if (active) setState({ data: null, error, loading: false });
      });
    return () => {
      active = false;
    };
  }, [url]);

  return state;
}

function ModerationTable() {
  const { data, loading, error } = useFetch(api.moderationReports());

  if (loading) return <LoadingState message="Chargement des signalements…" />;
  if (error)
    return (
      <ErrorState
        message="Impossible de récupérer les signalements."
        action={<button className="btn btn-ghost" onClick={() => window.location.reload()}>Recharger</button>}
      />
    );
  if (!data || data.length === 0)
    return <EmptyState title="Aucun signalement" description="Vous êtes à jour !" />;

  return (
    <div className="glass" style={{ padding: 16, display: "grid", gap: 12 }}>
      {data.map((report) => (
        <article key={report.id} className="glass" style={{ padding: 12, display: "grid", gap: 6 }}>
          <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <strong>Signalement #{report.id}</strong>
            <span className="tag">{report.status || "nouveau"}</span>
          </header>
          <p style={{ margin: 0 }}>{report.reason}</p>
          <footer className="muted" style={{ fontSize: "0.85rem" }}>
            {report.created_at ? new Date(report.created_at).toLocaleString() : "Date inconnue"}
          </footer>
        </article>
      ))}
    </div>
  );
}

function AuditLogList() {
  const { data, loading, error } = useFetch(api.auditLogs());

  if (loading) return <LoadingState message="Chargement de l'historique…" />;
  if (error)
    return (
      <ErrorState
        message="Impossible de récupérer l'historique."
        action={<button className="btn btn-ghost" onClick={() => window.location.reload()}>Recharger</button>}
      />
    );
  if (!data || data.length === 0)
    return <EmptyState title="Aucun événement" description="Aucune action récente à afficher." />;

  return (
    <div className="glass" style={{ padding: 16, display: "grid", gap: 8 }}>
      {data.map((entry) => (
        <div key={entry.id} className="glass" style={{ padding: 12 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <strong>{entry.action}</strong>
            <span className="muted" style={{ fontSize: "0.85rem" }}>
              {entry.timestamp ? new Date(entry.timestamp).toLocaleString() : "Date inconnue"}
            </span>
          </div>
          {entry.user && (
            <div className="muted" style={{ fontSize: "0.85rem" }}>
              Utilisateur : {entry.user.username || entry.user.email || entry.user.id}
            </div>
          )}
          {entry.details && <p style={{ margin: "8px 0 0" }}>{entry.details}</p>}
        </div>
      ))}
    </div>
  );
}

export default function AdminModerationPage() {
  return (
    <div className="page">
      <div className="container" style={{ display: "grid", gap: 32 }}>
        <header className="grid" style={{ gap: 12 }}>
          <span className="tag">Modération</span>
          <h1 className="heading-l">Tableau de bord</h1>
          <p className="lead">Surveille les signalements, prends des décisions et garde une trace des actions.</p>
        </header>

        <section className="grid" style={{ gap: 16 }}>
          <h2 style={{ margin: 0 }}>Signalements</h2>
          <ModerationTable />
        </section>

        <section className="grid" style={{ gap: 16 }}>
          <h2 style={{ margin: 0 }}>Historique des actions</h2>
          <AuditLogList />
        </section>
      </div>
    </div>
  );
}
import { useMemo, useState } from "react";
import {
  useAuditLogs,
  useModerationReports,
  useUpdateModerationReport,
  useDeleteModerationReport,
} from "../hooks/useModeration.js";
import { useToast } from "../hooks/useToast.js";
import { LoadingState, EmptyState, ErrorState } from "../components/Feedback.jsx";

const STATUS_LABELS = {
  pending: "En attente",
  accepted: "Accepté",
  rejected: "Rejeté",
};

const TYPE_LABELS = {
  message: "Message",
  user: "Utilisateur",
  poll: "Scrutin",
  project: "Projet",
};

function StatusBadge({ status }) {
  const map = {
    pending: { label: "En attente", color: "rgba(255, 200, 0, 0.2)" },
    accepted: { label: "Accepté", color: "rgba(0, 180, 120, 0.2)" },
    rejected: { label: "Rejeté", color: "rgba(200, 60, 80, 0.2)" },
  };
  const { label, color } = map[status] ?? { label: status, color: "rgba(255,255,255,0.1)" };
  return (
    <span className="tag" style={{ background: color, color: "inherit" }}>
      {label}
    </span>
  );
}

function ModerationTable({ onSelectReport }) {
  const { data, isLoading, isError } = useModerationReports();

  if (isLoading) return <LoadingState message="Chargement des signalements…" />;
  if (isError)
    return (
      <ErrorState
        message="Erreur de chargement des signalements."
        action={<button className="btn btn-ghost" onClick={() => window.location.reload()}>Recharger</button>}
      />
    );
  if (!data || data.length === 0) return <EmptyState title="Aucun signalement" description="Les signalements apparaîtront ici." />;

  return (
    <div className="glass" style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr className="muted" style={{ textAlign: "left" }}>
            <th style={{ padding: "12px" }}>Type</th>
            <th style={{ padding: "12px" }}>Cible</th>
            <th style={{ padding: "12px" }}>Statut</th>
            <th style={{ padding: "12px" }}>Reporter</th>
            <th style={{ padding: "12px" }}>Créé le</th>
            <th style={{ padding: "12px" }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {data.map((report) => (
            <tr key={report.id} style={{ borderTop: "1px solid rgba(255,255,255,0.08)" }}>
              <td style={{ padding: "12px" }}>{TYPE_LABELS[report.report_type] || report.report_type}</td>
              <td style={{ padding: "12px" }}>{report.target_id}</td>
              <td style={{ padding: "12px" }}>
                <StatusBadge status={report.status} />
              </td>
              <td style={{ padding: "12px" }}>{report.reporter?.username || "—"}</td>
              <td style={{ padding: "12px" }}>{new Date(report.created_at).toLocaleString()}</td>
              <td style={{ padding: "12px" }}>
                <button className="btn btn-ghost" type="button" onClick={() => onSelectReport(report)}>
                  Examiner
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ReportDrawer({ report, onClose }) {
  const update = useUpdateModerationReport(report?.id);
  const remove = useDeleteModerationReport();
  const [notes, setNotes] = useState(report?.resolution || "");
  const toast = useToast();

  if (!report) return null;

  const changeStatus = async (status) => {
    try {
      await update.mutateAsync({ status, resolution: notes });
      toast.success(status === "accepted" ? "Signalement accepté." : "Signalement rejeté.");
      onClose();
    } catch (err) {
      toast.error("Mise à jour impossible.");
    }
  };

  const deleteReport = async () => {
    if (!window.confirm("Supprimer ce signalement ?")) return;
    try {
      await remove.mutateAsync(report.id);
      toast.info("Signalement supprimé.");
      onClose();
    } catch (err) {
      toast.error("Suppression impossible.");
    }
  };

  return (
    <aside className="glass" style={{ padding: 24, display: "grid", gap: 16 }}>
      <header>
        <h2 style={{ margin: 0 }}>Signalement #{report.id}</h2>
        <p className="muted" style={{ margin: "4px 0 0" }}>
          {TYPE_LABELS[report.report_type] || report.report_type} — cible : {report.target_id}
        </p>
      </header>

      <section>
        <h3 style={{ marginBottom: 8 }}>Motif</h3>
        <p style={{ whiteSpace: "pre-wrap" }}>{report.reason}</p>
      </section>

      <section style={{ display: "grid", gap: 12 }}>
        <label className="grid" style={{ gap: 6 }}>
          <span>Notes / résolution</span>
          <textarea className="input-textarea" rows={4} value={notes} onChange={(e) => setNotes(e.target.value)} />
        </label>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          <button type="button" className="btn btn-primary" onClick={() => changeStatus("accepted")} disabled={update.isPending}>
            {update.isPending ? "Mise à jour…" : "Accepter"}
          </button>
          <button type="button" className="btn btn-ghost" onClick={() => changeStatus("rejected")} disabled={update.isPending}>
            Rejeter
          </button>
          <button type="button" className="btn btn-ghost" onClick={deleteReport} disabled={remove.isPending}>
            Supprimer
          </button>
        </div>
      </section>

      <section>
        <h3 style={{ marginBottom: 8 }}>Métadonnées</h3>
        <pre style={{ background: "rgba(255,255,255,0.05)", padding: 12, borderRadius: 12, overflowX: "auto" }}>
          {JSON.stringify(report.metadata || {}, null, 2)}
        </pre>
      </section>

      <button type="button" className="btn btn-ghost" onClick={onClose}>
        Fermer
      </button>
    </aside>
  );
}

function AuditLogList() {
  const { data, isLoading, isError } = useAuditLogs();

  if (isLoading) return <LoadingState message="Chargement des logs…" />;
  if (isError)
    return (
      <ErrorState
        message="Erreur de chargement des logs."
        action={<button className="btn btn-ghost" onClick={() => window.location.reload()}>Recharger</button>}
      />
    );
  if (!data || data.length === 0) return <EmptyState title="Aucun log" description="Les actions récentes apparaîtront ici." />;

  return (
    <div className="glass" style={{ padding: 16 }}>
      <h3 style={{ marginTop: 0 }}>Journal des actions</h3>
      <div style={{ display: "grid", gap: 12 }}>
        {data.map((log) => (
          <article key={log.id} className="glass" style={{ padding: 12 }}>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <strong>{log.action}</strong>
              <span className="muted">{new Date(log.created_at).toLocaleString()}</span>
            </div>
            <p className="muted" style={{ margin: "4px 0" }}>
              {log.actor?.username || "Système"} — {log.target_type} #{log.target_id || "—"}
            </p>
            {log.metadata && (
              <pre style={{ background: "rgba(255,255,255,0.05)", padding: 12, borderRadius: 10, overflowX: "auto" }}>
                {JSON.stringify(log.metadata, null, 2)}
              </pre>
            )}
          </article>
        ))}
      </div>
    </div>
  );
}

export default function AdminModerationPage() {
  const [selectedReport, setSelectedReport] = useState(null);

  const onSelectReport = (report) => {
    setSelectedReport(report);
  };

  const onCloseDrawer = () => {
    setSelectedReport(null);
  };

  return (
    <div className="page">
      <div className="container" style={{ display: "grid", gap: 24 }}>
        <header className="grid" style={{ gap: 12 }}>
          <span className="tag">Modération</span>
          <h1 className="heading-l">Tableau de bord</h1>
          <p className="lead">Gestion des signalements, suivi des décisions et journal d’audit.</p>
        </header>

        <div className="grid" style={{ gap: 24, gridTemplateColumns: "minmax(0, 2fr) minmax(0, 1fr)" }}>
          <div className="grid" style={{ gap: 16 }}>
            <ModerationTable onSelectReport={onSelectReport} />
            <AuditLogList />
          </div>
          <ReportDrawer report={selectedReport} onClose={onCloseDrawer} />
        </div>
      </div>
    </div>
  );
}
