# ⚠️ READ THIS FIRST - Python Version Issue

## Your Current Situation

**Your Python Version**: 3.13.5  
**Required Version**: 3.8 - 3.12  
**Problem**: MediaPipe (required for pose detection) doesn't support Python 3.13 yet

---

## 🚀 Quick Solutions (Choose One)

### Option 1: Automated Setup with Python 3.12 (Easiest)

**If you have Python 3.12 installed**:
```cmd
setup_python312.bat
```

This script will:
- ✅ Check for Python 3.12
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Verify setup

---

### Option 2: Automated Setup with Conda (Recommended)

**If you have Conda/Miniconda**:
```cmd
setup_conda.bat
```

**Don't have Conda?** Download from: https://docs.conda.io/en/latest/miniconda.html

---

### Option 3: Manual Setup

See detailed instructions in: **`PYTHON_VERSION_FIX.md`**

---

## 📥 Installing Python 3.12

### Method 1: Official Python Installer

1. Go to: https://www.python.org/downloads/
2. Download **Python 3.12.x** (latest 3.12 version)
3. Run installer
4. ✅ Check "Add Python 3.12 to PATH"
5. Install
6. Run: `setup_python312.bat`

### Method 2: Miniconda (Easier for ML projects)

1. Download: https://docs.conda.io/en/latest/miniconda.html
2. Install Miniconda
3. Run: `setup_conda.bat`

---

## ✅ After Setup

Once you have Python 3.12 environment set up:

```cmd
# Activate environment
venv_stgcn\Scripts\activate
# OR
conda activate stgcn

# Verify setup
python test_inference_setup.py

# Run inference
python stgcn_inference.py --video_path your_video.mp4
```

---

## 📋 What You Need

### Required Files (Already Created)
- ✅ `stgcn_inference.py` - Main inference script
- ✅ `model_outputs/stgcn_regressor.pth` - Your trained model
- ✅ `requirements_inference.txt` - Dependencies list

### What You Need to Install
- Python 3.12 (or 3.11)
- Dependencies from `requirements_inference.txt`

---

## 🔧 Troubleshooting

### "Python 3.12 not found"
- Install Python 3.12 from python.org
- OR use Conda: `conda create -n stgcn python=3.12`

### "MediaPipe installation failed"
- Make sure you're using Python 3.12 or earlier
- Check: `python --version`

### "Model file not found"
- Ensure `model_outputs/stgcn_regressor.pth` exists
- This file should be from your training

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **README_FIRST.md** | This file - Start here! |
| **PYTHON_VERSION_FIX.md** | Detailed Python version solutions |
| **QUICK_START.md** | Quick reference guide |
| **INFERENCE_README.md** | Complete user guide |
| **DEPLOYMENT_GUIDE.md** | Web deployment guide |

---

## 🎯 Recommended Path

1. **Install Python 3.12** (or Miniconda)
2. **Run setup script**: `setup_python312.bat` or `setup_conda.bat`
3. **Verify**: `python test_inference_setup.py`
4. **Test**: `python stgcn_inference.py --video_path test_video.mp4`
5. **Deploy**: See `DEPLOYMENT_GUIDE.md`

---

## 💡 Why Not Just Use Python 3.13?

Python 3.13 was released in October 2024 and is very new. Many ML libraries (including MediaPipe) haven't released compatible versions yet. Python 3.12 is stable, well-supported, and works perfectly for this project.

---

## 🆘 Need Help?

1. **Check Python version**: `python --version`
2. **List available Python versions**: `py --list`
3. **Read detailed guide**: `PYTHON_VERSION_FIX.md`
4. **Run validation**: `python test_inference_setup.py`

---

## ✨ Once Setup is Complete

You'll be able to:
- ✅ Process dance videos
- ✅ Generate future poses
- ✅ Deploy as web service
- ✅ Integrate with your application

**Next Steps**: After setup, see `QUICK_START.md` for usage examples!

---

**Let's get you set up!** 🚀

Choose your preferred method above and follow the steps.
