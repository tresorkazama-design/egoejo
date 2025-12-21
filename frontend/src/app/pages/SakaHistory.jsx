/**
 * Page SakaHistory - Historique des transactions SAKA
 * Affiche toutes les transactions (gains et dépenses) de l'utilisateur
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { fetchAPI, handleAPIError } from '../../utils/api';
import { useLanguage } from '../../contexts/LanguageContext';
import { useAuth } from '../../contexts/AuthContext';
import { t } from '../../utils/i18n';
import SEO from '../../components/SEO';
import { useSEO } from '../../hooks/useSEO';
import { Loader } from '../../components/Loader';
import { Skeleton, SkeletonText } from '../../components/ui/Skeleton';
import Breadcrumbs from '../../components/ui/Breadcrumbs';
import ErrorBoundary from '../../components/ErrorBoundary';
import { formatReasonWithMetadata } from '../../utils/sakaReasons';

export default function SakaHistory() {
  const { language } = useLanguage();
  const { user } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // État de pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(50);
  const [totalCount, setTotalCount] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrevious, setHasPrevious] = useState(false);
  
  // État des filtres
  const [filterDirection, setFilterDirection] = useState(''); // '', 'EARN', 'SPEND'

  const seoProps = useSEO({
    title: 'Historique SAKA - EGOEJO',
    description: 'Consultez l\'historique complet de vos transactions SAKA',
  });

  useEffect(() => {
    if (!user) {
      setLoading(false);
      return;
    }

    loadTransactions();
  }, [user, currentPage, filterDirection]);

  const loadTransactions = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Construire les query params
      const params = new URLSearchParams({
        page: currentPage.toString(),
        page_size: pageSize.toString(),
      });
      
      if (filterDirection) {
        params.append('direction', filterDirection);
      }
      
      const data = await fetchAPI(`/api/saka/transactions/?${params.toString()}`);
      
      // Format DRF standard : { count, next, previous, results }
      setTransactions(data.results || []);
      setTotalCount(data.count || 0);
      setHasNext(!!data.next);
      setHasPrevious(!!data.previous);
    } catch (err) {
      setError(handleAPIError(err));
    } finally {
      setLoading(false);
    }
  };
  
  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    // Scroll vers le haut de la page
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };
  
  const handleFilterChange = (direction) => {
    setFilterDirection(direction);
    setCurrentPage(1); // Reset à la première page lors d'un changement de filtre
  };

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

  if (!user) {
    return (
      <div className="page" style={{ padding: '2rem', textAlign: 'center' }}>
        <p>Veuillez vous connecter pour voir votre historique SAKA.</p>
        <Link to="/login" className="btn btn-primary">
          Se connecter
        </Link>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <SEO {...seoProps} />
      <div className="page" style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
        {/* Breadcrumbs */}
        <Breadcrumbs
          items={[
            { label: 'Accueil', to: '/' },
            { label: 'Dashboard', to: '/dashboard' },
            { label: 'Historique SAKA' },
          ]}
        />

        <h1 style={{ marginBottom: '2rem', fontSize: '2rem' }}>Historique SAKA</h1>

        {/* Filtres */}
        <div style={{ marginBottom: '1.5rem', display: 'flex', gap: '1rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <label style={{ fontSize: '0.875rem', fontWeight: '500', color: 'var(--text)' }}>
            Filtrer par type :
          </label>
          <select
            value={filterDirection}
            onChange={(e) => handleFilterChange(e.target.value)}
            style={{
              padding: '0.5rem 1rem',
              borderRadius: 'var(--radius)',
              border: '1px solid var(--border)',
              backgroundColor: 'var(--surface)',
              color: 'var(--text)',
              fontSize: '0.875rem',
              cursor: 'pointer',
            }}
          >
            <option value="">Tous</option>
            <option value="EARN">Gains uniquement</option>
            <option value="SPEND">Dépenses uniquement</option>
          </select>
          
          {totalCount > 0 && (
            <span style={{ fontSize: '0.875rem', color: 'var(--muted)', marginLeft: 'auto' }}>
              {totalCount} transaction{totalCount > 1 ? 's' : ''} au total
            </span>
          )}
        </div>

        {loading ? (
          <div>
            {/* Skeleton pour le tableau */}
            <div style={{ marginBottom: '1rem' }}>
              <Skeleton width="100%" height="3rem" style={{ marginBottom: '0.5rem' }} />
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton width="100%" height="4rem" style={{ marginBottom: '0.5rem' }} key={i} />
              ))}
            </div>
          </div>
        ) : error ? (
          <div 
            style={{ 
              padding: '2rem', 
              textAlign: 'center', 
              backgroundColor: 'var(--surface)',
              borderRadius: 'var(--radius)',
              border: '1px solid var(--border)',
            }}
            role="alert"
            aria-live="polite"
          >
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
            <h2 style={{ marginBottom: '0.5rem', color: 'var(--text)' }}>Erreur de chargement</h2>
            <p style={{ color: 'var(--muted)', marginBottom: '1.5rem' }}>
              {error}
            </p>
            <button 
              onClick={loadTransactions} 
              className="btn btn-primary" 
              style={{ marginTop: '1rem' }}
              aria-label="Réessayer de charger les transactions"
            >
              🔄 Réessayer
            </button>
          </div>
        ) : transactions.length === 0 ? (
          <div style={{ padding: '3rem', textAlign: 'center', backgroundColor: 'var(--surface)', borderRadius: 'var(--radius)' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📜</div>
            <h2 style={{ marginBottom: '0.5rem' }}>Aucune transaction</h2>
            <p style={{ color: 'var(--muted)' }}>
              Vos transactions SAKA apparaîtront ici une fois que vous commencerez à gagner ou dépenser des grains.
            </p>
            <Link to="/dashboard" className="btn btn-primary" style={{ marginTop: '1rem' }}>
              Retour au Dashboard
            </Link>
          </div>
        ) : (
          <>
            {/* Vue Desktop : Tableau */}
            <div
              className="saka-history-desktop"
              style={{
                backgroundColor: 'var(--surface)',
                borderRadius: 'var(--radius)',
                border: '1px solid var(--border)',
                overflow: 'hidden',
                display: 'none', // Caché sur mobile
              }}
            >
              <table
                style={{
                  width: '100%',
                  borderCollapse: 'collapse',
                }}
                aria-label="Historique des transactions SAKA"
              >
                <thead>
                  <tr style={{ backgroundColor: 'var(--bg)', borderBottom: '2px solid var(--border)' }}>
                    <th style={{ padding: '1rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: 'var(--muted)' }}>
                      Date
                    </th>
                    <th style={{ padding: '1rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: 'var(--muted)' }}>
                      Type
                    </th>
                    <th style={{ padding: '1rem', textAlign: 'right', fontSize: '0.875rem', fontWeight: '600', color: 'var(--muted)' }}>
                      Montant
                    </th>
                    <th style={{ padding: '1rem', textAlign: 'left', fontSize: '0.875rem', fontWeight: '600', color: 'var(--muted)' }}>
                      Raison
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((tx) => (
                    <tr
                      key={tx.id}
                      style={{
                        borderBottom: '1px solid var(--border)',
                        transition: 'background-color 0.2s',
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.backgroundColor = 'var(--bg)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.backgroundColor = 'transparent';
                      }}
                    >
                      <td style={{ padding: '1rem', fontSize: '0.875rem', color: 'var(--text)' }}>
                        {formatDate(tx.created_at)}
                      </td>
                      <td style={{ padding: '1rem' }}>
                        <span
                          style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '0.25rem',
                            padding: '0.25rem 0.75rem',
                            borderRadius: '9999px',
                            fontSize: '0.75rem',
                            fontWeight: '500',
                            backgroundColor: tx.direction === 'EARN' ? '#f0fdf4' : '#fef3c7',
                            color: tx.direction === 'EARN' ? '#15803d' : '#92400e',
                          }}
                        >
                          {tx.direction === 'EARN' ? '➕' : '➖'}
                          {tx.direction === 'EARN' ? 'Gain' : 'Dépense'}
                        </span>
                      </td>
                      <td
                        style={{
                          padding: '1rem',
                          textAlign: 'right',
                          fontSize: '0.875rem',
                          fontWeight: '600',
                          color: tx.direction === 'EARN' ? '#84cc16' : '#f59e0b',
                        }}
                      >
                        {tx.direction === 'EARN' ? '+' : '-'}
                        {tx.amount} SAKA
                      </td>
                      <td style={{ padding: '1rem', fontSize: '0.875rem', color: 'var(--text)' }}>
                        {formatReasonWithMetadata(tx.reason, tx.metadata || {})}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Vue Mobile : Cards */}
            <div
              className="saka-history-mobile"
              style={{
                display: 'grid',
                gap: '1rem',
              }}
              role="list"
              aria-label="Historique des transactions SAKA"
            >
              {transactions.map((tx) => (
                <div
                  key={tx.id}
                  role="listitem"
                  style={{
                    backgroundColor: 'var(--surface)',
                    borderRadius: 'var(--radius)',
                    border: '1px solid var(--border)',
                    padding: '1rem',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-2px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.1)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontSize: '0.75rem', color: 'var(--muted)', marginBottom: '0.25rem' }}>
                        {formatDate(tx.created_at)}
                      </div>
                      <div style={{ fontSize: '0.875rem', fontWeight: '600', color: 'var(--text)', marginTop: '0.25rem' }}>
                        {formatReasonWithMetadata(tx.reason, tx.metadata || {})}
                      </div>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem' }}>
                      <span
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '0.25rem',
                          padding: '0.25rem 0.75rem',
                          borderRadius: '9999px',
                          fontSize: '0.75rem',
                          fontWeight: '500',
                          backgroundColor: tx.direction === 'EARN' ? '#f0fdf4' : '#fef3c7',
                          color: tx.direction === 'EARN' ? '#15803d' : '#92400e',
                        }}
                      >
                        {tx.direction === 'EARN' ? '➕' : '➖'}
                        {tx.direction === 'EARN' ? 'Gain' : 'Dépense'}
                      </span>
                      <div
                        style={{
                          fontSize: '1rem',
                          fontWeight: '600',
                          color: tx.direction === 'EARN' ? '#84cc16' : '#f59e0b',
                        }}
                      >
                        {tx.direction === 'EARN' ? '+' : '-'}
                        {tx.amount} SAKA
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {/* Pagination */}
        {!loading && transactions.length > 0 && (
          <div style={{ 
            marginTop: '2rem', 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center',
            gap: '1rem',
            flexWrap: 'wrap',
          }}>
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={!hasPrevious}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: hasPrevious ? 'var(--accent)' : 'var(--border)',
                color: hasPrevious ? 'white' : 'var(--muted)',
                border: 'none',
                borderRadius: 'var(--radius)',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: hasPrevious ? 'pointer' : 'not-allowed',
                opacity: hasPrevious ? 1 : 0.5,
                transition: 'opacity 0.2s',
              }}
              onMouseEnter={(e) => {
                if (hasPrevious) e.currentTarget.style.opacity = '0.9';
              }}
              onMouseLeave={(e) => {
                if (hasPrevious) e.currentTarget.style.opacity = '1';
              }}
            >
              ← Précédent
            </button>
            
            <span style={{ fontSize: '0.875rem', color: 'var(--text)' }}>
              Page {currentPage} {totalCount > 0 && `sur ${Math.ceil(totalCount / pageSize)}`}
            </span>
            
            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={!hasNext}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: hasNext ? 'var(--accent)' : 'var(--border)',
                color: hasNext ? 'white' : 'var(--muted)',
                border: 'none',
                borderRadius: 'var(--radius)',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: hasNext ? 'pointer' : 'not-allowed',
                opacity: hasNext ? 1 : 0.5,
                transition: 'opacity 0.2s',
              }}
              onMouseEnter={(e) => {
                if (hasNext) e.currentTarget.style.opacity = '0.9';
              }}
              onMouseLeave={(e) => {
                if (hasNext) e.currentTarget.style.opacity = '1';
              }}
            >
              Suivant →
            </button>
          </div>
        )}

        {/* Lien retour */}
        <div style={{ marginTop: '2rem', textAlign: 'center' }}>
          <Link
            to="/dashboard"
            style={{
              display: 'inline-block',
              padding: '0.75rem 1.5rem',
              color: 'var(--accent)',
              textDecoration: 'none',
              border: '1px solid var(--accent)',
              borderRadius: 'var(--radius)',
              transition: 'opacity 0.2s',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.opacity = '0.8';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.opacity = '1';
            }}
          >
            ← Retour au Dashboard
          </Link>
        </div>
      </div>
    </ErrorBoundary>
  );
}

