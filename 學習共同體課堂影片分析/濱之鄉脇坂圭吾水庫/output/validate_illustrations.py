from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
IMAGES = ROOT / "images"
EXTS = (".jpg", ".jpeg", ".png")


def find_slide_image(index: int) -> Path | None:
    for ext in EXTS:
        path = IMAGES / f"slide_{index}{ext}"
        if path.exists():
            return path
    return None


def main() -> int:
    missing = []
    bad_ratio = []
    present = []

    for i in range(1, 22):
        path = find_slide_image(i)
        if path is None:
            missing.append(i)
            continue

        with Image.open(path) as im:
            w, h = im.size
        ratio = w / h
        present.append((i, w, h, path.stat().st_size, path.suffix))
        if abs(ratio - (16 / 9)) > 0.03:
            bad_ratio.append((i, w, h))

    print(f"present={len(present)} missing={missing}")
    for i, w, h, size, suffix in present:
        print(f"slide_{i}{suffix} {w}x{h} bytes={size}")

    if bad_ratio:
        print(f"bad_ratio={bad_ratio}")
        return 2
    if missing:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
