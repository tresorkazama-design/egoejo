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
      </div>
    </div>
  );
}
