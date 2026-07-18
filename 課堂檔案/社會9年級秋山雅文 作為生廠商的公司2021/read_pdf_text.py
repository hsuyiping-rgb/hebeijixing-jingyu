import sys
import os
from pathlib import Path

# Try importing pypdf or pdfplumber
try:
    import pypdf
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "pypdf"], capture_output=True)
    import pypdf

def extract_text(pdf_path, txt_output):
    reader = pypdf.PdfReader(pdf_path)
    print(f"Total pages: {len(reader.pages)}")
    text_content = []
    for i, page in enumerate(reader.pages, 1):
        text = page.extract_text()
        text_content.append(f"--- PAGE {i} ---")
        text_content.append(text)
        
    with open(txt_output, "w", encoding="utf-8") as f:
        f.write("\n".join(text_content))
    print(f"Successfully extracted PDF text to {txt_output}")

def main():
    pdf_path = r"g:\我的雲端硬碟\2021日本學共年會\資料\國中社會作為生產公司的人.pdf"
    txt_output = "output/字幕/國中社會作為生產公司的人_extracted.txt"
    extract_text(pdf_path, txt_output)
    return 0

if __name__ == "__main__":
    sys.exit(main())
