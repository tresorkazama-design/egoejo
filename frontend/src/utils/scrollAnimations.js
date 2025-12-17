import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export function initScrollAnimations() {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;    

  // Animations de texte adoucies
  gsap.utils.toArray(".heading-xl, .heading-l").forEach((heading) => {
    gsap.fromTo(
      heading,
      { 
        y: 30, 
        opacity: 0
      },
      {
        y: 0,
        opacity: 1,
        duration: 0.6,
        ease: "power2.out",
        scrollTrigger: {
          trigger: heading,
          start: "top 85%",
          toggleActions: "play none none reverse",
        },
      }
    );
  });

  // Sections reveal avec parallaxe douce
  gsap.utils.toArray(".section[data-animate], .citation-group, .glass").forEach((section, index) => {
    gsap.fromTo(
      section,
      { 
        y: 40, 
        opacity: 0
      },
      {
        y: 0,
        opacity: 1,
        duration: 0.8,
        ease: "power2.out",
        scrollTrigger: {
          trigger: section,
          start: "top 80%",
          toggleActions: "play none none reverse",
        },
      }
    );

    // Parallaxe douce au scroll (très subtile)
    gsap.to(section, {
      y: -15,
      ease: "none",
      scrollTrigger: {
        trigger: section,
        start: "top bottom",
        end: "bottom top",
        scrub: 2,
      },
    });
  });

  // Citations cards avec révélation douce
  gsap.utils.toArray(".citation-card").forEach((card, index) => {
    gsap.fromTo(
      card,
      {
        opacity: 0,
        y: 20,
      },
      {
        opacity: 1,
        y: 0,
        duration: 0.5,
        delay: index * 0.05,
        ease: "power2.out",
        scrollTrigger: {
          trigger: card,
          start: "top 85%",
          toggleActions: "play none none reverse",
        },
      }
    );
  });

  // Stats avec compteur animé
  gsap.utils.toArray(".citations-hero__stats dt").forEach((stat) => {
    const text = stat.textContent;
    const number = text.match(/\d+/);
    if (number) {
      const targetValue = parseInt(number[0]);
      gsap.fromTo(
        { value: 0 },
        { value: targetValue },
        {
          value: targetValue,
          duration: 2,
          ease: "power2.out",
          onUpdate: function() {
            stat.textContent = text.replace(/\d+/, Math.floor(this.targets()[0].value));
          },
          scrollTrigger: {
            trigger: stat,
            start: "top 80%",
            toggleActions: "play none none reverse",
          },
        }
      );
    }
  });

  // Footer reveal amélioré
  const footer = document.querySelector(".layout-footer");
  if (footer) {
    gsap.from(".layout-footer__inner", {
      y: 100,
      opacity: 0,
      scale: 0.95,
      scrollTrigger: {
        trigger: footer,
        start: "-30% bottom",
        end: "bottom bottom",
        scrub: 1.5,
      },
    });

    gsap.from(".layout-footer__inner > *", {
      y: 50,
      opacity: 0,
      stagger: 0.15,
      scrollTrigger: {
        trigger: footer,
        start: "-20% bottom",
        end: "bottom bottom",
        scrub: true,
      },
    });
  }

}

export function cleanupScrollAnimations() {
  ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
}

