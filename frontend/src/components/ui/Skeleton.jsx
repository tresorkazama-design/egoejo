/**
 * Composant Skeleton - Écran de chargement qui imite la forme du contenu
 * Alternative élégante aux spinners génériques
 */
import React from 'react';

/**
 * @param {Object} props
 * @param {string} props.width - Largeur (ex: '100%', '200px', '50%')
 * @param {string} props.height - Hauteur (ex: '20px', '2rem')
 * @param {string} props.borderRadius - Rayon de bordure (défaut: 'var(--radius, 4px)')
 * @param {boolean} props.circle - Si true, crée un cercle (ignore width/height)
 * @param {string} props.className - Classes CSS additionnelles
 */
export function Skeleton({ 
  width = '100%', 
  height = '1rem', 
  borderRadius = 'var(--radius, 4px)',
  circle = false,
  className = '',
  style = {}
}) {
  const skeletonStyle = {
    width: circle ? height : width,
    height: circle ? height : height,
    borderRadius: circle ? '50%' : borderRadius,
    backgroundColor: 'var(--surface, #f3f4f6)',
    backgroundImage: 'linear-gradient(90deg, var(--surface, #f3f4f6) 0%, var(--border, #e5e7eb) 50%, var(--surface, #f3f4f6) 100%)',
    backgroundSize: '200% 100%',
    animation: 'skeleton-loading 1.5s ease-in-out infinite',
    display: 'inline-block',
    ...style,
  };

  return (
    <div
      className={`skeleton ${className}`}
      style={skeletonStyle}
      aria-hidden="true"
      role="presentation"
    />
  );
}

/**
 * Composant SkeletonText - Pour les lignes de texte
 * @param {Object} props
 * @param {number} props.lines - Nombre de lignes (défaut: 3)
 * @param {string} props.width - Largeur de chaque ligne (défaut: '100%')
 * @param {string} props.lastLineWidth - Largeur de la dernière ligne (défaut: '60%')
 */
export function SkeletonText({ 
  lines = 3, 
  width = '100%',
  lastLineWidth = '60%',
  className = ''
}) {
  return (
    <div className={`skeleton-text ${className}`} style={{ width: '100%' }}>
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton
          key={index}
          width={index === lines - 1 ? lastLineWidth : width}
          height="1rem"
          style={{ marginBottom: index < lines - 1 ? '0.5rem' : '0' }}
        />
      ))}
    </div>
  );
}

/**
 * Composant SkeletonCard - Pour les cartes de contenu
 * @param {Object} props
 * @param {boolean} props.withImage - Afficher un skeleton d'image
 * @param {number} props.textLines - Nombre de lignes de texte
 */
export function SkeletonCard({ 
  withImage = true, 
  textLines = 3,
  className = ''
}) {
  return (
    <div
      className={`skeleton-card ${className}`}
      style={{
        padding: '1.5rem',
        backgroundColor: 'var(--surface)',
        borderRadius: 'var(--radius)',
        border: '1px solid var(--border)',
      }}
    >
      {withImage && (
        <Skeleton
          width="100%"
          height="200px"
          borderRadius="var(--radius)"
          style={{ marginBottom: '1rem' }}
        />
      )}
      <Skeleton width="60%" height="1.5rem" style={{ marginBottom: '0.75rem' }} />
      <SkeletonText lines={textLines} />
    </div>
  );
}

// Ajouter l'animation CSS via un style tag (ou dans un fichier CSS global)
if (typeof document !== 'undefined') {
  const styleId = 'skeleton-animation-style';
  if (!document.getElementById(styleId)) {
    const style = document.createElement('style');
    style.id = styleId;
    style.textContent = `
      @keyframes skeleton-loading {
        0% {
          background-position: 200% 0;
        }
        100% {
          background-position: -200% 0;
        }
      }
    `;
    document.head.appendChild(style);
  }
}

export default Skeleton;

