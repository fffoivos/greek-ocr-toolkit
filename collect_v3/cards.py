"""Uniform C1 source/class and fresh C2 class cards in the blind v2 shape."""
from collections import defaultdict
import random,shutil
from pathlib import Path
from .common import rows,read_json,write_json,write_rows,sha,sha_bytes,dumps
from .rules import word_scripts
from .audits import reports

CROP_OK='Exactly one complete printed line, first to last character; other-line/column ink only thin ascender/descender slivers, no readable characters or whole letter bodies.'

def draw(pool,n,seed):return random.Random(seed).sample(sorted(pool,key=lambda r:r['id']),min(n,len(pool)))

def emit(dest,pick,prefix='c'):
    public=[];key={}
    for i,r in enumerate(pick,1):
        from .storage import ensure_crop
        ensure_crop(r)
        cid=f'{prefix}{i:03d}';crop=dest/'crops'/(cid+'.png');crop.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r['crop'],crop)
        if sha(crop)!=r['crop_sha256']:raise ValueError('card crop hash mismatch')
        label=r['label_after_conventions']
        public.append(dict(card_id=cid,crop='crops/'+crop.name,google_text=label,word_scripts=word_scripts(label)))
        key[cid]=dict(line_id=r['id'],source=r['source'],primary_class=r['primary_class'],screen_merged=r['screen_merged'],tags=r['tags'],source_marks=r['source_marks'],literal_label=r.get('literal_label',r.get('fixed_label')),crop_tight_page=r.get('crop_tight_page',False),exclusion_manifest_sha256=r.get('exclusion_manifest_sha256'))
    return public,key

def cards(c,tranche,phase=None):
    phase=phase or ('C1' if tranche=='W1' else 'C2')
    out=Path(c['output_root']);root=out/tranche/phase.lower()
    if not (out/tranche/'features.jsonl').exists():
        from .storage import materialize
        materialize(out,tranche,c['cache'],c['serbian_codec'])
    features=rows(out/tranche/'features.jsonl');pools=defaultdict(list);report=[]
    if phase=='C2' and tranche=='W2':
        # Release caps and the fresh class audit cover all new unique rows,
        # including W1. W2 finalization already dedupes against W1 first.
        if not (out/'W1/features.jsonl').exists() and (out/'W1/pages').exists():
            from .storage import materialize
            materialize(out,'W1',c['cache'],c['serbian_codec'])
        features=rows(out/'W1/features.jsonl')+features
    context=out/'convention_context.json';reports(out,tranche,features,read_json(context) if context.exists() else None)
    blocked=set()
    if phase=='C2':
        spread=read_json(out/tranche/'audits/spread_caps.json')
        blocked={r['primary_class'] for r in spread['rows'] if r['population']=='admitted' and not r['passed']}
        write_json(root/'release_cap_blocks.json',dict(stage='after_dedupe',blocked_classes=sorted(blocked),action='class withheld from release until unique-row book/issue and Gazette-year caps pass'))
    for r in features:
        if r['primary_class'] in blocked:continue
        eligible=r.get('candidate_before_dedupe',r.get('candidate_usable',r.get('usable_final',False))) if phase=='C1' else r['usable_final']
        if eligible:
            pools[(r['source'],r['primary_class'],r.get('gazette_stratum','')) if phase=='C1' else ('release',r['primary_class'],'')].append(r)
    for (source,cls,stratum),pool in sorted(pools.items()):
        seed=f"{c['seed']}:{phase}:{tranche}:{source}:{cls}"+((':'+stratum) if stratum else '');pick=draw(pool,100,seed);name=source+'__'+cls+(('__'+stratum) if stratum else '');dest=root/name
        public,key=emit(dest,pick)
        key.update(_population_sha256=sha_bytes(dumps([r['id'] for r in sorted(pool,key=lambda r:r['id'])]).encode()),_seed=seed,_pool=len(pool),_requested=100,_shortfall=max(0,100-len(pool)),_population='fixed usable, no text exclusions, incl hold; before measured duplicate loss' if phase=='C1' else 'deduped admitted release class')
        write_rows(dest/'cards.jsonl',public);write_json(root/(name+'_key.json'),key)
        # Supplements have their own file, seed, IDs and key. They never enter
        # uniform denominators or the 100-card gate.
        selected={r['id'] for r in pick}
        targeted=[r for r in features if (source=='release' or r['source']==source) and r['primary_class']==cls and (not stratum or r.get('gazette_stratum')==stratum) and r['id'] not in selected and (r.get('assembly_changed') or r.get('lookalike_rule') in ('mapped','excluded') or r.get('roman_fixes') or r.get('roman_ambiguous') or r.get('join_evidence') or r.get('hyphen_test')=='lowercase_continuation_fragment_unknown')]
        supplement=draw(targeted,40,seed+':supplement');sup,supkey=emit(dest,supplement,'s')
        write_rows(dest/'supplement.jsonl',sup);write_json(root/(name+'_supplement_key.json'),dict(_seed=seed+':supplement',_pool=len(targeted),_never_pool_with_uniform=True,**supkey))
        report.append(dict(source=source,primary_class=cls,name=name,gazette_stratum=stratum or None,pool=len(pool),cards=len(pick),seed=seed,shortfall=max(0,100-len(pool)),supplement_cards=len(supplement),supplement_pool=len(targeted)))
    if phase=='C1':
        pagepools=defaultdict(list)
        for p in (out/tranche/'pages').glob('*.json'):
            r=read_json(p)
            if r.get('status')=='completed':pagepools[r['source']].append(r)
        for source,pool in sorted(pagepools.items()):
            seed=f"{c['seed']}:C1:{tranche}:{source}:pages";small=len(pool)<60;pick=sorted(pool,key=lambda r:r['id']) if small else draw(pool,60,seed)
            public=[];key={'_seed':seed,'_pool':len(pool),'_requested':len(pool) if small else 60,'_all_pages_small_pool':small};dest=root/(source+'__pages')
            for i,r in enumerate(pick,1):
                cid=f'p{i:03d}';original=Path(r.get('image') or r['preview']);expected=r['image_sha256'] if r.get('image') else r['preview_sha256']
                if not original.exists():raise ValueError('page-check raster missing; retention contract violated')
                crop=dest/'pages'/(cid+original.suffix);crop.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(original,crop)
                if sha(crop)!=expected:raise ValueError('blind page hash mismatch')
                public.append(dict(card_id=cid,crop='pages/'+crop.name,google_text='',word_scripts=[]))
                key[cid]=dict(page_id=r['id'],item=r['item'],page=r['page'],image_sha256=expected)
            write_rows(dest/'cards.jsonl',public);write_json(root/(source+'__pages_key.json'),key)
            report.append(dict(source=source,stratum='blind_pages',pool=len(pool),cards=len(pick),seed=seed,shortfall=0,all_pages_small_pool=small))
    write_json(root/'receipt.json',dict(tranche=tranche,phase=phase,sampling='uniform seeded sample without replacement from ID-sorted exact eligible population; targeted supplements separate',strata=report,crop_ok_definition=CROP_OK,small_page_pool_rule='all pages when fewer than 60; no shortage',release_assurance='C2 fresh per-class 100; report Wilson lower >=80%, do not gate; W1-to-W2 drift per C1 stratum'))
    return report


def wilson_lower(y,n,z=1.959963984540054):
    if not n:return None
    p=y/n
    return (p+z*z/(2*n)-z*((p*(1-p)/n+z*z/(4*n*n))**.5))/(1+z*z/n)
