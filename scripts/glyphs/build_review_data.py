"""Build review-page data. Usage: build_review_data.py MODE OUT.json [PREVIOUS.json ...]

MODE fixes : every line shown in earlier batches (docs/records/glyphs/glyphs_shown_batches.json), re-run with the current tools, with
             a before → now summary taken from the previous batches' data files (PREVIOUS.json, newest first)
MODE new   : 40 lines never shown before, selected per issue after running every check on the whole pool
             (400 parliament sample crops + 44 fixture lines + regression pairs)
"""
import glob, json, sys, time
from pathlib import Path
import numpy as np
from greekocr.glyphs.report import document_priors, line_record

ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT / 'tests' / 'fixtures'
mode, out_path, previous = sys.argv[1], sys.argv[2], sys.argv[3:]
t0 = time.time()
pool = sorted(glob.glob(str(FIX / 'o4d_sample400' / 'crops' / '*.png'))) + \
    sorted(glob.glob(str(FIX / 'o4d_lines' / 'line*.png'))) + sorted(glob.glob(str(FIX / 'o4d_lines' / 'regressions' / '*.png')))
priors = document_priors(pool)
by_stem = {}
for p in pool:                                    # a stem can exist twice (sample crop and fixture copy): keep the first
    by_stem.setdefault(Path(p).stem, p)
line_id = lambda stem: stem.replace('_old', '').replace('_new', '')
shown = json.loads((ROOT / 'docs' / 'glyphs_shown_batches.json').read_text())
shown_ids = list(dict.fromkeys(shown['batch2'] + shown['batch1']))

NOTES = {
    's2-7534648e60694be1d180-p00023-l00013': 'Fit failure kept from batch 2: two separate pieces of text at different heights are joined into one steep line.',
}


def summary(r: dict) -> str:
    parts = [f"skew {r['angle_deg']:+.2f}°", f"{len(r['cut_spans'])} cut span(s)"]
    if 'n_broken' in r:
        parts.append(f"{r['n_broken']} broken, {r.get('n_faint', 0)} faint, {r.get('n_merged', 0)} merged")
    else:
        parts.append(f"{r.get('n_under', 0)} under / {r.get('n_over', 0)} over (old ink score)")
    if 'double_line' in r:
        parts.append('two lines' if r['double_line'] else 'one line')
    if 'n_lines' in r:
        parts.append(f"{r['n_lines']} line(s) detected ({r['n_full_lines']} full, {r['n_edge_lines']} edges only), {r['n_columns']} column(s)")
    elif 'lines' in r:
        parts.append(f"{len(r['lines']) - 1} neighbour line(s) placed")
    return ', '.join(parts)


if mode == 'fixes':
    before = {}
    for path in previous:                          # newest first: the latest earlier version of each line wins
        for r in json.loads(Path(path).read_text())['lines']:
            before.setdefault(r['id'], r)
    out = []
    for sid in shown_ids:
        r = line_record(by_stem[sid], priors=priors)
        old = before[sid]
        r.update(section='fixes', label=old.get('label', ''), before=summary(old), now=summary(r))
        if sid in NOTES:
            r['note'] = NOTES[sid]
        out.append(r)
    pool_n = len(shown_ids)
else:
    seen = {line_id(s) for s in shown_ids}
    records = {p: line_record(p, priors=priors) for p in pool if line_id(Path(p).stem) not in seen}
    print(len(records), 'unseen crops measured in', round(time.time() - t0, 1), 's', file=sys.stderr)
    chosen, out = set(), []

    def bend_px(r):
        seg = r['segments'][r['main_segment']]
        b = np.array(seg['baseline']); x = np.arange(len(b))
        lo, hi = (int(v / r['step']) for v in seg['support_x'])
        return float(np.abs(b[lo:hi] - np.polyval(np.polyfit(x[lo:hi], b[lo:hi], 1), x[lo:hi])).max()) if hi - lo >= 4 else 0.0

    def take(key, label, n, cond=lambda r: True):
        ranked = sorted(((p, r) for p, r in records.items() if line_id(Path(p).stem) not in chosen and cond(r)),
                        key=lambda pr: key(pr[1]), reverse=True)
        for p, r in ranked[:n]:
            chosen.add(line_id(Path(p).stem))
            out.append(dict(r, section='new', label=label))

    take(lambda r: abs(r['angle_deg']), 'Steep skew', 5, lambda r: r['confidence'] == 'high')
    take(bend_px, 'Strong bend in the line', 5, lambda r: r['degree'] == 2)
    take(lambda r: len(r['lines']), 'Several lines in one crop (neighbours placed)', 6, lambda r: len(r['lines']) >= 3)
    take(lambda r: r['n_full_lines'], 'Second full line or column in the crop', 5, lambda r: r['n_full_lines'] >= 2)
    take(lambda r: len(r['cut_spans']) + sum(c['body_cut'] for c in r['cut_letters']) / 10, 'Letters cut by the crop edge', 5)
    take(lambda r: r['n_broken'] / max(1, len(r['letters'])), 'Many broken letters', 4, lambda r: len(r['letters']) >= 15)
    take(lambda r: r['n_faint'], 'Faint letters', 3, lambda r: r['n_faint'] > 0)
    take(lambda r: r['n_merged'], 'Letters run together', 4, lambda r: r['n_merged'] > 0)
    take(lambda r: -abs(r['angle_deg']) - r['n_broken'] - r['n_merged'] - len(r['lines']), 'Quiet line (nothing found)', 3,
         lambda r: not r['double_line'] and not r['cut_spans'])
    pool_n = len(records)
json.dump(dict(built=time.strftime('%Y-%m-%d %H:%M'), mode=mode, pool=pool_n, n_priors=len(priors), lines=out),
          open(out_path, 'w'), ensure_ascii=False, allow_nan=False)
print(len(out), 'lines on the page', file=sys.stderr)
for r in out:
    print(r['section'][:5], r['id'][:44], '|', r['label'][:40], '|', r.get('now') or summary(r), file=sys.stderr)
