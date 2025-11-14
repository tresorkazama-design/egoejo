import { useEffect, useRef, useState, Suspense } from "react";
import * as THREE from "three";

/* ---------- texture "grain de sorgho" ---------- */
function makeSorghumTexture() {
  const size = 64;
  const c = document.createElement("canvas");
  c.width = c.height = size;
  const ctx = c.getContext("2d");
  ctx.clearRect(0,0,size,size);
  const cx = size/2, cy = size/2;
  const rx = size*0.34, ry = size*0.22;
  const grad = ctx.createRadialGradient(cx-8, cy-6, rx*0.1, cx, cy, rx);
  grad.addColorStop(0,   "#c7934e"); // centre un peu assombri
  grad.addColorStop(0.5, "#9a6a34");
  grad.addColorStop(1,   "#5a330f");
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

/* ---------- Glow contrôlé par query (?glow=soft|bright|boost) ---------- */
function getGlow(){
  const q = new URLSearchParams(location.search);
  const g = (q.get("glow") || "soft").toLowerCase();
  if (g === "boost")  return { blending: THREE.AdditiveBlending, opacity: 0.72 };
  if (g === "bright") return { blending: THREE.AdditiveBlending, opacity: 0.60 };
  return                { blending: THREE.NormalBlending,   opacity: 0.72 }; // défaut : doux mais visible
}

/* ---------- WebGL Hero (nuage de grains) ---------- */
function SorghoWebGL() {
  const mountRef = useRef(null);

  useEffect(() => {
    let renderer, scene, camera, points, animId, ro;
    try {
      const el = mountRef.current;
      const w = el.clientWidth, h = el.clientHeight;

      renderer = new THREE.WebGLRenderer({ antialias:false, alpha:true });
      renderer.setSize(w, h);
      renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
      el.appendChild(renderer.domElement);

      scene = new THREE.Scene(); scene.background = null;
      camera = new THREE.PerspectiveCamera(60, w/h, 0.1, 100);
      camera.position.set(0, 0.65, 10);

      // densité auto (base sur deviceMemory)
      const mem   = (navigator.deviceMemory || 4);
      const small = (window.innerWidth < 768);
      const base  = 90000;
      const mFactor = (mem < 4 ? 0.35 : (mem < 8 ? 0.6 : 1.0));
      const sFactor = small ? 0.70 : 1.0;
      const COUNT  = Math.max(40000, Math.floor(base * Math.max(0.25, Math.min(1.0, mFactor*sFactor))));

      const geo = new THREE.BufferGeometry();
      const positions = new Float32Array(COUNT*3);
      const colors    = new Float32Array(COUNT*3);
      const sizes     = new Float32Array(COUNT);

      const bounds = { x:10, y:2.2, z:4.5 };
      const velocities = new Float32Array(COUNT*3);
      const baseCol = new THREE.Color("#c98b4e");
      const tmpCol  = new THREE.Color();

      for (let i=0;i<COUNT;i++){
        const ix = i*3;
        positions[ix]   = (Math.random()-0.5)*bounds.x;
        positions[ix+1] = (Math.random()-0.2)*bounds.y;
        positions[ix+2] = (Math.random()-0.5)*bounds.z;

        tmpCol.copy(baseCol).offsetHSL((Math.random()-0.5)*0.03, (Math.random()-0.5)*0.1, (Math.random()-0.5)*0.05);
        colors[ix]   = tmpCol.r; colors[ix+1] = tmpCol.g; colors[ix+2] = tmpCol.b;

        sizes[i] = 10 + Math.random()*12;
        velocities[ix]   = 0.006 + Math.random()*0.02;
        velocities[ix+1] = (Math.random()-0.5)*0.006;
        velocities[ix+2] = (Math.random()-0.5)*0.008;
      }
      geo.setAttribute("position", new THREE.BufferAttribute(positions,3));
      geo.setAttribute("color",    new THREE.BufferAttribute(colors,3));
      geo.setAttribute("size",     new THREE.BufferAttribute(sizes,1));

      const map = makeSorghumTexture();
      const glow = getGlow();
      const mat = new THREE.PointsMaterial({
        map,
        transparent:true,
        blending: glow.blending,
        opacity: glow.opacity,
        depthWrite:false,
        size: 0.025, // sprite très petit
        sizeAttenuation:true,
        vertexColors:true
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
      const WIND = 0.018, SWIRL=0.004, FALL=0.00045;

      const animate = () => {
        t += 0.01;
        for (let i=0;i<COUNT;i++){
          const ix=i*3;
          pos.array[ix]   += velocities[ix]   + Math.cos(t*0.8 + pos.array[ix+2])*WIND;
          pos.array[ix+1] += velocities[ix+1] + Math.sin(t + i*0.002)*SWIRL - FALL;
          pos.array[ix+2] += velocities[ix+2] + Math.sin(t*0.6 + pos.array[ix])*WIND;

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
    } catch(e){ console.error(e); }

    return () => {
      try { cancelAnimationFrame(animId); } catch{}
      try { ro && ro.disconnect(); } catch{}
      try { renderer && renderer.dispose(); } catch{}
      if (mountRef.current) mountRef.current.innerHTML = "";
    };
  }, []);

  return (
    <div className="section section--dark" style={{position:"relative", minHeight:"80svh", overflow:"hidden"}}>
      <div ref={mountRef} style={{position:"absolute", inset:0}}/>
    </div>
  );
}

/* ---------- wrapper auto ---------- */
export default function HeroSorgho(){
  const [ok, setOk] = useState(false);
  useEffect(() => {
    const reduce = matchMedia("(prefers-reduced-motion: reduce)")?.matches;
    const webgl = (() => {
      try {
        const canvas = document.createElement("canvas");
        return !!(window.WebGLRenderingContext &&
          (canvas.getContext("webgl") || canvas.getContext("experimental-webgl")));
      } catch { return false; }
    })();
    setOk(!reduce && webgl);
  }, []);
  return ok ? <Suspense fallback={<div/>}><SorghoWebGL/></Suspense> : <div style={{minHeight:"70svh"}}/>;
}