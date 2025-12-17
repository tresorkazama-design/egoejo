import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { t } from '../../utils/i18n';
import { Input } from '../../components/Input';
import { Button } from '../../components/Button';
import { isValidEmail } from '../../utils/validation';
import CardTilt from '../../components/CardTilt';
import { useNotificationContext } from '../../contexts/NotificationContext';
import NotificationContainer from '../../components/NotificationContainer';

export default function Register() {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    passwordConfirm: '',
  });
  const [errors, setErrors] = useState({});
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const { language } = useLanguage();
  const navigate = useNavigate();
  const { notifications, showSuccess, removeNotification } = useNotificationContext();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: null }));
    }
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.username.trim()) {
      newErrors.username = t('register.error_username_required', language);
    } else if (formData.username.length < 3) {
      newErrors.username = t('register.error_username_length', language);
    }

    if (!formData.email.trim()) {
      newErrors.email = t('register.error_email_required', language);
    } else if (!isValidEmail(formData.email)) {
      newErrors.email = t('register.error_email_invalid', language);
    }

    if (!formData.password) {
      newErrors.password = t('register.error_password_required', language);
    } else if (formData.password.length < 10) {
      newErrors.password = t('register.error_password_length', language);
    }

    if (formData.password !== formData.passwordConfirm) {
      newErrors.passwordConfirm = t('register.error_password_match', language);
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!validate()) {
      return;
    }

    setLoading(true);

    try {
      await register({
        username: formData.username,
        email: formData.email,
        password: formData.password,
      });
      showSuccess(t('register.success', language), 5000);
      setTimeout(() => {
        navigate('/login', { state: { message: t('register.success', language) } });
      }, 1500);
    } catch (err) {
      setError(err.message || t('register.error', language));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page page--citations">
      <NotificationContainer
        notifications={notifications}
        onRemove={removeNotification}
      />
      <section className="citations-hero">
        <div className="citations-hero__badge">{t('register.badge', language)}</div>
        <h1 className="citations-hero__title">{t('register.title', language)}</h1>
        <p className="citations-hero__subtitle">
          {t('register.subtitle', language)}
        </p>
      </section>

      <section className="citation-group">
        <header className="citation-group__header">
          <span className="citation-group__tag">{t('register.form_tag', language)}</span>
          <h2 className="citation-group__title">{t('register.form_title', language)}</h2>
          <p className="citation-group__description">
            {t('register.form_description', language)}
          </p>
        </header>
        <div className="citation-group__quotes">
          <CardTilt>
            <div className="citation-card">
              <form onSubmit={handleSubmit} className="auth-form">
                {error && (
                  <div className="auth-form__error">
                    <p>{error}</p>
                  </div>
                )}

                <Input
                  label={t('register.username_label', language)}
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  error={errors.username}
                  required
                  autoComplete="username"
                />

                <Input
                  label={t('register.email_label', language)}
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  error={errors.email}
                  required
                  autoComplete="email"
                />

                <Input
                  label={t('register.password_label', language)}
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange}
                  error={errors.password}
                  required
                  autoComplete="new-password"
                />

                <Input
                  label={t('register.password_confirm_label', language)}
                  name="passwordConfirm"
                  type="password"
                  value={formData.passwordConfirm}
                  onChange={handleChange}
                  error={errors.passwordConfirm}
                  required
                  autoComplete="new-password"
                />

                <Button type="submit" disabled={loading} className="auth-form__submit">
                  {loading ? t('register.submitting', language) : t('register.submit', language)}
                </Button>

                <div className="auth-form__links">
                  <Link to="/login" className="auth-form__link">
                    {t('register.has_account', language)}
                  </Link>
                </div>
              </form>
            </div>
          </CardTilt>
        </div>
      </section>
    </div>
  );
}

