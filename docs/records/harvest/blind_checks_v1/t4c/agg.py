"""Aggregate F2 samples: per cohort page-gate pass, geometry-screen rate, usable rows/read page per class (page bootstrap)."""
import json, sys, random, math, collections

def wilson(k, n, z=1.96):
    if n == 0: return (float('nan'),) * 3
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0, c - h), min(1, c + h)

def boot(vals, B=4000, seed=7):
    rng = random.Random(seed); n = len(vals)
    if n == 0: return (float('nan'),) * 3
    ms = sorted(sum(rng.choice(vals) for _ in range(n)) / n for _ in range(B))
    return sum(vals) / n, ms[int(.025 * B)], ms[int(.975 * B) - 1]

def run(base, cohort_key):
    P = [json.loads(l) for l in open(base + '/pages.jsonl')]
    L = [json.loads(l) for l in open(base + '/lines.jsonl')]
    read = [p for p in P if p.get('machine_pass') and not p.get('excluded') and p.get('read_status', 'ok') != 'not_read']
    coh = lambda r: cohort_key(r)
    by_page = collections.defaultdict(list)
    for l in L: by_page[l['page_id']].append(l)
    out = {}
    for c in sorted({coh(p) for p in read}):
        pages = [p for p in read if coh(p) == c]
        bad = sum(1 for p in pages if any('bad_page' in l['rejection_reasons'] for l in by_page[p['id']]) or not by_page[p['id']])
        cand = [l for p in pages for l in by_page[p['id']] if l['admitted'] and l.get('codec_v1_pass') and not l.get('duplicate_crop_label')]
        geo_pos = sum(1 for l in cand if l.get('geometry_positive') is not False)  # True or unresolved = screened out
        classes = collections.Counter(l['primary_allocation'] for p in pages for l in by_page[p['id']] if l.get('usable_candidate'))
        rows = {}
        for k in classes:
            vals = [sum(1 for l in by_page[p['id']] if l.get('usable_candidate') and l['primary_allocation'] == k) for p in pages]
            rows[k] = boot(vals)
        out[c] = dict(read=len(pages), gate_pass=wilson(len(pages) - bad, len(pages)), geo_screen=wilson(geo_pos, len(cand)), geo_n=len(cand), rows=rows,
                      usable_total=boot([sum(1 for l in by_page[p['id']] if l.get('usable_candidate')) for p in pages]))
    return out

def fmt(out):
    for c, d in out.items():
        g, gl, gh = d['gate_pass']; s, sl, sh = d['geo_screen']
        print(f"{c}: read {d['read']} | page gate {g:.0%} ({gl:.0%}-{gh:.0%}) | geometry screen {s:.0%} ({sl:.0%}-{sh:.0%}) of {d['geo_n']} | usable/page {d['usable_total'][0]:.1f} ({d['usable_total'][1]:.1f}-{d['usable_total'][2]:.1f})")
        for k, (m, lo, hi) in sorted(d['rows'].items(), key=lambda x: -x[1][0]):
            if m >= 0.5: print(f"    {k}: {m:.2f} ({lo:.2f}-{hi:.2f})")

if __name__ == '__main__':
    base, mode = sys.argv[1], sys.argv[2]
    key = {'ia': lambda r: r['source'], 'intl': lambda r: r.get('census_group') or r['source'], 'gr': lambda r: r.get('census_group') or r['source']}[mode]
    o = run(base, key); fmt(o)
    json.dump(o, open(sys.argv[3], 'w'), indent=1) if len(sys.argv) > 3 else None
