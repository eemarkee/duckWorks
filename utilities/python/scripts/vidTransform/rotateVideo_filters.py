import subprocess
import sys
import os
import subprocess
import re

def get_duplicate_frames(input_file, mpdecimate_options="hi=64*32:lo=64*24:frac=0.05"):
    """
    Use FFmpeg with mpdecimate to identify duplicate frames in the input video.
    
    Args:
        input_file (str): Path to the video file.
        mpdecimate_options (str): Options for the mpdecimate filter.
    
    Returns:
        list: List of timestamps or frame numbers to exclude.
    """
    command = [
        "ffmpeg", "-i", input_file, 
        "-vf", f"mpdecimate={mpdecimate_options}", 
        "-loglevel", "debug", 
        "-f", "null", "-"
    ]
    
    result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
    duplicate_frames = []
    
    # Parse FFmpeg output for frame drop information
    for line in result.stderr.splitlines():
        if "drop" in line and "pts_time" in line:
            match = re.search(r"pts_time:(\d+\.\d+)", line)
            if match:
                duplicate_frames.append(float(match.group(1)))
    
    return duplicate_frames

def generate_trim_filter(duplicate_frames, fps):
    """
    Generate a complex FFmpeg trim filter to exclude duplicate frames.

    Args:
        duplicate_frames (list): List of timestamps or frame numbers to exclude.
        fps (float): Frames per second of the input video.

    Returns:
        str: Complex FFmpeg filter string.
    """
    trim_intervals = []
    last_frame = -1  # Initialize to -1 to include frames before the first duplicate.

    # Convert timestamps into intervals
    for frame_time in duplicate_frames:
        frame_number = int(frame_time * fps)
        if frame_number > last_frame + 1:  # Ensure there's a valid interval
            trim_intervals.append(f"between(n,{last_frame+1},{frame_number-1})")
        last_frame = frame_number

    # Add an interval fosr frames after the last duplicate
    if last_frame >= 0:
        trim_intervals.append(f"gte(n,{last_frame+1})")

    if trim_intervals:
        filter_string = "select='" + "+".join(trim_intervals) + "',setpts=N/FRAME_RATE/TB"
        return filter_string
    else:
        return None

    
def get_fps(input_file):
    """
    Retrieves the frames per second (fps) of the input video using FFmpeg.

    Args:
        input_file (str): Path to the video file.

    Returns:
        float: Frames per second (fps) of the video.
    """
    command = [
        "ffmpeg", "-i", input_file, 
        "-hide_banner"
    ]
    result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
    for line in result.stderr.splitlines():
        if "fps" in line:
            parts = line.split(", ")
            for part in parts:
                if "fps" in part:
                    try:
                        return float(part.split()[0])
                    except ValueError:
                        pass
    raise RuntimeError(f"Unable to determine FPS for {input_file}")

def process_video(input_file, direction, encoder="nvidia", crf=28, decimate=True):
    # Get the file directory, name, and extension
    file_dir, file_name = os.path.split(input_file)
    file_root, file_ext = os.path.splitext(file_name)
    output_file = os.path.join(file_dir, f"{file_root}_processed_{direction}{file_ext}")
    
    # Determine FPS dynamically
    fps = get_fps(input_file)
    print(f"Detected FPS: {fps}")
    
    # Set the transpose filter if rotation is required
    transpose_filter = None
    if direction in ["right", "left", "180"]:
        transpose_filter = {
            "right": "transpose=1",
            "left": "transpose=2",
            "180": "transpose=2,transpose=2"
        }[direction]

    # Generate filters
    filters = []
    if transpose_filter:
        filters.append(transpose_filter)
    
    if decimate:
        duplicate_frames = get_duplicate_frames(input_file)
        if duplicate_frames:
            trim_filter = generate_trim_filter(duplicate_frames, fps)
            if trim_filter:
                filters.append(trim_filter)
    
    # Combine filters
    if filters:
        filter_chain = ",".join(filters)
    else:
        filter_chain = None
    
    # Construct FFmpeg command
    command = ["ffmpeg", "-i", input_file]
    if filter_chain:
        command.extend(["-vf", filter_chain])
    
    if encoder == "nvidia":
        command.extend(["-c:v", "hevc_nvenc", "-cq:v", str(crf), "-preset", "medium"])
    elif encoder == "intel":
        command.extend(["-c:v", "hevc_qsv", "-global_quality", str(crf), "-preset", "medium"])
    elif encoder == "sw":
        command.extend(["-c:v", "libx265", "-crf", str(crf), "-preset", "medium"])
    else:
        print("Invalid encoder specified.")
        return

    command.extend(["-acodec", "copy", output_file])
    
    try:
        subprocess.run(command, check=True)
        print(f"Video processed successfully. Output: {output_file}")
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
