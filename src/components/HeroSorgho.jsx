import { useEffect, useRef, useState, Suspense } from "react";

/* ---------- Fallback (sans WebGL) ---------- */
function FallbackHero() {
  return (
    <div className="section section--dark" style={{minHeight:"70svh", display:"grid", placeItems:"center", textAlign:"center"}}>
      <div>
        <h1 style={{fontSize:"clamp(40px,8vw,112px)", lineHeight:.9, margin:0}}>
          RELIONS Lâ€™HISTOIRE AU <span className="accent">FUTUR</span>
        </h1>
        <p style={{opacity:.8, marginTop:12}}>Une communautÃ© qui transforme la lecture et lâ€™analyse en impact social.</p>
        <div style={{marginTop:24, display:"flex", gap:12, justifyContent:"center", flexWrap:"wrap"}}>
          <a className="btn" href="#projets">DÃ©couvrir nos projets</a>
          <a className="btn btn--ghost" href="#soutenir">Soutenir</a>
        </div>
      </div>
    </div>
  );
}

/* ---------- Texture â€œgrain de sorghoâ€ ---------- */
function makeSorghumTexture(THREE) {
  const size = 64;
  const c = document.createElement("canvas");
  c.width = c.height = size;
  const ctx = c.getContext("2d");
  ctx.clearRect(0,0,size,size);
  const cx = size/2, cy = size/2;
  const rx = size*0.34, ry = size*0.22;
  const grad = ctx.createRadialGradient(cx-8, cy-6, rx*0.1, cx, cy, rx);
  grad.addColorStop(0,   "#e3b577");
  grad.addColorStop(0.5, "#c98b4e");
  grad.addColorStop(1,   "#814b17");
  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.ellipse(cx, cy, rx, ry, Math.PI/12, 0, Math.PI*2);
  ctx.fill();
  ctx.strokeStyle = "rgba(255,255,255,.12)";
  ctx.lineWidth = 1.2;
  ctx.beginPath();
  ctx.moveTo(cx-8, cy);
  ctx.quadraticCurveTo(cx, cy-2, cx+8, cy+1);
  ctx.stroke();
  const tex = new THREE.CanvasTexture(c);
  tex.needsUpdate = true;
  tex.flipY = false;
  return tex;
}

/* ---------- WebGL Hero (nuage de grains) ---------- */
function SorghoWebGL() {
  const mountRef = useRef(null);

  useEffect(() => {
    let renderer, scene, camera, points, animId, ro;
    let velocities, bounds;
    (async () => {
      const THREE = await import("three");
      const el = mountRef.current;
      const w = el.clientWidth, h = el.clientHeight;

      renderer = new THREE.WebGLRenderer({ antialias:false, alpha:true });
      renderer.setSize(w, h);
      renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
      el.appendChild(renderer.domElement);

      scene = new THREE.Scene(); scene.background = null;
      camera = new THREE.PerspectiveCamera(60, w/h, 0.1, 100);
      camera.position.set(0, 0.6, 7);

      const COUNT = 4500;
      const geo = new THREE.BufferGeometry();
      const positions = new Float32Array(COUNT*3);
      const colors    = new Float32Array(COUNT*3);
      const sizes     = new Float32Array(COUNT);

      bounds = { x: 12, y: 5, z: 10 };
      velocities = new Float32Array(COUNT*3);

      const base = new THREE.Color("#c98b4e");
      const tmp  = new THREE.Color();

      for (let i=0;i<COUNT;i++){
        const ix=i*3;
        positions[ix]   = (Math.random()-0.5)*bounds.x;
        positions[ix+1] = (Math.random()-0.2)*bounds.y;
        positions[ix+2] = (Math.random()-0.5)*bounds.z;

        tmp.copy(base).offsetHSL((Math.random()-0.5)*0.03, (Math.random()-0.5)*0.1, (Math.random()-0.5)*0.05);
        colors[ix]   = tmp.r; colors[ix+1] = tmp.g; colors[ix+2] = tmp.b;

        sizes[i] = 10 + Math.random()*12;

        velocities[ix]   = 0.006 + Math.random()*0.02;
        velocities[ix+1] = (Math.random()-0.5)*0.006;
        velocities[ix+2] = (Math.random()-0.5)*0.008;
      }
      geo.setAttribute("position", new THREE.BufferAttribute(positions,3));
      geo.setAttribute("color",    new THREE.BufferAttribute(colors,3));
      geo.setAttribute("size",     new THREE.BufferAttribute(sizes,1));

      const map = makeSorghumTexture(THREE);
      const mat = new THREE.PointsMaterial({
        map, transparent:true, alphaTest: 0.3, depthWrite:false,
        size: 2.2, sizeAttenuation:true, vertexColors:true
      });
      points = new THREE.Points(geo, mat); scene.add(points);

      const onResize = () => {
        const W = el.clientWidth, H = el.clientHeight;
        renderer.setSize(W,H);
        camera.aspect = W/H; camera.updateProjectionMatrix();
      };
      ro = new ResizeObserver(onResize); ro.observe(el);

      const pos = geo.getAttribute("position");
      let t=0;
      const animate = () => {
        t+=0.01;
        for (let i=0;i<COUNT;i++){
          const ix=i*3;
          pos.array[ix]   += velocities[ix];
          pos.array[ix+1] += velocities[ix+1] + Math.sin(t+i)*0.0008;
          pos.array[ix+2] += velocities[ix+2];

          if (pos.array[ix]   >  bounds.x/2) pos.array[ix]   = -bounds.x/2;
          if (pos.array[ix]   < -bounds.x/2) pos.array[ix]   =  bounds.x/2;
          if (pos.array[ix+1] >  bounds.y/2) pos.array[ix+1] = -bounds.y/2;
          if (pos.array[ix+1] < -bounds.y/2) pos.array[ix+1] =  bounds.y/2;
          if (pos.array[ix+2] >  bounds.z/2) pos.array[ix+2] = -bounds.z/2;
          if (pos.array[ix+2] < -bounds.z/2) pos.array[ix+2] =  bounds.z/2;
        }
        pos.needsUpdate = true;
        renderer.render(scene, camera);
        animId = requestAnimationFrame(animate);
      };
      animate();

      return () => {
        cancelAnimationFrame(animId);
        ro && ro.disconnect();
        renderer.dispose();
        el.innerHTML = "";
      };
    })();

    return () => void 0;
  }, []);

  return (
    <div className="section section--dark" style={{position:"relative", minHeight:"80svh", overflow:"hidden"}}>
      <div ref={mountRef} style={{position:"absolute", inset:0}}/>
      <div style={{position:"relative", zIndex:2, display:"grid", placeItems:"center", minHeight:"80svh", textAlign:"center"}}>
        <div>
          <h1 style={{fontSize:"clamp(40px,8vw,112px)", lineHeight:.9, margin:0}}>
            RELIONS Lâ€™HISTOIRE AU <span className="accent">FUTUR</span>
          </h1>
          <p style={{opacity:.8, marginTop:12}}>Grains de <strong>sorgho</strong>, idÃ©es en mouvement.</p>
          <div style={{marginTop:24, display:"flex", gap:12, justifyContent:"center", flexWrap:"wrap"}}>
            <a className="btn" href="#projets">DÃ©couvrir nos projets</a>
            <a className="btn btn--ghost" href="#soutenir">Soutenir</a>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ---------- Wrapper (auto WebGL / motion) ---------- */
export default function HeroSorgho(){
  const [ok, setOk] = useState(false);
  useEffect(() => {
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const webgl = (() => {
      try {
        const canvas = document.createElement("canvas");
        return !!(window.WebGLRenderingContext &&
          (canvas.getContext("webgl") || canvas.getContext("experimental-webgl")));
      } catch { return false; }
    })();
    setOk(!reduce && webgl);
  }, []);
  return ok ? <Suspense fallback={<FallbackHero/>}><SorghoWebGL/></Suspense> : <FallbackHero/>;
}