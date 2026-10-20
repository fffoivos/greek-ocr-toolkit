#!/usr/bin/env python3
"""Create portable recorded excerpts from this run's HTTP cache; zero network."""
from o4c_common import *
def main():
    folder=EVIDENCE/'fixtures';manifest={}
    metas=[(p,json.loads(p.read_text())) for p in (EVIDENCE/'http').glob('*.json')]
    def record(name,match,extract=None,status=200):
        for p,m in metas:
            if match(m) and m['status']==status:
                data=p.with_suffix('.body').read_bytes()
                if extract:data=(json.dumps(extract(json.loads(data)),ensure_ascii=False,indent=2)+'\n').encode()
                (folder/name).write_bytes(data);manifest[name]={'url':m['url'],'range':m.get('range'),'response_sha256':m['sha256'],'fixture_sha256':hashlib.sha256(data).hexdigest(),'excerpt':extract is not None,'fetched_at':m['fetched_at']};return
    record('parliament_item.json',lambda m:m['url'].startswith('https://digitallibrary.parliament.gr/records/api/core/items/deed75c5-d87d-499b-9f43-1dab990922ba?'),lambda d:{k:d[k] for k in ('uuid','name','metadata','type')})
    record('parliament_bundles.json',lambda m:m['url'].endswith('/items/deed75c5-d87d-499b-9f43-1dab990922ba/bundles?size=100'))
    record('parliament_bitstreams.json',lambda m:m['url'].endswith('/bundles/508d8657-85fd-4e71-9b43-1b4a338079fb/bitstreams?size=100'))
    record('archive_greek_metadata.json',lambda m:m['url']=='https://archive.org/metadata/b28038630')
    record('archive_cyrillic_metadata.json',lambda m:m['url']=='https://archive.org/metadata/tolstojvojnaimirtom_3_4')
    record('archive_pdf_prefix.bin',lambda m:m.get('source')=='archive_media' and '/b28038630/' in m['url'] and m.get('range')=='bytes=0-511',status=206)
    record('anemi_search.html',lambda m:m['url'].startswith('https://anemi.lib.uoc.gr/search/') and 'store_query' in m['url'])
    record('anemi_standards.html',lambda m:m['url']=='https://anemi.lib.uoc.gr/tutorials/Standards/')
    record('commons_robots.txt',lambda m:m['url']=='https://commons.wikimedia.org/robots.txt')
    record('gallica_robots.txt',lambda m:m['url']=='https://gallica.bnf.fr/robots.txt')
    record('anemi_robots.txt',lambda m:m['url']=='https://anemi.lib.uoc.gr/robots.txt')
    record('wellcome_results.json',lambda m:m['url'].startswith('https://api.wellcomecollection.org/catalogue/v2/works?query='))
    for lang,predicate in [('greek',lambda u:'b28038630_djvu.txt' in u),('cyrillic',lambda u:'tolstojvojnaimirtom_3_4_djvu.txt' in u)]:
        for p,m in metas:
            if predicate(m['url']) and m['status']==200:
                data=p.with_suffix('.body').read_bytes().decode('utf-8','replace')[:8000];name='archive_'+lang+'_text.txt';(folder/name).write_text(data)
                manifest[name]={'url':m['url'],'response_sha256':m['sha256'],'fixture_sha256':hashlib.sha256(data.encode()).hexdigest(),'excerpt':True,'fetched_at':m['fetched_at'],'measurement':metrics(data)};break
    write_json(folder/'recordings.json',manifest);print(list(manifest))
if __name__=='__main__':main()
