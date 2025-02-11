import subprocess
import sys
import os

def process_video(input_file, direction, encoder="nvidia", crf=28, decimate=False):
    # Get the file directory, name, and extension
    file_dir, file_name = os.path.split(input_file)
    file_root, file_ext = os.path.splitext(file_name)
    output_file = os.path.join(file_dir, f"{file_root}_compressed_{direction}{file_ext}" if direction == "none" else f"{file_root}_rotated_{direction}{file_ext}")
    
    # Set the transpose filter if rotation is required
    transpose_filter = None
    if direction in ["right", "left", "180"]:
        transpose_filter = {
            "right": "transpose=1",  # 90 degrees clockwise
            "left": "transpose=2",   # 90 degrees counterclockwise
            "180": "transpose=2,transpose=2"  # 180 degrees
        }[direction]

    # Base ffmpeg command
    command = ["ffmpeg", "-i", input_file]

    # Build the video filter chain
    filters = []
    if transpose_filter:
        filters.append(transpose_filter)
    
    # Add the duplicate frame removal filter
    if decimate:
        filters.append("mpdecimate,setpts=N/FRAME_RATE/TB") # Note - this fucks up the audio sync!

    # Combine filters
    if filters:
        command.extend(["-vf", ",".join(filters)])
    
    # Add encoding settings based on the specified encoder
    if encoder == "nvidia":
        command.extend(["-c:v", "hevc_nvenc", "-cq:v", str(crf), "-preset", "medium"])
    elif encoder == "intel":
        command.extend(["-c:v", "hevc_qsv", "-global_quality", str(crf), "-preset", "medium"])
    elif encoder == "sw":
        command.extend(["-c:v", "libx265", "-crf", str(crf), "-preset", "medium"])
    else:
        print("Invalid encoder specified. Choose 'nvidia', 'intel', or 'sw'.")
        return

    # Add the audio copy setting and output file
    command.extend(["-acodec", "copy", output_file])

    # Execute the ffmpeg command
    try:
        subprocess.run(command, check=True)
        print(f"Video processed successfully with {encoder} encoder at CRF {crf}. Saved as: {output_file}")
        print(f"FFMPEG Command used: {command} ")
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
