#!/usr/bin/env python3
"""S1: Parliament DSpace 7.6 (live API), not InvenioRDM. Resumable metadata census."""
from o4c_common import *
BASE='https://digitallibrary.parliament.gr/records/api'

def local_url(url):return url.replace('https://sylloges.parliament.gr/records/api',BASE)
def values(m,k):return [x['value'] for x in m.get(k,[])]
def parse_record(item):
    m=item.get('metadata',{});get=lambda k:(values(m,k) or [None])[0]
    date=get('dcterms.created.from') or get('dc.date.issued')
    found=re.search(r'\b(1[6789]\d\d|20\d\d)\b',str(date or ''))
    pages=None
    try:pages=int(get('bibo.pageEnd'))-int(get('bibo.pageStart'))+1
    except (TypeError,ValueError):
        n=re.search(r'\d+',str(get('bibo.numPages') or ''));pages=int(n[0]) if n else None
    return row('parliament',item['uuid'],get('dc.title') or item.get('name'),get('dc.identifier.uri') or 'https://digitallibrary.parliament.gr/items/'+item['uuid'],
      year=int(found[0]) if found else None,pages=pages,rights=values(m,'dc.rights')+values(m,'dc.rights.uri'),
      language=values(m,'dc.language.rfc3066'),collection=get('lpgr.Collection'),
      metadata_url=BASE+'/core/items/'+item['uuid'],metadata_pages=pages,media_status='unverified')

def paginate(h,url,key):
    page=0
    while True:
        d=h.json(api(url,size=100,page=page));yield from d.get('_embedded',{}).get(key,[])
        page+=1
        if page>=d.get('page',{}).get('totalPages',1):break

def resolve_files(h,r):
    files=[];text=[]
    for bundle in paginate(h,BASE+'/core/items/'+r['document_id']+'/bundles','bundles'):
        if bundle['name'] not in ('ORIGINAL','TEXT'):continue
        for f in paginate(h,BASE+'/core/bundles/'+bundle['uuid']+'/bitstreams','bitstreams'):
            u=local_url(f['_links']['content']['href'])
            obj={'name':f['name'],'url':u,'size':f.get('sizeBytes'),'checksum':f.get('checkSum')}
            if f['name'].lower().endswith(('.pdf','.djvu')):files.append(obj)
            elif bundle['name']=='TEXT':text.append(obj)
    r['scan_files']=files;r['text_files']=text;r['media_status']='source-declared' if files else 'no-PDF-or-DjVu'
    if files:
        f=sorted(files,key=lambda f:-(f['size'] or 0))[0];r['download_url']=f['url'];r['size']=f['size']
    return r

def validate_page(result):
    page=result['page'];expected=min(page['size'],max(0,page['totalElements']-page['number']*page['size']))
    actual=len(result.get('_embedded',{}).get('objects',[]))
    if actual!=expected:raise ProbeError(f'API pagination mismatch: returned {actual}, expected {expected}, reported size {page["size"]}; do not advance cursor')

def main():
    p=parser('parliament');p.add_argument('--query',default='ΣΥΝΕΔΡΙΑΣΗ',help='empty string gives the unfiltered catalogue')
    p.add_argument('--resolve-all',action='store_true',help='enumerate original bundles for all rights-compatible historical candidates; probes remain capped')
    p.add_argument('--resolve-docs',type=int,default=30);p.add_argument('--rows',type=int,default=100)
    p.add_argument('--resize-page',action='store_true',help='safely resize metadata pages by rewinding to an overlapping row boundary')
    p.add_argument('--baseline',action='store_true',help='include/probe the existing S17 107 as separately labelled baseline')
    args=p.parse_args();h=HTTP('parliament',args.offline,args.interval,retry_errors=args.retry_errors);path,state=load_state(args)
    streams=state.setdefault('streams',{});s=streams.setdefault(args.query,{'next_page':0,'complete':False,'rows_per_page':args.rows})
    if s['rows_per_page']!=args.rows:
        if not args.resize_page:raise ValueError('resuming with changed rows requires --resize-page')
        offset=s['next_page']*s['rows_per_page'];s.update(next_page=offset//args.rows,rows_per_page=args.rows)
        s['page_resize']={'previous_offset':offset,'new_offset':s['next_page']*args.rows,'overlap_only':True}
        write_json(path,state)
    rows={r['document_id']:r for r in read_rows(args.out)}
    baseline={r['item_id']:r for r in read_rows(ROOT/'docs/evidence/s17/pdf_cache_refetch.jsonl')}
    if args.baseline:
        for id,b in baseline.items():
            if id not in rows:
                r=row('parliament',id,b['title'],b['handle'],year=b['year'],rights=b['rights'],collection=b['collection'])
                r.update(download_url=b['download_url'],existing_s17=True,pdf_cache_sha256=b['pdf_cache_sha256'])
                rows[id]=r
    count=0
    while not s['complete'] and (args.all or count<args.max_pages):
        params=dict(size=args.rows,page=s['next_page'],sort='dc.title,asc')
        if args.query:params['query']=args.query
        try:d=h.json(api(BASE+'/discover/search/objects',**params))['_embedded']['searchResult']
        except Exception as e:h.event(stage='catalogue',query=args.query,error=str(e));break
        validate_page(d)
        if d['page']['size']!=args.rows:raise ValueError('server capped page size to '+str(d['page']['size'])+'; resume with that --rows and --resize-page')
        for hit in d.get('_embedded',{}).get('objects',[]):
            item=hit['_embedded']['indexableObject']
            if item.get('type')!='item':continue
            r=parse_record(item);id=r['document_id']
            r['existing_s17']=id in baseline
            if id not in rows:rows[id]=r
        s.update(next_page=s['next_page']+1,num_found=d['page']['totalElements'],complete=s['next_page']+1>=d['page']['totalPages'])
        save_rows(args.out,rows.values());write_json(path,state);count+=1
        print('catalogue',args.query,'page',s['next_page'],'rows',len(rows),'bytes',h.transferred,flush=True)
    # Probe longest historical print first, exclude S17 by default.
    eligible=sorted((r for r in rows.values() if r['rights']['compatible'] and (r.get('year') is None or 1800<=r['year']<=1980)
      and (args.baseline or not r.get('existing_s17'))),key=lambda r:(not str(r.get('title','')).startswith('ΣΥΝΕΔΡΙΑΣΗ'),-(r.get('pages') or 0)))
    resolved=probed=0
    if args.resolve_all:args.resolve_docs=len(eligible)
    if args.resolve_docs==0 and args.probe_docs==0:eligible=[]
    for r in eligible:
        if h.transferred>=h.budget:
            h.event(stage='budget',error='task transfer budget exhausted; remaining files/layers unverified');break
        if args.baseline and r.get('pdf_cache_sha256') and probed<args.probe_docs:
            local=ROOT/'data/raw/pdf_cache'/(r['pdf_cache_sha256']+'.pdf')
            if local.exists() and r['text_layer']['status']!='verified':probe_pdf(h,r,local);probed+=1
        if r.get('media_status')=='unverified' and resolved<args.resolve_docs and (not r.get('media_error') or args.retry_errors):
            resolved+=1
            try:resolve_files(h,r)
            except Exception as e:r['media_error']=str(e);h.event(stage='files',id=r['document_id'],error=str(e))
        if r.get('download_url') and probed<args.probe_docs and r['text_layer']['status']!='verified' and not r.get('pdf_cache_sha256') and (not r['text_layer'].get('error') or args.retry_errors):
            probed+=1;probe_pdf(h,r)
        save_rows(args.out,rows.values())
        print('resolve',resolved,'probe',probed,r['document_id'],r['text_layer']['status'],'bytes',h.transferred,flush=True)
        if resolved>=args.resolve_docs and (probed>=args.probe_docs or not any(x.get('download_url') and x['text_layer']['status']!='verified' for x in eligible)):break
    write_json(path,state)
if __name__=='__main__':main()
