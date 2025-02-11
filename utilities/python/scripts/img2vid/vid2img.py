import os
import subprocess
import sys

def extract_all_frames(video_path):
    """
    Extracts every frame from a video and saves them in a subfolder next to the video file.

    Args:
        video_path (str): Path to the video file.

    Example:
        python3 vid2img.py 2.mp4
    """
    if not os.path.exists(video_path):
        print(f"Error: File '{video_path}' not found.")
        return

    # Get the directory and filename of the video
    video_dir = os.path.dirname(os.path.abspath(video_path))  # Absolute path
    video_name = os.path.splitext(os.path.basename(video_path))[0]  # Remove extension

    # Create a subfolder in the same directory as the video
    frame_folder = os.path.join(video_dir, video_name)
    os.makedirs(frame_folder, exist_ok=True)

    # Define FFmpeg command to extract every frame
    ffmpeg_cmd = [
        "ffmpeg", "-i", video_path,  # Input video
        os.path.join(frame_folder, f"{video_name}_%06d.png"),  # Output format: example_000001.png
        "-hide_banner", "-loglevel", "info"  # Show processing details
    ]

    # Run FFmpeg command
    print(f"Extracting frames from '{video_path}' to '{frame_folder}'...")
    subprocess.run(ffmpeg_cmd)

    print(f"Extraction complete. Frames saved in: {frame_folder}")

# Handle command-line arguments
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 vid2img.py <video_file>")
    else:
        extract_all_frames(sys.argv[1])
