"""
Flask Backend Server for Dance Pose Generation
Handles video upload, pose extraction, and AI generation
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Import inference function
from stgcn_inference import generate_poses_from_video

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['MAX_CONTENT_PATH'] = MAX_FILE_SIZE

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# No need for model cache - stgcn_inference.py handles everything


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Backend server is running'
    })


@app.route('/api/upload', methods=['POST'])
def upload_video():
    """
    Handle video upload and return file info
    """
    try:
        # Check if file is in request
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        file = request.files['video']
        
        # Check if filename is empty
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({
            'message': 'Video uploaded successfully',
            'filename': filename,
            'filepath': filepath
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate', methods=['POST'])
def generate_poses():
    """
    Generate poses from uploaded video
    Expects JSON: { "filename": "video.mp4", "num_frames": 100, "proc_fps": 4 }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'filename' not in data:
            return jsonify({'error': 'Missing filename parameter'}), 400
        
        filename = data['filename']
        num_frames = data.get('num_frames', 100)
        proc_fps = data.get('proc_fps', 4)
        
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Check if file exists
        if not os.path.exists(video_path):
            return jsonify({'error': 'Video file not found'}), 404
        
        # Generate poses using stgcn_inference.py
        print(f"Generating poses from {filename}...")
        output_data = generate_poses_from_video(
            video_path=video_path,
            model_dir='model_outputs',
            num_frames=num_frames,
            proc_fps=proc_fps,
            output_file='generated_poses.json'
        )
        
        print(f"✅ Successfully generated {output_data['total_frames']} poses")
        
        return jsonify(output_data), 200
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error: {error_trace}")
        return jsonify({
            'error': str(e),
            'trace': error_trace
        }), 500


@app.route('/api/models/status', methods=['GET'])
def model_status():
    """Check if models are available"""
    import os
    model_exists = os.path.exists('model_outputs/stgcn_regressor.pth')
    return jsonify({
        'model_available': model_exists,
        'model_path': 'model_outputs/stgcn_regressor.pth'
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Starting Dance Pose Generation Backend Server")
    print("="*60)
    print("Server will run on: http://localhost:5000")
    print("Endpoints:")
    print("  - GET  /api/health          - Health check")
    print("  - POST /api/upload          - Upload video")
    print("  - POST /api/generate        - Generate poses")
    print("  - GET  /api/models/status   - Check model status")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
