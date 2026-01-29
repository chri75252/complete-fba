
import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Environment, Float, ContactShadows } from '@react-three/drei';
import * as THREE from 'three';

// --- 3D Components ---


const boxGeo = new THREE.BoxGeometry(0.9, 0.9, 0.9);
const edgesGeo = new THREE.EdgesGeometry(boxGeo);

const CubeBlock = ({ position, isInner }) => {
  // Inner blocks are orange/glowing, Outer are dark/glassy
  return (
    <group position={position}>
      <mesh geometry={boxGeo}>
        {isInner ? (
          <meshStandardMaterial
            color="#f59e0b"
            emissive="#f59e0b"
            emissiveIntensity={2}
            toneMapped={false}
          />
        ) : (
          <meshPhysicalMaterial
            color="#111827"
            metalness={0.8}
            roughness={0.2}
            transparent
            opacity={0.8}
            transmission={0.2}
          />
        )}
      </mesh>
      {/* Wireframe Edge for Tech Look */}
      {!isInner && (
        <lineSegments geometry={edgesGeo}>
          <lineBasicMaterial color="#3b82f6" transparent opacity={0.4} />
        </lineSegments>
      )}
    </group>
  );
};


const TechCube = () => {
  const group = useRef();

  // Create a 3x3x3 grid
  const cubes = useMemo(() => {
    const temp = [];
    const size = 3;
    const offset = (size - 1) / 2;

    for (let x = 0; x < size; x++) {
      for (let y = 0; y < size; y++) {
        for (let z = 0; z < size; z++) {
          // Determine if it's an "inner" cube (center of the 3x3x3)
          // Actually, let's make the core glowing.
          const isCenter = x === 1 && y === 1 && z === 1;
          const isCore = (x >= 0 && x <= 2) && (y >= 0 && y <= 2) && (z >= 0 && z <= 2) && (Math.abs(x - 1) + Math.abs(y - 1) + Math.abs(z - 1) <= 1);

          // Randomly remove some outer blocks for a "constructed" look
          if (!isCore && Math.random() > 0.8) continue;

          temp.push({
            position: [x - offset, y - offset, z - offset],
            isInner: isCenter || (Math.random() > 0.9 && isCore) // Random glowing bits
          });
        }
      }
    }
    return temp;
  }, []);

  useFrame((state) => {
    const t = state.clock.getElapsedTime();
    group.current.rotation.y = t * 0.2;
    group.current.rotation.x = Math.sin(t * 0.1) * 0.1;
  });

  return (
    <group ref={group}>
      {cubes.map((data, i) => (
        <CubeBlock key={i} position={data.position} isInner={data.isInner} />
      ))}
    </group>
  );
};

const Scene = () => {
  return (
    <>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} color="#3b82f6" />
      <pointLight position={[-10, -10, -10]} intensity={1} color="#f59e0b" />

      <Float speed={2} rotationIntensity={0.5} floatIntensity={0.5}>
        <TechCube />
      </Float>

      <ContactShadows position={[0, -3, 0]} opacity={0.4} scale={10} blur={2.5} far={4} />
      <Environment preset="city" />
    </>
  );
};

// --- Main App Component ---

function App() {
  return (
    <div className="app">
      {/* 3D Background */}
      <div className="canvas-container">
        <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
          <Scene />
        </Canvas>
      </div>

      {/* UI Overlay */}
      <div className="container">
        <header>
          <a href="#" className="logo">
            {/* Simple SVG Icon */}
            <svg className="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
            </svg>
            The Blacksmith Market
          </a>
          <nav>
            <ul>
              <li><a href="#">About Us</a></li>
              <li><a href="#">Categories</a></li>
              <li><a href="#">Suppliers</a></li>
            </ul>
          </nav>
          <a href="#" className="btn btn-primary">Contact Sales</a>
        </header>

        <section className="hero">
          <div className="hero-content">
            <h1>Your Trusted Partner in UK Wholesale Distribution</h1>
            <p className="subtitle">Connecting Quality Brands with UK Retailers</p>
          </div>

          {/* Buttons pushed down by CSS to frame the cube */}
          <div className="cta-group">
            <a href="#" className="btn btn-primary">Contact Sales</a>
            <a href="#" className="btn btn-outline">Become a Supplier</a>
          </div>
        </section>
      </div>

      {/* Footer Sparkle */}
      <svg className="sparkle-icon" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 0L14.59 9.41L24 12L14.59 14.59L12 24L9.41 14.59L0 12L9.41 9.41L12 0Z" />
      </svg>
    </div>
  );
}

export default App;
