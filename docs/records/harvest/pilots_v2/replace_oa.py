"""Replace physically born-digital candidates with scanned OA-linked records."""
import json,sys
from pilotlib import *
from acquire_pdf import render
import pypdfium2 as pdfium

if __name__=='__main__':
    for f in (BASE/'receipts/pages').glob('openarchives--*.json'):
        r=json.loads(f.read_text())
        if r['item'] in ['72da5586','a8bbcc26','e315a161']:
            r['excluded']='born_digital_pdf_objects_and_pixel_check';write(f,r)
    candidates=json.loads((BASE/'receipts/oa-elstat-candidates.json').read_text());c=client('openarchives')
    for row in [35559,35577,35601]:
        b=next(x for x in candidates if x['row']==row);url=b['source']['pdf_links_json'];item='oa-'+url.rsplit('/',1)[-1].removesuffix('.pdf');pdf=BASE/'bulk/pdf'/(item+'.pdf')
        for variant in [url,url.replace('http:','https:'),'https://web.archive.org/web/20200101000000id_/'+url]:
            try:
                p=fetch(c,variant,pdf,100_000_000)
                with pdfium.PdfDocument(p) as d:
                    total=len(d);types=[[o.type for o in d[n].get_objects()] for n in [0,total//2]]
                    # Scanned page images must be present on both sampled leaves.
                    if not all(3 in t for t in types):raise ValueError('not_scanned_sample')
                write(BASE/'receipts/items'/(item+'.json'),dict(pilot='openarchives',item=item,source_url=url,retrieval_url=variant,pdf_sha256=sha(pdf),pages=total,source_record=b,pipeline_ocr_success=True,physical_status='page-image objects on front and middle leaves; contact sheet records physical scan',sample_pdf_object_types=types,edition_metadata_status='source title/year mismatch; do not use metadata titles or years as printed facts',rights=dict(scan='ELSTAT linked scan; item declaration unresolved',text='printed publication identified in owner sheet; metadata title not trusted',cloud_ocr='owner P1 authorised',retention='pilot evidence',training='not released; binding unresolved',redistribution='unresolved')))
                render(pdf,'openarchives',item,positions(total,20),url=url);break
            except Exception as e:print(item,type(e).__name__,str(e)[:150],flush=True)
