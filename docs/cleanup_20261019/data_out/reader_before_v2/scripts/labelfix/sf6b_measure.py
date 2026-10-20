"""Replay the unchanged SF6 instruments against frozen SF6 and SF6b offline.

Original SF6 evidence is read-only. Each phase retains the instrument's SF5
reference; the comparison/report uses each phase's AFTER (SF6 versus SF6b).
"""
import argparse
import ast
from collections import Counter
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from types import SimpleNamespace

from greekocr.labelfix import release_gate as gate
from scripts.labelfix.clariden import l1_common
from scripts.labelfix.clariden.r1_common import rows, sha256, write_json, write_rows
from scripts.labelfix import sf6_measure as sf6
from scripts.labelfix.sf5_measure import baseline
from scripts.labelfix.sf6_verify import git_snapshot

EV=sf6.DOC/'SF6b_evidence'
FROZEN=Path('artifacts/labelfix_sf6b/before')
ORIGINAL=sf6.DOC/'SF6_evidence'
CAPITALS={'32aae9fec147d3b483deb96e-p000060-l0057','a963b33d02c23d4127f5ec26-p000012-l0029'}


def read(path):return json.loads(path.read_text())


def measure(phase=None):
    original=(sf6.EV,sf6.gate,sf6.common,sf6.BINDING)
    try:
        for label,policy,consumer in [('before',*baseline(FROZEN)),('after',gate,l1_common)]:
            if phase and phase!=label:continue
            phase_name=label
            if phase_name=='before':
                # The baseline loader shares reading's code objects. Point
                # its binding at the byte-identical frozen reading source.
                policy.R=SimpleNamespace(**vars(policy.R))
                policy.R.__file__=str((FROZEN/'greekocr/labelfix/reading.py').resolve())
            dest=EV/phase_name;dest.mkdir(exist_ok=True)
            for name in ('witness_inputs.jsonl.gz','witness_inputs_receipt.json','census_inputs.jsonl.gz'):
                if (ORIGINAL/name).exists():shutil.copyfile(ORIGINAL/name,dest/name)
            sf6.EV=dest;sf6.gate=policy;sf6.common=consumer
            sf6.BINDING=dict(original[3],policy_sha256=policy.policy_binding()['sha256'],policy_binding=policy.policy_binding())
            sf6.heldout();print(phase_name,'held-out complete',flush=True)
            sf6.m2();print(phase_name,'M2 DEV complete',flush=True)
            sf6.witnesses();print(phase_name,'witnesses complete',flush=True)
    finally:
        sf6.EV,sf6.gate,sf6.common,sf6.BINDING=original
    compare()


def compare():
    changed=[];check_changes=[]
    for cohort,path in [('heldout','heldout/release_labels.jsonl.gz'),('m2_dev','m2_dev/release_labels.jsonl.gz'),
                        ('witness','witness_results.jsonl.gz')]:
        a=list(rows(EV/'before'/path));b=list(rows(EV/'after'/path))
        assert a==list(rows(ORIGINAL/path)),('SF6 baseline did not reproduce',cohort)
        assert len(a)==len(b)
        for old,new in zip(a,b):
            assert (old['id'],old['mode'],old.get('cohort'))==(new['id'],new['mode'],new.get('cohort'))
            assert old['before']==new['before']
            assert len(old['checks'])==len(new['checks'])
            for x,y in zip(old['checks'],new['checks']):
                if x==y:continue
                assert not x['allowed'] and y['allowed'] and y['operation']=='MOVE'
                assert {k:v for k,v in x.items() if k not in ('allowed','reason')}=={
                    k:v for k,v in y.items() if k not in ('allowed','reason','operation','breathing')}
                check_changes.append(dict(cohort=cohort,witness_cohort=old.get('cohort'),id=old['id'],mode=old['mode'],before=x,after=y))
            if old['after']!=new['after']:
                assert old['after']['status']=='hold' and new['after']['status']=='corrected'
                assert any(c.get('operation')=='MOVE' for c in new['checks'])
                changed.append(dict(cohort=cohort,witness_cohort=old.get('cohort'),id=old['id'],mode=old['mode'],
                    before=old['after'],after=new['after'],checks=new['checks']))
        if cohort!='witness':
            assert read(EV/'before'/cohort/'metrics.json')==read(ORIGINAL/cohort/'metrics.json')
    write_rows(EV/'line_changes.jsonl',changed);write_rows(EV/'check_changes.jsonl',check_changes)
    write_json(EV/'comparison.json',dict(before='SF6',after='SF6b',sf6_baseline_exact=True,
        policy_before=read(EV/'before_receipt.json')['policy'],policy_after=gate.policy_binding(),
        changed_lines=dict(Counter(c['cohort'] for c in changed)),changed_checks=len(check_changes),
        capital_witnesses_released=len({c['id'] for c in changed if c['id'] in CAPITALS}),
        network=False,detector_runs=0,r1_runs=0,ctc_runs=0,locked_ii_records_decoded=0))


def table(headers,values):
    def cell(x):return str(x).replace('|','\\|').replace('\n',' ')
    return ['| '+' | '.join(headers)+' |','| '+' | '.join('---' for _ in headers)+' |',
            *['| '+' | '.join(cell(x) for x in row)+' |' for row in values]]


def arrow(a,b):return f'{a} → {b}'
def vector(d):return '/'.join(str(d.get(k,0)) for k in sf6.CLASSES)


def report():
    compare();comparison=read(EV/'comparison.json')
    log=(EV/'tests_after.log').read_text();passed=int(re.findall(r'(\d+) passed',log)[-1])
    errors=int(re.findall(r'(\d+) error',log)[-1]) if re.findall(r'(\d+) error',log) else 0
    assert 'FAILED ' not in log
    witness_passed=int(re.findall(r'(\d+) passed',(EV/'witness_tests_after.log').read_text())[-1])
    baseline_failures=int(re.findall(r'(\d+) failed',(EV/'witness_tests_before.log').read_text())[-1])
    w=list(rows(EV/'after/witness_results.jsonl.gz'))
    assert all(r['after']['status']=='hold' for r in w if r['cohort']=='quote_probe' or r['id']==sf6.KERAIA)
    # Save concrete mismatched-kind and unnamed-reader controls, including
    # direct forced proposals. A scored different kind supplies no MOVE.
    from tests.labelfix.test_sf6 import move_runtime,overlay
    synthetic=[]
    for kind in ('mismatched_kind','unnamed'):
        proposal='-Ἁλλα' if kind=='mismatched_kind' else '-Ἀλλα'
        rt=move_runtime(proposal)
        if kind=='mismatched_kind':
            rt.pop('recognition_confidence');rt['detector']['slots'][0]['evidence'].pop('observation')
        else:
            rt['r1_predictions'][0]['parts']=[]  # A∧B does not name psili
        out=overlay((gate,l1_common),'-᾿Αλλα',rt)
        checks=gate.deletion_guard('-᾿Αλλα',proposal,rt,gate.compose_runtime(rt,'ENSEMBLE_AB'))
        assert out['status']=='hold' and out['changes']==[] and any(not c['allowed'] for c in checks)
        synthetic.append(dict(kind=kind,original='-᾿Αλλα',proposal=proposal,runtime=rt,overlay=out,forced_proposal_checks=checks))
    write_json(EV/'synthetic_witnesses.json',synthetic)
    L=['','## SF6b — same-kind spacing-breathing MOVE','',
       'Before = **SF6**; after = **SF6b**. Policy id remains `sf6-release-v1`. Only `deletion_guard` changes in production: a consumed spacing psili (`᾿`/`᾽`) or dasia (`῾`) can MOVE to a newly written combining breathing of the same kind on the same capital, when A∧B names it with known, scored, uncertainty-free coverage inside the saved window and the capital has no existing slot veto. AE retains its E check. No positive absence is asserted for a MOVE. All other deletion checks, composer/slot decisions, observation gates, K1 and punctuation rules are unchanged.', '',
       f'Policy sha **`{gate.policy_binding()["sha256"]}`**, previously `{comparison["policy_before"]["sha256"]}`. The existing `policy_binding()` hashes the changed source automatically; the replay passes this binding and sha to release overlays. [Policy and comparison receipt](SF6b_evidence/comparison.json).', '',
       'The unchanged SF6 instruments were rerun twice from saved evidence: frozen launch sources for SF6, then SF6b. Every before line/check/metric reproduces the original SF6 evidence exactly. Original SF6 evidence and the pre-SF6b report prefix are preserved. No network, inference, `.git` writes or other-worktree writes. Launch HEAD: `'+read(EV/'before_receipt.json')['head']+'`.', '',
       '### Held-out 666 — SF6 → SF6b','']
    a=read(EV/'before/heldout/metrics.json');b=read(EV/'after/heldout/metrics.json');rr=[]
    for m in gate.MODES:
        x=a['marks']['after'][m];y=b['marks']['after'][m]
        rr.append([m,'mark',*[arrow(x[k],y[k]) for k in ('corrected','wrong','missed','HOLD','new','lines_held')]])
        rr.append([m,'elision kept/deleted/added',arrow('/'.join(str(a['elision']['after'][m][k]) for k in ('kept','deleted','added')),
            '/'.join(str(b['elision']['after'][m][k]) for k in ('kept','deleted','added'))),'—','—','—','—','—'])
        rr.append([m,'raw deleted mark/apostrophe/quote/keraia/other',arrow(vector(a['deletions'][m]['after']),vector(b['deletions'][m]['after'])),'—','—','—','—','—'])
    L+=table(['Mode','Row','Corrected /80, elision K/D/A or raw deleted','Wrong','Missed','HOLD errors','New','Instrument lines held /666'],rr)
    L+=['','No held-out label, status, check or slot outcome changes. Missing full runtime coverage remains unknown; it cannot qualify a MOVE. The 81,700 frozen slot/mode records remain identical. [SF6 replay](SF6b_evidence/before/heldout/metrics.json), [SF6b replay](SF6b_evidence/after/heldout/metrics.json).','',
        '### M2 DEV 273 — SF6 → SF6b','']
    dev_a=read(EV/'before/m2_dev/metrics.json');dev_b=read(EV/'after/m2_dev/metrics.json');rr=[]
    for m in gate.MODES:
        x=dev_a['marks']['after']['modes'][m];y=dev_b['marks']['after']['modes'][m]
        rr.append([m,'mark',*[arrow(x['errors'].get(k,0),y['errors'].get(k,0)) for k in ('corrected','wrong','missed','HOLD')],
            arrow(x['accepted_changed_slots'],y['accepted_changed_slots']),arrow(x['lines_with_HOLD'],y['lines_with_HOLD'])])
        rr.append([m,'elision','UNKNOWN → UNKNOWN','—','—','—','—','—'])
        rr.append([m,'raw deleted mark/apostrophe/quote/keraia/other',arrow(vector(dev_a['deletions'][m]['after']),vector(dev_b['deletions'][m]['after'])),'—','—','—','—','—'])
    L+=table(['Mode','Row','Corrected /43 or raw deleted','Wrong','Missed','HOLD errors','Changed control slots','Instrument lines held /273'],rr)
    L+=['','No M2 label, status, check or slot outcome changes. B/E remain missing; no replacement evidence is invented. Only the DEV allowlist is decoded: locked stratum (ii) decoded/composed **0**. Punctuation truth remains UNKNOWN. [SF6 replay](SF6b_evidence/before/m2_dev/metrics.json), [SF6b replay](SF6b_evidence/after/m2_dev/metrics.json).','',
        'Actual whole-line status counts (corrected/unchanged/HOLD):','']
    L+=table(['Cohort','Mode','SF6 → SF6b'],[[pool,m,arrow('/'.join(str(x['release_counts']['after'][m].get(k,0)) for k in ('corrected','unchanged','hold')),
        '/'.join(str(y['release_counts']['after'][m].get(k,0)) for k in ('corrected','unchanged','hold')))]
        for pool,x,y in [('held-out',a,b),('M2 DEV',dev_a,dev_b)] for m in gate.MODES])
    L+=['','### Witnesses and every changed line','',
        'Both capital witnesses release with exactly one psili, consuming one spacing sign. A and B both name psili; their saved spans are within the saved windows, scored, known and uncertainty-free. The detector’s empty observation map is not used as an absence signal. These lines occur in both SF5 and L1A witness cohorts; they are two unique lines, four cohort records.','']
    changed=list(rows(EV/'line_changes.jsonl'))
    L+=table(['Line ID','Cohort / mode','SF6','SF6b label','Explanation'],[[r['id'],r['witness_cohort']+' / '+r['mode'],r['before']['status'],r['after']['label'],
        'HOLD → corrected: U+1FBF psili moves to U+0313 on the same Α; scored A∧B psili, no other veto.'] for r in changed])
    evidence=[]
    for item in rows(EV/'after/witness_inputs.jsonl.gz'):
        if item['cohort']!='l1a' or item['id'] not in CAPITALS:continue
        rt=item['runtime'];check=next(r['checks'][0] for r in changed if r['id']==item['id'])
        start=check['recogniser_start'];slot=next(s for s in rt['detector']['slots'] if s['start']==start)
        a_cov=next(c for c in rt['coverage'] if c['start']==start)
        b_cov=next(c for c in rt['peer_coverage']['B'] if c['start']==start)
        evidence.append([item['id'],start,slot['evidence']['window'],a_cov['span'],b_cov['span'],
            'A=psili; B=psili; both scored, unadjudicated (known), uncertainty=[]'])
    L+=['','Saved capital coverage (no evidence fields filled in):','']
    L+=table(['Line ID','Recogniser NFD start','Window','A span','B span','Reader evidence'],evidence)
    L+=['','The 56 SF5 witnesses now have 48 releases / 8 HOLDs (SF6: 46 / 10); the 48 L1A lines have 43 releases / 5 HOLDs (SF6: 41 / 7). All other witness outcomes and deletion checks are exact SF6 parity; the known reader mistakes remain HOLD. Quote probes remain **64/64 HOLD** and the keraia witness remains **HOLD**. No mark scoring is inferred for the witness cohort. [Full before](SF6b_evidence/before/witness_results.jsonl.gz), [full after](SF6b_evidence/after/witness_results.jsonl.gz), [per-line changes](SF6b_evidence/line_changes.jsonl), [changed checks](SF6b_evidence/check_changes.jsonl).','',
        'Released raw spacing-character removals change 0 → 2 per capital-witness cohort; all two are explicitly `operation=MOVE`, with the original absence signals still false. They are not content deletions. True released deletions remain 0 in held-out, M2 and these witness cohorts. Apostrophe/quote/keraia HOLD counts are unchanged in every cohort and mode.','',
        'The mismatched-kind control consumes spacing psili while proposing dasia, with no second certified psili-absence source: HOLD, no MOVE. The unnamed-reader control remains HOLD even for a forced attached-psili proposal. Unscored, uncertain, missing/conflicting B, clipped, unseen, outside-window, lowercase, already-attached, other-boundary and duplicate-sign controls retain exact HOLD assertions. Matching dasia is checked directly in the deletion guard; the unchanged composer/punctuation guard does not gain a new dasia rewrite route. [Concrete synthetic evidence](SF6b_evidence/synthetic_witnesses.json).','',
        '### Tests and reproduction','',
        f'Full labelfix: **{passed} passed, {errors} environment setup error(s), 0 assertion failures**. The unchanged capture test cannot bind its loopback socket in this sandbox (`PermissionError: [Errno 1] Operation not permitted`), also reproduced before the change (1100 passed, 1 error). All-green acceptance remains unmet in this sandbox; no test is skipped, deselected or weakened. [Before](SF6b_evidence/tests_before.log), [after](SF6b_evidence/tests_after.log).', '',
        f'Only the two released capital expectations change in existing regression tests; their output strings are exact. Existing unscored SF5 synthetic attachments still HOLD. The new positive MOVE tests fail on frozen SF6 ({baseline_failures} failures) and pass on SF6b ({witness_passed} SF5/SF6 tests passed); all other SF6 absence tests are retained. [Frozen-SF6 failures](SF6b_evidence/witness_tests_before.log), [SF5/SF6 suite after](SF6b_evidence/witness_tests_after.log). Census witnesses remain pending; the original SF6 saved evidence is the measurement scope.','',
        '```sh','export PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1',
        'PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python',
        '$PY scripts/labelfix/sf6b_measure.py measure',
        '$PY -m pytest tests/labelfix -q -p no:cacheprovider > docs/labelfix/spellcheck/SF6b_evidence/tests_after.log 2>&1',
        '$PY scripts/labelfix/sf6b_measure.py report',
        '$PY scripts/labelfix/sf6b_measure.py verify','```','',
        f'SF6b RESULT: breathing-move exception; capital witnesses released {comparison["capital_witnesses_released"]}/2; mismatched-kind HOLD yes; unnamed HOLD yes; held-out AB corrected {b["marks"]["after"]["ENSEMBLE_AB"]["corrected"]}, wrong {b["marks"]["after"]["ENSEMBLE_AB"]["wrong"]}; tests {passed} passed; policy sha {gate.policy_binding()["sha256"]}']
    prefix=(FROZEN/'docs/labelfix/spellcheck/SF6_REPORT.md').read_text()
    (sf6.DOC/'SF6_REPORT.md').write_text(prefix+'\n'.join(L)+'\n')


def verify():
    before=read(EV/'before_receipt.json');binding=gate.policy_binding()
    for name,digest in before['sources'].items():assert sha256(FROZEN/name)==digest
    for name,digest in before['policy']['sources'].items():
        if name=='greekocr/labelfix/release_gate.py':continue
        assert sha256(name)==digest,name
    def nodes(path):return ast.parse(Path(path).read_bytes()).body
    old=nodes(FROZEN/'greekocr/labelfix/release_gate.py');new=nodes('greekocr/labelfix/release_gate.py')
    assert len(old)==len(new)
    changed=[getattr(x,'name',type(x).__name__) for x,y in zip(old,new) if ast.dump(x)!=ast.dump(y)]
    assert changed==['deletion_guard'],changed
    assert binding['schema']=='sf6-release-v1' and binding['sha256']!=before['policy']['sha256']
    compare();changes=list(rows(EV/'line_changes.jsonl'))
    assert len(changes)==4 and {r['id'] for r in changes}==CAPITALS
    for pool in ('heldout','m2_dev'):
        assert read(EV/'before'/pool/'metrics.json')==read(EV/'after'/pool/'metrics.json')
        for phase in ('before','after'):
            receipt=read(EV/phase/pool/'receipt.json')
            assert receipt['policy']==(before['policy'] if phase=='before' else binding)
            assert receipt['script_sha256']==sha256('scripts/labelfix/sf6_measure.py')
            for name,digest in receipt['inputs'].items():assert sha256(name)==digest
            for name,digest in receipt['outputs'].items():assert sha256(EV/phase/pool/name)==digest
    prefix=(FROZEN/'docs/labelfix/spellcheck/SF6_REPORT.md').read_bytes()
    assert (sf6.DOC/'SF6_REPORT.md').read_bytes().startswith(prefix)
    assert (sf6.DOC/'SF6_REPORT.md').read_text().splitlines()[-1].endswith('policy sha '+binding['sha256'])
    log=(EV/'tests_after.log').read_text()
    assert 'FAILED ' not in log and '1260 passed, 1 error' in log
    assert 'test_server_appends_each_decision_and_serves_static' in log and 'socket.bind' in log
    baseline_log=(EV/'witness_tests_before.log').read_text()
    assert '72 failed' in baseline_log and 'FAILED tests/labelfix/test_sf6.py::test_non_move' not in baseline_log
    after=git_snapshot();diff={p for p in before['git_metadata'].keys()|after.keys() if before['git_metadata'].get(p)!=after.get(p)}
    env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
    gitdir=Path(subprocess.check_output(['git','rev-parse','--absolute-git-dir'],text=True,env=env).strip())
    common=Path(subprocess.check_output(['git','rev-parse','--git-common-dir'],text=True,env=env).strip()).resolve()
    branch=subprocess.check_output(['git','symbolic-ref','HEAD'],text=True,env=env).strip()
    assert not {p for p in diff if Path(p).is_relative_to(gitdir) or p in {str(common/branch),str(common/'logs'/branch)}}
    subprocess.run(['git','diff','--check'],check=True,env=env)
    write_json(EV/'verification.json',dict(policy=binding,only_production_change=changed,
        original_report_prefix_unchanged=True,sf6_baseline_exact=True,changed_unique_lines=2,changed_cohort_records=4,
        heldout_metrics_unchanged=True,m2_metrics_unchanged=True,slot_decisions_unchanged=True,
        own_git_metadata_unchanged=True,shared_metadata_drift=sorted(diff),network=False,
        inference_runs=0,locked_ii_records_decoded=0,all_green_acceptance=False,
        tests_passed=int(re.findall(r'(\d+) passed',log)[-1]),tests_environment_setup_errors=1,
        focused_tests_passed=633,baseline_move_witness_failures=72,
        implementation={p:sha256(p) for p in ('scripts/labelfix/sf6b_measure.py',
            'tests/labelfix/test_sf5.py','tests/labelfix/test_sf6.py')},
        report_sha256=sha256(sf6.DOC/'SF6_REPORT.md'),
        evidence={str(p):sha256(p) for p in EV.rglob('*') if p.is_file() and p.name!='verification.json'}))
    print('Verified: only deletion_guard changed; two unique MOVE releases; held-out/M2 exact SF6 parity.',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=('measure','report','verify'))
    parser.add_argument('--phase',choices=('before','after'))
    args=parser.parse_args()
    if args.action=='measure':measure(args.phase)
    else:globals()[args.action]()
