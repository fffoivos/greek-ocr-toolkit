"""Bounded execution of the unchanged RU3T finalizer; stop before label creation."""
import os
import sys
from pathlib import Path

ROOT = Path(os.environ['RU3TF1_ROOT']).resolve()
TARGET = ROOT / 'scripts/secondary/ru3t.py'
STOP = next(i for i, s in enumerate(TARGET.read_text().splitlines(), 1) if s.startswith('    partial=(art/'))

def guard(event, args):
    if event in {'socket.connect', 'socket.connect_ex', 'socket.getaddrinfo', 'socket.bind'}:
        raise RuntimeError('RU3TF1 network OFF')
    if event == 'open':
        path, mode, flags = args
        if isinstance(path, (str, bytes, os.PathLike)) and ((isinstance(mode, str) and any(c in mode for c in 'wax+')) or (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))):
            p = Path(os.fsdecode(path)).resolve()
            if '.git' in p.parts or p.name.startswith('ru1_v3_train') or p == ROOT/'docs/labelfix/lqb/versions.json':
                raise RuntimeError('RU3TF1 forbidden write: '+str(p))
sys.addaudithook(guard)

def finish(frame):
    from collections import Counter
    import json
    m = sys.modules['__main__']
    # ru3t_delivery imports ru3t by name: use the already executing module.
    sys.modules['ru3t'] = m
    v = frame.f_locals
    art = v['art']; decisions = v['decisions']; contexts = v['contexts']
    m.jsonl(art/'decisions.jsonl', decisions)
    m.jsonl(art/'decisions_merged.jsonl', v['inherited']+decisions)
    m.jsonl(art/'fresh_r3_positions.jsonl', v['fresh'])
    bad = {k:c for k,c in contexts.items() if c['status'] != 'VALID'}
    failed_positions = []
    for identity, status in bad.items():
        ctx, reader = identity.split('/')
        key = json.loads((art/f'keys/{m.reader_stem(ctx,reader)}.json').read_text())
        for iid, meta in key['items'].items():
            if meta['control']: continue
            for slot in meta['slots']:
                k = meta['row_id'], slot['offset']
                if k in v['expected']:
                    failed_positions.append(dict(context=identity,row_id=k[0],offset=k[1],item_id=iid,status=status['status'],action='fresh-r3 re-read; fresh ids and independent context required'))
    m.jsonl(art/'r3_context_positions.jsonl', failed_positions)
    summary = dict(schema='RU3TF1-v1',status='COMBINED',contexts=contexts,valid_contexts=sum(c['status']=='VALID' for c in contexts.values()),invalid_contexts=bad,counts=dict(Counter(d['decision'] for d in decisions)),lead_review_reasons=dict(Counter(d['reason'] for d in decisions if d['decision']=='lead_review')),positions=len(decisions),fresh_r3_positions=len(v['fresh']),r3_context_positions=len(failed_positions),coverage=v['coverages'],evidence=v['evidence'],scanner_sha256=m.SCANNER_SHA,network=False,new_readings=False,browser=False,computer_use=False,git_writes=False,labels_written=False,registry_written=False,lqb_scored=False,stop_before='merge_labels and ru1_v3_train creation',execution='unchanged scripts/secondary/ru3t_finalize.sh with line stop hook',hook_sha256=m.sha(__file__))
    m.dump(art/'phase1/combine.json',summary)
    print(json.dumps({k:summary[k] for k in ['valid_contexts','invalid_contexts','counts','lead_review_reasons','fresh_r3_positions']},ensure_ascii=False),flush=True)
    from ru3t_delivery import build_sheets, OUT
    summary['sheets'] = build_sheets()
    index=json.loads((OUT/'sheets_index.json').read_text())['items']
    template=list(m.rows(art/'lead_review_template.jsonl'))
    assert len(index)==len(template)
    assert [{k:c[k] for k in ['cell','row_id','offset','set']} for c in index] == [{k:c[k] for k in ['cell','row_id','offset','set']} for c in template]
    for kind in ('review','audit'):
        m.jsonl(OUT/f'{kind}_template.jsonl',[c for c in template if c['set']==kind])
    m.jsonl(OUT/'lead_review_template.jsonl',template)
    m.jsonl(OUT/'fresh_r3_positions.jsonl',v['fresh'])
    m.jsonl(OUT/'r3_context_positions.jsonl',failed_positions)
    summary['review_sheets']=len({c['sheet'] for c in index if c['set']=='review'})
    summary['audit_sheets']=len({c['sheet'] for c in index if c['set']=='audit'})
    assert summary['sheets']['audit_cells']==60
    assert Counter(c['decision'] for c in index if c['set']=='audit')==dict(edit_hard=40,keep_soft=20)
    summary['status']='READY'
    summary['outputs']={str(p):m.sha(p) for p in [art/'decisions.jsonl',art/'decisions_merged.jsonl',art/'fresh_r3_positions.jsonl',art/'r3_context_positions.jsonl',*OUT.rglob('*')] if p.is_file()}
    m.dump(art/'RU3TF1_RECEIPT.json',summary)
    m.dump(OUT/'RU3TF1_RECEIPT.json',summary)
    counts=summary['counts']; reasons=', '.join(f'{k} {n}' for k,n in sorted(summary['lead_review_reasons'].items()))
    line=f"RU3TF1 READY: contexts valid {summary['valid_contexts']}/38 (void {','.join(bad) or 'none'}); edit_hard {counts.get('edit_hard',0)}, keep_soft {counts.get('keep_soft',0)}, lead_review {counts.get('lead_review',0)} ({reasons}); review cells {summary['sheets']['review_cells']} on {summary['review_sheets']} sheets; audit cells 60"
    (art/'phase1/ready.txt').write_text(line+'\n')
    print(line,flush=True)
    raise SystemExit(0)

def trace(frame,event,arg):
    if frame.f_code.co_filename == str(TARGET) and frame.f_code.co_name == 'finalize':
        if event == 'line' and frame.f_lineno == STOP:
            sys.settrace(None)
            finish(frame)
        return trace
    return None
sys.settrace(trace)
