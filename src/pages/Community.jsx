import { useEffect, useMemo, useRef, useState } from "react";
import {
  useChatThreads,
  useChatThread,
  useChatMessages,
  useCreateThread,
  useSendMessage,
} from "../features/community/hooks/useChat.js";
import { createWebSocket } from "../utils/realtime.js";
import { api } from "../config/api.js";
import { useToast } from "../shared/hooks/useToast.jsx";
import { LoadingState, EmptyState, ErrorState } from "../shared/components/Feedback.jsx";

function ThreadList({ selectedId, onSelect }) {
  const { data, isLoading, isError } = useChatThreads();

  if (isLoading) return <LoadingState message="Chargement des fils…" />;
  if (isError)
    return (
      <ErrorState
        message="Impossible de charger les fils."
        action={<button className="btn btn-ghost" onClick={() => window.location.reload()}>Recharger</button>}
      />
    );
  if (!data || data.length === 0)
    return <EmptyState title="Aucun fil" description="Crée un nouveau fil pour démarrer une conversation." />;

  return (
    <div className="glass" style={{ padding: 16, display: "grid", gap: 12 }}>
      {data.map((thread) => (
        <button
          key={thread.id}
          type="button"
          onClick={() => onSelect(thread.id)}
          className={`btn ${selectedId === thread.id ? "btn-primary" : "btn-ghost"}`}
          style={{ justifyContent: "flex-start" }}
        >
          <div>
            <div style={{ fontWeight: 600 }}>{thread.title || `Fil #${thread.id}`}</div>
            <div className="muted" style={{ fontSize: "0.85rem" }}>
              {thread.participants?.map((p) => p.username).join(", ")}
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}

function MessageList({ threadId }) {
  const { data, isLoading, isError, refetch } = useChatMessages(threadId, Boolean(threadId));
  const messagesEndRef = useRef(null);

  useEffect(() => {
    const el = messagesEndRef.current;
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  }, [data?.length]);

  if (!threadId) {
    return <EmptyState title="Aucun fil sélectionné" description="Choisis un fil à gauche pour voir la discussion." />;
  }

  if (isLoading) return <LoadingState message="Chargement des messages…" />;
  if (isError)
    return (
      <ErrorState
        message="Impossible de charger les messages."
        action={<button className="btn btn-ghost" onClick={() => refetch()}>Réessayer</button>}
      />
    );

  if (!data || data.length === 0) {
    return <EmptyState title="Aucun message" description="Lance la discussion !" />;
  }

  return (
    <div className="glass" style={{ padding: 16, display: "grid", gap: 12, maxHeight: "60vh", overflowY: "auto" }}>
      {data.map((msg) => (
        <article key={msg.id} className="glass" style={{ padding: 12 }}>
          <header style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
            <strong>{msg.author?.username || "Moi"}</strong>
            <time className="muted" dateTime={msg.created_at}>
              {new Date(msg.created_at).toLocaleString()}
            </time>
          </header>
          <p style={{ margin: 0 }}>{msg.content}</p>
        </article>
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
}

function Composer({ threadId }) {
  const [value, setValue] = useState("");
  const sendMessage = useSendMessage(threadId);
  const toast = useToast();

  const onSubmit = async (event) => {
    event.preventDefault();
    if (!value.trim()) return;
    try {
      await sendMessage.mutateAsync({ content: value });
      setValue("");
    } catch (err) {
      toast.error("Envoi impossible. Réessaie plus tard.");
    }
  };

  if (!threadId) return null;

  return (
    <form onSubmit={onSubmit} className="glass" style={{ padding: 16, display: "grid", gap: 12 }}>
      <textarea
        value={value}
        onChange={(event) => setValue(event.target.value)}
        className="input-textarea"
        rows={3}
        placeholder="Ecris ton message…"
        required
        disabled={sendMessage.isPending}
      />
      <button type="submit" className="btn btn-primary" disabled={sendMessage.isPending}>
        {sendMessage.isPending ? "Envoi…" : "Envoyer"}
      </button>
    </form>
  );
}

function RealtimeBridge({ threadId }) {
  const query = useChatMessages(threadId, Boolean(threadId));
  const wsRef = useRef(null);
  const toast = useToast();

  useEffect(() => {
    if (!threadId) return () => {};
    const url = api.wsChat(threadId);
    const socket = createWebSocket(url, {
      onMessage: ({ type, payload }) => {
        if (type === "chat_message") {
          query.refetch();
          if (payload?.author?.username) {
            const preview = payload.content?.slice(0, 80) || "Nouveau message";
            toast.info(`${payload.author.username} : ${preview}`);
          }
        }
      },
    });
    wsRef.current = socket;
    return () => socket.close();
  }, [threadId, query, toast]);

  return null;
}

export default function CommunityPage() {
  const [selectedThread, setSelectedThread] = useState(null);
  const createThread = useCreateThread();
  const { data: threadDetail } = useChatThread(selectedThread, Boolean(selectedThread));
  const toast = useToast();

  const onCreateThread = async () => {
    const title = window.prompt("Titre du fil ?");
    if (!title) return;
    try {
      await createThread.mutateAsync({ title });
      toast.success("Fil créé avec succès.");
    } catch (err) {
      toast.error("Création impossible.");
    }
  };

  const sortedParticipants = useMemo(() => {
    return threadDetail?.participants?.map((p) => p.username).join(", ") || "";
  }, [threadDetail]);

  return (
    <div className="page">
      <div className="container" style={{ display: "grid", gap: 24 }}>
        <header className="grid" style={{ gap: 12 }}>
          <span className="tag">Messagerie</span>
          <h1 className="heading-l">Echanges en temps réel</h1>
          <p className="lead">
            Discute avec les membres de la communauté et co-construis vos projets.
          </p>
        </header>

        <div className="grid" style={{ gap: 24, gridTemplateColumns: "minmax(220px, 1fr) minmax(0, 2fr)" }}>
          <div style={{ display: "grid", gap: 12 }}>
            <button type="button" className="btn btn-primary" onClick={onCreateThread} disabled={createThread.isPending}>
              {createThread.isPending ? "Création…" : "Nouveau fil"}
            </button>
            <ThreadList selectedId={selectedThread} onSelect={setSelectedThread} />
          </div>

          <div style={{ display: "grid", gap: 16 }}>
            {selectedThread && (
              <div className="glass" style={{ padding: 16 }}>
                <h2 style={{ margin: 0 }}>{threadDetail?.title || `Fil #${selectedThread}`}</h2>
                {sortedParticipants && (
                  <p className="muted" style={{ margin: "6px 0 0" }}>
                    Participants : {sortedParticipants}
                  </p>
                )}
              </div>
            )}
            <MessageList threadId={selectedThread} />
            <Composer threadId={selectedThread} />
          </div>
        </div>
      </div>
      <RealtimeBridge threadId={selectedThread} />
    </div>
  );
}
