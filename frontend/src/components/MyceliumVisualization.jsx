/**
 * Composant pour visualisation 3D "Mycélium Numérique"
 * Affiche les projets et contenus comme une constellation 3D basée sur leurs embeddings
 * 
 * REFACTORING "Performance Organique" :
 * - Instancing : InstancedMesh pour réduire drastiquement les draw calls
 * - DPR limité (max 2) pour éviter sur-rendu
 * - LOD (Level of Detail) : 3 niveaux de qualité selon distance
 * - Raycasting pour interactions (hover, click) avec Instancing
 * - useMemo pour calculs coûteux
 */
import React, { useRef, useEffect, useState, useMemo, useCallback } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Text, Line } from '@react-three/drei';
import { fetchAPI } from '../utils/api';
import { useEcoMode } from '../contexts/EcoModeContext';
import { getSobrietyFeature } from '../design-tokens';
// OPTIMISATION : Imports nommés pour Tree Shaking (réduit la taille du bundle)
import {
  SphereGeometry,
  MeshStandardMaterial,
  InstancedMesh,
  LOD,
  Vector3,
  Vector2,
  Matrix4,
  Sphere
} from 'three';

// Composant InstancedNodes : Rendu optimisé avec InstancedMesh + LOD
function InstancedNodes({ nodes, onHover, onLeave, onClick }) {
  const groupRef = useRef();
  const hoveredIndexRef = useRef(-1);
  const { camera, raycaster, size } = useThree();
  const [hoveredNode, setHoveredNode] = useState(null);
  const pointerRef = useRef(new Vector2());
  
  // OPTIMISATION : Géométries LOD : 3 niveaux de qualité
  const geometries = useMemo(() => ({
    high: new SphereGeometry(0.2, 16, 16),   // Proche : 16 segments
    medium: new SphereGeometry(0.2, 12, 12), // Moyen : 12 segments
    low: new SphereGeometry(0.2, 8, 8)       // Loin : 8 segments
  }), []);

  // OPTIMISATION : Matériaux par type (projet vs content)
  const materials = useMemo(() => ({
    projet: new MeshStandardMaterial({
      color: '#00ffa3',
      emissive: '#00ffa3',
      emissiveIntensity: 0.3
    }),
    content: new MeshStandardMaterial({
      color: '#ff6b6b',
      emissive: '#ff6b6b',
      emissiveIntensity: 0.3
    })
  }), []);

  // OPTIMISATION : Cleanup des géométries et matériaux Three.js (évite memory leaks)
  useEffect(() => {
    return () => {
      // Disposer les géométries
      geometries.high.dispose();
      geometries.medium.dispose();
      geometries.low.dispose();
      
      // Disposer les matériaux
      materials.projet.dispose();
      materials.content.dispose();
    };
  }, [geometries, materials]);

  // Créer InstancedMesh avec LOD pour chaque type
  useEffect(() => {
    if (!groupRef.current || nodes.length === 0) return;

    // OPTIMISATION : Nettoyer les anciens meshes (dispose pour éviter memory leaks)
    while (groupRef.current.children.length > 0) {
      const child = groupRef.current.children[0];
      if (child instanceof LOD) {
        child.children.forEach(mesh => {
          if (mesh instanceof InstancedMesh) {
            mesh.geometry.dispose();
            mesh.material.dispose();
          }
        });
      }
      groupRef.current.remove(child);
    }

    // Séparer les nœuds par type
    const projetNodes = nodes.filter(n => n.type === 'projet');
    const contentNodes = nodes.filter(n => n.type === 'content');

    // Créer InstancedMesh pour projets (avec LOD)
    if (projetNodes.length > 0) {
      // LOD High (proche : 0-5 unités)
      const highMesh = new InstancedMesh(geometries.high, materials.projet, projetNodes.length);
      // LOD Medium (moyen : 5-10 unités)
      const mediumMesh = new InstancedMesh(geometries.medium, materials.projet, projetNodes.length);
      // LOD Low (loin : 10+ unités)
      const lowMesh = new InstancedMesh(geometries.low, materials.projet, projetNodes.length);

      projetNodes.forEach((node, index) => {
        const matrix = new Matrix4();
        matrix.setPosition(node.x, node.y, node.z);
        highMesh.setMatrixAt(index, matrix);
        mediumMesh.setMatrixAt(index, matrix);
        lowMesh.setMatrixAt(index, matrix);
      });

      highMesh.instanceMatrix.needsUpdate = true;
      mediumMesh.instanceMatrix.needsUpdate = true;
      lowMesh.instanceMatrix.needsUpdate = true;

      // Créer LOD group pour projets
      const projetLOD = new LOD();
      projetLOD.addLevel(highMesh, 0);
      projetLOD.addLevel(mediumMesh, 5);
      projetLOD.addLevel(lowMesh, 10);
      groupRef.current.add(projetLOD);
    }

    // Créer InstancedMesh pour contenus (avec LOD)
    if (contentNodes.length > 0) {
      const highMesh = new InstancedMesh(geometries.high, materials.content, contentNodes.length);
      const mediumMesh = new InstancedMesh(geometries.medium, materials.content, contentNodes.length);
      const lowMesh = new InstancedMesh(geometries.low, materials.content, contentNodes.length);

      contentNodes.forEach((node, index) => {
        const matrix = new Matrix4();
        matrix.setPosition(node.x, node.y, node.z);
        highMesh.setMatrixAt(index, matrix);
        mediumMesh.setMatrixAt(index, matrix);
        lowMesh.setMatrixAt(index, matrix);
      });

      highMesh.instanceMatrix.needsUpdate = true;
      mediumMesh.instanceMatrix.needsUpdate = true;
      lowMesh.instanceMatrix.needsUpdate = true;

      const contentLOD = new LOD();
      contentLOD.addLevel(highMesh, 0);
      contentLOD.addLevel(mediumMesh, 5);
      contentLOD.addLevel(lowMesh, 10);
      groupRef.current.add(contentLOD);
    }
  }, [nodes, geometries, materials]);

  // OPTIMISATION PERFORMANCE : Pré-calculer les positions des nœuds (évite création d'objets à chaque frame)
  // Les positions sont stockées comme arrays [x, y, z] pour éviter les allocations Vector3
  const nodePositionsRef = useRef([]);
  const nodeRadius = 0.2;
  const nodeRadiusSq = nodeRadius * nodeRadius; // Pré-calculer le rayon au carré
  
  useEffect(() => {
    // Mettre à jour les positions seulement si les nœuds changent (format [x, y, z] pour éviter allocations)
    nodePositionsRef.current = nodes.map(node => [node.x, node.y, node.z]);
  }, [nodes]);

  // Raycasting pour interactions (hover, click)
  useFrame(({ camera, raycaster }) => {
    if (!groupRef.current || nodes.length === 0) return;

    // Mettre à jour le raycaster avec le pointer
    raycaster.setFromCamera(pointerRef.current, camera);
    
    // Tester l'intersection avec chaque nœud (sphère)
    let closestDistance = Infinity;
    let closestIndex = -1;

    // OPTIMISATION PERFORMANCE : Calcul direct sans créer d'objets Vector3/Sphere à chaque frame
    // Utiliser des calculs mathématiques purs (pas d'allocations d'objets)
    const rayOrigin = raycaster.ray.origin;
    const rayDir = raycaster.ray.direction;
    
    nodePositionsRef.current.forEach((pos, index) => {
      // Calculer la distance point-ligne (formule optimisée sans allocations)
      const dx = pos[0] - rayOrigin.x;
      const dy = pos[1] - rayOrigin.y;
      const dz = pos[2] - rayOrigin.z;
      
      // Projection du vecteur vers le centre sur la direction du rayon
      const projection = dx * rayDir.x + dy * rayDir.y + dz * rayDir.z;
      
      // Point le plus proche sur le rayon
      const closestX = rayOrigin.x + projection * rayDir.x;
      const closestY = rayOrigin.y + projection * rayDir.y;
      const closestZ = rayOrigin.z + projection * rayDir.z;
      
      // Distance au carré (évite sqrt)
      const distX = closestX - pos[0];
      const distY = closestY - pos[1];
      const distZ = closestZ - pos[2];
      const distanceSq = distX * distX + distY * distY + distZ * distZ;
      
      // Vérifier si la distance est inférieure au rayon (comparaison au carré)
      if (distanceSq < nodeRadiusSq) {
        const distance = Math.sqrt(distanceSq);
        if (distance < closestDistance) {
          closestDistance = distance;
          closestIndex = index;
        }
      }
    });

    // Gérer hover
    if (closestIndex !== hoveredIndexRef.current) {
      if (hoveredIndexRef.current >= 0) {
        // Leave
        onLeave && onLeave();
        setHoveredNode(null);
      }
      
      if (closestIndex >= 0) {
        // Hover
        hoveredIndexRef.current = closestIndex;
        const node = nodes[closestIndex];
        setHoveredNode(node);
        onHover && onHover(node);
      } else {
        hoveredIndexRef.current = -1;
      }
    }

    // Mettre à jour LOD selon distance caméra
    groupRef.current.children.forEach((lod) => {
      if (lod instanceof LOD) {
        lod.update(camera);
      }
    });

    // Animation subtile (respiration organique) pour nœuds proches
    groupRef.current.children.forEach((lod) => {
      if (lod instanceof LOD) {
        lod.children.forEach((mesh) => {
          if (mesh instanceof InstancedMesh) {
            mesh.rotation.y += 0.001;
          }
        });
      }
    });
  });

  // Gérer click
  const handleClick = useCallback(() => {
    if (hoveredIndexRef.current >= 0 && hoveredNode) {
      onClick && onClick(hoveredNode);
    }
  }, [hoveredNode, onClick]);

  // Mettre à jour pointer pour raycasting
  const handlePointerMove = useCallback((event) => {
    if (event.target) {
      const rect = event.target.getBoundingClientRect();
      pointerRef.current.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      pointerRef.current.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    }
  }, []);

  return (
    <group 
      ref={groupRef} 
      onClick={handleClick}
      onPointerMove={handlePointerMove}
    >
      {/* Les InstancedMesh avec LOD sont ajoutés dans useEffect */}
    </group>
  );
}

// Composant Node individuel pour hover (scale effect)
function HoveredNode({ node, position }) {
  const meshRef = useRef();
  
  useFrame(() => {
    if (meshRef.current) {
      // Animation de scale (respiration organique)
      meshRef.current.rotation.y += 0.001;
      const scale = 1.0 + Math.sin(Date.now() * 0.002) * 0.1;
      meshRef.current.scale.setScalar(scale);
    }
  });

  const color = node.type === 'projet' ? '#00ffa3' : '#ff6b6b';
  const size = 0.3; // Taille agrandie pour hover

  return (
    <group position={[position.x, position.y, position.z]}>
      <mesh ref={meshRef}>
        <sphereGeometry args={[size, 16, 16]} />
        <meshStandardMaterial 
          color={color} 
          emissive={color} 
          emissiveIntensity={0.5} 
        />
      </mesh>
      <Text
        position={[0, size + 0.1, 0]}
        fontSize={0.1}
        color="white"
        anchorX="center"
        anchorY="middle"
      >
        {node.titre || node.title}
      </Text>
    </group>
  );
}

// OPTIMISATION : Composant Connection optimisé avec React.memo
const Connection = React.memo(({ start, end, opacity = 0.2 }) => {
  const points = useMemo(
    () => [
      new Vector3(start.x, start.y, start.z),
      new Vector3(end.x, end.y, end.z)
    ],
    [start.x, start.y, start.z, end.x, end.y, end.z]
  );
  
  return (
    <Line
      points={points}
      color="#00ffa3"
      lineWidth={1}
      opacity={opacity}
      transparent
    />
  );
});

export default function MyceliumVisualization() {
  const [data, setData] = useState({ projets: [], contenus: [] });
  const [loading, setLoading] = useState(true);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [showConnections, setShowConnections] = useState(false);
  const { sobrietyLevel, sobrietyConfig } = useEcoMode();
  
  // Vérifier si 3D est activé selon le niveau de sobriété
  const canRender3D = getSobrietyFeature(sobrietyLevel, 'enable3D');
  const canRenderBloom = getSobrietyFeature(sobrietyLevel, 'enableBloom');

  // OPTIMISATION : Envelopper les handlers dans useCallback pour éviter les rerenders
  const handleHover = useCallback((node) => {
    setHoveredNode(node);
  }, []);

  const handleLeave = useCallback(() => {
    setHoveredNode(null);
  }, []);

  const handleClick = useCallback((node) => {
    setSelectedNode(node);
  }, []);

  useEffect(() => {
    const loadData = async () => {
      try {
        const myceliumData = await fetchAPI('/mycelium/data/');
        setData(myceliumData);
      } catch (error) {
        logger.error('Erreur chargement données Mycélium:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // useMemo : Calculer allNodes une seule fois
  const allNodes = useMemo(() => [
    ...data.projets.map(p => ({ ...p, type: 'projet' })),
    ...data.contenus.map(c => ({ ...c, type: 'content' }))
  ], [data.projets, data.contenus]);

  // OPTIMISATION ALGORITHMIQUE : Spatial Hash Grid pour réduire O(n²) à O(n)
  // Au lieu de vérifier la distance avec tous les nœuds, on utilise un hash grid spatial
  // pour ne vérifier que les voisins proches (complexité O(n) au lieu de O(n²))
  const connections = useMemo(() => {
    if (!showConnections || allNodes.length === 0) return [];
    
    const threshold = 2.0;
    const thresholdSq = threshold * threshold;
    const cellSize = threshold; // Taille de la cellule du hash grid = threshold
    
    // Créer un Spatial Hash Grid (Map)
    const spatialGrid = new Map();
    
    // Fonction pour obtenir la clé de la cellule pour un point 3D
    const getCellKey = (x, y, z) => {
      const cellX = Math.floor(x / cellSize);
      const cellY = Math.floor(y / cellSize);
      const cellZ = Math.floor(z / cellSize);
      return `${cellX},${cellY},${cellZ}`;
    };
    
    // Étape 1 : Insérer tous les nœuds dans le hash grid (O(n))
    allNodes.forEach((node, index) => {
      const key = getCellKey(node.x, node.y, node.z);
      if (!spatialGrid.has(key)) {
        spatialGrid.set(key, []);
      }
      spatialGrid.get(key).push({ node, index });
    });
    
    // Étape 2 : Pour chaque nœud, vérifier seulement les voisins dans les cellules adjacentes (O(n))
    const conns = [];
    const processedPairs = new Set(); // Éviter les doublons
    
    allNodes.forEach((node, i) => {
      const cellX = Math.floor(node.x / cellSize);
      const cellY = Math.floor(node.y / cellSize);
      const cellZ = Math.floor(node.z / cellSize);
      
      // Vérifier les 27 cellules adjacentes (3x3x3) au lieu de tous les nœuds
      for (let dx = -1; dx <= 1; dx++) {
        for (let dy = -1; dy <= 1; dy++) {
          for (let dz = -1; dz <= 1; dz++) {
            const neighborKey = `${cellX + dx},${cellY + dy},${cellZ + dz}`;
            const neighbors = spatialGrid.get(neighborKey);
            
            if (neighbors) {
              neighbors.forEach(({ node: neighbor, index: j }) => {
                // Éviter les doublons et les auto-connexions
                if (i >= j) return;
                const pairKey = `${Math.min(i, j)},${Math.max(i, j)}`;
                if (processedPairs.has(pairKey)) return;
                
                // Calculer la distance au carré (plus rapide que sqrt)
                const distX = node.x - neighbor.x;
                const distY = node.y - neighbor.y;
                const distZ = node.z - neighbor.z;
                const distSq = distX * distX + distY * distY + distZ * distZ;
                
                if (distSq < thresholdSq) {
                  processedPairs.add(pairKey);
                  conns.push({ start: node, end: neighbor });
                }
              });
            }
          }
        }
      }
    });
    
    return conns;
  }, [showConnections, allNodes]);

  if (loading) {
    return (
      <div className="mycelium-loading">
        <p>Chargement du Mycélium Numérique...</p>
      </div>
    );
  }

  // Dégradation gracieuse : version statique si 3D désactivé (sobriété >= 3)
  if (!canRender3D) {
    return (
      <div className="mycelium-visualization">
        <div className="mycelium-loading">
          <p>Mycélium Numérique (Niveau Sobriété {sobrietyLevel})</p>
          <p style={{ fontSize: '0.875rem', color: 'var(--muted)', marginTop: '0.5rem' }}>
            La visualisation 3D est désactivée pour économiser l'énergie.
          </p>
        </div>
      </div>
    );
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
            {/* CONVENTION NAVIGATION : Si node.url est toujours une route interne, utiliser <Link to={node.url}>
                Pour l'instant, on garde <a> car les URLs peuvent être dynamiques (routes internes ou externes) */}
            <a href={hoveredNode.url} className="btn btn-primary">
              Voir
            </a>
          </div>
        )}
      </div>

      <Canvas 
        camera={{ position: [5, 5, 5], fov: 75 }}
        dpr={[1, 2]} // Performance Organique : DPR limité (max 2)
        gl={{ 
          antialias: false, // Performance : désactiver antialiasing
          alpha: true,
          powerPreference: "high-performance"
        }}
        onPointerMove={(e) => {
          // Mettre à jour pointer pour raycasting
          e.stopPropagation();
        }}
      >
        <ambientLight intensity={0.5} />
        <pointLight position={[10, 10, 10]} />
        <OrbitControls enableDamping dampingFactor={0.05} />

        {/* Connexions */}
        {connections.map((conn, idx) => (
          <Connection key={idx} start={conn.start} end={conn.end} />
        ))}

        {/* Nœuds avec Instancing */}
        <InstancedNodes
          nodes={allNodes}
          onHover={handleHover}
          onLeave={handleLeave}
          onClick={handleClick}
          data-3d={canRender3D}
          data-bloom={getSobrietyFeature(sobrietyLevel, 'enableBloom')}
        />

        {/* Nœud hovered (rendu individuel pour effet scale) */}
        {hoveredNode && (
          <HoveredNode
            node={hoveredNode}
            position={{ x: hoveredNode.x, y: hoveredNode.y, z: hoveredNode.z }}
          />
        )}
      </Canvas>

      {selectedNode && (
        <div className="mycelium-detail">
          <h2>{selectedNode.titre || selectedNode.title}</h2>
          <p>{selectedNode.description}</p>
          {/* CONVENTION NAVIGATION : Si node.url est toujours une route interne, utiliser <Link to={node.url}>
              Pour l'instant, on garde <a> car les URLs peuvent être dynamiques (routes internes ou externes) */}
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
