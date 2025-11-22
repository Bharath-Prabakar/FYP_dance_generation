@echo off
echo ========================================
echo Dance Pose Visualizer - Quick Start
echo ========================================
echo.

cd pose-visualizer

echo Checking if node_modules exists...
if not exist "node_modules\" (
    echo Installing dependencies...
    call npm install
    echo.
)

echo Checking for pose data...
if not exist "public\generated_poses.json" (
    echo Copying generated_poses.json to public folder...
    if exist "..\generated_poses.json" (
        copy "..\generated_poses.json" "public\"
        echo Pose data copied successfully!
    ) else (
        echo WARNING: generated_poses.json not found!
        echo Please run stgcn_inference.py first to generate poses.
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Starting React development server...
echo The app will open in your browser at http://localhost:3000
echo.
echo Press Ctrl+C to stop the server when done.
echo.

call npm start

pause
