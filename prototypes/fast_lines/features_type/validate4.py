"""Validate repeated exports and retain per-page feature disagreements."""
import hashlib
import json
from collections import Counter
import numpy as np
from ..round2 import manifest
from ..shared.manifest import ROOT, digest
from ..shared.timing import dump
from .reference import DEST
from .audit4 import pointer


def load(path):
    return json.loads(path.read_text())


def run():
    final = pointer('active-final4.json')
    old = DEST / 'corrections-v4-fa2e30087b47'
    receipt = dict(checks=0, pages=[], repeats=[], comparisons={})

    def check(ok, message):
        assert ok, message
        receipt['checks'] += 1

    numbers = []
    for row in manifest()['pages']:
        page = row['page']
        record = load(final / (page + '.json'))
        before = load(old / (page + '.json'))
        check(record['page'] == page, page + ' page')
        check(record['image_size'] == row['image_size'], page + ' size')
        check(record['seconds'] >= 0 and np.isfinite(record['seconds']), page + ' time')
        check((final / (page + '.jpg')).is_file(), page + ' image')
        for item in record['items']:
            p = np.asarray(item['polygon'])
            check(p.ndim == 2 and p.shape[1] == 2 and len(p) >= 3 and np.isfinite(p).all(), page + ' polygon')
            check('baseline' in item and 'score' in item, page + ' contract')
        # Each old item must occur with its multiplicity; extra native recovery
        # is allowed, alteration or loss of an old separator result is not.
        a = Counter(json.dumps(x, sort_keys=True) for x in before['items'])
        b = Counter(json.dumps(x, sort_keys=True) for x in record['items'])
        check(not a - b, page + ' old correction changed')
        extra = len(record['items']) - len(before['items'])
        if row['group'] == 'agreement':
            check(record['items'] == before['items'], page + ' agreement changed')
        h = hashlib.sha256(json.dumps(record['items'], sort_keys=True).encode()).hexdigest()
        for repeat in (1, 2, 3):
            r = load(final / (page + f'.r{repeat}.json'))
            check(r['exact_baseline'] and r['final_sha256'] == h, page + ' fresh repeat')
            numbers.append(r)
        receipt['pages'].append(dict(page=page, extra_vs_round3=extra, final_sha256=h))
    check(len(list(final.glob('*.r1.json'))) == 195, 'repeat1 coverage')
    check(len(list(final.glob('*.r2.json'))) == 195, 'repeat2 coverage')
    check(len(list(final.glob('*.r3.json'))) == 195, 'repeat3 coverage')
    for f in (final / 'source').glob('*.py'):
        src = ROOT / 'prototypes/fast_lines' / ('features_type' if f.name == 'extended4.py' else 'shared') / f.name
        check(digest(f) == digest(src), 'source changed ' + f.name)
    for repeat in (2, 3):
        for name, predicate in [
            ('agreement', lambda r: r['group'] == 'agreement'),
            ('new_discrepancy', lambda r: r['group'] not in ('agreement', 'development')),
            ('correction_pages', lambda r: r['added'] > 0),
            ('all', lambda r: True),
        ]:
            subset = [r for r in numbers if r['repeat'] == repeat and predicate(r)]
            summary = dict(cohort=name, repeat=repeat, n=len(subset))
            for key in ('type_s', 'stack_added_s', 'total_s'):
                v = [r[key] * 1000 for r in subset]
                summary[key] = dict(median=float(np.median(v)), p95=float(np.percentile(v, 95)),
                                    maximum=max(v), maximum_page=max(subset, key=lambda r: r[key])['page'])
            receipt['repeats'].append(summary)
    audit = DEST / 'round4-audit'
    receipt['comparisons']['rows'] = load(audit / 'rows-summary.json')
    for name, groupkey, routes in [('tables-per-line', 'page', ('explicit', 'heuristic')),
                                   ('grid-per-slot', 'page', ('explicit', 'heuristic'))]:
        records = load(audit / (name + '.json'))
        summaries = []
        for page in sorted({r[groupkey] for r in records}):
            rs = [r for r in records if r[groupkey] == page]
            if name == 'tables-per-line':
                s = dict(page=page, n=len(rs), slow=sum(r['slow'] for r in rs),
                         **{route: dict(protected=sum(r[route] for r in rs), disagreements=sum(r[route] != r['slow'] for r in rs)) for route in routes})
            else:
                positive = lambda r, route: r[route]['supported'] and r[route]['owned_fraction'] < .25
                s = dict(page=page, n=len(rs), slow_positive=sum(positive(r, 'slow') for r in rs),
                         **{route: dict(positive=sum(positive(r, route) for r in rs), disagreements=sum(positive(r, route) != positive(r, 'slow') for r in rs)) for route in routes})
            summaries.append(s)
        receipt['comparisons'][name] = summaries
    records = load(audit / 'identity-per-glyph.json')
    pairs = sorted({(r['query'], r['atlas']) for r in records})
    receipt['comparisons']['identity'] = [dict(query=q, atlas=a, route=route,
        both=sum(r['within_slow_top3'] is not None for r in records if r['query']==q and r['atlas']==a and r['route']==route),
        within=sum(r['within_slow_top3'] is True for r in records if r['query']==q and r['atlas']==a and r['route']==route))
        for q,a in pairs for route in ('explicit','heuristic')]
    dump(DEST / 'round4-validation.json', receipt)
    print(json.dumps({k:v for k,v in receipt.items() if k not in ('pages','comparisons')}))


if __name__ == '__main__':
    run()
