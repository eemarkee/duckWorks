import os
import sys
import subprocess
import glob
import re

def natural_sort_key(filename):
    """Sorts filenames naturally (e.g., test_1.png, test_2.png, test_10.png)."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', filename)]

def create_video_from_images(image_folder, frame_rate):
    """
    Creates a video from a sequence of images in a given folder.
    Explicitly sorts filenames and uses a text file for FFmpeg input.

    Args:
        image_folder (str): Path to the folder containing images.
        frame_rate (int): Frame rate of the output video.

    Example:
        python3 img2vid.py "C:/Users/marke/OneDrive/Videos/Captures/test_images" 30
    """
    if not os.path.exists(image_folder):
        print(f"Error: Folder '{image_folder}' not found.")
        return

    # Get the folder name to use as the video filename
    video_name = os.path.basename(image_folder)
    video_output = os.path.join(os.path.dirname(image_folder), f"{video_name}.mp4")

    # Detect all image files (supports PNG, JPG, JPEG)
    image_formats = ("png", "jpg", "jpeg", "tiff", "bmp")
    images = sorted(
        [f for f in os.listdir(image_folder) if f.lower().endswith(image_formats)],
        key=natural_sort_key
    )

    if not images:
        print("Error: No valid images found.")
        return

    # Create an input text file for FFmpeg
    input_txt_path = os.path.join(image_folder, "input.txt")
    with open(input_txt_path, "w") as f:
        for img in images:
            f.write(f"file '{os.path.join(image_folder, img).replace(os.sep, '/')}'\n")

    # FFmpeg Configuration
    ffmpeg_bin = "ffmpeg"  # Change to full path if needed (e.g., "C:/ffmpeg/bin/ffmpeg.exe")
    input_options = ["-r", str(frame_rate), "-f", "concat", "-safe", "0", "-i", input_txt_path]
    encoding_options = ["-c:v", "libx264", "-preset", "slow", "-crf", "23", "-pix_fmt", "yuv420p"]
    output_options = ["-r", str(frame_rate), video_output]

    # Combine all parts into the final command
    ffmpeg_cmd = [ffmpeg_bin] + input_options + encoding_options + output_options

    # Run FFmpeg command
    print(f"Creating video '{video_output}' from images in '{image_folder}' at {frame_rate} FPS...")
    subprocess.run(ffmpeg_cmd)

    print(f"Video saved as: {video_output}")

# Handle command-line arguments
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 img2vid.py <image_folder> <frame_rate>")
    else:
        image_folder = sys.argv[1]
        frame_rate = int(sys.argv[2])
        create_video_from_images(image_folder, frame_rate)
