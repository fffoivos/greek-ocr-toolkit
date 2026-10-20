#!/usr/bin/env python3
"""S4: Commons imageinfo joined to Wikisource proofread metadata; fail closed on robots."""
import html
from greekocr._vendor.scripts.fetch.o4c_common import *
LANG={'el':'Greek','ru':'Russian','uk':'Ukrainian','bg':'Bulgarian','sr':'Serbian'}
COMMONS='https://commons.wikimedia.org/w/api.php'

def parse_file(page,lang):
    info=(page.get('imageinfo') or [{}])[0];ext=info.get('extmetadata',{});get=lambda k:ext.get(k,{}).get('value')
    r=row('wikimedia',page['title'],page['title'],'https://commons.wikimedia.org/wiki/'+urllib.parse.quote(page['title'].replace(' ','_')),
      size=info.get('size'),rights=[get('LicenseShortName'),get('LicenseUrl'),get('UsageTerms')],language=lang,
      artist=get('Artist'),credit=get('Credit'),copyrighted=get('Copyrighted'),metadata_url=COMMONS)
    r['download_url']=info.get('url');r['pages']=info.get('pagecount');r['mime']=info.get('mime')
    r['proofread_status']={'status':'unverified'}
    return r

def join_status(h,r,lang):
    endpoint=f'https://{lang}.wikisource.org/w/api.php'
    site=h.json(api(endpoint,action='query',meta='siteinfo',siprop='namespaces',format='json',maxlag=5))
    names=site['query']['namespaces'];index=names.get('106',{}).get('*','Index');pages=names.get('104',{}).get('*','Page')
    filename=r['document_id'].split(':',1)[1];title=index+':'+filename
    data=h.json(api(endpoint,action='query',titles=title,prop='revisions',rvprop='ids|timestamp|content',rvslots='main',format='json',maxlag=5))
    r['proofread_status']={'status':'index-present' if any('missing' not in p for p in data['query']['pages'].values()) else 'index-unverified',
        'index_url':f'https://{lang}.wikisource.org/wiki/'+urllib.parse.quote(title.replace(' ','_')),'gold_text':'unverified'}
    # At most two proofread text/status pages plus one PDF page per document. Quality is not gold certification.
    data=h.json(api(endpoint,action='query',generator='allpages',gapnamespace=104,gapprefix=filename+'/',gaplimit=2,prop='revisions',rvprop='ids|content',rvslots='main',format='json',maxlag=5))
    levels={};samples=[]
    for p in data.get('query',{}).get('pages',{}).values():
        rev=(p.get('revisions') or [{}])[0];text=rev.get('slots',{}).get('main',{}).get('*','')
        match=re.search(r'pagequality\s+level=["\'](\d)',text)
        if match:levels[match[1]]=levels.get(match[1],0)+1
        samples.append({'title':p['title'],'revid':rev.get('revid'),'quality':int(match[1]) if match else None})
    r['proofread_status'].update(sample_quality_counts=levels,pages=samples,count_complete='continue' not in data)
    return r

def main():
    p=parser('wikimedia');p.add_argument('--languages',default=','.join(LANG));args=p.parse_args();h=HTTP('wikimedia',args.offline,args.interval,retry_errors=args.retry_errors)
    path,state=load_state(args);rows={r['document_id']:r for r in read_rows(args.out)};probes=0
    for lang in args.languages.split(','):
        # Record the proofread interface's policy explicitly even when Commons discovery is blocked.
        proofread_url=api(f'https://{lang}.wikisource.org/w/api.php',action='query',meta='siteinfo',siprop='namespaces',format='json',maxlag=5)
        try:h.check_robots(proofread_url);h.event(stage='wikisource-robots',language=lang,status='allowed; API not fetched by this policy check',url=proofread_url)
        except Exception as e:h.event(stage='wikisource-robots',language=lang,status='unverified',url=proofread_url,error=str(e))
        cont=state.get(lang,{}).get('continue',{});count=0
        while args.all or count<args.max_pages:
            params=dict(action='query',generator='search',gsrnamespace=6,gsrsearch=f'{LANG[lang]} (filetype:pdf OR filetype:djvu)',gsrlimit=50,prop='imageinfo',iiprop='url|size|mime|extmetadata',format='json',maxlag=5,**cont)
            try:d=h.json(api(COMMONS,**params))
            except Exception as e:h.event(stage='commons-api',language=lang,error=str(e));state[lang]={'status':'unverified','error':str(e)};write_json(path,state);break
            for page in d.get('query',{}).get('pages',{}).values():
                if not page['title'].lower().endswith(('.pdf','.djvu')):continue
                r=parse_file(page,lang)
                if r['document_id'] in rows:continue
                if r['rights']['compatible']:
                    try:join_status(h,r,lang)
                    except Exception as e:r['proofread_status']['error']=str(e)
                    if r.get('mime')=='application/pdf' and probes<args.probe_docs:probe_pdf(h,r);probes+=1
                    elif r.get('mime')=='image/vnd.djvu':r['text_layer']={'status':'unverified','error':'bounded DjVu text-layer endpoint not verified; no full media fetched'}
                rows[r['document_id']]=r
            cont=d.get('continue');state[lang]={'continue':cont or {},'complete':not cont};write_json(path,state);save_rows(args.out,rows.values());count+=1
            if not cont:break
    save_rows(args.out,rows.values());write_json(path,state)
    print('wikimedia documents',len(rows),'bytes',h.transferred)
if __name__=='__main__':main()
