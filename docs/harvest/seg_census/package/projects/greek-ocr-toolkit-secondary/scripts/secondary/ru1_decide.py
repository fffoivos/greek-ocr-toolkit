"""Combine independent RU1 r1 plus r2 (ctx01-03) / r3 (ctx04) contexts; proposals only, never writes labels.
Missing r2 evidence is explicitly lead_review. Context identity includes reader.
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'reading'))
from common import ROOT, rows, dump, jsonl
from ru1_map_answers import score_controls


def accepted_contexts():
    """The lead's accepted assignments; ctx04/r2 is permanently excluded."""
    return [(f'ctx{n:02}', reader, f'ctx{n:02}' + ('.'+reader if reader != 'r1' else ''))
            for second in [False, True] for n in range(1, 5)
            for reader in [('r3' if n == 4 else 'r2') if second else 'r1']]


def decide(position, reads):
    if position['google']!='ь' or position['kind']!='final' or position.get('control'):
        return None
    base='lead_review';reason='missing_independent_reads'
    calls=[r['call'] for r in reads]
    second = 'r3' if any(r['context'].split('/')[0] == 'ctx04' for r in reads) else 'r2'
    independent=len(reads)==2 and {r['reader'] for r in reads}=={'r1',second} and len({r['context'] for r in reads})==2
    if independent:
        if any(c in {'u','other'} for c in calls):reason='uncertain_read'
        elif calls[0]!=calls[1]:reason='reader_disagreement'
        elif calls==['ъ','ъ']:
            if any(r['gate_status']=='VALID' for r in reads):base='edit_hard';reason='two_hard_at_least_one_valid'
            else:reason='only_void_hard_reads'
        elif calls==['ь','ь']:base='keep_soft';reason='two_soft'
        else:raise ValueError('invalid calls')
    prior_disagreement=(base=='edit_hard' and position['prior']=='ь_only') or (base=='keep_soft' and position['prior']=='ъ_only')
    return dict(row_id=position['row_id'],source_id=position['source_id'],offset=position['offset'],
                google=position['google'],kind=position['kind'],prior=position['prior'],
                reads={reader:next((r for r in reads if r['reader']==reader),None) for reader in ['r1',second]},
                decision='lead_review' if prior_disagreement else base, vote_decision=base,
                prior_disagreement=prior_disagreement,reason='prior_disagreement' if prior_disagreement else reason)


def combine(art=ROOT):
    positions={};votes={};inputs=[];gates={}
    for ctx, reader, stem in accepted_contexts():
        path=art/f'answers/{stem}.mapped.jsonl'
        if not path.exists():
            if reader=='r1':raise ValueError('missing r1 mapped answers')
            continue
        gate=json.loads((art/f'answers/{stem}.controls.json').read_text())
        scan=json.loads((art/f'answers/{stem}.scan.json').read_text())
        if scan.get('ok') is not True or scan.get('violations') or gate['status'] not in {'VALID','VOID'}:raise ValueError('unclean scan or unknown gate')
        records=rows(path)
        rescored=score_controls(records,ctx)
        if gate['status']!=rescored['status']:raise ValueError('stale control gate; remap answers')
        gates[stem]={k:rescored[k] for k in ['wrong_signs','abstentions','excluded','correct','control_slots','status']}
        inputs.append(stem)
        seen=set()
        for p in records:
            if p['control']:continue
            k=(p['row_id'],p['offset'])
            if k in seen:raise ValueError('duplicate position in context')
            seen.add(k)
            if k in positions and any(p[f]!=positions[k][f] for f in ['source_id','google','kind','prior']):raise ValueError('position metadata differs')
            positions[k]=p
            if any(v['reader']==reader for v in votes.get(k,[])):raise ValueError('duplicate reader position')
            if p['call'] not in {'ъ','ь','u','other'} or p['context_void']!=(gate['status']=='VOID'):raise ValueError('invalid call/gate mismatch')
            votes.setdefault(k,[]).append(dict(reader=reader,context=f'{ctx}/{reader}',pack_context=ctx,
                gate_status=gate['status'],call=p['call'],item_id=p['item_id'],confidence=p['confidence']))
    out=[d for k,p in sorted(positions.items()) if (d:=decide(p,votes[k])) is not None]
    disagreements=[dict(row_id=d['row_id'],offset=d['offset'],prior=d['prior'],vote_decision=d['vote_decision']) for d in out if d['prior_disagreement']]
    summary=dict(status='complete' if len(inputs)==8 else 'pending_r2',input_contexts=inputs,positions=len(out),
        counts=dict(Counter(d['decision'] for d in out)),
        lead_review_reasons=dict(Counter(d['reason'] for d in out if d['decision']=='lead_review')),
        reader_contexts=gates,prior_disagreement_count=len(disagreements),prior_disagreements=disagreements)
    jsonl(art/'decisions.jsonl',out);dump(art/'decisions.summary.json',summary)
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--art',type=Path,default=ROOT);a=p.parse_args();print(json.dumps(combine(a.art),ensure_ascii=False,indent=2))
