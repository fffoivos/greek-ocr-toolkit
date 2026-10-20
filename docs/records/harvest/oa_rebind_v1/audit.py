"""Read-only wave-4 provenance audit. Writes only beside this file."""
from __future__ import annotations
import collections, datetime, hashlib, html, importlib.util, json, re, sys, unicodedata
sys.dont_write_bytecode=True
from pathlib import Path
import pyarrow.parquet as pq

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sys.path.insert(0, str(ROOT))
spec=importlib.util.spec_from_file_location('oa_binding_contract',ROOT/'greekocr/harvest/openarchives.py')
contract=importlib.util.module_from_spec(spec);spec.loader.exec_module(contract)
canonical_url,urls,document_type=contract.canonical_url,contract.urls,contract.document_type
MAIN = ROOT.parent / 'greek-ocr-toolkit'
OA = MAIN / 'docs/harvest/openarchives'
COL = MAIN / 'docs/harvest/collection'
GR = ROOT.parent / 'greek-ocr-toolkit-sol-funnel-gr/docs/harvest/funnel_v1/gr'

def sha(data): return hashlib.sha256(data).hexdigest()
def write(path, data):
    path = OUT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
def rows(path):
    with path.open() as f:
        for line in f:
            if line.strip(): yield json.loads(line)
def norm(s):
    s = re.sub(r'\s*\((?:EL|EN)\)\s*$', '', html.unescape(s or ''), flags=re.I)
    return ' '.join(unicodedata.normalize('NFC', s).split()).casefold()
def input_receipt(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return dict(path=str(p),bytes=p.stat().st_size,sha256=h.hexdigest())

def prepare():
    books=json.loads((OA/'books.json').read_text())
    acquisitions=json.loads((OA/'acquisition_results.json').read_text())
    assert {b['key'] for b in books}=={b['key'] for b in acquisitions if b['outcome']=='downloaded'}
    assert len(books)==len({b['book'] for b in books})==89
    hf=json.loads((GR/'receipts/hf-link-table.json').read_text())
    table=GR/hf['local_dir']/hf['file']
    assert sha(table.read_bytes())==hf['sha256']
    write('receipts/hf-link-table.json',dict(**hf,source_receipt=str(GR/'receipts/hf-link-table.json'),verified_local_path=str(table)))
    downloads={b['key']:json.loads((MAIN/b['download_receipt']).read_text()) for b in books}
    targets={canonical_url(b['pdf_url']) for b in books}|{canonical_url(d['url']) for d in downloads.values()}
    index=collections.defaultdict(list)
    for batch in pq.ParquetFile(table).iter_batches(batch_size=8192):
        for row in batch.to_pylist():
            matched=collections.defaultdict(list)
            for field in ['pdf_links_json','refined_pdf_links_json']:
                for u in urls(row.get(field)):
                    c=canonical_url(u)
                    if c in targets:matched[c].append(dict(field=field,url=u))
            for c, matches in matched.items():
                index[c].append({k:row.get(k) for k in ['collection_slug','external_link','edm_url','type','status_code']}|dict(matched_links=matches))
    result=[];inputs=[OA/n for n in ['books.json','candidates.json','inventory.json','records.jsonl','admitted.jsonl','holdout_books.json','identity_audit.json','acquisition_results.json','selection.json','selection_config.json','manifest.json','admission_summary.json']]
    for b in books:
        p=MAIN/b['download_receipt'];d=json.loads(p.read_text());inputs.append(p)
        assert d['sha256']==b['pdf_sha256'] and d['bytes']==b['pdf_bytes'] and d['status']==200
        a=OA/'acquisitions'/f"{b['key']}.json";inputs.append(a)
        ab=json.loads(a.read_text())['book']
        assert ab['pdf_sha256']==b['pdf_sha256'] and ab['pdf_url']==b['pdf_url']
        matches=index[canonical_url(b['pdf_url'])]
        assert len({(r['collection_slug'],r['external_link'],r['edm_url'],r['type']) for r in matches})<=1, matches
        fresh=matches[0] if matches else None
        pipe=b.get('pipeline_metadata',{})
        result.append(dict(book_id=b['book'],book_key=b['key'],pdf_url=b['pdf_url'],canonical_pdf_url=canonical_url(b['pdf_url']),download_final_url=d['url'],download_final_url_matches=index[canonical_url(d['url'])],download_url_changed=canonical_url(d['url'])!=canonical_url(b['pdf_url']),pdf_sha256=d['sha256'],pdf_bytes=d['bytes'],actual_download_page_count=b['page_count'],download_receipt=b['download_receipt'],recorded={k:b.get(k) for k in ['title','year','decade','collection_slug','type','type_raw','source_url','licence','attribution','metadata_row']},old_pipeline_metadata={k:pipe.get(k) for k in ['ocr_success','page_count','pages_total','polytonic_ratio','url','processing_stage','needs_ocr']},link_table=fresh,all_link_table_matches=matches,collection_mismatch=bool(fresh and fresh['collection_slug']!=b['collection_slug']),type_mismatch=bool(fresh and document_type(fresh['type'])!=b['type'])))
    write('receipts/initial-bindings.json',result)
    write('receipts/input-files.json',[input_receipt(p) for p in inputs])
    print(json.dumps(dict(books=len(result),collection_mismatch=sum(b['collection_mismatch'] for b in result),not_in_table=sum(not b['link_table'] for b in result),actual_collections=dict(collections.Counter(b['link_table']['collection_slug'] for b in result if b['link_table'])))))

if __name__=='__main__':prepare()
