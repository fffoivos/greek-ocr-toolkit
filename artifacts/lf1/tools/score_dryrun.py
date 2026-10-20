"""Score frozen LF1 owner ratings. Never reads images or changes labels."""
import argparse
import collections
import json
from lf1 import BASE, rows, dump, sha

def score(contexts, ledger, truth):
    names={c['name'] for c in contexts}
    ledger=[r for r in ledger if r['context'] in names]
    by_line={r['line_id']:r for r in truth}; predictions={}; per_class=collections.defaultdict(collections.Counter)
    terminal={}; tokens=collections.Counter(); weekly=0.; weekly_missing=False; card_reads=0
    for record in ledger:
        terminal[record['context']]=record
        if record.get('run'):
            card_reads+=record['cards']
            usage=record['run'].get('usage') or {}
            for k,v in usage.items():
                if isinstance(v,(int,float)):tokens[k]+=v
        before=(record.get('before') or {}).get('weekly_used');after=(record.get('after') or {}).get('weekly_used')
        if before is not None and after is not None and after>=before:weekly+=after-before
        elif record.get('run'):weekly_missing=True
    for context in contexts:
        record=terminal.get(context['name'])
        if not record or record['status']!='VALID':continue
        key=json.loads(open(context['key']).read())['items']
        path=BASE/'runs'/(context['name']+f'.attempt{record["attempt"]}')/'verdicts.jsonl'
        for v in rows(path):
            k=key[v['card_id']]
            if k['control']:continue
            predictions[k['line_id']]=v
    confusion=collections.defaultdict(collections.Counter);agreement=0;crop_agreement=0;crop_scored=0
    for line,t in by_line.items():
        prediction=predictions.get(line);expected=t['expected']
        state=('OK' if prediction['verdict']=='OK' else 'not OK') if prediction else 'UNRESOLVED'
        confusion[expected][state]+=1
        agreement+=state==expected
        if prediction:
            crop_state='not OK' if prediction['verdict']=='CROP_VIOLATES' else 'OK'
            crop_agreement+=crop_state==expected;crop_scored+=1
        # Scheme is overlapping; a line contributes to every available quota facet.
        for cls in t.get('quota_classes') or ['UNASSIGNED']:
            per_class[cls]['selected']+=1
            per_class[cls]['mapped']+=prediction is not None
            per_class[cls]['flagged']+=bool(prediction and prediction['verdict']!='OK')
            per_class[cls]['unresolved']+=prediction is None
    return dict(selected=len(truth),mapped=len(predictions),unresolved=len(truth)-len(predictions),
        agreement=dict(count=agreement,denominator=len(truth),fraction=agreement/len(truth) if truth else None),
        crop_only_agreement=dict(count=crop_agreement,denominator=crop_scored,
            note='Owner marks judge segmentation; TEXT_DIFFERS alone is crop OK in this separate diagnostic.'),
        confusion={k:dict(v) for k,v in confusion.items()},
        per_class={c:dict(v,flag_rate=v['flagged']/v['mapped'] if v['mapped'] else None) for c,v in sorted(per_class.items())},
        tokens=dict(tokens),card_reads=card_reads,
        tokens_per_100_cards={k:100*v/card_reads for k,v in tokens.items()} if card_reads else None,
        weekly_pp_observed_sum=None if weekly_missing else weekly if card_reads else None,
        weekly_pp_per_100_cards=100*weekly/card_reads if card_reads and not weekly_missing else None,
        weekly_caveat='Shared integer-resolution meter; summed per-context deltas overlap under concurrency and include other sessions. Not attributable consumption. Use --jobs 1 for an interpretable dry-run interval.',
        context_statuses={k:v['status'] for k,v in terminal.items()})

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',default=str(BASE/'dryrun_score.json'));a=p.parse_args()
    contexts=json.loads((BASE/'contexts.json').read_text())
    ledger=json.loads((BASE/'ledger.json').read_text()) if (BASE/'ledger.json').exists() else []
    truth=rows(BASE/'keys/owner_rating_truth.jsonl')
    result=score(contexts,ledger,truth)
    result['inputs']={str(p):sha(p) for p in (BASE/'contexts.json',BASE/'keys/owner_rating_truth.jsonl')}
    if (BASE/'ledger.json').exists():result['inputs'][str(BASE/'ledger.json')]=sha(BASE/'ledger.json')
    result['status']='MEASURED' if ledger else 'NOT_RUN'
    dump(a.output,result);print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
