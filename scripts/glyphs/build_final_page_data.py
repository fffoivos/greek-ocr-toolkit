"""Final review page data (owner 8 Oct 16:40: ≥ 200 lines): the owner's cases, then a stratified sample of the 444 real
crops by readability verdict and reason. Per line: the report record (per-column), the calibrated readability verdict
with reasons and x-ranges, and the straightened (tight) line images from the lines API. Crops as JPEG to stay < 16 MB.
Usage: build_final_page_data.py OUT.json   (then build_review_page.py OUT.json PAGE.html --template final_page.html)"""
import base64, glob, io, json, random, sys, time
from pathlib import Path

PKG = Path(__file__).resolve().parents[2]; OUT = Path(sys.argv[1])
sys.path.insert(0, str(PKG))
import numpy as np                                                     # noqa: E402
from PIL import Image                                                  # noqa: E402
import greekocr                                                        # noqa: E402
assert str(PKG) in greekocr.__file__, greekocr.__file__
from greekocr.glyphs.report import document_priors, document_of, line_record, needs_prior   # noqa: E402
from greekocr.glyphs.components import line_glyphs                     # noqa: E402
from greekocr.glyphs.readability import readability                    # noqa: E402
from greekocr.glyphs.lines_api import separate_lines                   # noqa: E402

FIX = PKG / 'tests' / 'fixtures'
STEP = 12


def jpeg(im: Image.Image, q: int = 50) -> str:
    b = io.BytesIO(); im.convert('L').save(b, 'JPEG', quality=q, optimize=True)
    return base64.b64encode(b.getvalue()).decode()


def thin(rec: dict) -> dict:
    """Keep every 2nd sample of the (step-4) arrays → step 8; drop fields the page does not draw."""
    def every2(v):                          # step-4 samples → every 3rd → step 12
        return v[::3] + ([v[-1]] if (len(v) - 1) % 3 else [])
    for seg in rec['segments']:
        for key in ('baseline', 'meanline', 'visible'):
            seg[key] = every2(seg[key])
        for L in seg['lines']:
            for key in ('ascender', 'mean', 'base', 'descender'):
                L[key] = every2(L[key])
    rec['step'] = STEP
    for key in ('letters', 'cut_spans', 'cut_letters', 'lines'):
        rec.pop(key, None)                   # flattened copies: the page draws from segments
    return rec


t0 = time.time()
pool = sorted(glob.glob(str(FIX / 'o4d_sample400/crops/*.png'))) + sorted(glob.glob(str(FIX / 'o4d_lines/line*.png'))) \
    + sorted(glob.glob(str(FIX / 'o4d_lines/regressions/*_old.png')))
priors = document_priors(pool)
recs = {}
for p in pool:
    im = Image.open(p); doc = document_of(Path(p).name)
    pr = priors[doc]['xh'] if doc in priors and needs_prior(line_glyphs(im)) else None
    rd = readability(im, xh_prior=pr)
    recs[p] = (pr, rd)
print(len(recs), 'crops judged in', round(time.time() - t0, 1), 's', file=sys.stderr)

owner = ['o4d_lines/regressions/s2-60f24a3d8a2d714767f2-p00003-l00024_old.png', 'o4d_lines/line04_medium.png',
         'o4d_lines/line08_medium.png', 'o4d_sample400/crops/s2-49598b2e848ab1f0ee1e-p00001-l00054.png',
         'o4d_sample400/crops/s2-3229200bf47ca465a42d-p00004-l00018.png', 'o4d_sample400/crops/s2-86865c33eef5932c013b-p00005-l00020.png',
         'o4d_sample400/crops/s2-7534648e60694be1d180-p00023-l00011.png', 'o4d_sample400/crops/s2-200e977f2dab5291c42c-p00035-l00002.png',
         'o4d_sample400/crops/s2-b1ce8959da62cc55c839-p00009-l00068.png', 'o4d_sample400/crops/s2-74cdb23a34ca4a6cd01e-p00002-l00048.png',
         'o4d_sample400/crops/s2-74cdb23a34ca4a6cd01e-p00010-l00018.png', 'o4d_sample400/crops/s2-49598b2e848ab1f0ee1e-p00001-l00043.png']
owner = [str(FIX / o) for o in owner]
lid = lambda p: Path(p).stem.replace('_old', '')
chosen, picks = set(), []
for p in owner:
    picks.append((p, 'owner', 'Your case')); chosen.add(lid(p))
rng = random.Random(8)
rest = [p for p in pool if lid(p) not in chosen and not p.endswith('_old.png')]
rng.shuffle(rest)


def take(cond, label, n):
    got = 0
    for p in rest:
        if got >= n:
            break
        if lid(p) in chosen or not cond(recs[p][1]):
            continue
        picks.append((p, 'sample', label)); chosen.add(lid(p)); got += 1


R = lambda key: (lambda r: any(s['reason'] == key for s in r.spans))
take(lambda r: r.verdict == 'unreadable', 'Unreadable', 20)
take(R('top_cut'), 'Letter bodies cut at the top', 20)
take(R('bottom_cut'), 'Letter bodies cut at the bottom', 10)
take(R('tail_cut'), 'Tails cut at the bottom', 10)
take(lambda r: r.verdict == 'partly' and R('accent_cut')(r), 'Accents / tall letters cut at the top', 45)
take(lambda r: len(r.measures['segments']) > 1, 'Two columns in the crop', 20)
take(lambda r: r.target == 'ambiguous' and len(r.measures['segments']) == 1, 'Several full lines in the crop', 25)
take(lambda r: r.verdict == 'readable' and r.target == 'clear', 'Readable, clear target', 80)
take(lambda r: r.verdict == 'partly', 'Partly readable (other)', 15)
print(len(picks), 'lines picked', file=sys.stderr)

lines = []
for p, section, label in picks:
    pr, rd = recs[p]
    doc = document_of(Path(p).name)
    rec = line_record(p, priors={doc: priors[doc]} if pr else None)
    rec = thin(rec)
    rec['png'] = jpeg(Image.open(p)); rec['img_type'] = 'jpeg'
    rec.update(section=section, label=label,
               readability=dict(verdict=rd.verdict, target=rd.target, reasons=rd.reasons, spans=rd.spans,
                                over_share=rd.measures['over_share']))
    straight = []
    for L in [l for l in (separate_lines(Image.open(p), xh_prior=pr, tight=True) if pr else separate_lines(Image.open(p), tight=True)) if l.side == 'main']:
        straight.append(dict(segment=L.segment, side=L.side, shift_xh=round(L.shift_xh, 2), x0=L.x0, x1=L.x1,
                             w=L.image.width, h=L.image.height, jpg=jpeg(L.image, 45),
                             top_cut=round(float(L.top_cut.mean()), 3), bottom_cut=round(float(L.bottom_cut.mean()), 3)))
    rec['straightened'] = straight
    lines.append(rec)
counts = {}
for p, (pr, rd) in recs.items():
    if p.endswith('_old.png'):
        continue
    counts[rd.verdict] = counts.get(rd.verdict, 0) + 1
json.dump(dict(built=time.strftime('%Y-%m-%d %H:%M'), mode='final', pool=sum(counts.values()), verdict_counts=counts,
               lines=lines), open(OUT, 'w'), ensure_ascii=False, allow_nan=False)
print(len(lines), 'lines;', round(OUT.stat().st_size / 1e6, 1), 'MB;', round(time.time() - t0, 1), 's', file=sys.stderr)
