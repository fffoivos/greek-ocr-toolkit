"""Verify S7 evidence, unchanged instruments, negative qualification and scope."""
from greekocr.ops.data_root import input_path as _data_input
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
from greekocr.labelfix.reading import QUALIFIED_GEOMETRY
from scripts.labelfix.owner_reading import digest,load_configuration
from scripts.labelfix.s5_validate import read

O=Path('docs/records/labelfix/spellcheck');E=O/'S7_evidence'


def main():
    receipt=json.loads((E/'receipt.json').read_text())
    assert receipt['network'] is False and receipt['ctc_forward_passes']==receipt['r1_forward_passes']==0
    assert receipt['lines']==1264
    for p,d in receipt['source_sha256'].items():assert digest(p)==d,p
    load_configuration(E/'accepted_config.json')
    original=json.loads((E/'original_launch_baseline.json').read_text())
    metrics=json.loads((E/'metrics.json').read_text())
    assert set(metrics)=={'baseline','S1','S2','S3','accepted'}
    for k in ('pixel','combined'):
        assert original['capitals'][k]=={q:metrics['baseline']['capitals'][k][q] for q in ('tp','fp','fn')}
    assert metrics['accepted']==metrics['baseline']
    # Full line equality, not just equal aggregate scores.
    count=0
    with gzip.open(_data_input(E/'baseline_lines.jsonl.gz'),'rt') as a,gzip.open(_data_input(E/'accepted_lines.jsonl.gz'),'rt') as b:
        for x,y in zip(a,b,strict=True):
            assert x==y
            count+=1
    assert count==1264
    assert not QUALIFIED_GEOMETRY
    assert metrics['S1']['heldout']['presence']['fused']['recall']<metrics['baseline']['heldout']['presence']['fused']['recall']
    assert metrics['S2']['capitals']['pixel']['recall']<metrics['baseline']['capitals']['pixel']['recall']
    assert metrics['S3']['heldout']['presence']==metrics['baseline']['heldout']['presence']
    for k,v in metrics.items():
        assert v['kind_disagreements']['original']==80
        assert v['heldout']['presence']['all']['n']==20425
        assert v['heldout']['presence']['all']['known_slots']==19249
        assert v['heldout']['presence']['fused']['n']==756
        assert v['heldout']['presence']['merged_accent']['n']==590
        assert v['capitals']['pixel']['n']==18960 and v['capitals']['pixel']['tp']+v['capitals']['pixel']['fn']==1189
        assert v['capital_disagreement']['pixel']['n']==753
        assert v['owner']['review_v16']['combined']['n']==49 and v['owner']['examples_v10']['combined']['n']==57
    assert metrics['accepted']['kind_disagreements']['all_owner_slots']==80
    assert metrics['accepted']['hold_slots']['slots']==87
    # The CN1 evaluation body is verbatim, including all strict assertions.
    old=Path('scripts/labelfix/cn1_measure.py').read_text();new=Path('scripts/labelfix/s7_owner.py').read_text()
    assert old[old.index('    parsed=R1.evaluate'):old.index('    holds=[];pred={}')]==new[new.index('    parsed=R1.evaluate'):new.index('    return records, summaries')]
    head=subprocess.check_output(['git','--no-optional-locks','rev-parse','HEAD'],text=True).strip()
    assert head==original['head']
    tracked=subprocess.check_output(['git','--no-optional-locks','ls-tree','-r','--name-only','HEAD','tests/labelfix'],text=True).splitlines()
    for p in tracked:
        assert Path(p).read_bytes()==subprocess.check_output(['git','--no-optional-locks','show','HEAD:'+p]),p
    summary={}
    for variant in ('scope_only','S1','S2','S3','accepted'):
        d=E/('m2_'+variant);r=json.loads((d/'M2_runtime_receipt.json').read_text())
        assert r['ctc_forward_passes']==r['r1_forward_passes']==r['newly_aligned_lines']==0
        assert r['scope_excluded_lines']==40 and r['inferred_lines']==433
        assert digest(d/'runtime.jsonl')==r['runtime_sha256']
        assert digest(r['alignment_path'])==r['alignment_sha256']
        score_receipt=json.loads((d/'M2_score_receipt.json').read_text())
        assert score_receipt['scorer_sha256']==digest('scripts/labelfix/m2_score.py')
        assert score_receipt['runtime_sha256']==r['runtime_sha256']
        for name,h in score_receipt['outputs'].items():assert digest(d/name)==h
        for p,h in r['protected_source_sha256'].items():assert digest(p)==h,p
        runs=read(d/'runtime.jsonl')
        assert len(runs)==513 and Counter(x['status'] for x in runs)=={'ok':433,'skipped':80}
        for run in runs:
            if run['status']!='ok':continue
            assert len(run['detector']['slots'])==len(run['modes']['PRESENCE']['slots'])==len(run['modes']['FULL']['slots'])
            for p,f in zip(run['modes']['PRESENCE']['slots'],run['modes']['FULL']['slots'],strict=True):
                assert p['base']==f['base'] and p['start']==f['start']
                assert f['hold'] or not p['hold']
        score=json.loads((d/'M2_metrics.json').read_text())['POOLED']
        assert sum(score['modes']['PRESENCE']['errors'].values())==77
        summary[variant]=score['modes']['PRESENCE']
    assert summary['scope_only']==summary['accepted']
    assert summary['accepted']['errors']=={'corrected':25,'HOLD':40,'missed':12}
    assert summary['accepted']['accepted_changed_slots']==20
    assert summary['accepted']['lines_with_HOLD']==327
    assert summary['accepted']['by_type']['capital_breathing_dropped_or_apostrophe']['corrected']==1
    assert summary['S3']['errors']['corrected']==3
    assert summary['S3']['lines_with_HOLD']>summary['accepted']['lines_with_HOLD']
    boxes=json.loads((E/'box_summaries.json').read_text())
    for key,v in boxes['launch_to_accepted'].items():
        if any(' / '+k+' / ' in key for k in ('lost','added','moved')):assert v==0
    assert boxes['launch_to_accepted']['lines compared']==92
    oldreceipt=O/'clariden/R1_result_3678928/score_receipt.json'
    rr=json.loads(oldreceipt.read_text())
    for p,h in rr['scorer_sha256'].items():assert digest(p)==h
    for name in ('metrics.json','RESULT.md'):
        assert (oldreceipt.parent/name).read_bytes()==(E/'R1_score_final'/name).read_bytes()
    full=(E/'pytest_full.txt').read_text();offline=(E/'pytest_offline.txt').read_text()
    assert '241 passed' in full and '1 error' in full and 'Operation not permitted' in full
    assert '241 passed, 1 deselected' in offline
    files=[Path(__file__),Path('scripts/labelfix/s7_report.py'),Path('scripts/labelfix/s7_m2_replay.py'),Path('scripts/labelfix/s7_m2_scope.py'),
           Path('scripts/labelfix/s7_box_regression.py'),Path('scripts/labelfix/s7_launch_baseline.py'),Path('tests/labelfix/test_s7.py'),
           E/'metrics.json',E/'receipt.json',E/'box_summaries.json',E/'pytest_full.txt',E/'pytest_offline.txt',E/'original_launch_baseline.json',oldreceipt,
           Path('scripts/labelfix/m2_score.py'),Path('scripts/labelfix/m2_run.py'),E/'accepted_config.json']
    files += [E/('m2_'+v)/'M2_score_receipt.json' for v in ('scope_only','S1','S2','S3','accepted')]
    for p in (O/'S7_REPORT.md',E/'qualification.json'):
        if p.exists():files.append(p)
    result=dict(status='PASS for runnable offline checks; HTTP fixture BLOCKED by sandbox',head=head,
        tests_passed=241,http_fixture_blocked=1,existing_test_sources_unchanged=len(tracked),accepted=[],
        baseline_and_accepted_lines_identical=count,ctc_forward_passes=0,r1_forward_passes=0,retraining=False,network=False,
        source_sha256=receipt['source_sha256'],evidence_sha256={str(p):digest(p) for p in files})
    (E/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','evidence_sha256')},indent=2))


if __name__=='__main__':main()
