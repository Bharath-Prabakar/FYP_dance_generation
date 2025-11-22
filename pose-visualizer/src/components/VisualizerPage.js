import React, { useState } from 'react';
import './VisualizerPage.css';
import StickFigureViewer from './StickFigureViewer';
import AnimatedHumanViewer from './AnimatedHumanViewer';

const VisualizerPage = ({ poseData, onBackToHome }) => {
  const [viewMode, setViewMode] = useState('stick'); // 'stick' or 'animated'

  return (
    <div className="visualizer-page">
      {/* Header */}
      <header className="visualizer-header">
        <button className="back-button" onClick={onBackToHome}>
          <span className="icon">←</span>
          Back
        </button>
        
        <div className="header-info">
          <h1 className="page-title">Dance Pose Visualization</h1>
          <div className="stats">
            <span className="stat seed">
              <span className="stat-icon">🟢</span>
              Seed: {poseData?.seed_frames || 0}
            </span>
            <span className="stat generated">
              <span className="stat-icon">🟡</span>
              Generated: {poseData?.generated_frames || 0}
            </span>
            <span className="stat total">
              <span className="stat-icon">📊</span>
              Total: {poseData?.total_frames || 0}
            </span>
          </div>
        </div>
      </header>

      {/* Mode Selector */}
      <div className="mode-selector">
        <div className="mode-tabs">
          <button
            className={`mode-tab ${viewMode === 'stick' ? 'active' : ''}`}
            onClick={() => setViewMode('stick')}
          >
            <span className="tab-icon">🦴</span>
            <span className="tab-label">Stick Figure</span>
            <span className="tab-description">2D Skeleton View</span>
          </button>
          
          <button
            className={`mode-tab ${viewMode === 'animated' ? 'active' : ''}`}
            onClick={() => setViewMode('animated')}
          >
            <span className="tab-icon">💃</span>
            <span className="tab-label">Animated Human</span>
            <span className="tab-description">3D Interactive Model</span>
          </button>
        </div>
        
        <div className="mode-indicator" style={{
          transform: viewMode === 'stick' ? 'translateX(0)' : 'translateX(100%)'
        }}></div>
      </div>

      {/* Viewer Container */}
      <div className="viewer-wrapper">
        <div className={`viewer-slide ${viewMode === 'stick' ? 'active' : ''}`}>
          {viewMode === 'stick' && <StickFigureViewer poseData={poseData} />}
        </div>
        <div className={`viewer-slide ${viewMode === 'animated' ? 'active' : ''}`}>
          {viewMode === 'animated' && <AnimatedHumanViewer poseData={poseData} />}
        </div>
      </div>

      {/* Info Panel */}
      <div className="info-panel">
        <div className="info-card">
          <span className="info-icon">ℹ️</span>
          <p>
            {viewMode === 'stick' 
              ? 'Viewing 2D skeleton with 33 pose landmarks. Green frames are from your video, yellow are AI-generated.'
              : 'Viewing 3D humanoid model. Drag to rotate, scroll to zoom, right-click to pan.'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default VisualizerPage;
