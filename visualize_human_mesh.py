"""
Create realistic human mesh visualization from pose JSON
Uses PyVista for 3D rendering with smooth human-like appearance

Requirements:
    pip install pyvista numpy pillow tqdm
"""

import json
import numpy as np
import pyvista as pv
from pathlib import Path
from tqdm import tqdm
import os


# MediaPipe Pose connections
MP_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,7),(0,4),(4,5),(5,6),(6,8), # Head/Face
    (9,10),(11,12),(11,13),(13,15),(12,14),(14,16), # Arms
    (15,17),(15,19),(15,21),(16,18),(16,20),(16,22), # Hands
    (23,24),(11,23),(12,24),(23,25),(24,26),(25,27),(26,28), # Torso/Legs
    (27,29),(27,31),(29,31),(28,30),(28,32),(30,32) # Feet
]


def create_human_mesh_from_pose(pose_99d, joint_radius=0.04, bone_radius=0.025):
    """
    Create a realistic 3D human mesh from a 99-D pose vector
    
    Args:
        pose_99d: 99-D pose vector (33 joints × 3 coords)
        joint_radius: Radius of joint spheres
        bone_radius: Radius of bone cylinders
    
    Returns:
        PyVista mesh object
    """
    # Reshape to (33, 3)
    landmarks = pose_99d.reshape(33, 3).copy()
    landmarks[:, 1] = -landmarks[:, 1]  # Invert Y-axis
    
    # Create plotter
    meshes = []
    
    # Create joints (spheres)
    for point in landmarks:
        sphere = pv.Sphere(radius=joint_radius, center=point, theta_resolution=20, phi_resolution=20)
        meshes.append(sphere)
    
    # Create bones (cylinders connecting joints)
    for a, b in MP_CONNECTIONS:
        if a < 33 and b < 33:
            point_a = landmarks[a]
            point_b = landmarks[b]
            
            # Create cylinder between two points
            direction = point_b - point_a
            length = np.linalg.norm(direction)
            
            if length > 0.001:  # Avoid zero-length bones
                center = (point_a + point_b) / 2
                cylinder = pv.Cylinder(
                    center=center,
                    direction=direction,
                    radius=bone_radius,
                    height=length,
                    resolution=16
                )
                meshes.append(cylinder)
    
    # Combine all meshes
    combined_mesh = meshes[0]
    for mesh in meshes[1:]:
        combined_mesh = combined_mesh.merge(mesh)
    
    return combined_mesh


def render_pose_to_image(pose_99d, output_path, camera_position=(0, 0, 3), 
                         window_size=(1920, 1080), background='white'):
    """
    Render a single pose to an image file
    
    Args:
        pose_99d: 99-D pose vector
        output_path: Output image path
        camera_position: Camera position (x, y, z)
        window_size: Image size (width, height)
        background: Background color
    """
    # Create mesh
    mesh = create_human_mesh_from_pose(pose_99d)
    
    # Create plotter
    plotter = pv.Plotter(off_screen=True, window_size=window_size)
    plotter.set_background(background)
    
    # Add mesh with realistic material
    plotter.add_mesh(
        mesh,
        color='#E0AC69',  # Skin tone
        smooth_shading=True,
        ambient=0.3,
        diffuse=0.7,
        specular=0.3,
        specular_power=15
    )
    
    # Set camera
    plotter.camera_position = [
        camera_position,  # Camera location
        (0, 0, 0),        # Focal point
        (0, 1, 0)         # View up direction
    ]
    plotter.camera.zoom(1.5)
    
    # Add lighting for better appearance
    plotter.add_light(pv.Light(position=(2, 2, 2), intensity=0.8))
    plotter.add_light(pv.Light(position=(-2, 2, 2), intensity=0.5))
    
    # Render and save
    plotter.show(screenshot=output_path)
    plotter.close()


def create_video_from_poses(json_path, output_video="dance_animation.mp4", 
                            fps=30, sample_rate=1):
    """
    Create a video animation from all poses in JSON
    
    Args:
        json_path: Path to generated_poses.json
        output_video: Output video file path
        fps: Frames per second
        sample_rate: Sample every Nth frame (1 = all frames)
    """
    # Load poses
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    poses = np.array(data['poses'])
    print(f"Loaded {len(poses)} poses")
    
    # Create temporary directory for frames
    temp_dir = Path("temp_frames")
    temp_dir.mkdir(exist_ok=True)
    
    # Render each frame
    print("Rendering frames...")
    frame_paths = []
    
    for i in tqdm(range(0, len(poses), sample_rate)):
        pose = poses[i]
        frame_path = temp_dir / f"frame_{i:05d}.png"
        render_pose_to_image(pose, str(frame_path))
        frame_paths.append(str(frame_path))
    
    # Create video using ffmpeg (if available)
    try:
        import subprocess
        cmd = [
            'ffmpeg', '-y',
            '-framerate', str(fps),
            '-pattern_type', 'glob',
            '-i', str(temp_dir / 'frame_*.png'),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-crf', '23',
            output_video
        ]
        subprocess.run(cmd, check=True)
        print(f"\n✅ Video saved: {output_video}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("\n⚠️  ffmpeg not found. Frames saved in temp_frames/")
        print("Install ffmpeg to create video: https://ffmpeg.org/download.html")
    
    # Cleanup (optional)
    # import shutil
    # shutil.rmtree(temp_dir)


def create_interactive_viewer(json_path):
    """
    Create an interactive 3D viewer for poses
    
    Args:
        json_path: Path to generated_poses.json
    """
    # Load poses
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    poses = np.array(data['poses'])
    print(f"Loaded {len(poses)} poses")
    
    # Create plotter
    plotter = pv.Plotter()
    plotter.set_background('white')
    
    current_frame = [0]  # Use list to allow modification in callback
    
    def update_pose():
        plotter.clear()
        mesh = create_human_mesh_from_pose(poses[current_frame[0]])
        plotter.add_mesh(
            mesh,
            color='#E0AC69',
            smooth_shading=True,
            ambient=0.3,
            diffuse=0.7,
            specular=0.3
        )
        plotter.add_text(
            f"Frame: {current_frame[0]}/{len(poses)-1}",
            position='upper_left',
            font_size=12
        )
    
    def next_frame():
        current_frame[0] = (current_frame[0] + 1) % len(poses)
        update_pose()
    
    def prev_frame():
        current_frame[0] = (current_frame[0] - 1) % len(poses)
        update_pose()
    
    # Add keyboard controls
    plotter.add_key_event('Right', next_frame)
    plotter.add_key_event('Left', prev_frame)
    plotter.add_key_event('space', next_frame)
    
    # Initial pose
    update_pose()
    
    # Add instructions
    plotter.add_text(
        "Controls: ← → or Space to navigate\nMouse: Rotate/Zoom",
        position='lower_left',
        font_size=10
    )
    
    # Show
    plotter.show()


def export_poses_as_images(json_path, output_dir="pose_images", max_frames=50):
    """
    Export poses as individual high-quality images
    
    Args:
        json_path: Path to generated_poses.json
        output_dir: Output directory for images
        max_frames: Maximum number of frames to export
    """
    # Load poses
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    poses = np.array(data['poses'])
    print(f"Loaded {len(poses)} poses")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Sample frames evenly
    sample_rate = max(1, len(poses) // max_frames)
    
    print(f"Exporting {len(range(0, len(poses), sample_rate))} images...")
    
    for i in tqdm(range(0, len(poses), sample_rate)):
        pose = poses[i]
        img_path = output_path / f"pose_{i:04d}.png"
        render_pose_to_image(
            pose,
            str(img_path),
            window_size=(1920, 1080),
            background='white'
        )
    
    print(f"\n✅ Images saved to: {output_dir}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Visualize dance poses as realistic 3D human mesh")
    parser.add_argument("--json", type=str, default="generated_poses.json", help="Path to JSON file")
    parser.add_argument("--mode", type=str, choices=['interactive', 'video', 'images'], 
                       default='interactive', help="Visualization mode")
    parser.add_argument("--output", type=str, default="output", help="Output path")
    parser.add_argument("--fps", type=int, default=30, help="FPS for video")
    parser.add_argument("--max_frames", type=int, default=50, help="Max frames for image export")
    
    args = parser.parse_args()
    
    print("="*60)
    print("DANCE POSE MESH VISUALIZER")
    print("="*60)
    
    if args.mode == 'interactive':
        print("\nStarting interactive viewer...")
        print("Controls: Arrow keys or Space to navigate")
        create_interactive_viewer(args.json)
    
    elif args.mode == 'video':
        output_video = args.output if args.output.endswith('.mp4') else f"{args.output}.mp4"
        print(f"\nCreating video: {output_video}")
        create_video_from_poses(args.json, output_video, fps=args.fps)
    
    elif args.mode == 'images':
        print(f"\nExporting images to: {args.output}")
        export_poses_as_images(args.json, args.output, max_frames=args.max_frames)
