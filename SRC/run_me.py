import subprocess
import os
import glob
import random

def get_video_duration(file_path):
    """Safely gets duration for Windows 7."""
    try:
        cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{file_path}"'
        output = subprocess.check_output(cmd, shell=True).decode().strip()
        return float(output)
    except:
        return 3600.0 

def process_all_videos():
    video_extensions = ['*.mkv', '*.mp4', '*.avi', '*.mov']
    files_to_process = [f for ext in video_extensions for f in glob.glob(ext) if "shard_" not in f]

    if not files_to_process:
        print("No video files found!")
        return

    output_folder = "output_shards"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for video in files_to_process:
        duration = get_video_duration(video)
        print(f"Processing {video}...")
        
        interval = 59.5
        # We start at a random point in the first 10 seconds to ensure uniqueness
        start_time = random.uniform(0, 10.0)
        count = 1

        while start_time + interval < duration:
            output_name = os.path.join(output_folder, f"shard_{count:03d}.mp4")
            
            # Simplified Mutation Engine: Flip, Zoom, Hue, and Audio Mask
            cmd = (
                f'ffmpeg -ss {start_time} -t {interval} -i "{video}" '
                f'-f lavfi -i "sine=f=100:d=5" '
                f'-filter_complex "[0:v]hflip,scale=iw*1.2:-1,crop=iw/1.2:ih/1.1,hue=h=1[v];'
                f'[0:a][1:a]amix=inputs=2:duration=first:weights=1 0.05[a]" '
                f'-map "[v]" -map "[a]" -c:v libx264 -crf 18 -preset fast "{output_name}" -y'
            )
            
            print(f"-> Generating Shard {count}...")
            subprocess.run(cmd, shell=True)
            
            start_time += interval
            count += 1

if __name__ == "__main__":
    process_all_videos()
