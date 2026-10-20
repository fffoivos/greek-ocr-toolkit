"""Offline SF7 replay. Inputs and outputs are individually SHA-bound."""
from greekocr.ops.data_root import input_path as _data_input
from collections import defaultdict
from copy import deepcopy
import gzip
import json
from pathlib import Path
from greekocr.labelfix import release_gate as sf6
from scripts.labelfix import release_gate_sf7 as gate
from scripts.labelfix.clariden.l1_common import overlay as sf6_overlay
from scripts.labelfix.clariden.r1_common import rows, sha256, write_rows
from scripts.labelfix.clariden.sf7_recompose import receipt
from scripts.labelfix.sf5_measure import runtime_from_overlay
from scripts.labelfix.sf6_measure import BINDING

DOC=Path('docs/records/labelfix/spellcheck');EV=DOC/'SF7_evidence'


def audit_inputs():
    inventory=DOC/'S8_DEV/private/audit100/line_inventory.json'
    overlays=DOC/'S8_DEV/private/audit100/selected_overlays.json.gz'
    truth=DOC/'S8_DEV/audit100_private/audit100_final.json'
    inv={r['line_id']:r for r in json.loads(_data_input(inventory).read_text())};truths=json.loads(_data_input(truth).read_text())
    data=json.load(gzip.open(_data_input(overlays),'rt'))['records']
    assert len(data)==len(inv)==len(truths)==100
    result=[]
    for o in data:
        lid=o['line_id'];record=dict(id=lid,label=inv[lid]['original_label'],wave=inv[lid]['wave'],script_class='greek_poly')
        rt=runtime_from_overlay(o)
        before=sf6_overlay(record,rt,'ENSEMBLE_AB',BINDING)
        assert (before['status'],before.get('label'))==(o['status'],o.get('label'))
        result.append(dict(id=lid,record=record,runtime=rt,truth=truths[lid],saved_sf6_label=o['label']))
    return result,{str(p):sha256(_data_input(p)) for p in (inventory,overlays,truth)}


def cards_inputs():
    from scripts.labelfix.clariden.l1e_measure import saved_runtime
    cards=DOC/'R2_evidence/reader_errors_39_owner_final.json'
    meta_path=Path('artifacts/labelfix_r1/heldout_font/lines.jsonl.gz')
    recovery=DOC/'clariden/L1E_evidence/heldout_final/observation_recovery.json'
    det_path=DOC/'S6_lines.jsonl.gz';source_path=DOC/'R0_evidence/continuity_666.jsonl'
    cc=json.loads(_data_input(cards).read_text())['cards'];assert len(cc)==39
    ids={r['line_id'] for r in cc};meta={r['id']:r for r in rows(meta_path) if r['id'] in ids}
    entries=json.loads(_data_input(recovery).read_text())['entries']
    for lid,r in meta.items():
        # Exact old extractor predicates, using the saved recovery's native PNG
        # dimensions. No missing observation is silently defaulted to clean.
        for c in r['coverage']:
            if 'evidence_state' in c and 'uncertainty' in c:continue
            e=entries[lid];u=[]
            assert e['pixel_measurements']==r['font_size']['pixel_measurements']
            if e['pixel_measurements']==0:u.append('no_pixel_evidence')
            if c['span'][0]<0 or c['span'][1]>e['width']:u.append('out_of_image_span')
            c.update(uncertainty=u,evidence_state='UNKNOWN' if u else 'unadjudicated')
    preds={a:defaultdict(list) for a in ('A','B','E')};paths=[cards,meta_path,recovery,det_path,source_path]
    for a in preds:
        p=Path('artifacts/labelfix_r1/output_3678928')/a/'heldout_predictions.jsonl'
        pr=p.with_suffix('.receipt.json');assert json.loads(_data_input(pr).read_text())['prediction_sha256']==sha256(_data_input(p))
        paths.extend((p,pr))
        for r in rows(p):
            if r['line_id'] in ids:preds[a][r['line_id']].append(r)
    detectors={r['line_id']:r for r in rows(det_path) if r['line_id'] in ids}
    sources={r['line_id']:r for r in rows(source_path) if r['line_id'] in ids}
    runtimes={lid:saved_runtime(detectors[lid],meta[lid],{a:preds[a][lid] for a in preds}) for lid in ids}
    result=[]
    for c in cc:
        lid=c['line_id'];rt=runtimes[lid]
        result.append(dict(card=c,record=dict(id=lid,label=sources[lid]['google'],script_class='greek_poly'),runtime=rt))
    return result,{str(p):sha256(_data_input(p)) for p in paths}


def measure():
    EV.mkdir(exist_ok=True)
    audit,inputs=audit_inputs();binding=dict(BINDING,policy_sha256=gate.policy_binding()['sha256'])
    write_rows(EV/'audit_inputs.jsonl.gz',audit)
    summary={};results=[]
    for v in 'AB':
        fixed=lost=0
        for w in audit:
            o=gate.overlay(w['record'],w['runtime'],v,binding)
            retained=o['status'] in ('corrected','unchanged') and o.get('label')==w['saved_sf6_label']
            if w['truth']['ok']:lost+=not retained
            else:fixed+=o['status']=='hold' or o.get('label')==w['record']['label']
            results.append(dict(id=w['id'],variant=v,audit_right=w['truth']['ok'],retained=retained,overlay=o))
        summary[v]=dict(fixed=fixed,wrong_total=17,lost=lost,right_total=83)
    write_rows(EV/'audit_replay.jsonl.gz',results)
    receipt(EV/'audit_receipt.json',dict(policy=gate.policy_binding(),inputs=inputs,
        outputs={n:sha256(EV/n) for n in ('audit_inputs.jsonl.gz','audit_replay.jsonl.gz')},
        summary=summary,sf6_replayed=100,fix_definition='wrong sf6 release prevented (HOLD), not corrected print truth; 1 unreadable remains unknown',
        saved_evidence_reconstruction='only retained accepted overlay fields; no invented recogniser score or peer E'))
    cards,ci=cards_inputs();write_rows(EV/'cards39_inputs.jsonl.gz',cards)
    results=[]
    for w in cards:
        for v in 'AB':
            results.append(dict(card=w['card'],variant=v,overlay=gate.overlay(w['record'],w['runtime'],v,binding)))
    write_rows(EV/'cards39_replay.jsonl.gz',results)
    receipt(EV/'cards39_receipt.json',dict(inputs=ci,cards=39,variants=2,policy=gate.policy_binding(),
        outputs={n:sha256(EV/n) for n in ('cards39_inputs.jsonl.gz','cards39_replay.jsonl.gz')},
        evidence='saved heldout detector, A/B/E predictions, extractor metadata, native header recovery; no inference'))
    prior=json.loads((_data_input(EV/'sf6_before.json')).read_text());assert sf6.policy_binding()==prior['policy']
    witnesses=list(rows(DOC/'SF6c_evidence/after/witness_inputs.jsonl.gz'))
    after=[sf6_overlay(w['record'],w['runtime'],w.get('mode','ENSEMBLE_AB'),BINDING) for w in witnesses]
    assert json.loads(json.dumps(after,ensure_ascii=False,sort_keys=True))==prior['outputs']
    receipt(EV/'sf6_reproduction.json',dict(identical=True,fixtures=len(after),policy=sf6.policy_binding(),
        before_sha256=sha256(_data_input(EV/'sf6_before.json')),canonical_output_sha256=__import__('hashlib').sha256(json.dumps(after,ensure_ascii=False,sort_keys=True).encode()).hexdigest()))
    print(json.dumps(summary))


if __name__=='__main__':measure()
