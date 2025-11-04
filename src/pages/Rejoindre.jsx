import React, { useState } from "react";
import { api } from "../config/api.js";

export default function Rejoindre() {
  const [nom, setNom] = useState("");
  const [email, setEmail] = useState("");
  const [profil, setProfil] = useState("je-protege");
  const [message, setMessage] = useState("");
  const [website, setWebsite] = useState("");
  const [sending, setSending] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setSending(true);

    try {
      const resp = await fetch(api.rejoindre(), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          nom,
          email,
          profil,
          message,
          website,
        }),
      });

      const data = await resp.json();

      if (!resp.ok || !data.ok) {
        alert(
          "Oups. Le message n'a pas pu être envoyé.\nTu peux réessayer plus tard."
        );
      } else {
        alert(
          "Merci. Ton intention est reçue.\nNous te recontacterons quand le cercle d'alliances sera ouvert publiquement."
        );

        // reset simple
        setNom("");
        setEmail("");
        setProfil("je-protege");
        setMessage("");
      }
    } catch (err) {
      console.error("Erreur envoi /rejoindre:", err);
      alert(
        "Erreur réseau. Si ça continue, écris-nous directement quand on publiera l'adresse de contact."
      );
    } finally {
      setSending(false);
    }
  }

  return (
    <main
      style={{
        color: "#dffdf5",
        backgroundColor: "#060b0a",
        padding: "clamp(2rem,2vw,3rem) 6vw",
        maxWidth: "1200px",
        margin: "0 auto",
        lineHeight: 1.5,
        fontFamily:
          "system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif",
      }}
    >
      {/* Intro */}
      <header style={{ maxWidth: "800px" }}>
        <h1
          style={{
            fontSize: "clamp(1.6rem,1vw,2rem)",
            lineHeight: 1.2,
            color: "#74ffd7",
            textShadow: "0 0 20px rgba(0,255,170,.4)",
            marginBottom: "1rem",
          }}
        >
          Rejoindre l'alliance vivante
        </h1>

        <p style={{ fontSize: "1rem", opacity: 0.9 }}>
          EGOEJO met en lien deux forces&nbsp;:
        </p>

        <ul
          style={{
            fontSize: "1rem",
            opacity: 0.9,
            lineHeight: 1.5,
            paddingLeft: "1rem",
          }}
        >
          <li style={{ marginBottom: ".75rem" }}>
            <strong style={{ color: "#dffdf5" }}>
              celles et ceux qui protègent déjà le vivant
            </strong>{" "}
            (gardiennes d'eau, paysan·ne·s qui sauvent les semences, sages-femmes,
            communautés qui tiennent encore un lien sacré avec la Terre…)
          </li>
          <li>
            <strong style={{ color: "#dffdf5" }}>
              celles et ceux qui veulent soutenir sans domination
            </strong>{" "}
            (alliés, finance éthique, gens prêts à s'engager vraiment).
          </li>
        </ul>

        <p style={{ fontSize: "1rem", opacity: 0.9 }}>
          Dis-nous qui tu es. On ne promet pas de « financement rapide ».
          On construit une relation vivante, pas une transaction.
        </p>
      </header>

      {/* Formulaire */}
      <section
        style={{
          marginTop: "2.5rem",
          maxWidth: "700px",
          background: "rgba(6,11,10,.6)",
          border: "1px solid rgba(255,255,255,.07)",
          borderRadius: "16px",
          boxShadow: "0 0 30px rgba(0,255,170,.12)",
          backdropFilter: "blur(6px)",
          padding: "1.5rem 1.5rem 1rem",
        }}
      >
        <h2
          style={{
            color: "#9bf6e5",
            fontSize: "1.1rem",
            margin: "0 0 1rem 0",
            textShadow: "0 0 10px rgba(0,255,170,.4)",
          }}
        >
          Parle-nous de toi
        </h2>

        <form
          onSubmit={handleSubmit}
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "1rem 1rem",
          }}
        >
          {/* Nom */}
          <div style={{ gridColumn: "span 1" }}>
            <label
              style={{
                fontSize: ".8rem",
                color: "#9bf6e5",
                display: "block",
                marginBottom: ".4rem",
              }}
            >
              Nom / Collectif
            </label>
            <input
              value={nom}
              onChange={(e) => setNom(e.target.value)}
              required
              style={{
                width: "100%",
                backgroundColor: "#000",
                border: "1px solid rgba(116,255,215,.4)",
                borderRadius: "8px",
                padding: ".6rem .75rem",
                color: "#dffdf5",
                fontSize: ".9rem",
                outline: "none",
              }}
              placeholder="ex: Collectif des Mères de la Source"
            />
          </div>

          {/* Email */}
          <div style={{ gridColumn: "span 1" }}>
            <label
              style={{
                fontSize: ".8rem",
                color: "#9bf6e5",
                display: "block",
                marginBottom: ".4rem",
              }}
            >
              Email de contact
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{
                width: "100%",
                backgroundColor: "#000",
                border: "1px solid rgba(116,255,215,.4)",
                borderRadius: "8px",
                padding: ".6rem .75rem",
                color: "#dffdf5",
                fontSize: ".9rem",
                outline: "none",
              }}
              placeholder="tu seras recontacté·e ici"
            />
          </div>

          {/* Profil */}
          <div style={{ gridColumn: "span 2" }}>
            <label
              style={{
                fontSize: ".8rem",
                color: "#9bf6e5",
                display: "block",
                marginBottom: ".4rem",
              }}
            >
              Je suis plutôt…
            </label>

            <select
              value={profil}
              onChange={(e) => setProfil(e.target.value)}
              style={{
                width: "100%",
                backgroundColor: "#000",
                border: "1px solid rgba(116,255,215,.4)",
                borderRadius: "8px",
                padding: ".6rem .75rem",
                color: "#dffdf5",
                fontSize: ".9rem",
                outline: "none",
              }}
            >
              <option value="je-protege">
                Je protège déjà un morceau de vivant / d'héritage
              </option>
              <option value="je-soutiens">
                Je veux soutenir sans dominer ni imposer
              </option>
              <option value="je-decouvre">
                Je découvre, je veux apprendre sans abîmer
              </option>
            </select>
          </div>

          {/* Message libre */}
          <div style={{ gridColumn: "span 2" }}>
            <label
              style={{
                fontSize: ".8rem",
                color: "#9bf6e5",
                display: "block",
                marginBottom: ".4rem",
              }}
            >
              Message / Besoin / Offre
            </label>
            <textarea
              rows={4}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              style={{
                width: "100%",
                backgroundColor: "#000",
                border: "1px solid rgba(116,255,215,.4)",
                borderRadius: "8px",
                padding: ".6rem .75rem",
                color: "#dffdf5",
                fontSize: ".9rem",
                outline: "none",
                resize: "vertical",
              }}
              placeholder="Dis-nous avec tes mots. (Exemples : «Je suis gardienne d'une source et on nous coupe l'accès à l'eau.» ou «Je peux financer des semences paysannes et je veux le faire proprement.»)"
            />
          </div>

          {/* Bouton submit */}
          <div style={{ gridColumn: "span 2", textAlign: "right" }}>
            <button
              type="submit"
              disabled={sending}
              style={{
                appearance: "none",
                background:
                  "linear-gradient(90deg,#00ffa3 0%,#008061 100%)",
                border: "0",
                borderRadius: "10px",
                padding: ".7rem 1rem",
                fontSize: ".9rem",
                fontWeight: 600,
                color: "#001710",
                boxShadow: "0 10px 30px rgba(0,255,170,.4)",
                cursor: "pointer",
                minWidth: "150px",
                opacity: sending ? 0.6 : 1,
              }}
            >
              {sending ? "Envoi..." : "Envoyer"}
            </button>
          </div>
          <input
            type="text"
            name="website"
            value={website}
            onChange={(e) => setWebsite(e.target.value)}
            style={{ display: "none" }}
            autoComplete="off"
            tabIndex="-1"
          />
        </form>
      </section>
    </main>
  );
}
