"""依 corrections.json 由 large-v3 清理版字幕產出 subtitles_final.srt 與 transcript_corrected.md。"""
import json, re, sys
from pathlib import Path

out = Path(sys.argv[1])
src = out / 'subtitles_clean_lv3.srt'
cfg = json.loads((out / 'corrections.json').read_text(encoding='utf-8'))

def ts2s(t):
    h, m, s = t.replace(',', '.').split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)

def s2ts(x):
    ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

cues = []
for block in re.split(r'\n\s*\n', src.read_text(encoding='utf-8').strip()):
    lines = block.strip().splitlines()
    if len(lines) < 3: continue
    a, b = [x.strip() for x in lines[1].split('-->')]
    cues.append([ts2s(a), ts2s(b), ' '.join(lines[2:]).strip()])

segs = [(ts2s(a), ts2s(b), c, t) for a, b, c, t in cfg['segments']]
unclear = [(ts2s(a), ts2s(b), note) for a, b, note in cfg['unclear_ranges']]
covered = segs + [(a, b, '', '') for a, b, _ in unclear]

def overlaps(c):
    return any(c[0] < b and c[1] > a for a, b, *_ in covered)

def split_text(t, n=26):
    parts = [p for p in re.split(r'(?<=[。？！，、：])', t) if p]
    lines, cur = [], ''
    for p in parts:
        if len(cur) + len(p) > n and cur:
            lines.append(cur); cur = p
        else:
            cur += p
    if cur: lines.append(cur)
    return lines

final = []
for c in cues:
    if overlaps(c): continue
    t = c[2]
    for a, b in cfg['terms']:
        t = t.replace(a, b)
    final.append([c[0], c[1], t])
for a, b, conf, t in segs:
    pieces = split_text(t)
    total = sum(len(p) for p in pieces)
    cur = a
    for p in pieces:
        dur = (b - a) * len(p) / total
        final.append([cur, cur + dur, p]); cur += dur
for a, b, note in unclear:
    final.append([a, min(a + 4, b), f'（{note}）'])
final.sort(key=lambda x: x[0])

srt = '\n\n'.join(f'{i}\n{s2ts(a)} --> {s2ts(b)}\n{t}' for i, (a, b, t) in enumerate(final, 1)) + '\n'
(out / 'subtitles_final.srt').write_text(srt, encoding='utf-8')

md = ['# 校正逐字稿（關鍵段落）', '',
      '> 來源：三源交叉比對＋課本 p.67–71＋31:45 黑板畫面。（…）＝聽不清楚；（ ）內為依上下文補足。',
      '> 可信度：高＝三源一致；中＝兩源一致或依教材語境推定。**引用前請確認可信度**；學生姓名已以角色代稱取代。', '',
      '| 時間 | 可信度 | 內容 |', '|---|---|---|']
rows = [(a, f'{s2ts(a)[3:8]}–{s2ts(b)[3:8]}', conf, t) for a, b, conf, t in segs]
rows += [(a, f'{s2ts(a)[3:8]}–{s2ts(b)[3:8]}', '—', f'*（{note}）*') for a, b, note in unclear]
for _, span, conf, t in sorted(rows):
    md.append(f'| {span} | {conf} | {t} |')
(out / 'transcript_corrected.md').write_text('\n'.join(md) + '\n', encoding='utf-8')
print(len(final), 'cues;', len(segs), 'corrected segments;', len(unclear), 'unclear ranges')
