# ST-GCN Dance Pose Generation - Inference Guide

## Overview
This inference script loads a pre-trained ST-GCN model and generates future dance poses from a single input video. It's designed for real-world deployment in web applications.

## Features
- ✅ **Self-contained**: All model definitions included
- ✅ **Fast processing**: Only processes the uploaded video (no training)
- ✅ **Minimal dependencies**: Standard ML libraries only
- ✅ **Production-ready**: Error handling and validation
- ✅ **JSON output**: Easy integration with web services

## Requirements

```bash
pip install opencv-python-headless mediapipe torch numpy scikit-learn tqdm
```

## File Structure

```
project/
├── stgcn_inference.py          # Main inference script
├── example_usage.py             # Usage examples
├── model_outputs/               # Saved model files
│   ├── stgcn_regressor.pth     # ST-GCN model weights + config
│   ├── pca_transformer.pkl     # PCA model (optional)
│   └── kmeans_clusters.pkl     # K-Means model (optional)
└── INFERENCE_README.md          # This file
```

## Usage

### Command Line

Basic usage:
```bash
python stgcn_inference.py --video_path dance_video.mp4
```

With custom parameters:
```bash
python stgcn_inference.py \
    --video_path dance_video.mp4 \
    --model_dir model_outputs \
    --num_frames 100 \
    --proc_fps 4 \
    --output_file generated_poses.json
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--video_path` | str | **required** | Path to input video file |
| `--model_dir` | str | `model_outputs` | Directory containing model files |
| `--num_frames` | int | `100` | Number of future frames to generate |
| `--proc_fps` | int | `4` | Processing frame rate |
| `--output_file` | str | `generated_poses.json` | Output file path |

### Python API

```python
import subprocess
import json

# Run inference
cmd = [
    "python", "stgcn_inference.py",
    "--video_path", "dance.mp4",
    "--num_frames", "50"
]
subprocess.run(cmd)

# Load results
with open("generated_poses.json", 'r') as f:
    data = json.load(f)

poses = data['poses']  # List of 99-D pose vectors
print(f"Generated {len(poses)} poses")
```

## Output Format

The script generates a JSON file with the following structure:

```json
{
  "video_path": "dance_video.mp4",
  "seed_frames": 32,
  "generated_frames": 100,
  "total_frames": 132,
  "pose_dimension": 99,
  "poses": [
    [0.123, -0.456, 0.789, ...],  // 99-D pose vector
    [0.124, -0.455, 0.788, ...],
    ...
  ]
}
```

Each pose is a 99-dimensional vector representing 33 body landmarks (x, y, z coordinates).

## Pose Vector Format

The 99-D pose vector contains normalized 3D coordinates for 33 body landmarks:

```
[x0, y0, z0, x1, y1, z1, ..., x32, y32, z32]
```

Landmarks follow MediaPipe Pose convention:
- 0-10: Face landmarks
- 11-16: Upper body (shoulders, elbows, wrists)
- 17-22: Hands
- 23-28: Lower body (hips, knees, ankles)
- 29-32: Feet

## Normalization

Poses are normalized using:
1. **Translation**: Centered on hip midpoint
2. **Scale**: Normalized by torso length

This ensures pose invariance to position and scale.

## Web Service Integration

### Flask Example

```python
from flask import Flask, request, jsonify
import subprocess
import json
import os

app = Flask(__name__)

@app.route('/generate_poses', methods=['POST'])
def generate_poses():
    # Save uploaded video
    video = request.files['video']
    video_path = 'temp_video.mp4'
    video.save(video_path)
    
    # Run inference
    subprocess.run([
        'python', 'stgcn_inference.py',
        '--video_path', video_path,
        '--num_frames', str(request.form.get('num_frames', 100)),
        '--output_file', 'output.json'
    ])
    
    # Load and return results
    with open('output.json', 'r') as f:
        result = json.load(f)
    
    # Cleanup
    os.remove(video_path)
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### FastAPI Example

```python
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import subprocess
import json
import os

app = FastAPI()

@app.post("/generate_poses")
async def generate_poses(
    video: UploadFile = File(...),
    num_frames: int = 100
):
    # Save uploaded video
    video_path = f"temp_{video.filename}"
    with open(video_path, "wb") as f:
        f.write(await video.read())
    
    # Run inference
    subprocess.run([
        'python', 'stgcn_inference.py',
        '--video_path', video_path,
        '--num_frames', str(num_frames),
        '--output_file', 'output.json'
    ])
    
    # Load results
    with open('output.json', 'r') as f:
        result = json.load(f)
    
    # Cleanup
    os.remove(video_path)
    
    return JSONResponse(content=result)
```

## Performance Considerations

### Processing Time
- **Video processing**: ~1-2 seconds per 100 frames (depends on video resolution)
- **Pose generation**: ~0.5-1 second per 100 frames (GPU) or 2-5 seconds (CPU)
- **Total**: Typically 2-7 seconds for a 30-second video + 100 generated frames

### Optimization Tips
1. **Use GPU**: Set `CUDA_VISIBLE_DEVICES` for faster inference
2. **Reduce proc_fps**: Lower frame rate = faster processing
3. **Batch processing**: Process multiple videos in parallel
4. **Cache models**: Keep models loaded in memory for repeated requests

## Error Handling

The script handles common errors:

- **Video not found**: Validates video path before processing
- **Model files missing**: Checks for required model files
- **Insufficient frames**: Requires minimum frames for seed sequence
- **MediaPipe errors**: Graceful handling of pose detection failures

## Troubleshooting

### "MediaPipe not initialized"
```bash
pip install mediapipe
```

### "CUDA out of memory"
Use CPU instead:
```bash
export CUDA_VISIBLE_DEVICES=""
python stgcn_inference.py --video_path video.mp4
```

### "Video has insufficient frames"
The video must have at least 32 frames (8 seconds at 4 FPS). Use a longer video or reduce `proc_fps`.

## Model Files

Required files in `model_dir`:
- ✅ **stgcn_regressor.pth**: ST-GCN model weights + training config (required)
- ⚠️ **pca_transformer.pkl**: PCA model (optional, for analysis)
- ⚠️ **kmeans_clusters.pkl**: K-Means model (optional, for keyframe analysis)

## License

This inference script is designed for the Bharatanatyam dance pose generation project.

## Support

For issues or questions, please refer to the main project documentation.
