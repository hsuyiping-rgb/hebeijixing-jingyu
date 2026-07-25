import base64
import io
import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "slides.html"
DEST = ROOT / "output" / "slides_illustrated.html"
IMAGE_DIR = ROOT / "output" / "images"

html = SOURCE.read_text(encoding="utf-8")

# Make the presentation image-forward while retaining readable editable text.
html = html.replace("height: 70vh;", "height: 78vh;")
html = html.replace("max-width: 1200px;", "max-width: 1380px;")
html = html.replace("flex: 1.2;", "flex: 0.9;")
html = html.replace("flex: 0.8;", "flex: 1.1;")
html = html.replace("aspect-ratio: 1;", "aspect-ratio: 16 / 9;")
html = html.replace("object-fit: cover;", "object-fit: cover;\n      width: 100%;")
html = html.replace(
    "      transition: opacity 0.2s, transform 0.1s;",
    "      transition: opacity 0.2s, transform 0.1s;\n"
    "      display: inline-flex;\n"
    "      align-items: center;\n"
    "      justify-content: center;\n"
    "      gap: 8px;",
)
html = html.replace(
    "    .btn:hover {",
    "    .btn svg {\n"
    "      width: 19px;\n"
    "      height: 19px;\n"
    "      fill: none;\n"
    "      stroke: currentColor;\n"
    "      stroke-width: 2.4;\n"
    "      stroke-linecap: round;\n"
    "      stroke-linejoin: round;\n"
    "      flex: none;\n"
    "    }\n"
    "    .btn:hover {",
)
html = html.replace(
    '<button class="btn" id="prev-btn" onclick="changeSlide(-1)">上一頁</button>',
    '<button class="btn" id="prev-btn" onclick="changeSlide(-1)" aria-label="上一頁">'
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>'
    '<span>上一頁</span></button>',
)
html = html.replace(
    '<button class="btn" id="next-btn" onclick="changeSlide(1)">下一頁</button>',
    '<button class="btn" id="next-btn" onclick="changeSlide(1)" aria-label="下一頁">'
    '<span>下一頁</span>'
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>'
    '</button>',
)

section_pattern = re.compile(
    r'(<section class="slide" id="slide-(\d+)">.*?)(\s*</div>\s*</section>)',
    re.DOTALL,
)


def add_image(match: re.Match[str]) -> str:
    index = int(match.group(2))
    image_path = IMAGE_DIR / f"slide_{index:02d}.png"
    if not image_path.exists():
        raise FileNotFoundError(image_path)
    with Image.open(image_path) as image:
        image = image.convert("RGB")
        if image.width > 1440:
            height = round(image.height * 1440 / image.width)
            image = image.resize((1440, height), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, format="WEBP", quality=84, method=6)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    image_block = (
        '\n        <div class="slide-image">\n'
        f'          <img src="data:image/webp;base64,{encoded}" '
        f'alt="第 {index} 頁課堂學習插圖">\n'
        "        </div>"
    )
    return match.group(1) + image_block + match.group(3)


html, count = section_pattern.subn(add_image, html)
if count != 13:
    raise RuntimeError(f"Expected 13 slides, embedded {count}")

DEST.write_text(html, encoding="utf-8")
print(DEST)
