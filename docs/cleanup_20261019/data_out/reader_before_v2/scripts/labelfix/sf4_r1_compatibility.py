"""Rebind historical R1 sources only after exact saved-reading compatibility.

Does not reconstruct missing extraction coverage or relabel historical metrics
as a new score. Regenerates every saved raw/normalised reading from frozen S4
slots and saved predictions, including K1 flags/removals and serialization.
"""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path

from greekocr.labelfix import reading as R,release_gate as gate
from greekocr.labelfix.text import clusters,nfd,is_letter
from scripts.labelfix.clariden.r1_common import rows,sha256,write_json
from scripts.labelfix.owner_reading import policy


def main():
    out=Path('docs/labelfix/spellcheck/SF4_evidence');root=Path('docs/labelfix/spellcheck/clariden/R1_result_3678928')
    receipt_path=root/'score_receipt.json';original_bytes=receipt_path.read_bytes()
    original=json.loads(original_bytes)
    if 'sf4_compatibility' in original:
        prior=original['sf4_compatibility']
        assert sha256(prior['prior_receipt'])==prior['prior_receipt_sha256']
        original_bytes=Path(prior['prior_receipt']).read_bytes();original=json.loads(original_bytes)
    baseline=Path('artifacts/labelfix_sf4/before/greekocr/labelfix/release_gate.py')
    spec=importlib.util.spec_from_file_location('greekocr.labelfix._sf3_serialize',baseline)
    old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
    frozen={l['line_id']:l for l in rows('docs/labelfix/spellcheck/S4_lines.jsonl.gz')}
    inputs={str(receipt_path):sha256(receipt_path),'docs/labelfix/spellcheck/S4_lines.jsonl.gz':sha256('docs/labelfix/spellcheck/S4_lines.jsonl.gz')}
    checks={}
    for arm in 'ABCDE':
        pred={}
        for name in ('heldout','owner'):
            path=Path('artifacts/labelfix_r1/output_3678928')/arm/(name+'_predictions.jsonl')
            assert sha256(path)==original['predictions'][arm][name]['sha256']
            inputs[str(path)]=sha256(path)
            pred.update({(p['line_id'],p['start']):p for p in rows(path)})
        for pn in ('raw','filtered'):
            path=root/f'{arm}_{pn}_readings.jsonl.gz';inputs[str(path)]=sha256(path)
            saved=list(rows(path));count=0
            for record in saved:
                line=frozen[record['line_id']];slots=deepcopy(line['recogniser_slots'])
                for s in slots:
                    p=pred.get((line['line_id'],s['start']))
                    s.update(mark_support_source='reader',reader_evidence=p.get('evidence',{}) if p else {},
                        detector_evidence=s.get('evidence',{}),evidence=p.get('evidence',{}) if p else {},
                        parts=p['cls'].split('+') if p and p['cls']!='none' else [],naming={},
                        mark_probabilities=p.get('mark_probabilities',{}) if p else {})
                by={s['start']:s for s in slots}
                text=''.join(c.base+''.join(R.MARKS[p] for p in by.get(c.start,{}).get('parts',[]) if p in R.MARKS)
                             for c in clusters(nfd(line['recogniser_text'])))
                assert all(c.base.isalpha()==is_letter(c.base) for c in clusters(nfd(text)))
                rd,_=R.apply_constraints(R.LineReading(text,slots,[]),output='normalised' if pn=='filtered' else 'print')
                current=dict(line_id=line['line_id'],reading=rd.text,removed_by_constraint=rd.removed_by_constraint,constraint_flags=rd.constraint_flags)
                if json.loads(json.dumps(current))!=record:
                    write_json(out/'r1_compatibility_mismatch.json',dict(arm=arm,policy=pn,current=current,saved=record))
                    raise ValueError((arm,pn,line['line_id']))
                assert gate.serialize(rd)==old.serialize(rd)
                count+=1
            checks[arm+'_'+pn]=count
    before=out/'r1_score_receipt_before.json';before.write_bytes(original_bytes)
    inputs.pop(str(receipt_path));inputs[str(before)]=sha256(before)
    compatibility=out/'r1_compatibility.json'
    proof=dict(schema='sf4-r1-reading-compatibility-v1',complete=True,readings=checks,exact_readings_flags_removals=True,
        exact_serialization=True,metrics_rescored=False,extraction_coverage_synthesized=False,
        metrics_sha256=sha256(root/'metrics.json'),result_sha256=sha256(root/'RESULT.md'),
        inputs=inputs,scorer_sha256={p:sha256(p) for p in original['scorer_sha256']},script_sha256=sha256(Path(__file__)))
    write_json(compatibility,proof)
    updated=deepcopy(original)
    updated['historical_scorer_sha256']=original['scorer_sha256']
    updated['historical_constraint_policy']=original['constraint_policy']
    updated['scorer_sha256']=proof['scorer_sha256']
    updated['constraint_policy']={pn:policy('normalised' if pn=='filtered' else 'print') for pn in ('raw','filtered')}
    updated['sf4_compatibility']=dict(path=str(compatibility),sha256=sha256(compatibility),
        prior_receipt=str(before),prior_receipt_sha256=sha256(before),scope='exact saved R1 readings and K1 receipts, not full metric rescoring')
    write_json(receipt_path,updated)
    print(json.dumps(checks))


if __name__=='__main__':main()
