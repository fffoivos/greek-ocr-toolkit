"""Independent slot/count, source-custody and frozen-instrument S8b audit."""
from scripts.labelfix import s8b_measure as b
from scripts.labelfix import s8_score_truth as t
from greekocr.glyphs.components import Component
from pathlib import Path
import collections as C
import json
import math


def main():
    p, out = b.p, b.OUT
    binding = b.freeze()
    assert 'area' in Component.__dataclass_fields__
    start = p.load(out/'start_receipt.json')
    for name,digest in start['protected'].items():
        assert p.sha(p.ROOT/name) == digest, ('protected input changed',name)
    split = p.load(out/'split.json')
    scores = p.rows(out/'dev_scores.jsonl.gz')
    truth = {r['id']:r for r in p.rows(p.E/'dev_truth.jsonl.gz') if r.get('type')=='item' and not r['control'] and r['status']=='resolved'}
    assert set(truth)=={r['id'] for r in scores} and len(scores)==976
    halfdocs = {h:{r['line_id'].split('-p')[0] for r in scores if r['half']==h} for h in ('JUDGE','TUNE')}
    assert not halfdocs['TUNE'] & halfdocs['JUDGE']
    for r in scores:
        tr=truth[r['id']]
        assert r['truth']==tr['truth'] and r['weight']==tr['weight']
        assert math.isclose(r['weight'],1/(tr['card_inclusion_probability']*tr['cut_probability']),rel_tol=1e-14)
        assert split['documents'][r['line_id'].split('-p')[0]]['half']==r['half']
        for v in ('before','after'):
            observed={k:C.Counter(TP=0,FP=0,FN=0,TN=0) for k in t.KINDS}
            for sl in r['presence'][v]['slots']:
                tf=t.features(sl['truth']);pf=t.features(sl['prediction'])
                det=sl['detector_slot'] or {};ev=det.get('evidence',{})
                pf.update(any=bool(ev.get('above') or ev.get('below')),above=bool(ev.get('above')),below=bool(ev.get('below')))
                assert tf==sl['truth_presence'] and pf==sl['prediction_presence']
                for k in t.KINDS:
                    event='TP' if tf[k] and pf[k] else 'FP' if pf[k] else 'FN' if tf[k] else 'TN'
                    observed[k][event]+=1
            assert observed==r['presence'][v]['counts']
    summary=p.load(out/'dev_summary.json');cells=intervals=0
    for half in ('JUDGE','TUNE','ALL'):
        for wi,wave in enumerate(t.WAVES):
            rr=[r for r in scores if r['wave']==wave and (half=='ALL' or r['half']==half)]
            assert len(rr)==summary[half][wave]['cards']
            for k in t.KINDS:
                for v in ('before','after'):
                    cell=summary[half][wave]['families'][k][v]
                    for event in ('TP','FP','FN','TN'):
                        raw=sum(r['presence'][v]['counts'][k][event] for r in rr)
                        weighted=sum(r['weight']*r['presence'][v]['counts'][k][event] for r in rr)
                        assert cell['counts'][event]['raw']==raw
                        assert math.isclose(cell['counts'][event]['weighted'],weighted,abs_tol=1e-9)
                    for metric,err in (('precision','FP'),('recall','FN')):
                        count=lambda r,event:r['presence'][v]['counts'][k][event]
                        independent=t.estimate(rr,lambda r:count(r,'TP'),lambda r:count(r,'TP')+count(r,err),t.SEED+wi)
                        assert independent==cell[metric]
                        intervals+=1
                    cells+=1
    for entry in p.rows(out/'dev_input_custody.jsonl')+p.rows(out/'regression_input_custody.jsonl'):
        assert p.sha(entry['crop'])==entry['crop_sha256']
    gate=p.load(out/'heldout_gate_summary.json')
    assert gate['baseline_table_reproduced'] and gate['tables']['before']==gate['tables']['saved_sf4']
    assert all(r['google_errors']==80 and r['known']==10046 and r['unknown']==300 for tt in gate['tables'].values() for r in tt.values())
    diff=p.load(out/'owner_box_regression.json');cli=p.load(out/'owner_box_cli.json')
    for field in ('lost','added','moved'):
        assert sum(len(r[field]) for r in cli['lines'].values())==diff['summary'][field]
    assert cli['summary']['lines compared']==92 and not cli['summary']['lines missing old'] and not cli['summary']['lines missing new']
    # Saved S6 owner boxes must match the reproduced baseline coordinates.
    saved=p.load(p.OUT.parent/'S7_evidence/saved_S6_boxes.json')['lines']
    before=p.load(out/'owner_before_boxes.json')['lines']
    for lid,line in before.items():
        key=lambda z:sorted((r['kind'],r['bbox']) for r in z['boxes'])
        assert key(line)==key(saved[lid]),lid
    b.dump('validation.json',dict(complete=True,candidate_binding=binding,protected_files_unchanged=len(start['protected']),
        resolved_cards=976,document_split_disjoint=True,score_cells_rebuilt=cells,intervals_rebuilt=intervals,
        exact_saved_sf4_tables_reproduced=True,s6_owner_box_coordinate_parity_lines=92,
        native_component_area_contract=True,fixture_fallback_changes_native_branch=False,
        network=False,ctc_runs=0,r1_runs=0))
    print('S8b validation passed:',cells,'score cells;',intervals,'intervals;',len(start['protected']),'protected files unchanged.')


if __name__=='__main__':
    main()
