import React from "react";
import "../styles.css"; // si tes classes sont dedans

export default function Logo() {
  return (
    <div className="logo-container fade-in">
      <img
        src="/assets/logo/ego_ejo.svg"
        alt="EGOEJO Logo"
        className="logo breathing-logo"
      />
    </div>
  );
}
