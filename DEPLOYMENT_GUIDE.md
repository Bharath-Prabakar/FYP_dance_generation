# ST-GCN Inference - Web Deployment Guide

## Quick Start

### 1. Setup Environment

```bash
# Install dependencies
pip install -r requirements_inference.txt

# Verify setup
python test_inference_setup.py
```

### 2. Test Inference

```bash
# Test with a sample video
python stgcn_inference.py --video_path sample_dance.mp4 --num_frames 50
```

### 3. Deploy to Web Service

Choose your preferred framework below.

---

## Deployment Options

### Option 1: Flask (Simple & Fast)

**File: `app_flask.py`**

```python
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import subprocess
import json
import os
import uuid
from pathlib import Path

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'

# Create folders
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path(app.config['OUTPUT_FOLDER']).mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "stgcn-inference"})

@app.route('/generate', methods=['POST'])
def generate_poses():
    """
    Generate dance poses from uploaded video
    
    Form data:
        - video: Video file (required)
        - num_frames: Number of frames to generate (optional, default: 100)
    
    Returns:
        JSON with generated poses
    """
    # Validate request
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400
    
    video = request.files['video']
    if video.filename == '':
        return jsonify({"error": "Empty filename"}), 400
    
    if not allowed_file(video.filename):
        return jsonify({"error": "Invalid file type"}), 400
    
    # Get parameters
    num_frames = int(request.form.get('num_frames', 100))
    
    # Generate unique ID for this request
    request_id = str(uuid.uuid4())
    
    # Save uploaded video
    filename = secure_filename(video.filename)
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{request_id}_{filename}")
    video.save(video_path)
    
    # Output file
    output_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{request_id}_output.json")
    
    try:
        # Run inference
        result = subprocess.run([
            'python', 'stgcn_inference.py',
            '--video_path', video_path,
            '--model_dir', 'model_outputs',
            '--num_frames', str(num_frames),
            '--output_file', output_file
        ], capture_output=True, text=True, timeout=300)  # 5 min timeout
        
        if result.returncode != 0:
            return jsonify({
                "error": "Inference failed",
                "details": result.stderr
            }), 500
        
        # Load and return results
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        return jsonify({
            "success": True,
            "request_id": request_id,
            "data": data
        })
    
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Processing timeout"}), 504
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(output_file):
            os.remove(output_file)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

**Run Flask:**
```bash
python app_flask.py
```

**Test:**
```bash
curl -X POST -F "video=@dance.mp4" -F "num_frames=50" http://localhost:5000/generate
```

---

### Option 2: FastAPI (Modern & Async)

**File: `app_fastapi.py`**

```python
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json
import os
import uuid
from pathlib import Path
import asyncio

app = FastAPI(title="ST-GCN Dance Pose Generator")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create folders
Path("uploads").mkdir(exist_ok=True)
Path("outputs").mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}

@app.get("/")
async def root():
    return {"message": "ST-GCN Dance Pose Generator API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/generate")
async def generate_poses(
    video: UploadFile = File(...),
    num_frames: int = Form(100)
):
    """
    Generate dance poses from uploaded video
    
    Args:
        video: Video file
        num_frames: Number of frames to generate (default: 100)
    
    Returns:
        JSON with generated poses
    """
    # Validate file type
    file_ext = Path(video.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {ALLOWED_EXTENSIONS}"
        )
    
    # Generate unique ID
    request_id = str(uuid.uuid4())
    
    # Save uploaded video
    video_path = f"uploads/{request_id}_{video.filename}"
    output_file = f"outputs/{request_id}_output.json"
    
    try:
        # Save video
        with open(video_path, "wb") as f:
            content = await video.read()
            f.write(content)
        
        # Run inference
        process = await asyncio.create_subprocess_exec(
            'python', 'stgcn_inference.py',
            '--video_path', video_path,
            '--model_dir', 'model_outputs',
            '--num_frames', str(num_frames),
            '--output_file', output_file,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=300  # 5 min timeout
        )
        
        if process.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Inference failed: {stderr.decode()}"
            )
        
        # Load results
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        return JSONResponse(content={
            "success": True,
            "request_id": request_id,
            "data": data
        })
    
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Processing timeout")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(output_file):
            os.remove(output_file)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Install FastAPI:**
```bash
pip install fastapi uvicorn python-multipart
```

**Run FastAPI:**
```bash
uvicorn app_fastapi:app --host 0.0.0.0 --port 8000
```

**Test:**
```bash
curl -X POST -F "video=@dance.mp4" -F "num_frames=50" http://localhost:8000/generate
```

**Interactive docs:** http://localhost:8000/docs

---

## Production Deployment

### Docker Deployment

**Dockerfile:**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_inference.txt .
RUN pip install --no-cache-dir -r requirements_inference.txt

# Copy application files
COPY stgcn_inference.py .
COPY app_fastapi.py .
COPY model_outputs/ ./model_outputs/

# Create directories
RUN mkdir -p uploads outputs

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app_fastapi:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run:**
```bash
docker build -t stgcn-inference .
docker run -p 8000:8000 stgcn-inference
```

---

### Cloud Deployment

#### AWS Lambda (Serverless)

1. Package dependencies:
```bash
pip install -r requirements_inference.txt -t package/
cp stgcn_inference.py package/
cp -r model_outputs package/
```

2. Create Lambda handler:
```python
# lambda_handler.py
import json
import base64
import tempfile
import os
from stgcn_inference import load_pipeline_models, get_seed_sequence_from_video, predict_pose_sequence

# Load models once (cold start)
model, pca, kmeans, config = load_pipeline_models("model_outputs")

def lambda_handler(event, context):
    # Decode video from base64
    video_data = base64.b64decode(event['body'])
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as f:
        f.write(video_data)
        video_path = f.name
    
    try:
        # Process
        seed = get_seed_sequence_from_video(video_path, 4, config['seq_len'])
        poses = predict_pose_sequence(model, seed, 100, config['device'], config['seq_len'])
        
        return {
            'statusCode': 200,
            'body': json.dumps({'poses': poses.tolist()})
        }
    finally:
        os.remove(video_path)
```

#### Google Cloud Run

```bash
gcloud run deploy stgcn-inference \
    --source . \
    --platform managed \
    --region us-central1 \
    --memory 4Gi \
    --timeout 300
```

---

## Performance Optimization

### 1. Model Caching
Keep models loaded in memory:

```python
# Global model cache
_model_cache = None

def get_model():
    global _model_cache
    if _model_cache is None:
        _model_cache = load_pipeline_models("model_outputs")
    return _model_cache
```

### 2. GPU Acceleration
Use GPU for faster inference:

```python
# Set CUDA device
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
```

### 3. Batch Processing
Process multiple videos in parallel:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(process_video, v) for v in videos]
    results = [f.result() for f in futures]
```

### 4. Video Preprocessing
Reduce video resolution for faster processing:

```python
# In sample_frames_from_video, resize frames
frame = cv2.resize(frame, (640, 480))
```

---

## Monitoring & Logging

### Add logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.post("/generate")
async def generate_poses(...):
    logger.info(f"Processing video: {video.filename}")
    # ... processing ...
    logger.info(f"Generated {len(poses)} poses")
```

### Metrics:

```python
import time

start_time = time.time()
# ... processing ...
duration = time.time() - start_time
logger.info(f"Processing took {duration:.2f}s")
```

---

## Security Considerations

1. **File validation**: Check file size and type
2. **Rate limiting**: Limit requests per IP
3. **Authentication**: Add API keys
4. **Sanitization**: Validate all inputs
5. **Timeouts**: Set processing timeouts
6. **Resource limits**: Limit concurrent requests

---

## Troubleshooting

### High memory usage
- Reduce batch size
- Process videos sequentially
- Clear cache after each request

### Slow processing
- Use GPU
- Reduce proc_fps
- Optimize video resolution

### CUDA errors
- Check CUDA compatibility
- Fall back to CPU
- Update PyTorch version

---

## Support

For issues or questions, refer to the main project documentation.
