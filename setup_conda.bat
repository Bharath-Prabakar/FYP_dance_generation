@echo off
REM Setup script for ST-GCN Inference using Conda
REM This script creates a conda environment with Python 3.12

echo ============================================================
echo ST-GCN Inference - Conda Setup
echo ============================================================
echo.

REM Check if conda is available
echo Checking for Conda...
conda --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Conda not found!
    echo.
    echo Please install Miniconda from:
    echo https://docs.conda.io/en/latest/miniconda.html
    echo.
    echo After installation, restart this script.
    pause
    exit /b 1
)

echo [OK] Conda found!
conda --version
echo.

REM Check if environment already exists
conda env list | findstr "stgcn" >nul 2>&1
if %errorlevel% equ 0 (
    echo [WARNING] Conda environment 'stgcn' already exists.
    echo Delete and recreate? (Y/N)
    set /p confirm=
    if /i "%confirm%"=="Y" (
        echo Removing old environment...
        conda env remove -n stgcn -y
    ) else (
        echo Using existing environment.
        goto activate
    )
)

REM Create conda environment
echo Creating conda environment with Python 3.12...
conda create -n stgcn python=3.12 -y
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create conda environment
    pause
    exit /b 1
)
echo [OK] Conda environment created!
echo.

:activate
REM Activate conda environment
echo Activating conda environment...
call conda activate stgcn
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate conda environment
    echo.
    echo Try manually:
    echo   conda activate stgcn
    pause
    exit /b 1
)
echo [OK] Conda environment activated!
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
    echo   conda activate stgcn
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
echo   1. Activate environment: conda activate stgcn
echo   2. Run inference: python stgcn_inference.py --video_path your_video.mp4
echo.
echo The conda environment is currently activated.
echo.
echo To deactivate: conda deactivate
echo.
pause
