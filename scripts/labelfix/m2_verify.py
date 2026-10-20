"""Check the delivered M2 evidence, source bindings and numerical partitions."""
from collections import Counter
import json
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from PIL import Image
from greekocr.labelfix.text import clusters, nfd
from scripts.labelfix.m2_run import ROOT, OUT, CACHE, rows, sha


def letters(text):
    return [c for c in clusters(nfd(text)) if c.base.isalpha()]


def main():
    receipt = json.loads((OUT/'M2_runtime_receipt.json').read_text())
    initial = json.loads((OUT/'M2_initial_runtime_receipt.json').read_text())
    assert receipt['device']=='cpu'
    assert initial['newly_aligned_lines']==473
    assert receipt['newly_aligned_lines']==0
    assert initial['alignment_sha256']==receipt['alignment_sha256']==sha(CACHE/'align_s0.jsonl')
    assert initial['runtime_sha256']==receipt['runtime_sha256']==sha(CACHE/'runtime.jsonl')
    assert receipt['script_sha256']==sha(ROOT/'scripts/labelfix/m2_run.py')
    for group in ('model_bindings','input_sha256'):
        for p,expected in receipt[group].items():
            assert sha(p)==expected, p
    for p,expected in receipt['protected_source_sha256'].items():
        assert sha(ROOT/p)==expected, p
        # Source state must also match task launch, regardless of external docs commits.
        original = subprocess.check_output(['git','show',receipt['launch_head']+':'+p],cwd=ROOT)
        assert hashlib.sha256(original).hexdigest()==expected, p
    lines = rows(OUT/'M2_lines.jsonl.gz')
    assert len(lines)==513 and len({l['id'] for l in lines})==513
    assert all(l['line_id']==l['key']['line_id'] for l in lines)
    inferred = [l for l in lines if l['status']=='ok']
    assert len(inferred)==473 and len({l['source'] for l in inferred})==12
    assert len({l['source'] for l in lines})==13
    skipped = [l for l in lines if l['status']!='ok']
    assert len(skipped)==40 and all(l['skip_reason']=='non_Greek_cyrillic_cohort' for l in skipped)
    coverage=Counter()
    for l in inferred:
        assert sha(l['crop'])==receipt['crop_sha256'][l['id']]
        cov={c['start']:c for c in l['coverage']}
        pred={p['start']:p for p in l['r1_predictions']}
        assert len(cov)==len(l['coverage']) and len(pred)==len(l['r1_predictions'])
        assert set(pred)=={i for i,c in cov.items() if c['scored']}
        coverage['eligible']+=len(cov);coverage['admitted']+=len(pred)
        recognized_bases=[c.base for c in letters(l['recogniser_nfd'])]
        for mode in ('PRESENCE','FULL'):
            rd=l['modes'][mode]
            assert [c.base for c in letters(rd['text'])]==recognized_bases
            assert [s['base'] for s in rd['slots']]==recognized_bases
            assert {s['start'] for s in rd['hold_slots']}=={s['start'] for s in rd['slots'] if s['hold']}
            assert all(bool(s['hold_reasons'])==bool(s['hold']) for s in rd['slots'])
            assert not rd['removed_by_constraint']
        for p,f in zip(l['modes']['PRESENCE']['slots'],l['modes']['FULL']['slots']):
            assert p['parts']==f['parts']
            assert not p['hold'] or f['hold']
    assert coverage==Counter(eligible=8876,admitted=8858)
    ledger=rows(OUT/'M2_pair_ledger.jsonl')
    cases=rows(OUT/'M2_pairs_scored.jsonl')
    assert {c['case_id'] for c in cases}=={c['case_id'] for c in ledger if c['included']}
    assert len(cases)==77
    byid={l['id']:l for l in lines}
    reverse={'psili':'\u0313','dasia':'\u0314','acute':'\u0301','grave':'\u0300',
             'circumflex':'\u0342','subscript':'\u0345','dialytika':'\u0308'}
    for c in cases:
        for mode in ('PRESENCE','FULL'):
            outcome=c['modes'][mode]['outcome']
            assert outcome in ('corrected','HOLD','missed')
            slots={s['start']:s for s in byid[c['id']]['modes'][mode]['slots']}
            if outcome=='corrected':
                mapped=[slots[i] for i in c['recognizer_nfd_letter_offsets']]
                assert not any(s['hold'] for s in mapped)
                assert [(s['base'],{reverse[p] for p in s['parts']}) for s in mapped]==[(p.base,set(p.marks)) for p in letters(c['printed'])]
            elif outcome=='HOLD':
                assert any(slots[i]['hold'] for i in c['recognizer_nfd_letter_offsets'] if i is not None)
    metrics=json.loads((OUT/'M2_metrics.json').read_text())
    for mode in ('PRESENCE','FULL'):
        pooled=metrics['POOLED']['modes'][mode]
        assert pooled['errors']==dict(Counter(c['modes'][mode]['outcome'] for c in cases))
        for field in ('accepted_changed_slots','accepted_mark_edits','held_reference_marks','held_slots_on_correct_cards','lines_with_HOLD'):
            assert pooled[field]==sum(m['modes'][mode][field] for s,m in metrics.items() if s!='POOLED')
        for typ,counts in pooled['by_type'].items():
            assert counts==dict(Counter(c['modes'][mode]['outcome'] for c in cases if c['type']==typ))
    reviews=rows(OUT/'M2_spotchecks.jsonl')
    queue=rows(OUT/'M2_spotcheck_queue.jsonl')
    assert len(reviews)==len(queue)==20
    assert [r['id'] for r in reviews]==[r['id'] for r in queue]
    assert Counter(r['matches_print'] for r in reviews)==Counter(yes=14,no=3,uncertain=3)
    for r in json.loads((OUT/'M2_visual/manifest.json').read_text()):
        with Image.open(r['crop']) as im:
            expected=np.asarray(im.convert('RGB').crop(tuple(r['native_window'])))
        with Image.open(OUT/'M2_visual'/r['native_png']) as im:
            assert np.array_equal(expected,np.asarray(im))
    report=(OUT/'M2_REPORT.md').read_text()
    assert 'pending' not in report
    assert report.splitlines()[-1].startswith('M2 RESULT: 473 lines/12 sources; Google mark errors 77:')
    artifacts=sorted(p for p in OUT.glob('M2*') if p.is_file() and p.name!='M2_validation.json')
    scripts=sorted((ROOT/'scripts/labelfix').glob('m2_*.py'))
    result=dict(status='PASS',inventory=513,inferred=473,sources=12,excluded=40,
        error_pairs=77,coverage=dict(coverage),visual_checks=20,initial_replay_runtime_identical=True,
        launch_inference_sources_match=True,head_changes=receipt['changes_since_launch'],
        artifact_sha256={p.name:sha(p) for p in artifacts},script_sha256={p.name:sha(p) for p in scripts})
    (OUT/'M2_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if not k.endswith('sha256')},indent=2))


if __name__=='__main__':
    main()
