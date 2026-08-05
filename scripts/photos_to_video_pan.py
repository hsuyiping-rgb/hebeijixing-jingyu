#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
photos_to_video_pan.py — 將 16:9 橫式照片串成 9:16 直式 Reels，採用 Camera Pan (動態平移橫搖) 效果。

使用 ffmpeg filter：
1. 將 1920x1080 照片縮放為高度 1920 (寬度等比例放大為 3412)。
2. 利用 zoompan 的 X 運算式，在 4 秒內將 1080 寬的可見視窗從左平移到右（或反向），展現 16:9 原圖完整細節。
3. 照片之間套用淡入淡出轉場。
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
    """組出 filter_complex：縮放高度為 1920 + 鏡頭水平平移 (Camera Pan) + xfade 轉場。"""
    frames = max(int(per * fps), 1)
    
    # 定義 12 張圖的運鏡方向：
    # 0: 從左到右, 1: 從右到左, 2: 置中靜止
    pan_directions = [
        0,  # Slide 1: L -> R (老師 -> 學生)
        2,  # Slide 2: Center (父子)
        0,  # Slide 3: L -> R (生產線 -> 老技師)
        1,  # Slide 4: R -> L (小學生地圖討論)
        2,  # Slide 5: Center (小組討論)
        2,  # Slide 6: Center (低頭傾聽)
        0,  # Slide 7: L -> R (匯率卡片 -> 學生)
        1,  # Slide 8: R -> L (地圖 -> 2500人數據)
        0,  # Slide 9: L -> R (辦公室 -> 社長)
        1,  # Slide 10: R -> L (全球地圖 -> 職人打磨)
        2,  # Slide 11: Center (學生寫日記)
        0   # Slide 12: L -> R (黃昏教室 -> 女教師)
    ]
    
    segs = []
    for i in range(n):
        # 取得這張圖的運鏡方向（如果 n > 12 則循環使用）
        direction = pan_directions[i % len(pan_directions)]
        
        # 1. 先等比例放大高度到目標高 h (1920)，寬度等比例放大為 w_scale (3413)
        w_scale = int(h * 16 / 9)
        if w_scale % 2 != 0:
            w_scale += 1
            
        base = f"[{i}:v]scale={w_scale}:{h},setsar=1,fps={fps}"
        
        # 2. X 軸平移公式
        max_x = w_scale - w  # 3412 - 1080 = 2332
        
        if direction == 0:
            # 從左到右 (L -> R)
            x_expr = f"trunc({max_x}*on/({frames}-1))"
        elif direction == 1:
            # 從右到左 (R -> L)
            x_expr = f"trunc({max_x}*(1-on/({frames}-1)))"
        else:
            # 置中靜止 (Center)
            x_expr = f"trunc({max_x}/2)"
            
        # 套用 zoompan，高度不變 (z=1.0)，X 軸平移，輸出為 w x h
        base += f",zoompan=z=1.0:d={frames}:s={w}x{h}:fps={fps}:x='{x_expr}':y=0"
        segs.append(f"{base}[v{i}]")

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
    ap = argparse.ArgumentParser(description="橫式照片 → 直式水平平移 Reels 影片")
    ap.add_argument("images", nargs="+", help="照片路徑（依序播放）")
    ap.add_argument("--out", default="reels_pan.mp4")
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
    print(f"[social-post-kit] 橫搖平移版: {n} 張照片 × 每張 {per:.1f}s，轉場 {trans:.1f}s → 約 {real_total:.1f}s，{w}x{h}")

    filt = build_filter(n, w, h, per, trans, args.fps)

    cmd = ["ffmpeg", "-y"]
    for p in images:
        cmd += ["-loop", "1", "-t", f"{per:.3f}", "-i", str(p)]

    cmd += ["-filter_complex", filt, "-map", "[vout]"]
    cmd += [
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(args.fps),
        "-t", f"{real_total:.3f}", str(args.out),
    ]

    print("[social-post-kit] 執行 ffmpeg 直式鏡頭平移版編譯…")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("[錯誤] ffmpeg 失敗。", file=sys.stderr)
        return res.returncode
    print(f"[social-post-kit] 完成：{args.out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
