import { useEffect, useState } from "react";
import { api } from "../config/api.js";

export default function Community() {
  const [threads, setThreads] = useState([]);
  const [threadsLoading, setThreadsLoading] = useState(true);
  const [selectedId, setSelectedId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [messagesLoading, setMessagesLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        setThreadsLoading(true);
        const response = await fetch(api.chatThreads());
        const data = await response.json();
        if (!cancelled) {
          setThreads(Array.isArray(data) ? data : []);
        }
      } catch (err) {
        if (!cancelled) setThreads([]);
      } finally {
        if (!cancelled) setThreadsLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    let cancelled = false;
    (async () => {
      try {
        setMessagesLoading(true);
        const response = await fetch(api.chatMessages(selectedId));
        const data = await response.json();
        if (!cancelled) {
          setMessages(Array.isArray(data) ? data : []);
        }
      } catch (err) {
        if (!cancelled) setMessages([]);
      } finally {
        if (!cancelled) setMessagesLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [selectedId]);

  return (
    <div className="page" style={{ display: "grid", gap: 24 }}>
      <header className="container" style={{ display: "grid", gap: 12 }}>
        <span className="tag">Messagerie</span>
        <h1 className="heading-l">Echanges en temps réel</h1>
        <p className="lead">
          Retrouve les derniers messages des membres de l'alliance.
        </p>
      </header>

      <div className="container" style={{ display: "grid", gap: 24, gridTemplateColumns: "minmax(220px, 1fr) minmax(0, 2fr)" }}>
        <section className="glass" style={{ padding: 16, display: "grid", gap: 12 }}>
          <h2 style={{ margin: 0 }}>Fils de discussion</h2>
          {threadsLoading ? (
            <p className="muted">Chargement…</p>
          ) : threads.length === 0 ? (
            <p className="muted">Aucun fil disponible.</p>
          ) : (
            threads.map((thread) => (
              <button
                key={thread.id}
                type="button"
                className={`btn ${selectedId === thread.id ? "btn-primary" : "btn-ghost"}`}
                onClick={() => setSelectedId(thread.id)}
              >
                {thread.title || `Fil #${thread.id}`}
              </button>
            ))
          )}
        </section>

        <section className="glass" style={{ padding: 16, minHeight: 220, display: "grid", gap: 12 }}>
          {messagesLoading ? (
            <p className="muted">Chargement…</p>
          ) : !selectedId ? (
            <p className="muted">Sélectionne un fil pour voir les messages.</p>
          ) : messages.length === 0 ? (
            <p className="muted">Aucun message pour ce fil.</p>
          ) : (
            messages.map((message) => (
              <article key={message.id} className="glass" style={{ padding: 12 }}>
                <header style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                  <strong>{message.author?.username || "Anonyme"}</strong>
                  <time className="muted" dateTime={message.created_at}>{new Date(message.created_at).toLocaleString()}</time>
                </header>
                <p style={{ margin: 0 }}>{message.content}</p>
              </article>
            ))
          )}
        </section>
      </div>
    </div>
  );
}
