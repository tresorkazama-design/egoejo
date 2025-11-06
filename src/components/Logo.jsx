import React from "react";

export default function Logo(){
  return (
    <div className="logo-wrap">
      <img
        className="logo"
        src="/assets/logo/ego_ejo.svg"
        alt="EGOEJO logo"
        onError={(e)=>{ e.currentTarget.style.display="none"; }}
      />
    </div>
  );
}
