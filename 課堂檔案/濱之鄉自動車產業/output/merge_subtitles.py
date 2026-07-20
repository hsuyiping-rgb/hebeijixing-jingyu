from pathlib import Path
import re


ROOT = Path(__file__).parent
TIME = re.compile(r"(\d\d):(\d\d):(\d\d),(\d\d\d) --> (\d\d):(\d\d):(\d\d),(\d\d\d)")


def seconds(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def stamp(value):
    millis = round(value * 1000)
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1_000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def parse(path):
    entries = []
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8-sig").strip()):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 3:
            continue
        match = TIME.fullmatch(lines[1])
        if not match:
            continue
        values = match.groups()
        entries.append((seconds(*values[:4]), seconds(*values[4:]), " ".join(lines[2:])))
    return entries


def write(path, entries):
    chunks = []
    for index, (start, end, text) in enumerate(entries, 1):
        chunks.append(f"{index}\n{stamp(start)} --> {stamp(end)}\n{text}\n")
    path.write_text("\n".join(chunks), encoding="utf-8")


spoken = []
for index in range(3):
    for start, end, text in parse(ROOT / "audio_segments" / f"audio_{index:02d}.srt"):
        spoken.append((start + index * 300, end + index * 300, text))
for index in range(6, 20):
    for start, end, text in parse(ROOT / "audio_parts" / f"part_{index:02d}.srt"):
        spoken.append((start + index * 150, end + index * 150, text))
spoken.sort()
write(ROOT / "subtitles.original.multilingual.srt", spoken)

official = parse(ROOT / "subtitles.zh-TW.srt")
bilingual = []
for start, end, text in spoken:
    translations = []
    for chinese_start, chinese_end, chinese_text in official:
        if chinese_end >= start and chinese_start <= end:
            if chinese_text not in translations:
                translations.append(chinese_text)
    if not translations:
        center = (start + end) / 2
        nearest = min(official, key=lambda item: abs(((item[0] + item[1]) / 2) - center))
        if abs(((nearest[0] + nearest[1]) / 2) - center) <= 12:
            translations.append(nearest[2])
    translation = " ".join(translations) if translations else "（未能對齊官方中文譯文）"
    bilingual.append((start, end, f"原語：{text}\n中文：{translation}"))
write(ROOT / "subtitles.bilingual.zh-TW.srt", bilingual)
