"""Offline F1-GR report from receipts, with conservative supply accounting."""
from funnellib import *
from collections import Counter,defaultdict
import statistics,math

SOURCES={
'openarchives':('Open Archives / HF','Repository item → direct PDF from revision-pinned external_pdfs.parquet; cached text projection is not identity-safe.','cached HF login for table; repository PDFs public','alternative','Resolve and bind the text-shard metadata correctly; host-specific verified subsets only.','ELSTAT and Pergamos scanned print'),
'kosmopolis':('Kosmopolis','/index.php/<journal>/issue/view/<issue> → article/view/<article>/<galley> → article/download/<article>/<galley>/<file>','none','continue-partial','Only a bounded issue/article cohort is qualified.','Pleias / Lekythos literary periodicals'),
'pleias':('Pleias','/index.php/kritiki/issue/view/<issue> → article/view/<article>/<galley> → article/download/<article>/<galley>/<file>','none','continue-partial','Short article PDFs work; volume-scale supply is not established.','Kosmopolis / Lekythos'),
'pergamos':('Pergamos (UoA)','/item/uoadl:<id> → public-api/search published Page.webFile → /public-api/files/uoadl/<file-id>/payload-inline','none for published files','continue-partial','Printed books work; typed-thesis sample is born digital; sampled volumes below quota.','NLG IIIF / Kosmopolis'),
'nlg-digital':('NLG digital library','/nlg-repo/dl/el/browse/<item> → /nlg-repo/dl/el/iiifmetadata/<item> → published IIIF canvas image @id','none','continue-partial','IIIF works; mixed-language/Ancient Greek content needs item selection.','Pergamos printed books'),
'nlg-newspapers':('NLG newspapers','/ns/ftr.asp → POST /ns/search.asp → obsolete www.nlg.gr/digitalnewspapers/ns/pdfwin_ftr.asp; current /ns/pages_ftr.asp reports unavailable','none','alternative','No fresh page raster; stale viewer link and unavailable issue frames.','NLG digitalcollections@nlg.gr; Kosmopolis / Lekythos'),
'elstat':('ELSTAT dlib','http://dlib.statistics.gr/portal/page/portal/ESYE/categoryyears → yeararticles → showdetails?p_id=<id> → /Book/<code>.pdf','none','continue-partial','Scanned yearbooks work; later yearbook is born digital; 1859 is not yearbook start.','Historic ΦΕΚ / Pergamos'),
'government-gazette':('ΦΕΚ / Government Gazette','search.et.gr official UI getFekLink → https://ia37rg02wpsa01.blob.core.windows.net/fek/<issue:02>/<year>/<year><issue:02><number:05>.pdf','none','continue-partial','Historic scans verified; only sampled issues count as supply.','ELSTAT / official ET Museum–Library contact'),
'bank-of-greece':('Bank of Greece','Governor report page → publication catalogue static PDF links → /Publications/ekthdkth<year>.pdf','none','alternative','Sampled reports are born digital; historical scanned-report route remains unqualified.','ELSTAT scanned reports / BoG library historical digitisation enquiry'),
'psifiothiki':('Psifiothiki (AUTh)','/collection/Rare Books → /record/<id> → /record/<id>/files/<name>.pdf (robots-disallowed)','none','alternative','robots.txt disallows *.pdf; no PDF requested after refusal.','Pergamos / NLG IIIF printed books'),
'lekythos':('Lekythos (University of Cyprus)','/archive/item/<id> → /archive/download/<published-uuid>.pdf','none','continue-partial','Literary print scans verified; bounded issue cohort below class quota.','Pleias / Kosmopolis'),
'medusa-veria':('Medusa (Veria)','Current Iguana books page → published Vfocus Session/staticContent services returned empty bodies; no printed item media path','none','alternative','JavaScript shell and empty published content responses; no page/PDF route verified.','Provider-supported export/IIIF; Pergamos / NLG printed books'),
'anemi':('Anemi','logged-in catalogue pdf_pager.php iframe → pdf_split.php?filename=<published-path>&pageno=<n>&pagenum=1','held account; environment only; memory-only cookies','continue-partial','50-page cap completed; five measured books already collected; no new supply census.','Kosmopolis / Pleias / Pergamos for new editions'),
'gennadius':('Gennadius','No fetch, per brief; existing inventory describes on-demand scanning','not probed','drop','On-demand scanning is not an existing machine acquisition route.','Pergamos / NLG IIIF Greek print'),
'laskaridis-travelogues':('Laskaridis Travelogues','No fetch, per brief; existing inventory is illustration-oriented','not probed','drop','No existing printed-Greek-prose machine route established.','Kosmopolis / Pleias Greek prose')}

def sec(s):return datetime.datetime.fromisoformat(s).timestamp()
def pct(v,p):
    if not v:return None
    a=sorted(v);i=(len(a)-1)*p;l=int(i);return a[l]+(a[min(l+1,len(a)-1)]-a[l])*(i-l)
def errkind(r):
    s=r.get('error','')
    if 'robots' in s:return 'robots/refused preflight'
    if 'size_limit' in s:return 'PDF above probe byte bound'
    if 'HTML_or_non_PDF' in s:return 'HTML/non-PDF (includes restricted-resource pages)'
    if '404' in s:return 'HTTP 404'
    if '429' in s:return 'HTTP 429'
    if '503' in s:return 'HTTP 503'
    status=re.search(r'HTTP (\d{3})',s)
    if status and status[1]!='200':return 'HTTP '+status[1]
    if 'ChunkedEncodingError' in s or 'truncated' in s:return 'truncated/incomplete body'
    if 'Timeout' in s or 'timeout' in s or 'curl_28' in s:return 'timeout'
    if '400 MB' in s:return 'local image disk cap'
    return s[:120] or 'unknown'
def metrics(rr):
    success=[r for r in rr if r['success']];np=sum(r.get('decoded_pages',0) for r in success)
    elapsed=max(sec(r['ended_at']) for r in rr)-min(sec(r['started_at']) for r in rr) if rr else 0
    ordered=sorted(rr,key=lambda r:sec(r['started_at']));segments=[]
    for r in ordered:
        if not segments or sec(r['started_at'])-sec(segments[-1][-1]['ended_at'])>60:segments.append([])
        segments[-1].append(r)
    benchmark=next((ss for ss in segments if sum(r.get('decoded_pages',0) for r in ss if r['success'])>=50 and len({r['item'] for r in ss if r['success']})>=5),None)
    active=sum(max(sec(ss[-1]['ended_at'])-sec(ss[0]['started_at']),.001) for ss in segments)
    br=benchmark or ordered;bn=sum(r.get('decoded_pages',0) for r in br if r['success'])
    be=sec(br[-1]['ended_at'])-sec(br[0]['started_at']) if benchmark else active
    times=[r['total_seconds']/r.get('decoded_pages',1) for r in success for _ in range(r.get('decoded_pages',1))]
    sizes=[r.get('bytes',0)/r.get('decoded_pages',1) for r in success for _ in range(r.get('decoded_pages',1))]
    pdfs=[r for r in success if r['kind']=='pdf']
    return dict(media_attempts=len(rr),successful_media=len(success),decoded_pages=np,success_percent=100*len(success)/len(rr) if rr else None,
                sustained_pages_per_minute=60*bn/be if be else None,elapsed_seconds=elapsed,wall_span_pages_per_minute=60*np/elapsed if elapsed else None,
                rate_benchmark=dict(qualifying_continuous_50_pages_5_items=bool(benchmark),decoded_pages=bn,items=len({r['item'] for r in br if r['success']}),elapsed_seconds=be,
                                    method='first continuous cohort with >=50 decoded pages and >=5 items; otherwise pooled active segments; gaps >60s split segments'),
                median_seconds_per_decoded_page=statistics.median(times) if times else None,p90_seconds_per_decoded_page=pct(times,.9),
                median_original_bytes_per_decoded_page=statistics.median(sizes) if sizes else None,
                pdfs_per_minute=60*len(pdfs)/elapsed if elapsed else None,
                median_MB_per_PDF=statistics.median(r.get('bytes',0)/1e6 for r in pdfs) if pdfs else None,
                median_pages_per_PDF=statistics.median(r.get('page_count',0) for r in pdfs) if pdfs else None,
                median_time_to_first_page_seconds=statistics.median(r['time_to_first_page_seconds'] for r in pdfs if r.get('time_to_first_page_seconds') is not None) if any(r.get('time_to_first_page_seconds') is not None for r in pdfs) else None,
                failure_modes=dict(Counter(errkind(r) for r in rr if not r['success'])))
def fmt(n,d=2):return '—' if n is None else f'{n:.{d}f}'
def clean(s):return str(s).replace('|','/').replace('\n',' ')[:650]

def build():
    media=rows(BASE/'receipts/media.jsonl');http=rows(BASE/'receipts/http.jsonl');pages=rows(BASE/'probe_pages.jsonl')
    pacingaudit=json.loads((BASE/'receipts/pacing-exact-start-audit.json').read_text()) if (BASE/'receipts/pacing-exact-start-audit.json').exists() else {}
    output=[];candidates=[];text=[]
    text+=['# F1-GR — Greek institutions funnel verification','',f'Run date: {stamp()}. Branch `sol/funnel-gr`. No Google requests, collection admission, cloud compute or spend. No push.','',
    '**Commit status:** the managed worker could not create the shared worktree `index.lock`, which lies outside its writable roots. No worker commit exists. [commit-blocker.json](receipts/commit-blocker.json) records the refusal; `python3 docs/harvest/funnel_v1/gr/commit_gr.py` is the guarded owner-side commit command. A source-bound patch is supplied under ignored `bulk/F1-GR.patch`.','',
    '**Readout:** individual access is fresh-decode evidence; all supply counts below are bounded, enumerated lower bounds. A catalogue total or a plausible URL is never counted as an accessible item. No source has demonstrated the complete usable-row quota.','',
    'Pages/min is **decoded witness pages per minute** in the first continuous cohort containing ≥50 decoded pages over ≥5 items. Gaps above 60 seconds split exploratory runs; sources without such a cohort use pooled active segments and are marked in `rate_benchmark`. Intervening polite waits and catalogue work remain included. The full wall-span rate is retained in JSONL. Whole-PDF rates and sizes are separate. A PDF download is one network fetch even when several pages are rendered. Timing includes the local render; this is not an OCR throughput measurement. Sequential and concurrency-three cohorts are separated in machine-readable metrics.','',
    '| source | access path Y/N | pages/min | success % | failure modes | blocker | candidate items with page access per period (and target class) | overlap with collected/test | proposed decision + one-line reason | alternative named |',
    '|---|---|---:|---:|---|---|---|---|---|---|']
    for src,(name,route,auth,decision,reason,alternative) in SOURCES.items():
        rr=[r for r in media if r['source']==src and r.get('mode')!='concurrency3' and r['kind']!='construction_recheck'];m=metrics(rr)
        cand=rows(BASE/f'candidates_{src}.jsonl');candidates.extend(cand)
        unique={r['id']:r for r in cand};cand=list(unique.values());period=Counter(str(r.get('decade') or 'unknown') for r in cand)
        new=[r for r in cand if r.get('new_candidate_eligible')];newperiod=Counter(str(r.get('decade') or 'unknown') for r in new)
        classes=Counter(cl for r in new for cl in r.get('target_classes',[]))
        overlap=Counter('held-out' if r.get('held_out_test') else 'collected' if r.get('overlap_flag')=='collected' else 'no exact match; edition unresolved' for r in cand)
        path=any(r['source']==src for r in pages)
        if src not in ['gennadius','laskaridis-travelogues'] and m['success_percent'] is not None:
            if m['success_percent']<80 or (m['sustained_pages_per_minute'] or 0)<2:decision='alternative'
        issues={r.get('issue') for r in cand if r.get('issue')};journals={r.get('journal') for r in cand if r.get('journal')}
        if src in ['kosmopolis','pleias']:reason+=f' Counted unit: {len(cand)} articles in {len(issues)} issues / {len(journals)} periodicals, not {len(cand)} volumes.'
        robots=[dict(url=r['url'],status=r.get('status'),error=r.get('error'),sha256=r.get('sha256')) for r in http if r['source']==src and r['kind'] in ['robots','robots_refusal']]
        blocker_ref={'openarchives':'receipts/oa-projection-rebinding.json','nlg-newspapers':'receipts/nlg-newspapers-blocker.json','medusa-veria':'receipts/medusa-blocker.json','bank-of-greece':'receipts/bank-of-greece-blocker.json','psifiothiki':'receipts/robots/'+sha(b'https://digital.lib.auth.gr')[:16]+'.json','anemi':'receipts/anemi-run.json','elstat':'receipts/elstat-yearbook-years.json'}.get(src)
        if blocker_ref is None:blocker_ref=f'candidates_{src}.jsonl' if cand else f'receipts/prior/{src}/source-assessment.json'
        record=dict(source=src,name=name,access_path_verified=path,access_pattern=route,auth=auth,robots=robots,**m,
                    concurrency3=metrics([r for r in media if r['source']==src and r.get('mode')=='concurrency3']),
                    construction_rechecks=metrics([r for r in media if r['source']==src and r['kind']=='construction_recheck']),
                    candidate_items_with_page_access=len(cand),candidate_items_by_decade=dict(period),new_target_candidates=len(new),new_target_candidates_by_decade=dict(newperiod),target_classes=dict(classes),
                    unique_fresh_JPEG_hashes=len({p['image_sha256'] for p in pages if p['source']==src}),
                    overlap=dict(overlap),blocker=reason,blocker_receipt=blocker_ref,
                    proposed_decision=decision,decision_reason=reason,alternative=alternative,issues_with_page_access=len(issues),periodicals_with_page_access=len(journals),
                    rights_record='Per-item candidate records, and receipts/prior/'+src+'/source-assessment.json; owner decides rights. Unresolved is not a rejection gate.')
        output.append(record)
        failure=', '.join(f'{k}: {v}' for k,v in m['failure_modes'].items()) or ('none in media sample' if rr else 'not sampled / blocked before media')
        supply=f'all access {dict(period)}; new target {dict(newperiod)}; classes {dict(classes)}'
        text.append('| '+' | '.join(map(clean,[name,'Y' if path else 'N',fmt(m['sustained_pages_per_minute']),fmt(m['success_percent'],1),failure,reason+f' [receipt]({blocker_ref})',supply,dict(overlap),decision+' — '+reason,alternative]))+' |')
    (BASE/'funnel.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n' for r in output))
    text+=['','## Per-class supply at ≤40 pages per item','',
    'These are candidate **pages**, not usable or labelled rows. Class tags are source/format leads; headings, numerics, leaders and dialogue still need the later page/line pilot. Unbound document metadata, retained test matches and already-collected books are excluded from new-item totals. Cross-repository edition equivalence remains a screening limitation. The same item can appear in several classes; these rows are not additive. `poly1850` uses 1850–1890 inclusive; `poly1900` uses 1900–1982 inclusive.','',
    '| target class | new candidate sources | candidate items | pages available at ≤40/item | item gate / status |','|---|---|---:|---:|---|']
    needs={'poly1850':112,'poly1900':98,'modern':80,'Greek+Latin':50,'Latin':None,'Cyrillic':30,'numerics':None,'headings':None,'leaders':None,'dialogue':None}
    supply={}
    for cl,need in needs.items():
        chosen=[r for r in candidates if r.get('new_candidate_eligible') and cl in r.get('target_classes',[])]
        bysource=Counter(r['source'] for r in chosen);n=len(chosen);np=sum(r.get('pages_at_cap40',0) for r in chosen)
        supply[cl]=dict(candidate_items=n,pages_at_cap40=np,sources=dict(bysource),item_gate=need,usable_rows=None)
        text.append(f'| {cl} | {clean(dict(bysource)) if chosen else "No verified new supply in this track"} | {n} | {np} | '+(f'{need} items required; ' if need else 'usable-row quota unmeasured; ')+('partial' if n else 'unproven')+' |')
    write(BASE/'receipts/class-supply.json',supply)
    exact=json.loads((BASE/'receipts/exact-page-overlap.json').read_text())
    text+=['',f'Known exact raster overlap: **{exact["groups_count"]}** cross-item groups in [exact-page-overlap.json](receipts/exact-page-overlap.json), including article PDFs sharing a boundary page. These known duplicates are subtracted before the 40-page cap, and wholly duplicated short items are excluded from new supply. Rescans and unseen pages are not asserted distinct. Fetch-rate counts still include the requests actually made.','']
    review=json.loads((BASE/'receipts/script-review.json').read_text())
    text+=['','## Script verification','',
    'A manual check uses one fresh decoded leaf per listed sampled item, bound to JPEG hashes in [script-review.json](receipts/script-review.json). The two demonstrated unreliable mixed pools meet the ≥20-item check: Open Archives and NLG digital. A Greek catalogue tag is not treated as proof of the script on every leaf.','',
    '| source | sampled items | Greek visibly present | verified share |','|---|---:|---:|---:|']
    for rr in review['counts']:text.append(f'| {rr["source"]} | {rr["n"]} | {rr["Greek_visible"]} | {100*rr["Greek_visible"]/rr["n"]:.1f}% |')
    text+=['','Open Archives includes an English leaf, a Latin leaf, an uncertain poster and a non-Greek manuscript counterexample. NLG includes two English leaves. Anemi’s five-book cap includes a French-only sampled leaf in a bilingual volume; the cap was not expanded. These are leaf-script observations, not whole-volume language or within-line mixing classifications.','']
    text+=['','## Routes, rate details and rights','',
    '| source | verified pattern / stopping point | authentication | median / p90 s per decoded page | median original bytes per decoded page | PDFs/min; MB/PDF; pages/PDF; first-page seconds |','|---|---|---|---:|---:|---|']
    for r in output:
        pdfstats='; '.join([fmt(r['pdfs_per_minute']),fmt(r['median_MB_per_PDF']),fmt(r['median_pages_per_PDF'],0),fmt(r['median_time_to_first_page_seconds'])])
        text.append('| '+' | '.join(map(clean,[r['name'],r['access_pattern'],r['auth'],fmt(r['median_seconds_per_decoded_page'])+' / '+fmt(r['p90_seconds_per_decoded_page']),fmt(r['median_original_bytes_per_decoded_page'],0),pdfstats]))+' |')
    text+=['','Every candidate records scan rights, text rights, published licence string (null when not recovered), access-terms URL, restriction flags and overlap evidence. Rights were recorded without acting as an acquisition gate. Public access is not treated as a reuse licence. The original declarations are preserved in the copied inventory source assessments; per-item overrides are retained verbatim as metadata.','',
    'Anemi’s fresh terms receipt records: “Systematic storage or printing of the whole content of the digital items is strictly forbidden.” The owner decides rights. The test used held account credentials only in memory, no `pdf_dump.php`, no CAPTCHA solving, and exactly 50 ordinary one-page viewer responses over five books. See [terms](receipts/anemi-terms.json), [run](receipts/anemi-run.json), and [transport](receipts/anemi-transfer.jsonl).','',
    'Psifiothiki’s `*.pdf$` robots rule was honoured. No query-string trick, mirror path, login, or access-control workaround was used to fetch those PDFs. NLG newspapers: [official digital collections contact](https://digitalcollections.nlg.gr/nlg-repo/dl/el/about.html), `digitalcollections@nlg.gr`; no message sent. Medusa: request a supported current item export/page interface from Veria Public Library; no request sent.','',
    '## Open Archives: identity, hosts and physical construction','',
    'The fresh HF table is pinned by revision and hash in [hf-link-table.json](receipts/hf-link-table.json). The 15 October cached text metadata projection contains unrelated title/date/collection and direct-PDF combinations. [Exact URL rebinding](receipts/oa-projection-rebinding.json) maps its first 60 fresh PDFs to **five**, rather than the ten projection labels. The unbound title/date/ocr_success population is never counted as dated new scanned supply. Additional directly link-table-bound probes are separate in [oa-external-physical.jsonl](receipts/oa-external-physical.jsonl).','']
    reb=json.loads((BASE/'receipts/oa-projection-rebinding.json').read_text()) if (BASE/'receipts/oa-projection-rebinding.json').exists() else {}
    physical={r['id']:dict(r,collection_slug=r['link_table_collection_unambiguous'],success=True) for r in reb.get('documents',[]) if r.get('link_table_collection_unambiguous')}
    for r in rows(BASE/'receipts/oa-external-physical.jsonl'):
        if r['success'] and r.get('mode')=='sequential':physical[r['metadata_id']]=r
    for r in rows(BASE/'receipts/physical-rechecks.jsonl'):
        if r.get('success') and r['id'] in physical:physical[r['id']]['physical_pages']=r['physical_pages']
    cols=defaultdict(list)
    for r in physical.values():cols[r['collection_slug']].append(r)
    text+= [f'Physically decoded, link-table-bound distinct PDFs: **{len(physical)} across {len(cols)} collections**. This is a deliberately bounded access/format sample, not a random population scan-share estimate.','',
    '| actual HF collection | distinct decoded PDFs | scanned body verified | all sampled pages scanned | born-digital content | uncertain / mixed construction |','|---|---:|---:|---:|---:|---:|']
    physicalsummary=[]
    for col,rs in sorted(cols.items()):
        scans=sum(document_scan(r['physical_pages'],r['url'])['scanned_body_verified'] for r in rs)
        allscan=sum(document_scan(r['physical_pages'],r['url'])['all_sampled_pages_scanned'] for r in rs)
        born=sum(document_scan(r['physical_pages'],r['url'])['has_born_digital_content'] for r in rs)
        uncertain=sum(document_scan(r['physical_pages'],r['url'])['mixed_or_uncertain'] for r in rs)
        physicalsummary.append(dict(collection=col,n=len(rs),scanned=scans,scanned_share=scans/len(rs),all_sampled_pages_scanned=allscan,has_born_digital_content=born,uncertain=uncertain))
        text.append(f'| {col} | {len(rs)} | {scans} ({100*scans/len(rs):.1f}%) | {allscan} | {born} | {uncertain} |')
    write(BASE/'receipts/oa-physical-summary.json',dict(unique_pdfs=len(physical),actual_collections=len(cols),collections=physicalsummary,required_60_across_10_met=len(physical)>=60 and len(cols)>=10))
    recovered=[json.loads(p.read_text()) for p in (BASE/'receipts/oa-catalogue-rebinding').glob('*.json')]
    text+=['',f'Fresh repository catalogue rebinding verified an exact offered PDF-attachment path and title for **{sum(r.get("verified",False) for r in recovered)}/{len(recovered)}** earlier documents. Those fresh catalogue dates, where present, replace the discarded projection dates; the old pipeline `ocr_success/page_count/polytonic_ratio` binding remains unresolved. See [catalogue rebinding receipts](receipts/oa-catalogue-rebinding).','',
    '| decade (pre-2000 first) | decoded scanned-body documents | new class candidates after overlap/script screening | capped candidate pages |','|---|---:|---:|---:|']
    oa_candidates=[r for r in candidates if r['source']=='openarchives' and r.get('physical_scanned_sample')]
    decades=sorted({r.get('decade') for r in oa_candidates if r.get('decade') is not None})+[None]
    for decade in decades:
        rs=[r for r in oa_candidates if r.get('decade')==decade];new=[r for r in rs if r.get('new_candidate_eligible')]
        if rs:text.append(f'| {decade if decade is not None else "unknown / unbound"} | {len(rs)} | {len(new)} | {sum(r.get("pages_at_cap40",0) for r in new)} |')
    text+=['','Construction test: recursively enumerate PDF page objects, record text drawing-object counts/render modes and placed image bounds. A full-page image covers ≥85% of the page bounds. With no text objects it is scanned; with only invisible (render mode 3) text it is scanned with hidden OCR. Render-mode-0 OCR is also hidden when every text object is drawn **before** a decoded opaque image that covers every text bound. This refinement is bound to identical PDF hashes in [physical-rechecks.jsonl](receipts/physical-rechecks.jsonl). Visible text above an image and ambiguous constructions remain uncertain. EKT-generated DOI metadata covers are reported separately from the scanned body and excluded from candidate scanned-page counts. Dynamically regenerated PDFs whose hashes changed were not substituted into earlier witnesses. `ocr_success` never supplies the scan label. Each rendered page has its source-PDF hash, physical object evidence and retained JPEG hash.','',
    '| host (Open Archives probes only) | route attempts / qualified success | success % | complete PDF HTTP responses / non-redirect attempts | decoded pages/min | PDFs/min | median MB/PDF | median / p90 s/page |','|---|---:|---:|---:|---:|---:|---:|---:|']
    hoststats=[]
    for host in sorted({urlsplit(r['url']).netloc for r in media if r['source']=='openarchives'}):
        rr=[r for r in media if r['source']=='openarchives' and urlsplit(r['url']).netloc==host and r.get('mode')!='concurrency3' and r['kind']!='construction_recheck'];m=metrics(rr)
        wire=[r for r in http if r['source']=='openarchives' and urlsplit(r['url']).netloc==host and r['kind'] in ['pdf','pdf_structure_recheck'] and r.get('status') not in [301,302,303,307,308]]
        wireok=sum(r.get('status') in [200,206] and not r.get('error') and 'pdf' in r.get('headers',{}).get('content-type','').lower() for r in wire)
        hoststats.append(dict(host=host,HTTP_PDF_attempts=len(wire),complete_PDF_HTTP_responses=wireok,**m))
        text.append(f'| {host} | {m["media_attempts"]} / {m["successful_media"]} | {fmt(m["success_percent"],1)} | {wireok} / {len(wire)} | {fmt(m["sustained_pages_per_minute"])} | {fmt(m["pdfs_per_minute"])} | {fmt(m["median_MB_per_PDF"])} | {fmt(m["median_seconds_per_decoded_page"])} / {fmt(m["p90_seconds_per_decoded_page"])} |')
    write(BASE/'receipts/oa-host-rates.json',hoststats)
    oa=next(r for r in output if r['source']=='openarchives')
    text+=['',f'Concurrency 3: {oa["concurrency3"]["media_attempts"]} PDF fetches, {oa["concurrency3"]["successful_media"]} decoded successes; host starts still spaced at least one second. HTTP 429/503 and Retry-After, if any, are in the HTTP ledger. A short clean run cannot establish a production throttle ceiling.','',
    '## Protocol and validation record','',
    f'The [exact start-timestamp audit](receipts/pacing-exact-start-audit.json) retains **{pacingaudit.get("count",0)}** historical intervals below the requested spacing; **{pacingaudit.get("below_target_by_over_1ms",0)}** were short by over 1 ms. The minimum was **0.949 seconds**, from a Dione robots.txt request to a PDF start. This run therefore does **not** receive a clean strict-pacing certificate. Historical rate measurements are descriptive. The limiter was corrected to serialize actual starts per host with a 100-ms margin. A fresh bounded concurrency-three check is recorded in [concurrency3-v2.json](receipts/concurrency3-v2.json); no old timing evidence was removed. The earlier Ahrefs-only Crawl-delay overapplication, which caused waiting rather than excessive request rate, is recorded separately in [rate-parser-correction.json](receipts/rate-parser-correction.json).','',
    'One separate diagnostic HEAD request to Bank of Greece robots.txt used curl’s default User-Agent instead of the required contact UA; it fetched no page body. This is recorded in [operator-diagnostics.json](receipts/operator-diagnostics.json). It is a protocol deviation, not hidden inside the instrumented acquisition ledger.','',
    'The native macOS TLS fallback kept certificate verification enabled. Raw PDF originals were discarded after measuring bytes/hashes and decoding witnesses; grayscale JPEGs remain under the 400-MB page-image cap. HF metadata-library calls and web-search discovery are outside the repository HTTP timing benchmark. Media attempts include failed route/preflight attempts and hash-bound construction rechecks; full HTTP discovery counts remain in the ledger. See [validation.json](receipts/validation.json) for artifact consistency and the retained pacing exception.','',
    '## Supply boundaries and owner questions','',
    '- Approve or revise the proposed source decisions before step 2; this report does not authorise collection.',
    '- Open Archives needs a correctly identity-bound text-shard projection before its large `ocr_success`, date and polytonic-ratio counts can be trusted. Freshly decoded documents with unknown dates remain unknown; no decade population is extrapolated.',
    '- ELSTAT’s catalogue year list starts at 1930. The 1859 date concerns the wider historical publication collection. Pre-1930 historical-series supply is not counted as yearbooks.',
    '- Decide which published per-item rights and retention conditions to use; Anemi’s systematic-storage notice remains explicitly recorded.',
    '- Cross-repository edition identity remains open where no exact ID/URL/title overlap was found. Test matches are flagged and excluded from proposed new supply.',
    '- Within-line Greek+Latin, Cyrillic and Latin usable-row supply is not established by this Greek track. Ancient Greek script and facing-language columns are not automatically the requested modern prose or within-line mixing.',
    '- Later page sampling and Google-output checks remain separate, unperformed steps. Candidate page totals are not usable-row forecasts.','']
    (BASE/'FUNNEL.md').write_text('\n'.join(text))
    decisions=Counter(r['proposed_decision'] for r in output);success=sum(r['success'] for r in media)
    summary=dict(sources=len(output),path_Y=sum(r['access_path_verified'] for r in output),decisions=decisions,fetches=len(media),successful_fetches=success,success_percent=100*success/len(media) if media else 0,per_class={k:v['candidate_items'] for k,v in supply.items()},page_image_MB=sum(p.stat().st_size for p in (BASE/'bulk/pages').rglob('*.jpg'))/1e6,bulk_MB=sum(p.stat().st_size for p in (BASE/'bulk').rglob('*') if p.is_file())/1e6)
    write(BASE/'receipts/summary.json',summary);print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__':build()
