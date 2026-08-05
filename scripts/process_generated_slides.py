import os
import sys
from pathlib import Path
from PIL import Image

# 定義路徑
ARTIFACTS_DIR = Path(r"C:\Users\vm\.gemini\antigravity\brain\70f360c7-0978-425a-a2b4-cc9c95e121fe")
OUTPUT_DIR = Path(r"g:\我的雲端硬碟\和北極星境遇\學習共同體課堂影片分析\濱之鄉小學脇坂歸晤社會課\自動車生產公開課\output\圖片")

def process_image(src_path: Path, dest_path: Path):
    try:
        print(f"Processing {src_path.name} -> {dest_path.name} ...")
        with Image.open(src_path) as img:
            # 轉換為 RGB 格式（如果是 RGBA）
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                # 建立白色背景
                bg = Image.new('RGB', img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[3] if img.mode == 'RGBA' else None)
                img_rgb = bg
            else:
                img_rgb = img.convert('RGB')
            
            # 儲存為 JPEG q90
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            img_rgb.save(dest_path, 'JPEG', quality=90)
            print(f"Successfully saved to {dest_path}")
            return True
    except Exception as e:
        print(f"Error processing {src_path.name}: {e}", file=sys.stderr)
        return False

def main():
    print("Starting slide image process script...")
    
    # 掃描 1 到 12 頁
    processed_count = 0
    for i in range(1, 13):
        png_name = f"slide_{i:02d}.png"
        jpg_name = f"slide_{i:02d}.jpg"
        
        src_file = ARTIFACTS_DIR / png_name
        dest_file = OUTPUT_DIR / jpg_name
        
        # 也支援不帶前導零的檔名 slide_1.png
        src_file_no_zero = ARTIFACTS_DIR / f"slide_{i}.png"
        
        target_src = None
        if src_file.exists():
            target_src = src_file
        elif src_file_no_zero.exists():
            target_src = src_file_no_zero
            
        if target_src:
            success = process_image(target_src, dest_file)
            if success:
                processed_count += 1
                # 刪除原 PNG 以節省空間
                try:
                    os.remove(target_src)
                    print(f"Removed source file {target_src.name}")
                except Exception as e:
                    print(f"Failed to remove {target_src.name}: {e}")
        else:
            print(f"Source file for slide {i} not found, skipping.")
            
    print(f"Process complete. Total processed: {processed_count}/12")

if __name__ == '__main__':
    main()
