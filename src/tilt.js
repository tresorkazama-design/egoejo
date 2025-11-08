import { useRef, useEffect } from "react";
import * as THREE from "three";

export function useParallax({ factor = 0.02 } = {}) {
  const ref = useRef(null);
  useEffect(() => {
    let mx = 0, my = 0, w = window.innerWidth, h = window.innerHeight;
    const onMove = (e) => { mx = (e.clientX / w) * 2 - 1; my = (e.clientY / h) * 2 - 1; };
    const onResize = () => { w = window.innerWidth; h = window.innerHeight; };
    window.addEventListener("mousemove", onMove, { passive: true });
    window.addEventListener("resize", onResize);
    const raf = requestAnimationFrame(function loop(){
      const g = ref.current; if (g) { g.rotation.y += ((mx * factor) - g.rotation.y) * 0.08;
                                     g.rotation.x += ((-my * factor) - g.rotation.x) * 0.08; }
      requestAnimationFrame(loop);
    });
    return () => { cancelAnimationFrame(raf);
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("resize", onResize); };
  }, [factor]);
  return ref;
}

export function ParallaxGroup({ refObj, par = 0.02 }) {
  // dÃƒÂ©cor optionnel (halo trÃƒÂ¨s lÃƒÂ©ger)
  return null;
}
