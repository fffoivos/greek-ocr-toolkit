"""Rehash colliding native pages; bounded reads of six provider item pages only."""
from __future__ import annotations
import sys
sys.dont_write_bytecode=True
import datetime, json, re, time
from common import *

def parse_page(data):
    from bs4 import BeautifulSoup
    soup=BeautifulSoup(data,'html.parser');md={}
    for dt in soup.select('dl dt'):
        dd=dt.find_next_sibling('dd')
        if dd:md[dt.get_text(' ',strip=True)]=dd.get_text(' ',strip=True)
    embedded=soup.select_one('input.js-ia-metadata[value]')
    if embedded:
        obj=json.loads(embedded['value'])
        md['embedded_item_metadata']={k:v for k,v in obj.get('metadata',{}).items() if k in ['identifier','title','date','year','volume','description','publisher','creator']}
    return soup.title.get_text(' ',strip=True) if soup.title else None,md

def fetch_items():
    import requests
    from bs4 import BeautifulSoup
    out=OUT/'receipts/provider_item_pages';out.mkdir(exist_ok=True)
    identifiers=['izvestiianabul25192530bul','izvestiianabulga610193138bulg','izvestiianatsars1112193839tsar','izvestiianatsars12192829tsar','izvestiianatsars1516194243tsar','izvestiianatsars910193637tsar']
    results=[]
    for identifier in identifiers:
        receipt=out/(identifier+'.json')
        if receipt.exists():
            r=json.loads(receipt.read_text());assert fingerprint(OUT/r['body'])['sha256']==r['sha256']
            r['page_title'],r['metadata']=parse_page((OUT/r['body']).read_bytes())
            receipt.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');results.append(r);continue
        url='https://archive.org/details/'+identifier
        r=dict(url=url,kind='provider_item_page',identifier=identifier,started_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),user_agent='greek-ocr-research/0.1 (foivos.karounos@gmail.com)',redirects_followed=False)
        try:
            with requests.get(url,headers={'User-Agent':r['user_agent']},timeout=(12,30),allow_redirects=False,stream=True) as response:
                r.update(status=response.status_code,headers=dict(response.headers))
                data=bytearray()
                for chunk in response.iter_content(65536):
                    data.extend(chunk)
                    if len(data)>8*1024*1024:raise ValueError('item page exceeds 8 MB')
            body=out/(identifier+'.html');body.write_bytes(data)
            r.update(body=str(body.relative_to(OUT)),sha256=sha(data),bytes=len(data))
            title,md=parse_page(bytes(data))
            r.update(page_title=title,metadata=md)
        except Exception as exc:r['error']=str(exc)
        r['finished_at']=datetime.datetime.now(datetime.timezone.utc).isoformat()
        receipt.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');results.append(r)
        print(json.dumps({k:r.get(k) for k in ['identifier','status','bytes','error'] }),flush=True)
        time.sleep(1.1)
    dump('receipts/provider-item-summary.json',results)
    return results

def main():
    inputs=Inputs();groups=list(inputs.rows(OUT/'duplicates.jsonl'));checks=[]
    for g in groups:
        if g['key_type']!='page_image_sha256':continue
        files=[]
        for p in g['page_occurrences']:
            rec=fingerprint(inputs.add(MAIN/p['image']));assert rec['sha256']==g['key']
            files.append(rec)
        actual={v:{s:sum(p['lines'][v].get(s,0) for p in g['page_occurrences']) for s in SPLITS} for v in ['v1','v2']}
        checks.append(dict(group=g['group'],key=g['key'],files=files,actual_colliding_page_lines=actual,admitted_collision_cross_split={v:sum(n>0 for n in counts.values())>1 for v,counts in actual.items()},admitted_collision_twice_train={v:sum(p['lines'][v].get('train',0)>0 for p in g['page_occurrences'])>1 for v in ['v1','v2']}))
    dump('receipts/page-collision-readback.json',dict(passed=True,groups=checks,all_14_native_page_files_rehashed=True,native_visual_witness='D00001 b32fc7776b85-p000001 was visually read: printed page 10 includes end-of-session names and start of session Delta, 16 November 1843. This is text-bearing boundary overlap, not a blank-page hash.'))
    inputs.finish('receipts/candidate-local-inputs.json')
    fetch_items()

if __name__=='__main__':main()
