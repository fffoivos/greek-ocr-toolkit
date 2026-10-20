"""Google's mark-error types on the held-out print truth, and which ones each reader arm fixes (or newly breaks).

Types (coordinator, from the sourcing lead's blind checks): grave->acute (word-final), capital breathing dropped, breathing->acute
on a one-letter article (ὁ ἡ ἑ ...), iota subscript dropped; everything else = other. Google's marks per recogniser letter come from
word pairing (candidates.pair_tokens) where Google's and the recogniser's base letters agree; slots without that pairing are skipped.
Usage: PYTHONPATH=. python scripts/labelfix/r1_error_types.py <score_dir> [arms...]
"""
import gzip, json, sys
from collections import Counter, defaultdict
from greekocr.labelfix.candidates import pair_tokens
from greekocr.labelfix.text import nfd, clusters, strip_marks
from greekocr.labelfix.validate import load_three_way
NAME = {'̓': ('breathing', 'psili'), '̔': ('breathing', 'dasia'), '́': ('accent', 'acute'), '̀': ('accent', 'grave'),
        '͂': ('accent', 'circumflex'), 'ͅ': ('subscript', 'subscript'), '̈': ('dialytika', 'dialytika')}
G = {l['line_id']: l['google'] for l in load_three_way(0)}

def google_marks(google, rec):
    """recogniser NFD start -> set of Google (kind,name) marks, for letters inside words whose bases agree."""
    out = {}
    for g, m in pair_tokens(google, rec):
        if m is None or strip_marks(nfd(g.core)) != strip_marks(nfd(m.core)): continue
        gc = [c for c in clusters(nfd(g.core))]; mc = [c for c in clusters(nfd(m.core))]
        for a, b in zip(gc, mc):
            out[m.core_start + b.start] = {NAME[x] for x in a.marks if x in NAME}
    return out

KIND = {'psili': 'breathing', 'dasia': 'breathing', 'acute': 'accent', 'grave': 'accent', 'circumflex': 'accent',
        'subscript': 'subscript', 'dialytika': 'dialytika'}

def atomic(marks):
    """Truth/detector marks -> atomic (kind,name) set; compounds split; apostrophes dropped (outside the reader's heads)."""
    out = set()
    for k, n in marks:
        if k == 'apostrophe': continue
        for part in (n.split('+') if k == 'compound' else [n]): out.add((KIND.get(part, k), part))
    return out

def kind(s, truth, google, word_len):
    if ('accent', 'grave') in truth and ('accent', 'acute') in google and s.get('word_final'): return 'grave->acute'
    br_t = {x for x in truth if x[0] == 'breathing'}; br_g = {x for x in google if x[0] == 'breathing'}
    if s['base'].isupper() and br_t and not br_g: return 'capital breathing dropped'
    if word_len == 1 and br_t and not br_g and ('accent', 'acute') in google: return 'breathing->acute (ὁ ἡ ἑ)'
    if ('subscript', 'subscript') in truth and ('subscript', 'subscript') not in google: return 'subscript dropped'
    return 'other'

def main(d, arms):
    res = {}
    for arm in arms:
        fixed, total, broke = Counter(), Counter(), Counter()
        for l in gzip.open(f'{d}/{arm}_mapped_lines.jsonl.gz', 'rt'):
            r = json.loads(l)
            if r.get('dev'): continue  # DEV books: no reader inference; held-out only
            gm = google_marks(G[r['line_id']], nfd(r['recogniser_text']))
            wl = defaultdict(int)
            for s in r['slots']: wl[(s.get('word'))] += 1
            for s in r['slots']:
                if s.get('truth') is None or s.get('recogniser_start') not in gm: continue
                truth = atomic(s['truth']); google = gm[s['recogniser_start']]; ours = atomic(s.get('detected', []))
                if google != truth:
                    k = kind(s, truth, google, wl[s.get('word')]); total[k] += 1; fixed[k] += ours == truth
                elif ours != truth:
                    broke['new error where Google was right'] += 1
        res[arm] = dict(google_errors=dict(total), fixed=dict(fixed), new_errors=broke['new error where Google was right'])
    print(json.dumps(res, ensure_ascii=False, indent=1)); return res

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:] or ['A', 'B', 'C', 'D', 'E'])
