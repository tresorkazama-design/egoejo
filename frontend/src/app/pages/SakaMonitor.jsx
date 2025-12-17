/**
 * Page "Saka Monitor" - Monitoring & KPIs du Protocole SAKA 🌾
 * Réservée aux administrateurs
 */
import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { useSakaStats, useSakaCompostLogs, useSakaCompostRun } from '../../hooks/useSaka';
import { useNotificationContext } from '../../contexts/NotificationContext';
import { fetchAPI } from '../../utils/api';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';
import SEO from '../../components/SEO';
import ErrorBoundary from '../../components/ErrorBoundary';
import { Loader } from '../../components/Loader';
import { Button } from '../../components/Button';

export default function SakaMonitor() {
  const { user } = useAuth();
  const { language } = useLanguage();
  
  // États locaux pour les filtres
  const [days, setDays] = useState(30);
  const [limit, setLimit] = useState(10);
  
  const { data: stats, loading, error, refetch } = useSakaStats(days, limit);
  const { data: compostLogs, loading: isCompostLogsLoading, refetch: refetchCompostLogs } = useSakaCompostLogs(10);
  const { runCompostDryRun, isRunning: isRunningCompost } = useSakaCompostRun();
  const { showSuccess, showError, showInfo } = useNotificationContext();

  // Vérifier si l'utilisateur est admin
  const isAdmin = user && (user.is_staff || user.is_superuser);

  if (!user) {
    return (
      <ErrorBoundary>
        <SEO
          title="Saka Monitor - EGOEJO"
          description="Monitoring et KPIs du Protocole SAKA"
        />
        <div className="saka-monitor-page" style={{ padding: '2rem', textAlign: 'center' }}>
          <p>Veuillez vous connecter pour accéder au monitoring SAKA.</p>
        </div>
      </ErrorBoundary>
    );
  }

  if (!isAdmin) {
    return (
      <ErrorBoundary>
        <SEO
          title="Saka Monitor - EGOEJO"
          description="Monitoring et KPIs du Protocole SAKA"
        />
        <div className="saka-monitor-page" style={{ padding: '2rem', textAlign: 'center' }}>
          <p style={{ color: 'red' }}>Accès réservé aux administrateurs.</p>
        </div>
      </ErrorBoundary>
    );
  }

  // Afficher le loader seulement lors du premier chargement (pas lors du refetch)
  const isInitialLoad = loading && !stats;

  if (isInitialLoad) {
    return (
      <ErrorBoundary>
        <SEO
          title="Saka Monitor - EGOEJO"
          description="Monitoring et KPIs du Protocole SAKA"
        />
        <div className="saka-monitor-page" style={{ padding: '2rem', textAlign: 'center' }}>
          <Loader message="Chargement des statistiques SAKA…" />
        </div>
      </ErrorBoundary>
    );
  }

  if (error) {
    return (
      <ErrorBoundary>
        <SEO
          title="Saka Monitor - EGOEJO"
          description="Monitoring et KPIs du Protocole SAKA"
        />
        <div className="saka-monitor-page" style={{ padding: '2rem', textAlign: 'center' }}>
          <p style={{ color: 'red' }}>{error}</p>
          <button
            onClick={refetch}
            style={{
              marginTop: '1rem',
              padding: '0.75rem 1.5rem',
              backgroundColor: 'var(--accent)',
              color: 'white',
              border: 'none',
              borderRadius: 'var(--radius)',
              cursor: 'pointer',
            }}
          >
            Réessayer
          </button>
        </div>
      </ErrorBoundary>
    );
  }

  if (!stats || !stats.enabled) {
    return (
      <ErrorBoundary>
        <SEO
          title="Saka Monitor - EGOEJO"
          description="Monitoring et KPIs du Protocole SAKA"
        />
        <div className="saka-monitor-page" style={{ padding: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
          <h1 style={{ marginBottom: '1rem', fontSize: '2rem' }}>Saka Monitor</h1>
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
            <p>Le protocole SAKA n'est pas encore activé sur cet environnement.</p>
          </div>
        </div>
      </ErrorBoundary>
    );
  }

  const { global, daily, top_users, top_projects } = stats;

  return (
    <ErrorBoundary>
      <SEO
        title="Saka Monitor - EGOEJO"
        description="Monitoring et KPIs du Protocole SAKA"
      />
      <div className="saka-monitor-page" style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto', position: 'relative' }}>
        {/* Overlay de chargement lors du refetch */}
        {loading && stats && (
          <div
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(255, 255, 255, 0.7)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 10,
              borderRadius: 'var(--radius)',
            }}
          >
            <div style={{ textAlign: 'center' }}>
              <Loader message="Actualisation des données…" />
            </div>
          </div>
        )}

        {/* En-tête avec filtres */}
        <section
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '1rem',
            marginBottom: '2rem',
          }}
        >
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              gap: '1rem',
            }}
          >
            <div>
              <h1 style={{ marginBottom: '0.5rem', fontSize: '2rem' }}>Saka Monitor 🌾</h1>
              <p style={{ fontSize: '0.875rem', color: 'var(--muted)' }}>
                Surveille l'économie vivante SAKA (grains récoltés, plantés, compostés).
              </p>
            </div>

            <div
              style={{
                display: 'flex',
                gap: '1rem',
                alignItems: 'center',
                flexWrap: 'wrap',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>Période :</span>
                <select
                  value={days}
                  onChange={(e) => setDays(Number(e.target.value))}
                  style={{
                    padding: '0.5rem',
                    borderRadius: 'var(--radius)',
                    border: '1px solid var(--border)',
                    backgroundColor: 'var(--surface)',
                    color: 'var(--text)',
                    fontSize: '0.875rem',
                    cursor: 'pointer',
                  }}
                >
                  <option value={7}>7 jours</option>
                  <option value={30}>30 jours</option>
                  <option value={90}>90 jours</option>
                </select>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--muted)' }}>Top :</span>
                <select
                  value={limit}
                  onChange={(e) => setLimit(Number(e.target.value))}
                  style={{
                    padding: '0.5rem',
                    borderRadius: 'var(--radius)',
                    border: '1px solid var(--border)',
                    backgroundColor: 'var(--surface)',
                    color: 'var(--text)',
                    fontSize: '0.875rem',
                    cursor: 'pointer',
                  }}
                >
                  <option value={5}>Top 5</option>
                  <option value={10}>Top 10</option>
                  <option value={20}>Top 20</option>
                </select>
              </div>
              {/* Bouton Dry-run compost, seulement si SAKA activé */}
              {stats?.enabled && (
                <Button
                  variant="outline"
                  disabled={isRunningCompost}
                  onClick={async () => {
                    try {
                      const res = await runCompostDryRun();
                      if (res?.ok) {
                        showSuccess(
                          `🌾 Dry-run compost lancé : ${res.wallets_affected} wallets affectés, ${res.total_composted} SAKA seraient compostés.`,
                          6000
                        );
                        // Refetch des logs et stats
                        refetchCompostLogs();
                        refetch();
                      } else {
                        showError(
                          res?.reason === 'SAKA_PROTOCOL_DISABLED'
                            ? 'Le protocole SAKA n\'est pas activé.'
                            : res?.reason === 'SAKA_COMPOST_DISABLED'
                            ? 'Le compostage SAKA n\'est pas activé.'
                            : 'Le cycle de compost n\'a pas pu être lancé.',
                          5000
                        );
                      }
                    } catch (err) {
                      console.error('Erreur lors du dry-run compost:', err);
                      showError(
                        'Impossible de lancer le cycle de compost. Vérifiez que vous êtes administrateur et que le protocole SAKA est activé.',
                        5000
                      );
                    }
                  }}
                  style={{
                    fontSize: '0.875rem',
                    padding: '0.5rem 1rem',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {isRunningCompost ? 'Simulation en cours…' : 'Lancer un dry-run maintenant'}
                </Button>
              )}
            </div>
          </div>
        </section>

        {/* Cartes globales */}
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
            <p style={{ fontSize: '0.875rem', color: 'var(--muted)', marginBottom: '0.5rem' }}>
              Utilisateurs avec SAKA
            </p>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--accent)' }}>
              {global.total_users_with_saka}
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
            <p style={{ fontSize: '0.875rem', color: 'var(--muted)', marginBottom: '0.5rem' }}>
              Total de grains en circulation
            </p>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--accent)' }}>
              {global.total_balance} SAKA
            </p>
            <p style={{ fontSize: '0.75rem', color: 'var(--muted)', marginTop: '0.5rem' }}>
              Moyenne par utilisateur : {global.avg_balance.toFixed(1)} SAKA
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
            <p style={{ fontSize: '0.875rem', color: 'var(--muted)', marginBottom: '0.5rem' }}>
              Grains compostés (Silo)
            </p>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#84cc16' }}>
              {global.total_composted} SAKA
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
            <p style={{ fontSize: '0.875rem', color: 'var(--muted)', marginBottom: '0.5rem' }}>
              Total récolté (EARN)
            </p>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#10b981' }}>
              {global.total_earned} SAKA
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
            <p style={{ fontSize: '0.875rem', color: 'var(--muted)', marginBottom: '0.5rem' }}>
              Total planté (SPEND)
            </p>
            <p style={{ fontSize: '2rem', fontWeight: 'bold', color: '#f59e0b' }}>
              {global.total_spent} SAKA
            </p>
          </div>
        </section>

        {/* Graphique des flux quotidiens */}
        <section style={{ marginBottom: '3rem' }}>
          <h2 style={{ marginBottom: '1.5rem', fontSize: '1.8rem' }}>
            Flux quotidiens ({days} jour{days > 1 ? 's' : ''})
          </h2>
          <div
            style={{
              padding: '2rem',
              backgroundColor: 'var(--surface)',
              borderRadius: 'var(--radius)',
              border: '1px solid var(--border)',
              height: '400px',
            }}
          >
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={daily}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis
                  dataKey="date"
                  stroke="var(--text)"
                  style={{ fontSize: '0.75rem' }}
                  tickFormatter={(value) => {
                    // Formater la date pour l'affichage (ex: "2025-01-27" -> "27/01")
                    const date = new Date(value);
                    return `${date.getDate()}/${date.getMonth() + 1}`;
                  }}
                />
                <YAxis stroke="var(--text)" style={{ fontSize: '0.75rem' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--surface)',
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius)',
                  }}
                  labelFormatter={(value) => {
                    const date = new Date(value);
                    return date.toLocaleDateString('fr-FR', {
                      day: 'numeric',
                      month: 'long',
                      year: 'numeric',
                    });
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="earned"
                  name="Récolté"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="spent"
                  name="Planté (dépensé)"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  dot={{ r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="net"
                  name="Net"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={{ r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>

        {/* Top utilisateurs et projets */}
        <section
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
            gap: '2rem',
            marginBottom: '3rem',
          }}
        >
          {/* Top utilisateurs */}
          <div
            style={{
              padding: '2rem',
              backgroundColor: 'var(--surface)',
              borderRadius: 'var(--radius)',
              border: '1px solid var(--border)',
            }}
          >
            <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem' }}>
              Top utilisateurs (Grands jardiniers)
            </h2>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', fontSize: '0.875rem' }}>
                <thead>
                  <tr style={{ textAlign: 'left', borderBottom: '1px solid var(--border)' }}>
                    <th style={{ padding: '0.75rem 0.5rem', fontSize: '0.75rem', color: 'var(--muted)' }}>
                      Utilisateur
                    </th>
                    <th style={{ padding: '0.75rem 0.5rem', fontSize: '0.75rem', color: 'var(--muted)' }}>
                      Récolté
                    </th>
                    <th style={{ padding: '0.75rem 0.5rem', fontSize: '0.75rem', color: 'var(--muted)' }}>
                      Planté
                    </th>
                    <th style={{ padding: '0.75rem 0.5rem', fontSize: '0.75rem', color: 'var(--muted)' }}>
                      Solde
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {top_users.length > 0 ? (
                    top_users.map((u) => (
                      <tr
                        key={u.user_id}
                        style={{ borderBottom: '1px solid var(--border)' }}
                      >
                        <td style={{ padding: '0.75rem 0.5rem' }}>{u.username}</td>
                        <td style={{ padding: '0.75rem 0.5rem' }}>{u.total_harvested}</td>
                        <td style={{ padding: '0.75rem 0.5rem' }}>{u.total_planted}</td>
                        <td style={{ padding: '0.75rem 0.5rem', fontWeight: 'bold' }}>
                          {u.balance}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="4" style={{ padding: '1rem', textAlign: 'center', color: 'var(--muted)' }}>
                        Aucun utilisateur avec SAKA
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Top projets */}
          <div
            style={{
              padding: '2rem',
              backgroundColor: 'var(--surface)',
              borderRadius: 'var(--radius)',
              border: '1px solid var(--border)',
            }}
          >
            <h2 style={{ marginBottom: '1.5rem', fontSize: '1.5rem' }}>Top projets nourris</h2>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', fontSize: '0.875rem' }}>
                <thead>
                  <tr style={{ textAlign: 'left', borderBottom: '1px solid var(--border)' }}>
                    <th style={{ padding: '0.75rem 0.5rem', fontSize: '0.75rem', color: 'var(--muted)' }}>
                      Projet
                    </th>
                    <th style={{ padding: '0.75rem 0.5rem', fontSize: '0.75rem', color: 'var(--muted)' }}>
                      Grains reçus
                    </th>
                    <th style={{ padding: '0.75rem 0.5rem', fontSize: '0.75rem', color: 'var(--muted)' }}>
                      Supporters
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {top_projects.length > 0 ? (
                    top_projects.map((p) => (
                      <tr
                        key={p.project_id}
                        style={{ borderBottom: '1px solid var(--border)' }}
                      >
                        <td style={{ padding: '0.75rem 0.5rem' }}>{p.name}</td>
                        <td style={{ padding: '0.75rem 0.5rem', fontWeight: 'bold' }}>
                          {p.saka_nourished}
                        </td>
                        <td style={{ padding: '0.75rem 0.5rem' }}>
                          {p.supporters_count ?? '-'}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="3" style={{ padding: '1rem', textAlign: 'center', color: 'var(--muted)' }}>
                        Aucun projet nourri avec SAKA
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </section>

        {/* Derniers cycles de compost */}
        <section style={{ marginBottom: '3rem' }}>
          <h2 style={{ marginBottom: '1.5rem', fontSize: '1.8rem' }}>Derniers cycles de compost</h2>
          <div
            style={{
              padding: '2rem',
              backgroundColor: 'var(--surface)',
              borderRadius: 'var(--radius)',
              border: '1px solid var(--border)',
            }}
          >
            {isCompostLogsLoading && (
              <div style={{ fontSize: '0.875rem', color: 'var(--muted)', textAlign: 'center', padding: '2rem' }}>
                Chargement des cycles de compost…
              </div>
            )}

            {!isCompostLogsLoading && (!compostLogs || compostLogs.length === 0) && (
              <div style={{ fontSize: '0.875rem', color: 'var(--muted)', textAlign: 'center', padding: '2rem' }}>
                Aucun cycle de compost enregistré pour le moment.
              </div>
            )}

            {!isCompostLogsLoading && compostLogs && compostLogs.length > 0 && (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', fontSize: '0.875rem' }}>
                  <thead>
                    <tr style={{ textAlign: 'left', borderBottom: '1px solid var(--border)' }}>
                      <th style={{ padding: '0.75rem 0.5rem', fontSize: '0.75rem', color: 'var(--muted)' }}>#</th>
                      <th style={{ padding: '0.75rem 0.5rem', fontSize: '0.75rem', color: 'var(--muted)' }}>Début</th>
                      <th style={{ padding: '0.75rem 0.5rem', fontSize: '0.75rem', color: 'var(--muted)' }}>Fin</th>
                      <th style={{ padding: '0.75rem 0.5rem', fontSize: '0.75rem', color: 'var(--muted)' }}>Mode</th>
                      <th style={{ padding: '0.75rem 0.5rem', fontSize: '0.75rem', color: 'var(--muted)' }}>Wallets</th>
                      <th style={{ padding: '0.75rem 0.5rem', fontSize: '0.75rem', color: 'var(--muted)' }}>Composté</th>
                      <th style={{ padding: '0.75rem 0.5rem', fontSize: '0.75rem', color: 'var(--muted)' }}>Source</th>
                    </tr>
                  </thead>
                  <tbody>
                    {compostLogs.map((log) => {
                      // Style de ligne selon le mode : dry-run = gris clair, live = normal
                      const rowStyle = log.dry_run
                        ? {
                            backgroundColor: '#f8fafc',
                            color: '#64748b',
                            borderBottom: '1px solid var(--border)',
                          }
                        : {
                            backgroundColor: 'var(--surface)',
                            color: 'var(--text)',
                            borderBottom: '1px solid var(--border)',
                          };

                      return (
                        <tr key={log.id} style={rowStyle}>
                          <td style={{ padding: '0.75rem 0.5rem', fontSize: '0.75rem', color: 'var(--muted)' }}>
                            #{log.id}
                          </td>
                          <td style={{ padding: '0.75rem 0.5rem' }}>
                            {log.started_at
                              ? new Date(log.started_at).toLocaleString('fr-FR', {
                                  day: '2-digit',
                                  month: '2-digit',
                                  year: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit',
                                })
                              : '—'}
                          </td>
                          <td style={{ padding: '0.75rem 0.5rem' }}>
                            {log.finished_at
                              ? new Date(log.finished_at).toLocaleString('fr-FR', {
                                  day: '2-digit',
                                  month: '2-digit',
                                  year: 'numeric',
                                  hour: '2-digit',
                                  minute: '2-digit',
                                })
                              : '—'}
                          </td>
                          <td style={{ padding: '0.75rem 0.5rem' }}>
                            {log.dry_run ? (
                              <span
                                style={{
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  borderRadius: '9999px',
                                  backgroundColor: '#f1f5f9',
                                  padding: '0.125rem 0.5rem',
                                  fontSize: '10px',
                                  fontWeight: '500',
                                  color: '#475569',
                                  border: '1px solid #e2e8f0',
                                }}
                              >
                                DRY-RUN
                              </span>
                            ) : (
                              <span
                                style={{
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  borderRadius: '9999px',
                                  backgroundColor: '#d1fae5',
                                  padding: '0.125rem 0.5rem',
                                  fontSize: '10px',
                                  fontWeight: '500',
                                  color: '#065f46',
                                  border: '1px solid #a7f3d0',
                                }}
                              >
                                LIVE
                              </span>
                            )}
                          </td>
                          <td style={{ padding: '0.75rem 0.5rem' }}>{log.wallets_affected}</td>
                          <td style={{ padding: '0.75rem 0.5rem', fontWeight: 'bold' }}>
                            {log.total_composted} SAKA
                          </td>
                          <td style={{ padding: '0.75rem 0.5rem', fontSize: '0.75rem', color: 'var(--muted)' }}>
                            {log.source}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </section>
      </div>
    </ErrorBoundary>
  );
}

