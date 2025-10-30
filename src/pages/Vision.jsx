import React from "react";

export default function Vision() {
  return (
    <main style={{
      color:"#dffdf5",
      backgroundColor:"#060b0a",
      padding:"clamp(2rem,2vw,3rem) 6vw",
      maxWidth:"1200px",
      margin:"0 auto",
      lineHeight:1.5,
      fontFamily:"system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif"
    }}>
      <header style={{maxWidth:"800px"}}>
        <h1 style={{
          fontSize:"clamp(1.6rem,1vw,2rem)",
          lineHeight:1.2,
          color:"#74ffd7",
          textShadow:"0 0 20px rgba(0,255,170,.4)"
        }}>
          Réenchanter le monde n’est pas un concept. C’est un lien.
        </h1>
        <p style={{fontSize:"1rem",opacity:.9,marginTop:"1rem"}}>
          Nous vivons dans une civilisation qui a coupé l’humain de la Terre.
          On nous a vendu l’idée que la technique, l’économie et la croissance
          suffiraient à tout réparer. Mais ce système a généré l’épuisement,
          la destruction du vivant, et un vide spirituel. La modernité qui
          promettait le progrès infini nous a aussi donné le mal-être infini.
        </p>
        <p style={{fontSize:"1rem",opacity:.9}}>
          EGOEJO naît dans cette fracture.
        </p>
      </header>

      <section style={{marginTop:"3rem",maxWidth:"800px"}}>
        <h2 style={{color:"#9bf6e5",fontSize:"1.2rem",marginBottom:".5rem"}}>
          1. Ce que nous croyons
        </h2>
        <p style={{fontSize:"1rem",opacity:.9}}>
          Il n’existe pas qu’une seule manière d’habiter le monde. Des peuples,
          des communautés, des femmes, des gardien·ne·s du vivant ont maintenu
          d’autres relations à l’eau, à la nourriture, au soin, aux cycles.
          On les a traités comme « arriérés », « folklore », « tradition ».
          Nous disons : non. Ce ne sont pas des reliques. Ce sont des sources.
        </p>
        <p style={{fontSize:"1rem",opacity:.9}}>
          Notre rôle n’est pas de les idéaliser comme s’ils étaient parfaits.
          Notre rôle est de reconnaître qu’ils portent des savoirs vitaux pour
          la suite. On écoute, on respecte, on soutient. On n’arrive pas en
          sauveur, on arrive en élève.
        </p>
      </section>

      <section style={{marginTop:"2rem",maxWidth:"800px"}}>
        <h2 style={{color:"#9bf6e5",fontSize:"1.2rem",marginBottom:".5rem"}}>
          2. Remettre le féminin vivant au centre
        </h2>
        <p style={{fontSize:"1rem",opacity:.9}}>
          Partout où le féminin (le soin, la régénération, la fertilité,
          la transmission, la protection de l’eau, la capacité de nourrir
          et d’accueillir la vie) a été écrasé, le vivant a été écrasé avec.
        </p>
        <p style={{fontSize:"1rem",opacity:.9}}>
          Nous refusons un monde où le corps des femmes n’est pas sacré,
          où l’eau n’est pas sacrée, où la naissance n’est pas sacrée.
          Remettre le féminin au centre, ce n’est pas du marketing :
          c’est rebrancher nos sociétés à la vie.
        </p>
        <p style={{fontSize:"1rem",opacity:.9}}>
          Les cosmologies où la Terre est une Mère, une Source, une Présence
          ont été ridiculisées par le patriarcat moderne. Nous, on dit :
          elles sont essentielles pour ne pas finir sur une planète morte.
        </p>
      </section>

      <section style={{marginTop:"2rem",maxWidth:"800px"}}>
        <h2 style={{color:"#9bf6e5",fontSize:"1.2rem",marginBottom:".5rem"}}>
          3. Réparer la relation à l’argent
        </h2>
        <p style={{fontSize:"1rem",opacity:.9}}>
          L’argent aujourd’hui est utilisé pour dominer, prendre, extraire.
          Mais l’argent peut aussi circuler comme une offrande, comme un soin,
          comme une façon d’alimenter la vie. Dans beaucoup de cultures, la
          monnaie n’était pas seulement du pouvoir : elle incarnait la
          fertilité, la prospérité partagée, la continuité entre les êtres.
        </p>
        <p style={{fontSize:"1rem",opacity:.9}}>
          Nous voulons revenir à cette idée simple :
          donner n’est pas acheter un pardon moral.
          Donner, c’est participer à ce qui doit continuer.
        </p>
        <p style={{fontSize:"1rem",opacity:.9}}>
          Chez EGOEJO, soutenir quelqu’un, ce n’est pas « faire un don à un projet ».
          C’est entrer dans une alliance vivante. C’est dire :
          « je reconnais ta place dans le tissu du monde,
          et je choisis d’y prendre part avec toi ».
        </p>
      </section>

      <section style={{marginTop:"2rem",maxWidth:"800px"}}>
        <h2 style={{color:"#9bf6e5",fontSize:"1.2rem",marginBottom:".5rem"}}>
          4. Avec qui nous marchons
        </h2>
        <p style={{fontSize:"1rem",opacity:.9}}>
          EGOEJO relie deux familles :
        </p>
        <ul style={{fontSize:"1rem",opacity:.9,lineHeight:1.5,paddingLeft:"1rem"}}>
          <li style={{marginBottom:".75rem"}}>
            <strong style={{color:"#dffdf5"}}>Celles et ceux qui protègent déjà le vivant :</strong>
            gardiennes d’eau, paysannes qui ressuscitent les sols,
            femmes qui tiennent encore des savoirs de naissance,
            communautés qui transmettent des rites de passage non violents.
            Elles et ils n’ont pas besoin d’être « sauvés ».
            Elles et ils existent, et tiennent encore le fil du monde.
          </li>
          <li>
            <strong style={{color:"#dffdf5"}}>Celles et ceux qui veulent agir avec humilité :</strong>
            des gens qui sentent que le modèle dominant est cassé et veulent
            soutenir sans écraser, apprendre sans s’approprier,
            contribuer sans coloniser le récit.
          </li>
        </ul>
        <p style={{fontSize:"1rem",opacity:.9}}>
          EGOEJO est le pont entre ces deux mondes.
        </p>
      </section>
    </main>
  );
}