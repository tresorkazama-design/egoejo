import { useEffect, useRef } from "react";
import { gsap } from "gsap";

export default function AnimatedTitle({ children, as: Tag = "h1", className = "" }) {
  const titleRef = useRef(null);

  useEffect(() => {
    const el = titleRef.current;
    if (!el) return;

    const prefersReduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const text = el.textContent;
    const letters = text.split("").map((letter) => {
      const span = document.createElement("span");
      span.textContent = letter === " " ? "\u00A0" : letter;
      span.className = "letter";
      span.style.display = "inline-block";
      return span;
    });

    el.innerHTML = "";
    letters.forEach((span) => el.appendChild(span));

    if (prefersReduce) return;

    gsap.fromTo(
      letters,
      { y: "110%", opacity: 0 },
      {
        y: "0%",
        opacity: 1,
        duration: 0.8,
        ease: "power3.out",
        stagger: 0.05,
      }
    );

    return () => {
      el.innerHTML = text;
    };
  }, [children]);

  return (
    <Tag ref={titleRef} className={`animated-title ${className}`.trim()}>
      {children}
    </Tag>
  );
}

