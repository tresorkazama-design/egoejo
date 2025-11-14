import React from "react";

export default function Logo3D({ text = "EGOEJO", className = "" }) {
  const main = text.charAt(0) || "E";
  const tail = text.slice(1);

  return (
    <span className={`logo-3d ${className}`.trim()} aria-label={text}>
      <span className="logo-3d__letter" data-letter={main}>
        <span>{main}</span>
      </span>
      <span className="logo-3d__word">{tail}</span>
    </span>
  );
}

