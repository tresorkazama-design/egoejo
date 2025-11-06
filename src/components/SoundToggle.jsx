import React from "react";
export default function SoundToggle(){
  const ref = React.useRef(null);
  const [on, setOn] = React.useState(false);
  React.useEffect(() => { if (ref.current){ ref.current.volume = 0.3; if(on) ref.current.play().catch(()=>{}); else ref.current.pause(); } }, [on]);
  return (
    <div style={{position:"fixed", right:18, bottom:18, zIndex:6}}>
      <audio ref={ref} loop src="/assets/audio/ambience.mp3"></audio>
      <button onClick={()=>setOn(v=>!v)}
        style={{background:"rgba(0,0,0,.35)", color:"#7affcf", border:"1px solid rgba(0,255,160,.25)",
                borderRadius:12, padding:"10px 14px", cursor:"pointer",
                boxShadow:"0 0 12px rgba(0,255,160,.25)"}}>
        {on?"🔊 Ambiance":"🔈 Ambiance"}
      </button>
    </div>
  );
}
