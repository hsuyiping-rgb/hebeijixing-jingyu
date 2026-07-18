import re
from pathlib import Path

def parse_time(t_str):
    parts = t_str.split(',')
    ms = int(parts[1])
    h, m, s = map(int, parts[0].split(':'))
    return h * 3600 + m * 60 + s + ms / 1000.0

def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds - int(seconds)) * 1000))
    if ms >= 1000:
        s += 1
        ms -= 1000
    if s >= 60:
        m += 1
        s -= 60
    if m >= 60:
        h += 1
        m -= 60
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def load_srt_blocks(srt_path):
    if not srt_path.exists():
        return []
    content = srt_path.read_text(encoding="utf-8")
    raw_blocks = re.split(r'\n\n+', content.strip())
    blocks = []
    for rb in raw_blocks:
        lines = rb.split('\n')
        if len(lines) >= 3:
            num = int(lines[0])
            time_range = lines[1]
            text = '\n'.join(lines[2:])
            start_str, end_str = time_range.split(' --> ')
            blocks.append({
                "num": num,
                "start_str": start_str,
                "end_str": end_str,
                "start": parse_time(start_str),
                "end": parse_time(end_str),
                "text": text
            })
    return blocks

def main():
    output_dir = Path("output")
    srt1_path = output_dir / "subtitles_backup.srt"
    
    # Backup original subtitles.srt (which has part 1 + C9 hallicinations) if not already backed up
    orig_srt = output_dir / "subtitles.srt"
    if orig_srt.exists() and not srt1_path.exists():
        orig_srt.rename(srt1_path)
        print("Backed up original subtitles.srt to subtitles_backup.srt")
    
    if not srt1_path.exists():
        print("Error: subtitles_backup.srt not found.")
        return 1
        
    srt2_path = output_dir / "subtitles2.srt"
    if not srt2_path.exists():
        print("Error: subtitles2.srt not found. Transcription part 2 might still be running.")
        return 1

    blocks1 = load_srt_blocks(srt1_path)
    blocks2 = load_srt_blocks(srt2_path)

    # 1. Truncate blocks1: remove blocks where time >= 00:32:27,000 (1947 seconds)
    # and also remove trailing blocks that contain 'C9'
    limit_time = 1947.0
    filtered_blocks1 = []
    for b in blocks1:
        if b["start"] < limit_time:
            # Check if it is a C9 or repetitive character block
            text_clean = b["text"].strip()
            if text_clean == "C9" or text_clean == "C8" or text_clean == "C1" or text_clean == "C2" or text_clean == "C4" or text_clean == "C5":
                continue
            filtered_blocks1.append(b)

    # 2. Shift blocks2 by 1947.0 seconds (32:27)
    shift_amount = 1947.0
    shifted_blocks2 = []
    for b in blocks2:
        text_clean = b["text"].strip()
        # Avoid any repetitive C9 blocks in part 2 too
        if text_clean == "C9" or text_clean == "C8" or text_clean == "C1" or text_clean == "C2" or text_clean == "C4" or text_clean == "C5":
            continue
        shifted_blocks2.append({
            "start": b["start"] + shift_amount,
            "end": b["end"] + shift_amount,
            "text": b["text"]
        })

    # Combine blocks
    combined_blocks = filtered_blocks1 + shifted_blocks2
    
    # Write combined SRT
    srt_lines = []
    txt_lines = []
    for i, b in enumerate(combined_blocks, 1):
        start_str = format_time(b["start"])
        end_str = format_time(b["end"])
        srt_lines.append(f"{i}\n{start_str} --> {end_str}\n{b['text']}\n")
        txt_lines.append(b["text"].replace('\n', ' '))

    orig_srt.write_text("\n".join(srt_lines), encoding="utf-8")
    (output_dir / "transcript.txt").write_text("\n".join(txt_lines), encoding="utf-8")
    print(f"Successfully merged subtitles into {orig_srt} and transcript into output/transcript.txt")
    print(f"Total merged segments: {len(combined_blocks)}")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
