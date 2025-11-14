<<<<<<< HEAD:src/pages/Polls.jsx
import { useEffect, useRef, useState } from "react";
import {
  subscribePollUpdates,
  useCreatePoll,
  usePoll,
  usePollAction,
  usePolls,
  useVote,
} from "../features/polls/hooks/usePolls.js";
import { useToast } from "../shared/hooks/useToast.jsx";
import { LoadingState, EmptyState, ErrorState } from "../shared/components/Feedback.jsx";

function PollCard({ poll, onSelect }) {
  return (
    <article className="glass" style={{ padding: 16, display: "grid", gap: 8 }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h3 style={{ margin: 0 }}>{poll.title}</h3>
          <p className="muted" style={{ margin: "4px 0 0" }}>{poll.question}</p>
        </div>
        <span className="tag" style={{ background: "rgba(0,0,0,0.25)" }}>{poll.status}</span>
      </header>
      <p className="muted" style={{ margin: "4px 0 0" }}>Total votes : {poll.total_votes}</p>
      <button type="button" className="btn btn-primary" onClick={() => onSelect(poll.id)}>
        Voir le détail
      </button>
    </article>
  );
}

function PollList({ onSelect }) {
  const { data, isLoading, isError } = usePolls();

  if (isLoading) return <LoadingState message="Chargement des scrutins…" />;
  if (isError)
    return (
      <ErrorState
        message="Impossible de charger les scrutins."
        action={<button className="btn btn-ghost" onClick={() => window.location.reload()}>Recharger</button>}
      />
    );
  if (!data || data.length === 0)
    return <EmptyState title="Aucun scrutin" description="Crée un vote pour démarrer la prise de décision." />;

  return (
    <div className="grid" style={{ gap: 16 }}>
      {data.map((poll) => (
        <PollCard key={poll.id} poll={poll} onSelect={onSelect} />
      ))}
    </div>
  );
}

function PollDetail({ pollId }) {
  const { data, refetch } = usePoll(pollId, Boolean(pollId));
  const vote = useVote(pollId);
  const openPoll = usePollAction(pollId, "open");
  const closePoll = usePollAction(pollId, "close");
  const [selectedOptions, setSelectedOptions] = useState([]);
  const toast = useToast();
  const votesRef = useRef(null);
  const statusRef = useRef(null);

  useEffect(() => {
    votesRef.current = data?.total_votes ?? null;
    statusRef.current = data?.status ?? null;
  }, [data?.total_votes, data?.status]);

  useEffect(() => {
    if (!pollId) return () => {};
    const socket = subscribePollUpdates(pollId, (payload) => {
      const newVotes = payload?.total_votes ?? null;
      if (votesRef.current !== null && newVotes !== null && newVotes > votesRef.current) {
        const diff = newVotes - votesRef.current;
        toast.info(`${diff} nouveau(x) vote(s).`);
      }
      if (payload?.status && statusRef.current && payload.status !== statusRef.current) {
        if (payload.status === "open") {
          toast.info("Un scrutin vient de s'ouvrir." );
        } else if (payload.status === "closed") {
          toast.info("Un scrutin vient d'être clôturé." );
        }
      }
      votesRef.current = newVotes;
      statusRef.current = payload?.status ?? statusRef.current;
      refetch();
    });
    return () => socket.close();
  }, [pollId, refetch, toast]);

  useEffect(() => {
    if (data?.allow_multiple) return;
    setSelectedOptions((opts) => (opts.length > 1 ? [opts[0]] : opts));
  }, [data?.allow_multiple]);

  const onVote = async () => {
    if (!selectedOptions.length) return;
    try {
      await vote.mutateAsync({ options: selectedOptions });
      toast.success("Vote enregistré.");
      await refetch();
    } catch (err) {
      toast.error("Vote impossible.");
    }
  };

  const onCheckboxChange = (optionId) => {
    if (data.allow_multiple) {
      setSelectedOptions((current) =>
        current.includes(optionId)
          ? current.filter((id) => id !== optionId)
          : [...current, optionId]
      );
    } else {
      setSelectedOptions([optionId]);
    }
  };

  const isOpen = data?.status === "open";

  if (!data) return <EmptyState title="Aucun scrutin sélectionné" description="Choisis un scrutin pour consulter les détails." />;

  return (
    <div className="glass" style={{ padding: 24, display: "grid", gap: 16 }}>
      <header style={{ display: "grid", gap: 4 }}>
        <h2 style={{ margin: 0 }}>{data.title}</h2>
        <p className="muted" style={{ margin: 0 }}>{data.question}</p>
        <div className="muted" style={{ fontSize: "0.9rem" }}>
          Anonyme : {data.is_anonymous ? "oui" : "non"} · Votes multiples : {data.allow_multiple ? "oui" : "non"}
        </div>
      </header>

      <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: 12 }}>
        {data.options.map((option) => {
          const checked = selectedOptions.includes(option.id);
          return (
            <li key={option.id} className="glass" style={{ padding: 12 }}>
              <label style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 12 }}>
                <div style={{ display: "grid", gap: 4 }}>
                  <span style={{ fontWeight: 600 }}>{option.label}</span>
                  <span className="muted" style={{ fontSize: "0.85rem" }}>{option.votes} vote(s)</span>
                </div>
                <input
                  type={data.allow_multiple ? "checkbox" : "radio"}
                  checked={checked}
                  onChange={() => onCheckboxChange(option.id)}
                  name="poll-option"
                />
              </label>
            </li>
          );
        })}
      </ul>

      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        <button type="button" className="btn btn-primary" onClick={onVote} disabled={!selectedOptions.length || !isOpen || vote.isPending}>
          {vote.isPending ? "Vote en cours…" : "Voter"}
        </button>
        <button type="button" className="btn btn-ghost" onClick={() => refetch()}>
          Rafraîchir
        </button>
        {isOpen ? (
          <button
            type="button"
            className="btn btn-ghost"
            onClick={async () => {
              try {
                await closePoll.mutateAsync();
                toast.info("Scrutin clôturé.");
              } catch (err) {
                toast.error("Clôture impossible.");
              }
            }}
            disabled={closePoll.isPending}
          >
            {closePoll.isPending ? "Fermeture…" : "Clore"}
          </button>
        ) : (
          <button
            type="button"
            className="btn btn-ghost"
            onClick={async () => {
              try {
                await openPoll.mutateAsync();
                toast.info("Scrutin ouvert.");
              } catch (err) {
                toast.error("Ouverture impossible.");
              }
            }}
            disabled={openPoll.isPending}
          >
            {openPoll.isPending ? "Ouverture…" : "Ouvrir"}
          </button>
        )}
      </div>
    </div>
  );
}

function PollCreator({ onCreated }) {
  const createPoll = useCreatePoll();
  const [title, setTitle] = useState("");
  const [question, setQuestion] = useState("");
  const [options, setOptions] = useState(["", ""]);
  const [allowMultiple, setAllowMultiple] = useState(false);
  const [isAnonymous, setIsAnonymous] = useState(true);
  const toast = useToast();

  const canSubmit = title.trim() && question.trim() && options.every((opt) => opt.trim());

  const onSubmit = async (event) => {
    event.preventDefault();
    if (!canSubmit) return;
    try {
      await createPoll.mutateAsync({
        title,
        question,
        allow_multiple: allowMultiple,
        is_anonymous: isAnonymous,
        options: options.map((label, position) => ({ label, position })),
      });
      toast.success("Scrutin créé.");
      setTitle("");
      setQuestion("");
      setOptions(["", ""]);
      onCreated?.();
    } catch (err) {
      toast.error("Création impossible.");
    }
  };

  return (
    <form className="glass" style={{ padding: 16, display: "grid", gap: 12 }} onSubmit={onSubmit}>
      <h3 style={{ margin: 0 }}>Créer un scrutin</h3>
      <label className="grid" style={{ gap: 6 }}>
        <span>Titre</span>
        <input className="input-text" value={title} onChange={(e) => setTitle(e.target.value)} required />
      </label>
      <label className="grid" style={{ gap: 6 }}>
        <span>Question</span>
        <textarea className="input-textarea" rows={3} value={question} onChange={(e) => setQuestion(e.target.value)} required />
      </label>
      <fieldset className="grid" style={{ gap: 6, border: "none", padding: 0 }}>
        <legend style={{ fontWeight: 600 }}>Options</legend>
        {options.map((opt, index) => (
          <input
            key={index}
            className="input-text"
            placeholder={`Option #${index + 1}`}
            value={opt}
            onChange={(e) => {
              const next = [...options];
              next[index] = e.target.value;
              setOptions(next);
            }}
            required
          />
        ))}
        <button type="button" className="btn btn-ghost" onClick={() => setOptions((prev) => [...prev, ""])}>
          Ajouter une option
        </button>
      </fieldset>
      <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <input type="checkbox" checked={allowMultiple} onChange={(e) => setAllowMultiple(e.target.checked)} /> Votes multiples autorisés
      </label>
      <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <input type="checkbox" checked={isAnonymous} onChange={(e) => setIsAnonymous(e.target.checked)} /> Vote anonyme
      </label>
      <button type="submit" className="btn btn-primary" disabled={!canSubmit || createPoll.isPending}>
        {createPoll.isPending ? "Création…" : "Créer"}
      </button>
    </form>
  );
}

export default function PollsPage() {
  const [selectedPoll, setSelectedPoll] = useState(null);
  const { refetch } = usePolls();

  const onCreated = () => {
    refetch();
  };

  return (
    <div className="page">
      <div className="container" style={{ display: "grid", gap: 24 }}>
        <header className="grid" style={{ gap: 12 }}>
          <span className="tag">Votes</span>
          <h1 className="heading-l">Décider ensemble</h1>
          <p className="lead">Participe aux scrutins de la communauté et suis les résultats en direct.</p>
        </header>

        <div className="grid" style={{ gap: 24, gridTemplateColumns: "minmax(0, 1.5fr) minmax(0, 1fr)" }}>
          <div className="grid" style={{ gap: 16 }}>
            <PollList onSelect={setSelectedPoll} />
            <PollDetail pollId={selectedPoll} />
          </div>
          <PollCreator onCreated={onCreated} />
        </div>
=======
import { useEffect, useState } from "react";
import { api } from "../config/api.js";

export default function Polls() {
  const [polls, setPolls] = useState([]);
  const [pollsLoading, setPollsLoading] = useState(true);
  const [selectedId, setSelectedId] = useState(null);
  const [detail, setDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [selectedOption, setSelectedOption] = useState(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        setPollsLoading(true);
        const response = await fetch(api.polls());
        const data = await response.json();
        if (!cancelled) setPolls(Array.isArray(data) ? data : []);
      } catch (err) {
        if (!cancelled) setPolls([]);
      } finally {
        if (!cancelled) setPollsLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedId) {
      setDetail(null);
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        setDetailLoading(true);
        const response = await fetch(api.pollDetail(selectedId));
        const data = await response.json();
        if (!cancelled) {
          setDetail(data);
          setSelectedOption(data.options?.[0]?.id ?? null);
        }
      } catch (err) {
        if (!cancelled) setDetail(null);
      } finally {
        if (!cancelled) setDetailLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [selectedId]);

  const handleVote = async () => {
    if (!selectedId || !selectedOption) return;
    await fetch(api.pollVote(selectedId), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ options: [selectedOption] }),
    });
    const response = await fetch(api.pollDetail(selectedId));
    const data = await response.json();
    setDetail(data);
  };

  return (
    <div className="page" style={{ display: "grid", gap: 24 }}>
      <header className="container" style={{ display: "grid", gap: 12 }}>
        <span className="tag">Votes</span>
        <h1 className="heading-l">Décider ensemble</h1>
        <p className="lead">Consulte les scrutins en cours et apporte ta voix.</p>
      </header>

      <div className="container" style={{ display: "grid", gap: 24, gridTemplateColumns: "minmax(220px, 1fr) minmax(0, 2fr)" }}>
        <section className="glass" style={{ padding: 16, display: "grid", gap: 12 }}>
          <h2 style={{ margin: 0 }}>Scrutins</h2>
          {pollsLoading ? (
            <p className="muted">Chargement…</p>
          ) : polls.length === 0 ? (
            <p className="muted">Aucun scrutin pour le moment.</p>
          ) : (
            polls.map((poll) => (
              <button
                key={poll.id}
                type="button"
                className={`btn ${selectedId === poll.id ? "btn-primary" : "btn-ghost"}`}
                onClick={() => setSelectedId(poll.id)}
              >
                {poll.title}
              </button>
            ))
          )}
        </section>

        <section className="glass" style={{ padding: 16, display: "grid", gap: 12 }}>
          {detailLoading ? (
            <p className="muted">Chargement…</p>
          ) : !detail ? (
            <p className="muted">Sélectionne un scrutin pour voir le détail.</p>
          ) : (
            <>
              <h2 style={{ margin: 0 }}>{detail.title}</h2>
              <p className="muted" style={{ margin: 0 }}>{detail.question}</p>
              <form className="grid" style={{ gap: 12 }}>
                {detail.options?.map((option) => (
                  <label key={option.id} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <input
                      type="radio"
                      name="poll-option"
                      value={option.id}
                      checked={selectedOption === option.id}
                      onChange={() => setSelectedOption(option.id)}
                    />
                    <span>{option.label}</span>
                    <span className="muted">({option.votes} vote(s))</span>
                  </label>
                ))}
              </form>
              <button type="button" className="btn btn-primary" onClick={handleVote} disabled={!selectedOption}>
                Voter
              </button>
            </>
          )}
        </section>
>>>>>>> 154e1db72fc940dea87fbfb88c6ceeb01aac9d19:frontend/src/pages/Polls.jsx
      </div>
    </div>
  );
}
