"""
Test script to validate inference setup
Checks if all required files and dependencies are available
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed"""
    print("Checking dependencies...")
    required = ['cv2', 'numpy', 'torch', 'mediapipe', 'tqdm', 'sklearn']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
            print(f"  ✅ {pkg}")
        except ImportError:
            print(f"  ❌ {pkg} - NOT INSTALLED")
            missing.append(pkg)
    
    return len(missing) == 0, missing


def check_model_files(model_dir="model_outputs"):
    """Check if required model files exist"""
    print(f"\nChecking model files in '{model_dir}'...")
    model_dir = Path(model_dir)
    
    if not model_dir.exists():
        print(f"  ❌ Model directory not found: {model_dir}")
        return False
    
    required_files = {
        "stgcn_regressor.pth": True,  # Required
        "pca_transformer.pkl": False,  # Optional
        "kmeans_clusters.pkl": False   # Optional
    }
    
    all_required_exist = True
    for filename, is_required in required_files.items():
        filepath = model_dir / filename
        if filepath.exists():
            print(f"  ✅ {filename}")
        else:
            if is_required:
                print(f"  ❌ {filename} - REQUIRED FILE MISSING")
                all_required_exist = False
            else:
                print(f"  ⚠️  {filename} - Optional file not found")
    
    return all_required_exist


def check_inference_script():
    """Check if inference script exists and is valid"""
    print("\nChecking inference script...")
    
    if not os.path.exists("stgcn_inference.py"):
        print("  ❌ stgcn_inference.py not found")
        return False
    
    print("  ✅ stgcn_inference.py exists")
    
    # Try to import it
    try:
        import stgcn_inference
        print("  ✅ Script imports successfully")
        return True
    except Exception as e:
        print(f"  ❌ Import error: {e}")
        return False


def check_cuda():
    """Check CUDA availability"""
    print("\nChecking CUDA availability...")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"  ✅ CUDA available: {torch.cuda.get_device_name(0)}")
            print(f"     PyTorch version: {torch.__version__}")
        else:
            print("  ⚠️  CUDA not available - will use CPU (slower)")
        return True
    except Exception as e:
        print(f"  ❌ Error checking CUDA: {e}")
        return False


def main():
    print("="*60)
    print("ST-GCN INFERENCE SETUP VALIDATION")
    print("="*60)
    
    results = []
    
    # Check dependencies
    deps_ok, missing = check_dependencies()
    results.append(("Dependencies", deps_ok))
    
    # Check model files
    models_ok = check_model_files()
    results.append(("Model Files", models_ok))
    
    # Check inference script
    script_ok = check_inference_script()
    results.append(("Inference Script", script_ok))
    
    # Check CUDA
    cuda_ok = check_cuda()
    results.append(("CUDA", cuda_ok))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    all_ok = True
    for name, status in results:
        if name == "CUDA":  # CUDA is optional
            continue
        status_str = "✅ PASS" if status else "❌ FAIL"
        print(f"{name:20s}: {status_str}")
        if not status:
            all_ok = False
    
    print("="*60)
    
    if all_ok:
        print("\n✅ All checks passed! Ready for inference.")
        print("\nUsage:")
        print("  python stgcn_inference.py --video_path <video_file>")
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        if not deps_ok:
            print("\nInstall missing dependencies:")
            print("  pip install opencv-python-headless mediapipe torch numpy scikit-learn tqdm")
    
    print()
    return all_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
