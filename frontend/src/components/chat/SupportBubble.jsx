/**
 * Composant SupportBubble - Bulle flottante pour le Concierge Support
 * Affiche une icône flottante en bas à droite, ouvre un panneau de chat slide-in
 */
import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { fetchAPI } from '../../utils/api';
import ChatWindow from '../ChatWindow';
import { useNotificationContext } from '../../contexts/NotificationContext';

const SUPPORT_ROUTES = ['/dashboard', '/wallet', '/projets'];

export default function SupportBubble() {
  const { user } = useAuth();
  const { language } = useLanguage();
  const { showSuccess, showError } = useNotificationContext();
  const [isOpen, setIsOpen] = useState(false);
  const [isEligible, setIsEligible] = useState(false);
  const [loading, setLoading] = useState(true);
  const [thread, setThread] = useState(null);
  const [showContactForm, setShowContactForm] = useState(false);
  const [contactForm, setContactForm] = useState({
    name: '',
    email: '',
    message: '',
  });
  const [isOnline, setIsOnline] = useState(false); // Statut en ligne des modérateurs

  // Vérifier si on est sur une route support
  const [shouldShow, setShouldShow] = useState(false);

  useEffect(() => {
    const checkRoute = () => {
      const currentPath = window.location.pathname;
      const isSupportRoute = SUPPORT_ROUTES.some((route) => currentPath.startsWith(route));
      setShouldShow(isSupportRoute);
    };
    
    checkRoute();
    // Écouter les changements de route
    window.addEventListener('popstate', checkRoute);
    return () => window.removeEventListener('popstate', checkRoute);
  }, []);

  // Vérifier l'éligibilité au chargement
  useEffect(() => {
    if (!user || !shouldShow) {
      setLoading(false);
      return;
    }

    checkEligibility();
  }, [user, shouldShow]);

  const checkEligibility = async () => {
    try {
      const data = await fetchAPI('/api/support/concierge/eligibility/');
      setIsEligible(data.eligible);
      
      if (data.eligible) {
        // Charger le thread
        loadConciergeThread();
        // Vérifier le statut en ligne (simplifié - à améliorer avec WebSocket)
        checkOnlineStatus();
      }
    } catch (err) {
      console.error('Erreur vérification éligibilité:', err);
      setIsEligible(false);
    } finally {
      setLoading(false);
    }
  };

  const loadConciergeThread = async () => {
    try {
      const data = await fetchAPI('/api/support/concierge/');
      if (data.eligible && data.thread) {
        setThread(data.thread);
      }
    } catch (err) {
      console.error('Erreur chargement thread concierge:', err);
    }
  };

  const checkOnlineStatus = async () => {
    // TODO: Implémenter avec WebSocket ou endpoint dédié
    // Pour l'instant, on simule (à remplacer par une vraie vérification)
    setIsOnline(false); // Par défaut, considérer hors ligne
  };

  const handleOpen = async () => {
    if (!isEligible) {
      setShowContactForm(true);
      return;
    }

    if (!thread) {
      await loadConciergeThread();
    }
    setIsOpen(true);
  };

  const handleClose = () => {
    setIsOpen(false);
    setShowContactForm(false);
  };

  const handleContactSubmit = async (e) => {
    e.preventDefault();
    try {
      await fetchAPI('/api/support/contact/', {
        method: 'POST',
        body: JSON.stringify({
          name: contactForm.name || user?.username || '',
          email: contactForm.email || user?.email || '',
          message: contactForm.message,
        }),
      });
      showSuccess('Message envoyé ! Nous vous répondrons sous 24h.');
      setShowContactForm(false);
      setContactForm({ name: '', email: '', message: '' });
    } catch (err) {
      showError('Erreur lors de l\'envoi du message.');
    }
  };

  // Ne pas afficher si pas éligible ou pas sur une route support
  if (!shouldShow || loading || (!isEligible && !showContactForm)) {
    return null;
  }

  return (
    <>
      {/* Bulle flottante */}
      <button
        onClick={handleOpen}
        aria-label="Ouvrir le support Concierge"
        style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          width: '64px',
          height: '64px',
          borderRadius: '50%',
          backgroundColor: '#10b981', // Vert EGOEJO
          color: 'white',
          border: 'none',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          cursor: 'pointer',
          zIndex: 1000,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '24px',
          transition: 'transform 0.2s, box-shadow 0.2s',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'scale(1.1)';
          e.currentTarget.style.boxShadow = '0 6px 16px rgba(0,0,0,0.2)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'scale(1)';
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
        }}
      >
        💬
      </button>

      {/* Panneau slide-in (chat ou formulaire) */}
      {(isOpen || showContactForm) && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            right: 0,
            bottom: 0,
            width: '400px',
            maxWidth: '90vw',
            backgroundColor: 'var(--surface)',
            boxShadow: '-4px 0 12px rgba(0,0,0,0.15)',
            zIndex: 1001,
            display: 'flex',
            flexDirection: 'column',
            transform: isOpen || showContactForm ? 'translateX(0)' : 'translateX(100%)',
            transition: 'transform 0.3s ease-in-out',
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: '1.5rem',
              borderBottom: '1px solid var(--border)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <h3 style={{ margin: 0, fontSize: '1.25rem' }}>
              {isEligible ? 'Support Concierge' : 'Contactez-nous'}
            </h3>
            <button
              onClick={handleClose}
              aria-label="Fermer"
              style={{
                background: 'none',
                border: 'none',
                fontSize: '1.5rem',
                cursor: 'pointer',
                color: 'var(--muted)',
              }}
            >
              ×
            </button>
          </div>

          {/* Contenu */}
          <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
            {isEligible && thread ? (
              <>
                {/* Indicateur de statut */}
                <div
                  style={{
                    padding: '0.75rem 1.5rem',
                    backgroundColor: isOnline ? '#10b981' : '#f59e0b',
                    color: 'white',
                    fontSize: '0.875rem',
                    textAlign: 'center',
                  }}
                >
                  {isOnline ? 'Réponse en < 5 min' : 'Hors ligne - Formulaire disponible'}
                </div>
                {/* Chat Window */}
                <div style={{ flex: 1, overflow: 'hidden' }}>
                  <ChatWindow thread={thread} />
                </div>
              </>
            ) : (
              /* Formulaire de contact */
              <form
                onSubmit={handleContactSubmit}
                style={{
                  padding: '1.5rem',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '1rem',
                  flex: 1,
                }}
              >
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem' }}>Nom</label>
                  <input
                    type="text"
                    value={contactForm.name || user?.username || ''}
                    onChange={(e) => setContactForm({ ...contactForm, name: e.target.value })}
                    required
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      borderRadius: 'var(--radius)',
                      border: '1px solid var(--border)',
                    }}
                  />
                </div>
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem' }}>Email</label>
                  <input
                    type="email"
                    value={contactForm.email || user?.email || ''}
                    onChange={(e) => setContactForm({ ...contactForm, email: e.target.value })}
                    required
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      borderRadius: 'var(--radius)',
                      border: '1px solid var(--border)',
                    }}
                  />
                </div>
                <div style={{ flex: 1 }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem' }}>Message</label>
                  <textarea
                    value={contactForm.message}
                    onChange={(e) => setContactForm({ ...contactForm, message: e.target.value })}
                    required
                    rows={8}
                    style={{
                      width: '100%',
                      padding: '0.75rem',
                      borderRadius: 'var(--radius)',
                      border: '1px solid var(--border)',
                      resize: 'vertical',
                    }}
                  />
                </div>
                <button
                  type="submit"
                  style={{
                    padding: '0.75rem 1.5rem',
                    backgroundColor: 'var(--accent)',
                    color: 'white',
                    border: 'none',
                    borderRadius: 'var(--radius)',
                    cursor: 'pointer',
                    fontWeight: '600',
                  }}
                >
                  Envoyer
                </button>
              </form>
            )}
          </div>
        </div>
      )}

      {/* Overlay pour fermer en cliquant à côté */}
      {(isOpen || showContactForm) && (
        <div
          onClick={handleClose}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.3)',
            zIndex: 1000,
          }}
        />
      )}
    </>
  );
}

