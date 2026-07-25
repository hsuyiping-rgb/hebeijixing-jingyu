from pathlib import Path
import base64
from io import BytesIO
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SLIDES = ROOT / "output" / "notebooklm_revised_illustrations_html_slides"
OUT = ROOT / "output" / "notebooklm_lesson_study_illustrated_pdf_3editable_revised_illustrations_integrated.html"
TITLE = "四年級數學課例研究：變化的方式"


def webp_data(path: Path) -> str:
    im = Image.open(path).convert("RGB")
    buf = BytesIO()
    im.save(buf, format="WEBP", quality=82, method=6)
    return base64.b64encode(buf.getvalue()).decode("ascii")


slides = sorted(SLIDES.glob("slide_*.png"))
if not slides:
    raise SystemExit("No slides found")

sections = []
for i, p in enumerate(slides):
    active = " active" if i == 0 else ""
    hidden = "false" if i == 0 else "true"
    sections.append(
        f'<section class="slide{active}" aria-hidden="{hidden}">'
        f'<img src="data:image/webp;base64,{webp_data(p)}" alt="Slide {i+1}"></section>'
    )

html = f"""<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITLE}</title>
<style>
:root{{--g:#23412d;--bg:#eef2eb;--muted:#cfcfcf}}
*{{box-sizing:border-box}}html,body{{width:100%;height:100%;margin:0}}
body{{display:grid;place-items:center;background:var(--bg);font-family:"Microsoft JhengHei",sans-serif;overflow:hidden}}
.deck{{width:min(97vw,1540px);height:min(96vh,960px);display:grid;grid-template-rows:minmax(0,1fr) 44px;background:#fff;border-radius:18px;overflow:hidden;box-shadow:0 14px 40px #142d1e24}}
.stage{{position:relative;display:grid;place-items:center;min-height:0;padding:10px 12px 4px}}
.slide{{display:none;width:100%;height:100%;align-items:center;justify-content:center}}
.slide.active{{display:flex}}
.slide img{{max-width:100%;max-height:100%;aspect-ratio:16/9;object-fit:contain}}
.controls{{height:44px;display:grid;grid-template-columns:42px 1fr 42px 58px;gap:12px;align-items:center;padding:5px 16px 9px;border-top:1px solid #e1e7df;background:#fff}}
.btn{{width:38px;height:30px;border:0;border-radius:8px;background:var(--g);color:#fff;display:inline-flex;align-items:center;justify-content:center;cursor:pointer}}
.btn:disabled{{background:var(--muted);cursor:not-allowed}}
.btn svg{{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2.7;stroke-linecap:round;stroke-linejoin:round}}
.btn span{{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap}}
.track{{height:5px;border-radius:4px;background:#e7ebe6;overflow:hidden}}
.bar{{height:100%;background:var(--g);width:0%}}
.counter{{font-size:15px;font-weight:700;text-align:right;white-space:nowrap;color:#485047}}
@media(max-width:720px){{.deck{{width:100vw;height:100vh;border-radius:0}}.stage{{padding:4px}}.controls{{grid-template-columns:36px 1fr 36px 50px;padding:4px 8px 7px;gap:8px}}.btn{{width:34px;height:28px}}}}
</style></head>
<body><main class="deck" aria-label="{TITLE}">
<div class="stage">{''.join(sections)}</div>
<nav class="controls" aria-label="播放控制">
<button class="btn" id="prev" title="上一頁" aria-label="上一頁"><svg viewBox="0 0 24 24"><path d="M15 18l-6-6 6-6"/></svg><span>上一頁</span></button>
<div class="track" aria-hidden="true"><div class="bar" id="bar"></div></div>
<button class="btn" id="next" title="下一頁" aria-label="下一頁"><svg viewBox="0 0 24 24"><path d="M9 6l6 6-6 6"/></svg><span>下一頁</span></button>
<div class="counter" id="counter">1 / {len(slides)}</div>
</nav></main>
<script>
const slides=[...document.querySelectorAll('.slide')], prev=document.getElementById('prev'), next=document.getElementById('next'), bar=document.getElementById('bar'), counter=document.getElementById('counter');
let idx=0;
function show(i){{idx=Math.max(0,Math.min(slides.length-1,i));slides.forEach((s,n)=>{{s.classList.toggle('active',n===idx);s.setAttribute('aria-hidden',n===idx?'false':'true')}});prev.disabled=idx===0;next.disabled=idx===slides.length-1;counter.textContent=`${{idx+1}} / ${{slides.length}}`;bar.style.width=`${{(idx+1)/slides.length*100}}%`;}}
prev.addEventListener('click',()=>show(idx-1));next.addEventListener('click',()=>show(idx+1));
document.addEventListener('keydown',e=>{{if(e.key==='ArrowRight'||e.key===' '){{e.preventDefault();show(idx+1)}}if(e.key==='ArrowLeft'){{e.preventDefault();show(idx-1)}}}});
show(0);
</script></body></html>"""

OUT.write_text(html, encoding="utf-8")
print(OUT)
print(len(slides))
