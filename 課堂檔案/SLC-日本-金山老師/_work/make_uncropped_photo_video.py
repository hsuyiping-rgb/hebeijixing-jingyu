from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: make_uncropped_photo_video.py <image_dir> <out_mp4> <seconds>")
        return 2

    image_dir = Path(sys.argv[1])
    out_mp4 = Path(sys.argv[2])
    total_seconds = float(sys.argv[3])

    images = sorted(
        p for p in image_dir.iterdir()
        if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    )
    if not images:
        raise SystemExit(f"No images found in {image_dir}")

    per = total_seconds / len(images)
    out_mp4.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        frames: list[Path] = []
        for idx, img_path in enumerate(images, start=1):
            with Image.open(img_path) as im:
                im = im.convert("RGB")
                im.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
                canvas = Image.new("RGB", (1920, 1080), (245, 248, 244))
                x = (1920 - im.width) // 2
                y = (1080 - im.height) // 2
                canvas.paste(im, (x, y))
                frame = temp / f"frame_{idx:03d}.jpg"
                canvas.save(frame, quality=95)
                frames.append(frame)

        list_file = temp / "concat.txt"
        lines: list[str] = []
        for frame in frames:
            safe = frame.as_posix().replace("'", "'\\''")
            lines.append(f"file '{safe}'")
            lines.append(f"duration {per:.6f}")
        safe_last = frames[-1].as_posix().replace("'", "'\\''")
        lines.append(f"file '{safe_last}'")
        list_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(list_file),
            "-vf", "fps=30,format=yuv420p",
            "-movflags", "+faststart",
            "-c:v", "libx264",
            "-crf", "18",
            "-preset", "medium",
            str(out_mp4),
        ]
        subprocess.run(cmd, check=True)

    print(out_mp4)
    print(len(images))
    print(f"{per:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
