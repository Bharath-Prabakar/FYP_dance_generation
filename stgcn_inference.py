"""
ST-GCN Dance Pose Generation - Standalone Inference Script
===========================================================
This script loads a pre-trained ST-GCN model and generates future dance poses
from a single input video. Designed for real-world deployment (web service).

Usage:
    python stgcn_inference.py --video_path <path_to_video> --model_dir <path_to_model_outputs> --num_frames <frames_to_generate>

Requirements:
    - opencv-python-headless
    - mediapipe
    - torch
    - numpy
    - scikit-learn
    - tqdm
"""

import os
import sys
import argparse
import json
import pickle
from pathlib import Path
from collections import deque

import cv2
import numpy as np
from tqdm import tqdm

# PyTorch
import torch
import torch.nn as nn

# MediaPipe for pose extraction
try:
    import mediapipe as mp
    mp_pose = mp.solutions.pose
    POSE_DETECTOR = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
except Exception as e:
    print(f"Warning: MediaPipe initialization failed: {e}")
    POSE_DETECTOR = None


# ============================================================================
# MODEL ARCHITECTURE DEFINITIONS (Must match training definitions exactly)
# ============================================================================

class TemporalConv(nn.Module):
    """Temporal convolution layer for ST-GCN"""
    def __init__(self, in_channels, out_channels, kernel_size=3, stride=1, padding=1):
        super().__init__()
        self.conv = nn.Conv2d(
            in_channels, out_channels, 
            kernel_size=(kernel_size, 1),
            padding=(padding, 0), 
            stride=(stride, 1)
        )
        self.bn = nn.BatchNorm2d(out_channels)
        self.act = nn.ReLU()

    def forward(self, x):
        return self.act(self.bn(self.conv(x)))


class STBlock(nn.Module):
    """Spatial-Temporal block for ST-GCN"""
    def __init__(self, in_channels, out_channels, kernel_size=3):
        super().__init__()
        self.tconv = TemporalConv(in_channels, out_channels, kernel_size=kernel_size)
        self.sconv = nn.Conv2d(out_channels, out_channels, kernel_size=(1, 1))
        self.bn = nn.BatchNorm2d(out_channels)
        self.act = nn.ReLU()

    def forward(self, x):
        x = self.tconv(x)
        x = self.sconv(x)
        x = self.bn(x)
        return self.act(x)


class STGCNRegressor(nn.Module):
    """ST-GCN Regressor for pose prediction"""
    def __init__(self, in_channels=3, num_joints=33, seq_len=32, hidden_channels=[64, 128, 256]):
        super().__init__()
        self.input_proj = nn.Conv2d(in_channels, hidden_channels[0], kernel_size=(1, 1))
        self.blocks = nn.ModuleList()
        ch_in = hidden_channels[0]
        for h in hidden_channels:
            self.blocks.append(STBlock(ch_in, h))
            ch_in = h
        self.pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(hidden_channels[-1], num_joints * 3)

    def forward(self, x):
        x = self.input_proj(x)
        for b in self.blocks:
            x = b(x)
        x = self.pool(x)
        x = x.view(x.size(0), -1)
        out = self.fc(x)
        return out


# ============================================================================
# VIDEO PREPROCESSING UTILITIES
# ============================================================================

def sample_frames_from_video(video_path, sample_fps):
    """
    Generator to sample frames from a video at a specified FPS.
    
    Args:
        video_path: Path to the video file
        sample_fps: Target frames per second for sampling
        
    Yields:
        (frame_index, timestamp, frame_bgr)
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return
    
    video_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    step = max(1, int(round(video_fps / sample_fps)))
    
    idx = 0
    with tqdm(total=total_frames, desc=f"Processing {os.path.basename(video_path)}") as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if idx % step == 0:
                yield idx, idx / video_fps, frame
            idx += 1
            pbar.update(1)
    
    cap.release()


def extract_pose_landmarks(image_bgr):
    """
    Extracts 33 3D landmarks from a BGR image using MediaPipe.
    
    Args:
        image_bgr: OpenCV BGR image
        
    Returns:
        np.array of shape (33, 3) or None if no pose detected
    """
    if POSE_DETECTOR is None:
        raise RuntimeError("MediaPipe POSE_DETECTOR not initialized")
    
    img_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    results = POSE_DETECTOR.process(img_rgb)
    
    if not results.pose_landmarks:
        return None
    
    landmarks = [[lm.x, lm.y, lm.z] for lm in results.pose_landmarks.landmark]
    return np.array(landmarks, dtype=np.float32)


def normalize_landmarks(landmarks):
    """
    Normalizes 33x3 landmarks based on torso length and hip midpoint.
    
    Normalization steps:
    1. Translation: Center on hip midpoint (average of P23 and P24)
    2. Scale: Normalize by torso length (distance from hip to shoulder midpoint)
    
    Args:
        landmarks: np.array of shape (33, 3)
        
    Returns:
        Flattened 99-D normalized vector or None if invalid
    """
    if landmarks is None:
        return None
    
    # 1. Translation Normalization (Hip Mid-point)
    left_hip = landmarks[23, :]
    right_hip = landmarks[24, :]
    hip_mid = (left_hip + right_hip) / 2.0
    centered = landmarks - hip_mid
    
    # 2. Scale Normalization (Torso Length)
    left_shoulder = landmarks[11, :]
    right_shoulder = landmarks[12, :]
    shoulder_mid = (left_shoulder + right_shoulder) / 2.0
    
    torso_vec = shoulder_mid - hip_mid
    torso_len = np.linalg.norm(torso_vec)
    
    if torso_len < 1e-6:
        torso_len = 1.0  # Avoid division by zero
    
    normalized = (centered / torso_len).flatten()
    return normalized


def get_seed_sequence_from_video(video_path, proc_fps, seq_len):
    """
    Processes a single video and extracts the first seq_len frames as seed sequence.
    
    Args:
        video_path: Path to input video
        proc_fps: Processing frame rate
        seq_len: Number of frames needed for seed sequence
        
    Returns:
        np.array of shape (seq_len, 99) - normalized pose vectors
    """
    frames_vecs = []
    video_name = os.path.basename(video_path)
    print(f"\n{'='*60}")
    print(f"Processing video: {video_name}")
    print(f"{'='*60}")
    
    for f_idx, ts, frame in sample_frames_from_video(video_path, proc_fps):
        lm = extract_pose_landmarks(frame)
        if lm is None:
            continue
        vec99 = normalize_landmarks(lm)
        frames_vecs.append(vec99)
    
    if len(frames_vecs) < seq_len:
        raise ValueError(
            f"Video '{video_name}' has only {len(frames_vecs)} usable frames, "
            f"but requires minimum {seq_len} frames for seed sequence."
        )
    
    seed_sequence = np.stack(frames_vecs[:seq_len], axis=0)
    print(f"✅ Extracted {len(frames_vecs)} frames. Using first {seq_len} as seed.")
    return seed_sequence


# ============================================================================
# MODEL LOADING AND INFERENCE
# ============================================================================

def load_pipeline_models(model_dir):
    """
    Loads all pre-trained models and configuration for inference.
    
    Args:
        model_dir: Directory containing saved model files
        
    Returns:
        (model, pca_model, kmeans_model, config_dict)
    """
    model_dir = Path(model_dir)
    
    # Check for CUDA availability
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n{'='*60}")
    print(f"Loading models from: {model_dir}")
    print(f"Device: {device}")
    print(f"{'='*60}")
    
    try:
        # 1. Load ST-GCN checkpoint (contains model weights + original config)
        stgcn_path = model_dir / "stgcn_regressor.pth"
        if not stgcn_path.exists():
            raise FileNotFoundError(f"Model file not found: {stgcn_path}")
        
        checkpoint = torch.load(str(stgcn_path), map_location=device)
        loaded_cfg = checkpoint['cfg']
        
        print(f"✅ Loaded configuration (seq_len={loaded_cfg['seq_len']})")
        
        # 2. Initialize ST-GCN model with loaded config
        model = STGCNRegressor(
            in_channels=3,
            num_joints=33,
            seq_len=loaded_cfg["seq_len"],
            hidden_channels=[64, 128, 256]
        )
        model.load_state_dict(checkpoint['model_state'])
        model.to(device)
        model.eval()
        print(f"✅ Loaded ST-GCN model: {stgcn_path.name}")
        
        # 3. Load PCA model
        pca_path = model_dir / "pca_transformer.pkl"
        if pca_path.exists():
            with open(pca_path, 'rb') as f:
                pca_model = pickle.load(f)
            print(f"✅ Loaded PCA model: {pca_path.name}")
        else:
            pca_model = None
            print(f"⚠️  PCA model not found (optional)")
        
        # 4. Load K-Means model
        kmeans_path = model_dir / "kmeans_clusters.pkl"
        if kmeans_path.exists():
            with open(kmeans_path, 'rb') as f:
                kmeans_model = pickle.load(f)
            print(f"✅ Loaded K-Means model: {kmeans_path.name}")
        else:
            kmeans_model = None
            print(f"⚠️  K-Means model not found (optional)")
        
        return model, pca_model, kmeans_model, loaded_cfg
    
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        raise


def predict_pose_sequence(model, initial_sequence, num_frames_to_generate, device, seq_len):
    """
    Performs autoregressive prediction to generate future poses.
    
    Args:
        model: Trained STGCNRegressor in eval mode
        initial_sequence: np.array of shape (seq_len, 99) - seed sequence
        num_frames_to_generate: Number of future frames to predict
        device: torch device ('cuda' or 'cpu')
        seq_len: Sequence length used during training
        
    Returns:
        np.array of shape (seq_len + num_frames_to_generate, 99)
    """
    if model is None:
        raise ValueError("Model is None")
    
    # Safety check: ensure device is valid and available
    if device == "cuda" and not torch.cuda.is_available():
        print("⚠️  Warning: CUDA requested but not available. Falling back to CPU.")
        device = "cpu"
    
    print(f"\n{'='*60}")
    print(f"Generating {num_frames_to_generate} future poses...")
    print(f"Using device: {device}")
    print(f"{'='*60}")
    
    # Initialize history with seed sequence
    pose_history = deque(initial_sequence.tolist(), maxlen=seq_len)
    generated_poses = initial_sequence.tolist()
    
    with torch.no_grad():
        for _ in tqdm(range(num_frames_to_generate), desc="Generating poses"):
            # 1. Prepare input: (seq_len, 99) -> (1, 3, seq_len, 33)
            input_array = np.array(list(pose_history), dtype=np.float32)
            
            # Reshape: (seq_len, 99) -> (seq_len, 33, 3)
            input_reshaped = input_array.reshape(seq_len, 33, 3)
            
            # Convert to tensor and permute: (seq_len, 33, 3) -> (3, seq_len, 33)
            input_tensor = torch.from_numpy(input_reshaped).permute(2, 0, 1)
            input_tensor = input_tensor.unsqueeze(0).to(device)  # (1, 3, seq_len, 33)
            
            # 2. Predict next pose
            pred_pose = model(input_tensor).cpu().numpy()[0]  # (99,)
            
            # 3. Update history (autoregressive)
            pose_history.append(pred_pose)
            generated_poses.append(pred_pose)
    
    result = np.array(generated_poses)
    print(f"✅ Generated sequence shape: {result.shape}")
    return result


# ============================================================================
# MAIN INFERENCE PIPELINE
# ============================================================================

def generate_poses_from_video(video_path, model_dir="model_outputs", num_frames=100, proc_fps=4, output_file="generated_poses.json"):
    """
    Main function to generate poses from video (no argparse, for API use)
    
    Args:
        video_path: Path to input video file
        model_dir: Directory containing saved model files
        num_frames: Number of future frames to generate
        proc_fps: Processing frame rate
        output_file: Output JSON file path
        
    Returns:
        dict: Generated pose data
    """
    # Validate inputs
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    if not os.path.exists(model_dir):
        raise FileNotFoundError(f"Model directory not found: {model_dir}")
    
    print("\n" + "="*60)
    print("ST-GCN DANCE POSE GENERATION - INFERENCE")
    print("="*60)
    print(f"Video: {video_path}")
    print(f"Model Directory: {model_dir}")
    print(f"Frames to Generate: {num_frames}")
    print(f"Processing FPS: {proc_fps}")
    print("="*60)
    
    # Step 1: Load models
    model, pca_model, kmeans_model, config = load_pipeline_models(model_dir)
    
    seq_len = config["seq_len"]
    # Always check current CUDA availability (don't trust saved config)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")
    
    # Step 2: Extract seed sequence from video
    seed_sequence = get_seed_sequence_from_video(
        video_path,
        proc_fps,
        seq_len
    )
    
    # Step 3: Generate future poses
    # Ensure device is set correctly (use CPU if CUDA not available)
    inference_device = "cuda" if torch.cuda.is_available() else "cpu"
    generated_sequence = predict_pose_sequence(
        model,
        seed_sequence,
        num_frames,
        inference_device,
        seq_len
    )
    
    # Step 4: Prepare output
    output_data = {
        "video_path": video_path,
        "seed_frames": seq_len,
        "generated_frames": num_frames,
        "total_frames": generated_sequence.shape[0],
        "pose_dimension": 99,
        "poses": generated_sequence.tolist()
    }
    
    # Save to file
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ SUCCESS!")
    print(f"{'='*60}")
    print(f"Total poses generated: {generated_sequence.shape[0]}")
    print(f"Output saved to: {output_file}")
    print(f"{'='*60}\n")
    
    return output_data


def main():
    """Command line interface (optional, for manual testing)"""
    parser = argparse.ArgumentParser(
        description="ST-GCN Dance Pose Generation - Inference Script"
    )
    parser.add_argument(
        "--video_path",
        type=str,
        required=True,
        help="Path to input video file"
    )
    parser.add_argument(
        "--model_dir",
        type=str,
        default="model_outputs",
        help="Directory containing saved model files (default: model_outputs)"
    )
    parser.add_argument(
        "--num_frames",
        type=int,
        default=100,
        help="Number of future frames to generate (default: 100)"
    )
    parser.add_argument(
        "--proc_fps",
        type=int,
        default=4,
        help="Processing frame rate (default: 4)"
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="generated_poses.json",
        help="Output file for generated poses (default: generated_poses.json)"
    )
    
    args = parser.parse_args()
    
    # Call the main function
    generate_poses_from_video(
        video_path=args.video_path,
        model_dir=args.model_dir,
        num_frames=args.num_frames,
        proc_fps=args.proc_fps,
        output_file=args.output_file
    )


if __name__ == "__main__":
    main()
