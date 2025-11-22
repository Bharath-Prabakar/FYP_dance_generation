"""
Example usage of the ST-GCN inference script
This demonstrates how to use the inference script programmatically
"""

import subprocess
import json
import sys

def run_inference(video_path, model_dir="model_outputs", num_frames=100):
    """
    Run inference on a video file
    
    Args:
        video_path: Path to input video
        model_dir: Directory containing model files
        num_frames: Number of frames to generate
    
    Returns:
        Generated pose sequence as numpy array
    """
    cmd = [
        sys.executable,  # Python interpreter
        "stgcn_inference.py",
        "--video_path", video_path,
        "--model_dir", model_dir,
        "--num_frames", str(num_frames),
        "--output_file", "output_poses.json"
    ]
    
    print("Running inference...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Error running inference:")
        print(result.stderr)
        return None
    
    print(result.stdout)
    
    # Load generated poses
    with open("output_poses.json", 'r') as f:
        data = json.load(f)
    
    return data


if __name__ == "__main__":
    # Example: Generate 50 future frames from a video
    video_path = "path/to/your/dance_video.mp4"
    
    result = run_inference(
        video_path=video_path,
        model_dir="model_outputs",
        num_frames=50
    )
    
    if result:
        print(f"\nGenerated {result['total_frames']} total poses")
        print(f"Seed frames: {result['seed_frames']}")
        print(f"New frames: {result['generated_frames']}")
