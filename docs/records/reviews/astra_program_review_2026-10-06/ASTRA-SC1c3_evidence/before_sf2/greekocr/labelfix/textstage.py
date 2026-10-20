"""Text-stage candidates (no crop, no ink) over recorded predictions, to count and to pick
lines worth a model forward pass for the review deck.

    python -m greekocr.labelfix.textstage --predictions .../full_s0_v2_test.jsonl \
        --records docs/harvest/collection/v2/import_real_v2_test.jsonl --out <dir> --pick 2400
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import random

from .candidates import LineContext, line_candidates
from .lexicon import load_all
from .rules import RULES
from .validate import TOOLKIT


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--predictions', type=Path, required=True)
    ap.add_argument('--records', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--pick', type=int, default=0, help='lines to pick for a forward pass (lexicon-passing, per-rule round robin)')
    ap.add_argument('--exclude-docs', type=Path, nargs='*', default=[], help='jsonl files whose line ids\' documents are excluded (e.g. the human set)')
    ap.add_argument('--lexicons', type=Path, default=TOOLKIT / 'docs/labelfix/lexicons')
    a = ap.parse_args(argv)
    lexicons = load_all(a.lexicons)
    recs = {}
    for line in open(a.records, encoding='utf-8'):
        r = json.loads(line)
        recs[r['id']] = r
    excluded = set()
    for path in a.exclude_docs:
        for line in open(path, encoding='utf-8'):
            r = json.loads(line)
            k = r['line_id'][:-len('-human')] if r['line_id'].endswith('-human') else r['line_id']
            if k in recs:
                excluded.add(recs[k]['doc'])
    per_rule_wave = defaultdict(Counter)
    lex_pass = defaultdict(list)
    n = 0
    with open(a.out / 'textstage_candidates.jsonl', 'w', encoding='utf-8') as fh:
        for line in open(a.predictions, encoding='utf-8'):
            p = json.loads(line)
            r = recs.get(p['line_id'])
            if r is None or r['doc'] in excluded:
                continue
            n += 1
            ctx = LineContext(p['line_id'], p['gt'], p['prediction'], p['script_class'], r['wave'], str(TOOLKIT / r['crop']),
                              None, None, extra=dict(doc=r['doc']))
            for c in line_candidates(ctx, lexicons, 'strict'):
                rule = c['decision']['rule']
                per_rule_wave[rule][r['wave']] += 1
                ok = c['decision']['lexicon_ok'] if c['decision']['lexicon_ok'] is not None else not c['decision']['reason'].startswith('excluded')
                if ok and not c['decision']['reason'].startswith('excluded'):
                    lex_pass[rule].append(p['line_id'])
                fh.write(json.dumps(c, ensure_ascii=False) + '\n')
    L = [f'# Text-stage candidates over {n} lines of `{a.predictions.name}` (no ink)', '',
         '| rule | ' + ' | '.join(sorted({w for v in per_rule_wave.values() for w in v})) + ' | total | lexicon-passing lines |',
         '|---|' + '---:|' * (len({w for v in per_rule_wave.values() for w in v}) + 2)]
    waves = sorted({w for v in per_rule_wave.values() for w in v})
    for rule in list(RULES) + ['none']:
        if rule not in per_rule_wave:
            continue
        L.append(f'| {rule} | ' + ' | '.join(str(per_rule_wave[rule][w]) for w in waves) + f' | {sum(per_rule_wave[rule].values())} | {len(set(lex_pass[rule]))} |')
    (a.out / 'textstage_summary.md').write_text('\n'.join(L) + '\n')
    print('\n'.join(L))
    if a.pick:
        rng = random.Random(20261016)
        picked = []
        pools = {r: list(dict.fromkeys(v)) for r, v in lex_pass.items()}
        for v in pools.values():
            rng.shuffle(v)
        seen = set()
        while len(picked) < a.pick and any(pools.values()):
            for r in list(pools):
                if pools[r] and len(picked) < a.pick:
                    k = pools[r].pop()
                    if k not in seen:
                        seen.add(k)
                        picked.append(k)
        (a.out / 'picked_ids.txt').write_text('\n'.join(picked) + '\n')
        print('picked', len(picked))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
