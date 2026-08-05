#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
photos_to_video_border.py — 橫式照片 → 直式 Reels（茶白留白設計邊框 + 水平橫搖運鏡）。

設計規格：
1. 輸出直式 1080x1920 影片。
2. 背景為有機茶白色 (0xfaf8f5)。
3. 中間為 1080x1440 的橫搖運鏡插圖（上下各留白 240px 邊框）。
4. 上方留白處加上標題文字 "HAMANOSATO ELEMENTARY SCHOOL - LESSON STUDY"。
5. 下方留白處加上每張投影片專屬的 SLIDE 主題文字與序號。
"""
import argparse
import subprocess
import sys
from pathlib import Path

MIN_TOTAL, MAX_TOTAL = 30, 90

def probe_ok() -> bool:
    for tool in ("ffmpeg", "ffprobe"):
        try:
            subprocess.run([tool, "-version"], capture_output=True, check=True)
        except (OSError, subprocess.CalledProcessError):
            print(f"[錯誤] 找不到 {tool}，請確認 ffmpeg 已安裝並在 PATH。", file=sys.stderr)
            return False
    return True

def build_filter(n: int, w: int, h: int, per: float, trans: float, fps: int) -> str:
    """組出 filter_complex：有機茶白背景 + 1080x1440 平移插圖疊加 + 上下英文標題字卡 + xfade 轉場。"""
    frames = max(int(per * fps), 1)
    
    # 投影片底部的專屬英文主題 (只含字母、空格、減號以防 ffmpeg 解析出錯)
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
    
    # 運鏡方向：0 L->R, 1 R->L, 2 Center
    pan_directions = [0, 2, 0, 1, 2, 2, 0, 1, 0, 1, 2, 0]
    
    # 圖片高度與置中 overlay y 座標
    pic_h = 1440
    overlay_y = (h - pic_h) // 2  # (1920 - 1440) / 2 = 240
    
    segs = []
    for i in range(n):
        direction = pan_directions[i % len(pan_directions)]
        theme_text = slide_themes[i % len(slide_themes)]
        
        # 1. 圖片等比例放大高度到 1440，寬度為 2560
        w_scale = int(pic_h * 16 / 9)
        if w_scale % 2 != 0:
            w_scale += 1
            
        max_x = w_scale - w  # 2560 - 1080 = 1480
        
        if direction == 0:
            x_expr = f"trunc({max_x}*on/({frames}-1))"
        elif direction == 1:
            x_expr = f"trunc({max_x}*(1-on/({frames}-1)))"
        else:
            x_expr = f"trunc({max_x}/2)"
            
        # 2. 組合影像處理鏈
        # color 濾鏡的顏色使用 '#faf8f5' 單引號包住以防解讀錯誤
        # drawtext 的 fontfile 使用 'arial'，ffmpeg 在 Windows 下會自動找到系統字型
        base_pic = f"[{i}:v]scale={w_scale}:{pic_h},setsar=1,fps={fps}"
        base_pic += f",zoompan=z=1.0:d={frames}:s={w}x{pic_h}:fps={fps}:x='{x_expr}':y=0[pic_layer{i}]"
        
        # 使用 drawtext 加上頂部與底部英文字
        slide_filter = (
            f"color=c='#faf8f5':s={w}x{h}:d={per}[bg_layer{i}];"
            f"[bg_layer{i}][pic_layer{i}]overlay=x=0:y={overlay_y}:shortest=1,"
            f"drawtext=text='HAMANOSATO ELEMENTARY SCHOOL - LESSON STUDY':x=(w-text_w)/2:y=100:fontcolor='#2d5a27':fontsize=28:font='Arial',"
            f"drawtext=text='{theme_text}':x=(w-text_w)/2:y=1760:fontcolor='#2d5a27':fontsize=24:font='Arial'[v{i}]"
        )
        
        segs.append(f"{base_pic};{slide_filter}")

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

    real_total = per * n - trans * (n - 1)
    print(f"[social-post-kit] 設計邊框版: {n} 張照片 × 每張 {per:.1f}s，轉場 {trans:.1f}s → 約 {real_total:.1f}s，{w}x{h}")

    filt = build_filter(n, w, h, per, trans, args.fps)

    cmd = ["ffmpeg", "-y"]
    for p in images:
        cmd += ["-loop", "1", "-t", f"{per:.3f}", "-i", str(p)]

    cmd += ["-filter_complex", filt, "-map", "[vout]"]
    cmd += [
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(args.fps),
        "-t", f"{real_total:.3f}", str(args.out),
    ]

    print("[social-post-kit] 執行 ffmpeg 直式設計邊框版編譯…")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("[錯誤] ffmpeg 失敗。", file=sys.stderr)
        return res.returncode
    print(f"[social-post-kit] 完成：{args.out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
