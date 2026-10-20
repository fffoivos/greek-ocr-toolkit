# BENCH02D — offline benchmark 0.2 draw tool

Implemented `extract`, `draw` and candidate `readout`, without network, SSH, crop reading, model calls, spend, submission, staging, commit or push. Local draw/test artifacts stay inside this directory; extract/readout accept an explicit absolute output root, and the batch wrappers require scratch outputs. Time in `draw_plan.json` comes from `TZ=Europe/Athens date`. The requested model/effort is a session setting; this tool does not launch or select a model.

Read programme §3.1–3.3 in full at `~/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/POST_CLEANUP_PROGRAMME_20261019.md` and night-plan P5 at `~/Projects/greek-ocr-toolkit-main-next/docs/programme_20261019/NIGHT_PLAN.md`. The programme's per-class table governs the implementation.

## Rule discrepancies and decisions

* Coordinator ruling, 20 October (BENCH02F): the 16-entry class table stands at **2,460 test / 615 dev**. Nominal 20% overdraw is **3,690**, within P6’s **3,700** checks. Per-subgroup ceiling after dev fonts 13/12 gives 16/15 candidates and **3,691** total targets (one extra rounding slot); still within budget. Sizes are resolved; quotas are unchanged.
* The sample is **3,885 HOLD + 115 DROP**, not all HOLD. Zero rows are admitted. Only **114** have exactly the sole split-identity reason. Other reasons are never waived.
* Numeric/table classification follows §3.2's third column: numeric grammar **and explicit cell flag with A ≤ 6**, plus >1 alnum. Numeric text alone is a secondary observation, not evidence of a cell. Missing cell/A makes that numeric tag unavailable. Non-cell evidence is also required for short lines. The brief's shorthand omits these conditions; §3 wins.
* Segmentation baseline curves are present: their base-minus-mean median gives physical x-height; endpoint slope gives angle, and maximum baseline departure from that chord gives curve deviation. These are measurements of existing segmentation evidence, with no image access. No snapshot proxy x-height is substituted. The sample uses legacy segmentation tool_version 0.5, not the programme's named 0.9-s2/s3; receipt provenance remains visible in the inputs. The census_05 source mapping is recorded below; full live availability remains unmeasured.
* Cap scope is global across classes and all ordered candidates, including replacements: ≤4 per edition and ≤12 per evidenced series. Missing series is reported, never used to exclude rows or invent a series. Gazette identity stays at issue/edition level. The supplied maps do not identify book series, so actual cross-edition series compliance cannot be certified until that evidence exists.
* Within each quota class the fixed precedence below assigns one primary class. Secondary facets never consume another quota. Missing/undefined tag evidence is reported; there are no additional quality/confidence/length/deduplication filters.

## Dry run

Inputs: four independently grepped 2,000-row census_02 sample files; both pinned W1/W2 snapshots; SPLIT2 row split and edition map, supplemented by SPLIT1 edition metadata; all three original v2 manifests; the registered locked-eval manifest and its relevant ID files. Supplied sample and snapshot checksums were verified; see `input_checksums.json`. All input byte hashes and code hash are in `dryrun_census02/draw_plan.json` and the extract receipt.

Keyed join is `(binding.parent_id, binding.id)`, independently of order: **W1 2,000/2,000; W2 2,000/2,000; total 4,000/4,000 (100%) in both directions**, zero unmatched diagnostics. Diagnostic decisions never replace the authoritative decisions file. All 4,000 sampled rows are from `bsb_poly1850`, so this sample cannot establish source-wide coverage.

**Pre-filter supply = 114 rows**, before split eligibility and edition exclusions. Of those, **63** belong to excluded editions and **51** to TRAIN editions. Therefore test/dev supply is **0/0**, candidates **0/0**, classes filled **0/16 test, 0/16 dev**. This is an empty, deliberately unqualified dry draw, not a sealed benchmark. **99 forced-test editions** are excluded across the full split map. No edition or series cap is reached.

Pre-filter primary classes are 44 curved/skewed, 14 font extremes and 56 unclassified (missing cell evidence prevents assigning the remaining short numeric rows). Counts are metadata-derived, not pixel verification. See `dryrun_census02/COUNTS.md` and `counts.json` for quotas, deficits, supply, secondary facets, class × source × edition counts, excluded edition IDs and cap hits.

## Historical BENCH02E tag availability in census_02

The following table and census02 artifacts are preserved BENCH02E results, not a BENCH02F rerun. Availability counts cover all 4,000 decision/diagnostic joins, not only the 114-row pre-filter supply. `unavailable` differs from an observed negative.

| Field / tag evidence | Present / missing | Use |
|---|---|---|
| `expectations.orthography`, `expectations.scripts`, `expectations.languages` | present 4,000 | Greek orthography and expected scripts; languages all polytonic Greek |
| `final_inventory.{greek_letters,latin_letters,cyrillic_letters,letter_count,mixed_words}`, `characters`, `final_text` | inventory present 769, missing 3,231; final_text present 4,000 in source decisions | script tags unavailable where the final inventory is absent; slim export retains only script/letter counts, characters (inventory value, otherwise final-text length), mixed-word flag and text-derived flags |
| diagnostic/snapshot `source`, `primary_class` | present 4,000 | bsb/ia poly1850, headings classes |
| CENSUS3 ru/sr/bg/uk document language | missing (including the 2 collector-class Cyrillic rows, whose final inventories are absent) | modern-Cyrillic tag unavailable where inventory/language evidence is absent; script alone never determines language |
| `cell_flag`, numeric `A` | missing 4,000 | numeric_cells unavailable for 129 numeric-grammar rows; short unavailable for all 4,000 |
| `segmentation.result.frame.{normalization_cw,source_width,source_height}` | present 4,000 | source h>w or 90° turn; tag available, no inferred turn from bbox |
| `segmentation.result.evidence.detected_rows[side=main].curves.{base,mean}` | present 4,000 | x-height from median base−mean; small ≤10 / large ≥30 px |
| same main baseline `curves.base` | present 4,000 | absolute angle ≥2° or chord deviation ≥8 px |
| snapshot `xheight`, `xheight_method`, `row_xheight` | present; distinct proxy/row measurements | diagnostic only; never substituted for segmentation x-height |
| `primary_class=headings_caps` + final-text case inventory | present | all-caps headings branch |
| explicit `letter_spaced` | missing 4,000 | letter-spaced branch unavailable; caps branch remains usable |
| `leader_runs`, `emdash_label_count` | present | explicit leader/dash facets; no punctuation-share cutoff invented |
| final punctuation share | measurable; qualifying threshold missing | `punctuation_heavy=unavailable` |
| `confidence` + `confidence_scope` | present 4,000 (DocAI symbol mean) | reported only; low-confidence cutoff unspecified |
| physical `ink_density`, calibrated low-density/low-confidence rule or explicit evidence-bound `degraded` | missing | `degraded=unavailable` 4,000; `density_ratio` is not an ink-density substitute |
| edition-map `series` / `book_series`, including metadata records | missing | `series=null`, limitation reported; titles, volumes and journals are not inferred series |

## BENCH02F census_05 availability and exact adapter paths

Read-only source: `~/Projects/greek-ocr-toolkit-main-next/greekocr/harvest/{line_pipeline.py,line_pipeline_census.py,line_pipeline_sources.py,line_pipeline_adapters.py,numeric_cells.py}` and `tests/{test_content_gate.py,test_line_pipeline.py,test_numeric_cells.py}`. `census05_evidence` documents the same paths. Full census_05 receipts have not been read; this is a producer-schema audit, not a live availability count.

| Decision / diagnostic path | Adapter and availability |
|---|---|
| `evaluation_diagnostics.row.crop_bbox` | Gate `line_pipeline.crop_aspect`: `A=max(width,height)/min(width,height)`; `cell_flag=(A<=6)`, including tall crops. This exact gate calculation is reproduced without opening crops. Missing bbox means unavailable. The gate does **not** emit a standalone cell flag or universal A. `decisions.reasons[].A` occurs only for `single_character_cell`; it is not a universal measurement. |
| `numeric_cells.classify_cell(...).is_cell` | A separate numeric/small-image descriptor; not emitted by line_pipeline and not substituted for gate 0.3 cell status. |
| `decisions.raw_inventory.{scripts,greek_letters,latin_letters,cyrillic_letters,letter_count,mixed_words,characters}` | Gate script inventory. Use `final_inventory` when present, otherwise the gate raw inventory (early-return `final_text` remains raw). Keep counts/flags only, never a word inventory. |
| `decisions.expectations.{languages,scripts,orthography,orthographies}` | Declared document/page/source expectations; scripts never imply ru/sr/bg/uk language. |
| `evaluation_diagnostics.row.doc`, `.book_id`; `decisions.binding.book_id` | Exact CENSUS3 Serbian allowlist only: `cyrillic:7235f8d0`, `cyrillic:975289f3` → `sr`. Read-only `git show sol/census-v2-serbian:greekocr/harvest/admission.py` (`SERBIAN_DOCUMENTS`), corroborated by `docs/harvest/collection/v2/census2_document_language.json`. Branch commit `504bdb1e13bed4883bd8d88c1ac3e795952d79c9`. No substring, source, script, orthography or edition inference. Other missing language evidence stays unavailable. |
| `evaluation_diagnostics.row.confidence`, fallback `.docai_confidence`; `.confidence_scope` | Numeric DocAI mean line confidence; **degraded iff <0.89**, or the density branch below. Export `evidence.confidence` as number/null. |
| ink density | **Absent** from inspected gate/numeric_cells/line_pipeline producers. `ink_pixels`, `density_ratio`, aspect and component counts are not substitutes. Export `evidence.ink_density=null` when absent; census_05 degraded therefore uses confidence only. |
| `evaluation_diagnostics.row.leader_runs`, `.emdash_label_count` | Retained collector N1 fields; slim export reduces leaders to a boolean. |
| `decisions.routes.dashes.evidence.dashes` | Actual pipeline N1 dash-tag path from `automatic_result`; reduce to `evidence.dash_tag` boolean. Nonempty leaders OR positive emdash count OR this flag fires the leader/dash branch. |
| `decisions.final_text` | Export numeric `text_facets.punctuation_share`: characters that are neither letter, digit nor whitespace / non-whitespace characters (empty denominator → 0). **punctuation-heavy iff share ≥1/3 OR N1 leader/dash tag**. This is a secondary facet; class precedence stays unchanged. |
| `split2/edition_map.jsonl`: `edition_id`, joined via row split | Edition identity present; supplement with SPLIT1 metadata as before. Edition identity is not book-series identity. |
| `letter_spaced`; edition `series` / `book_series` | No new producer found. Missing evidence remains unavailable/null and is reported; no substitution, invented series or additional filter. |

The density implementation accepts explicit numeric density evidence for fixtures/future receipts. When present, it computes p25 separately for each source over **all extracted census W1/W2 rows before admission, splitting or exclusions**, using linear interpolation at `(n-1)*0.25`. `draw_plan.json.degraded.density_p25_by_source` records each p25 and row count; density **strictly below** p25 fires, equality does not. With the inspected census_05 schema that map is empty and the density branch is explicitly unavailable. No density is derived from pixels or collector proxies.

Missing class/subgroup evidence produces deficits in `counts.json` (including subgroup quotas, targets and deficits), never transfer to another class/language/font group. Missing series is a reported cap-verification limitation; it does not exclude rows. Ordinary script classes remain fallback classes after specialist strata under the unchanged precedence.

## Deterministic assignment and draw

Precedence (first available true tag wins): vertical_turned → font_extremes → degraded → curved_skewed → numeric_cells → caps_headings → leaders_dashes → short → long → greek_latin → historical_russian → modern_cyrillic → latin → poly_dictionary_journal → polytonic → monotonic. Unclassified rows are reported; no other class absorbs their quota.

For each split/class, seed `bench02:<split>:<class>` initializes Python's seeded PRNG. Sort then shuffle sources, editions within each source, and row keys within each edition. Take one row from each source per round, advancing the persistent edition deque within that source. Exhausted/capped editions cease supplying rows; other sources continue. Only the named split's rows enter each pool. Quota processing follows precedence so global caps have a recorded deterministic allocation order. `draw_plan.json` records this order, caps, quotas, input hashes and code hash.

Modern Cyrillic has fixed ru/sr/bg/uk subquotas (40 each test; 10 each dev), with 20% overdraw per subgroup. Fonts have 50 small / 50 large test quotas and **13 small / 12 large dev quotas**, per coordinator ruling. Per-subgroup 20% overdraw gives **60/60 test and 16/15 dev** candidate targets. There is no transfer between missing subgroups or between classes. For P6 replacements, filter ordered candidates by split, class and source, then take the next unused rank.

Edition exclusion uses the edition map's preserved `leakage_matches` (including SPLIT1 acquisition-metadata identity witnesses), plus current direct v2 document/row and registered locked-ID membership. Relevant locked/eval ID files are checksum-checked. Other release-exclusion classes (e.g. separator ambiguity) do not become additional draw filters. Existing edition witnesses are not a new semantic-identity audit.

## Submit blocks: census_03 mechanics and census_05 real run — not executed

(a) Mechanics dry run, using the same `extract.sbatch` and one input-directory variable:

```bash
B="$(pwd)/docs/harvest/collect_v3_admission/bench02"
CENSUS=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03/current
OUT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02/census03
bash "$B/submit_job.sh" extract "$CENSUS" "$OUT"
```

After transfer, use the explicit draw command in [run_dryrun_census03.md](run_dryrun_census03.md), with `--dry-run`: the pool contains exactly rows whose **sole reason** is `split_or_edition_identity_unresolved`. This is a mechanics test, not a benchmark qualification.

(b) Real census_05 run, the same sbatch; input path left to the coordinator:

The census_05 output directory has not been supplied and does not yet exist in this workspace. `CENSUS05` must be set by the coordinator to the completed, receipt-pinned directory containing `decisions.jsonl` and `evaluation_diagnostics.jsonl`; the commands do not invent a deployment path.

On Clariden, from the deployed repository root, after setting that variable:

```bash
: "${CENSUS05:?set to the completed census_05 directory}"
B="$(pwd)/docs/harvest/collect_v3_admission/bench02"
OUT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02/census05
bash "$B/submit_job.sh" extract "$CENSUS05" "$OUT"
```

`extract.sbatch` requests account a0140, partition **normal**, one node, one task/CPU, **01:00:00**, no memory option. The wrapper supplies the absolute log path `$OUT/extract-%j.log` through `sbatch --output` and exports the deployed `BENCH02_DIR` for Slurm's spooled script. Both jobs use `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python`; the tool asserts Python >=3.10 at startup. No partition probe or job submission was performed. SQLite stores only slim diagnostic evidence and seen keys in a temporary database beneath the output directory, so neither full multi-GB file is loaded into memory. It streams each input and joins by both identity fields, reports both join rates, and removes the temporary database on normal completion.

After extract completes, stage `tags.jsonl.gz` and `tags.jsonl.receipt.json` into the same relative `bench02/census05/` directory on the draw machine. The draw machine needs the split maps, W1/W2 snapshots and exclusion inputs under the configured Projects root. Then run:

```bash
# Default is "$HOME/Projects"; set PROJECTS_ROOT if staged elsewhere.
bash docs/harvest/collect_v3_admission/bench02/run_census05_draw.sh
```

The wrapper runs the tool's `draw` subcommand with every input path explicit. It prefers SPLIT2; if absent it uses SPLIT1 `row_split_proposal.jsonl.gz` and `proposed_split`. It does **not** pass `--dry-run`; only `admitted=true` W1/W2 rows enter the production pool. The production extraction receipt carries the original census input hashes into the draw plan. No images are needed for either stage.

To reproduce this dry run, execute the same `extract` command with the two local `census02_sample/decisions_{W1,W2}_2000.jsonl.gz` files and the corresponding diagnostics, passing `--output-dir "$(pwd)/docs/harvest/collect_v3_admission/bench02/dryrun_census02"`; then run `bash .../bench02/run_dryrun.sh`. `BRIEF.md` preserves the full task request.

## BENCH02E changes

* `tags.jsonl.gz` contains only parent/row/crop identity, admission/disposition/reason codes, split if supplied, classifier evidence and sufficient text statistics. It contains no final text, full inventory, word lists or expectations provenance. `text_facets` stores script/letter counts (preserving missing evidence), character count, punctuation share, mixed-word flag, numeric-grammar flag, upper/lowercase flags, orthographies, scripts and languages. The evidence fields follow the availability table above; geometry curves reduce to their existing physical measurements, and leader payloads reduce to a flag. No draw rule, precedence, quota, admission condition or cap changed; no filter was added.
* `draw` reads the slim facets; long uses characters and short uses letter_count with the existing explicit non-cell requirement. BENCH02D full tags remain readable. Candidate records contain parent/row, split/source and edition identifiers, class, tags/evidence facets and rank; text, crop payloads and series metadata are omitted.
* `readout --candidates /absolute/candidates.jsonl --census-dir /absolute/census --output-dir /absolute/scratch/output` streams decisions and diagnostics, keeps only candidate records, and writes `candidates_readout.jsonl`. Use `submit_job.sh readout CENSUS OUT CANDIDATES` on Clariden with absolute paths. Text and crop metadata are retrieved for the approximately 3,700 candidate lines only. Crop files come from CROPS4 `--include-heldout`.
* The complete census_03 coordinator commands are in [run_dryrun_census03.md](run_dryrun_census03.md). They are prepared only. The 4,000-row bsb_poly1850 sample cannot establish real class supply; the full census_03 dry run is the real test.

Local measurement (`python3 -B .../bench02/measure_extract.py`), Python **3.11.3**, `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3`: 4,000 decisions + 4,000 diagnostics streamed and joined in **1.258059 s**, including input hashing and SQLite/gzip output; **6,359.00 input rows/s** (3,179.50 decision/diagnostic pairs/s). The four compressed inputs total 26,307,186 bytes. Projection to 593,000 + 593,000 input rows (approximately 9 + 7 GB): **186.51 s**. Three times that is 559.52 s; rounded up to a 15-minute boundary gives **00:15**, below 02:00. This is a local compressed-sample extrapolation, potentially warm-cache; Clariden storage and full-census compression are unmeasured. BENCH02E used 00:15. BENCH02F sets **both extract and readout to 01:00:00**, one node on `normal`, because Clariden Lustre I/O for roughly 16 GB of streamed input is unmeasured. The Mac extrapolation is not a Lustre measurement.

Sample slim gzip: **376,840 bytes / 4,000 = 94.21 B/row**; projected **30.1923 MB** (decimal) for **320,479 rows**, below the 40 MB target. Content diversity can change the full-census compression ratio. The machine-readable measurement is [BENCH02E_measurements.json](BENCH02E_measurements.json). Slim-vs-full candidate parity includes a nonempty fixture using the real sample text/evidence with synthetic admission/split/edition assignments; this tests transport equivalence and is not real class-supply evidence. The original census_02 dry draw remains empty.

## Validation and open questions

Run `python3 -B docs/harvest/collect_v3_admission/bench02/run_tests.py`. The stdlib test suite checks deterministic bytes/order, reversed input order, all class/split overdraw targets when supply permits, global edition/series caps, source/edition rotation, no subgroup substitution, unique primary class, exact test/dev assignment, v2/locked exclusions, production admission versus the sole-reason dry pool, physical-evidence availability, full-sample streaming/in-memory parity, unordered partial joins, W1/W2 scope, symlink-safe output confinement and normal-partition job directives. All 20 original tests remain, with transport/partition assertions updated; six BENCH02E tests add text-free export checks, pinned-BENCH02D unchanged-tag/precedence/quota parity and full/slim candidate parity under the ruled adapter, exact candidate readout, output confinement and mocked sbatch/srun execution from an unrelated working directory. The process-wide audit denies Python file opens for writing, mkdir and SQLite databases outside bench02. `tests.log` records the result. Shell launchers also pass `bash -n`.

Remaining inputs: coordinator supplies the completed census_05 path and receipt; missing ru/bg/uk document metadata, letter-spacing and book-series evidence remain deficits/limitations, with no substitutions. Serbian evidence and gate bbox/script mapping are resolved; ink density is absent. Sizes, thresholds and dev font rounding are resolved by the 20 October rulings. Until series metadata exists the physical series cap is unverified. The brief requested no P6 reads; none were performed, and no candidate is certified.

BENCH02F validation adds eight tests for confidence/p25 boundaries per source, punctuation at and below 1/3 and N1 paths, dev fonts, exact Serbian membership, gate bbox/inventory fields, numeric/null slim measurements and deficits without substitution. Historical BENCH02E measurements and census02 artifacts remain unchanged.
