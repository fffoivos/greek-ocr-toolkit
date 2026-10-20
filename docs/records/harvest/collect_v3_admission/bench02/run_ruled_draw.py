#!/usr/bin/env python3
"""BENCH02I offline cap evaluation and census_03 dry draw; stdlib only."""
from collections import Counter
import json
from pathlib import Path
import tempfile
import bench02_draw as b
from run_sweep import inputs, summarize

TAGS_SHA='9f8f0c721766a95a10cece695726f8e9581214169f0fcde3abe46d3add46d26b'
CAPS=(12,25,50)


def below(counts):
    return [k for k,v in counts['classes'].items() if v['supply']>0 and v['credited']<.9*v['quota']]


def main():
    cache={};evaluations=[];original=b.sha(b.HERE/'census03/dryrun/candidates.jsonl')
    with tempfile.TemporaryDirectory(dir=b.HERE,prefix='.ruled-') as td:
        for cap in CAPS:
            c=b.draw(**inputs(),dest=Path(td),edition_cap=cap,upper_bound=True,
                tags_sha256=TAGS_SHA,_cache=cache)
            candidates=list(b.rows(Path(td)/'candidates.jsonl'))
            assert not {r['row_id'] for r in candidates}&cache['locked']
            assert max(c['edition_counts'].values(),default=0)<=cap
            assert max(c['series_counts'].values(),default=0)<=3*cap
            evaluations.append(dict(cap=cap,below90=below(c),**summarize(c,candidates)))
            print(cap, evaluations[-1]['splits'], 'below90',below(c),flush=True)
        chosen=next((r['cap'] for r in evaluations if not r['below90']),50)
        assert chosen==b.DEFAULT_EDITION_CAP, f'Update DEFAULT_EDITION_CAP to {chosen}, then rerun'
        upper=b.draw(**inputs(),dest=b.HERE/'sweep/upper_bound_ruled',upper_bound=True,tags_sha256=TAGS_SHA,_cache=cache)
        dest=b.HERE/'census03/dryrun_v2'
        dry=b.draw(**inputs(),dest=dest,dry_run=True,tags_sha256=TAGS_SHA,_cache=cache)
        candidate_bytes=(dest/'candidates.jsonl').read_bytes()
        replay=b.draw(**inputs(),dest=Path(td),dry_run=True,tags_sha256=TAGS_SHA)
        assert candidate_bytes==(Path(td)/'candidates.jsonl').read_bytes()
        assert dry==replay
    candidates=list(b.rows(dest/'candidates.jsonl'))
    assert len({(r['parent_id'],r['row_id']) for r in candidates})==len(candidates)
    assert not {r['row_id'] for r in candidates}&cache['locked']
    assert b.sha(b.HERE/'census03/dryrun/candidates.jsonl')==original
    dsum=summarize(dry,candidates)
    usum=summarize(upper,list(b.rows(b.HERE/'sweep/upper_bound_ruled/candidates.jsonl')))
    plan=json.loads((dest/'draw_plan.json').read_text())
    payload=dict(chosen=chosen,evaluations=evaluations,dry=dsum,upper_bound=usum,
        pool=dry['pool_options'],upper_pool=upper['pool_options'],tags=plan['tags_verification'],
        checks=dict(locked_row_intersections=0,deterministic=True,original_dryrun_candidates_sha256=original),
        input_shas=plan['input_shas'],runner_sha256=b.sha(__file__),code_sha256=b.sha(b.__file__))
    b.dump(b.HERE/'sweep/cap_choice.json',payload)
    md=['# BENCH02I cap choice','',
        'Coordinator ruling: both forced pools; per class × edition cap and per class × series cap (3×). All-rows upper bound (not admitted), unchanged classification, quotas, precedence, exclusions and subgroup limits. Credit = min(drawn, quota), including candidates up to the unchanged 20% overdraw target.',
        '', 'With supply means eligible primary-class supply > 0. Test and dev are evaluated independently; every supplied class must reach 90%. No-supply classes remain deficits and do not block. Diversity counts all drawn candidates; books are edition IDs (gazette issues included), not verified canonical works.',
        '', '| Cap | Test credit /2460 | Dev credit /615 | Supplied classes below 90% (test; dev) | Pass |','|---:|---:|---:|---|---|']
    for r in evaluations:
        md.append(f"| {r['cap']} | {r['splits']['test']['credited']} | {r['splits']['dev']['credited']} | "+'; '.join(', '.join(k.split(':')[1] for k in r['below90'] if k.startswith(s+':')) or 'none' for s in ('test','dev'))+f" | {not r['below90']} |")
    md+=['',f'Chosen production default: **{chosen}**. '+('No tested value meets the condition; fallback 50. Below 90%: '+', '.join(evaluations[-1]['below90']) if all(r['below90'] for r in evaluations) else 'Smallest passing value.'),
        '', 'Series cap compliance is unverifiable without series identity; no identity is invented. Zero-supply deficits, bg/uk subquotas, Serbian-only modern Cyrillic and polytonic awaiting sf7 remain visible. No quota transfer.',
        '', '## Evaluation per class and split','', '| Cap | Split:class | Supply | Credit/quota | Editions | Sources | Top-edition share | ≥10 books / ≥3 sources |','|---:|---|---:|---|---:|---:|---:|---|']
    for r in evaluations:
        for k,v in r['classes'].items():
            md.append(f"| {r['cap']} | {k} ({v['label']}) | {v['supply']} | {v['credited']}/{v['quota']} | {v['editions']} | {v['sources']} | {v['top_edition_share']:.2%} | {v['diversity_pass']} |")
    b.output(b.HERE/'sweep/CAP_CHOICE.md').write_text('\n'.join(md)+'\n')
    md=['# BENCH02I — census_03 dry draw v2','',
        f'Offline metadata only, network OFF, no spend. Production defaults: {chosen} per class × edition; both forced pools. Sole split-identity reason only; no admission or benchmark qualification. BENCH02G dryrun/ preserved. Reproduce: `python3 -B bench02/run_ruled_draw.py` from collect_v3_admission/.',
        '',f"Tags: {plan['tags_verification']}. The old receipt is unchanged; coordinator-pinned checksum supplied by argument and checked. New extract receipts carry tags_sha256 and tags_bytes; census_05 wrapper requires receipt sha. Input hashes and exact deterministic selection/emission order are in dryrun_v2/draw_plan.json.",
        '', '| Split | Class | Pre-filter | Eligible supply | Quota | Target | Drawn | Credited | Deficit | Editions | Sources | Top-edition share | ≥10 books / ≥3 sources |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    pre=Counter()
    for k,n in dry['pre_filter_class_source_edition'].items():
        side,cl,_,_=k.split('|');pre[(side,cl)]+=n
    for cl in sorted(b.QUOTAS):
        for side in ('test','dev'):
            v=dry['classes'][f'{side}:{cl}'];label=cl+(' (Serbian-only)' if v['label']=='Serbian-only' else '')
            md.append(f'| {side} | {label} | {pre[(side,cl)]} | '+' | '.join(str(v[k]) for k in ('supply','quota','overdraw_target','drawn','credited','deficit','editions','sources'))+f" | {v['top_edition_share']:.2%} | {v['diversity_pass']} |")
    for title,result in (('Dry v2',dsum),('All-rows upper bound (not admitted)',usum)):
        for side,v in result['splits'].items():
            md+=['',f"{title} {side}: credit {v['credited']}/{v['quota']}; drawn {v['drawn']}; filled {v['filled']}/16; deficit {v['deficit']}; subgroup-qualified filled {v['subgroup_qualified_filled']}/16."]
    md+=['', f"Forced-pool additions before caps/class selection (dry): {dry['pool_options']}; upper bound: {upper['pool_options']}.",
        '', 'Books diagnostic uses distinct edition IDs, including gazette issues; canonical-work independence is unverified. Series identity remains absent, so 3× per-class series cap is unverifiable. Polytonic and dictionary/journal deficits remain (sf7 pending); bg/uk have no supply, and modern Cyrillic is Serbian-only. Reopening forced editions restores historical Russian test supply (345 sole-reason rows, 120/120 credit); the earlier zero-supply test deficit no longer applies. Historical Russian dev still has no supply. No quota transfers.',
        '', '## Subgroup deficits','', '| Split:class | Supply by subgroup | Drawn | Quotas | Deficits |','|---|---|---|---|---|']
    for side in ('test','dev'):
        for cl in ('modern_cyrillic','font_extremes'):
            v=dry['classes'][side+':'+cl];group='language' if cl=='modern_cyrillic' else 'font_size'
            supplied=Counter(r.get(group) for r in cache['slimrows'] if r.get('split')==side and r['primary_class']==cl and r['row_id'] not in cache['locked'] and r['reasons']==[b.REASON] and r.get('edition_id') not in set(dry['excluded_editions']))
            md.append('| '+side+':'+cl+' | '+' | '.join(json.dumps(x,sort_keys=True) for x in (dict(supplied),v['subgroups'],v['subgroup_quotas'],v['subgroup_deficits']))+' |')
    md+=['','Full tag availability, cap-hit IDs, source/edition accounting and deficits are in dryrun_v2/counts.json. Fresh-cache replay produced identical candidates and counts; no locked rows drawn; candidates unique; original dryrun candidate checksum unchanged. Thresholds and classifier are unchanged. census_05 still requires admitted supply and its own receipt; the upper bound is not admission evidence.']
    b.output(b.HERE/'census03/DRYRUN_V2.md').write_text('\n'.join(md)+'\n')
    print(json.dumps(dict(cap=chosen,dry=dsum['splits'],upper=usum['splits'],pool=dry['pool_options']),indent=2))


if __name__=='__main__':main()
