/**
 * Composant pour recherche sémantique
 * Recherche conceptuelle (pas juste mots-clés)
 */
import { useState } from 'react';
import { fetchAPI } from '../utils/api';
import { Link } from 'react-router-dom';

export default function SemanticSearch({ onResultSelect }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchType, setSearchType] = useState('both'); // 'projet', 'content', 'both'

  const handleSearch = async (e) => {
    e.preventDefault();
    if (query.length < 2) return;

    setLoading(true);
    try {
      const params = new URLSearchParams({
        q: query,
        type: searchType
      });

      const data = await fetchAPI(`/projets/semantic-search/?${params}`);
      setResults(data.results || []);
    } catch (error) {
      console.error('Erreur recherche sémantique:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="semantic-search">
      <form onSubmit={handleSearch} className="semantic-search__form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Recherche sémantique (concepts, pas juste mots-clés)..."
          className="semantic-search__input"
          minLength={2}
        />
        <select
          value={searchType}
          onChange={(e) => setSearchType(e.target.value)}
          className="semantic-search__type"
        >
          <option value="both">Tout</option>
          <option value="projet">Projets</option>
          <option value="content">Contenus</option>
        </select>
        <button type="submit" disabled={loading || query.length < 2} className="btn btn-primary">
          {loading ? 'Recherche...' : 'Rechercher'}
        </button>
      </form>

      {results.length > 0 && (
        <div className="semantic-search__results">
          <h3>Résultats ({results.length})</h3>
          {results.map((result, index) => (
            <div key={index} className="semantic-search__result">
              <Link
                to={result.url}
                onClick={() => onResultSelect && onResultSelect(result)}
                className="semantic-search__result-link"
              >
                <span className="semantic-search__result-type">
                  {result.type === 'projet' ? '📁 Projet' : '📚 Contenu'}
                </span>
                <span className="semantic-search__result-title">
                  {result.titre || result.title}
                </span>
                {result.description && (
                  <p className="semantic-search__result-description">{result.description}</p>
                )}
                {result.similarity && (
                  <span className="semantic-search__result-similarity">
                    Similarité: {Math.round(result.similarity * 100)}%
                  </span>
                )}
              </Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

