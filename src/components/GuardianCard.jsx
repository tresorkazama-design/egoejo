import React from "react";

export default function GuardianCard({
  name,
  protects,
  whySacred,
  needNow,
}) {
  return (
    <article style={{
      background:"rgba(6,11,10,.6)",
      border:"1px solid rgba(255,255,255,.07)",
      borderRadius:"16px",
      padding:"1rem 1.25rem",
      boxShadow:"0 0 30px rgba(0,255,170,.12)",
      backdropFilter:"blur(6px)",
      width:"100%",
      maxWidth:"360px",
      color:"#dffdf5",
      display:"flex",
      flexDirection:"column",
      justifyContent:"space-between",
      minHeight:"260px"
    }}>
      <header style={{marginBottom:"0.75rem"}}>
        <h3 style={{
          margin:0,
          fontSize:"1.1rem",
          lineHeight:1.3,
          color:"#74ffd7",
          textShadow:"0 0 10px rgba(0,255,170,.4)"
        }}>
          {name}
        </h3>
        <p style={{
          margin:"0.4rem 0 0 0",
          fontSize:".9rem",
          lineHeight:1.4,
          color:"#9bf6e5"
        }}>
          Protège : {protects}
        </p>
      </header>

      <section style={{fontSize:".9rem",lineHeight:1.4,opacity:.9}}>
        <p style={{margin:"0 0 .5rem 0"}}>{whySacred}</p>
        <p style={{margin:0}}>
          <strong style={{color:"#dffdf5"}}>Besoin actuel :</strong> {needNow}
        </p>
      </section>

      <footer style={{marginTop:"1rem"}}>
        <button style={{
          appearance:"none",
          background:"linear-gradient(90deg,#00ffa3 0%,#008061 100%)",
          border:"0",
          borderRadius:"10px",
          padding:".6rem .9rem",
          fontSize:".9rem",
          fontWeight:600,
          color:"#001710",
          boxShadow:"0 10px 30px rgba(0,255,170,.4)",
          cursor:"pointer",
          width:"100%",
          textAlign:"center"
        }}>
          Soutenir
        </button>
      </footer>
    </article>
  );
}