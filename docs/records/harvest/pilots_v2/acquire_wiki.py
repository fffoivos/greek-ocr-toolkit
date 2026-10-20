import hashlib, json, re, sys
from urllib.parse import quote
from pilotlib import *

if __name__=='__main__':
    scan_file=sys.argv[1] if len(sys.argv)>1 else 'Βίοι_Πελοποννησίων_ανδρών.djvu'
    count=int(sys.argv[2]) if len(sys.argv)>2 else 50
    book=next(b for b in json.loads((ROOT/'docs/harvest/wikisource/source_books.json').read_text()) if b['scan_file']==scan_file)
    prior={p['url'] for p in json.loads((ROOT/'docs/harvest/wikisource/manifest.json').read_text())}
    eligible=[p for p in book['eligible_pages'] if p['quality']==4 and p['url'] not in prior]
    ns=positions(len(eligible),count);selected=[eligible[i-1] for i in ns]
    numbers={p['page'] for p in selected}
    for f in (BASE/'receipts/pages').glob('wikisource--'+book['key']+'--*.json'):
        r=json.loads(f.read_text())
        if r['page'] not in numbers:r['excluded']='outside_final_50_page_sample';write(f,r)
    write(BASE/'receipts'/('wiki-selection-'+book['key']+'.json'),dict(book=book,prior_manifest_sha256=sha(ROOT/'docs/harvest/wikisource/manifest.json'),selection=selected,excluded_prior_pages=len(prior),overlap=0,policy='validated pages, deterministic spread across unused leaves'))
    c=client('wikisource');name=book['scan_file'];md5=hashlib.md5(name.encode()).hexdigest();encoded=quote(name,safe='')
    for p in selected:
        n=p['page'];item=book['key'];ident=f'wikisource--{item}--{n:06d}'
        try:
            hp=fetch(c,p['url'],BASE/'bulk/text'/f'{ident}.html');s=hp.read_text()
            revision=re.search(r'"wgRevisionId"\s*:\s*(\d+)',s) or re.search(r'oldid=(\d+)',s)
            if not revision:raise ValueError('revision_not_bound')
            revision=int(revision[1]);raw=fetch(c,p['url']+'?oldid='+str(revision)+'&action=raw',BASE/'bulk/text'/f'{ident}.wiki')
            text=raw.read_text()
            level=re.search(r'<pagequality\b[^>]*level=["\'](\d)',text)
            if not level or int(level[1])!=4:raise ValueError('validated_status_changed')
            url=f'https://thumb.wikimedia.org/wikipedia/commons/thumb/{md5[0]}/{md5[:2]}/{encoded}/page{n}-3840px-{encoded}.jpg'
            try:r=raster('wikisource',item,n,url,c)
            except Exception:
                url=url.replace('-3840px-','-1920px-');r=raster('wikisource',item,n,url,c)
            r.pop('excluded',None)
            r.update(text_path=str(raw.relative_to(BASE)),text_sha256=sha(raw),text_revision=revision,proofreading_status='validated (4)',page_url=p['url'],edition=book['title'],edition_year=book['year'],commons_url=book['commons_url'],licence=book['licence'])
            write(BASE/'receipts/pages'/(ident+'.json'),r);print('wikisource',n,'ok',flush=True)
        except Exception as e:print('wikisource',n,type(e).__name__,str(e)[:180],flush=True)
    write(BASE/'receipts/items'/f'{book["key"]}.json',dict(pilot='wikisource',item=book['key'],title=book['title'],year=book['year'],source_url=book['index_url'],scan_file=book['scan_file'],rights=dict(scan=book['licence'],text='Wikisource CC BY-SA contribution terms; original edition separate',cloud_ocr='owner authorised P1',retention='pilot evidence',training='evaluation candidate excluded from all training inputs',redistribution='source licences require attribution')))
