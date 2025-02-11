import subprocess
import sys
import os

def process_video(input_file, direction, encoder="nvidia", crf=28):
    # Get the file directory, name, and extension
    file_dir, file_name = os.path.split(input_file)
    file_root, file_ext = os.path.splitext(file_name)
    output_file = os.path.join(file_dir, f"{file_root}_compressed_{direction}{file_ext}" if direction == "none" else f"{file_root}_rotated_{direction}{file_ext}")
    
    # Configure ffmpeg command based on encoder and direction
    command = None
    if direction in ["right", "left", "180"]:
        # Set the transpose filter based on the rotation direction
        transpose_filter = {
            "right": "transpose=1",  # 90 degrees clockwise
            "left": "transpose=2",   # 90 degrees counterclockwise
            "180": "transpose=2,transpose=2"  # 180 degrees
        }[direction]
    elif direction == "none":
        transpose_filter = None  # No rotation
    else:
        print("Invalid direction specified. Choose 'right', 'left', '180', or 'none'.")
        return

    if encoder == "nvidia":
        # Use NVIDIA's H.265 encoder
        command = [
            "ffmpeg", "-hwaccel", "cuda", "-i", input_file,
            "-c:v", "hevc_nvenc", "-cq:v", str(crf), "-preset", "medium", "-acodec", "copy", output_file
        ]
    elif encoder == "intel":
        # Use Intel's H.265 encoder
        command = [
            "ffmpeg", "-hwaccel", "qsv", "-i", input_file,
            "-c:v", "hevc_qsv", "-global_quality", str(crf), "-preset", "medium", "-acodec", "copy", output_file
        ]
    elif encoder == "sw":
        # Use software-based H.265 encoder
        command = [
            "ffmpeg", "-i", input_file,
            "-c:v", "libx265", "-crf", str(crf), "-preset", "medium", "-acodec", "copy", output_file
        ]
    else:
        print("Invalid encoder specified. Choose 'nvidia', 'intel', or 'sw'.")
        return

    # Add rotation filter if applicable
    if transpose_filter:
        command.insert(-2, "-vf")
        command.insert(-2, transpose_filter)

    try:
        subprocess.run(command, check=True)
        print(f"Video processed successfully with {encoder} encoder at CRF {crf}. Saved as: {output_file}")
    except subprocess.CalledProcessError as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    if len(sys.argv) > 4:
        input_file = sys.argv[1]
        direction = sys.argv[2].lower()  # e.g., "right", "left", "180", or "none"
        encoder = sys.argv[3].lower()    # "nvidia", "intel", or "sw"
        crf = int(sys.argv[4])           # Quality compression value
        if os.path.isfile(input_file) and direction in ["right", "left", "180", "none"]:
            process_video(input_file, direction, encoder=encoder, crf=crf)
        else:
            print("Please provide a valid video file, direction ('right', 'left', '180', or 'none'), encoder (nvidia, intel, or sw), and quality value (CRF).")
    else:
        print("Usage: python rotateVideo.py <input_file> <direction> <encoder> <quality>")
    input("\nPress Enter to close...")
