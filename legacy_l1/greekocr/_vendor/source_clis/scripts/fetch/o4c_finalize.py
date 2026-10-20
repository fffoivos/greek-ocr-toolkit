#!/usr/bin/env python3
"""Offline merge, byte/hash audit, conservative qualification, ranking and summary."""
from collections import Counter
from o4c_common import *
from o4c_discover_archive import parse_item
from o4c_discover_anemi import ANEMI_BUDGET
INPUTS=['parliament_catalogue.jsonl','parliament.jsonl','anemi.jsonl','archive.jsonl','archive_licensed.jsonl','archive_modern_greek.jsonl','wikimedia.jsonl','other.jsonl']

def accounting_source(receipt):
    """Assign early recon/redirect bytes to the library whose interface was probed."""
    if receipt.get('kind')=='preflight-reserve':return 'preflight-reserve'
    host=urllib.parse.urlsplit(receipt.get('url') or '').hostname or ''
    if host in ('digitallibrary.parliament.gr','sylloges.parliament.gr'):return 'parliament'
    if host=='archive.org' or host.endswith('.archive.org'):return 'archive'
    if host=='anemi.lib.uoc.gr':return 'anemi'
    if host.endswith('.wikimedia.org') or host.endswith('.wikisource.org'):return 'wikimedia'
    if receipt['source'] in ('parliament','anemi','archive','wikimedia','other'):return receipt['source']
    if host in ('gallica.bnf.fr','pergamos.lib.uoa.gr','digitalcollections.nlg.gr','api.wellcomecollection.org'):return 'other'
    return 'unattributed'

def qualify(r):
    return bool(r.get('download_url') and r['rights']['compatible'] and r['text_layer']['status']=='verified' and r['text_layer'].get('scan_status') in ('verified-large-raster-object','source-declared')
      and (r.get('polytonic_document') or r.get('cyrillic_document')) and not r.get('existing_s17')
      and r.get('print_review',{}).get('status') not in ('unverified-conflict','non-target-sample','unverified-scan-origin')
      and (r['source']!='archive' or (r.get('print_review',{}).get('status')=='verified-target-sample'
        and r.get('media_probe',{}).get('status')=='verified-file-prefix'
        and r['media_probe'].get('probe_url')==r['download_url'])))

def mark_baseline(r,baseline_rows):
    """Exclude the original S17 scans even if another catalogue record aliases them."""
    selected=next((f for f in r.get('scan_files',[]) if f.get('url')==r.get('download_url')), {})
    checksum=selected.get('checksum') or {}
    if checksum.get('checkSumAlgorithm','').upper()=='MD5':r['scan_md5']=checksum.get('value','').lower()
    ids={x['item_id'] for x in baseline_rows};md5s={x.get('content_md5','').lower() for x in baseline_rows}-{''}
    r['existing_s17']=r['document_id'] in ids or bool(r.get('scan_md5') and r['scan_md5'] in md5s)
    r['baseline_match_basis']='record-id' if r['document_id'] in ids else ('scan-MD5' if r['existing_s17'] else None)

def main(retain_source_measurements=False,prior_candidates=None):
    prior_path=pathlib.Path(prior_candidates or EVIDENCE/'candidates.jsonl')
    prior_hash=hashlib.sha256(prior_path.read_bytes()).hexdigest() if retain_source_measurements else None
    prior={(r['source'],r['document_id']):r for r in read_rows(prior_path)} if retain_source_measurements else {}
    recordings={};by_url={}
    for p in (EVIDENCE/'http').glob('*.json'):
        m=json.loads(p.read_text());body=p.with_suffix('.body')
        if m['status'] in (200,206) and not m.get('truncated'):
            recordings.setdefault(m['sha256'],(m,body));by_url[m['url']]=(m,body)
    rows={};baseline=read_rows(ROOT/'docs/evidence/s17/pdf_cache_refetch.jsonl')
    reviews={(r['source'],r['document_id']):r for r in read_rows(EVIDENCE/'print_reviews.jsonl')}
    media={(r['source'],r['document_id']):r for r in read_rows(EVIDENCE/'media_probes.jsonl')}
    for filename in INPUTS:
        for r in read_rows(EVIDENCE/filename):
            key=(r['source'],r['document_id']);old=rows.get(key)
            quality=lambda x:(x['text_layer']['status']=='verified',bool(x.get('download_url')),x.get('media_status')!='unverified')
            if old is None or quality(r)>quality(old):rows[key]=r
    # Recompute complete-text statistics with the final, tested definition, using bound bytes only.
    for r in rows.values():
        r['rights']=license_info(r['rights']['raw'])
        if r['source']=='parliament':mark_baseline(r,baseline)
        r['print_review']=reviews.get((r['source'],r['document_id']),{'status':'unverified','scope':'printed script not visually adjudicated'})
        r['media_probe']=media.get((r['source'],r['document_id']),{'status':'unverified'})
        if r['source']=='archive':
            # Retained, hash-bound measurements can outlive their optional raw cache.
            # A media receipt still supplies the access status for such rows.
            r.setdefault('media_access','verified-file-prefix' if r['media_probe']['status']=='verified-file-prefix'
                else 'unverified; source-declared scan URL')
            meta=by_url.get(r.get('metadata_url'))
            if meta:
                raw=meta[1].read_bytes()
                if hashlib.sha256(raw).hexdigest()!=meta[0]['sha256']:raise ProbeError('metadata hash mismatch')
                parsed=parse_item(r['document_id'],json.loads(raw))
                for k in ('scan_files','download_url','size','rights','language','creator','year','pages'):r[k]=parsed[k]
                # Underlying format/sidecars are source declarations; embedded PDF text is not inferred from TXT.
                r['media_access']='verified-file-prefix' if r['media_probe']['status']=='verified-file-prefix' else 'unverified; source-declared scan URL'
                if r.get('scan_files'):
                    md=json.loads(raw).get('files',[])
                    chosen=next((f for f in md if f['name']==r['scan_files'][0]['name']),{})
                    r['scan_md5']=chosen.get('md5')
            tl=r['text_layer'];binding=recordings.get(tl.get('probe_sha256'))
            # Interrupted page-level saves can be replayed from complete recorded text bytes as well.
            if binding is None and r.get('text_url') and r['rights']['compatible']:
                needle='/'+r['document_id']+'/'+urllib.parse.unquote(r['text_url'].rsplit('/',1)[-1])
                binding=next(((m,p) for m,p in recordings.values() if m['status']==200 and urllib.parse.unquote(urllib.parse.urlsplit(m['url']).path).endswith(needle)),None)
            if binding and r['rights']['compatible'] and not retain_source_measurements:
                m,p=binding;raw=p.read_bytes()
                if hashlib.sha256(raw).hexdigest()!=m['sha256']:raise ProbeError('text hash mismatch')
                apply_text(r,raw.decode('utf-8','replace'),'IA complete _djvu.txt silver OCR',None)
                r['text_layer'].update(probe_url=r['text_url'],resolved_probe_url=m['url'],probe_sha256=m['sha256'],probe_bytes=m['bytes'],scan_status='source-declared',pdf_embedded_text='unverified; separate OCR sidecar measured')
                if r.get('geometry_url'):
                    needle='/'+r['document_id']+'/'+urllib.parse.unquote(r['geometry_url'].rsplit('/',1)[-1])
                    gb=next(((gm,gp) for gm,gp in recordings.values() if gm['status']==206 and urllib.parse.unquote(urllib.parse.urlsplit(gm['url']).path).endswith(needle)),None)
                    if gb:
                        gm,gp=gb;data=gp.read_bytes();r['geometry_status']='verified-word-coordinates-in-prefix' if b'<WORD' in data and b'coords=' in data else 'unverified'
                        r['geometry_sample_sha256']=gm['sha256'];r['geometry_sample_bytes']=len(data)
                    else:r['geometry_status']='source-declared; coordinates unverified'
                r.pop('probe_error',None)
        if retain_source_measurements and r['source']!='anemi' and (r['source'],r['document_id']) in prior:
            original=prior[(r['source'],r['document_id'])]
            if original['download_url']!=r['download_url']:raise ProbeError('prior measurement media identity changed')
            for field in ('text_layer','polytonic_ratio','cyrillic_ratio','estimated_polytonic_lines',
                'estimated_cyrillic_lines','polytonic_document','cyrillic_document'):
                if field in original:r[field]=original[field]
            r['measurement_retention']='prior compatible-candidate manifest; OCR not recalculated'
        if r['print_review']['status'] in ('unverified-conflict','non-target-sample','unverified-scan-origin'):
            r['status']=r['print_review']['status']
    candidates=[];duplicates=[];content={}
    for r in rows.values():
        if not qualify(r):continue
        r['candidate_id']=r['source']+':'+r['document_id'];r['status']='candidate-silver-needs-adjudication'
        r['field_verification']={'year':'source-declared; printed edition unverified','pages':'PDFium count verified' if r['source']=='parliament' else 'API imagecount declared',
          'size':'API-declared','download_url':'sparse byte-range access verified' if r['source']=='parliament' else r['media_access']+'; embedded PDF text unverified',
          'language':'source-declared; OCR script measured; printed sample review in print_review; specific language unverified','rights':'source-declared exact record statement; underlying rights unverified'}
        r['estimated_target_lines']=(r['estimated_polytonic_lines'] or 0)+(r['estimated_cyrillic_lines'] or 0)
        r['estimate_method']='complete OCR sidecar newline census' if r['source']=='archive' else 'one sampled PDF page times PDFium page count'
        r['orthography_scope']='modern Greek parliamentary print' if r['source']=='parliament' else 'unverified; inspect edition and language before admitting lines'
        ident=r.get('scan_md5') or r['download_url']
        if ident in content:
            duplicates.append({'kept':content[ident]['candidate_id'],'duplicate':r['candidate_id'],'basis':'identical scan MD5 or download URL'});continue
        content[ident]=r;candidates.append(r)
    candidates.sort(key=lambda r:(-r['estimated_target_lines'],r['candidate_id']))
    for i,r in enumerate(candidates,1):r['rank']=i
    save_rows(EVIDENCE/'candidates.jsonl',candidates)
    save_rows(EVIDENCE/'discovery_merged.jsonl',rows.values())
    write_json(EVIDENCE/'duplicates.json',duplicates)
    ledger=read_rows(EVIDENCE/'transfer.jsonl');charged=sum(r['bytes'] for r in ledger);assert charged<=BUDGET
    transferred=Counter();assigned=Counter()
    for r in ledger:transferred[r['source']]+=r['bytes'];assigned[accounting_source(r)]+=r['bytes']
    counts={}
    for source in ('parliament','anemi','archive','wikimedia','other'):
        rr=[r for r in rows.values() if r['source']==source];accepted=[r for r in candidates if r['source']==source]
        counts[source]={'records_found':len(rr),'documents_with_media_url':sum(bool(r['download_url']) for r in rr),
          'text_layer_declared_or_measured':sum(r['text_layer']['status'] in ('declared','verified') for r in rr),
          'text_layer_measured':sum(r['text_layer']['status']=='verified' for r in rr),'ranked_documents':len(accepted),
          'polytonic_documents':sum(r.get('polytonic_document',False) for r in accepted),'cyrillic_documents':sum(r.get('cyrillic_document',False) for r in accepted),
          'estimated_polytonic_lines':sum(r['estimated_polytonic_lines'] or 0 for r in accepted),'estimated_cyrillic_lines':sum(r['estimated_cyrillic_lines'] or 0 for r in accepted),
          'licence_breakdown_all_found':dict(Counter(r['rights']['identifier'] for r in rr)),
          'licence_breakdown_ranked':dict(Counter(r['rights']['identifier'] for r in accepted)),
          'print_conflicts_excluded':sum(r['print_review']['status'] in ('unverified-conflict','non-target-sample') for r in rr),
          'scan_origin_unverified_excluded':sum(r['print_review']['status']=='unverified-scan-origin' for r in rr),
          'transfer_payload_bytes':assigned[source]}
    state=json.loads((EVIDENCE/'parliament_catalogue.state.json').read_text()) if (EVIDENCE/'parliament_catalogue.state.json').exists() else {}
    source_states={p.name:json.loads(p.read_text()) for p in EVIDENCE.glob('*.state.json')}
    anemi_state=source_states.get('anemi.state.json',{})
    ar=[r for r in rows.values() if r['source']=='anemi' and r.get('catalogue_queries') and r.get('in_scope')]
    anemi_discovery={
      'documents':sum(r.get('in_scope',False) for r in ar),
      'polytonic_docs':sum(r.get('polytonic_document',False) for r in ar),
      'pdf_with_layer':sum(r['text_layer']['status']=='verified' for r in ar),
      'sampled_documents':sum(bool(r['text_layer'].get('page_indices')) for r in ar),
      'listed_PDF_documents':sum(bool(r.get('download_url')) for r in ar),
      'empty_sample_documents':sum(r['text_layer']['status']=='empty-sample' for r in ar),
      'unprobed_PDF_documents':sum(bool(r.get('download_url')) and not r['text_layer'].get('page_indices') for r in ar),
      'rights_tier':'research-access-only; excluded from compatible ranking',
      'original_PDF_embedded_text':'unverified; source viewer derivatives measured',
      'catalogue_complete':anemi_state.get('catalogue_complete',False),
      'inventory_complete':anemi_state.get('inventory_complete',False),
      'stop_reason':anemi_state.get('stop_reason'),
      'cumulative_transfer_limit_bytes':ANEMI_BUDGET}
    if anemi_state.get('schema_version')=='anemi-crawl-2':assert charged<=ANEMI_BUDGET
    unfiltered=state.get('streams',{}).get('',{})
    catalogue_coverage={'unique_saved_item_records':len({r['document_id'] for r in read_rows(EVIDENCE/'parliament_catalogue.jsonl')}),
      'reported_total_objects':unfiltered.get('num_found'),'end_cursor':unfiltered.get('next_page'),
      'all_pages_traversed':unfiltered.get('complete',False),'snapshot_complete_unique_item_census':'unverified; live equal-title pages overlap',
      'all_PDF_file_bundles_resolved':False}
    reported_total_display=f"{catalogue_coverage['reported_total_objects']:,}" if catalogue_coverage['reported_total_objects'] is not None else 'unverified'
    report={'schema_version':'o4c-summary-1','generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'documents':len(candidates),'polytonic_docs':sum(r.get('polytonic_document',False) for r in candidates),
      'cyrillic_docs':sum(r.get('cyrillic_document',False) for r in candidates),'sources':counts,
      'payload_bytes_including_preflight_reserve':charged,'payload_bytes_recorded':sum(r['bytes'] for r in ledger if r.get('kind')!='preflight-reserve'),
      'transfer_by_source':dict(transferred),'transfer_assigned_to_library':dict(assigned),'transfer_limit_bytes':BUDGET,'parliament_catalogue_state':state,
      'parliament_catalogue_coverage':catalogue_coverage,
      'source_crawl_states':source_states,'archive_catalogue_coverage':'bounded first search pages; not exhaustive',
      'catalogue_is_not_file_census':True,'snapshot_complete_unique_item_census':'unverified; live equal-title pagination can overlap',
      'print_conflicts_excluded':sum(r['print_review']['status'] in ('unverified-conflict','non-target-sample') for r in rows.values()),
      'scan_origin_unverified_excluded':sum(r['print_review']['status']=='unverified-scan-origin' for r in rows.values()),
      'raw_ocr_is_silver':True,'baseline_s17_excluded':True,'anemi_authenticated_discovery':anemi_discovery,
      'measurement_replay':'retained-source-measurements' if retain_source_measurements else 'recorded-text-refreshed',
      'prior_candidate_measurements_sha256':prior_hash}
    write_json(EVIDENCE/'summary.json',report)
    lines=['# O4c discovery summary','',f"Ranked **{report['documents']} additional licensed documents**: **{report['polytonic_docs']} polytonic**, **{report['cyrillic_docs']} Cyrillic**. Counts require a media URL, affirmative compatible record rights and measured target-script OCR; the 107 S17 documents are excluded. OCR and line estimates are silver evidence, awaiting adjudication.",'',
      '| Source | Catalogue records found | Media URLs | Layer declared / measured | Ranked | Poly / Cyrillic docs | Estimated poly / Cyrillic lines | Recorded payload bytes |',
      '|---|---:|---:|---:|---:|---:|---:|---:|']
    for source,s in counts.items():
        lines.append(f"| {source} | {s['records_found']} | {s['documents_with_media_url']} | {s['text_layer_declared_or_measured']} / {s['text_layer_measured']} | {s['ranked_documents']} | {s['polytonic_documents']} / {s['cyrillic_documents']} | {s['estimated_polytonic_lines']:,} / {s['estimated_cyrillic_lines']:,} | {s['transfer_payload_bytes']:,} |")
    lines+=['','Catalogue-record counts are unique parsed records, including unverified/rejected items; they are not verified-document counts or the sources\' full holdings. Archive discovery sampled one sorted 20-hit base page and one 8-hit explicit-rights page per requested language, plus a negative modern-Greek publication query. Search hit totals and resumable cursors are bound in `summary.json`; Archive coverage is not exhaustive.',
      '',f"Unfiltered Parliament traversal: cursor {catalogue_coverage['end_cursor']}, all-pages-traversed={catalogue_coverage['all_pages_traversed']}; {catalogue_coverage['unique_saved_item_records']:,} unique saved item records versus {reported_total_display} API-reported objects. Equal-title overlap/live pagination prevents certifying complete unique-item coverage. The table combines all retained discovery queries, so its Parliament count can differ from the unfiltered stream. Full PDF-file bundle coverage remains **unverified**.",
      '',f"Task transfer charged: **{charged:,} bytes ({charged/1e9:.3f} GB)**, including a 1 MiB conservative reserve for pre-ledger connectivity/HEAD/tool-search work. Original O4c limit: 2,000,000,000 bytes; authenticated Anemi continuation enforces **1,500,000,000 cumulative bytes**, including the earlier ledger. Ledger counts response payload bytes actually read (compressed bytes for gzip metadata); HTTP/TLS headers are not a wire capture. Cache hits charge zero. Robots, errors, aborted bounded reads and redirects are included. Reconnaissance and reserve are shown separately in `summary.json`.",'',
      '## Coverage and limitations','',
      '- S1: live [Parliament API](https://digitallibrary.parliament.gr/records/api) identifies DSpace 7.6. The InvenioRDM endpoint `/api/records` returned 404. The unfiltered catalogue reports 76,274 records. Catalogue cursor/traversal completion is bound in `summary.json`; equal-title pages can overlap, so snapshot-complete unique-item coverage is unverified even at the end cursor. Requests above 100 records silently truncate despite reporting the larger page size; the tested cardinality gate rejects that mismatch. Resolving all original bundles is a separate unfinished file census. Existing S17 rows are excluded from the ranked supply. Large parent volumes may expose page images but no PDF; session records do expose PDFs. One page per new PDF was measured by PDFium through sparse byte ranges, with a 4 MB per-open/probe cap and no large full-file fallback.',
      f"- S2: Authenticated [Anemi public search](https://anemi.lib.uoc.gr/search/) traverses 1800–1950 decade/year-range streams for `gre`/`grc` and monographs/multi-volume editions; exact requests and completion are in `anemi.state.json` and the ledger. Catalogue complete={anemi_discovery['catalogue_complete']}; media inventory complete={anemi_discovery['inventory_complete']}. {anemi_discovery['documents']:,} in-scope metadata records, {anemi_discovery['sampled_documents']:,} bounded viewer PDF samples, {anemi_discovery['pdf_with_layer']:,} nonempty sampled layers and {anemi_discovery['polytonic_docs']:,} measured polytonic documents. Full-PDF download CAPTCHA was not crossed; the public viewer supplies at most three pages per book. Empty samples do not prove that other pages or original PDFs lack OCR. {anemi_discovery['unprobed_PDF_documents']:,} listed PDFs remain unprobed; stop reason: {anemi_discovery['stop_reason'] or 'none'}. Source terms permit personal/educational/research access, prohibit commercial use and systematic storage of whole items, and grant no redistribution licence. Thus Anemi contributes zero to the compatible ranking. Credentials, cookies and authenticated raw bodies are never persisted. `/tools/` and `/db/` remain unqueried. Earlier OAI guesses returned 404.",
      '- S3: [Internet Archive advancedsearch](https://archive.org/advancedsearch.php) uses the requested language clauses, then prioritises 1800–1950 scans with DjVu sidecars, plus an explicit-rights query. Full `_djvu.txt` files are measured; `_djvu.xml` prefixes, where fetched, verify WORD coordinates only in that prefix. A Text PDF or DjVu is listed by the item API. Embedded PDF text and full-file integrity remain unverified: the external OCR sidecar is the measured layer, and bounded media headers verify format/access. Only 512-byte Archive file prefixes are fetched to verify media signatures/access; no full scan PDF/DjVu is downloaded. Bounded single-page JPEG probes check printed script; those bytes are included in the Archive transfer figure. Four misleading OCR results (German Korrespondenzblatt and three Syriac Anecdota volumes) are excluded after sampled print contradicted their Cyrillic layer/metadata. Their other pages remain unverified, and raw measurements plus image-bound reviews remain in discovery evidence. Missing rights, NC/ND and non-target OCR are not ranked.',
      '- S4: [Commons robots](https://commons.wikimedia.org/robots.txt) and all five language Wikisource robots disallow the requested `/w/api.php` query paths. No imageinfo or proofread API request crossed that block. Live scan rights, text-layer presence and gold text are unverified; ranked contribution is zero.',
      '- S5: [Pergamos robots](https://pergamos.lib.uoa.gr/robots.txt) blocks OAI/search; the obsolete frontend URL returned 404. [Gallica robots](https://gallica.bnf.fr/robots.txt) blocks SRU search query URLs; no prohibited SRU/text endpoint was fetched. [National Library of Greece](https://digitalcollections.nlg.gr/) is reachable, an OAI guess returned 500, and HTML search yielded no parsed print candidates. The [Wellcome catalogue API](https://api.wellcomecollection.org/catalogue/v2/works) returned Greek query matches, including unrelated items/manuscripts; no qualifying Greek print PDF with measured OCR was verified. These attempts are recorded, not claimed as zero holdings.',
      '- Two CC0 Tolstoy uploads have clear modern digital-looking typesetting on plain white pages and original Text PDFs of only about 3 MB for 1,266/1,295 pages. Their scanned physical-print origin is unverified; both are conservatively excluded despite real Cyrillic OCR. No PDF was downloaded to resolve that uncertainty.',
      '- Ratios measure the noisy layer, not the printed truth. Low ratios can reflect OCR mark loss; high ratios do not certify labels. PDF estimates extrapolate one page and can be strongly biased. Archive counts count nonempty OCR newline units bearing the relevant script/marks; they are neither geometry-adjudicated nor gold lines. Dictionary/classical editions may rank above modern prose and must be selected by edition for the training goal.',
      '- PD/CC declarations are reproduced exactly with source URLs, not independently adjudicated copyright decisions. Attribution, CC-BY-SA obligations, publication/author checks and doc-level train/dev/test separation remain admission gates. No training or external publication was performed.',
      '', '## Licence breakdown','']
    for source,s in counts.items():lines+=['- '+source+': ranked '+json.dumps(s['licence_breakdown_ranked'],ensure_ascii=False)+'; all found '+json.dumps(s['licence_breakdown_all_found'],ensure_ascii=False)]
    lines+=['','## Highest expected supply','', '| Rank | Source / document | Year | Poly lines | Cyrillic lines | Exact licence |','|---:|---|---:|---:|---:|---|']
    for r in candidates[:20]:
        title=str(r['title']).replace('|','/').replace('\n',' ')[:100]
        lines.append(f"| {r['rank']} | [{title}]({r['record_url']}) | {r['year']} | {r['estimated_polytonic_lines'] or 0:,} | {r['estimated_cyrillic_lines'] or 0:,} | {r['rights']['identifier']} |")
    lines+=['','## Anemi research-access discovery: top 20 nonempty viewer PDF layers','',
      'Separate from the compatible candidate manifest. Sorted by the same descending polytonic + Cyrillic line estimate, then source/document ID. Only nonempty measured viewer layers are listed; empty samples and unprobed documents remain in discovery evidence. Sizes and selected full-file page counts are catalogue declarations. These probes measure viewer derivatives, not verified original-PDF OCR.','',
      '| Position | Document | Year | PDF pages / bytes | Sample pages | Chars/page | Poly ratio | Cyrillic ratio | Layer |',
      '|---:|---|---:|---:|---:|---:|---:|---:|---|']
    sampled=sorted((r for r in ar if r['text_layer']['status']=='verified' and r['text_layer'].get('page_indices')),key=lambda r:(
        -((r['estimated_polytonic_lines'] or 0)+(r['estimated_cyrillic_lines'] or 0)),r['source']+':'+r['document_id']))
    for i,r in enumerate(sampled[:20],1):
        m=r['text_layer']['measurement'];title=str(r['title']).replace('|','/').replace('\n',' ')[:90]
        size=f"{r['size']:,}" if r['size'] is not None else 'unverified'
        lines.append(f"| {i} | [{title}]({r['record_url']}) | {r['year']} | {r['pages']} / {size} | {r['text_layer']['sample_pages']} | {m['chars_per_page']:.1f} | {m['polytonic_ratio']:.4f} | {m['cyrillic_ratio']:.4f} | {r['text_layer']['status']} |")
    lines+=['','Exact Anemi terms and interpretation: `anemi_terms.json` and `docs/ocr_program_2026-10-06/O4c_NOTES.md`. Anemi offline tests: `anemi_tests.log`.']
    lines+=['','Machine-readable counts: `summary.json`. Schema and continuation commands: `O4c_NOTES.md`. Recorded-fixture test log: `tests.log`.']
    (EVIDENCE/'summary.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:report[k] for k in ('documents','polytonic_docs','cyrillic_docs','payload_bytes_including_preflight_reserve')},ensure_ascii=False))
if __name__=='__main__':
    arguments=argparse.ArgumentParser(description=__doc__)
    arguments.add_argument('--retain-source-measurements',action='store_true',
        help='merge stored measurements without replaying other-source OCR bodies')
    arguments.add_argument('--prior-candidates',type=pathlib.Path,
        help='prior compatible-candidate manifest to retain (default: existing candidates.jsonl)')
    options=arguments.parse_args()
    if options.prior_candidates and not options.retain_source_measurements:
        arguments.error('--prior-candidates requires --retain-source-measurements')
    main(options.retain_source_measurements,options.prior_candidates)
