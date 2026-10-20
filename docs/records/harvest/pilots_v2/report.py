"""Build P1 source manifests, disjoint allocations, yield tables and receipts."""
from __future__ import annotations
from collections import Counter,defaultdict
import json,math,pathlib,shutil,sys
from pilotlib import *
sys.path.insert(0,str(ROOT))
from greekocr.harvest.admission import page_quality
from classify import inspect

PILOTS=['ia1850','ia1900','bsb','elstat','kosmopolis','openarchives','ajax','wikisource','gutenberg','perseus']
COLLECTION=PILOTS[:6]
TARGETS={'poly1850':40000,'poly1900':50000,'modern_scanned':40000,'mixed_greek_latin':20000,'latin':8000,'cyrillic':12000,'headings_caps':6000,'numerics_tables':10000,'leaders_indices':4000,'dialogue_fiction':12000}

def jsonl(path,records):
    path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(''.join(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n' for r in records))

def primary(r):
    inv=r.get('inventory',{});greek=inv.get('greek_letters',0);tags=r.get('line_tags',[])
    if r.get('mixed_line'):return 'mixed_greek_latin'
    if 'leaders' in tags:return 'leaders_indices'
    if greek>=3 and any(t in tags for t in ['caps','heading']):return 'headings_caps'
    if 'numeric' in tags:return 'numerics_tables'
    if greek>=3 and any(t in tags for t in ['dialogue_punctuation','fiction_source']):return 'dialogue_fiction'
    if r['script_class']=='greek_poly' and r['pilot']=='ia1850':return 'poly1850'
    if r['script_class']=='greek_poly' and r['pilot']=='ia1900':return 'poly1900'
    if r['script_class'] in ('greek_mono','greek_poly') and r['pilot']=='openarchives':return 'modern_scanned'
    return r['script_class']

def coverage(r):
    out=[];greek=r.get('inventory',{}).get('greek_letters',0);tags=r.get('line_tags',[])
    if r.get('mixed_line'):out.append('mixed_greek_latin')
    if r['script_class']=='greek_poly' and r['pilot']=='ia1850':out.append('poly1850')
    if r['script_class']=='greek_poly' and r['pilot']=='ia1900':out.append('poly1900')
    if r['pilot']=='openarchives' and greek:out.append('modern_scanned')
    if r['script_class'] in ('latin','cyrillic'):out.append(r['script_class'])
    if greek>=3 and any(t in tags for t in ['caps','heading']):out.append('headings_caps')
    if 'numeric' in tags:out.append('numerics_tables')
    if 'leaders' in tags:out.append('leaders_indices')
    if greek>=3 and any(t in tags for t in ['dialogue_punctuation','fiction_source']):out.append('dialogue_fiction')
    return out

def counter(records,field):return dict(Counter(r[field] for r in records))

if __name__=='__main__':
    pages=[json.loads(p.read_text()) for p in sorted((BASE/'receipts/pages').glob('*.json'))]
    selected=[p for p in pages if not p.get('excluded') and p['pilot'] in PILOTS];selected_ids={p['id'] for p in selected}
    canonical=[];quality=[];analyses=[];global_seen=set()
    for p in selected:
        if p['pilot']=='ajax':continue
        lp=BASE/'bulk/lines'/(p['id']+'.jsonl')
        if not lp.exists():continue
        rr=rows(lp)
        for r in rr:r.update(inspect(r['docai_raw_text'],r['confidence'],tall=r['tall_box']))
        qinput=[dict(page_id=p['id'],docai_text=r['text'],confidence=r['confidence'] or 0,flags=['tall_box'] if r['tall_box'] and 'heading' not in r['line_tags'] else []) for r in rr]
        q=page_quality(qinput).get(p['id'],dict(bad_page=False));quality.append(dict(page_id=p['id'],**q))
        seen=set()
        for r in rr:
            if p['pilot']=='kosmopolis' and p['item'] in ('xrysallis-61109','xrysallis-61117','xrysallis-61118','xrysallis-61120'):
                r['line_tags']=sorted(set(r['line_tags']+['fiction_source']))
            r['pre_page_admitted']=r['admitted'];r['bad_page']=q['bad_page']
            if q['bad_page']:
                r['admitted']=False;r['rejection_reasons']=sorted(set(r['rejection_reasons']+['bad_page']))
            # Exact same crop+label within a page is never two usable rows.
            key=(r['crop_sha256'],r['canonical_label']);r['duplicate_within_page']=key in seen;seen.add(key)
            r['duplicate_crop_label']=key in global_seen
            if r['admitted'] and r['codec_v1_pass'] and r['geometry_positive'] is False:global_seen.add(key)
            r['usable_candidate']=r['admitted'] and r['codec_v1_pass'] and r['geometry_positive'] is False and not r['duplicate_crop_label']
            r['primary_allocation']=primary(r);r['target_coverage']=coverage(r)
        canonical.extend(rr)
        analyses.append(dict(page_id=p['id'],path=str(lp.relative_to(BASE)),sha256=sha(lp),lines=len(rr)))
    jsonl(BASE/'bulk/records.jsonl',canonical);jsonl(BASE/'page_quality.jsonl',quality);jsonl(BASE/'lines_manifest.jsonl',analyses)
    items=[json.loads(p.read_text()) for p in sorted((BASE/'receipts/items').glob('*.json'))]
    jsonl(BASE/'items.jsonl',items);jsonl(BASE/'pages.jsonl',pages)
    budget=rows(BASE/'google/budget.jsonl');read_receipts={json.loads(p.read_text())['page_id']:json.loads(p.read_text()) for p in (BASE/'receipts/reads').glob('*.json')}
    image_pilots=defaultdict(set)
    for p in selected:image_pilots[p['image_sha256']].add(p['pilot'])
    cost=Counter()
    for r in budget:
        owners=sorted(image_pilots[r['key']]);cost[owners[0] if owners else 'unassigned']+=r['micro_usd']
    ajax=json.loads((BASE/'receipts/ajax-summary.json').read_text());ag=[json.loads(p.read_text()) for p in (BASE/'receipts/ajax-geometry').glob('*.json')];ajax_rows=[r for p in (BASE/'bulk/ajax-geometry').glob('*.jsonl') for r in rows(p)]
    gt_lookup={r['id']:r for r in rows(BASE/'bulk/ajax-lines.jsonl')};gt_seen=set()
    for r in ajax_rows:
        info=gt_lookup[r['id'].removesuffix('.gt')];r.update(info)
        key=(r['page_id'],r['crop_sha256'],r['canonical_label']);r['duplicate_crop_label']=key in gt_seen;gt_seen.add(key)
        r['usable_candidate']=r['admitted'] and r['codec_v1_pass'] and r['geometry_positive'] is False and not r['duplicate_crop_label']
    bound_ids={r['id'] for r in ajax_rows}
    missing_gt=[r for key,r in gt_lookup.items() if key not in bound_ids]
    for info in missing_gt:
        ajax_rows.append(dict(**info,page_id='ajax--'+info['id'].rsplit('_',1)[0],pilot='ajax',binding='original_page_not_published_in_archive',geometry_positive=None,duplicate_crop_label=False,usable_candidate=False))
    write(BASE/'receipts/ajax-binding-coverage.json',dict(published_gt_pairs=len(gt_lookup),geometry_rows=len(ajax_rows),published_native_pages=len(ag),gt_crops_without_published_native_page=len(missing_gt),unpublished_page_groups=sorted({r['id'].rsplit('_',1)[0] for r in missing_gt}),policy='Every published line pair is retained; absent original page images are geometry-unresolved, not silently excluded from the admission denominator. No substitute scan or Google read.'))
    jsonl(BASE/'bulk/ajax-geometry-final.jsonl',ajax_rows)
    align=json.loads((BASE/'receipts/alignment-summary.json').read_text());aligned=rows(BASE/'bulk/alignment.jsonl');alignment_pages=align['pages'];summaries=[]
    # Preserve every sampled page and every provider region, including abstentions.
    page_coverage=[{k:v for k,v in p.items() if k!='transformations'} for p in alignment_pages]
    jsonl(BASE/'alignment_pages.jsonl',page_coverage)
    region_keys=['id','page_id','pilot','item','accepted','accepted_for_target_reference','release_status','human_script_class','human_mixed_line','target_rejection_reasons','reasons','source_span_nfd','literal_source_ownership','crop_path','crop_sha256','bbox','geometry_positive','text_revision','text_sha256','page_image_sha256','proofreading_status']
    jsonl(BASE/'alignment_regions.jsonl',[{k:r.get(k) for k in region_keys} for r in aligned])
    grouped=defaultdict(list)
    for p in page_coverage:grouped[(p['pilot'],p['item'],p['layout'],p['regime'])].append(p)
    coverage_groups=[]
    for (pilot,item,layout,regime),pp in sorted(grouped.items()):
        total=sum(p['google_nfd_characters'] for p in pp);kept=sum(p['target_retained_nfd_characters'] for p in pp)
        coverage_groups.append(dict(pilot=pilot,item=item,layout=layout,regime=regime,pages=len(pp),google_lines=sum(p['google_lines'] for p in pp),target_lines=sum(p['target_retained_lines'] for p in pp),target_retained_nfd_characters=kept,all_page_ocr_nfd_characters=total,target_character_coverage_pct=100*kept/total if total else 0,zero_target_label_pages=sum(not p['target_retained_lines'] for p in pp),target_rejection_reasons=dict(sum((Counter(p['target_rejection_reasons']) for p in pp),Counter()))))
    jsonl(BASE/'alignment_coverage.jsonl',coverage_groups)
    for name in PILOTS:
        pp=[p for p in selected if p['pilot']==name];allpp=[p for p in pages if p['pilot']==name];rr=[r for r in canonical if r['pilot']==name]
        usable=[r for r in rr if r['usable_candidate']];admitted=[r for r in rr if r['admitted'] and r['codec_v1_pass']]
        evaluable=[r for r in admitted if r['geometry_positive'] is not None]
        read_pages=sum(p['id'] in read_receipts and read_receipts[p['id']]['status']=='ok' for p in pp)
        flags=Counter(t for r in rr for t in r['line_tags']);primary_counts=Counter(r['primary_allocation'] for r in usable);cover=Counter(t for r in usable for t in r['target_coverage'])
        result=dict(pilot=name,pages_requested={'ia1850':100,'ia1900':60,'bsb':50,'elstat':50,'kosmopolis':50,'openarchives':60,'ajax':None,'wikisource':50,'gutenberg':50,'perseus':50}[name],pages_fetched=len(allpp),pages_rendered=len(allpp),pages_sampled=len(pp),pages_read=read_pages,lines=len(rr),script_classes=counter(rr,'script_class'),line_tags=dict(flags),admitted=sum(r['admitted'] for r in rr),admitted_codec=len(admitted),usable_candidates=len(usable),usable_rows_per_read_page=len(usable)/read_pages if read_pages else None,admission_rule_counts=dict(Counter(t for r in rr if r['admitted'] for t in r['admission_rules'])),rejection_reasons=dict(Counter(t for r in rr for t in r['rejection_reasons'])),geometry_positive=sum(r['geometry_positive'] is True for r in evaluable),geometry_evaluable=len(evaluable),geometry_unresolved=sum(r['geometry_positive'] is None for r in admitted),geometry_positive_pct=100*sum(r['geometry_positive'] is True for r in evaluable)/len(evaluable) if evaluable else None,all_line_geometry_positive=sum(r['geometry_positive'] is True for r in rr),all_line_geometry_evaluable=sum(r['geometry_positive'] is not None for r in rr),mixed_lines=sum(r['mixed_line'] for r in rr),mixed_share=sum(r['mixed_line'] for r in rr)/len(rr) if rr else None,primary_allocations=dict(primary_counts),primary_rows_per_read_page={k:v/read_pages for k,v in primary_counts.items()} if read_pages else {},target_coverage=dict(cover),target_coverage_rows_per_read_page={k:v/read_pages for k,v in cover.items()} if read_pages else {},cost_usd=cost[name]/1e6,contact_sheet='contact_sheets/'+name+'-20-pages.jpg',label_status='pilot candidates, not released training rows or independent truth')
        if name=='ajax':
            eligible=[r for r in ajax_rows if r['admitted'] and r['codec_v1_pass']]
            result.update(lines=ajax['lines'],script_classes=ajax['script_classes'],line_tags=ajax['tags'],admitted=ajax['admitted_content_rules'],admitted_codec=ajax['admitted_and_codec'],mixed_lines=ajax['mixed_lines'],mixed_share=ajax['mixed_share'],rejection_reasons=ajax['rejection_reasons'],geometry_positive=sum(r['geometry_positive'] is True for r in eligible),geometry_evaluable=sum(r['geometry_positive'] is not None for r in eligible),geometry_unresolved=sum(r['geometry_positive'] is None for r in eligible),usable_candidates=sum(r['usable_candidate'] for r in ajax_rows),admission_confidence_policy=ajax['confidence_policy'])
            result['geometry_positive_pct']=100*result['geometry_positive']/result['geometry_evaluable'] if result['geometry_evaluable'] else None
        if name in ('wikisource','gutenberg','perseus'):
            aa=[r for r in aligned if r['pilot']==name];aps=[r for r in alignment_pages if r['pilot']==name];accepted=[r for r in aa if r['accepted']]
            result.update(human_label_candidates=len(accepted),human_labels_per_read_page=len(accepted)/read_pages if read_pages else None,greek_bearing_label_candidates=sum(r['mixed_line'] or r['script_class'].startswith('greek') for r in accepted),retained_nfd_characters=sum(r.get('retained_nfd_characters',0) for r in aps),proofread_nfd_characters=sum(r.get('proofread_nfd_characters',0) for r in aps),google_nfd_characters=sum(r.get('google_nfd_characters',0) for r in aps),retained_lines=len(accepted),rejected_alignment_lines=len(aa)-len(accepted),alignment_rejection_reasons=dict(Counter(reason for r in aa for reason in r['reasons'])),zero_label_pages=sum(not r.get('retained_lines',0) for r in aps),printed_page_verified_pages=sum(r.get('printed_page_verified',False) for r in aps),blind_sheet='blind_sheets/'+name+'/sheet.html',released_reference_lines=0)
            result['proofread_body_character_coverage_pct']=100*result['retained_nfd_characters']/result['proofread_nfd_characters'] if result['proofread_nfd_characters'] else 0
            result['google_page_character_coverage_pct']=100*result['retained_nfd_characters']/result['google_nfd_characters'] if result['google_nfd_characters'] else 0
            target=[r for r in accepted if r['accepted_for_target_reference']]
            result['raw_ocr_greek_bearing_label_candidates']=result['greek_bearing_label_candidates'];result['greek_bearing_label_candidates']=len(target)
            result['target_reference_candidates']=len(target);result['target_reference_labels_per_page']=len(target)/read_pages if read_pages else 0
            result['target_retained_nfd_characters']=sum(r['source_span_nfd'][1]-r['source_span_nfd'][0] for r in target)
            result['target_page_character_coverage_pct']=100*result['target_retained_nfd_characters']/result['google_nfd_characters'] if result['google_nfd_characters'] else 0
        summaries.append(result)
        rule_yield={};rule_rows=ajax_rows if name=='ajax' else rr
        if name=='ajax':result['admission_rule_counts']=dict(Counter(t for r in ajax_rows if r['admitted'] for t in r['admission_rules']))
        for rule in sorted({rule for r in rule_rows for rule in r['admission_rules']}):
            eligible=[r for r in rule_rows if rule in r['admission_rules']]
            rule_yield[rule]=dict(eligible=len(eligible),admitted=sum(r['admitted'] for r in eligible),usable=sum(r['usable_candidate'] for r in eligible),admission_yield=sum(r['admitted'] for r in eligible)/len(eligible))
        result['admission_rule_yield']=rule_yield
        def digit_bin(r):
            n=r['inventory']['digits']
            return '1' if n==1 else '2-3' if n<=3 else '4-7' if n<=7 else '8+'
        result['numeric_usable_digit_counts']=dict(Counter(digit_bin(r) for r in usable if 'numeric' in r['line_tags']))
    jsonl(BASE/'pilots.jsonl',summaries)
    shutil.copyfile(BASE/'google/budget.jsonl',BASE/'receipts/p1-budget.jsonl');shutil.copyfile(BASE/'google/docai/ledger.jsonl',BASE/'receipts/p1-provider-ledger.jsonl')
    total_cost=sum(r['micro_usd'] for r in budget)/1e6;total_read=sum(s['pages_read'] for s in summaries);collection=[s for s in summaries if s['pilot'] in COLLECTION]
    gp=sum(s['geometry_positive'] for s in collection);ge=sum(s['geometry_evaluable'] for s in collection);rate=100*gp/ge if ge else 0
    alignment=[s for s in summaries if s['pilot'] in ('wikisource','gutenberg','perseus')];retained=sum(s['target_retained_nfd_characters'] for s in alignment);denom=sum(s['google_nfd_characters'] for s in alignment);cov=100*retained/denom if denom else 0
    by={s['pilot']:s for s in summaries}
    fmt=lambda v:'n/a' if v is None else f'{v:.2f}'
    lines=['# P1 — collection and alignment pilots','',f'**Execution:** {total_read} scan-page deliveries; {len(budget)} unique paid attempts reserved; **USD {total_cost:.4f}** at list price, below the USD 5 cumulative P1 cap. This is reservation accounting, not invoice readback. All published human-text labels remain **proposals pending the coordinator’s blind pixel adjudication**; released reference lines = 0.','',
    'The old collection has separate wave ledgers. P1 preserves their format in `google/budget.jsonl` and `google/docai/ledger.jsonl`; copies prepared for tracking are [reservations](receipts/p1-budget.jsonl) and [provider ledger](receipts/p1-provider-ledger.jsonl). The [authorization interpretation](receipts/authorization.json), [historical ledger hashes](receipts/prior-ledger-snapshot.json), [processor binding](receipts/processor-binding.json) and [pricing receipt](receipts/pricing.json) record the scope. Every new attempt was reserved before network I/O. No failed/ambiguous attempt is refunded by the local cap, and no free tier is deducted. [Official pricing](https://cloud.google.com/products/document-ai/pricing).','',
    '## Scope and reading rules','',
    'Collection targeted 370 pages in the six Google-read pilots. Actual front matter was added after native review found bindings among the first leaves; the original pages stay in every read denominator. IA documents remain below 40 sampled pages each. Kosmopolis has 32 and 20 pages from two issues. Three first OA downloads were physically born digital and are retained as excluded witnesses; replacement records link three actual scanned statistical publications (1962, 1974, 1982). Their unrelated metadata titles/years are not used as printed facts. These are one provider stratum, not evidence of broad OA diversity.','',
    f'**Gutenberg qualification limit:** PG #69810, Blackie, *The Pronunciation of Greek* (1852), is English prose with Greek, Latin and German quotations. It credits IA as image provider without an item locator. The matched IA edition is separately bound by title/imprint/year and page headers. Only **{by["gutenberg"]["target_reference_candidates"]} Greek-bearing candidates / 50 pages = {by["gutenberg"]["target_reference_labels_per_page"]:.2f}/page** qualify for the target cohort; the 802 all-language candidates cannot be used as a Greek yield. Target script is classified from the proofread label; raw OCR script counts are retained separately. This is a disclosed exploratory philology pilot. **The strict Greek-language-catalogue IA-citation pairing requested in the brief remains unqualified**; this report does not assert that condition was fulfilled.','',
    'Rasters are grayscale, maximum long side 3500 px; PDF rendering uses at most 200 dpi. All sampled pages are read, including page/detector failures, covers and zero-label leaves. Main harvest/source modules remain unchanged. G1b is imported read-only from the supplied geometry worktree; its detector cache uses this worktree’s actual page/glyph code hash.','',
    'Admission keeps main content rules and confidence ≥0.89, with the requested overlays: caps ≥3 letters; digit share ≥40%; ≥5-dot runs retained with `DOTS:n` plus literal repeated-dot canonical text; tall heading candidates get a separate crop path. Long dot runs without a contents/index pattern are not counted as leader targets. Dot counts from Google remain silver counts, not independently adjudicated physical truth. Page-quality rejection is retained, exempting heading crops from the tall-box page trigger. The shipped codec is v1; unsupported characters are rejected visibly. No codec-v2 recovery is assumed.','',
    'A usable candidate is admitted after page quality, codec-supported, G1b-negative and not an exact crop/label duplicate across the Google-read pilots. G1b positives and unresolved rows are withheld. This is a measured pipeline yield, not a released training count. Exact-identifier/URL/PDF overlap checks and unresolved semantic edition binding are recorded separately; no training, lexicon or synthetic-seed release occurs.','',
    '## Collection results','',
    '| Pilot | Fetched/rendered | Sampled/read | Lines | Admitted | + codec | Usable candidates | Rows/read page | Mixed lines | G1b + / evaluable (unresolved) | USD | 20-page sheet |',
    '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    for s in summaries[:7]:
        lines.append(f'| {s["pilot"]} | {s["pages_fetched"]}/{s["pages_rendered"]} | {s["pages_sampled"]}/{s["pages_read"]} | {s["lines"]} | {s["admitted"]} | {s["admitted_codec"]} | {s["usable_candidates"]} | {fmt(s["usable_rows_per_read_page"])} | {s["mixed_lines"]} ({100*(s["mixed_share"] or 0):.1f}%) | {s["geometry_positive"]}/{s["geometry_evaluable"]} = {fmt(s["geometry_positive_pct"])}% ({s["geometry_unresolved"]}) | {s["cost_usd"]:.4f} | [sheet]({s["contact_sheet"]}) |')
    lines += ['', 'Ajax has 3,364 actual paired files versus the README’s stated 3,356. Of its 921 mixed lines, 783 pass content admission plus codec. Its confidence gate is inapplicable to publisher-declared human GT; content-rule and codec counts are shown rather than inventing confidence scores. The archive supplies 68 full native page images; 332 GT crop pairs belong to eight other page groups whose full-page images are absent. Those pairs remain geometry-unresolved in the denominator ([binding coverage](receipts/ajax-binding-coverage.json)). Pixel-template binding and G1b are reported separately. Original GT/images and their pinned archive remain under `bulk/ajax/`.','',
    '## Script classes, tags and admission rules','',
    '| Pilot | Raw script classes | Raw line tags (overlapping) | Accepted rule firings (overlapping) | Rejection reasons (overlapping) |','|---|---|---|---|---|']
    show=lambda d:'; '.join(f'{k}: {v}' for k,v in sorted(d.items())) or 'none'
    for s in summaries[:7]:lines.append(f'| {s["pilot"]} | {show(s["script_classes"])} | {show(s["line_tags"])} | {show(s["admission_rule_counts"])} | {show(s["rejection_reasons"])} |')
    lines += ['', 'Rule eligible/admitted/usable counts and fractions are in `pilots.jsonl` (`admission_rule_yield`); rule firings overlap. Script class uses the unchanged main classifier. The mixed-line flag additionally counts Greek inside Latin-majority lines; those must not disappear into the Latin-majority class. Kosmopolis fiction-source tags identify the sampled article PDFs for episodes/stories 61109, 61117, 61118 and 61120; shared pages may include neighbouring material, so this is a source-level fiction cohort rather than adjudicated line-level semantics. Explicit dialogue punctuation is counted separately. Primary allocations below are disjoint; target-coverage flags in `pilots.jsonl` overlap and must not be summed.','',
    '## Quota inputs: usable primary rows per read page','',
    '| Primary target | Target rows | ia1850 | ia1900 | bsb | elstat | kosmopolis | openarchives | Best measured source / indicative pages |','|---|---:|---:|---:|---:|---:|---:|---:|---|']
    for target,quota in TARGETS.items():
        values=[by[p]['primary_rows_per_read_page'].get(target,0) for p in COLLECTION];best=max(range(len(values)),key=lambda i:values[i]);estimate=f'{COLLECTION[best]} / {math.ceil(quota/values[best]):,}' if values[best]>0 else 'not estimable; no qualifying pilot rows'
        if target=='cyrillic':estimate='not piloted; no quota inferred from incidental rows'
        lines.append('| '+target+' | '+str(quota)+' | '+' | '.join(f'{v:.2f}' for v in values)+' | '+estimate+' |')
    lines += ['', 'These page projections use the measured primary allocation once. They do not add another admission/codec multiplier. They remain planning estimates from purposive pilots, including covers and front/back matter, and do not certify repository-wide yield. Cyrillic was not a selected collection pilot.','',
    '**Numeric unit:** a row here is a provider line crop, often one table cell or a single digit. It is not a reconstructed physical table row. The numeric projections therefore estimate cell/line examples only. BSB mixed yield is below the data plan’s 10 mixed lines/page planning assumption; this pilot does not support that assumption.','',
    '| Pilot | Usable numeric crops: 1 digit | 2–3 digits | 4–7 digits | ≥8 digits |','|---|---:|---:|---:|---:|']
    for s in collection:
        counts=s['numeric_usable_digit_counts'];lines.append('| '+s['pilot']+' | '+' | '.join(str(counts.get(k,0)) for k in ['1','2-3','4-7','8+'])+' |')
    lines += ['',
    '## Alignment release-contract accounting','',
    '| Source | Read pages | All-language label candidates | All labels/read page | Greek-bearing target labels (per page) | All retained NFD characters / proofread body | Target / all page-OCR characters | Zero all-label pages | Page witness verified | 40-line blind sheet |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    for s in alignment:
        lines.append(f'| {s["pilot"]} | {s["pages_read"]} | {s["human_label_candidates"]} | {fmt(s["human_labels_per_read_page"])} | {s["target_reference_candidates"]} ({s["target_reference_labels_per_page"]:.2f}) | {s["retained_nfd_characters"]}/{s["proofread_nfd_characters"]} ({s["proofread_body_character_coverage_pct"]:.1f}%) | {s["target_page_character_coverage_pct"]:.1f}% | {s["zero_label_pages"]} | {s["printed_page_verified_pages"]} | [blind sheet]({s["blind_sheet"]}) |')
    lines += ['', 'NFD sequence alignment assigns only uniquely owned literal spans with anchored boundaries, ≥0.92 sequence similarity and ≥0.90 matched-atom support. These thresholds nominate candidates; Google similarity never establishes truth. Printed line-end hyphens absent from the proofread source abstain. Repeated spans, inside-word boundaries, unknown markup/editorial regions, unverified printed page numbers and G1b-positive/unresolved crops abstain.','',
    'Each candidate retains the scan hash, exact text revision/body hash, proofreading declaration, source span and raw-wikitext NFD offsets or XML/HTML XPath text-node offsets. TEI `choice` resolves only an explicit printed branch (`orig`, `sic`, `abbr`), otherwise abstains; supplied text/apparatus/notes are not flattened into body truth. PG boilerplate, moved notes/references and editorial notes are recorded transformations/excluded regions. Wikisource uses validated revision-pinned pages with zero overlap with the prior 400-page manifest.','',
    'All 50 sampled pages per source remain in coverage, including empty/zero-label pages. Proofread-body coverage and page-OCR-character coverage are separate. Neither is a full-page truth claim. Reference release is pending the 40-card accepted/rejected blind audit for each source; no judgments have been supplied. Candidate works are listed as excluded from future training/lexicon/synthetic inputs; existing global seed pools were not rewritten or certified clean by this pilot.','',
    '| Source | Alignment rejection reasons (overlapping) |','|---|---|']
    for s in alignment:lines.append(f'| {s["pilot"]} | {show(s["alignment_rejection_reasons"])} |')
    lines += ['', 'Coverage includes the full normalized Document AI document text, including headers and page numbers outside the proofread body. [Every sampled page](alignment_pages.jsonl), [every accepted/rejected provider region with crop coordinates and literal ownership](alignment_regions.jsonl), and [grouped coverage/reasons](alignment_coverage.jsonl) retain the denominator. Layout and dominant script regime below are detector/classifier diagnostics, not adjudicated layout truth. No unanchored nonspace document characters were silently removed.','',
    '| Source / edition | Layout / dominant regime | Pages | Target lines / all provider lines | Target characters / all page OCR characters | Coverage | Zero-target pages |','|---|---|---:|---:|---:|---:|---:|']
    for g in coverage_groups:
        lines.append(f'| {g["pilot"]} / {g["item"]} | {g["layout"]} / {g["regime"]} | {g["pages"]} | {g["target_lines"]}/{g["google_lines"]} | {g["target_retained_nfd_characters"]}/{g["all_page_ocr_nfd_characters"]} | {g["target_character_coverage_pct"]:.1f}% | {g["zero_target_label_pages"]} |')
    lines += ['', '## Item rights and witnesses','', 'Rights are records, not an acquisition gate under the owner’s P1 instruction. An owner-authorised cloud read is not rewritten as a source-issued cloud licence. Every selected item has a [rights/witness record](items.jsonl); the detailed records preserve original metadata, physical corrections and unresolved fields.','', '| Item | Pilot | Printed/source title | Scan/text/retention/training/redistribution record |','|---|---|---|---|']
    selected_items={p['item'] for p in selected}
    for item in items:
        key=item['item']
        if key not in selected_items:continue
        metadata=item.get('metadata',{})
        if isinstance(metadata,list):metadata={'title':next((m['value'] for m in metadata if any(label.get('@value')=='Title' for label in m.get('label',[]))),'see source metadata')}
        metadata=metadata if isinstance(metadata,dict) else {}
        title=item.get('printed_title',item.get('title',metadata.get('title','see source metadata')))
        lines.append(f'| {key} | {item["pilot"]} | {" ".join(str(title).replace("|","/").split())} | [item record](receipts/items/{key}.json) |')
    lines += ['', '## Artifacts and limitations','',
    '- [Pilot records](pilots.jsonl), [all page witnesses including exclusions](pages.jsonl), [item records](items.jsonl), [line-file manifest](lines_manifest.jsonl), [page-quality decisions](page_quality.jsonl), [file inventory](FILES.tsv).',
    '- Bulk raster pages, original downloads, raw Google responses, native crops, detector caches and row/alignment ledgers are ignored under this directory. Contact and blind sheets remain available locally at their linked paths.',
    '- The [geometry source receipt](receipts/source-bindings.json), [admission contract checks](receipts/admission-contract-check.json), [budget checks](receipts/budget-contract-check.json) and [validation](receipts/validation.json) bind the methods. G1b thresholds are inherited diagnostics in a new source population; positives are not adjudicated error prevalence.',
    '- Source sampling is purposive, not representative. The OA pilot is restricted to three scanned statistical publications. The Gutenberg scope and provider-credit limitation are explicit above. Dot counts remain silver until native adjudication. No proposed label, crop repair or source exception was promoted into a production dataset.',
    '- The [Gutenberg qualification evidence](receipts/gutenberg-qualification.json) binds the bounded S1 census and full Fairley follow-up. It does not assert that no qualifying ebook exists.',
    '- Interactive browser QA was blocked by the managed environment. [Representative static raster inspection](receipts/visual-qa.json) and all-card/link checks are recorded separately from unperformed browser UI verification.',
    '- Git staging/commit was blocked because the shared worktree index is outside the writable roots; no files were staged or committed. The [source-bound staging handoff](README.md) and `receipts/git-handoff.json` record the exact normal-terminal continuation. Bulk files are not candidates for Git tracking.','']
    sheets=len(list((BASE/'receipts/sheets').glob('*.json')))+len(list((BASE/'receipts/blind-sheets').glob('*.json')))
    focus={'ia1850':'poly1850','ia1900':'poly1900','bsb':'mixed_greek_latin','elstat':'numerics_tables','kosmopolis':'dialogue_fiction','openarchives':'modern_scanned'}
    y={p:by[p]['primary_rows_per_read_page'].get(target,0) for p,target in focus.items()}
    footer=f'P1: done | pages_read: {total_read} usd: {total_cost:.4f} | collection: ia1850 {y["ia1850"]:.2f} ia1900 {y["ia1900"]:.2f} bsb {y["bsb"]:.2f} elstat {y["elstat"]:.2f} kosmopolis {y["kosmopolis"]:.2f} openarchives {y["openarchives"]:.2f} ajax {ajax["admitted_and_codec"]} | geometry_positive: {rate:.2f}% | alignment: wikisource {by["wikisource"]["target_reference_labels_per_page"]:.2f} gutenberg {by["gutenberg"]["target_reference_labels_per_page"]:.2f} perseus {by["perseus"]["target_reference_labels_per_page"]:.2f} coverage {cov:.2f}% | sheets: {sheets}'
    lines += [f'Footer geometry denominator: {gp}/{ge} evaluable admitted+codec collection rows (six Google pilots; Ajax reported separately). Footer alignment yields count Greek-bearing target candidates; coverage is their retained NFD characters divided by all sampled page-OCR NFD characters. The auxiliary English/Latin-only labels are not counted as Greek reference yield. Footer collection yields are the disjoint primary focus-class yields: historical/later polytonic, mixed Greek+Latin, numeric tables, fiction/dialogue and modern scanned Greek respectively. All-class yields are kept in the first table.','',footer]
    (BASE/'PILOTS.md').write_text('\n'.join(lines)+'\n')
    write(BASE/'receipts/totals.json',dict(pages_read=total_read,paid_attempts=len(budget),usd_reserved=total_cost,geometry_positive=gp,geometry_evaluable=ge,geometry_positive_pct=rate,alignment_retained_nfd_characters=retained,alignment_all_page_ocr_nfd_characters=denom,alignment_page_ocr_coverage_pct=cov,sheets=sheets,footer=footer))
    print(footer)
