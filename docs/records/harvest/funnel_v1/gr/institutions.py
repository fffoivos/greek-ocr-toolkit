from probe import *
from urllib.parse import urlencode,parse_qs,unquote

def localmeta(source,contains):
    rr=[r for r in rows(BASE/'receipts/http.jsonl') if r['source']==source and r['kind']=='metadata' and r['status']==200 and contains in r['url']]
    r=rr[-1];b=(BASE/'bulk/metadata'/(sha(r['url'].encode())+'.body')).read_bytes()
    return BeautifulSoup(b,'html.parser'),r,b

def nlg():
    source='nlg-digital';c=HTTP(source);base='https://digitalcollections.nlg.gr'
    s,_,_=localmeta(source,'search.html')
    items=[]
    for a in s.select('a[href]'):
        if re.search(r'/browse/\d+$',a['href']) and a.get_text(' ',strip=True):items.append((a['href'].rsplit('/',1)[-1],a.get_text(' ',strip=True)))
    # Greek and Ancient Greek catalogue facets, explicitly published by the UI.
    for start in [0,20,40]:
        u=base+'/nlg-repo/dl/el/search.html?'+urlencode({'p.proto':'/butterfly/backie/monograph','p.collabKinds':'NLG_ONLY','p.languages':'/lib/default/data/100091','p.start':start,'p.count':20})
        ss,_,_=meta(c,u)
        if ss:
            for a in ss.select('a[href]'):
                if re.search(r'/browse/\d+$',a['href']) and a.get_text(' ',strip=True):items.append((a['href'].rsplit('/',1)[-1],a.get_text(' ',strip=True)))
    # Prioritize Greek-titled works rather than English Plotinus volumes.
    items=sorted(dict(items).items(),key=lambda it:-sum('\u0370'<=z<='\u03ff' or '\u1f00'<=z<='\u1fff' for z in it[1]))
    for k,(item,title) in enumerate(items[:24]):
        url=base+'/nlg-repo/dl/el/iiifmetadata/'+item
        try:r,b=c.get(url);d=json.loads(b)
        except Exception as e:print(source,item,str(e),flush=True);continue
        canvases=d.get('sequences',[{}])[0].get('canvases',[])
        if not canvases:continue
        metadata=d.get('metadata',[]);year=None
        for m in metadata:
            label=str(m.get('label','')).lower()
            if any(t in label for t in ['date','χρονολογ','έκδοση','publication']):
                ys=re.findall(r'\b(1[5-9]\d\d|20[0-2]\d)\b',str(m.get('value','')))
                if ys:year=int(ys[0]);break
        ok=0;fail=0
        for i in positions(len(canvases),3 if k<20 else 1):
            imurl=canvases[i]['images'][0]['resource']['@id']
            rr=image(c,imurl,item,i+1,dict(manifest_url=url,manifest_sha256=r['sha256']))
            ok+=rr['success'];fail+=not rr['success']
            if not rr['success'] and any(t in rr.get('error','') for t in ['429','503']):return
        if ok:
            candidate(source,item,title,year,base+'/nlg-repo/dl/el/browse/'+item,dict(success=True,page_count=len(canvases),http_sha256=r['sha256']),
                      manifest_url=url,metadata=metadata,scan_rights=d.get('license') or d.get('rights') or 'NLG item licence; see metadata',
                      licence_string=d.get('license') or d.get('rights'),access_terms_url=base+'/nlg-repo/dl/el/terms.html',
                      target_classes=['poly1850' if year and 1850<=year<1900 else 'poly1900' if year and 1900<=year<=1982 else 'historical_other','headings'])
        print(source,item,'pages',ok,'of',len(canvases),year,flush=True)

def elstat():
    c=HTTP('elstat');root='http://dlib.statistics.gr/portal/page/portal/ESYE/'
    s,_,_=meta(c,root+'categoryyears?p_cat=10007369&p_topic=10007369')
    if s is None:return
    years=[(a.get_text(' ',strip=True),a['href']) for a in s.select('a[href]') if '/yeararticles?' in a['href']]
    write(BASE/'receipts/elstat-yearbook-years.json',dict(series='Statistical Yearbook of Greece',years=years,note='1859 refers to broader historical publications, not yearbook inception'))
    selected=[]
    # At least one in each available decade, then chronological earliest years.
    seen=set()
    for label,u in years:
        ys=re.findall(r'\d{4}',label)
        if not ys:continue
        y=int(ys[0]);dec=y//10*10
        if dec not in seen:selected.append((y,u));seen.add(dec)
    for label,u in years:
        ys=re.findall(r'\d{4}',label)
        if ys and u not in {v for _,v in selected}:selected.append((int(ys[0]),u))
    for k,(year,u) in enumerate(selected[:24]):
        ss,rr,_=meta(c,u)
        if ss is None:continue
        links=list(dict.fromkeys(urljoin(u,a['href']) for a in ss.select('a[href]') if '/Book/' in a['href'] and '.pdf' in a['href']))
        if not links:
            details=list(dict.fromkeys(urljoin(u,a['href']) for a in ss.select('a[href]') if '/showdetails?' in a['href']))
            for detail in details[:1]:
                ds,dr,_=meta(c,detail)
                if ds:links+=list(dict.fromkeys(urljoin(detail,a['href']) for a in ds.select('a[href]') if '/Book/' in a['href'] and '.pdf' in a['href']))
        for url in links[:1]:
            item=url.rsplit('/',1)[-1][:-4];result=pdf(c,url,item,pages=10 if k<5 else 1,limit=130_000_000)
            candidate('elstat',item,'Στατιστική Επετηρίς της Ελλάδος '+str(year),year,url,result,catalogue_url=u,
                      target_classes=['numerics','leaders','modern'],scan_rights='Copyright ELSTAT; item-specific reuse unresolved',access_terms_url=root+'faq')

def et_discover():
    c=HTTP('government-gazette');s,r,b=localmeta('government-gazette','search-legislation')
    print('scripts',[(x.get('id'),x.get('src')) for x in s.select('script[src]') if any(t in str(x).lower() for t in ['custom','legis','search','listing'])],flush=True)
    texts=[x.get_text() for x in s.select('script:not([src])')]
    for t in texts:
        if 'listingItemsEle' in t or 'selectYear' in t:print(t[:14000],flush=True)
    for x in s.select('script[src]'):
        if any(t in x['src'] for t in ['custom','legislation','search.js','main.js']):meta(c,x['src'])

def pergamos_discover():
    c=HTTP('pergamos')
    for item in ['col_psachosbooks','col_rarebooks','2880893','59592']:
        s,r,b=meta(c,'https://pergamos.lib.uoa.gr/item/uoadl:'+item)
        if not s or not s.find('script',id='__NEXT_DATA__'):continue
        d=json.loads(s.find('script',id='__NEXT_DATA__').string)
        data=d['props']['pageProps']['page']['pageElements']
        write(BASE/'bulk'/('pergamos-'+item+'.json'),data)
        for key,val in data.items():
            print(item,key,str(val.get('data'))[:2500],flush=True)

def lekythos_discover():
    c=HTTP('lekythos');base='https://lekythos.library.ucy.ac.cy'
    u=base+'/archive/search?'+urlencode({'lang':'en','tr1':'14018','tr2':'Ελληνικά Γράμματα','tr3':'tree','tree':'Ελληνικά Γράμματα‡14018'})
    s,r,b=meta(c,u)
    if not s:return
    items=list(dict.fromkeys(a['href'] for a in s.select('a[href]') if '/archive/item/' in a['href']))
    for item in items[:7]:
        ss,rr,bb=meta(c,urljoin(base,item))
        if ss:
            print(item,ss.get_text(' ',strip=True)[:2500],flush=True)
            print('MEDIA',re.findall(r'.{0,140}(?:\.pdf|/download/|/viewer/|\.jpg|iiif).{0,180}',str(ss))[:14],flush=True)

def lekythos():
    c=HTTP('lekythos');base='https://lekythos.library.ucy.ac.cy';found=[]
    for item in ['14212','14019','14020','14021']:
        s,r,b=meta(c,base+'/archive/item/'+item)
        if not s:continue
        for li in s.select('li.bitstreams-item'):
            a=li.select_one('a[href*="/archive/download/"]')
            if not a:continue
            text=li.get_text(' ',strip=True);years=re.findall(r'\b(19\d\d)\b',text);year=int(years[0]) if years else None
            url=urljoin(base,a['href']);ident=url.rsplit('/',1)[-1][:-4]
            found.append((item,ident,text,year,url))
    for k,(item,ident,title,year,url) in enumerate(found[:20]):
        rr=pdf(c,url,ident,pages=10 if k<5 else 1,limit=65_000_000)
        candidate('lekythos',ident,title,year,url,rr,catalogue_url=base+'/archive/item/'+item,access_terms_url=base+'/archive/item/'+item,target_classes=['poly1900','dialogue','headings'])

def gazette():
    c=HTTP('government-gazette')
    # Public download formula read from the current official React bundle.
    root='https://ia37rg02wpsa01.blob.core.windows.net/fek/01/'
    selected=[(y,1) for y in [1833]+list(range(1840,1991,10))]+[(y,2) for y in [1833,1850,1900,1950]]
    for year,number in selected:
        ident=f'{year}01{number:05d}';url=root+str(year)+'/'+ident+'.pdf'
        rr=pdf(c,url,ident,pages=10,limit=40_000_000)
        candidate('government-gazette',ident,f'ΦΕΚ Α {number}/{year}',year,url,rr,route_basis='Official current UI getFekLink formula; individual existence verified by decode',
                  access_terms_url='https://search.et.gr/el/',target_classes=['numerics','headings','leaders','poly1850' if 1850<=year<1900 else 'poly1900' if 1900<=year<=1982 else 'historical_other'])
        if not rr['success'] and any(t in rr.get('error','') for t in ['429','503','robots']):return

def pergamos_api():
    c=HTTP('pergamos');c.session.headers['Content-Type']='application/json'
    query=dict(start=0,count=25,models=['RareBook'],filters={},aggregations=[],sortOptions=[],fields=[],strict=False)
    try:
        r,b=c.get('https://pergamos.lib.uoa.gr/public-api/search',method='POST',data=json.dumps(query),limit=12_000_000)
        write(BASE/'bulk/pergamos-rare-search.json',json.loads(b));write(BASE/'receipts/pergamos-public-search.json',dict(request=query,response_sha256=r['sha256'],response_bytes=r['bytes'],url=r['url']))
        print(b[:4000].decode('utf8','replace'),flush=True)
    except Exception as e:print(str(e),flush=True)

def pergamos():
    c=HTTP('pergamos');c.session.headers['Content-Type']='application/json';api='https://pergamos.lib.uoa.gr/public-api/'
    def search(model,filters=None,count=20,sort=None,label=''):
        q=dict(start=0,count=count,models=[model],fields=[],strict=False,query=dict(filters=filters or {},aggregations=[],sorting=sort or []))
        r,b=c.get(api+'search','api_query',15_000_000,method='POST',data=json.dumps(q));d=json.loads(b)
        write(BASE/'receipts/pergamos-queries'/(sha(json.dumps(q,sort_keys=True).encode())+'.json'),dict(request=q,response_sha256=r['sha256'],total=d.get('total'),label=label))
        write(BASE/'bulk'/('pergamos-query-'+sha(json.dumps(q,sort_keys=True).encode())+'.json'),d)
        return d
    books=search('ArchivalBook',count=24)['items']
    for k,it in enumerate(books):
        ident=it['id'];title=it.get('title') or ident
        if isinstance(title,list):title=title[0]['value']
        yearobj=it.get('creationYear') or it.get('temporalCoverageDateRange')
        year=datetime.datetime.fromtimestamp(yearobj['from']/1000,datetime.timezone.utc).year if isinstance(yearobj,dict) and yearobj.get('from') else None
        ps=search('Page',{'and':[{'eq':{'parents':'uoadl:'+ident}},{'exists':'webFile'}]},count=300,sort=['pageNumber:asc'],label='pages of '+ident)
        pp=[p for p in ps['items'] if (p.get('webFile') or {}).get('published')]
        successes=0
        for i in positions(len(pp),10 if k<5 else 1):
            page=pp[i];file=page['webFile'];url=api+'files/uoadl/'+file['id']+'/payload-inline'
            rr=image(c,url,ident,int(page.get('pageNumber') or i+1),dict(page_item=page['id'],public_file_id=file['id']))
            successes+=rr['success']
        if successes:
            candidate('pergamos',ident,title,year,'https://pergamos.lib.uoa.gr/item/uoadl:'+ident,dict(success=True,page_count=ps['total']),
                      published_page_count=len(pp),target_classes=['poly1850' if year and year<1900 else 'poly1900','headings'],
                      public_type=it['publicType'],scan_rights=it.get('license') or 'default CC BY-NC 4.0',licence_string=it.get('license'),
                      text_rights=it.get('rightsHolder') or 'per author unresolved',access_terms_url='https://pergamos.lib.uoa.gr/about/policies')
        print('pergamos printed',ident,'accessible',len(pp),'fetched',successes,flush=True)
    theses=search('BornDigitalThesis',count=5,sort=['creationYear:asc'])['items']
    for it in theses:
        file=it.get('theFile') or {};ident=it['id']
        if not file.get('published') or file.get('embargo.isActive'):continue
        url=api+'files/uoadl/'+file['id']+'/payload-inline';rr=pdf(c,url,ident,pages=3,limit=45_000_000)
        yr=it.get('creationYear') or {};year=datetime.datetime.fromtimestamp(yr['from']/1000,datetime.timezone.utc).year if yr.get('from') else None
        candidate('pergamos',ident,it.get('title'),year,url,rr,public_type=it['publicType'],target_classes=['modern'] if rr.get('success') and all(p['classification'].startswith('scanned_') for p in rr.get('physical_pages',[])) else [],licence_string=it.get('license'),access_terms_url='https://pergamos.lib.uoa.gr/about/policies')

def newspapers():
    c=HTTP('nlg-newspapers');s,r,b=localmeta(c.source,'ftr.asp');done=0
    for col,year in [('126',1883),('108',1896),('123',1900),('124',1911),('64',1944),('65',1920)]:
        fields={i['name']:i.get('value','') for i in s.select('input[type=hidden][name]')}
        fields.update(cols=col,efim='1',Cols_Newspapers=col,date_from=f'1/1/{year}',date_to=f'12/31/{year}',searchtype='1',title='',sign='',series='',ektasi='',pagelen='10')
        try:rr,bb=c.get('http://efimeris.nlg.gr/ns/search.asp','api_query',method='POST',data=fields)
        except Exception as e:print(col,year,str(e),flush=True);continue
        page=BeautifulSoup(bb,'html.parser');write(BASE/'receipts'/f'nlg-search-{col}-{year}.json',dict(url=rr['url'],query=fields,response_sha256=rr['sha256'],result_text=page.get_text(' ',strip=True)[:8000]))
        links=list(dict.fromkeys(a['href'] for a in page.select('a[href]') if 'pdfwin_ftr.asp' in a['href']))
        for viewer in links[:2]:
            current=viewer.replace('http://www.nlg.gr/digitalnewspapers','http://efimeris.nlg.gr')
            frame=current.replace('pdfwin_ftr.asp','pages_ftr.asp');fs,fr,fb=meta(c,frame)
            if not fs:continue
            text=fs.get_text(' ',strip=True)
            if 'Το φύλλο δεν είναι διαθέσιμο' in text:
                append(BASE/'receipts/nlg-unavailable-issues.jsonl',dict(viewer=current,page_frame=frame,source_year=year,message='Το φύλλο δεν είναι διαθέσιμο.',response_sha256=fr['sha256']));continue
            print('AVAILABLE FRAME',frame,fb.decode('utf8','replace')[:6000],flush=True)
            # Only follow an actual page link offered by the frame.
            for a in fs.select('a[href]'):
                match=re.search(r'GetPdf\((\d+)\)',a['href'])
                if not match:continue
                params=parse_qs(urlsplit(frame).query);params={k:v[0] for k,v in params.items()};params['p']=match[1]
                u='http://efimeris.nlg.gr/ns/showpdf.asp?'+urlencode(params);rr=pdf(c,u,col+'-'+match[1],pages=1,limit=12_000_000)
                done+=rr['success']
        if done>=50:return


if __name__=='__main__':globals()[sys.argv[1]]()
