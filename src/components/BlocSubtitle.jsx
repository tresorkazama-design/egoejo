import { useEffect, useMemo, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export default function BlocSubtitle({ content, id = undefined, className = "" }) {
  const containerRef = useRef(null);
  const letters = useMemo(
    () =>
      content.split("").map((letter, index) => (
        <span key={index} className="letter">
          {letter === " " ? "\u00A0" : letter}
        </span>
      )),
    [content]
  );

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    const tl = gsap.timeline({
      scrollTrigger: {
        trigger: el,
        start: "top 85%",
        toggleActions: "play none none reverse",
      },
    });

    const lettersEls = el.querySelectorAll(".letter");
    const backdropEls = el.querySelectorAll(".bloc__subtitle-background div");

    tl.fromTo(
      lettersEls,
      { yPercent: 120, opacity: 0 },
      {
        yPercent: 0,
        opacity: 1,
        duration: 0.8,
        ease: "power3.out",
        stagger: 0.035,
      }
    ).fromTo(
      backdropEls,
      { scaleY: 0 },
      {
        scaleY: 1,
        transformOrigin: "bottom",
        duration: 0.6,
        ease: "power2.out",
        stagger: 0.02,
      },
      "<"
    );

    return () => {
      tl.kill();
    };
  }, [content]);

  return (
    <div
      ref={containerRef}
      className={`bloc__subtitle-container ${className}`.trim()}
      id={id}
    >
      <span className="bloc__subtitle">{letters}</span>
      <div className="bloc__subtitle-background">
        {Array.from({ length: 16 }).map((_, index) => (
          <div key={index} />
        ))}
      </div>
    </div>
  );
}

