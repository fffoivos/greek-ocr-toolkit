"""Stratified physical-PDF audit; prior projection is explicitly revision-unbound."""
from funnellib import *
from greekocr.harvest.openarchives import urls,metadata,extract_year,canonical_url
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor
import html,sys

CACHE=MAIN/'docs/harvest/harvest_big/openarchives'

def select():
    prior=rows(MAIN/'docs/harvest/collection/import_real_all.jsonl')
    oldbooks=json.loads((MAIN/'docs/harvest/openarchives/books.json').read_text())
    excluded={b['pdf_url'] for b in oldbooks}
    counts=Counter();periods=Counter();pools=defaultdict(list)
    with (CACHE/'doc_metadata.jsonl').open() as f:
        for line in f:
            r=json.loads(line);s=r['source_metadata'];p=r['pipeline_metadata'];slug=s.get('collection_slug')
            if not p.get('ocr_success'):continue
            links=urls(s.get('pdf_links_json'))
            if not links:continue
            m=metadata(s.get('metadata_json'));year,yr=extract_year(m)
            counts[slug]+=1;periods[(slug,year//10*10 if year else None)]+=1
            if links[0] in excluded or slug in ['elstat']:continue
            title=next((str(m[k]) for k in ['Τίτλος','Title','title','dc.title'] if m.get(k)),s.get('filename',''))
            ident=sha((str(slug)+'\n'+canonical_url(links[0])).encode())
            pools[slug].append(dict(id=ident[:16],document_id=ident,title=title,year=year,year_evidence=yr,collection_slug=slug,
                                   pdf_url=html.unescape(links[0]),source_metadata=s,pipeline_metadata=p,
                                   metadata_projection_warning='Prior projection extraction revision unbound; PDF identity requires physical title/date verification.'))
    chosen=[]
    for slug,pool in sorted(pools.items(),key=lambda x:-len(x[1])):
        pool.sort(key=lambda r:(not(r['year'] and r['year']<2000),not(r['year'] and r['year']>=1950),r['pipeline_metadata'].get('page_count',9999) or 9999,r['id']))
        # Unique documents, not repeated aliases.
        seen=set();keep=[]
        for r in pool:
            if r['pdf_url'] not in seen:keep.append(r);seen.add(r['pdf_url'])
            if len(keep)>=12:break
        chosen.extend(keep)
    write(BASE/'receipts/oa-local-census.json',dict(counts_by_collection=counts,decades=[dict(collection=k[0],decade=k[1],ocr_success_metadata_count=v) for k,v in periods.items()],projection_sha256=sha((CACHE/'doc_metadata.jsonl').read_bytes()),projection_revision_bound=False))
    write(BASE/'bulk/oa-selection.json',chosen)
    print('selected',len(chosen),len(pools),flush=True)

def hf():
    from huggingface_hub import hf_hub_download,HfApi
    root=BASE/'bulk/hf';root.mkdir(exist_ok=True)
    try:
        info=HfApi(user_agent=UA).dataset_info('glossAPI/openarchives.gr',files_metadata=False)
        # Login is read automatically by huggingface_hub; never inspect it.
        p=pathlib.Path(hf_hub_download('glossAPI/openarchives.gr','data/external_pdfs.parquet',repo_type='dataset',revision=info.sha,local_dir=str(root),user_agent=UA))
        write(BASE/'receipts/hf-link-table.json',dict(repository='glossAPI/openarchives.gr',revision=info.sha,file='data/external_pdfs.parquet',bytes=p.stat().st_size,sha256=sha(p.read_bytes()),prior_cache_sha256=sha((CACHE/'external_pdfs.parquet').read_bytes()),auth='cached huggingface_hub login; credential never inspected',local_dir='bulk/hf'))
        print('HF table downloaded',p.stat().st_size,flush=True)
    except Exception as e:
        # Exception strings may contain signed URLs; only type is recorded.
        write(BASE/'receipts/hf-link-table.json',dict(error=type(e).__name__,auth='cached login automatically read',fallback='cached 15 October table'))
        print('HF',type(e).__name__,flush=True)

def one(row,mode='sequential'):
    c=HTTP('openarchives');url=row['pdf_url'];rr=pdf(c,url,row['id'],pages=3,limit=90_000_000,extra=dict(collection_slug=row['collection_slug']),mode=mode)
    rr.update(collection_slug=row['collection_slug'],year=row['year'],title=row['title'],metadata_id=row['id'])
    append(BASE/'receipts/oa-physical.jsonl',rr)
    if rr['success']:
        phys=rr['physical_pages'];scanned=all(p['classification'].startswith('scanned_') for p in phys)
        candidate('openarchives',row['id'],row['title'],row['year'],url,rr,collection_slug=row['collection_slug'],
                  physical_scanned_sample=scanned,physical_classifications=Counter(p['classification'] for p in phys),
                  target_classes=['modern','numerics','headings'] if scanned else [],pipeline_metadata=row['pipeline_metadata'],
                  metadata_projection_warning=row['metadata_projection_warning'],scan_rights=metadata(row['source_metadata'].get('metadata_json')).get('Δικαιώματα','per repository unresolved'),
                  access_terms_url='https://www.openarchives.gr/aggregator-openarchives/portal/termsOfUse')
    return rr

def run():
    chosen=json.loads((BASE/'bulk/oa-selection.json').read_text());pools=defaultdict(list)
    for r in chosen:pools[r['collection_slug']].append(r)
    successful=0;cols=set()
    # Six documents per collection, at most twelve attempts, stop when >=60 across >=10.
    for slug,pool in pools.items():
        n=0
        for r in pool:
            rr=one(r)
            if rr['success']:successful+=1;n+=1;cols.add(slug)
            if n>=6:break
            if any(s in rr.get('error','') for s in ['host stopped','HTTP 429','HTTP 503']):break
        if successful>=60 and len(cols)>=10:break
    print('OA sequential',successful,'collections',len(cols),flush=True)
    successful_ids={r['metadata_id'] for r in rows(BASE/'receipts/oa-physical.jsonl') if r.get('success')}
    short=[r for r in chosen if r['id'] in successful_ids][:12]
    # Three in flight, globally spaced starts remain <=1/s/host.
    with ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(lambda r:one(r,'concurrency3'),short):
            if any(s in result.get('error','') for s in ['HTTP 429','HTTP 503']):
                print('Concurrency throttle: no further work submitted',flush=True);break

def external_select():
    import pyarrow.parquet as pq
    cols=['collection_slug','pdf_links_json','status_code','external_link','type','edm_url']
    source=BASE/'bulk/hf/data/external_pdfs.parquet';table=pq.read_table(source,columns=cols).to_pylist()
    desired=['ntua','uth_rep','psepheda','uoi','hellanicus','Dione','rep_ihu','anaktisis','elocus','polynoe','dias','aua','ktisis','apothesis','uowm','pyxida']
    pools=defaultdict(list)
    for ext in table:
        us=urls(ext.get('pdf_links_json'));col=ext['collection_slug']
        if col not in desired or ext['status_code']!=200 or not us:continue
        url=html.unescape(us[0])
        if any(host in urlsplit(url).netloc for host in ['archive.org','anemi.','digitale-sammlungen','bsb']):continue
        pools[col].append(dict(id='ext-'+sha((col+'\n'+canonical_url(url)).encode())[:16],collection_slug=col,pdf_url=url,external_link=ext.get('external_link'),edm_url=ext.get('edm_url'),type=ext.get('type')))
    selected=[]
    for col in desired:
        pool=pools[col];pool.sort(key=lambda r:(not any(z in str(r.get('type','')).lower() for z in ['book','βιβλ']),sha(r['pdf_url'].encode())))
        seen=set()
        for r in pool:
            if r['pdf_url'] not in seen:selected.append(r);seen.add(r['pdf_url'])
            if len(seen)>=12:break
    write(BASE/'bulk/oa-external-selection.json',selected)
    write(BASE/'receipts/oa-external-selection.json',dict(table_sha256=sha(source.read_bytes()),row_count=len(table),selection='6 successful PDFs per collection, up to 12 attempts; book type first, URL hash stable order; no dates inferred from filenames',selected=selected))

def external_one(row,mode='sequential'):
    from bs4 import BeautifulSoup
    c=HTTP('openarchives');title=None;year=None;licence=None;lang=None;cat=row.get('external_link');metadata_error=None
    if mode=='sequential' and cat:
        try:
            mr,mb=c.get(cat);s=BeautifulSoup(mb,'html.parser')
            def val(*names):
                for n in names:
                    el=s.select_one('meta[name="'+n+'"],meta[property="'+n+'"]')
                    if el and el.get('content'):return el['content']
            title=val('citation_title','DC.title','dc.title','DCTERMS.title','og:title') or (s.title.get_text(' ',strip=True) if s.title else None)
            date=val('citation_date','citation_publication_date','DC.date.issued','dc.date.issued','DC.date','DCTERMS.issued')
            yr=re.search(r'\b(1[5-9]\d\d|20[0-2]\d)\b',date or '')
            if yr:year=int(yr[0])
            licence=val('DC.rights','dc.rights','DCTERMS.rights');lang=val('DC.language','dc.language','citation_language')
        except Exception as e:metadata_error=str(e)[:300]
    rr=pdf(c,row['pdf_url'],row['id'],pages=3,limit=70_000_000,extra=dict(collection_slug=row['collection_slug'],link_table_bound=True),mode=mode)
    rr.update(collection_slug=row['collection_slug'],year=year,title=title,metadata_id=row['id'],link_table_bound=True,catalogue_error=metadata_error)
    append(BASE/'receipts/oa-external-physical.jsonl',rr)
    if rr['success'] and mode=='sequential':
        ph=Counter(p['classification'] for p in rr['physical_pages']);scanned=all(k.startswith('scanned_') for k in ph)
        candidate('openarchives',row['id'],title or 'Title unresolved: '+str(cat or row['pdf_url']),year,row['pdf_url'],rr,
                  collection_slug=row['collection_slug'],physical_scanned_sample=scanned,physical_classifications=ph,
                  target_classes=['modern','numerics','headings'] if scanned else [],metadata_identity_bound=True,
                  metadata_basis='Fresh repository catalogue plus revision-bound HF external link table; cached text projection not joined',
                  catalogue_url=cat,catalogue_error=metadata_error,pipeline_metadata={'binding':'unresolved; corrupted cached projection deliberately excluded'},
                  scan_rights=licence or 'per repository unresolved',licence_string=licence,language_tag=lang,
                  access_terms_url=cat,link_table_bound=True)
    return rr

def external_run():
    selected=json.loads((BASE/'bulk/oa-external-selection.json').read_text());pools=defaultdict(list)
    for r in selected:pools[r['collection_slug']].append(r)
    total=0;cols=set();successrows=[]
    for col,pool in pools.items():
        n=0
        for row in pool:
            result=external_one(row)
            if result['success']:n+=1;total+=1;cols.add(col);successrows.append(row)
            if n>=6:break
            if any(x in result.get('error','') for x in ['429','503','host stopped','robots']):break
        if total>=60 and len(cols)>=10:break
    print('EXTERNAL BOUND sequential',total,'collections',len(cols),flush=True)
    # Submit at most three at once, inspect throttles before another batch.
    short=successrows[:12]
    for i in range(0,len(short),3):
        with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(lambda r:external_one(r,'concurrency3'),short[i:i+3]))
        if any(any(t in r.get('error','') for t in ['HTTP 429','HTTP 503']) for r in results):break

def external_complete():
    """Finish coverage using actual link-table collection IDs, never projection labels."""
    import pyarrow.parquet as pq
    reb=json.loads((BASE/'receipts/oa-projection-rebinding.json').read_text())
    covered=set(reb['unambiguous_collection_counts']);total=reb['verified_pdfs']
    done={r['metadata_id'] for r in rows(BASE/'receipts/oa-external-physical.jsonl')}
    candidates=pq.read_table(BASE/'bulk/hf/data/external_pdfs.parquet',columns=['collection_slug','pdf_links_json','status_code','external_link','edm_url','type']).to_pylist()
    desired=['psepheda','uoi','anaktisis','elocus','polynoe','dias','aua','ktisis','apothesis','uowm','pyxida']
    for col in desired:
        if col in covered:continue
        book=[];other=[]
        for ext in candidates:
            if ext['collection_slug']!=col or ext['status_code']!=200:continue
            us=urls(ext['pdf_links_json'])
            if not us:continue
            url=html.unescape(us[0]);ident='ext-'+sha((col+'\n'+canonical_url(url)).encode())[:16]
            if ident in done:continue
            row=dict(id=ident,collection_slug=col,pdf_url=url,external_link=ext.get('external_link'),edm_url=ext.get('edm_url'),type=ext.get('type'))
            (book if 'book' in str(ext.get('type','')).lower() else other).append(row)
        book.sort(key=lambda r:sha(r['pdf_url'].encode()));other.sort(key=lambda r:sha(r['pdf_url'].encode()))
        # Preserve book leads but avoid a sample consisting only of restricted rare books.
        pool=book[:2]+other[:8]+book[2:4];n=0
        for row in pool:
            r=external_one(row);done.add(row['id'])
            if r['success']:n+=1;total+=1
            if n>=2:covered.add(col);break
            error=r.get('error','')
            if any(t in error for t in ['robots','429','503','host stopped','Timeout','timeout','native_curl_28']):break
        if total>=60 and len(covered)>=10:break
    write(BASE/'receipts/oa-coverage-completion.json',dict(distinct_physical_pdfs=total,actual_collections=sorted(covered),target_met=total>=60 and len(covered)>=10,note='Earlier 60 fresh PDFs were exact-URL rebound to five actual HF collections; additions use direct external rows and fresh catalogues.'))
    print('Coverage completion',total,len(covered),flush=True)

if __name__=='__main__':globals()[sys.argv[1]]()
