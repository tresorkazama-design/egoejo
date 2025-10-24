import React from "react";
const LOGO_URL = "/assets/logo/ego_ejo.svg";

/** Watermark du logo (overlay, non cliquable) */
export default function WatermarkLogo({
  position = "top-left",
  size = 120,
  opacity = 0.08,
}) {
  const pos = {
    "top-left":    { top: 18,  left: 20 },
    "top-right":   { top: 18,  right: 20 },
    "bottom-left": { bottom: 18, left: 20 },
    "bottom-right":{ bottom: 18, right: 20 },
  }[position] || { top: 18, left: 20 };

  return (
    <div
      className="wm-logo breathing-glow"
      style={{
        position: "fixed",
        zIndex: 5,
        pointerEvents: "none",
        width: size,
        height: "auto",
        opacity,
        filter: "drop-shadow(0 0 12px rgba(0,255,163,0.25))",
        ...pos,
      }}
      aria-hidden
    >
      <img
        src={LOGO_URL}
        alt=""
        style={{ display: "block", width: "100%", height: "auto", userSelect: "none" }}
      />
    </div>
  );
}
