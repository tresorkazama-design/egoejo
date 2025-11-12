export default function AdminModerationPage() {
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
      </div>
    </div>
  );
}
