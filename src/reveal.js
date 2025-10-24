export function initReveal({ rootMargin = "0px 0px -10% 0px", threshold = 0.15 } = {}) {
  const els = Array.from(document.querySelectorAll("[data-reveal]"));
  if (!("IntersectionObserver" in window)) { els.forEach(el => el.classList.add("reveal-in")); return () => {}; }
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add("reveal-in"); io.unobserve(e.target); } });
  }, { root: null, rootMargin, threshold });
  els.forEach(el => io.observe(el));
  return () => io.disconnect();
}
