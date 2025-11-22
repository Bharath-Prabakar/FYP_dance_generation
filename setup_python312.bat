@echo off
REM Setup script for ST-GCN Inference with Python 3.12
REM This script helps create a virtual environment with the correct Python version

echo ============================================================
echo ST-GCN Inference - Python 3.12 Setup
echo ============================================================
echo.

REM Check if Python 3.12 is available
echo Checking for Python 3.12...
py -3.12 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.12 not found!
    echo.
    echo Please install Python 3.12 from:
    echo https://www.python.org/downloads/
    echo.
    echo Or use Miniconda:
    echo https://docs.conda.io/en/latest/miniconda.html
    echo.
    echo See PYTHON_VERSION_FIX.md for detailed instructions.
    pause
    exit /b 1
)

echo [OK] Python 3.12 found!
py -3.12 --version
echo.

REM Create virtual environment
echo Creating virtual environment...
if exist venv_stgcn (
    echo [WARNING] venv_stgcn already exists. Delete it? (Y/N)
    set /p confirm=
    if /i "%confirm%"=="Y" (
        echo Removing old environment...
        rmdir /s /q venv_stgcn
    ) else (
        echo Keeping existing environment.
        goto activate
    )
)

py -3.12 -m venv venv_stgcn
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment created!
echo.

:activate
REM Activate virtual environment
echo Activating virtual environment...
call venv_stgcn\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated!
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [OK] pip upgraded!
echo.

REM Install dependencies
echo Installing dependencies from requirements_inference.txt...
echo This may take a few minutes...
pip install -r requirements_inference.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    echo.
    echo Try manually:
    echo   venv_stgcn\Scripts\activate
    echo   pip install -r requirements_inference.txt
    pause
    exit /b 1
)
echo [OK] Dependencies installed!
echo.

REM Verify installation
echo ============================================================
echo Verifying installation...
echo ============================================================
python test_inference_setup.py
echo.

echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo To use the inference script:
echo   1. Activate environment: venv_stgcn\Scripts\activate
echo   2. Run inference: python stgcn_inference.py --video_path your_video.mp4
echo.
echo The virtual environment is currently activated.
echo.
pause
