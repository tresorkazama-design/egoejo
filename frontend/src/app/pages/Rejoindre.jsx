import React, { useState } from 'react';
import { Input } from '../../components/Input';
import { Button } from '../../components/Button';
import { isValidEmail } from '../../utils/validation';
import { fetchAPI, handleAPIError } from '../../utils/api';
import { useLanguage } from '../../contexts/LanguageContext';
import { t } from '../../utils/i18n';
import SEO from '../../components/SEO';
import { useSEO } from '../../hooks/useSEO';

export const Rejoindre = () => {
  const { language } = useLanguage();
  const [formData, setFormData] = useState({
    nom: '',
    email: '',
    profil: '',
    message: '',
    website: '' // Honeypot
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const seoProps = useSEO({
    titleKey: "seo.rejoindre_title",
    descriptionKey: "seo.rejoindre_description",
    keywords: t("seo.rejoindre_keywords", language),
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Effacer l'erreur du champ modifié
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.nom.trim()) {
      newErrors.nom = t("rejoindre.error_nom", language);
    }

    if (!formData.email.trim()) {
      newErrors.email = t("rejoindre.error_email", language);
    } else if (!isValidEmail(formData.email)) {
      newErrors.email = t("rejoindre.error_email_invalid", language);
    }

    if (!formData.profil) {
      newErrors.profil = t("rejoindre.error_profil", language);
    }

    if (formData.message && formData.message.length > 1000) {
      newErrors.message = t("rejoindre.error_message_length", language);
    }

    // Honeypot - si rempli, c'est un bot
    if (formData.website) {
      newErrors.website = t("rejoindre.error_spam", language);
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');

    if (!validate()) {
      return;
    }

    setLoading(true);

    try {
      const { website, ...dataToSend } = formData; // Exclure le honeypot
      const response = await fetchAPI('/intents/rejoindre/', {
        method: 'POST',
        body: JSON.stringify(dataToSend)
      });

      setSuccess(true);
      setFormData({
        nom: '',
        email: '',
        profil: '',
        message: '',
        website: ''
      });
    } catch (error) {
      setErrorMessage(handleAPIError(error));
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="rejoindre-page" data-testid="rejoindre-page">
        <SEO {...seoProps} />
        <div className="success-message bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded" role="alert" aria-live="polite">
          <h2>{t("rejoindre.success_title", language)}</h2>
          <p>{t("rejoindre.success_message", language)}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="rejoindre-page" data-testid="rejoindre-page">
      <SEO {...seoProps} />
      <h1 className="text-3xl font-bold mb-6">{t("rejoindre.title", language)}</h1>
      
      <form onSubmit={handleSubmit} data-testid="rejoindre-form" aria-label={t("rejoindre.title", language)} noValidate>
        <Input
          label={t("rejoindre.nom", language)}
          name="nom"
          id="rejoindre-nom"
          value={formData.nom}
          onChange={handleChange}
          error={errors.nom}
          required
          aria-describedby={errors.nom ? "rejoindre-nom-error" : undefined}
        />

        <Input
          label={t("rejoindre.email", language)}
          name="email"
          id="rejoindre-email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          error={errors.email}
          required
          aria-describedby={errors.email ? "rejoindre-email-error" : undefined}
        />

        <div className="mb-4">
          <label htmlFor="profil-select" className="block text-sm font-medium mb-1">
            {t("rejoindre.profil", language)} <span className="text-red-500" aria-label={t("common.required", language)}>*</span>
          </label>
          <select
            id="profil-select"
            name="profil"
            value={formData.profil}
            onChange={handleChange}
            className={`w-full px-3 py-2 border rounded-md ${
              errors.profil ? 'border-red-500' : 'border-gray-300'
            }`}
            required
            aria-invalid={errors.profil ? 'true' : 'false'}
            aria-describedby={errors.profil ? 'profil-select-error' : undefined}
          >
            <option value="">{t("rejoindre.profil_select", language)}</option>
            <option value="je-decouvre">{t("rejoindre.profil_decouvre", language)}</option>
            <option value="je-participe">{t("rejoindre.profil_participe", language)}</option>
            <option value="je-contribue">{t("rejoindre.profil_contribue", language)}</option>
          </select>
          {errors.profil && (
            <p className="text-red-500 text-sm mt-1" role="alert" id="profil-select-error">{errors.profil}</p>
          )}
        </div>

        <Input
          label={t("rejoindre.message", language)}
          name="message"
          id="rejoindre-message"
          value={formData.message}
          onChange={handleChange}
          error={errors.message}
          aria-describedby={errors.message ? "rejoindre-message-error" : undefined}
        />

        {/* Honeypot - caché pour les utilisateurs */}
        <input
          type="text"
          name="website"
          value={formData.website}
          onChange={handleChange}
          style={{ display: 'none' }}
          tabIndex="-1"
          autoComplete="off"
          aria-hidden="true"
        />
        {errors.website && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {errors.website}
          </div>
        )}

        {errorMessage && (
          <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded" role="alert" aria-live="polite">
            {errorMessage}
          </div>
        )}

        <Button type="submit" disabled={loading}>
          {loading ? t("rejoindre.envoi", language) : t("rejoindre.envoyer", language)}
        </Button>
      </form>
    </div>
  );
};

export default Rejoindre;

