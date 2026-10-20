"""T4c: score fresh blind cards by arm (screen pass vs reject)."""
import json, os, sys, collections
sys.path.insert(0, os.path.dirname(__file__)); from agg import wilson
D = os.path.dirname(os.path.abspath(__file__)) + '/t4c/'
G = {'crop_overrun', 'merged_two_lines', 'extra_text'}
def w(k, n):
    if not n: return '—'
    p, lo, hi = wilson(k, n); return f'{k}/{n} {p:.0%} ({lo:.0%}–{hi:.0%})'
print('| stratum | pass: letters-y | pass: marks-y | reject: letters-y | reject: geometry-error share | pool pass/reject | top pass errors |')
print('|---|---|---|---|---|---|---|')
for name in ['gazette_modern', 'gazette_poly1900', 'lekythos_poly1900', 'bsb_poly1850', 'bsb_mixed', 'oa_poly1900', 'pleias_poly1850', 'anemi_poly1850']:
    f = D + name + '_out.jsonl'
    if not os.path.exists(f): print(f'| {name} | pending |'); continue
    K = json.load(open(D + name + '_key.json')); R = [json.loads(l) for l in open(f) if l.strip()]
    arm = collections.defaultdict(list)
    for r in R: arm[K[r['card_id']]['arm']].append(r)
    P, J = arm['pass'], arm['reject']
    ly = sum(r['letters'] == 'y' for r in P); ld = sum(r['letters'] in 'yn' for r in P) + sum(r['letters'] == 'u' for r in P)
    my = sum(r['marks'] == 'y' for r in P); mn = sum(r['marks'] == 'n' for r in P)
    jy = sum(r['letters'] == 'y' for r in J); jg = sum(1 for r in J if r['letters'] != 'y' and set(r['errors']) & G)
    k0 = next(iter(K.values()))
    e = collections.Counter(x for r in P if r['letters'] == 'n' for x in r['errors']).most_common(3)
    print(f"| {name} | {w(ly, ld)} | {w(my, my + mn)} | {w(jy, len(J))} | {w(jg, len(J))} | {k0['pool_pass']}/{k0['pool_reject']} | {e} |")
