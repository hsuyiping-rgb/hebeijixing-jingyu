import base64
import argparse
import io
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--slides-dir", type=Path, default=ROOT / "output" / "ppt_html_slides")
parser.add_argument("--output", type=Path, default=ROOT / "output" / "slides_from_ppt.html")
parser.add_argument("--title", default="四年級數學公開課分析｜PPT 轉製版")
args = parser.parse_args()
SLIDES_DIR = args.slides_dir
DEST = args.output


def encode_webp(path: Path) -> str:
    with Image.open(path) as image:
        image = image.convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, "WEBP", quality=88, method=6)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


slide_paths = sorted(SLIDES_DIR.glob("slide_*.png"))
if not slide_paths:
    raise RuntimeError("No PPT slide exports found")

slides_markup = []
for index, path in enumerate(slide_paths, 1):
    active = " active" if index == 1 else ""
    slides_markup.append(
        f'<section class="slide{active}" id="slide-{index}" aria-hidden="{str(index != 1).lower()}">'
        f'<img src="data:image/webp;base64,{encode_webp(path)}" alt="投影片 {index}">'
        "</section>"
    )

html = f'''<!doctype html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{args.title}</title>
<style>
:root{{--green:#23412d;--paper:#eef2eb;--disabled:#cfcfcf}}
*{{box-sizing:border-box}}
html,body{{width:100%;height:100%;margin:0}}
body{{display:grid;place-items:center;background:var(--paper);font-family:"Microsoft JhengHei",sans-serif;overflow:hidden}}
.deck{{width:min(96vw,1500px);height:min(94vh,940px);display:grid;grid-template-rows:minmax(0,1fr) 76px;background:#fff;border-radius:18px;overflow:hidden;box-shadow:0 14px 40px rgba(20,45,30,.14)}}
.stage{{position:relative;display:grid;place-items:center;min-height:0;padding:18px;background:#fff}}
.slide{{display:none;width:100%;height:100%;align-items:center;justify-content:center}}
.slide.active{{display:flex}}
.slide img{{display:block;max-width:100%;max-height:100%;width:auto;height:auto;aspect-ratio:16/9;object-fit:contain}}
.controls{{display:grid;grid-template-columns:150px minmax(180px,1fr) 150px 72px;gap:22px;align-items:center;padding:12px 28px;border-top:1px solid #e1e7df;background:#fff}}
.btn{{height:48px;border:0;border-radius:11px;background:var(--green);color:#fff;font-size:18px;font-weight:700;display:inline-flex;align-items:center;justify-content:center;gap:9px;cursor:pointer}}
.btn:disabled{{background:var(--disabled);color:#f5f5f5;cursor:not-allowed}}
.btn svg{{width:21px;height:21px;fill:none;stroke:currentColor;stroke-width:2.5;stroke-linecap:round;stroke-linejoin:round}}
.track{{height:9px;border-radius:5px;background:#e7ebe6;overflow:hidden}}
.bar{{height:100%;width:0;background:var(--green);transition:width .2s ease}}
.counter{{font-size:18px;font-weight:700;color:#40463f;text-align:right;white-space:nowrap}}
@media(max-width:720px){{.deck{{width:100vw;height:100vh;border-radius:0}}.controls{{grid-template-columns:52px 1fr 52px 58px;gap:10px;padding:10px}}.btn span{{display:none}}.btn{{width:52px}}.stage{{padding:6px}}}}
</style>
</head>
<body>
<main class="deck">
  <div class="stage">{''.join(slides_markup)}</div>
  <nav class="controls" aria-label="投影片導覽">
    <button class="btn" id="prev" type="button" aria-label="上一頁" disabled><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg><span>上一頁</span></button>
    <div class="track" aria-hidden="true"><div class="bar" id="bar"></div></div>
    <button class="btn" id="next" type="button" aria-label="下一頁"><span>下一頁</span><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg></button>
    <div class="counter" id="counter" aria-live="polite">1 / {len(slide_paths)}</div>
  </nav>
</main>
<script>
const slides=[...document.querySelectorAll('.slide')];
const prev=document.getElementById('prev'),next=document.getElementById('next');
const bar=document.getElementById('bar'),counter=document.getElementById('counter');
let current=0;
function render(){{
  slides.forEach((slide,index)=>{{const active=index===current;slide.classList.toggle('active',active);slide.setAttribute('aria-hidden',String(!active));}});
  prev.disabled=current===0;next.disabled=current===slides.length-1;
  counter.textContent=`${{current+1}} / ${{slides.length}}`;
  bar.style.width=`${{((current+1)/slides.length)*100}}%`;
}}
function move(delta){{const target=Math.max(0,Math.min(slides.length-1,current+delta));if(target!==current){{current=target;render();}}}}
prev.addEventListener('click',()=>move(-1));next.addEventListener('click',()=>move(1));
document.addEventListener('keydown',event=>{{if(event.key==='ArrowLeft')move(-1);if(event.key==='ArrowRight'||event.key===' '){{event.preventDefault();move(1);}}}});
render();
</script>
</body>
</html>'''

DEST.write_text(html, encoding="utf-8")
print(DEST)
