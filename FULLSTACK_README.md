# Dance Pose Visualizer - Full Stack Application

Complete end-to-end application for uploading dance videos, generating AI poses, and visualizing them.

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   React Frontend│─────▶│  Flask Backend   │─────▶│  ST-GCN Model   │
│   (Port 3000)   │◀─────│   (Port 5000)    │◀─────│  (PyTorch)      │
└─────────────────┘      └──────────────────┘      └─────────────────┘
     │                            │
     │                            │
     ▼                            ▼
  Browser UI              Video Processing
  - Upload Video          - MediaPipe Pose
  - View Modes            - AI Generation
  - Controls              - JSON Output
```

## Quick Start

### Option 1: Automated (Easiest)
```cmd
START_FULL_APP.bat
```

This will:
1. Install all dependencies
2. Start Flask backend (port 5000)
3. Start React frontend (port 3000)
4. Open browser automatically

### Option 2: Manual

**Terminal 1 - Backend:**
```cmd
pip install -r requirements_backend.txt
python backend_server.py
```

**Terminal 2 - Frontend:**
```cmd
cd pose-visualizer
npm install --legacy-peer-deps
npm start
```

## How to Use

1. **Upload Video**
   - Click "Choose Video File"
   - Select MP4, AVI, MOV, or MKV file
   - Set number of frames to generate (default: 100)
   - Click "Generate Poses"

2. **Wait for Processing**
   - Backend extracts first 32 frames as seed
   - AI model generates future poses
   - Takes 30-60 seconds depending on video

3. **Visualize Results**
   - Switch between "Stick Figure" and "Animated Human" modes
   - Use Play/Pause controls
   - Adjust playback speed
   - Green frames = Original from video (SEED)
   - Yellow frames = AI generated

4. **Upload New Video**
   - Click "New Video" button
   - Repeat process

## API Endpoints

### Backend (Flask - Port 5000)

**Health Check**
```
GET /api/health
Response: { "status": "healthy", "message": "..." }
```

**Upload Video**
```
POST /api/upload
Body: FormData with 'video' file
Response: { "message": "...", "filename": "...", "filepath": "..." }
```

**Generate Poses**
```
POST /api/generate
Body: { "filename": "video.mp4", "num_frames": 100, "proc_fps": 4 }
Response: { "poses": [...], "seed_frames": 32, "generated_frames": 100, ... }
```

**Model Status**
```
GET /api/models/status
Response: { "loaded": true, "config": {...} }
```

## Features

### Frontend (React)
- ✅ Video upload with preview
- ✅ Real-time progress indicators
- ✅ Two visualization modes (Stick Figure & 3D Human)
- ✅ Interactive playback controls
- ✅ Frame counter with seed/generated labels
- ✅ Responsive design

### Backend (Flask)
- ✅ Video file upload handling
- ✅ MediaPipe pose extraction
- ✅ ST-GCN model inference
- ✅ Model caching (loads once)
- ✅ CORS enabled for React
- ✅ Error handling

### AI Model (PyTorch)
- ✅ ST-GCN architecture
- ✅ Autoregressive generation
- ✅ 33-landmark pose format
- ✅ GPU support (CUDA if available)

## File Structure

```
project/
├── backend_server.py              # Flask API server
├── stgcn_inference.py            # Model inference logic
├── requirements_backend.txt       # Python dependencies
├── model_outputs/                 # Trained model files
│   └── stgcn_regressor.pth
├── uploads/                       # Uploaded videos (auto-created)
├── pose-visualizer/              # React frontend
│   ├── src/
│   │   ├── App.js                # Main app component
│   │   ├── components/
│   │   │   ├── VideoUploader.js  # Upload interface
│   │   │   ├── StickFigureViewer.js
│   │   │   └── AnimatedHumanViewer.js
│   │   └── ...
│   ├── public/
│   └── package.json
└── START_FULL_APP.bat            # Automated startup script
```

## Requirements

### System
- Windows 10/11
- 8GB RAM minimum
- GPU optional (faster inference)

### Software
- Python 3.8+
- Node.js 16+
- npm 8+

### Python Packages
- flask
- flask-cors
- opencv-python-headless
- mediapipe
- torch
- numpy
- scikit-learn
- tqdm

### Node Packages
- react
- react-dom
- three
- @react-three/fiber
- @react-three/drei

## Troubleshooting

### Backend won't start
- Check if port 5000 is available
- Ensure model files exist in `model_outputs/`
- Verify Python dependencies: `pip list`

### Frontend won't start
- Check if port 3000 is available
- Clear npm cache: `npm cache clean --force`
- Reinstall: `rm -rf node_modules && npm install --legacy-peer-deps`

### Video upload fails
- Check file size (max 100MB)
- Verify file format (MP4, AVI, MOV, MKV)
- Check backend logs for errors

### Pose generation is slow
- First run loads models (30s)
- Subsequent runs are faster (cached)
- GPU speeds up inference significantly

### CORS errors
- Ensure backend is running on port 5000
- Check `flask-cors` is installed
- Verify proxy in `package.json`

## Performance Tips

1. **Use GPU**: Install CUDA-enabled PyTorch for 5-10x speedup
2. **Reduce frames**: Generate fewer frames for faster results
3. **Lower FPS**: Use `proc_fps: 2` for faster extraction
4. **Close other apps**: Free up RAM and CPU

## Development

### Backend Development
```cmd
python backend_server.py
# Server runs with auto-reload on code changes
```

### Frontend Development
```cmd
cd pose-visualizer
npm start
# Hot reload enabled
```

### Testing API
```cmd
# Health check
curl http://localhost:5000/api/health

# Model status
curl http://localhost:5000/api/models/status
```

## Future Enhancements

- [ ] Support for multiple video formats
- [ ] Batch processing
- [ ] Export generated poses as video
- [ ] Real-time webcam input
- [ ] Cloud deployment
- [ ] User authentication
- [ ] Pose comparison tools

## License

Educational project for Final Year Project.

## Credits

- ST-GCN Model: Spatial Temporal Graph Convolutional Networks
- MediaPipe: Google's pose detection
- Three.js: 3D visualization
- React: Frontend framework
- Flask: Backend API
