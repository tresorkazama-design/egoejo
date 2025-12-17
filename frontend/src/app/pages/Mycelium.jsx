/**
 * Page de visualisation "Mycélium Numérique"
 * Visualisation 3D des projets et contenus basée sur leurs embeddings sémantiques
 */
import { useEffect } from 'react';
import { useSEO } from '../../hooks/useSEO';
import MyceliumVisualization from '../../components/MyceliumVisualization';

export default function Mycelium() {
  useSEO({
    title: 'Mycélium Numérique - EGOEJO',
    description: 'Visualisation 3D des projets et contenus éducatifs basée sur leurs relations sémantiques',
  });

  return (
    <div className="page-mycelium">
      <div className="mycelium-header">
        <h1>Mycélium Numérique</h1>
        <p>
          Explorez visuellement les connexions entre projets et contenus éducatifs.
          Chaque point représente un projet ou un contenu, positionné selon sa proximité sémantique.
        </p>
        <p className="mycelium-info">
          💡 Les points proches partagent des concepts similaires, créant un réseau de savoir visible.
        </p>
      </div>

      <div className="mycelium-container">
        <MyceliumVisualization />
      </div>
    </div>
  );
}

