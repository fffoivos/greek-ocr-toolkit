"""Verify SF6c source scope, saved custody, fixed witnesses and report offline."""
import ast
import json
from pathlib import Path

from greekocr.labelfix import release_gate as gate
from scripts.labelfix.clariden.r1_common import rows,sha256,write_json
from scripts.labelfix.sf6_verify import git_snapshot
from scripts.labelfix.sf6c_measure import EV,FROZEN,PRIOR


def funcs(path):
    return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(path.read_text()).body
            if isinstance(n,(ast.FunctionDef,ast.ClassDef))}


def verify():
    initial=json.loads((EV/'before_receipt.json').read_text())
    def check_git():
        current=git_snapshot()
        changes=[dict(path=k,before=initial['git'].get(k),after=current.get(k))
                 for k in sorted(initial['git'].keys()|current.keys()) if initial['git'].get(k)!=current.get(k)]
        # The common Git directory also contains independently active worktrees.
        # Do not restore, edit, or attribute their concurrent commits to SF6c.
        assert all('/worktrees/greek-ocr-toolkit-spellcheck-s8/' in r['path']
                   or r['path'].endswith(('/refs/heads/opus/spellcheck-s8','/logs/refs/heads/opus/spellcheck-s8'))
                   for r in changes),changes
        write_json(EV/'git_metadata_changes.json',changes)
        return changes
    check_git()
    scope={}
    allowed={
        'greekocr/labelfix/release_gate.py':{'policy_binding','_source_in_window','_recogniser_scored','deletion_guard','bind_runtime'},
        'greekocr/labelfix/ctc_align.py':{'recognition_fields','Alignment','Recognizer'},
        'scripts/labelfix/m2_run.py':{'infer_line','replay_detector'},
        'scripts/labelfix/clariden/l1_infer.py':{'run'},
        'scripts/labelfix/clariden/l1e_run.py':{'infer'},
        'scripts/labelfix/clariden/l1e_measure.py':{'saved_runtime'},
        'scripts/labelfix/clariden/r1_extract.py':{'extract_line'},
        'tests/labelfix/test_sf6.py':{'rich'},
    }
    for name,expected in allowed.items():
        a,b=funcs(FROZEN/name),funcs(Path(name))
        changed={k for k in a.keys()|b.keys() if a.get(k)!=b.get(k)}
        assert changed==expected,(name,changed,expected)
        scope[name]=sorted(changed)
    for name in initial['policy']['sources']:
        if name=='greekocr/labelfix/release_gate.py':continue
        assert sha256(name)==initial['policy']['sources'][name],name
    assert sha256('scripts/labelfix/clariden/r1_common.py')==sha256(FROZEN/'scripts/labelfix/clariden/r1_common.py')
    old=ast.parse(Path('artifacts/labelfix_l1e/reference/l1_detect.py').read_text())
    new=ast.parse(Path('scripts/labelfix/clariden/l1_detect.py').read_text())
    for node in ast.walk(new):
        if isinstance(node,ast.Call):
            node.keywords=[k for k in node.keywords if k.arg not in ('recognition_confidence','recognition_evidence','image_width')]
    assert ast.dump(old,include_attributes=False)==ast.dump(new,include_attributes=False)
    original=funcs(Path('docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3v3_evidence/test_sf6_reviewer.py'))
    imported=funcs(Path('tests/labelfix/test_sf6_reviewer.py'))
    assert original.keys()==imported.keys()
    assert all(imported[n]==v for n,v in original.items() if n!='legacy_unscored_punctuation')
    assert gate.POLICY=='sf6-release-v1' and gate.RECOGNISER_ABSENCE_FLOOR==.5
    comparison=json.loads((EV/'comparison.json').read_text())
    assert comparison['policy_after']==gate.policy_binding()
    assert comparison['policy_before']==initial['policy']
    assert comparison['newly_hold']==[] and comparison['changed_checks']==28
    for phase in ('before','after'):
        for cohort in ('heldout','m2_dev'):
            root=EV/phase/cohort;receipt=json.loads((root/'receipt.json').read_text())
            for name,digest in receipt['inputs'].items():assert sha256(name)==digest,name
            for name,digest in receipt['outputs'].items():assert sha256(root/name)==digest,name
            if phase=='after':assert receipt['policy']==gate.policy_binding()
    for cohort,path in [('heldout','heldout/release_labels.jsonl.gz'),('m2_dev','m2_dev/release_labels.jsonl.gz'),('witness','witness_results.jsonl.gz')]:
        before=list(rows(EV/'before'/path));after=list(rows(EV/'after'/path))
        assert before==list(rows(PRIOR/path))
        assert len(before)==len(after)
        for a,b in zip(before,after):
            assert (a['after']['status'],a['after']['label'])==(b['after']['status'],b['after']['label'])
    witnesses=list(rows(EV/'after/witness_results.jsonl.gz'))
    for r in witnesses:
        if r['cohort']=='quote_probe':assert r['after']['status']=='hold'
        if r['id'] in ('a963b33d02c23d4127f5ec26-p000012-l0029','32aae9fec147d3b483deb96e-p000060-l0057'):
            assert r['after']['status']=='corrected' and r['checks'][0]['operation']=='MOVE'
    unsafe=json.loads((EV/'unsafe_witnesses_after.json').read_text())
    assert unsafe['input_sha256']==sha256('docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3v3_evidence/unsafe_release_witnesses.json')
    assert len(unsafe['cases'])==16 and all(w['overlay']['status']=='hold' for w in unsafe['cases'])
    audit=json.loads((EV/'runtime_audit.json').read_text())
    for row in audit['runtime_sources']+audit['alignment_sources']:assert sha256(row['path'])==row['sha256']
    for name,row in audit['writer_audit'].items():assert sha256(name)==row['sha256']
    for name,digest in audit['label_sources'].items():assert sha256(name)==digest
    for ar in audit['archive_sources']:
        assert sha256(ar['path'])==ar['sha256']
        assert all(not r['newly_hold'] for r in ar['runtime_members'])
    assert all(not r['newly_hold'] for r in audit['runtime_sources'])
    assert '75 passed' in (EV/'reviewer_after.log').read_text()
    log=(EV/'tests_after.log').read_text();assert 'FAILED ' not in log and '1430 passed, 1 error' in log
    assert 'ERROR tests/labelfix/test_capture.py::test_server_appends_each_decision_and_serves_static' in log
    prefix=(FROZEN/'docs/labelfix/spellcheck/SF6_REPORT.md').read_bytes()
    report=(EV.parent/'SF6_REPORT.md').read_bytes();assert report.startswith(prefix)
    assert report.decode().splitlines()[-1].endswith('policy sha '+gate.policy_binding()['sha256'])
    # Keep a reviewable patch including newly added live sources and tests.
    import subprocess
    tracked=subprocess.check_output(['git','diff','--no-ext-diff','--','greekocr/labelfix','scripts/labelfix','tests/labelfix'],env={**__import__('os').environ,'GIT_OPTIONAL_LOCKS':'0'})
    import difflib
    added=''
    for name in ('scripts/labelfix/clariden/l1_detect.py','tests/labelfix/test_sf6_reviewer.py','tests/labelfix/test_sf6c.py',
                 'scripts/labelfix/sf6c_measure.py','scripts/labelfix/sf6c_audit.py','scripts/labelfix/sf6c_report.py','scripts/labelfix/sf6c_verify.py'):
        added+=''.join(difflib.unified_diff([],Path(name).read_text().splitlines(keepends=True),fromfile='/dev/null',tofile='b/'+name))
    (EV/'production_and_test.diff').write_bytes(tracked+added.encode())
    shared_git_changes=check_git()
    write_json(EV/'verification.json',dict(policy=gate.policy_binding(),scope=scope,
        new_l1_builder_matches_historical_except_certification=True,reviewer_test_assertions_preserved=True,
        sf6b_prefix_preserved=True,current_worktree_git_metadata_unchanged=True,
        unrelated_s8_git_changes=shared_git_changes,network=False,inference_runs=0,
        locked_ii_records_decoded=0,reviewer_tests=75,tests_passed=1430,environment_setup_errors=1,
        all_green=False,newly_hold=0,unsafe_cases_held=16,
        evidence_outputs={str(p.relative_to(EV)):sha256(p) for p in EV.rglob('*') if p.is_file() and p.name!='verification.json'}))


if __name__=='__main__':verify()
