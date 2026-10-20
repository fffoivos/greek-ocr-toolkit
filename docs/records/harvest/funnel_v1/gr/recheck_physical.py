"""Hash-bound construction refinement: no new witnesses or OCR, PDFs discarded."""
from funnellib import *

def run():
    docs={r['metadata_id']:r for r in rows(BASE/'receipts/oa-external-physical.jsonl') if r['success'] and r.get('mode')=='sequential'}
    for d in json.loads((BASE/'receipts/oa-projection-rebinding.json').read_text())['documents']:
        d=dict(d,metadata_id=d['id'],http_sha256=d['fresh_pdf_sha256']);docs.setdefault(d['id'],d)
    for ident,doc in docs.items():
        if not any(p['classification']=='full_page_image_with_visible_text_uncertain' for p in doc['physical_pages']):continue
        c=HTTP('openarchives');start=time.time();attempt=dict(source='openarchives',item=ident,url=doc['url'],kind='construction_recheck',mode='structural_recheck',started_at=stamp(),success=False,decoded_pages=0)
        result=dict(id=ident,url=doc['url'],expected_PDF_sha256=doc['http_sha256'],success=False)
        try:
            r,b=c.get(doc['url'],'pdf_structure_recheck',90_000_000)
            if sha(b)!=doc['http_sha256']:raise Blocked('PDF changed; construction refinement not applied')
            with pdfium.PdfDocument(b) as pdfdoc:
                result['physical_pages']=[]
                for old in doc['physical_pages']:
                    with contextlib.closing(pdfdoc[old['page']-1]) as p:result['physical_pages'].append(dict(page=old['page'],**physical(p)))
                result.update(success=True,PDF_sha256=r['sha256'])
            attempt.update(success=True,bytes=r['bytes'],page_count=len(pdfdoc) if False else doc['page_count'])
        except Exception as e:result['error']=str(e)[:350];attempt['error']=str(e)[:350]
        attempt.update(ended_at=stamp(),total_seconds=time.time()-start);append(BASE/'receipts/media.jsonl',attempt)
        append(BASE/'receipts/physical-rechecks.jsonl',result)
        print('recheck',ident,result['success'],[p['classification'] for p in result.get('physical_pages',[])],flush=True)

if __name__=='__main__':run()
