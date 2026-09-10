# -*- coding: utf-8 -*-
"""把「文本結構分析」的概念鏈畫成流程圖 PNG，供 build_docx.py 插進制式表。

制式表這一欄的抬頭寫著「一、文本結構分析：(用圖形和文字表示)」——**圖形優先**，
所以本模組把節次鏈、概念鏈、教材地位畫成一張橫向流程圖，文字敘述只當補充。

圖的規格（JSON `教材組織與學生分析.文本結構分析.圖`）：

    {
      "帶": [
        {"標題": "單元節次",
         "節點": [{"文": "1-1 生活中的統計圖", "註": "2 節"},
                  {"文": "1-2 製作折線圖", "註": "1.5 節", "重點": true}]},
        {"標題": "概念鏈", "節點": [{"文": "分辨兩種圖的使用時機"}, ...]}
      ],
      "註腳": "本節為第 4 節……"
    }

`重點: true` 的節點會加粗框、淺灰底，用來標出本節位置。
無圖規格時 build_docx.py 會退回純文字，不會壞掉。
"""
import os

from PIL import Image, ImageDraw, ImageFont

# 3 倍取樣後縮回，Word 裡看起來才不糊。
SS = 3
W = 1740                      # 對應 17.4 cm
FONT_CANDIDATES = [
    r'C:\Windows\Fonts\kaiu.ttf',      # 標楷體，與制式表同字體
    r'C:\Windows\Fonts\msjh.ttc',      # 微軟正黑
    r'C:\Windows\Fonts\mingliu.ttc',
]

INK = (0, 0, 0)
GREY = (110, 110, 110)
FILL = (245, 245, 245)
HILITE = (222, 222, 222)


def _font(size):
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    return ImageFont.load_default()


def _wrap(draw, text, font, max_w):
    """CJK 逐字斷行；遇到既有換行符先切段。"""
    lines = []
    for seg in str(text).split('\n'):
        cur = ''
        for ch in seg:
            if draw.textlength(cur + ch, font=font) > max_w and cur:
                lines.append(cur)
                cur = ch
            else:
                cur += ch
        lines.append(cur)
    return lines or ['']


def _text_h(font):
    return int(font.size * 1.35)


def render(spec, out_path, width=W):
    """畫圖並存檔，回傳 (檔名, 圖寬 px)。"""
    bands = spec.get('帶') or []
    footnote = spec.get('註腳', '')

    w = width * SS
    pad = 12 * SS
    label_w = 130 * SS
    arrow_w = 46 * SS
    band_gap = 18 * SS

    f_box = _font(21 * SS)
    f_note = _font(17 * SS)
    f_label = _font(20 * SS)
    f_foot = _font(19 * SS)

    probe = ImageDraw.Draw(Image.new('RGB', (10, 10)))

    # ---- 先量測，決定畫布高度 ----
    plans = []
    for band in bands:
        nodes = band.get('節點') or []
        n = max(len(nodes), 1)
        box_w = (w - 2 * pad - label_w - (n - 1) * arrow_w) // n
        inner = box_w - 16 * SS
        rows, h = [], 0
        for nd in nodes:
            body = _wrap(probe, nd.get('文', ''), f_box, inner)
            note = _wrap(probe, nd.get('註', ''), f_note, inner) if nd.get('註') else []
            hh = len(body) * _text_h(f_box) + len(note) * _text_h(f_note) + 16 * SS
            h = max(h, hh)
            rows.append((nd, body, note))
        plans.append((band.get('標題', ''), rows, box_w, h))

    foot_lines = _wrap(probe, footnote, f_foot, w - 2 * pad) if footnote else []
    total_h = pad + sum(p[3] + band_gap for p in plans)
    total_h += len(foot_lines) * _text_h(f_foot) + (pad if foot_lines else 0)

    img = Image.new('RGB', (w, int(total_h)), 'white')
    d = ImageDraw.Draw(img)

    # ---- 逐帶繪製 ----
    y = pad
    for title, rows, box_w, h in plans:
        d.text((pad, y + h // 2 - f_label.size // 2), title, font=f_label, fill=GREY)
        x = pad + label_w
        for i, (nd, body, note) in enumerate(rows):
            if i:
                cy = y + h // 2
                ax = x - arrow_w + 8 * SS
                bx = x - 8 * SS
                d.line([(ax, cy), (bx, cy)], fill=INK, width=2 * SS)
                d.polygon([(bx, cy), (bx - 9 * SS, cy - 6 * SS),
                           (bx - 9 * SS, cy + 6 * SS)], fill=INK)
            hot = bool(nd.get('重點'))
            d.rounded_rectangle([x, y, x + box_w, y + h], radius=8 * SS,
                                fill=HILITE if hot else FILL,
                                outline=INK, width=(3 if hot else 1) * SS)
            ty = y + (h - len(body) * _text_h(f_box)
                      - len(note) * _text_h(f_note)) // 2
            for ln in body:
                tw = d.textlength(ln, font=f_box)
                d.text((x + (box_w - tw) // 2, ty), ln, font=f_box, fill=INK)
                ty += _text_h(f_box)
            for ln in note:
                tw = d.textlength(ln, font=f_note)
                d.text((x + (box_w - tw) // 2, ty), ln, font=f_note, fill=GREY)
                ty += _text_h(f_note)
            x += box_w + arrow_w
        y += h + band_gap

    if foot_lines:
        for ln in foot_lines:
            d.text((pad, y), ln, font=f_foot, fill=INK)
            y += _text_h(f_foot)

    img = img.resize((width, max(1, int(total_h) // SS)), Image.LANCZOS)
    img.save(out_path)
    return out_path, width
