import React, { useState, useEffect } from 'react';
import './LandingPage.css';

const API_BASE_URL = 'http://localhost:5000/api';

const LandingPage = ({ onVideoSelected, onUploadProgress, onPoseDataGenerated }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [error, setError] = useState(null);
  const [numFrames, setNumFrames] = useState(100);
  const [showSettings, setShowSettings] = useState(false);
  const [currentProgress, setCurrentProgress] = useState(0);

  useEffect(() => {
    // Trigger animations on mount
    const elements = document.querySelectorAll('.animate-in');
    elements.forEach((el, index) => {
      setTimeout(() => {
        el.classList.add('visible');
      }, index * 100);
    });
  }, []);

  const processFile = (file) => {
    const validTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/x-matroska'];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(mp4|avi|mov|mkv)$/i)) {
      setError('Invalid file type. Please upload MP4, AVI, MOV, or MKV');
      return;
    }

    if (file.size > 500 * 1024 * 1024) {
      setError('File too large. Maximum size is 500MB');
      return;
    }

    setSelectedFile(file);
    setError(null);
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) processFile(file);
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

  const handleGenerate = async () => {
    if (!selectedFile) return;

    try {
      onVideoSelected();
      
      // Upload video (0-20%)
      onUploadProgress(5, 'Uploading video...');
      const formData = new FormData();
      formData.append('video', selectedFile);
      
      onUploadProgress(10, 'Uploading video...');
      
      const uploadResponse = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
      });
      
      if (!uploadResponse.ok) {
        const errorData = await uploadResponse.json();
        throw new Error(errorData.error || 'Upload failed');
      }
      
      const uploadData = await uploadResponse.json();
      onUploadProgress(20, 'Video uploaded successfully');
      
      // Start simulating progress during backend processing
      let simulatedProgress = 20;
      const progressInterval = setInterval(() => {
        if (simulatedProgress < 90) {
          simulatedProgress += 0.5; // Slower increment for more realistic feel
          
          // Update message based on progress
          let message = 'Processing...';
          if (simulatedProgress < 30) {
            message = 'Loading AI model...';
          } else if (simulatedProgress < 50) {
            message = 'Extracting poses from video...';
          } else if (simulatedProgress < 70) {
            message = 'Analyzing dance patterns...';
          } else if (simulatedProgress < 90) {
            message = 'Generating AI poses...';
          }
          
          onUploadProgress(Math.round(simulatedProgress), message);
        }
      }, 300); // Update every 300ms
      
      // Generate poses (this is the long-running backend operation)
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
      
      clearInterval(progressInterval);
      
      if (!generateResponse.ok) {
        const errorData = await generateResponse.json();
        throw new Error(errorData.error || 'Generation failed');
      }
      
      onUploadProgress(95, 'Finalizing results...');
      
      const poseData = await generateResponse.json();
      
      onUploadProgress(100, 'Complete!');
      
      setTimeout(() => {
        onPoseDataGenerated(poseData);
      }, 800);
      
    } catch (err) {
      setError(err.message);
      onUploadProgress(0, '');
    }
  };

  return (
    <div className="landing-page">
      {/* Animated background */}
      <div className="background-animation">
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
        <div className="gradient-orb orb-3"></div>
      </div>

      {/* Floating particles */}
      <div className="particles">
        {[...Array(20)].map((_, i) => (
          <div key={i} className="particle" style={{
            left: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 5}s`,
            animationDuration: `${5 + Math.random() * 10}s`
          }}></div>
        ))}
      </div>

      <div className="landing-content">
        {/* Hero Section */}
        <div className="hero-section animate-in">
          <h1 className="hero-title">
            <span className="gradient-text">Dance Pose</span>
            <br />
            <span className="gradient-text-alt">AI Generator</span>
          </h1>
          <p className="hero-subtitle">
            Upload your dance video and watch AI predict future movements
          </p>
        </div>

        {/* Upload Card */}
        <div className="upload-card animate-in">
          <div 
            className={`drop-zone ${isDragging ? 'dragging' : ''} ${selectedFile ? 'has-file' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              id="video-input"
              type="file"
              accept="video/mp4,video/avi,video/mov,video/mkv"
              onChange={handleFileSelect}
              className="file-input"
            />
            
            <label htmlFor="video-input" className="drop-zone-content">
              {selectedFile ? (
                <>
                  <div className="file-icon">✓</div>
                  <div className="file-info">
                    <p className="file-name">{selectedFile.name}</p>
                    <p className="file-size">{(selectedFile.size / (1024 * 1024)).toFixed(2)} MB</p>
                  </div>
                  <p className="change-file">Click to change file</p>
                </>
              ) : (
                <>
                  <div className="upload-icon">📹</div>
                  <p className="upload-text">Drag & Drop your video here</p>
                  <p className="upload-subtext">or click to browse</p>
                  <p className="upload-formats">MP4, AVI, MOV, MKV • Max 500MB</p>
                </>
              )}
            </label>
          </div>

          {error && (
            <div className="error-banner">
              <span className="error-icon">⚠️</span>
              {error}
            </div>
          )}

          {/* Settings Toggle */}
          <button 
            className="settings-toggle"
            onClick={() => setShowSettings(!showSettings)}
          >
            <span className="icon">⚙️</span>
            Advanced Settings
            <span className={`arrow ${showSettings ? 'up' : 'down'}`}>▼</span>
          </button>

          {showSettings && (
            <div className="settings-panel">
              <div className="setting-item">
                <label>Frames to Generate</label>
                <div className="slider-container">
                  <input
                    type="range"
                    min="10"
                    max="300"
                    value={numFrames}
                    onChange={(e) => setNumFrames(Number(e.target.value))}
                    className="slider"
                  />
                  <span className="slider-value">{numFrames}</span>
                </div>
                <p className="setting-hint">
                  More frames = longer generation time
                </p>
              </div>
            </div>
          )}

          <button
            className={`generate-button ${selectedFile ? 'active' : ''}`}
            onClick={handleGenerate}
            disabled={!selectedFile}
          >
            <span className="button-icon">🚀</span>
            Generate AI Poses
            <div className="button-shine"></div>
          </button>
        </div>

        {/* Features */}
        <div className="features animate-in">
          <div className="feature">
            <div className="feature-icon">🎯</div>
            <h3>Accurate Tracking</h3>
            <p>33-point pose detection</p>
          </div>
          <div className="feature">
            <div className="feature-icon">🤖</div>
            <h3>AI Prediction</h3>
            <p>ST-GCN neural network</p>
          </div>
          <div className="feature">
            <div className="feature-icon">🎨</div>
            <h3>Dual Visualization</h3>
            <p>2D & 3D rendering</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
