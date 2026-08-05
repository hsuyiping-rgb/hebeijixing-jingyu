import os
import sys
from pathlib import Path
from PIL import Image

# 定義路徑
INPUT_DIR = Path(r"g:\我的雲端硬碟\和北極星境遇\學習共同體課堂影片分析\濱之鄉小學脇坂歸晤社會課\自動車生產公開課\output\圖片")
OUTPUT_IMAGES_DIR = Path(r"g:\我的雲端硬碟\和北極星境遇\學習共同體課堂影片分析\濱之鄉小學脇坂歸晤社會課\自動車生產公開課\output\images")
OUTPUT_SLIDES_IMAGES_DIR = Path(r"g:\我的雲端硬碟\和北極星境遇\學習共同體課堂影片分析\濱之鄉小學脇坂歸晤社會課\自動車生產公開課\output\簡報\images")

def main():
    print("Starting deploy_slides_images.py ...")
    
    # 建立輸出目錄
    OUTPUT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_SLIDES_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    
    deployed_count = 0
    # 12 張投影片，對應 slide_1.png 到 slide_12.png
    for i in range(1, 13):
        jpg_name = f"slide_{i:02d}.jpg" # 來源是有前導零的 slide_01.jpg
        src_path = INPUT_DIR / jpg_name
        
        # 套版工具要找的是沒有前導零的 slide_1.png
        dest_name = f"slide_{i}.png"
        dest_path_1 = OUTPUT_IMAGES_DIR / dest_name
        dest_path_2 = OUTPUT_SLIDES_IMAGES_DIR / dest_name
        
        if src_path.exists():
            try:
                with Image.open(src_path) as img:
                    # 另存為 PNG
                    img.save(dest_path_1, "PNG")
                    img.save(dest_path_2, "PNG")
                print(f"Deployed {jpg_name} -> {dest_name} in both output folders.")
                deployed_count += 1
            except Exception as e:
                print(f"Error deploying {jpg_name}: {e}", file=sys.stderr)
        else:
            print(f"Source file {src_path} not found!")
            
    print(f"Deployment complete. Deployed: {deployed_count}/12")

if __name__ == '__main__':
    main()
