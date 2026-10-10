"""Repeated on-demand feature cost, including extraction, excluding image I/O.

This is an offline census measurement, not the clean-page runtime path. Query
and atlas extraction are charged again for each independent pairing.
"""
from time import perf_counter
import cv2
from ..round2 import manifest, get_baseline
from ..shared.manifest import ROOT
from ..shared.type_rows import render
from ..shared.type_table_extent import analyze
from ..shared.type_identity import extract, sample, witnesses
from ..shared.timing import dump
from .rows4 import NAMES
from .tables import names
from .reference import DEST
from .identity_routes import heuristic
from .audit4 import pointer


def run():
    import json
    rows = {r['page']: r for r in manifest()['pages']}
    pairings = [(d['query'], d['atlas']) for f in pointer('active-identity4.json').glob('*.json')
                for d in [json.loads(f.read_text())]]
    records = []
    for repeat in (1, 2):
        for feature, selected in [('rows', NAMES), ('table_extents', sorted(names()))]:
            for page in selected:
                row = rows[page]
                gray = cv2.imread(str(ROOT / row['path']), 0)
                items = get_baseline(row)
                for route in ('slow', 'explicit', 'heuristic'):
                    start = perf_counter()
                    if feature == 'rows':
                        [render(gray, q, route=route, version=3) for q in items]
                    else:
                        analyze(gray, items, route=route, version=6)
                    records.append(dict(feature=feature, page=page, route=route,
                                        repeat=repeat, seconds=perf_counter()-start))
        for query, atlas in pairings:
            a, b = rows[query], rows[atlas]
            g = cv2.imread(str(ROOT / a['path']), 0)
            h = g if query == atlas else cv2.imread(str(ROOT / b['path']), 0)
            gi, hi = get_baseline(a), get_baseline(b)
            for route in ('slow', 'explicit', 'heuristic'):
                start = perf_counter()
                q = sample(extract(g, gi, version=2)[0])
                p = q if query == atlas else sample(extract(h, hi, version=2)[0])
                if route == 'heuristic':
                    heuristic(q, p, same_page=query == atlas)
                else:
                    witnesses(q, p, same_page=query == atlas, route=route, version=2)
                records.append(dict(feature='glyph_atlas', page=query, atlas=atlas,
                                    route=route, repeat=repeat, seconds=perf_counter()-start))
        print('repeat', repeat, 'records', len(records), flush=True)
    dump(DEST / 'round4-feature-timings.json', records)


if __name__ == '__main__':
    cv2.setNumThreads(1)
    run()
