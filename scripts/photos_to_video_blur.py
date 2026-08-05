#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
photos_to_video_blur.py — 將 16:9 橫式照片串成 9:16 直式 Reels，完整保留人物（模糊背景版）。

使用 ffmpeg filter：
1. 將原圖分流為前景與背景。
2. 背景放大至 1080x1920 並套用 boxblur 模糊效果。
3. 前景保持 16:9 完整比例縮放為 1080x608，疊加在模糊背景正中央。
4. 套用溫和的 Ken Burns 推移與淡入淡出轉場。
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

def build_filter(n: int, w: int, h: int, per: float, trans: float,
                 fps: int, kenburns: bool) -> str:
    """組出 filter_complex：模糊背景 + 前景完整比例疊加 + 可選 Ken Burns + xfade 轉場。"""
    frames = max(int(per * fps), 1)
    
    # 前景高 (16:9 比例下，寬 1080 對應的高大約為 608)
    fg_h = int(w * 9 / 16)
    if fg_h % 2 != 0:
        fg_h += 1
    # 置中 y 座標
    overlay_y = (h - fg_h) // 2
    
    segs = []
    for i in range(n):
        # 1. 複製為兩路
        # 2. bg 路：放大裁剪填滿 + 高斯/盒狀模糊
        # 3. fg 路：等比例縮放為 1080x608
        # 4. overlay：把 fg 疊加在 bg 正中央
        base = (
            f"[{i}:v]split[bg{i}][fg{i}];"
            f"[bg{i}]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=40:5[bg_blur{i}];"
            f"[fg{i}]scale={w}:{fg_h},setsar=1[fg_scale{i}];"
            f"[bg_blur{i}][fg_scale{i}]overlay=x=0:y={overlay_y}:shortest=1,fps={fps}"
        )
        
        if kenburns:
            # 整個直式畫面（背景+前景）一起緩慢推移，呼吸感更佳，避免裁切前景人物
            base += (
                f",zoompan=z='min(zoom+0.0005,1.05)':d={frames}:"
                f"s={w}x{h}:fps={fps}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            )
        else:
            base += f",trim=duration={per},setpts=PTS-STARTPTS"
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
    ap = argparse.ArgumentParser(description="橫式照片 → 直式模糊背景完整人物影片")
    ap.add_argument("images", nargs="+", help="照片路徑（依序播放）")
    ap.add_argument("--out", default="reels_blur.mp4")
    ap.add_argument("--total", type=float, default=45.0)
    ap.add_argument("--per", type=float, default=None)
    ap.add_argument("--size", default="1080x1920")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--transition", type=float, default=0.8)
    ap.add_argument("--no-kenburns", action="store_true")
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
    print(f"[social-post-kit] 模糊背景版: {n} 張照片 × 每張 {per:.1f}s，轉場 {trans:.1f}s → 約 {real_total:.1f}s，{w}x{h}")

    filt = build_filter(n, w, h, per, trans, args.fps, not args.no_kenburns)

    cmd = ["ffmpeg", "-y"]
    for p in images:
        cmd += ["-loop", "1", "-t", f"{per:.3f}", "-i", str(p)]

    cmd += ["-filter_complex", filt, "-map", "[vout]"]
    cmd += [
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", str(args.fps),
        "-t", f"{real_total:.3f}", str(args.out),
    ]

    print("[social-post-kit] 執行 ffmpeg 直式模糊版編譯…")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("[錯誤] ffmpeg 失敗。", file=sys.stderr)
        return res.returncode
    print(f"[social-post-kit] 完成：{args.out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
