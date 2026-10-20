"""Shared SR-B2 unit definitions. Missing is never an answer."""
import copy,json
from common import *
from owner39_validate import normalize
HEADS=('breathing','accent','diaeresis','subscript')
BSB=('letters','marks','crop_ok')
def read_json(p):return json.loads(Path(p).read_text())
def source_items(bed):
    p=EFF/'packs'/bed/('E0a' if bed=='owner39' else 'E1')/'r1'/itemfile(bed)
    return {r[idfield(bed)]:r for r in rows(p)}
def index(data,bed):
    out={}
    for row in data:
        iid=row[idfield(bed)]
        if iid in out:raise ValueError('duplicate id: '+iid)
        out[iid]=row
    return out
def load_run(bed,reader):
    d=ROOT/'answers'/bed;p=d/f'{reader}.mapped.jsonl';scan=d/f'{reader}.scan.json'
    if not p.exists():return {},'MISSING'
    if reader=='S2':
        receipt=d/'S2.unresolved.json'
        if not receipt.exists():return {},'MISSING resolution receipt'
        for run in read_json(receipt).get('used_readers',[]):
            _,status=load_run(bed,run)
            if status!='OK':return {},'VOID dependency '+run if status.startswith('VOID') else 'MISSING dependency '+run
        return index(rows(p),bed),'OK'
    if not scan.exists():return {},'MISSING scan'
    if read_json(scan).get('ok') is not True:return {},'VOID'
    return index(rows(p),bed),'OK'
def owner_tuple(row,item):
    n=normalize(row,item)
    return (n['base'],*(n['heads'][h] for h in HEADS))
def units(row,bed,item=None):
    if bed=='bsb':return {f:row[f] for f in BSB}
    if bed=='yer':return row['slots']
    return {'anchor':owner_tuple(row,item)}
def disagreements(bed,left,right,items):
    out={}
    for iid in sorted(set(left)&set(right)):
        a=units(left[iid],bed,items.get(iid));b=units(right[iid],bed,items.get(iid))
        different=[u for u in a if u in b and a[u]!=b[u]]
        if different:out[iid]=different
    return out

def majority(a,b,c=None):
    if a==b:return a
    return c if c is not None and (c==a or c==b) else None

def resolve_records(bed,left,right,third,items):
    out=[];unresolved=[]
    for iid in sorted(set(left)|set(right)):
        a=left.get(iid);b=right.get(iid);c=third.get(iid)
        if a is None or b is None:
            unresolved.append({'id':iid,'unit':'missing_primary','missing':[r for r,v in [('r1',a),('r2',b)] if v is None]})
        template=copy.deepcopy(a or b);u1=units(a,bed,items.get(iid)) if a else {};u2=units(b,bed,items.get(iid)) if b else {};u3=units(c,bed,items.get(iid)) if c else {}
        if bed=='owner39':
            value=majority(u1.get('anchor'),u2.get('anchor'),u3.get('anchor')) if a and b else None
            winner=next((r for r in (a,b,c) if r and units(r,bed,items[iid])['anchor']==value),None)
            if winner:template=copy.deepcopy(winner)
            else:
                template.update(choice='unreadable',anchor_heads=dict.fromkeys(HEADS,'unknown'),letter_heads=[],readability='unreadable',ownership_ok=None,confidence='low',note='S2 unresolved');template.pop('transcription',None)
                unresolved.append(dict(id=iid,unit='anchor',r1=u1.get('anchor'),r2=u2.get('anchor'),r3=u3.get('anchor')))
        else:
            keys=BSB if bed=='bsb' else sorted(set(u1)|set(u2),key=int)
            for unit in keys:
                value=majority(u1.get(unit),u2.get(unit),u3.get(unit)) if unit in u1 and unit in u2 else None
                if value is None:
                    value='u';unresolved.append(dict(id=iid,unit=unit,r1=u1.get(unit),r2=u2.get(unit),r3=u3.get(unit)))
                if bed=='bsb':template[unit]=value
                else:template['slots'][unit]=value;template.setdefault('confidence',{})[unit]='low'
        out.append(template)
    return out,unresolved

def change_accounting(left,right,truth):
    common=sorted(set(left)&set(right)&set(truth));counts=dict(changed_to_correct=0,changed_to_wrong=0,changed_between_wrong=0)
    changed=[]
    for unit in common:
        a,b,t=left[unit],right[unit],truth[unit]
        if a==b:continue
        kind='changed_to_correct' if b==t else 'changed_to_wrong' if a==t else 'changed_between_wrong'
        counts[kind]+=1;changed.append(dict(unit=unit,before=a,after=b,truth=t,kind=kind))
    net=counts['changed_to_correct']-counts['changed_to_wrong']
    return dict(**counts,compared=len(common),changed=changed,net_correct=net,net_accuracy_change=net/len(common) if common else None)
