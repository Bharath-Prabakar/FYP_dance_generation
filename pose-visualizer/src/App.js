import React, { useState } from 'react';
import './App.css';
import LandingPage from './components/LandingPage';
import LoadingScreen from './components/LoadingScreen';
import VisualizerPage from './components/VisualizerPage';

function App() {
  const [currentPage, setCurrentPage] = useState('landing'); // 'landing', 'loading', 'visualizer'
  const [poseData, setPoseData] = useState(null);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [loadingMessage, setLoadingMessage] = useState('');

  const handleVideoSelected = () => {
    setCurrentPage('loading');
    setLoadingProgress(0);
    setLoadingMessage('Uploading video...');
  };

  const handleUploadProgress = (progress, message) => {
    setLoadingProgress(progress);
    setLoadingMessage(message);
  };

  const handlePoseDataGenerated = (data) => {
    setPoseData(data);
    setLoadingProgress(100);
    setLoadingMessage('Complete!');
    
    // Smooth transition to visualizer
    setTimeout(() => {
      setCurrentPage('visualizer');
    }, 500);
  };

  const handleBackToHome = () => {
    setCurrentPage('landing');
    setPoseData(null);
    setLoadingProgress(0);
    setLoadingMessage('');
  };

  return (
    <div className="app">
      <div className={`page-container ${currentPage}`}>
        {currentPage === 'landing' && (
          <LandingPage 
            onVideoSelected={handleVideoSelected}
            onUploadProgress={handleUploadProgress}
            onPoseDataGenerated={handlePoseDataGenerated}
          />
        )}
        
        {currentPage === 'loading' && (
          <LoadingScreen 
            progress={loadingProgress}
            message={loadingMessage}
          />
        )}
        
        {currentPage === 'visualizer' && (
          <VisualizerPage 
            poseData={poseData}
            onBackToHome={handleBackToHome}
          />
        )}
      </div>
    </div>
  );
}

export default App;
