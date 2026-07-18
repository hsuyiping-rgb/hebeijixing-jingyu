import subprocess
from pathlib import Path

def main():
    output_dir = Path("output/screenshots")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    video_path = "output/video.mp4"
    if not Path(video_path).exists():
        print(f"Error: {video_path} does not exist.")
        return 1
        
    times = {
        "1": "00:00:10",
        "2": "00:00:25",
        "3": "00:00:50",
        "4": "00:01:20",
        "5": "00:01:55",
        "6": "00:22:45",
        "7": "00:24:50",
        "8": "00:26:35",
        "9": "00:27:34",
        "10": "00:28:30",
        "11": "00:30:17",
        "12": "00:32:40",
        "13": "00:35:00",
        "14": "00:40:00",
        "15": "00:41:30",
        "16": "00:43:00",
        "17": "00:44:30",
        "18": "00:46:00",
        "19": "00:50:00"
    }

    for name, t in times.items():
        dest = output_dir / f"screenshot_{name}.png"
        cmd = [
            "ffmpeg",
            "-y",
            "-ss", t,
            "-i", video_path,
            "-vframes", "1",
            "-q:v", "2",
            str(dest)
        ]
        print(f"Capturing screenshot for slide {name} at {t}...")
        subprocess.run(cmd, capture_output=True)
        if dest.exists():
            print(f"[OK] Captured {dest}")
        else:
            print(f"Failed to capture {dest}")
            
    print("Screenshot capture process finished!")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
