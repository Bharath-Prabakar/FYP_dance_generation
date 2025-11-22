# ST-GCN Inference - Quick Start Guide

## ⚠️ Python Version Requirement

**Required**: Python 3.8 - 3.12 (MediaPipe not yet available for 3.13)  
**If you have Python 3.13**: See `PYTHON_VERSION_FIX.md` for solutions

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies (1 minute)
```bash
pip install -r requirements_inference.txt
```

**If you get MediaPipe error**: You need Python 3.12 or earlier. See `PYTHON_VERSION_FIX.md`

### Step 2: Verify Setup (30 seconds)
```bash
python test_inference_setup.py
```

### Step 3: Run Inference (2-5 seconds)
```bash
python stgcn_inference.py --video_path your_dance_video.mp4
```

**Output**: `generated_poses.json` with 132 pose vectors (32 seed + 100 generated)

---

## 📋 Command Line Options

```bash
python stgcn_inference.py \
    --video_path dance.mp4 \        # Required: Input video
    --model_dir model_outputs \     # Model directory (default: model_outputs)
    --num_frames 100 \              # Frames to generate (default: 100)
    --proc_fps 4 \                  # Processing FPS (default: 4)
    --output_file output.json       # Output file (default: generated_poses.json)
```

---

## 📦 What You Need

### Required Files
- ✅ `stgcn_inference.py` - Main script
- ✅ `model_outputs/stgcn_regressor.pth` - Model weights

### Optional Files
- ⚠️ `model_outputs/pca_transformer.pkl` - For analysis
- ⚠️ `model_outputs/kmeans_clusters.pkl` - For keyframes

---

## 🔧 Common Commands

### Basic Inference
```bash
python stgcn_inference.py --video_path dance.mp4
```

### Generate More Frames
```bash
python stgcn_inference.py --video_path dance.mp4 --num_frames 200
```

### Faster Processing (Lower FPS)
```bash
python stgcn_inference.py --video_path dance.mp4 --proc_fps 2
```

### Custom Output Location
```bash
python stgcn_inference.py --video_path dance.mp4 --output_file results/output.json
```

---

## 🌐 Web Service (Flask)

### Create `app.py`:
```python
from flask import Flask, request, jsonify
import subprocess
import json

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    video = request.files['video']
    video.save('temp.mp4')
    
    subprocess.run([
        'python', 'stgcn_inference.py',
        '--video_path', 'temp.mp4',
        '--output_file', 'output.json'
    ])
    
    with open('output.json') as f:
        return jsonify(json.load(f))

if __name__ == '__main__':
    app.run(port=5000)
```

### Run:
```bash
pip install flask
python app.py
```

### Test:
```bash
curl -X POST -F "video=@dance.mp4" http://localhost:5000/generate
```

---

## 📊 Output Format

```json
{
  "video_path": "dance.mp4",
  "seed_frames": 32,
  "generated_frames": 100,
  "total_frames": 132,
  "pose_dimension": 99,
  "poses": [
    [0.123, -0.456, 0.789, ...],  // 99 values per pose
    [0.124, -0.455, 0.788, ...],
    ...
  ]
}
```

**Pose Format**: 33 joints × 3 coordinates (x, y, z) = 99 values

---

## 🐛 Troubleshooting

### Error: "MediaPipe not initialized"
```bash
pip install mediapipe
```

### Error: "Model file not found"
```bash
# Check if model exists
ls model_outputs/stgcn_regressor.pth

# Run validation
python test_inference_setup.py
```

### Error: "Video has insufficient frames"
- Video needs ≥32 frames at processing FPS
- Solution: Use longer video or reduce `--proc_fps`

### Slow Processing
```bash
# Use GPU (if available)
python stgcn_inference.py --video_path dance.mp4

# Or reduce processing FPS
python stgcn_inference.py --video_path dance.mp4 --proc_fps 2
```

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `QUICK_START.md` | This file - Quick reference |
| `INFERENCE_README.md` | Complete user guide |
| `DEPLOYMENT_GUIDE.md` | Production deployment |
| `INFERENCE_FILES_SUMMARY.md` | All files overview |

---

## 💡 Tips

1. **First time?** Run `test_inference_setup.py` to verify everything
2. **Need speed?** Use GPU or reduce `--proc_fps`
3. **Web service?** See `DEPLOYMENT_GUIDE.md` for Flask/FastAPI examples
4. **Debugging?** Check output of `test_inference_setup.py`

---

## ⚡ Performance

| Metric | Value |
|--------|-------|
| Video processing | 1-2 sec per 100 frames |
| Pose generation (GPU) | 0.5-1 sec per 100 frames |
| Pose generation (CPU) | 2-5 sec per 100 frames |
| Total (typical) | 2-7 seconds |

---

## 🎯 Next Steps

1. ✅ Install dependencies
2. ✅ Verify setup
3. ✅ Test with sample video
4. 🚀 Deploy to web service
5. 📈 Monitor and optimize

---

## 🆘 Need Help?

- Run validation: `python test_inference_setup.py`
- Check logs: Look for error messages in terminal
- Read docs: `INFERENCE_README.md` has detailed troubleshooting
- Test setup: Verify all files exist with `ls -la`

---

**Ready to go!** 🎉

Start with: `python stgcn_inference.py --video_path your_video.mp4`
