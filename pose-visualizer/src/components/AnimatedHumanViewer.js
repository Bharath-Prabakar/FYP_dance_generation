import React, { useRef, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import * as THREE from 'three';
import './AnimatedHumanViewer.css';

// MediaPipe body parts mapping
const BODY_PARTS = {
  head: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
  torso: [11, 12, 23, 24],
  leftArm: [11, 13, 15],
  rightArm: [12, 14, 16],
  leftLeg: [23, 25, 27],
  rightLeg: [24, 26, 28]
};

// Simple humanoid body using cylinders and spheres
const HumanoidBody = ({ landmarks }) => {
  if (!landmarks || landmarks.length !== 33) return null;

  // Helper to create limb
  const createLimb = (start, end, color, thickness = 0.05) => {
    const startPos = new THREE.Vector3(start.x, start.y, start.z);
    const endPos = new THREE.Vector3(end.x, end.y, end.z);
    const direction = new THREE.Vector3().subVectors(endPos, startPos);
    const length = direction.length();
    const midpoint = new THREE.Vector3().addVectors(startPos, endPos).multiplyScalar(0.5);
    
    return {
      position: midpoint,
      rotation: new THREE.Euler().setFromQuaternion(
        new THREE.Quaternion().setFromUnitVectors(
          new THREE.Vector3(0, 1, 0),
          direction.normalize()
        )
      ),
      length,
      color,
      thickness
    };
  };

  // Body parts
  const torso = createLimb(
    { x: (landmarks[11].x + landmarks[12].x) / 2, y: (landmarks[11].y + landmarks[12].y) / 2, z: (landmarks[11].z + landmarks[12].z) / 2 },
    { x: (landmarks[23].x + landmarks[24].x) / 2, y: (landmarks[23].y + landmarks[24].y) / 2, z: (landmarks[23].z + landmarks[24].z) / 2 },
    '#ff6b9d',
    0.12
  );

  const leftUpperArm = createLimb(landmarks[11], landmarks[13], '#4ecca3', 0.06);
  const leftLowerArm = createLimb(landmarks[13], landmarks[15], '#4ecca3', 0.05);
  const rightUpperArm = createLimb(landmarks[12], landmarks[14], '#4ecca3', 0.06);
  const rightLowerArm = createLimb(landmarks[14], landmarks[16], '#4ecca3', 0.05);

  const leftUpperLeg = createLimb(landmarks[23], landmarks[25], '#00d4ff', 0.08);
  const leftLowerLeg = createLimb(landmarks[25], landmarks[27], '#00d4ff', 0.07);
  const rightUpperLeg = createLimb(landmarks[24], landmarks[26], '#00d4ff', 0.08);
  const rightLowerLeg = createLimb(landmarks[26], landmarks[28], '#00d4ff', 0.07);

  const limbs = [
    torso,
    leftUpperArm, leftLowerArm,
    rightUpperArm, rightLowerArm,
    leftUpperLeg, leftLowerLeg,
    rightUpperLeg, rightLowerLeg
  ];

  return (
    <group>
      {/* Draw limbs */}
      {limbs.map((limb, idx) => (
        <mesh
          key={idx}
          position={[limb.position.x, limb.position.y, limb.position.z]}
          rotation={[limb.rotation.x, limb.rotation.y, limb.rotation.z]}
        >
          <cylinderGeometry args={[limb.thickness, limb.thickness, limb.length, 16]} />
          <meshStandardMaterial color={limb.color} />
        </mesh>
      ))}

      {/* Head */}
      <mesh position={[landmarks[0].x, landmarks[0].y, landmarks[0].z]}>
        <sphereGeometry args={[0.15, 32, 32]} />
        <meshStandardMaterial color="#ffd93d" />
      </mesh>

      {/* Joints */}
      {[11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28].map((idx) => (
        <mesh key={`joint-${idx}`} position={[landmarks[idx].x, landmarks[idx].y, landmarks[idx].z]}>
          <sphereGeometry args={[0.04, 16, 16]} />
          <meshStandardMaterial color="#ffffff" />
        </mesh>
      ))}
    </group>
  );
};

const AnimatedScene = ({ poseData, currentFrame }) => {
  const groupRef = useRef();

  if (!poseData || !poseData.poses[currentFrame]) return null;

  // Get current pose and reshape to landmarks
  const poseVector = poseData.poses[currentFrame];
  const landmarks = [];
  for (let i = 0; i < 33; i++) {
    landmarks.push({
      x: poseVector[i * 3],
      y: -poseVector[i * 3 + 1], // Flip Y for proper orientation
      z: poseVector[i * 3 + 2]
    });
  }

  return (
    <>
      <PerspectiveCamera makeDefault position={[0, 0, 3]} />
      <OrbitControls enableZoom={true} enablePan={true} />
      
      <ambientLight intensity={0.5} />
      <directionalLight position={[5, 5, 5]} intensity={1} />
      <directionalLight position={[-5, -5, -5]} intensity={0.5} />
      
      <group ref={groupRef}>
        <HumanoidBody landmarks={landmarks} />
      </group>

      {/* Ground plane */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1, 0]}>
        <planeGeometry args={[10, 10]} />
        <meshStandardMaterial color="#1a1a2e" opacity={0.5} transparent />
      </mesh>

      {/* Grid helper */}
      <gridHelper args={[10, 10, '#444', '#222']} position={[0, -1, 0]} />
    </>
  );
};

const AnimatedHumanViewer = ({ poseData }) => {
  const [currentFrame, setCurrentFrame] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [fps, setFps] = useState(10);
  const animationRef = useRef(null);

  useEffect(() => {
    if (!isPlaying || !poseData) return;

    const interval = 1000 / fps;
    let lastTime = Date.now();

    const animate = () => {
      const now = Date.now();
      if (now - lastTime >= interval) {
        setCurrentFrame(prev => (prev + 1) % poseData.poses.length);
        lastTime = now;
      }
      animationRef.current = requestAnimationFrame(animate);
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isPlaying, fps, poseData]);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleReset = () => {
    setCurrentFrame(0);
  };

  if (!poseData) return <div>Loading...</div>;

  const frameType = currentFrame < poseData.seed_frames ? 'SEED' : 'GENERATED';

  return (
    <div className="animated-human-viewer">
      <div className="canvas-container">
        <Canvas>
          <AnimatedScene poseData={poseData} currentFrame={currentFrame} />
        </Canvas>
        
        <div className="frame-info">
          <div className="frame-number">Frame: {currentFrame + 1}/{poseData.poses.length}</div>
          <div className={`frame-type ${frameType.toLowerCase()}`}>{frameType}</div>
        </div>
      </div>

      <div className="controls">
        <button onClick={handlePlayPause} className="control-btn">
          {isPlaying ? '⏸️ Pause' : '▶️ Play'}
        </button>
        <button onClick={handleReset} className="control-btn">
          🔄 Reset
        </button>
        
        <div className="slider-group">
          <label>Speed: {fps} FPS</label>
          <input
            type="range"
            min="1"
            max="30"
            value={fps}
            onChange={(e) => setFps(Number(e.target.value))}
            className="fps-slider"
          />
        </div>
      </div>

      <div className="instructions">
        <p>🖱️ Drag to rotate • Scroll to zoom • Right-click to pan</p>
      </div>
    </div>
  );
};

export default AnimatedHumanViewer;
