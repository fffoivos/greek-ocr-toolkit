#!/usr/bin/env python3
"""Offline artifact audit and O4c handoff; never writes .git or contacts network."""
from greekocr._vendor.scripts.fetch.o4c_common import *
from greekocr._vendor.scripts.fetch.o4c_finalize import qualify, INPUTS

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--in-progress',action='store_true');args=parser.parse_args()
    rows=read_rows(EVIDENCE/'candidates.jsonl');summary=json.loads((EVIDENCE/'summary.json').read_text())
    schema=json.loads((EVIDENCE/'candidate_schema.json').read_text());required=set(schema['required'])
    assert len(rows)==summary['documents']
    assert len({r['candidate_id'] for r in rows})==len(rows)
    assert [r['rank'] for r in rows]==list(range(1,len(rows)+1))
    assert [r['estimated_target_lines'] for r in rows]==sorted((r['estimated_target_lines'] for r in rows),reverse=True)
    assert sum(r['polytonic_document'] for r in rows)==summary['polytonic_docs']
    assert sum(r['cyrillic_document'] for r in rows)==summary['cyrillic_docs']
    if not args.in_progress:assert summary['parliament_catalogue_coverage']['all_pages_traversed']
    baseline_rows=read_rows(ROOT/'docs/evidence/s17/pdf_cache_refetch.jsonl')
    baseline={r['item_id'] for r in baseline_rows};baseline_md5={r['content_md5'].lower() for r in baseline_rows}
    media_replay=HTTP('audit',offline=True);prefix_count=0
    for r in rows:
        assert required<=r.keys(),r['candidate_id']
        assert qualify(r) and not r.get('existing_s17')
        assert r['schema_version']=='o4c-1' and r['status']=='candidate-silver-needs-adjudication'
        assert r['rights']['raw'] and r['rights']['compatible']
        assert 0<=r['polytonic_ratio']<=1 and 0<=r['cyrillic_ratio']<=1
        assert r['estimated_target_lines']==(r['estimated_polytonic_lines'] or 0)+(r['estimated_cyrillic_lines'] or 0)>0
        if r['source']=='parliament':
            assert r['document_id'] not in baseline and len(r['text_layer']['page_indices'])==1
            assert r.get('scan_md5') not in baseline_md5
            assert r['text_layer']['scan_status']=='verified-large-raster-object'
        elif r['source']=='archive':
            assert r.get('text_url') and r['text_layer']['probe_sha256']
            p=r['media_probe'];assert p['status']=='verified-file-prefix' and p['bytes']<=512
            m,b=media_replay.get(p['probe_url'],range_header='bytes=0-511',limit=512)
            assert m['sha256']==p['prefix_sha256'] and m['status']==206 and b.startswith((b'%PDF-',b'AT&TFORM'))
            prefix_count+=1
    assert media_replay.requests==0
    reviews=read_rows(EVIDENCE/'print_reviews.jsonl');excluded=set()
    for r in reviews:
        if r['status'] in ('unverified-conflict','non-target-sample','unverified-scan-origin'):excluded.add((r['source'],r['document_id']))
        for p in r['page_probes']:
            assert hashlib.sha256((ROOT/p['local_path']).read_bytes()).hexdigest()==p['sha256']
    assert not excluded&{(r['source'],r['document_id']) for r in rows}
    page_counts={}
    for p in (EVIDENCE/'print_probes').glob('*.jpg'):
        identifier=p.stem.rsplit('_n',1)[0];page_counts.setdefault(identifier,set()).add(int(p.stem.rsplit('_n',1)[1]))
    page_counts.setdefault('bub_gb_VkZMAAAAYAAJ',set()).add(5)
    assert all(len(pages)<=3 for pages in page_counts.values())
    ledger=read_rows(EVIDENCE/'transfer.jsonl')
    charged=sum(r['bytes'] for r in ledger);assert charged<=BUDGET
    assert sum(summary['transfer_assigned_to_library'].values())==summary['payload_bytes_including_preflight_reserve']
    assert all(summary['sources'][source]['transfer_payload_bytes']==summary['transfer_assigned_to_library'].get(source,0) for source in summary['sources'])
    if not args.in_progress:assert charged==summary['payload_bytes_including_preflight_reserve'],'summary/ledger changed; rebuild summary after crawlers stop'
    archive_scan_reads=[r for r in ledger if r.get('source') in ('archive','archive_media','archive_visual') and r.get('bytes',0)>0 and
      (r.get('headers',{}).get('content-type','').startswith('application/pdf') or urllib.parse.urlsplit(r.get('url','')).path.lower().endswith(('.pdf','.djvu')))
      and (r.get('range')!='bytes=0-511' or r['bytes']>512)]
    assert not archive_scan_reads
    parliament_full_media=[r for r in ledger if r.get('source')=='parliament' and '/bitstreams/' in r.get('url','') and r['url'].endswith('/content') and r.get('bytes',0)>0 and not r.get('range')]
    assert not parliament_full_media
    # Bind every ranked Parliament measurement to its sparse recordings; no transport fallback.
    replay=[]
    for sample in (r for r in rows if r['source']=='parliament'):
        copy=json.loads(json.dumps(sample))
        h=HTTP('audit',offline=True);probe_pdf(h,copy)
        assert h.requests==0 and copy['text_layer']['status']=='verified'
        assert copy['text_layer']['text_sha256']==sample['text_layer']['text_sha256']
        assert copy['pages']==sample['pages'] and copy['text_layer']['page_indices']==sample['text_layer']['page_indices']
        replay.append({'document_id':sample['document_id'],'http_requests':h.requests,'text_sha256':copy['text_layer']['text_sha256']})
    paths=list((ROOT/'scripts/fetch').glob('o4c*.py'))+[ROOT/'bench/tests/test_o4c.py',ROOT/'O4c_NOTES.md']
    paths+=[EVIDENCE/name for name in ('candidates.jsonl','candidate_schema.json','summary.md','summary.json','duplicates.json','transfer.jsonl','tests.log','print_reviews.jsonl','media_probes.jsonl','discovery_merged.jsonl')]
    paths+=[EVIDENCE/name for name in INPUTS]
    paths+=list(EVIDENCE.glob('*.state.json'))+list((EVIDENCE/'print_probes').glob('*'))
    paths+=list(EVIDENCE.glob('*_events.jsonl'))
    paths+=list((EVIDENCE/'fixtures').glob('*'))
    bindings={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}
    report={'status':'passed','checks':['schema-required-fields','unique-document-IDs','rank-order','licence-and-script-gate','S17-ID-and-content-MD5-exclusion','printed-script-conflict-exclusion','print-probe-hash-and-three-page-bound','single-PDF-page-bound','transfer-budget','Archive-scan-header-only','offline-media-prefix-replay','no-Parliament-full-media-request','offline-all-ranked-PDF-replay'],
      'documents':len(rows),'polytonic_docs':summary['polytonic_docs'],'cyrillic_docs':summary['cyrillic_docs'],'charged_bytes':charged,'offline_pdf_replays':replay,
      'offline_media_prefix_replays':{'documents':prefix_count,'http_requests':media_replay.requests}}
    write_json(EVIDENCE/'audit.json',report)
    bindings['docs/evidence/o4c/audit.json']=hashlib.sha256((EVIDENCE/'audit.json').read_bytes()).hexdigest()
    handoff={'task':'O4c','status':'in-progress' if args.in_progress else 'done-with-explicit-unverified-coverage','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'documents':len(rows),'polytonic_docs':summary['polytonic_docs'],'cyrillic_docs':summary['cyrillic_docs'],
      'manifest':'docs/evidence/o4c/candidates.jsonl','summary':'docs/evidence/o4c/summary.md','notes':'O4c_NOTES.md','audit':'docs/evidence/o4c/audit.json',
      'tests_log':'docs/evidence/o4c/tests.log','transfer_payload_bytes_including_reserve':charged,'transfer_limit_bytes':BUDGET,
      'scripts':[str(p.relative_to(ROOT)) for p in (ROOT/'scripts/fetch').glob('o4c*.py')],
      'git_writes':False,'o4b_files_touched':False,'training_launched':False,'bulk_scan_downloads':False,
      'remaining_unverified':['snapshot-complete unique Parliament record/PDF census','unprobed documents and missing/restricted licences','Anemi scan rights and OCR','Wikimedia API scan rights/OCR/proofread-gold due robots','other-library qualifying scan supply','IA embedded PDF text and full-file integrity beyond bounded header access','silver-to-gold text/geometry adjudication and usable line count'],
      'parliament_catalogue_state':summary['parliament_catalogue_state'],'file_sha256':bindings}
    write_json(ROOT/'O4c_HANDOFF.json',handoff)
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
