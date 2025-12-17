import { useEffect, useRef } from 'react';

export default function CursorSpotlight() {
  const spotlightRef = useRef(null);

  useEffect(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const spotlight = spotlightRef.current;
    if (!spotlight) return;

    const handleMouseMove = (e) => {
      const { clientX, clientY } = e;
      spotlight.style.background = `radial-gradient(600px circle at ${clientX}px ${clientY}px, rgba(0, 245, 160, 0.08), transparent 40%)`;
    };

    document.addEventListener('mousemove', handleMouseMove);
    return () => document.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div
      ref={spotlightRef}
      className="cursor-spotlight"
      aria-hidden="true"
    />
  );
}

