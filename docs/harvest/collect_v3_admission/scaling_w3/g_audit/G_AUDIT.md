# G-AUDIT — legacy renderer coverage, 20 October 2026

The legacy inputs provide broad Greek/Latin/Cyrillic font support and generic bold, tracking and polarity variation. They do **not** establish qualified coverage of the complete Track G bundle for any benchmark source. Condensed faces and a line-level leader GT/crop contract are absent. Old-style-number and capital-mark qualification remains incomplete. A8 ablation shards and A9 twins are deferred until S1; nothing was built for either.

**Exposure result is partial.** The complete, historically hash-bound upstream O5 input manifest contains **2 exact matching rows**, both `o1d_real`. The seven other raw source manifests and the assembled corpus were not fully scanned under the small-read constraint; their total hits are **unknown**, not zero. The terminal hit count means newly checked input-manifest rows only. Separately, MIX1 already records **287 exposed rendered training labels**; that count is not an input-manifest count. See the exposure section and `exposure_hits.json`.

Scope: metadata and text only. No image was opened, rendered, measured or read by OCR. Clariden access used read-only SSH on the login node; no scheduler commands, allocation, job, remote write, package, A7 measurement or font installation. Local font metadata was parsed only after its file hash matched the remote and historical hashes. Existing unrelated worktree changes were preserved. Full manifest streaming was left pending clarification of “small reads”; no answer was assumed to authorize it.

## Evidence and custody

`W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`; here `P=$W/greek-page-ocr`. The brief's custody-chain `P` instead denotes `$W/greek-page-ocr/out`.

- A12: `$P/out/e4/wave1b/v2-codec/old_v2/synthetic/build_info.json`, SHA `94e899a34929ee82c564c935b21a6659515a30d3fbdddae42366dc0ed71219cc`. Its `encoding_derivation` points to `$P/out/e1_run4/synthetic`, binds source receipt SHA `495453433c2efff88a8a0d7d39de32e856d878d815b923dbf3eb9354411bfbff`, and records unchanged original columns/labels/pixels/order with a codec-v2 tag. This audit checked the small receipts, not shard payload equality. Witnesses: [A12](evidence/a12_build_info.json), [E1](evidence/e1_build_info.json).
- Recipe file SHA `2f228950e9a508b5e130e82ce5b89de2b911be4a23872c3acc7f53e83c59dce7`; effective recipe SHA `76cef226be77777dff9cc2e37c019712455b3a6999ab6f73963445ca0ec9663a`. The effective recipe is embedded in both receipts. The two SHAs are not two recipes. [v5 file](evidence/recipe.v5.json).
- Current v6 file SHA `789731ac9f5b3e28ac60542f75b2117beede8361582efcce99641a454f58c7c4` adds `estia_word_final_grave_v1`, retains polarity `.02`, and is not the recipe bound to A12. [v6 file](evidence/recipe.v6.json). The input count is **2 inspected recipe files**, one A12-generating distribution; other listed smoke/evaluation/v1/v7/v8 files are outside this anchored comparison and are not claimed to be audited recipes.
- Remote metadata paths, original byte sizes and full SHAs are in [remote_metadata_index.json](evidence/remote_metadata_index.json). Full seal JSONL copies were transient; their final witness is the compact projection `benchmark_metadata.jsonl`, not a byte-identical file. [remote_details.json](evidence/remote_details.json) contains selected historical preparation bindings and bounded text heads, with unrelated crop bindings omitted. Each final artifact is SHA-bound in `GUARDED_COMMIT_LIST.json`.

The sibling repository's `docs/data_contracts.md`, Provenance P1–P5, requires factory-owned generation/import, a mix manifest, a git-committed recipe hash plus `audit_ok`, and versioned recipe changes. `audit_ok=true` in the historical receipt does not certify a new benchmark exclusion audit or the G bundle. Current rule excerpts and historical code witnesses are in [source_witnesses.json](evidence/source_witnesses.json). Historical `build.rs`, `render.rs`, `select.rs`, `corpus.rs` and `e1_prepare.py` at preparation revision `2e3cf6f2b68dfca94a8c4ae7403a6b61a37d8d7b` match the preparation input hashes. Current documentation is labelled separately.

## Renderer inputs

**67 font files**, all matching the remote SHA256 and the full historical preparation SHA256; **64 sampled stems** in the legacy audit, over **203,693 rows across train/val/reserved**. Train alone is **190,486 rows**. The receipt's stem/sha16 list is an input inventory, not a per-training-split font census. Sources: [font_inventory.json](evidence/font_inventory.json), [audit_report.json](evidence/audit_report.json), [E1 receipt](evidence/e1_build_info.json).

`font_inventory.json` lists every remote filename, full SHA, receipt sha16, family, style, OS/2 weight and width class, GSUB feature tags and recorded all-split sample count. `font_cmaps.json` preserves the cmap evidence separately. Family/style labels are font-table metadata, not guessed from filenames. [FONTS_provenance.json](evidence/FONTS_provenance.json) is retained as a provenance witness; this audit does not newly qualify licensing.

The **3 never-sampled input faces** are **IBMPlexSans-Regular, LibertinusSerif-Regular, TheanoDidot-Regular**. The v5 and current v6 recipes explicitly hold them out; all remaining input stems have positive counts in the historical `font_spread.per_font` audit. There is no evidence here that any non-held-out face was never sampled. Per-split counts and v6 realised font sampling are unknown.

The **9 recorded rendered text-source IDs** are `arxiv_meta`, `estianews`, `gutenberg_el`, `gutenberg_latin`, `gutenberg_ru`, `o1d_real`, `synth_furniture`, `wikisource_cyr_uk`, `wikisource_el` (MIX1 per-source ledger). Of these, **7 raw JSONL files** are SHA-bound as external preparation inputs; O5 supplies `o1d_real` and the selector generates `synth_furniture`. The source catalogue has **18 entries**, not 18 demonstrated renderer inputs. The `wikisource_cyr` catalogue key and `wikisource_cyr_uk` actual ledger key must not be silently conflated. Catalogue names, declared scripts, eras/registers and acquisition notes are retained in [sources.json](evidence/sources.json); they do not prove downloaded corpus completeness.

The actual assembled `$P/out/e1_run4/corpus.jsonl` is **919,649,599 bytes**, and `pool.jsonl` is **317,968,619 bytes** (remote stat witnesses). Ingest reports **3,076,410 read / 996,049 kept**, with split counts **936,146 train / 45,057 val / 14,846 reserved**. These are input/pool populations, not sampled training rows. [ingest report](evidence/pool.jsonl.ingest_report.json). The preparation binding's raw corpus paths and SHAs are reproduced under `raw_input_bindings` in `exposure_hits.json`; no large manifest was rehashed remotely.

Appearance: [appearance_band.json](evidence/appearance_band.json), SHA `3f7e7c5c2f58507d7bafdd580afcf6e71aec5ebc5bbede1a1349bd382d2099f7`, derives from **58 crops** and records contrast/ink/polarity only. Its embedded statistics are contrast p10/p50/p90 **.34509802/.5764706/.83137256**, median ink fraction **.09629037**, dark-on-light fraction **1.0**, accepted median-contrast range **[.24156861007213593,.9976471066474915]**, minimum dark-on-light **.95**. Crop membership, train-only status, source/era/type conditioning, x-height/stroke/blur/leading/skew/padding distributions are not supplied by that band. No new measurement was made.

## Benchmark sources, editions and metadata

Seal suite SHA is **`9447f09c6073028c1085996e1663232a18ac70ef8b81eda4be5c232a4025b924`**. The directly read final JSONLs contain **2,690 references: 2,253 test + 437 dev**. Use the final rows, not quota targets, as actual population counts. [suite](evidence/suite.json), [seal receipt](evidence/SEAL_RECEIPT.json), [summary](evidence/benchmark_summary.json).

Seal rows contain **199 distinct `doc` identities** and **0 explicit `edition_id` fields**. Joining every final `row_id` to the hash-bound `release_v3/inputs/candidates_v3.jsonl` recovers **2,690/2,690 edition bindings, 199 edition IDs**, with no split conflicts. These are recorded edition identities, not newly verified bibliographic editions. Titles, printing dates, printer/typeface and named historical font cuts are not present in the inspected final-row metadata. Work identity remains unreviewed; do not infer edition equivalence to a synthetic text corpus from a collection name. [edition join](evidence/benchmark_edition_join.json), [source inventory](evidence/benchmark_source_inventory.json).

| Source | References | Recorded editions | Reference scripts |
|---|---:|---:|---|
| bsb_poly1850 | 312 | 5 | greek, greek+latin, latin, none |
| elstat | 147 | 6 | greek, greek+latin, latin, none |
| gazette_modern | 685 | 151 | greek, greek+latin, latin, none |
| ia_greek_latin | 237 | 5 | greek, greek+latin, latin, none |
| ia_poly1850 | 321 | 9 | greek, greek+latin, latin, none |
| ia_russian | 223 | 10 | cyrillic, none |
| kosmopolis | 224 | 3 | greek, greek+latin, latin, none |
| lekythos | 213 | 3 | greek, greek+latin, latin, none |
| nlg | 139 | 2 | greek, greek+latin, none |
| serbia | 189 | 5 | cyrillic, none |

The script column is computed from Unicode letter names in the existing reference text, not inferred from pixels. `none` means no alphabetic letters; it is not an unknown language. Recorded expected scripts and orthography remain separately in the metadata witness. Edition totals per source need not be assumed disjoint; the global count above is deduplicated.

Actual primary-class counts (mutually exclusive; both splits):

| Class | Rows |
|---|---:|
| caps_headings | 149 |
| curved_skewed | 123 |
| degraded | 100 |
| font_extremes | 120 |
| greek_latin | 164 |
| historical_russian | 120 |
| latin | 160 |
| leaders_dashes | 119 |
| long | 184 |
| modern_cyrillic | 48 |
| monotonic | 300 |
| numeric_cells | 249 |
| poly_dictionary_journal | 155 |
| polytonic | 430 |
| short | 149 |
| vertical_turned | 120 |

Reference-script counts: **Greek 1,446; Greek+Latin 238; Latin 250; Cyrillic 325; no letters 431** ([summary](evidence/benchmark_summary.json)). Cyrillic language tags are **ru 188 / sr 137**; this is metadata, not language recognition. Relevant nonexclusive tags are **caps_headings 189, numeric_cells 407, leaders_dashes 156, font_extremes 149**; these are not primary-class totals. `letter_spaced` is **unavailable for all 2,690 rows**. The combined leaders/dashes tag does not certify a dot leader; numeric cells do not establish old-style numeral shapes; caps do not establish weight or condensation. No dedicated old-style-numeral, bold, condensed or polarity field was found in the final tags. Source-specific typography remains unknown beyond those recorded tags.

## Coverage matrix and font candidates

[coverage_matrix.csv](coverage_matrix.csv) crosses **184 observed joint (source, primary class, reference-script) groups × 7 features = 1,288 cells**. It preserves actual group row counts, face names, status, rationale and evidence paths. It is not an expansion of all possible empty combinations. Counts: **yes 0 / partial 920 / no 368 / unknown 0** ([coverage summary](evidence/coverage_summary.json)). The many repeated statuses reflect common recipe limitations, not measured equivalence between sources.

`yes` would require both feature-specific font support and an evidenced recipe/qualification path. `partial` means only some ingredients exist (including metadata/cmap candidates), with the missing ingredient named. `no` means an identified missing input or GT contract. `unknown` is reserved for a cell with no usable support evidence; none is wholly unevidenced in this input-capability matrix. **Unknown benchmark typography and unknown visual qualification are recorded separately and are not converted into yes.** No face is visually qualified by this audit.

Each cell's candidates pass a strict union-of-NFC-reference-codepoints cmap check for its group; this is an audit lookup, not rendering benchmark texts. It does not test shaping, marks, defaults, raster visibility or codec acceptance. The font list can differ by source/class/script even where the status is identical. All script categories have letter-cmap candidate faces, but this does not establish complete historical-script training coverage. [script coverage](evidence/script_coverage.json).

| Feature | Input support and named examples | Coverage limit |
|---|---|---|
| Orthography-specific capital marks | Alegreya-Regular/Bold, EBGaramond-Regular/Bold, DejaVuSans/Serif, NotoSerif-Regular/Bold, FiraSans-Regular/Bold offer broad letter/mark cmap candidates. GFSBodoni-Regular, GFSDidot-Regular, GFSGalatea-Regular are Greek candidates; use per-cell lists for exact eligibility. | Legacy v5 does not bind the Track G capital-stripping/Latin/Cyrillic-preserving policy. v6's Estia word-final-grave policy is a different change. No per-mark paired visual qualification. |
| Bold caps | Sampled metadata-bold faces include Alegreya-Bold, AlegreyaSans-Bold, EBGaramond-Bold, FiraSans-Bold, GFSNeohellenicBold, GentiumPlus-Bold, NotoSans-Bold, NotoSerif-Bold, SourceSans3-Bold. | Bold is sampled globally; no caps-conditioned display-face routing or source-style qualification. Full eligible bold/BoldItalic lists are in the CSV. |
| Condensed caps | **None** with OS/2 width class below normal in the 67-file inventory. | No metadata-qualified condensed face; visually narrow cuts without a condensed width label are not ruled out or certified. |
| Letter-spaced caps | Eligible faces in each CSV cell; v5 `letterspacing_fraction=.03`, tracking sampled in **[.08,.18) em** (`build.rs`). | Generic tracking rather than caps/source conditioning; no benchmark spacing measurement and no paired qualification. |
| Old-style numerals | `onum` present in sampled Alegreya, AlegreyaSans, EBGaramond, FiraSans variants; also GFSArtemisia-Regular, GFSBodoni-Regular, GFSDidot-Regular, GFSElpis-Regular, GFSGalatea-Regular, NotoSerif variants, OldStandard-Regular, XCharter-Regular and others listed individually in font inventory/CSV. | GSUB tag is potential support, not proof of active old-style digits. Historical `rustybuzz::shape(&rb, &[], buf)` enables no explicit `onum`; defaults were not visually checked. No grouped-number/face routing. |
| Light-on-dark | Every eligible face can use the recipe's image-level polarity operation. v5 input **.02**, realised all-split fraction **.019915470670125293**, from legacy `distortion_marginals` audit. | Track G target **.05** absent; no source-conditioned polarity statistics/qualification. |
| Leader dots | Eligible period-bearing faces include DejaVuSans, Alegreya-Regular, EBGaramond-Regular, NotoSerif-Regular (full per-cell lists in CSV). | Period glyph coverage is not leader-run GT. Track G states compositor leaders have no recognition GT and requires a new line-level target/crop-ownership contract. |

The historical letterpress routing explicitly names **GFSDidot_Classic, GFSBodoni-Regular, GFSGalatea-Regular, OldStandard-Regular**. Its recipe sets cohort fraction **.20**, independent lunate fraction **.07**, and the build records **57 routing fallbacks**. These are a specific Greek old-form treatment, not evidence for arbitrary benchmark editions or old-style decimal numerals. Sources: E1 recipe/receipt and historical `build.rs` witness.

## Seven gap groups

1. **Capital policy/visibility:** no qualified orthography-specific capital policy and per-mark physical acceptance evidence for the G change; ordinary glyph support is insufficient.
2. **Display caps:** bold candidates exist, but caps routing and source-style qualification are missing; no metadata-condensed face is available. Generic tracking is not a qualified letter-spaced-caps distribution.
3. **Old-style grouped numbers:** candidate `onum` faces exist; active/default numeral form and grouped-number routing are unqualified. No face can be named as visually qualified for this feature.
4. **Polarity calibration:** the legacy low exposure exists, but the proposed higher exposure and train-only conditional domain statistics do not.
5. **Leader target/ownership:** no qualified line-level explicit dot-run GT/crop contract, regardless of period coverage.
6. **Source/edition/appearance binding:** no benchmark font attribution, matched edition-specific renderer face qualification, conditional A7 manifest or complete new input-corpus exposure result. Historical font licence evidence also remains a separate unresolved qualification.
7. **Historical/Serbian script admission:** faces have letter cmap support, but v1 rejects unsupported codepoints. Against the reference text, the v1 atom table lacks **111 occurrences of ѣ and 87 of ј** ([script_coverage.json](evidence/script_coverage.json)); these are occurrence counts, not line counts. A12's v2 retagging keeps original labels, so it does not recover missing training texts. No claim that a new face is needed follows from a codec gap. Full script-specific shaped/mark qualification remains absent.

These are **7 decision-oriented gap groups**, not a count of missing fonts or failed benchmark rows. No script category has zero letter-cmap candidates; no script has new visual qualification from this audit.

## Text exposure and old exclusions

The audit reuses MIX1's exact `normalize_text` and `TextExposure` definitions, extracted with AST into [mix1_text_exposure.py](evidence/mix1_text_exposure.py), without importing image readers. NFC, then Unicode-whitespace collapse/strip; exact full-string match first, otherwise any shared substring of at least **30 Unicode codepoints** via all 30-codepoint windows. The **2,690 references** produce **24,320 distinct windows** (same as MIX1); no approximate matching or hash collision test is substituted. Short strings still match exactly.

Complete newly checked input: local O5 `synth_corpus.jsonl`, **4,297,380 bytes**, SHA `a1e281490045ff0af7eb39077e167f5c0e37f076e3ab049882ea1a270ca27000`, exactly matching its historical preparation binding. **20,016 input rows; 2 exact hits; 0 substring-only hits**, source `o1d_real`. [o5_source_exposure.json](evidence/o5_source_exposure.json) retains hit line/doc IDs and text witnesses. This is the upstream input before `e1_prepare.py` filters O5 rows to train documents/texts and excludes old held-out documents. It is not proof both rows survived to the assembled corpus or were rendered.

Per-source exposure populations are deliberately separate:

| Text source | Full upstream input manifest, newly checked | Full assembled corpus/pool | MIX1 historical rendered train: exact / substring30 / hit rows |
|---|---|---|---:|
| arxiv_meta | Unknown; SHA binding only | Unknown | 0 / 0 / 0 |
| estianews | Unknown; SHA binding only | Unknown | 1 / 10 / 11 |
| gutenberg_el | Unknown; SHA binding only | Unknown | 0 / 0 / 0 |
| gutenberg_latin | Unknown; SHA binding only | Unknown | 0 / 0 / 0 |
| gutenberg_ru | Unknown; SHA binding only | Unknown | 0 / 0 / 0 |
| o1d_real | 20,016 rows; 2 exact / 0 substring30 (O5 before filtering) | Unknown | 1 / 0 / 1 |
| synth_furniture | Generated by selector; no raw file manifest | Unknown | 274 / 0 / 274 |
| wikisource_cyr_uk | Unknown; SHA binding only | Unknown | 0 / 0 / 0 |
| wikisource_el | Unknown; SHA binding only | Unknown | 1 / 0 / 1 |

MIX1's prior full rendered-train total is **287/190,486 hit rows across 4 source IDs**, including short exact furniture references; a hit is a potential text exposure, not proof of the same edition or memorisation. Its per-source ledger is preserved in [mix1_prior_text_audit.json](evidence/mix1_prior_text_audit.json), bound to the prior receipt SHA and current A12 receipt identity. It was not rerun on Parquet in this small-read audit. In particular it cannot certify unrendered input texts clean. No rendered-train hits from the other sources in that ledger means only that earlier selected-label population had zero recorded hits.

Only the first **3 rows each** of assembled corpus and pool were newly read; their **0 observed hits** are not a population result. Seven external raw source manifests are historically bound by SHA but were not opened/scanned in full. Their current availability and full hit counts remain unknown. `exposure_hits.json` uses JSON nulls for unknown manifest totals. The source catalogue's remaining entries are not treated as actual inputs or zero-hit sources.

The recipe's `factory/exclusions/realcrops_v1.txt` has **6,839 lines**, SHA `a38531ef4702e37e8b9fd9039abc1553a9173050d003b18e21947afbd934908d`; none matches a seal04 reference by MIX1's exact/30-character check. The old O5 exclusion file is separately SHA-bound in the historical preparation witness; it was not fully rescanned here. Old exclusions predate seal04 and **do not provide a seal04-bound edition/key/reference exclusion receipt**. Zero overlap with the inspected old exclusion list is not evidence that renderer input text is clean; the positive O5 and prior A12 hits show why a new audit is needed.

## A7 measurement strata to specify later — no measurements now

Use train-only release v3/v4 crop identities joined to the SCALE1/BENCH02-style tags and edition map; bind release receipt, tag producer/version, row key, source, edition, crop SHA and raw-label/overlay choice. v4 membership must come from its successful release receipt; the local REL4 specification is not proof that release production has completed. Use REL4's raw admission/overlay contract when choosing labels. Existing SCALE1 tags are not automatically a v4 tag release. Sources: `../scale.py` (tag schema), `../vendor/bench02_draw.py` (classification/availability), `../../release_v3/REL3.md`, `../../release_v4/REL4.md`.

List a sampling frame and requested crop allocation per stratum; **counts and sample sizes remain open under Q4**. Do not take benchmark/dev/test crops or unknown-edition crops into a training calibration pool. Exclude locked editions and audit calibration text/crop exposure before measurement.

- Source × recorded edition × era/register/type: the observed benchmark source families above as domain targets; choose only eligible training editions. Era/printing type requires catalogue binding or annotation when absent; do not derive it from a source-name suffix.
- Script/orthography/language: Greek monotonic/polytonic and dictionary/journal; Latin; Greek–Latin mixed; historical Russian, modern Cyrillic and Serbian; numeric/nonletter. Preserve mixed-script/mark inventories and unsupported-codec strata.
- Typography: caps/headings, ordinary text, small/large font-extreme tags, bold, condensed, tracked caps, grouped-number prose/old-style numerals, light-on-dark, leaders versus dashes. Mark absent fields as needing annotation; do not use the combined leaders/dashes tag as dot-run truth.
- Acquisition/geometry: source-specific degradation strata, curved/skewed, vertical/turned, short/long, cells versus running text, crop tightness/padding, page/line context for leading. Missing confidence is not the lowest-confidence bin; “degraded” is a source-relative ranking, not measured physical damage.
- Later measurements: conditional x-height, stroke width, contrast, blur, leading, skew/curvature and padding, polarity and mark visibility; report missingness, methods/units, tails and source/edition uncertainty. Leading needs page context rather than isolated strips alone. Explicitly separate human annotations from derived measurements.

The legacy 58-crop appearance band cannot substitute for this frame. No sample count, crop selection, statistic or job was created here. A8 paired audits and A9 twins remain deferred.

## Guarded commit list and validation

Only the exact paths enumerated in [GUARDED_COMMIT_LIST.json](GUARDED_COMMIT_LIST.json) are review candidates. Its entries bind every final report/evidence file by size and SHA256; the list excludes itself to avoid a recursive hash. The coordinator brief `docs/briefs/G_calibration_scan_audit.md` was read but unchanged and is not included. Nothing outside `g_audit/` was written. No `git add` or `git commit` was run. Do not stage the whole pre-existing dirty worktree.

Validation: final JSON parsing; CSV row/status reconciliation; benchmark split/source/class/script totals; complete final-row edition join; all font hashes against remote/preparation identities; input-manifest O5 SHA match; custody receipt/recipe SHA links; guarded file hashes. This validates metadata/report consistency, not rendered typography or full corpus cleanliness. Evidence scripts are audit/read helpers, not a training package; do not execute collectors to launch or prepare A8/A9.

## Open decisions Q4–Q6 — wait for S1

**Q4:** S1 must inform whether to test a declared bundle or separate variants, their sample sizes, eligible real-domain A7 strata and train-only calibration allocations. Decide which missing face/style evidence and complete text-manifest audit are needed before qualification. This report does not select new fonts, a recipe or a calibration population.

**Q5:** S1 must inform the leader dot-run GT/crop-ownership contract, damaged/partly visible glyph target policy and per-mark acceptance thresholds, including the capital-mark paired-visibility gate. No leader exposure change or paired audit is built now.

**Q6:** S1 must inform eligible twin source pages/editions, degradation severities, coherent geometry scope, GT transform/ambiguity policy and counts. Whole-page raster-only twins remain unbuilt.

G-AUDIT: done | renderer inputs <fonts 67, recipes 2, text sources 9> | coverage yes/partial/no/unknown 0/920/368/0 over 1288 | exposure hits 2 (o1d_real) | gaps 7 | no jobs
