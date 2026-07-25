from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent
IMAGES = ROOT / "images"


def main() -> int:
    missing = []
    bad_ratio = []
    present = []

    for i in range(1, 22):
        path = IMAGES / f"slide_{i}.png"
        if not path.exists():
            missing.append(i)
            continue

        with Image.open(path) as im:
            w, h = im.size
        ratio = w / h
        present.append((i, w, h, path.stat().st_size))
        if abs(ratio - (16 / 9)) > 0.03:
            bad_ratio.append((i, w, h))

    print(f"present={len(present)} missing={missing}")
    for i, w, h, size in present:
        print(f"slide_{i}.png {w}x{h} bytes={size}")

    if bad_ratio:
        print(f"bad_ratio={bad_ratio}")
        return 2
    if missing:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
