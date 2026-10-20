"""Offline evidence curation. No network requests or OCR."""
from funnellib import *
from collections import Counter,defaultdict
from bs4 import BeautifulSoup
import unicodedata
from greekocr.harvest.openarchives import canonical_url,metadata

def norm(s):
    s=unicodedata.normalize('NFD',str(s or '')).lower()
    return ''.join(c for c in s if c.isalnum() and not unicodedata.combining(c))

def overlap():
    ids=set();testids=set();urls=set();testurls=set();titles=set();testtitles=set();files=[]
    coll=MAIN/'docs/harvest/collection'
    for p in [coll/'import_real_all.jsonl',coll/'v2/import_real_v2_all.jsonl',coll/'v2/import_real_v2_test.jsonl']:
        if not p.exists():continue
        files.append(dict(path=str(p),sha256=sha(p.read_bytes()),bytes=p.stat().st_size))
        with p.open() as f:
            for line in f:
                r=json.loads(line);doc=r.get('doc','');ident=doc.split(':')[-1]
                ids.add(ident)
                u=r.get('source_url');test='test' in p.name or r.get('split') in ['test','reserved']
                if test:testids.add(ident)
                if u:
                    urls.add(canonical_url(u))
                    if test:testurls.add(canonical_url(u))
    # Edition metadata supplements line manifests; never copy labels into receipts.
    for wave in ['round1','mixed','cyrillic','openarchives','wikisource']:
        root=MAIN/'docs/harvest'/wave
        for p in [root/'books.json',root/'selection.json',root/'holdout_books.json']:
            if not p.exists():continue
            d=json.loads(p.read_text());files.append(dict(path=str(p),sha256=sha(p.read_bytes()),bytes=p.stat().st_size))
            rr=d if isinstance(d,list) else d.get('books',[]) if isinstance(d,dict) else []
            for r in rr:
                if not isinstance(r,dict):continue
                key=r.get('key') or r.get('book_key') or r.get('book')
                if key:ids.add(key)
                title=norm(r.get('title'));test=r.get('split') in ['test','reserved']
                if len(title)>12:titles.add(title)
                if test:
                    if key:testids.add(key)
                    if title:testtitles.add(title)
                for k in ['pdf_url','source_url','record_url']:
                    if r.get(k):
                        urls.add(canonical_url(r[k]))
                        if test:testurls.add(canonical_url(r[k]))
    write(BASE/'receipts/overlap-inputs.json',dict(inputs=files,collected_ids=len(ids),heldout_ids=len(testids),collected_urls=len(urls),heldout_urls=len(testurls),collected_titles=len(titles),test_titles=len(testtitles),method='Exact ID/URL and normalized title screening; cross-repository edition equivalence remains unresolved. No label text copied.'))
    return ids,testids,urls,testurls,titles,testtitles

def curate():
    ids,testids,urls,testurls,titles,testtitles=overlap()
    allpages=rows(BASE/'probe_pages.jsonl');byitem=defaultdict(list)
    physical_map={r['item']:r['physical_pages'] for r in rows(BASE/'receipts/media.jsonl') if r['source']=='openarchives' and r.get('physical_pages') and r.get('mode')!='concurrency3'}
    rechecks={r['id']:r for r in rows(BASE/'receipts/physical-rechecks.jsonl') if r.get('success')}
    rebound=json.loads((BASE/'receipts/oa-projection-rebinding.json').read_text()) if (BASE/'receipts/oa-projection-rebinding.json').exists() else {}
    rebound={r['id']:r for r in rebound.get('documents',[])}
    for r in allpages:byitem[(r['source'],r.get('book_key') if r['source']=='anemi' else r['item'])].append(r)
    hash_items=defaultdict(set)
    for p in allpages:hash_items[p['image_sha256']].add((p['source'],p.get('book_key',p['item']) if p['source']=='anemi' else p['item'],p.get('source_page',p['page'])))
    duplicate_pages=defaultdict(list);duplicate_groups=[]
    for digest,items in hash_items.items():
        if len({(i[0],i[1]) for i in items})<=1:continue
        ordered=sorted(items);owner=ordered[0];duplicate_groups.append(dict(image_sha256=digest,owner=owner,witnesses=ordered))
        for src,item,page in ordered[1:]:duplicate_pages[(src,item)].append(dict(page=page,duplicate_of=owner,image_sha256=digest))
    write(BASE/'receipts/exact-page-overlap.json',dict(method='Exact retained grayscale JPEG hashes across items; no near-duplicate or rescan equivalence inferred',groups=duplicate_groups,groups_count=len(duplicate_groups)))
    # Manual physical script assessment is bound to the reviewed page hashes.
    review={}
    for p in sorted((BASE/'receipts/review').glob('*.json')):
        d=json.loads(p.read_text());src=d['source']
        for e in d['entries']:
            pos=e['position'];assessment=None
            if src=='openarchives' and p.name.startswith('openarchives-bound-'):
                assessment='non-Greek manuscript on selected leaf' if pos==14 else 'Greek visible'
            elif src=='openarchives' and p.name=='openarchives-1.json' and pos<=20:
                assessment='Greek visible' if pos not in [6,9,16] else 'Latin only' if pos==9 else 'English only' if pos==16 else 'uncertain poster script'
            elif src=='nlg-digital' and pos<=20:assessment='English only' if pos in [17,18] else 'Greek visible with Latin/Italian' if pos==20 else 'Greek visible'
            elif src in ['kosmopolis','pleias','pergamos','lekythos','elstat','bank-of-greece']:assessment='Greek visible'
            elif src=='anemi':assessment='French only on selected leaf' if pos==1 else 'Greek visible'
            elif src=='government-gazette':assessment='blank sampled leaf; script unverified' if pos in [9,11,13] else 'Greek visible'
            if assessment:
                review[(src,e['item'])]=dict(assessment=assessment,page=e['page'],image_sha256=e['image_sha256'],review_sheet=d['sheet'])
    raw=[]
    for path in BASE.glob('candidates_*.jsonl'):
        src=path.stem[len('candidates_'):];unique={r['id']:r for r in rows(path)};out=[]
        for r in unique.values():
            derived={'held_out_test_do_not_propose','sample_not_verified_Greek','Greek_script_not_verified_on_fetched_leaf','outside_target_poly_period','prior_metadata_projection_revision_unbound','target_period_unresolved','exclude_generated_metadata_cover_from_scanned_supply','not_verified_scanned','all_pages_duplicate_of_other_candidate'}
            r['restriction_flags']=[x for x in r.get('restriction_flags',[]) if x not in derived]
            freshpath=BASE/'receipts/oa-catalogue-rebinding'/(r['id']+'.json')
            if src=='openarchives' and freshpath.exists():
                fresh=json.loads(freshpath.read_text())
                if fresh.get('verified'):
                    r.setdefault('unbound_metadata_title',r.get('title'));r.setdefault('unbound_metadata_year',r.get('year'))
                    r['title']=fresh['title'];r['year']=fresh.get('year');r['decade']=r['year']//10*10 if r['year'] else None
                    r['collection_slug']=fresh['collection_slug'];r['link_table_bound']=True;r['metadata_identity_bound']=True
                    r['catalogue_url']=fresh['catalogue_url'];r['metadata_identity_basis']='Fresh catalogue title/date plus exact offered PDF attachment-path match and revision-pinned HF link table'
                    r['metadata_binding_receipt']=str(freshpath.relative_to(BASE));r['language_tag']=fresh.get('language')
                    oldpipe=r.get('pipeline_metadata',{})
                    if 'binding' not in oldpipe:r['unbound_pipeline_metadata']={k:oldpipe.get(k) for k in ['ocr_success','page_count','polytonic_ratio']}
                    r['pipeline_metadata']={'binding':'unresolved; prior projection not used as document metadata'}
                    r['licence_string']=fresh.get('licence');r['scan_rights']=fresh.get('licence') or 'per repository unresolved'
                    r['access_terms_url']=fresh['catalogue_url']
            pages=byitem[(src,r['id'])];r['fresh_pages_decoded']=len({(p.get('source_page',p['page']),p['image_sha256']) for p in pages})
            r['decoded_page_receipts']=[dict(page=p.get('source_page',p['page']),image_sha256=p['image_sha256'],fetch_sha256=p['fetch_sha256']) for p in pages[:12]]
            if src in ['kosmopolis','pleias']:
                parts=urlsplit(r['page_access_route']);m=re.search(r'/article/(?:download|view)/(\d+)',parts.path)
                if m:
                    article=parts.scheme+'://'+parts.netloc+re.sub(r'/article/(?:download|view)/.*','/article/view/'+m[1],parts.path)
                    p=BASE/'bulk/metadata'/(sha(article.encode())+'.body')
                    if p.exists():
                        soup=BeautifulSoup(p.read_bytes(),'html.parser');date=soup.select_one('meta[name=citation_date]')
                        if date:
                            ys=re.findall(r'\b(18\d\d|19\d\d|20\d\d)\b',date.get('content',''))
                            if ys:r['year']=int(ys[0]);r['decade']=r['year']//10*10;r['year_basis']='article citation_date'
            rid=r['id'];route=canonical_url(r['page_access_route']);title=norm(r.get('title'))
            possible_id=next((i for i in ids if i and (rid.startswith(i) or i.startswith(rid))),None)
            possible_test=next((i for i in testids if i and (rid.startswith(i) or i.startswith(rid))),None)
            exact=bool(possible_id or route in urls);titlehit=len(title)>12 and title in titles
            held=bool(possible_test or route in testurls or (len(title)>12 and title in testtitles))
            r['held_out_test']=held;r['overlap_flag']='held-out test or possible same title' if held else 'collected' if exact or titlehit else 'no exact ID/URL/title match; edition not certified'
            r['overlap_evidence']=dict(exact_id=possible_id,exact_url=route in urls,normalized_title=titlehit,cross_source_edition_review='unresolved')
            if held:r['restriction_flags']=list(set(r.get('restriction_flags',[])+['held_out_test_do_not_propose']))
            reviewed=review.get((src,rid));r['script_review']=reviewed
            if reviewed:r['language_script_evidence']=reviewed['assessment']+' on fresh page '+str(reviewed['page'])
            if reviewed and not reviewed['assessment'].startswith('Greek'):r['restriction_flags'].append('sample_not_verified_Greek')
            if src=='openarchives':
                refined=rechecks.get(rid);physical_pages=refined['physical_pages'] if refined else physical_map.get(rid,[])
                ph=Counter(p['classification'] for p in physical_pages) if physical_pages else r.get('physical_classifications',{})
                r['physical_classifications']=dict(ph)
                scan=document_scan(physical_pages,r['page_access_route']);r['physical_scan_evidence']=scan
                r['physical_scanned_sample']=scan['scanned_body_verified']
                if refined:r['physical_refinement_receipt']='receipts/physical-rechecks.jsonl';r['physical_refinement_PDF_sha256']=refined['PDF_sha256']
                if scan['generated_wrapper_pages']:r['restriction_flags'].append('exclude_generated_metadata_cover_from_scanned_supply')
                r['metadata_identity_bound']=r.get('link_table_bound',False)
                if not r['metadata_identity_bound']:
                    r['restriction_flags'].append('prior_metadata_projection_revision_unbound')
                    r.setdefault('unbound_metadata_year',r.get('year'));r.setdefault('unbound_metadata_title',r.get('title'))
                    r['year']=None;r['decade']=None
                    rb=rebound.get(rid)
                    if rb:
                        r['projection_collection_slug']=rb['projection_collection'];r['collection_slug']=rb['link_table_collection_unambiguous']
                        r['link_table_exact_URL_bound']=True
                    r['target_classes']=[]
                # Full scan documents only; label/script/date uncertainty remains visible.
                if not r['physical_scanned_sample']:r['target_classes']=[]
                elif r['metadata_identity_bound']:
                    year=r.get('year');classes=['headings']
                    if year and 1850<=year<=1890:classes.insert(0,'poly1850')
                    elif year and 1900<=year<=1982:classes.insert(0,'poly1900')
                    elif year and year>=1983:classes.insert(0,'modern')
                    else:r['restriction_flags'].append('target_period_unresolved')
                    r['target_classes']=classes
            if src=='bank-of-greece':r['target_classes']=[];r['restriction_flags'].append('sampled_reports_born_digital_or_scan_unconfirmed')
            if src=='elstat':
                physical=[p.get('physical',{}).get('classification') for p in pages]
                r['physical_scanned_sample']=bool(physical) and all(str(x).startswith('scanned_') for x in physical)
                r['target_classes']=['numerics','leaders','modern'] if r['physical_scanned_sample'] else []
                if not r['physical_scanned_sample']:r['restriction_flags'].append('not_verified_scanned')
            if src in ['kosmopolis','pleias']:r['target_classes']=['headings','dialogue']
            if src=='pergamos':r['target_classes']=['headings'] if r.get('public_type')=='ArchivalBook' else []
            if src=='nlg-digital':r['target_classes']=['headings']
            if src=='anemi':r['target_classes']=['dialogue']
            if src=='government-gazette':
                r['target_classes']=['numerics','headings','leaders']
                if r.get('year') and 1850<=r['year']<=1890:r['target_classes'].append('poly1850')
                elif r.get('year') and 1900<=r['year']<=1982:r['target_classes'].append('poly1900')
            if src=='lekythos':r['target_classes']=['poly1900','dialogue','headings']
            if src in ['kosmopolis','pleias','pergamos','nlg-digital','anemi']:
                classes=[x for x in r.get('target_classes',[]) if x not in ['poly1850','poly1900','historical_other']]
                if r.get('year') and 1850<=r['year']<=1890:classes.insert(0,'poly1850')
                elif r.get('year') and 1900<=r['year']<=1982:classes.insert(0,'poly1900')
                else:r['restriction_flags'].append('outside_target_poly_period')
                r['target_classes']=classes
            if reviewed and not reviewed['assessment'].startswith('Greek'):r['target_classes']=[]
            r['new_candidate_eligible']=not held and not(exact or titlehit) and bool(r.get('target_classes'))
            if src=='openarchives' and not r.get('metadata_identity_bound'):r['new_candidate_eligible']=False
            if src=='nlg-digital' and not reviewed:r['new_candidate_eligible']=False;r['restriction_flags'].append('Greek_script_not_verified_on_fetched_leaf')
            r['candidate_status']='funnel only; physical access demonstrated, usable rows and Google output unmeasured'
            if r.get('page_count') is not None:r['pages_at_cap40']=min(40,max(0,int(r['page_count'])-len(r.get('physical_scan_evidence',{}).get('generated_wrapper_pages',[]))))
            else:r['pages_at_cap40']=min(40,r.get('published_page_count') or r['fresh_pages_decoded'])
            if src=='anemi':r['new_candidate_eligible']=False;r['proposed_for_collection']=False
            duplicates=duplicate_pages[(src,r['id'])];r['known_cross_item_duplicate_pages']=duplicates
            if r.get('page_count') and len(duplicates)>=r['page_count'] and r['fresh_pages_decoded']>=r['page_count']:
                r['new_candidate_eligible']=False;r['restriction_flags'].append('all_pages_duplicate_of_other_candidate')
            r['restriction_flags']=sorted(set(r['restriction_flags']))
            r['pages_at_cap40']=min(40,max(0,int(r.get('page_count') or r.get('published_page_count') or r['fresh_pages_decoded'])-len(r.get('physical_scan_evidence',{}).get('generated_wrapper_pages',[]))-len(duplicates)))
            out.append(r);raw.append(r)
        path.write_text(''.join(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n' for r in out))
    write(BASE/'receipts/script-review.json',dict(method='Visual script check on fresh decoded page; no OCR model used',sample=[dict(source=k[0],item=k[1],**v) for k,v in review.items()],counts=[dict(source=src,n=sum(k[0]==src for k in review),Greek_visible=sum(k[0]==src and v['assessment'].startswith('Greek') for k,v in review.items())) for src in sorted({k[0] for k in review})],limitation='Visible script on one leaf does not establish all pages, within-line mixing, usable lines, or modern language versus Ancient Greek.'))
    print('curated',len(raw),'fresh access items;',sum(r['new_candidate_eligible'] for r in raw),'new class candidates;',sum(r['held_out_test'] for r in raw),'held-out flags')

if __name__=='__main__':curate()
