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

  return (
    <main className="page page--form">
      <h1 ref={titleRef} className="heading-l">
        Rejoindre EGOEJO
      </h1>
      <p ref={introRef} className="lead" style={{ marginBottom: "2rem" }}>
        Partagez votre intention de rejoindre notre organisation. Nous vous recontacterons rapidement.
      </p>

      {error && (
        <div className="form-message form-message--error" role="alert">
          {error}
        </div>
      )}

      {success && (
        <div className="form-message form-message--success" role="alert">
          Merci ! Votre intention a été enregistrée avec succès. Nous vous recontacterons bientôt.
        </div>
      )}

      <form ref={formRef} onSubmit={handleSubmit} className="form-grid">
        <input
          type="text"
          name="website"
          value={formData.website}
          onChange={handleChange}
          className="honeypot-field"
          tabIndex="-1"
          autoComplete="off"
        />

        <div className="form-field">
          <label htmlFor="nom">
            Nom <span className="required">*</span>
          </label>
          <input
            type="text"
            id="nom"
            name="nom"
            value={formData.nom}
            onChange={handleChange}
            required
            className="input-text"
            disabled={loading}
          />
        </div>

        <div className="form-field">
          <label htmlFor="email">
            Email <span className="required">*</span>
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
            className="input-text"
            disabled={loading}
          />
        </div>

        <div className="form-field">
          <label htmlFor="profil">
            Profil <span className="required">*</span>
          </label>
          <select
            id="profil"
            name="profil"
            value={formData.profil}
            onChange={handleChange}
            required
            className="input-select"
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

        <div className="form-field">
          <label htmlFor="message">Message (optionnel)</label>
          <textarea
            id="message"
            name="message"
            value={formData.message}
            onChange={handleChange}
            maxLength={2000}
            className="input-textarea"
            disabled={loading}
            placeholder="Partagez vos motivations, vos compétences ou toute information pertinente..."
          />
          <div className="input-help">{formData.message.length}/2000 caractères</div>
        </div>

        <div className="form-field">
          <label htmlFor="document_url">URL d'un document (optionnel)</label>
          <input
            type="url"
            id="document_url"
            name="document_url"
            value={formData.document_url}
            onChange={handleChange}
            className="input-text"
            disabled={loading}
            placeholder="https://..."
          />
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? "Envoi en cours..." : "Envoyer"}
        </button>
      </form>
    </main>
  );
}

