// src/three/HeroWater.jsx
import { useEffect, useRef } from "react";
import * as THREE from "three";

export default function HeroWater() {
  const mountRef = useRef(null);
  const rafRef = useRef(null);

  useEffect(() => {
    const container = mountRef.current;
    const scene = new THREE.Scene();

    // Caméra
    const camera = new THREE.PerspectiveCamera(
      45,
      window.innerWidth / window.innerHeight,
      0.1,
      100
    );
    camera.position.set(0, 1.2, 3);

    // Renderer
    const renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true, // fond transparent pour se fondre dans le dégradé CSS
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    container.appendChild(renderer.domElement);
    renderer.domElement.className = "three-bg"; // style via CSS

    // Lumière douce
    const light = new THREE.DirectionalLight(0x66ffcc, 1.1);
    light.position.set(2, 3, 2);
    scene.add(light);
    scene.add(new THREE.AmbientLight(0x224433, 0.6));

    // Plan “eau” — Shader simple (ondulations + specular doux)
    const geometry = new THREE.PlaneGeometry(8, 8, 256, 256);
    geometry.rotateX(-Math.PI / 2);

    const uniforms = {
      uTime: { value: 0 },
      uColorA: { value: new THREE.Color("#07251D") }, // sombre
      uColorB: { value: new THREE.Color("#0a2f26") }, // léger dégradé
      uSpecular: { value: 0.4 },
    };

    const material = new THREE.ShaderMaterial({
      uniforms,
      vertexShader: /* glsl */`
        uniform float uTime;
        varying vec3 vNormal;
        varying vec3 vPos;
        void main(){
          vec3 pos = position;
          float f = sin((pos.x*0.75 + uTime*0.8))*0.02
                  + sin((pos.z*1.10 + uTime*1.2))*0.03;
          pos.y += f;
          vPos = pos;
          vNormal = normalMatrix * normalize(normal);
          gl_Position = projectionMatrix * modelViewMatrix * vec4(pos,1.0);
        }
      `,
      fragmentShader: /* glsl */`
        uniform vec3 uColorA;
        uniform vec3 uColorB;
        uniform float uSpecular;
        varying vec3 vNormal;
        varying vec3 vPos;
        void main(){
          // dégradé en fonction de la distance
          float d = clamp(length(vPos.xz)/4.0, 0.0, 1.0);
          vec3 base = mix(uColorB, uColorA, d);

          // specular simple (feint reflet menthe)
          vec3 n = normalize(vNormal);
          vec3 l = normalize(vec3(0.4, 1.0, 0.2));
          float spec = pow(max(dot(reflect(-l, n), vec3(0,1,0)), 0.0), 32.0) * uSpecular;

          // liseré menthe subtil
          float rim = pow(1.0 - max(dot(n, vec3(0,1,0)), 0.0), 2.0);
          vec3 mint = vec3(0.0, 1.0, 0.64);
          vec3 col = base + mint * (spec + rim*0.08);

          gl_FragColor = vec4(col, 0.85); // alpha < 1 pour fondre
        }
      `,
      transparent: true,
      side: THREE.DoubleSide,
    });

    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.y = -0.25;
    scene.add(mesh);

    // Resize
    const onResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };
    window.addEventListener("resize", onResize);

    // RAF
    const clock = new THREE.Clock();
    const tick = () => {
      uniforms.uTime.value = clock.getElapsedTime();
      renderer.render(scene, camera);
      rafRef.current = requestAnimationFrame(tick);
    };
    tick();

    // Clean
    return () => {
      cancelAnimationFrame(rafRef.current);
      window.removeEventListener("resize", onResize);
      geometry.dispose();
      material.dispose();
      renderer.dispose();
      container.removeChild(renderer.domElement);
    };
  }, []);

  return <div ref={mountRef} className="three-container" />;
}
