# -*- coding: utf-8 -*-
"""把教案內容填進「公開課教案參考格式.docx」制式表，輸出可編輯的 .docx。

用法：
    python -X utf8 build_docx.py <內容.json> <範本.docx> <輸出.docx> [--附件 <附件.json>] [--無圖]

`--無圖` 略過內容裡所有夾在文字中的課本圖（`{"圖": ...}` 元素與附件的「圖」清單），
用來產進版控的無圖版；含圖版另外跑一次不帶此旗標，檔名帶「（含課本圖）」。
流程表的「教學活動內容」「教師支援」與附件「段落」的串列元素都可以是
`{"圖": "附件_課本圖_xxx.png", "寬cm": 6, "說明": "圖說"}`，圖會夾在前後文字之間。

`--附件` 指向另一份 JSON（形如 `{"附件": [...]}`），內容會併進主 JSON 後才產表。
用途：出版社課文之類**不進版控**的素材另存一檔，版控版與含附件版共用同一份教案內容，
只差在產出時有沒有帶 `--附件`。

內容 JSON 的結構見同目錄 `教案內容.schema.md`，或參考實際範例
`教案成果/五年級_數學_折線圖_20260909/教案內容.json`。

⚠️ 一定要加 `-X utf8`，否則 Windows 下中文會變亂碼。

範本的已知結構（勿假設，改版時請先用 --inspect 重新確認）：
    P[0..4]  表頭五行
    T[0] 2x1  教學設計理念
    T[1] 4x2  核心素養（r0/r1 表頭，r2/r3 可填兩列）
    T[2] 3x2  領域課程綱要 ⚠️ 這是一張**二維表**，不是三個並排欄位：
              r1c0 是斜線表頭（內含「學習目標／學習表現／學習內容」三個標籤，**不要覆寫**）
              r1c1 = 橫軸，填與本節公開課相關的「學習表現」（最多 2 條）
              r2c0 = 縱軸，填本節重要的「學習內容」（最多 2 條）
              r2c1 = 交會處，填由前兩者整合而成的「學習目標」
    T[3] 4x1  教材組織與學生分析（r1/r2/r3 三小段，抬頭沿用範本原文）
    T[4] 2x1  各節次學習活動設計的重點
    T[5] 4x4  流程表（r1~r3 = 導入與發現／探究與深化／挑戰與聚斂）
    P        「公開授課觀課紀錄表」
    T[6] 6x3  觀課資訊
    P        「觀課重點」← 本課觀課焦點插在這一段之後
    T[7] 4x4  觀課紀錄表（留白）

制式表沒有「教學設計理據」與「理答預想表」，本腳本會另外插表。
理據表依「教師／教材／學生／環境」四大類排序，同類的「類」欄自動縱向合併。
"""
import json
import os
import sys

import docx
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.enum.text import WD_BREAK
from docx.shared import Cm, Pt

try:
    from structure_diagram import render as render_structure
except ImportError:                                  # 沒有 Pillow 時退回純文字
    render_structure = None

# 教學設計理據的四大類順序：備課時先看教師怎麼教，再看教材、學生，最後看環境怎麼營造。
LEI_ORDER = ['教師', '教材', '學生', '環境']
# 理據表欄寬（cm）：類窄、項目中、內容吃滿剩下的版面，合計＝制式表寬度。
LEI_COL_CM = [1.4, 3.6, 13.4]


# ---------------------------------------------------------------- 工具

def detect_font(d):
    """回傳範本使用的字型名稱與 eastAsia 設定（通常是標楷體）。"""
    name = None
    for p in d.paragraphs:
        for r in p.runs:
            if r.font.name:
                name = r.font.name
                break
        if name:
            break
    ea = None
    rpr = d.styles['Normal'].element.find(qn('w:rPr'))
    if rpr is not None:
        rf = rpr.find(qn('w:rFonts'))
        if rf is not None:
            ea = rf.get(qn('w:eastAsia'))
    return name, ea


class Filler:
    def __init__(self, template, out_dir='.', no_img=False):
        self.out_dir = out_dir
        self.no_img = no_img          # --無圖：略過所有課本圖，產版控用的無圖版
        self.d = docx.Document(template)
        self.font, self.ea = detect_font(self.d)

    # ---- 低階 ----
    def _style(self, run, bold=False):
        if self.font:
            run.font.name = self.font
        if self.ea:
            run._element.get_or_add_rPr().get_or_add_rFonts().set(qn('w:eastAsia'), self.ea)
        run.bold = bold

    def cell(self, cell, lines, bold=False):
        """清空儲存格後逐行寫入。lines 可為字串或字串串列（空字串＝空行）。"""
        if isinstance(lines, str):
            lines = [lines]
        ps = cell.paragraphs
        for p in ps[1:]:
            p._element.getparent().remove(p._element)
        p0 = ps[0]
        for r in list(p0.runs):
            r._element.getparent().remove(r._element)
        p0.paragraph_format.space_after = Pt(0)
        # 串列元素可以是 {"圖": 路徑, "寬cm": 6, "說明": "圖說"}：把課本圖夾在文字中間，
        # 讓「各自觀看甘蔗吸管圖片」這類活動旁邊就看得到那張圖。
        first = True
        for ln in lines:
            if isinstance(ln, dict):
                if self.no_img or not self._img_path(ln['圖']):
                    continue
                self.picture(cell, self._img_path(ln['圖']), ln.get('寬cm', 6))
                if ln.get('說明'):
                    pc = cell.add_paragraph()
                    pc.paragraph_format.space_after = Pt(4)
                    pc.alignment = 1
                    self._style(pc.add_run(ln['說明']))
                continue
            np = p0 if first else cell.add_paragraph()
            first = False
            np.paragraph_format.space_after = Pt(0)
            self._style(np.add_run(ln), bold)
        if first:                       # 全是被略過的圖，留一個空段落
            self._style(p0.add_run(''), bold)

    def _img_path(self, src):
        """相對路徑以輸出 docx 的目錄為準；找不到就回 None 並提醒（課本圖不進版控，可能不在）。"""
        if not os.path.isabs(src):
            cand = os.path.join(self.out_dir, src)
            src = cand if os.path.exists(cand) else src
        if not os.path.exists(src):
            print(f'  ⚠️ 找不到圖，已略過：{src}')
            return None
        return src

    def picture(self, cell, png, width_cm):
        """在儲存格末尾加一張置中的圖。"""
        p = cell.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        p.alignment = 1
        p.add_run().add_picture(png, width=Cm(width_cm))
        return p

    @staticmethod
    def col_widths(t, cms):
        """固定表格欄寬（Word 只認 tblLayout=fixed ＋ 每格 w:tcW）。"""
        pr = t._element.tblPr
        el = OxmlElement('w:tblLayout')
        el.set(qn('w:type'), 'fixed')
        pr.append(el)
        t.autofit = False
        for row in t.rows:
            seen = set()
            i = 0
            for c in row.cells:
                if id(c._tc) in seen:
                    continue
                seen.add(id(c._tc))
                c.width = Cm(cms[min(i, len(cms) - 1)])
                i += 1

    def para(self, p, text):
        """就地改寫既有段落，保留原格式。"""
        for r in list(p.runs)[1:]:
            r._element.getparent().remove(r._element)
        if p.runs:
            p.runs[0].text = text
        else:
            self._style(p.add_run(text))

    def new_table(self, anchor, rows, cols, after=True):
        t = self.d.add_table(rows=rows, cols=cols)
        try:
            t.style = self.d.styles['Table Grid']
        except KeyError:
            pass
        el = t._element
        el.getparent().remove(el)
        (anchor.addnext if after else anchor.addprevious)(el)
        return t

    def new_para(self, anchor, text, after=True, bold=True):
        p = self.d.add_paragraph()
        self._style(p.add_run(text), bold=bold)
        el = p._element
        el.getparent().remove(el)
        (anchor.addnext if after else anchor.addprevious)(el)
        return p

    @staticmethod
    def distinct(row):
        """回傳該列實際的儲存格數（合併後會少於欄數）。"""
        return len({id(c._tc) for c in row.cells})

    def grid(self, rows, cols, header, data, anchor, title=None):
        """在 anchor 之後插入一張含表頭的表（可選一行標題段落）。"""
        t = self.new_table(anchor, rows, cols)
        for i, h in enumerate(header):
            self.cell(t.rows[0].cells[i], h, bold=True)
        for i, row in enumerate(data, 1):
            for j, v in enumerate(row):
                self.cell(t.rows[i].cells[j], v)
        if title:
            self.new_para(anchor, title)
        return t


# ---------------------------------------------------------------- 主流程

def build(content, template, out, no_img=False):
    f = Filler(template, os.path.dirname(os.path.abspath(out)), no_img)
    d = f.d
    c = content
    T = d.tables
    ps = d.paragraphs

    # 表頭
    h = c['表頭']
    f.para(ps[0], h['標題'])
    f.para(ps[1], f"授課年級：{h['授課年級']}　　　　　　授課日期：{h['授課日期']}")
    f.para(ps[2], f"任教學科：{h['任教學科']}　　　　　　教 學 者（教案設計）：{h['教學者']}")
    f.para(ps[3], f"單元名稱：{h['單元名稱']}　　備課成員：{h['備課成員']}")
    f.para(ps[4], f"使用版本：{h['使用版本']}")

    # 教學設計理念
    f.cell(T[0].rows[1].cells[0], c['教學設計理念'])

    # 核心素養（最多兩列）
    for i, item in enumerate(c['核心素養'][:2]):
        f.cell(T[1].rows[2 + i].cells[0], item['總綱'])
        f.cell(T[1].rows[2 + i].cells[1], item['領綱'])

    # 領域課程綱要（二維表：橫軸學習表現 × 縱軸學習內容 → 交會處整合出學習目標）
    # ⚠️ r1c0 是斜線表頭，本身就印著三個標籤，**不要覆寫**。
    # ⚠️ 每列只有 2 個實際格（舊版範本是 3 欄且 r2 後兩欄合併，寫入位置相同）。
    g = c['領域課程綱要']
    biao = g['學習表現']
    biao = [biao] if isinstance(biao, str) else list(biao)
    f.cell(T[2].rows[1].cells[1], biao[:2])              # 橫軸：學習表現（最多 2 條）
    f.cell(T[2].rows[2].cells[0], g['學習內容'])          # 縱軸：學習內容
    f.cell(T[2].rows[2].cells[1], list(g['學習目標']))    # 交會處：學習目標

    # 教材組織與學生分析（三小段，各自保留原有的「一、二、三」抬頭）
    # JSON 鍵沿用舊名，抬頭一律取範本原文（現行範本是「三、特殊學生特性描述：」）
    for i, key in enumerate(['文本結構分析', '學習困難及發現', '部份學生特性'], 1):
        cell = T[3].rows[i].cells[0]
        head = cell.paragraphs[0].text.strip()
        val = c['教材組織與學生分析'][key]
        # 文本結構分析可寫成 {"圖": {...}, "文字": [...]}：抬頭之後先擺圖，文字只當補充。
        if isinstance(val, dict):
            f.cell(cell, [head] + list(val.get('文字', [])))
            spec = val.get('圖')
            if spec and render_structure:
                png = os.path.join(os.path.dirname(os.path.abspath(out)),
                                   '文本結構圖.png')
                render_structure(spec, png)
                # 圖插在抬頭那一段之後，文字敘述之前
                pic = f.picture(cell, png, 17.4)
                cell.paragraphs[0]._element.addnext(pic._element)
        else:
            f.cell(cell, [head] + list(val))

    # 教學設計理據 12 項（制式表沒有，另插）
    # 依「教師→教材→學生→環境」四大類排序，同類的「類」欄縱向合併成一格。
    if c.get('教學設計理據'):
        items = sorted(c['教學設計理據'],
                       key=lambda r: (LEI_ORDER.index(r['類'])
                                      if r['類'] in LEI_ORDER else len(LEI_ORDER)))
        t = f.grid(len(items) + 1, 3, ['類', '項目', '內容'],
                   [[r['類'], r['項目'], r['內容']] for r in items],
                   T[3]._element, title='教學設計理據')
        f.col_widths(t, LEI_COL_CM)
        start = 0
        for k in range(1, len(items) + 1):
            if k == len(items) or items[k]['類'] != items[start]['類']:
                if k - start > 1:
                    merged = t.cell(start + 1, 0).merge(t.cell(k, 0))
                    f.cell(merged, items[start]['類'])
                start = k

    # 各節次重點
    f.cell(T[4].rows[0].cells[0], c['各節次重點']['標題'], bold=True)
    f.cell(T[4].rows[1].cells[0], c['各節次重點']['內容'])

    # 流程表
    for ri, seg in enumerate(c['流程'], 1):
        f.cell(T[5].rows[ri].cells[0], [seg['流程'], seg['主軸']], bold=True)
        f.cell(T[5].rows[ri].cells[1], seg['教學活動內容'])
        f.cell(T[5].rows[ri].cells[2], seg['教師支援'])
        f.cell(T[5].rows[ri].cells[3], seg['時間'], bold=True)

    # 理答預想表 + 彈性條款（制式表沒有，另插）
    if c.get('理答預想表'):
        f.grid(len(c['理答預想表']) + 1, 4,
               ['預想的學生回應', '判讀', '策略', '教師台詞'],
               [[r['回應'], r['判讀'], r['策略'], r['台詞']] for r in c['理答預想表']],
               T[5]._element, title=c.get('理答預想表標題', '附錄：理答預想表'))
    if c.get('彈性條款'):
        f.new_para(T[5]._element, c['彈性條款'], bold=False)

    # 觀課資訊
    for i, v in enumerate(c['觀課資訊']):
        f.cell(T[6].rows[i].cells[1], v)

    # 觀課重點（插在範本「觀課重點」段落之後）
    for p in d.paragraphs:
        if p.text.strip() == '觀課重點':
            for txt in reversed(c['觀課焦點']):
                f.new_para(p._element, txt, bold=False)
            break

    # 附件（制式表沒有，接在文件最後；例如公開課要附上的課文全文、課本圖）
    # JSON: "附件": [{"標題":..., "說明":..., "段落":[...], "圖":[...], "表":[...]}]
    # 排版順序：標題 → 說明 → 段落 → 圖 → 表
    for i, att in enumerate(c.get('附件') or []):
        p = d.add_paragraph()
        p.add_run().add_break(WD_BREAK.PAGE)          # 附件另起一頁
        f._style(p.add_run(att['標題']), bold=True)
        if att.get('說明'):
            f._style(d.add_paragraph().add_run(att['說明']))
        for line in att.get('段落') or []:
            if isinstance(line, dict):          # 段落中夾圖，格式同流程表
                src = None if f.no_img else f._img_path(line['圖'])
                if src:
                    pi = d.add_paragraph()
                    pi.paragraph_format.space_after = Pt(2)
                    pi.alignment = 1
                    pi.add_run().add_picture(src, width=Cm(line.get('寬cm', 6)))
                    if line.get('說明'):
                        pc = d.add_paragraph()
                        pc.alignment = 1
                        f._style(pc.add_run(line['說明']))
                continue
            np = d.add_paragraph()
            np.paragraph_format.space_after = Pt(0)
            f._style(np.add_run(line))
        # 附件也可以放圖（例如公開課要附上的課本天氣圖、示意圖）
        # {"檔": 路徑, "寬cm": 15, "說明": "圖說"}；路徑可為絕對，或相對輸出 docx 的目錄
        for im in att.get('圖') or []:
            src = None if f.no_img else f._img_path(im['檔'])
            if not src:
                continue
            pi = d.add_paragraph()
            pi.paragraph_format.space_after = Pt(2)
            pi.alignment = 1
            pi.add_run().add_picture(src, width=Cm(im.get('寬cm', 15)))
            if im.get('說明'):
                pc = d.add_paragraph()
                pc.alignment = 1
                f._style(pc.add_run(im['說明']))

        # 附件也可以放表格（例如學習單的填寫格）
        # {"標題":..., "欄寬":[cm,...], "列":[[格,...],...], "表頭":bool, "列高":cm}
        for tb in att.get('表') or []:
            if tb.get('標題'):
                f._style(d.add_paragraph().add_run(tb['標題']), bold=True)
            rows = tb['列']
            t = d.add_table(rows=len(rows), cols=len(rows[0]))
            try:
                t.style = d.styles['Table Grid']
            except KeyError:
                pass
            for ri, row in enumerate(rows):
                for ci, val in enumerate(row):
                    f.cell(t.rows[ri].cells[ci], val,
                           bold=(ri == 0 and tb.get('表頭')))
                if tb.get('列高') and not (ri == 0 and tb.get('表頭')):
                    t.rows[ri].height = Cm(tb['列高'])
            if tb.get('欄寬'):
                f.col_widths(t, tb['欄寬'])
            d.add_paragraph()

    d.save(out)
    return out


def inspect(template):
    """列出範本的段落與表格結構，改版時先跑這個確認幾何。"""
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    d = docx.Document(template)
    ti = 0
    for ch in d.element.body.iterchildren():
        if ch.tag.endswith('}p'):
            t = Paragraph(ch, d).text.strip()
            if t:
                print('P:', t[:70])
        elif ch.tag.endswith('}tbl'):
            tb = Table(ch, d)
            print(f'T[{ti}] {len(tb.rows)}x{len(tb.columns)}')
            for ri, r in enumerate(tb.rows):
                mark = '' if Filler.distinct(r) == len(r.cells) else f'  ⚠️合併(實際 {Filler.distinct(r)} 格)'
                print(f'   r{ri}: ' + ' || '.join(
                    c.text.strip().replace(chr(10), '⏎')[:26] for c in r.cells) + mark)
            ti += 1


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--inspect':
        inspect(sys.argv[2])
    elif '--無圖' in sys.argv or len(sys.argv) in (4, 6):
        no_img = '--無圖' in sys.argv
        argv = [a for a in sys.argv if a != '--無圖']
        with open(argv[1], encoding='utf-8') as fh:
            data = json.load(fh)
        if len(argv) == 6:
            if argv[4] != '--附件':
                print(__doc__)
                sys.exit(1)
            with open(argv[5], encoding='utf-8') as fh:
                extra = json.load(fh)
            for k, v in extra.items():
                # 附件是串接不是覆寫：主 JSON 的學習單在前，外掛的課文在後。
                if isinstance(v, list) and isinstance(data.get(k), list):
                    data[k] = data[k] + v
                else:
                    data[k] = v
        print('已輸出:', build(data, argv[2], argv[3], no_img=no_img))
    else:
        print(__doc__)
        sys.exit(1)
