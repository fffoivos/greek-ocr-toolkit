# Release plan — Greek OCR models, line dataset and code (v0.n), 28 October 2026 — rev 2

Rev 2 folds in the single Astra plan review ([ASTRA_PLAN_REVIEW.md](ASTRA_PLAN_REVIEW.md), HOLD 0/8, PLAN rev 1 SHA `5c3f56b4…`, kept as [PLAN_rev1.md](PLAN_rev1.md)). Disposition of every finding: §9. Per the owner, no second plan review.

Owner's words: [OWNER_BRIEF.md](OWNER_BRIEF.md) (verbatim). This plan implements them; where the
plan and the brief disagree, the brief wins. Ledger: `EXECUTION_STATE.md` beside this file.
Authorisation: owner item 9 — one Astra review of this plan, coordinator fixes, then autonomous
end-to-end execution, including the GitHub push and making the two HF repos public at the steps
named below. Deletions remain the owner's call; nothing in this plan deletes data.

## 0. Inputs (as of 28 Oct 2026)

| Item | State |
| --- | --- |
| Models | TRAIN_FULL_v1 Stage C. ×1.5 (`w1.5-full`, attempt 013) and ×2 (`w2-full`, 013) COMPLETE: 254/254 loss points, 4/4 CER. ×1 (`w1h14-full`, attempt 014, job 3768981, trial h14) running since 11:12, ETA ≈ early 29 Oct. Old ×1 h13 (`w1-full`) retired at 26 %, not released. |
| Checkpoints per run (Clariden) | 254 weights-only loss checkpoints (`loss_checkpoints/`), 4 full-state checkpoints at 25/50/75/100 % (`checkpoints/`: model, AdamW state, scheduler, RNG, data cursor, SHAs), `best`/`last` `.pt` + `.safetensors`, per-line dev/test predictions at each CER step (`eval/`). |
| HF dataset `fffoivos/greek-ocr-lines` | private; branches `main` (empty), `harvest-20261025` (18.2 GB, 497,556 lines incl. Gennadius), `staging-v4` (40.7 GB, pages + raw Google responses + provenance; **no v4 line images**). |
| Real training population (authoritative) | prepared005 runtime `21b92bdf…` used by every Stage C run: S1 v4 input **364,871** rows → **364,870** retained (one train/eval crop removal) + harvest train **428,357** = **793,227** real train rows; harvest dev **16,350**, harvest test **52,847**; seal04 dev **437** / test **2,253**. Factory remaps harvest ids to `harvest:<wave>:<id>`. The older registry figure 364,173 (wave-2 v4 pool) differs by 698 keys: reconciled by key in step 4 (H01). v4 line images exist only on Clariden. |
| Synthetic lines | prepared005 reads only the **train** role: **190,486** rows / 47 files in `full-v1-005-genn/data/prepared/synthetic/`, built from `scaling_w3/mix1_runs/MIX1D-8d25940f-export-001/prep/A12`. val/reserved (9,208 / 3,999 in the registry spec) come from their own builds and are published only if their exact build is identified (H03). Columns incl. `applied_ops`, `severity`, `font`, `polarity`, `bg_type`, `accent_survival`, `source_dataset`, `source_doc_id`, `reuse_index`, `license`. |
| GitHub `fffoivos/greek-ocr-toolkit` | **public**; `main` = squash of 20 Oct 17:05; local branch `train-full-v1` = 1,838 files changed since, plus 128 uncommitted files. Local history holds >100 MB blobs → push as squash. |
| Agreed metadata | `docs/programme_20261019/registry/HF_REPO_SPEC.md` (22–23 Oct) and the `harvest-20261025` card, amended by the owner's items 5–6. |

## 1. Versioning (owner item 8)

Every component is **v0.n**, n = that component's own generation count, until the owner declares
the end of beta (then v1). `VERSIONS.md` (repo root) is the register: per component the current
v0.n, each generation with date, evidence (commit / HF revision / run ids) and old names as aliases.

**Counting rule (M02).** A generation of a component is one completed round that produced a new
version of that component which we evaluated or used as the incumbent. Bake-offs of external
teachers, preparation work and reruns of the same version do not count. Components: OCR model;
line dataset; synthetic generator; synthetic line set; segmenter (A lineage, already numbered by
generation); B crop policy / content gate / content repair / composer / final eligibility / census /
inventory (from `docs/harvest/line_pipeline/tool_versions.json`); correction tools sf7, ru1, n1,
dashes; release builder. Existing numeric versions (e.g. segmentation 0.13, gate 0.3) are kept
where they already follow the scheme; otherwise the register maps the old name to v0.n.

**OCR model.** Provisional v0.6 (C1 recogniser, E1 run4, E3, E4 waves, post-E3 round, TRAIN_FULL_v1).
Step 2 settles the count with the evidence table — including E4 wave 1b and the greek-page-ocr
O-series — and the value is a parameter (`OCR_VERSION`) everywhere (fields, tags, cards), never
hard-coded. The register is shown to the owner in the step-3 report.

**Tags.** HF repos each carry plain `v0.n` tags (one component per repo). In the monorepo, git tags
are component-qualified: `ocr-v0.n`, `lines-v0.n`, `synth-v0.n`, etc., with the same `v0.n` value.
A published tag is never moved; ×1 completing later does not move anything (see §7 barrier).

## 2. GitHub `fffoivos/greek-ocr-toolkit` (public)

**Producing source vs release code (H08).** Each released model records `training_source`
separately from `release_code_commit`:
- ×1.5 and ×2: attempt 013, sealed package `7e8a497f…` (payload records `producing_commit e1d67490f…`,
  `source_state UNCOMMITTED_PREPARE_ONLY`; upstream trainer `71e72bfb…` + patch per `vendor/UPSTREAM.json`),
  adopted configs `w1.5-*.json` / `w2-*.json` as bound in each run's CLAIM/RUN_BINDING.
- ×1: attempt 014, package `e808f6ff…`, trial **h14**, PLAN `d9d72fa0…`, config `c3cc2728…`.
  The retired h13 lane (`w1-full`, attempt 013, `adopted/w1-h13.json`) is excluded everywhere.
- The sealed packages are published **unchanged** (hash-verifiable) in the public snapshot and as
  archives in the model repo (`training_source/`), so the producing code is accessible.
The new public commit is the release that *contains* the producing source; it is not described as
the commit that trained the models.

**One live copy of the trainer.** `greekocr/train/` becomes the maintained copy, taken from the
executed Stage C numerical implementation (the source of truth: model incl. width support, heads,
codec, evaluation, decoding). Adaptations are limited to packaging/import changes and are listed in
a mapping file; an equivalence test runs the sealed and consolidated code on the same dev inputs and
requires identical logits/decodes (fp32, CPU). The sealed packages are not edited.
`greekocr/_vendor/train/` becomes a pointer or is retired with the mapping.

**Docling plugin (M01).** The plugin loads models through `greekocr/train/` (width multiplier,
codec v2.1, 266 classes, NFD head, NFC output). The acceptance test runs on the **exported release
artefacts** (step 6), all three widths, through the actual Docling recognizer path with strict state
loading, and reproduces the stored dev predictions (compared in NFD, same preprocessing profile and
fp32). It gates publication of the model repo.

**Publication commit (H07).** Built on a fresh fetch of the public `origin/main` (`89821975b…`) as
its only parent, with `git commit-tree` from a reviewed public-file inventory — no private ancestry,
no private branches or tags pushed. Excluded from the snapshot: raw Google payloads, credentials,
private operational material, and the ≈630 bulk smoke receipts (copied to Clariden first, SHA
verified, then excluded; git keeps their manifest; local files untouched). Checks: candidate commit
parents; every newly reachable object; no blob > 5,000,000 B; public-inventory diff reviewed; after
push, read back the public commit. Commits and pushes are done by the coordinator (Sol cannot write git).

**Also in the snapshot:** `VERSIONS.md`, `MODELS.json` (model id → HF repo + `main`/`training-state`
commit ids, weights SHA, training_source, release_code_commit, dataset tag + commit, scores),
and the README (owner item 8) introducing each artefact in pipeline order with its pinned link:
pages and boxes (HF), segmenter (git), content gate (git), corrected Google lines (HF), correction
tools (git), review method (git), latest synthetic lines (HF), training (git), models (HF), Docling
use (git), known gaps (issues `gap`), the HF collection — each with its v0.n.

## 3. HF dataset `fffoivos/greek-ocr-lines` (public, `main` only)

**Cutover (H06), nothing deleted.**
1. Preflight: pin every source read to commit ids (`harvest-20261025` `103c6dcd…`, `staging-v4`
   `8ee9cb2e…`); check that `fffoivos/greek-ocr-lines-v0` and `fffoivos/greek-ocr-lines-archive`
   are free; record current refs/visibility.
2. Create a **fresh private** repo `fffoivos/greek-ocr-lines-v0` (verify it is new: no refs, no
   history). Upload and verify there (step 4).
3. Rename the old repo `greek-ocr-lines` → `greek-ocr-lines-archive`; verify it is still private and
   its refs unchanged.
4. Rename `greek-ocr-lines-v0` → `greek-ocr-lines`; verify identity (same commit ids), refs = `main`
   + tag only, then make it public. If any rename behaves unexpectedly, stop with both repos private.

**Public tables and layout.** The agreed relational contract (HF_REPO_SPEC) is kept; the public repo
removes only the licence fields and the raw Google response payloads. `CROSSWALK.md` maps every
field/relation of the spec to its destination or a recorded amendment (H02).

```
README.md                                    dataset card (v0.n)
data/real/<split>/part-*.parquet             convenience view: one row per published real line, images embedded
data/synthetic/<split>/part-*.parquet        synthetic lines (separate config)
synthetic/RECIPE.json, synthetic/BUILD/      source + effective recipes, build manifests, op→function map
tables/pages.parquet                         every page observation incl. failed/excluded (null rasters kept)
tables/page_images/part-*.parquet            page rasters (original bytes)
tables/page_frames.parquet                   Document AI dimensions/transforms vs raster, mapping status (sanitised from raw responses)
tables/boxes.parquet                         every box, all segmenters; raw vs derived kind; run/config/model; emitted + geometric order
tables/segmenter_page_results.parquet        ok / zero_detections / error / not_run per page and run
tables/rows.parquet                          every row observation (ADMIT/HOLD/DROP), (parent_id,row_id), row_key, FKs
tables/label_versions.parquet                raw / census / sf7 / ru1 / n1 / factory-codec labels, each with text, hash, codec
tables/row_features.parquet                  keyed by (row_key, label_variant, feature_version)
tables/row_instruments.parquet               lqb_row / release_excluded_row lists with names + hashes
tables/training_membership.parquet           keyed per model run: pool, trainer line id, image/label variant consumed
tables/references.parquet                    seal04 raw/corrected (diagnostic_only + exposure notes), v2 coverage memberships, validation membership
registry/book_registry.parquet               canonical book/split + source split, assignment status, aliases, harvest_protection
decisions/decisions.jsonl.gz                 verbatim decision/reason records
manifests/{MANIFEST.json,SHA256SUMS,BUILD_RECEIPT.json,COVERAGE.json}
```

Parquet with original image bytes, never re-encoded. Every file ≤ 1,000,000,000 B (target ≈ 512 MB),
checked on the closed file; any table that outgrows the cap moves to `…/part-*.parquet` with the
card config updated in the same commit (M07). HF configs: `real` (default), `synthetic`, plus one
config per table.

**Real-line view fields** (each also lives in its table; denormalised here for convenience)
1. Identity: `id` (namespaced `<release>:<original id>`), `parent_id`, `row_id`, `row_key`, `page_id`, `box_id`, `crop_id`, `book_id`, `canonical_book_id`, `edition_id`, `wave`, `release` (`v4` | `harvest-20261025` | `seal04`).
2. Images: `image` = original crop bytes, `crop_sha256`; `trainer_image` = the exact factory payload the trainer read (resized/letterboxed), `training_image_sha256` — both published (H01).
3. Position on the page: `crop_bbox` px, `polygon_px`, `polygon_norm`, `box_kind`, `segmenter` + run id, `emitted_index`, `reading_order`, `top_index`, `coordinate_frame` + `frame_status` (from `page_frames`; unresolved frames keep source coordinates, never rescaled).
4. Text: `text` (final label), `gt_nfc`, `gt_nfd`, `label_ids`, `codec_version`, `label_version`, `label_sha256`, `raw_text`, `raw_text_sha256`, `corrections_applied`, per-route status (absent ≠ no change).
5. Split: `split`, `source_book_id`, `source_split`, `assignment_status`, `book_registry_sha256`, `harvest_protection`, `lqb_row`, `release_excluded_row`.
6. Decision: `decision`, `decision_reasons`, `primary_class`.
7. Features (`feature_version` stated): NFC and raw-codepoint lengths, six bucket counts and percentages (non-whitespace NFC denominator, agreed precedence rules), polytonic, all_caps, has_capitals, mixed_script, named scripts, language + method + scoped confidence, crop dimensions/aspect + which pixels supplied them, normalised box centre.
8. **Source (replaces licence):** `provider`, `source`, `item`, `edition`/`volume` where known, `source_title`, `year`, `page` + page-number convention, `catalogue_url`, `manifest_url`, `source_url`, `source_record_sha256`. `COVERAGE.json` reports per population how many rows carry each field; missing values are null with a reason, never invented (M04).
9. Training: `trained_in` (list of model ids that drew it), `pool`, `trainer_line_id`; full keyed detail in `training_membership`. "Available", "eligible", "drawn for training" and "used for selection/evaluation" are distinct fields.

**Synthetic fields** (owner item 6; H03)

| Group | Fields |
| --- | --- |
| Identity | `line_id`, `reuse_index`, `split`, `factory_build_id`, `source_build` |
| Image (computed) | `image`, `image_sha256`, `width`, `height` |
| Text | `text` (NFC), `gt_nfd`, `label_ids`, `codec_version`, `script_class` |
| Text origin (recovered) | `source_dataset`, `source_doc_id`, `text_source_locator`, `text_sha256` |
| Rendering (recovered) | `font`, `font_file_sha256` or `font_sha16` (whichever the build recorded), `polarity`, `bg_type`, `accent_survival` |
| Applied to this line | `severity` (0–3), `applied_ops` (ordered, incl. variant suffix), `n_ops` (computed) |
| Generator (recovered) | `generator_code_sha256`, `generator_binary_sha256`, `recipe_name`, `recipe_sha256`, `recipe_effective_sha256` |
| Provenance status | `provenance_completeness`, `historical_unknown_fields` (each unknown with its reason and search receipt) |
| Training | `trained_in` |

No licence column. `synthetic/BUILD/` holds the frozen source + effective recipes and build
manifests; `synthetic/OPS.md` maps each op name to its function in the factory source
(`greekocr/_vendor/factory/src/…`). The card shows configured (recipe) versus realised (files)
distributions per split. val/reserved are published only from their identified builds.

**Acceptance for the dataset (H02, M07).** Byte checks: full download, every path/byte/SHA in the
manifest. Semantic checks: every source key present with its status/reason; foreign keys resolve
(row→box→page→book); split and instrument counts reconcile with the registry; the 364,870 + 428,357
real train rows and their consumed variants reconcile **by key** with prepared005 (and the 698-key
difference to the old 364,173 pool is explained by key); image/label identities match the sources;
references and coverage memberships complete; an independent feature replay on a sample agrees;
configs load and join images. Public checks: visibility, archive still private, refs = `main` + tag.

**Card** states: version and component versions; scripts covered; how to load each config and join
tables; **selection roles** — seal04_dev selected checkpoints, pooled dev (harvest_dev + seal04_dev)
selected hyperparameters in Stage B, seal04_test and harvest_test are report-only, with the inherited
exposure caveats (H04); Astra's label-quality sample (33/412 = 8 % labels not matching print on the
base harvest); licence fields intentionally removed (owner decision); known gaps with issue links.

## 4. HF model repo `fffoivos/greek-ocr` — "Greek OCR" (public)

**Release-selection contract (H04).** Per width, the released weights are the trainer's `best.pt`:
the strict-improvement best of the **8 epoch-end evaluations on seal04_dev (437 rows, val_cer,
Stage C scorer)**. Stage B chose hyperparameters on pooled dev. For each width the card records the
selected epoch/step and the weight SHA, and states whether it coincides with a 25/50/75/100 % archive
(for ×1.5 and ×2 the best epoch is 8 = the 100 % archive; verified by weight SHA in step 6). All
published predictions and scores are bound to that weight SHA; if a needed prediction set is missing
for the selected weights it is produced after the choice is fixed. No test number influences any
choice.

- `main`: `x1/`, `x1.5/`, `x2/`, each with `model.safetensors`, `codec.json` (v2.1), `config.json`
  (arch, width multiplier, head, n_classes, input height, normalisation, decode), selected-checkpoint
  dev + test predictions, loss curves, CER table; `training_source/` with the sealed packages.
- Card (owner item 6): leads with **multiple scripts — Greek, both modern (monotonic) and polytonic;
  Latin; Cyrillic; mixed Greek-Latin; numbers and page furniture**; per-width scores with roles as
  above; parameters; speed (ms/line CPU + GPU); error analysis summary (dev for any claim used in a
  decision; test descriptive); known weak spots; usage (Python + Docling); pinned dataset tag + commit;
  `training_source` and `release_code_commit`.
- Branch `training-state` (justified: keeps pickle files off `main`): for each of the 12 full-state
  checkpoints its **dependency closure** (H05) — the checkpoint unchanged, every referenced
  `segment_artifacts/<digest>`, the run's PLAN/config/RUN_BINDING/CLAIM, codec, runtime + pool
  manifests and batch plan, sealed package reference, environment record — plus SHA manifest and a
  pickle warning. The card states exactly what continuation needs (this closure + the dataset tag's
  trainer payloads in pool order); if any piece cannot be published, the states are labelled
  archival, with no exact-continuation claim.
- `MANIFEST.json` pins `main` and `training-state` by their separate commit ids; tag `v0.n` on `main`.
- The 254 weights-only checkpoints per run stay on Clariden; their manifest goes on `main`.

## 5. Collection

Public HF collection "Greek OCR": the dataset and the model repo, pinned revisions in descriptions,
pointing to the GitHub README; the README links the collection.

## 6. Gap method (owner item 7; M05)

During work, documentation/provenance gaps that are **not release-critical** (historical
information we cannot recover, improvements for future versions) go into the checkpoint's `GAPS.md`
(what / where / impact / fix). Release-critical defects are fixed in the plan's normal flow. At each
checkpoint end the coordinator triages the entries together: groups related ones, drops trivial or
already-resolved ones, and files the remaining ones as GitHub issues on `fffoivos/greek-ocr-toolkit`
(label `gap`), writing issue numbers back into `GAPS.md` and the card's "Known gaps". Not every entry
becomes an issue. Every Sol/Astra brief carries one line: *"If you find a documentation or provenance
gap, add it to GAPS.md (what / where / impact / fix); don't fix it here."* (for reviewers, "here" =
in the review; it does not restrict the coordinator's fixes).
Owner's gaps 1–2: (1) synthetic per-operation parameters and per-line seeds not recorded → `GAPS.md`
entry, grouped into one generator-provenance issue at checkpoint B. (2) licence column → removed by
owner decision; recorded as intentional on the cards; no issue, never reinstated.

## 7. Steps, dependencies and checkpoints (M06)

×1.5 and ×2 are complete; all work that does not need ×1 proceeds now. ×1 joins steps 0–1 and 6 when
it finishes. **Release barrier:** the dataset (steps 4–5) does not depend on ×1 (all three models drew
from the same pools; `trained_in` lists the three model ids); the model repo is made public and tagged
only when all three widths are exported and verified. No tag is moved afterwards.

| # | Step | Executor | Gate / acceptance |
| --- | --- | --- | --- |
| 0 | Final verification per run (254 loss points, 4 CER evals, COMPLETE.json, `sacct -D` accounting): ×1.5/×2 now, ×1 when done | coordinator | numbers in ledger |
| 1 | Analysis on Clariden (CPU): CER by source / script / length / digits-vs-letters, top confusions, cross-model error overlap, paired bootstrap between widths **on dev**; test breakdowns descriptive only. Speed benchmark CPU + GPU per width. ×1.5/×2 now; ×1 with the same code when ready | Sol code; coordinator runs jobs | report + JSON per model |
| 2 | `greekocr/train/` + mapping + equivalence test; Docling loader migration; `VERSIONS.md` with the counting evidence; `MODELS.json` skeleton; README; public-file inventory; receipt manifest | Sol | tests pass |
| — | **Checkpoint A** (code): Sol xhigh review of step 2 | Sol review | PASS |
| 3 | Copy bulk receipts to Clariden + verify; build the publication commit on public `origin/main`; object/size/inventory checks; push `main` + `ocr-v0.n` release-code tag; read back; triage checkpoint-A gaps → issues | coordinator | §2 checks |
| 4 | Dataset builder (Clariden CPU jobs, credential-free): tables + views per §3 from pinned sources and prepared005; `CROSSWALK.md`; `COVERAGE.json`; upload to fresh private `greek-ocr-lines-v0`; full download; byte + semantic acceptance | Sol code; coordinator runs | §3 acceptance |
| — | **Checkpoint B** (dataset): Astra review of builder, crosswalk, acceptance evidence, card | Astra | PASS |
| 5 | Cutover per §3 (rename old → `-archive`, rename `-v0` → `greek-ocr-lines`), verify, make public, tag `v0.n`; triage checkpoint-B gaps → issues | coordinator | public checks |
| 6 | Model export per width (selected weights per §4) → actual Docling-path load + dev prediction parity → `main` + `training-state` closure upload to a private `greek-ocr`; verify | Sol code; coordinator runs | parity + SHA |
| — | **Checkpoint C** (models): Astra review of cards, numbers vs evidence, selection contract, closure | Astra | PASS |
| 7 | Make `greek-ocr` public, tag `v0.n`; collection; update README/MODELS.json with pinned revisions (second public commit on `main`); verify every link; triage checkpoint-C gaps → issues | coordinator | links resolve |
| 8 | Next phase, started by the coordinator right after step 7 under the same authorisation (own brief, no extra approval gate): full segmentation → OCR pipeline test, first on the owner's two PDFs — `~/Downloads/ΣΤΡΑΓΓΑΣ ΠΑΠΟΥΣ ΠΟΙΗΣΗ/20260727184649649.pdf` (23 landscape pages) and `…/20260727185315673.pdf` (49) — with a review page per PDF: each page with numbered line boxes in reading order, crop + text per line, full text per page, dropped lines with reasons; no CER (the `.docx` is not a transcription). Then Docling tests and glossAPI integration | coordinator → Sol | review pages published |

Checkpoint reviews A/B/C are artefact reviews, distinct from the single plan review. A HOLD is fixed
and re-reviewed; a third cycle on the same object stops for a decision. Reviews run in sequence.

**Credentials (M03).** Builders run credential-free on Clariden compute. Uploads run as a separate
foreground process on a Clariden login node with the token injected ephemerally from the Mac
Keychain over ssh **stdin** into that process's environment (never argv, files, `hf auth login`,
shell tracing, scheduler export, logs or receipts). The coordinator does not read or print any token
stored on Clariden. If this channel fails, the package is retained and the channel is fixed; no
credential is persisted.

**Preflight (M07).** Before step 4 and step 6: inventory closed-file sizes, per-directory and total
file counts, repo bytes, scratch space for build + full readback, installed `huggingface_hub`
version/capabilities, and current Hub limits; record them in the ledger.

## 8. Risks and decisions taken in-plan

- Public test sets: seal04 dev/test become public; noted on the card (owner chose public).
- Exact continuation is claimed only if the §4 closure is complete.
- Sizes (to be measured in preflight): harvest lines ≈ 18 GB; v4 lines + trainer payloads TBD;
  synthetic ≈ 5.5 GB; page rasters TBD (the 40.7 GB staging figure includes raw Google archives,
  which are not published).

## 9. Disposition of the Astra plan review

| Finding | Disposition in rev 2 |
| --- | --- |
| H01 population mismatch | §0 authoritative prepared005 counts; key reconciliation with the old 364,173 pool; trainer image variant, labels/codec and keyed per-run membership published (§3) |
| H02 agreed spec weakened | relational tables retained (§3 layout), `CROSSWALK.md`, sanitised `page_frames`, semantic acceptance |
| H03 synthetic provenance | sources named per role; restored fields; computed vs recovered separated; nulls with reasons; op→function map; val/reserved only from identified builds |
| H04 selection contract | §4 contract (trainer epoch-best on seal04_dev), roles stated on both cards, predictions bound to weight SHA |
| H05 continuation closure | §4 closure incl. `segment_artifacts`; separate commit pins; archival label otherwise |
| H06 cutover order | §3 fresh `-v0` repo → rename old → rename new → public |
| H07 public history | §2 publication commit on public `origin/main`, object/inventory checks, read-back |
| H08 producing source | §2 `training_source` vs `release_code_commit`, sealed packages published unchanged, h13 excluded, commits by coordinator |
| M01 Docling on final artefacts | §2/§7 step 6 gate on exported artefacts, all widths |
| M02 version count/tags | §1 counting rule, parameterised version, component-qualified git tags |
| M03 credentials | §7 credentials paragraph |
| M04 source coverage | §3 field 8 + `COVERAGE.json`, nulls with reasons |
| M05 gap rule | §6 release-critical fixed in flow; triage; licence disposition |
| M06 ×1 handoff / next phase | §7 dependencies, release barrier, step 8 executor and PDF paths |
| M07 Hub acceptance | §3 acceptance, §7 preflight |
