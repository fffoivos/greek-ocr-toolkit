"""Offline T24b feasibility evidence. No fallback changes the approved join."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import shutil
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

import pyarrow.parquet as pq

from greekocr.harvest import admission
from greekocr.harvest.openarchives import (LinkIndex, base_filters, build_pool, canonical_url,
    metadata, stratified_draw, urls)
from greekocr.harvest.readers import atomic, read_jsonl
from scripts.harvest.openarchives import REPO, OUT, BULK, ADMISSION_SHA, sha, relative, check, git_snapshot


def identity_audit(parquet,jsonl):
    """Exact URL-only matches are diagnostic evidence, never admitted joins."""
    index=LinkIndex(pq.read_table(parquet).to_pylist())
    by_url=defaultdict(list)
    for i,row in enumerate(index.rows):
        for url in urls(row.get('pdf_links_json')):
            by_url[canonical_url(url)].append(i)
    counts=Counter();repos=defaultdict(Counter);examples=[]
    for number,line in enumerate(open(jsonl),1):
        row=json.loads(line);src=row.get('source_metadata',{});pipe=row.get('pipeline_metadata',{})
        if not all(passed for _,passed in base_filters(pipe)):continue
        counts['before_join']+=1;repo=src.get('collection_slug','unknown');repos[repo]['before_join']+=1
        meta=metadata(src.get('metadata_json'))
        edm_fields=[value for obj in (row,src,pipe,meta) for key,value in obj.items()
            if 'edm' in key.lower() and isinstance(value,str) and value.startswith(('http://','https://'))]
        counts['explicit_edm_fields']+=len(edm_fields)
        matches,method=index.join(row)
        if matches:
            status=index.rows[matches[0]].get('status_code')
            repos[repo]['joined_status_'+str(status)]+=1
            counts['joined']+=1
            continue
        counts['unmatched']+=1;repos[repo]['unmatched']+=1
        global_matches=set()
        for url in urls(src.get('pdf_links_json')):global_matches.update(by_url.get(canonical_url(url),[]))
        others=sorted({index.rows[i]['collection_slug'] for i in global_matches})
        if others:
            counts['unmatched_url_exists_in_other_collection']+=1
            repos[repo]['unmatched_url_exists_in_other_collection']+=1
        if others and (len(examples)<25 and not any(e['metadata_collection_slug']==repo for e in examples)):
            examples.append(dict(metadata_row=number,metadata_collection_slug=repo,filename=src.get('filename'),
                pdf_urls=urls(src.get('pdf_links_json')),matching_external_collections=others,
                explicit_edm_fields=edm_fields,external_matches=[{k:index.rows[i].get(k) for k in
                    ('collection_slug','edm_url','external_link','status_code')} for i in sorted(global_matches)[:3]]))
    return dict(schema='t24b-identity-audit-1',counts=dict(counts),per_repository={k:dict(v) for k,v in sorted(repos.items())},
        examples=examples,policy='URL-only matches are diagnostics. They do not repair metadata or qualify a document. '
        'Approved joins remain (collection_slug, exact canonical PDF URL) or explicit edm_url.',
        inference='These are source-metadata/table identity inconsistencies; the affected row fields cannot be safely relinked by assuming only the collection slug is wrong.')


def validate():
    check()
    pre=json.loads((OUT/'preflight.json').read_text())
    for name,receipt in pre['inputs'].items():
        assert (REPO/name).stat().st_size==receipt['bytes'] and sha(REPO/name)==receipt['sha256']
    pool,wave5,summary=build_pool(BULK/'external_pdfs.parquet',BULK/'doc_metadata.jsonl')
    actual=json.loads((OUT/'pool_summary.json').read_text())
    assert all(actual[k]==v for k,v in summary.items())
    assert pool==json.loads((OUT/'candidates.json').read_text())
    assert wave5==json.loads((OUT/'wave5_candidates.json').read_text())
    draw=stratified_draw(pool)
    assert draw==json.loads((OUT/'selection.json').read_text())
    assert len(draw)<130 and pre['status']=='blocked' and pre['null_scores_waived']
    assert pre['blockers']==[dict(code='repository_capacity_shortfall',detail='Cannot select 130 at <=10 documents per repository.')]
    assert max(Counter(b['collection_slug'] for b in draw).values(),default=0)<=10
    for name in ('records.jsonl','admitted.jsonl','rejected.jsonl'):
        assert (OUT/name).read_bytes()==b''
    for name in ('books.json','manifest.json','holdout_books.json'):
        assert json.loads((OUT/name).read_text())==[]
    assert (BULK/'google/budget.jsonl').read_bytes()==b''
    assert json.loads((BULK/'google/budget.state.json').read_text())=={'calls':0}
    assert not (BULK/'google/vision').exists() and not (BULK/'google/docai').exists()
    assert not list((BULK/'crops').rglob('*.png'))
    assert not list((BULK/'pdf').glob('*'))
    audit=identity_audit(BULK/'external_pdfs.parquet',BULK/'doc_metadata.jsonl')
    atomic(OUT/'identity_audit.json',audit)
    result=dict(schema='t24b-preflight-validation-1',passed=True,status='blocked_before_acquisition',
        scope='full-input join, corrected filters, stratified draw, identity diagnostic, zero-execution artifacts',
        metadata_rows=summary['counts']['metadata_rows'],joined_metadata_rows=summary['counts']['joined_metadata_rows'],
        corrected_pool_size=len(pool),repositories=len(summary['pool_per_repository']),capped_capacity=len(draw),
        inputs_hash_verified=True,full_join_replayed=True,selection_replayed=True,admission_unchanged=True,
        documents_tried=0,pages_rendered=0,pages_accepted=0,pages_read=0,crops=0,google_calls=0,vision_calls=0,cost_usd=0,
        no_network_calls=True,holdout_status='not_assigned; cannot fulfill 20 of 130 without the required source pool')
    atomic(OUT/'validation.json',result)
    return result


def publish():
    check()
    pre=json.loads((OUT/'preflight.json').read_text());pool=json.loads((OUT/'pool_summary.json').read_text())
    validation=json.loads((OUT/'validation.json').read_text());identity=json.loads((OUT/'identity_audit.json').read_text())
    assert validation['passed'] and validation['status']=='blocked_before_acquisition'
    suites=list(ET.parse(OUT/'tests.xml').getroot().iter('testsuite'))
    tests=sum(int(s.get('tests',0)) for s in suites)
    assert tests and not any(int(s.get(k,0)) for s in suites for k in ('failures','errors','skipped'))
    before=json.loads((OUT/'git_before_t24b.json').read_text());after=git_snapshot()
    audit=dict(schema='t24b-git-audit-1',unchanged=before==after,before=before,after=after,git_write_operations=0,
        note='T24b issues no Git commands or writes; equality checks tracked bookkeeping files only.')
    atomic(OUT/'git_audit.json',audit)
    cost=dict(calls_reserved=0,calls_by_engine={'docai':0,'vision':0},cost_usd=0,cap_usd=3,
        price_per_page_usd=.0015,ledger=relative(BULK/'google/budget.jsonl'),policy='No ADC or provider calls. Empty ledger; not invoice readback.')
    atomic(OUT/'cost_receipt.json',cost)
    summary=dict(schema='t24b-admission-1',status='not_run',blocked_by='repository_capacity_shortfall',
        input_lines=0,admitted=0,rejected=0,crops=0,documents_tried=0,documents_downloaded=0,dead_links=0,skipped_size=0,
        pages_rendered=0,pages_accepted=0,pages_read=0,per_class={c:0 for c in admission.CLASSES},
        per_split={s:0 for s in ('train','dev','test')},
        per_class_split={c:{s:0 for s in ('train','dev','test')} for c in admission.CLASSES},
        per_class_split_repository={c:{s:{repo:0 for repo in pool['pool_per_repository']} for s in ('train','dev','test')} for c in admission.CLASSES},
        per_reason={r:0 for r in admission.REASONS},holdout_policy=dict(status='not_assigned',target_books=20,target_test=15,target_dev=5,seed=20261015),
        admission_module_sha256=ADMISSION_SHA)
    atomic(OUT/'admission_summary.json',summary)
    c=pool['counts'];draw=json.loads((OUT/'selection.json').read_text())
    table=['| Sequential filter | Documents / rows remaining |','| --- | ---: |']
    for key,label in [('metadata_rows','All metadata rows'),('ocr_success','ocr_success is true'),('filter_ok','filter == ok'),
        ('is_empty_false','is_empty is false'),('percentage_greek_ge80','percentage_greek >= 80'),
        ('mojibake_zero','Mojibake zero OR null (T24b)'),('pages_20_600','Page count 20–600'),
        ('finite_greek_badness','Greek badness finite OR null (T24b)'),('external_status_200','Joined external row has status 200'),
        ('unique_pre_median_documents','Distinct PDF documents before median'),('greek_badness_le_median','Measured Greek badness <= median OR null')]:
        table.append(f'| {label} | {c[key]:,} |')
    repo_table=['| Repository | Eligible documents | Maximum at cap 10 |','| --- | ---: | ---: |']
    repo_table += [f'| {repo} | {n:,} | {min(n,10)} |' for repo,n in sorted(pool['pool_per_repository'].items())]
    terminal=f'T24b: blocked | docs: 0/0 | pages: 0/0/0 | lines: 0 | admitted: 0 | mono: 0 | cs: 0 | train: 0 | dev: 0 | test: 0 | usd: 0.00 | tests: {tests} passed'
    selection=['# T24b — Wave 4 selection feasibility','',
        f'**Blocked before acquisition:** {len(draw)} available under the repository cap; required 130 successful downloads from an overdraw of 173.','',
        'Seed 20264. Existing T24 repository round-robin and least-used type × decade strata, seeded ties; '
        'cap 10 per collection_slug across the full overdraw. No cap, join, date, quality, or status rule was relaxed. '
        'The rows below are a diagnostic draw, not selected/downloaded documents.','',*repo_table,'',
        '| Order | Repository | Type | Year | Title | Direct PDF | Outcome |',
        '| ---: | --- | --- | ---: | --- | --- | --- |']
    for i,b in enumerate(draw,1):
        title=' '.join(b['title'].split()).replace('|','\\|')
        selection.append(f"| {i} | {b['collection_slug']} | {b['type']} | {b['year']} | {title} | [PDF]({b['pdf_url']}) | not attempted |")
    selection += ['', 'No hold-out assigned. A 20-document acquisition would place every document in hold-out and cannot implement the requested 130-document design.',
        '', '[Pool filters](pool_summary.json), [join identity evidence](identity_audit.json), [report](READS.md).']
    (OUT/'SELECTION.md').write_text('\n'.join(selection)+'\n')
    report=['# T24b — Open Archives Wave 4 rerun','',
        f"**Blocked before downloads; harvest not complete.** The null-score fix yields {pre['pool_size']:,} eligible documents, "
        f"all in {len(pool['pool_per_repository'])} repositories. The <=10-per-repository rule permits only {len(draw)} documents, "
        'so neither the 173-candidate overdraw nor the 130-document sample is feasible. No PDF/network/ADC requests or paid reads were made.','',
        'The 15 October coordinator correction is applied without replacing nulls by zero: null mojibake passes; '
        'null Greek badness passes and is excluded from the median. Non-null mojibake must equal zero; measured Greek badness must not exceed '
        f"the median **{pool['median_greek_badness']}**, computed over {pool['measured_greek_badness_documents']:,} distinct documents after all other filters, including the joined 200 status. "
        'T20 admission remains byte-identical.','',
        f"Final inputs: {c['metadata_rows']:,} metadata rows; {pool['external_rows']:,} external-PDF rows; "
        f"{pool['catalogue_inputs']['all_links_rows']:,} all-links rows; {pool['catalogue_inputs']['collections']} collections. "
        'No partial metadata file exists. All four input SHA-256 values were checked before/after preparation and in independent validation.','',
        f"Join coverage: **{c['joined_metadata_rows']:,}/{c['metadata_rows']:,} ({pool['join_coverage']:.2%})** overall; "
        f"**{c['joined_scanned_rows']:,}/{c['scanned_metadata_rows']:,} ({pool['scanned_join_coverage']:.2%})** scanned. "
        f"{pool['external_rows_joined']:,} distinct external rows matched; {c['multiple_external_matches']} metadata rows had multiple matches. "
        'Matches use (collection_slug, canonical full PDF URL); explicit edm_url fallback added no matches. '
        'Queries and reserved escapes retain identity; no filename, host, title or cross-collection fallback was used.','',*table,'',*repo_table,'',
        f"Year coverage: {pool['pool_with_year']:,}/{pre['pool_size']:,} ({pool['pool_year_share']:.2%}). "
        'Years come only from metadata date fields, preferring publication chronology over accession dates. '
        'No title/creator-year inference or extra chronology/character threshold was introduced.','',
        f"The expected approximately 6,000 pool is approached **before** the required join: {identity['counts']['before_join']:,} "
        f"documents pass quality/page filters, but {identity['counts']['unmatched']:,} cannot join. "
        f"For {identity['counts'].get('unmatched_url_exists_in_other_collection',0):,} of those, the exact PDF URL exists in external_pdfs under a different collection_slug. "
        'These are input identity inconsistencies; assuming only the slug is wrong would attach unverified metadata, years, quality scores and repository labels to PDFs. '
        f"There are {identity['counts']['explicit_edm_fields']} explicit EDM fields in this pre-join population. "
        'Examples and counts per repository are in [identity_audit.json](identity_audit.json).','',
        f"Wave 5: {pool['wave5_count']:,} scanned latin_percentage 20–50 records remain in [wave5_candidates.json](wave5_candidates.json), "
        'with original metadata and join/status flags. Their bytes are unchanged from the T24 file consumed by T25. '
        'That retention does not certify upstream PDF/metadata identity.','',
        '| Execution metric | Count |','| --- | ---: |',
        '| Documents tried / downloaded / dead-link / skipped-size | 0 / 0 / 0 / 0 |',
        '| Pages rendered / accepted / read | 0 / 0 / 0 |','| Lines / admitted / rejected / crops | 0 / 0 / 0 / 0 |',
        '| Train / dev / test | 0 / 0 / 0 |','| Google reservations / USD | 0 / 0.00 |','',
        'The admission summary is explicitly `not_run`, with zero class × split × repository counts. '
        'No hold-out, compiled pages, crops or contact sheets were fabricated. All existing hold-outs remain unchanged. '
        'The USD 3.00 ledger and state have no reservations; zero Vision calls.','',
        f"Disk: {shutil.disk_usage(REPO).free/2**30:.2f} GiB free at publication. There are no PDFs, rendered images or raw responses for this wave. "
        'The required 3,500-pixel cap, scale/native-size receipt, PNG compression 6, pre-save response image stripping, '
        'one-PDF lifetime and <4 GB graceful abort remain execution requirements; they have not been exercised. '
        'No acquisition/read runner is claimed as complete.','',
        f"**{tests} offline tests passed**, covering the reused join, corrected null/finite filters, measured-only median, deterministic "
        'type/decade/repository stratification, repository-cap infeasibility, 20-document 15/5 hold-out, cross-collection mismatch diagnostics and unchanged T20 admission. '
        'Full-input offline validation independently recomputed the join/pool/draw and verified empty execution artifacts. '
        f"Git bookkeeping unchanged during T24b: **{audit['unchanged']}**; no Git commands or writes issued. Native-image/crop verification is not applicable. "
        'The original T24 report and receipts are retained under [t24_preflight/](t24_preflight/READS.md).','',
        '**Required to continue:** corrected metadata-to-PDF identities or an explicit document-to-EDM mapping that supplies enough qualifying repositories. '
        'A cross-collection URL fallback or higher per-collection cap would change the brief and has not been applied.','',
        '[Selection](SELECTION.md), [pool](pool_summary.json), [preflight](preflight.json), [identity audit](identity_audit.json), '
        '[validation](validation.json), [tests](tests.xml), [cost](cost_receipt.json), [Git audit](git_audit.json), [inventory](inventory.json).','',terminal]
    (OUT/'READS.md').write_text('\n'.join(report)+'\n')
    state_path=REPO/'docs/harvest/collection/EXECUTION_STATE.md';state=state_path.read_text()
    now=datetime.now(ZoneInfo('Europe/Athens')).strftime('%Y-%m-%d %H:%M')
    old=next(line for line in state.splitlines() if line.startswith('| 4 Open Archives |'))
    state=state.replace(old,f'| 4 Open Archives | T24b | blocked (repository capacity 20/130) | {now} | | 0 / 0 / 0 | 0 | 0 |')
    section=f'''## Wave 4

T24b preflight {now} Athens: **blocked before acquisition, not complete**. Coordinator null-score fix applied unchanged; {pre['pool_size']:,} candidates remain in only two repositories (IKEE_AUT {pool['pool_per_repository']['IKEE_AUT']}, Dione {pool['pool_per_repository']['Dione']}). At <=10 per collection_slug, capacity is 20/130 documents; the 173 overdraw is impossible. No repository/ADC calls, downloads, renders, reads, admissions, hold-outs or crops; USD 0.00 of USD 3.00.

{identity['counts']['before_join']:,} rows pass quality/page filters before joining; {identity['counts']['unmatched']:,} cannot join. Exact URLs for {identity['counts'].get('unmatched_url_exists_in_other_collection',0):,} unmatched rows occur under a different external-table collection_slug. Corrected input identities or explicit EDM mapping are required. Join coverage {pool['join_coverage']:.2%} overall / {pool['scanned_join_coverage']:.2%} scanned. No join/cap relaxation. {pool['wave5_count']:,} Wave 5 records retained byte-identically. {tests} offline tests passed; full-input replay passed; T20 unchanged; no Git writes.

[Report](../openarchives/READS.md), [selection](../openarchives/SELECTION.md), [identity audit](../openarchives/identity_audit.json), [pool](../openarchives/pool_summary.json), [validation](../openarchives/validation.json), [inventory](../openarchives/inventory.json).

{terminal}
'''
    start,rest=state.split('\n## Wave 4\n',1);pos=rest.find('\n## ')
    state_path.write_text(start.rstrip()+'\n\n'+section+(rest[pos:] if pos>=0 else ''))
    inventory_path=REPO/'docs/INVENTORY.md';text=inventory_path.read_text()
    entry=f'''<!-- T24:begin -->
## T24b — Open Archives Wave 4 corrected preflight (15 October 2026)

**Blocked, not complete:** the corrected null-score policy yields {pre['pool_size']:,} candidates in two repositories, capacity 20/130 at <=10 per repository. Exact-URL/collection identity inconsistencies block other repositories. No network, ADC calls, downloads or paid reads; USD 0.00. {pool['wave5_count']:,} Wave 5 records retained unchanged; {tests} offline tests passed; T20 unchanged.

Entrypoints: `python -m scripts.harvest.openarchives prepare|validate|publish` (offline feasibility only). Reused policy: [openarchives.py](../greekocr/harvest/openarchives.py); [evidence publisher](../scripts/harvest/openarchives_preflight.py); [fixtures/tests](../tests/test_openarchives.py).

[Report](harvest/openarchives/READS.md), [selection](harvest/openarchives/SELECTION.md), [pool](harvest/openarchives/pool_summary.json), [identity evidence](harvest/openarchives/identity_audit.json), [validation](harvest/openarchives/validation.json), [tests](harvest/openarchives/tests.xml), [file/hash inventory](harvest/openarchives/inventory.json). Required crops/compiled pages/sheets are not generated because the requested sample cannot be selected. Original T24 evidence is archived under `openarchives/t24_preflight/`.
<!-- T24:end -->'''
    start,rest=text.split('<!-- T24:begin -->',1);_,tail=rest.split('<!-- T24:end -->',1)
    inventory_path.write_text(start+entry+tail)
    paths={p for root in (OUT,BULK) for p in root.rglob('*') if p.is_file() and p!=OUT/'inventory.json'}
    paths.update([REPO/'greekocr/harvest/openarchives.py',REPO/'scripts/harvest/openarchives.py',REPO/'scripts/harvest/openarchives_preflight.py',
        REPO/'tests/test_openarchives.py',REPO/'tests/test_openarchives_preflight.py',REPO/'greekocr/harvest/admission.py',
        REPO/'tests/test_harvest_admission.py',state_path,inventory_path,REPO/'docs/briefs/T24b_openarchives_modern.md',
        REPO/'docs/harvest/COLLECTION_PLAN_v1.md'])
    atomic(OUT/'inventory.json',dict(schema='t24b-inventory-1',status='blocked_before_acquisition',excluded_self=relative(OUT/'inventory.json'),
        files=[dict(path=relative(p),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(paths)],file_count=len(paths)))
    print(terminal,flush=True)
