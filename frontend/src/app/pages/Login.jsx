import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { t } from '../../utils/i18n';
import { Input } from '../../components/Input';
import { Button } from '../../components/Button';
import CardTilt from '../../components/CardTilt';
import { useNotificationContext } from '../../contexts/NotificationContext';
import NotificationContainer from '../../components/NotificationContainer';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const { language } = useLanguage();
  const navigate = useNavigate();
  const location = useLocation();
  const { notifications, showSuccess, removeNotification } = useNotificationContext();

  // Afficher le message de succès après inscription
  useEffect(() => {
    if (location.state?.message) {
      showSuccess(location.state.message, 6000);
      // Nettoyer le state pour éviter de réafficher le message
      navigate(location.pathname, { replace: true, state: {} });
    }
  }, [location.state, showSuccess, navigate, location.pathname]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username, password);
      showSuccess(t('login.success', language), 4000);
      setTimeout(() => {
        navigate('/');
      }, 1000);
    } catch (err) {
      setError(err.message || t('login.error', language));
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
        <div className="citations-hero__badge">{t('login.badge', language)}</div>
        <h1 className="citations-hero__title">{t('login.title', language)}</h1>
        <p className="citations-hero__subtitle">
          {t('login.subtitle', language)}
        </p>
      </section>

      <section className="citation-group">
        <header className="citation-group__header">
          <span className="citation-group__tag">{t('login.form_tag', language)}</span>
          <h2 className="citation-group__title">{t('login.form_title', language)}</h2>
          <p className="citation-group__description">
            {t('login.form_description', language)}
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
                  label={t('login.username_label', language)}
                  name="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoComplete="username"
                />

                <Input
                  label={t('login.password_label', language)}
                  name="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                />

                <Button type="submit" disabled={loading} className="auth-form__submit">
                  {loading ? t('login.submitting', language) : t('login.submit', language)}
                </Button>

                <div className="auth-form__links">
                  <Link to="/register" className="auth-form__link">
                    {t('login.no_account', language)}
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

