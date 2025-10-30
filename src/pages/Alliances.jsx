import React from "react";
import GuardianCard from "../components/GuardianCard.jsx";

export default function Alliances() {
  return (
    <main style={{
      minHeight:"100dvh",
      backgroundColor:"#060b0a",
      color:"#dffdf5",
      fontFamily:"system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif",
      padding:"clamp(2rem,2vw,3rem) 6vw"
    }}>
      <header style={{maxWidth:"800px",margin:"0 auto 2rem auto"}}>
        <h1 style={{
          fontSize:"clamp(1.5rem,1vw,2rem)",
          lineHeight:1.2,
          color:"#74ffd7",
          textShadow:"0 0 20px rgba(0,255,170,.4)"
        }}>
          Alliances vivantes
        </h1>
        <p style={{fontSize:"1rem",opacity:.9,lineHeight:1.5}}>
          Ici nous présentons des personnes et des communautés qui protègent
          déjà le vivant. Pas des « projets à financer » comme dans une
          plateforme classique. Des mondes vivants auxquels tu peux te relier.
        </p>
        <p style={{fontSize:"1rem",opacity:.9,lineHeight:1.5}}>
          Leur rôle n’est pas d’être « inspirants ». Leur rôle est d’exister.
          Le nôtre est de les soutenir sans les déformer.
        </p>
      </header>

      <section style={{
        display:"grid",
        gridTemplateColumns:"repeat(auto-fit,minmax(min(100%,360px),1fr))",
        gap:"1.5rem",
        maxWidth:"1200px",
        margin:"0 auto"
      }}>
        <GuardianCard
          name="Collectif des Mères de la Source"
          protects="Une nappe d’eau qui nourrit trois villages"
          whySacred="Elles veillent sur l’accès à l’eau, transmettent aux enfants
          le lien entre eau et vie, et maintiennent les chants de remerciement
          à la source. L’eau n’est pas une ressource. C’est une parente."
          needNow="3 cuves de récupération d’eau de pluie pour survivre à la saison sèche."
        />

        <GuardianCard
          name="Gardiens du Sorgho Ancien"
          protects="Des variétés de semences résilientes au climat"
          whySacred="Ils cultivent encore des graines qui résistent à la chaleur,
          et enseignent comment nourrir sans dépendre du pétrole, ni des
          intrants chimiques. C’est de l’autonomie alimentaire, pas du business."
          needNow="Matériel simple de séchage et stockage des graines pour éviter la perte."
        />
      </section>

      <footer style={{maxWidth:"800px",margin:"3rem auto 0 auto",fontSize:".9rem",opacity:.6,lineHeight:1.4}}>
        <p>
          Tu fais partie d’un collectif qui protège le vivant, l’eau,
          la souveraineté alimentaire, les rites de passage, le soin corporel,
          ou la transmission d’un savoir vivant ? Parlons.
        </p>
        <p>
          EGOEJO n’achète pas ton image. EGOEJO ne parle pas à ta place.
          EGOEJO te laisse exister et invite d’autres à marcher avec toi.
        </p>
      </footer>
    </main>
  );
}