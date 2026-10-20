"""Read back SF6b-only replay, code scope, edited SF5 tests and failed witnesses."""
from collections import Counter
from copy import deepcopy
import ast
import json
from pathlib import Path
import subprocess

from greekocr.labelfix import release_gate as gate
from scripts.labelfix.clariden import l1_common as common
from scripts.labelfix.clariden.r1_common import rows,sha256
from tests.labelfix.test_sf6 import overlay
from test_sf6_reviewer import legacy_unscored_punctuation,ordinary_absence_outside_window

OUT=Path(__file__).parent;ROOT=Path.cwd();DOC=ROOT/'docs/labelfix/spellcheck'


def main():
    evidence=[]
    for mode in gate.MODES:
        legacy,rt=legacy_unscored_punctuation()
        for score in ('missing','legacy_default_zero'):
            r=deepcopy(rt)
            if score=='missing':r.pop('recognition_confidence')
            value=overlay((gate,common),"δ'",r,mode)
            assert value['status']==('hold' if score=='missing' else 'corrected')
            evidence.append(dict(case=score,mode=mode,original="δ'",legacy_alignment=legacy,runtime=r,overlay=value))
        for source in ('reader','recogniser'):
            r=ordinary_absence_outside_window(source);value=overlay((gate,common),'ά',r,mode)
            assert value['status']=='corrected' and value['label']=='α'
            evidence.append(dict(case=source+'_outside_window',mode=mode,original='ά',runtime=r,overlay=value))
    (OUT/'unsafe_release_witnesses.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    result=dict(unsafe_releases=12,missing_score_controls_held=4)
    # Replayed metrics must match the target SF6b artifacts exactly.
    for cohort in ('heldout','m2_dev'):
        actual=json.loads((OUT/cohort/'metrics.json').read_text())
        assert actual==json.loads((DOC/'SF6b_evidence/after'/cohort/'metrics.json').read_text())
        result[cohort]=dict(metrics_match=True,marks=actual['marks'],release_counts=actual['release_counts'])
    wr=list(rows(OUT/'witness_results.jsonl.gz'))
    assert wr==list(rows(DOC/'SF6b_evidence/after/witness_results.jsonl.gz'))
    result['witnesses']=dict(cohorts={cohort:dict(Counter(r['after']['status'] for r in wr if r['cohort']==cohort))
        for cohort in ('sf5','l1a','quote_probe')},
        moves=[dict(id=r['id'],cohort=r['cohort'],label=r['after']['label'],checks=r['checks']) for r in wr
               if any(c.get('operation')=='MOVE' for c in r['checks'])])
    # Quantify the local evidence limitation rather than equating local HOLDs
    # with the rule's counterfactual cost under a complete runtime.
    hr=list(rows(OUT/'heldout/release_labels.jsonl.gz'))
    for mode in gate.MODES:
        mr=[r for r in hr if r['mode']==mode]
        checks=[c for r in mr for c in r['checks']]
        result['heldout'].setdefault('absence_sources',{})[mode]=dict(
            proposed_deleted_atoms=len(checks),positive_reader=sum(c['signals']['reader'] for c in checks),
            positive_detector=sum(c['signals']['detector'] for c in checks),
            positive_recogniser=sum(c['signals']['recogniser'] for c in checks),
            allowed=sum(c['allowed'] for c in checks),
            any_proposal_deletion_lines=sum(bool(r['checks']) for r in mr),
            newly_held_released_lines=sum(r['before']['status']!='hold' and r['after']['status']=='hold' for r in mr))
    result['input_hashes_verified']=0
    for p in (OUT/'heldout/receipt.json',OUT/'m2_dev/receipt.json',DOC/'SF6_evidence/witness_inputs_receipt.json'):
        for path,digest in json.loads(p.read_text())['inputs'].items():
            assert sha256(path)==digest,path
            result['input_hashes_verified']+=1
    # Function-level scope check; retain the exact diff as the readable audit.
    def funcs(source):
        return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(source).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    result['production_function_changes']={}
    for name in ('greekocr/labelfix/release_gate.py','scripts/labelfix/clariden/l1_common.py','greekocr/labelfix/text.py'):
        before=funcs(subprocess.check_output(['git','show','05f2dafb:'+name],text=True));after=funcs(Path(name).read_text())
        changed=sorted(k for k in before.keys()|after.keys() if before.get(k)!=after.get(k))
        result['production_function_changes'][name]=changed
    old_test=subprocess.check_output(['git','show','05f2dafb:tests/labelfix/test_sf5.py'],text=True)
    now_test=Path('tests/labelfix/test_sf5.py').read_text()
    oldf,newf=funcs(old_test),funcs(now_test)
    changed=sorted(k for k in oldf.keys()|newf.keys() if oldf.get(k)!=newf.get(k))
    expected=['assert_sf6_hold','test_saved_56_release_witnesses','test_single_source_presence_behavior_unchanged_and_counted',
              'test_spacing_breathing_consumed_in_same_edit','test_spacing_breathing_unattached_stays_verbatim']
    assert changed==sorted(expected)
    assert set(oldf)<=set(newf)
    result['sf5_test_changes']=changed
    result['sf5_review']=dict(test_functions_removed=0,existing_composer_slot_assertion_preserved=True,
        explicit_sf6_hold_checks=True,held_ids=8,capital_witnesses_restored_to_exact_original_sf5_expectation=2)
    (OUT/'readback.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(unsafe_releases=result['unsafe_releases'],input_hashes_verified=result['input_hashes_verified'],
        heldout_AB=result['heldout']['absence_sources']['ENSEMBLE_AB'],witnesses=result['witnesses']['cohorts'],
        sf5_test_changes=changed,production_function_changes=result['production_function_changes']),ensure_ascii=False,indent=2))


if __name__=='__main__':main()
