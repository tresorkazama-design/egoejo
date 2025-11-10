export default function Projets(){
  const wrap = { padding:"min(4vw,28px)", color:"#c8ffee", minHeight:"100svh", background:"#060d0c" };
  const h = { margin:"6vh 0 2vh 0", fontSize:"min(8.8vw,88px)", lineHeight:.92, letterSpacing:".01em" };
  const sub = { color:"#9bfbd6", opacity:.9, margin:"0 0 28px 2px" };
  const grid = {
    display:"grid",
    gridTemplateColumns:"repeat(auto-fit, minmax(280px,1fr))",
    gap:"min(2vw,18px)"
  };
  const card = {
    background:"#0b1815", border:"1px solid #123a2f", borderRadius:"16px",
    overflow:"hidden", transition:"transform .18s ease, box-shadow .18s ease", cursor:"pointer"
  };
  const media = { aspectRatio:"16/10", background:"#182926" };
  const caption = { padding:"14px 16px", color:"#e9fff7", fontWeight:700, letterSpacing:".01em" };

  const items = Array.from({length:9}).map((_,i)=>({
    title: `Projet #${i+1}`,
    cover: `https://picsum.photos/seed/egoejo-${i}/800/500`
  }));

  return (
    <main style={wrap}>
      <h1 style={h}>Projets</h1>
      <p style={sub}>Sélection d’études et de réalisations — bientôt enrichie.</p>
      <section style={grid}>
        {items.map((it,idx)=>(
          <article key={idx} style={card}
            onMouseEnter={e=>{e.currentTarget.style.transform="translateY(-3px)";e.currentTarget.style.boxShadow="0 10px 24px rgba(0,0,0,.35)"}}
            onMouseLeave={e=>{e.currentTarget.style.transform="none";e.currentTarget.style.boxShadow="none"}}>
            <div style={media}>
              <img src={it.cover} alt="" style={{width:"100%",height:"100%",objectFit:"cover"}}/>
            </div>
            <div style={caption}>{it.title}</div>
          </article>
        ))}
      </section>
    </main>
  );
}