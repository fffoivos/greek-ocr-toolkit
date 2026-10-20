#!/usr/bin/env python3
"""Offline audit of the bounded authenticated Anemi discovery and unchanged ranking.

Run after the crawler and finalizer stop. This never constructs an HTTP client.
Credential values, if present, are read only from os.environ for a boolean privacy
check and are never included in output or evidence.
"""
import html
import posixpath
from collections import Counter, defaultdict
from greekocr._vendor.scripts.fetch.o4c_common import *
from greekocr._vendor.scripts.fetch.o4c_discover_anemi import ANEMI_BUDGET, BASE


def main():
    rows=read_rows(EVIDENCE/'anemi.jsonl')
    scoped=[r for r in rows if r.get('catalogue_queries') and r.get('in_scope')]
    state=json.loads((EVIDENCE/'anemi.state.json').read_text())
    terms=json.loads((EVIDENCE/'anemi_terms.json').read_text())
    ledger=read_rows(EVIDENCE/'transfer.jsonl')
    assert len({r['document_id'] for r in rows})==len(rows)
    assert all(r['source']=='anemi' and r['schema_version']=='o4c-1' for r in rows)
    assert len(state['streams'])==64 and state['catalogue_complete'] and state['inventory_complete']
    assert all(s['complete'] and s['offset']==1+s['records_returned'] for s in state['streams'].values())
    queried={u for s in state['streams'].values() for u in s['urls']}
    nonempty={u for r in rows for u in r.get('catalogue_queries',[])}
    assert nonempty<=queried and set(state['media_inventories'])==nonempty
    assert all(x['complete'] for x in state['media_inventories'].values())
    assert state['documents']==len(scoped)
    assert state['polytonic_docs']==sum(r.get('polytonic_document',False) for r in scoped)
    assert state['pdf_with_layer']==sum(r['text_layer']['status']=='verified' for r in scoped)
    for r in scoped:
        assert 1800<=r['year']<=1950 and r.get('catalogue_materials')
        assert set(r['catalogue_materials'])<=set(('010','020'))
        assert set(r['catalogue_languages'])<=set(('gre','grc'))
        assert r['record_url']==BASE+r['document_id']
        assert terms['quote'] in r['rights']['raw'] and not r['rights']['compatible']
        assert r['licence_tier'].startswith('research-access-only')
        assert all(k in r for k in ('author','creator','pages','size','pdf_availability'))
        assert r['metadata_status'].startswith('verified-source-')
        if r.get('download_url'):
            assert r['scan_files'] and r['download_url']==r['scan_files'][0]['url']
            assert r['pages']==r['scan_files'][0]['pages'] and r['size']==r['scan_files'][0]['size']
    sampled=[r for r in scoped if r['text_layer'].get('page_indices')]
    for r in sampled:
        tl=r['text_layer'];m=tl['measurement'];n=tl['sample_pages']
        assert 1<=n<=3 and len(tl['page_indices'])==n
        assert len(set(tl['page_indices']))==n
        assert [p['page_index'] for p in tl['page_measurements']]==tl['page_indices']
        assert tl['original_pdf_embedded_text']=='unverified; viewer derivative measured'
        q=urllib.parse.parse_qs(urllib.parse.urlsplit(tl['probe_url']).query)
        assert q['pagenum']==[str(n)] and int(q['pageno'][0])-1==tl['page_indices'][0]
        binding=next((x for x in ledger if x.get('url')==tl['probe_url'] and x['sha256']==tl['probe_sha256']),None)
        assert binding and binding['status']==200 and binding['bytes']==tl['probe_bytes']
        pp=tl['page_measurements']
        for key in ('greek_letters','polytonic_letters','cyrillic_letters','letters','sample_lines',
                    'sample_polytonic_lines','sample_cyrillic_lines'):
            assert m[key]==sum(p[key] for p in pp)
        chars=sum(p['chars'] for p in pp)
        assert m['chars']==chars+(n-1 if chars else 0)
        assert m['chars_per_page']==m['chars']/n
        assert m['polytonic_ratio']==(m['polytonic_letters']/m['greek_letters'] if m['greek_letters'] else 0)
        assert m['cyrillic_ratio']==(m['cyrillic_letters']/m['letters'] if m['letters'] else 0)
        assert r['polytonic_ratio']==m['polytonic_ratio'] and r['cyrillic_ratio']==m['cyrillic_ratio']
        assert r['estimated_polytonic_lines']==m['estimated_polytonic_lines']
        assert r['estimated_cyrillic_lines']==m['estimated_cyrillic_lines']
        assert bool(r.get('polytonic_document'))==(m['greek_letters']>=50 and m['polytonic_ratio']>=.01)
        assert tl['status']==('verified' if m['chars'] else 'empty-sample')
    payload=sum(x['bytes'] for x in ledger)
    assert payload<=ANEMI_BUDGET and state['payload_bytes_cumulative']==payload
    authenticated=[x for x in ledger if x.get('body_storage')=='memory-only']
    assert authenticated and all(x['source']=='anemi' for x in authenticated)
    forbidden_headers={'cookie','set-cookie','location','authorization'}
    for x in authenticated:
        assert not forbidden_headers.intersection(k.lower() for k in x['headers'])
    starts=defaultdict(list);page_sets=defaultdict(set)
    for x in ledger:
        parts=urllib.parse.urlsplit(x.get('url') or '')
        if parts.hostname!='anemi.lib.uoc.gr':continue
        assert not forbidden_headers.intersection(k.lower() for k in x.get('headers',{}))
        path=posixpath.normpath(urllib.parse.unquote(parts.path))
        assert path not in ('/tools','/db') and not path.startswith(('/tools/','/db/'))
        assert path!='/php/pdf_dump.php'  # Full-PDF CAPTCHA was never submitted.
        if x.get('request_started_at'):
            starts[parts.hostname].append(datetime.datetime.fromisoformat(x['request_started_at']).timestamp())
        if path=='/php/pdf_split.php':
            q=urllib.parse.parse_qs(parts.query);n=int(q.get('pagenum',['1'])[0])
            first=int(q['pageno'][0])-1
            assert 1<=n<=3
            page_sets[q['filename'][0]].update(range(first,first+n))
    gaps=[b-a for values in starts.values() for a,b in zip(values,values[1:])]
    assert gaps and min(gaps)>=1.99 and all(len(p)<=3 for p in page_sets.values())
    fixture_dir=EVIDENCE/'fixtures'
    recordings=json.loads((fixture_dir/'anemi_recordings.json').read_text())
    assert all(hashlib.sha256((fixture_dir/name).read_bytes()).hexdigest()==p['fixture_sha256']
               for name,p in recordings.items())
    validation=json.loads((EVIDENCE/'anemi_inventory_validation.json').read_text())
    assert len(validation)>=3 and all(x['download_url_match'] and x['pages_match'] and x['size_match'] for x in validation)
    candidates=read_rows(EVIDENCE/'candidates.jsonl')
    before=json.loads((EVIDENCE/'anemi_prior_ranking.json').read_text())
    assert hashlib.sha256((EVIDENCE/'anemi_prior_candidates.jsonl').read_bytes()).hexdigest()==before['file_sha256']
    signature=hashlib.sha256(json.dumps([(r['candidate_id'],r['rank'],r['estimated_target_lines'],
        r['rights']['identifier']) for r in candidates],ensure_ascii=False).encode()).hexdigest()
    assert len(candidates)==before['documents'] and signature==before['ranking_signature']
    assert not any(r['source']=='anemi' for r in candidates)
    report=json.loads((EVIDENCE/'summary.json').read_text())
    assert report['measurement_replay']=='retained-source-measurements'
    assert report['prior_candidate_measurements_sha256']==before['file_sha256']
    merged={r['document_id']:r for r in read_rows(EVIDENCE/'discovery_merged.jsonl') if r['source']=='anemi'}
    assert set(merged)=={r['document_id'] for r in rows}
    for r in rows:
        for field in ('title','year','pages','size','download_url','text_layer','author'):
            assert r.get(field)==merged[r['document_id']].get(field)
    summary=report['anemi_authenticated_discovery']
    assert summary['documents']==len(scoped) and summary['sampled_documents']==len(sampled)
    assert summary['pdf_with_layer']==sum(r['text_layer']['status']=='verified' for r in scoped)
    # Scan only relevant artifacts. Output is boolean; actual values never escape.
    patterns=[]
    for key in ('ANEMI_USER','ANEMI_PASS'):
        value=os.environ.get(key,'')
        if value:patterns.extend(s.encode() for s in {value,urllib.parse.quote(value,safe=''),
            urllib.parse.quote_plus(value,safe=''),html.escape(value),
            json.dumps(value,ensure_ascii=False)[1:-1],json.dumps(value,ensure_ascii=True)[1:-1]})
    paths=set(EVIDENCE.glob('anemi*'))|set(fixture_dir.glob('anemi*'))|{
        EVIDENCE/'transfer.jsonl',EVIDENCE/'discovery_merged.jsonl',EVIDENCE/'candidates.jsonl',
        EVIDENCE/'summary.json',EVIDENCE/'summary.md',ROOT/'docs/ocr_program_2026-10-06/O4c_NOTES.md',
        ROOT/'scripts/fetch/o4c_discover_anemi.py',ROOT/'scripts/fetch/o4c_finalize.py',
        ROOT/'scripts/fetch/o4c_audit_anemi.py',ROOT/'bench/tests/test_o4c_anemi.py',ROOT/'O4c_anemi_HANDOFF.json'}
    scanned=0
    for path in paths:
        if path.is_file():
            data=path.read_bytes();scanned+=1
            assert not any(p in data for p in patterns), 'private account data excluded from evidence'
    result={'schema_version':'o4c-anemi-audit-1',
        'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,
        'documents':len(scoped),'retained_records':len(rows),
        'query_bound_records':sum(bool(r.get('catalogue_queries')) for r in rows),
        'polytonic_docs':sum(r.get('polytonic_document',False) for r in scoped),
        'pdf_with_layer':sum(r['text_layer']['status']=='verified' for r in scoped),
        'PDF_documents':sum(bool(r.get('download_url')) for r in scoped),
        'PDF_files':sum(len(r.get('scan_files',[])) for r in scoped),
        'sampled_documents':len(sampled),'sampled_original_pages':sum(r['text_layer']['sample_pages'] for r in sampled),
        'text_layer_statuses':dict(Counter(r['text_layer']['status'] for r in scoped)),
        'catalogue_streams':len(state['streams']),'media_inventory_pages':len(nonempty),
        'cumulative_payload_bytes':payload,'authenticated_payload_bytes':sum(x['bytes'] for x in authenticated),
        'authenticated_receipts':len(authenticated),'timed_requests':sum(len(v) for v in starts.values()),
        'minimum_observed_start_spacing_seconds':min(gaps),'maximum_distinct_pages_per_PDF':max(map(len,page_sets.values())),
        'prohibited_paths_queried':False,'original_PDF_downloads_submitted':False,
        'account_secrets_present_for_boolean_scan':bool(patterns),'credential_material_persisted':False,
        'cookie_headers_persisted':False,'privacy_scanned_files':scanned,
        'offline_fixtures_bound':len(recordings),'individual_inventory_validations':len(validation),
        'compatible_candidates':len(candidates),'candidate_ranking_unchanged':True,'ranking_signature':signature}
    write_json(EVIDENCE/'anemi_audit.json',result)
    print(json.dumps({k:result[k] for k in ('passed','documents','polytonic_docs','pdf_with_layer',
        'sampled_documents','cumulative_payload_bytes','candidate_ranking_unchanged')}))


if __name__=='__main__':main()
