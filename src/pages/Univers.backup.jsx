// src/pages/Univers.jsx
import React, { useMemo, useRef, useEffect, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Stars, Html, Environment, SoftShadows } from "@react-three/drei";
import * as THREE from "three";
import CustomCursor from "../cursor.jsx";

/* ---------- Hook parallax (renvoie {x,y} dans [-1,1]) ---------- */
function useParallax() {
  const [par, setPar] = useState({ x: 0, y: 0 });
  useEffect(() => {
    const onMove = (e) => {
      const nx = (e.clientX / window.innerWidth) * 2 - 1;
      const ny = (e.clientY / window.innerHeight) * 2 - 1;
      setPar({ x: nx, y: ny });
    };
    window.addEventListener("mousemove", onMove, { passive: true });
    return () => window.removeEventListener("mousemove", onMove);
  }, []);
  return par;
}

/* ---------- Applique le parallax au group ciblé ---------- */
function ParallaxGroup({ refObj, par, rx = 0.06, ry = 0.12, ease = 0.08 }) {
  useFrame(() => {
    if (!refObj.current) return;
    const targetX = -par.y * rx; // inversé pour une sensation naturelle
    const targetY =  par.x * ry;
    refObj.current.rotation.x += (targetX - refObj.current.rotation.x) * ease;
    refObj.current.rotation.y += (targetY - refObj.current.rotation.y) * ease;
  });
  return null;
}

/* ---------------- Sorgho (plante) ---------------- */
function Sorgho({
  height = 1.4,
  leafCount = 6,
  panicleBranches = 10,
  windStrength = 0.22,
  growthSeconds = 5.5,
}) {
  const group = useRef();
  const timeRef = useRef({ t0: performance.now() });

  const stemMat = useMemo(
    () => new THREE.MeshStandardMaterial({ color: "#2f6e38", roughness: 0.9, metalness: 0 }),
    []
  );
  const leafMat = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: "#245d31",
        roughness: 0.85,
        metalness: 0,
        side: THREE.DoubleSide,
      }),
    []
  );
  const panicleMat = useMemo(
    () => new THREE.MeshStandardMaterial({ color: "#d8bf67", roughness: 0.6, metalness: 0.05 }),
    []
  );

  const sphere = useMemo(() => new THREE.SphereGeometry(0.012, 10, 10), []);
  const stemGeo = useMemo(
    () => new THREE.CylinderGeometry(0.017, 0.024, height, 10, 1),
    [height]
  );

  const leafShape = useMemo(() => {
    const s = new THREE.Shape();
    const w = 0.085;
    s.moveTo(0, 0);
    s.quadraticCurveTo(w * 0.45, 0.3, 0, 0.7);
    s.quadraticCurveTo(-w * 0.45, 0.3, 0, 0);
    return s;
  }, []);

  const leaves = useMemo(() => {
    const arr = [];
    for (let i = 0; i < leafCount; i++) {
      const y = (i / (leafCount + 2)) * height * 0.9 + 0.2;
      const side = i % 2 === 0 ? 1 : -1;
      const spread = 0.34 + 0.22 * Math.random();
      const points = [
        new THREE.Vector3(0, y, 0),
        new THREE.Vector3(0.18 * side, y + 0.25, 0.08 * side),
        new THREE.Vector3(0.22 * side, y + 0.48, 0.12 * side),
      ];
      const curve = new THREE.CatmullRomCurve3(points);
      const extrudeSettings = { steps: 24, bevelEnabled: false, extrudePath: curve, depth: 0.001 };
      const geom = new THREE.ExtrudeGeometry(leafShape, extrudeSettings);
      geom.rotateZ(THREE.MathUtils.degToRad(side * THREE.MathUtils.randFloat(7, 12)));
      geom.scale(1.0, spread, 1.0);
      arr.push({ geom });
    }
    return arr;
  }, [leafCount, height, leafShape]);

  const panicle = useMemo(() => {
    const instances = [];
    const baseY = height * 0.9;
    for (let b = 0; b < panicleBranches; b++) {
      const angle = (b / panicleBranches) * Math.PI * 2;
      const len = THREE.MathUtils.lerp(0.14, 0.26, Math.random());
      const dir = new THREE.Vector3(Math.cos(angle), 0.25, Math.sin(angle)).normalize();
      const start = new THREE.Vector3(0, baseY, 0);
      const end = start.clone().addScaledVector(dir, len);
      const count = 18 + Math.floor(Math.random() * 10);
      for (let i = 0; i < count; i++) {
        const t = i / count;
        const pos = new THREE.Vector3().lerpVectors(start, end, t);
        pos.x += (Math.random() - 0.5) * 0.012;
        pos.z += (Math.random() - 0.5) * 0.012;
        instances.push(pos);
      }
    }
    return { positions: instances };
  }, [height, panicleBranches]);

  useFrame(({ clock }) => {
    const elapsed = (performance.now() - timeRef.current.t0) / 1000;
    const growth = THREE.MathUtils.clamp(elapsed / growthSeconds, 0, 1);
    const w = windStrength;
    const sway =
      Math.sin(clock.elapsedTime * 0.9) * w +
      Math.sin(clock.elapsedTime * 1.5) * w * 0.6;

    if (group.current) {
      group.current.scale.y = 0.2 + growth * 0.8;
      group.current.rotation.z = sway * 0.1;
      group.current.rotation.y = Math.sin(clock.elapsedTime * 0.15) * 0.08;
    }
  });

  return (
    <group ref={group} position={[0.22, 0, 0]}>
      <mesh geometry={stemGeo} material={stemMat} position={[0, height / 2, 0]} castShadow />
      {leaves.map((lf, idx) => (
        <mesh key={idx} geometry={lf.geom} material={leafMat} castShadow />
      ))}
      <instancedMesh
        args={[sphere, panicleMat, panicle.positions.length]}
        frustumCulled={false}
        castShadow
      >
        {panicle.positions.map((p, i) => {
          const m = new THREE.Matrix4();
          m.setPosition(p);
          return <primitive key={i} object={m} attach="instanceMatrix" />;
        })}
      </instancedMesh>
    </group>
  );
}

/* ---------------- Carte (Html overlay) ---------------- */
function Card() {
  return (
    <Html center position={[-0.25, -0.1, 0]} transform distanceFactor={1.3}>
      <div
        style={{
          width: "min(92vw, 420px)",
          padding: "22px 26px",
          borderRadius: "18px",
          background: "linear-gradient(180deg, rgba(10,28,22,0.92), rgba(6,18,14,0.9))",
          boxShadow: "0 0 50px rgba(0,255,170,0.14), 0 0 16px rgba(0,255,170,0.12) inset",
          border: "1px solid rgba(0,255,160,0.10)",
          color: "#dffdf5",
          lineHeight: 1.6,
          fontFamily: "Poppins, system-ui, sans-serif",
          textAlign: "left",
          backdropFilter: "blur(4px)",
        }}
      >
        <h2
          style={{
            color: "#7affcf",
            fontSize: "28px",
            margin: 0,
            textShadow: "0 0 12px rgba(0,255,170,0.35)",
            letterSpacing: 1,
          }}
        >
          EGOEJO
        </h2>
        <p style={{ marginTop: 10, fontSize: 16 }}>
          Ici, le don n’est <em>pas</em> une perte — c’est une énergie qui <em>circule</em>,{" "}
          <em>relie</em> et <em>féconde</em>. Chaque contribution devient un élan&nbsp;: une
          graine de lumière semée pour un monde plus humain, plus durable.
        </p>
      </div>
    </Html>
  );
}

/* ---------------- Scène ---------------- */
export default function Univers() {
  const isMobile =
    typeof window !== "undefined" &&
    window.matchMedia("(pointer: coarse)").matches;

  // Parallax
  const sceneRef = useRef(null);
  const par = useParallax();

  return (
    <div
      className={isMobile ? "" : "hide-default-cursor"}
      style={{ width: "100%", height: "100%", background: "black" }}
    >
      {!isMobile && <CustomCursor />}

      <Canvas shadows camera={{ position: [0.5, 1.15, 2.5], fov: 45 }} gl={{ antialias: true }}>
        <color attach="background" args={["#030806"]} />
        <SoftShadows size={30} samples={24} />

        {/* pilote le parallax du groupe ci-dessous */}
        <ParallaxGroup refObj={sceneRef} par={par} />

        {/* Lumières / environnement */}
        <ambientLight intensity={0.35} />
        <directionalLight
          position={[2, 5, 3]}
          intensity={1.1}
          castShadow
          shadow-mapSize-width={1024}
          shadow-mapSize-height={1024}
        />
        <hemisphereLight intensity={0.35} groundColor="#0c1d16" />
        <Environment preset="forest" />
        <Stars radius={100} depth={30} count={1800} factor={2} fade speed={0.2} />

        {/* >>> Groupe entier soumis au parallax <<< */}
        <group ref={sceneRef}>
          {/* Sol */}
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.4, 0]} receiveShadow>
            <planeGeometry args={[10, 10]} />
            <shadowMaterial transparent opacity={0.25} />
          </mesh>

          {/* Contenu */}
          <group position={[0, -0.4, 0]}>
            <Sorgho />
          </group>
          <Card />
        </group>

        <OrbitControls enablePan={false} enableZoom={false} enableRotate={false} makeDefault />
      </Canvas>
    </div>
  );
}
