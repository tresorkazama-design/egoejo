import { useState, useEffect, useRef } from 'react';
import { logger } from '../utils/logger';

/**
 * Composant Image optimisé pour le SEO
 * - Lazy loading natif
 * - Alt text obligatoire
 * - Placeholder pendant le chargement
 * - Support des images responsives
 * 
 * @param {Object} props
 * @param {string} props.src - URL de l'image
 * @param {string} props.alt - Texte alternatif (obligatoire pour l'accessibilité et le SEO)
 * @param {string} props.className - Classes CSS
 * @param {string} props.width - Largeur de l'image
 * @param {string} props.height - Hauteur de l'image
 * @param {boolean} props.loading - 'lazy' par défaut, 'eager' pour les images above-the-fold
 * @param {string} props.srcSet - Source set pour les images responsives
 * @param {string} props.sizes - Tailles pour les images responsives
 */
export default function OptimizedImage({
  src,
  alt,
  className = '',
  width,
  height,
  loading = 'lazy',
  srcSet,
  sizes,
  ...props
}) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [isInView, setIsInView] = useState(loading === 'eager'); // Charger immédiatement si eager
  const imgRef = useRef(null);

  useEffect(() => {
    if (!imgRef.current || loading === 'eager') {
      // Si eager, charger immédiatement
      if (loading === 'eager') {
        setIsInView(true);
      }
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observer.disconnect();
        }
      },
      { rootMargin: '50px' } // Commencer à charger 50px avant que l'image soit visible
    );

    observer.observe(imgRef.current);

    return () => observer.disconnect();
  }, [loading]);

  useEffect(() => {
    if (isInView && !isLoaded && !hasError && src) {
      // L'image est visible, on peut la charger
      const img = new Image();
      img.onload = () => setIsLoaded(true);
      img.onerror = () => setHasError(true);
      img.src = src;
    }
  }, [isInView, src, isLoaded, hasError]);

  if (!alt) {
    logger.warn('OptimizedImage: alt text is required for accessibility and SEO');
  }

  return (
    <div
      className={`optimized-image ${className}`}
      style={{
        position: 'relative',
        width: width || '100%',
        height: height || 'auto',
        backgroundColor: '#f0f0f0',
        overflow: 'hidden',
      }}
    >
      {!isLoaded && !hasError && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            backgroundColor: '#e0e0e0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          aria-hidden="true"
        >
          <div
            style={{
              width: '40px',
              height: '40px',
              border: '3px solid #ccc',
              borderTopColor: '#00ffa3',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
            }}
          />
        </div>
      )}
      {hasError ? (
        <div
          style={{
            width: '100%',
            height: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#999',
            fontSize: '14px',
          }}
          role="img"
          aria-label={alt || 'Image non disponible'}
        >
          {alt || 'Image non disponible'}
        </div>
      ) : (
        <img
          ref={imgRef}
          src={isInView ? (isLoaded ? src : undefined) : undefined}
          alt={alt || ''}
          width={width}
          height={height}
          loading={loading}
          srcSet={srcSet}
          sizes={sizes}
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            opacity: isLoaded ? 1 : 0,
            transition: 'opacity 0.3s ease-in-out',
          }}
          {...props}
        />
      )}
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

