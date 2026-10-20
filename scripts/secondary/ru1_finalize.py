"""Finalize RU1-0 evidence, including a blocked build. No reader launches.
--record-failed-attempt records the completed, all-failed crop inventory without
retrying or substituting the mismatched crops. It requires every usable ID in it.
"""
import argparse
import json
from pathlib import Path
import sys
from ru1_census import *

WORK=Path(__file__).resolve().parents[2]
READING=PROJECTS/'greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading'

def record_failed_attempt():
    # Pillow imported only under the documented x86_64 Python invocation.
    import ru1_build_packs as builder
    census=json.loads((ART/'census.json').read_text());pp=list(rows(ART/'positions.jsonl'))
    rr=[r for r in rows(SOURCE) if r['source']=='ia_russian'];byid={r['id']:r for r in rr}
    inputs=census['inputs'];vocab=json.loads((ART/'keys/prior_vocab.json').read_text())
    controls=builder.control_inventory(byid,vocab,census['books'],inputs)
    unavailable=list(rows(ART/'crop_unavailable.jsonl'));excluded,_=exclusion_ids()
    expected={r['id'] for r in rr if usable(r,excluded)}|{c['row_id'] for c in controls if c['row_id']}
    assert {r['row_id'] for r in unavailable}==expected
    assert all(r['reason']=='regenerated crop hash mismatch' for r in unavailable)
    assert len(unavailable)==len(expected)==1146
    for path in {byid[r]['crop_source_image'] for r in expected}:
        inputs[path]=sha(path)
    assert all(inputs[byid[r]['crop_source_image']]==byid[r]['crop_source_sha256'] for r in expected)
    inputs[str(COLLECT/'collect_v3/storage.py')]=sha(COLLECT/'collect_v3/storage.py')
    for c in controls:
        if c['row_id'] is None:
            m=c['legacy'];inputs[m['source_crop']]=sha(m['source_crop'])
            assert inputs[m['source_crop']]==m['source_crop_sha256']
    builder.record_blocked(rr,pp,census,controls,inputs,unavailable)


def finalize():
    build=json.loads((ART/'build.json').read_text());census=json.loads((ART/'census.json').read_text());c=build['counts']
    closure=json.loads((ART/'pack_closure.json').read_text())
    tests=json.loads((ART/'tests.json').read_text())
    inputs=build['inputs']
    for path in [WORK/'docs/records/labelfix/secondary/PLAN.md',WORK/'docs/records/briefs/RU10_census_packs.md',
                 COLLECT/'collect_v3/rules.py',COLLECT/'collect_v3/runner.py',COLLECT/'collect_v3/cards.py',
                 COLLECT/'docs/records/harvest/collect_v3/c1/efficiency/build.py']:
        inputs[str(path)]=sha(path)
    for rel in ['HANDOVER.md','prompts/yer.md','tools/build_packs.py','tools/map_answers.py','tools/common.py',
                'tools/scan_packs.py','tools/scan_rollout.py','tools/test_scan_rollout_v4.py','tools/replay_literal.py',
                'tools/ledger.py','launchers/run_bed.sh','launchers/run_read.sh','launchers/limit_probe.sh']:
        inputs[str(READING/rel)]=sha(READING/rel)
    assert sha(WORK/'docs/records/labelfix/secondary/prompts/yer.md')==sha(READING/'prompts/yer.md')
    assert all(sha(p)==h for p,h in inputs.items()),'input changed since census/build'
    lines=['# RU1-0 census and pack preparation', '',
           '**BLOCKED: no reader packs are ready.** All 1,146 W1 crop regenerations failed the required crop SHA256 check; '
           'the retained source-raster hashes passed. No replacement crops were used. No reader or limit probe ran, '
           'no image was viewed, no network was used, and no collector or .git writes were made.', '',
           'The 1,146 usable-row rule is reproduced exactly: cyrillic 949, numerics_tables 156, latin 40, nonletter 1. '+RULE, '',
           'All 10 W1 Russian books are pre1918 by the requested rule (at least 5 final hard signs or any ѣ/і/ѳ/ѵ); '
           'there are zero modern books. The requested 20-position modern spot check is unavailable in this input.', '',
           '## Census per book', '',
           'Final means immediately not followed by a Cyrillic letter, except `-` gets its own pre_hyphen class. '
           'A preceding Cyrillic letter is required. Offsets index Python Unicode code points in the unnormalized current `label`. '
           'Pre-hyphen positions are recorded and masked but never edit candidates. Uppercase signs are outside the specified lowercase ъ/ь census.', '',
           '| Book (source ia_russian) | Rows / usable | Final ъ all / usable | Final ь all / usable | Pre-hyphen ъ all / usable | Pre-hyphen ь all / usable |',
           '|---|---:|---:|---:|---:|---:|']
    for b in census['books'].values():
        fields=[f"{b['rows']} / {b['usable_rows']}"]
        for k in ['final:ъ','final:ь','pre_hyphen:ъ','pre_hyphen:ь']:fields.append(f"{b['all'].get(k,0)} / {b['usable'].get(k,0)}")
        lines.append('| '+b['book'].split(':',1)[1]+' | '+' | '.join(fields)+' |')
    lines+=['', 'Counts by book and primary_class are in `artifacts/ru1/census.json`; every position and prior is in '
            '`artifacts/ru1/positions.jsonl`. Across all rows: final ъ 4,156, final ь 1,053, pre-hyphen ъ 41, pre-hyphen ь 31. '
            'Usable: final ъ 1,653, final ь 435, pre-hyphen ъ 19, pre-hyphen ь 15.', '',
            '## Orthographic prior', '', PRIOR_METHOD, '',
            '| Prior on Google ь (final and pre_hyphen) | All | Usable |','|---|---:|---:|']
    for k in ['ъ_only','ь_only','both','unknown']:lines.append(f"| {k} | {c['prior_all'].get(k,0)} | {c['prior_usable'].get(k,0)} |")
    finalpp=[p for p in rows(ART/'positions.jsonl') if p['google']=='ь' and p['kind']=='final']
    from collections import Counter
    lines+=['', 'Final-only Google-ь prior distributions: all '+str(dict(Counter(p['prior'] for p in finalpp)))+
            '; usable '+str(dict(Counter(p['prior'] for p in finalpp if p['usable'])))+'.', '',
            '## Bed, controls and contexts', '',
            f"The planned pre1918 bed has **{c['planned_bed_lines']} lines / {c['planned_bed_slots']} masked slots**, "
            f"including {c['planned_bed_soft_final_positions']} candidate final ь positions after excluding all C1 control lines. "
            'All final yer signs are masked, including Google hard signs and pre-hyphen signs. Actual packed bed: **0 lines / 0 slots**.', '',
            'The control inventory has **59 lines / 65 slots**: 31 slot-bearing lines plus 28 zero-slot lines. '
            '19 C1 lines map exactly to W1; the 40 v2 lines have older source IDs and no W1 match. '
            'Their saved adjudication crops match the recorded SHA256 values from the original efficiency builder. '
            'The 19 C1 crops failed regeneration; no controls were packed. `keys/control_inventory.json` preserves table ink truth, '
            'offsets and the missing-W1 status explicitly. No invented W1 IDs.', '',
            f"Context list: **empty (0 built; {c['planned_contexts']} planned at ≤90 bed items plus about 10% controls)**. "
            'The builder uses seeded ordering and round-robin controls without within-context repetition; opaque IDs are fresh random hex. '
            'The closure scanner was run against the empty root; the overall readiness gate is FAIL because required contexts are absent. '
            'There are no manifests to issue for a nonexistent context.', '',
            f"Codex estimate: approximately {c['planned_bed_lines']+round(c['planned_bed_lines']/9)} item reads × 0.2/100 = "
            f"{(c['planned_bed_lines']+round(c['planned_bed_lines']/9))*.002:.3f} weekly points for the available planned bed and controls. "
            'The modern supplement is excluded from this estimate because no eligible positions exist. '
            'Live meter: not probed (network OFF and no reading run). Usage ledger remains empty.', '',
            '## Tooling and validation', '',
            'The yer prompt and scanner-v4 test are copied verbatim. Scanner-v4 differs only in its replay temporary-directory path. '
            'Pack scanner adaptations select context-specific private keys, permit one reader, and check the pack-root shape. '
            'The original builder and mapper are retained under `scripts/secondary/reading/reference/`. '
            'The prepared launchers use gpt-6.1-sol / medium, network and web disabled, before/after probes, and the 78% refusal. '
            'They were syntax-checked, never executed. The mapper voids every edit proposal after more than one control-slot error, '
            'keeps u/other for review, and never edits Google ъ or pre-hyphen slots. Its output is a review proposal, not a label version.', '',
            f"Tests: {tests['passed']} passed ({tests['text_passed']} text tests; {tests['scanner_passed']} copied scanner-v4 tests). "
            'See `artifacts/ru1/text_tests.txt`, `scanner_tests.txt`, and `tests.json`.', '',
            'Rebuild with the required x86_64 Python: `python3 -B scripts/secondary/ru1_census.py`; '
            '`/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B scripts/secondary/ru1_build_packs.py`. '
            'The builder fails closed and records a blocked build if any required crop fails. '
            'The sourcing lead must resolve the regeneration/hash recipe and identify a modern-book input before this can become READY.']
    report=WORK/'docs/records/labelfix/secondary/RU10_REPORT.md';report.write_text('\n'.join(lines)+'\n')
    outputs={}
    for root in [WORK/'scripts/secondary',WORK/'artifacts/ru1',WORK/'docs/records/labelfix/secondary']:
        for p in root.rglob('*'):
            if p.is_file() and p.name!='RU10_RECEIPT.json' and '__pycache__' not in p.parts and p.name!='PLAN.md':outputs[str(p)]=sha(p)
    for n in ['test_ru1_census.py','test_ru1_map_answers.py']:outputs[str(WORK/'tests'/n)]=sha(WORK/'tests'/n)
    receipt=dict(schema='RU10-v1',status='BLOCKED',inputs=inputs,outputs=outputs,counts=c,contexts=[],
                 usable_rule=RULE,prior_method=PRIOR_METHOD,pack_closure=closure,tests=tests,
                 no_reader_run=True,no_images_viewed=True,network=False,collector_writes=False,git_writes=False,
                 blockers=build['limitations'],receipt_hash_policy='Receipt excludes itself; all deliverable hashes bound here.')
    dump(ART/'RU10_RECEIPT.json',receipt)
    print(json.dumps(dict(status=receipt['status'],counts=c,tests=tests),ensure_ascii=False,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--record-failed-attempt',action='store_true');a=p.parse_args()
    if a.record_failed_attempt:record_failed_attempt()
    else:finalize()
