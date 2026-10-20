"""Post-freeze locked enumeration and sep2 pack preparation; NO reader launch."""
import hashlib
import json
import math
from pathlib import Path
import sys
import subprocess
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
from greekocr.numerics.ink_rule import load_rule,decide,sha
from greekocr.numerics.locks import load_locks
from greekocr.numerics.line_complete import enumerate_locked_line
from greekocr.numerics.tokens import tokenize
from greekocr.numerics.slots_geom import locate_slot
from greekocr.numerics.dash import digit_widths,measure_dash
from greekocr.numerics.prune import has_gap_component
from n1_render import SCRATCH,render,cached_crop,clean_png
from n1t_packs import build,typed_controls,rows
from n1r_fit import write,jsonl
SEED='20261017:N1E:marked-ten-percent'
BASE=ROOT/'artifacts/n1';OUT=BASE/'n1e';PACK=SCRATCH/'sol_packs/n1e'


def choose(slots,decisions):
    selected={};remaining=[]
    for s,d in zip(slots,decisions):
        if not s.get('boundary') and s['glyph'] in ('-','.'):
            selected[s['slot_id']]='google-minus-or-dot'
        elif d['class'] in ('raised dot','hyphen','en dash','em dash'):
            selected[s['slot_id']]='frozen-ink-mark'
        elif s['glyph'].strip() or (s['geometry']['geom_status']=='ok' and has_gap_component(s)):
            remaining.append(s)
    audit=sorted(remaining,key=lambda s:hashlib.sha256((SEED+':'+s['slot_id']).encode()).hexdigest())[:math.ceil(len(remaining)*.1)]
    selected.update({s['slot_id']:'marked-ten-percent' for s in audit})
    return selected,len(remaining)


def main():
    # This must be the first data access. Frozen bytes predate every locked feature.
    rulepath=BASE/'n1r/rule.json';rule=load_rule(rulepath)
    if OUT.exists() or PACK.exists():raise ValueError('refusing to overwrite locked build')
    locks=load_locks(BASE)
    locked_path=BASE/'n1_locked_eval_line_ids_alt.txt'
    ids=locked_path.read_text().splitlines()
    if len(ids)!=258 or len(set(ids))!=258 or not set(ids)<=locks.reserved_line_ids:raise ValueError('locked draw mismatch')
    OUT.mkdir()
    run=Path.home()/'Projects/collect-v3-data/run/W1'
    inputs={str(locked_path):sha(locked_path),str(rulepath):sha(rulepath),str(run/'features.jsonl'):sha(run/'features.jsonl')}
    byid={}
    with (run/'features.jsonl').open() as f:
        for raw in f:
            row=json.loads(raw)
            if row['id'] in ids:byid[row['id']]=row
    if set(byid)!=set(ids):raise ValueError('missing locked rows')
    from PIL import Image
    from greekocr.glyphs.components import line_glyphs
    docs={};slots=[];lines=[];decisions=[]
    for index,lid in enumerate(ids):
        row=dict(byid[lid],label=byid[lid]['text']);pagepath=run/'pages'/(row['page_id']+'.json');inputs[str(pagepath)]=sha(pagepath)
        page=json.loads(pagepath.read_text());resp=Path(page['response'])
        if str(resp) not in docs:
            inputs[str(resp)]=sha(resp)
            if inputs[str(resp)]!=page['response_sha256']:raise ValueError('response custody')
            docs[str(resp)]=json.loads(resp.read_text())['document']
        doc=docs[str(resp)];crop=cached_crop(row)
        with Image.open(crop) as im:glyphs=line_glyphs(im)
        widths={i:digit_widths(row,t,doc) for i,t in enumerate(tokenize(row['text']))}
        current=enumerate_locked_line(row,locks,set(ids))
        for s in current:
            s.update(geometry=locate_slot(row,s,doc,exact_boundary=True),document=row['source']+':'+row['item'],
                     source=row['source'],google_glyph=s['glyph'],crop_sha256=row['crop_sha256'])
            if s['geometry']['geom_status']=='ok':
                s.update(render(crop,s['geometry'],SCRATCH/'n1_cache/n1e_rendered',glyphs=glyphs))
                s['dash']=measure_dash(s['measurements'],widths[s['token_index']])
            else:
                with Image.open(crop) as im:images=[im.convert('RGB'),im.convert('RGB').resize((im.width*3,im.height*3),Image.Resampling.LANCZOS)]
                for name,im in zip(('line','zoom'),images):
                    data=clean_png(im);digest=hashlib.sha256(data).hexdigest();p=SCRATCH/'n1_cache/n1e_rendered'/(digest+'.png')
                    p.parent.mkdir(exist_ok=True,parents=True)
                    if not p.exists():p.write_bytes(data)
                    s[name]=str(p);s[name+'_sha256']=digest
                s['render_scope']='whole_line_unlocalized'
            slots.append(s);decisions.append(decide(s,rule,row['text']))
        lines.append(dict(line_id=lid,text=row['text'],parent_label=byid[lid]['label'],crop=str(crop),crop_sha256=sha(crop),slots=[s['slot_id'] for s in current]))
        if (index+1)%25==0:print('locked lines',index+1,'slots',len(slots),flush=True)
    selected,pool=choose(slots,decisions)
    for s in slots:s['read_reason']=selected.get(s['slot_id'],'not_selected')
    bed=[s for s in slots if s['slot_id'] in selected]
    jsonl(OUT/'slots.jsonl',slots);jsonl(OUT/'lines.jsonl',lines);jsonl(OUT/'rule_decisions.jsonl',decisions)
    jsonl(OUT/'read_set.jsonl',bed)
    controls=typed_controls(rows(BASE/'controls/approved.jsonl'),rows(BASE/'controls/dash_types.jsonl'))
    jsonl(OUT/'controls.jsonl',controls)
    packs=build(bed,controls,PACK,OUT,locks,seed=SEED,evaluation_ids=set(ids),frozen_rule=rulepath)
    write(OUT/'pack_build.json',packs)
    dry=[]
    for ctx in packs['contexts']:
        for reader in ('r1','r2'):
            cmd=[sys.executable,'-B','-s',str(ROOT/'scripts/secondary/reading/n1_launch.py'),'n1e',ctx['context'],reader,'--dry-run']
            r=subprocess.run(cmd,capture_output=True,text=True)
            if r.returncode:raise ValueError(r.stdout+r.stderr)
            dry.append(json.loads(r.stdout))
    nreads=sum(sum(c['readers'].values()) for c in packs['contexts'])
    result=dict(rule_hash=rule['rule_hash'],rule_frozen_before_locked=True,inputs=inputs,lines=len(lines),slots=len(slots),
        selected_slots=len(bed),read_reasons=dict(Counter(selected.values())),remaining_marked_pool=pool,seed=SEED,
        unlocalized_read_slots=sum(s.get('render_scope')=='whole_line_unlocalized' for s in bed),
        geometry=dict(Counter(s['geometry']['geom_status'] for s in slots)),classes=dict(Counter(d['class'] for d in decisions)),
        contexts=len(packs['contexts']),reads_including_controls=nreads,points=nreads*.2/100,dry_runs=dry,
        no_readers_launched=True,pack_root=str(PACK))
    write(OUT/'build.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('inputs','dry_runs')},indent=2))
if __name__=='__main__':main()
