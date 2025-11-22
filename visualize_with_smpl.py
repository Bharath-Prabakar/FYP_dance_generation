"""
Visualize generated poses using SMPL human mesh model
This creates realistic 3D human avatars from your pose JSON data

Requirements:
    pip install smplx trimesh pyrender pillow
    
Download SMPL model:
    https://smpl.is.tue.mpg.de/ (free for research)
"""

import json
import numpy as np
import trimesh
import pyrender
from PIL import Image
import os

try:
    import smplx
    SMPLX_AVAILABLE = True
except ImportError:
    SMPLX_AVAILABLE = False
    print("⚠️  smplx not installed. Install with: pip install smplx")


def mediapipe_to_smpl_pose(pose_99d):
    """
    Convert MediaPipe 33-joint pose to SMPL body pose parameters
    
    Args:
        pose_99d: 99-D pose vector (33 joints × 3 coords)
    
    Returns:
        SMPL pose parameters (body_pose, global_orient)
    """
    # Reshape to (33, 3)
    joints = pose_99d.reshape(33, 3)
    
    # SMPL uses 23 body joints + 1 root
    # This is a simplified mapping - you may need to refine based on your needs
    
    # MediaPipe to SMPL joint mapping (approximate)
    # SMPL joints: pelvis, left_hip, right_hip, spine1, left_knee, right_knee, etc.
    
    # For now, we'll use a simple approach:
    # Extract key body joints and estimate SMPL parameters
    
    # Root position (hip center)
    left_hip = joints[23]
    right_hip = joints[24]
    root_pos = (left_hip + right_hip) / 2.0
    
    # Body pose (simplified - 69 parameters for 23 joints × 3 rotation axes)
    # This is a placeholder - proper conversion requires inverse kinematics
    body_pose = np.zeros(69)
    
    # Global orientation (root rotation)
    global_orient = np.zeros(3)
    
    return body_pose, global_orient, root_pos


def render_smpl_mesh(body_model, body_pose, global_orient, transl, output_path):
    """
    Render SMPL mesh to image
    
    Args:
        body_model: SMPL model
        body_pose: Body pose parameters
        global_orient: Global orientation
        transl: Translation
        output_path: Output image path
    """
    # Generate mesh
    output = body_model(
        body_pose=body_pose,
        global_orient=global_orient,
        transl=transl
    )
    
    vertices = output.vertices.detach().cpu().numpy().squeeze()
    faces = body_model.faces
    
    # Create trimesh object
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    
    # Create pyrender scene
    scene = pyrender.Scene()
    mesh_pyrender = pyrender.Mesh.from_trimesh(mesh, smooth=True)
    scene.add(mesh_pyrender)
    
    # Add lighting
    light = pyrender.DirectionalLight(color=np.ones(3), intensity=3.0)
    scene.add(light, pose=np.eye(4))
    
    # Add camera
    camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0)
    camera_pose = np.array([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 3.0],
        [0.0, 0.0, 0.0, 1.0]
    ])
    scene.add(camera, pose=camera_pose)
    
    # Render
    renderer = pyrender.OffscreenRenderer(800, 800)
    color, depth = renderer.render(scene)
    
    # Save image
    Image.fromarray(color).save(output_path)
    renderer.delete()
    
    print(f"✅ Saved: {output_path}")


def visualize_poses_with_smpl(json_path, smpl_model_path, output_dir="smpl_renders"):
    """
    Main function to visualize poses using SMPL
    
    Args:
        json_path: Path to generated_poses.json
        smpl_model_path: Path to SMPL model files
        output_dir: Output directory for rendered images
    """
    if not SMPLX_AVAILABLE:
        print("❌ smplx library not available")
        return
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load poses
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    poses = np.array(data['poses'])
    print(f"Loaded {len(poses)} poses")
    
    # Load SMPL model
    body_model = smplx.create(
        smpl_model_path,
        model_type='smpl',
        gender='neutral',
        use_face_contour=False,
        ext='pkl'
    )
    
    # Render each pose (or sample every N frames)
    sample_rate = max(1, len(poses) // 50)  # Render max 50 frames
    
    for i in range(0, len(poses), sample_rate):
        pose_99d = poses[i]
        
        # Convert to SMPL parameters
        body_pose, global_orient, transl = mediapipe_to_smpl_pose(pose_99d)
        
        # Convert to torch tensors
        import torch
        body_pose_t = torch.tensor(body_pose, dtype=torch.float32).unsqueeze(0)
        global_orient_t = torch.tensor(global_orient, dtype=torch.float32).unsqueeze(0)
        transl_t = torch.tensor(transl, dtype=torch.float32).unsqueeze(0)
        
        # Render
        output_path = os.path.join(output_dir, f"pose_{i:04d}.png")
        render_smpl_mesh(body_model, body_pose_t, global_orient_t, transl_t, output_path)
    
    print(f"\n✅ Rendered {len(range(0, len(poses), sample_rate))} poses to {output_dir}")


if __name__ == "__main__":
    # Example usage
    json_path = "generated_poses.json"
    smpl_model_path = "path/to/smpl/models"  # Download from https://smpl.is.tue.mpg.de/
    
    visualize_poses_with_smpl(json_path, smpl_model_path)
