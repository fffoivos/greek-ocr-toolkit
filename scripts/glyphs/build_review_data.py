"""Build the review-page data: (1) the owner's cases with the fixes, (2) interesting cases selected after running the
tools on every crop of the pool (400 parliament sample crops + 44 fixture lines + regression pairs).
Usage: build_review_data.py OUT.json"""
import glob, json, sys, time
from pathlib import Path
from greekocr.glyphs.report import document_priors, line_record

ROOT = Path(__file__).resolve().parents[2] / 'tests' / 'fixtures'
REG = ROOT / 'o4d_lines' / 'regressions'
SAMPLE = ROOT / 'o4d_sample400' / 'crops'
OWNER = 's2-60f24a3d8a2d714767f2-p00003-l00024'
t0 = time.time()
pool = sorted(glob.glob(str(SAMPLE / '*.png'))) + sorted(glob.glob(str(ROOT / 'o4d_lines' / 'line*.png'))) + sorted(glob.glob(str(REG / '*.png')))
priors = document_priors(pool)
records = {}
for p in pool:
    records[p] = line_record(p, priors=priors)
print(len(records), 'crops measured in', round(time.time() - t0, 1), 's', file=sys.stderr)

fixes = [
    (REG / f'{OWNER}_old.png', 'Owner example, original crop: start a quarter visible (inside-the-crop curve)'),
    (REG / f'{OWNER}_new.png', 'Owner example, re-cut: faint letters, broken pieces now grouped per letter'),
    (ROOT / 'o4d_lines' / 'line04_medium.png', 'Owner note: first two words had no underline (bend at the line start)'),
    (ROOT / 'o4d_lines' / 'line08_medium.png', 'Owner note: two lines in one crop'),
    (SAMPLE / 's2-49598b2e848ab1f0ee1e-p00001-l00054.png', 'Owner note: a bit of a second line, and the line curves down at first'),
    (ROOT / 'o4d_lines' / 'line01_large.png', 'Two lines in one crop'),
]
chosen = {str(p) for p, _ in fixes}
line_id = lambda p: Path(p).stem.replace('_old', '').replace('_new', '')
shown_ids = {line_id(p) for p, _ in fixes}
out = [dict(records[str(p)], section='fixes', label=lab) for p, lab in fixes]


def take(key, label, n, cond=lambda r: True):
    ranked = sorted(((p, r) for p, r in records.items() if p not in chosen and line_id(p) not in shown_ids and cond(r)),
                    key=lambda pr: key(pr[1]), reverse=True)
    for p, r in ranked[:n]:
        chosen.add(p); shown_ids.add(line_id(p))
        out.append(dict(r, section='interesting', label=label))


def bend_px(r):
    import numpy as np
    b = np.array(r['baseline']); x = np.arange(len(b))
    lo, hi = (int(v / r['step']) for v in r['support_x'])
    if hi - lo < 4:
        return 0.0
    lin = np.polyval(np.polyfit(x[lo:hi], b[lo:hi], 1), x[lo:hi])
    return float(np.abs(b[lo:hi] - lin).max())


take(lambda r: abs(r['angle_deg']), 'Steepest skew in the pool', 3, lambda r: r['confidence'] == 'high')
take(bend_px, 'Strongest bend (curved fit)', 3, lambda r: r['degree'] == 2)
take(lambda r: r['second']['ratio'] if r['second'] else 0, 'Second line inside the crop', 3, lambda r: r['double_line'])
take(lambda r: len(r['cut_spans']) + sum(c['body_cut'] for c in r['cut_letters']) / 10, 'Most letter body cut by the crop edge', 3)
take(lambda r: r['n_broken'] / max(1, len(r['letters'])), 'Highest share of broken letters', 3, lambda r: len(r['letters']) >= 15)
take(lambda r: r['n_faint'], 'Most faint letters', 2, lambda r: r['n_faint'] > 0)
take(lambda r: r['n_merged'], 'Most merged (touching) letters', 2, lambda r: r['n_merged'] > 0)
take(lambda r: -abs(r['angle_deg']) - r['n_broken'] - r['n_merged'], 'Quiet line for comparison (no issues found)', 1,
     lambda r: not r['double_line'] and not r['cut_spans'])
# implementer's inspection notes on the rendered page (8 Oct, after looking at each selected card)
NOTES = {
    's2-7534648e60694be1d180-p00023-l00013': 'Fit failure: two separate pieces of text at different heights ("οἱ ἑξῆς καρποί·" and the heading "Α. Σῖτος") are joined into one steep line. The real lines are each level.',
    'line42_large': 'The main line is right; the second-line fit slants across the crop because the other text ("(θόρυβος.)") sits only at the left.',
    's2-49598b2e848ab1f0ee1e-p00001-l00054': 'The target line is followed, including where it comes down into the crop at the start (x≈97–221). The partial second line at the lower left ("μάτων.") is NOT flagged: it covers about a quarter of the width and curves, and the double-line check needs a band across the line.',
}
for r in out:
    if r['id'] in NOTES:
        r['note'] = NOTES[r['id']]
json.dump(dict(built=time.strftime('%Y-%m-%d %H:%M'), pool=len(records), n_priors=len(priors), lines=out),
          open(sys.argv[1], 'w'), ensure_ascii=False, allow_nan=False)
print(len(out), 'lines on the page', file=sys.stderr)
for r in out:
    print(r['section'][:4], r['id'][:44], '|', r['label'][:44], '| angle', r['angle_deg'], 'double', r['double_line'],
          'broken', r['n_broken'], 'faint', r['n_faint'], 'merged', r['n_merged'], 'cuts', len(r['cut_spans']), file=sys.stderr)
