from __future__ import annotations

import os
import re
import sys
import time
from pathlib import Path
import google.generativeai as genai

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IN = ROOT / "學習共同體課堂影片分析" / "濱之鄉小學脇坂歸晤社會課" / "自動車生產公開課" / "output" / "字幕檔" / "subtitles_ja.srt"
DEFAULT_OUT = ROOT / "學習共同體課堂影片分析" / "濱之鄉小學脇坂歸晤社會課" / "自動車生產公開課" / "output" / "字幕檔" / "subtitles_zh_TW.srt"
DEFAULT_TXT = ROOT / "學習共同體課堂影片分析" / "濱之鄉小學脇坂歸晤社會課" / "自動車生產公開課" / "output" / "逐字稿與報告" / "transcript.txt"

CHUNK_SIZE = 40  # Number of SRT items to translate at once

PROMPT_TEMPLATE = """你是一位精通日中翻譯的專業教育學譯者，特別熟悉佐藤學教授的「學習共同體（Learning Community）」哲學與實踐。
請將以下日文 SRT 字幕翻譯成自然流暢的台灣繁體中文（zh-TW）。

請遵守以下重要規範：
1. 必須嚴格保持原本的 SRT 格式（包含序號、時間軸 `-->` 與換行結構）。
2. 僅翻譯日文內文文字，絕對不要修改、合併、刪除或新增任何時間軸或序號。
3. 專有名詞對照規範：
   - 「脇坂」老師翻譯為「脇坂」老師。
   - 「小長」或「校長」翻譯為「校長」或「校長老師」。
   - 學生姓名：
     * 「江次」 -> 「江次」
     * 「藤田」 -> 「藤田」
     * 「佐々木」 -> 「佐佐木」
     * 「廣瀬」或「廣瀨」 -> 「廣瀨」
     * 「内田」 -> 「內田」
     * 「石井」 -> 「石井」
     * 「陶」或「たお」 -> 「小陶」
   - 學習共同體專有名詞：
     * 「学びの共同体」 -> 「學習共同體」
     * 「ジャンプ」或「ジャンプの課題」 -> 「伸展跳躍」或「伸展跳躍的課題」
     * 「聴き合う」或「傾聴」 -> 「互相傾聽」或「傾聽」
     * 「つなぐ」 -> 「串聯」
     * 「もどす」 -> 「回歸/還原」
     * 「葛藤」或「ジレンマ」 -> 「糾結/兩難」
4. 請直接返回翻譯後的完整 SRT 內容，不要用 markdown 圍欄包裹（不要加上 ```srt 或 ```），也不要包含任何額外的引言、結語或翻譯說明。

【待翻譯日文 SRT】：
{srt_chunk}
"""

def parse_srt(srt_path: Path) -> list[dict]:
    with srt_path.open("r", encoding="utf-8") as f:
        content = f.read()
    
    # Normalize line endings
    content = content.replace("\r\n", "\n")
    
    # Regex to extract blocks
    pattern = r"(\d+)\n(\d{2}:\d{2}:\d{2}[,\.]\d{3}) --> (\d{2}:\d{2}:\d{2}[,\.]\d{3})\n(.*?)(?=\n\n|\Z)"
    matches = re.finditer(pattern, content, re.DOTALL)
    
    blocks = []
    for m in matches:
        blocks.append({
            "number": int(m.group(1)),
            "start": m.group(2),
            "end": m.group(3),
            "text": m.group(4).strip()
        })
    return blocks

def timestamp_to_text(timestamp_str: str) -> str:
    # 00:12:34,567 -> [00:12:34.567]
    return timestamp_str.replace(",", ".")

def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("[Error] GOOGLE_API_KEY or GEMINI_API_KEY environment variable is not set. Please configure it first.")
        sys.exit(1)
    
    srt_in = DEFAULT_IN
    srt_out = DEFAULT_OUT
    txt_out = DEFAULT_TXT

    if not srt_in.exists():
        print(f"[Error] Input SRT file not found: {srt_in}. Please wait for the transcription task to complete.")
        sys.exit(1)

    print(f"Parsing input SRT: {srt_in.name}")
    blocks = parse_srt(srt_in)
    total_blocks = len(blocks)
    print(f"Loaded {total_blocks} subtitle blocks.")

    # Configure Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    translated_blocks = []
    
    # Process in chunks
    for i in range(0, total_blocks, CHUNK_SIZE):
        chunk = blocks[i : i + CHUNK_SIZE]
        print(f"Translating blocks {chunk[0]['number']} to {chunk[-1]['number']} of {total_blocks}...")
        
        # Format SRT chunk
        srt_chunk_text = ""
        for b in chunk:
            srt_chunk_text += f"{b['number']}\n{b['start']} --> {b['end']}\n{b['text']}\n\n"
        
        prompt = PROMPT_TEMPLATE.format(srt_chunk=srt_chunk_text)
        
        retries = 3
        translated_text = ""
        while retries > 0:
            try:
                response = model.generate_content(prompt)
                translated_text = response.text.strip()
                # Clean up any potential markdown wraps
                if translated_text.startswith("```"):
                    translated_text = re.sub(r"^```[a-zA-Z0-9]*\n", "", translated_text)
                    translated_text = re.sub(r"\n```$", "", translated_text)
                
                # Basic check if it has SRT-like content
                if "-->" not in translated_text:
                    raise ValueError("Gemini returned invalid SRT format (no timestamp separator found)")
                break
            except Exception as e:
                retries -= 1
                print(f"  [Warning] Translation failed: {e}. Retrying... ({retries} left)")
                time.sleep(2)
        
        if not translated_text:
            print("  [Error] Failed to translate this chunk. Falling back to original Japanese text.")
            translated_text = srt_chunk_text
            
        translated_blocks.append(translated_text)
        time.sleep(1) # Rate limit courtesy

    # Write output SRT
    print(f"Writing translated subtitles to: {srt_out.name}")
    srt_out.parent.mkdir(parents=True, exist_ok=True)
    
    full_translated_srt = ""
    for chunk_output in translated_blocks:
        full_translated_srt += chunk_output.strip() + "\n\n"
        
    with srt_out.open("w", encoding="utf-8") as out:
        out.write(full_translated_srt)
        
    # Generate clean Chinese transcript
    print(f"Generating clean Chinese transcript to: {txt_out.name}")
    txt_out.parent.mkdir(parents=True, exist_ok=True)
    
    # Parse the translated SRT again to write transcript.txt
    try:
        translated_content = full_translated_srt.replace("\r\n", "\n")
        pattern = r"(\d+)\n(\d{2}:\d{2}:\d{2}[,\.]\d{3}) --> (\d{2}:\d{2}:\d{2}[,\.]\d{3})\n(.*?)(?=\n\n|\Z)"
        matches = re.finditer(pattern, translated_content, re.DOTALL)
        
        with txt_out.open("w", encoding="utf-8") as text_f:
            text_f.write("濱之鄉小學脇坂歸晤社會課《自動車生產公開課》中文逐字稿\n\n")
            for m in matches:
                start_t = timestamp_to_text(m.group(2))
                text_content = m.group(4).strip().replace("\n", " ")
                text_f.write(f"[{start_t}] {text_content}\n")
    except Exception as e:
        print(f"[Warning] Failed to generate clean transcript: {e}")
            
    print("[OK] SRT Translation and Transcript generation finished successfully.")

if __name__ == "__main__":
    main()
