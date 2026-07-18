from __future__ import annotations

import argparse
from pathlib import Path

from faster_whisper import WhisperModel


ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "output" / "影音" / "宇津木台語文寫作_20141112" / "宇津木台語文寫作_完整課堂_音訊.mp3"
OUT = ROOT / "output" / "文字稿"
SRT = OUT / "宇津木台語文寫作_20141112_完整課堂.srt"
TEXT = OUT / "宇津木台語文寫作_20141112_完整課堂_逐字稿.txt"


def timestamp(seconds: float, srt: bool = False) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    secs, milliseconds = divmod(milliseconds, 1000)
    separator = "," if srt else "."
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{milliseconds:03d}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=AUDIO)
    parser.add_argument("--srt", type=Path, default=SRT)
    parser.add_argument("--transcript", type=Path, default=TEXT)
    parser.add_argument("--offset", type=float, default=0.0)
    parser.add_argument("--model", default="small")
    args = parser.parse_args()
    args.srt.parent.mkdir(parents=True, exist_ok=True)
    args.transcript.parent.mkdir(parents=True, exist_ok=True)
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        str(args.input),
        language="ja",
        beam_size=5,
        vad_filter=True,
        condition_on_previous_text=True,
    )
    items = list(segments)
    with args.srt.open("w", encoding="utf-8") as srt:
        for number, segment in enumerate(items, 1):
            srt.write(f"{number}\n{timestamp(segment.start + args.offset, True)} --> {timestamp(segment.end + args.offset, True)}\n{segment.text.strip()}\n\n")
    with args.transcript.open("w", encoding="utf-8") as text:
        text.write(f"語言：{info.language}｜可信度：{info.language_probability:.3f}\n\n")
        for segment in items:
            text.write(f"[{timestamp(segment.start + args.offset)} - {timestamp(segment.end + args.offset)}] {segment.text.strip()}\n")
    print(f"language={info.language}; segments={len(items)}")
    print(args.srt)
    print(args.transcript)


if __name__ == "__main__":
    main()
