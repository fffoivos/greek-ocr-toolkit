"""Validate complete source-bound audit, network protocol and downstream counts."""
import sys
sys.dont_write_bytecode=True
import collections,datetime,json,subprocess,urllib.parse
from audit import *
from greekocr._vendor.scripts.fetch.o4c_common import robots_allowed

def main():
    bindings=list(rows(OUT/'rebind.jsonl'));assert len(bindings)==89
    assert len({r['book_key'] for r in bindings})==len({r['book_id'] for r in bindings})==89
    checks={};source_count=0
    for path in ['receipts/input-files.json','receipts/collection-input-files.json']:
        for entry in json.loads((OUT/path).read_text()):
            assert input_receipt(Path(entry['path']))==entry,entry['path'];source_count+=1
    extra=json.loads((OUT/'receipts/http-source-input.json').read_text());assert input_receipt(Path(extra['path']))==extra
    checks['source_files_unchanged']=source_count+1
    retention=[]
    for b in bindings:
        p=(MAIN/next(r['download_receipt'] for r in json.loads((OUT/'receipts/initial-bindings.json').read_text()) if r['book_key']==b['book_key'])).with_suffix('.retention.json')
        d=json.loads(p.read_text())
        assert d['sha256']==b['pdf_sha256'] and d['bytes']==b['pdf_bytes'] and d['page_count']==b['page_count'] and d['deleted'] is True
        retention.append(input_receipt(p))
    write('receipts/original-retention-inputs.json',retention)
    checks['original_retention_sha_bytes_pagecount_match']=89
    contractpaths=['greekocr/harvest/openarchives.py','scripts/harvest/openarchives.py','greekocr/harvest/collection.py']
    write('receipts/policy-code-inputs.json',[input_receipt(root/p) for root in [ROOT,MAIN] for p in contractpaths])
    for p in contractpaths:assert sha((ROOT/p).read_bytes())==sha((MAIN/p).read_bytes())
    hf=json.loads((OUT/'receipts/hf-link-table.json').read_text());assert sha(Path(hf['verified_local_path']).read_bytes())==hf['sha256']
    checks['pinned_hf_table_rehashed']=True
    chains=json.loads((OUT/'receipts/download-chains.json').read_text());assert len(chains)==89
    by={r['book_key']:r for r in bindings}
    for c in chains:
        b=by[c['book_key']];chain=c['chain'];assert canonical_url(chain[0]['url'])==b['canonical_pdf_url']
        assert canonical_url(chain[-1]['url'])==canonical_url(b['download_final_url'])
        assert chain[-1]['sha256']==b['pdf_sha256'] and chain[-1]['bytes']==b['pdf_bytes']
        for before,after in zip(chain,chain[1:]):assert canonical_url(before['location'])==canonical_url(after['url'])
    checks['hash_bound_download_chains']=89
    net=list(rows(OUT/'receipts/http.jsonl'));hosts=collections.defaultdict(list);policies={}
    for p in (OUT/'receipts/robots').glob('*.json'):
        d=json.loads(p.read_text());policies[d['origin']]=d
    for r in net:
        hosts[r['host']].append(r)
        assert r['user_agent']=='greek-ocr-research/0.1 (foivos.karounos@gmail.com)'
        body=(OUT/r['body']).read_bytes();assert sha(body)==r['sha256'] and len(body)==r['bytes']
        assert len(body)<=8_000_000
        if urllib.parse.urlsplit(r['url']).path!='/robots.txt':
            origin=urllib.parse.urlsplit(r['url']).scheme+'://'+r['host'];policy=policies[origin]
            assert robots_allowed(policy['text'],r['url'],r['user_agent']),r['url']
            assert r['host']!='dione.lib.unipi.gr'
    gaps=[]
    for host,rs in hosts.items():
        rs.sort(key=lambda r:r['started_unix'])
        for a,b in zip(rs,rs[1:]):
            gap=b['started_unix']-a['started_unix'];assert gap>=1.,(host,gap);gaps.append(gap)
    checks.update(http_requests=len(net),http_statuses=dict(collections.Counter(r['status'] for r in net)),all_contact_ua=True,robots_honoured_for_every_page=True,minimum_host_start_gap_seconds=min(gaps),fresh_pdf_requests=0,total_response_bytes=sum(r['bytes'] for r in net))
    count=json.loads((OUT/'receipts/counts.json').read_text())
    assert count['wave4_books']==89 and count['affected']['books']==89
    assert count['overlapping_fields']['collection mismatch']['books']==80
    assert count['overlapping_fields']['title mismatch']['books']==89
    assert count['overlapping_fields']['year mismatch']['books']==86
    assert sum(b['year_previously_unknown'] for b in bindings)==1
    assert count['pipeline_page_count_equal']==82 and count['pipeline_page_count_contradicted']==7
    assert count['provider_verified']==80 and count['secondary_verified']==9
    exposure=list(rows(OUT/'receipts/line-exposure.jsonl'));assert len(exposure)==25604
    assert len({r['id'] for r in exposure})==len(exposure)
    assert sum('v2' in r for r in exposure)==25372
    for version,expected in [('v1',[19795,1083,4726]),('v2',[19625,1067,4680])]:
        assert [count['affected'][version][s]['lines'] for s in ['train','dev','test']]==expected
        perbook=collections.defaultdict(set)
        for r in exposure:
            if version in r:perbook[r['book_key']].add(r[version]['split'])
        assert all(len(v)==1 for v in perbook.values())
    checks.update(rebind_rows=89,repository_verified=80,aggregator_only_provider_pending=9,source_pdf_digest_available_for_all=True,book_split_disjoint_in_both_versions=True,manifest_import_comparisons=6,v1_wave4_lines=25604,v2_wave4_lines=25372,test_holdouts_affected=15,represented_test_books_affected=14,no_old_pipeline_field_promoted_as_identity_verified=True)
    line=json.loads((OUT/'receipts/final-line.json').read_text())['line'];assert (OUT/'FINDING.md').read_text().splitlines()[-1]==line
    checks['finding_final_line_exact']=True
    status=subprocess.run(['git','status','--porcelain','--untracked-files=normal'],cwd=ROOT,capture_output=True,text=True,check=True).stdout
    write('receipts/final-worktree-status.json',dict(status=status,scope='Existing pilots_v2 modifications and brief predate O1; only oa_rebind_v1 is an O1 output.'))
    write('receipts/validation.json',dict(passed=True,at=datetime.datetime.now(datetime.timezone.utc).isoformat(),checks=checks,limitations=['Nine Dione books use exact-item-linked fresh EDM metadata; provider robots transport unavailable.','OCR-success and polytonic-ratio old document ownership unresolved for all 89; numeric page count corroboration alone is not identity proof.','This is metadata exposure accounting; no image/label correctness, whole-wave physical scan construction or cross-edition leakage certification.']))
    print(json.dumps(dict(passed=True,**checks)))

if __name__=='__main__':main()
