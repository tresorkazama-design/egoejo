import { useEffect, useRef, useState } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

import { api } from "../config/api.js";

gsap.registerPlugin(ScrollTrigger);

const PROFILS = [
  { value: "je-decouvre", label: "Je découvre" },
  { value: "je-protege", label: "Je protège" },
  { value: "je-soutiens", label: "Je soutiens" },
];

export default function Rejoindre() {
  const [formData, setFormData] = useState({
    nom: "",
    email: "",
    profil: "",
    message: "",
    document_url: "",
    website: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const titleRef = useRef(null);
  const introRef = useRef(null);
  const formRef = useRef(null);

  useEffect(() => {
    const prefersReduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduce) return;

    const ctx = gsap.context(() => {
      if (titleRef.current) {
        gsap.from(titleRef.current, {
          y: 50,
          opacity: 0,
          duration: 0.8,
          ease: "power2.out",
        });
      }

      if (introRef.current) {
        gsap.from(introRef.current, {
          y: 30,
          opacity: 0,
          duration: 0.7,
          delay: 0.2,
          ease: "power2.out",
        });
      }

      if (formRef.current) {
        gsap.from(formRef.current.children, {
          y: 30,
          opacity: 0,
          stagger: 0.1,
          duration: 0.6,
          ease: "power2.out",
          scrollTrigger: {
            trigger: formRef.current,
            start: "top 80%",
            toggleActions: "play none none reverse",
          },
        });
      }
    });

    return () => ctx.revert();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    setError("");
  };

  const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess(false);

    if (!formData.nom.trim()) {
      setError("Le nom est requis");
      return;
    }
    if (!formData.email.trim()) {
      setError("L'email est requis");
      return;
    }
    if (!validateEmail(formData.email)) {
      setError("L'email n'est pas valide");
      return;
    }
    if (!formData.profil) {
      setError("Veuillez sélectionner un profil");
      return;
    }
    if (formData.message && formData.message.length > 2000) {
      setError("Le message ne peut pas dépasser 2000 caractères");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(api.rejoindre(), {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          nom: formData.nom.trim(),
          email: formData.email.trim(),
          profil: formData.profil,
          message: formData.message.trim() || null,
          document_url: formData.document_url.trim() || null,
          website: formData.website,
        }),
      });

      const data = await response.json();
      if (!response.ok || !data.ok) {
        throw new Error(data.error || "Erreur lors de l'envoi");
      }

      setSuccess(true);
      setFormData({
        nom: "",
        email: "",
        profil: "",
        message: "",
        document_url: "",
        website: "",
      });

      setTimeout(() => setSuccess(false), 5000);
    } catch (err) {
      setError(err.message || "Une erreur est survenue. Veuillez réessayer.");
    } finally {
      setLoading(false);
    }
  };

  const containerStyle = {
    maxWidth: "720px",
    margin: "0 auto",
    padding: "60px 6vw",
    fontFamily: "inherit",
    color: "#dffdf5",
  };

  const formStyle = {
    display: "flex",
    flexDirection: "column",
    gap: "1.2rem",
    background: "rgba(8,18,16,.6)",
    borderRadius: 18,
    padding: "28px 24px",
    boxShadow: "0 30px 60px -45px rgba(12,220,180,.45)",
    border: "1px solid rgba(116,255,215,.08)",
  };

  const inputStyle = {
    padding: "0.75rem 1rem",
    borderRadius: "10px",
    border: "1px solid rgba(255,255,255,.1)",
    background: "rgba(10,18,16,0.6)",
    color: "inherit",
    fontSize: "1rem",
    fontFamily: "inherit",
    transition: "border-color .25s ease, box-shadow .25s ease",
  };

  const textareaStyle = {
    ...inputStyle,
    minHeight: "140px",
    resize: "vertical",
  };

  const buttonStyle = {
    padding: "0.85rem 1.6rem",
    borderRadius: "12px",
    border: "none",
    background: loading
      ? "linear-gradient(135deg, rgba(117,255,214,.4), rgba(54,185,154,.3))"
      : "linear-gradient(135deg, #20f3a6, #12bfa5)",
    color: "#041310",
    fontSize: "1.05rem",
    fontWeight: 700,
    cursor: loading ? "not-allowed" : "pointer",
    opacity: loading ? 0.7 : 1,
    transition: "transform .25s ease, box-shadow .25s ease, opacity .25s ease",
    boxShadow: loading ? "none" : "0 22px 45px -20px rgba(20,220,170,.55)",
  };

  const alertStyle = (background, border, color) => ({
    padding: "0.9rem 1rem",
    borderRadius: "12px",
    background,
    color,
    border,
    fontWeight: 500,
  });

  const honeypotStyle = {
    position: "absolute",
    left: "-9999px",
    opacity: 0,
    pointerEvents: "none",
  };

  const labelStyle = {
    display: "block",
    marginBottom: "0.4rem",
    fontWeight: 600,
    color: "#bffbea",
  };

  return (
    <main className="section" data-animate style={containerStyle}>
      <div style={{ marginBottom: "2rem" }}>
        <h1 ref={titleRef} className="animated-title" style={{ fontSize: "2.5rem", marginBottom: "0.75rem" }}>
          Rejoindre EGOEJO
        </h1>
        <p ref={introRef} style={{ maxWidth: "54ch", color: "#b1eee0", lineHeight: 1.6 }}>
          Partagez votre intention de nous rejoindre. Nous reviendrons vers vous rapidement pour
          explorer les alliances possibles et imaginer ensemble de nouvelles manières d’habiter la
          Terre.
        </p>
      </div>

      {error && (
        <div role="alert" style={alertStyle("#330f11", "1px solid #ffb3b9", "#ff9aa2")}> {error} </div>
      )}

      {success && (
        <div role="status" style={alertStyle("#103321", "1px solid #98ffcc", "#8cf8c5")}>
          Merci ! Votre intention a été enregistrée. Nous vous recontacterons bientôt.
        </div>
      )}

      <form ref={formRef} onSubmit={handleSubmit} style={formStyle}>
        <input
          type="text"
          name="website"
          value={formData.website}
          onChange={handleChange}
          style={honeypotStyle}
          tabIndex="-1"
          autoComplete="off"
        />

        <div>
          <label htmlFor="nom" style={labelStyle}>
            Nom <span style={{ color: "#ff8585" }}>*</span>
          </label>
          <input
            type="text"
            id="nom"
            name="nom"
            value={formData.nom}
            onChange={handleChange}
            required
            style={inputStyle}
            disabled={loading}
          />
        </div>

        <div>
          <label htmlFor="email" style={labelStyle}>
            Email <span style={{ color: "#ff8585" }}>*</span>
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            style={inputStyle}
            disabled={loading}
          />
        </div>

        <div>
          <label htmlFor="profil" style={labelStyle}>
            Profil <span style={{ color: "#ff8585" }}>*</span>
          </label>
          <select
            id="profil"
            name="profil"
            value={formData.profil}
            onChange={handleChange}
            required
            style={inputStyle}
            disabled={loading}
          >
            <option value="">Sélectionnez un profil</option>
            {PROFILS.map((profil) => (
              <option key={profil.value} value={profil.value}>
                {profil.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="message" style={labelStyle}>
            Message (optionnel)
          </label>
          <textarea
            id="message"
            name="message"
            value={formData.message}
            onChange={handleChange}
            maxLength={2000}
            style={textareaStyle}
            disabled={loading}
            placeholder="Partagez vos motivations, vos compétences ou toute information pertinente..."
          />
          <div style={{ fontSize: "0.85rem", color: "#87d9cb", marginTop: "0.25rem" }}>
            {formData.message.length}/2000 caractères
          </div>
        </div>

        <div>
          <label htmlFor="document_url" style={labelStyle}>
            URL d'un document (optionnel)
          </label>
          <input
            type="url"
            id="document_url"
            name="document_url"
            value={formData.document_url}
            onChange={handleChange}
            style={inputStyle}
            disabled={loading}
            placeholder="https://..."
          />
        </div>

        <button
          type="submit"
          style={buttonStyle}
          disabled={loading}
          onMouseEnter={(e) => {
            if (!loading) {
              e.currentTarget.style.transform = "translateY(-3px)";
              e.currentTarget.style.boxShadow = "0 26px 55px -20px rgba(20,220,170,.65)";
            }
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = "translateY(0)";
            e.currentTarget.style.boxShadow = loading
              ? "none"
              : "0 22px 45px -20px rgba(20,220,170,.55)";
          }}
        >
          {loading ? "Envoi en cours..." : "Envoyer"}
        </button>
      </form>
    </main>
  );
}
