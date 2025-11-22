import React, { useEffect, useState } from 'react';
import './LoadingScreen.css';

const LoadingScreen = ({ progress, message }) => {
  const [dots, setDots] = useState('');

  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? '' : prev + '.');
    }, 500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="loading-screen">
      {/* Animated background */}
      <div className="loading-background">
        <div className="loading-orb orb-1"></div>
        <div className="loading-orb orb-2"></div>
        <div className="loading-orb orb-3"></div>
        <div className="loading-orb orb-4"></div>
      </div>

      <div className="loading-content">
        {/* Dancing figure animation */}
        <div className="loading-animation">
          <div className="dancer">
            <div className="dancer-head"></div>
            <div className="dancer-body"></div>
            <div className="dancer-arm left"></div>
            <div className="dancer-arm right"></div>
            <div className="dancer-leg left"></div>
            <div className="dancer-leg right"></div>
          </div>
        </div>

        {/* Progress circle */}
        <div className="progress-circle">
          <svg width="200" height="200">
            <circle
              cx="100"
              cy="100"
              r="90"
              fill="none"
              stroke="rgba(255, 255, 255, 0.1)"
              strokeWidth="8"
            />
            <circle
              cx="100"
              cy="100"
              r="90"
              fill="none"
              stroke="url(#gradient)"
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={`${2 * Math.PI * 90}`}
              strokeDashoffset={`${2 * Math.PI * 90 * (1 - progress / 100)}`}
              transform="rotate(-90 100 100)"
              className="progress-ring"
            />
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#667eea">
                  <animate attributeName="stop-color" 
                    values="#667eea; #f093fb; #4facfe; #43e97b; #667eea" 
                    dur="4s" repeatCount="indefinite" />
                </stop>
                <stop offset="100%" stopColor="#764ba2">
                  <animate attributeName="stop-color" 
                    values="#764ba2; #f5576c; #00f2fe; #38f9d7; #764ba2" 
                    dur="4s" repeatCount="indefinite" />
                </stop>
              </linearGradient>
            </defs>
          </svg>
          <div className="progress-text">
            <span className="progress-number">{Math.round(progress)}%</span>
          </div>
        </div>

        {/* Loading message */}
        <div className="loading-message">
          <h2>{message}{dots}</h2>
          <div className="loading-steps">
            <div className={`step ${progress >= 10 ? 'active' : ''} ${progress >= 30 ? 'complete' : ''}`}>
              <div className="step-icon">📤</div>
              <span>Upload</span>
            </div>
            <div className="step-line"></div>
            <div className={`step ${progress >= 30 ? 'active' : ''} ${progress >= 60 ? 'complete' : ''}`}>
              <div className="step-icon">🎯</div>
              <span>Extract</span>
            </div>
            <div className="step-line"></div>
            <div className={`step ${progress >= 60 ? 'active' : ''} ${progress >= 90 ? 'complete' : ''}`}>
              <div className="step-icon">🤖</div>
              <span>Generate</span>
            </div>
            <div className="step-line"></div>
            <div className={`step ${progress >= 90 ? 'active complete' : ''}`}>
              <div className="step-icon">✨</div>
              <span>Finalize</span>
            </div>
          </div>
        </div>

        {/* Fun facts */}
        <div className="loading-facts">
          <p className="fact">
            {progress < 20 
              ? '💡 Uploading your video to the server...' 
              : progress < 30 
              ? '🧠 Loading ST-GCN neural network model...'
              : progress < 50 
              ? '🎯 Extracting 33-point pose landmarks from video...'
              : progress < 70 
              ? '🤖 AI analyzing dance movement patterns...'
              : progress < 90 
              ? '✨ Generating future dance poses...'
              : '🎉 Finalizing and preparing visualization...'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoadingScreen;
