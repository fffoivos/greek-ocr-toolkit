#!/usr/bin/env python3
"""S3: Internet Archive advancedsearch + per-item files + OCR text sidecars."""
import re, urllib.parse
from o4c_common import *
LANGUAGES={'el':'(language:gre OR language:Greek)','ru':'(language:rus OR language:Russian)',
 'uk':'(language:ukr OR language:Ukrainian)','bg':'(language:bul OR language:Bulgarian)','sr':'(language:srp OR language:Serbian)'}

def parse_item(identifier,d):
    m=d.get('metadata',{}); files=d.get('files',[])
    def num(v):
        try:return int(v)
        except (TypeError,ValueError):return None
    r=row('archive',identifier,m.get('title',identifier),'https://archive.org/details/'+identifier,
        year=num(str(m.get('year',m.get('date','')))[:4]),pages=num(m.get('imagecount')),
        rights=[m.get('licenseurl'),m.get('rights')],language=m.get('language'),creator=m.get('creator'),
        metadata_url='https://archive.org/metadata/'+identifier)
    base='https://archive.org/download/'+urllib.parse.quote(identifier,safe='')+'/'
    allowed=[f for f in files if f.get('name','').lower().endswith(('.pdf','.djvu')) and f.get('private') not in ('true',True)]
    allowed.sort(key=lambda f:('text' not in f.get('format','').lower(),not f['name'].endswith('.djvu'),num(f.get('size')) or 0))
    r['scan_files']=[{'name':f['name'],'size':num(f.get('size')),'format':f.get('format'),'url':base+urllib.parse.quote(f['name'])} for f in allowed]
    if allowed:r['download_url']=r['scan_files'][0]['url'];r['size']=r['scan_files'][0]['size']
    txt=next((f for f in files if f['name'].endswith('_djvu.txt') and f.get('private') not in ('true',True)),None)
    xml=next((f for f in files if f['name'].endswith('_djvu.xml') and f.get('private') not in ('true',True)),None)
    r['text_layer']={'status':'declared' if txt or xml else 'unverified','kind':'IA OCR sidecar','scan_status':'source-declared' if txt or xml else 'unverified'}
    r['text_url']=base+urllib.parse.quote(txt['name']) if txt else None
    r['text_size']=num(txt.get('size')) if txt else None
    r['geometry_url']=base+urllib.parse.quote(xml['name']) if xml else None
    r['geometry_status']='declared' if xml else 'unverified'
    return r

def main():
    p=parser('archive');p.add_argument('--languages',default=','.join(LANGUAGES));p.add_argument('--rows',type=int,default=50)
    p.add_argument('--query-extra',default='',help='additional advancedsearch clause; cursor is query-bound')
    p.add_argument('--licensed',action='store_true',help='prioritise explicit rights/license fields')
    p.add_argument('--broad',action='store_true',help='all years/formats, instead of dated OCR-scan prioritisation')
    args=p.parse_args();h=HTTP('archive',args.offline,args.interval,retry_errors=args.retry_errors);path,state=load_state(args)
    key=('broad' if args.broad else 'scans')+('-licensed' if args.licensed else '')+('-'+hashlib.sha256(args.query_extra.encode()).hexdigest()[:12] if args.query_extra else ''); state.setdefault(key,{})
    rows={r['document_id']:r for r in read_rows(args.out)};probes=0
    for lang in args.languages.split(','):
        query='mediatype:texts AND '+LANGUAGES[lang]
        if not args.broad:query+=' AND year:[1800 TO 1950] AND (format:"DjVuTXT" OR format:"Djvu XML") AND NOT collection:inlibrary'
        if args.query_extra:query+=' AND ('+args.query_extra+')'
        if args.licensed:query+=' AND (licenseurl:* OR rights:"public domain")'
        page=state[key].get(lang,{}).get('next_page',1);done=state[key].get(lang,{}).get('complete',False);count=0
        if state[key].get(lang,{}).get('rows_per_page',args.rows)!=args.rows:raise ValueError('resuming with changed rows would skip metadata')
        if done:continue
        while args.all or count<args.max_pages:
            u=api('https://archive.org/advancedsearch.php',q=query,**{'fl[]':['identifier','title','year','imagecount','language','licenseurl','rights'],'sort[]':['imagecount desc','identifier asc'],'rows':args.rows,'page':page,'output':'json'})
            try:d=h.json(u)['response']
            except Exception as e:h.event(stage='search',language=lang,error=str(e));break
            h.event(stage='search',language=lang,query=query,page=page,num_found=d['numFound'],returned=len(d['docs']))
            for hit in d['docs']:
                identifier=hit['identifier']
                if identifier not in rows:
                    try:r=parse_item(identifier,h.json('https://archive.org/metadata/'+urllib.parse.quote(identifier,safe='')))
                    except Exception as e:
                        h.event(stage='metadata',id=identifier,error=str(e));continue
                    r['discovery_query']=query;r['query_language']=lang;rows[identifier]=r
                    append(args.out,r)
                r=rows[identifier]
                if probes<args.probe_docs and r.get('text_url') and r['rights']['compatible'] and r['text_layer']['status']!='verified':
                    probes+=1
                    try:
                        meta,b=h.get(r['text_url'],limit=30_000_000)
                        apply_text(r,b.decode('utf-8','replace'),'IA complete _djvu.txt silver OCR',None)
                        r['text_layer'].update(probe_url=r['text_url'],probe_sha256=meta['sha256'],probe_bytes=len(b),scan_status='source-declared',pdf_embedded_text='unverified; sidecar measured')
                        if r['geometry_url']:
                            gm,gb=h.get(r['geometry_url'],limit=131072,range_header='bytes=0-131071')
                            r['geometry_status']='verified-word-coordinates' if b'<WORD' in gb and b'coords=' in gb else 'unverified'
                            r['geometry_sample_sha256']=gm['sha256']
                    except Exception as e:r['probe_error']=str(e);h.event(stage='text',id=identifier,error=str(e))
                    save_rows(args.out,rows.values())
            save_rows(args.out,rows.values())
            page+=1;count+=1;complete=(page-1)*args.rows>=d['numFound']
            state[key][lang]={'next_page':page,'complete':complete,'num_found':d['numFound'],'query':query,'rows_per_page':args.rows};write_json(path,state)
            print(lang,'page',page-1,'documents',len(rows),'probes',probes,'bytes',h.transferred,flush=True)
            if complete:break
    # Increasing --probe-docs also measures previously discovered rows without re-enumerating them.
    for r in rows.values():
        if probes>=args.probe_docs:break
        if r.get('text_url') and r['rights']['compatible'] and r['text_layer']['status']!='verified' and not r.get('probe_error'):
            probes+=1
            try:
                m,b=h.get(r['text_url'],limit=30_000_000);apply_text(r,b.decode('utf-8','replace'),'IA complete _djvu.txt silver OCR',None)
                r['text_layer'].update(probe_url=r['text_url'],probe_sha256=m['sha256'],probe_bytes=len(b),scan_status='source-declared',pdf_embedded_text='unverified; sidecar measured')
            except Exception as e:r['probe_error']=str(e)
    save_rows(args.out,rows.values())
if __name__=='__main__':main()
