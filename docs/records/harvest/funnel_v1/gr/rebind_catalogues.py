"""Recover dates/titles from actual repository records, not the faulty projection."""
from funnellib import *
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import unquote

def one(doc):
    ext=next(e for e in doc['external_records'] if e['collection_slug']==doc['link_table_collection_unambiguous'])
    url=ext.get('external_link');result=dict(id=doc['id'],pdf_url=doc['url'],collection_slug=ext['collection_slug'],catalogue_url=url,verified=False)
    if not url:return result
    c=HTTP('openarchives')
    try:
        r,b=c.get(url,'rebind_catalogue');s=BeautifulSoup(b,'html.parser')
        def val(names):
            for n in names:
                el=s.select_one('meta[name="'+n+'"],meta[property="'+n+'"]')
                if el and el.get('content'):return el['content']
        title=val(['citation_title','DC.title','dc.title','DCTERMS.title','og:title'])
        date=val(['citation_date','citation_publication_date','DC.date.issued','dc.date.issued','DCTERMS.issued'])
        year=re.search(r'\b(1[5-9]\d\d|20[0-2]\d)\b',date or '')
        pdfs=[urljoin(url,a['href']) for a in s.select('a[href]')]+[el['content'] for el in s.select('meta[name=citation_pdf_url][content]')]
        path=unquote(urlsplit(doc['url']).path)
        matched=any(unquote(urlsplit(u).path)==path for u in pdfs)
        result.update(title=title,year=int(year[0]) if year else None,date_raw=date,metadata_sha256=r['sha256'],attachment_path_match=matched,
                      verified=bool(title and matched),licence=val(['DC.rights','dc.rights','DCTERMS.rights']),language=val(['DC.language','dc.language','citation_language']))
    except Exception as e:result['error']=str(e)[:350]
    write(BASE/'receipts/oa-catalogue-rebinding'/(doc['id']+'.json'),result)
    return result

if __name__=='__main__':
    docs=json.loads((BASE/'receipts/oa-projection-rebinding.json').read_text())['documents']
    # Different repositories proceed independently; the shared host ledger keeps starts polite.
    with ThreadPoolExecutor(max_workers=3) as pool:result=list(pool.map(one,docs))
    print('Rebound fresh catalogue',sum(r['verified'] for r in result),'of',len(result),flush=True)
