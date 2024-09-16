# Copyright (c) 2024 Strawberry Software
# Licensed under the GNU General Public License

import os
import subprocess
import json

presets = [
    8,
    10,
    25,
    50,
    100,
    8 # Preset option!
]

welcome_text ="""
Thank you for using my Python Video Compressor.
While it is meant for Discord, and the presets are targeted at Discord File Sizes, it can be used for any kind of video compression to fit under almost any size.
The speed of the conversion is determined by your hardware - the better the hardware the faster it will be done. Please not that this does not change the speed of the video(s).\n
Created by Strawberry Software (C)2024
"""

print(welcome_text)

sizechooser = input("Choose the targeted maximum size:\n(1) 8 mb - Default, will be chosen if input is empty or otherwise unrecognized.\n(2) 10 mb\n(3) 25 mb\n(4) 50 mb\n(5) 100 mb\n(6) Custom\n\nInput: ")

try:
    sizechooser = float(sizechooser)  # Try converting to a float
    if sizechooser < 1 or sizechooser > len(presets):
        raise ValueError()  # Raise an error if the choice is out of range
except (ValueError, TypeError):  # Catch invalid inputs and default to 1
    sizechooser = 1  # Default to the first option (10mb)

if sizechooser == 6:
    custom_size = True
    target_size = float(input("Input your target size in megabytes\nNote: 0.5 will automatically be removed by the program!\n\nInput: "))
else:
    target_size = presets[int(sizechooser) - 1]

# Remove 0.5 mb because Discord is weird about sizes
target_size = target_size - 0.5

# Directories
uncompressed_dir = './Uncompressed'
compressed_dir = './Compressed'

# Ensure the compressed directory exists
os.makedirs(compressed_dir, exist_ok=True)

# Target size in bytes
target_size_bytes = target_size * 1024 * 1024

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

    print("""
###  ###  ###  ###   ##  # #  ###  ##
##    #   # #   #    #   ###  ##   # #
#    ###  # #  ###  ##   # #  ###  ##
Finished!
Your videos have been processed and can be found in .\\Compressed\\
The originals remain in .\\Uncompressed\\
""")