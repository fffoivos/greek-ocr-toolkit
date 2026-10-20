"""N1W1 offline preparation and fail-closed two-read/lead finalisation."""
from greekocr.ops.data_root import input_path as _data_input
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
from n1w1_render import SCRATCH, render
from n1w1_packs import build as packs, typed_controls
from n1w1_closure import scan
from n1w1_tokens import tokenize
from n1w1_locks import load_locks
from n1w1_combine import MEANINGS, decode_and_gate
from n1w1_geometry import locate_slot
from PIL import Image, ImageDraw
import n1w1_scan_rollout
from n1w1_coverage import coverage
from n1w1_exclusions import exclusion_ids
ADMISSIONS=Path.home()/'Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/w1_originals_v3_admitted.jsonl'
RUN=Path.home()/'Projects/collect-v3-data/run/W1'
ART=ROOT/'artifacts/n1/n1w1'; PACK=SCRATCH/'sol_packs/n1w1'; REVIEW=SCRATCH/'n1_review/n1w1'
SOURCE=ART/'parent.jsonl'
PROMPT=Path(__file__).with_name('n1w1_sep2.md')
REGISTRY=ROOT/'docs/records/labelfix/lqb/versions.json'
SCANNER_SHA='3bbe72cbc74c3fe58a70a4a143f3ea1b0c4e383ef47a32634e7e83f741dd49db'
def rows(p):return [json.loads(s) for s in _data_input(Path(p)).read_text().splitlines() if s.strip()]
def sha(p):
    h=hashlib.sha256()
    with _data_input(Path(p)).open('rb') as f:
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

def validate(art=ART,pack=PACK):
    if pack.resolve().is_relative_to(ROOT.resolve()):raise ValueError('in-repo pack root')
    info=json.loads((art/'build.json').read_text())
    if sha(ROOT/'scripts/secondary/reading/n1w1_scan_rollout.py')!=SCANNER_SHA:raise ValueError('canonical scanner changed')
    for p,h in {**info['inputs'],**info['pack_inputs']}.items():
        if sha(p)!=h:raise ValueError('bound input changed: '+p)
    for c in info['contexts']:
        for reader in ('r1','r2'):
            s=scan(pack/c['context']/reader,art,completed=True,meanings=MEANINGS)
            if not s['ok']:raise ValueError(s['violations'])
    return info

def select_admission(admission,features,excluded):
    selected=[];removed=[]
    for a in admission:
        if a['source']!='elstat' or a['primary_class']!='numerics_tables':continue
        if 'admission' in a and a['admission'].get('passed') is not True:raise ValueError('nonpassing admission row')
        ident=a.get('row_id',a.get('id'))
        if ident in excluded:removed.append(a);continue
        r=features[ident]
        for k in ('label','crop_bbox','crop_sha256','page_id'):
            if a[k]!=r[k]:raise ValueError('admission/W1 mismatch: '+ident+':'+k)
        selected.append(dict(a,id=ident,item=r['item'],document=document(r)))
    if len({r['id'] for r in selected})!=len(selected):raise ValueError('duplicate admission ids')
    return selected,removed

def build(source=ADMISSIONS,art=ART,pack=PACK):
    if art.exists() or pack.exists():raise ValueError('refusing overwrite of N1W1 build')
    if pack.resolve().is_relative_to(ROOT.resolve()):raise ValueError('in-repo pack root')
    excluded,inputs=exclusion_ids();locks=load_locks(ROOT/'artifacts/n1')
    inputs[str(source)]=sha(source);fp=RUN/'features.jsonl';inputs[str(fp)]=sha(fp)
    receipt=source.with_name('w1_originals_v3_admission_receipt.json');inputs[str(receipt)]=sha(receipt)
    admission_receipt=json.loads(receipt.read_text())
    original=Path(admission_receipt['input_path']);inputs[str(original)]=sha(original)
    if inputs[str(original)]!=admission_receipt['input_sha256']:raise ValueError('admission original input hash mismatch')
    if len(rows(source))!=admission_receipt['rows_pass']:raise ValueError('admission passing row count mismatch')
    readme=source.with_name('README.md');inputs[str(readme)]=sha(readme)
    features={r['id']:r for r in rows(fp)}
    data,removed=select_admission(rows(source),features,excluded)
    # Release-admitted reserved-document slots remain in output as holds, never packs.
    slots,omitted=enumerate_slots(data,excluded,locks)
    for s in omitted:s.update(geometry=dict(geom_status='unlocalised',reason=s['exclusion']),decision='hold',hold_reason=s['exclusion'])
    slots+=omitted
    cp=ROOT/'artifacts/n1/controls/approved.jsonl';dp=cp.with_name('dash_types.jsonl')
    controls=typed_controls(rows(cp),rows(dp));inputs.update({str(cp):sha(cp),str(dp):sha(dp)})
    bedids={s['slot_id'] for s in slots}
    controls=[c for c in controls if c['slot_id'] not in bedids and c.get('document') not in locks.reserved_docs and c['line_id'] not in locks.reserved_line_ids]
    rendered=[];responses={};crops={};requests={}
    for s in slots:
        if 'geometry' in s:continue
        r=features[s['line_id']];recordpath=RUN/'pages'/(r['page_id']+'.json');inputs[str(recordpath)]=sha(recordpath)
        record=json.loads(recordpath.read_text());response=Path(record['response']);inputs[str(response)]=sha(response)
        if inputs[str(response)]!=record['response_sha256']:raise ValueError('response hash mismatch')
        if str(response) not in responses:responses[str(response)]=json.loads(response.read_text())['document']
        geom=locate_slot(r,s,responses[str(response)]);s['geometry']=geom
        if geom['geom_status']=='ok':requests[r['id']]=r
    # Use collector Python for byte-identical regeneration, with a scratch-only crop copy.
    request=SCRATCH/'n1_cache/n1w1/request.jsonl';result=request.with_name('crops.json')
    jsonl(request,list(requests.values()))
    import subprocess
    subprocess.run(['/usr/bin/arch','-arm64',str(Path.home()/'Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python'),'-B',str(Path(__file__).with_name('n1w1_crops.py')),str(request),str(result)],check=True)
    inputs[str(request)]=sha(request);inputs[str(result)]=sha(result)
    crops={r['line_id']:r for r in json.loads(result.read_text())['records']}
    for s in slots:
        if s['geometry']['geom_status']!='ok':continue
        c=crops[s['line_id']]
        if c['crop_unavailable']:s['geometry']=dict(geom_status='unlocalised',reason=c['crop_error']);continue
        p=Path(c['crop']);inputs[str(p)]=sha(p)
        if inputs[str(p)]!=features[s['line_id']]['crop_sha256']:raise ValueError('crop hash mismatch')
        s.update(crop=str(p),crop_sha256=inputs[str(p)])
        s.update(render(p,s['geometry'],SCRATCH/'n1_cache/n1w1/rendered'));rendered.append(s)
    for s in slots:
        if s['geometry']['geom_status']!='ok':s.update(decision='hold',hold_reason=s['geometry'].get('reason',s['geometry']['geom_status']))
    for c in controls:
        for k in ('line','zoom'):inputs[c[k]]=sha(c[k])
    result=packs(rendered,controls,pack,art,locks,seed='N1W1:20261018:sep2')
    jsonl(art/'parent.jsonl',data);jsonl(art/'candidates.jsonl',slots);jsonl(art/'excluded.jsonl',removed)
    jsonl(art/'reserved_holds.jsonl',omitted);jsonl(art/'unlocalised.jsonl',[s for s in slots if s['geometry']['geom_status']!='ok']);jsonl(art/'controls.jsonl',controls)
    dump(art/'closure.json',result['closure'])
    for name in ('n1_reserved_docs.txt','n1_reserved_doc_line_ids.txt','n1_locked_eval_line_ids.txt'):
        p=ROOT/'artifacts/n1'/name;inputs[str(p)]=sha(p)
    for p in [*Path(__file__).parent.glob('n1w1*'),*(ROOT/'scripts/secondary/reading').glob('n1w1*'),ROOT/'scripts/secondary/reading/run_n1w1_all.sh']:
        if p.is_file():inputs[str(p)]=sha(p)
    reads=sum(sum(c['readers'].values()) for c in result['contexts'])
    info=dict(schema='N1W1-v1',admission=str(source),admission_sha256=sha(source),source=str(art/'parent.jsonl'),parent_sha256=sha(art/'parent.jsonl'),parent_rows=len(data),admission_elstat_rows=len(data)+len(removed),candidates=len(slots),localised=len(rendered),by_glyph=dict(Counter(s['glyph'] for s in slots)),excluded_rows=len(removed),reserved_hold_slots=len(omitted),unlocalised=len(slots)-len(rendered),contexts=result['contexts'],reads=reads,points=round(reads*.002,3),inputs=inputs,pack_inputs={str(p):sha(p) for p in [*pack.rglob('*'),*(art/'keys').glob('*.json'),art/'parent.jsonl',art/'candidates.jsonl',art/'controls.jsonl',art/'unlocalised.jsonl',art/'reserved_holds.jsonl',art/'excluded.jsonl'] if p.is_file()},pack=str(pack),network=False,no_readings=True,git_writes=False,localisation='collector exact W1 symbol anchors; no proportional/projection fallback')
    dump(art/'build.json',info);validate(art,pack);return info

def collect(art,pack,context,reader,seen):
    stem=context+'.'+reader;base=art/'answers'/stem;rd=pack/context/reader
    runpath=Path(str(base)+'.run.json');run=json.loads(runpath.read_text());roll=Path(run['rollout']);digest=sha(roll)
    if run['rc']!=0 or run['model']!='gpt-6.1-sol' or digest in seen:raise ValueError('failed/model/reused rollout')
    seen.add(digest)
    meta=[r.get('payload',{}) for r in rows(roll) if r.get('type') in ('session_meta','turn_context')]
    if {m['model'] for m in meta if m.get('model')}!={'gpt-6.1-sol'} or {m.get('effort',m.get('reasoning_effort')) for m in meta if m.get('effort',m.get('reasoning_effort'))}!={'medium'}:raise ValueError('model/effort provenance')
    scanned=n1w1_scan_rollout.inspect(roll,rd)
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
    from n1w1_combine import control_matches
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
    from n1w1_sheets import paste_fit, font
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
    output=output or ROOT/'artifacts/n1/n1_v1_w1.jsonl'
    obj=json.loads(registry.read_text());versions=obj['versions'];parent=versions.get('n1w1_admitted_elstat')
    if parent and parent['sha256']!=sha(source):raise ValueError('LQB parent differs')
    jsonl(output,result);output.with_suffix('.sha256').write_text(sha(output)+'  '+output.name+'\n')
    manifest=dict(version='n1_v1_w1',partial=partial,parent=dict(path=str(source),sha256=sha(source)),output=dict(path=str(output),sha256=sha(output),rows=len(result)),edits=sum(len(r['edits']) for r in result),holds=sum(len(r['holds']) for r in result),contexts=contexts,lead=dict(path=str(review/'lead_template.jsonl'),sha256=sha(review/'lead_template.jsonl')),build_sha256=sha(art/'build.json'),decisions_sha256=sha(art/'decisions.jsonl'),scanner_sha256=SCANNER_SHA)
    if partial:manifest['stop_sha256']=sha(art/'STOPPED_AT_70.json')
    dump(output.with_name(output.stem+'_manifest.json'),manifest)
    versions['n1w1_admitted_elstat']=dict(path=str(source),sha256=sha(source),parent=None,text_field='label',id_field='id',status='local')
    versions['n1_v1_w1']=dict(path=str(output),sha256=sha(output),parent='n1w1_admitted_elstat',text_field='label',id_field='id',status='local',population=dict(rows=len(result),partial=partial,definition='admitted W1 ELSTAT numerics population; unresolved slots HOLD'))
    if scorer:manifest['lqb']=scorer(manifest)
    else:manifest['lqb']=dict(registration='n1_v1_w1',registry=str(registry),rescored=False,reason='release-excluded benchmark rows are outside this admitted population')
    dump(registry,obj)
    dump(output.with_name(output.stem+'_manifest.json'),manifest);dump(art/'FINALIZED_RECEIPT.json',manifest);return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','finalize']);p.add_argument('--apply-lead',action='store_true');a=p.parse_args()
    print(json.dumps(build() if a.action=='build' else finalize(apply_lead=a.apply_lead),ensure_ascii=False,indent=2))
