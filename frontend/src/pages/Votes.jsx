import { useEffect, useMemo, useRef, useState } from "react";
import { usePolls, usePoll, useCreatePoll, usePollAction, useVote } from "../features/polls/hooks/usePolls.js";
import { api } from "../config/api.js";
import { createWebSocket } from "../utils/realtime.js";

function PollList({ onSelect, selected }) {
  const { data, isLoading, isError } = usePolls();

  if (isLoading) return <div className="glass" style={{ padding: 16 }}>Chargement…</div>;
  if (isError) return <div className="glass" style={{ padding: 16 }}>Impossible de charger les scrutins.</div>;
  if (!data || data.length === 0) return <div className="glass" style={{ padding: 16 }}>Aucun scrutin disponible.</div>;

  return (
    <div className="glass" style={{ padding: 16, display: "grid", gap: 12 }}>
      {data.map((poll) => (
        <button
          key={poll.id}
          type="button"
          onClick={() => onSelect(poll.id)}
          className={`btn ${selected === poll.id ? "btn-primary" : "btn-ghost"}`}
          style={{ justifyContent: "flex-start" }}
        >
          <div>
            <div style={{ fontWeight: 600 }}>{poll.title}</div>
            <div className="muted" style={{ fontSize: "0.85rem" }}>
              {poll.status.toUpperCase()} • {poll.total_votes} votes
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}

function PollDetail({ pollId }) {
  const { data, isLoading } = usePoll(pollId, Boolean(pollId));

  if (!pollId) {
    return <div className="glass" style={{ padding: 16 }}>Sélectionne un scrutin pour afficher le détail.</div>;
  }

  if (isLoading) {
    return <div className="glass" style={{ padding: 16 }}>Chargement du scrutin…</div>;
  }

  if (!data) {
    return <div className="glass" style={{ padding: 16 }}>Scrutin introuvable.</div>;
  }

  return (
    <div className="glass" style={{ padding: 16, display: "grid", gap: 16 }}>
      <header>
        <h2 style={{ margin: 0 }}>{data.title}</h2>
        <p className="muted" style={{ margin: "6px 0" }}>{data.question}</p>
        {data.description && <p style={{ margin: 0 }}>{data.description}</p>}
      </header>
      <ul style={{ listStyle: "none", padding: 0, display: "grid", gap: 12 }}>
        {data.options?.map((option) => (
          <li key={option.id} className="glass" style={{ padding: 12 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span>{option.label}</span>
              <span className="muted">{option.votes} voix</span>
            </div>
            <div
              style={{
                marginTop: 8,
                height: 6,
                borderRadius: 999,
                background: "rgba(255,255,255,0.1)",
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  width: data.total_votes > 0 ? `${Math.round((option.votes / data.total_votes) * 100)}%` : "0%",
                  height: "100%",
                  background: "var(--accent)",
                }}
              />
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}

function PollActions({ pollId, poll }) {
  const openPoll = usePollAction(pollId, "open");
  const closePoll = usePollAction(pollId, "close");
  const vote = useVote(pollId);
  const [selectedOptions, setSelectedOptions] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    setSelectedOptions([]);
    setError("");
  }, [pollId]);

  if (!pollId || !poll) return null;

  const toggleOption = (optionId) => {
    setSelectedOptions((prev) => {
      if (poll.allow_multiple) {
        return prev.includes(optionId) ? prev.filter((id) => id !== optionId) : [...prev, optionId];
      }
      return [optionId];
    });
  };

  const handleVote = async () => {
    setError("");
    if (selectedOptions.length === 0) {
      setError("Sélectionne au moins une option.");
      return;
    }
    try {
      await vote.mutateAsync({ options: selectedOptions });
    } catch (err) {
      setError(err.message || "Impossible d’enregistrer ton vote.");
    }
  };

  return (
    <div className="glass" style={{ padding: 16, display: "grid", gap: 12 }}>
      <h3 style={{ margin: 0 }}>Actions</h3>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
        <button type="button" className="btn btn-ghost" onClick={() => openPoll.mutate()} disabled={openPoll.isPending}>
          Ouvrir
        </button>
        <button type="button" className="btn btn-ghost" onClick={() => closePoll.mutate()} disabled={closePoll.isPending}>
          Clore
        </button>
      </div>
      <div>
        <h4 style={{ margin: "12px 0" }}>Voter</h4>
        <div style={{ display: "grid", gap: 8 }}>
          {poll.options?.map((option) => (
            <label key={option.id} className="glass" style={{ padding: 10, display: "flex", gap: 8 }}>
              <input
                type={poll.allow_multiple ? "checkbox" : "radio"}
                name="poll-option"
                value={option.id}
                checked={selectedOptions.includes(option.id)}
                onChange={() => toggleOption(option.id)}
              />
              <span>{option.label}</span>
            </label>
          ))}
        </div>
        {error && (
          <div className="form-message form-message--error" style={{ marginTop: 8 }}>
            {error}
          </div>
        )}
        <button
          type="button"
          className="btn btn-primary"
          style={{ marginTop: 12 }}
          onClick={handleVote}
          disabled={vote.isPending}
        >
          {vote.isPending ? "Vote en cours…" : "Envoyer mon vote"}
        </button>
      </div>
    </div>
  );
}

function RealtimeBridge({ pollId }) {
  const pollQuery = usePoll(pollId, Boolean(pollId));
  const wsRef = useRef(null);

  useEffect(() => {
    if (!pollId) return () => {};
    const socket = createWebSocket(api.wsPoll(pollId), {
      onMessage: ({ type }) => {
        if (type === "poll_update") {
          pollQuery.refetch();
        }
      },
    });
    wsRef.current = socket;
    return () => socket.close();
  }, [pollId, pollQuery]);

  return null;
}

function CreatePoll() {
  const createPoll = useCreatePoll();
  const [isOpen, setIsOpen] = useState(false);
  const [form, setForm] = useState({
    title: "",
    question: "",
    description: "",
    allow_multiple: false,
    is_anonymous: true,
    options: ["", ""],
  });

  const onChange = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const updateOption = (index, value) => {
    setForm((prev) => {
      const options = [...prev.options];
      options[index] = value;
      return { ...prev, options };
    });
  };

  const addOption = () => {
    setForm((prev) => ({ ...prev, options: [...prev.options, ""] }));
  };

  const onSubmit = async (event) => {
    event.preventDefault();
    const options = form.options.filter((opt) => opt.trim());
    if (!form.title.trim() || !form.question.trim() || options.length < 2) {
      return;
    }
    await createPoll.mutateAsync({
      title: form.title.trim(),
      question: form.question.trim(),
      description: form.description.trim(),
      allow_multiple: form.allow_multiple,
      is_anonymous: form.is_anonymous,
      options: options.map((label) => ({ label })),
    });
    setForm({
      title: "",
      question: "",
      description: "",
      allow_multiple: false,
      is_anonymous: true,
      options: ["", ""],
    });
    setIsOpen(false);
  };

  return (
    <div className="glass" style={{ padding: 16 }}>
      <button type="button" className="btn btn-primary" onClick={() => setIsOpen((prev) => !prev)}>
        {isOpen ? "Fermer" : "Nouveau scrutin"}
      </button>
      {isOpen && (
        <form onSubmit={onSubmit} style={{ marginTop: 16, display: "grid", gap: 12 }}>
          <label className="grid" style={{ gap: 4 }}>
            <span>Titre</span>
            <input
              type="text"
              className="input-text"
              value={form.title}
              onChange={(event) => onChange("title", event.target.value)}
              required
            />
          </label>
          <label className="grid" style={{ gap: 4 }}>
            <span>Question</span>
            <textarea
              className="input-textarea"
              rows={3}
              value={form.question}
              onChange={(event) => onChange("question", event.target.value)}
              required
            />
          </label>
          <label className="grid" style={{ gap: 4 }}>
            <span>Description</span>
            <textarea
              className="input-textarea"
              rows={3}
              value={form.description}
              onChange={(event) => onChange("description", event.target.value)}
            />
          </label>
          <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <input
              type="checkbox"
              checked={form.allow_multiple}
              onChange={(event) => onChange("allow_multiple", event.target.checked)}
            />
            <span>Autoriser plusieurs choix</span>
          </label>
          <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <input
              type="checkbox"
              checked={form.is_anonymous}
              onChange={(event) => onChange("is_anonymous", event.target.checked)}
            />
            <span>Vote anonyme</span>
          </label>
          <div style={{ display: "grid", gap: 6 }}>
            <span>Options</span>
            {form.options.map((value, idx) => (
              <input
                key={idx}
                type="text"
                className="input-text"
                value={value}
                placeholder={`Option ${idx + 1}`}
                onChange={(event) => updateOption(idx, event.target.value)}
                required={idx < 2}
              />
            ))}
            <button type="button" className="btn btn-ghost" onClick={addOption}>
              Ajouter une option
            </button>
          </div>
          <button type="submit" className="btn btn-primary" disabled={createPoll.isPending}>
            {createPoll.isPending ? "Création…" : "Créer"}
          </button>
        </form>
      )}
    </div>
  );
}

export default function VotesPage() {
  const [selected, setSelected] = useState(null);
  const { data: poll } = usePoll(selected, Boolean(selected));

  return (
    <div className="page">
      <div className="container" style={{ display: "grid", gap: 24 }}>
        <header className="grid" style={{ gap: 12 }}>
          <span className="tag">Votes</span>
          <h1 className="heading-l">Décider ensemble</h1>
          <p className="lead">
            Lance des scrutins, vote anonymement et suis les résultats en direct.
          </p>
        </header>

        <CreatePoll />

        <div className="grid" style={{ gap: 24, gridTemplateColumns: "minmax(240px, 1fr) minmax(0, 2fr)" }}>
          <PollList selected={selected} onSelect={setSelected} />
          <div style={{ display: "grid", gap: 16 }}>
            <PollDetail pollId={selected} />
            <PollActions pollId={selected} poll={poll} />
          </div>
        </div>
      </div>
      <RealtimeBridge pollId={selected} />
    </div>
  );
}
