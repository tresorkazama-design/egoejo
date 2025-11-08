import React from "react";

export default function Loader(){
  return (
    <div style={{
      position:"absolute", inset:0, display:"grid", placeItems:"center",
      background:"radial-gradient(60% 60% at 50% 50%, rgba(0,255,170,.05), transparent)",
      color:"#9bf6e5", fontFamily:"system-ui", fontSize:14
    }}>
      <div style={{display:"grid", placeItems:"center", gap:12}}>
        <div style={{
          width:40,height:40,borderRadius:"50%",
          border:"2px solid rgba(0,255,170,.25)",
          borderTopColor:"rgba(0,255,170,.9)",
          animation:"ego-spin 0.9s linear infinite"
        }}/>
        <span>Chargement de la scÃƒÂ¨neÃ¢â‚¬Â¦</span>
      </div>
      <style>
        {`@keyframes ego-spin{to{transform:rotate(360deg)}}`}
      </style>
    </div>
  );
}
