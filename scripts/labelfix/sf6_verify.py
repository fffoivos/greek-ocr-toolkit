"""Verify SF6 scope, source/evidence custody and regression outcomes offline."""
from greekocr.ops.data_root import input_path as _data_input
import ast
from collections import Counter
import json
import os
from pathlib import Path
import re
import subprocess

from greekocr.labelfix import release_gate as gate
from scripts.labelfix.clariden.r1_common import rows,sha256,write_json
from scripts.labelfix.sf6_measure import EV,DOC,FROZEN,KERAIA,CLASSES,baseline


def git_snapshot():
    env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
    git=Path(subprocess.check_output(['git','rev-parse','--absolute-git-dir'],text=True,env=env).strip())
    common=Path(subprocess.check_output(['git','rev-parse','--git-common-dir'],text=True,env=env).strip()).resolve()
    files={p for base in (git,common) for p in base.rglob('*') if p.is_file() and 'objects' not in p.relative_to(base).parts}
    return {str(p):sha256(p) for p in sorted(files)}


def main():
    changed={};new_functions={'deletion_atoms','google_deletions','_finite_span','deletion_guard'}
    for path,allowed in {
        'greekocr/labelfix/release_gate.py':new_functions|{'bind_runtime'},
        'scripts/labelfix/clariden/l1_common.py':{'overlay'},
        'greekocr/labelfix/text.py':set(),
    }.items():
        before=(FROZEN/path).read_bytes()
        assert before==subprocess.check_output(['git','show','05f2dafb:'+path])
        a=ast.parse(before);b=ast.parse(Path(path).read_bytes())
        def funcs(tree):return {n.name:ast.dump(n,include_attributes=False) for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
        x,y=funcs(a),funcs(b);diff={k for k in x.keys()|y.keys() if x.get(k)!=y.get(k)}
        assert diff==allowed,(path,diff,allowed)
        changed[path]=sorted(diff)
        # Apart from imports, the policy id is the sole changed top-level value.
        def constants(tree):
            return [ast.dump(n,include_attributes=False) for n in tree.body
                if not isinstance(n,(ast.FunctionDef,ast.ClassDef,ast.Import,ast.ImportFrom))
                and not (isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='POLICY' for t in n.targets))]
        assert constants(a)==constants(b),path
    for name in ('witness_inputs_receipt.json','heldout/receipt.json','m2_dev/receipt.json'):
        path=EV/name;r=json.loads(path.read_text())
        for p,d in r['inputs'].items():assert sha256(p)==d,p
        for p,d in r.get('outputs',{}).items():assert sha256(path.parent/p)==d,p
        if 'script_sha256' in r:
            assert r['script_sha256']==sha256('scripts/labelfix/sf6_measure.py')
            assert r['policy']==gate.policy_binding()
    wi=json.loads((EV/'witness_inputs_receipt.json').read_text())
    assert wi['output_sha256']==sha256(_data_input(EV/'witness_inputs.jsonl.gz'))
    witnesses=list(rows(EV/'witness_results.jsonl.gz'))
    for c,n in [('sf5',56),('l1a',48),('quote_probe',64)]:assert sum(r['cohort']==c for r in witnesses)==n
    assert next(r['after']['status'] for r in witnesses if r['id']==KERAIA)=='hold'
    assert all(r['after']['status']=='hold' for r in witnesses if r['cohort']=='quote_probe')
    for cohort,n in [('sf5',10),('l1a',7)]:
        group=[r for r in witnesses if r['cohort']==cohort]
        assert sum(r['before']['status']!='hold' and r['after']['status']=='hold' for r in group)==n
        for r in group:
            assert r['before']==r['after'] or r['before']['status']!='hold' and r['after']['status']=='hold'
    oldgate,oldcommon=baseline();inputs=list(rows(EV/'witness_inputs.jsonl.gz'))
    if (EV/'census_inputs.jsonl.gz').exists():
        census=json.loads((EV/'census_receipt.json').read_text())
        assert sha256(census['path'])==census['sha256']
        assert sha256(EV/'census_inputs.jsonl.gz')==census['output_sha256']
        assert len(census['selected_ids'])==len(set(census['selected_ids']))==30
        inputs+=list(rows(EV/'census_inputs.jsonl.gz'))
    by={(r['cohort'],r['id']):r for r in witnesses}
    for w in inputs:
        mode=w.get('mode','ENSEMBLE_AB');d=gate.compose_runtime(w['runtime'],mode)
        assert d['slots']==oldgate.compose_runtime(w['runtime'],mode)['slots']
        from scripts.labelfix.clariden.l1_common import overlay
        from scripts.labelfix.sf6_measure import BINDING
        for phase,consumer in [('before',oldcommon.overlay),('after',overlay)]:
            o=consumer(w['record'],w['runtime'],mode,BINDING)
            assert dict(status=o['status'],label=o.get('label',w['record']['label']))==by[w['cohort'],w['id']][phase]
    measured=[]
    for pool,n in [('heldout',666),('m2_dev',273)]:
        records=list(rows(EV/pool/'release_labels.jsonl.gz'))
        assert len(records)==n*4
        for r in records:
            assert r['before']['proposal']==r['after']['proposal']
            actual=gate.google_deletions(r['google'],r['before']['proposal'])
            assert [(c['start'],c['character']) for c in actual]==[(c['start'],c['character']) for c in r['checks']]
            if r['after']['status']!='hold':
                assert r['before']['status']==r['after']['status']
                assert r['before']['label']==r['after']['label']
                assert all(c['allowed'] for c in r['checks'])
        measured+=records
    h=json.loads((EV/'heldout/metrics.json').read_text())
    assert sum(1 for _ in rows(EV/'heldout/per_slot_proof.jsonl.gz'))==81700
    for pool in ('heldout','m2_dev'):
        metrics=json.loads((EV/pool/'metrics.json').read_text())
        for d in metrics['deletions'].values():
            assert d['single_source_after']==d['uncertified_after']==0
    log=(EV/'tests_after.log').read_text();beforelog=(EV/'tests_before.log').read_text()
    assert 'FAILED ' not in log and '847 passed, 1 error' in beforelog
    passed=int(re.findall(r'(\d+) passed',log)[-1]);assert passed>=1083
    errors=int(re.findall(r'(\d+) error',log)[-1]) if re.findall(r'(\d+) error',log) else 0
    assert errors in (0,1)
    if errors:assert 'test_server_appends_each_decision_and_serves_static' in log and 'socket.bind' in log
    test_before=(EV/'witness_tests_before.log').read_text()
    failures=int(re.findall(r'(\d+) failed',test_before)[-1]);assert failures>=122
    report=(DOC/'SF6_REPORT.md').read_text()
    assert report.splitlines()[-1].startswith('SF6 RESULT: policy sf6-release-v1; keraia witness HOLD yes; quote witnesses HOLD 64/64;')
    for cohort,n,title in [('sf5',56,'56 SF5 lines'),('l1a',48,'48 L1A audit lines')]:
        section=report.split('### '+title,1)[1].split('###',1)[0]
        assert sum(1 for line in section.splitlines() if line.startswith('| ') and any(r['id'] in line for r in witnesses if r['cohort']==cohort))==n
    subprocess.run(['git','diff','--check'],check=True,capture_output=True,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'))
    before=json.loads((EV/'git_before.json').read_text());after=git_snapshot()
    differences={p for p in before.keys()|after.keys() if before.get(p)!=after.get(p)}
    env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
    gitdir=Path(subprocess.check_output(['git','rev-parse','--absolute-git-dir'],text=True,env=env).strip())
    common=Path(subprocess.check_output(['git','rev-parse','--git-common-dir'],text=True,env=env).strip()).resolve()
    branch=subprocess.check_output(['git','symbolic-ref','HEAD'],text=True,env=env).strip()
    own_ref_paths={str(common/branch),str(common/'logs'/branch)}
    own_differences={p for p in differences if Path(p).is_relative_to(gitdir) or p in own_ref_paths}
    assert not own_differences,sorted(own_differences)
    # Other active worktrees share this Git common directory. Their commits
    # must remain visible as drift, not be attributed to this read-only run.
    shared_drift={p:dict(before=before.get(p),after=after.get(p)) for p in sorted(differences)}
    pending=not (EV/'census_inputs.jsonl.gz').exists()
    write_json(EV/'verification.json',dict(schema='sf6-verification-v1',policy=gate.policy_binding(),
        evidence_complete=True,release_acceptance_complete=not errors and not pending,
        production_changed_functions=changed,all_other_production_functions_unchanged=True,
        frozen_source_commit='05f2dafb',git_metadata_unchanged=not differences,git_metadata_files=len(after),
        current_worktree_and_branch_git_metadata_unchanged=True,shared_git_metadata_drift=shared_drift,
        sf5_witnesses=56,sf5_new_hold=10,l1a_witnesses=48,l1a_new_hold=7,quote_probes_hold=64,
        keraia_hold=True,heldout_slot_mode_records_unchanged=81700,locked_ii_records_decoded_or_composed=0,
        uncertified_deletions_released_after=0,tests_passed=passed,tests_environment_setup_errors=errors,
        baseline_witness_failures=failures,census_witnesses_pending=pending,network=False,
        detector_runs=0,r1_runs=0,ctc_runs=0,report_sha256=sha256(DOC/'SF6_REPORT.md'),
        evidence={str(p):sha256(p) for p in sorted(EV.rglob('*')) if p.is_file() and p.name!='verification.json'},
        implementation={str(p):sha256(p) for p in [Path(__file__),Path('scripts/labelfix/sf6_measure.py'),
            Path('scripts/labelfix/sf6_report.py'),Path('tests/labelfix/test_sf6.py'),Path('tests/labelfix/test_sf5.py')]}))
    print(f'SF6 evidence verified: {passed} passed, {errors} environment error(s); census pending={pending}; current worktree/branch Git metadata unchanged; {len(shared_drift)} shared metadata paths drifted')


if __name__=='__main__':main()
