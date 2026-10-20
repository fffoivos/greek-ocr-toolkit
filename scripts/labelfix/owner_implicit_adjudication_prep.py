import json, re, html, random, sys, unicodedata as ud
from pathlib import Path
from PIL import Image
from greekocr.labelfix.text import nfd, clusters, tokenize
from greekocr.labelfix.sheet import load_alignments, crop_key
from greekocr.labelfix.validate import load_three_way
from greekocr.labelfix.ctc_align import transfer_alignment
S = sys.argv[1]; rnd = random.Random(20261016)
line_map = {l['line_id']: l for l in load_three_way(0)}
aligns = load_alignments(Path('.cache/labelfix/align_s0.jsonl'))
def cards(f):
    s = open(f).read()
    return {l: html.unescape(re.sub('<[^>]+>', '', o)) for l, o in re.findall(r'<div class="lid">(.*?)</div>.*?<th>Ours</th><td>(.*?)</td>', s, re.S)}
O4 = {**cards(f'{S}/s4_examples.html'), **cards(f'{S}/s4_review.html')}
O6 = {**cards(f'{S}/options_examples.html'), **cards(f'{S}/owner_sheet.html')}
rows = [r for r in json.load(open(f'{S}/implicit_regressions_s6.json')) if r['kind'].startswith('REGRESSION')]
def word_box(lid, wi):
    ln = line_map[lid]; text = nfd(ln['model']); al = aligns[crop_key(ln['crop'])]
    if nfd(al.prediction) != text: al = transfer_alignment(text, al)
    toks = [t for t in tokenize(text)]
    t = toks[wi]; x0, _ = al.window(t.start, t.start + 1); _, x1 = al.window(t.end - 1, t.end)
    return x0, x1
items, seen = [], set()
for r in rows:
    lid = r['line']; w4, w6 = O4[lid].split(), O6[lid].split()
    for wi, (a, b) in enumerate(zip(w4, w6)):
        if a == b or (lid, wi) in seen: continue
        seen.add((lid, wi))
        items.append(dict(line=lid, word=wi, s4=a, s6=b, note=r['note'], control=False))
# planted controls: Google word == human word (and recogniser letters agree) -> truth; fake = one mark removed or acute<->grave swapped
ctrl = 0
for lid in sorted(set(O4)):
    if ctrl >= 8: break
    ln = line_map[lid]; gw, hw, mw = [ud.normalize('NFC', ln[k]).split() for k in ('google', 'human', 'model')]
    if not (len(gw) == len(hw) == len(mw)): continue
    for wi, (g, h) in enumerate(zip(gw, hw)):
        if g == h and len(g) > 3 and g.isalpha() and any(ud.category(ch) == 'Mn' for ch in nfd(g)):
            d = nfd(g); i = next(k for k, ch in enumerate(d) if ud.category(ch) == 'Mn')
            sw = {'́': '̀', '̀': '́'}
            fake = d[:i] + (sw[d[i]] if d[i] in sw and ctrl % 2 else '') + d[i + 1:]
            items.append(dict(line=lid, word=wi, s4=ud.normalize('NFC', d), s6=ud.normalize('NFC', fake), note='', control=True)); ctrl += 1; break
out = []
for k, it in enumerate(items):
    try: x0, x1 = word_box(it['line'], it['word'])
    except Exception as e: print('skip', it['line'], e); continue
    im = Image.open(line_map[it['line']]['crop']).convert('RGB'); W, H = im.size
    pad = 0.6 * H; c = im.crop((max(0, int(x0 - pad)), 0, min(W, int(x1 + pad)), H))
    sc = min(3, 900 / max(1, c.width)); c = c.resize((int(c.width * sc), int(c.height * sc)), Image.LANCZOS)
    p = f'{S}/adj_s6/img/item{k:03d}.png'; c.save(p)
    full = f'{S}/adj_s6/img/line{k:03d}.png'; im.save(full)
    forms = [it['s4'], it['s6']]; rnd.shuffle(forms)
    out.append(dict(id=f'item{k:03d}', img=p, line_img=full, A=forms[0], B=forms[1], **it))
json.dump(out, open(f'{S}/adj_s6/items_key.json', 'w'), ensure_ascii=False, indent=1)
json.dump([dict(id=o['id'], img=o['img'], line_img=o['line_img'], A=o['A'], B=o['B']) for o in out], open(f'{S}/adj_s6/items_blind.json', 'w'), ensure_ascii=False, indent=1)
print(len(out), 'items,', sum(o['control'] for o in out), 'controls')
