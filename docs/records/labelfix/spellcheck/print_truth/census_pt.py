import json, sys, unicodedata as u
from collections import Counter, defaultdict
W = '/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/'
pt = json.load(open(sys.argv[1]))
nfd = lambda s: u.normalize('NFD', s or '')
def compound(w):
    for ch in u.normalize('NFD', w):
        pass
    # a cluster carrying a breathing AND an accent
    cl, cur = [], ''
    for ch in nfd(w):
        if u.category(ch).startswith('M'): cur += ch
        else:
            cl.append(cur); cur = ''
    cl.append(cur)
    return any(any(m in c for m in '̓̔') and any(m in c for m in '́̀͂') for c in cl)
for seed in (0, 1):
    E = [json.loads(l) for l in open(W + f'reach_s{seed}.jsonl')]
    tab = defaultdict(Counter); tot = Counter(); comp = Counter()
    for e in E:
        v = pt.get(f"{e['line_id']}|{e['word_index']}", {})
        verdict = v.get('verdict', 'missing')
        tab[e['stage']][verdict] += 1; tot[verdict] += 1
        if verdict in ('human', 'other'):
            target = v.get('printed') or e['human']
            tab[e['stage']]['real_mw' if not e['model_right'] else 'real_mr'] += 1
            c = compound(e['google']) or compound(target)
            comp['real'] += 1; comp['compound'] += c
    print(f'seed {seed} totals', dict(tot), 'compound among real errors', dict(comp))
    if seed == 0:
        print('| T1 stage | diffs | printed = human (real Google error) | printed = Google (human normalised) | printed = neither | unresolved | real, model also wrong |')
        print('|---|---:|---:|---:|---:|---:|---:|')
        for s in ('human_error', 'guard', 'constraint', 'grave', 'grave_line_end', 'lex_unique', 'lex_compete', 'lex_miss', 'real_word', 'human_unatt'):
            c = tab[s]; n = sum(c[k] for k in ('human', 'google', 'other', 'disagree', 'unreadable', 'missing'))
            print(f"| {s} | {n} | {c['human']} | {c['google']} | {c['other']} | {c['disagree'] + c['unreadable'] + c['missing']} | {c['real_mw']} |")
