from pathlib import Path
import sys
from faster_whisper import WhisperModel


def stamp(seconds: float) -> str:
    millis = round(seconds * 1000)
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    seconds, millis = divmod(millis, 1_000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


model = WhisperModel("medium", device="cpu", compute_type="int8")
for source_name in sys.argv[1:]:
    source = Path(source_name)
    print(f"Transcribing {source.name}", flush=True)
    segments, _ = model.transcribe(str(source), language="ja", beam_size=5)
    entries = []
    text = []
    for index, segment in enumerate(segments, 1):
        line = segment.text.strip()
        if line:
            entries.append(f"{index}\n{stamp(segment.start)} --> {stamp(segment.end)}\n{line}\n")
            text.append(line)
    source.with_suffix(".srt").write_text("\n".join(entries), encoding="utf-8")
    source.with_suffix(".txt").write_text("\n".join(text), encoding="utf-8")
    print(f"Completed {source.name}", flush=True)
