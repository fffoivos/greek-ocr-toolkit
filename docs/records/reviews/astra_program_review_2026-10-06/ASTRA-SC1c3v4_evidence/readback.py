"""Read-only verification of SF6c source scope, test custody and fresh replays."""
import ast
from collections import Counter
import difflib
import hashlib
import json
from pathlib import Path
import subprocess

from greekocr.labelfix import release_gate as gate
from scripts.labelfix.clariden.r1_common import rows

ROOT=Path.cwd();EV=Path(__file__).parent
DOC=ROOT/'docs/labelfix/spellcheck'
REFERENCE=DOC/'SF6c_evidence'
FROZEN=ROOT/'artifacts/labelfix_sf6c/before'
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()


def funcs(source):
    return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(source).body
            if isinstance(n,(ast.FunctionDef,ast.ClassDef))}


def main():
    result=dict(policy=gate.policy_binding(),production_changes={})
    expected={
        'greekocr/labelfix/release_gate.py':{'policy_binding','_source_in_window','_recogniser_scored','deletion_guard','bind_runtime'},
        'greekocr/labelfix/ctc_align.py':{'recognition_fields','Alignment','Recognizer'},
        'scripts/labelfix/m2_run.py':{'infer_line','replay_detector'},
        'scripts/labelfix/clariden/l1_infer.py':{'run'},
        'scripts/labelfix/clariden/l1e_run.py':{'infer'},
        'scripts/labelfix/clariden/l1e_measure.py':{'saved_runtime'},
        'scripts/labelfix/clariden/r1_extract.py':{'extract_line'},
        'tests/labelfix/test_sf6.py':{'rich'},
    }
    for name,allowed in expected.items():
        before=subprocess.check_output(['git','show','8c5ad361:'+name],text=True)
        assert (FROZEN/name).read_text()==before,name
        a,b=funcs(before),funcs((ROOT/name).read_text())
        changed={k for k in a.keys()|b.keys() if a.get(k)!=b.get(k)}
        assert changed==allowed,(name,changed)
        result['production_changes'][name]=sorted(changed)
    unchanged=['greekocr/labelfix/text.py','greekocr/labelfix/reading.py','greekocr/labelfix/segmentation.py',
               'scripts/labelfix/clariden/l1_common.py','scripts/labelfix/clariden/r1_common.py','tests/labelfix/test_sf5.py']
    for name in unchanged:
        assert (ROOT/name).read_bytes()==subprocess.check_output(['git','show','8c5ad361:'+name]),name
    result['unchanged_sources']=unchanged

    # Compare the exact original scratch tests, rather than trusting a new copy.
    original=EV.parent.parent/'ASTRA-SC1c3v3/ASTRA-SC1c3v3_evidence/test_sf6_reviewer.py'
    imported=ROOT/'tests/labelfix/test_sf6_reviewer.py'
    old,new=original.read_text(),imported.read_text()
    assert ast.dump(ast.parse(old.replace('alignment.confidence==0.','alignment.confidence is None')),include_attributes=False)==ast.dump(ast.parse(new),include_attributes=False)
    (EV/'reviewer_test_import.diff').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=str(original),tofile=str(imported))))
    result['reviewer_test_custody']=dict(original_sha256=sha(original),imported_sha256=sha(imported),only_executable_change='loader default assertion 0.0 to None',release_assertions_identical=True)

    snapshot=ROOT/'artifacts/labelfix_l1e/reference/l1_detect.py'
    builder=ROOT/'scripts/labelfix/clariden/l1_detect.py'
    added=('            recognition_confidence=al.confidence,image_width=image.width,\n'
           '            recognition_evidence=al.recognition_evidence(raw.slots,image.width),\n')
    assert builder.read_text().count(added)==1
    assert builder.read_text().replace(added,'')==snapshot.read_text()
    result['historical_builder']=dict(snapshot_sha256=sha(snapshot),current_sha256=sha(builder),only_three_fields_added=True)

    comparisons={}
    inputs=set()
    for phase in ('before','after'):
        for cohort in ('heldout','m2_dev'):
            root=EV/'replay'/phase/cohort;ref=REFERENCE/phase/cohort
            for name in ('metrics.json',):
                assert json.loads((root/name).read_text())==json.loads((ref/name).read_text()),(phase,cohort,name)
            for name in ('release_labels.jsonl.gz','per_slot_proof.jsonl.gz'):
                assert list(rows(root/name))==list(rows(ref/name)),(phase,cohort,name)
            receipt=json.loads((root/'receipt.json').read_text())
            for name,digest in receipt['inputs'].items():
                assert sha(name)==digest,name
                inputs.add((name,digest))
        assert list(rows(EV/'replay'/phase/'witness_results.jsonl.gz'))==list(rows(REFERENCE/phase/'witness_results.jsonl.gz'))
    for name in ('comparison.json','unsafe_witnesses_after.json'):
        assert json.loads((EV/'replay'/name).read_text())==json.loads((REFERENCE/name).read_text()),name
    for name in ('line_changes.jsonl','check_changes.jsonl'):
        assert list(rows(EV/'replay'/name))==list(rows(REFERENCE/name)),name
    result['replay']=json.loads((EV/'replay/comparison.json').read_text())
    checks=list(rows(EV/'replay/check_changes.jsonl'))
    result['replay']['changed_check_unique_lines']=len({r['id'] for r in checks})
    result['replay']['saved_unsafe_cases_held']=len(json.loads((EV/'replay/unsafe_witnesses_after.json').read_text())['cases'])
    result['input_hashes_verified']=len(inputs)
    for cohort in ('heldout','m2_dev'):
        before=json.loads((EV/'replay/before'/cohort/'metrics.json').read_text())
        after=json.loads((EV/'replay/after'/cohort/'metrics.json').read_text())
        assert before==after
        result.setdefault('outcomes',{})[cohort]=dict(marks=after['marks']['after'],releases=after['release_counts']['after'])
    witnesses=list(rows(EV/'replay/after/witness_results.jsonl.gz'))
    result['outcomes']['witnesses']={c:dict(Counter(r['after']['status'] for r in witnesses if r['cohort']==c)) for c in ('sf5','l1a','quote_probe')}

    audit=json.loads((EV/'runtime_audit.json').read_text())
    reference_audit=json.loads((REFERENCE/'runtime_audit.json').read_text())
    # Archive enumeration follows unsorted rg output; compare complete rows by
    # path. The first comparison differed only in that enumeration order.
    def ordered(value):
        return dict(value,archive_sources=sorted(value['archive_sources'],key=lambda r:r['path']))
    assert ordered(audit)==ordered(reference_audit)
    for row in audit['runtime_sources']+audit['alignment_sources']+audit['archive_sources']:
        assert sha(row['path'])==row['sha256'],row['path']
    assert all(not r['newly_hold'] for r in audit['runtime_sources'])
    assert all(not r['newly_hold'] for ar in audit['archive_sources'] for r in ar['runtime_members'])
    result['runtime_audit_exact_by_path']=True
    result['score_distributions']=dict(heldout=audit['heldout_alignment_distribution'],
        m2=next(r for r in audit['runtime_sources'] if r['path']=='.cache/labelfix/m2/runtime.jsonl'),
        c1=next(r for r in audit['alignment_sources'] if 'C1_alignments' in r['path']))
    (EV/'readback.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(policy=result['policy']['sha256'],test_assertions_preserved=True,historical_builder_only_three_fields=True,
        newly_hold=result['replay']['newly_hold'],changed_checks=len(checks),changed_check_unique_lines=result['replay']['changed_check_unique_lines'],
        saved_unsafe_cases_held=result['replay']['saved_unsafe_cases_held'],input_hashes_verified=len(inputs),runtime_audit_exact_by_path=True),indent=2))


if __name__=='__main__':main()
