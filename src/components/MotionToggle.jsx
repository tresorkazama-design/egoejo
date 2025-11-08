import React from "react";

export default function MotionToggle(){
  const [on,setOn] = React.useState(()=>localStorage.getItem("ego-rm")==="1");

  React.useEffect(()=>{
    document.documentElement.classList.toggle("rm-on", on);
    localStorage.setItem("ego-rm", on ? "1":"0");
  },[on]);

  return (
    <button onClick={()=>setOn(v=>!v)}
      style={{
        position:"fixed", left:16, bottom:16, zIndex:50,
        background:"rgba(6,11,10,.75)", color:"#9bf6e5",
        border:"1px solid rgba(255,255,255,.08)", borderRadius:10,
        padding:"8px 12px", boxShadow:"0 0 20px rgba(0,255,170,.15)",
        backdropFilter:"blur(6px)", cursor:"pointer"
      }}>
      {on ? "Animations rÃ©duites" : "Animations normales"}
    </button>
  );
}
