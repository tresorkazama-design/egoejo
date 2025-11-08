import HeroSorgho from "../components/HeroSorgho.jsx";

export default function Home() {
  const btn = {
    background: "#111",
    color: "#fff",
    padding: "10px 16px",
    borderRadius: 8,
    textDecoration: "none",
    display: "inline-block",
    border: "none",
    cursor: "pointer"
  };

  const btnGhost = {
    ...btn,
    background: "transparent",
    color: "#111",
    outline: "1px solid #111"
  };

  return (
    <>
      <HeroSorgho />
      <section id="soutenir" style={{ padding: "40px 16px", maxWidth: 1200, margin: "0 auto" }}>
        <h2 style={{ margin: "0 0 12px" }}>Soutenir le projet</h2>
        <p>Deux options rapides : AdhÃ©sion/Don via Stripe, ou HelloAsso si vous Ãªtes en France (asso).</p>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
          <a href="/api/checkout-create" style={btn}>AdhÃ©rer / Donner (Stripe)</a>
          <a href="https://www.helloasso.com/associations" target="_blank" rel="noreferrer" style={btnGhost}>HelloAsso (externe)</a>
        </div>
      </section>
    </>
  );
}