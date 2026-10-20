"""LF2d: same-scope/source replacements and seal02 final-list emission."""
import argparse
import collections
from pathlib import Path
from lf1 import dump, rows, jsonl, sha, replace_flagged
from prod_map import vertical_override
from prod_adapter import DRAW, DRAW_POLICY, partition, draw_counts


def finalize(candidates, verdict_rows, vertical_rows=None):
    verdicts={v['line_id']:v for v in verdict_rows}
    vertical={v['line_id']:v for v in (vertical_rows or [])}
    for row in candidates:
        if row.get('draw_class',row['class'])!='vertical_turned':continue
        rid=row.get('line_id',row['row_id'])
        v=vertical.get(rid,verdicts.get(rid,{}))
        # A first-read OK cannot stand in for a missing vertical re-read.
        first=v.get('first_verdict',verdicts.get(rid))
        verdicts[rid]=dict(vertical_override(first,v.get('reread_verdict')),line_id=rid)
    final=[];replacements=[];summary=[];blocked=[]
    for scope,group in partition(candidates).items():
        side,cl=scope.split(':')[:2];sub=group[0]['subgroup']
        selected=[r for r in group if r['in_quota']]
        reserve=sorted((r for r in group if not r['in_quota']),key=lambda r:r['overdraw_order'])
        used={r['line_id'] for r in reserve if verdicts.get(r['line_id'],{}).get('verdict')!='OK'}
        blocked.extend(dict(line_id=r['line_id'],verdict=verdicts.get(r['line_id'])) for r in reserve if r['line_id'] in used)
        counters=collections.defaultdict(collections.Counter)
        # Each source consumes its eligible reserves in flagged scope-rank order.
        for old in sorted(selected,key=lambda r:r['scope_rank']):
            v=verdicts.get(old['line_id'],dict(verdict=None,state='UNRESOLVED'))
            count=counters[old['source']]
            if v.get('verdict')=='OK':
                count['in_quota_OK']+=1;final.append(old);continue
            count['flagged']+=1
            count['no_verdict' if v.get('verdict') is None else 'verdict_flags']+=1
            if v.get('state') in ('VOID_TWICE','VOID_THREE'):count[v['state']]+=1
            elif v.get('verdict') is None:count['unresolved']+=1
            rec=replace_flagged([old['line_id']],selected,reserve,used)[0]
            rec.update(quota_scope=scope,split=side,draw_class=cl,subgroup=sub,flag_reason=dict(
                verdict=v.get('verdict'),reasons=v.get('reasons',[]),state=v.get('state'),where=v.get('where',[]),no_verdict=v.get('no_verdict')))
            count[rec['status']]+=1
            if rec['replacement_id'] is not None:
                used.add(rec['replacement_id'])
                replacement=next(r for r in reserve if r['line_id']==rec['replacement_id'])
                rec['replacement_source']=replacement['source']
                rec['overdraw_order']=replacement['overdraw_order'];final.append(replacement)
            replacements.append(rec)
        for source,count in counters.items():
            summary.append(dict(quota_scope=scope,split=side,**{'class':cl},subgroup=sub,source=source,
                **{k:count[k] for k in ('in_quota_OK','flagged','REPLACED','UNFILLED','unresolved','VOID_TWICE','VOID_THREE','no_verdict','verdict_flags')}))
    return final,dict(draw_policy=DRAW_POLICY,scopes=draw_counts(candidates),summary=summary,replacements=replacements,non_OK_reserve_used=blocked,
        vertical_verdicts=[v for v in verdicts.values() if 'reread_verdict' in v])


def seal_rows(final, details, candidates, verdicts_sha256):
    by_id={r.get('line_id',r['row_id']):r for r in candidates}
    replaced={r['replacement_id']:by_id[r['flagged_id']]
              for r in details['replacements'] if r['replacement_id'] is not None}
    result=[]
    for row in final:
        old=replaced.get(row['line_id'])
        result.append(dict(parent_id=row['parent_id'],row_id=row['row_id'],
            split=row['split'],quota_scope=row['quota_scope'],lf1_verdict='OK',
            replaces=None if old is None else dict(parent_id=old['parent_id'],row_id=old['row_id']),
            lf1_receipt_ref=dict(verdicts_sha256=verdicts_sha256,line_id=row['line_id']),mock=False))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidates',type=Path,default=DRAW)
    p.add_argument('--verdicts',type=Path,required=True)
    p.add_argument('--vertical-verdicts',type=Path,help='separate first/re-read vertical records')
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--receipt',type=Path,required=True)
    p.add_argument('--details',type=Path,help='LF1 reasons side receipt (default: RECEIPT.details.json)')
    p.add_argument('--bindings',type=Path,help='three-file SHA handoff (default: RECEIPT.bindings.json)')
    a=p.parse_args()
    candidates=rows(a.candidates)
    final,details=finalize(candidates,rows(a.verdicts),rows(a.vertical_verdicts) if a.vertical_verdicts else None)
    verdicts_sha256=sha(a.verdicts);candidates_sha256=sha(a.candidates)
    jsonl(a.output,seal_rows(final,details,candidates,verdicts_sha256))
    counts={k:sum(r[k] for r in details['summary']) for k in ('flagged','REPLACED','UNFILLED')}
    dump(a.receipt,dict(status='FINALIZED',mock=False,final_list_sha256=sha(a.output),
        verdicts_sha256=verdicts_sha256,candidates_sha256=candidates_sha256,counts=counts))
    dump(a.details or Path(str(a.receipt)+'.details.json'),dict(details,
        candidates_sha256=candidates_sha256,verdicts_sha256=verdicts_sha256,final_list_sha256=sha(a.output)))
    dump(a.bindings or Path(str(a.receipt)+'.bindings.json'),
        {role:dict(path=str(path.resolve()),sha256=sha(path)) for role,path in
         (('final_list',a.output),('final_receipt',a.receipt),('verdicts',a.verdicts))})

if __name__=='__main__':main()
