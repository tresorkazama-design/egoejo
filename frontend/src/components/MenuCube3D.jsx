import { Suspense, useRef, useState, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Text } from "@react-three/drei";
// OPTIMISATION BUNDLE : Imports nommés pour Tree Shaking (réduit la taille du bundle)
import { MathUtils } from "three";
import { useNavigate } from "react-router-dom";
import { logger } from "../utils/logger";

// Composant pour une face du cube
function CubeFace({ position, rotation, text, onClick, isActive, onPointerOver, onPointerOut, color = "#00f5a0" }) {
  const meshRef = useRef();

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.material.emissive.setHex(
        isActive ? parseInt(color.replace("#", ""), 16) : 0x000000
      );
    }
  });

  return (
    <mesh
      ref={meshRef}
      position={position}
      rotation={rotation}
      onClick={(e) => {
        e.stopPropagation();
        e.nativeEvent.stopImmediatePropagation();
        if (onClick) onClick(e);
      }}
      onPointerOver={onPointerOver}
      onPointerOut={onPointerOut}
    >
      <boxGeometry args={[2, 2, 0.1]} />
      <meshStandardMaterial
        color={isActive ? color : "#0b1013"}
        emissive={isActive ? color : "#000000"}
        emissiveIntensity={isActive ? 0.3 : 0}
        metalness={0.8}
        roughness={0.2}
      />
      {text && (
        <Text
          position={[0, 0, 0.06]}
          fontSize={0.3}
          color={isActive ? "#ffffff" : "#99b8b0"}
          anchorX="center"
          anchorY="middle"
          outlineWidth={0.02}
          outlineColor="#000000"
        >
          {text}
        </Text>
      )}
    </mesh>
  );
}

// Composant principal du cube
function Cube({ links, onLinkClick, isOpen, onNavigate }) {
  const cubeRef = useRef();
  const [hoveredFace, setHoveredFace] = useState(null);

  // Animation de rotation
  useFrame((state) => {
    if (cubeRef.current) {
      if (isOpen) {
        // Rotation pour révéler les faces
        cubeRef.current.rotation.x = MathUtils.lerp(
          cubeRef.current.rotation.x,
          Math.PI / 4,
          0.05
        );
        cubeRef.current.rotation.y = MathUtils.lerp(
          cubeRef.current.rotation.y,
          Math.PI / 4,
          0.05
        );
      } else {
        // Retour à la position initiale
        cubeRef.current.rotation.x = MathUtils.lerp(
          cubeRef.current.rotation.x,
          0,
          0.05
        );
        cubeRef.current.rotation.y = MathUtils.lerp(
          cubeRef.current.rotation.y,
          0,
          0.05
        );
      }
    }
  });

  const handleFaceClick = (e, link) => {
    e.stopPropagation();
    logger.debug('Face clicked:', link);
    if (link && link.to) {
      logger.debug('Navigating to:', link.to);
      onNavigate(link.to);
      onLinkClick();
    }
  };

  // Positions des faces du cube
  const faces = [
    { position: [0, 0, 1], rotation: [0, 0, 0], text: "MENU", link: null }, // Face avant
    { position: [0, 0, -1], rotation: [0, Math.PI, 0], text: (links[0]?.label || "").toUpperCase(), link: links[0] }, // Face arrière
    { position: [0, 1, 0], rotation: [-Math.PI / 2, 0, 0], text: (links[1]?.label || "").toUpperCase(), link: links[1] }, // Face haut
    { position: [0, -1, 0], rotation: [Math.PI / 2, 0, 0], text: (links[2]?.label || "").toUpperCase(), link: links[2] }, // Face bas
    { position: [1, 0, 0], rotation: [0, Math.PI / 2, 0], text: (links[3]?.label || "").toUpperCase(), link: links[3] }, // Face droite
    { position: [-1, 0, 0], rotation: [0, -Math.PI / 2, 0], text: (links[4]?.label || "").toUpperCase(), link: links[4] }, // Face gauche
  ];

  return (
    <group ref={cubeRef}>
      {faces.map((face, index) => (
        <CubeFace
          key={index}
          position={face.position}
          rotation={face.rotation}
          text={face.text}
          onClick={(e) => {
            e.stopPropagation();
            handleFaceClick(e, face.link);
          }}
          isActive={hoveredFace === index || (isOpen && index > 0)}
          onPointerOver={(e) => {
            e.stopPropagation();
            if (isOpen && face.link) {
              setHoveredFace(index);
              document.body.style.cursor = "pointer";
            }
          }}
          onPointerOut={(e) => {
            e.stopPropagation();
            setHoveredFace(null);
            document.body.style.cursor = "auto";
          }}
        />
      ))}
    </group>
  );
}

// Composant principal
export default function MenuCube3D({ links, isOpen, onToggle, onLinkClick }) {
  const [canRender, setCanRender] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Vérifier si WebGL est disponible
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)")?.matches;
    const webgl = (() => {
      try {
        const canvas = document.createElement("canvas");
        return !!(
          window.WebGLRenderingContext &&
          (canvas.getContext("webgl") || canvas.getContext("experimental-webgl"))
        );
      } catch {
        return false;
      }
    })();
    setCanRender(!reduce && webgl);
  }, []);

  if (!canRender) {
    // Fallback : bouton simple si WebGL n'est pas disponible
    return (
      <button
        type="button"
        className="menu-cube-fallback"
        onClick={onToggle}
        aria-label={isOpen ? "Fermer le menu" : "Ouvrir le menu"}
      >
        MENU
      </button>
    );
  }

  return (
    <div className="menu-cube-container">
      <div
        className={`menu-cube-button ${isOpen ? "is-open" : ""}`}
        onClick={(e) => {
          // Ouvrir le menu seulement si fermé et si on clique sur le conteneur (pas sur le canvas)
          if (!isOpen && e.target === e.currentTarget) {
            e.stopPropagation();
            onToggle();
          }
        }}
        style={{ pointerEvents: isOpen ? "none" : "auto" }}
        role="button"
        tabIndex={0}
        aria-label={isOpen ? "Fermer le menu" : "Ouvrir le menu"}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            if (!isOpen) onToggle();
          }
        }}
      >
        <Canvas
          camera={{ position: [0, 0, 5], fov: 50 }}
          style={{ width: "100%", height: "100%", display: "block", pointerEvents: isOpen ? "auto" : "none" }}
          gl={{ antialias: true, alpha: true }}
          dpr={[1, 2]}
        >
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} intensity={1} />
          <pointLight position={[-10, -10, -10]} intensity={0.5} color="#00f5a0" />
          <Suspense fallback={null}>
            <Cube links={links} onLinkClick={onLinkClick} isOpen={isOpen} onNavigate={navigate} />
          </Suspense>
        </Canvas>
      </div>
      {isOpen && (
        <>
          <div 
            className="menu-cube-overlay" 
            onClick={(e) => {
              e.stopPropagation();
              onToggle();
            }} 
          />
          <div 
            className="menu-cube-close-button"
            onClick={(e) => {
              e.stopPropagation();
              onToggle();
            }}
            aria-label="Fermer le menu"
          >
            ×
          </div>
        </>
      )}
    </div>
  );
}

