/**
 * Composant pour afficher les suggestions sémantiques
 * Affiche des contenus/projets liés conceptuellement
 */
import { useState, useEffect } from 'react';
import { fetchAPI } from '../utils/api';
import { Link } from 'react-router-dom';

export default function SemanticSuggestions({ projetId, contentId, limit = 5 }) {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!projetId && !contentId) return;

    const loadSuggestions = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        if (projetId) params.append('projet_id', projetId);
        if (contentId) params.append('content_id', contentId);
        params.append('limit', limit);

        const data = await fetchAPI(`/projets/semantic-suggestions/?${params}`);
        setSuggestions(data.suggestions || []);
      } catch (error) {
        console.error('Erreur chargement suggestions:', error);
        setSuggestions([]);
      } finally {
        setLoading(false);
      }
    };

    loadSuggestions();
  }, [projetId, contentId, limit]);

  if (loading) {
    return <div className="semantic-suggestions loading">Chargement des suggestions...</div>;
  }

  if (suggestions.length === 0) {
    return null;
  }

  return (
    <div className="semantic-suggestions">
      <h3 className="semantic-suggestions__title">Suggestions liées</h3>
      <div className="semantic-suggestions__list">
        {suggestions.map((suggestion, index) => (
          <div key={index} className="semantic-suggestions__item">
            {/* CONVENTION NAVIGATION : Utiliser <Link> pour les routes internes */}
            <Link to={suggestion.url} className="semantic-suggestions__link">
              <span className="semantic-suggestions__type">
                {suggestion.type === 'projet' ? '📁 Projet' : '📚 Contenu'}
              </span>
              <span className="semantic-suggestions__title">
                {suggestion.titre || suggestion.title}
              </span>
              {suggestion.similarity && (
                <span className="semantic-suggestions__similarity">
                  {Math.round(suggestion.similarity * 100)}% de similarité
                </span>
              )}
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}

