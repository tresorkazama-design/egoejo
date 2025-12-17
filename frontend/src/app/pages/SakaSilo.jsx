/**
 * Page "Silo Commun SAKA" - Phase 3 : Compostage & Silo Commun
 * Affiche l'état du Silo Commun où sont stockés les grains SAKA compostés
 */
import { Link } from 'react-router-dom';
import { useSakaSilo } from '../../hooks/useSaka';
import { Loader } from '../../components/Loader';
import SEO from '../../components/SEO';
import ErrorBoundary from '../../components/ErrorBoundary';
import { useLanguage } from '../../contexts/LanguageContext';

export default function SakaSilo() {
  const { language } = useLanguage();
  const { data: silo, loading, error } = useSakaSilo();

  // Fonction pour formater les dates
  const formatDate = (dateString) => {
    if (!dateString) return '';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('fr-FR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch (e) {
      return dateString;
    }
  };

  if (loading) {
    return (
      <ErrorBoundary>
        <SEO
          title="Silo Commun SAKA - EGOEJO"
          description="Visualisez l'état du Silo Commun où sont stockés les grains SAKA compostés"
        />
        <div className="saka-silo-page" style={{ padding: '2rem', textAlign: 'center' }}>
          <Loader message="Chargement du Silo Commun…" />
        </div>
      </ErrorBoundary>
    );
  }

  if (error) {
    return (
      <ErrorBoundary>
        <SEO
          title="Silo Commun SAKA - EGOEJO"
          description="Visualisez l'état du Silo Commun où sont stockés les grains SAKA compostés"
        />
        <div className="saka-silo-page" style={{ padding: '2rem', textAlign: 'center' }}>
          <p style={{ color: 'red' }}>{error}</p>
          <Link
            to="/dashboard"
            style={{
              display: 'inline-block',
              marginTop: '1rem',
              padding: '0.75rem 1.5rem',
              backgroundColor: 'var(--accent)',
              color: 'white',
              borderRadius: 'var(--radius)',
              textDecoration: 'none',
            }}
          >
            Retour au Dashboard
          </Link>
        </div>
      </ErrorBoundary>
    );
  }

  if (!silo?.enabled) {
    return (
      <ErrorBoundary>
        <SEO
          title="Silo Commun SAKA - EGOEJO"
          description="Visualisez l'état du Silo Commun où sont stockés les grains SAKA compostés"
        />
        <div className="saka-silo-page" style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto' }}>
          <h1 style={{ marginBottom: '1rem', fontSize: '2rem' }}>Silo Commun (Compost SAKA)</h1>
          <div
            style={{
              padding: '2rem',
              backgroundColor: 'var(--surface)',
              borderRadius: 'var(--radius)',
              border: '1px solid var(--border)',
              textAlign: 'center',
              color: 'var(--muted)',
            }}
          >
            <p>Le compostage SAKA n'est pas encore activé.</p>
            <p style={{ marginTop: '0.5rem', fontSize: '0.875rem' }}>
              Le Silo Commun sera disponible lorsque le compostage sera activé.
            </p>
            <Link
              to="/dashboard"
              style={{
                display: 'inline-block',
                marginTop: '1rem',
                padding: '0.75rem 1.5rem',
                backgroundColor: 'var(--accent)',
                color: 'white',
                borderRadius: 'var(--radius)',
                textDecoration: 'none',
              }}
            >
              Retour au Dashboard
            </Link>
          </div>
        </div>
      </ErrorBoundary>
    );
  }

  return (
    <ErrorBoundary>
      <SEO
        title="Silo Commun SAKA - EGOEJO"
        description="Visualisez l'état du Silo Commun où sont stockés les grains SAKA compostés"
      />
      <div className="saka-silo-page" style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ marginBottom: '2rem' }}>
          <Link
            to="/dashboard"
            style={{
              display: 'inline-block',
              marginBottom: '1rem',
              color: 'var(--accent)',
              textDecoration: 'none',
              fontSize: '0.875rem',
            }}
          >
            ← Retour au Dashboard
          </Link>
          <h1 style={{ marginBottom: '0.5rem', fontSize: '2.5rem' }}>Silo Commun (Compost SAKA)</h1>
          <p style={{ color: 'var(--muted)', fontSize: '1rem' }}>
            Les grains SAKA inactifs retournent à la terre pour nourrir le collectif
          </p>
        </div>

        {/* Métriques principales */}
        <section
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '1.5rem',
            marginBottom: '3rem',
          }}
        >
          <div
            style={{
              padding: '2rem',
              backgroundColor: 'var(--surface)',
              borderRadius: 'var(--radius)',
              border: '1px solid var(--border)',
            }}
          >
            <div style={{ fontSize: '0.875rem', color: 'var(--muted)', marginBottom: '0.5rem' }}>
              Grains en Silo
            </div>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#84cc16' }}>
              {silo.total_balance ?? 0} SAKA
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.5rem' }}>
              Solde actuel disponible
            </p>
          </div>

          <div
            style={{
              padding: '2rem',
              backgroundColor: 'var(--surface)',
              borderRadius: 'var(--radius)',
              border: '1px solid var(--border)',
            }}
          >
            <div style={{ fontSize: '0.875rem', color: 'var(--muted)', marginBottom: '0.5rem' }}>
              Grains compostés
            </div>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--accent)' }}>
              {silo.total_composted ?? 0}
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.5rem' }}>
              Total historique
            </p>
          </div>

          <div
            style={{
              padding: '2rem',
              backgroundColor: 'var(--surface)',
              borderRadius: 'var(--radius)',
              border: '1px solid var(--border)',
            }}
          >
            <div style={{ fontSize: '0.875rem', color: 'var(--muted)', marginBottom: '0.5rem' }}>
              Cycles effectués
            </div>
            <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--accent)' }}>
              {silo.total_cycles ?? 0}
            </div>
            {silo.last_compost_at && (
              <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.5rem' }}>
                Dernier cycle le {formatDate(silo.last_compost_at)}
              </p>
            )}
          </div>
        </section>

        {/* Section projets financés (à venir) */}
        <section
          style={{
            padding: '2rem',
            backgroundColor: 'var(--surface)',
            borderRadius: 'var(--radius)',
            border: '1px solid var(--border)',
          }}
        >
          <h2 style={{ marginBottom: '1rem', fontSize: '1.5rem' }}>Projets financés par le Silo</h2>
          <p style={{ color: 'var(--muted)', fontSize: '0.875rem' }}>
            À venir : liste des projets soutenus par le Silo Commun grâce aux grains compostés.
          </p>
          <p style={{ color: 'var(--muted)', fontSize: '0.875rem', marginTop: '0.5rem' }}>
            Les grains compostés retournent à la communauté pour nourrir de nouveaux projets collectifs.
          </p>
        </section>
      </div>
    </ErrorBoundary>
  );
}

