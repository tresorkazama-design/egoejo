import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

export function initScrollAnimations() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  // Sections reveal
  gsap.utils.toArray(".section[data-animate]").forEach((section) => {
    gsap.fromTo(
      section,
      { y: 60, opacity: 0.2 },
      {
        y: 0,
        opacity: 1,
        duration: 1,
        ease: "power2.out",
        scrollTrigger: {
          trigger: section,
          start: "top 80%",
          toggleActions: "play none none reverse",
        },
      }
    );
  });

  // Footer reveal
  const footer = document.querySelector(".footer_area");
  if (footer) {
    gsap.from(".footer__container", {
      y: 200,
      opacity: 0,
      scrollTrigger: {
        trigger: footer,
        start: "-70% bottom",
        end: "bottom bottom",
        scrub: 1,
      },
    });

    gsap.from(".footer__container > *", {
      y: 40,
      opacity: 0,
      stagger: 0.1,
      scrollTrigger: {
        trigger: footer,
        start: "-50% bottom",
        end: "bottom bottom",
        scrub: true,
      },
    });
  }
}

export function cleanupScrollAnimations() {
  ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
}

