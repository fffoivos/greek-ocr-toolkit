# DATA_NEEDS — wave 3 novelty data, 20 October 2026

| Family | Artefact | Exists? | Custody | Exposure audit | Package effort | Blocking decision |
|---|---|---|---|---|---|---|
| C2 | A1 auxiliary target encoding/manifest | No separate package found; labels exist | none | inherit pinned rows; audit any additional vocabulary corpus | label pass; 0 new images | Q1 |
| P1 | A2 unlabelled train-only crop manifest + supervised-control exposure schedule | No | none | new, including rejects | CPU selection/audit; GPU pretraining later | Q2 |
| S3 | A3 SCALE1 tags + census confidence evidence | Yes: 364,871 rows; confidence on 168,637 | R1 | subset audit pending | join census by parent/id | Q3 |
| S3 | A4 older v2 confidence source | Yes: 271,987 source rows, current join coverage unknown | R2 | train-only join required | 248.55 MB source pass | Q3 |
| S3 | A5 book-separated calibration examples/model + row weights | No qualified S3 package found | none | new calibration partition and weight binding | S2 validation + fit + row pass | Q3 |
| G | A6 legacy renderer inputs: recipes/fonts/text-source manifests/appearance band | Yes, legacy scope only | R3; corpus completeness unqualified | new benchmark-edition/text audit | reuse inputs; qualify required faces | Q4 |
| G | A7 conditional real-statistics measurements | No full specified package found | none | train-only calibration crops | image measurement job | Q4 |
| G | A8 v6 ablation shards + 2,000-pair visibility audit | No full §5b package found | none | new text/font/crop lineage audit | rendering job + 4,000 audit images | Q4–Q5 |
| G | A9 raster-only degraded twins + tracked GT | No controlled package found | none | new source-edition and output audit | raster/degradation/detector job | Q6 |
| M1 | A10 E1 born-digital train pool | Yes: 19,657 rows | R4 | old document audit exists; benchmark 0.2 audit new | reuse 446.37 MB / 5 shards | Q7 |
| M1 | A11 wave-3 matched replay draw manifest | No; old-release plan exists | none for wave 3 | new binding to audited parents | CPU draw job; no render | Q7 |
| M2 | A12 synthetic v5 train shards | Yes: 190,486 rows | R5 | new benchmark text/source audit | reuse 5.815 GB / 47 shards | Q8 |
| M2 | A13 fraction/curriculum exact draw manifests | No wave-3 package | none | parents + every drawn row | CPU draw job; no fraction-specific render required | Q8 |
| M3/M4 | A14 class/cap/temperature draw manifests; A3 tags reused | No wave-3 manifests; tags exist | none for A14 | pending subset receipt + draw binding | CPU quota/draw job; 0 new images | Q9–Q10 |

Counts: **8 families, 14 distinct artefact groups, 5 existing, 5 with custody**. A3 is counted once across S3/M3/M4. “Existing” includes legacy inputs requiring a new audit; it does not mean wave-3-ready. “No” means no qualified package located in the inspected records/paths, not an exhaustive filesystem absence proof. Custody means a recorded hash/receipt binding, not qualification of labels or exposure.

Scope: beyond REL3 `rel3_c05_full_01` (168,637 rows), SCALE1 `scale1-c05-003` (**pending**, job 3705111 per brief), and benchmark `seal04` (`9447f09c…`). `W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`; `P=$W/greek-page-ocr`; `C=$W/census_05_20261020/attempts/full-split-001/current`. Live evidence below was read through `ssh clariden`: directory listings, metadata, bounded heads, small JSON receipts and small-file hashes only. No large-file rehash, processing build, submission, remote write or spend.

Sources: [D = TRAINING_DIRECTIONS](../../../../../greek-page-ocr/docs/ocr_program_2026-10-06/TRAINING_DIRECTIONS_20261016.md), Track entries S3/M/C2/P1/G (lines 31, 38–41, 46, 50, 54); [L = 7 October literature review](../../../../../greek-page-ocr/docs/ocr_program_2026-10-06/LITERATURE_REVIEW_ASTRA_20261007.md), §§1,3,4 and Experiment 3; [R = E3 directions literature review](../../../../../greek-page-ocr/docs/ocr_program_2026-10-06/reviews/ASTRA-E3dir_review_1.md), §2 D3/D5–D10 and “Three implementation choices”; [programme](../../../../../greek-page-ocr/docs/ocr_program_2026-10-06/POST_CLEANUP_PROGRAMME_20261019.md), §§3.5,5b,7. Paths to the sibling repo in these links are resolved from this document's directory.

## C2

D C2: “auxiliary loss on/off, inference unchanged. After C1.” R D10 specifies **0 new lines**, same compact model/NFD head, resize, mixture and decoder. L §1 / Experiment 3 keeps training texts fixed and removes the auxiliary head at inference. These specifications **do not define** word targets, tokenisation, auxiliary codec, lexicon or pretrained semantic embeddings. L's optional lexicon discussion is a decoder proposal, not a C2 requirement.

A1 therefore needs a declared target encoder over the existing labels; labels suffice for a label-derived sequence head, but that is conditional on Q1, not an already-selected implementation. No separate C2 target receipt was located. Package: bind row IDs, exact label bytes, codec/tokenisation and loss configuration; 0 additional crops. At the full available real pool, one pass is 364,871 labels. A 4-byte token-ID cache with mean length `L` is `1,459,484 × L` bytes plus keys. Preparation time is `364,871 / label_rows_per_second`; throughput is unmeasured. No image-production job; target materialisation can be a CPU job or loader operation. Dependency: C1 and the pinned wave control.

Exposure: inherit the completed subset audit only for identical row/crop/label identities; new vocabulary text, if selected, requires an additional edition/text audit. **Q1:** what auxiliary prediction target, segmentation, codec and loss does C2 use; does it require any external semantic resource?

## P1

D P1 requires a “train-only, edition-deduplicated” manifest of unlabelled scanned line crops, excluding the **1,557 label-in-holdout flags** and every held-out book/edition. Its supervised extra-training control uses labelled train rows, never rejected labels; match measured GPU-seconds and optimizer steps, or match seconds and disclose the step difference under the spec's “exposure-matched” terminology. Same subsequent 8-epoch run; ≤56 GPU-h pending probe. L §4 and R D9 provide the unlabelled-image rationale, not permission to include held-out imagery.

A2 does not exist as a sealed P1 pool. Eligible *candidates*: admitted train W1/W2 **168,637**, admitted v_c **196,234** (364,871 total), after edition deduplication and exposure audit. HOLD/DROP train crops can be image-only candidates when rejection concerns labels, but require an explicit geometry/eligibility rule and exclusion audit; they are not automatically safe. Other unlabelled page lines need extraction, crop ownership, edition identity and hashes first. Born-digital E1 is outside “scanned” P1's stated pool. The historical **84,799 initial rejects** are a different population from census_05 HOLD/DROP; the two must not be added without identity deduplication ([data plan §1/§2](../../../../../greek-page-ocr/docs/ocr_program_2026-10-06/DATA_PLAN_v2_20261016.md)). Their historical raw-wave paths were not found under either `$W/greek-ocr-toolkit/docs/{records/harvest,harvest}/harvest_big`; custody of a P1-ready reject pool: none.

Reusable custody: C summary binds `admitted_train.jsonl` SHA `fe955d00…`, **7,870,677,512 bytes**; `admission_records.jsonl` SHA `0acfb1c9…`, **10,412,166,460 bytes**; **592,466 input rows**, global dispositions ADMIT 457,991 / HOLD 78,040 / DROP 56,435. These totals include non-train rows and are **not** P1 yield. Summary SHA `096b18a8…` is pinned in [inputs.json](inputs.json).

Package inputs: those records, split/edition map, v2 dev/test document identities, all locked editions and historical holdout flags, seal04 keys/hashes, original crops (REL3 paths for W1/W2). CPU job: select/deduplicate, bind every crop and publish manifest/exposure receipt. At an explicit 256 bytes/manifest row, the admitted candidate ceiling is **93.41 MB**; no image copy required. One 10.412 GB parse at the SCALE1 synthetic proxy **110.76 MB/s** is **94 s**, not a measured ETA; crop audit at assumed **10 ms/open** is **3,649 s ≈61 min** for 364,871 candidates. Additional candidates add `N ×256 bytes` and `N ×10 ms`. Pretraining GPU time requires its throughput probe; ≤56 h is a campaign ceiling, not data-preparation time.

Exposure: **new audit required**, including crops never supervised; no unknown-edition candidate qualifies. Subset receipts cannot cover added rejects. **Q2:** which rejection reasons/other-line sources enter, what deduplication selection rule applies, and what objective, masking schedule, exposure and epochs bind P1/control? Dependency: C1.

## S3

D S3: “per-line CTC loss weights from an error model calibrated on book-separated validated examples”; **after S2 validated corrections**, weighted/unweighted identical rows. R §2 additionally requires calibration by script/mark; raw confidence or model agreement is not correctness truth.

R1 live availability, **available / unavailable**:

| Parent | Rows | `evidence.confidence` | `evidence.source` |
|---|---:|---:|---:|
| W1 | 50,736 | 50,736 / 0 | 50,736 / 0 |
| W2 | 117,901 | 117,901 / 0 | 117,901 / 0 |
| v_c (`collection-v2-train`) | 196,234 | 0 / 196,234 | 196,234 / 0 |

Important schema boundary: A3's emitted tag rows contain keys/source/edition/classes/facet tags/crop identities, **not numeric confidence**; the receipt counts confidence availability in the bound census. Recover W1/W2 values by census join ([scale.py:102](scale.py:102)). Missing v_c is not zero or calibrated confidence.

A4 exists: `$W/collection_v2/jsonl/admitted_all_v2.jsonl`, **248,552,165 bytes**, **271,987 rows** per [v2 CLEAN_REPORT](../../../../../greek-ocr-toolkit-mainwt/docs/records/harvest/collection/v2/CLEAN_REPORT.md); R2 binds its SHA. Live first row has confidence **0.9245044408333334**, split **dev**, illustrating why a train-only join is mandatory. Older `$P/out/e3/records/{round1,cyrillic}.meta.jsonl` heads each contain **20/20 numeric confidences**; sizes **12,632,569 / 2,443,096 bytes**. These are samples, not v_c coverage. The sidecars are not outputs bound by `prepare_binding.json`; custody of those derivative confidence sidecars: **none located**. The original source has custody; join current v_c by wave/ID and crop identity, report recovered/missing/conflicting counts, including codec-recovered rows. Do not infer 196,234/196,234 coverage.

A5 needs validated S2 examples with book-separated calibration/validation memberships, error targets, calibrated model and per-parent row-weight sidecar. No qualified S3 package found; sf7/RU1/N1 evidence alone is not that receipt. Package: CPU source join, calibration fit (GPU only if the selected model needs it), weight export and audit. At **128 bytes/row**, 364,871 weights ≈**46.70 MB**. Source scan proxy `248.55/110.76=2.24 s`; census pass `7,870.68/110.76=71.06 s`, excluding joins/fit/audit. Calibration sample size and model time remain unspecified. Exposure: new book-separated training calibration audit; dev/test benchmark images must not train the error model. **Q3:** calibration sample/split/model/features, weight transform and missing-v_c policy? Dependency: validated S2.

## G

D G requires orthography-specific capital marks, bold/condensed/letter-spaced caps, old-style numerals, **2→5% light-on-dark**, a per-mark gate audited on **2,000 paired lines**, and a new explicit leader-dot GT/crop contract. Programme §5b and L §3 add conditional x-height/stroke/contrast/blur/leading/skew/padding statistics and **whole-page raster-only twins**, with GT transformed alongside geometry.

A6 exists in `$P/factory/{src,recipe.v5.json,recipe.v6.json,appearance_band.json}`, `$P/assets/fonts`, `$P/data/sources.json`; binaries at `$P/factory/target/{release-e2,e4-grave}/linefactory` (the generic `target/release/linefactory` is absent). R3 binds legacy recipes/appearance/font inputs; the synthetic build receipt lists **64 font stems** and hashes. Legacy appearance band derives from **58 crops**, contrast/ink/polarity only, without the required conditional train-only measurement manifest. `data/sources.json` is a catalogue, not proof that every raw corpus object is present or benchmark-clean.

The live v6 recipe SHA `789731ac…` specifies **`estia_word_final_grave_v1`** and **0.02 polarity**, not the full new bundle. `$P/out/e4/wave1a/grave/` contains `DO_NOT_TRAIN.md`, qualification evidence and synthetic output; it is not evidence of qualified A8. A7–A9 have no located family receipts. Required display/old-style glyph coverage and licences need binding; presence of fonts is not coverage qualification.

Package: A7 train-only image measurements conditioned by era/type/source; A8 versioned text corpus and exclusions, fonts/hashes, recipes/seeds, rendered labels/crop ownership, rejection/resampling ledger and 2,000-pair audit; A9 accepted train PDF raster/labels/polygons, coherent page degradation, detector crops, transform and ambiguity ledger. CPU render/measurement jobs; detector inference may require a GPU job, depending on implementation. No new OCR API calls specified.

Arithmetic only: legacy A12 compression is **5,815,265,039 /190,486 ≈30,528 bytes/line**; 4,000 audit images ≈**122 MB**, or `B ×190,486` variant lines ≈**B ×5.815 GB** if that legacy count is reused (not a specified wave-3 size). Rendering time `B ×190,486 / measured_lines_per_second`; audit `2,000 × seconds_per_pair`; no measured rates. A7 on N crops costs `N / measure_rate`; A9 on P pages with D degraded variants costs `(D+1) ×P × raster_bytes_per_page` plus crops, and `D ×P × (degrade_seconds+detect_seconds)`; P/D/resolution unspecified. R D7 gives **4–7 engineering days**, L recommendation 5 approximately **1 week**, both planning estimates, not job ETAs.

Exposure: **new** audit across calibration scans, synthetic text editions, twin pages and output hashes; old exclusion manifests predate seal04. Dependencies: frozen data/control; rendered mark/spacing/polarity/ownership qualification and leader contract before leader exposure changes. **Q4:** bundle versus separate variants (D Track G versus §2b), sample sizes and real-domain measurement strata? **Q5:** leader GT and damaged/partly visible glyph target policy, mark acceptance thresholds? **Q6:** twin source pages, degradation severities, geometry scope and count?

**G-AUDIT 20 Oct** (`g_audit/G_AUDIT.md`, commit f65fe2696; metadata evidence only): coverage 0 yes / 920 partial / 368 no over 1,288 cells; 7 gap groups. **Prerequisite (coordinator, 20 Oct):** the renderer text path moves to codec v2.1 before any G ablation; codec v1 rejects ѣ (111 occurrences) and ј (87) in the seal04 references, which affects the Cyrillic classes (gap 7). The full corpus text-exposure scan (7 raw corpora + corpus.jsonl + pool.jsonl) is packaged separately as GEXP.

## M1

D M1: “50/50 → 50/40/10 synthetic/scanned/born-digital”, train-only, matched to removed scanned draws by **script class and length bucket** (R D3). A10 is `$P/out/e1_run4/real/train/`, **19,657 rows**, **5 shards /446,374,678 bytes**; val **359** and reserved **3,600** must not enter replay. R4 provides build/shard custody. Its `build_info.audit_ok=false` is recorded; custody is not an audit pass.

Older `$P/out/e4prep/mixes/m1_replay10.{json,draws.json.gz}` exists: draw file **1,490,637 bytes**, **8 epochs**, mix SHA `e7c71129…`, draw SHA `3259cd4d…`, validation receipt SHA `22b0777d…`. It checks E1 test document/ID disjointness, matches **script × ceil(width/128)×128**, and redistributes across supported strata; **31 unavailable strata** stay scanned ([m1_mix.md](../../../../../greek-page-ocr/out/e4prep/m1_mix.md)). It is tied to the old release, not A11 for wave 3.

Package: reuse A10 shards; join edition/crop provenance to current blocked sets; regenerate exact matched positions against selected SCALE1 pool and unchanged synthetic positions. At old draw budget **428,872**, each epoch has synthetic **214,436**, scanned **171,549**, replay **42,887**; eight epochs **343,096 replay draws**, **3,430,976 total**. Existing compressed-plan density extrapolates to ≈**1.49 MB** at that same budget; time `3,430,976 / draw_validation_rate`, plus shard reads. CPU job, no rendering/GPU data job. Exposure: **new seal04 edition/key/crop audit**, beyond old E1 test-disjoint proof. Dependencies: F1/control/pending subsets. **Q7:** use which length bucket, and what policy for unsupported matched strata on the new pool?

## M2

D M2: **40/50/60%**, fixed total draws and real pool; then **70% ×4 epochs →30% ×4**, identical cumulative per-image exposure and published manifests. L §4/R D6 establish no universal fraction. A12 exists at `$P/out/e1_run4/synthetic/train/`: **190,486 rows**, **47 shards**, **5,815,265,039 bytes**, R5 custody. Historical `$P/out/e4/wave1a/mixes/syn{40,60}.json` reweight these same shards; **separate synthetic shards per fraction are not required by this spec** ([e4_wave1a.py:60](../../../../../greek-page-ocr/bench/e4_wave1a.py:60)).

A13 needs new parent-bound mixes, per-epoch row IDs/order, unique/repeat counts and a curriculum schedule proving per-image exposure equality. CPU job; **0 new image bytes** if reusing A12. At D=428,872, unrounded synthetic counts/epoch are **171,548.8 /214,436 /257,323.2**; curriculum **300,210.4 /128,661.6**. Eight-epoch 50% total is **1,715,488** synthetic draws; integer allocation must preserve that total for the curriculum. Three fractions plus curriculum require **4 ×8 ×D =13,723,904 draw entries**; at 16 bytes/index entry ≈**219.58 MB** before keys/metadata. Time `13,723,904 / draw_rate`, unmeasured; no rerender time. Exposure: new synthetic source-edition/text audit against seal04, plus pending real subset audit; old shard custody does not prove current exclusions. **Q8:** exact integer/cumulative per-image allocation and control binding? Dependency: F1/control, fractions before curriculum.

## M3

D M3: Cyrillic real **3.1→6% after V**; parliament **25% cap first**, renormalise non-parliament classes; grouping **wave**; separate capped/uncapped contrast. A3 already supplies per-row class/source tags and parent IDs for all **364,871** rows; no new class-labelled crop pool is required. Do not substitute benchmark `primary_class` for the requested script quota without an explicit mapping: primary classes include length/font/geometry strata. Original source/census metadata supplies script and legacy wave joins.

A14 package: bind that mapping, wave counts/cap order, exact quotas/draws and repetitions against the pinned subset/control. CPU job, 0 new images. At 50% synthetic and D=428,872: real **214,436**, 6% Cyrillic ≈**12,866.16** versus 3.1% ≈**6,647.52**, before integer allocation; 8D=**3,430,976 entries/arm**, ≈**54.90 MB** at 16 bytes/index. Time `8D / draw_rate`. Exposure: completed subset receipt can cover unchanged rows; new draw receipt must bind it. Tags receipt alone is not a crop exposure audit. **Q9:** mapping from current script/source metadata to the historical class/wave quotas and exact baseline shares? Dependency: V and F1.

## M4

D M4: “α 1 → 0.5 on wave-level counts, cap applied after temperature; only after M3.” R specifies `p_i ∝ n_i^α`. A3 supplies source/parent identity; legacy v_c's individual waves require source/census metadata join, not treating its single parent as one wave. No new crops or new SCALE1 tag generation needed.

A14 also needs wave count table, `n_i^α` probabilities, post-temperature cap/normalisation ledger and exact drawn rows; CPU job. Storage/time same **8D entries /54.90 MB per arm** proxy as M3, 0 new images. Exposure: inherit audited subset identities and bind new draws, pending subset receipt. **Q10:** exact mapping of W1/W2 source identities and legacy v_c sources into the declared wave grouping? Dependency: M3.

## Custody references and effort basis

- **R1:** `$W/scaling_w3/tags/scale1-c05-002/TAGS_RECEIPT.json`, SHA **`e4a155ebf5a2b13e28b5b3a45f3244bc0d2612e1704b00df3b24362a03335d39`**; `status=ok`; output `train_tags.jsonl.gz`, **20,522,877 bytes**, SHA **`4a2f4ccbb7af923287dfb7a8bc380fb81b0516c2735766c1e6f623b5adadd71a`**. Receipt hash recomputed; output size checked, large source SHA accepted from receipt. [SCALE1C](SCALE1.md) documents the stale W1/W2 tag crop paths: resolve through REL3 originals, not removed census input paths.
- **R2:** `$P/out/e3/prepare_binding.json`, live SHA **`19696512cdcf1f7921a78daa7fb60871f8483a30c1bd657f06d782c487e6a637`**, binds `$W/collection_v2/jsonl/admitted_all_v2.jsonl` SHA **`ba27767a4bbac44a155ee1cd8c982e246441d03ee6484cbcbba378b920335018`**. Source size/head verified; source not rehashed.
- **R3:** live recipe v5 SHA **`2f228950e9a508b5e130e82ce5b89de2b911be4a23872c3acc7f53e83c59dce7`**; v6 **`789731ac9f5b3e28ac60542f75b2117beede8361582efcce99641a454f58c7c4`**; appearance **`3f7e7c5c2f58507d7bafdd580afcf6e71aec5ebc5bbede1a1349bd382d2099f7`** (also in real build receipt). Fonts provenance SHA **`eea27274b160f2b07f2ae2fee75311760656016c8416e06a40081298f4d24edd`**; source catalogue **`8e2d816b2c95ed468850ac0068910ce8b68ff0a28bc8e00907b31b7e4b3f21fe`**. These bind legacy inputs, not a complete v6 campaign corpus.
- **R4:** `$P/out/e1_run4/real/build_info.json`, live SHA **`dfd1ff0c17edbff898b550d173a6f8e175ebf1794a811f65b070b8ebb0e0e73e`**, `partition_id=o5-docs-v1`, records/crop/shard hashes and split counts. Receipt and shard inventory also bound by [wave1a release.json](../../../../../greek-page-ocr/out/e4/wave1a/release.json), release binding `af1ff902…`. Shards statted, not rehashed.
- **R5:** `$P/out/e1_run4/synthetic/build_info.json`, live SHA **`495453433c2efff88a8a0d7d39de32e856d878d815b923dbf3eb9354411bfbff`**, `audit_ok=true`, v5 recipe/shard hashes; counts train **190,486**, val **9,208**, reserved **3,999**. Only train is A12. Same release receipt binds shard inventory; shards statted, not rehashed.

Every new training input requires **0 dev/test editions, 0 seal04 keys, 0 seal04 crop SHAs**, with crop-byte binding; tuning/evaluation sets remain distinct. Current full-crop SCALE1 audits are pending, not certified by this inventory. Estimates above are arithmetic, not measured ETAs: [SYNTHETIC_THROUGHPUT.json](SYNTHETIC_THROUGHPUT.json) supplies 110.76 MB/s parsing; [SCALE1.md](SCALE1.md) supplies the explicit unmeasured 10 ms/crop assumption. Draw/label/render/measurement rates require bounded probes in later authorised packages. Programme §7 requires deployment-ready code/exposure review before each family's launch; no such launch is performed here.

## Guarded commit list

Review only these exact paths; **no staging or commit performed**:

- `docs/harvest/collect_v3_admission/scaling_w3/DATA_NEEDS.md` — this inventory, including this allowlist.
- `docs/briefs/DATA_NEEDS_wave3_novelties.md` — existing coordinator brief, unchanged.

No other path is in scope; preserve all pre-existing tracked and untracked changes. Ten open decision groups are Q1–Q10 above; none is resolved here.

DATA_NEEDS: done | families 8 | artefacts 14 (exist 5, with custody 5) | open decisions 10 | no builds, no jobs
