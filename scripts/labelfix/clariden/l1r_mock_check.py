"""Check the complete saved 64-line runtime against SF6c and actual L1R releases.

Only verification inputs are read. Runs the exact L1R job entry point; never
loads a checkpoint, runs inference, or processes the training population.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from greekocr.labelfix import release_gate as gate
from greekocr.labelfix.release_gate import MODES, compose_runtime
from scripts.labelfix.sf6_measure import effective
from scripts.labelfix.clariden.l1_common import rows, sha256, write_json
from scripts.labelfix.clariden.l1r_recompose_ext import load, VARIANTS, validate_release


def check(config, out, evidence):
    cfg=load(config); evidence=Path(evidence);out=Path(out)
    reference=load('docs/records/labelfix/spellcheck/SF4_evidence/runtime64_parity.json')
    for name,wanted in reference['inputs'].items():
        if sha256(name)!=wanted:raise ValueError('saved verification runtime changed: '+name)
    frozen=load('docs/records/labelfix/spellcheck/SF6c_evidence/verification.json')
    # These gate/science bytes must stay identical to the full-composer check.
    for name in ('greekocr/labelfix/release_gate.py','greekocr/labelfix/reading.py',
                 'greekocr/labelfix/text.py','greekocr/labelfix/segmentation.py',
                 'scripts/labelfix/clariden/l1_common.py'):
        if sha256(name)!=frozen['policy']['sources'][name]:raise ValueError('SF6c frozen policy/science source changed')
    subprocess.run([sys.executable,'-B','scripts/labelfix/clariden/l1r_recompose_ext.py',
                    '--config',str(config),'--out',str(out),'--workers','2','--audit-decisions'],check=True)
    runtime=[r for p in sorted(Path(cfg['ensemble_run']).glob('shard-*-combined.jsonl.gz')) for r in rows(p)]
    if len(runtime)!=64 or len({r['id'] for r in runtime})!=64:raise ValueError('not complete runtime64')
    actual={r['id']:r['decisions'] for p in sorted((out/'shards').glob('*/decisions.jsonl.gz')) for r in rows(p)}
    line_modes=slot_modes=0;holds={m:0 for m in MODES};full={}
    for r in runtime:
        full[r['id']]={}
        for m in MODES:
            v=compose_runtime(r,m);full[r['id']][m]=v
            comparable=v
            if actual[r['id']][m]!=comparable:raise ValueError('full composer parity failed: '+r['id']+':'+m)
            line_modes+=1;slot_modes+=len(v['slots']);holds[m]+=bool(v['hold_slots'])
    if set(actual)!={r['id'] for r in runtime}:raise ValueError('decision population mismatch')
    for m in MODES:
        if holds[m]!=reference['modes'][m]['lines_held']:raise ValueError('SF4 saved full-composer totals changed')
    selected=list(rows(cfg['selection']));records={r['id']:r for r in selected}
    byid={r['id']:r for r in runtime}
    adapter_modes=adapter_slots=0
    for v in VARIANTS:
        for overlay in rows(out/'release'/f'overlay_{v}.jsonl.gz'):
            expected=full[overlay['line_id']][v.upper()]
            if overlay['composed_text']!=expected['text']:raise ValueError('release composed text differs')
            if len(overlay['gate_decisions'])!=len(expected['slots']):raise ValueError('release slot count differs')
            for a,b in zip(overlay['gate_decisions'],expected['slots']):
                if any(a.get(k)!=b.get(k) for k in a):raise ValueError('actual release slot decision differs')
                adapter_slots+=1
            lid=overlay['line_id']
            label=effective(records[lid]['label'],byid[lid]['recogniser_text'],expected,gate,byid[lid])
            if overlay['deletion_checks']!=json.loads(json.dumps(label['deletion_checks'])):
                raise ValueError('SF6c deletion check parity failed')
            for key in ('status','alias_only'):
                actual_value=overlay[key] if key=='status' else (overlay[key] and overlay['status']=='unchanged')
                if actual_value!=label[key]:raise ValueError('SF6c measurement adapter differs: '+key)
            expected_label=records[lid]['label'] if label['status']=='unchanged' else label['label']
            if overlay['status'] in ('corrected','unchanged') and overlay['label']!=expected_label:
                raise ValueError('SF6c measurement released label differs')
            for key,value in overlay['elision_census'].items():
                if value!=label['elision_census'][key]:raise ValueError('SF6c measurement elision census differs')
            if expected['hold_slots'] and overlay['status']!='hold':raise ValueError('HOLD admitted')
            adapter_modes+=1
    validation=validate_release(out/'release',selected,VARIANTS)
    result=dict(complete=True,verification_only=True,lines=64,exact_lines=64,
                mode_decisions=line_modes,exact_mode_decisions=line_modes,
                slot_mode_decisions=slot_modes,exact_slot_mode_decisions=slot_modes,
                release_mode_decisions=adapter_modes,release_slot_decisions=adapter_slots,
                full_composer_and_release_adapter_parity=True,
                full_composer_lines_held=holds,release_format=validation,
                sf6_measure_sha256=sha256('scripts/labelfix/sf6_measure.py'),
                frozen_sf6c_verification_sha256=sha256('docs/records/labelfix/spellcheck/SF6c_evidence/verification.json'),
                reference_sha256=sha256('docs/records/labelfix/spellcheck/SF4_evidence/runtime64_parity.json'),
                receipt_sha256=sha256(out/'receipt.json'),runtime_sha256=reference['inputs'],
                current_policy=load(out/'receipt.json')['policy'],inference_runs=0,detector_runs=0)
    assert line_modes==reference['mode_decisions']==256 and slot_modes==reference['slot_mode_decisions']==7620
    evidence.mkdir(parents=True,exist_ok=True)
    write_json(evidence/'mock_parity.json',result)
    print('L1R_MOCK_PARITY '+json.dumps({k:v for k,v in result.items() if k not in ('current_policy','runtime_sha256')},ensure_ascii=False))


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--evidence',type=Path,required=True)
    a=ap.parse_args();check(a.config,a.out,a.evidence)
