/**
 * Composant Confetti - Animation de particules pour célébrer une action
 * Légère et performante, utilise Canvas pour l'animation
 */
import { useEffect, useRef } from 'react';

/**
 * @param {Object} props
 * @param {boolean} props.active - Active l'animation
 * @param {number} props.particleCount - Nombre de particules (défaut: 50)
 * @param {Array<string>} props.colors - Couleurs des particules (défaut: couleurs SAKA)
 * @param {number} props.duration - Durée de l'animation en ms (défaut: 2000)
 */
export default function Confetti({ 
  active = false,
  particleCount = 50,
  colors = ['#84cc16', '#22c55e', '#f59e0b', '#10b981'],
  duration = 2000
}) {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const particlesRef = useRef([]);

  useEffect(() => {
    if (!active || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Ajuster la taille du canvas
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    // Créer les particules
    const createParticle = (x, y) => {
      return {
        x,
        y,
        vx: (Math.random() - 0.5) * 4,
        vy: Math.random() * -3 - 2,
        size: Math.random() * 4 + 2,
        color: colors[Math.floor(Math.random() * colors.length)],
        rotation: Math.random() * Math.PI * 2,
        rotationSpeed: (Math.random() - 0.5) * 0.2,
        gravity: 0.1,
        life: 1.0,
        decay: Math.random() * 0.02 + 0.01,
      };
    };

    // Initialiser les particules depuis le centre de l'écran
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    particlesRef.current = Array.from({ length: particleCount }, () =>
      createParticle(centerX, centerY)
    );

    let startTime = Date.now();

    const animate = () => {
      const elapsed = Date.now() - startTime;
      if (elapsed > duration) {
        // Animation terminée, nettoyer
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        return;
      }

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particlesRef.current = particlesRef.current.filter(particle => {
        // Mettre à jour la position
        particle.x += particle.vx;
        particle.y += particle.vy;
        particle.vy += particle.gravity;
        particle.rotation += particle.rotationSpeed;
        particle.life -= particle.decay;

        if (particle.life <= 0 || particle.y > canvas.height) {
          return false;
        }

        // Dessiner la particule
        ctx.save();
        ctx.globalAlpha = particle.life;
        ctx.translate(particle.x, particle.y);
        ctx.rotate(particle.rotation);
        ctx.fillStyle = particle.color;
        ctx.fillRect(-particle.size / 2, -particle.size / 2, particle.size, particle.size);
        ctx.restore();

        return true;
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    // Cleanup
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    };
  }, [active, particleCount, colors, duration]);

  if (!active) return null;

  return (
    <canvas
      ref={canvasRef}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 9999,
      }}
      aria-hidden="true"
    />
  );
}

