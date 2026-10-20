#!/usr/bin/env python3
"""Deterministic offline build; sources read only, packs copied, never linked.
Run with the Python 3.11 / Pillow command documented in README_B1.md.
"""
import argparse, hashlib, io, json, math, random, re, shutil, unicodedata as U
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from common import *
import geometry
geometry.read_json=lambda p: read(p)
from owner39_common import clusters, is_letter, tuple_heads, literal_normalize, options
INPUTS={}
BLOCKERS=[]
INVENTORY={}
YER_OVERRIDES={
    's003': dict(slots={'1':'ь','2':'ь','3':'ъ','4':'ъ','5':'ъ'},
                 provenance='lead pixel review 2026-10-17 12:41 (LEAD_REVIEW.md)')
}

def owner_options(base, anchor, source_id):
    return options(base, anchor, 'accent', 'eff:owner39:options:'+source_id)

def verify_owner_options(data):
    for card in data:
        assert card['options']==owner_options(next(iter(card['options'].values())),card['anchor_index'],card['card_id']), 'owner39 source option mismatch: '+card['card_id']
    return len(data)

def apply_yer_override(meta):
    override=YER_OVERRIDES.get(meta['source_id'])
    if override:
        assert set(meta['expected']['slots'])==set(override['slots'])
        meta['expected']={'slots':dict(override['slots'])}
        meta['provenance']=override['provenance']
    return meta

def bind(p):
    p=Path(p); INPUTS[str(p.resolve())]=sha(p); return p

def read(p): return json.loads(bind(p).read_text())
def load(p): return rows(bind(p))
def stream(p):
    with bind(p).open() as f:
        for line in f:
            if line.strip():yield json.loads(line)
def rgb(p):
    with Image.open(bind(p)) as im: return im.convert('RGB')
def encode(im):
    im=im.convert('RGB'); im.info.clear(); b=io.BytesIO(); im.save(b,format='PNG'); return b.getvalue()
def save_image(im, directory, sub='crops'):
    data=encode(im); name=hashlib.sha256(data).hexdigest()+'.png'; rel=Path(sub)/name
    dest=directory/rel; dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists() and dest.read_bytes()!=data: raise ValueError('image collision')
    if not dest.exists():dest.write_bytes(data)
    return str(rel)
def word_scripts(text):
    result=[]
    for word in text.split():
        scripts=set()
        for c in word:
            if not c.isalpha(): continue
            name=U.name(c,''); scripts.add(next((s for s in ('Greek','Latin','Cyrillic') if s.upper() in name),'Other'))
        result.append([word,next(iter(scripts)) if len(scripts)==1 else 'Mixed' if scripts else 'none'])
    return result

def mask(text):
    # Same boundary rule as the adjudication artifacts: lowercase ъ/ь at a
    # Unicode word boundary; numbering follows left-to-right character order.
    calls=[]
    def replace(m):
        calls.append(m.group()); return '⟦'+str(len(calls))+'⟧'
    return re.sub(r'[ъь]\b',replace,text),calls

def edited(text, kind, rng):
    candidates=[]
    for m in re.finditer(r'\S+',text):
        cc=clusters(m.group()); letters=[i for i,c in enumerate(cc) if is_letter(c[0])]
        if len(letters)<5: continue
        if kind=='letters':
            for i in letters[1:-1]:
                if len(cc[i])==1 and 'GREEK' in U.name(cc[i][0],''):
                    new=cc.copy(); new[i]='λ' if cc[i]=='π' else 'π'
                    candidates.append((m.start(),m.end(),U.normalize('NFC',''.join(new)),m.group()))
        else:
            for i in letters:
                if any(c in cc[i] for c in '\u0301\u0300\u0342'):
                    new=cc.copy(); new[i]=''.join(c for c in cc[i] if c not in '\u0301\u0300\u0342')
                    candidates.append((m.start(),m.end(),U.normalize('NFC',''.join(new)),m.group()))
    if not candidates: return None
    a,b,new,old=rng.choice(candidates)
    return text[:a]+new+text[b:],dict(original_word=old,shown_word=new,offset=a,kind=kind)

def bsb_controls(excluded):
    key=read(RUN/'nlg__poly1850_key.json'); cards=load(RUN/'nlg__poly1850/cards.jsonl')
    verdicts=[r for p in sorted((C1/'verdicts').glob('nlg__poly1850__*.jsonl')) for r in load(p)]
    good={r['card_id'] for r in verdicts if all(r.get(k)=='y' for k in ('letters','marks','crop_ok'))}
    rng=random.Random('sol-reading:bsb:r1'); rng.shuffle(cards); out=[]; used=set(excluded)
    for kind in ['letters']*5+['marks']*5:
        for c in cards:
            cid=c['card_id']; line=key[cid]['line_id']
            if cid not in good or line in used: continue
            edit=edited(c['google_text'],kind,rng)
            if not edit: continue
            text,change=edit; pub=dict(c,google_text=text,word_scripts=word_scripts(text))
            out.append((pub,RUN/'nlg__poly1850',dict(control=True,source_id=cid,line_id=line,expected={kind:'n'},edit=change)))
            used.add(line);break
        else: raise ValueError('Insufficient bsb controls')
    return out

def yer_controls(excluded):
    key=read(RUN/'ia_russian__cyrillic_key.json'); key.update(read(RUN/'ia_russian__cyrillic_supplement_key.json')); cards=load(RUN/'ia_russian__cyrillic/cards.jsonl')+load(RUN/'ia_russian__cyrillic/supplement.jsonl')
    INVENTORY['yer_soft_sign_candidates']=[dict(source_id=c['card_id'],line_id=key[c['card_id']]['line_id'],in_bed=key[c['card_id']]['line_id'] in excluded,text=c['google_text']) for c in cards if mask(c['google_text'])[1] and set(mask(c['google_text'])[1])=={'ь'} and not re.search('[ъѣіѳ]',c['google_text'],re.I)]
    rng=random.Random('sol-reading:yer:r1');rng.shuffle(cards);out=[];used=set(excluded)
    # Publication year, not guessed language date, qualifies pre-1918 lines.
    wanted={m['line_id'] for m in key.values() if isinstance(m,dict) and 'line_id' in m}; features={}
    for r in stream(PROJECTS/'collect-v3-data/run/W1/features.jsonl'):
        if r['id'] in wanted: features[r['id']]=r
    for call in ['ъ']*3+['ь']*3:
        for c in cards:
            cid=c['card_id'];meta=key[cid];line=meta['line_id'];text=c['google_text'];shown,calls=mask(text)
            if line in used or not calls or set(calls)!={call}:continue
            year=None
            if call=='ь' and re.search('[ъѣіѳ]',text,re.I):continue
            if call=='ъ':
                feature=features[line]; page=read(PROJECTS/'collect-v3-data/run/W1/pages'/f'{feature["page_id"]}.json')
                # Source metadata can nest publication dates; inspect explicit year fields.
                def years(obj):
                    out=[]
                    if isinstance(obj,dict):
                        for k,v in obj.items():
                            if k in ('year','publication_year','date') and re.fullmatch(r'\d{4}',str(v)):out.append(int(v))
                            else:out.extend(years(v))
                    elif isinstance(obj,list):
                        for v in obj:out.extend(years(v))
                    return out
                yy=years(page)+years(feature)
                if not yy or not all(y<1918 for y in yy):continue
                year=yy
            pub=dict(item_id=cid,crop=c['crop'],masked_text=shown,slots=len(calls))
            feature=features[line];page=read(PROJECTS/'collect-v3-data/run/W1/pages'/f'{feature["page_id"]}.json')
            meta=dict(row=feature,source_crop=str(RUN/'ia_russian__cyrillic'/c['crop']),response=page['response'],native_size=[page['analysis_page']['width'],page['analysis_page']['height']])
            words,reason=geometry.word_geometry(meta,text)
            masked_words=shown.split();boxes=[w['box'] for w in words if re.search(r'⟦\d+⟧',masked_words[w['word_index']-1])] if not reason else []
            out.append((pub,RUN/'ia_russian__cyrillic',dict(control=True,source_id=cid,line_id=line,expected={'slots':{str(i+1):v for i,v in enumerate(calls)}},publication_years=year,original_text=text,word_boxes=boxes,geometry_reason=reason)))
            used.add(line);break
        else:
            BLOCKERS.append('yer: only two distinct eligible soft-sign C1 lines outside bed (including supplement); requested three; no duplicate or bed-line substitution')
            break
    for _,_,meta in out:apply_yer_override(meta)
    return out

def owner_controls(reuse_images=False):
    candidates=[]
    for deck in ('T2','T4'):
        d=R2/deck; controls=read(d/'private/controls_proposed.json')
        private={r['card_id']:r for r in load(d/'private/key.jsonl')}
        for ctl in controls.get('controls',[]):
            if ctl.get('lead_verified') is not True:continue
            p=private[ctl['card_id']];pub=p['public']
            if set(pub)!=FIELDS['owner39']:continue
            form=ctl['expected_form'];anchor=pub['anchor_index'];ls=[c for c in clusters(form) if is_letter(c[0])]
            heads=tuple_heads(ls[anchor]);marked=any(v!='none' for v in heads.values())
            literal=literal_normalize('NFC',form) not in [literal_normalize('NFC',v) for v in pub['options'].values()]
            candidates.append((deck,p,ctl,heads,marked,literal))
    rng=random.Random('sol-reading:owner39:r1');rng.shuffle(candidates);chosen=[];seen=set()
    for predicate in (lambda x:x[4],lambda x:x[5],lambda x:True,lambda x:True):
        eligible=[x for x in candidates if x[1]['card_id'] not in seen and predicate(x)]
        if not eligible:raise ValueError('STOP owner39: insufficient verified controls/mix')
        x=eligible[0];chosen.append(x);seen.add(x[1]['card_id'])
    out=[]
    for deck,p,ctl,heads,marked,literal in chosen:
        # R2 word_box is already padded by the native renderer. Re-render the
        # saved box with the exact E0 integer <=3x LANCZOS formula.
        native=rgb(R2/deck/'blind'/p['public']['line_image'])
        box=tuple(p['word_box']);crop=native.crop(box);scale=max(1,min(3,math.floor(min(3.,1200/crop.width))))
        zoom=rgb(R2/deck/'blind'/p['public']['word_image']) if reuse_images else crop.resize((crop.width*scale,crop.height*scale),Image.Resampling.LANCZOS)
        original=rgb(R2/deck/'blind'/p['public']['word_image'])
        if original.size!=zoom.size or original.tobytes()!=zoom.tobytes():raise ValueError('STOP owner39: render differs')
        pub=dict(p['public']); pub['options']=owner_options(next(iter(pub['options'].values())),pub['anchor_index'],p['card_id']); pub['_images']={'word_image':zoom,'line_image':native}
        expected=dict(form=ctl['expected_form'],heads=heads,choice=next((k for k,v in pub['options'].items() if U.normalize('NFC',v)==U.normalize('NFC',ctl['expected_form'])),'literal'))
        out.append((pub,R2/deck/'blind',dict(control=True,source_id=p['card_id'],expected=expected,verification=ctl,deck=deck,word_box=box,scale=scale)))
    return out

def review(bed, records, directory):
    controls=[(pub,m) for pub,m in records if m['control']]; tiles=[];md=['# '+bed+' controls — private lead review','', 'Pixel review is required before readers start. Expected calls are planted checks, not new ink adjudication.','']
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/STIXGeneral.otf' if bed=='yer' else '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',19)
    for pub,m in controls:
        p=directory/pub.get('crop',pub.get('word_image'));im=rgb(p)
        if m.get('word_boxes'):
            overlay=ImageDraw.Draw(im)
            for box in m['word_boxes']:overlay.rectangle(box,outline='red',width=2)
        # No approximate geometry is presented as measured word geometry.
        tile=Image.new('RGB',(1600,300),'white'); im.thumbnail((1560,150));tile.paste(im,(20,35));draw=ImageDraw.Draw(tile)
        shown=pub.get('google_text',pub.get('masked_text',json.dumps(pub.get('options'),ensure_ascii=False)))
        expected=json.dumps(m['expected'],ensure_ascii=False)
        for y,text in [(5,pub[idfield(bed)]),(190,'Shown: '+shown),(240,'Expected: '+expected)]:
            for j in range(0,len(text),135):draw.text((20,y+(j//135)*23),text[j:j+135],font=font,fill='black')
        tiles.append(tile);md.extend([f'## {pub[idfield(bed)]}', '',f'Shown: {shown}', '',f'Expected: `{expected}`',''])
        if m.get('provenance'):md.extend(['Provenance: '+m['provenance'],''])
    sheet=Image.new('RGB',(1600,300*len(tiles)),'white')
    for i,t in enumerate(tiles):sheet.paste(t,(0,i*300))
    dest=ROOT/'keys/control_review';dest.mkdir(parents=True,exist_ok=True)
    sheet.save(dest/f'{bed}.png');(dest/f'{bed}.md').write_text('\n'.join(md)+'\n')

def copy_reference():
    cached=Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/eff')
    out=ROOT/'opus_reference';out.mkdir(parents=True,exist_ok=True);sources={}
    paths=[(p,p.name) for p in sorted((cached/'out').glob('*.jsonl')) if p.name.startswith(('bsb_','yer_'))]
    paths += [(cached/n,n) for n in ('usage_log.tsv','agents.tsv')]
    paths += [(p,f'owner39_{p.parent.parent.name}_{p.parent.name}.jsonl') for p in sorted((EFF/'packs/owner39').glob('*/*/answers.jsonl'))]
    for p,name in paths:
        shutil.copyfile(bind(p),out/name);assert sha(p)==sha(out/name);sources[name]={'source':str(p),'sha256':sha(out/name)}
    dump(out/'SHA256_MANIFEST.json',sources)

def check_pack_root():
    # No private artifacts may be created beside the public bed directories.
    if not PACK_ROOT.exists():return
    assert {p.name for p in PACK_ROOT.iterdir()}<=set(FIELDS), 'unexpected PACK_ROOT entry'
    for bed in FIELDS:
        directory=PACK_ROOT/bed
        if directory.exists():
            assert directory.is_dir() and not directory.is_symlink()
            assert {p.name for p in directory.iterdir()}<={'r1','r2','MANIFEST.r1.json','MANIFEST.r2.json'}, 'unexpected bed entry'

def build(reuse_images=False):
    check_pack_root()
    INPUTS.clear(); BLOCKERS.clear(); INVENTORY.clear()
    if not reuse_images:copy_reference()
    mapping=read(EFF/'keys/input_mapping.json'); allrecords={}; packs=[]
    # Binding the design and ports makes implementation provenance reviewable.
    for p in [Path(__file__),ROOT/'tools/owner39_common.py',ROOT/'keys/control_review/LEAD_REVIEW.md',ROOT/'PLAN.md',EFF/'build.py',EFF/'build_owner39.py',EFF/'score.py',EFF/'owner39_score.py',EFF/'owner39_common.py',PROJECTS/'greek-ocr-toolkit-spellcheck-r2cards/scripts/labelfix/r2_cards_prepare.py']:
        if p.exists():bind(p)
    for bed in ('bsb','yer','owner39'):
        src=EFF/'packs'/bed/('E0a' if bed=='owner39' else 'E1')/'r1'; data=load(src/itemfile(bed)); field=idfield(bed)
        records=[(dict(r),src,dict(control=False,source_id=r[field],line_id=mapping.get(bed,{}).get(r[field],{}).get('line_id'))) for r in data]
        excluded={m['line_id'] for _,_,m in records}
        if bed=='bsb':records+=bsb_controls(excluded)
        elif bed=='yer':
            adjud=read(C1/'yer_adjudication/key.json')
            for r in data:
                shown,calls=mask(adjud[r[field]]['google_text']);assert shown==r['masked_text'] and len(calls)==r['slots'],'mask rule mismatch'
            records+=yer_controls(excluded)
        else:
            INVENTORY['owner39_options_reproduced']=verify_owner_options(data)
            records+=owner_controls(reuse_images)
        rng=random.Random(f'sol-reading:{bed}:r1'); rng.shuffle(records); keyed={};public=[]
        for index,(r,base,m) in enumerate(records):
            old=r[field];iid='k'+hashlib.sha256(f'sol-reading:{bed}:r1:id:{index}:{old}:{m["control"]}'.encode()).hexdigest()[:10]
            assert iid not in keyed;r[field]=iid
            if bed=='owner39':
                letters=sorted(r['options']);permuted=letters.copy();rng.shuffle(permuted)
                m['option_to_source']=dict(zip(letters,permuted));r['options']={a:r['options'][b] for a,b in m['option_to_source'].items()}
                if m['control'] and m['expected']['choice']!='literal':m['expected']['choice']=next(a for a,b in m['option_to_source'].items() if b==m['expected']['choice'])
            m['source_public_id']=old;keyed[iid]=m;public.append((r,base,m))
        reader_rows={}
        for reader,ordered in [('r1',public),('r2',list(reversed(public)))]:
            dest=PACK_ROOT/bed/reader;dest.mkdir(parents=True,exist_ok=True);out=[]
            for r,base,m in ordered:
                pub={k:v for k,v in r.items() if k!='_images'}
                for f in ('crop','word_image','line_image'):
                    if f not in pub:continue
                    if '_images' in r:im=r['_images'][f]
                    else:
                        image=base/pub[f]
                        if not image.exists() and f.endswith('_image'):image=base/'img'/pub[f]
                        im=rgb(image)
                    pub[f]=save_image(im,dest,'img' if bed=='owner39' else 'crops')
                assert set(pub)==FIELDS[bed];out.append(pub)
            jsonl(dest/itemfile(bed),out)
            if bed=='owner39':
                for n in ('README.md','answer_schema.json'):shutil.copyfile(bind(src/n),dest/n)
            reader_rows[reader]=[r[field] for r in out]
            packs.append(dict(bed=bed,reader=reader,path=str(dest),items=len(out),control_ids=[r[field] for r in out if keyed[r[field]]['control']]))
            if reader=='r1' and (not reuse_images or bed in ('yer','owner39')):review(bed,[(p,keyed[p[field]]) for p in out],dest)
        dump(ROOT/f'keys/{bed}.json',dict(bed=bed,seed=f'sol-reading:{bed}:r1',r2_seed=f'sol-reading:{bed}:r2',r2_rule='exact reverse; same opaque ids, images and option permutation',readers=reader_rows,items=keyed))
    # Review rendering reads generated images; only read-only source inputs belong here.
    inputs={p:h for p,h in INPUTS.items() if not Path(p).is_relative_to(PACK_ROOT)}
    assert all(sha(p)==h for p,h in inputs.items()),'input changed during build'
    dump(ROOT/'BUILD_RECEIPT_B1.json',dict(inputs=inputs,packs=packs,control_inventory=INVENTORY,choices={
        'order':'random.Random(sol-reading:<bed>:r1).shuffle; r2 exact reverse, shared opaque ids',
        'control_shortfall':BLOCKERS,
        'r2_seed':'reserved; no independent shuffle or permutation, to meet exact reversal',
        'ids':'k plus first 10 SHA256 hex of bed/seed/order/source/control; collisions rejected',
        'images':'RGB re-encode, metadata cleared, filename SHA256 encoded PNG, independent copies',
        'controls':'bsb checks only injected field; yer checks all masked slots; owner39 exact verified form and anchor heads',
        'owner39_verification':'private per-control lead_verified=true overrides stale public summary and initial receipt',
        'owner39_render':'native line + saved padded word_box; E0 integer 1..3 LANCZOS; pixel-equal to original R2 zoom required',
        'yer_geometry':'ported exact OCR token alignment; box masked words only when alignment succeeds; no estimated boxes',
        'source_supplement':'included 40 C1 Russian supplement cards after uniform pool lacked enough eligible controls; still only two outside-bed soft-sign lines',
        'review_pngs':'only keys/control_review; no review artifacts written under PACK_ROOT',
        'lead_review':'lead pixel review 2026-10-17 12:41 (LEAD_REVIEW.md); SR-B1b corrections applied; no readers launched'},git={'before':'50ef367bd886b983da3e03defa42326649622714','target':'55a302d463fcb0f22bcc163211070f4679d230d5','merge':'blocked: sandbox ORIG_HEAD.lock Operation not permitted'}))
    check_pack_root()
    print(json.dumps({'packs':packs},ensure_ascii=False))
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--reuse-images',action='store_true',help='SR-B1b: preserve existing PNGs and reuse saved control zooms')
    build(parser.parse_args().reuse_images)
