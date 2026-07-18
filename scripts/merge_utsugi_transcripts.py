"""Merge per-part SRT and transcript files after timestamp-offset transcription."""

from __future__ import annotations

import re
from pathlib import Path


BASE = Path("output/文字稿")
PARTS = [
    "宇津木台語文寫作_20141112_part01",
    "宇津木台語文寫作_20141112_part02",
    "宇津木台語文寫作_20141112_part03",
    "宇津木台語文寫作_20141112_part04",
]
TARGET = "宇津木台語文寫作_20141112_完整課堂"


def merge_srt() -> None:
    blocks: list[str] = []
    for part in PARTS:
        content = (BASE / f"{part}.srt").read_text(encoding="utf-8-sig").strip()
        blocks.extend(re.split(r"\r?\n\r?\n", content))

    normalized: list[str] = []
    for index, block in enumerate(blocks, start=1):
        lines = block.splitlines()
        normalized.append("\n".join([str(index), *lines[1:]]))
    (BASE / f"{TARGET}.srt").write_text("\n\n".join(normalized) + "\n", encoding="utf-8")


def merge_transcript() -> None:
    sections: list[str] = ["# 20141112 宇津木台語文寫作：完整課堂逐字稿", ""]
    for index, part in enumerate(PARTS, start=1):
        content = (BASE / f"{part}_逐字稿.txt").read_text(encoding="utf-8-sig").strip()
        sections.extend([f"## 第 {index} 段", content, ""])
    (BASE / f"{TARGET}_逐字稿.txt").write_text("\n".join(sections), encoding="utf-8")


if __name__ == "__main__":
    merge_srt()
    merge_transcript()
