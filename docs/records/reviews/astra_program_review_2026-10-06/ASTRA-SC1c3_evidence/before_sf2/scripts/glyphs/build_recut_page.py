"""Static review page for a recut_real.py run: per line, the page context (text-layer box in red, the fixed boundary of
every output line in green), the stored text-layer crop, and the output line(s) with the step that changed them.
Usage: build_recut_page.py RUN_DIR OUT.html [N_LINES]"""
import base64, html, io, json, random, sys, time
from collections import Counter
from pathlib import Path

from PIL import Image

RUN, OUT = Path(sys.argv[1]), Path(sys.argv[2])
N = int(sys.argv[3]) if len(sys.argv) > 3 else 220
OWNER = ['s2-60f24a3d8a2d714767f2-p00003-l00024', 's2-49598b2e848ab1f0ee1e-p00001-l00054',
         's2-3229200bf47ca465a42d-p00004-l00018', 's2-86865c33eef5932c013b-p00005-l00020',
         's2-7534648e60694be1d180-p00023-l00011', 's2-200e977f2dab5291c42c-p00035-l00002',
         's2-b1ce8959da62cc55c839-p00009-l00068', 's2-74cdb23a34ca4a6cd01e-p00002-l00048',
         's2-74cdb23a34ca4a6cd01e-p00010-l00018', 's2-49598b2e848ab1f0ee1e-p00001-l00043']


def jpg(path: Path, max_w: int, q: int = 55, mode: str = 'L') -> tuple[str, int, int]:
    im = Image.open(path).convert(mode)
    if im.width > max_w:
        im = im.resize((max_w, max(1, round(im.height * max_w / im.width))), Image.LANCZOS)
    b = io.BytesIO()
    im.save(b, 'JPEG', quality=q, optimize=True)
    return base64.b64encode(b.getvalue()).decode(), im.width, im.height


rows = [json.loads(l) for l in open(RUN / 'meta.jsonl')]
ok = [r for r in rows if 'lines' in r]
err = [r for r in rows if 'lines' not in r]
lines = [l for r in ok for l in r['lines']]
c_sides = Counter(s for l in lines for s in l['cut_sides'])
n_unchanged = sum(not any(l['fixed'] for l in r['lines']) for r in ok)
n_multi = sum(sum(l['kind'] == 'main' for l in r['lines']) > 1 for r in ok)
n_split = sum(any(l['kind'] == 'split' for l in r['lines']) for r in ok)
ext = [l['added'][0] / l['xh'] for l in lines if l['added'][0] > 0] + [l['added'][1] / l['xh'] for l in lines if l['added'][1] > 0]
stops = Counter(s for l in lines for s in l['stops'] if s != 'box')

by_id = {r['line_id']: r for r in ok}
rng = random.Random(8)
pool = list(ok)
rng.shuffle(pool)
picked, seen = [], set()


def take(cond, label, n):
    got = 0
    for r in pool:
        if got >= n:
            break
        if r['line_id'] in seen or not cond(r):
            continue
        picked.append((r, label)); seen.add(r['line_id']); got += 1


for lid in OWNER:
    if lid in by_id:
        picked.append((by_id[lid], 'Your case')); seen.add(lid)
sides = lambda r: {s for l in r['lines'] for s in l['cut_sides']}
take(lambda r: any(l['kind'] == 'split' for l in r['lines']), 'Box held a second line: split', 25)
take(lambda r: sum(l['kind'] == 'main' for l in r['lines']) > 1, 'Box held two columns: split at the rule / gap', 20)
take(lambda r: {'left', 'right'} & sides(r), 'Line continued past the box left / right: extended', 30)
take(lambda r: {'top', 'bottom'} <= sides(r), 'Cut at top and bottom: boundary follows the curve', 25)
take(lambda r: sides(r) == {'top'}, 'Cut at the top only', 35)
take(lambda r: sides(r) == {'bottom'}, 'Cut at the bottom only', 20)
take(lambda r: not any(l['fixed'] for l in r['lines']), 'Not cut off: box kept', 40)
take(lambda r: True, 'Other', max(0, N - len(picked)))

CSS = (Path(__file__).parent / 'final_page.html').read_text().split('<style>')[1].split('</style>')[0]
out = [f'<title>Page Line Fix</title>', '<link rel="preconnect" href="https://fonts.googleapis.com">',
       '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Serif:wght@500&display=swap">',
       '<style>' + CSS + '''
.pics { display: grid; gap: 8px; }
.pics figure { margin: 0; display: grid; gap: 3px; min-width: 0; }
.pics figcaption { font-size: .75rem; color: var(--muted); font-family: var(--font-data); }
.pics img { display: block; max-width: 100%; height: auto; border: 1px solid var(--rule); background: var(--surface); }
.layer { font-size: .85rem; color: var(--muted); overflow-wrap: anywhere; }
.chip.ok { border-color: var(--accent); color: var(--accent); }
.chip.fix { border-color: var(--under); color: var(--under); }
.chip.split { border-color: var(--second); color: var(--second); }
</style>''', '<div class="wrap">', '<header class="intro">', '<h1>Page Line Fix</h1>',
       '<p>Whole-page line geometry for real parliament scans, from the text-layer boxes: every box on the page is fitted; '
       'boxes holding more than one line are split; where a line runs past its box, the boundary follows the line — '
       'along its curve or slant at the top and bottom, letter by letter to the left and right until the page edge, a wide gap or a column rule. '
       'Neighbouring lines bound each other, so an output line carries no ink of the lines around it. Lines that are not cut off keep their box.</p>',
       '<p class="muted">Red: the text-layer box. Green: the boundary of each output line. The text layer is shown only to identify the line; it is another OCR, not a reference.</p>',
       '<div class="summary">']
for v, lab in ((len(ok), f'lines on {len({r["page_key"] for r in ok})} pages'), (n_unchanged, 'not cut off: box kept'),
               (c_sides['top'], 'cut at the top'), (c_sides['bottom'], 'cut at the bottom'),
               (c_sides['left'] + c_sides['right'], 'line ends cut (left / right)'), (n_multi, 'boxes split into columns'),
               (n_split, 'boxes holding a second line'), (len(err), 'errors')):
    out.append(f'<div><b>{v}</b>{html.escape(lab)}</div>')
out.append('</div>')
med = sorted(ext)[len(ext) // 2] if ext else 0
out.append(f'<p class="muted">Sideways extensions: {len(ext)} line ends, median {med:.1f} letter heights; stops: '
           + ', '.join(f'{k.replace("_", " ")} {v}' for k, v in stops.most_common()) + f'. Built {time.strftime("%Y-%m-%d %H:%M")}; {len(picked)} lines shown.</p>')
out.append('</header>')
last = None
for r, label in picked:
    lid = r['line_id']
    if label != last:
        out.append(f'<section class="section-head"><h2>{html.escape(label)}</h2></section>'); last = label
    chips = []
    for n, l in enumerate(r['lines']):
        cls = 'split' if l['kind'] == 'split' else ('fix' if l['fixed'] else 'ok')
        txt = ('second line' if l['kind'] == 'split' else f'line {n + 1}') + ': ' + ('; '.join(l['reason']) if l['fixed'] else 'box kept')
        chips.append(f'<span class="chip {cls}">{html.escape(txt)}</span>')
        if l['added'][0] or l['added'][1]:
            chips.append(f'<span class="chip">+{l["added"][0]} px left · +{l["added"][1]} px right · stops {l["stops"][0].replace("_", " ")} / {l["stops"][1].replace("_", " ")}</span>')
    img = RUN / 'img'
    ctx, cw, ch = jpg(img / f'{lid}.context.jpg', 1000, 50, 'RGB')
    org, ow, oh = jpg(img / f'{lid}.orig.png', 1200, 50)
    figs = [f'<figure><img loading="lazy" src="data:image/jpeg;base64,{ctx}" width="{cw}" height="{ch}" alt="page context"><figcaption>page: text-layer box (red), output lines (green)</figcaption></figure>',
            f'<figure><img loading="lazy" src="data:image/jpeg;base64,{org}" width="{ow}" height="{oh}" alt="text-layer crop"><figcaption>text-layer crop (before)</figcaption></figure>']
    for n, l in enumerate(r['lines']):
        p = img / f'{lid}.line{n}.png'
        if not p.exists():
            continue
        b, w, h = jpg(p, 1200, 50)
        what = 'straightened along its curve, own ink only' if l['fixed'] else 'unchanged box'
        figs.append(f'<figure><img loading="lazy" src="data:image/jpeg;base64,{b}" width="{w}" height="{h}" alt="output line"><figcaption>output {n + 1} ({l["kind"]}): {what}</figcaption></figure>')
    feat = ' featured' if label == 'Your case' else ''
    out.append(f'<article class="line{feat}"><div class="head"><span class="id">{lid}</span><span class="label">{html.escape(label)}</span></div>'
               f'<div class="chips">{"".join(chips)}</div><div class="pics">{"".join(figs)}</div>'
               f'<p class="layer">text layer: {html.escape(r.get("text") or "")}</p></article>')
out.append('</div>')
OUT.write_text('\n'.join(out))
print(f'{len(picked)} lines; {OUT.stat().st_size / 1e6:.1f} MB')
