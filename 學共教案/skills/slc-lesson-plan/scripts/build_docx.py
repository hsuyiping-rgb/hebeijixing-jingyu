# -*- coding: utf-8 -*-
"""把教案內容填進「公開課教案參考格式.docx」制式表，輸出可編輯的 .docx。

用法：
    python -X utf8 build_docx.py <內容.json> <範本.docx> <輸出.docx>

內容 JSON 的結構見同目錄 `教案內容.schema.md`，或參考實際範例
`教案成果/五年級_數學_折線圖_20260909/教案內容.json`。

⚠️ 一定要加 `-X utf8`，否則 Windows 下中文會變亂碼。

範本的已知結構（勿假設，改版時請先用 --inspect 重新確認）：
    P[0..4]  表頭五行
    T[0] 2x1  教學設計理念
    T[1] 4x2  核心素養（r0/r1 表頭，r2/r3 可填兩列）
    T[2] 3x3  領域課程綱要 ⚠️ 這是一張**二維表**，不是三個並排欄位：
              r1c0 是斜線表頭（內含「學習目標／學習表現／學習內容」三個標籤，**不要覆寫**）
              r1c1、r1c2 = 橫軸，填與本節公開課相關的「學習表現」（1~2 項）
              r2c0       = 縱軸，填本節重要的「學習內容」
              r2c1(=c2，合併儲存格) = 由前兩者整合而成的「學習目標」
    T[3] 4x1  教材組織與學生分析（r1/r2/r3 三小段）
    T[4] 2x1  各節次學習活動設計的重點
    T[5] 4x4  流程表（r1~r3 = 導入與發現／探究與深化／挑戰與聚斂）
    P        「公開授課觀課紀錄表」
    T[6] 6x3  觀課資訊
    P        「觀課重點」← 本課觀課焦點插在這一段之後
    T[7] 4x4  觀課紀錄表（留白）

制式表沒有「教學設計理據 12 項」與「理答預想表」，本腳本會另外插表。
"""
import json
import sys

import docx
from docx.oxml.ns import qn
from docx.shared import Pt


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
    def __init__(self, template):
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
        self._style(p0.add_run(lines[0]), bold)
        for ln in lines[1:]:
            np = cell.add_paragraph()
            np.paragraph_format.space_after = Pt(0)
            self._style(np.add_run(ln), bold)

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

def build(content, template, out):
    f = Filler(template)
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
    # ⚠️ r2 的第 2、3 欄是合併儲存格（整列只有 2 個實際格），學習目標寫進那一格。
    g = c['領域課程綱要']
    biao = g['學習表現']
    biao = [biao] if isinstance(biao, str) else list(biao)
    for i, item in enumerate(biao[:2]):                 # 橫軸：學習表現
        f.cell(T[2].rows[1].cells[i + 1], item)
    f.cell(T[2].rows[2].cells[0], g['學習內容'])          # 縱軸：學習內容
    f.cell(T[2].rows[2].cells[1], list(g['學習目標']))    # 交會處：學習目標

    # 教材組織與學生分析（三小段，各自保留原有的「一、二、三」抬頭）
    for i, key in enumerate(['文本結構分析', '學習困難及發現', '部份學生特性'], 1):
        head = T[3].rows[i].cells[0].paragraphs[0].text.strip()
        f.cell(T[3].rows[i].cells[0], [head] + list(c['教材組織與學生分析'][key]))

    # 教學設計理據 12 項（制式表沒有，另插）
    if c.get('教學設計理據'):
        f.grid(len(c['教學設計理據']) + 1, 3, ['類', '項目', '內容'],
               [[r['類'], r['項目'], r['內容']] for r in c['教學設計理據']],
               T[3]._element, title='教學設計理據')

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
    elif len(sys.argv) == 4:
        with open(sys.argv[1], encoding='utf-8') as fh:
            data = json.load(fh)
        print('已輸出:', build(data, sys.argv[2], sys.argv[3]))
    else:
        print(__doc__)
        sys.exit(1)
