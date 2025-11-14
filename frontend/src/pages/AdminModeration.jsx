<<<<<<< HEAD:src/pages/AdminModeration.jsx
import { useState } from "react";

import {
  useAuditLogs,
  useModerationReports,
  useUpdateModerationReport,
  useDeleteModerationReport,
} from "../features/moderation/hooks/useModeration.js";
import { useToast } from "../shared/hooks/useToast.jsx";
import { LoadingState, EmptyState, ErrorState } from "../shared/components/Feedback.jsx";

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
        action={
          <button className="btn btn-ghost" onClick={() => window.location.reload()}>
            Recharger
          </button>
        }
      />
    );
  if (!data || data.length === 0) {
    return <EmptyState title="Aucun signalement" description="Les signalements apparaîtront ici." />;
  }

  return (
    <div className="glass" style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr className="muted" style={{ textAlign: "left" }}>
            <th style={{ padding: 12 }}>Type</th>
            <th style={{ padding: 12 }}>Cible</th>
            <th style={{ padding: 12 }}>Statut</th>
            <th style={{ padding: 12 }}>Reporter</th>
            <th style={{ padding: 12 }}>Créé le</th>
            <th style={{ padding: 12 }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {data.map((report) => (
            <tr key={report.id} style={{ borderTop: "1px solid rgba(255,255,255,0.08)" }}>
              <td style={{ padding: 12 }}>{TYPE_LABELS[report.report_type] || report.report_type}</td>
              <td style={{ padding: 12 }}>{report.target_id}</td>
              <td style={{ padding: 12 }}>
                <StatusBadge status={report.status} />
              </td>
              <td style={{ padding: 12 }}>{report.reporter?.username || "—"}</td>
              <td style={{ padding: 12 }}>{new Date(report.created_at).toLocaleString()}</td>
              <td style={{ padding: 12 }}>
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
    <aside className="glass" style={{ padding: 24, display: "grid", gap: 16, height: "100%" }}>
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
          <textarea className="input-textarea" rows={4} value={notes} onChange={(event) => setNotes(event.target.value)} />
        </label>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          <button
            type="button"
            className="btn btn-primary"
            onClick={() => changeStatus("accepted")}
            disabled={update.isPending}
          >
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
        action={
          <button className="btn btn-ghost" onClick={() => window.location.reload()}>
            Recharger
          </button>
        }
      />
    );
  if (!data || data.length === 0) {
    return <EmptyState title="Aucun log" description="Les actions récentes apparaîtront ici." />;
  }

  return (
    <div className="glass" style={{ padding: 16, display: "grid", gap: 12 }}>
      <h3 style={{ marginTop: 0 }}>Journal des actions</h3>
      {data.map((log) => (
        <article key={log.id} className="glass" style={{ padding: 12 }}>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "center" }}>
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
  );
}

export default function AdminModerationPage() {
  const [selectedReport, setSelectedReport] = useState(null);

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
            <ModerationTable onSelectReport={setSelectedReport} />
            <AuditLogList />
          </div>
          <ReportDrawer report={selectedReport} onClose={() => setSelectedReport(null)} />
        </div>
=======
﻿export default function AdminModerationPage() {
  return (
    <div className="page">
      <div className="container" style={{ display: "grid", gap: 32 }}>
        <header className="grid" style={{ gap: 12 }}>
          <span className="tag">ModÃ©ration</span>
          <h1 className="heading-l">Surveillance & Journal</h1>
          <p className="lead">
            Cette page servira de tableau de bord pour gÃ©rer les signalements, les audits et les actions de
            modÃ©ration.
          </p>
        </header>

        <section className="glass" style={{ padding: 24 }}>
          <h2 style={{ marginTop: 0 }}>Signalements rÃ©cents</h2>
          <p className="muted">
            En attente dâ€™implÃ©mentation. Ici sâ€™afficheront les signalements en cours avec les dÃ©tails nÃ©cessaires
            pour les traiter.
          </p>
        </section>

        <section className="glass" style={{ padding: 24 }}>
          <h2 style={{ marginTop: 0 }}>Historique des actions</h2>
          <p className="muted">
            En attente dâ€™implÃ©mentation. Cette section listera les actions effectuÃ©es par lâ€™Ã©quipe de modÃ©ration
            pour assurer la traÃ§abilitÃ©.
          </p>
        </section>
>>>>>>> 154e1db72fc940dea87fbfb88c6ceeb01aac9d19:frontend/src/pages/AdminModeration.jsx
      </div>
    </div>
  );
}
