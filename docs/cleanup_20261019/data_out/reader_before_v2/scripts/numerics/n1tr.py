"""N1TR offline preparation and fail-closed two-read/lead finalisation."""
import argparse
from collections import Counter, defaultdict
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import re
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT),str(Path(__file__).parent),str(ROOT/'scripts/secondary'),str(ROOT/'scripts/secondary/reading')]
from n1_render import SCRATCH, render
from n1t_packs import build as packs, typed_controls
from n1_pack_closure import scan
from greekocr.numerics.tokens import tokenize
from greekocr.numerics.locks import load_locks
from greekocr.numerics.combine_v2 import MEANINGS, decode_and_gate
from greekocr.glyphs.components import line_glyphs
from PIL import Image, ImageDraw
import scan_rollout
from ru2t_coverage import coverage
from ru1_census import exclusion_ids
SOURCE=Path.home()/'Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl'
ART=ROOT/'artifacts/n1/n1tr'; PACK=SCRATCH/'sol_packs/n1tr'; REVIEW=SCRATCH/'n1_review/n1tr'
REGISTRY=ROOT/'docs/labelfix/lqb/versions.json'
SCANNER_SHA='dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547'
def rows(p):return [json.loads(s) for s in Path(p).read_text().splitlines() if s.strip()]
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def dump(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def jsonl(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in v))
def document(r):return r.get('doc') or r['source']+':'+r.get('item','')
def era(r):
    y=r.get('year');return r['source']+':'+(str(y//50*50)+'-'+str(y//50*50+49) if isinstance(y,int) else 'unknown')
def enumerate_slots(data,excluded,locks):
    out=[];omitted=[]
    for r in data:
        reason='release_exclusions' if r['id'] in excluded else 'N1_reserved' if r['id'] in locks.reserved_line_ids or document(r) in locks.reserved_docs else None
        for ti,t in enumerate(tokenize(r['label'])):
            if t.digit_count<4:continue
            for s in t.slots:
                if s.boundary or s.glyph not in ('-','.'):continue
                v=dict(asdict(s),slot_id=f"{r['id']}:t{ti}:s{s.index}",line_id=r['id'],token_index=ti,token_start=t.start,token_end=t.end,digit_count=t.digit_count,source=r['source'],source_era=era(r),document=document(r),google_glyph=s.glyph)
                if reason:omitted.append(dict(v,exclusion=reason))
                else:out.append(v)
    return out,omitted

def crop_geometry(image,text,slot,glyphs=None):
    """Unique whitespace-word and exact projection-run counts, never proportional x.

    Uses the existing line_glyphs native mask. Only all-numeric whitespace words
    are eligible. Every visible character must have a distinct horizontal run;
    digit flanks must reach >=60% of the local digit band. Touching/fragmented
    digits, word-count mismatches and mixed words fail closed.
    """
    import numpy as np
    g=glyphs or line_glyphs(image)
    mask=g.ink
    def runs(active):
        edges=np.diff(np.r_[False,active,False].astype(int));return list(zip(np.where(edges==1)[0],np.where(edges==-1)[0]))
    rr=runs(mask.any(axis=0))
    words=list(re.finditer(r'\S+',text))
    if not rr:return dict(geom_status='unlocalised',reason='no_ink')
    # Word boundaries must be distinctly wider than character gaps. Match count
    # at every observed gap cutoff; require one unique partition, not best fit.
    gaps=[rr[i+1][0]-rr[i][1] for i in range(len(rr)-1)]
    partitions=set()
    for cut in sorted(set(gaps)):
        split=tuple(i+1 for i,v in enumerate(gaps) if v>cut)
        if len(split)+1==len(words):partitions.add(split)
    if len(words)==1:partitions.add(())
    if len(partitions)!=1:return dict(geom_status='unlocalised',reason='word_partition_ambiguous')
    bounds=(0,*next(iter(partitions)),len(rr))
    wi=next((i for i,w in enumerate(words) if w.start()<=slot['start'] and slot['end']<=w.end()),None)
    if wi is None:return dict(geom_status='unlocalised',reason='no_word')
    word=words[wi];value=word.group()
    if not re.fullmatch(r'[0-9]+(?:[.\-··,][0-9]+)+',value):return dict(geom_status='unlocalised',reason='mixed_or_non_numeric_word')
    pieces=rr[bounds[wi]:bounds[wi+1]]
    if len(pieces)!=len(value):return dict(geom_status='unlocalised',reason='character_run_count_differs')
    boxes=[]
    for a,b in pieces:
        ys=np.where(mask[:,a:b].any(axis=1))[0];boxes.append([int(a),int(ys[0]),int(b),int(ys[-1]+1)])
    di=[boxes[i] for i,c in enumerate(value) if c.isdigit()];h=max(b[3]-b[1] for b in di)
    if any(b[3]-b[1]<.6*h for b in di):return dict(geom_status='unlocalised',reason='digit_fragment_or_band_mismatch')
    i=slot['start']-word.start();l,r=boxes[i-1],boxes[i+1];mark=boxes[i]
    top=min(l[1],r[1]);base=max(l[3],r[3]);h=base-top
    return dict(geom_status='ok',method='native_mask_unique_word_exact_character_runs',left_digit=l,right_digit=r,symbol_bbox=mark,digit_top=top,baseline=base,digit_height=h,gap=[l[2],r[0]],gap_width=r[0]-l[2],gap_center=(mark[0]+mark[2])/2,zoom_bbox=[math.floor(l[0]-.3*h),math.floor(top-.3*h),math.ceil(r[2]+.3*h),math.ceil(base+.3*h)])

def validate(art=ART,pack=PACK):
    if pack.resolve().is_relative_to(ROOT.resolve()):raise ValueError('in-repo pack root')
    info=json.loads((art/'build.json').read_text())
    if sha(ROOT/'scripts/secondary/reading/scan_rollout.py')!=SCANNER_SHA:raise ValueError('canonical scanner changed')
    for p,h in {**info['inputs'],**info['pack_inputs']}.items():
        if sha(p)!=h:raise ValueError('bound input changed: '+p)
    for c in info['contexts']:
        for reader in ('r1','r2'):
            s=scan(pack/c['context']/reader,art,completed=True,meanings=MEANINGS)
            if not s['ok']:raise ValueError(s['violations'])
    return info

def build(source=SOURCE,art=ART,pack=PACK):
    if art.exists() or pack.exists():raise ValueError('refusing overwrite of N1TR build')
    if pack.resolve().is_relative_to(ROOT.resolve()):raise ValueError('in-repo pack root')
    data=rows(source);byid={r['id']:r for r in data}
    if len(byid)!=len(data):raise ValueError('duplicate parent IDs')
    locks=load_locks(ROOT/'artifacts/n1');excluded,inputs=exclusion_ids()
    inputs[str(source)]=sha(source)
    for name in ('n1_reserved_docs.txt','n1_reserved_doc_line_ids.txt','n1_locked_eval_line_ids.txt'):
        p=ROOT/'artifacts/n1'/name;inputs[str(p)]=sha(p)
    slots,omitted=enumerate_slots(data,excluded,locks)
    # Approved controls must never simultaneously be bed items.
    cp=ROOT/'artifacts/n1/controls/approved.jsonl';dp=cp.with_name('dash_types.jsonl')
    controls=typed_controls(rows(cp),rows(dp));inputs.update({str(cp):sha(cp),str(dp):sha(dp)})
    bedids={s['slot_id'] for s in slots};controls=[c for c in controls if c['slot_id'] not in bedids and c.get('document') not in locks.reserved_docs]
    rendered=[];cache={};admitted=source.with_name('admitted_all_v2.jsonl');inputs[str(admitted)]=sha(admitted)
    metadata={r['id']:r for r in rows(admitted) if r['id'] in byid}
    for index,s in enumerate(slots):
        r=byid[s['line_id']];p=Path(r['crop']);p=p if p.is_absolute() else source.parents[4]/p
        try:
            if s['line_id'] not in cache:
                digest=sha(p);inputs[str(p)]=digest
                meta=metadata.get(r['id'],{})
                if meta.get('crop_sha256') and meta['crop_sha256']!=digest:raise ValueError('crop hash differs from admitted v2')
                with Image.open(p) as im:image=im.convert('RGB')
                cache[s['line_id']]=(image,line_glyphs(image))
            image,g=cache[s['line_id']]
            if r.get('numeric_slots'):
                # Explicit per-slot geometry only: never reuse one row-level box.
                geom=next((v['geometry'] for v in r.get('numeric_slots',[]) if v.get('start')==s['start'] and v.get('end')==s['end']),None)
            else:geom=None
            geom=geom or crop_geometry(image,r['label'],s,g)
            s.update(geometry=geom,crop=str(p),crop_sha256=inputs[str(p)])
            if geom['geom_status']=='ok':s.update(render(p,geom,SCRATCH/'n1_cache/n1tr',glyphs=g));rendered.append(s)
        except (OSError,ValueError) as e:s['geometry']=dict(geom_status='unlocalised',reason=str(e))
        if (index+1)%250==0:print('localised',index+1,'/',len(slots),flush=True)
    for s in slots:
        if s['geometry']['geom_status']!='ok':s.update(decision='hold',hold_reason='unlocalised')
    for c in controls:
        for k in ('line','zoom'):inputs[c[k]]=sha(c[k])
    result=packs(rendered,controls,pack,art,locks,seed='N1TR:20261017:sep2')
    jsonl(art/'candidates.jsonl',slots);jsonl(art/'excluded.jsonl',omitted);jsonl(art/'unlocalised.jsonl',[s for s in slots if s['geometry']['geom_status']!='ok']);jsonl(art/'controls.jsonl',controls)
    dump(art/'closure.json',result['closure'])
    for p in [Path(__file__),ROOT/'scripts/numerics/n1tr_finalize.sh',ROOT/'scripts/secondary/reading/run_n1tr_all.sh',ROOT/'scripts/secondary/reading/n1tr_driver.py',ROOT/'docs/labelfix/secondary/prompts/sep2.md',ROOT/'scripts/numerics/n1t_packs.py',ROOT/'scripts/numerics/n1_pack_closure.py',ROOT/'scripts/secondary/ru2t_coverage.py',ROOT/'scripts/secondary/reading/scan_rollout.py',ROOT/'scripts/secondary/reading/run_read.sh',ROOT/'scripts/secondary/reading/limit_probe.sh']:
        inputs[str(p)]=sha(p)
    reads=sum(sum(c['readers'].values()) for c in result['contexts'])
    info=dict(schema='N1TR-v1',source=str(source),parent_sha256=sha(source),parent_rows=len(data),candidates=len(slots),by_source=dict(Counter(s['source'] for s in slots)),by_source_era=dict(Counter(s['source_era'] for s in slots)),by_glyph=dict(Counter(s['glyph'] for s in slots)),excluded=len(omitted),unlocalised=len(slots)-len(rendered),contexts=result['contexts'],reads=reads,points=round(reads*.002,3),inputs=inputs,pack_inputs={str(p):sha(p) for p in [*pack.rglob('*'),*(art/'keys').glob('*.json'),art/'candidates.jsonl',art/'controls.jsonl',art/'unlocalised.jsonl'] if p.is_file()},pack=str(pack),network=False,no_readings=True,git_writes=False,ink_rule='FAILED 0/5; never used for edits')
    dump(art/'build.json',info);validate(art,pack);return info

def collect(art,pack,context,reader,seen):
    stem=context+'.'+reader;base=art/'answers'/stem;rd=pack/context/reader
    runpath=Path(str(base)+'.run.json');run=json.loads(runpath.read_text());roll=Path(run['rollout']);digest=sha(roll)
    if run['rc']!=0 or run['model']!='gpt-6.1-sol' or digest in seen:raise ValueError('failed/model/reused rollout')
    seen.add(digest)
    meta=[r.get('payload',{}) for r in rows(roll) if r.get('type') in ('session_meta','turn_context')]
    if {m['model'] for m in meta if m.get('model')}!={'gpt-6.1-sol'} or {m.get('effort',m.get('reasoning_effort')) for m in meta if m.get('effort',m.get('reasoning_effort'))}!={'medium'}:raise ValueError('model/effort provenance')
    scanned=scan_rollout.inspect(roll,rd)
    if not scanned['ok'] or scanned['scanner_version']!='v4.4-canonical':raise ValueError('unclean v4.4 scan')
    items=rows(rd/'items.jsonl')
    # Both native line and zoom are legitimate roots for derived ancestry.
    cov=coverage(scanned,roll,rd,items,image_fields=('line','zoom'));unviewed=set(cov['unviewed_crops'])
    dropped={i['item_id'] for i in items if i['line'] in unviewed and i['zoom'] in unviewed}
    keypath=art/'keys'/(context+('' if reader=='r1' else '.r2')+'.json');key=json.loads(keypath.read_text())
    gate,decoded=decode_and_gate(key,rows(rd/'answers.jsonl'))
    # Controls are gated on viewed evidence only, and the raised control must be
    # correctly read. Unseen/abstained controls cannot certify a context.
    seencontrols=[d for d in decoded if d['control'] and d['item_id'] not in dropped]
    from greekocr.numerics.combine_v2 import control_matches
    wrong=sum(d['meaning']!='unreadable' and not control_matches(key['items'][d['item_id']]['control_truth'],d['meaning']) for d in seencontrols)
    raised=any(key['items'][d['item_id']]['control_truth']=='raised dot' and d['meaning']=='raised dot' for d in seencontrols)
    gate.update(status='VALID' if wrong<=1 and raised and len(seencontrols)>=2 else 'VOID',viewed_controls=len(seencontrols),viewed_wrong=wrong,raised_control_correct=raised)
    votes=[dict(d,reader=reader,context=context+'/'+reader,context_status=gate['status'],read_status='ok' if d['item_id'] not in dropped else 'unviewed',rollout_sha256=digest) for d in decoded]
    ev={str(p):sha(p) for p in (runpath,roll,rd/'answers.jsonl',keypath)}
    dump(Path(str(base)+'.scan.json'),scanned);dump(Path(str(base)+'.coverage.json'),dict(cov,dropped_items=sorted(dropped)));dump(Path(str(base)+'.gate.json'),gate)
    ev.update({str(Path(str(base)+suffix)):sha(Path(str(base)+suffix)) for suffix in ('.scan.json','.coverage.json','.gate.json')})
    return votes,dict(gate=gate,coverage=dict(cov,dropped_items=sorted(dropped)),evidence=ev)

def combine(slot,reads):
    valid=[r for r in reads if r['context_status']=='VALID' and r['read_status']=='ok']
    agreed=len(valid)==2 and {r['reader'] for r in valid}=={'r1','r2'} and all(r['meaning']=='raised dot' for r in valid)
    reason='awaiting_two_valid_raised_reads'
    if slot['geometry']['geom_status']!='ok':reason='unlocalised';agreed=False
    elif 'range' in slot['grammar_candidates']:reason='range_never_edit'
    elif agreed:reason='lead_pixel_check_required'
    elif any(r['context_status']=='VOID' for r in reads):reason='VOID'
    elif any(r['context_status']=='INVALID' for r in reads):reason='invalid_or_missing_context'
    elif len(valid)==2:reason='disagreement' if valid[0]['meaning']!=valid[1]['meaning'] else 'other_or_unreadable_or_nonraised'
    return dict(slot_id=slot['slot_id'],line_id=slot['line_id'],start=slot['start'],end=slot['end'],old=slot['glyph'],agreed_raised=agreed,decision='hold',reason=reason,reads=reads)

def apply_rows(data,slots,decisions,lead):
    wanted={d['slot_id'] for d in decisions if d['agreed_raised']}
    if len({r['slot_id'] for r in lead})!=len(lead) or {r['slot_id'] for r in lead}!=wanted:raise ValueError('lead must cover exactly every agreed raised slot')
    lm={r['slot_id']:r for r in lead};sm={s['slot_id']:s for s in slots};byline=defaultdict(list)
    for d0 in decisions:
        d=dict(d0);s=sm[d['slot_id']];l=lm.get(d['slot_id'])
        if l:
            if l.get('printed') not in ('raised dot','baseline dot','hyphen','en dash','em dash','range','other','unreadable') or l.get('pixel_checked') is not True:raise ValueError('lead pixel check incomplete')
            d['lead']=l
            if d['agreed_raised'] and l['printed']=='raised dot' and 'range' not in s['grammar_candidates']:
                d.update(decision='edit',reason='two_valid_raised_reads_and_lead_pixels',new='·')
            else:d['reason']='range_never_edit' if 'range' in s['grammar_candidates'] or l['printed']=='range' else 'lead_hold'
        byline[d['line_id']].append(d)
    out=[]
    for r in data:
        ds=byline[r['id']];label=r['label'];chars=list(label)
        for d in ds:
            if d['end']!=d['start']+1 or label[d['start']:d['end']]!=d['old'] or d['old'] not in ('-','.'):raise ValueError('parent offset mismatch')
            if d['decision']=='edit':chars[d['start']]='·'
        new=''.join(chars)
        out.append(dict(r,parent_label=label,label=new,new_label=new,edits=[d for d in ds if d['decision']=='edit'],holds=[d for d in ds if d['decision']=='hold'],slot_provenance=ds))
    return out

def lead_sheet(slots,decisions,review=REVIEW,controls=(),labels=None):
    from n1_raised_sheets import paste_fit, font
    review.mkdir(parents=True,exist_ok=True);sm={s['slot_id']:s for s in slots};selected=[sm[d['slot_id']] for d in decisions if d['agreed_raised']];index=[]
    for j,s in enumerate(selected,1):
        refs=[r for r in controls if r.get('document')==s['document'] and r.get('truth')=='raised dot']
        # Agreed candidates from this document are explicitly unadjudicated refs.
        if not refs:refs=[dict(r,reference_basis='two-read agreement; NOT adjudicated') for r in selected if r['document']==s['document'] and r['slot_id']!=s['slot_id']][:2]
        canvas=Image.new('RGB',(1500,1000),'white');draw=ImageDraw.Draw(canvas)
        draw.text((20,15),s['slot_id'],fill='black')
        text=(labels or {}).get(s['line_id'],'')
        draw.text((20,35),f"offset {s['start']}:{s['end']} | "+text[max(0,s['start']-35):s['end']+35],fill='black',font=font(20));paste_fit(canvas,s['zoom'],(20,55,1480,350));paste_fit(canvas,s['line'],(20,360,1480,480))
        draw.text((20,500),'Same-document raised references: '+('available' if refs else 'UNAVAILABLE - do not infer truth'),fill='black')
        for k,ref in enumerate(refs[:2]):
            draw.text((20+k*740,535),ref.get('reference_basis','lead-approved raised dot'),fill='black');paste_fit(canvas,ref['zoom'],(20+k*740,560,730+k*740,900))
        path=review/f'cell_{j:05}.png';canvas.save(path)
        index.append(dict(cell=j,slot_id=s['slot_id'],document=s['document'],start=s['start'],end=s['end'],parent_label=text,sheet=str(path),sha256=sha(path),zoom_sha256=s['zoom_sha256'],references=[dict(slot_id=r['slot_id'],basis=r.get('reference_basis','lead-approved'),zoom_sha256=r['zoom_sha256']) for r in refs],reference_shortfall=not bool(refs)))
    dump(review/'index.json',index)
    template=review/'lead_template.jsonl'
    entries=[dict(slot_id=s['slot_id'],zoom_sha256=s['zoom_sha256'],pixel_checked=False,printed=None,note='') for s in selected]
    if not template.exists():jsonl(template,entries)
    elif {r['slot_id'] for r in rows(template)}!={s['slot_id'] for s in selected}:raise ValueError('lead template stale; preserve existing work and use new review directory')
    return index

def finalize(art=ART,pack=PACK,source=SOURCE,review=REVIEW,apply_lead=False,registry=REGISTRY,output=None,scorer=None):
    info=validate(art,pack)
    if sha(source)!=info['parent_sha256']:raise ValueError('parent changed')
    votes=defaultdict(list);contexts={};seen=set();missing=[]
    for c in info['contexts']:
        for reader in ('r1','r2'):
            ctx=c['context'];identity=ctx+'/'+reader
            try:
                vv,ev=collect(art,pack,ctx,reader,seen);contexts[identity]=ev
                for v in vv:
                    if not v['control']:votes[v['slot_id']].append(v)
            except (ValueError,KeyError,TypeError,OSError) as e:
                contexts[identity]=dict(status='INVALID',reason=str(e))
                base=art/'answers'/(ctx+'.'+reader)
                contexts[identity]['evidence']={str(Path(str(base)+suffix)):sha(Path(str(base)+suffix)) for suffix in ('.run.json','.attempt.json','.launcher.log') if Path(str(base)+suffix).exists()}
                if not any(Path(str(base)+suffix).exists() for suffix in ('.run.json','.attempt.json','.launcher.log')):missing.append(identity)
                kp=art/'keys'/(ctx+('' if reader=='r1' else '.r2')+'.json')
                if kp.exists():
                    key=json.loads(kp.read_text())
                    for iid,k in key['items'].items():
                        if k['control_truth'] is None:votes[k['slot_id']].append(dict(item_id=iid,reader=reader,context=identity,context_status='INVALID',read_status='invalid',meaning=None,reason=str(e)))
    partial=(art/'STOPPED_AT_70.json').exists()
    if missing and not partial:raise ValueError('incomplete contexts; partial mode requires STOPPED_AT_70.json: '+str(missing))
    slots=rows(art/'candidates.jsonl');ds=[combine(s,votes[s['slot_id']]) for s in slots]
    jsonl(art/'decisions.jsonl',ds)
    if not apply_lead:
        index=lead_sheet(slots,ds,review,rows(art/'controls.jsonl'),labels={r['id']:r['label'] for r in rows(source)})
        result=dict(status='AWAITING_LEAD',partial=partial,agreed_raised=len(index),contexts=contexts,decisions_sha256=sha(art/'decisions.jsonl'))
        dump(review/'review_binding.json',dict(decisions_sha256=result['decisions_sha256'],index_sha256=sha(review/'index.json'),parent_sha256=info['parent_sha256']))
        dump(art/'review.json',result);return result
    binding=json.loads((review/'review_binding.json').read_text())
    if binding['decisions_sha256']!=sha(art/'decisions.jsonl') or binding['index_sha256']!=sha(review/'index.json') or binding['parent_sha256']!=sha(source):raise ValueError('review evidence changed')
    for cell in json.loads((review/'index.json').read_text()):
        if sha(cell['sheet'])!=cell['sha256']:raise ValueError('lead sheet changed')
    lead=rows(review/'lead_template.jsonl');sm={s['slot_id']:s for s in slots}
    for l in lead:
        if l.get('zoom_sha256')!=sm[l['slot_id']]['zoom_sha256']:raise ValueError('lead crop changed')
    result=apply_rows(rows(source),slots,ds,lead)
    output=output or ROOT/'artifacts/n1/n1_v1_train.jsonl'
    obj=json.loads(registry.read_text());versions=obj['versions'];parent=versions.get('collection_v2_train')
    if parent and parent['sha256']!=sha(source):raise ValueError('LQB parent differs')
    jsonl(output,result);output.with_suffix('.sha256').write_text(sha(output)+'  '+output.name+'\n')
    manifest=dict(version='n1_v1_train',partial=partial,parent=dict(path=str(source),sha256=sha(source)),output=dict(path=str(output),sha256=sha(output),rows=len(result)),edits=sum(len(r['edits']) for r in result),holds=sum(len(r['holds']) for r in result),contexts=contexts,lead=dict(path=str(review/'lead_template.jsonl'),sha256=sha(review/'lead_template.jsonl')),build_sha256=sha(art/'build.json'),decisions_sha256=sha(art/'decisions.jsonl'),scanner_sha256=SCANNER_SHA)
    if partial:manifest['stop_sha256']=sha(art/'STOPPED_AT_70.json')
    dump(output.with_name(output.stem+'_manifest.json'),manifest)
    versions['collection_v2_train']=dict(path=str(source),sha256=sha(source),parent=None,text_field='label',id_field='id',status='local')
    versions['n1_v1_train']=dict(path=str(output),sha256=sha(output),parent='collection_v2_train',text_field='label',id_field='id',status='local',population=dict(rows=len(result),partial=partial,definition='full train population; unresolved slots HOLD'))
    if scorer:manifest['lqb']=scorer(manifest)
    else:
        from greekocr.labelfix.lqb import run
        target=art/'lqb_rescore.json';score=run(ROOT/'docs/labelfix/lqb/truth_v1_1.jsonl',obj,['collection_v2_train','n1_v1_train']);dump(target,score);manifest['lqb']=dict(path=str(target),sha256=sha(target))
    dump(registry,obj)
    dump(output.with_name(output.stem+'_manifest.json'),manifest);dump(art/'FINALIZED_RECEIPT.json',manifest);return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','finalize']);p.add_argument('--apply-lead',action='store_true');a=p.parse_args()
    print(json.dumps(build() if a.action=='build' else finalize(apply_lead=a.apply_lead),ensure_ascii=False,indent=2))
