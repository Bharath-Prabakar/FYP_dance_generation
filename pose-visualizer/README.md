# Dance Pose Visualizer

A React application for visualizing AI-generated dance poses with two viewing modes:
- **Stick Figure Mode**: Classic 2D skeleton visualization
- **Animated Human Mode**: 3D humanoid model with interactive camera controls

## Setup Instructions

### 1. Install Dependencies
```bash
cd pose-visualizer
npm install
```

### 2. Copy Pose Data
Copy your `generated_poses.json` file to the `public` folder:
```bash
copy ..\generated_poses.json public\
```

### 3. Run the Application
```bash
npm start
```

The app will open at `http://localhost:3000`

## Features

### Stick Figure Mode
- 2D skeleton visualization with MediaPipe pose connections
- Color-coded joints (upper body vs lower body)
- Frame type indicator (SEED vs GENERATED)
- Smooth animation playback

### Animated Human Mode
- 3D humanoid model with realistic body proportions
- Interactive 3D camera controls:
  - **Drag**: Rotate view
  - **Scroll**: Zoom in/out
  - **Right-click + Drag**: Pan camera
- Color-coded body parts:
  - Head: Yellow
  - Torso: Pink
  - Arms: Green
  - Legs: Blue
- Grid floor for spatial reference

### Playback Controls
- Play/Pause animation
- Reset to first frame
- Adjustable playback speed (1-30 FPS)
- Frame counter with seed/generated indicator

## Project Structure
```
pose-visualizer/
├── public/
│   ├── index.html
│   └── generated_poses.json (copy your file here)
├── src/
│   ├── components/
│   │   ├── StickFigureViewer.js
│   │   ├── StickFigureViewer.css
│   │   ├── AnimatedHumanViewer.js
│   │   └── AnimatedHumanViewer.css
│   ├── App.js
│   ├── App.css
│   ├── index.js
│   └── index.css
└── package.json
```

## Technologies Used
- **React 18**: UI framework
- **Three.js**: 3D graphics rendering
- **@react-three/fiber**: React renderer for Three.js
- **@react-three/drei**: Useful helpers for React Three Fiber
- **Canvas API**: 2D stick figure rendering

## Customization

### Adjust Colors
Edit the color values in the viewer components:
- `StickFigureViewer.js`: Lines 70-80
- `AnimatedHumanViewer.js`: Lines 40-60

### Change Animation Speed
Default FPS range is 1-30. Modify in the viewer components:
```javascript
<input type="range" min="1" max="30" ... />
```

### Modify 3D Model
Adjust body part sizes in `AnimatedHumanViewer.js`:
- Head size: Line 110 `sphereGeometry args={[0.15, ...]}`
- Limb thickness: Lines 40-60 in `createLimb` calls

## Troubleshooting

### "Failed to load pose data"
- Ensure `generated_poses.json` is in the `public` folder
- Check that the JSON file is valid

### 3D model not rendering
- Check browser console for WebGL errors
- Ensure your browser supports WebGL 2.0

### Performance issues
- Reduce FPS slider value
- Close other browser tabs
- Try stick figure mode (less GPU intensive)

## Building for Production
```bash
npm run build
```

The optimized build will be in the `build` folder.
