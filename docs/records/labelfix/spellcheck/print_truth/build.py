"""Blind print-truth adjudication items: every Google-vs-human mark difference on the three-way lines (seed-0 census, 189)
plus 20 planted controls (Google = human = model; the alternative is a one-mark swap). Each item = one PNG
(full line with the word boxed, word zoom x4, vowel zoom x8) and two alternatives A/B in random order."""
import json, random, sys
from PIL import Image, ImageDraw
from greekocr.labelfix.candidates import pair_tokens
from greekocr.labelfix.ctc_align import transfer_alignment
from greekocr.labelfix.sheet import load_alignments, crop_key
from greekocr.labelfix.spellink import locate
from greekocr.labelfix.text import MARK_BEARERS, clusters, nfc, nfd, tokenize
from greekocr.labelfix.validate import DEV_BOOKS, TOOLKIT, load_three_way

OUT = sys.argv[1]
rng = random.Random(20261016)
L = {l['line_id']: l for l in load_three_way(0)}
A = load_alignments(TOOLKIT / '.cache/labelfix/align_s0.jsonl')
errs = [json.loads(x) for x in open(TOOLKIT / 'docs/labelfix/spellcheck/reach_s0.jsonl')]

def windows(l, wi, ci):
    al = A[crop_key(l['crop'])]
    if nfd(al.prediction) != l['model']:
        al = transfer_alignment(l['model'], al)
    g = tokenize(l['google'])[wi]
    m = dict((a.index, b) for a, b in pair_tokens(l['google'], l['model'])).get(wi)
    ww = al.window(m.start, m.end) if m else None
    loc = locate(g, m, al, ci) if (m is not None and ci is not None) else None
    return ww, (loc[3], loc[4]) if loc else None, al.char_width()

def card(l, wi, ci, path):
    im = Image.open(l['crop']).convert('RGB')
    w, h = im.size
    ww, vw, cw = windows(l, wi, ci)
    line = im.copy()
    d = ImageDraw.Draw(line)
    if ww:
        d.rectangle([ww[0] - 3, 0, ww[1] + 3, h - 1], outline=(220, 0, 0), width=3)
    scale = min(1.0, 1600 / w)
    line = line.resize((int(w * scale), int(h * scale)))
    parts = [line]
    if ww:
        x0, x1 = max(0, int(ww[0] - 1.5 * cw)), min(w, int(ww[1] + 1.5 * cw))
        z = im.crop((x0, 0, x1, h)); f = min(4, 1500 / max(1, z.size[0]))
        parts.append(z.resize((int(z.size[0] * f), int(h * f)), Image.LANCZOS))
    if vw:
        x0, x1 = max(0, int(vw[0] - 1.2 * cw)), min(w, int(vw[1] + 1.2 * cw))
        z = im.crop((x0, 0, x1, h)); f = min(8, 1500 / max(1, z.size[0]))
        parts.append(z.resize((int(z.size[0] * f), int(h * f)), Image.LANCZOS))
    W = max(p.size[0] for p in parts); H = sum(p.size[1] + 16 for p in parts)
    c = Image.new('RGB', (W, H), 'white'); y = 0
    for p in parts:
        c.paste(p, (0, y)); y += p.size[1] + 16
        ImageDraw.Draw(c).line([0, y - 8, W, y - 8], fill=(150, 150, 150), width=2)
    c.save(path)

def diff_cluster(a, b):
    ca, cb = clusters(nfd(a)), clusters(nfd(b))
    if len(ca) != len(cb):
        return None
    d = [i for i, (x, y) in enumerate(zip(ca, cb)) if x.marks != y.marks]
    return d[0] if len(d) == 1 else None

items, key = [], {}
for e in errs:
    items.append(dict(line_id=e['line_id'], w=e['word_index'], google=e['google'], human=e['human'], kind='diff'))
# planted controls
SWAP = {'́': '̀', '̀': '́', '̓': '̔', '̔': '̓', '͂': '́'}
pool = []
for l in L.values():
    if l['doc'] in DEV_BOOKS:
        continue
    gt = tokenize(l['google']); gh = dict((a.index, b) for a, b in pair_tokens(l['google'], l['human']))
    gm = dict((a.index, b) for a, b in pair_tokens(l['google'], l['model']))
    for g in gt:
        h, m = gh.get(g.index), gm.get(g.index)
        if g.core and h is not None and m is not None and g.core == h.core == m.core and len(g.core) >= 3:
            pool.append((l['line_id'], g.index, g.core))
rng.shuffle(pool)
for lid, wi, core in pool:
    if sum(1 for i in items if i['kind'] == 'control') >= 20:
        break
    cl = clusters(nfd(core))
    cand = [i for i, c in enumerate(cl) if any(m in SWAP for m in c.marks)]
    if not cand:
        continue
    i = cand[0]; c = cl[i]
    m = next(x for x in c.marks if x in SWAP)
    alt = ''.join(cc.base + (cc.marks.replace(m, SWAP[m]) if k == i else cc.marks) for k, cc in enumerate(cl))
    items.append(dict(line_id=lid, w=wi, google=nfc(core), human=nfc(core), alt=nfc(alt), kind='control'))
rng.shuffle(items)
public = []
for n, it in enumerate(items):
    iid = f'P{n:03d}'
    l = L[it['line_id']]
    other = it['alt'] if it['kind'] == 'control' else it['human']
    ci = diff_cluster(it['google'], other)
    card(l, it['w'], ci, f'{OUT}/img/{iid}.png')
    ab = [it['google'], other]
    if rng.random() < 0.5:
        ab.reverse()
    public.append(dict(id=iid, image=f'{OUT}/img/{iid}.png', A=nfc(ab[0]), B=nfc(ab[1])))
    key[iid] = dict(it, A=nfc(ab[0]), B=nfc(ab[1]), cluster=ci)
json.dump(public, open(f'{OUT}/items_public.json', 'w'), ensure_ascii=False, indent=0)
json.dump(key, open(f'{OUT}/key_SEALED.json', 'w'), ensure_ascii=False, indent=0)
print(len(public), sum(1 for k in key.values() if k['kind'] == 'control'))
