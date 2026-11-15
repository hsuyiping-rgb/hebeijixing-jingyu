"""議課簡報 v2：含截圖與燒字幕影片，加上圖解總覽與《教師花傳書》p.44–62 對照（learning 風格）。

結構：封面 → 概覽 → 圖解（課堂流程圖、理答策略統計）→ 16 段 × 3 頁（A 畫面與描述 → B 詮釋・理答・反思，
右上標出對應的花傳書概念 → C 片段影片）→ 花傳書 × 504（摘要、13 個概念、討論問題、主持流程）→ 結語。
內容來源：output/簡報/slides_content.json、media_plan.json、shots/、clips/；output/圖解/*.png；
花傳書對照取 花傳書p44-62×504課例_概念對照與討論問題_v2_呼應張力詳述.md；備忘稿取 analysis.txt 全文。
用法：python -X utf8 -I build_slides_media_v2.py <lesson_dir> [輸出檔名.pptx] [媒體後綴，如 _720]
"""
import base64, html, json, math, re, sys
from pathlib import Path
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

root = Path(sys.argv[1])
out = root / 'output'
deck = out / '簡報'
C = json.loads((deck / 'slides_content.json').read_text(encoding='utf-8'))
M = json.loads((deck / 'media_plan.json').read_text(encoding='utf-8'))
SUF = sys.argv[3] if len(sys.argv) > 3 else ''  # 媒體版本後綴，如 _720 → shots_720/、clips_720/、board_31m45_720.png
board_img = out / 'screenshots' / f'board_31m45{SUF}.png'
figs = [(out / '圖解' / '課堂流程圖.png', '圖解一　課堂流程',
         '前段用箱子檢查垂直，後段從開放分類走到數學定義，兩段在第 15 節以「平行」串連。'),
        (out / '圖解' / '理答策略統計.png', '圖解二　理答策略統計',
         '轉問最多、反問僅開場一次；評價語與接近代答處值得在議課細看（第 11、15 節待確認）。')]

# ---- 花傳書對照（取自 v2 md）----
md = (root / '花傳書p44-62×504課例_概念對照與討論問題_v2_呼應張力詳述.md').read_text(encoding='utf-8')
plain = lambda t: t.replace('**', '')
K_SUMMARY = plain(re.search(r'## 一、[^\n]*\n\n(.+?)\n', md).group(1))
concepts = []  # (n, 名稱, 花傳書說明, 課堂事實, 判定, [詳述段落])
for row in re.findall(r'^\| (\d+) \|(.+)\|$', md, re.M):
    n, rest = row
    concept, fact, detail = [c.strip() for c in rest.split(' | ')]
    m = re.match(r'\*\*(.+?)\*\*[；：]?(.*)', concept)
    paras = detail.split('<br>')
    verdict = re.match(r'\*\*(.+?)\*\*', paras[0]).group(1)
    concepts.append((int(n), m.group(1), plain(m.group(2)).strip('；：'), plain(fact), verdict,
                     [plain(p) for p in paras[1:]]))
qgroups = []  # (組名, [(題號, 星號, 題名, 內文)])
for head, body in re.findall(r'^### (.+?)\n\n(.+?)(?=\n### |\n---)', md, re.M | re.S):
    qs = re.findall(r'^(\d+)\. (★ )?\*\*(.+?)\*\*(.*)$', body, re.M)
    qgroups.append((head, [(int(a), bool(b), c, d.lstrip('：')) for a, b, c, d in qs]))
host = [[c.strip() for c in l.strip('|').split('|')] for l in
        re.search(r'## 四、[^\n]*\n\n((?:\|.*\n)+)', md).group(1).splitlines()[2:]]
host_title = re.search(r'## 四、(.+)', md).group(1)
host_note = re.search(r'## 四、.*?\n> (.+)', md, re.S).group(1).strip()
# 各段對應的花傳書概念編號（依 v2 md 表格「課堂對應事實」欄引用的節次）
SEC_CONCEPTS = {1: [1, 5], 2: [1, 5], 3: [6, 9], 4: [9], 5: [2], 6: [11], 7: [1], 8: [6, 9, 11], 9: [4],
                10: [3, 6], 11: [4, 8], 12: [6, 9], 13: [11], 14: [5], 15: [5, 8, 10], 16: [3]}
cname = {c[0]: c[1] for c in concepts}

BG, GREEN, BODY, GREY = '#EEF2EB', '#23412D', '#2C332D', '#6B736C'
CARD, SOFT, ACCENT, WHITE = '#FFFFFF', '#DCE6D8', '#7A9A6E', '#FFFFFF'
FONT = 'Microsoft JhengHei'


def rgb(h):
    return RGBColor.from_string(h.lstrip('#'))


def mmss(t):
    h, m, s = t.split(':')
    return f'{int(h) * 60 + int(m):02}:{s}'


analysis = (out / 'analysis.txt').read_text(encoding='utf-8')
notes_by_n = {}
for block in re.split(r'\n(?=Slide \d+\n)', analysis.split('---', 1)[1]):
    m = re.match(r'\s*Slide (\d+)\n', block)
    if m:
        keep = [l for l in block.splitlines()[1:] if re.match(r'^(描述|詮釋|理答|反思)：', l) or l.startswith('（')]
        notes_by_n[int(m.group(1))] = '\n\n'.join(keep)

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def new_slide(notes=None):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid(); s.background.fill.fore_color.rgb = rgb(BG)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def box(s, x, y, w, h, fill=None, shape=MSO_SHAPE.RECTANGLE, radius=None):
    sh = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill:
        sh.fill.solid(); sh.fill.fore_color.rgb = rgb(fill)
    else:
        sh.fill.background()
    sh.line.fill.background(); sh.shadow.inherit = False
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        sh.adjustments[0] = radius
    return sh


def text(s, x, y, w, h, runs, size=20, color=BODY, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         spacing=1.15, after=0):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05); tf.margin_top = tf.margin_bottom = Inches(0.02)
    paras = [[(runs, {})]] if isinstance(runs, str) else runs
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.line_spacing = spacing; p.space_after = Pt(after)
        pPr = p._p.get_or_add_pPr(); pPr.set('eaLnBrk', '1'); pPr.set('hangingPunct', '1')  # 中文避頭尾
        for t, o in para:
            r = p.add_run(); r.text = t
            f = r.font; f.name = FONT; f.size = Pt(o.get('size', size)); f.bold = o.get('bold', bold)
            f.color.rgb = rgb(o.get('color', color))
            rPr = r._r.get_or_add_rPr(); rPr.set('lang', 'zh-TW'); rPr.set('altLang', 'en-US')
            rPr.append(rPr.makeelement(qn('a:ea'), {'typeface': FONT}))  # 不設 ea 會退回新細明體
    return tb


def header(s, kicker, title, sub=None, title_size=38):
    text(s, 0.6, 0.28, 12, 0.4, kicker, size=15, color=ACCENT, bold=True)
    text(s, 0.6, 0.66, 12.1, 0.8, title, size=title_size, color=GREEN, bold=True)
    if sub:
        text(s, 0.6, 1.4, 12.1, 0.45, sub, size=19, color=GREY)


def picture_fit(s, path, x, y, w, h):
    from PIL import Image
    with Image.open(path) as im:
        iw, ih = im.size
    pw = w; ph = w * ih / iw
    if ph > h:
        ph = h; pw = h * iw / ih
    return s.shapes.add_picture(str(path), Inches(x + (w - pw) / 2), Inches(y + (h - ph) / 2), Inches(pw), Inches(ph))


def fit(paras, w, h, sizes=(20, 19, 18, 17, 16, 15, 14, 13), spacing=1.25, after=6):
    """回傳能讓段落塞進 w×h 英吋的最大字級（以全形字寬估算）。"""
    for sz in sizes:
        cpl = max(1, int(w / (sz / 72 * 1.02)))
        lines = sum(math.ceil(len(p) / cpl) for p in paras)
        if lines * sz * spacing * 1.2 / 72 + len(paras) * after / 72 <= h:
            return sz
    return sizes[-1]


def label(s, lab, x, y, dark=False):
    box(s, x, y, 0.95, 0.44, fill=GREEN if dark else ACCENT, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.3)
    text(s, x, y, 0.95, 0.44, lab, size=15, color=WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)


# ---- 封面 ----
s = new_slide()
box(s, 9.2, -1.2, 5.6, 5.6, fill=SOFT, shape=MSO_SHAPE.OVAL)
box(s, 10.6, 4.4, 3.4, 3.4, fill='#C9D8C3', shape=MSO_SHAPE.OVAL)
box(s, 0.9, 1.35, 0.12, 3.0, fill=GREEN)
text(s, 1.25, 1.2, 10, 3.2, [[(l, {})] for l in C['cover']['title'].split('\n')], size=50, color=GREEN, bold=True,
     spacing=1.1)
text(s, 1.25, 4.45, 10.5, 1.0, [[(C['cover']['subtitle'], {})],
                                [('含課堂畫面、影片片段與《教師花傳書》對照', {'size': 19, 'color': ACCENT})]], size=24, after=4)
text(s, 1.25, 5.65, 10.5, 1.0, C['cover']['meta'], size=17, color=GREY)

# ---- 概覽 ----
o = C['overview']
s = new_slide()
text(s, 0.6, 0.45, 12, 0.8, o['title'], size=40, color=GREEN, bold=True)
for i, side in enumerate((o['left'], o['right'])):
    x = 0.6 + i * 6.15
    box(s, x, 1.5, 5.95, 4.75, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.05)
    box(s, x, 1.5, 5.95, 0.12, fill=GREEN if i == 0 else ACCENT)
    text(s, x + 0.35, 1.8, 5.4, 0.55, side['head'], size=27, color=GREEN, bold=True)
    text(s, x + 0.35, 2.42, 5.4, 0.5, side['sub'], size=18, color=GREY)
    text(s, x + 0.35, 3.1, 5.35, 3.1, [[('●  ', {'color': ACCENT, 'size': 14}), (t, {})] for t in side['items']],
         size=21, after=10, spacing=1.15)
box(s, 0.6, 6.45, 12.1, 0.62, fill=SOFT, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.3)
text(s, 0.8, 6.45, 11.7, 0.62, o['lens'], size=17, color=GREEN, bold=True, anchor=MSO_ANCHOR.MIDDLE,
     align=PP_ALIGN.CENTER)

# ---- 圖解（與 Word v4 卷首相同的兩張圖）----
for path, title, cap in figs:
    s = new_slide(cap)
    text(s, 0.6, 0.28, 12, 0.4, '圖解總覽', size=15, color=ACCENT, bold=True)
    text(s, 0.6, 0.66, 12.1, 0.8, title, size=34, color=GREEN, bold=True)
    box(s, 0.6, 1.5, 12.1, 5.25, fill=WHITE, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.03)
    picture_fit(s, path, 0.75, 1.6, 11.8, 5.05)
    text(s, 0.6, 6.85, 12.1, 0.45, cap, size=16, color=GREY, align=PP_ALIGN.CENTER)

# ---- 各段：A 畫面與描述 → B 詮釋・理答・反思 → C 影片 ----
missing = []
for sec in C['sections']:
    n = sec['n']; plan = M[str(n)]
    shot = board_img if sec.get('image') == 'board' and board_img.exists() else deck / f'shots{SUF}' / f'shot_{n:02}.jpg'
    clip = deck / f'clips{SUF}' / f'clip_{n:02}_sub.mp4'
    kick = f"第 {n} 段　{sec['time']}"
    notes = notes_by_n.get(n)

    # A
    s = new_slide(notes)
    header(s, kick, sec['title'], sec['sub'])
    picture_fit(s, shot, 0.6, 2.0, 6.7, 3.77)
    cap = ('31:45 黑板（720p 放大）' if SUF else '31:45 黑板（360p 放大）') if shot == board_img else f"課堂畫面 {mmss(plan['shot'])}"
    text(s, 0.6, 5.8, 6.7, 0.32, cap, size=13, color=GREY)
    box(s, 7.55, 2.0, 5.15, 3.77, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06)
    box(s, 7.55, 2.0, 0.12, 3.77, fill=GREEN)
    qsize = 25 if len(sec['quote']) <= 22 else 22
    text(s, 7.9, 2.2, 4.6, 2.85, [[('「', {'color': ACCENT}), (sec['quote'], {}), ('」', {'color': ACCENT})]],
         size=qsize, bold=True, anchor=MSO_ANCHOR.MIDDLE, spacing=1.25)
    text(s, 7.9, 5.1, 4.6, 0.55, f"— {sec['who']}｜可信度：{sec['conf']}", size=13, color=GREY)
    label(s, '描述', 0.6, 6.2)
    text(s, 1.7, 6.13, 11.0, 1.25, sec['desc'], size=19, spacing=1.2)

    # B
    s = new_slide(notes)
    header(s, kick, sec['title'] + '　詮釋・理答・反思', None, title_size=34)
    tag = '花傳書對照　' + '｜'.join(f'概念 {k} {cname[k]}' for k in SEC_CONCEPTS[n])
    text(s, 4.6, 0.28, 8.1, 0.4, tag, size=12, color=GREEN, bold=True, align=PP_ALIGN.RIGHT)
    label(s, '詮釋', 0.6, 1.62, dark=True)
    text(s, 1.7, 1.55, 11.0, 1.3, sec['interp'], size=22, spacing=1.25)
    top = 3.05
    box(s, 0.6, top, 7.45, 7.1 - top, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.04)
    text(s, 0.9, top + 0.2, 7, 0.45, '理答策略', size=18, color=GREEN, bold=True)
    step = min(0.95, (7.1 - top - 0.85) / max(1, len(sec['strat'])))
    for i, (tag, d) in enumerate(sec['strat']):
        text(s, 0.9, top + 0.8 + i * step, 6.95, step, [[(tag, {'bold': True, 'color': GREEN, 'size': 19}),
                                                         ('　' + d, {'size': 18})]], spacing=1.15)
    box(s, 8.3, top, 4.4, 7.1 - top, fill=GREEN, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.05)
    text(s, 8.6, top + 0.2, 3.9, 0.45, '反思', size=18, color='#CFE0C6', bold=True)
    text(s, 8.6, top + 0.75, 3.85, 7.1 - top - 0.9, sec['reflect'], size=21, color=WHITE, spacing=1.3)
    if sec.get('note'):
        text(s, 0.6, 7.13, 12, 0.32, '※ ' + sec['note'], size=12, color=GREY)

    # C
    s = new_slide(notes)
    a, b = plan['clip']
    header(s, f"第 {n} 段　影片片段 {mmss(a)}–{mmss(b)}", '▶ ' + sec['title'], None, title_size=32)
    vw, vh = 9.9, 5.57  # 16:9，下緣留給說明列
    vx, vy = (13.333 - vw) / 2, 1.45
    if clip.exists():
        s.shapes.add_movie(str(clip), Inches(vx), Inches(vy), Inches(vw), Inches(vh),
                           poster_frame_image=str(deck / f'shots{SUF}' / f'shot_{n:02}.jpg'), mime_type='video/mp4')
    else:
        missing.append(clip.name)
        box(s, vx, vy, vw, vh, fill=SOFT)
        text(s, vx, vy, vw, vh, f'（找不到 {clip.name}）', size=20, color=GREY, align=PP_ALIGN.CENTER,
             anchor=MSO_ANCHOR.MIDDLE)
    text(s, 0.6, 7.12, 12.1, 0.32, '點畫面播放｜已燒錄校正字幕（未校正語句不上字幕）｜音訊經增益處理', size=12,
         color=GREY, align=PP_ALIGN.CENTER)

# ---- 花傳書 × 504：章節頁 ----
s = new_slide(K_SUMMARY)
box(s, 9.2, -1.2, 5.6, 5.6, fill=SOFT, shape=MSO_SHAPE.OVAL)
box(s, 0.9, 1.0, 0.12, 1.9, fill=GREEN)
text(s, 1.25, 0.9, 10, 1.2, '《教師花傳書》p.44–62 × 504 課例', size=40, color=GREEN, bold=True)
text(s, 1.25, 1.95, 10, 0.9, '專家型教師的養成／教師作為學的專家／從成熟型教師的教學中學習', size=19, color=GREY)
box(s, 0.9, 3.25, 11.8, 3.75, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.04)
label(s, '摘要', 1.2, 3.5, dark=True)
text(s, 1.2, 4.1, 11.2, 2.8, K_SUMMARY, size=fit([K_SUMMARY], 11.2, 2.8, spacing=1.35), spacing=1.35)

# ---- 13 個概念：上排「花傳書說／課堂事實」，下排「呼應或張力」詳述 ----
for n, name, says, fact, verdict, paras in concepts:
    s = new_slide('\n\n'.join([f'{name}：{says}', f'課堂事實：{fact}', verdict] + paras))
    tension = '張力' in verdict and '呼應' not in verdict
    header(s, f'花傳書 × 504　概念 {n} / {len(concepts)}', name, None, title_size=32)
    for i, (lab, body) in enumerate((('花傳書', says), ('課堂事實', fact))):
        x = 0.6 + i * 6.15
        box(s, x, 1.5, 5.95, 1.85, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06)
        box(s, x, 1.5, 0.1, 1.85, fill=GREEN if i == 0 else ACCENT)
        text(s, x + 0.3, 1.6, 5.4, 0.35, lab, size=14, color=ACCENT if i else GREEN, bold=True)
        text(s, x + 0.3, 1.97, 5.45, 1.32, body, size=fit([body], 5.45, 1.32, sizes=(17, 16, 15, 14, 13), spacing=1.2),
             spacing=1.2)
    box(s, 0.6, 3.5, 12.1, 3.8, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.03)
    vw = min(11.6, 0.3 + len(verdict) * 0.25)
    box(s, 0.85, 3.65, vw, 0.42, fill='#A0522D' if tension else GREEN, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.3)
    text(s, 0.85, 3.65, vw, 0.42, verdict, size=15, color=WHITE, bold=True, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE)
    sz = fit(paras, 11.6, 3.05, sizes=(18, 17, 16, 15, 14, 13, 12), spacing=1.2, after=4)
    text(s, 0.85, 4.18, 11.6, 3.05, [[(p, {})] for p in paras], size=sz, spacing=1.2, after=4)

# ---- 討論問題 ----
stars = [(q, g) for g, qs in qgroups for q in qs if q[1]]
s = new_slide('\n\n'.join(f'{q[0]}. {q[2]}：{q[3]}' for q, _ in stars))
header(s, '討論問題', '建議優先討論的三題', '每題附文本頁碼與課例節次，方便引導回證據')
for i, ((num, _, ttl, body), g) in enumerate(stars):
    y = 2.05 + i * 1.72
    box(s, 0.6, y, 12.1, 1.55, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08)
    box(s, 0.85, y + 0.33, 0.9, 0.9, fill=GREEN, shape=MSO_SHAPE.OVAL)
    text(s, 0.85, y + 0.33, 0.9, 0.9, f'{g[0]}{num}', size=20, color=WHITE, bold=True, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE)
    para = [[(ttl, {'bold': True, 'color': GREEN}), ('　' + body, {})]]
    text(s, 2.0, y + 0.08, 10.5, 1.4, para, size=fit([ttl + body], 10.5, 1.4, sizes=(17, 16, 15, 14, 13)),
         anchor=MSO_ANCHOR.MIDDLE, spacing=1.2)
for h, qs in qgroups:  # 每組一頁，超過 4 題分頁
    for ci in range(0, len(qs), 4):
        chunk = qs[ci:ci + 4]
        s = new_slide('\n\n'.join(f'{q[0]}. {q[2]}：{q[3]}' for q in chunk))
        header(s, '討論問題' + ('（續）' if ci else ''), h, None, title_size=30)
        for i, (num, star, ttl, body) in enumerate(chunk):
            y = 1.55 + i * 1.45
            box(s, 0.6, y, 12.1, 1.32, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08)
            box(s, 0.6, y, 0.1, 1.32, fill=GREEN if star else ACCENT)
            text(s, 0.9, y + 0.05, 11.6, 1.22, [[(f'{num}. {"★ " if star else ""}{ttl}', {'bold': True, 'color': GREEN}),
                                                ('　' + body, {})]],
                 size=fit([f'{num}. {ttl}　{body}'], 11.6, 1.22, sizes=(18, 17, 16, 15, 14, 13)),
                 anchor=MSO_ANCHOR.MIDDLE, spacing=1.2)

# ---- 主持流程 ----
s = new_slide(host_note)
header(s, '討論問題', host_title, None, title_size=32)
cols = [(0.6, 2.0, '時段'), (2.7, 6.9, '內容'), (9.7, 3.0, '用到的題目')]
for x, w, h in cols:
    box(s, x, 1.55, w - 0.1, 0.55, fill=GREEN)
    text(s, x, 1.55, w - 0.1, 0.55, h, size=17, color=WHITE, bold=True, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
for r, row in enumerate(host):
    y = 2.2 + r * 0.86
    for (x, w, _), val in zip(cols, row):
        box(s, x, y, w - 0.1, 0.78, fill=CARD if r % 2 == 0 else SOFT)
        text(s, x + 0.12, y, w - 0.34, 0.78, val, size=16, anchor=MSO_ANCHOR.MIDDLE, spacing=1.1,
             align=PP_ALIGN.LEFT if x == 2.7 else PP_ALIGN.CENTER)
text(s, 0.6, 6.6, 12.1, 0.75, '※ ' + host_note, size=13, color=GREY, spacing=1.2)

# ---- 結語 ----
cl = C['closing']
s = new_slide()
text(s, 0.6, 0.45, 12, 0.8, cl['title'], size=40, color=GREEN, bold=True)
for i, q in enumerate(cl['items']):
    y = 1.55 + i * 1.6
    box(s, 0.6, y, 12.1, 1.38, fill=CARD, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.1)
    box(s, 0.85, y + 0.24, 0.9, 0.9, fill=GREEN, shape=MSO_SHAPE.OVAL)
    text(s, 0.85, y + 0.24, 0.9, 0.9, str(i + 1), size=28, color=WHITE, bold=True, align=PP_ALIGN.CENTER,
         anchor=MSO_ANCHOR.MIDDLE)
    text(s, 2.0, y + 0.08, 10.5, 1.22, q, size=25, anchor=MSO_ANCHOR.MIDDLE, spacing=1.15)
text(s, 0.6, 6.5, 12.1, 0.8, cl['foot'], size=14, color=GREY)

name = sys.argv[2] if len(sys.argv) > 2 else 'slides_含截圖與影片.pptx'
dst = deck / name
prs.save(dst)
print('saved', dst, len(prs.slides), 'slides', f'{dst.stat().st_size / 1048576:.0f}MB', 'missing:', missing)

# ---- HTML 版（引用相對路徑的 shots/ 與 clips/，與 pptx 放同一資料夾）----
e = html.escape
pages = [f"""<section class="cover"><div class="bar"></div><h1>{'<br>'.join(e(l) for l in C['cover']['title'].split(chr(10)))}</h1>
<p class="sub">{e(C["cover"]["subtitle"])}（含課堂畫面、影片片段與花傳書對照）</p><p class="muted">{e(C['cover']['meta'])}</p></section>"""]
cols = ''.join(f"<div class='card'><h3>{e(x['head'])}</h3><p class='muted'>{e(x['sub'])}</p><ul>{''.join(f'<li>{e(i)}</li>' for i in x['items'])}</ul></div>"
               for x in (o['left'], o['right']))
pages.append(f"<section><h2>{e(o['title'])}</h2><div class='two'>{cols}</div><p class='lens'>{e(o['lens'])}</p></section>")
for path, title, cap in figs:
    src = 'data:image/png;base64,' + base64.b64encode(path.read_bytes()).decode()
    pages.append(f"<section><p class='kicker'>圖解總覽</p><h2>{e(title)}</h2><figure class='fig'><img src='{src}' alt='{e(title)}'></figure><p class='muted center'>{e(cap)}</p></section>")
board_src = 'data:image/png;base64,' + base64.b64encode(board_img.read_bytes()).decode() if board_img.exists() else ''
for sec in C['sections']:
    n = sec['n']; plan = M[str(n)]; a, b = plan['clip']
    img = board_src if sec.get('image') == 'board' and board_src else f'shots{SUF}/shot_{n:02}.jpg'
    strat = ''.join(f'<li><b>{e(t)}</b>　{e(d)}</li>' for t, d in sec['strat'])
    note = f"<p class='muted small'>※ {e(sec['note'])}</p>" if sec.get('note') else ''
    k = f"第 {n} 段　{e(sec['time'])}"
    pages.append(f"""<section><p class="kicker">{k}</p><h2>{e(sec['title'])}</h2><p class="muted">{e(sec['sub'])}</p>
<div class="two"><figure><img src="{img}" alt="課堂畫面"></figure><blockquote>「{e(sec['quote'])}」<cite>— {e(sec['who'])}｜可信度：{e(sec['conf'])}</cite></blockquote></div>
<p class="big"><span class="tag">描述</span>{e(sec['desc'])}</p></section>""")
    ktag = '｜'.join(f'概念 {c} {e(cname[c])}' for c in SEC_CONCEPTS[n])
    pages.append(f"""<section><p class="kicker">{k}　<span class="ktag">花傳書對照　{ktag}</span></p><h2>{e(sec['title'])}　詮釋・理答・反思</h2>
<p class="big"><span class="tag dark">詮釋</span>{e(sec['interp'])}</p><div class="grid"><div class="card"><h4>理答策略</h4><ul class="strat">{strat}</ul></div>
<div class="reflect"><h4>反思</h4><p>{e(sec['reflect'])}</p></div></div>{note}</section>""")
    pages.append(f"""<section><p class="kicker">第 {n} 段　影片片段 {mmss(a)}–{mmss(b)}</p><h2>▶ {e(sec['title'])}</h2>
<video controls preload="none" poster="shots{SUF}/shot_{n:02}.jpg" src="clips{SUF}/clip_{n:02}_sub.mp4"></video>
<p class="muted small center">已燒錄校正字幕（未校正語句不上字幕）｜音訊經增益處理</p></section>""")
pages.append(f"""<section><h2>《教師花傳書》p.44–62 × 504 課例</h2><p class="muted">專家型教師的養成／教師作為學的專家／從成熟型教師的教學中學習</p>
<div class="card"><p class="big"><span class="tag dark">摘要</span>{e(K_SUMMARY)}</p></div></section>""")
for n, name, says, fact, verdict, paras in concepts:
    pages.append(f"""<section><p class="kicker">花傳書 × 504　概念 {n} / {len(concepts)}</p><h2>{e(name)}</h2>
<div class="two"><div class="card"><h4>花傳書</h4><p>{e(says)}</p></div><div class="card"><h4>課堂事實</h4><p>{e(fact)}</p></div></div>
<div class="card" style="margin-top:22px"><span class="tag dark">{e(verdict)}</span>{''.join(f'<p>{e(p)}</p>' for p in paras)}</div></section>""")
qli = lambda q: f"<li value='{q[0]}'><b>{'★ ' if q[1] else ''}{e(q[2])}</b>　{e(q[3])}</li>"
pages.append(f"<section><p class='kicker'>討論問題</p><h2>建議優先討論的三題</h2><ol class='qs'>{''.join(qli(q) for q, _ in stars)}</ol></section>")
for h, qs in qgroups:
    pages.append(f"<section><p class='kicker'>討論問題</p><h2>{e(h)}</h2><ol class='qs small-q'>{''.join(qli(q) for q in qs)}</ol></section>")
rows = ''.join('<tr>' + ''.join(f'<td>{e(v)}</td>' for v in r) + '</tr>' for r in host)
pages.append(f"""<section><p class='kicker'>討論問題</p><h2>{e(host_title)}</h2><table class='host'><tr><th>時段</th><th>內容</th><th>用到的題目</th></tr>{rows}</table>
<p class='muted small'>※ {e(host_note)}</p></section>""")
pages.append(f"<section><h2>{e(cl['title'])}</h2><ol class='qs'>{''.join(f'<li>{e(q)}</li>' for q in cl['items'])}</ol><p class='muted small'>{e(cl['foot'])}</p></section>")

css = """:root{--bg:#EEF2EB;--green:#23412D;--body:#2C332D;--grey:#6B736C;--card:#fff;--soft:#DCE6D8;--accent:#7A9A6E}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#18201A;--green:#B9D3AE;--body:#E3E8E0;--grey:#9AA597;--card:#222C24;--soft:#2D3A2F;--accent:#8FB083}}
:root[data-theme="dark"]{--bg:#18201A;--green:#B9D3AE;--body:#E3E8E0;--grey:#9AA597;--card:#222C24;--soft:#2D3A2F;--accent:#8FB083}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--body);font-family:"Microsoft JhengHei","Noto Sans TC",sans-serif}
section{display:none;max-width:1240px;margin:0 auto;padding:36px 16px 96px;min-height:100vh}section.on{display:block}
h1{font-size:clamp(34px,5.5vw,60px);color:var(--green);line-height:1.2;margin:0 0 20px}h2{font-size:clamp(28px,4vw,46px);color:var(--green);margin:4px 0}
h3,h4{color:var(--green);margin:0 0 10px;font-size:24px}.muted,cite{color:var(--grey)}.small{font-size:15px}.center{text-align:center}.kicker{color:var(--accent);font-weight:700;margin:0;font-size:18px}
.cover{padding-top:16vh}.cover .bar{width:9px;height:150px;background:var(--green);float:left;margin-right:26px}.sub{font-size:26px}
.two,.grid{display:grid;grid-template-columns:1.3fr 1fr;gap:24px;margin-top:22px}@media (max-width:760px){.two,.grid{grid-template-columns:1fr}}
.card{background:var(--card);border-radius:14px;padding:20px 22px}figure{margin:0}img,video{width:100%;border-radius:12px;display:block;background:#000}
blockquote{background:var(--card);border-left:8px solid var(--green);border-radius:12px;margin:0;padding:24px;font-size:clamp(22px,2.6vw,30px);font-weight:700;line-height:1.5;display:flex;flex-direction:column;justify-content:center}
cite{font-size:15px;font-weight:400;margin-top:12px;font-style:normal}p,li{line-height:1.7;font-size:21px}.big{font-size:23px}
.tag{display:inline-block;background:var(--accent);color:#fff;border-radius:99px;padding:2px 14px;margin-right:12px;font-size:16px;font-weight:700}.tag.dark{background:var(--green)}
.strat{padding-left:20px}.strat li{margin:10px 0}.strat b{color:var(--green)}.reflect{background:var(--green);color:#fff;border-radius:14px;padding:22px}.reflect h4{color:#CFE0C6}.reflect p{margin:0;font-size:24px}
video{margin-top:18px;max-height:72vh}.lens{background:var(--soft);border-radius:99px;padding:12px 20px;text-align:center;color:var(--green);font-weight:700}
.bars .row{display:grid;grid-template-columns:70px 1fr 34px;align-items:center;gap:12px;margin:16px 0;font-size:22px}.track{background:var(--soft);border-radius:6px;height:30px}.fill{background:var(--accent);height:100%;border-radius:6px}
.qs li{background:var(--card);border-radius:14px;padding:24px;margin:18px 0;font-size:27px;line-height:1.5}.qs b{color:var(--green)}.small-q li{font-size:20px;padding:16px 20px}
.ktag{color:var(--green);font-size:15px}.fig img{background:#fff;padding:12px}.host{width:100%;border-collapse:collapse;margin-top:20px;font-size:20px}.host th{background:var(--green);color:var(--bg);padding:10px}.host td{background:var(--card);padding:12px;border-bottom:1px solid var(--soft)}
nav{position:fixed;bottom:0;left:0;right:0;display:flex;justify-content:center;gap:16px;align-items:center;padding:12px;background:var(--bg)}
nav button{background:var(--green);color:var(--bg);border:0;border-radius:99px;padding:9px 20px;font-size:16px;cursor:pointer}nav button:disabled{opacity:.35}"""
js = """const S=[...document.querySelectorAll('section')];let i=0;const c=document.getElementById('c'),p=document.getElementById('p'),n=document.getElementById('n');
function go(k){document.querySelectorAll('video').forEach(v=>v.pause());i=Math.max(0,Math.min(S.length-1,k));S.forEach((s,j)=>s.classList.toggle('on',j===i));c.textContent=(i+1)+' / '+S.length;p.disabled=i===0;n.disabled=i===S.length-1;window.scrollTo(0,0)}
p.onclick=()=>go(i-1);n.onclick=()=>go(i+1);document.addEventListener('keydown',e=>{if(e.target.tagName==='VIDEO')return;if(e.key==='ArrowRight')go(i+1);if(e.key==='ArrowLeft')go(i-1)});go(0);"""
(dst.with_suffix('.html')).write_text(f"""<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>立體形體議課簡報</title><style>{css}</style></head><body>{''.join(pages)}
<nav><button id="p">上一頁</button><span id="c"></span><button id="n">下一頁</button></nav><script>{js}</script></body></html>""", encoding='utf-8')
print('saved', dst.with_suffix('.html'))
