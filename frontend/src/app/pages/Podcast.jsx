/**
 * Page "Podcast" - Liste des contenus avec versions audio
 * Permet d'écouter les contenus éducatifs en mode audio
 */
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { fetchAPI } from '../../utils/api';
import AudioPlayer from '../../components/AudioPlayer';
import { useSEO } from '../../hooks/useSEO';
import { sanitizeContent } from '../../utils/content';

export default function Podcast() {
  useSEO({
    title: 'Podcast - EGOEJO',
    description: 'Écoutez les contenus éducatifs en mode audio, idéal pour le terrain',
  });

  const [contenus, setContenus] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedContent, setSelectedContent] = useState(null);

  useEffect(() => {
    const loadContenus = async () => {
      try {
        const data = await fetchAPI('/contents/?status=published');
        // Filtrer uniquement ceux avec audio
        const avecAudio = data.filter(c => c.audio_file);
        setContenus(avecAudio);
      } catch (error) {
        console.error('Erreur chargement contenus:', error);
      } finally {
        setLoading(false);
      }
    };

    loadContenus();
  }, []);

  if (loading) {
    return <div className="podcast-loading">Chargement des podcasts...</div>;
  }

  return (
    <div className="page-podcast">
      <div className="podcast-header">
        <h1>Podcast EGOEJO</h1>
        <p>
          Écoutez nos contenus éducatifs en mode audio, idéal pour le terrain.
          Les mains dans la terre, les oreilles dans le savoir.
        </p>
      </div>

      <div className="podcast-list">
        {contenus.length === 0 ? (
          <div className="podcast-empty">
            <p>Aucun contenu audio disponible pour le moment.</p>
            <p>Les versions audio sont générées automatiquement lors de la publication.</p>
          </div>
        ) : (
          contenus.map((contenu) => (
            <div key={contenu.id} className="podcast-item">
              <div className="podcast-item__header">
                <h3>{sanitizeContent(contenu.title)}</h3>
                <span className="podcast-item__type">{sanitizeContent(contenu.type)}</span>
              </div>
              {contenu.description && (
                <p className="podcast-item__description">{sanitizeContent(contenu.description)}</p>
              )}
              <AudioPlayer
                contentId={contenu.id}
                autoPlay={selectedContent === contenu.id}
              />
              {/* CONVENTION NAVIGATION : Utiliser <Link> pour les routes internes */}
              <Link to={`/contenus/${contenu.slug}`} className="btn btn-ghost">
                Voir le contenu complet
              </Link>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

