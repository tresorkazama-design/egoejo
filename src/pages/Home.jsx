import React from "react";

export default function Home(){
  return (
    <main style={{fontFamily:"system-ui", color:"#111", background:"#fff"}}>
      <section style={{padding:"56px 16px", maxWidth:1200, margin:"0 auto"}}>
        <h1 style={{fontSize:48, margin:0}}>EGOEJO</h1>
        <p style={{fontSize:18, marginTop:12, maxWidth:720}}>
          Lier Histoire et Futur pour soutenir des projets à impact social et culturel.
        </p>
        <div style={{display:"flex", gap:12, marginTop:24}}>
          <a href="#soutenir" style={btn}>Soutenir</a>
          <a href="/admin" style={{...btn, background:"#eee", color:"#111"}}>Admin</a>
        </div>
      </section>

      <section style={{padding:"32px 16px", maxWidth:1200, margin:"0 auto"}}>
        <h2 id="soutenir">Soutenir le projet</h2>
        <p>Deux options rapides : Adhésion/Don via Stripe, ou HelloAsso si vous êtes en France (asso).</p>
        <div style={{display:"flex", gap:12, flexWrap:"wrap"}}>
          <button onClick={pay} style={btn}>Adhérer / Donner (Stripe)</button>
          <a href="https://www.helloasso.com/associations" target="_blank" rel="noreferrer" style={{...btn, background:"#0a66c2"}}>
            HelloAsso (externe)
          </a>
        </div>
      </section>

      <section style={{padding:"16px", maxWidth:1200, margin:"0 auto"}}>
        <h2>Vision</h2>
        <p>Une communauté de lecture et d’analyse d’œuvres pour aborder les sujets de société, et
           une plateforme pour structurer, financer et mesurer l’impact.</p>
      </section>
    </main>
  );
}

const btn = {
  background:"#111", color:"#fff", padding:"10px 16px", borderRadius:8, textDecoration:"none",
  display:"inline-block", border:"none", cursor:"pointer"
};

async function pay(){
  try{
    const r = await fetch("/api/checkout-create", { method:"POST" });
    if(!r.ok) throw new Error("HTTP "+r.status);
    const json = await r.json();
    if(json.url) location.href = json.url;
  }catch(e){
    alert("Paiement indisponible – contactez-nous.");
    console.error(e);
  }
}
