import * as THREE from 'three';
import { gsap } from 'gsap';

// --- Scène ---
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('bg'), alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);

// --- Lumières ---
const light1 = new THREE.PointLight(0xb4ffb4, 1.5);
light1.position.set(2, 2, 5);
scene.add(light1);

const light2 = new THREE.PointLight(0x7fbfff, 1);
light2.position.set(-3, -2, -5);
scene.add(light2);

// --- Fond dynamique ---
const geometry = new THREE.SphereGeometry(4, 64, 64);
const material = new THREE.MeshStandardMaterial({
  color: 0x143d28,
  emissive: 0x224d38,
  metalness: 0.3,
  roughness: 0.8
});
const sphere = new THREE.Mesh(geometry, material);
scene.add(sphere);

camera.position.z = 6;

// --- Animation continue ---
function animate() {
  requestAnimationFrame(animate);
  sphere.rotation.y += 0.001;
  sphere.rotation.x += 0.0005;
  renderer.render(scene, camera);
}
animate();

// --- Animation du texte ---
const lines = document.querySelectorAll('.narration p');
gsap.set(lines, { opacity: 0, y: 20 });

gsap.to(lines, {
  opacity: 1,
  y: 0,
  duration: 1.5,
  stagger: 2,
  ease: "power2.out"
});
