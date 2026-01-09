/**
 * Composant SwipeButton - Slider horizontal style déverrouillage iPhone
 * Utilise Framer Motion pour les animations fluides
 * Accessible : fallback bouton pour clavier/lecteur d'écran
 */
import { useState, useRef, useEffect } from 'react';
import { motion, useMotionValue, useTransform, useSpring } from 'framer-motion';
import { useNotificationContext } from '../../contexts/NotificationContext';

const SWIPE_THRESHOLD = 0.9; // 90% pour déclencher
const SPRING_CONFIG = { stiffness: 300, damping: 30 };

export default function SwipeButton({
  label = 'Glisser pour valider',
  onSuccess,
  disabled = false,
  color = '#10b981', // Vert par défaut
  ariaLabel,
  className = '',
}) {
  const [isDragging, setIsDragging] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [error, setError] = useState(null);
  const [isKeyboardMode, setIsKeyboardMode] = useState(false);
  const containerRef = useRef(null);
  const sliderRef = useRef(null);
  const { showSuccess: showNotificationSuccess } = useNotificationContext();

  // Motion values pour le drag
  const x = useMotionValue(0);
  const width = useTransform(x, (latest) => Math.max(0, latest));
  const opacity = useTransform(x, (latest) => {
    const progress = Math.abs(latest) / (containerRef.current?.offsetWidth || 300);
    return Math.min(1, progress * 1.5);
  });

  // Spring animation pour le retour
  const springX = useSpring(x, SPRING_CONFIG);

  // Détecter le mode clavier
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Tab' || e.key === 'Enter' || e.key === ' ') {
        setIsKeyboardMode(true);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleDragStart = () => {
    if (disabled || isSubmitting) return;
    setIsDragging(true);
    setError(null);
  };

  const handleDrag = (event, info) => {
    if (disabled || isSubmitting) return;
    const containerWidth = containerRef.current?.offsetWidth || 300;
    const maxDrag = containerWidth - (sliderRef.current?.offsetWidth || 50);
    
    // Limiter le drag à la largeur du conteneur
    if (x.get() > maxDrag) {
      x.set(maxDrag);
    }
  };

  const handleDragEnd = async () => {
    if (disabled || isSubmitting) return;
    setIsDragging(false);

    const containerWidth = containerRef.current?.offsetWidth || 300;
    const sliderWidth = sliderRef.current?.offsetWidth || 50;
    const maxDrag = containerWidth - sliderWidth;
    const currentX = x.get();
    const progress = currentX / maxDrag;

    // Si on atteint 90% ou plus, déclencher onSuccess
    if (progress >= SWIPE_THRESHOLD) {
      setIsSubmitting(true);
      try {
        await onSuccess();
        setShowSuccess(true);
        // Animation de confettis (simple notification)
        showNotificationSuccess('✅ Action confirmée !');
        
        // Verrouiller le slider (impossible de re-glisser)
        x.set(maxDrag);
      } catch (err) {
        setError(err.message || 'Une erreur est survenue');
        // Remettre au début
        x.set(0);
        setIsSubmitting(false);
      }
    } else {
      // Retour au début avec animation de ressort
      x.set(0);
    }
  };

  // Gestion du clavier (fallback accessible)
  const handleKeyDown = async (e) => {
    if (disabled || isSubmitting) return;
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      setIsSubmitting(true);
      try {
        await onSuccess();
        setShowSuccess(true);
        showNotificationSuccess('✅ Action confirmée !');
      } catch (err) {
        setError(err.message || 'Une erreur est survenue');
        setIsSubmitting(false);
      }
    }
  };

  // Si mode clavier ou lecteur d'écran, afficher un bouton standard
  if (isKeyboardMode || disabled) {
    return (
      <button
        onClick={async () => {
          if (disabled || isSubmitting) return;
          setIsSubmitting(true);
          try {
            await onSuccess();
            setShowSuccess(true);
            showNotificationSuccess('✅ Action confirmée !');
          } catch (err) {
            setError(err.message || 'Une erreur est survenue');
            setIsSubmitting(false);
          }
        }}
        disabled={disabled || isSubmitting}
        aria-label={ariaLabel || label}
        className={className}
        style={{
          width: '100%',
          padding: '1rem 2rem',
          backgroundColor: disabled ? '#9ca3af' : color,
          color: 'white',
          border: 'none',
          borderRadius: 'var(--radius, 8px)',
          cursor: disabled || isSubmitting ? 'not-allowed' : 'pointer',
          opacity: disabled || isSubmitting ? 0.6 : 1,
          fontSize: '1rem',
          fontWeight: '600',
        }}
      >
        {isSubmitting ? 'Traitement...' : showSuccess ? '✅ Confirmé' : label}
      </button>
    );
  }

  return (
    <div
      ref={containerRef}
      className={`swipe-button ${className}`}
      style={{
        position: 'relative',
        width: '100%',
        height: '56px',
        backgroundColor: disabled ? '#e5e7eb' : '#f3f4f6',
        borderRadius: 'var(--radius, 8px)',
        overflow: 'hidden',
        cursor: disabled || isSubmitting ? 'not-allowed' : 'grab',
        opacity: disabled ? 0.6 : 1,
      }}
      role="slider"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={Math.min(100, (Math.abs(x.get()) / (containerRef.current?.offsetWidth || 300)) * 100)}
      aria-label={ariaLabel || label}
      aria-disabled={disabled || isSubmitting}
      tabIndex={disabled ? -1 : 0}
      onKeyDown={handleKeyDown}
    >
      {/* Fond coloré qui s'étend */}
      <motion.div
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          bottom: 0,
          width: width,
          backgroundColor: color,
          opacity: opacity,
        }}
      />

      {/* Label au centre */}
      <div
        style={{
          position: 'absolute',
          left: '50%',
          top: '50%',
          transform: 'translate(-50%, -50%)',
          color: disabled ? '#9ca3af' : '#374151',
          fontWeight: '600',
          fontSize: '1rem',
          pointerEvents: 'none',
          zIndex: 'var(--z-content)', // Utiliser z-index centralisé
        }}
      >
        {isSubmitting ? 'Traitement...' : showSuccess ? '✅ Confirmé' : label}
      </div>

      {/* Slider (poignée) */}
      <motion.div
        ref={sliderRef}
        drag="x"
        dragConstraints={{ left: 0, right: containerRef.current?.offsetWidth || 300 }}
        dragElastic={0.1}
        onDragStart={handleDragStart}
        onDrag={handleDrag}
        onDragEnd={handleDragEnd}
        style={{
          x: springX,
          position: 'absolute',
          left: 0,
          top: 0,
          bottom: 0,
          width: '56px',
          backgroundColor: disabled ? '#9ca3af' : color,
          borderRadius: 'var(--radius, 8px)',
          cursor: disabled || isSubmitting ? 'not-allowed' : 'grab',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 'var(--z-floating)', // Utiliser z-index centralisé
          boxShadow: isDragging ? '0 4px 12px rgba(0,0,0,0.15)' : '0 2px 4px rgba(0,0,0,0.1)',
        }}
        whileDrag={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M9 18L15 12L9 6"
            stroke="white"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </motion.div>

      {/* Message d'erreur */}
      {error && (
        <div
          style={{
            position: 'absolute',
            bottom: '-2rem',
            left: 0,
            right: 0,
            color: '#ef4444',
            fontSize: '0.875rem',
            textAlign: 'center',
          }}
        >
          {error}
        </div>
      )}
    </div>
  );
}

