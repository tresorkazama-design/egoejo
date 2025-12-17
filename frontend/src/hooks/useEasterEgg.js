import { useEffect, useState } from 'react';

/**
 * Hook pour l'easter egg "vivant"
 * Si l'utilisateur tape "vivant" sur son clavier, une animation se déclenche
 */
export const useEasterEgg = () => {
  const [input, setInput] = useState('');
  const sequence = 'vivant'; // Le mot magique

  useEffect(() => {
    const handleKeyDown = (e) => {
      // Ignorer si l'utilisateur est en train de taper dans un input/textarea
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        return;
      }

      const nextInput = (input + e.key).slice(-sequence.length);
      
      if (nextInput === sequence) {
        // Déclenche l'effet
        console.log("🌱 La nature reprend ses droits...");
        
        // Effet visuel "Terre/Vert"
        document.body.style.transition = 'filter 0.5s ease-in-out';
        document.body.style.filter = "sepia(0.5) hue-rotate(90deg)";
        
        setTimeout(() => {
          document.body.style.filter = "none";
          
          // Message de confirmation (optionnel, peut être remplacé par une notification)
          if (window.confirm) {
            // Utiliser une notification plus douce si disponible
            if ('Notification' in window && Notification.permission === 'granted') {
              new Notification("🌿 Merci de faire partie du vivant.", {
                body: "La nature vous remercie.",
                icon: '/favicon.ico',
                tag: 'easter-egg'
              });
            } else {
              // Fallback sur alert si notifications non disponibles
              alert("🌿 Merci de faire partie du vivant.");
            }
          }
        }, 2000);
      }
      
      setInput(nextInput);
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [input]);
};

