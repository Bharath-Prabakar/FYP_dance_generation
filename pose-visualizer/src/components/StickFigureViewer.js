import React, { useEffect, useRef, useState } from 'react';
import './StickFigureViewer.css';

// MediaPipe pose connections (33 landmarks)
const POSE_CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 7], [0, 4], [4, 5], [5, 6], [6, 8],
  [9, 10], [11, 12], [11, 13], [13, 15], [15, 17], [15, 19], [15, 21],
  [17, 19], [12, 14], [14, 16], [16, 18], [16, 20], [16, 22], [18, 20],
  [11, 23], [12, 24], [23, 24], [23, 25], [25, 27], [27, 29], [27, 31],
  [29, 31], [24, 26], [26, 28], [28, 30], [28, 32], [30, 32]
];

const StickFigureViewer = ({ poseData }) => {
  const canvasRef = useRef(null);
  const [currentFrame, setCurrentFrame] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [fps, setFps] = useState(10);
  const animationRef = useRef(null);

  useEffect(() => {
    if (!poseData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const poses = poseData.poses;

    const drawPose = (frameIndex) => {
      // Clear canvas
      ctx.fillStyle = '#1a1a2e';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Get current pose (99-dimensional vector)
      const poseVector = poses[frameIndex];
      
      // Reshape to 33 landmarks x 3 coordinates
      const landmarks = [];
      for (let i = 0; i < 33; i++) {
        landmarks.push({
          x: poseVector[i * 3],
          y: poseVector[i * 3 + 1],
          z: poseVector[i * 3 + 2]
        });
      }

      // Find bounding box for scaling
      const xs = landmarks.map(l => l.x);
      const ys = landmarks.map(l => l.y);
      const minX = Math.min(...xs);
      const maxX = Math.max(...xs);
      const minY = Math.min(...ys);
      const maxY = Math.max(...ys);

      const rangeX = maxX - minX || 1;
      const rangeY = maxY - minY || 1;
      const scale = Math.min(canvas.width / rangeX, canvas.height / rangeY) * 0.7;
      const offsetX = canvas.width / 2;
      const offsetY = canvas.height / 2;

      // Transform function
      const transform = (lm) => ({
        x: offsetX + (lm.x - (minX + maxX) / 2) * scale,
        y: offsetY + (lm.y - (minY + maxY) / 2) * scale
      });

      // Draw connections
      ctx.strokeStyle = '#00d4ff';
      ctx.lineWidth = 3;
      ctx.lineCap = 'round';

      POSE_CONNECTIONS.forEach(([i, j]) => {
        const p1 = transform(landmarks[i]);
        const p2 = transform(landmarks[j]);
        
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();
      });

      // Draw joints
      landmarks.forEach((lm, idx) => {
        const p = transform(lm);
        ctx.beginPath();
        ctx.arc(p.x, p.y, 5, 0, 2 * Math.PI);
        ctx.fillStyle = idx < 11 ? '#ff6b9d' : '#c44569'; // Different colors for upper/lower body
        ctx.fill();
      });

      // Draw frame info
      ctx.fillStyle = 'white';
      ctx.font = '16px monospace';
      ctx.fillText(`Frame: ${frameIndex + 1}/${poses.length}`, 10, 30);
      
      const frameType = frameIndex < poseData.seed_frames ? 'SEED' : 'GENERATED';
      ctx.fillStyle = frameIndex < poseData.seed_frames ? '#4ecca3' : '#ffd93d';
      ctx.fillText(frameType, 10, 55);
    };

    drawPose(currentFrame);
  }, [poseData, currentFrame]);

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

  return (
    <div className="stick-figure-viewer">
      <canvas
        ref={canvasRef}
        width={800}
        height={600}
        className="pose-canvas"
      />
      
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
    </div>
  );
};

export default StickFigureViewer;
