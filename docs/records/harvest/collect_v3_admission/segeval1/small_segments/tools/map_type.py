"""Validate blind answers and score only the lead-verified controls."""
import json,sys
from ss4_common import *
VALUES={
 'type':set('word caps_display abbrev_label marker roman_lower digits_letters number punctuation noise handwriting foreign_script figure_ornament watermark show_through cut_fragment multi_line part_of_line other'.split()),
 'text':set('match minor wrong not_text unreadable'.split()),
 'crop':set('ok clipped extra na'.split()),'rotated':{'yes','no'}}
FIELDS={'card_id','type','text','crop','rotated','detail'}
def validate(answers,order,items,ctx):
    if len(answers)!=len(order): raise ValueError('missing or extra card')
    mapped=[]; results=[]
    for a,cid in zip(answers,order):
        if set(a)!=FIELDS or a['card_id']!=cid: raise ValueError('answer fields/card order mismatch')
        if not isinstance(a['detail'],str): raise ValueError('detail must be a string')
        for k,vs in VALUES.items():
            if not isinstance(a[k],str) or a[k] not in vs: raise ValueError('out-of-list '+k)
        m=items[cid]
        mapped.append(dict(line_id=m['line_id'],ctx=ctx,control=m['control'],**a))
        if m['control']:
            e=m['expected']; errors=[k for k in ('type','text','crop','rotated') if a[k] not in ({e['type'],*e.get('accept',[])} if k=='type' else {e[k]} if k=='rotated' else set(e[k]))]
            results.append(dict(card_id=cid,line_id=m['line_id'],ok=not errors,errors=errors,expected=e))
    n=sum(not r['ok'] for r in results)
    return mapped,dict(ctx=ctx,items=len(order),bed=len(order)-len(results),controls=len(results),control_errors=n,control_results=results,flagged=n>1,valid=True)
def main(ctx,layout="type2"):
    c,items=assignment(ctx,layout); dest=SS/'q3/answers'
    mapped,check=validate(rows(dest/f'{ctx}.jsonl'),c['card_ids'],items,ctx)
    jsonl(dest/f'{ctx}.mapped.jsonl',mapped); dump(dest/f'{ctx}.check.json',check)
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('ctx'); parser.add_argument('--layout',choices=['type','type2'],default='type2'); args=parser.parse_args()
    try: main(args.ctx,args.layout)
    except Exception as e: print(str(e),file=sys.stderr); sys.exit(1)
