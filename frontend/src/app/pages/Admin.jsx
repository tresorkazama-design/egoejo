import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { t } from '../../utils/i18n';
import { Loader } from '../../components/Loader';
import { Button } from '../../components/Button';
import { Input } from '../../components/Input';
import { fetchAPI, handleAPIError } from '../../utils/api';
import { useSakaStats } from '../../hooks/useSaka';

export const Admin = () => {
  const { token, user } = useAuth();
  const { language } = useLanguage();
  const [intents, setIntents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    search: '',
    profil: '',
    dateFrom: '',
    dateTo: ''
  });
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Hook pour les stats SAKA (snapshot 7 jours, top 5)
  const { data: sakaStats, loading: isSakaStatsLoading } = useSakaStats(7, 5);

  useEffect(() => {
    if (token) {
      loadIntents();
    }
  }, [token, currentPage, filters]);

  const loadIntents = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        page: currentPage.toString(),
        ...Object.fromEntries(
          Object.entries(filters).filter(([_, v]) => v)
        )
      });
      
      const data = await fetchAPI(`/intents/admin/?${params}`);
      setIntents(data.results || data || []);
      setTotalPages(data.total_pages || 1);
    } catch (err) {
      setError(handleAPIError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm(t("admin.delete_confirm", language))) {
      return;
    }

    try {
      await fetchAPI(`/intents/${id}/delete/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${import.meta.env.VITE_ADMIN_TOKEN || ''}`
        }
      });
      loadIntents();
    } catch (err) {
      setError(handleAPIError(err));
    }
  };

  const handleExport = async () => {
    try {
      const params = new URLSearchParams(
        Object.fromEntries(
          Object.entries(filters).filter(([_, v]) => v)
        )
      );
      const apiBase = import.meta.env.VITE_API_URL 
        ? `${import.meta.env.VITE_API_URL}/api` 
        : 'http://localhost:8000/api';
      const response = await fetch(
        `${apiBase}/intents/export/?${params}`,
        {
          headers: {
            'Authorization': `Bearer ${process.env.REACT_APP_ADMIN_TOKEN || ''}`
          }
        }
      );
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'intents.csv';
      a.click();
    } catch (err) {
      setError(handleAPIError(err));
    }
  };

  if (!token) {
    return (
      <div className="admin-page" data-testid="admin-page">
        <p>{t("admin.login_required", language)}</p>
      </div>
    );
  }

  if (loading && intents.length === 0) {
    return (
      <div className="admin-page" data-testid="admin-page">
        <Loader fullScreen message={t("common.loading", language)} />
      </div>
    );
  }

  // Vérifier si l'utilisateur est admin
  const isAdmin = user && (user.is_staff || user.is_superuser);

  return (
    <div className="admin-page" data-testid="admin-page" role="main" aria-label={t("admin.title", language)}>
      <h1 className="text-3xl font-bold mb-6">{t("admin.title", language)}</h1>

      {/* Widget Santé SAKA (fondateur uniquement) */}
      {isAdmin && (
        <section
          style={{
            marginBottom: '2rem',
            padding: '1.5rem',
            backgroundColor: 'var(--surface)',
            borderRadius: 'var(--radius)',
            border: '1px solid var(--border)',
          }}
        >
          <h2 style={{ marginBottom: '1rem', fontSize: '1.25rem', fontWeight: '600' }}>
            Santé SAKA (7 derniers jours) 🌾
          </h2>

          {isSakaStatsLoading && (
            <p style={{ fontSize: '0.875rem', color: 'var(--muted)' }}>Analyse en cours…</p>
          )}

          {!isSakaStatsLoading && sakaStats && sakaStats.enabled && (
            <>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1rem' }}>
                <p style={{ fontSize: '0.875rem', color: 'var(--muted)' }}>
                  Grains récoltés (7j) :{' '}
                  <span style={{ fontWeight: '600' }}>
                    {sakaStats.daily.reduce((sum, d) => sum + d.earned, 0)} SAKA
                  </span>
                </p>
                <p style={{ fontSize: '0.875rem', color: 'var(--muted)' }}>
                  Grains plantés (7j) :{' '}
                  <span style={{ fontWeight: '600' }}>
                    {sakaStats.daily.reduce((sum, d) => sum + d.spent, 0)} SAKA
                  </span>
                </p>
                <p style={{ fontSize: '0.875rem', color: 'var(--muted)' }}>
                  Balance nette (7j) :{' '}
                  <span
                    style={{
                      fontWeight: '600',
                      color: (() => {
                        const net = sakaStats.daily.reduce((sum, d) => sum + d.net, 0);
                        return net >= 0 ? '#10b981' : '#f59e0b';
                      })(),
                    }}
                  >
                    {(() => {
                      const net = sakaStats.daily.reduce((sum, d) => sum + d.net, 0);
                      return net >= 0 ? '+' : '';
                    })()}
                    {sakaStats.daily.reduce((sum, d) => sum + d.net, 0)} SAKA
                  </span>
                </p>
              </div>

              <div
                style={{
                  padding: '0.75rem',
                  borderRadius: 'var(--radius)',
                  backgroundColor: (() => {
                    const net = sakaStats.daily.reduce((sum, d) => sum + d.net, 0);
                    if (net > 0) return '#d1fae5';
                    if (net < 0) return '#fef3c7';
                    return '#f3f4f6';
                  })(),
                }}
              >
                {(() => {
                  const net = sakaStats.daily.reduce((sum, d) => sum + d.net, 0);
                  if (net > 0) {
                    return (
                      <p style={{ fontSize: '0.875rem', color: '#065f46', margin: 0 }}>
                        ✅ Économie vivante en croissance (plus de grains récoltés que plantés).
                      </p>
                    );
                  }
                  if (net < 0) {
                    return (
                      <p style={{ fontSize: '0.875rem', color: '#92400e', margin: 0 }}>
                        ⚠️ Beaucoup de grains sont plantés : surveille l'équilibre récolte / usage.
                      </p>
                    );
                  }
                  return (
                    <p style={{ fontSize: '0.875rem', color: 'var(--muted)', margin: 0 }}>
                      ℹ️ Économie stable sur 7 jours (entrées ≈ sorties).
                    </p>
                  );
                })()}
              </div>
            </>
          )}

          {!isSakaStatsLoading && (!sakaStats || !sakaStats.enabled) && (
            <p style={{ fontSize: '0.875rem', color: 'var(--muted)' }}>
              Le protocole SAKA n'est pas encore activé sur cet environnement.
            </p>
          )}
        </section>
      )}

      <section className="mb-6" aria-label={t("admin.filters", language) || t("admin.search", language)} role="search">
        <div className="flex gap-4 flex-wrap">
          <Input
            label={t("admin.search", language)}
            name="search"
            id="admin-search"
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            placeholder={t("admin.search_placeholder", language)}
            aria-describedby="admin-search-desc"
            data-testid="admin-search-input"
          />
          <div className="mb-4">
            <label htmlFor="admin-profil" className="block text-sm font-medium mb-1">{t("admin.profil", language)}</label>
            <select
              id="admin-profil"
              value={filters.profil}
              onChange={(e) => setFilters({ ...filters, profil: e.target.value })}
              className="w-full px-3 py-2 border rounded-md"
              aria-label={t("admin.profil", language)}
              data-testid="admin-profil-filter"
            >
            <option value="">{t("admin.profil_all", language)}</option>
            <option value="je-decouvre">{t("admin.profil_decouvre", language)}</option>
            <option value="je-participe">{t("admin.profil_participe", language)}</option>
            <option value="je-contribue">{t("admin.profil_contribue", language)}</option>
          </select>
        </div>
          <Button onClick={handleExport} aria-label={t("admin.export_csv", language)} data-testid="admin-export-button">{t("admin.export_csv", language)}</Button>
        </div>
      </section>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded" role="alert" aria-live="polite">
          {error}
        </div>
      )}

      <section aria-label={t("admin.table_title", language) || t("admin.title", language)}>
        <div className="overflow-x-auto">
          <table className="min-w-full border-collapse border border-gray-300" role="table" aria-label={t("admin.table_title", language) || t("admin.intents_list", language)} data-testid="admin-table">
            <thead>
              <tr className="bg-gray-100" role="row" data-testid="admin-table-header">
                  <th className="border border-gray-300 px-4 py-2" scope="col" data-testid="admin-table-header-id">{t("admin.table_id", language)}</th>
                <th className="border border-gray-300 px-4 py-2" scope="col" data-testid="admin-table-header-nom">{t("admin.table_nom", language)}</th>
                <th className="border border-gray-300 px-4 py-2" scope="col" data-testid="admin-table-header-email">{t("admin.table_email", language)}</th>
                <th className="border border-gray-300 px-4 py-2" scope="col" data-testid="admin-table-header-profil">{t("admin.table_profil", language)}</th>
                <th className="border border-gray-300 px-4 py-2" scope="col" data-testid="admin-table-header-date">{t("admin.table_date", language)}</th>
                <th className="border border-gray-300 px-4 py-2" scope="col" data-testid="admin-table-header-actions">{t("admin.table_actions", language)}</th>
            </tr>
          </thead>
            <tbody>
              {intents.map((intent) => (
                <tr key={intent.id} data-testid={`intent-${intent.id}`} role="row">
                  <td className="border border-gray-300 px-4 py-2" role="gridcell">{intent.id}</td>
                  <td className="border border-gray-300 px-4 py-2" role="gridcell">{intent.nom}</td>
                  <td className="border border-gray-300 px-4 py-2" role="gridcell">{intent.email}</td>
                  <td className="border border-gray-300 px-4 py-2" role="gridcell">{intent.profil}</td>
                  <td className="border border-gray-300 px-4 py-2" role="gridcell">
                    {new Date(intent.date_creation || intent.created_at).toLocaleDateString('fr-FR')}
                  </td>
                  <td className="border border-gray-300 px-4 py-2" role="gridcell">
                    <Button
                      variant="danger"
                      onClick={() => handleDelete(intent.id)}
                      aria-label={`${t("admin.delete", language)} ${t("admin.intent", language)} ${intent.id}`}
                    >
                      {t("admin.delete", language)}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {totalPages > 1 && (
        <nav className="mt-6 flex justify-center gap-2" aria-label={t("admin.pagination", language) || t("admin.page", language)} role="navigation">
          <Button
            disabled={currentPage === 1}
            onClick={() => setCurrentPage(p => p - 1)}
            aria-label={t("admin.previous", language)}
          >
            {t("admin.previous", language)}
          </Button>
          <span className="px-4 py-2" aria-current="page" aria-label={`${t("admin.page", language)} ${currentPage} ${t("admin.page_of", language)} ${totalPages}`}>
            {t("admin.page", language)} {currentPage} {t("admin.page_of", language)} {totalPages}
          </span>
          <Button
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage(p => p + 1)}
            aria-label={t("admin.next", language)}
          >
            {t("admin.next", language)}
          </Button>
        </nav>
      )}
    </div>
  );
};

export default Admin;

