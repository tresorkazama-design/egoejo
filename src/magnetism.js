// src/magnetism.js
export function initMagnetism(opts = {}) {
  const {
    // Sélectionne tes cibles "aimantées"
    selector = 'button, .cta, a[data-magnetic], [data-magnetic="true"], [data-magnetic]',
    // Intensité et zone d’attraction
    strength = 0.28,   // 0.15–0.40 : doux -> fort
    radius = 100,      // px
    // Lissage
    easing = 0.18,     // 0.1–0.25
    decay = 0.82       // retour quand on est hors rayon
  } = opts;

  // Respecte l’accessibilité et évite l’init sur tactile
  const prefersReduce =
    typeof window !== "undefined" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const isCoarse =
    typeof window !== "undefined" &&
    window.matchMedia("(pointer: coarse)").matches;

  if (prefersReduce || isCoarse) {
    return () => {};
  }

  const els = Array.from(document.querySelectorAll(selector)).filter(Boolean);
  if (!els.length) return () => {};

  const states = new Map();
  const listeners = [];

  // Prépare chaque élément + listeners d’entrée/sortie
  els.forEach((el) => {
    el.style.willChange = "transform";
    el.style.transform = "translate3d(0,0,0)";
    states.set(el, { tx: 0, ty: 0 });

    const onEnter = () => el.classList.add("mag-on");
    const onLeave = () => {
      const st = states.get(el);
      if (!st) return;
      st.tx = 0; st.ty = 0;
      el.style.transform = "translate3d(0,0,0)";
      el.classList.remove("mag-on");
    };

    el.addEventListener("mouseenter", onEnter);
    el.addEventListener("mouseleave", onLeave);
    listeners.push({ el, onEnter, onLeave });
  });

  let mx = 0, my = 0, rafId = 0;
  const onMove = (e) => { mx = e.clientX; my = e.clientY; };

  const loop = () => {
    for (const el of els) {
      const st = states.get(el);
      const r = el.getBoundingClientRect();
      const cx = r.left + r.width / 2;
      const cy = r.top + r.height / 2;

      const dx = mx - cx;
      const dy = my - cy;
      const dist = Math.hypot(dx, dy);

      if (dist < radius) {
        const force = 1 - dist / radius; // 0 -> 1
        const tx = dx * strength * force;
        const ty = dy * strength * force;

        // easing doux vers la cible
        st.tx += (tx - st.tx) * easing;
        st.ty += (ty - st.ty) * easing;
      } else {
        // retour progressif au repos
        st.tx *= decay;
        st.ty *= decay;
        if (Math.abs(st.tx) < 0.01) st.tx = 0;
        if (Math.abs(st.ty) < 0.01) st.ty = 0;
      }

      el.style.transform = `translate3d(${st.tx}px, ${st.ty}px, 0)`;
    }
    rafId = requestAnimationFrame(loop);
  };

  window.addEventListener("mousemove", onMove, { passive: true });
  rafId = requestAnimationFrame(loop);

  // --- cleanup ---
  return () => {
    cancelAnimationFrame(rafId);
    window.removeEventListener("mousemove", onMove);
    for (const { el, onEnter, onLeave } of listeners) {
      el.removeEventListener("mouseenter", onEnter);
      el.removeEventListener("mouseleave", onLeave);
      el.style.transform = "translate3d(0,0,0)";
      el.style.willChange = "";
      el.classList.remove("mag-on");
    }
    states.clear();
  };
}
