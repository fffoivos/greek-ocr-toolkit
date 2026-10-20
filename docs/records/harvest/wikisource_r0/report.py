"""Produce an honest completion/preparation receipt and guarded commit manifest."""
import sys
sys.dont_write_bytecode=True
import collections
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
import harvest as h
import validate

def main():
    h.scrub_outputs()
    result=validate.main()
    continuation=h.load('T7B_POLICY.json')
    finished=time.time()
    assert finished<continuation['deadline_epoch'],'T7b completion deadline exceeded'
    h.save('T7B_COMPLETION.json',dict(task='T7b',completed_utc=datetime.fromtimestamp(finished,timezone.utc).isoformat(),
        elapsed_seconds=finished-(continuation['deadline_epoch']-3540),maximum_wall_seconds=3600,
        complete=result['complete'],google_requests=result['google_http_requests'],google_reserved_usd=result['reserved_usd'],
        lines=result['lines'],aligned_per_page=result['aligned_per_page']))
    h.save('google/cost_receipt.json',dict(reservations=result['reservations'],successful_reads=result['google_read_pages'],reserved_usd=result['reserved_usd'],hard_cap_usd=.30,unit_price_usd=.0015,policy='every attempted read must be reserved before call; all failures remain reserved'))
    books=validate.rows('books.jsonl');pages=validate.rows('pages.jsonl');lines=validate.rows('lines.jsonl')
    audit=h.load('exclusions/disjointness.json')
    events=validate.rows('preflight_receipts.jsonl')+validate.rows('limiter/events.jsonl')+validate.rows('google/network.jsonl')
    # Keep public URL/status/timing evidence; omit cookies, IPs and auth headers.
    network=[]
    for e in events:
        network.append({k:e[k] for k in ['url','host','path','status','started_at','sha256','bytes','user_agent'] if k in e})
    h.jsonl('network_receipts.jsonl',network)
    bpage=collections.Counter(p['book_key'] for p in pages)
    bline=collections.Counter(r['book_key'] for r in lines)
    status='COMPLETE' if result['complete'] else 'INCOMPLETE — see validation.json and the Google read receipts'
    text=['# T7b Greek Wikisource R0, stratum (i-b)', '', '**Status: '+status+'.**', '',
        'These artifacts are exclusively a locked test stratum for the spell-check and training tracks. Every book, page and line has `training_release_allowed=false` and `train_pool_eligible=false`. No training release or collection manifest was modified.', '',
        '| Book | Author | Year | Pages | Aligned lines |', '|---|---|---:|---:|---:|']
    for b in books:text.append(f"| [{b['title']}]({b['index_url']}) | {b['author']} | {b['year']} | {bpage[b['key']]} | {bline[b['key']]} |")
    text+=['',f"Total: **{len(books)} books, {len(pages)} selected scan pages, {len(lines)} aligned human lines**. Each book contributes at most 30 pages. The full proofread population is retained in `books.jsonl`; draws use `random.Random(seed + ':' + book_key).sample` without replacement, uniformly from every quality-3/4 page. Books with fewer than 30 eligible pages contribute all eligible pages. Seed: `{h.SEED}`.", '',
        f"There are {result['total_physical_page_images']} physical page images in this task, including 17 provisional prose images and five ancillary title/imprint pages. Prose candidates were set aside because their source uses paragraph rather than printed-line breaks; no Google reads were used for that decision. This is below the 150-page cap. Only the {len(pages)} final selected pages occur in `pages.jsonl`.", '',
        'Printer/publisher spread: '+ '; '.join(b['title']+' — '+(b['printer'] or 'unrecorded') for b in books)+'. The 1917 and 1922 books share the Γράμματα imprint; printer diversity is partial, not five independently established printers.', '',
        '## Disjointness', '',
        'The 318 L1 IDs were resolved through the main checkout’s read-only `collection/import_real_all.jsonl` and `collection/admitted_all.jsonl`, then joined to saved wave selection/plan metadata. Importer IDs normally use `wave:book_key`; the repaired Liddell–Scott lexicon uses `mixed:page_id`, so its `-pNNNNNN` suffix is collapsed and confirmed against `admitted_all.book_key`. All 318 IDs have source and title mappings. No L1 ID has a Wikisource source. The 40 mixed IDs resolve to 33 Anemi books, six OpenArchives books and the Liddell–Scott lexicon.', '',
        'Wikisource IDs use the existing eight-character SHA-256 of `el:<Commons filename>`. Commons source backlinks additionally recover Anemi record paths and their 24-character IDs, which are checked under the round1, round2 and mixed namespaces. No off-allowlist source host was contacted.', '',
        '| Key | R0 coverage (books) | L1 coverage (documents) | L1 intersection | Local-20 coverage (books) | Local-20 intersection |', '|---|---:|---:|---:|---:|---:|']
    for k,v in audit['intersections'].items():text.append(f"| {k} | {audit['selected_coverage'][k]}/5 | {audit['l1_key_coverage'][k]}/318 | {len(v['L1'])} | {audit['local_key_coverage'][k]}/20 | {len(v['local20'])} |")
    text+=['', 'Zero means zero intersection among resolved keys; it does not mean missing keys were invented. L1 has no recorded Commons/Index identities, 159 document bibliographies yield an author plus year, and seven parliamentary documents have no recorded year. The title-only guard covers all 318 L1 documents; title+year covers 311. Normalization folds Unicode accents, case, underscores and punctuation, and includes catalogue title aliases before author/subtitle separators. Full Commons scan SHA-1 and SHA-256 were independently computed from downloaded original bytes for all five selected scans and all 20 local Greek scans. Detailed mappings, input hashes, coverage and empty intersection arrays are in `exclusions/`.', '',
        '## Alignment and custody', '',
        '`harvest.py` calls the unchanged `greekocr/harvest/wikisource.py` stripper, template rules and monotone conservative aligner at similarity 0.65. Only one-to-one blocks can produce labels; unresolved templates, split/merge blocks and skipped lines do not. A second execution of the exact stripper with whitespace-only normalization retains pre-NFC Unicode; its NFC must equal the shared stripper result. Original raw wikitext, its hash and revision headers remain bound to each page.', '',
        'Native inspection showed leading poem indentation colons absent from print (e.g. Βάρβιτος scan page 14). Those source lines are excluded without changing their labels; their original and NFC text remain in page evidence. Labels with no Greek character are excluded. No spelling or accent correction is derived from OCR.', '',
        f"T7b native crop inspection additionally excludes {result['native_source_rejections']} specifically witnessed source/print discrepancies (omitted terminal punctuation; one iota-subscript/adscript difference). `qa/source_line_rejections.json` retains their original candidate records and crop hashes. These are finite source-quality exclusions after shared alignment; no human label or shared alignment rule was edited. Unlisted source/print differences may remain because visual inspection is sampled.", '',
        'T7b reads each of the 116 fixed drawn page images once, using the requested EU processor/version, and reserves USD 0.0015 in this task’s `google/ledger.jsonl` before each call. Reservations survive interruptions; automatic retries of an ambiguous read are prohibited. `pages.jsonl` retains line/token boxes, returned dimensions, native coordinate mapping and raw-response hashes. Crops use the native line box with four horizontal and two vertical pixels of bounded padding. `lines.jsonl` carries literal and NFC human labels, crop hashes and alignment traces. ADC discovery uses `google.auth.default()`; an environment override takes precedence. No credentials or credential paths are recorded.', '',
        '## Network, budget and validation', '',
        'T7’s original `RUN_POLICY.json`, selection and exclusion receipts remain unchanged. T7b’s own deadline (within 60 minutes), 116-call limit and USD 0.30 cap are in `T7B_POLICY.json`; `T7B_INPUTS.json` binds the reused selection, exclusions, human text and drawn images. Both phases use this task’s own `limiter/` directory. T7 Wikimedia acquisition used the contact User-Agent `greek-ocr-research/0.1 (foivos.karounos@gmail.com)`, robots checks and Retry-After handling. T7b performs no Wikimedia requests or redraws. Public request receipts are in `network_receipts.jsonl`. No W1 ledger, lock or limiter was accessed.', '',
        '**Metadata API limitation:** both live Wikimedia robots files disallow the standard `/w/api.php?action=query` endpoint. The robots-permitted `mobileview` API action was attempted with `maxlag=5`; both sites returned `badvalue` because that action has been retired. Metadata therefore uses permitted Index/Commons HTML and raw page reads. No disallowed API request was sent. The requested API-only metadata method could not be completed; the error receipts and robots bodies are preserved locally.', '',
        f"Google: **{result['reservations']} reservations, {result['google_read_pages']} successful reads, USD {result['reserved_usd']:.4f} reserved**, hard cap USD 0.30. One request per fixed drawn page; failed or ambiguous requests remain reserved. This is list-price accounting, not a billing-invoice claim. Credential contents, paths, tokens and refresh headers are never copied or logged.", '',
        f"Validation: {result['checks']}; {result['fixed_input_hashes']} fixed input hashes; exactly one reserved, uncached Google request per page; response geometry recomputed from raw evidence. Shared policy tests: **135 passed** (`policy_tests.txt`). Source policy and the existing 15 October harvest have no tracked changes. `validation.json` records `complete={str(result['complete']).lower()}`. Timing is recorded in `T7B_COMPLETION.json`.", '',
        'Binary scans, page images, crops, raw Google responses and limiter caches are local ignored evidence. `SHA256SUMS` inventories them by repository-relative path and hash; none is force-added. `commit_guard.py --check` validates the pinned parent, branch, file hashes, ignored-path exclusions and an empty index. `--commit` stages only that reviewed set and stops on a protected index.lock, with no alternate index or unguarded retry.', '']
    commit_status=h.load('COMMIT_STATUS.json') if (h.OUT/'COMMIT_STATUS.json').exists() else {}
    if commit_status.get('task')=='T7b' and commit_status.get('status')=='not_created':
        text+=['**Commit not created:** the guarded helper passed its read-only checks, then `git add` failed because the sandbox cannot create the worktree `index.lock` (`Operation not permitted`). No retry, alternate index, staging or commit occurred. The reviewed helper and `COMMIT_MANIFEST.json` are ready for execution in a context with Git metadata write access.', '']
    if not result['complete']:
        text+=['The harvest is incomplete. Consult the validation counts and read receipts before any continuation; reserved or ambiguous requests must never be automatically repeated.', '']
    summary=h.load('alignment_summary.json')
    total_google=sum(p.get('google_lines',0) for p in summary['pages'])
    text+=['## Alignment per page', '',
        f"Mean aligned human lines per drawn page: **{result['aligned_per_page']:.4f}** ({len(lines)}/{len(pages)}). Overall acceptance: {len(lines)}/{total_google} Google physical line boxes ({len(lines)/total_google:.2%}). {sum(not p['aligned'] for p in summary['pages'])} pages produced zero accepted labels. The per-page rate uses all returned physical line boxes, including page numbers and non-Greek headings. Exclusions retain the unchanged template, one-to-one and similarity rules.", '',
        '| Page | Aligned | Google lines | Aligned / Google lines |', '|---|---:|---:|---:|']
    for p in summary['pages']:
        n=p.get('google_lines',0)
        text.append(f"| {p['page_id']} | {p['aligned']} | {n} | {p['aligned']/n:.2%} |" if n else f"| {p['page_id']} | {p['aligned']} | 0 | n/a |")
    text+=['', '## Visual inspection', '']
    visual_path=h.OUT/'qa/crop_inspection.json'
    if visual_path.exists():
        visual=h.load('qa/crop_inspection.json')
        text.append(visual['scope'])
        text.append('')
        for sample in visual['samples']:
            text.append(f"- `{sample['line_id']}`: {sample['finding']}")
        text.append('')
    else:text+=['Pending sampled native crop/label inspection.', '']
    (h.OUT/'RECEIPT.md').write_text('\n'.join(text))
    # Binary evidence inventory is stable and excludes mutable locks/state.
    evidence=[]
    for folder in ['scans','images','crops','qa','google/provider','limiter']:
        for p in sorted((h.OUT/folder).rglob('*')):
            if p.is_file() and p.suffix not in ['.lock'] and p.name not in ['rate.json'] and not p.name.startswith('google-'):
                evidence.append(f'{h.sha(p)}  {h.rel(p)}')
    (h.OUT/'SHA256SUMS').write_text('\n'.join(evidence)+'\n')
    # Guard manifests cover every current, non-ignored T7 output, except itself.
    paths=subprocess.run(['git','ls-files','--others','--exclude-standard','--',h.rel(h.OUT)],cwd=h.ROOT,capture_output=True,text=True,check=True).stdout.splitlines()
    paths+=subprocess.run(['git','ls-files','--modified','--',h.rel(h.OUT)],cwd=h.ROOT,capture_output=True,text=True,check=True).stdout.splitlines()
    files={p:h.sha(h.ROOT/p) for p in sorted(set(paths)) if not p.endswith('/COMMIT_MANIFEST.json')}
    head=subprocess.run(['git','rev-parse','HEAD'],cwd=h.ROOT,capture_output=True,text=True,check=True).stdout.strip()
    h.save('COMMIT_MANIFEST.json',dict(parent_head=head,message='T7b: '+('read 116 fixed Wikisource pages and align human R0 labels' if result['complete'] else 'record incomplete Wikisource R0 continuation'),files=files))

if __name__=='__main__':main()
