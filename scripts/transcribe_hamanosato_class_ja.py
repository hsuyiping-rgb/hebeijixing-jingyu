from __future__ import annotations

import argparse
from pathlib import Path

from faster_whisper import WhisperModel

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIO = ROOT / "學習共同體課堂影片分析" / "濱之鄉小學脇坂歸晤社會課" / "自動車生產公開課" / "output" / "音檔" / "hamanosato_auto_class_merged.mp3"
OUT_SRT = ROOT / "學習共同體課堂影片分析" / "濱之鄉小學脇坂歸晤社會課" / "自動車生產公開課" / "output" / "字幕檔" / "subtitles_ja.srt"
OUT_TXT = ROOT / "學習共同體課堂影片分析" / "濱之鄉小學脇坂歸晤社會課" / "自動車生產公開課" / "output" / "逐字稿與報告" / "transcript_ja.txt"


def timestamp(seconds: float, srt: bool = False) -> str:
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    secs, milliseconds = divmod(milliseconds, 1000)
    separator = "," if srt else "."
    return f"{hours:02d}:{minutes:02d}:{secs:02d}{separator}{milliseconds:03d}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_AUDIO)
    parser.add_argument("--srt", type=Path, default=OUT_SRT)
    parser.add_argument("--transcript", type=Path, default=OUT_TXT)
    parser.add_argument("--offset", type=float, default=0.0)
    parser.add_argument("--model", default="medium")
    args = parser.parse_args()

    args.srt.parent.mkdir(parents=True, exist_ok=True)
    args.transcript.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading Whisper model: {args.model}")
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    
    print(f"Transcribing audio: {args.input}")
    segments, info = model.transcribe(
        str(args.input),
        language="ja",
        beam_size=5,
        vad_filter=True,
        condition_on_previous_text=True,
    )
    
    items = list(segments)
    print(f"Saving SRT to {args.srt}")
    with args.srt.open("w", encoding="utf-8") as srt:
        for number, segment in enumerate(items, 1):
            srt.write(
                f"{number}\n"
                f"{timestamp(segment.start + args.offset, True)} --> {timestamp(segment.end + args.offset, True)}\n"
                f"{segment.text.strip()}\n\n"
            )
            
    print(f"Saving Transcript to {args.transcript}")
    with args.transcript.open("w", encoding="utf-8") as text:
        text.write(f"語言：{info.language}｜可信度：{info.language_probability:.3f}\n\n")
        for segment in items:
            text.write(f"[{timestamp(segment.start + args.offset)}] {segment.text.strip()}\n")
            
    print(f"Done! language={info.language}; segments={len(items)}")


if __name__ == "__main__":
    main()
