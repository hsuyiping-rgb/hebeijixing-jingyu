import base64
import io
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SLIDES = ROOT / "output" / "圖片" / "宇津木台語文寫作_20141112_簡報匯出"
OUTPUT = ROOT / "output" / "簡報" / "宇津木台語文寫作_20141112_課例分析.html"


def main():
    sections = []
    for index, path in enumerate(sorted(SLIDES.glob("slide_*.png")), start=1):
        with Image.open(path) as image:
            buffer = io.BytesIO()
            image.convert("RGB").save(buffer, "WEBP", quality=90, method=6)
        payload = base64.b64encode(buffer.getvalue()).decode("ascii")
        active = " active" if index == 1 else ""
        sections.append(
            f'<section class="slide{active}" aria-hidden="{str(index != 1).lower()}">'
            f'<img src="data:image/webp;base64,{payload}" alt="課例分析第 {index} 頁"></section>'
        )

    html = f"""<!doctype html>
<html lang="zh-TW"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>宇津木台語文寫作｜課例分析</title>
<style>
*{{box-sizing:border-box}} html,body{{width:100%;height:100%;margin:0;background:#eef4ec;overflow:hidden}}
body{{display:grid;place-items:center}} .deck{{width:min(100vw,177.78vh);height:min(100vh,56.25vw);background:#fff}}
.slide{{display:none;width:100%;height:100%}} .slide.active{{display:block}} .slide img{{display:block;width:100%;height:100%;object-fit:contain}}
</style></head><body><main class="deck" id="deck" aria-label="宇津木台語文寫作課例分析簡報">{''.join(sections)}</main>
<script>
const slides=[...document.querySelectorAll('.slide')]; let current=0;
function render(){{slides.forEach((slide,index)=>{{const active=index===current;slide.classList.toggle('active',active);slide.setAttribute('aria-hidden',String(!active));}})}}
function move(delta){{current=Math.max(0,Math.min(slides.length-1,current+delta));render();}}
document.addEventListener('keydown',event=>{{if(event.key==='ArrowLeft')move(-1);if(event.key==='ArrowRight'||event.key===' '){{event.preventDefault();move(1);}}}});
document.querySelector('#deck').addEventListener('click',event=>move(event.clientX<innerWidth/2?-1:1)); render();
</script></body></html>"""
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html, encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
