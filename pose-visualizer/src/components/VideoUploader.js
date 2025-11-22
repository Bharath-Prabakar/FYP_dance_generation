import React, { useState } from 'react';
import './VideoUploader.css';

const API_BASE_URL = 'http://localhost:5000/api';

const VideoUploader = ({ onPoseDataGenerated }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [progress, setProgress] = useState('');
  const [error, setError] = useState(null);
  const [numFrames, setNumFrames] = useState(100);
  const [videoPreview, setVideoPreview] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      processFile(file);
    }
  };

  const processFile = (file) => {
    // Validate file type
    const validTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/x-matroska'];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(mp4|avi|mov|mkv)$/i)) {
      setError('Invalid file type. Please upload MP4, AVI, MOV, or MKV');
      return;
    }

    setSelectedFile(file);
    setError(null);
    
    // Create video preview
    const videoUrl = URL.createObjectURL(file);
    setVideoPreview(videoUrl);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);

    const files = event.dataTransfer.files;
    if (files && files.length > 0) {
      processFile(files[0]);
    }
  };

  const handleUploadAndGenerate = async () => {
    if (!selectedFile) {
      setError('Please select a video file first');
      return;
    }

    try {
      setError(null);
      
      // Step 1: Upload video
      setUploading(true);
      setProgress('Uploading video...');
      
      const formData = new FormData();
      formData.append('video', selectedFile);
      
      const uploadResponse = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
      });
      
      if (!uploadResponse.ok) {
        const errorData = await uploadResponse.json();
        throw new Error(errorData.error || 'Upload failed');
      }
      
      const uploadData = await uploadResponse.json();
      setUploading(false);
      
      // Step 2: Generate poses
      setGenerating(true);
      setProgress('Extracting poses from video...');
      
      const generateResponse = await fetch(`${API_BASE_URL}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: uploadData.filename,
          num_frames: numFrames,
          proc_fps: 4
        }),
      });
      
      if (!generateResponse.ok) {
        const errorData = await generateResponse.json();
        throw new Error(errorData.error || 'Generation failed');
      }
      
      setProgress('Generating AI poses...');
      const poseData = await generateResponse.json();
      
      setGenerating(false);
      setProgress('');
      
      // Pass data to parent component
      onPoseDataGenerated(poseData);
      
    } catch (err) {
      setError(err.message);
      setUploading(false);
      setGenerating(false);
      setProgress('');
    }
  };

  const isProcessing = uploading || generating;

  return (
    <div className="video-uploader">
      <div className="upload-card">
        <h2>Upload Your Dance Video</h2>
        <p className="description">
          Upload a video to extract poses and generate AI-predicted dance movements
        </p>

        {videoPreview && (
          <div className="video-preview">
            <video src={videoPreview} controls width="400" />
          </div>
        )}

        <div 
          className={`upload-section ${isDragging ? 'dragging' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <label htmlFor="video-input" className="file-label">
            <span className="icon">📹</span>
            <div className="upload-text">
              {selectedFile ? (
                <span className="file-name">{selectedFile.name}</span>
              ) : (
                <>
                  <span className="main-text">Drag & Drop Video Here</span>
                  <span className="sub-text">or click to browse</span>
                </>
              )}
            </div>
          </label>
          <input
            id="video-input"
            type="file"
            accept="video/mp4,video/avi,video/mov,video/mkv"
            onChange={handleFileSelect}
            disabled={isProcessing}
            className="file-input"
          />
        </div>

        <div className="settings">
          <label>
            Frames to Generate:
            <input
              type="number"
              min="10"
              max="500"
              value={numFrames}
              onChange={(e) => setNumFrames(Number(e.target.value))}
              disabled={isProcessing}
              className="number-input"
            />
          </label>
          <p className="hint">
            The model will extract the first 32 frames from your video as seed,
            then generate {numFrames} new AI-predicted poses
          </p>
        </div>

        {error && (
          <div className="error-message">
            <span className="error-icon">❌</span>
            {error}
          </div>
        )}

        {progress && (
          <div className="progress-message">
            <div className="spinner-small"></div>
            {progress}
          </div>
        )}

        <button
          onClick={handleUploadAndGenerate}
          disabled={!selectedFile || isProcessing}
          className="generate-btn"
        >
          {isProcessing ? (
            <>
              <div className="spinner-small"></div>
              Processing...
            </>
          ) : (
            <>
              <span className="icon">🚀</span>
              Generate Poses
            </>
          )}
        </button>

        <div className="info-box">
          <h3>How it works:</h3>
          <ol>
            <li>Upload your dance video (MP4, AVI, MOV, MKV)</li>
            <li>AI extracts the first 32 frames as "seed" poses</li>
            <li>Model generates future dance movements</li>
            <li>Visualize in Stick Figure or 3D Animated mode</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default VideoUploader;
