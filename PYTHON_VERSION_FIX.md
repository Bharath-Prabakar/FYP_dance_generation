# Python Version Compatibility Fix

## ⚠️ Issue: MediaPipe Not Available for Python 3.13

MediaPipe (required for pose detection) doesn't support Python 3.13 yet. You need Python 3.8-3.12.

**Your current version**: Python 3.13.5  
**Required version**: Python 3.11 or 3.12 (recommended)

---

## 🔧 Solution Options

### Option 1: Use Python 3.12 (Recommended)

#### Windows - Using Python Installer

1. **Download Python 3.12**:
   - Go to: https://www.python.org/downloads/
   - Download Python 3.12.x (latest 3.12 version)

2. **Install Python 3.12**:
   - Run installer
   - ✅ Check "Add Python 3.12 to PATH"
   - Choose "Customize installation"
   - Install to a different location (e.g., `C:\Python312`)

3. **Create Virtual Environment with Python 3.12**:
   ```cmd
   cd B:\work\Academics_SSN\Final_Year_Project\project-files\kiro_files
   C:\Python312\python.exe -m venv venv312
   venv312\Scripts\activate
   python --version  # Should show Python 3.12.x
   ```

4. **Install Dependencies**:
   ```cmd
   pip install -r requirements_inference.txt
   ```

---

### Option 2: Use Conda/Miniconda (Easier)

#### Install Miniconda

1. **Download Miniconda**:
   - https://docs.conda.io/en/latest/miniconda.html
   - Choose Windows installer

2. **Create Environment with Python 3.12**:
   ```cmd
   conda create -n stgcn python=3.12
   conda activate stgcn
   ```

3. **Install Dependencies**:
   ```cmd
   pip install -r requirements_inference.txt
   ```

---

### Option 3: Quick Fix - Install Compatible Versions Manually

If you want to try with Python 3.13 (experimental):

```cmd
pip install opencv-python-headless
pip install torch torchvision
pip install numpy scikit-learn tqdm

# MediaPipe alternative - build from source (advanced)
# OR wait for official Python 3.13 support
```

**Note**: This won't work without MediaPipe. You'll need to use Python 3.12.

---

## ✅ Recommended Setup (Step-by-Step)

### Using Virtual Environment with Python 3.12

```cmd
# 1. Install Python 3.12 from python.org
# 2. Navigate to your project
cd B:\work\Academics_SSN\Final_Year_Project\project-files\kiro_files

# 3. Create virtual environment with Python 3.12
py -3.12 -m venv venv_stgcn

# 4. Activate virtual environment
venv_stgcn\Scripts\activate

# 5. Verify Python version
python --version
# Should show: Python 3.12.x

# 6. Upgrade pip
python -m pip install --upgrade pip

# 7. Install dependencies
pip install -r requirements_inference.txt

# 8. Verify installation
python test_inference_setup.py
```

---

## 🐍 Using Conda (Recommended for ML Projects)

```cmd
# 1. Install Miniconda from https://docs.conda.io/en/latest/miniconda.html

# 2. Create environment
conda create -n stgcn python=3.12 -y

# 3. Activate environment
conda activate stgcn

# 4. Install dependencies
pip install -r requirements_inference.txt

# 5. Verify installation
python test_inference_setup.py
```

---

## 📋 Verify Your Setup

After installing Python 3.12 and dependencies:

```cmd
# Check Python version
python --version

# Check if MediaPipe is installed
python -c "import mediapipe; print('MediaPipe version:', mediapipe.__version__)"

# Run full validation
python test_inference_setup.py
```

---

## 🔍 Check Available Python Versions

### Windows

```cmd
# List all Python versions
py --list

# Use specific version
py -3.12 --version
py -3.11 --version
```

---

## 💡 Why Python 3.12?

- ✅ Fully supported by MediaPipe
- ✅ Stable and well-tested
- ✅ Compatible with all ML libraries
- ✅ Good performance
- ⚠️ Python 3.13 is too new (released Oct 2024)

---

## 🚀 Quick Start After Fix

Once you have Python 3.12 set up:

```cmd
# Activate your environment
venv_stgcn\Scripts\activate
# OR
conda activate stgcn

# Verify setup
python test_inference_setup.py

# Run inference
python stgcn_inference.py --video_path your_video.mp4
```

---

## 📦 Alternative: Docker (No Python Version Issues)

If you don't want to manage Python versions:

**Create `Dockerfile`**:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements_inference.txt .
RUN pip install --no-cache-dir -r requirements_inference.txt

COPY stgcn_inference.py .
COPY model_outputs/ ./model_outputs/

CMD ["python", "stgcn_inference.py", "--help"]
```

**Build and run**:
```cmd
docker build -t stgcn-inference .
docker run -v "%cd%":/data stgcn-inference python stgcn_inference.py --video_path /data/video.mp4
```

---

## 🆘 Still Having Issues?

### Check Python Installation
```cmd
py --list
python --version
where python
```

### Check pip
```cmd
python -m pip --version
python -m pip list
```

### Clean Install
```cmd
# Remove old virtual environment
rmdir /s venv_stgcn

# Create fresh environment
py -3.12 -m venv venv_stgcn
venv_stgcn\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements_inference.txt
```

---

## 📚 Resources

- Python Downloads: https://www.python.org/downloads/
- Miniconda: https://docs.conda.io/en/latest/miniconda.html
- MediaPipe: https://google.github.io/mediapipe/
- Virtual Environments: https://docs.python.org/3/tutorial/venv.html

---

## ✅ Summary

**Problem**: Python 3.13 is too new for MediaPipe  
**Solution**: Use Python 3.12 or 3.11  
**Best Method**: Create virtual environment with Python 3.12  
**Alternative**: Use Conda or Docker

After switching to Python 3.12, everything will work smoothly! 🎉
