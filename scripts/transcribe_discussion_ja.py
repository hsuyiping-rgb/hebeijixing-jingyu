from __future__ import annotations

import argparse
from pathlib import Path
import sys
from faster_whisper import WhisperModel

VIDEO = Path(r"G:\我的雲端硬碟\和北極星境遇\學習共同體課堂影片分析\濱之鄉小學脇坂歸晤社會課\自動車生產議課\output\hamanosato_wakisaka_social_discussion_20141114_merged_720p.mp4")
OUT_DIR = Path(r"G:\我的雲端硬碟\和北極星境遇\學習共同體課堂影片分析\濱之鄉小學脇坂歸晤社會課\自動車生產議課\output")
SRT_OUT = OUT_DIR / "subtitles_ja.srt"
TEXT_OUT = OUT_DIR / "transcript_ja.txt"

def timestamp(seconds: float, srt: bool = False) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    secs, milliseconds = divmod(milliseconds, 1000)
    separator = "," if srt else "."
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{milliseconds:03d}"

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=VIDEO)
    parser.add_argument("--srt", type=Path, default=SRT_OUT)
    parser.add_argument("--transcript", type=Path, default=TEXT_OUT)
    parser.add_argument("--model", default="medium")
    args = parser.parse_args()

    args.srt.parent.mkdir(parents=True, exist_ok=True)
    args.transcript.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading Whisper model '{args.model}' on CPU...")
    # Int8 computation is faster and consumes less RAM
    model = WhisperModel(args.model, device="cpu", compute_type="int8")

    print(f"Transcribing audio in Japanese from: {args.input.name}")
    # Force language="ja" to ignore Chinese overrides and capture original Japanese audio
    segments, info = model.transcribe(
        str(args.input),
        language="ja",
        beam_size=5,
        vad_filter=True,
        condition_on_previous_text=True,
    )

    print(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
    
    items = list(segments)
    
    print(f"Writing subtitles to: {args.srt.name}")
    with args.srt.open("w", encoding="utf-8") as srt:
        for number, segment in enumerate(items, 1):
            text = segment.text.strip()
            srt.write(f"{number}\n{timestamp(segment.start, True)} --> {timestamp(segment.end, True)}\n{text}\n\n")

    print(f"Writing transcript to: {args.transcript.name}")
    with args.transcript.open("w", encoding="utf-8") as text:
        text.write(f"語言：{info.language}｜可信度：{info.language_probability:.3f}｜總句數：{len(items)}\n\n")
        for segment in items:
            text.write(f"[{timestamp(segment.start)} - {timestamp(segment.end)}] {segment.text.strip()}\n")

    print("[OK] Transcription finished successfully.")

if __name__ == "__main__":
    main()
