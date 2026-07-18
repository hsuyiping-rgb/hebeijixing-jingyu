import os
import subprocess
import sys
from pathlib import Path

def run_cmd(cmd):
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if result.returncode != 0:
        print(f"Error running command: {' '.join(cmd)}")
        print(f"Stdout:\n{result.stdout}")
        print(f"Stderr:\n{result.stderr}")
        return False
    return True

def main():
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    url1 = "https://youtu.be/PK7-TOJLgBQ"
    url2 = "https://youtu.be/jfZ97dLrf_k"
    
    v1_temp = output_dir / "temp_video1.mp4"
    v2_temp = output_dir / "temp_video2.mp4"
    
    print("Downloading Video 1...")
    cmd1 = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "-o", str(v1_temp),
        url1
    ]
    if not run_cmd(cmd1):
        # Fallback to general download if format specifier fails
        cmd1_fallback = ["yt-dlp", "-f", "mp4", "-o", str(v1_temp), url1]
        run_cmd(cmd1_fallback)
        
    print("Downloading Video 2...")
    cmd2 = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "-o", str(v2_temp),
        url2
    ]
    if not run_cmd(cmd2):
        # Fallback to general download if format specifier fails
        cmd2_fallback = ["yt-dlp", "-f", "mp4", "-o", str(v2_temp), url2]
        run_cmd(cmd2_fallback)

    # Check if download succeeded
    if not v1_temp.exists() or not v2_temp.exists():
        print("Error: One or both videos failed to download.", file=sys.stderr)
        return 1

    # Concatenate using ffmpeg
    # We will convert them to TS first or use concat demuxer.
    # To be safe and avoid issues with different parameter sets, we can re-encode them or use concat demuxer.
    # Since they are part of the same class, they should be identical. Let's try concat demuxer first.
    list_path = output_dir / "concat_list.txt"
    # Write absolute paths or relative paths. Using relative paths is safer.
    list_content = f"file 'temp_video1.mp4'\nfile 'temp_video2.mp4'\n"
    list_path.write_text(list_content, encoding="utf-8")
    
    merged_video = output_dir / "video.mp4"
    print("Merging videos using ffmpeg...")
    concat_cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_path),
        "-c", "copy",
        str(merged_video)
    ]
    
    if not run_cmd(concat_cmd):
        print("Concat copy failed. Attempting concat with re-encoding...")
        # Fallback: re-encode to ensure compatibility
        reencode_cmd = [
            "ffmpeg",
            "-y",
            "-i", str(v1_temp),
            "-i", str(v2_temp),
            "-filter_complex", "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[outv][outa]",
            "-map", "[outv]",
            "-map", "[outa]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            str(merged_video)
        ]
        if not run_cmd(reencode_cmd):
            print("Re-encoding concat also failed.", file=sys.stderr)
            return 1

    print("Extracting integrated audio track...")
    audio_path = output_dir / "audio.mp3"
    audio_cmd = [
        "ffmpeg",
        "-y",
        "-i", str(merged_video),
        "-q:a", "0",
        "-map", "a",
        str(audio_path)
    ]
    if run_cmd(audio_cmd):
        print("Audio extraction successful!")
    else:
        print("Failed to extract audio track.", file=sys.stderr)
        return 1

    print("Download and merge complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
