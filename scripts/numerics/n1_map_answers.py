"""Decode private option maps; invalid/missing/duplicate answers stay unresolved."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from greekocr.numerics.combine_v2 import control_matches


ROOTS = ('n1', 'n1cal', 'n1cal2', 'n1t', 'n1t2', 'n1t3', 'n1e')


def output_stem(base, root, context, reader):
    """One canonical answer namespace shared by launcher and mapper CLI."""
    import re
    if root not in ROOTS or reader not in ('r1', 'r2', 'r3'):
        raise ValueError('invalid root or reader')
    pattern = r'cal[0-9]{2}' if root in ('n1cal', 'n1cal2') else r'ctx[0-9]{2}'
    if not re.fullmatch(pattern, context):
        raise ValueError('root/context mismatch')
    return Path(base)/'answers'/root/(context+'.'+reader)


def map_answers(key, answers):
    grouped={}
    for row in answers: grouped.setdefault(row.get('item_id'),[]).append(row)
    decoded=[]; errors=0; controls=0
    if len(key['readers']) != 1: raise ValueError('one reader assignment required')
    expected=next(iter(key['readers'].values()))
    if set(key['items']) != set(expected): raise ValueError('inconsistent key')
    for item_id in expected:
        item=key['items'][item_id]; found=grouped.get(item_id,[])
        answer=found[0] if len(found)==1 else {}
        letter=answer.get('answer'); meaning=item['option_map'].get(letter) if isinstance(letter,str) else None
        status='missing' if not found else 'duplicate' if len(found)>1 else 'invalid_letter' if meaning is None else 'unreadable' if meaning=='unreadable' else 'ok'
        control=item.get('control_truth')
        if control is not None:
            controls+=1; errors+=not control_matches(control, meaning) or status in {'missing','duplicate','invalid_letter'}
        decoded.append(dict(item_id=item_id,slot_id=item['slot_id'],meaning=meaning,status=status,
            geometry=item['geometry'],measurements=item.get('measurements'),geometry_record_ref=item.get('geometry_record_ref'),
            google_glyph=item['google_glyph'],control=control is not None,confidence=answer.get('confidence'),note=answer.get('note','')))
    void=errors>1
    for row in decoded: row['context_status']='VOID' if void else 'VALID'
    return dict(context_status='VOID' if void else 'VALID',control_errors=errors,controls=controls,
                unexpected_ids=sorted(str(i) for i in set(grouped)-set(expected)),slots=decoded)


def main():
    p=argparse.ArgumentParser();p.add_argument('key',type=Path);p.add_argument('answers',type=Path);p.add_argument('--root',required=True,choices=ROOTS);p.add_argument('--context',required=True);p.add_argument('--reader',default='r1');p.add_argument('--output-base',type=Path,default=Path(__file__).resolve().parents[2]/'artifacts/n1');a=p.parse_args()
    result=map_answers(json.loads(a.key.read_text()),[json.loads(s) for s in a.answers.read_text().splitlines() if s.strip()])
    output=Path(str(output_stem(a.output_base,a.root,a.context,a.reader))+'.mapped.json')
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x') as f: json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
if __name__=='__main__':main()
