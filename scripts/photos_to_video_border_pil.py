#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
photos_to_video_border_pil.py — 橫式照片 → 直式 Reels（使用 Pillow 繪製設計邊框 + FFmpeg 動態水平平移）。

解決 Windows FFmpeg Fontconfig error 字型載入崩潰的問題。
工作原理：
1. 用 Pillow 將 16:9 圖片縮放至 2560x1440。
2. 新建 2560x1920 的茶白底圖 (#faf8f5)，將插圖置中貼上。
3. 用 Pillow 內建 ImageFont 繪製頂部與底部精美英文字卡（避開 ffmpeg drawtext 字型問題）。
4. 輸出臨時的 2560x1920 圖片。
5. 調用 FFmpeg 對這 12 張大圖進行 1080x1920 橫移裁切與轉場編譯。
6. 清理臨時大圖。
"""
import os
import shutil
import argparse
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

MIN_TOTAL, MAX_TOTAL = 30, 90

def probe_ok() -> bool:
    for tool in ("ffmpeg", "ffprobe"):
        try:
            subprocess.run([tool, "-version"], capture_output=True, check=True)
        except (OSError, subprocess.CalledProcessError):
            print(f"[錯誤] 找不到 {tool}，請確認 ffmpeg 已安裝並在 PATH。", file=sys.stderr)
            return False
    return True

def create_bordered_images(images: list, temp_dir: Path):
    """使用 Pillow 為 12 張圖生成 2560x1920 的帶邊框設計圖。"""
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    slide_themes = [
        "SLIDE 1 - CLASS INTRODUCTION AND ORIENTATION",
        "SLIDE 2 - SAFETY AND THE AUTOMOTIVE INDUSTRY",
        "SLIDE 3 - QUALITY CONTROL VS PRODUCTION COST",
        "SLIDE 4 - OUTSOURCING AND DOMESTIC MANUFACTURING",
        "SLIDE 5 - GROUP DISCUSSION AND WAGE ANALYSIS",
        "SLIDE 6 - CONNECTING STUDENT LIFE AND ECONOMY",
        "SLIDE 7 - REALITY OF EXCHANGE RATES AND TARIFFS",
        "SLIDE 8 - AUSTRALIA FACTORY CLOSURE CASE STUDY",
        "SLIDE 9 - CONTEMPLATION AND HARD CORPORATE DECISIONS",
        "SLIDE 10 - CRAFTSMANSHIP VS GLOBAL EXPANSION",
        "SLIDE 11 - INDIVIDUAL REFLECTION AND LEARNING DIARY",
        "SLIDE 12 - TEACHER PROFESSIONAL SELF-REFLECTION"
    ]
    
    # 載入字型
    font_paths = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/segoeuib.ttf"
    ]
    font = None
    for p in font_paths:
        if os.path.exists(p):
            try:
                font = ImageFont.truetype(p, 48)
                print(f"[Pillow] Loaded font: {p}")
                break
            except Exception:
                pass
    if not font:
        font = ImageFont.load_default()
        print("[Pillow] Font not found, using default font.")
        
    processed_paths = []
    for i, p in enumerate(images):
        theme_text = slide_themes[i % len(slide_themes)]
        top_text = "HAMANOSATO ELEMENTARY SCHOOL - LESSON STUDY"
        
        # 1. 建立 2560x1920 茶白底色畫布 (#faf8f5)
        canvas = Image.new("RGB", (2560, 1920), (250, 248, 245))
        
        # 2. 開啟原圖，縮放至 2560x1440
        with Image.open(p) as img:
            img_resized = img.resize((2560, 1440), Image.Resampling.LANCZOS)
            canvas.paste(img_resized, (0, 240))
            
        # 3. 繪製文字
        draw = ImageDraw.Draw(canvas)
        
        # 松針綠色 (#2d5a27 -> RGB (45, 90, 39))
        text_color = (45, 90, 39)
        
        # 頂部文字置中
        try:
            # Pillow 新版支援 textlength
            w_top = draw.textlength(top_text, font=font)
        except AttributeError:
            w_top = font.getbbox(top_text)[2]
        draw.text(((2560 - w_top) / 2, 100), top_text, fill=text_color, font=font)
        
        # 底部文字置中
        try:
            w_bottom = draw.textlength(theme_text, font=font)
        except AttributeError:
            w_bottom = font.getbbox(theme_text)[2]
        draw.text(((2560 - w_bottom) / 2, 1760), theme_text, fill=text_color, font=font)
        
        # 4. 存檔到暫存資料夾
        out_path = temp_dir / f"temp_{i:02d}.jpg"
        canvas.save(out_path, "JPEG", quality=95)
        processed_paths.append(out_path)
        print(f"[Pillow] Created bordered image: {out_path.name}")
        
    return processed_paths

def build_filter(n: int, w: int, h: int, per: float, trans: float, fps: int) -> str:
    """組出 filter_complex：僅處理 2560x1920 大圖的水平平移與轉場。"""
    frames = max(int(per * fps), 1)
    
    pan_directions = [0, 2, 0, 1, 2, 2, 0, 1, 0, 1, 2, 0]
    
    segs = []
    for i in range(n):
        direction = pan_directions[i % len(pan_directions)]
        max_x = 2560 - w  # 2560 - 1080 = 1480
        
        if direction == 0:
            x_expr = f"trunc({max_x}*on/({frames}-1))"
        elif direction == 1:
            x_expr = f"trunc({max_x}*(1-on/({frames}-1)))"
        else:
            x_expr = f"trunc({max_x}/2)"
            
        base = f"[{i}:v]zoompan=z=1.0:d={frames}:s={w}x{h}:fps={fps}:x='{x_expr}':y=0[v{i}]"
        segs.append(base)

    if n == 1:
        return ";".join(segs) + f";[v0]format=yuv420p[vout]"

    # xfade 轉場串接
    chain = segs[:]
    prev = "v0"
    offset = per - trans
    for i in range(1, n):
        out = f"x{i}" if i < n - 1 else "vpre"
        chain.append(
            f"[{prev}][v{i}]xfade=transition=fade:duration={trans}:offset={offset:.3f}[{out}]"
        )
        prev = out
        offset += per - trans
    chain.append("[vpre]format=yuv420p[vout]")
    return ";".join(chain)

def main() -> int:
    ap = argparse.ArgumentParser(description="橫式照片 → 直式設計感留白邊框 Reels 影片")
    ap.add_argument("images", nargs="+", help="照片路徑（依序播放）")
    ap.add_argument("--out", default="reels_border.mp4")
    ap.add_argument("--total", type=float, default=45.0)
    ap.add_argument("--per", type=float, default=None)
    ap.add_argument("--size", default="1080x1920")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--transition", type=float, default=0.8)
    args = ap.parse_args()

    if not probe_ok():
        return 1

    images = [Path(p) for p in args.images]
    missing = [p for p in images if not p.exists()]
    if missing:
        print(f"[錯誤] 找不到照片：{', '.join(str(m) for m in missing)}", file=sys.stderr)
        return 1

    n = len(images)
    w, h = (int(x) for x in args.size.lower().split("x"))
    trans = args.transition

    # 決定每張秒數
    if args.per:
        per = args.per
    else:
        total = min(max(args.total, MIN_TOTAL), MAX_TOTAL)
        per = total / n
        
    if trans >= per:
        trans = max(per * 0.3, 0.2)

    # 1. 執行 Pillow 批次留白圖形與文字繪製
    temp_dir = Path("學習共同體課堂影片分析/濱之鄉小學脇坂歸晤社會課/自動車生產公開課/output/圖片_temp")
    temp_images = create_bordered_images(images, temp_dir)

    real_total = per * n - trans * (n - 1)
    print(f"[social-post-kit] 設計邊框版: {n} 張照片 × 每張 {per:.1f}s，轉場 {trans:.1f}s → 約 {real_total:.1f}s，{w}x{h}")

    filt = build_filter(n, w, h, per, trans, args.fps)

    cmd = ["ffmpeg", "-y"]
    for p in temp_images:
        cmd += ["-loop", "1", "-t", f"{per:.3f}", "-i", str(p)]

    cmd += ["-filter_complex", filt, "-map", "[vout]"]
    cmd += [
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(args.fps),
        "-t", f"{real_total:.3f}", str(args.out),
    ]

    print("[social-post-kit] 執行 ffmpeg 鏡頭平移編譯 (大圖輸入)...")
    res = subprocess.run(cmd)
    
    # 清理臨時資料夾
    try:
        shutil.rmtree(temp_dir)
        print("[Pillow] Cleaned up temporary directory.")
    except Exception as e:
        print(f"[警告] 清理臨時目錄失敗: {e}")

    if res.returncode != 0:
        print("[錯誤] ffmpeg 失敗。", file=sys.stderr)
        return res.returncode
        
    print(f"[social-post-kit] 完成：{args.out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
