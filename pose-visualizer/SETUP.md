# Quick Setup Guide

## Step 1: Install Node.js
If you don't have Node.js installed, download it from: https://nodejs.org/
(Choose the LTS version)

## Step 2: Install Dependencies
Open Command Prompt in the `pose-visualizer` folder and run:
```cmd
npm install
```

This will install:
- React (UI framework)
- Three.js (3D graphics)
- React Three Fiber (React + Three.js integration)

## Step 3: Copy Your Pose Data
Copy your generated poses file to the public folder:
```cmd
copy ..\generated_poses.json public\
```

## Step 4: Start the App
```cmd
npm start
```

The app will automatically open in your browser at `http://localhost:3000`

## What You'll See

### Two Viewing Modes:

1. **🦴 Stick Figure Mode**
   - Classic 2D skeleton visualization
   - Shows all 33 MediaPipe landmarks
   - Color-coded joints
   - Frame counter showing SEED vs GENERATED frames

2. **💃 Animated Human Mode**
   - 3D humanoid model with realistic proportions
   - Interactive camera controls:
     - Drag to rotate
     - Scroll to zoom
     - Right-click + drag to pan
   - Color-coded body parts:
     - Yellow head
     - Pink torso
     - Green arms
     - Blue legs
   - Grid floor for spatial reference

### Playback Controls:
- ▶️/⏸️ Play/Pause button
- 🔄 Reset to first frame
- Speed slider (1-30 FPS)

## Troubleshooting

### "npm is not recognized"
- Node.js is not installed or not in PATH
- Restart Command Prompt after installing Node.js

### "Failed to load pose data"
- Make sure `generated_poses.json` is in the `public` folder
- Check that the file is valid JSON

### Port 3000 already in use
- Close other React apps or use a different port:
  ```cmd
  set PORT=3001 && npm start
  ```

### 3D view is black/not rendering
- Your browser might not support WebGL
- Try updating your browser or graphics drivers
- Use Stick Figure mode as fallback

## Next Steps

Once running, you can:
1. Switch between Stick Figure and Animated Human modes
2. Adjust playback speed
3. Observe the difference between SEED frames (from video) and GENERATED frames (AI predictions)
4. Interact with the 3D model in Animated Human mode

Enjoy visualizing your dance poses! 🕺💃
