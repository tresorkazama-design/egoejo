import { useEffect, useRef, useState } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

import { api } from "../config/api.js";

const PROFILS = [
  { value: "je-decouvre", label: "Je decouvre" },
  { value: "je-protege", label: "Je protege" },
  { value: "je-soutiens", label: "Je soutiens" },
];

const PROJECT_TEMPLATE = `Titre du projet :
Objectifs principaux :
Publics touches :
Ressources disponibles :
Ressources recherchees :
Impacts esperes :
`;

const PROJECT_GUIDELINES = [
  "Precisez le contexte et les personnes impliquees (collectifs, territoires, partenaires).",
  "Indiquez les besoins materiels ou financiers si vous en avez identifies.",
  "Ajoutez des liens vers des supports en ligne ou des pieces jointes pour illustrer votre projet.",
  "Mentionnez vos disponibilites ou les dates clefs si vous avez un calendrier en tete.",
];

const ACCEPTED_FILE_TYPES = "application/pdf,image/*,video/*";
const MAX_PROJECT_FILES = 3;

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
  const [projectBrief, setProjectBrief] = useState(PROJECT_TEMPLATE);
  const [projectLinks, setProjectLinks] = useState("");
  const [projectFiles, setProjectFiles] = useState([]);
  const [fileError, setFileError] = useState("");

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

  const handleProjectFiles = async (event) => {
    const files = Array.from(event.target.files || []);
    if (!files.length) return;

    const availableSlots = MAX_PROJECT_FILES - projectFiles.length;
    if (availableSlots <= 0) {
      setFileError(`Vous pouvez ajouter jusqu'a ${MAX_PROJECT_FILES} fichiers.`);
      event.target.value = "";
      return;
    }

    const selected = files.slice(0, availableSlots);
    try {
      const encoded = await Promise.all(
        selected.map(
          (file) =>
            new Promise((resolve, reject) => {
              const reader = new FileReader();
              reader.onload = () => {
                resolve({
                  id: `${file.name}-${Date.now()}-${Math.random().toString(16).slice(2)}`,
                  name: file.name,
                  type: file.type,
                  size: file.size,
                  dataUrl: reader.result,
                });
              };
              reader.onerror = () => reject(new Error("Lecture du fichier impossible."));
              reader.readAsDataURL(file);
            })
        )
      );
      setProjectFiles((prev) => [...prev, ...encoded]);
      setFileError("");
    } catch (err) {
      setFileError(err.message || "Impossible d'ajouter ce fichier.");
    } finally {
      event.target.value = "";
    }
  };

  const handleRemoveProjectFile = (id) => {
    setProjectFiles((prev) => prev.filter((file) => file.id !== id));
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
          project_brief: projectBrief.trim() || null,
          project_links: projectLinks.trim() || null,
          project_files: projectFiles.map(({ name, type, size, dataUrl }) => ({
            name,
            type,
            size,
            data_url: dataUrl,
          })),
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
      setProjectBrief(PROJECT_TEMPLATE);
      setProjectLinks("");
      setProjectFiles([]);
      setFileError("");

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
        Partagez votre intention de rejoindre notre organisation. Racontez-nous qui vous etes, ce qui vous anime et, si
        vous le souhaitez, decrivez un projet ou une idee que vous aimeriez porter avec EGOEJO.
      </p>

      <section className="glass" style={{ marginBottom: "32px", padding: "24px", display: "grid", gap: "12px" }}>
        <h2 className="heading-l" style={{ margin: 0, fontSize: "clamp(1.3rem, 2.5vw, 1.8rem)" }}>
          Comment nous aider a comprendre votre elan
        </h2>
        <p className="muted" style={{ margin: 0 }}>
          Quelques pistes pour nous transmettre les informations utiles. Vous pouvez vous en inspirer librement ou
          utiliser l'espace de redaction pre-rempli plus bas.
        </p>
        <ul className="muted" style={{ margin: 0, paddingLeft: 20, display: "grid", gap: 6 }}>
          <li>Qui etes-vous et quelles sont vos motivations principales ?</li>
          <li>Quel lien souhaitez-vous tisser avec EGOEJO (apprendre, transmettre, co-construire...)?</li>
          <li>Quels savoirs, experiences ou ressources souhaitez-vous partager ?</li>
          <li>Y a-t-il un projet concret que vous aimeriez decrire ou documenter ?</li>
        </ul>
      </section>

      <div aria-live="assertive" style={{ minHeight: error ? "auto" : 0 }}>
        {error && (
          <div className="form-message form-message--error" role="alert" data-testid="intent-error">
          {error}
          </div>
        )}
      </div>

      {success && (
        <div className="form-message form-message--success" role="alert">
          Merci ! Votre intention a été enregistrée avec succès. Nous vous recontacterons bientôt.
        </div>
      )}

      <form ref={formRef} onSubmit={handleSubmit} noValidate className="form-grid">
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

        <section
          className="glass"
          style={{ gridColumn: "1 / -1", padding: "24px", display: "grid", gap: "16px" }}
        >
          <h2 className="heading-l" style={{ margin: 0, fontSize: "clamp(1.3rem, 2.5vw, 1.8rem)" }}>
            Partager un projet
          </h2>
          <p className="muted" style={{ margin: 0 }}>
            Ajoutez un resume, des liens ou des fichiers (PDF, images ou videos) pour presenter votre projet ou une idee en cours de maturation.
          </p>

          <div className="form-field" style={{ margin: 0 }}>
            <label>Quelques reperes</label>
            <ul className="muted" style={{ margin: 0, paddingLeft: 20, display: "grid", gap: 6 }}>
              {PROJECT_GUIDELINES.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          </div>

          <div className="form-field" style={{ margin: 0 }}>
            <label htmlFor="project_brief">Espace de redaction (pre-rempli)</label>
            <textarea
              id="project_brief"
              name="project_brief"
              value={projectBrief}
              onChange={(event) => setProjectBrief(event.target.value)}
              className="input-textarea"
              rows={8}
              disabled={loading}
            />
          </div>

          <div className="form-field" style={{ margin: 0 }}>
            <label htmlFor="project_links">
              Liens vers des ressources (drive, portfolio, video...) <span className="muted">(optionnel)</span>
            </label>
            <textarea
              id="project_links"
              name="project_links"
              value={projectLinks}
              onChange={(event) => setProjectLinks(event.target.value)}
              className="input-textarea"
              rows={4}
              placeholder="https://exemple.com/mon-projet"
              disabled={loading}
            />
          </div>

          <div className="form-field" style={{ margin: 0 }}>
            <label htmlFor="project_files">
              Ajouter des fichiers (PDF, images, videos)
            </label>
            <input
              id="project_files"
              type="file"
              accept={ACCEPTED_FILE_TYPES}
              multiple
              onChange={handleProjectFiles}
              className="input-text"
              disabled={loading || projectFiles.length >= MAX_PROJECT_FILES}
            />
            <div className="input-help">
              {projectFiles.length}/{MAX_PROJECT_FILES} fichier(s) selectionne(s).
            </div>
            {fileError && (
              <div className="form-message form-message--error" role="alert" style={{ marginTop: 12 }}>
                {fileError}
              </div>
            )}
            {projectFiles.length > 0 && (
              <ul className="muted" style={{ margin: "12px 0 0", paddingLeft: 18, display: "grid", gap: 8 }}>
                {projectFiles.map((file) => (
                  <li key={file.id} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span>
                      {file.name} ({Math.round(file.size / 1024)} Ko)
                    </span>
                    <button
                      type="button"
                      className="btn btn-ghost"
                      style={{ padding: "4px 10px", fontSize: "0.8rem" }}
                      onClick={() => handleRemoveProjectFile(file.id)}
                      disabled={loading}
                    >
                      Retirer
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? "Envoi en cours..." : "Envoyer"}
        </button>
      </form>
    </main>
  );
}

