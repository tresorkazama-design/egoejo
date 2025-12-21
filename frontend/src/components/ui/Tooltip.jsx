/**
 * Composant Tooltip - Tooltip accessible avec support clavier
 * Affiche une info-bulle au survol ou au focus
 */
import React, { useState, useRef, useEffect } from 'react';

/**
 * @param {Object} props
 * @param {React.ReactNode} props.children - Élément déclencheur (doit accepter ref)
 * @param {string|React.ReactNode} props.content - Contenu du tooltip
 * @param {string} props.position - Position: 'top', 'bottom', 'left', 'right' (défaut: 'top')
 * @param {number} props.delay - Délai avant affichage en ms (défaut: 200)
 */
export default function Tooltip({ 
  children, 
  content, 
  position = 'top',
  delay = 200 
}) {
  const [isVisible, setIsVisible] = useState(false);
  const [tooltipStyle, setTooltipStyle] = useState({});
  const triggerRef = useRef(null);
  const tooltipRef = useRef(null);
  const timeoutRef = useRef(null);

  useEffect(() => {
    if (isVisible && triggerRef.current && tooltipRef.current) {
      const triggerRect = triggerRef.current.getBoundingClientRect();
      const tooltipRect = tooltipRef.current.getBoundingClientRect();
      const scrollY = window.scrollY;
      const scrollX = window.scrollX;

      let top, left;

      switch (position) {
        case 'top':
          top = triggerRect.top + scrollY - tooltipRect.height - 8;
          left = triggerRect.left + scrollX + (triggerRect.width / 2) - (tooltipRect.width / 2);
          break;
        case 'bottom':
          top = triggerRect.bottom + scrollY + 8;
          left = triggerRect.left + scrollX + (triggerRect.width / 2) - (tooltipRect.width / 2);
          break;
        case 'left':
          top = triggerRect.top + scrollY + (triggerRect.height / 2) - (tooltipRect.height / 2);
          left = triggerRect.left + scrollX - tooltipRect.width - 8;
          break;
        case 'right':
          top = triggerRect.top + scrollY + (triggerRect.height / 2) - (tooltipRect.height / 2);
          left = triggerRect.right + scrollX + 8;
          break;
        default:
          top = triggerRect.top + scrollY - tooltipRect.height - 8;
          left = triggerRect.left + scrollX + (triggerRect.width / 2) - (tooltipRect.width / 2);
      }

      // Ajuster pour éviter le débordement
      const padding = 8;
      if (left < padding) left = padding;
      if (left + tooltipRect.width > window.innerWidth - padding) {
        left = window.innerWidth - tooltipRect.width - padding;
      }
      if (top < padding) top = padding + scrollY;

      setTooltipStyle({ top: `${top}px`, left: `${left}px` });
    }
  }, [isVisible, position]);

  const showTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
    }, delay);
  };

  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsVisible(false);
  };

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  // Cloner l'enfant avec les props nécessaires
  const triggerElement = React.isValidElement(children)
    ? React.cloneElement(children, {
        ref: triggerRef,
        onMouseEnter: showTooltip,
        onMouseLeave: hideTooltip,
        onFocus: showTooltip,
        onBlur: hideTooltip,
        'aria-describedby': isVisible ? 'tooltip-content' : undefined,
      })
    : children;

  return (
    <>
      {triggerElement}
      {isVisible && (
        <div
          ref={tooltipRef}
          id="tooltip-content"
          role="tooltip"
          style={{
            position: 'absolute',
            zIndex: 1000,
            padding: '0.75rem 1rem',
            backgroundColor: 'var(--bg-inverse, #1a1a1a)',
            color: 'var(--text-inverse, #ffffff)',
            borderRadius: 'var(--radius, 8px)',
            fontSize: '0.875rem',
            lineHeight: 1.5,
            maxWidth: '300px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            pointerEvents: 'none',
            ...tooltipStyle,
          }}
          className="tooltip"
        >
          {typeof content === 'string' ? (
            <p style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{content}</p>
          ) : (
            content
          )}
          {/* Flèche du tooltip */}
          <div
            style={{
              position: 'absolute',
              width: 0,
              height: 0,
              borderStyle: 'solid',
              ...(position === 'top' && {
                bottom: '-6px',
                left: '50%',
                transform: 'translateX(-50%)',
                borderWidth: '6px 6px 0 6px',
                borderColor: 'var(--bg-inverse, #1a1a1a) transparent transparent transparent',
              }),
              ...(position === 'bottom' && {
                top: '-6px',
                left: '50%',
                transform: 'translateX(-50%)',
                borderWidth: '0 6px 6px 6px',
                borderColor: 'transparent transparent var(--bg-inverse, #1a1a1a) transparent',
              }),
              ...(position === 'left' && {
                right: '-6px',
                top: '50%',
                transform: 'translateY(-50%)',
                borderWidth: '6px 0 6px 6px',
                borderColor: 'transparent transparent transparent var(--bg-inverse, #1a1a1a)',
              }),
              ...(position === 'right' && {
                left: '-6px',
                top: '50%',
                transform: 'translateY(-50%)',
                borderWidth: '6px 6px 6px 0',
                borderColor: 'transparent var(--bg-inverse, #1a1a1a) transparent transparent',
              }),
            }}
            aria-hidden="true"
          />
        </div>
      )}
    </>
  );
}

