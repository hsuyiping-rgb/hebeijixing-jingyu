from __future__ import annotations

import os
import sys
from pathlib import Path
import google.generativeai as genai

OUT_DIR = Path(r"G:\我的雲端硬碟\和北極星境遇\學習共同體課堂影片分析\濱之鄉小學脇坂歸晤社會課\自動車生產議課\output")
SRT_ZH_INTERPRETED = OUT_DIR / "subtitles.zh_TW.srt"
SRT_ZH_DIRECT = OUT_DIR / "subtitles_ja_translated_zh_TW.srt"
REPORT_OUT = OUT_DIR / "translation_comparison_report.md"

PROMPT_TEMPLATE = """你是一位精通教育學、語言學與日中對譯的專業學者，特別專長於佐藤學教授的「學習共同體（Learning Community）」課例研究方法。

請仔細閱讀並對比以下兩份針對同一場 115 分鐘日本濱之鄉小學社會公開課議課影片的字幕文本：
1. 【口譯與解說版繁體中文字幕】（由當天中文同步口譯/解說人員的發音轉譯）：代表口譯人員在現場實時轉譯和說明的內容。
2. 【日文原音直譯版繁體中文字幕】（由影片中原本的日文發音轉譯，並由 AI 直接直譯為繁體中文）：代表影片中日本老師、校長及佐藤學教授真實發言的原汁原味翻譯。

請為本專案撰寫一份學術級的【日文原音直譯 vs 同步口譯解說之差異對比研究報告】。

報告內容需包含：
一、 總體對比與分析 (Executive Summary)：
    - 口譯解說版與日文原音直譯版在語氣、資訊完整度、學術嚴謹度上的主要差異。
    - 分析口譯解說人員是否存在「增譯（加入過多個人主觀詮釋）」、「漏譯（簡化或遺漏重要微觀發言）」或「誤譯（偏離日文發言者原意）」的情形。

二、 經典案例對照表 (Classic Case Studies Table)：
    - 精選至少 10 處最具教育分析價值或差異最顯著的段落，以表格形式進行三欄對照：
      1. 「日文原音直譯中文」
      2. 「同步口譯/解說內容」
      3. 「差異評析與教育學影響（例如該差異是否削弱了學習共同體的核心理念，如互相傾聽、伸展跳躍或課題糾結等）」
    - 案例必須涵蓋授課教師脇坂老師、觀課教師（包含校長、年輕與資深教師的討論）以及佐藤學教授的終極評講。

三、 結論與教育學實踐建議 (Conclusion & Recommendations)：
    - 此次翻譯對比對課例研究的啟示。我們在進行跨國課例研究時，應如何看待同步口譯的局限性？

【口譯與解說版中文字幕片段摘要】：
{zh_interpreted_text}

---

【日文原音直譯版中文字幕片段摘要】：
{zh_direct_text}
"""

def clean_srt(srt_path: Path) -> str:
    """Read srt, strip numbers and timestamps to save context window tokens."""
    with srt_path.open("r", encoding="utf-8") as f:
        content = f.read()
    # Remove timestamps and numbers, keep text
    lines = content.split("\n")
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.isdigit():
            continue
        if "-->" in line:
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

def main() -> None:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("[Error] GOOGLE_API_KEY or GEMINI_API_KEY environment variable is not set.")
        sys.exit(1)
        
    if not SRT_ZH_INTERPRETED.exists():
        print(f"[Error] Interpreted SRT not found: {SRT_ZH_INTERPRETED.name}")
        sys.exit(1)
        
    if not SRT_ZH_DIRECT.exists():
        print(f"[Error] Translated direct SRT not found: {SRT_ZH_DIRECT.name}")
        sys.exit(1)

    print("Reading and cleaning interpreted subtitles...")
    interpreted_txt = clean_srt(SRT_ZH_INTERPRETED)
    
    print("Reading and cleaning direct translated subtitles...")
    direct_txt = clean_srt(SRT_ZH_DIRECT)

    # Let's take samples from start, middle, and end if the file is extremely large,
    # or feed the whole content if tokens fit.
    # 100KB of text is about 30,000 words, which fits well within Gemini's 1M token limit.
    # To keep it extremely focused, we feed the entire cleaned text.
    print(f"Total interpreted chars: {len(interpreted_txt)}, Total direct chars: {len(direct_txt)}")

    # Configure Gemini
    genai.configure(api_key=api_key)
    # Using Pro for deep academic analysis
    model = genai.GenerativeModel("gemini-3.5-flash")

    print("Generating translation comparison report using Gemini Pro...")
    prompt = PROMPT_TEMPLATE.format(
        zh_interpreted_text=interpreted_txt,
        zh_direct_text=direct_txt
    )

    try:
        response = model.generate_content(prompt)
        report_content = response.text.strip()
        
        REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
        with REPORT_OUT.open("w", encoding="utf-8") as out:
            out.write(report_content)
        print(f"[OK] Comparison report generated at: {REPORT_OUT.name}")
    except Exception as e:
        print(f"[Error] Failed to generate comparison report: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
