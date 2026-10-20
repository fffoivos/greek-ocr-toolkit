# B.a — source populations, orthography and split custody

Documentation, 19 October 2026. Counts below identify their layer: raw Google page lines, original historical admitted crops, cleaned-v2 membership, or frozen collect-v3 snapshot rows. They are not additive across layers. Scripts and reports are repository-relative. Current eligibility belongs to [B.c](../c_pipeline/README.md).

## Original waves and cleaned v2

The raw/historical columns come from each wave's `read_summary.json` and `admission_summary.json`; the v2 column comes from `docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261018b.md`. These v2 wave counts sum to 271,987. Admission rules in these historical reports are not the current gate/segmentation rules.

| Source/wave; collector | Pages / Google lines | Historical admitted / cleaned-v2 lines | Script/orthography and split policy |
|---|---:|---:|---|
| Anemi round1; `scripts/harvest/{round1,round1_reads,round1_reads_rest}.py` | 1,532 / 75,061 | 61,882 / 58,213 | Primarily historical polytonic Greek, with Latin/mixed strata; seeded book holdouts and global held-out label protection. Internal-only data. |
| Vouli 1850s; `scripts/harvest/vouli.py` | 779 / 48,169 | 37,367 / 28,259 | Historical polytonic Greek proceedings; book-level holdouts, source contribution cap in historical pool. 772 fresh reservations differ from 779 processed pages; retain the wave receipts rather than pricing processed pages again. |
| Anemi round2; `scripts/harvest/round2.py` | 613 / 29,943 | 24,430 / 23,128 | Historical Greek; 8 held-out books frozen before reads (2 dev, 6 test), one per decade; cross-wave label holdout checks. 50 books fetched, 49 read. Internal-only. |
| Parliament 1975–2000; `scripts/harvest/parliament.py` | 705 / 95,438 | 85,042 / 81,181 | Polytonic/monotonic transition and minority Latin; actual source/class expectations apply. Admission summary counts 690 contributing pages; preserve the full read denominator. Document-disjoint holdouts. |
| OpenArchives wave4; `scripts/harvest/openarchives.py` | 917 / 30,788 | 25,606 / 25,372 | Mostly modern Greek with Latin/mixed lines; old dates/titles/collections are contradicted by O1. Keep frozen book splits; apply metadata only through the separate O2 release. |
| Mixed A/B/C; `scripts/harvest/mixed.py` | 782 / 46,515 | 33,114 / 30,839 | Anemi polytonic, repository mixed Greek–Latin, IA Latin/lexicon material. Book disjointness; cleaned v2 moves lexicon wholly into train. Anemi part remains internal. |
| Cyrillic IA; `scripts/harvest/cyrillic.py` | 566 / 37,398 | 13,683 / 12,900 | Catalogue languages include Russian, Bulgarian and Serbian; modern/historical orthography must be declared. RU1 applies only to historical Russian. Frozen source/book holdouts. |
| Wikisource scans/transcriptions; `scripts/harvest/wikisource.py` | 400 / 14,967 | 12,356 / 12,095 | 20 Greek + 10 Russian works, polytonic/historical regimes preserved. Original historical admitted split: 0 train / 1,118 dev / 11,238 test. Transcription alignment is separate from Google labels. |
| **Total cleaned v2** | — | **271,987** | **214,436 train / 13,522 dev / 44,029 test**. Legacy row aliases `val`/`reserved` become dev/test only under matching frozen parent declarations; literal `source_split` is retained. |

Collection v2 derives from pool v1 293,439: 21,449 rule drops, 3 global holdout rejections, 10,313 relabels and 2,868 lexicon split moves are recorded in `CLEAN_REPORT.md`. The v2 census called **CENSUS3/ADM5c** is the standard historical v2 admission census (2,489 failures); it is a different artifact from the Clariden **census_03** whole-pipeline job. Neither changes the frozen input membership.

## collect-v3 snapshot sources

Rows below are sums of `source_class_counts` in `docs/records/harvest/collect_v3_admission/split1/summary.json`, over the exact W1/W2 18 October 05:24 snapshots. Page allocations are the W1/W2 **plan**, not completed-read counts (`docs/records/harvest/collect_v3/README.md`). All snapshot rows remain unassigned in the census inputs until a final edition split is explicitly supplied.

| Source; route class | Planned W1 / W2 pages | Snapshot rows W1+W2 | Expected source regime / caveat |
|---|---:|---:|---|
| `bsb_poly1850`; MDZ/BSB IIIF | 200 / 800 | 33,090 | Greek polytonic and Latin/bilingual editions; 10 W2 documents partial at snapshot. “poly1850” is a collector class, not proof every year is 1850–1890. |
| `ia_poly1850`; IA JPEG | 320 / 1,280 | 64,476 | Polytonic Greek, often Latin commentary; preserve per-book languages/scripts. |
| `ia_greek_latin`; IA JPEG | 200 / 800 | 11,755 | Greek–Latin; whole words may use either declared script, mixed-script words drop under gate 0.3. Historical `crop_tight_page` qualification hold is not removed by letter checks. |
| `ia_russian`; IA JPEG | 80 / 320 | 2,963 | Historical Russian Cyrillic, independent language/orthography declaration; all snapshot rows proposed forced test through locked sets. |
| `serbia`; collector provider route | 60 / 240 | 8,897 | Modern Serbian Cyrillic with extended codec support. Never infer historical Russian eligibility. |
| `nlg`; NLG IIIF | 80 / 320 | 12,109 | Greek polytonic source expectations with catalogue dates; missing or inconsistent geometry remains evidence. |
| `elstat`; official PDF | 12 / 48 | 19,879 | Greek/Latin numeric-table roles; role is separate from recognized `nonletter` script class. Annual-title edition merges need review for missing month/volume. |
| `kosmopolis`; OJS/provider | 120 / 480 | 5,356 | Historical polytonic periodical material; issue identity and page binding retained. |
| `lekythos`; OJS/provider | 58 / 232 | 13,407 | Historical Greek periodicals, normally poly1900; issue-disjoint allocation. |
| `gazette_modern`; official PDF | 240 / 960 | 148,547 | Sampling spans 1982–1990; census expectations use monotonic from 1982, while collector **primary class is text-based**. Failed polytonic Gazette stratum is not promoted by year. |
| **Total** | **1,370 / 5,480** | **320,479** | W1 **101,098**, W2 **219,381**. These are all rows, not only usable candidates or split-only holds. |

Routes are implemented in `collect_v3/routes/providers.py`; collection/features in `runner.py`/`pipeline.py`; expected census metadata construction is recorded in `docs/records/harvest/seg_census/remote_evidence/HANDOFF.md`. Its expectations and observations are different fields: seeing Greek in an OCR label does not establish the intended language of a book.

## SPLIT1 is a proposal

`docs/records/harvest/collect_v3_admission/split1/SPLIT_PROPOSAL.md` covers **all 320,479 rows**, not the 142,959 downstream split-only holds. It proposes 1,359 editions, with 11 collapsed document edges forming 9 proposed merged groups. The default unit is `<source>--<dochash>`; shared provider/global identifiers or normalized title+year+volume supply merge edges. No fuzzy/transliteration equality is assumed. Gazette issues remain independent editions; year cards are a display grouping.

The fallback target is 85/5/10 raw rows at edition granularity; the plan supplies no split ratio. Deterministic allocation uses `split1:<source>:<class>` seeds and whole editions. Forced locks initialize counts. Proposal totals are **253,402 train / 7,007 dev / 60,070 test**, including **99 forced test editions / 52,468 rows**. Raw allocation is not a usable-train forecast. The nine ELSTAT annual-title groups, unknown volumes, missing v2 titles and cross-provider aliases remain review limitations; direct v2 metadata matches were zero, not proof of semantic non-overlap.

The archived census04 input adapter accepts a pinned file with `parent_id`, `row_id`, `edition_id`, **`split`** (`train/dev/test`). SPLIT1's `proposed_split` alone is not accepted as a final allocation. Its receipt has no real split pinned. Top-level `line_pipeline_census` accepts metadata `row_splits`/book declarations but has no separate census04 split-file entry point. Do not silently rename the proposal field or substitute a proposal as a release.

## Locked evaluation and overlap checks

| Evidence set | Recorded protection / limitation |
|---|---|
| Original v2 dev/test | Preserve every 13,522/44,029 input row; diagnostic failures do not delete the evaluation cohort. |
| `wikisource_human` | Census03 protection receipt includes 1,527 historical human-label rows; this is not all 12,356 T27 admitted rows or all original 2,030 aligned pairs. |
| `e1_real_test` | 3,600 external test rows in the census03 protected-cohort receipt. |
| LQB truth | 2,665 unique frozen truth-line IDs; 2,652 occur in census parents. Frozen truth file SHA is retained in `docs/records/harvest/seg_census/OUT_OF_GIT_RECEIPT.md`. |
| SPLIT1 registered locks | Includes registered LQB/N1 and other exclusion classes; forced editions preserve the locked side. The per-edition evidence and release-exclusion matches, not a generic TEST label, define allowed use. |
| Reader comparison fixtures | `docai_manifest.py` keeps exact Polyton-DB 300 supplied gold separate from O4D/born-digital diagnostics. Their existence does not make the collection's OCR labels independent gold. |

The census03 prepared protection binds 61 external edition IDs and 9,119 external/reference/raw crop hashes. Its archived integration patch wires external crop hashes into deduplication. **Historical limitation before SEG10:** top-level deduplication lacked the configured crop-hash union. Current `line_pipeline_census.py::Ledger.deduplicate()` unions `final_policy.heldout_crop_sha256` with observed held-out crop hashes; deployment still requires exact package/config verification. See the exact discrepancy in [B.c](../c_pipeline/README.md). Edition protection in the top-level pipeline still runs.

## Known sourcing issues

- **OA metadata correction:** O1 found all 89 wave4 titles wrong, 80 collections wrong and 86 known years contradictory. O2 publishes `docs/records/harvest/oa_rebind_v1/o2/v2_meta1/`: metadata changes on 25,372 active rows, zero added/dropped/moved/relabelled rows, plus an 89-book sidecar. Nine Dione books / 2,828 active occurrences remain `pending_provider_verification`. Old OCR-success/polytonic-ratio fields are unbound to the corrected books and must not be promoted. O2 records 7 cross-split duplicate groups and 6 within-train groups; it does not remove them or certify leakage clearance. The pinned census parents still name the original v2 files, not v2-meta1.
- **Cached foreground/label disagreement:** `docs/records/harvest/collect_v3/KNOWN_ISSUES.md` records 4 inconsistent distinct page payloads in 99 cache entries (plus a duplicated inconsistent fallback entry). About 4% describes that snapshot only. `pixels.py` clears foreground after labelling without updating labels; strict adapters report `geometry_unavailable`.
- **Inverted envelopes:** same issue record: 181 inverted rows on 10 pages / 9,975 rows in 99 caches; 4 also have zero-height columns. Saved curves and code support a seam-conflict inference; no repair/rerun is recorded. Resulting qualification losses are unavailable geometry, not measured detection failures.
- **Partial BSB and historical admission:** the 05:24 snapshot omits 436 later BSB pages. `w2_originals_v3_*`, Gazette originals and W1 screened ADMW2 admissions are parked/superseded by the Clariden pipeline. Later BSB/Gazette collection progress requires its own exact snapshot/receipt.
- **Access and rights:** ≤1 request/s per host, robots and access-stop receipts apply. Anemi remains internal. Old source metadata and a successful download do not verify per-item reuse rights.

## Sources read

- `docs/cleanup_20261019/{OWNER_BRIEF.md,PLAN.md}`; `docs/records/harvest/collection/v2/{CLEAN_REPORT.md,ADMISSION_CENSUS_20261018b.md}`.
- `docs/records/harvest/{round1,round2,vouli,parliament,openarchives,mixed,cyrillic,wikisource}/admission_summary.json`; available wave `read_summary.json` and `cost_receipt.json` files (round1 uses reads_d1/reads_rest summaries).
- `docs/records/harvest/round2/READS.md`; `docs/records/harvest/wikisource/READS.md`; `docs/records/harvest/collect_v3/{README.md,KNOWN_ISSUES.md}`.
- `scripts/harvest/{vouli,parliament,openarchives,mixed,cyrillic,wikisource,_anemi_round1_fetcher}.py`; `greekocr/harvest/{parliament,openarchives,mixed,cyrillic,wikisource}.py` (selection/transport interfaces).
- `collect_v3/routes/providers.py`; `collect_v3/{pipeline,transport,reader,exclusions}.py`; `greekocr/readers/services/docai_manifest.py`.
- `docs/records/harvest/collect_v3_admission/split1/{SPLIT_PROPOSAL.md,summary.json}`.
- `docs/records/harvest/oa_rebind_v1/FINDING.md`; `docs/records/harvest/oa_rebind_v1/o2/RELEASE_NOTE.md`.
- `docs/records/harvest/collect_v3_admission/HANDOFF_20261018_sourcing.md`; `docs/records/harvest/seg_census/OUT_OF_GIT_RECEIPT.md`.
- `greekocr/harvest/{line_pipeline_sources,line_pipeline_census}.py`; `docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census04.py`.
- `docs/records/harvest/seg_census/remote_evidence/{HANDOFF.md,census03_config.json,integration_fixes.diff}`; `docs/records/harvest/seg_census/receipt.json`.
