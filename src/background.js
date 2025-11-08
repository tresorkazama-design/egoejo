import * as THREE from "three";

document.addEventListener("DOMContentLoaded", () => {
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
  const renderer = new THREE.WebGLRenderer({ alpha: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);
  camera.position.z = 5;

  // LumiÃ¨re douce
  const light = new THREE.PointLight(0x36f9b1, 1.2);
  light.position.set(2, 3, 5);
  scene.add(light);

  // --- 1ï¸âƒ£ Eau : onde douce avec points lumineux ---
  const waterGeometry = new THREE.PlaneGeometry(15, 15, 50, 50);
  const waterMaterial = new THREE.MeshPhongMaterial({
    color: 0x001f1f,
    shininess: 80,
    transparent: true,
    opacity: 0.8,
    side: THREE.DoubleSide,
    wireframe: true
  });
  const water = new THREE.Mesh(waterGeometry, waterMaterial);
  water.rotation.x = -Math.PI / 2.3;
  water.position.y = -1.2;
  scene.add(water);

  // --- 2ï¸âƒ£ Particules lÃ©gÃ¨res (air, esprit) ---
  const particlesGeometry = new THREE.BufferGeometry();
  const particleCount = 600;
  const positions = new Float32Array(particleCount * 3);
  for (let i = 0; i < particleCount * 3; i++) {
    positions[i] = (Math.random() - 0.5) * 10;
  }
  particlesGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  const particlesMaterial = new THREE.PointsMaterial({
    color: 0x36f9b1,
    size: 0.02,
    transparent: true
  });
  const particles = new THREE.Points(particlesGeometry, particlesMaterial);
  scene.add(particles);

  // --- 3ï¸âƒ£ Ã‰pis de sorgho stylisÃ©s ---
  const sorghoGeometry = new THREE.ConeGeometry(0.05, 0.3, 10);
  const sorghoMaterial = new THREE.MeshStandardMaterial({ color: 0xffcc66, roughness: 0.6 });
  const sorghos = [];
  for (let i = 0; i < 10; i++) {
    const sorgho = new THREE.Mesh(sorghoGeometry, sorghoMaterial);
    sorgho.position.set((Math.random() - 0.5) * 5, -1, (Math.random() - 0.5) * 5);
    scene.add(sorgho);
    sorghos.push(sorgho);
  }

  // Animation continue
  function animate() {
    requestAnimationFrame(animate);
    water.rotation.z += 0.001;
    particles.rotation.y += 0.0008;
    sorghos.forEach(s => s.rotation.y += 0.005);
    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
});
