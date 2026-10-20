#!/usr/bin/env python3
"""Offline BENCH02H metadata sweep. Run with python3 -B bench02/run_sweep.py."""
from collections import Counter
import json
from pathlib import Path
import tempfile
import bench02_draw as b

CAPS=(4,12,25,50,100,None)
POOLS=('none','n1','lqb','both')


def inputs():
    a=b.HERE.parent; projects=Path.home()/'Projects'
    return dict(tags_path=b.HERE/'census03/tags.jsonl.gz',split_path=a/'split2/row_split.jsonl.gz',
        edition_paths=[a/'split1/editions.jsonl',a/'split2/edition_map.jsonl'],
        features=[projects/f'collect-v3-data/snapshots/{w}_features_20261018_0524.jsonl' for w in ('W1','W2')],
        v2_paths=[projects/f'greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_{s}.jsonl' for s in ('train','dev','test')],
        manifest=projects/'greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_exclusions/release_exclusions.json')


def summarize(counts,candidates):
    result=dict(classes=counts['classes'],splits={})
    for side in ('test','dev'):
        cc={k.split(':')[1]:v for k,v in counts['classes'].items() if k.startswith(side+':')}
        drawn=[r for r in candidates if r['split']==side]
        ec=Counter(r['edition_id'] for r in drawn)
        result['splits'][side]=dict(credited=sum(min(v['drawn'],v['quota']) for v in cc.values()),
            quota=sum(v['quota'] for v in cc.values()),drawn=len(drawn),
            filled=sum(v['deficit']==0 for v in cc.values()),deficit=sum(v['deficit'] for v in cc.values()),
            subgroup_qualified_filled=sum(v['deficit']==0 and not any(v['subgroup_deficits'].values()) for v in cc.values()),
            diversity_pass_classes=sum(v['editions']>=10 and v['sources']>=3 for v in cc.values()),
            max_edition_lines=max(ec.values(),default=0),top5_lines=sum(n for _,n in ec.most_common(5)),
            top5_share=sum(n for _,n in ec.most_common(5))/max(1,len(drawn)))
    return result


def main():
    dest=b.HERE/'sweep';dest.mkdir(exist_ok=True);cache={};runs=[];default_sha=None
    with tempfile.TemporaryDirectory(dir=b.HERE,prefix='.sweep-') as td:
        for rule in ('dry','upper_bound'):
            for cap in CAPS:
                for pool in POOLS:
                    c=b.draw(**inputs(),dest=Path(td),dry_run=rule=='dry',edition_cap=cap,
                        pool_include_forced=pool,upper_bound=rule=='upper_bound',_cache=cache)
                    candidates=list(b.rows(Path(td)/'candidates.jsonl'))
                    assert not {r['row_id'] for r in candidates}&cache['locked']
                    assert cap is None or max(c['edition_counts'].values(),default=0)<=cap
                    assert cap is None or max(c['series_counts'].values(),default=0)<=3*cap
                    if rule=='dry' and cap==4 and pool=='none':
                        actual=(Path(td)/'candidates.jsonl').read_bytes()
                        assert actual==(b.HERE/'census03/dryrun/candidates.jsonl').read_bytes()
                        default_sha=b.sha(Path(td)/'candidates.jsonl')
                    result=dict(rule=rule,cap=cap,pool=pool,**summarize(c,candidates),
                        added_rows=c.get('diagnostic_options',{}).get('added_rows',{'n1':0,'lqb':0}),
                        added_classified_rows=c.get('diagnostic_options',{}).get('added_classified_rows',{'n1':0,'lqb':0}),
                        candidate_sha256=b.sha(Path(td)/'candidates.jsonl'))
                    runs.append(result)
                    print(f"{rule} {cap or 'unlimited'}/{pool}: "+' '.join(f"{s} {result['splits'][s]['credited']} ({result['splits'][s]['filled']}/16)" for s in ('test','dev')),flush=True)
        plan=json.loads((Path(td)/'draw_plan.json').read_text())
    upper=[r for r in runs if r['rule']=='upper_bound']
    # Best: test aggregate filled, test credit, dev aggregate filled, dev credit; ties keep sweep order.
    best=max(upper,key=lambda r:(r['splits']['test']['filled'],r['splits']['test']['credited'],r['splits']['dev']['filled'],r['splits']['dev']['credited']))
    eligible=[r for r in upper if r['splits']['test']['filled']>=14]
    smallest=eligible[0] if eligible else None
    payload=dict(description='BENCH02H diagnostic only; UPPER BOUND is not admitted or benchmark-qualified',
        inputs=plan['input_shas'],code_sha256=b.sha(b.__file__),runner_sha256=b.sha(__file__),
        default_candidates_sha256=default_sha,default_candidates_byte_identical=True,
        checks=dict(combinations=48,locked_row_intersections=0,cap_violations=0),
        forced_editions={g:len(v) for g,v in cache['forced_groups'].items()},
        best=dict(cap=best['cap'],pool=best['pool'],splits=best['splits']),
        smallest_14_test_classes=None if smallest is None else dict(cap=smallest['cap'],pool=smallest['pool']),runs=runs)
    b.dump(dest/'sweep.json',payload)
    md=['# BENCH02H — edition-cap / forced-pool diagnostic sweep','',
        'Offline metadata only; network OFF, no spend. Production defaults remain edition cap 4 / series cap 12, forced editions excluded. No admission or benchmark qualification.',
        '', 'Dry uses exactly the sole split-identity reason. **UPPER BOUND (not admitted)** uses all W1/W2 split rows regardless of census verdict, retaining the classifier, exclusions, seeded draw order and 20% overdraw. Exact registered locked/eval rows are excluded in every pool. Forced editions are identified by exact registered N1/LQB row membership and must already be forced test editions. No train/dev edition is reassigned.',
        '', 'Credit = min(drawn, class quota); class filled means aggregate deficit zero, as in BENCH02G. Language/font subgroup deficits remain separate and cannot be substituted. Edition/source counts, edition maxima and top-five shares describe all drawn candidates, including overdraw. Caps are global across classes and both splits. Unlimited disables both edition and series caps. No series is invented when metadata is absent.',
        '', 'Smallest change that fills ≥ 14/16 test classes in the upper bound: '+(f"{smallest['cap'] or 'unlimited'}/{smallest['pool']}." if smallest else 'none among the 24 tested combinations.')+' Search order: increasing cap, then none/n1/lqb/both; this is a numerical ordering, not a recommendation.',
        '', 'Best is ranked by test classes filled, test credit, dev classes filled, then dev credit; ties retain sweep order. Classes are reported test/dev separately.',
        '', f"BENCH02G default candidates reproduced byte-identically: `{default_sha}`. Sweep checks: 48 combinations, zero locked-row intersections, zero edition/series cap violations.",
        '', 'Input caveat retained from BENCH02G: tags have a locally measured checksum, but the extract receipt has no coordinator-pinned output checksum. This upper bound cannot establish census_05 admission supply. Book diversity uses distinct edition IDs (gazette issues count as editions); the ≥10 editions / ≥3 sources diagnostic does not establish independent canonical works.',
        '', '## Pool additions','', 'Rows added before class selection/caps, excluding every exact registered locked/eval ID. Classified additions are the drawable primary-class subset. Membership counts: '+str(payload['forced_editions'])+'.',
        '', '| Rule | Pool | N1 rows added | LQB rows added | N1 classified | LQB classified |','|---|---|---:|---:|---:|---:|']
    for r in runs:
        if r['cap']==4:md.append(f"| {r['rule']} | {r['pool']} | {r['added_rows']['n1']} | {r['added_rows']['lqb']} | {r['added_classified_rows']['n1']} | {r['added_classified_rows']['lqb']} |")
    for rule in ('dry','upper_bound'):
        md+=['', '## '+('Dry — sole split reason' if rule=='dry' else 'UPPER BOUND (not admitted)'), '',
            '| Cap | Pool | Test credit /2460 | Dev credit /615 | Filled T/D /16 | Deficit T/D | Max edition T/D | Test top5 share | Diversity classes T/D | Subgroup-qualified T/D |',
            '|---|---|---:|---:|---|---|---|---:|---|---|']
        for r in runs:
            if r['rule']!=rule:continue
            t,d=(r['splits'][s] for s in ('test','dev'))
            md.append(f"| {r['cap'] or 'unlimited'} | {r['pool']} | {t['credited']} | {d['credited']} | {t['filled']}/{d['filled']} | {t['deficit']}/{d['deficit']} | {t['max_edition_lines']}/{d['max_edition_lines']} | {t['top5_share']:.2%} ({t['top5_lines']}/{t['drawn']}) | {t['diversity_pass_classes']}/{d['diversity_pass_classes']} | {t['subgroup_qualified_filled']}/{d['subgroup_qualified_filled']} |")
    md+=['','## Per-class deficits and diversity','', 'Each cell pair is test/dev; E/S are distinct editions/sources drawn. Diversity ✓ requires ≥10 editions AND ≥3 sources. Subgroup deficits are explicit JSON maps in the final column. Full precision and supply/overdraw counts are in sweep.json.']
    for r in runs:
        md+=['',f"### {r['rule']} — {r['cap'] or 'unlimited'}/{r['pool']}",'',
            '| Class | Credit T/D | Deficit T/D | Editions T/D | Sources T/D | Diversity T/D | Subgroup deficits T/D |','|---|---|---|---|---|---|---|']
        for cl in b.QUOTAS:
            t,d=(r['classes'][f'{s}:{cl}'] for s in ('test','dev'))
            pairs=[f"{min(t['drawn'],t['quota'])}/{min(d['drawn'],d['quota'])}"]
            pairs += [f"{t[k]}/{d[k]}" for k in ('deficit','editions','sources')]
            pairs += ['/'.join('✓' if v['editions']>=10 and v['sources']>=3 else '—' for v in (t,d)),
                ' / '.join(json.dumps(v['subgroup_deficits'],sort_keys=True) for v in (t,d))]
            md.append('| '+cl+' | '+' | '.join(pairs)+' |')
    b.output(dest/'SWEEP.md').write_text('\n'.join(md)+'\n')


if __name__=='__main__':main()
