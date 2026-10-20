"""Offline N1W1 replacement preparation. Original packs and bindings stay sealed."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import random
import re
import shutil
import sys
sys.path[:0]=[str(Path(__file__).parent),str(Path(__file__).resolve().parents[1]/'secondary/reading')]
import n1w1 as m
from PIL import Image, ImageDraw

R3=m.ART/'r3'
ORIGINAL_VALIDATE=m.validate

def keypath(art,ctx,reader):
    return art/'keys'/(ctx+('' if reader=='r1' else '.'+reader)+'.json')

def closure(ctx,reader,art=R3,pack=m.PACK,completed=False):
    rd=pack/ctx/reader;key=json.loads(keypath(art,ctx,reader).read_text());items=m.rows(rd/'items.jsonl')
    bad=[];files={};ids=[i['item_id'] for i in items];expected={'items.jsonl'}
    if ids!=key['readers'][reader] or len(set(ids))!=len(ids):bad.append('ids/order mismatch')
    earlier={}
    for r in ('r1','r2','r3'):
        if r==reader:break
        p=keypath(m.ART if r in ('r1','r2') else art,ctx,r)
        if p.exists():earlier.update(json.loads(p.read_text())['items'])
    if set(ids)&set(earlier):bad.append('reused ids')
    prior=defaultdict(list)
    for k in earlier.values():prior[k['slot_id']].append(k)
    for i in items:
        if set(i)!={'item_id','line','zoom','options'} or not re.fullmatch(r'k[0-9a-f]{10}',i['item_id']):bad.append('public schema')
        k=key['items'][i['item_id']]
        if set(i['options'])!=set('ABCDEFGHIJ') or set(i['options'].values())!=set(m.MEANINGS) or i['options']!=k['option_map']:bad.append('options')
        for old in prior[k['slot_id']]:
            if k['control_truth'] is not None:bad.append('reused control')
            if any(i['options'][a]==old['option_map'][a] for a in i['options']):bad.append('option letter reused')
        for f in ('line','zoom'):
            p=Path(i[f]);expected.add(str(p))
            if p.is_absolute() or len(p.parts)!=2 or p.parts[0]!='img' or '..' in p.parts:bad.append('unsafe image')
    for p in rd.rglob('*'):
        rel=str(p.relative_to(rd))
        if p.is_symlink() or (p.is_file() and p.stat().st_nlink!=1):bad.append('unsafe entry '+rel)
        if completed and (rel=='answers.jsonl' or rel=='zoom' or rel.startswith('zoom/')):continue
        if p.is_dir():
            if rel!='img':bad.append('unexpected directory '+rel)
            continue
        if rel not in expected:bad.append('unexpected file '+rel)
        files[rel]=m.sha(p)
        if p.suffix=='.png':
            with Image.open(p) as im:
                im.load()
                if im.format!='PNG' or im.mode not in ('L','RGB') or im.info:bad.append('image format/metadata')
            if p.name!=files[rel]+'.png':bad.append('image hash filename')
    if set(files)!=expected:bad.append('missing file')
    manifest=rd.parent/('MANIFEST.'+reader+'.json')
    if completed:
        if not manifest.exists() or json.loads(manifest.read_text())['files']!=files:bad.append('seal mismatch')
    elif not bad:m.dump(manifest,dict(bed='n1',reader=reader,files=files))
    return dict(context=ctx+'/'+reader,ok=not bad,violations=bad,items=len(items),files=files,manifest_sha256=m.sha(manifest) if manifest.exists() else None)

def validate(art=R3,pack=m.PACK):
    ORIGINAL_VALIDATE(m.ART,pack)
    info=json.loads((art/'build.json').read_text())
    for p,h in info['bindings'].items():
        if m.sha(p)!=h:raise ValueError('replacement binding changed: '+p)
    for c in info['replacements']:
        result=closure(c['context'],c['reader'],art,pack,True)
        if not result['ok']:raise ValueError(result['violations'])
    return info

def prepare(art=R3,pack=m.PACK):
    m.validate();review=json.loads((m.ART/'review.json').read_text());decisions=m.rows(m.ART/'decisions.jsonl')
    if m.sha(m.ART/'decisions.jsonl')!=review['decisions_sha256']:raise ValueError('stale review')
    if art.exists():raise ValueError('replacement build exists; never overwrite')
    missing=defaultdict(set)
    for d in decisions:
        for v in d['reads']:
            if v['context_status']!='VALID' or v['read_status']!='ok':missing[v['context']].add(d['slot_id'])
    controls=m.rows(m.ART/'controls.jsonl');slots={s['slot_id']:s for s in m.rows(m.ART/'candidates.jsonl')}
    rng=random.Random('N1-W1-R3:20261018:fresh');used=set();replacements=[];routes=[];causes=[];closures=[]
    for p in (m.ART/'keys').glob('*.json'):used.update(json.loads(p.read_text())['items'])
    contexts=sorted({c.split('/')[0] for c in missing})
    for ctx in contexts:
        oldkeys=[json.loads(keypath(m.ART,ctx,r).read_text()) for r in ('r1','r2')]
        excluded={v['slot_id'] for k in oldkeys for v in k['items'].values() if v['control_truth'] is not None}
        prior=defaultdict(list)
        for k in oldkeys:
            for v in k['items'].values():prior[v['slot_id']].append(v['option_map'])
        broken=[r for r in ('r1','r2') if ctx+'/'+r in missing]
        for number,logical in enumerate(broken,3):
            reader='r'+str(number);identity=ctx+'/'+logical;ev=review['contexts'][identity];gate=ev.get('gate',{})
            reasons=[]
            if gate.get('status')=='VOID':
                if not gate['raised_control_correct']:reasons.append('raised control not correctly read')
                if gate['viewed_wrong']>1:reasons.append(str(gate['viewed_wrong'])+' viewed control errors (>1)')
                if gate['viewed_controls']<2:reasons.append('fewer than 2 viewed controls')
            elif ev.get('status')=='INVALID':reasons.append(ev['reason'])
            else:reasons.append(str(len(missing[identity]))+' unviewed bed items in VALID context')
            causes.append(identity+': '+'; '.join(reasons)+f' -> {ctx}/{reader} ({len(missing[identity])} positions)')
            available=[c for c in controls if c['slot_id'] not in excluded];rng.shuffle(available)
            chosen=[]
            for truth in ('raised dot','baseline dot','hyphen','en dash','em dash'):
                chosen.append(next(c for c in available if c['truth']==truth))
            chosen += [c for c in available if c not in chosen][:9-len(chosen)]
            excluded.update(c['slot_id'] for c in chosen)
            group=[dict(slots[s]) for s in sorted(missing[identity])]+chosen;rng.shuffle(group)
            # Require an order different from either previous reader, including restricted bed order.
            bedorder=[s['slot_id'] for s in group if s['slot_id'] in missing[identity]]
            for k in oldkeys:
                old=[v['slot_id'] for v in k['items'].values() if v['slot_id'] in missing[identity]]
                if bedorder==old:raise ValueError('order not fresh')
            rd=pack/ctx/reader;(rd/'img').mkdir(parents=True,exist_ok=False);public=[];private={}
            for s in group:
                sid=s['slot_id'];meanings=list(m.MEANINGS)
                while True:
                    rng.shuffle(meanings);options=dict(zip('ABCDEFGHIJ',meanings))
                    if all(all(options[a]!=old[a] for a in options) for old in prior[sid]):break
                prior[sid].append(options)
                while True:
                    iid='k'+f'{rng.getrandbits(40):010x}'
                    if iid not in used:break
                used.add(iid);item=dict(item_id=iid,options=options)
                for f in ('line','zoom'):
                    src=Path(s[f]);h=m.sha(src)
                    if h!=s[f+'_sha256']:raise ValueError('source image hash')
                    target=rd/'img'/(h+'.png')
                    if not target.exists():shutil.copyfile(src,target)
                    item[f]='img/'+target.name
                public.append(item);private[iid]=dict(slot_id=sid,line_id=s['line_id'],option_map=options,control_truth=s.get('truth'),geometry=s['geometry'],google_glyph=s.get('google_glyph',s.get('glyph')),measurements=s.get('measurements'),dash=s.get('dash'))
            m.jsonl(rd/'items.jsonl',public);m.dump(keypath(art,ctx,reader),dict(readers={reader:[i['item_id'] for i in public]},items=private,calibration=False,schema='sep2'))
            route=dict(context=ctx,reader=reader,replaces=logical,slot_ids=sorted(missing[identity]),items=len(public),bed=len(missing[identity]),controls=len(chosen))
            replacements.append(route);routes.append(route);closures.append(closure(ctx,reader,art,pack))
    if not all(c['ok'] for c in closures):raise ValueError(closures)
    m.dump(art/'routing.json',dict(schema='N1W1-R3-routing-v1',routes=routes,policy='Replace only listed logical reader slots; retain original VALID viewed votes; no third vote; replacement VOID/INVALID remains HOLD.'))
    (art/'VOID_CAUSES.txt').write_text('\n'.join(causes)+'\n');m.dump(art/'closure.json',closures)
    bindings={str(p):m.sha(p) for p in [m.ART/'review.json',m.ART/'decisions.jsonl',art/'routing.json',*sorted((art/'keys').glob('*.json'))]}
    for c in replacements:
        rd=pack/c['context']/c['reader'];bindings[str(rd/'items.jsonl')]=m.sha(rd/'items.jsonl');p=rd.parent/('MANIFEST.'+c['reader']+'.json');bindings[str(p)]=m.sha(p)
    for p in [*Path(__file__).parent.glob('n1w1_r3*'),*(m.ROOT/'scripts/secondary/reading').glob('*n1w1_r3*')]:
        if p.is_file():bindings[str(p)]=m.sha(p)
    count=sum(c['items'] for c in replacements)
    result=dict(schema='N1W1-R3-v1',replacements=replacements,replacement_contexts=len(replacements),parent_contexts=len(contexts),items=count,bed_positions=sum(c['bed'] for c in replacements),points=round(count*.002,3),estimate_basis='original preparation estimate 0.002 weekly points/item; not measured',bindings=bindings,no_readings=True,network=False,git_writes=False)
    m.dump(art/'build.json',result);validate(art,pack);return result

def sheets(out=m.REVIEW/'sheets'):
    from n1w1_sheets import font,paste_fit
    ds=[d for d in m.rows(m.ART/'decisions.jsonl') if d['agreed_raised']]
    if len(ds)!=22:raise ValueError('expected exactly 22 agreed cells')
    if out.exists():raise ValueError('refusing overwrite sheets')
    out.mkdir(parents=True);sm={s['slot_id']:s for s in m.rows(m.ART/'candidates.jsonl')};controls=m.rows(m.ART/'controls.jsonl')
    refs=[c for t in ('raised dot','baseline dot') for c in [c for c in controls if c['truth']==t][:2]]
    if len(refs)!=4:raise ValueError('need four approved references')
    index=[]
    for offset in range(0,22,6):
        canvas=Image.new('RGB',(2400,3300),'white');draw=ImageDraw.Draw(canvas)
        draw.text((35,20),f'N1W1 agreed raised dots | sheet {offset//6+1}/4 | lead pixel review pending',font=font(32,True),fill='black')
        for j,c in enumerate(refs):
            x=30+j*595;draw.text((x,78),'APPROVED '+c['truth'],font=font(24,True),fill='black')
            draw.text((x,113),c['slot_id'],font=font(12),fill='black');paste_fit(canvas,c['zoom'],(x,145,x+570,490))
        cells=[]
        for j,d in enumerate(ds[offset:offset+6]):
            s=sm[d['slot_id']];x=30+(j%2)*1190;y=540+(j//2)*910
            draw.rectangle((x,y,x+1160,y+880),outline='#bbbbbb',width=2)
            draw.text((x+15,y+14),f"{offset+j+1:02d}  {d['slot_id']}",font=font(19,True),fill='black')
            readtext=' | '.join(f"{r['context']}: {r['meaning']} ({r['context_status']}, {r['read_status']})" for r in d['reads'])
            draw.text((x+15,y+48),readtext,font=font(18),fill='black')
            paste_fit(canvas,s['zoom'],(x+15,y+95,x+1145,y+690));paste_fit(canvas,s['line'],(x+15,y+720,x+1145,y+855))
            cells.append(dict(cell=offset+j+1,slot_id=s['slot_id'],reads=d['reads'],zoom_sha256=s['zoom_sha256'],line_sha256=s['line_sha256'],box=[x,y,x+1160,y+880]))
        path=out/f'raised_{offset//6+1:02}.png';canvas.save(path)
        with Image.open(path) as im:im.verify()
        index.append(dict(sheet=str(path),sha256=m.sha(path),dimensions=[2400,3300],cells=cells,references=[dict(slot_id=c['slot_id'],truth=c['truth'],zoom_sha256=c['zoom_sha256'],approval_provenance=c.get('approval_provenance')) for c in refs]))
    m.dump(out/'index.json',dict(decisions_sha256=m.sha(m.ART/'decisions.jsonl'),sheets=index,cell_count=22,reference_policy='Two approved raised-dot and two approved baseline-dot controls per sheet; not necessarily same document.'))
    (out/'index.md').write_text('# N1W1 raised-dot contact sheets\n\n22 agreed cells; lead pixel review pending. Each sheet repeats two approved raised-dot and two baseline-dot controls.\n\n'+'\n'.join(f"- [Sheet {i+1}](raised_{i+1:02}.png): cells {i*6+1}–{min(i*6+6,22)}" for i in range(4))+'\n\n'+ '\n'.join(f"- Cell {j+1}: `{d['slot_id']}` — sheet {j//6+1}" for j,d in enumerate(ds))+'\n')
    return dict(sheets=4,cells=22,index=str(out/'index.json'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','sheets','validate']);a=p.parse_args()
    print(json.dumps(prepare() if a.action=='build' else sheets() if a.action=='sheets' else validate(),ensure_ascii=False,indent=2))
