# Dance Pose Visualization Guide
## From JSON to Realistic Human Mesh

Your `generated_poses.json` contains 99-D pose vectors. Here are the best ways to visualize them as realistic human figures for presentations and demonstrations.

---

## 🎯 Quick Comparison

| Method | Quality | Ease | Best For |
|--------|---------|------|----------|
| **PyVista (Python)** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Quick visualization, research |
| **Three.js (Web)** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Web demos, interactive |
| **SMPL Model** | ⭐⭐⭐⭐⭐ | ⭐⭐ | Publication-quality |
| **Unity + Mixamo** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Professional demos |

---

## Option 1: PyVista - Easiest & Fastest ⭐ RECOMMENDED

### Installation
```bash
pip install pyvista numpy pillow tqdm
```

### Usage

#### Interactive 3D Viewer
```bash
python visualize_human_mesh.py --json generated_poses.json --mode interactive
```
**Controls**: Arrow keys or Space to navigate, mouse to rotate/zoom

#### Export as Video
```bash
# Requires ffmpeg: https://ffmpeg.org/download.html
python visualize_human_mesh.py --json generated_poses.json --mode video --output dance.mp4 --fps 30
```

#### Export as Images
```bash
python visualize_human_mesh.py --json generated_poses.json --mode images --output pose_images --max_frames 50
```

### Features
- ✅ Smooth 3D human mesh
- ✅ Realistic skin tone and lighting
- ✅ Interactive viewer
- ✅ Video export
- ✅ High-quality images (1920x1080)

---

## Option 2: Web Viewer - Best for Presentations ⭐⭐

### Setup
1. Open `web_pose_viewer.html` in a web browser
2. Click "Choose File" and select your `generated_poses.json`
3. Click Play to see the animation

### Features
- ✅ Interactive 3D viewer in browser
- ✅ Play/pause controls
- ✅ Frame-by-frame navigation
- ✅ Adjustable playback speed
- ✅ No installation required
- ✅ Works on any device with a browser

### Sharing
- Host on GitHub Pages, Netlify, or any web server
- Share link with domain experts
- Works on mobile devices

---

## Option 3: SMPL Model - Publication Quality ⭐⭐⭐

### Setup
1. **Download SMPL Model** (free for research):
   - Go to: https://smpl.is.tue.mpg.de/
   - Register and download SMPL model files

2. **Install Dependencies**:
```bash
pip install smplx trimesh pyrender pillow
```

3. **Run Visualization**:
```python
python visualize_with_smpl.py
```

### Features
- ✅ Industry-standard human model
- ✅ Anatomically accurate
- ✅ Publication-quality renders
- ✅ Used in research papers

### Note
Requires inverse kinematics to convert MediaPipe poses to SMPL parameters. The provided script includes a basic conversion - you may need to refine it for your specific use case.

---

## Option 4: Unity3D + Mixamo - Professional Demos ⭐⭐⭐

### Setup

1. **Get Mixamo Character** (free):
   - Go to: https://www.mixamo.com/
   - Download a rigged character (FBX format)

2. **Unity Setup**:
   - Create new Unity project
   - Import Mixamo character
   - Add `unity_pose_visualizer.cs` script
   - Assign character's joints in Inspector

3. **Load Poses**:
   - Copy `generated_poses.json` to Unity project
   - Press Play

### Features
- ✅ Professional-quality characters
- ✅ Smooth animations
- ✅ Interactive camera controls
- ✅ Export as video or GIF
- ✅ VR/AR ready

---

## 🎨 Customization Options

### PyVista Customization

```python
# Change colors
render_pose_to_image(
    pose,
    output_path,
    color='#FF6B6B',  # Custom color
    background='gradient'  # or 'white', 'black'
)

# Adjust mesh quality
create_human_mesh_from_pose(
    pose,
    joint_radius=0.05,  # Larger joints
    bone_radius=0.03    # Thicker bones
)
```

### Web Viewer Customization

Edit `web_pose_viewer.html`:
```javascript
// Change colors
const jointMaterial = new THREE.MeshPhongMaterial({ color: 0xff5555 });
const boneMaterial = new THREE.MeshPhongMaterial({ color: 0xE0AC69 });

// Change background
scene.background = new THREE.Color(0x87CEEB); // Sky blue
```

---

## 📊 Comparison for Your Use Case

### For Domain Experts (Bharatanatyam Teachers)
**Recommended**: PyVista Interactive Viewer or Web Viewer
- Easy to use
- Clear visualization
- Can pause and examine poses
- No technical knowledge required

### For Research Presentations
**Recommended**: PyVista Video Export or SMPL
- High-quality renders
- Professional appearance
- Can be embedded in slides

### For Web Deployment
**Recommended**: Three.js Web Viewer
- Works in browser
- No installation
- Interactive
- Mobile-friendly

### For Publications
**Recommended**: SMPL Model
- Industry standard
- Anatomically accurate
- Accepted in research papers

---

## 🚀 Quick Start Workflow

### 1. Generate Poses
```bash
python stgcn_inference.py --video_path dance.mp4 --num_frames 100
```

### 2. Visualize (Choose One)

**Option A: Quick Preview**
```bash
python visualize_human_mesh.py --json generated_poses.json --mode interactive
```

**Option B: Create Video**
```bash
python visualize_human_mesh.py --json generated_poses.json --mode video --output demo.mp4
```

**Option C: Web Demo**
```bash
# Just open web_pose_viewer.html in browser and load JSON
```

---

## 💡 Tips for Best Results

### 1. Lighting
- Use multiple light sources for depth
- Add ambient + directional lighting
- Avoid harsh shadows

### 2. Camera Angles
- Front view: Best for pose clarity
- Side view: Shows depth and balance
- 45° angle: Most natural perspective

### 3. Colors
- Skin tone (#E0AC69) for realism
- Bright colors for emphasis
- Gradient backgrounds for depth

### 4. Animation
- 30 FPS for smooth playback
- Add motion blur for realism
- Use easing for natural movement

---

## 🎬 Creating Professional Demos

### For Presentations

1. **Export Key Frames**:
```bash
python visualize_human_mesh.py --json generated_poses.json --mode images --max_frames 10
```

2. **Create Comparison**:
   - Show original video frame
   - Show extracted pose
   - Show generated future pose

3. **Add Annotations**:
   - Use image editing software
   - Highlight key joints
   - Add labels

### For Videos

1. **Create Animation**:
```bash
python visualize_human_mesh.py --json generated_poses.json --mode video --fps 30
```

2. **Add Music/Narration**:
   - Use video editing software
   - Add Bharatanatyam music
   - Add voiceover explanation

3. **Side-by-Side Comparison**:
   - Original video | Generated poses
   - Shows model accuracy

---

## 🔧 Troubleshooting

### "PyVista not rendering"
```bash
# Install VTK
pip install vtk

# For headless servers
export DISPLAY=:0
```

### "Web viewer not loading"
- Check browser console for errors
- Ensure JSON file is valid
- Try different browser (Chrome recommended)

### "SMPL model not found"
- Download from https://smpl.is.tue.mpg.de/
- Place in correct directory
- Check file paths in script

---

## 📚 Additional Resources

- **PyVista Docs**: https://docs.pyvista.org/
- **Three.js Docs**: https://threejs.org/docs/
- **SMPL**: https://smpl.is.tue.mpg.de/
- **Mixamo**: https://www.mixamo.com/
- **Unity**: https://unity.com/

---

## ✅ Recommended Workflow for Your Project

1. **Development**: Use PyVista interactive viewer
2. **Testing**: Use web viewer for quick checks
3. **Demos**: Create videos with PyVista
4. **Final Presentation**: Use Unity + Mixamo for professional quality

---

**Start with PyVista - it's the easiest and gives great results!** 🎉

```bash
python visualize_human_mesh.py --json generated_poses.json --mode interactive
```
