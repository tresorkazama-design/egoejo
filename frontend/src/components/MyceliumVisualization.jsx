/**
 * Composant pour visualisation 3D "Mycélium Numérique"
 * Affiche les projets et contenus comme une constellation 3D basée sur leurs embeddings
 */
import { useRef, useEffect, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Sphere, Line } from '@react-three/drei';
import { fetchAPI } from '../utils/api';
import * as THREE from 'three';

function Node({ position, data, type, onHover, onLeave, onClick }) {
  const meshRef = useRef();
  const [hovered, setHovered] = useState(false);

  useFrame((state) => {
    if (meshRef.current) {
      // Animation subtile
      meshRef.current.rotation.y += 0.001;
    }
  });

  const color = type === 'projet' ? '#00ffa3' : '#ff6b6b';
  const size = hovered ? 0.3 : 0.2;

  return (
    <group position={[position.x, position.y, position.z]}>
      <Sphere
        ref={meshRef}
        args={[size, 16, 16]}
        onPointerOver={(e) => {
          e.stopPropagation();
          setHovered(true);
          onHover && onHover(data);
        }}
        onPointerOut={(e) => {
          setHovered(false);
          onLeave && onLeave();
        }}
        onClick={(e) => {
          e.stopPropagation();
          onClick && onClick(data);
        }}
      >
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.3} />
      </Sphere>
      {hovered && (
        <Text
          position={[0, size + 0.1, 0]}
          fontSize={0.1}
          color="white"
          anchorX="center"
          anchorY="middle"
        >
          {data.titre || data.title}
        </Text>
      )}
    </group>
  );
}

function Connection({ start, end, opacity = 0.2 }) {
  const points = [new THREE.Vector3(start.x, start.y, start.z), new THREE.Vector3(end.x, end.y, end.z)];
  
  return (
    <Line
      points={points}
      color="#00ffa3"
      lineWidth={1}
      opacity={opacity}
      transparent
    />
  );
}

export default function MyceliumVisualization() {
  const [data, setData] = useState({ projets: [], contenus: [] });
  const [loading, setLoading] = useState(true);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [showConnections, setShowConnections] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        const myceliumData = await fetchAPI('/mycelium/data/');
        setData(myceliumData);
      } catch (error) {
        console.error('Erreur chargement données Mycélium:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  if (loading) {
    return (
      <div className="mycelium-loading">
        <p>Chargement du Mycélium Numérique...</p>
      </div>
    );
  }

  const allNodes = [
    ...data.projets.map(p => ({ ...p, type: 'projet' })),
    ...data.contenus.map(c => ({ ...c, type: 'content' }))
  ];

  // Calculer les connexions (proximité < seuil)
  const connections = [];
  if (showConnections) {
    const threshold = 2.0; // Distance seuil pour connexion
    for (let i = 0; i < allNodes.length; i++) {
      for (let j = i + 1; j < allNodes.length; j++) {
        const dist = Math.sqrt(
          Math.pow(allNodes[i].x - allNodes[j].x, 2) +
          Math.pow(allNodes[i].y - allNodes[j].y, 2) +
          Math.pow(allNodes[i].z - allNodes[j].z, 2)
        );
        if (dist < threshold) {
          connections.push({ start: allNodes[i], end: allNodes[j] });
        }
      }
    }
  }

  return (
    <div className="mycelium-visualization">
      <div className="mycelium-controls">
        <button
          onClick={() => setShowConnections(!showConnections)}
          className="btn btn-ghost"
        >
          {showConnections ? 'Masquer' : 'Afficher'} Connexions
        </button>
        {hoveredNode && (
          <div className="mycelium-tooltip">
            <h3>{hoveredNode.titre || hoveredNode.title}</h3>
            <p>{hoveredNode.description}</p>
            <a href={hoveredNode.url} className="btn btn-primary">
              Voir
            </a>
          </div>
        )}
      </div>

      <Canvas camera={{ position: [5, 5, 5], fov: 75 }}>
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} />
        <OrbitControls enableDamping dampingFactor={0.05} />

        {/* Connexions */}
        {connections.map((conn, idx) => (
          <Connection key={idx} start={conn.start} end={conn.end} />
        ))}

        {/* Nœuds */}
        {allNodes.map((node) => (
          <Node
            key={`${node.type}-${node.id}`}
            position={{ x: node.x, y: node.y, z: node.z }}
            data={node}
            type={node.type}
            onHover={setHoveredNode}
            onLeave={() => setHoveredNode(null)}
            onClick={setSelectedNode}
          />
        ))}
      </Canvas>

      {selectedNode && (
        <div className="mycelium-detail">
          <h2>{selectedNode.titre || selectedNode.title}</h2>
          <p>{selectedNode.description}</p>
          <a href={selectedNode.url} className="btn btn-primary">
            Voir le détail
          </a>
          <button
            onClick={() => setSelectedNode(null)}
            className="btn btn-ghost"
          >
            Fermer
          </button>
        </div>
      )}
    </div>
  );
}

