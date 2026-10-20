import json
from pilotlib import *
from acquire_pdf import render
import pypdfium2 as pdfium

if __name__=='__main__':
    books=json.loads((ROOT/'docs/harvest/openarchives/books.json').read_text())
    held={r['book_key'] for r in json.loads((ROOT/'docs/harvest/openarchives/holdout_books.json').read_text())}
    prior=json.loads((ROOT/'docs/harvest/openarchives/plan.json').read_text())['pages']
    c=client('openarchives')
    for key in ['72da5586','a8bbcc26','e315a161']:
        b=next(b for b in books if b['key']==key);assert key not in held
        try:
            pdf=fetch(c,b['pdf_url'],BASE/'bulk/pdf'/(key+'.pdf'),100_000_000)
            with pdfium.PdfDocument(pdf) as d:
                total=len(d);snippets=[];objects=[]
                for i in [0,min(4,total-1),total//2]:
                    page=d[i];tp=page.get_textpage();snippets.append(tp.get_text_range()[:500]);objects.append([o.type for o in page.get_objects()]);tp.close();page.close()
            old={p['page'] for p in prior if p['key']==key}
            ns=positions(total,20);ns=[n for n in ns if n not in old]
            for n in range(1,total+1):
                if len(ns)>=20:break
                if n not in old and n not in ns:ns.append(n)
            meta=json.loads(b['source_metadata']['metadata_json'])
            write(BASE/'receipts/items'/(key+'.json'),dict(pilot='openarchives',item=key,title=b['title'].splitlines()[0],metadata=b,source_url=b['source_url'],pdf_url=b['pdf_url'],pdf_sha256=sha(pdf),pages=total,pipeline_ocr_success=b['pipeline_metadata']['ocr_success'],sample_text_layer_snippets=snippets,sample_pdf_object_types=objects,prior_read_pages=sorted(old),sample_pages=sorted(ns),metadata_warning='S1 documents source-metadata/PDF identity inconsistencies; printed title and date require physical readback',rights=dict(scan=meta.get('Δικαιώματα','not specified'),text='per item author; metadata binding unverified',cloud_ocr='owner P1 authorisation',retention='pilot evidence',training='not released',redistribution='per item declaration unresolved')))
            render(pdf,'openarchives',key,sorted(ns),url=b['pdf_url'])
        except Exception as e:print(key,type(e).__name__,str(e)[:200],flush=True)
