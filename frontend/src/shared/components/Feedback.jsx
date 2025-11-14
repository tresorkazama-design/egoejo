const spinnerStyle = {
  width: 26,
  height: 26,
  border: "3px solid rgba(255,255,255,0.2)",
  borderTopColor: "#74ffd7",
  borderRadius: "50%",
  animation: "spin 1s linear infinite",
};

export function LoadingState({ message = "Chargement…" }) {
  return (
    <div className="glass" style={{ padding: 20, display: "flex", alignItems: "center", gap: 12 }}>
      <div style={spinnerStyle} />
      <span>{message}</span>
    </div>
  );
}

export function EmptyState({ title = "Aucun élément", description }) {
  return (
    <div className="glass" style={{ padding: 24, display: "grid", gap: 6 }}>
      <strong>{title}</strong>
      {description && <p className="muted" style={{ margin: 0 }}>{description}</p>}
    </div>
  );
}

export function ErrorState({ message = "Une erreur est survenue.", action }) {
  return (
    <div className="glass" style={{ padding: 24, display: "grid", gap: 12 }}>
      <strong style={{ color: "#ff7385" }}>{message}</strong>
      {action}
    </div>
  );
}

export function withFeedbackStyles() {
  const style = document.createElement("style");
  style.innerHTML = `
    @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
  `;
  document.head.appendChild(style);
}

