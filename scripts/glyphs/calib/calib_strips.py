"""Readability calibration strips (owner 8 Oct 16:40): synthetic lines with ONE controlled degradation each, at known
strengths, for an OCR reader (CLLG on the GPU node, run by the coordinator). Each strip's reading error is later set
against the glyph tools' measurements to find where readability limits lie.

Conditions (per line): clean control; top_cut / bottom_cut of the letter body (fraction of the x-height removed by the
crop edge); fade / thin / break / thick ink over the whole line; skew (degrees). Usage:
  calib_strips.py OUT_DIR TEXT_DIR [LINES_PER_CONDITION=40]
OUT_DIR/strips/*.png + OUT_DIR/manifest.jsonl rows {line_id, crop_path, gt_text, degradation, intensity, x0, x1,
font, size, xh, seed}.
"""
import json, random, sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts/glyphs/eval'))
from common import setup, pick_text                                     # noqa: E402
from greekocr.glyphs.synthetic import render_truth_line, LETTER, MARK, PUNCT, IGNORE   # noqa: E402

OUT, TEXT_DIR = Path(sys.argv[1]), sys.argv[2]
PER = int(sys.argv[3]) if len(sys.argv) > 3 else 40
# fonts close to the target regime (19th-c. parliament print) first; others for spread
PREFERRED = ('GFSDidot', 'TheanoDidot', 'GFSNeohellenic', 'OldStandard', 'EBGaramond', 'Gentium', 'NewCM', 'GFSBodoni',
             'LibertinusSerif', 'NotoSerif', 'GFSArtemisia')
# v2: cuts zone by zone on the four guide lines. The top cut first removes the accent / tall-letter zone above the
# mean line (accent_cut: fraction of that zone from its top), then the letter body (top_cut); the bottom cut first
# removes the tail zone below the baseline (tail_cut), then the body (bottom_cut). Skew strips are cropped tightly.
CONDITIONS = [('clean', 0.0)] \
    + [('accent_cut', v) for v in (.25, .5, .75, 1.0)] \
    + [('top_cut', v) for v in (.1, .2, .3, .4, .5)] \
    + [('tail_cut', v) for v in (.25, .5, .75, 1.0)] \
    + [('bottom_cut', v) for v in (.1, .2, .3, .4, .5)] \
    + [(k, v) for k in ('fade', 'thin', 'break', 'thick') for v in (.2, .4, .6, .8, 1.0)] \
    + [('skew', v) for v in (0.0, 1.0, 2.0, 3.0, 5.0)]


def main() -> None:
    fonts, texts = setup(TEXT_DIR)
    fonts = [f for f in fonts if f.name.startswith(PREFERRED)]
    (OUT / 'strips').mkdir(parents=True, exist_ok=True)
    rng = random.Random(91)
    rows = []
    for li in range(PER):
        font = rng.choice(fonts)
        text = pick_text(rng, texts, font, n=60).strip()
        size = rng.randint(30, 40)
        seed = 9000 + li
        for kind, v in CONDITIONS:
            kw: dict = {}
            if kind in ('fade', 'thin', 'break', 'thick'):
                kw['ink_defects'] = [(0.0, 1.0, kind, v)]
            r = render_truth_line(text, font, size=size, rng=random.Random(seed), **kw)
            img = r.image
            # tight crop around the main line like a page cutter, then the controlled cut
            ink_rows = np.nonzero(np.isin(r.truth, (LETTER, MARK, PUNCT, IGNORE)).any(axis=1))[0]
            pad = int(.3 * r.xh)
            top, bot = max(0, int(ink_rows[0]) - pad), min(img.height, int(ink_rows[-1]) + 1 + pad)
            base = float(np.median(r.base_truth))
            above = (base - r.xh) - top          # accent / tall-letter zone kept by the tight crop
            below = bot - base                   # tail zone
            if kind == 'accent_cut':
                top = int(round(top + v * above))
            if kind == 'top_cut':
                top = int(round(base - r.xh + v * r.xh))
            if kind == 'tail_cut':
                bot = int(round(bot - v * below))
            if kind == 'bottom_cut':
                bot = int(round(base - v * r.xh))
            if kind == 'skew':
                # rotate the rendered line to exactly v degrees, then crop it tightly like every other strip
                ang = v if li % 2 == 0 else -v
                big = r.image.rotate(ang - r.skew_deg, resample=Image.BICUBIC, expand=True,
                                     fillcolor=int(np.median(np.asarray(r.image))))
                arr = np.asarray(big, np.float64)
                ys, xs = np.nonzero(arr < np.median(arr) - 40)
                img = big.crop((max(0, xs.min() - pad), max(0, ys.min() - pad),
                                min(big.width, xs.max() + pad + 1), min(big.height, ys.max() + pad + 1)))
            else:
                img = img.crop((0, top, img.width, bot))
            name = f'c{li:03d}_{kind}_{v:.1f}.png'
            img.save(OUT / 'strips' / name)
            rows.append(dict(line_id=name[:-4], crop_path=f'strips/{name}', gt_text=text, degradation=kind,
                             intensity=v, x0=0, x1=img.width, font=r.font, size=size, xh=r.xh, seed=seed))
    with open(OUT / 'manifest.jsonl', 'w') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print(len(rows), 'strips in', OUT)


if __name__ == '__main__':
    main()
