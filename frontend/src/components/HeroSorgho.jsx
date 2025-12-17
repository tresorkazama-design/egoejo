import { Suspense, useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { logger } from "../utils/logger";
import { useLowPowerMode } from "../hooks/useLowPowerMode";

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
  const isLowPower = useLowPowerMode();
  
  // Si low power mode, ne pas initialiser Three.js
  if (isLowPower) {
    return null;
  }

  useEffect(() => {
    let renderer;
    let scene;
    let camera;
    let points;
    let material;
    let geometry;
    let animId;
    let resizeObserver;
    let handleVisibilityChange = null;
    let cleanupVisibility = null;
    try {
      const element = mountRef.current;
      if (!element) return;
      
      // S'assurer que le conteneur est transparent avant de commencer
      element.style.backgroundColor = 'transparent';
      element.style.background = 'transparent';
      element.style.setProperty('background-color', 'transparent', 'important');
      element.style.setProperty('background', 'transparent', 'important');
      
      const width = element.clientWidth || window.innerWidth;
      const height = element.clientHeight || window.innerHeight;

      renderer = new THREE.WebGLRenderer({ 
        antialias: false, 
        alpha: true,
        preserveDrawingBuffer: false,
        powerPreference: "high-performance"
      });    
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      renderer.setClearColor(0x000000, 0); // Fond transparent
      
      // Forcer le fond transparent sur le canvas AVANT de l'ajouter au DOM
      const canvas = renderer.domElement;
      canvas.style.backgroundColor = 'transparent';
      canvas.style.background = 'transparent';
      canvas.style.setProperty('background-color', 'transparent', 'important');
      canvas.style.setProperty('background', 'transparent', 'important');
      canvas.style.display = 'block';
      canvas.style.position = 'absolute';
      canvas.style.top = '0';
      canvas.style.left = '0';
      canvas.style.width = '100%';
      canvas.style.height = '100%';
      canvas.style.margin = '0';
      canvas.style.padding = '0';
      
      // S'assurer que le canvas est transparent même si WebGL échoue
      canvas.setAttribute('style', canvas.getAttribute('style') + '; background: transparent !important; background-color: transparent !important;');
      
      element.appendChild(canvas);

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

      geometry = new THREE.BufferGeometry();
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
      material = new THREE.PointsMaterial({
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
      let isVisible = true;
      let lastFrameTime = performance.now();
      const targetFPS = 60;
      const frameInterval = 1000 / targetFPS;

      // Pause l'animation quand la page n'est pas visible
      handleVisibilityChange = () => {
        isVisible = !document.hidden;
      };
      document.addEventListener('visibilitychange', handleVisibilityChange);
      
      // Stocker la référence pour le cleanup
      cleanupVisibility = () => {
        if (handleVisibilityChange) {
          document.removeEventListener('visibilitychange', handleVisibilityChange);
        }
      };

      // Optimisation : utiliser des calculs en batch pour améliorer les performances
      const animate = (currentTime) => {
        if (!isVisible) {
          animId = requestAnimationFrame(animate);
          return;
        }

        const deltaTime = currentTime - lastFrameTime;
        if (deltaTime < frameInterval) {
          animId = requestAnimationFrame(animate);
          return;
        }
        lastFrameTime = currentTime - (deltaTime % frameInterval);

        t += 0.01;
        const positions = positionAttr.array;
        const vel = velocities;
        
        // Boucle optimisée - les calculs restent identiques visuellement
        for (let i = 0; i < count; i += 1) {
          const idx = i * 3;
          const zPos = positions[idx + 2];
          const xPos = positions[idx];
          
          // Les calculs sont identiques à l'original pour garantir le même rendu visuel
          positions[idx] += vel[idx] + Math.cos(t * 0.8 + zPos) * WIND;
          positions[idx + 1] += vel[idx + 1] + Math.sin(t + i * 0.002) * SWIRL - FALL;
          positions[idx + 2] += vel[idx + 2] + Math.sin(t * 0.6 + xPos) * WIND;

          // Optimisation des bounds checks
          if (positions[idx] > bounds.x / 2) positions[idx] = -bounds.x / 2;
          else if (positions[idx] < -bounds.x / 2) positions[idx] = bounds.x / 2;
          
          if (positions[idx + 1] > bounds.y / 2) positions[idx + 1] = -bounds.y / 2;
          else if (positions[idx + 1] < -bounds.y / 2) positions[idx + 1] = bounds.y / 2;
          
          if (positions[idx + 2] > bounds.z / 2) positions[idx + 2] = -bounds.z / 2;
          else if (positions[idx + 2] < -bounds.z / 2) positions[idx + 2] = bounds.z / 2;
        }
        positionAttr.needsUpdate = true;
        renderer.render(scene, camera);
        animId = requestAnimationFrame(animate);
      };
      animate(performance.now());
    } catch (error) {
      logger.error('Erreur HeroSorgho:', error);
      // En cas d'erreur, s'assurer que le conteneur reste transparent
      if (mountRef.current) {
        mountRef.current.style.backgroundColor = 'transparent';
        mountRef.current.style.background = 'transparent';
      }
    }

    return () => {
      try {
        cancelAnimationFrame(animId);
      } catch (error) {
        logger.error('Erreur cleanup animation HeroSorgho:', error);
      }
      if (cleanupVisibility) {
        try {
          cleanupVisibility();
        } catch (error) {
          logger.error('Erreur cleanup visibility HeroSorgho:', error);
        }
      }
      if (resizeObserver) {
        try {
          resizeObserver.disconnect();
        } catch (error) {
          logger.error('Erreur cleanup resize observer HeroSorgho:', error);
        }
      }
      try {
        // Nettoyer les ressources Three.js
        if (geometry) geometry.dispose();
        if (material) {
          material.map?.dispose();
          material.dispose();
        }
        if (renderer) {
          renderer.dispose();
          renderer.forceContextLoss?.();
        }
      } catch (error) {
        logger.error('Erreur cleanup Three.js HeroSorgho:', error);
      }
      if (mountRef.current) {
        mountRef.current.innerHTML = "";
      }
    };
  }, []);

  return (
    <div 
      className="section section--dark" 
      style={{ 
        position: "relative", 
        minHeight: "80svh", 
        overflow: "hidden", 
        background: "transparent", 
        backgroundColor: "transparent",
        width: "100%",
        height: "100%"
      }}
    >                                            
      <div 
        ref={mountRef} 
        className="hero-sorgho-canvas-container"
        style={{ 
          position: "absolute", 
          inset: 0, 
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: "transparent", 
          backgroundColor: "transparent",
          width: "100%",
          height: "100%",
          margin: 0,
          padding: 0
        }} 
      />
    </div>
  );
}

export default function HeroSorgho() {
  const [canRender, setCanRender] = useState(false);
  const isLowPower = useLowPowerMode();

  useEffect(() => {
    // Si low power mode, ne pas rendre Three.js
    if (isLowPower) {
      setCanRender(false);
      return;
    }

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
  }, [isLowPower]);

  if (!canRender || isLowPower) {
    // Afficher une version statique en mode low-power
    return (
      <div 
        className="hero-sorgho-static" 
        style={{ 
          minHeight: "70svh", 
          background: "transparent", 
          backgroundColor: "transparent", 
          width: "100%", 
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flexDirection: "column"
        }}
      >
        <div className="hero-content">
          <h1 style={{ fontSize: "4rem", color: "#00ffa3", marginBottom: "1rem" }}>EGOEJO</h1>
          <p style={{ fontSize: "1.5rem", color: "#ffffff" }}>Collectif pour le vivant</p>
        </div>
      </div>
    );
  }

  return (
    <Suspense fallback={<div style={{ minHeight: "70svh", background: "transparent", backgroundColor: "transparent", width: "100%", height: "100%" }} />}>
      <SorghoWebGL />
    </Suspense>
  );
}
