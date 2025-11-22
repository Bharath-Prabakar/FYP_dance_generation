@echo off
echo ========================================
echo Dance Pose Visualizer - Full Stack App
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo Installing backend dependencies...
pip install -r requirements_backend.txt
if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)

echo.
echo Installing frontend dependencies...
cd pose-visualizer
if not exist "node_modules\" (
    call npm install --legacy-peer-deps
    if errorlevel 1 (
        echo ERROR: Failed to install frontend dependencies
        cd ..
        pause
        exit /b 1
    )
)
cd ..

echo.
echo ========================================
echo Starting Backend Server (Flask)...
echo ========================================
start "Backend Server" cmd /k "python backend_server.py"

timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo Starting Frontend (React)...
echo ========================================
cd pose-visualizer
start "Frontend Server" cmd /k "npm start"
cd ..

echo.
echo ========================================
echo Both servers are starting!
echo ========================================
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo The browser will open automatically.
echo Close both command windows to stop the servers.
echo ========================================
pause
