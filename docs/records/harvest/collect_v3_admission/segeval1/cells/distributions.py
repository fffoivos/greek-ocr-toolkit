"""Corpus-only distributions, before choosing any size threshold."""
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path
import sys

D = Path(__file__).resolve().parent
sys.path.insert(0, str(D.parents[4]))
from greekocr.harvest.numeric_cells import _numeric_reason


def quantiles(counts):
    total = sum(counts.values())
    if not total:
        return dict(n=0)
    result = dict(n=total)
    ordered = sorted(counts.items())
    for q in (0, .1, .25, .5, .75, .9, .95, .99, 1):
        rank = max(1, __import__('math').ceil(total * q))
        n = 0
        for v, c in ordered:
            n += c
            if n >= rank:
                result[str(q)] = v
                break
    return result


def main():
    counts = defaultdict(lambda: defaultdict(Counter))
    missing = defaultdict(Counter)
    widths = (25, 50, 75, 100, 150, 200, 250, 300, 400, 600, 800, 1200, 2000)
    heights = (15, 20, 25, 30, 40, 50, 60, 80, 100, 150, 200)
    chars = (1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 16, 20, 40, 80, 120)
    hist = defaultdict(lambda: defaultdict(Counter))
    numeric_rows = []
    methods = defaultdict(Counter)
    for line in gzip.open(D / 'population_cells.jsonl.gz', 'rt'):
        r = json.loads(line)
        numeric = _numeric_reason(r['raw_text']) is not None
        groups = ('all', 'numeric' if numeric else 'rest')
        values = {k: r[k] for k in ('width_px', 'height_px', 'characters', 'text_characters', 'xheight_px')}
        for k in ('width', 'height'):
            v, xh = r[k + '_px'], r['xheight_px']
            values[k + '_xh'] = round(v / xh, 6) if v is not None and xh is not None and xh > 0 else None
        for group in groups:
            methods[group][r['xheight_method']] += 1
            for k, v in values.items():
                if v is None:
                    missing[group][k] += 1
                else:
                    counts[group][k][v] += 1
            for key, bins in (('width_px', widths), ('height_px', heights), ('characters', chars), ('text_characters', chars)):
                value = values[key]
                label = 'missing' if value is None else next((f'<= {x}' for x in bins if value <= x), f'> {bins[-1]}')
                hist[group][key][label] += 1
        if numeric:
            numeric_rows.append(r)
    result = dict(quantiles={g: {k: quantiles(v) for k, v in fields.items()} for g, fields in counts.items()},
                  missing={g: dict(v) for g, v in missing.items()},
                  histograms={g: {k: dict(v) for k, v in fields.items()} for g, fields in hist.items()},
                  xheight_methods={g: dict(v) for g, v in methods.items()},
                  candidate_cuts=[])
    # Sensitivity grid reports observed inclusion, no accuracy interpretation.
    for w in (100, 150, 200, 250, 300, 400, 600):
        for h in (30, 40, 50, 60, 80, 100):
            for c in (8, 9, 10, 12, 16):
                n = sum(r['width_px'] is not None and r['height_px'] is not None
                        and 0 < r['width_px'] <= w and 0 < r['height_px'] <= h
                        and r['characters'] is not None and 0 < r['characters'] <= c for r in numeric_rows)
                result['candidate_cuts'].append(dict(width=w, height=h, chars=c, numeric_rows=n))
    (D / 'distributions.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result['quantiles'], indent=2))


if __name__ == '__main__':
    main()
