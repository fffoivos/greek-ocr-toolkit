"""Evidence-linked reports and correction lists. Applies no data decisions."""
from __future__ import annotations
import sys
sys.dont_write_bytecode=True
import collections, datetime, itertools, json
from common import *

def table(headers,rows):
    def cell(x):return str(x).replace('|','\\|').replace('\r','').replace('\n','<br>')
    return '\n'.join(['| '+' | '.join(map(cell,headers))+' |','| '+' | '.join('---' for _ in headers)+' |']+['| '+' | '.join(map(cell,r))+' |' for r in rows])+'\n'

def main():
    summary=json.loads((OUT/'duplicate_summary.json').read_text());groups=list(jsonl(OUT/'duplicates.jsonl'))
    books={(b['wave'],b['book_key']):b for b in jsonl(OUT/'books.jsonl')}
    rb=list(jsonl(O1/'rebind.jsonl'));release=json.loads((OUT/'v2_meta1/receipt.json').read_text())
    page=json.loads((OUT/'receipts/page-collision-readback.json').read_text())
    items=json.loads((OUT/'receipts/provider-item-summary.json').read_text())
    itemby={r['identifier']:r for r in items}
    decisions=[]
    for g in groups:
        if g['key_type']=='title_year':
            evidence=[]
            for m in g['members']:
                if m['book_id'] in itemby:
                    it=itemby[m['book_id']]
                    evidence.append(dict(book_key=m['book_key'],provider_item_url=it['url'],provider_volume=it['metadata']['Volume'],catalogue_date=it['metadata']['Publication date'],receipt='receipts/provider_item_pages/'+it['identifier']+'.json',body=it['body']))
            if evidence:
                assert len(evidence)==len(g['members'])
                assert len({e['provider_volume'] for e in evidence})==len(evidence)
                decisions.append(dict(group=g['group'],key_type=g['key_type'],decision='distinct_bound_volumes_same_serial_catalogue_title_and_date',duplicate_edition_proven=False,evidence=evidence,applied=False))
        if g['key_type']=='page_image_sha256':
            p=next(r for r in page['groups'] if r['group']==g['group'])
            decisions.append(dict(group=g['group'],key_type=g['key_type'],decision='exact_scanned_page_shared_across_provider_books',duplicate_edition_proven=False,native_image_files_rehashed=True,actual_colliding_page_lines=p['actual_colliding_page_lines'],admitted_collision_cross_split=p['admitted_collision_cross_split'],admitted_collision_twice_train=p['admitted_collision_twice_train'],applied=False))
        if g['members'][0]['book_key']=='4c207e1e':
            decisions.append(dict(group=g['group'],key_type=g['key_type'],decision='same_book_page_split_in_v1_already_whole_book_train_in_input_v2',evidence=[str(COL/'split_repairs.json'),str(COL/'v2/split_moves_v2.json')],applied=False))
    write_jsonl('duplicate_adjudications.jsonl',decisions)
    union={}
    for flag in ['cross_split','train_test','train_dev','dev_test','within_train','within_dev','within_test']:
        selected=[g for g in groups if any(g['versions'][v][flag] for v in ['v1','v2'])]
        ids={(m['wave'],m['book_key']) for g in selected for m in g['members']}
        union[flag]=dict(groups=len(selected),group_ids=[g['group'] for g in selected],test_books=sorted(f'{w}:{k}' for w,k in ids if any(books[w,k]['lines'][v].get('test',0) for v in ['v1','v2'])),lines_by_version={v:{s:sum(books[i]['lines'][v].get(s,0) for i in ids) for s in SPLITS} for v in ['v1','v2']})
    summary['version_union']=union
    summary['adjudication']=dict(exact_page_hash_groups=7,serial_title_year_groups_distinct_bound_volumes=2,legacy_page_split_key_groups=3,admitted_page_cross_split_groups={v:sum(p['admitted_collision_cross_split'][v] for p in page['groups']) for v in ['v1','v2']},admitted_page_twice_train_groups={v:sum(p['admitted_collision_twice_train'][v] for p in page['groups']) for v in ['v1','v2']},provider_item_requests=len(items),provider_item_statuses=dict(collections.Counter(str(r.get('status')) for r in items)))
    summary['network_requests']=len(items)
    dump('duplicate_summary.json',summary)
    testbooks=[r for r in rb if r['declared_holdout_split']=='test'];assert len(testbooks)==15
    write_jsonl('wave4_test_books.jsonl',[dict(book_id=r['book_id'],book_key=r['book_key'],true_title=r['title'],publication_year=r['year'],collection_slug=r['collection_slug'],declared_split='test',admitted_lines=r['admitted_lines']['v2'],provider_id=r['external_link'],edm_url=r['edm_url'],pdf_sha256=r['pdf_sha256'],exact_duplicate_groups=[],possible_groups=[]) for r in testbooks])
    # Source-cap corrections are a ledger, never an admission/re-cap operation.
    names=sorted({r['recorded']['collection_slug'] for r in rb}|{r['collection_slug'] for r in rb})
    cap=[]
    for name in names:
        old=[r for r in rb if r['recorded']['collection_slug']==name];new=[r for r in rb if r['collection_slug']==name]
        rec=dict(repository=name,old_downloaded_books=len(old),true_downloaded_books=len(new),old_admitted_books={s:sum(r['admitted_lines']['v2'].get(s,0)>0 for r in old) for s in SPLITS},true_admitted_books={s:sum(r['admitted_lines']['v2'].get(s,0)>0 for r in new) for s in SPLITS},versions={})
        for v in ['v1','v2']:
            ot=sum(r['admitted_lines'][v].get('train',0) for r in old);nt=sum(r['admitted_lines'][v].get('train',0) for r in new)
            wt=sum(r['admitted_lines'][v].get('train',0) for r in rb)
            ct=sum(b['lines'][v].get('train',0) for b in books.values())
            rec['versions'][v]=dict(old_train_lines=ot,true_train_lines=nt,wave4_train_denominator=wt,collection_train_denominator=ct,old_wave4_train_share_percent=ot/wt*100,true_wave4_train_share_percent=nt/wt*100,wave4_train_share_delta_pp=(nt-ot)/wt*100,collection_train_share_delta_pp=(nt-ot)/ct*100)
        cap.append(rec)
    dump('source_cap_corrections.json',dict(applied=False,reason='Metadata correction only. No source-cap recomputation, re-admission or resampling.',repositories=cap))
    rights=[]
    for r in rb:
        old=r['rights']['recorded_metadata_fields'];fresh=r['rights']['fresh_evidence']
        rights.append(dict(book_id=r['book_id'],book_key=r['book_key'],old_collection=r['recorded']['collection_slug'],true_collection=r['collection_slug'],recorded_licence_unchanged=r['rights']['recorded_licence'],old_item_rights_fields=old,true_item_rights_evidence=fresh,old_strings=list(old.values()),true_strings=[e.get('value') for e in fresh],status='wrong_item_bound_specific_rights' if old else 'generic_unverified_licence_only_no_old_specific_rights',true_rights_status='evidence_present' if any(e.get('value') for e in fresh) else 'not_established',provider_verified=r['provider_verified'],admitted_lines_v2=r['admitted_lines']['v2'],applied=False))
    write_jsonl('rights_string_corrections.jsonl',rights)
    corrections=[r for r in rights if r['old_item_rights_fields']]
    cov=summary['coverage']['all_including_empty_wave4_holdout']
    final=(f"O2: done | dup groups cross-split: {union['cross_split']['groups']} (train-test {union['train_test']['groups']} train-dev {union['train_dev']['groups']} dev-test {union['dev_test']['groups']}) within-train: {union['within_train']['groups']} | test books involved: {len(union['cross_split']['test_books'])} | key coverage pdf/provider/title: {cov['percent']['pdf']:.2f}%/{cov['percent']['provider']:.2f}%/{cov['percent']['title']:.2f}% | v2-meta1 rows changed: {release['unique_admitted_rows_changed']} lines added/dropped/moved: 0/0/0 | dione pending: 9")
    dump('receipts/final-line.json',dict(line=final,scope='Distinct exact-key groups active in either v1 or v2; near matches excluded; candidate groups retained even where provider volume evidence rules out duplicate editions; coverage includes the empty wave4 test holdout.'))
    # Full duplicate/edition report, with key counts separated from actual pages.
    d=['# O2 duplicate and edition re-check\n',
       'The corrected **89 wave-4 identities have no cross-split group found by keys PDF SHA256, provider item ID, normalized true title + publication year, or page-image SHA256**, and no within-split doubles or near matches at the specified threshold. All four keys cover 89/89 books, including the declared test holdout with zero admitted lines. All 15 corrected test-book identities are listed in [wave4_test_books.jsonl](wave4_test_books.jsonl).\n',
       'Across all waves there are **12 exact-key groups**: seven page-image hash collisions, two serial-title/year collisions, and three keys identifying the single v1 page-split lexicon. **Seven groups cross splits in v1; four in v2.** These are requested key groups, not seven or four independent duplicate editions. The two serial groups are different bound volumes, as verified on provider item pages. The three train/test page collisions have zero admitted training lines on the colliding pages in both versions. No release or split repair was applied.\n',
       '## Counts by key and version\n',
       'Lines are the union of whole-book admitted lines for members of the selected groups, deduplicated by book within each table row. This measures test-book exposure. It is distinct from the count of lines on the colliding pages shown below. A group can cross more than one split pair. Overlapping keys are not additive.\n']
    rows=[]
    for v in ['v1','v2']:
        for typ,stats in summary['versions'][v].items():
            cross=stats['cross_split'];rows.append([v,typ,cross['groups'],stats['train_test']['groups'],stats['train_dev']['groups'],stats['dev_test']['groups'],stats['within_train']['groups'],stats['within_dev']['groups'],stats['within_test']['groups'],' / '.join(str(cross['lines'][s]) for s in SPLITS),len(cross['test_books'])])
    d.append(table(['Version','Key','Cross-split','Train↔test','Train↔dev','Dev↔test','Within train','Within dev','Within test','Cross-group lines train/dev/test','Test books'],rows))
    d.append('Version-union hand-off counts use distinct group IDs active in **either** version: '+str(union['cross_split']['groups'])+' cross-split groups, '+str(union['within_train']['groups'])+' within-train groups, and '+str(len(union['cross_split']['test_books']))+' test books. They are not the sum of the version rows. The final line counts all requested exact-key candidates, including adjudicated serial-title collisions; it excludes possible matches.\n')
    d.append(table(['Category (either version)','Groups','v1 member lines train/dev/test','v2 member lines train/dev/test','Test books'],[[flag,r['groups'],*[' / '.join(str(r['lines_by_version'][v][s]) for s in SPLITS) for v in ['v1','v2']],len(r['test_books'])] for flag,r in union.items()]))
    d.append('## Every exact-key group\n')
    d.append(table(['Group','Key type','Book members','v1 splits','v2 splits','Meaning'],[[g['group'],g['key_type'],', '.join(m['wave']+':'+m['book_key'] for m in g['members']),', '.join(s for s in SPLITS if g['versions']['v1']['lines'][s]),', '.join(s for s in SPLITS if g['versions']['v2']['lines'][s]),next(r['decision'] for r in decisions if r['group']==g['group'])] for g in groups]))
    d.append('Full keys, legacy book IDs, true/recorded titles and years, wave, splits, per-version lines and page occurrences are in [duplicates.jsonl](duplicates.jsonl). [duplicate_adjudications.jsonl](duplicate_adjudications.jsonl) preserves decisions and source evidence without modifying input data.\n')
    d.append('## Exact scanned-page collisions\n')
    d.append('All 14 native image files were rehashed and agree with the saved page-image keys. One D00001 image was visually inspected: printed page 10 contains the end of one session and the start of session Δ on 16 November 1843. It is a text-bearing boundary overlap. Different parliamentary catalogue records can share a boundary page without representing the same complete book.\n')
    d.append(table(['Group','Pages (book:page)','v1 actual page lines train/dev/test','v2 actual page lines train/dev/test','Admitted page cross-split v1/v2'],[[p['group'],', '.join(q['book_key']+':'+str(q['page']) for g in groups if g['group']==p['group'] for q in g['page_occurrences']),*[' / '.join(str(p['actual_colliding_page_lines'][v][s]) for s in SPLITS) for v in ['v1','v2']],str(p['admitted_collision_cross_split']['v1'])+' / '+str(p['admitted_collision_cross_split']['v2'])] for p in page['groups']]))
    d.append('Four within-train page groups have both copies represented by admitted lines in v1; **zero** have both copies represented in v2. The seven shared page files remain real source collisions and are retained in the requested book-level report. Hashes are of encoded native image files; differently encoded, cropped or rescaled versions of the same scan may evade this check.\n')
    d.append('## Serial title/year candidates\n')
    d.append('The provider publication dates are serial-level dates, not sufficient bound-volume identities. Provider item pages confirm the following disjoint volume ranges. PDF hashes and provider item IDs are distinct. No claim of scan identity follows from the title/year collision.\n')
    d.append(table(['Group','Book','Provider volume','Catalogue date','Split v2','Provider item'],[[r['group'],e['book_key'],e['provider_volume'],e['catalogue_date'],', '.join(books['cyrillic',e['book_key']]['split']['v2']),'[item]('+e['provider_item_url']+')'] for r in decisions if r['decision']=='distinct_bound_volumes_same_serial_catalogue_title_and_date' for e in r['evidence']]))
    d.append('## Key coverage and matching rules\n')
    d.append(table(['Population','Books','PDF hash','Whole PDF hash','Provider item','Title + year','Page image'],[[name,c['books'],*[f"{c['counts'][k]}/{c['books']} ({c['percent'][k]:.2f}%)" for k in ['pdf','full_pdf','provider','title','page_image']]] for name,c in summary['coverage'].items()]))
    d.append('The final-line denominator is 558: the 557-book union of v1/v2 plus the empty declared wave-4 test holdout. All have page hashes, so all qualify for the requested audit. PDF coverage includes Anemi per-page PDF derivatives (218 books); it must not be read as whole-book PDF coverage. Thirty Wikisource books have no PDF hash. Provider aliases use exact item URLs, handles (repository-qualified for the reused placeholder prefix `123456789`), EDM IDs, IA identifiers, and Wikisource/Commons scan IDs. Pergamos numeric and `uoadl:` item aliases are normalized. URL schemes and the handle resolver are unified only for these defined identity forms; query parameters and item namespaces are retained.\n')
    d.append('True titles are NFC/casefolded, decomposed to strip combining accents for matching only, and non-alphanumeric punctuation is collapsed to whitespace. Title keys require an integer publication year. The stored title spelling is unchanged by matching. Thirty-five mixed-wave Open Archives titles are excluded because their join is unverified; nine other books lack a year. Those books remain covered by hashes and provider IDs. The mixed OA provider IDs were rebound for audit matching only from the same pinned PDF-to-item table; no mixed-wave metadata is released here. Cross-wave matching was enabled globally, and **zero exact cross-wave groups** were found.\n')
    d.append('Near matches are in [possible.jsonl](possible.jsonl): **37** possible pairs, with full members, split lines and scores; none involves wave 4. The threshold is `SequenceMatcher(autojunk=False).ratio() >= 0.9` on normalized `title | year`. Exact title/year groups are excluded from that list; title-only similarity and year equality are also shown. Similar session titles on different dates remain possible pairs, not inferred duplicate editions. No external OCR, downloads of PDFs, or perceptual image matching was performed.\n')
    d.append('Inputs and their unchanged final fingerprints are bound in [duplicate-inputs.json](receipts/duplicate-inputs.json); exact collision-file readback is in [page-collision-readback.json](receipts/page-collision-readback.json). Six bounded Internet Archive provider item pages were read (all HTTP 200), with no redirects followed, and are archived under [provider_item_pages](receipts/provider_item_pages/). No other network endpoint or paid service was used.\n')
    (OUT/'DUPLICATE_REPORT.md').write_text('\n'.join(d))
    note=['# Collection v2-meta1 — metadata-only release\n',
      '**25,372 active line records across 88 represented wave-4 books receive corrected metadata. Zero lines were added, dropped, moved or relabelled.** The 89-book sidecar also corrects the declared test holdout with zero admitted lines. This release applies the O1 proposal from commit `c22d7a78` to copies of the 14 existing `collection/v2/` files. Main and funnel worktrees were read-only; no collection rebuild, source cap, rights decision, label cleaning or admission was rerun.\n',
      '## What changed\n',
      'Existing source/source_dataset, attribution, publication year/decade and catalogue fields are replaced where present. The original trainer schemas omit book title, collection slug and EDM URL; those complete corrected fields are published in the **89-row auxiliary** [book_metadata.jsonl](v2_meta1/book_metadata.jsonl). It adds no training lines. Existing field sets are retained except the explicitly requested `metadata_status: pending_provider_verification` on Dione line metadata. No old OCR-success, type, ratio, licence or rights field is promoted or replaced.\n',
      table(['Active admitted field','Train changed','Dev changed','Test changed','Total'],[[field,*[counts.get(s,0) for s in SPLITS],sum(counts.values())] for field,counts in release['admitted_rows_changed_by_field_and_split'].items()]),
      'Book-level corrections: title 89/89; collection/source 80/89; year 87/89 (86 contradictions plus one previously unknown year resolved); decade 66/89 (65 contradictions plus the same previously unknown decade resolved). Catalogue item URLs were already correct and remain unchanged; all 89 EDM links are retained from the pinned identity evidence in the sidecar. Raw bibliographic type/evidence remain in O1 and are not applied.\n',
      'The sidecar comparison below is against the original 89 source-book records. Book split counts include the empty declared test holdout. EDM links are newly exposed in this auxiliary schema, not added training lines.\n',
      table(['Auxiliary book field','Train books','Dev books','Test books','Total changed/added metadata'],[[field,*[counts.get(s,0) for s in SPLITS],sum(counts.values())] for field,counts in release['book_metadata_comparison']['changed_fields_by_book_split'].items()]),
      table(['Split','Active rows before','Active rows after','Rows with metadata changed','Added','Dropped','Moved'],[[s,release['admitted_split_counts_before'][s],release['admitted_split_counts_after'][s],sum(r['admitted_lines']['v2'].get(s,0) for r in rb),0,0,0] for s in SPLITS]),
      '## File receipt and immutable data\n',
      table(['File','Logical rows before/after','Rows with metadata changed','(id, crop hash, label) SHA256 equal','ID sets/order/multisets equal','Added/dropped/moved'],[[r['file'],str(r['before']['line_count'])+' / '+str(r['after']['line_count']),r['changed_metadata_rows'],r['before']['id_crop_hash_label_sha256']==r['after']['id_crop_hash_label_sha256'],r['line_id_set_equal'] and r['line_id_order_equal'] and r['line_id_multiset_equal'],'0 / 0 / 0'] for r in release['files']]),
      'The [receipt](v2_meta1/receipt.json) gives full file SHA256/bytes, physical and logical line counts, before/after ID sets and multiplicities, split counts, immutable JSON-token hashes, ordered tuple hashes and per-field/per-split changes. IDs and crop hashes missing from manifest/import views are joined by the exact original crop path or line ID to the admitted record, with v1 used only for historical dropped/relabel/move rows. Every tuple has a crop hash. Original non-metadata JSON token spelling is preserved, including all labels and split decisions. The active admitted rows are counted once here; repeated import/manifest exports are not additional training rows. The 232 historical dropped wave-4 rows also receive metadata updates without being admitted.\n',
      '`CLEAN_REPORT.md`, `validation_v2.json`, split-move and relabel/rejection decision records are retained as historical v2 evidence. Their old artifact hashes refer to input v2, not v2-meta1; the new receipt binds the release files. A new independent readback is reported in [validation.json](receipts/validation.json).\n',
      '## Nine Dione books pending provider verification\n',
      'The fields are updated from the exact-item-linked official aggregator evidence accepted for this release. All nine auxiliary book rows and their 2,828 active line occurrences carry `metadata_status: pending_provider_verification`. The provider remains unverified; these are not counted as provider-verified titles. No new Dione request was made.\n',
      table(['Book key','True title','Publication year','Train/dev/test active lines','Provider item','EDM'],[[r['book_key'],r['title'],r['year'],' / '.join(str(r['admitted_lines']['v2'].get(s,0)) for s in SPLITS),'[item]('+r['external_link']+')','[EDM]('+r['edm_url']+')'] for r in rb if not r['provider_verified']]),
      '## Source-cap corrections — recorded, not applied\n',
      'These counts correct the repository attribution of all 89 downloaded wave-4 books. Train shares below use the unchanged 19,625 wave-4 train lines; the final column uses all 214,436 v2 train lines. Deltas are percentage points. [source_cap_corrections.json](source_cap_corrections.json) also records admitted book counts per split and the v1 comparison. No cap is reapplied and no line membership changes.\n',
      table(['Repository','Old/true downloaded books','Old/true train books','Old/true train lines','Old/true wave-4 train share','Δ wave-4 pp','Δ collection pp'],[[r['repository'],str(r['old_downloaded_books'])+' / '+str(r['true_downloaded_books']),str(r['old_admitted_books']['train'])+' / '+str(r['true_admitted_books']['train']),str(r['versions']['v2']['old_train_lines'])+' / '+str(r['versions']['v2']['true_train_lines']),f"{r['versions']['v2']['old_wave4_train_share_percent']:.3f}% / {r['versions']['v2']['true_wave4_train_share_percent']:.3f}%",f"{r['versions']['v2']['wave4_train_share_delta_pp']:+.3f}",f"{r['versions']['v2']['collection_train_share_delta_pp']:+.3f}"] for r in cap]),
      '## Rights-string corrections — recorded, not applied\n',
      f"**{len(corrections)} books** carry item-specific rights text from the wrong metadata binding. Their exact old raw strings and the true-item evidence strings (including unavailable/null evidence) are retained in [rights_string_corrections.jsonl](rights_string_corrections.jsonl). All 89 book rows are retained in that ledger; the other {89-len(corrections)} have only the generic recorded unverified licence, with no old item-specific rights string. Equal-looking licence families do not establish that the old text belonged to the downloaded item. No recorded rights/licence string is changed in any release file. Missing new rights evidence is an unresolved correction, not an inferred permission.\n",
      table(['Book','Old repository → true','Exact old rights string(s)','True-item rights evidence string(s)','Evidence'],[[r['book_key'],r['old_collection']+' → '+r['true_collection'],json.dumps(r['old_strings'],ensure_ascii=False),json.dumps(r['true_strings'],ensure_ascii=False),('provider' if r['provider_verified'] else 'aggregator; provider pending')+'; '+r['true_rights_status']] for r in corrections]),
      '## Duplicate/edition re-check and release implications\n',
      'The [duplicate report](DUPLICATE_REPORT.md) covers the 558 audit identities across all eight waves and both versions. Wave 4 has no cross-split or within-split key group, with 100% coverage of PDF/provider/title keys. The full audit has 12 exact-key groups, seven crossing splits in either version (four in v2); all are retained in [duplicates.jsonl](duplicates.jsonl). Two title/year groups are disjoint bound volumes according to six fresh provider item pages. Three parliamentary page-hash groups link train and test books, but the matching train pages have zero admitted lines. The v1 lexicon page split is already whole-book train in input v2. Thirty-seven near-title/year pairs are separately marked possible. This is a metadata release, with all such findings recorded and no split or deduplication decisions applied.\n',
      'The final-line duplicate counts use distinct exact-key groups active in **either v1 or v2**, including the adjudicated title/year candidates; the coverage denominator is 558 including the empty wave-4 holdout. Test-book count is the union of books in those cross-split groups. This avoids confusing the requested key-group census with independent duplicate editions or with admitted-page label leakage.\n',
      '## Reproduction and hand-off\n',
      'From the worktree root: `python3 docs/harvest/oa_rebind_v1/o2/audit_duplicates.py`, then `build_release.py`, `check_candidates.py`, `finalize_o2.py`, and `validate_release.py` from the same directory. The candidate check reuses archived provider pages on rerun. All writes are constrained to this O2 directory; inputs are rehashed before and after. Six provider item pages were the only network requests; no paid API, model generation, remote compute or PDF transfer was used.\n',
      'No worker commit was created: the single `git add -- docs/harvest/oa_rebind_v1/o2` attempt failed with `Operation not permitted` while creating the main repository shared-worktree `index.lock`, outside the managed writable roots. The exact error is in [commit-status.json](receipts/commit-status.json). The source-bound owner helper is `python3 docs/harvest/oa_rebind_v1/o2/commit_o2.py` (use `--check` for validation only); it refuses drift, unrelated staged paths, unexpected output files and symlinks, and never pushes.\n',
      final]
    (OUT/'RELEASE_NOTE.md').write_text('\n'.join(note)+'\n')
    dump('receipts/run-summary.json',dict(scope='O2',version_union=union,final_line=final,rights_specific_corrections=len(corrections),source_caps_applied=False,rights_applied=False,network_requests=len(items),network_kind='provider item pages only',spend=0,release_rows_changed=release['unique_admitted_rows_changed']))
    print(final)

if __name__=='__main__':main()
