import * as THREE from 'three';
import { gsap } from 'gsap';

// Assurez-vous que l'ÃƒÂ©lÃƒÂ©ment canvas avec l'ID 'bg' est dans votre index.html
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('bg'), alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);

// --- LumiÃƒÂ¨res ---
const light1 = new THREE.PointLight(0xb4ffb4, 1.5);
light1.position.set(2, 2, 5);
scene.add(light1);

const light2 = new THREE.PointLight(0x7fbfff, 1);
light2.position.set(-3, -2, -5);
scene.add(light2);

// --- Fond dynamique ---
// Taille augmentÃƒÂ©e pour devenir une source de lumiÃƒÂ¨re ambiante floue
const geometry = new THREE.SphereGeometry(25, 64, 64); // SphÃƒÂ¨re trÃƒÂ¨s grande
const material = new THREE.MeshStandardMaterial({
  color: 0x143d28,
  emissive: 0x224d38,
  metalness: 0.3,
  roughness: 0.8
});
const sphere = new THREE.Mesh(geometry, material);
scene.add(sphere);

// NOUVEL AJUSTEMENT : Recule la sphÃƒÂ¨re extrÃƒÂªmement loin pour qu'elle devienne un simple halo
sphere.position.z = -200; 

// Positionne la camÃƒÂ©ra plus en arriÃƒÂ¨re pour un plan plus large
camera.position.z = 100; 
// ...
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