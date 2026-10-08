"""Synthetic two-column pages with per-line ink truth; a tight, truncated 'text-layer' box per target line; measure
how much of the target line the original box and the recut keep, and how much foreign ink the recut output shows.
Usage: [HARD=1] synth_pages.py N_PAGES   (HARD: line pitch 0.98–1.1 × font size, page rotation ±3°)"""
import json, os, random, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from greekocr.glyphs.synthetic import render_truth_line, NEIGHBOUR      # noqa: E402
from greekocr.glyphs.recut import recut_page                                            # noqa: E402

HARD = bool(os.environ.get('HARD'))
FONTS = sorted((ROOT / 'tests/fixtures/fonts').glob('*.ttf'))
FONTS = [f for f in FONTS if any(k in f.name for k in ('Didot', 'Neohellenic', 'OldStandard', 'Gentium', 'Garamond'))] or FONTS
TEXT = ('ἀνδρώας κύστεως, μεταξὺ τῶν τῆς ἥβης καλουμένων ὀστῶν καθήκοντα γὰρ πονηρίας ἐρρίζωκεν ἐν αὐτῷ. καρδία '
        'συνετοῦ διανοηθήσεται παραβολήν πᾶν βρῶμα φάγεται κοιλία, ἔστι δὲ βρῶμα βρώματος κάλλιον ἐν τῇ ὁδῷ '
        'ἀνατομικὰ ἔσχον· ὅθεν οὐδ’ ἐκείνων μοι μέλει. περὶ δὲ τῶν ἀνδρῶν τούτων Ἡ Βουλὴ τῶν Ἑλλήνων ἀπεφάσισε').split()


def line_text(rng, n):
    i = rng.randrange(len(TEXT) - n)
    return ' '.join(TEXT[i:i + n])


def make_page(rng, font, size, sep):
    """Two columns of 6 lines; sep = 'rule' | 'gap'. Returns gray page, label map (line id per ink pixel), info, angle."""
    lo, hi = (0.98, 1.1) if HARD else (1.15, 1.35)
    pitch = int(size * rng.uniform(lo, hi))
    lines = []
    for col in range(2):
        for r in range(6):
            n = rng.randint(5, 8) if r < 5 else rng.randint(2, 4)          # last line of the paragraph short
            ren = render_truth_line(line_text(rng, n), font, size=size, degrade=False, pad=int(size * .6))
            lines.append((col, r, ren))
    colw = max(l[2].image.width for l in lines) + 10
    gapw = int(size * (1.6 if sep == 'rule' else 2.4))
    W = 60 + 2 * colw + gapw + 60
    H = 80 + 6 * pitch + 80
    page = np.full((H, W), 255.0)
    lab = np.zeros((H, W), np.int16)
    info = []
    for idx, (col, r, ren) in enumerate(lines, start=1):
        g = np.asarray(ren.image, np.float64)
        t = ren.truth
        bt = float(np.median(ren.base_truth))
        ox = 60 + col * (colw + gapw)
        oy = int(80 + r * pitch + pitch - bt)
        hh, ww = g.shape
        ya, yb = max(0, oy), min(H, oy + hh)
        src = slice(ya - oy, yb - oy)
        page[ya:yb, ox:ox + ww] = np.minimum(page[ya:yb, ox:ox + ww], g[src])
        m = ((t > 0) & (t != NEIGHBOUR))[src]
        sub = lab[ya:yb, ox:ox + ww]
        sub[m] = idx
        info.append(dict(id=idx, col=col, row=r, xh=ren.xh))
    if sep == 'rule':
        xr = 60 + colw + gapw // 2
        page[60:H - 60, xr:xr + 2] = 30
    ang = rng.uniform(-3, 3) if HARD else rng.uniform(-1.5, 1.5)
    im = Image.fromarray(page.astype(np.uint8)).rotate(ang, resample=Image.BICUBIC, fillcolor=255)
    im = im.filter(ImageFilter.GaussianBlur(.6))
    arr = np.asarray(im, np.float64) + np.random.default_rng(rng.randrange(1 << 30)).normal(0, 4, (H, W))
    labr = np.asarray(Image.fromarray(lab).rotate(ang, resample=Image.NEAREST, fillcolor=0))
    return np.clip(arr, 0, 255), labr, info, ang, pitch


def tight_box(lab, lid, xh, rng):
    """A text-layer-like box: axis-aligned around the whole (possibly skewed) line's letter bodies — from the highest
    mean line to the lowest baseline + 0.35 x-heights, so accents and tall tops are cut — truncated left/right at random."""
    ys, xs = np.nonzero(lab == lid)
    edges = np.linspace(xs.min(), xs.max() + 1, 9)
    bases = [np.percentile(ys[(xs >= a) & (xs < b)], 80) for a, b in zip(edges[:-1], edges[1:]) if ((xs >= a) & (xs < b)).sum() > 20]
    y0 = int(min(bases) - 1.05 * xh)
    y1 = int(max(bases) + .35 * xh)
    w = xs.max() - xs.min()
    cut_l = rng.choice([0, 0, .15, .3]) * w
    cut_r = rng.choice([0, 0, .15, .3]) * w
    return (int(xs.min() + cut_l), y0, int(xs.max() + 1 - cut_r), y1)


if __name__ == '__main__':
    n_pages = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    rng = random.Random(7)
    for p in range(n_pages):
        font = rng.choice(FONTS)
        size = rng.choice([30, 34, 38])
        sep = ['rule', 'gap'][p % 2]
        page, lab, info, ang, pitch = make_page(rng, font, size, sep)
        items = []
        for li in info:
            tgt = lab == li['id']
            if tgt.sum() < 200:
                continue
            items.append((li, tight_box(lab, li['id'], li['xh'], rng)))
        res_all = {}
        for mode in ('curve', 'box'):
            try:
                res_all[mode] = recut_page(page, [b for _, b in items], mode=mode)
            except Exception as e:                           # noqa: BLE001
                res_all[mode] = [repr(e)[:120]] * len(items)
        for j, (li, box) in enumerate(items):
            lid = li['id']
            tgt = lab == lid
            orig = np.zeros_like(tgt)
            orig[box[1]:box[3], box[0]:box[2]] = True
            res = {}
            for mode in ('curve', 'box'):
                rcs = res_all[mode][j]
                if isinstance(rcs, str) or not rcs:
                    res[mode] = dict(err=rcs or 'no line')
                    continue
                shown = np.zeros_like(tgt)
                for rc in rcs:
                    shown |= rc.erased
                ink_shown = (lab > 0) & shown
                foreign = ink_shown & (lab != lid)
                xs_t = np.nonzero(tgt)[1]
                res[mode] = dict(keep=round(float((tgt & shown).sum() / tgt.sum()), 3),
                                 foreign=round(float(foreign.sum() / max(1, ink_shown.sum())), 3),
                                 stops=[rcs[0].stop_left, rcs[-1].stop_right], n=len(rcs),
                                 over_l=round(float((xs_t.min() - rcs[0].x0) / li['xh']), 2),
                                 over_r=round(float((rcs[-1].x1 - 1 - xs_t.max()) / li['xh']), 2),
                                 notes=rcs[0].notes)
            print(json.dumps(dict(page=p, sep=sep, ang=round(ang, 2), col=li['col'], row=li['row'], pitch_true=round(pitch / li['xh'], 2),
                                  orig_keep=round(float((tgt & orig).sum() / tgt.sum()), 3), **res), ensure_ascii=False),
                  flush=True)
