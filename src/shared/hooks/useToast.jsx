import { createContext, useContext, useEffect, useMemo, useState } from "react";

const ToastContext = createContext(null);
let toastId = 0;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const api = useMemo(() => {
    const push = (toast) => {
      const id = ++toastId;
      setToasts((prev) => [...prev, { id, duration: 4500, ...toast }]);
      return id;
    };

    const remove = (id) => setToasts((prev) => prev.filter((entry) => entry.id !== id));

    const success = (message, options = {}) => push({ message, type: "success", ...options });
    const error = (message, options = {}) => push({ message, type: "error", ...options });
    const info = (message, options = {}) => push({ message, type: "info", ...options });

    return { push, remove, success, error, info };
  }, []);

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div
        id="toast-viewport"
        style={{
          position: "fixed",
          bottom: 20,
          right: 20,
          display: "grid",
          gap: 12,
          zIndex: 9999,
          maxWidth: "320px",
        }}
      >
        {toasts.map((toast) => (
          <ToastItem key={toast.id} toast={toast} onDismiss={api.remove} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

function ToastItem({ toast, onDismiss }) {
  const { id, message, type, duration } = toast;

  useEffect(() => {
    if (!duration) return undefined;
    const timer = setTimeout(() => onDismiss(id), duration);
    return () => clearTimeout(timer);
  }, [id, duration, onDismiss]);

  const colors = {
    success: { background: "rgba(20,180,120,0.12)", border: "1px solid rgba(20,180,120,0.4)" },
    error: { background: "rgba(220,50,80,0.15)", border: "1px solid rgba(220,50,80,0.45)" },
    info: { background: "rgba(80,120,220,0.15)", border: "1px solid rgba(80,120,220,0.35)" },
  };

  const style = {
    padding: "12px 16px",
    borderRadius: 12,
    backdropFilter: "blur(10px)",
    ...colors[type || "info"],
    boxShadow: "0 20px 40px -28px rgba(0,0,0,0.6)",
    color: "#f5f8fa",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: 12,
  };

  return (
    <div style={style} role="status">
      <span style={{ flex: 1 }}>{message}</span>
      <button
        type="button"
        onClick={() => onDismiss(id)}
        style={{
          background: "transparent",
          border: "none",
          color: "inherit",
          cursor: "pointer",
          fontSize: "1rem",
        }}
        aria-label="Fermer"
      >
        ×
      </button>
    </div>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast doit être utilisé dans ToastProvider");
  return ctx;
}

