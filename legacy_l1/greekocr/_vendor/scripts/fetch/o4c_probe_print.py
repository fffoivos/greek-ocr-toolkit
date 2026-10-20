#!/usr/bin/env python3
"""Bounded IA page-JPEG evidence for manual printed-script review (no OCR inference)."""
from greekocr._vendor.scripts.fetch.o4c_common import *

def page_url(identifier,page):
    return 'https://archive.org/download/'+urllib.parse.quote(identifier,safe='')+'/page/n'+str(page)+'.jpg'

def existing_pages(identifier,root=EVIDENCE):
    pages=set()
    for p in (root/'print_probes').glob(identifier+'_n*.json'):
        pages.add(int(p.stem.rsplit('_n',1)[1]))
    # The earlier blank-page experiment remains part of this item's three-page cap.
    if identifier=='bub_gb_VkZMAAAAYAAJ' and (root/'fixtures/korrespondenzblatt_page5.jpg').exists():pages.add(5)
    return pages

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--item',required=True)
    p.add_argument('--page',type=int,default=20,help='zero-based BookReader image index')
    p.add_argument('--offline',action='store_true');args=p.parse_args()
    if args.page<0:raise ValueError('negative page')
    pages=existing_pages(args.item)
    if args.page not in pages and len(pages)>=3:raise ProbeError('three-page per-document probe cap reached')
    merged={r['document_id']:r for r in read_rows(EVIDENCE/'discovery_merged.jsonl') if r['source']=='archive'}
    r=merged[args.item]
    if not r['rights']['compatible']:raise ProbeError('compatible record rights required before image probe')
    directory=EVIDENCE/'print_probes';directory.mkdir(exist_ok=True)
    target=directory/(args.item+'_n'+str(args.page)+'.jpg');receipt=target.with_suffix('.json')
    if target.exists() and receipt.exists():
        m=json.loads(receipt.read_text())
        if hashlib.sha256(target.read_bytes()).hexdigest()!=m['sha256']:raise ProbeError('page evidence hash mismatch')
        print(str(target.relative_to(ROOT)));return
    h=HTTP('archive_visual',offline=args.offline)
    m,data=h.get(page_url(args.item,args.page),limit=8_000_000)
    if not data.startswith(b'\xff\xd8\xff'):raise ProbeError('response is not a JPEG scan page')
    target.write_bytes(data);write_json(receipt,m)
    print(str(target.relative_to(ROOT)))
if __name__=='__main__':main()
