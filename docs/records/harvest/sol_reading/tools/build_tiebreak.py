#!/usr/bin/env python3
"""Build a blind r3 pack only from present, non-VOID r1/r2 disagreements."""
import argparse,copy,hashlib,math,random,re,shutil
from b2_common import *
from scan_packs import scan

def submask(text,google,disputed):
    calls=re.findall(r'[ъь]\b',google);mapping={str(i+1):s for i,s in enumerate(sorted(disputed,key=int))};reverse={s:n for n,s in mapping.items()}
    def replace(m):
        slot=m[1]
        return '⟦'+reverse[slot]+'⟧' if slot in reverse else calls[int(slot)-1]
    if len(calls)!=len(re.findall(r'⟦\d+⟧',text)):raise ValueError('Google/mask slot count differs')
    return re.sub(r'⟦(\d+)⟧',replace,text),mapping

def build(bed):
    left,s1=load_run(bed,'r1');right,s2=load_run(bed,'r2');items=source_items(bed)
    if s1!='OK' or s2!='OK':return dict(bed=bed,status='missing or excluded input',r1=s1,r2=s2)
    expected=set(items)
    if set(left)!=expected or set(right)!=expected:return dict(bed=bed,status='incomplete primaries',missing_r1=sorted(expected-set(left)),missing_r2=sorted(expected-set(right)))
    disputes=disagreements(bed,left,right,items)
    if not disputes:return dict(bed=bed,status='zero disagreements; no pack',disagreements=0)
    dest=PACK_ROOT/bed/'r3'
    if dest.exists():return dict(bed=bed,status='existing r3 retained; refusing rebuild',path=str(dest))
    key=read_json(ROOT/f'keys/{bed}.json');public=index(rows(PACK_ROOT/bed/'r1'/itemfile(bed)),bed)
    records=[(opaque,meta) for opaque,meta in key['items'].items() if not meta['control'] and meta['source_id'] in disputes]
    rng=random.Random(f'sol-reading:{bed}:r3');controls=[(o,m) for o,m in key['items'].items() if m['control']];rng.shuffle(controls)
    count=math.ceil(len(records)*.1)
    if count>len(controls):raise ValueError('insufficient distinct controls')
    records+=controls[:max(1,count)];rng.shuffle(records);out=[];private={};dest.mkdir(parents=True)
    yerkey=read_json(C1/'yer_adjudication/key.json') if bed=='yer' else None
    for n,(old,meta) in enumerate(records):
        row=copy.deepcopy(public[old]);m=copy.deepcopy(meta);iid='k'+hashlib.sha256(f'sol-reading:{bed}:r3:{n}:{old}'.encode()).hexdigest()[:10];row[idfield(bed)]=iid
        if bed=='yer' and not m['control']:
            row['masked_text'],m['slot_to_source']=submask(row['masked_text'],yerkey[m['source_id']]['google_text'],disputes[m['source_id']]);row['slots']=len(m['slot_to_source'])
        if bed=='owner39':
            letters=sorted(row['options']);permuted=letters.copy();rng.shuffle(permuted);oldopts=row['options'];oldmap=m['option_to_source'];m['option_to_source']={a:oldmap[b] for a,b in zip(letters,permuted)};row['options']={a:oldopts[b] for a,b in zip(letters,permuted)}
            if m['control'] and m['expected']['choice']!='literal':m['expected']['choice']=letters[permuted.index(m['expected']['choice'])]
        for f in ('crop','word_image','line_image'):
            if f in row:
                target=dest/row[f];target.parent.mkdir(parents=True,exist_ok=True)
                if not target.exists():shutil.copyfile(PACK_ROOT/bed/'r1'/row[f],target)
        out.append(row);private[iid]=m
    jsonl(dest/itemfile(bed),out)
    if bed=='owner39':
        for name in ('README.md','answer_schema.json'):shutil.copyfile(PACK_ROOT/bed/'r1'/name,dest/name)
    dump(ROOT/f'keys/{bed}_r3.json',dict(bed=bed,seed=f'sol-reading:{bed}:r3',readers={'r3':[r[idfield(bed)] for r in out]},items=private,disagreements=disputes))
    result=scan(dest,bed);dump(ROOT/f'validation/{bed}_r3.pack_scan.json',result)
    if not result['ok']:raise ValueError(str(result['violations']))
    return dict(bed=bed,status='built',disputed_items=len(disputes),controls=count,items=len(out),scan_ok=True,path=str(dest))
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('bed',choices=FIELDS);a=p.parse_args();print(json.dumps(build(a.bed),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
