"""Bound T23 working disk: discard only reproducible gate-rejected intermediates.

Keep every accepted native PNG and native examples of every rejection flag.
For other rejects, retain a preview, original hash, PDF hash/bitstream and render
recipe. Restoration streams the original PDF, verifies its SHA, re-renders the
one native page, verifies identical PNG bytes, and deletes the temporary PDF.
No Google calls or requested line/crop/compiled artifacts are removed.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import json
from pathlib import Path

from PIL import Image
import pypdfium2 as pdfium

from scripts.harvest.parliament import OUT, BULK, REPO, sha, relative
from greekocr.harvest.readers import atomic


def keep_examples(pages, extra=()):
    keep,seen=set(extra),set()
    for p in sorted(pages,key=lambda p:p['id']):
        if p['harvest_accepted']:continue
        for flag in p['gate']['flags']:
            if flag not in seen:keep.add(p['id']);seen.add(flag)
    return keep


def preview(page):
    source=REPO/page['image'];target=BULK/'rejected_previews'/(page['id']+'.jpg')
    if page['harvest_accepted']:raise ValueError('accepted PNGs cannot enter reject retention')
    if sha(source)!=page['image_sha256']:raise ValueError('rejected native PNG changed')
    size=source.stat().st_size
    with Image.open(source) as image:
        original_size=list(image.size)
        image.thumbnail((1200,1600),Image.Resampling.LANCZOS)
        target.parent.mkdir(parents=True,exist_ok=True);image.save(target,'JPEG',quality=85)
        preview_size=list(image.size)
    return dict(page_id=page['id'],image=page['image'],image_sha256=page['image_sha256'],native_bytes=size,
        native_size=original_size,preview=relative(target),preview_sha256=sha(target),preview_size=preview_size,
        pdf_sha256=page['pdf_sha256'],bitstream=page['bitstream'],page=page['page'],book=page['book'],
        dpi=200,mode='L',png_compress_level=1,flags=page['gate']['flags'])


def prepare():
    pages=json.loads((OUT/'manifest.json').read_text())
    visual=json.loads((OUT/'fetch_visual_qa.json').read_text())
    keep=keep_examples(pages,[p['page_id'] for p in visual['samples']])
    path=OUT/'page_image_retention.json'
    previous=json.loads(path.read_text())['pages'] if path.exists() else []
    done={p['page_id']:p for p in previous}
    rejected=[p for p in pages if not p['harvest_accepted']]
    pending=[p for p in rejected if p['id'] not in done]
    with ThreadPoolExecutor(max_workers=3) as pool:
        for i,result in enumerate(pool.map(preview,pending),1):
            retained=result['page_id'] in keep
            result['native_retained']=retained
            done[result['page_id']]=result
            # Journal all source/preview custody before deleting this intermediate.
            receipt=dict(schema='t23-page-image-retention-1',pages=list(done.values()),
                accepted_native_kept=sum(p['harvest_accepted'] for p in pages),
                rejected_native_kept=sum(p['native_retained'] for p in done.values()),
                rejected_native_removed=sum(not p['native_retained'] for p in done.values()),
                bytes_released=sum(p['native_bytes'] for p in done.values() if not p['native_retained']))
            atomic(path,receipt)
            if not retained:(REPO/result['image']).unlink()
            if i%50==0:print(f'rejected previews {i}/{len(pending)}; removed only gate rejects',flush=True)
    # Complete any journaled removal after interruption.
    for r in done.values():
        if not r['native_retained']:(REPO/r['image']).unlink(missing_ok=True)
    print(json.dumps({k:v for k,v in json.loads(path.read_text()).items() if k!='pages'}),flush=True)


def restore(page_id):
    from greekocr.harvest.parliament_http import ParliamentHTTP
    page=next(p for p in json.loads((OUT/'manifest.json').read_text()) if p['id']==page_id)
    target=REPO/page['image']
    if target.exists():
        if sha(target)!=page['image_sha256']:raise ValueError('existing PNG changed')
        return
    pdf=BULK/'pdf'/(page['book']+'.restore.pdf')
    try:
        bitstream=page['bitstream']
        receipt=ParliamentHTTP(BULK/'http_t23').download(bitstream['url'],pdf,bitstream['size'],bitstream['checksum'])
        if receipt['sha256']!=page['pdf_sha256']:raise ValueError('original PDF changed')
        with pdfium.PdfDocument(pdf) as doc:
            with closing(doc[page['page']-1]) as pdfpage:
                bitmap=pdfpage.render(scale=200/72,grayscale=True)
                image=bitmap.to_pil().copy().convert('L');bitmap.close()
        image.save(target,compress_level=1)
        if sha(target)!=page['image_sha256']:
            target.unlink();raise ValueError('restored PNG bytes differ from original render')
    finally:pdf.unlink(missing_ok=True)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--restore',metavar='PAGE_ID');args=p.parse_args()
    if args.restore:restore(args.restore)
    else:prepare()


if __name__=='__main__':main()
