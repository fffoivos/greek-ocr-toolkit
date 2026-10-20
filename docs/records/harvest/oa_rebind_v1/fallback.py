"""Fetch identity-bound aggregator records when provider transport is unavailable.

This is explicitly secondary evidence, never labelled a provider-page verification.
"""
import sys
sys.dont_write_bytecode=True
import json,re
import fetch_catalogues as f
from audit import norm,canonical_url

def parse(book,r,body):
    s=f.BeautifulSoup(body,'html.parser');fields={}
    for group in s.select('div.form-group'):
        label=group.select_one('label');value=group.select_one('div.col-sm-9')
        if label and value:fields[label.get_text(' ',strip=True)]=value.get_text(' ',strip=True)
    title=s.select_one('h1');date=fields.get('Χρονολογία')
    ys=re.findall(r'(?<!\d)(?:1[5-9]\d{2}|20[0-2]\d)(?!\d)',date or '')
    links=[a['href'] for a in s.select('a[href]')]
    matched=[u for u in links if u.startswith(('https://','http://')) and canonical_url(u)==canonical_url(book['link_table']['external_link'])]
    return dict(book_key=book['book_key'],url=r['url'],http_receipt=r,title=title.get_text(' ',strip=True) if title else None,date_raw=date,year=int(ys[0]) if len(set(ys))==1 else None,fields=fields,provider_item_link_matches=matched,basis='Fresh Open Archives EDM record with exact provider item URL; provider page remains unavailable',provider_verified=False)

if __name__=='__main__':
    books=json.loads((f.OUT/'receipts/initial-bindings.json').read_text())
    for b in books:
        if b['link_table']['collection_slug']!='Dione':continue
        p=f.OUT/'receipts/aggregator-fallback'/f"{b['book_key']}.json"
        try:
            if p.exists():
                d=json.loads(p.read_text());r=d['http_receipt'];body=(f.OUT/r['body']).read_bytes()
            else:r,body=f.get(b['link_table']['edm_url'],'aggregator_fallback')
            result=parse(b,r,body);assert result['provider_item_link_matches']
            f.write('receipts/aggregator-fallback/'+b['book_key']+'.json',result)
            print(b['book_key'],result['title'],result['year'],flush=True)
        except Exception as e:print(b['book_key'],str(e),flush=True)
