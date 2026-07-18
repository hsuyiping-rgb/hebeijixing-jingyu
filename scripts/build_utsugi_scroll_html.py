import base64
import io
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "課堂檔案" / "宇津木台語文寫作_20141112"
SLIDES = OUT / "圖片" / "簡報匯出"
OUTPUT = OUT / "簡報" / "宇津木台語文寫作_20141112_課例分析.html"


def main():
    sections = []
    for index, path in enumerate(sorted(SLIDES.glob("slide_*.png")), start=1):
        with Image.open(path) as image:
            buffer = io.BytesIO()
            image.convert("RGB").save(buffer, "WEBP", quality=90, method=6)
        payload = base64.b64encode(buffer.getvalue()).decode("ascii")
        sections.append(
            f'<section class="slide" aria-label="課例分析第 {index} 頁">'
            f'<img src="data:image/webp;base64,{payload}" alt="課例分析第 {index} 頁"></section>'
        )

    html = f"""<!doctype html>
<html lang="zh-TW"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>宇津木台語文寫作｜課例分析</title>
<style>
*{{box-sizing:border-box}} html{{scroll-behavior:smooth}} body{{margin:0;background:#eef4ec;color:#1f2b24}}
.deck{{width:min(100%,1280px);margin:0 auto;padding:24px 16px 48px}}
.slide{{width:100%;margin:0 0 24px;background:#fff;box-shadow:0 2px 10px rgba(31,43,36,.12)}}
.slide img{{display:block;width:100%;height:auto}}
@media (max-width:640px){{.deck{{padding:0}} .slide{{margin:0 0 12px;box-shadow:none}}}}
</style></head><body><main class="deck" aria-label="宇津木台語文寫作課例分析簡報">{''.join(sections)}</main>
</body></html>"""
    OUTPUT.write_text(html, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
