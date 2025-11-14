import { Suspense, useEffect, useRef, useState } from "react";
import * as THREE from "three";

function makeSorghumTexture() {
  const size = 64;
  const canvas = document.createElement("canvas");
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, size, size);
  const cx = size / 2;
  const cy = size / 2;
  const rx = size * 0.34;
  const ry = size * 0.22;
  const grad = ctx.createRadialGradient(cx - 8, cy - 6, rx * 0.1, cx, cy, rx);
  grad.addColorStop(0, "#c7934e");
  grad.addColorStop(0.5, "#9a6a34");
  grad.addColorStop(1, "#5a330f");
  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.ellipse(cx, cy, rx, ry, Math.PI / 12, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = "rgba(255,255,255,.12)";
  ctx.lineWidth = 1.2;
  ctx.beginPath();
  ctx.moveTo(cx - 8, cy);
  ctx.quadraticCurveTo(cx, cy - 2, cx + 8, cy + 1);
  ctx.stroke();
  const texture = new THREE.CanvasTexture(canvas);
  texture.needsUpdate = true;
  texture.flipY = false;
  return texture;
}

function getGlow() {
  const query = new URLSearchParams(window.location.search);
  const value = (query.get("glow") || "soft").toLowerCase();
  if (value === "boost") return { blending: THREE.AdditiveBlending, opacity: 0.72 };
  if (value === "bright") return { blending: THREE.AdditiveBlending, opacity: 0.6 };
  return { blending: THREE.NormalBlending, opacity: 0.72 };
}

function SorghoWebGL() {
  const mountRef = useRef(null);

  useEffect(() => {
    let renderer;
    let scene;
    let camera;
    let points;
    let animId;
    let resizeObserver;
    try {
      const element = mountRef.current;
      const width = element.clientWidth;
      const height = element.clientHeight;

      renderer = new THREE.WebGLRenderer({ antialias: false, alpha: true });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      element.appendChild(renderer.domElement);

      scene = new THREE.Scene();
      scene.background = null;
      camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 100);
      camera.position.set(0, 0.65, 10);

      const memory = window.navigator.deviceMemory || 4;
      const smallViewport = window.innerWidth < 768;
      const base = 90000;
      const memoryFactor = memory < 4 ? 0.35 : memory < 8 ? 0.6 : 1.0;
      const sizeFactor = smallViewport ? 0.7 : 1.0;
      const count = Math.max(40000, Math.floor(base * Math.max(0.25, Math.min(1.0, memoryFactor * sizeFactor))));

      const geometry = new THREE.BufferGeometry();
      const positions = new Float32Array(count * 3);
      const colors = new Float32Array(count * 3);
      const sizes = new Float32Array(count);
      const velocities = new Float32Array(count * 3);

      const bounds = { x: 10, y: 2.2, z: 4.5 };
      const baseColor = new THREE.Color("#c98b4e");
      const tempColor = new THREE.Color();

      for (let i = 0; i < count; i += 1) {
        const index = i * 3;
        positions[index] = (Math.random() - 0.5) * bounds.x;
        positions[index + 1] = (Math.random() - 0.2) * bounds.y;
        positions[index + 2] = (Math.random() - 0.5) * bounds.z;

        tempColor.copy(baseColor).offsetHSL((Math.random() - 0.5) * 0.03, (Math.random() - 0.5) * 0.1, (Math.random() - 0.5) * 0.05);
        colors[index] = tempColor.r;
        colors[index + 1] = tempColor.g;
        colors[index + 2] = tempColor.b;

        sizes[i] = 10 + Math.random() * 12;
        velocities[index] = 0.006 + Math.random() * 0.02;
        velocities[index + 1] = (Math.random() - 0.5) * 0.006;
        velocities[index + 2] = (Math.random() - 0.5) * 0.008;
      }

      geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
      geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
      geometry.setAttribute("size", new THREE.BufferAttribute(sizes, 1));

      const map = makeSorghumTexture();
      const glow = getGlow();
      const material = new THREE.PointsMaterial({
        map,
        transparent: true,
        blending: glow.blending,
        opacity: glow.opacity,
        depthWrite: false,
        size: 0.025,
        sizeAttenuation: true,
        vertexColors: true,
      });
      points = new THREE.Points(geometry, material);
      scene.add(points);

      const onResize = () => {
        const w = element.clientWidth;
        const h = element.clientHeight;
        renderer.setSize(w, h);
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
      };
      resizeObserver = new ResizeObserver(onResize);
      resizeObserver.observe(element);

      const positionAttr = geometry.getAttribute("position");
      let t = 0;
      const WIND = 0.018;
      const SWIRL = 0.004;
      const FALL = 0.00045;

      const animate = () => {
        t += 0.01;
        for (let i = 0; i < count; i += 1) {
          const idx = i * 3;
          positionAttr.array[idx] += velocities[idx] + Math.cos(t * 0.8 + positionAttr.array[idx + 2]) * WIND;
          positionAttr.array[idx + 1] += velocities[idx + 1] + Math.sin(t + i * 0.002) * SWIRL - FALL;
          positionAttr.array[idx + 2] += velocities[idx + 2] + Math.sin(t * 0.6 + positionAttr.array[idx]) * WIND;

          if (positionAttr.array[idx] > bounds.x / 2) positionAttr.array[idx] = -bounds.x / 2;
          if (positionAttr.array[idx] < -bounds.x / 2) positionAttr.array[idx] = bounds.x / 2;
          if (positionAttr.array[idx + 1] > bounds.y / 2) positionAttr.array[idx + 1] = -bounds.y / 2;
          if (positionAttr.array[idx + 1] < -bounds.y / 2) positionAttr.array[idx + 1] = bounds.y / 2;
          if (positionAttr.array[idx + 2] > bounds.z / 2) positionAttr.array[idx + 2] = -bounds.z / 2;
          if (positionAttr.array[idx + 2] < -bounds.z / 2) positionAttr.array[idx + 2] = bounds.z / 2;
        }
        positionAttr.needsUpdate = true;
        renderer.render(scene, camera);
        animId = requestAnimationFrame(animate);
      };
      animate();
    } catch (error) {
      console.error(error);
    }

    return () => {
      try {
        cancelAnimationFrame(animId);
      } catch (error) {
        console.error(error);
      }
      if (resizeObserver) {
        try {
          resizeObserver.disconnect();
        } catch (error) {
          console.error(error);
        }
      }
      try {
        renderer?.dispose();
      } catch (error) {
        console.error(error);
      }
      if (mountRef.current) {
        mountRef.current.innerHTML = "";
      }
    };
  }, []);

  return (
    <div className="section section--dark" style={{ position: "relative", minHeight: "80svh", overflow: "hidden" }}>
      <div ref={mountRef} style={{ position: "absolute", inset: 0 }} />
    </div>
  );
}

export default function HeroSorgho() {
  const [canRender, setCanRender] = useState(false);

  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)")?.matches;
    const webgl = (() => {
      try {
        const canvas = document.createElement("canvas");
        return !!(window.WebGLRenderingContext && (canvas.getContext("webgl") || canvas.getContext("experimental-webgl")));
      } catch {
        return false;
      }
    })();
    setCanRender(!reduce && webgl);
  }, []);

  if (!canRender) {
    return <div style={{ minHeight: "70svh" }} />;
  }

  return (
    <Suspense fallback={<div />}>
      <SorghoWebGL />
    </Suspense>
  );
}

