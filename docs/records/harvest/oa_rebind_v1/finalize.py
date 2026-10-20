"""Build the correction proposal and findings from preserved receipts only."""
import sys
sys.dont_write_bytecode=True
import collections,json,random
from audit import *

SPLITS=['train','dev','test']
def main():
    books=json.loads((OUT/'receipts/initial-bindings.json').read_text())
    originals={b['key']:b for b in json.loads((OA/'books.json').read_text())}
    counts=json.loads((OUT/'receipts/split-membership.json').read_text())
    holdouts={b['book_key']:b for b in json.loads((OA/'holdout_books.json').read_text())}
    result=[]
    for b in books:
        key=b['book_key'];catpath=f'receipts/catalogues/{key}.json';cat=json.loads((OUT/catpath).read_text())
        secondary=OUT/'receipts/aggregator-fallback'/f'{key}.json'
        fb=json.loads(secondary.read_text()) if secondary.exists() else None
        evidence=fb or cat
        assert evidence.get('title') and evidence.get('year') is not None
        if fb:assert fb['provider_item_link_matches']
        else:assert cat['verified']
        col=b['link_table']['collection_slug'];year=evidence['year']
        flags=[]
        if not b['link_table']:flags.append('not in link table')
        if col!=b['recorded']['collection_slug']:flags.append('collection mismatch')
        if norm(evidence['title'])!=norm(b['recorded']['title']):flags.append('title mismatch')
        if b['recorded']['year'] is not None and year!=b['recorded']['year']:flags.append('year mismatch')
        primary=next((f for f in ['not in link table','collection mismatch','title mismatch','year mismatch'] if f in flags),'consistent')
        md=json.loads(originals[key]['source_metadata']['metadata_json'])
        pipe=b['old_pipeline_metadata'];count_equal=pipe['page_count']==b['actual_download_page_count']
        types=cat.get('type_evidence',[]) if not fb else [dict(field='Open Archives Τύπος',value=fb['fields'].get('Τύπος'))]
        rights=cat.get('rights_evidence',[]) if not fb else [dict(field='Open Archives Δικαιώματα',value=fb['fields'].get('Δικαιώματα'))]
        result.append(dict(schema='oa-rebind-v1',book_id=b['book_id'],book_key=key,collection_slug=col,title=evidence['title'],year=year,decade=year//10*10,date_raw=evidence['date_raw'],date_basis=evidence.get('date_evidence') or 'Fresh EDM Χρονολογία; not repository accession date',pdf_url=b['pdf_url'],canonical_pdf_url=b['canonical_pdf_url'],download_final_url=b['download_final_url'],pdf_sha256=b['pdf_sha256'],pdf_bytes=b['pdf_bytes'],page_count=b['actual_download_page_count'],external_link=b['link_table']['external_link'],edm_url=b['link_table']['edm_url'],type=b['link_table']['type'],type_basis='HF link-table raw type; repository_type_evidence retained separately',repository_type_evidence=types,source='openarchives_'+col,recorded=b['recorded'],classification=primary,classification_flags=flags,link_table_type_mismatch=b['type_mismatch'],decade_mismatch=b['recorded']['decade'] is not None and year//10*10!=b['recorded']['decade'],year_previously_unknown=b['recorded']['year'] is None,decade_previously_unknown=b['recorded']['decade'] is None,status='rebound_repository_verified' if cat.get('verified') else 'rebound_aggregator_provider_unavailable',provider_verified=bool(cat.get('verified')),rights=dict(recorded_licence=b['recorded']['licence'],recorded_metadata_fields={k:v for k,v in md.items() if 'δικαι' in k.lower() or 'rights' in k.lower()},fresh_evidence=rights,apply_licence_automatically=False),pipeline_metadata=dict(recorded=pipe,ocr_success=dict(used_for_selection=True,binding='unresolved',reason='No old source-PDF hash or nonempty document URL binds this flag to the downloaded bytes; fresh page reads do not prove old OCR success.'),page_count=dict(used_for_selection=True,binding='count_corroborated_identity_unproven' if count_equal else 'contradicted_by_downloaded_pdf',recorded=pipe['page_count'],downloaded=b['actual_download_page_count']),polytonic_ratio=dict(used_for_selection=False,binding='unresolved',reason='Retained field; not a wave-4 base filter or type/decade stratum. No hash-bound old text identifies its document.')),admitted_lines=counts[key],declared_holdout_split=holdouts.get(key,{}).get('split'),evidence=dict(hf='receipts/hf-link-table.json',link_table_matches=b['all_link_table_matches'],final_endpoint_in_link_table=bool(b['download_final_url_matches']),download_chains='receipts/download-chains.json',provider_catalogue=catpath,secondary_catalogue=str(secondary.relative_to(OUT)) if fb else None,provider_error=cat.get('error')),apply=dict(preserve_book_id=True,preserve_book_key=True,preserve_line_ids=True,preserve_split=True,preserve_images_and_labels=True,recompute_pipeline_metadata=False)))
    with (OUT/'rebind.jsonl').open('w') as f:
        for row in sorted(result,key=lambda r:r['book_id']):f.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+'\n')
    def group(pred):
        rs=[r for r in result if pred(r)]
        return dict(books=len(rs),v1={s:dict(books=sum(counts[r['book_key']]['v1'].get(s,0)>0 for r in rs),lines=sum(counts[r['book_key']]['v1'].get(s,0) for r in rs)) for s in SPLITS},v2={s:dict(books=sum(counts[r['book_key']]['v2'].get(s,0)>0 for r in rs),lines=sum(counts[r['book_key']]['v2'].get(s,0) for r in rs)) for s in SPLITS})
    primary={c:group(lambda r,c=c:r['classification']==c) for c in ['consistent','collection mismatch','title mismatch','year mismatch','not in link table']}
    overlap={c:group(lambda r,c=c:c in r['classification_flags']) for c in ['collection mismatch','title mismatch','year mismatch','not in link table']}
    overlap['type mismatch (HF normalized)']=group(lambda r:r['link_table_type_mismatch'])
    overlap['decade mismatch']=group(lambda r:r['decade_mismatch'])
    affected=group(lambda r:bool(r['classification_flags']));total=group(lambda r:True)
    seed=20261016;consistent=sorted(r['book_key'] for r in result if r['classification']=='consistent');sample=random.Random(seed).sample(consistent,min(20,len(consistent)))
    write('receipts/control-sample.json',dict(seed=seed,method='random.Random(seed).sample(sorted(final consistent book keys), min(20, population))',requested=20,eligible=len(consistent),selected=sample,reason='No consistent books remain after census verification; all 89 were attempted. The nine collection-only-consistent Dione books received secondary EDM checks.'))
    summaries=dict(wave4_books=len(result),primary_classes=primary,overlapping_fields=overlap,total=total,affected=affected,declared_holdouts=dict(dev=sum(r['declared_holdout_split']=='dev' for r in result),test=sum(r['declared_holdout_split']=='test' for r in result)),test_books_affected=sum(r['declared_holdout_split']=='test' and bool(r['classification_flags']) for r in result),provider_verified=sum(r['provider_verified'] for r in result),secondary_verified=sum(not r['provider_verified'] for r in result),old_collections=dict(collections.Counter(r['recorded']['collection_slug'] for r in result)),fresh_collections=dict(collections.Counter(r['collection_slug'] for r in result)),old_decades=dict(sorted(collections.Counter(str(r['recorded']['decade']) for r in result).items())),fresh_decades=dict(sorted(collections.Counter(r['decade'] for r in result).items())),pipeline_page_count_equal=sum(r['pipeline_metadata']['page_count']['binding']=='count_corroborated_identity_unproven' for r in result),pipeline_page_count_contradicted=sum(r['pipeline_metadata']['page_count']['binding']=='contradicted_by_downloaded_pdf' for r in result))
    write('receipts/counts.json',summaries)
    # Contribution to source-cap reporting; this deliberately does not relabel other waves.
    contribution={}
    for version in ['v1','v2']:
        for split in SPLITS:
            contribution[version+'_'+split]=dict(old=dict(sorted(collections.Counter({slug:sum(r['admitted_lines'][version].get(split,0) for r in result if r['recorded']['collection_slug']==slug) for slug in summaries['old_collections']}).items())),fresh=dict(sorted(collections.Counter({slug:sum(r['admitted_lines'][version].get(split,0) for r in result if r['collection_slug']==slug) for slug in summaries['fresh_collections']}).items())))
    write('receipts/source-contributions.json',contribution)
    def table(groups):
        lines=['| Class | Downloaded books | v1 train | v1 dev | v1 test | v2 train | v2 dev | v2 test |','|---|---:|---:|---:|---:|---:|---:|---:|']
        for label,g in groups.items():lines.append('| '+label+' | '+str(g['books'])+' | '+' | '.join(f"{g[v][s]['books']} / {g[v][s]['lines']:,}" for v in ['v1','v2'] for s in SPLITS)+' |')
        return '\n'.join(lines)
    linesaffected=affected['v2'];last=f"O1: done | wave4_books: {len(result)} consistent: {primary['consistent']['books']} mismatched: {affected['books']} (collection {overlap['collection mismatch']['books']} title {overlap['title mismatch']['books']} year {overlap['year mismatch']['books']}) not_in_table: {primary['not in link table']['books']} | lines affected train/dev/test v2: {linesaffected['train']['lines']}/{linesaffected['dev']['lines']}/{linesaffected['test']['lines']} | test_books_affected: {summaries['test_books_affected']}"
    report=f'''# O1 — Wave-4 Open Archives metadata rebinding

The 15 October wave-4 collection contains **89 downloaded books; all 89 carry incorrect titles, 80 carry incorrect collections, and {overlap['year mismatch']['books']} carry incorrect publication years**. Exact canonical acquisition URLs match the revision-pinned HF table for all 89; their recorded SHA-256/bytes agree with the original download receipts and acquisitions. Fresh repository item pages confirm title, date and an offered attachment in the original download chain for **80/89**. Dione's robots endpoint resets connections: its nine provider pages were not fetched after failed preflight; fresh official Open Archives EDM pages, each matching the exact Dione item URL, establish their title/date contradictions as **secondary evidence**, with provider verification still pending. The affected metadata reaches **25,604 v1 lines and 25,372 v2 lines**. This finding concerns metadata attached to the downloaded page images and read labels; it does not establish an image or label defect. No manifest, image, label, split, account or external dataset was changed; no paid services or remote compute were used.

## Counts and scope

Wave 4 is exactly the 89 entries in `openarchives/books.json`, independently equal to the successful acquisitions among 173 attempts (84 dead links). Wave 5 and later Open Archives acquisitions are outside this correction population. Source files are read-only and fingerprinted in [input-files.json](receipts/input-files.json) and [collection-input-files.json](receipts/collection-input-files.json).

Each split cell is **books with admitted lines / admitted lines**, counted from that version's split-specific `import_real_*.jsonl` filename. The row's internal `split: reserved` is not treated as a fourth split. Ordered crop/label/source/year/class tuples match the corresponding manifests for all six splits: [checks](receipts/manifest-import-checks.json). A downloaded test holdout (`b6ee0fe8`) has no admitted lines; hence 89 downloaded books but 88 represented books, with 14 represented test books. All **15 declared test holdout identities** and all five dev holdout identities are affected. There is no split movement in this proposal.

Mutually exclusive primary classes use precedence: not in table → collection → title → year → consistent.

{table(primary|{'Any metadata mismatch':affected,'All wave-4 books':total})}

Field mismatches overlap; do not add these rows. Year mismatch means a conflicting known old year; one additional old unknown year (`d9880347`) is resolved to 2020 and is not counted as a contradiction. Year comparison uses publication/work dates, excluding repository accession dates; ELSTAT's reference year 1964 is separately retained from its publication year **1967**.

{table(overlap)}

The requested seeded control uses seed **{seed}**. There are **zero final consistent books**, so a 20-book sample cannot be drawn; the audit attempted the entire 89-book census and checked all nine initially collection-consistent books. See [control-sample.json](receipts/control-sample.json). Type comparison preserves raw HF values as well as normalized old/new categories; the requested five primary classes have no separate type class.

## Identity and evidence

HF dataset `glossAPI/openarchives.gr`, revision `6cef86201403003d26aa628099af93c3171aa7be`, `data/external_pdfs.parquet`, SHA-256 `ab2397b75a04382e8bd1ccda462c21c91e3ee0e79a6fbc7e186d59f52973262d`; the read-only F1-GR copy was rehashed locally. Both published and refined PDF fields were searched. All matches have one unambiguous collection/item/type tuple. Canonicalization decodes HTML entities/unreserved escapes and Unicode NFC, retains query strings and reserved escapes, and does not equate unrelated handles, basenames, schemes or arbitrary redirect destinations. See [initial bindings](receipts/initial-bindings.json), [table receipt](receipts/hf-link-table.json), and [original download chains](receipts/download-chains.json).

**39 final response URLs are absent as literal canonical endpoints from the link table.** These are not silently normalized into catalogue URLs: the original HTTP ledger records complete 301/302 chains from the table's exact acquisition URL to the final 200 response and its identical saved PDF hash. `not in link table = 0` above means no acquisition lacks an exact table URL and a complete hash-bound download chain; the raw final-endpoint absence is separately retained for every book in `rebind.jsonl`. 50 final endpoints match directly. The PDF hashes are recorded evidence from 15 October, not a claim to have re-downloaded today's PDFs; originals were removed by the earlier pipeline's recorded retention policy.

The 11 old collection labels resolve to 10 collections: `{summaries['fresh_collections']}`. Of the originally collection-consistent Dione books, `8ba4e15e` was recorded as *Επετηρίς ακαδημαϊκού έτους 1970–1971* (1971), but its exact item `unipi/7438` describes *Ποιότητα της προσφερόμενης μεταφορικής υπηρεσίας. Η ικανοποίηση των τουριστών από τις εταιρείες ενοικιάσεως αυτοκινήτων στην Ελλάδα* (2014). `46380632` was recorded as *Περί σακχάρου και σακχαρίνης* (1890, ntua), while its IHU item and offered exact attachment describe *Θέρμανση και δροσισμός κατοικίας με χρήση αβαθούς γεωθερμικής ενέργειας και ενδοδαπέδιας θέρμανσης* (2012, rep_ihu). All individual field values and evidence paths are in [rebind.jsonl](rebind.jsonl).

## Old pipeline fields

`ocr_success == true` and `page_count` 20–600 were selection gates in `base_filters`; type × decade and the metadata collection supplied the draw strata/cap. `polytonic_ratio` was retained but was **not** a wave-4 base filter or draw stratum. The old pipeline document URL is empty in all 89 books and no old source-PDF digest binds these fields to the downloaded bytes. Therefore old OCR success and polytonic-ratio ownership remain **unresolved**, not declared correct merely because new page reads succeeded. These fields cannot certify physical scan construction.

Old pipeline page count agrees with the actual downloaded PDF count for **82/89**, which corroborates the number but does not prove pipeline identity; it contradicts the physical count for **7/89**: `8ba4e15e` 114→150, `520de75a` 62→134, `c82ac45f` 74→92, `a181595d` 122→92, `0b63328a` 179→175, `6797597d` 104→73, `ab5e8994` 70→162. Do not transfer these old scores to a corrected record as verified; use the download-bound physical `page_count` supplied here. No new OCR or polytonic-ratio calculation was run. Per-field binding states and the original values are retained for every row.

## Downstream effects

- **Decade/period tags:** {overlap['decade mismatch']['books']} books have a different decade; {overlap['year mismatch']['books']} have a conflicting known year; one additional previously unknown year/decade is now 2020. Rebuild period reports and sampling summaries from corrected publication/work dates. Old book decades `{summaries['old_decades']}` become `{summaries['fresh_decades']}`; equal-year coincidences do not rescue wrong titles.
- **Source caps:** 80 book source labels change. The recorded per-repository book cap was 10, but actual downloaded recipients are Pergamos 18, Hellanicus 17 and IHU 13. Thus the old selection cap/coverage claim is invalid for those three recipients. Collection train source-share reports also need recomputation (`source_caps` groups by script class and normalized source, flagging >40%); [source-contributions.json](receipts/source-contributions.json) gives wave-4 deltas, not a claim that the complete multi-wave collection now passes or fails its cap.
- **Holdout/test-book identity:** five dev and 15 declared test books have misleading names/dates/attribution. The stored crop/book keys still identify the downloaded objects; retaining the existing split does not itself demonstrate or disprove cross-edition leakage. The one empty test book remains visible in the holdout correction.
- **Edition dedupe:** the legacy book digest includes the **old collection label plus acquisition URL**, so it is not an edition identifier. Preserve IDs as aliases during rebinding. Recheck exact PDF hashes, canonical URLs, provider item identifiers and edition-level evidence across other waves/splits before changing dedupe claims. No new cross-edition leakage claim is made by this audit.
- **Rights records:** generic `per-repository (recorded, unverified)` remains unverified, and source-metadata rights may describe the unrelated title. Keep original strings and fresh provider/secondary rights evidence separately. Review item-specific rights before attaching a corrected attribution/licence; the table does not automatically grant or apply a reuse licence.

## Apply procedure

1. Verify all input fingerprints and the pinned table hash. Read `rebind.jsonl` as a proposal keyed by **both** legacy `book_id` and `book_key`; require the expected old acquisition URL, PDF hash and recorded metadata before updating any row. Preserve the 39 explicit redirect chains. Provider-verified rows have status `rebound_repository_verified`; the nine Dione rows have status `rebound_aggregator_provider_unavailable` and require the data side to accept the secondary evidence or defer those fields until provider verification succeeds.
2. In a separately versioned data change, replace collection/source, title/attribution, publication year/decade and catalogue/EDM links using the supplied evidence. Preserve legacy book/line IDs, PDF/page/crop hashes, crop paths, labels, admission decisions and current split assignments. Keep raw HF type and repository type evidence separately; never infer a bibliographic type from a webpage's `og:type=website` or a PDF MIME type. Do not promote unresolved old OCR/ratio fields.
3. Propagate by legacy book identity into the book/holdout records, page metadata, wave records/admitted rows, collection admitted rows, v1/v2 manifests/imports, provenance/source summaries, and human-facing attributions. This audit applies none of these changes.
4. Rebuild decade/source-cap/rights and edition/holdout reports, comparing line membership, split assignment, crop bytes and label bytes before/after. Expected existing v1 exposure is **19,795 / 1,083 / 4,726**; v2 is **19,625 / 1,067 / 4,680**. The wave admitted file has 25,606 lines; two train labels were removed during collection admission, explaining v1's 25,604. Metadata rebinding should add/drop/move/relabel **zero** lines; any different data change needs its own review.

## Acquisition protocol and reproducibility

Fresh metadata reads used contact User-Agent `greek-ocr-research/0.1 (foivos.karounos@gmail.com)`, host start spacing ≥1 second (configured 1.1-second margin), manual redirect handling with destination robots checks, and bounded 8-MB/35-second responses. No PDFs were fetched in this audit. Dione's failed curl/requests/TLS-compatibility/HTTP robots probes are retained; no page request followed unavailable robots. The official EDM fallback uses its own allowed robots policy. Bodies, headers, exact timestamps, hashes and policy receipts are retained in [receipts](receipts/). [validation.json](receipts/validation.json) records the final protocol/data checks. `audit.py` builds initial bindings from read-only sources; `fetch_catalogues.py` performs the bounded reads; `fallback.py` handles the labelled EDM fallback; `analyse.py` verifies download chains and split exposure; `finalize.py` builds this proposal. Outputs stay under this directory.

**No worker commit was created.** `git add` failed because the shared worktree `index.lock` is outside managed writable roots; see [commit-status.json](receipts/commit-status.json). From the repository root, run `python3 docs/harvest/oa_rebind_v1/commit_o1.py` for the guarded owner-side commit. It validates the source-bound output receipt, stages only this output directory and refuses unrelated staged paths; it does not push.

{last}
'''
    (OUT/'FINDING.md').write_text(report)
    write('receipts/final-line.json',dict(line=last))
    print(last)

if __name__=='__main__':main()
