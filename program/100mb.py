import os
import subprocess
import json

# Directories
uncompressed_dir = './Uncompressed'
compressed_dir = './Compressed'

# Ensure the compressed directory exists
os.makedirs(compressed_dir, exist_ok=True)

# Target size in bytes (100MB, but making it 99.5 because exactly 10 is apparently not okay for Discord.)
target_size_bytes = 99.5 * 1024 * 1024

def get_video_duration(video_path):
    """Returns the duration of the video in seconds using ffprobe."""
    cmd = [
        'ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'format=duration', '-of', 'json', video_path
    ]
    
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    
    try:
        # Parse the output from ffprobe as JSON
        output = json.loads(result.stdout)
        return float(output['format']['duration'])
    except (ValueError, KeyError):
        print(f"Could not retrieve duration for {video_path}")
        return None

def compress_video(input_path, output_path, target_size_bytes):
    """Compresses the video at input_path to fit within target_size_bytes and saves it to output_path."""
    # Get the duration of the video
    duration = get_video_duration(input_path)
    if not duration:
        return

    # Calculate the target bitrate (bps)
    target_bitrate = (target_size_bytes * 8) / duration  # in bits per second

    # Set the video and audio bitrate to maintain the target size
    video_bitrate = target_bitrate * 0.85  # 85% of bitrate for video
    audio_bitrate = target_bitrate * 0.15  # 15% of bitrate for audio

    # Create ffmpeg command to compress the video
    cmd = [
        'ffmpeg', '-i', input_path,
        '-b:v', f'{int(video_bitrate)}',    # Video bitrate
        '-b:a', f'{int(audio_bitrate)}',    # Audio bitrate
        '-maxrate', f'{int(video_bitrate)}', # Max rate same as video bitrate
        '-bufsize', f'{int(video_bitrate / 2)}', # Buffer size half the bitrate
        '-y', output_path                   # Output file
    ]

    # Run the ffmpeg command
    subprocess.run(cmd)

def process_videos(uncompressed_dir, compressed_dir, target_size_bytes):
    """Process and compress all videos in the uncompressed directory."""
    for file_name in os.listdir(uncompressed_dir):
        input_path = os.path.join(uncompressed_dir, file_name)
        output_path = os.path.join(compressed_dir, file_name)
        
        if os.path.isfile(input_path):
            print(f"Compressing {file_name}...")
            compress_video(input_path, output_path, target_size_bytes)
            print(f"Saved compressed video to {output_path}")

if __name__ == "__main__":
    process_videos(uncompressed_dir, compressed_dir, target_size_bytes)