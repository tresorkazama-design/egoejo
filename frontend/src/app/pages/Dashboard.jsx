/**
 * Page Dashboard "Patrimoine Vivant"
 * Affiche le patrimoine global de l'utilisateur : liquidités, pockets, dons, equity, dividende social
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { fetchAPI } from '../../utils/api';
import { formatMoney, toDecimal } from '../../utils/money';
import { Decimal } from 'decimal.js';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import SEO from '../../components/SEO';
import ErrorBoundary from '../../components/ErrorBoundary';
import { Loader } from '../../components/Loader';
import { useSakaSilo, useSakaCompostPreview } from '../../hooks/useSaka';
import FourPStrip from '../../components/dashboard/FourPStrip';
import SakaSeasonBadge from '../../components/saka/SakaSeasonBadge';
import UserImpact4P from '../../components/dashboard/UserImpact4P';

const COLORS = {
  cash: '#10b981', // Vert
  donations: '#3b82f6', // Bleu
  equity: '#f59e0b', // Doré
};

export default function Dashboard() {
  const { user, loading: authLoading } = useAuth();
  const { language } = useLanguage();
  const [assets, setAssets] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [transferModal, setTransferModal] = useState(null); // { pocketId, pocketName }

  useEffect(() => {
    if (!user) {
      setLoading(false);
      return;
    }

    loadAssets();
  }, [user]);

  const loadAssets = async () => {
    try {
      setLoading(true);
      const data = await fetchAPI('/api/impact/global-assets/');
      setAssets(data);
      setError(null);
    } catch (err) {
      console.error('Erreur chargement patrimoine:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTransfer = async (pocketId, amount) => {
    try {
      await fetchAPI('/api/wallet/pockets/transfer/', {
        method: 'POST',
        body: JSON.stringify({
          pocket_id: pocketId,
          amount: String(amount),
        }),
      });
      // Recharger les données
      await loadAssets();
      setTransferModal(null);
    } catch (err) {
      console.error('Erreur transfert:', err);
      alert(err.message || 'Erreur lors du transfert');
    }
  };

  // Attendre que l'authentification soit terminée avant de vérifier user
  // Cela garantit que les hooks s'exécutent même si user est défini après le montage initial
  if (authLoading) {
    return (
      <div className="dashboard-page" style={{ padding: '2rem', textAlign: 'center' }}>
        <Loader message="Vérification de l'authentification..." />
      </div>
    );
  }

  if (!user) {
    return (
      <div className="dashboard-page" style={{ padding: '2rem', textAlign: 'center' }}>
        <h1>Patrimoine Vivant</h1>
        <p>Veuillez vous connecter pour voir votre patrimoine.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="dashboard-page" style={{ padding: '2rem', textAlign: 'center' }}>
        <Loader message="Chargement de votre patrimoine..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-page" style={{ padding: '2rem', textAlign: 'center' }}>
        <p style={{ color: 'red' }}>{error}</p>
        <button onClick={loadAssets}>Réessayer</button>
      </div>
    );
  }

  if (!assets) return null;

  // Préparer les données pour le graphique camembert
  const chartData = [
    {
      name: 'Liquidités',
      value: parseFloat(assets.cash_balance || '0'),
      color: COLORS.cash,
    },
    {
      name: 'Dons',
      value: parseFloat(assets.donations?.total_amount || '0'),
      color: COLORS.donations,
    },
  ];

  // Ajouter equity seulement si actif
  if (assets.equity_portfolio?.is_active && parseFloat(assets.equity_portfolio.valuation || '0') > 0) {
    chartData.push({
      name: 'Investissements',
      value: parseFloat(assets.equity_portfolio.valuation || '0'),
      color: COLORS.equity,
    });
  }

  // Filtrer les valeurs nulles pour le graphique
  const filteredChartData = chartData.filter((item) => item.value > 0);

  // Emoji par type de pocket
  const getPocketEmoji = (type) => {
    switch (type) {
      case 'DONATION':
        return '🌳';
      case 'INVESTMENT_RESERVE':
        return '📈';
      default:
        return '💰';
    }
  };

  // Hooks pour Phase 3 SAKA : Compostage & Silo Commun
  const { data: silo, loading: isSiloLoading } = useSakaSilo();
  const { data: compost } = useSakaCompostPreview();

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

  return (
    <ErrorBoundary>
      <SEO
        title="Patrimoine Vivant - EGOEJO"
        description="Visualisez votre patrimoine : liquidités, pockets, dons, investissements et dividende social"
      />
      <div className="dashboard-page" style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }}>
        <h1 style={{ marginBottom: '2rem', fontSize: '2.5rem' }}>Patrimoine Vivant</h1>

        {/* Bandeau 4P / Triple capital */}
        <FourPStrip
          financial={parseFloat(assets.cash_balance || '0')}
          saka={assets.saka?.balance ?? null}
          impact={assets.impact_score ?? null}
        />

        {/* Notification : Vos grains vont retourner à la terre (Phase 3 SAKA) */}
        {compost?.enabled && compost?.eligible && compost.amount && compost.amount >= 20 && (
          <div
            style={{
              padding: '1rem 1.5rem',
              backgroundColor: '#fef3c7',
              border: '1px solid #fbbf24',
              borderRadius: 'var(--radius)',
              marginBottom: '2rem',
            }}
          >
            <h3 style={{ margin: 0, marginBottom: '0.5rem', fontSize: '1rem', fontWeight: '600', color: '#92400e' }}>
              🌾 Vos grains vont bientôt retourner à la terre
            </h3>
            <p style={{ margin: 0, fontSize: '0.875rem', color: '#78350f' }}>
              Si vous restez inactif, environ <strong>{compost.amount} SAKA</strong> seront compostés lors du prochain cycle pour nourrir le Silo Commun.
              {compost.days_until_eligible !== undefined && compost.days_until_eligible > 0 && (
                <> Il vous reste environ <strong>{compost.days_until_eligible} jour{compost.days_until_eligible > 1 ? 's' : ''}</strong> avant l'éligibilité.</>
              )}
              {' '}Vous pouvez encore les planter dans des votes ou des projets si vous le souhaitez.
            </p>
          </div>
        )}

        {/* Section Capital Vivant (SAKA) */}
        {assets.saka && (
          <section style={{ marginBottom: '3rem' }}>
            <h2 style={{ marginBottom: '1.5rem', fontSize: '1.8rem' }}>Capital Vivant (SAKA)</h2>
            <div
              style={{
                padding: '2rem',
                backgroundColor: 'var(--surface)',
                borderRadius: 'var(--radius)',
                marginBottom: '1.5rem',
                border: '1px solid var(--border)',
              }}
            >
              <p style={{ fontSize: '0.875rem', color: 'var(--muted)', marginBottom: '0.5rem' }}>
                Capital vivant (SAKA)
              </p>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
                <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--accent)' }}>
                  {assets.saka.balance ?? 0} <span style={{ fontSize: '1.5rem', fontWeight: 'normal' }}>SAKA</span>
                </div>
                <SakaSeasonBadge balance={assets.saka.balance ?? 0} />
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.5rem' }}>
                Grains récoltés à vie : {assets.saka.total_harvested ?? 0}
              </p>
              {(assets.saka.total_planted > 0 || assets.saka.total_composted > 0) && (
                <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--border)' }}>
                  {assets.saka.total_planted > 0 && (
                    <p style={{ fontSize: '0.75rem', color: 'var(--muted)', margin: '0.25rem 0' }}>
                      Grains plantés : {assets.saka.total_planted}
                    </p>
                  )}
                  {assets.saka.total_composted > 0 && (
                    <p style={{ fontSize: '0.75rem', color: 'var(--muted)', margin: '0.25rem 0' }}>
                      Grains compostés : {assets.saka.total_composted}
                    </p>
                  )}
                </div>
              )}
              <Link
                to="/saka/saisons"
                style={{
                  display: 'inline-block',
                  marginTop: '1rem',
                  padding: '0.75rem 1.5rem',
                  backgroundColor: 'transparent',
                  color: 'var(--accent)',
                  border: '1px solid var(--accent)',
                  borderRadius: 'var(--radius)',
                  textDecoration: 'none',
                  fontSize: '0.875rem',
                  fontWeight: '500',
                  cursor: 'pointer',
                }}
              >
                Saisons SAKA 🌾
              </Link>
            </div>
          </section>
        )}

        {/* Section Silo Commun (Phase 3 SAKA) */}
        {isSiloLoading ? (
          <section style={{ marginBottom: '3rem' }}>
            <h2 style={{ marginBottom: '1.5rem', fontSize: '1.8rem' }}>Silo Commun (Compost SAKA)</h2>
            <div
              style={{
                padding: '2rem',
                backgroundColor: 'var(--surface)',
                borderRadius: 'var(--radius)',
                border: '1px solid var(--border)',
                textAlign: 'center',
              }}
            >
              <Loader message="Chargement du Silo Commun..." />
            </div>
          </section>
        ) : silo?.enabled ? (
          <section style={{ marginBottom: '3rem' }}>
            <h2 style={{ marginBottom: '1.5rem', fontSize: '1.8rem' }}>Silo Commun (Compost SAKA)</h2>
            <div
              style={{
                padding: '2rem',
                backgroundColor: 'var(--surface)',
                borderRadius: 'var(--radius)',
                marginBottom: '1.5rem',
                border: '1px solid var(--border)',
              }}
            >
              <p style={{ fontSize: '0.875rem', color: 'var(--muted)', marginBottom: '0.5rem' }}>
                Silo Commun (Compost SAKA)
              </p>
              <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#84cc16', marginBottom: '0.5rem' }}>
                {silo.total_balance ?? 0} <span style={{ fontSize: '1.5rem', fontWeight: 'normal' }}>SAKA</span>
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.5rem' }}>
                Grains compostés à ce jour : {silo.total_composted ?? 0}
              </p>
              {silo.last_compost_at && (
                <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.5rem' }}>
                  Dernier cycle : {formatDate(silo.last_compost_at)}
                </p>
              )}
              <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', flexWrap: 'wrap' }}>
                <Link
                  to="/saka/silo"
                  style={{
                    display: 'inline-block',
                    padding: '0.75rem 1.5rem',
                    backgroundColor: 'transparent',
                    color: 'var(--accent)',
                    border: '1px solid var(--accent)',
                    borderRadius: 'var(--radius)',
                    textDecoration: 'none',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    cursor: 'pointer',
                  }}
                >
                  Voir le détail
                </Link>
                <Link
                  to="/saka/saisons"
                  style={{
                    display: 'inline-block',
                    padding: '0.75rem 1.5rem',
                    backgroundColor: 'transparent',
                    color: 'var(--accent)',
                    border: '1px solid var(--accent)',
                    borderRadius: 'var(--radius)',
                    textDecoration: 'none',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    cursor: 'pointer',
                  }}
                >
                  Saisons SAKA 🌾
                </Link>
              </div>
            </div>
          </section>
        ) : null}

        {/* Section Liquidités */}
        <section style={{ marginBottom: '3rem' }}>
          <h2 style={{ marginBottom: '1.5rem', fontSize: '1.8rem' }}>Liquidités</h2>
          <div
            style={{
              padding: '2rem',
              backgroundColor: 'var(--surface)',
              borderRadius: 'var(--radius)',
              marginBottom: '1.5rem',
            }}
          >
            <div style={{ fontSize: '3rem', fontWeight: 'bold', color: 'var(--accent)', marginBottom: '0.5rem' }}>
              {formatMoney(assets.cash_balance)}
            </div>
            <p style={{ color: 'var(--muted)' }}>Solde disponible</p>
          </div>

          {/* Pockets */}
          <h3 style={{ marginBottom: '1rem', fontSize: '1.3rem' }}>Pockets</h3>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
              gap: '1.5rem',
            }}
          >
            {assets.pockets?.map((pocket) => (
              <div
                key={pocket.name}
                style={{
                  padding: '1.5rem',
                  backgroundColor: 'var(--surface)',
                  borderRadius: 'var(--radius)',
                  border: '1px solid var(--border)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
                  <span style={{ fontSize: '2rem', marginRight: '0.5rem' }}>{getPocketEmoji(pocket.type)}</span>
                  <div>
                    <h4 style={{ margin: 0, fontSize: '1.1rem' }}>{pocket.name}</h4>
                    <span
                      style={{
                        display: 'inline-block',
                        padding: '0.25rem 0.5rem',
                        backgroundColor: pocket.type === 'DONATION' ? '#3b82f6' : '#f59e0b',
                        color: 'white',
                        borderRadius: '4px',
                        fontSize: '0.75rem',
                        marginTop: '0.25rem',
                      }}
                    >
                      {pocket.type === 'DONATION' ? 'Don' : 'Réserve Investissement'}
                    </span>
                  </div>
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', marginBottom: '1rem' }}>
                  {formatMoney(pocket.amount)}
                </div>
                <button
                  onClick={() => setTransferModal({ pocketId: pocket.id || pocket.name, pocketName: pocket.name })}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    backgroundColor: 'var(--accent)',
                    color: 'white',
                    border: 'none',
                    borderRadius: 'var(--radius)',
                    cursor: 'pointer',
                  }}
                >
                  Transférer des fonds
                </button>
              </div>
            ))}
            {(!assets.pockets || assets.pockets.length === 0) && (
              <p style={{ color: 'var(--muted)', gridColumn: '1 / -1' }}>Aucune pocket configurée</p>
            )}
          </div>
        </section>

        {/* Section Actifs (Graphique + Liste) */}
        <section style={{ marginBottom: '3rem' }}>
          <h2 style={{ marginBottom: '1.5rem', fontSize: '1.8rem' }}>Répartition des Actifs</h2>
          
          {filteredChartData.length > 0 ? (
            <div style={{ marginBottom: '2rem' }}>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={filteredChartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {filteredChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => formatMoney(String(value))} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p style={{ color: 'var(--muted)', textAlign: 'center', padding: '2rem' }}>
              Aucun actif à afficher
            </p>
          )}

          {/* Liste des actifs */}
          <div style={{ display: 'grid', gap: '1rem' }}>
            {/* Dons majeurs */}
            {parseFloat(assets.donations?.total_amount || '0') > 0 && (
              <div
                style={{
                  padding: '1.5rem',
                  backgroundColor: 'var(--surface)',
                  borderRadius: 'var(--radius)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <div>
                  <h4 style={{ margin: 0, marginBottom: '0.5rem' }}>Dons totaux</h4>
                  <p style={{ margin: 0, color: 'var(--muted)' }}>
                    {assets.donations.metrics_count || 0} projet(s) soutenu(s)
                  </p>
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                  {formatMoney(assets.donations.total_amount)}
                </div>
                <span
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    borderRadius: '4px',
                    fontSize: '0.875rem',
                  }}
                >
                  Mécène
                </span>
              </div>
            )}

            {/* Positions Equity */}
            {assets.equity_portfolio?.is_active &&
              assets.equity_portfolio.positions?.map((position) => (
                <div
                  key={position.project_id}
                  style={{
                    padding: '1.5rem',
                    backgroundColor: 'var(--surface)',
                    borderRadius: 'var(--radius)',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <div>
                    <h4 style={{ margin: 0, marginBottom: '0.5rem' }}>{position.project_title}</h4>
                    <p style={{ margin: 0, color: 'var(--muted)' }}>
                      {position.shares} part(s)
                    </p>
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
                    {formatMoney(position.valuation)}
                  </div>
                  <span
                    style={{
                      padding: '0.5rem 1rem',
                      backgroundColor: '#f59e0b',
                      color: 'white',
                      borderRadius: '4px',
                      fontSize: '0.875rem',
                    }}
                  >
                    Actionnaire
                  </span>
                </div>
              ))}
          </div>
        </section>

        {/* Section Dividende Social */}
        {parseFloat(assets.social_dividend?.estimated_value || '0') > 0 && (
          <section style={{ marginBottom: '3rem' }}>
            <h2 style={{ marginBottom: '1.5rem', fontSize: '1.8rem' }}>Dividende Social</h2>
            <div
              style={{
                padding: '2rem',
                backgroundColor: 'var(--surface)',
                borderRadius: 'var(--radius)',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--accent)', marginBottom: '0.5rem' }}>
                {formatMoney(assets.social_dividend.estimated_value)}
              </div>
              <p style={{ color: 'var(--muted)' }}>Valeur estimée de votre impact</p>
            </div>
          </section>
        )}

        {/* Modal de transfert (version simple pour mobile/desktop) */}
        {transferModal && (
          <TransferModal
            pocketName={transferModal.pocketName}
            onClose={() => setTransferModal(null)}
            onTransfer={(amount) => handleTransfer(transferModal.pocketId, amount)}
            maxAmount={toDecimal(assets.cash_balance)}
          />
        )}
      </div>
    </ErrorBoundary>
  );
}

/**
 * Modal simple pour le transfert de fonds
 */
function TransferModal({ pocketName, onClose, onTransfer, maxAmount }) {
  const [amount, setAmount] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!amount || parseFloat(amount) <= 0) {
      setError('Montant invalide');
      return;
    }

    const amountDecimal = toDecimal(amount);
    if (amountDecimal.gt(maxAmount)) {
      setError(`Montant supérieur au solde disponible (${formatMoney(maxAmount)})`);
      return;
    }

    setLoading(true);
    try {
      await onTransfer(amountDecimal);
    } catch (err) {
      setError(err.message || 'Erreur lors du transfert');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
      }}
      onClick={onClose}
    >
      <div
        style={{
          backgroundColor: 'var(--surface)',
          padding: '2rem',
          borderRadius: 'var(--radius)',
          maxWidth: '400px',
          width: '90%',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <h3 style={{ marginBottom: '1rem' }}>Transférer vers {pocketName}</h3>
        <form onSubmit={handleSubmit}>
          <label style={{ display: 'block', marginBottom: '0.5rem' }}>
            Montant (max: {formatMoney(maxAmount)})
          </label>
          <input
            type="number"
            step="0.01"
            min="0.01"
            max={maxAmount.toString()}
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            style={{
              width: '100%',
              padding: '0.75rem',
              marginBottom: '1rem',
              borderRadius: 'var(--radius)',
              border: '1px solid var(--border)',
            }}
            required
          />
          {error && <p style={{ color: 'red', marginBottom: '1rem' }}>{error}</p>}
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button
              type="button"
              onClick={onClose}
              style={{
                flex: 1,
                padding: '0.75rem',
                backgroundColor: 'var(--muted)',
                color: 'white',
                border: 'none',
                borderRadius: 'var(--radius)',
                cursor: 'pointer',
              }}
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              style={{
                flex: 1,
                padding: '0.75rem',
                backgroundColor: 'var(--accent)',
                color: 'white',
                border: 'none',
                borderRadius: 'var(--radius)',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.6 : 1,
              }}
            >
              {loading ? 'Transfert...' : 'Transférer'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

