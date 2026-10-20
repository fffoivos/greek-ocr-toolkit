"""Seeded item-uniform draws over frozen on-disk A0 frames; no HTTP imports."""
from __future__ import annotations
from collections import Counter,defaultdict
import math,random
from pathlib import Path
from .common import iter_rows,read_json,sha,write_json,write_rows,write_rows_gz
from .config import SPECS,TARGETS,ITEM_CAPS,HOLD
from .exclusions import build

FRAME_NAMES={'bsb_poly1850':('intl','bsb_poly1850'),'nlg':('gr','nlg-digital'),'kosmopolis':('gr','kosmopolis'),'lekythos':('gr','lekythos'),'gazette_modern':('gr','government-gazette'),'elstat':('gr','elstat'),'serbia':('intl','serbian')}

def rng(seed,*parts):return random.Random(':'.join(map(str,(seed,*parts))))

def frames(projects):
    projects=Path(projects);result={};receipts=[]
    ia=projects/'greek-ocr-toolkit-sol-funnel-ia/docs/harvest/sample_v1/ia'
    pop={s:set(read_json(ia/'receipts'/f'population-{p}.json')['population_ids']) for s,p in [('ia_poly1850','poly1850'),('ia_greek_latin','greek_latin'),('ia_russian','cyrillic')]}
    frame=projects/'greek-ocr-toolkit-sol-funnel-ia/docs/harvest/funnel_v1/ia/receipts/catalogue-frame.jsonl.gz'
    for s in pop:result[s]=[]
    for r in iter_rows(frame):
        for s,ids in pop.items():
            if r.get('page_access_status')=='fresh_page_decoded' and r['id'] in ids and (s!='ia_russian' or r.get('cyrillic_language')=='Russian'):
                result[s].append(dict(r,provider='ia',route='ia',bounds_basis=r.get('page_count_basis')))
    receipts.append(dict(path=str(frame),sha256=sha(frame)))
    cached={}
    for s,(t,f) in FRAME_NAMES.items():
        if (t,f) not in cached:
            p=projects/f'greek-ocr-toolkit-sol-funnel-{t}'/'docs/harvest/sample_v1'/t/f'population_{f}.jsonl'
            actual=p if p.exists() else Path(str(p)+'.gz')
            cached[t,f]=list(iter_rows(p));receipts.append(dict(path=str(actual),sha256=sha(actual)))
        rr=cached[t,f]
        if s.startswith('gazette_'):
            lo,hi=1982,1990
            rr=[r for r in rr if r.get('year') and lo<=r['year']<=hi and r.get('official_catalogue_id')]
        if s=='bsb_poly1850':
            rr=[r for r in rr if not any(x in str(r).casefold() for x in ('fraktur',))]
        if s=='kosmopolis':rr=[r for r in rr if r['id']=='xrysallis-4141' or 1900<=int(r.get('year') or 0)<=1982]
        result[s]=[dict(r,provider=('bsb' if s=='bsb_poly1850' else 'serbia' if s=='serbia' else 'gazette' if s.startswith('gazette') else s),route=SPECS[s][2]) for r in rr]
    from bs4 import BeautifulSoup
    from .common import sha_bytes
    import re
    base=projects/'greek-ocr-toolkit-sol-funnel-gr/docs/harvest/sample_v1/gr'
    for r in result['kosmopolis']:
        body=base/'bulk/metadata'/(sha_bytes(r['catalogue_url'].encode())+'.body')
        if not body.exists():continue
        soup=BeautifulSoup(body.read_bytes(),'html.parser');leaves=set()
        for obj in soup.select('.obj_article_summary'):
            pg=obj.select_one('.pages');galley=obj.select_one('a.obj_galley_link[href]')
            numbers=re.findall(r'\d+',pg.get_text(' ',strip=True)) if pg else []
            if galley and numbers:
                first=int(numbers[0]);last=int(numbers[1]) if len(numbers)>1 else first
                if 0<=last-first<500:leaves.update(range(first,last+1))
        if leaves:
            start=min(leaves);r.update(page_count=max(leaves)-start+1,valid_leaves=[x-start+1 for x in sorted(leaves)],bounds_basis='cached own issue catalogue page spans',bounds_input_sha256=sha(body))
            receipts.append(dict(path=str(body),sha256=sha(body)))
    return result,receipts

def bounds(item):
    if item.get('valid_leaves') is not None:return list(item['valid_leaves'])
    n=int(item.get('page_count') or item.get('imagecount') or 0)
    return list(range(0,n)) if item.get('route')=='ia' and n else list(range(1,n+1)) if n else None

def split_waves(page_rows,total):
    """Spread W1 across the same uniformly drawn books as W2."""
    groups=defaultdict(list)
    for r in page_rows:groups[r['item']].append(r)
    first=set()
    for rr in groups.values():first.update(r['id'] for r in rr[:len(rr)//5])
    for rr in groups.values():
        if len(first)>=total//5:break
        for r in rr:
            if r['id'] not in first:first.add(r['id']);break
    if len(first)!=total//5:raise ValueError('cannot split wave quotas')
    for r in page_rows:r['tranche']='W1' if r['id'] in first else 'W2'
    return page_rows

def gazette_draws(pool,seed,price,digest):
    """40 early probe + 200 measured W1; W2 defaults to measured years only."""
    groups={year:sorted([r for r in pool if r['year']==year],key=lambda r:r['id']) for year in range(1982,1991)}
    for year,items in groups.items():rng(seed,'gazette_modern',year).shuffle(items)
    def make(item,tranche):
        bb=bounds(item);page=rng(seed,'gazette_modern',item['id'],'pages').choice(bb) if bb else None
        return dict(id='gazette_modern--'+__import__('hashlib').sha256(item['id'].encode()).hexdigest()[:16]+'--s000',source='gazette_modern',tranche=tranche,item=item['id'],item_record=item,item_pages=1,page=page,page_slot=0,page_seed=f"{seed}:gazette_modern:{item['id']}:pages",resolve_at_run=bb is None,bounds_basis=item.get('bounds_basis','provider PDF needed'),seed=seed,route='gazette',rights={k:item.get(k) for k in ('rights','licence_string','catalogue_url')},projected_micro_usd=price,exclusion_manifest_sha256=digest,crop_tight_page=True,gazette_stratum='probe_1982_1985' if item['year']<=1985 else 'measured_1986_1990')
    w1=[]
    for year,items in groups.items():
        n=10 if year<=1985 else 40
        if len(items)<n+192:raise ValueError('Gazette year capacity shortfall')
        w1.extend(make(item,'W1') for item in items[:n]);groups[year]=items[n:]
    baseline=[make(item,'W2') for year in range(1986,1991) for item in groups[year][:192]]
    alternative=[]
    for slot in range(960):
        year=1982+slot%9;alternative.append(make(groups[year][slot//9],'W2'))
    return w1+baseline,alternative

def plan(c,projects):
    out=Path(c['output_root']);out.mkdir(parents=True,exist_ok=True)
    ff,inputs=frames(projects);ex=build(projects,out,ff,inputs)
    exclusion_hash=sha(out/'exclusions_manifest.json')
    manifest=[];summary=[];inventory=[];excluded=Counter();drawn_items=set()
    for source,spec in SPECS.items():
        total,minitems,route,_,yields=spec;pool=[];statuses=Counter();hits_count=Counter()
        frame=sorted({r['id']:r for r in ff[source]}.values(),key=lambda r:r['id'])
        for r in frame:
            status,hits=ex.resolve(r,r['provider'],source)
            statuses[status]+=1;hits_count.update(hits)
            if status!='eligible':excluded.update(hits);continue
            pool.append(r)
        quota=min(ITEM_CAPS.get(source,40),math.ceil(total/minitems))
        if source=='kosmopolis':quota=40
        known=[r for r in pool if bounds(r) is not None];unknown=[r for r in pool if bounds(r) is None]
        inv=dict(source=source,frame_items=len(frame),excluded_items=statuses['excluded'],quarantined_items=statuses['quarantined'],remaining_items=len(pool),known_bound_items=len(known),unknown_bound_items=len(unknown),known_pages=sum(len(bounds(r)) for r in known),known_capped_pages=sum(min(quota,len(bounds(r))) for r in known),unknown_page_slots_upper_bound=len(unknown)*quota,item_page_cap=quota,exact_page_total=None if unknown else sum(len(bounds(r)) for r in known),exclusion_manifest_sha256=exclusion_hash,exclusion_hits_per_key=dict(hits_count))
        inventory.append(inv)
        write_rows_gz(out/'remaining_inventory'/f'{source}.jsonl.gz',[dict(item=r['id'],provider=r['provider'],page_count=len(bounds(r)) if bounds(r) is not None else None,capped_pages=min(quota,len(bounds(r))) if bounds(r) is not None else None) for r in pool])
        # Uniform item draws within year strata; round robin bounds every year.
        if source=='gazette_modern':
            groups=defaultdict(list)
            for r in pool:groups[r['year']].append(r)
            if set(groups)!=set(range(1982,1991)):raise ValueError('Gazette needs all nine year strata')
            for year,rs in groups.items():rng(c['seed'],source,year).shuffle(rs)
            order=[]
            while any(groups.values()):
                for year in sorted(groups):
                    if groups[year]:order.append(groups[year].pop())
        else:order=rng(c['seed'],source,'items').sample(pool,len(pool))
        # The one pre-1900 issue has an explicit <=40-page subquota. It is
        # independently uniform in pages; later issues remain uniformly ordered.
        if source=='kosmopolis':
            pre=[r for r in order if r['id']=='xrysallis-4141']
            if len(pre)!=1:raise ValueError('remaining pre-1900 Kosmopolis issue unavailable')
            order=pre+[r for r in order if r['id']!='xrysallis-4141']
        left=total;source_rows=[];used=[];portable_order=[]
        for rank,item in enumerate(order):
            rights=dict({k:item.get(k) for k in ('scan_rights','text_rights','licence_string','rights','rights_declaration','access_terms_url','catalogue_url')},provider_rights=(item.get('metadata') or {}).get('Право коришћења'),cloud_ocr_retention_note='page raster and Google line/token geometry retained; per-item rights recorded, not a gate',status='A0 declarations retained; missing fields unresolved; not independently verified')
            portable_order.append(dict(item_record=item,item_rank=rank,quota=quota,page_seed=f"{c['seed']}:{source}:{item['id']}:pages",rights=rights,exclusion_manifest_sha256=exclusion_hash))
        for entry in portable_order:
            if not left:break
            item=entry['item_record'];rank=entry['item_rank']
            if (item['provider'],item['id']) in drawn_items:continue
            bb=bounds(item);n=min(quota,left,len(bb) if bb is not None else quota)
            if not n:continue
            chosen=rng(c['seed'],source,item['id'],'pages').sample(bb,n) if bb is not None else [None]*n
            item_key=source+'--'+__import__('hashlib').sha256(item['id'].encode()).hexdigest()[:16]
            used.append(item['id']);drawn_items.add((item['provider'],item['id']))
            for slot,page in enumerate(chosen):
                tranche='W1' if len(source_rows)<total//5 else 'W2'
                source_rows.append(dict(id=f'{item_key}--s{slot:03d}',source=source,tranche=tranche,item=item['id'],item_record=item,item_rank=rank,item_pages=n,page=page,page_slot=slot,page_seed=entry['page_seed'],resolve_at_run=bb is None,bounds_basis=item.get('bounds_basis') or ('A0 page_count' if bb is not None else 'provider manifest/PDF needed'),seed=c['seed'],route=route,rights=entry['rights'],projected_micro_usd=c['page_micro_usd'],exclusion_manifest_sha256=exclusion_hash,crop_tight_page=source in HOLD))
            left-=n
        if left:raise ValueError(f'{source}: frame capacity is {total-left}, below {total}')
        # Full portable stream is saved even with known bounds, for validation.
        write_rows_gz(out/'item_draws'/f'{source}.jsonl.gz',portable_order)
        if source=='gazette_modern':
            source_rows,alternative=gazette_draws(pool,c['seed'],c['page_micro_usd'],exclusion_hash)
            write_rows(out/'W2_gazette_probe_qualified.jsonl',alternative)
        else:split_waves(source_rows,total)
        manifest+=source_rows
        summary.append(dict(source=source,frame=len(frame),eligible_items=len(pool),items=len(used),total_pages=total,W1_pages=total//5,W2_pages=total-total//5,W1_usd=total//5*.0015,W2_usd=(total-total//5)*.0015,W1_resolve_at_run=sum(r['resolve_at_run'] for r in source_rows if r['tranche']=='W1'),rows_W1={k:round(v*total/5,2) for k,v in yields.items()},rows_full={k:round(v*total,2) for k,v in yields.items()},crop_tight_page=source in HOLD,item_page_cap=quota))
    for source_summary in summary:
        if source_summary['source']=='gazette_modern':
            rates=SPECS['gazette_modern'][4]
            source_summary['rows_full_measured_equivalent_ceiling']=source_summary['rows_full']
            source_summary['rows_W1']={k:round(v*200,2) for k,v in rates.items()}
            source_summary['rows_full']={k:round(v*1160,2) for k,v in rates.items()}
            source_summary['unmeasured_probe_pages']=40
            source_summary['projection_scope']='Default W2 branch: 1160 measured-stratum pages plus 40 unprojected W1 probe pages. Alternate W2 needs new C1 yield estimates.'
    for t in ('W1','W2'):write_rows(out/f'{t}_manifest.jsonl',[r for r in manifest if r['tranche']==t])
    books=defaultdict(list)
    for row in manifest:
        if row['source']=='ia_poly1850':books[row['item']].append(row)
    if len(books)<40 or max(map(len,books.values()))>40:raise ValueError('IA poly1850 needs >=40 books and <=40 pages/book')
    def cell(value):return str(value).replace('|','\\|').replace('\n',' ')
    book_table=['# IA poly1850 planned books (rev 2.2)','',
                'Frozen offline draw; no collection. 1,600 pages, at least 40 books, at most 40 pages/book. W1 is 20% per source. The 10% new-poly1850-row cap is enforced after dedupe at C2; equal page quotas do not prove row shares.', '',
                '| ID | Title | Year | Planned pages | W1 pages |','|---|---|---:|---:|---:|']
    for item,rr in sorted(books.items()):
        meta=rr[0]['item_record'];book_table.append('| '+' | '.join(map(cell,(item,meta.get('title',''),meta.get('year',''),len(rr),sum(r['tranche']=='W1' for r in rr))))+' |')
    (out/'ia_poly1850_books.md').write_text('\n'.join(book_table)+'\n')
    projected=Counter();projected_w1=Counter();without_hold=Counter()
    for r in summary:
        projected.update(r['rows_full']);projected_w1.update(r['rows_W1'])
        if not r['crop_tight_page']:without_hold.update(r['rows_full'])
    comparisons={k:dict(target=v,candidate_rows=round(projected[k],2),candidate_rows_without_hold=round(without_hold[k],2),ratio=round(projected[k]/v,3),W1_candidate_rows=round(projected_w1[k],2)) for k,v in TARGETS.items()}
    w1=sum(r['tranche']=='W1' for r in manifest);w2=len(manifest)-w1
    receipt=dict(schema='collect-v3-plan-rev2.2',seed=c['seed'],algorithm='uniform seeded item permutation; uniform leaves without replacement; Gazette W1 40 probe/200 measured, W2 measured unless C1 qualifies probe; Kosmopolis explicit sole pre-1900 issue subquota',network=False,provider_calls=0,spend_usd=0,sources=summary,total_pages=len(manifest),W1_pages=w1,W1_projected_usd=w1*.0015,W1_cap_usd=c['caps_usd']['W1'],W2_pages=w2,W2_projected_usd=w2*.0015,W2_cap_usd=c['caps_usd']['W2'],class_projection=comparisons,inputs=inputs,exclusion_manifest_sha256=exclusion_hash,exclusion_hits=dict(excluded),remaining_inventory=inventory,notes=['Exact inventory counts refer to the frozen eligible frame, not estimated provider-wide supply. Unknown physical page bounds are explicit and are resolved before reads.','IA uses F1 individually decoded candidate editions, not the much larger metadata-only A0 population.','Latin projection is the 8000 subsample target; BSB mixed and Gazette <=1981 are excluded.','Crop-tight rows are not admitted. Class totals are candidates, not measured quality.'])
    receipt['gazette']=dict(frame_issues=37764,measured_years=[1986,1990],probe_years=[1982,1985],W1_probe_pages=40,W1_measured_pages=200,W2_default_years=[1986,1990],projection_denominator_pages=12,measured_rows=dict(modern_scanned=525,numerics_tables=67,headings_caps=57,dialogue_fiction=36),projection_scope='Rates measured only in 1986-1990; full-1200-page figures are conditional measured-equivalent ceilings, not measured early-year yields.',W1_measured_projection={k:round(v*200,2) for k,v in SPECS['gazette_modern'][4].items()},probe_yield=None)
    write_json(out/'remaining_inventory.json',dict(exclusion_manifest_sha256=exclusion_hash,sources=inventory))
    table=['# Remaining inventory after frozen exclusions','', 'Exact item counts in the offline frame. Known pages are catalogue bounds; unknown bounds are not estimated as physical pages.','', '| Source | Frame | Excluded | Quarantined | Remaining | Known pages | Known capped pages | Unknown items | Unknown slots (upper bound) |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in inventory:table.append('| '+' | '.join(str(r[k]) for k in ('source','frame_items','excluded_items','quarantined_items','remaining_items','known_pages','known_capped_pages','unknown_bound_items','unknown_page_slots_upper_bound'))+' |')
    (out/'REMAINING_INVENTORY.md').write_text('\n'.join(table)+'\n')
    plan_base=Path(projects)/'greek-page-ocr/docs/ocr_program_2026-10-06'
    reviewed=[plan_base/'SOURCING_T5_COLLECTION_PLAN_20261016.md',plan_base/'SOURCING_T5_CP5_REPLY_20261017.md',Path(projects)/'greek-ocr-toolkit-sol-funnel-gr/docs/harvest/blind_checks_v1/v2r/lookalike_rule.py',Path(projects)/'greek-ocr-toolkit-sol-funnel-gr/docs/harvest/blind_checks_v1/v2/LABEL_CHECK_v2.md']
    receipt['read_only_requirements']=[dict(path=str(p),sha256=sha(p)) for p in reviewed]
    write_json(out/'plan_receipt.json',receipt)
    return receipt
