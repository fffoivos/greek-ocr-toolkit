"""Map terminal production attempt records through sealed keys. No reading."""
import argparse
import json
from pathlib import Path
from lf1 import BASE, rows, jsonl, dump, sha

def map_lines(contexts, ledger, runs):
    result=[]
    for context in contexts:
        attempts=sorted([r for r in ledger if r['context']==context['name']],key=lambda r:r['attempt'])
        last=attempts[-1] if attempts else None
        status=last['status'] if last else 'NOT_RUN'
        verdicts={}
        if status=='VALID':
            verdicts={r['card_id']:r for r in rows(runs/(context['name']+f'.attempt{last["attempt"]}')/'verdicts.jsonl')}
        voids=sum(r['status']=='VOID' for r in attempts)
        terminal='VOID_THREE' if voids==3 else 'VOID_TWICE' if voids==2 else None
        for card_id,row in json.loads(Path(context['key']).read_text())['items'].items():
            if row['control']:continue
            verdict=verdicts.get(card_id)
            result.append(dict(line_id=row['line_id'],split=row['split'],source=row['source'],
                **{'class':row['class']},draw_class=row.get('draw_class'),context=context['name'],
                no_verdict=f'no verdict (reader VOID x{voids})' if not verdict and terminal else None,
                verdict=verdict['verdict'] if verdict else None,
                reasons=verdict.get('reasons',[]) if verdict else [],
                where=verdict.get('where',[]) if verdict else [],
                state='RESOLVED' if verdict else terminal or ('UNRESOLVED' if status=='VALID' else status)))
    return result

def vertical_override(first, reread):
    """Keep both full records; only the vertical re-read supplies the decision."""
    first=first or dict(verdict=None,state='NOT_RUN')
    reread=reread or dict(verdict=None,state='NOT_RUN')
    return dict(first,verdict=reread.get('verdict'),reasons=reread.get('reasons',[]),
                where=reread.get('where',[]),state=reread.get('state','NOT_RUN'),
                no_verdict=reread.get('no_verdict'),first_verdict=first,reread_verdict=reread)


def merge_vertical(first_rows, reread_rows):
    rereads={r['line_id']:r for r in reread_rows}
    result=[];vertical=[]
    for first in first_rows:
        if first.get('draw_class')=='vertical_turned':
            combined=vertical_override(first,rereads.get(first['line_id']))
            vertical.append(combined);result.append(combined)
        else:result.append(first)
    return result,vertical


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--contexts',type=Path,default=BASE/'candidate_contexts.json')
    p.add_argument('--ledger',type=Path,default=BASE/'ledger.json')
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--vertical-contexts',type=Path,nargs='+',default=[])
    p.add_argument('--vertical-output',type=Path,default=BASE/'prod/vertical_reread_verdicts.jsonl')
    a=p.parse_args()
    result=map_lines(json.loads(a.contexts.read_text()),json.loads(a.ledger.read_text()),BASE/'runs')
    if a.vertical_contexts:
        contexts=[c for p in a.vertical_contexts for c in json.loads(p.read_text())]
        reread=map_lines(contexts,json.loads(a.ledger.read_text()),BASE/'runs')
        result,vertical=merge_vertical(result,reread)
        jsonl(a.vertical_output,vertical)
    jsonl(a.output,result)
    dump(str(a.output)+'.receipt.json',dict(rows=len(result),inputs={str(f):sha(f) for f in (a.contexts,a.ledger,*a.vertical_contexts)},output_sha256=sha(a.output)))

if __name__=='__main__':main()
