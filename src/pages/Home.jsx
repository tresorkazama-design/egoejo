import { useMemo } from "react";

import HeroSorgho from "../components/HeroSorgho.jsx";
import AnimatedTitle from "../components/AnimatedTitle.jsx";
import BlocSubtitle from "../components/BlocSubtitle.jsx";

export default function Home() {
  const donationLinks = useMemo(
    () => [
      {
        label: "HelloAsso (externe)",
        href: "https://www.helloasso.com/associations",
        variant: "ghost",
      },
      {
        label: "Adhésion / Don Stripe",
        href: "https://donate.stripe.com",
        variant: "solid",
      },
    ],
    []
  );

  return (
    <>
      <HeroSorgho />
      <section
        id="soutenir"
        className="section section--support"
        data-animate
        style={{ padding: "48px 6vw", maxWidth: 1200, margin: "0 auto" }}
      >
        <AnimatedTitle as="h2" className="section-title">
          Soutenir le projet
        </AnimatedTitle>
        <BlocSubtitle content="Deux options rapides pour devenir allié·e du vivant" />

        <p style={{ margin: "20px 0", maxWidth: 720, color: "#d6fdef" }}>
          Adhérez ou faites un don pour soutenir nos actions. Les contributions financières
          permettent d’expérimenter et de partager de nouvelles manières d’habiter la Terre.
        </p>

        <div style={{ display: "flex", gap: 16, flexWrap: "wrap", marginTop: 24 }}>
          {donationLinks.map(({ label, href, variant }) => {
            const baseStyle = {
              borderRadius: 10,
              padding: "12px 20px",
              fontWeight: 600,
              fontSize: "1rem",
              textDecoration: "none",
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "transform 0.25s ease, box-shadow 0.25s ease, opacity 0.25s ease",
            };

            const specificStyle =
              variant === "ghost"
                ? {
                    ...baseStyle,
                    background: "transparent",
                    color: "#74ffd7",
                    border: "1px solid rgba(116,255,215,.6)",
                    boxShadow: "0 0 0 1px rgba(116,255,215,.3) inset",
                  }
                : {
                    ...baseStyle,
                    background: "linear-gradient(135deg, #20f3a6, #12bfa5)",
                    color: "#041310",
                    border: "none",
                    boxShadow: "0 18px 35px -18px rgba(20,220,170,.6)",
                  };

            return (
              <a
                key={href}
                href={href}
                target="_blank"
                rel="noreferrer"
                style={specificStyle}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "translateY(-4px)";
                  e.currentTarget.style.boxShadow =
                    variant === "ghost"
                      ? "0 12px 24px -16px rgba(116,255,215,.35)"
                      : "0 20px 40px -18px rgba(20,220,170,.7)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0)";
                  e.currentTarget.style.boxShadow =
                    variant === "ghost"
                      ? "0 0 0 1px rgba(116,255,215,.3) inset"
                      : "0 18px 35px -18px rgba(20,220,170,.6)";
                }}
              >
                {label}
              </a>
            );
          })}
        </div>
      </section>
    </>
  );
}