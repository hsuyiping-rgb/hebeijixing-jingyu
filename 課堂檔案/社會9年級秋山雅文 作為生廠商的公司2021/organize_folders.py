import os
import shutil
from pathlib import Path

def main():
    output_dir = Path("output")
    
    # 1. Create target directories
    folders = {
        "簡報": output_dir / "簡報",
        "字幕": output_dir / "字幕",
        "截圖": output_dir / "截圖",
        "繪圖": output_dir / "繪圖",
        "影片": output_dir / "影片"
    }
    
    for name, path in folders.items():
        path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {path}")
        
    # 2. File mappings (src_file -> dest_dir)
    file_moves = {
        # Presentations
        "slides.pptx": "簡報",
        "slides.html": "簡報",
        "slides_copy.pptx": "簡報",
        "slides_copy.html": "簡報",
        
        # Subtitles/Texts
        "subtitles.srt": "字幕",
        "transcript.txt": "字幕",
        "subtitles2.srt": "字幕",
        "transcript2.txt": "字幕",
        "subtitles_backup.srt": "字幕",
        "analysis.txt": "字幕",
        "concept.txt": "字幕",
        
        # Videos
        "video.mp4": "影片",
        "audio.mp3": "影片",
        "audio2.mp3": "影片",
        "temp_video1.mp4": "影片",
        "temp_video2.mp4": "影片",
        
        # Sharing image
        "concept_post.png": "繪圖"
    }
    
    for filename, folder_name in file_moves.items():
        src = output_dir / filename
        dest_dir = folders[folder_name]
        if src.exists():
            dest = dest_dir / filename
            try:
                shutil.move(str(src), str(dest))
                print(f"Moved {src} to {dest}")
            except Exception as e:
                print(f"Error moving {src}: {e}")
                
    # 3. Move images (from output/images/ to output/繪圖/)
    src_images = output_dir / "images"
    if src_images.exists():
        for f in src_images.glob("*"):
            if f.is_file():
                dest = folders["繪圖"] / f.name
                try:
                    shutil.move(str(f), str(dest))
                    print(f"Moved {f} to {dest}")
                except Exception as e:
                    print(f"Error moving image {f}: {e}")
        try:
            src_images.rmdir()
            print("Removed empty images folder")
        except Exception as e:
            print(f"Could not remove images folder: {e}")
            
    # 4. Move screenshots (from output/screenshots/ to output/截圖/)
    src_screenshots = output_dir / "screenshots"
    if src_screenshots.exists():
        for f in src_screenshots.glob("*"):
            if f.is_file():
                dest = folders["截圖"] / f.name
                try:
                    shutil.move(str(f), str(dest))
                    print(f"Moved {f} to {dest}")
                except Exception as e:
                    print(f"Error moving screenshot {f}: {e}")
        try:
            src_screenshots.rmdir()
            print("Removed empty screenshots folder")
        except Exception as e:
            print(f"Could not remove screenshots folder: {e}")
            
    print("Folders organization completed!")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
