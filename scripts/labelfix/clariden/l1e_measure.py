"""L1E held-out metadata-only R1 frozen-slot instrument; no pixel/model work.

Full 666-line scoring is run on Clariden, not the Mac. Export <=200 verification
lines for the identical l1e_run entry point. Truth never enters the reader.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from copy import deepcopy
import json
from pathlib import Path
import time
import numpy as np
from greekocr.labelfix.candidates import pair_tokens
from greekocr.labelfix.text import nfd,clusters,strip_marks
from greekocr.labelfix.reading import LineReading,MARKS
from greekocr.labelfix.linemetric import mark_set
from greekocr.labelfix.release_gate import MODES,serialize,compose_runtime,edit_guard,policy_binding
from greekocr.labelfix.ctc_align import recognition_fields
from scripts.labelfix.clariden.r1_common import rows,sha256,write_json,write_rows
from scripts.labelfix.clariden.l1e_run import decision_record

KINDS={p:'breathing' if p in ('psili','dasia') else 'accent' if p in ('acute','grave','circumflex') else p for p in MARKS}


def recover_observation(meta,crop_root):
    """Recover SF2's exact predicates from saved measurements and PNG headers.

    No pixels are decoded. Missing font evidence is never defaulted to clean.
    """
    from PIL import Image
    from scripts.labelfix.clariden.r1_common import crop_path
    receipts={}
    for lid,row in meta.items():
        if all('evidence_state' in c and 'uncertainty' in c for c in row['coverage']):continue
        path=crop_path(row['crop'],crop_root,'e3')
        with Image.open(path) as image:width,height=image.size
        measurements=row.get('font_size',{}).get('pixel_measurements')
        if measurements is None:raise ValueError('cannot recover observation without pixel measurements: '+lid)
        for c in row['coverage']:
            uncertainty=[]
            if measurements==0:uncertainty.append('no_pixel_evidence')
            if c['span'][0]<0 or c['span'][1]>width:uncertainty.append('out_of_image_span')
            c.setdefault('uncertainty',uncertainty)
            c.setdefault('evidence_state','UNKNOWN' if uncertainty else 'unadjudicated')
        receipts[lid]=dict(crop=str(path),crop_sha256=sha256(path),width=width,height=height,pixel_measurements=measurements)
    return receipts


def atomic(marks):
    # R1 error-type instrument: split compound truth; punctuation is separate.
    return {(KINDS.get(p,k),p) for k,name in marks if k!='apostrophe' for p in (name.split('+') if k=='compound' else [name])}


def google_marks(google,rec):
    # Same word/base pairing as r1_error_types.google_marks.
    names={v:(KINDS[k],k) for k,v in MARKS.items()};out={}
    for g,m in pair_tokens(google,rec):
        if m is None or strip_marks(nfd(g.core))!=strip_marks(nfd(m.core)):continue
        for a,b in zip(clusters(nfd(g.core)),clusters(nfd(m.core))):
            out[m.core_start+b.start]={names[x] for x in a.marks if x in names}
    return out


def saved_runtime(line,meta,predictions):
    raw=LineReading(line['reading'],deepcopy(line['recogniser_slots']),[],
        opening_quotes=deepcopy(line.get('opening_quotes',[])),constraint_flags=deepcopy(line.get('reading_flags',[])))
    if meta['recogniser_text']!=line['recogniser_text']:raise ValueError('recogniser identity mismatch')
    return dict(id=line['line_id'],recogniser_text=line['recogniser_text'],recogniser_nfd=line['recogniser_text'],
        **recognition_fields(meta),
        detector=serialize(raw),coverage=meta['coverage'],font_size=meta['font_size'],r1_predictions=predictions['A'],
        peer_predictions={a:predictions[a] for a in ('B','E')},peer_coverage={a:meta['coverage'] for a in ('B','E')})


def score_line(line,google,runtime,*,decisions=None):
    gm=google_marks(google,nfd(line['recogniser_text']));stats={};details={}
    owners=defaultdict(list)
    for s in line['recogniser_slots']:
        if s.get('component_slot') is not None:owners[s['component_slot']].append(s['start'])
    primary={p['start']:p for p in runtime['r1_predictions']}
    gclusters={c.start:c for c in clusters(nfd(line['recogniser_text']))}
    for mode in MODES:
        rd=compose_runtime(runtime,mode) if decisions is None else decisions[mode]
        by={s['start']:s for s in rd['slots']}
        c=Counter(corrected=0,wrong=0,missed=0,HOLD=0,new=0,google_errors=0,known=0,unknown=0,kept=0)
        events=[]
        for slot in line['slots']:
            matches=owners.get(slot['slot'],[])
            if len(matches)!=1:continue
            start=matches[0]
            # Exact R1 RESULT domain: a mapped scored A slot with paired Google.
            if start not in gm or start not in primary:continue
            s=by[start];g=gm[start];r=atomic(mark_set('+'.join(s['parts']) or 'none'))
            if slot['truth'] is None:c['unknown']+=1;continue
            truth=atomic(slot['truth']);c['known']+=1
            # Original-label supported-domain guard, in addition to the shared
            # recogniser/composer guard. No unsupported Google edit is accepted.
            original=slot['base']+''.join(MARKS[p] for _,p in sorted(g))
            proposal=gclusters[start].base+''.join(MARKS[p] for p in s['parts'])
            hold=bool(s['hold_reasons'] or edit_guard(original,proposal))
            if g!=truth:
                c['google_errors']+=1
                outcome='HOLD' if hold else 'corrected' if r==truth else 'missed' if r==g else 'wrong'
            else:outcome='HOLD_control' if hold else 'new' if r!=truth else 'kept'
            c[outcome]+=1
            if g!=truth or outcome=='new':
                events.append(dict(slot=slot['slot'],start=start,google=sorted(g),truth=sorted(truth),reader=sorted(r),
                    outcome=outcome,reasons=s['hold_reasons']))
        c['lines']=1;c['lines_held']=bool(rd['hold_slots']);stats[mode]=dict(c);details[mode]=events
    return stats,details


def measure(detector,frozen_path,extraction,runs,google_path,out,crop_root,mock_lines=64):
    from scripts.labelfix.clariden.r1_score import metadata,prediction_map
    started=time.monotonic();out=Path(out);out.mkdir(parents=True,exist_ok=False)
    meta=metadata(Path(extraction));pred={};inputs={}
    for a in ('A','B','E'):
        path=Path(runs)/a/'heldout_predictions.jsonl'
        p=prediction_map(path,meta,extraction=Path(extraction),checkpoint=Path(runs)/a/'best.pt')
        pred[a]=defaultdict(list)
        for (lid,_),v in p.items():pred[a][lid].append(v)
        inputs[str(path)]=sha256(path);inputs[str(path.with_suffix('.receipt.json'))]=sha256(path.with_suffix('.receipt.json'))
    recovered=recover_observation(meta,crop_root)
    recovery_path=out/'observation_recovery.json'
    write_json(recovery_path,dict(schema='l1e-observation-recovery-v1',lines=len(recovered),
        method='unchanged extract_line predicates: saved pixel_measurements, spans and hash-bound PNG header width; no pixel decode',
        r1_extract_sha256=sha256(Path(__file__).with_name('r1_extract.py')),entries=recovered))
    inputs[str(recovery_path)]=sha256(recovery_path)
    google={r['line_id']:r['gt'] for r in rows(google_path) if r['line_id'] in meta}
    totals={m:Counter() for m in MODES};allruntime={};decisions=[];events=[]
    frozen={r['line_id']:r for r in rows(frozen_path) if not r['dev']}
    for line in rows(detector):
        if line['dev']:continue
        lid=line['line_id']
        rt=saved_runtime(line,meta[lid],{a:pred[a][lid] for a in pred})
        stats,ev=score_line(frozen[lid],google[lid],rt)
        for m in MODES:totals[m].update(stats[m])
        allruntime[lid]=rt;decisions.append(dict(id=lid,decisions=decision_record(rt)))
        events.append(dict(id=lid,counts=stats,events=ev))
    if set(allruntime)!=set(meta) or len(meta)!=666:raise ValueError('held-out identity changed')
    for m in MODES:
        if totals[m]['google_errors']!=80:raise ValueError('R1 80-error instrument changed: '+m+': '+str(totals[m]['google_errors']))
    write_rows(out/'runtime.jsonl.gz',allruntime.values());write_rows(out/'decisions.jsonl.gz',decisions);write_rows(out/'events.jsonl',events)
    inputs.update({str(p):sha256(p) for p in [Path(detector),Path(frozen_path),Path(extraction)/'extraction_receipt.json',Path(extraction)/'lines.jsonl.gz',Path(google_path)]})
    report=dict(schema='l1e-heldout-v1',complete=True,lines=666,google_errors=80,modes={m:dict(c) for m,c in totals.items()},
        policy=policy_binding(),inputs=inputs,elapsed_seconds=time.monotonic()-started,
        instrument='R1 frozen physical slots; one frozen recogniser owner; scored A starts; base-identical Google word pairing; atomic mark sets; punctuation excluded; slot acceptance, not whole-line release',
        unknown_truth='excluded from corrected/wrong/missed/HOLD/new; retained in decisions',inference_runs=0,detector_runs=0)
    write_json(out/'measurement_receipt.json',report)
    # Prioritise all known-error/new-error lines, then ensure every book is
    # represented. Selection never changes the held-out table or reader inputs.
    chosen=[]
    for ev in events:
        if any(ev['events'][m] for m in MODES):chosen.append(ev['id'])
    for lid in meta:
        if lid not in chosen:chosen.append(lid)
    chosen=chosen[:mock_lines]
    prepare_mock(out/'mock',chosen,allruntime,meta,frozen,google,extraction,runs,decisions)
    return report


def prepare_mock(out,chosen,runtime,meta,frozen,google,extraction,runs,decisions):
    """Create a historical-format verification fixture, never a training shard."""
    from scripts.labelfix.clariden.l1_common import release
    out=Path(out);out.mkdir(parents=True);historical=out/'historical';data=historical/'detector';combined=historical/'combined'
    data.mkdir(parents=True);combined.mkdir();binding_dir=out/'binding';binding_dir.mkdir()
    selection=out/'selection.jsonl';records=[dict(id=i,label=google[i],doc=frozen[i]['doc'],wave='heldout-verification',source='print-instrument',script_class='greek_poly') for i in chosen]
    write_rows(selection,records);source=out/'source.jsonl';write_rows(source,records)
    index=np.load(Path(extraction)/'index.npy',allow_pickle=False);lines={r['line']:r['id'] for r in meta.values()}
    byid={lid:i for i,lid in enumerate(chosen)};samples=[];wide=[];cache={}
    for row in index:
        lid=lines[int(row['line'])]
        if lid not in byid:continue
        shard=int(row['shard'])
        if shard not in cache:cache[shard]=np.load(Path(extraction)/f'shard-{shard:05d}-wide.npy',mmap_mode='r',allow_pickle=False)
        samples.append(dict(line=byid[lid],start=int(row['start']),letter=int(row['letter']),mask=row['mask'][0].tolist()))
        wide.append(np.array(cache[shard][row['offset']],copy=True))
    # The L1 shard contract is ordered by line, then extraction slot.
    order=sorted(range(len(samples)),key=lambda i:(samples[i]['line'],samples[i]['start']))
    samples=[samples[i] for i in order];wide=[wide[i] for i in order]
    dp=data/'shard-00000-detector.jsonl.gz';sp=data/'shard-00000-samples.json';wp=data/'shard-00000-wide.npy'
    detector_records=[{k:v for k,v in runtime[i].items() if k not in ('r1_predictions','peer_predictions','peer_coverage')} for i in chosen]
    write_rows(dp,detector_records);write_json(sp,samples);np.save(wp,np.asarray(wide,dtype=np.uint8),allow_pickle=False)
    ds=dict(shard=0,lines=len(chosen),windows=len(samples),complete=True,sha256={p.name:sha256(p) for p in (dp,sp,wp)})
    write_json(data/'shard-00000-receipt.json',ds)
    write_json(data/'detector_receipt.json',dict(complete=True,lines=len(chosen),windows=len(samples),selection_sha256=sha256(selection),alignment_sha256={},shards=[ds]))
    cp=combined/'shard-00000-combined.jsonl.gz'
    original=[{k:v for k,v in runtime[i].items() if k not in ('peer_predictions','peer_coverage')} for i in chosen];write_rows(cp,original)
    write_json(combined/'shard-00000-receipt.json',dict(complete=True,shard=0,lines=len(chosen),samples=len(samples),output_sha256=sha256(cp)))
    binding=dict(detector='s6',detector_commit='0472a908-frozen-S6',code_commit='verification-only',
        r1_sha256=sha256(Path(runs)/'A/best.pt'),policy_sha256=policy_binding()['sha256'])
    write_json(binding_dir/'binding.json',binding)
    inp=dict(exclusions={'verification_only':True,'never_training_input':True},out_of_scope={},r0_policy='verification-only',input_documents_sha256={})
    write_json(historical/'input_receipt.json',inp)
    release(selection,[cp],historical/'release',binding,source,inp)
    run=dict(complete=True,lines=len(chosen),mock=True,verification_only=True,binding_sha256=sha256(binding_dir/'binding.json'),
        step_receipts={str(p.relative_to(historical)):sha256(p) for p in historical.rglob('*receipt.json')})
    write_json(historical/'run_receipt.json',run)
    write_rows(out/'expected_decisions.jsonl',[r for r in decisions if r['id'] in chosen])
    write_json(out/'fixture_receipt.json',dict(verification_only=True,never_training_input=True,lines=len(chosen),
        selection_sha256=sha256(selection),expected_decisions_sha256=sha256(out/'expected_decisions.jsonl')))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ('detector','frozen','extraction','runs','google','out','crop-root'):ap.add_argument('--'+k,type=Path,required=True)
    ap.add_argument('--mock-lines',type=int,default=64)
    a=ap.parse_args()
    if not 1<=a.mock_lines<=200:raise ValueError('verification bound')
    r=measure(a.detector,a.frozen,a.extraction,a.runs,a.google,a.out,a.crop_root,a.mock_lines)
    print(json.dumps({k:v for k,v in r.items() if k not in ('inputs','policy')},indent=2))


if __name__=='__main__':main()
