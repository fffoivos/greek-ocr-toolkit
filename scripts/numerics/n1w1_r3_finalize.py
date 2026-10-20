"""Offline replacement-aware finaliser; --dry-run validates routing without collecting reads."""
import argparse
import json
from pathlib import Path
from collections import defaultdict
import n1w1 as m
import n1w1_r3 as repl
from n1w1_combine import decode_and_gate,control_matches


def collect_replacement(ctx,reader,logical,seen,art=repl.R3,pack=m.PACK):
    base=art/'answers'/(ctx+'.'+reader);rd=pack/ctx/reader
    rp=Path(str(base)+'.run.json');run=json.loads(rp.read_text());roll=Path(run['rollout']);digest=m.sha(roll)
    if run['rc']!=0 or run['model']!='gpt-6.1-sol' or digest in seen:raise ValueError('failed/model/reused rollout')
    seen.add(digest)
    meta=[r.get('payload',{}) for r in m.rows(roll) if r.get('type') in ('session_meta','turn_context')]
    if {v['model'] for v in meta if v.get('model')}!={'gpt-6.1-sol'} or {v.get('effort',v.get('reasoning_effort')) for v in meta if v.get('effort',v.get('reasoning_effort'))}!={'medium'}:raise ValueError('model/effort provenance')
    scan=m.n1w1_scan_rollout.inspect(roll,rd)
    if not scan['ok'] or scan['scanner_version']!='v4.4-canonical':raise ValueError('unclean v4.4 scan')
    cov=m.coverage(scan,roll,rd,m.rows(rd/'items.jsonl'),image_fields=('line','zoom'));dropped=set(cov['dropped_items'])
    kp=repl.keypath(art,ctx,reader);key=json.loads(kp.read_text());gate,decoded=decode_and_gate(key,m.rows(rd/'answers.jsonl'))
    controls=[d for d in decoded if d['control'] and d['item_id'] not in dropped]
    wrong=sum(d['meaning']!='unreadable' and not control_matches(key['items'][d['item_id']]['control_truth'],d['meaning']) for d in controls)
    raised=any(key['items'][d['item_id']]['control_truth']=='raised dot' and d['meaning']=='raised dot' for d in controls)
    gate.update(status='VALID' if wrong<=1 and raised and len(controls)>=2 else 'VOID',viewed_controls=len(controls),viewed_wrong=wrong,raised_control_correct=raised)
    votes=[dict(d,reader=logical,physical_reader=reader,context=ctx+'/'+reader,replaces=ctx+'/'+logical,context_status=gate['status'],read_status='unviewed' if d['item_id'] in dropped else 'ok',rollout_sha256=digest) for d in decoded]
    m.dump(Path(str(base)+'.scan.json'),scan);m.dump(Path(str(base)+'.coverage.json'),cov);m.dump(Path(str(base)+'.gate.json'),gate)
    paths=[rp,roll,rd/'answers.jsonl',kp,*[Path(str(base)+s) for s in ('.scan.json','.coverage.json','.gate.json')]]
    return votes,dict(gate=gate,coverage=cov,evidence={str(p):m.sha(p) for p in paths})


def route_votes(original,replacement,route):
    selected=set(route['slot_ids']);logical=route['replaces']
    if any(v['context_status']=='VALID' and v['read_status']=='ok' and v['slot_id'] in selected for v in original if not v['control']):raise ValueError('routing would replace valid viewed evidence')
    kept=[v for v in original if v['control'] or v['slot_id'] not in selected]
    fresh=[v for v in replacement if not v['control'] and v['slot_id'] in selected]
    if {v['slot_id'] for v in fresh}!=selected or len(fresh)!=len(selected):raise ValueError('replacement slot coverage mismatch')
    if any(v['reader']!=logical for v in fresh):raise ValueError('wrong logical reader')
    return kept+fresh


def finalize(dry_run=False,apply_lead=False):
    info=repl.validate();routes={(r['context'],r['replaces']):r for r in info['replacements']}
    original_validate=m.validate;original_collect=m.collect
    if dry_run:
        total=0
        for (ctx,logical),r in routes.items():
            key=json.loads(repl.keypath(repl.R3,ctx,r['reader']).read_text())
            slots={v['slot_id'] for v in key['items'].values() if v['control_truth'] is None}
            if slots!=set(r['slot_ids']):raise ValueError('route and key slots differ')
            total+=len(slots)
        return dict(dry_run=True,routing='ok',replacement_contexts=len(routes),positions=total,reads_started=0,probes_started=0)
    def validate(art,pack):
        repl.validate();return original_validate(art,pack)
    def collect(art,pack,ctx,logical,seen):
        r=routes.get((ctx,logical))
        try:vv,ev=original_collect(art,pack,ctx,logical,seen)
        except (ValueError,KeyError,TypeError,OSError) as exc:
            if not r:raise
            k=json.loads(repl.keypath(art,ctx,logical).read_text())
            vv=[dict(item_id=i,slot_id=v['slot_id'],reader=logical,context=ctx+'/'+logical,control=v['control_truth'] is not None,context_status='INVALID',read_status='invalid',meaning=None,reason=str(exc)) for i,v in k['items'].items()]
            ev=dict(status='INVALID',reason=str(exc))
        if not r:return vv,ev
        rd=pack/ctx/r['reader'];base=repl.R3/'answers'/(ctx+'.'+r['reader'])
        if not Path(str(base)+'.run.json').exists():
            if not Path(str(base)+'.attempt.json').exists() and not (repl.R3/'STOPPED_AT_70.json').exists():raise ValueError('replacement incomplete; no attempt/stop receipt')
            fresh=[dict(item_id=i,slot_id=v['slot_id'],reader=logical,physical_reader=r['reader'],context=ctx+'/'+r['reader'],control=False,context_status='INVALID',read_status='invalid',meaning=None,reason='replacement missing or failed; HOLD') for i,v in json.loads(repl.keypath(repl.R3,ctx,r['reader']).read_text())['items'].items() if v['control_truth'] is None]
            replacement_ev=dict(status='INVALID',reason='replacement missing or failed; HOLD')
        else:
            try:fresh,replacement_ev=collect_replacement(ctx,r['reader'],logical,seen)
            except (ValueError,KeyError,TypeError,OSError) as exc:
                fresh=[dict(item_id=i,slot_id=v['slot_id'],reader=logical,physical_reader=r['reader'],context=ctx+'/'+r['reader'],control=False,context_status='INVALID',read_status='invalid',meaning=None,reason=str(exc)) for i,v in json.loads(repl.keypath(repl.R3,ctx,r['reader']).read_text())['items'].items() if v['control_truth'] is None]
                replacement_ev=dict(status='INVALID',reason=str(exc))
        return route_votes(vv,fresh,r),dict(original=ev,replacement=replacement_ev,route=r)
    # The original finaliser writes its outputs under ART. Stage in a separate
    # result directory while reading original evidence through explicit wrappers.
    out=repl.R3/'finalization';out.mkdir(exist_ok=True)
    for name in ('build.json','parent.jsonl','candidates.jsonl','controls.jsonl'):
        p=out/name
        if not p.exists():p.write_bytes((m.ART/name).read_bytes())
    if (repl.R3/'STOPPED_AT_70.json').exists():m.dump(out/'STOPPED_AT_70.json',json.loads((repl.R3/'STOPPED_AT_70.json').read_text()))
    def validate_staged(art,pack):return validate(m.ART,pack)
    def collect_staged(art,pack,ctx,logical,seen):return collect(m.ART,pack,ctx,logical,seen)
    # Preflight completion before m.finalize can classify missing runs as INVALID.
    if not (repl.R3/'STOPPED_AT_70.json').exists():
        missing=[f"{r['context']}/{r['reader']}" for r in info['replacements'] if not (repl.R3/'answers'/(r['context']+'.'+r['reader']+'.attempt.json')).exists()]
        if missing:raise ValueError('replacement reads not attempted: '+str(missing))
    m.validate=validate_staged;m.collect=collect_staged
    try:
        return m.finalize(art=out,pack=m.PACK,source=m.SOURCE,review=m.REVIEW/'r3',apply_lead=apply_lead,output=m.ROOT/'artifacts/n1/n1_v1_w1.jsonl')
    finally:m.validate=original_validate;m.collect=original_collect

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dry-run',action='store_true');p.add_argument('--apply-lead',action='store_true');a=p.parse_args()
    print(json.dumps(finalize(a.dry_run,a.apply_lead),ensure_ascii=False,indent=2))
