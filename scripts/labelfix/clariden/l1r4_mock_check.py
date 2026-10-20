"""Independent 64-line L1F join, frozen-composer parity and two natural demos."""
import argparse
from pathlib import Path

from greekocr.labelfix import release_gate as gate
from greekocr.labelfix.ctc_align import recognition_fields
from scripts.labelfix.sf6_measure import effective
from scripts.labelfix.clariden import l1c_census as c
from scripts.labelfix.clariden.l1r_recompose_ext import validate_release, VARIANTS

DEMO = ('384c3f89-p000059-l0023','384c3f89-p000096-l0031')


def check(config, root, destination):
    cfg=c.load(config);root=Path(root)
    raw={r['id']:r for p in sorted(Path(cfg['ensemble_run']).glob('shard-*-combined.jsonl.gz')) for r in c.rows(p)}
    frame_root=Path(cfg['l1f']['root']); final=c.load(frame_root/'receipt.json')
    frames={r['line_id']:r for entry in final['shards'] for r in c.rows(frame_root/entry['output'])}
    actual={r['id']:r['decisions'] for p in sorted((root/'shards').glob('*/decisions.jsonl.gz')) for r in c.rows(p)}
    joined={r['id']:r for p in sorted((root/'shards').glob('*/joined-runtime.jsonl.gz')) for r in c.rows(p)}
    selected={r['id']:r for r in c.rows(cfg['selection'])}
    assert len(raw)==len(frames)==len(actual)==len(joined)==64
    assert raw.keys()==frames.keys()==actual.keys()==joined.keys()==selected.keys()
    modes=slots=adapter_modes=adapter_slots=0; withheld=[]; full={}; expected_runtime={}
    for lid,old in raw.items():
        expected=dict(old); row=frames[lid]
        # Independent direct join from raw L1F outputs; no production join helper.
        if row['provenance']['alignment_identity_match']:
            expected.update(recognition_fields(row));expected['recognition_provenance']=row['provenance']
        else:
            assert all(k not in joined[lid] for k in ('recognition_confidence','recognition_evidence','image_width'))
            withheld.append(lid)
        assert expected==joined[lid]
        expected_runtime[lid]=expected;full[lid]={}
        for mode in gate.MODES:
            decision=gate.compose_runtime(expected,mode);full[lid][mode]=decision
            assert actual[lid][mode]==decision
            modes+=1;slots+=len(decision['slots'])
    demos=[]
    for variant in VARIANTS:
        baseline={r['line_id']:r for r in c.rows(Path(cfg['baseline']['release_root'])/'release'/f'overlay_{variant}.jsonl.gz')}
        for row in c.rows(root/'release'/f'overlay_{variant}.jsonl.gz'):
            lid=row['line_id'];rt=expected_runtime[lid];decision=full[lid][variant.upper()]
            assert row['composed_text']==decision['text']
            assert len(row['gate_decisions'])==len(decision['slots'])
            for a,b in zip(row['gate_decisions'],decision['slots']):
                assert all(a.get(k)==b.get(k) for k in a);adapter_slots+=1
            label=effective(selected[lid]['label'],rt['recogniser_text'],decision,gate,rt)
            assert row['deletion_checks']==__import__('json').loads(__import__('json').dumps(label['deletion_checks']))
            assert row['status']==label['status']
            assert (row['alias_only'] and row['status']=='unchanged')==label['alias_only']
            if row['status'] in ('corrected','unchanged'):
                expected_label=selected[lid]['label'] if label['status']=='unchanged' else label['label']
                assert row['label']==expected_label
            assert all(value==label['elision_census'][key] for key,value in row['elision_census'].items())
            if decision['hold_slots']: assert row['status']=='hold'
            adapter_modes+=1
            if variant=='presence' and lid in DEMO:
                before=baseline[lid]
                assert before['status']=='hold' and row['status']=='corrected'
                allowed=[(a,b) for a,b in zip(before['deletion_checks'],row['deletion_checks']) if not a['allowed'] and b['allowed'] and b['signals']['recogniser']]
                assert allowed
                from scripts.labelfix.clariden.l1r_recompose_ext import overlay
                width_only=overlay(selected[lid],dict(raw[lid],image_width=rt['image_width']),'presence',c.load(root/'receipt.json')['binding'])
                assert width_only['status']=='hold'
                demos.append(dict(line_id=lid,before=before['status'],after=row['status'],
                                  native_width_only=width_only['status'],checks=[dict(before=a,after=b) for a,b in allowed]))
    assert modes==256 and slots==7620 and adapter_modes==192 and adapter_slots==5715
    assert len(demos)==2 and len(withheld)==2
    result=dict(complete=True,verification_only=True,lines=64,exact_mode_decisions=modes,mode_decisions=modes,
        exact_slot_mode_decisions=slots,slot_mode_decisions=slots,release_mode_decisions=adapter_modes,
        release_slot_decisions=adapter_slots,full_composer_and_release_adapter_parity=True,
        demo_lines_allowed=2, demo_lines=demos,withheld_fields_missing=withheld,
        release_validation=validate_release(root/'release',list(selected.values()),VARIANTS),
        policy=c.load(root/'receipt.json')['policy'],receipt_sha256=c.sha256(root/'receipt.json'))
    c.atomic_json(destination,result)
    print('L1R4_MOCK_PARITY '+c.canonical({k:v for k,v in result.items() if k not in ('policy','demo_lines','release_validation')}))
    return result


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config',required=True);ap.add_argument('--input-dir',required=True);ap.add_argument('--out',required=True)
    a=ap.parse_args();check(a.config,a.input_dir,a.out)
