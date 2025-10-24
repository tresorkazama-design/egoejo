import { useEffect, useRef } from "react";

/**
 * Curseur vivant : un point + halo avec inertie.
 * Change d'état quand on survole des éléments ayant data-cursor="hover" ou "accent".
 */
export default function CustomCursor(){
  const dotRef = useRef(null);
  const haloRef = useRef(null);

  useEffect(() => {
    const dot = dotRef.current;
    const halo = haloRef.current;

    let x = window.innerWidth / 2;
    let y = window.innerHeight / 2;
    let hx = x, hy = y;

    const speed = 0.18;   // inertie halo
    const onMove = (e) => {
      x = e.clientX;
      y = e.clientY;
    };

    const loop = () => {
      // Dot suit la souris direct
      dot.style.transform = `translate3d(${x}px, ${y}px, 0)`;

      // Halo suit avec inertie
      hx += (x - hx) * speed;
      hy += (y - hy) * speed;
      halo.style.transform = `translate3d(${hx}px, ${hy}px, 0)`;

      requestAnimationFrame(loop);
    };
    loop();

    // États hover via attributs
    const enter = (e) => {
      const t = e.target.closest("[data-cursor]");
      if(!t) return;
      const mode = t.getAttribute("data-cursor");
      halo.classList.toggle("is-hover", mode === "hover");
      halo.classList.toggle("is-accent", mode === "accent");
      dot.classList.toggle("is-hidden", mode !== null);
    };
    const leave = () => {
      halo.classList.remove("is-hover","is-accent");
      dot.classList.remove("is-hidden");
    };

    document.addEventListener("mousemove", onMove);
    document.addEventListener("mouseover", enter);
    document.addEventListener("mouseout", leave);

    // Cacher le curseur natif sur desktop
    document.documentElement.style.cursor = "none";

    return () => {
      document.removeEventListener("mousemove", onMove);
      document.removeEventListener("mouseover", enter);
      document.removeEventListener("mouseout", leave);
      document.documentElement.style.cursor = "";
    };
  }, []);

  return (
    <>
      <div ref={haloRef} className="cursor-halo" />
      <div ref={dotRef}  className="cursor-dot"  />
    </>
  );
}
