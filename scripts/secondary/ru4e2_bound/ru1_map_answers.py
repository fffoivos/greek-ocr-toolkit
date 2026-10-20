"""RU1 adaptation of Sol map_answers.py. Control failures void edits context-wide.
Outputs are proposals for lead review only; this program never writes labels.
"""
import argparse
import json
from pathlib import Path
from common import ROOT, PACK_ROOT, rows, dump, jsonl


DISPUTED_CONTROL = ('ia_russian--d558bd3e803e7865--s003-l0032', 2)
SCORING_VERSION = 'RU1S-wrong-signs-v1'


def score_controls(records, context=None):
    """Gate on wrong signs only; retain excluded/abstaining observations."""
    checks = []
    for r in records:
        if not r['control'] or r.get('control_truth') is None:
            continue
        excluded = (r['source_id'], r['slot']) == DISPUTED_CONTROL or (r['row_id'], r['slot']) == DISPUTED_CONTROL
        call = r['call']; truth = r['control_truth']
        outcome = 'excluded' if excluded else 'abstention' if call == 'u' else 'correct' if call == truth else 'wrong_sign'
        checks.append(dict(item_id=r['item_id'], row_id=r['row_id'], source_id=r['source_id'],
                           slot=r['slot'], truth=truth, call=call, passed=call == truth,
                           excluded=excluded, outcome=outcome))
    wrong = sum(c['outcome'] == 'wrong_sign' for c in checks)
    return dict(context=context, scoring_version=SCORING_VERSION,
                status='VOID' if wrong > 1 else 'VALID', wrong_signs=wrong,
                abstentions=sum(c['outcome'] == 'abstention' for c in checks),
                correct=sum(c['outcome'] == 'correct' for c in checks),
                excluded=sum(c['excluded'] for c in checks),
                control_slots=sum(not c['excluded'] for c in checks), controls=checks,
                # Compatibility only: pre-RU1S raw mismatches, NOT the gate count.
                control_errors=sum(not c['passed'] for c in checks),
                control_errors_semantics='legacy raw mismatches including abstentions and excluded slots; gate uses wrong_signs')


def validate(answer, item):
    required={'item_id','slots','confidence','unmarked_final_hard_signs','pre1918','note'}
    if not isinstance(answer,dict) or not required<=answer.keys():raise ValueError('missing yer fields')
    if answer['item_id']!=item['item_id']:raise ValueError('answer order/id mismatch')
    slots={str(i+1) for i in range(item['slots'])}
    if not isinstance(answer['slots'],dict) or set(answer['slots'])!=slots or any(v not in {'ъ','ь','other','u'} for v in answer['slots'].values()):raise ValueError('invalid slot coverage/call')
    if not isinstance(answer['confidence'],dict) or set(answer['confidence'])!=slots or any(v not in {'high','low'} for v in answer['confidence'].values()):raise ValueError('invalid confidence')
    if not isinstance(answer['unmarked_final_hard_signs'],list) or any(not isinstance(v,str) for v in answer['unmarked_final_hard_signs']):raise ValueError('invalid unmarked list')
    if answer['pre1918'] not in {'yes','no','unclear'} or not isinstance(answer['note'],str):raise ValueError('invalid metadata')


def map_records(answers,key,items,reader="r1"):
    if len(answers)!=len(items):raise ValueError('answer count differs from assignment; missing item')
    if [i['item_id'] for i in items]!=key['readers'][reader]:raise ValueError('pack differs from key order')
    if len({a['item_id'] for a in answers})!=len(answers):raise ValueError('duplicate answer item')
    mapped=[];hard_to_soft=0
    for a,item in zip(answers,items):
        validate(a,item);m=key['items'][item['item_id']]
        if len(m['slots'])!=item['slots']:raise ValueError('private slot coverage differs')
        for n,s in enumerate(m['slots'],1):
            call=a['slots'][str(n)];truth=s.get('control_truth')
            if s['google']=='ъ' and call=='ь':hard_to_soft+=1
            eligible=(not m['control'] and s['google']=='ь' and s['kind']=='final' and call=='ъ')
            # Prior disagreement and u/other calls require an eye; never force a decision.
            disagree=call in {'ъ','ь'} and s['prior'] in {'ъ_only','ь_only'} and call+'_only'!=s['prior']
            mapped.append(dict(item_id=item['item_id'],row_id=m['row_id'],source_id=m['source_id'],
                               slot=n,offset=s['offset'],google=s['google'],kind=s['kind'],prior=s['prior'],
                               call=call,confidence=a['confidence'][str(n)],control=m['control'],
                               control_truth=truth,eligible_proposal=eligible,edit_proposal=None,
                               needs_review=call in {'u','other'} or disagree or a['confidence'][str(n)]=='low',
                               prior_disagreement=disagree,unmarked_final_hard_signs=a['unmarked_final_hard_signs']))
    score=score_controls(mapped,key.get('context'))
    void=score['status']=='VOID'
    for r in mapped:
        r['context_void']=void
        if r.pop('eligible_proposal') and not void:r['edit_proposal']=dict(offset=r['offset'],old='ь',new='ъ')
    score.update(google_hard_read_soft=hard_to_soft, edit_proposals=sum(r['edit_proposal'] is not None for r in mapped))
    return mapped,score


def main():
    p=argparse.ArgumentParser();p.add_argument('context');p.add_argument('answers',type=Path);p.add_argument('--reader',choices=['r1','r2','r3'],default='r1');p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    import re
    if not re.fullmatch('ctx[0-9]{2}',a.context):raise ValueError('invalid context')
    stem=a.context+('.'+a.reader if a.reader!='r1' else '')
    key=json.loads((ROOT/f'keys/{stem}.json').read_text());items=rows(PACK_ROOT/a.context/a.reader/'items.jsonl')
    if a.dry_run:
        if [i['item_id'] for i in items] != key['readers'][a.reader]: raise ValueError('pack differs from key order')
        print(json.dumps(dict(dry_run=True,reader=a.reader,items=len(items),key=str(ROOT/f'keys/{stem}.json'),
            answers=str(a.answers),mapped=str(ROOT/f'answers/{stem}.mapped.jsonl'),controls=str(ROOT/f'answers/{stem}.controls.json'))))
        return 0
    mapped,score=map_records(rows(a.answers),key,items,a.reader)
    jsonl(ROOT/f'answers/{stem}.mapped.jsonl',mapped);dump(ROOT/f'answers/{stem}.controls.json',score)
    print(json.dumps(score,ensure_ascii=False));return 2 if score['status']=='VOID' else 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError,KeyError,TypeError) as e:raise SystemExit(str(e))
