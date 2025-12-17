/**
 * Page "Ma Carte EGOEJO"
 * Affiche la carte digitale in-app et permet d'ajouter à Apple/Google Wallet
 */
import { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { fetchAPI } from '../../utils/api';
import { formatMoney } from '../../utils/money';
import { QRCodeSVG } from 'qrcode.react';
import SEO from '../../components/SEO';
import ErrorBoundary from '../../components/ErrorBoundary';
import { Loader } from '../../components/Loader';

export default function MyCard() {
  const { user } = useAuth();
  const { language } = useLanguage();
  const [wallet, setWallet] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [appleAvailable, setAppleAvailable] = useState(true);
  const [googleAvailable, setGoogleAvailable] = useState(true);
  const [downloading, setDownloading] = useState({ apple: false, google: false });

  useEffect(() => {
    if (!user) {
      setLoading(false);
      return;
    }

    loadWalletData();
  }, [user]);

  const loadWalletData = async () => {
    try {
      const data = await fetchAPI('/api/impact/global-assets/');
      setWallet(data);
      setError(null);
    } catch (err) {
      console.error('Erreur chargement wallet:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadApple = async () => {
    setDownloading({ ...downloading, apple: true });
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/wallet-pass/apple/`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || sessionStorage.getItem('token')}`,
        },
      });

      if (response.status === 503) {
        const data = await response.json();
        setAppleAvailable(false);
        alert(data.message || 'Apple Wallet n\'est pas encore disponible.');
        return;
      }

      if (!response.ok) {
        throw new Error('Erreur lors du téléchargement');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `egoejo-member-${user.id}.pkpass`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Erreur téléchargement Apple:', err);
      alert('Erreur lors du téléchargement du pass Apple Wallet');
    } finally {
      setDownloading({ ...downloading, apple: false });
    }
  };

  const handleDownloadGoogle = async () => {
    setDownloading({ ...downloading, google: true });
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/wallet-pass/google/`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token') || sessionStorage.getItem('token')}`,
        },
      });

      if (response.status === 503) {
        const data = await response.json();
        setGoogleAvailable(false);
        alert(data.message || 'Google Wallet n\'est pas encore disponible.');
        return;
      }

      if (!response.ok) {
        throw new Error('Erreur lors du téléchargement');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `egoejo-member-${user.id}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Erreur téléchargement Google:', err);
      alert('Erreur lors du téléchargement du pass Google Wallet');
    } finally {
      setDownloading({ ...downloading, google: false });
    }
  };

  // Détecter la plateforme
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
  const isAndroid = /Android/.test(navigator.userAgent);

  if (!user) {
    return (
      <div className="my-card-page" style={{ padding: '2rem', textAlign: 'center' }}>
        <h1>Ma Carte EGOEJO</h1>
        <p>Veuillez vous connecter pour voir votre carte.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="my-card-page" style={{ padding: '2rem', textAlign: 'center' }}>
        <Loader message="Chargement de votre carte..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="my-card-page" style={{ padding: '2rem', textAlign: 'center' }}>
        <p style={{ color: 'red' }}>{error}</p>
        <button onClick={loadWalletData}>Réessayer</button>
      </div>
    );
  }

  // Déterminer le statut du membre
  const getMemberStatus = () => {
    if (user.is_superuser || user.is_staff) {
      return 'Membre fondateur';
    }
    // TODO: Ajouter d'autres statuts selon les critères
    return 'Membre';
  };

  // Générer un identifiant unique pour le QR code
  const qrValue = `${user.id}-${user.email}-${Date.now()}`;

  return (
    <ErrorBoundary>
      <SEO
        title="Ma Carte EGOEJO"
        description="Votre carte membre digitale EGOEJO"
      />
      <div className="my-card-page" style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
        <h1 style={{ marginBottom: '2rem', fontSize: '2.5rem' }}>Ma Carte EGOEJO</h1>

        {/* Carte in-app universelle */}
        <div
          style={{
            background: 'linear-gradient(135deg, #065f46 0%, #047857 100%)',
            borderRadius: 'var(--radius, 16px)',
            padding: '2rem',
            color: 'white',
            marginBottom: '2rem',
            boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          {/* Logo EGOEJO (simplifié) */}
          <div style={{ marginBottom: '1.5rem', fontSize: '2rem', fontWeight: 'bold' }}>
            🌱 EGOEJO
          </div>

          {/* Informations membre */}
          <div style={{ marginBottom: '1.5rem' }}>
            <h2 style={{ margin: 0, marginBottom: '0.5rem', fontSize: '1.5rem' }}>
              {user.username || user.email}
            </h2>
            <p style={{ margin: 0, opacity: 0.9, fontSize: '0.9rem' }}>
              {getMemberStatus()}
            </p>
          </div>

          {/* Solde */}
          {wallet && (
            <div style={{ marginBottom: '1.5rem' }}>
              <p style={{ margin: 0, opacity: 0.8, fontSize: '0.875rem', marginBottom: '0.25rem' }}>
                Solde disponible
              </p>
              <p style={{ margin: 0, fontSize: '2rem', fontWeight: 'bold' }}>
                {formatMoney(wallet.cash_balance)}
              </p>
            </div>
          )}

          {/* QR Code */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              backgroundColor: 'white',
              padding: '1rem',
              borderRadius: '8px',
              marginTop: '1.5rem',
            }}
          >
            <QRCodeSVG
              value={qrValue}
              size={150}
              level="M"
              includeMargin={false}
            />
          </div>
        </div>

        {/* Section Ajouter à mon Wallet */}
        <section style={{ marginTop: '3rem' }}>
          <h2 style={{ marginBottom: '1.5rem', fontSize: '1.8rem' }}>
            Ajouter à mon Wallet
          </h2>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
              gap: '1.5rem',
            }}
          >
            {/* Bouton Apple Wallet */}
            <button
              onClick={handleDownloadApple}
              disabled={!appleAvailable || downloading.apple}
              style={{
                padding: '1.5rem',
                backgroundColor: appleAvailable ? '#000' : '#9ca3af',
                color: 'white',
                border: 'none',
                borderRadius: 'var(--radius)',
                cursor: appleAvailable && !downloading.apple ? 'pointer' : 'not-allowed',
                opacity: appleAvailable && !downloading.apple ? 1 : 0.6,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.75rem',
                fontSize: '1rem',
                fontWeight: '600',
              }}
              aria-label="Ajouter à Apple Wallet"
            >
              {downloading.apple ? (
                <>⏳ Téléchargement...</>
              ) : appleAvailable ? (
                <>
                  🍎 Ajouter à Apple Wallet
                </>
              ) : (
                <>🍎 Bientôt disponible</>
              )}
            </button>

            {/* Bouton Google Wallet */}
            <button
              onClick={handleDownloadGoogle}
              disabled={!googleAvailable || downloading.google}
              style={{
                padding: '1.5rem',
                backgroundColor: googleAvailable ? '#4285f4' : '#9ca3af',
                color: 'white',
                border: 'none',
                borderRadius: 'var(--radius)',
                cursor: googleAvailable && !downloading.google ? 'pointer' : 'not-allowed',
                opacity: googleAvailable && !downloading.google ? 1 : 0.6,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '0.75rem',
                fontSize: '1rem',
                fontWeight: '600',
              }}
              aria-label="Ajouter à Google Wallet"
            >
              {downloading.google ? (
                <>⏳ Téléchargement...</>
              ) : googleAvailable ? (
                <>
                  📱 Ajouter à Google Wallet
                </>
              ) : (
                <>📱 Bientôt disponible</>
              )}
            </button>
          </div>

          {/* Message d'information */}
          {(!appleAvailable || !googleAvailable) && (
            <p style={{ marginTop: '1rem', color: 'var(--muted)', fontSize: '0.875rem' }}>
              {!appleAvailable && !googleAvailable
                ? 'Les passes digitaux ne sont pas encore configurés sur cette plateforme.'
                : 'Certaines plateformes ne sont pas encore disponibles.'}
            </p>
          )}
        </section>
      </div>
    </ErrorBoundary>
  );
}

