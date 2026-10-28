# Release plan — Greek OCR models, line dataset and code (v0.n), 28 October 2026

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
| v4 real lines (364,173) | only on Clariden (training factory shards); not on HF. |
| Synthetic lines | 190,486 train (+ 9,208 val, 3,999 reserved per registry spec) in `full-v1-005-genn/data/prepared/synthetic/`, columns incl. `applied_ops`, `severity`, `font`, `polarity`, `bg_type`, `accent_survival`, `source_dataset`, `source_doc_id`, `reuse_index`, `license`. |
| GitHub `fffoivos/greek-ocr-toolkit` | **public**; `main` = squash of 20 Oct 17:05; local branch `train-full-v1` = 1,838 files changed since, plus 128 uncommitted files. Local history holds >100 MB blobs → push as squash. |
| Agreed metadata | `docs/programme_20261019/registry/HF_REPO_SPEC.md` (22–23 Oct) and the `harvest-20261025` card, amended by the owner's items 5–6. |

## 1. Versioning (owner item 8)

Every component is **v0.n**, n = that component's own generation count, until the owner declares
the end of beta (then v1). The same string is the git tag, HF tag and card title.
`VERSIONS.md` (repo root) records per component: current v0.n, what counted as each generation
(date, commit/HF revision), and old names as aliases (e.g. sf7, ru1, n1, segmentation 0.13, gate 0.3).
Components: OCR model, line dataset, synthetic generator + synthetic set, segmenter, content gate,
each correction tool (sf7 polytonic, ru1 Cyrillic, n1 numerics, dashes), release/pipeline builder.

Provisional OCR-model count = **v0.6**: (1) C1 3.77 M recogniser in the Docling plugin (pre-E1),
(2) E1 run4 7 Oct, (3) E3 16 Oct, (4) E4 waves 1a/1c 17–18 Oct, (5) post-E3 round (task 2 +
S1 width ladder) 20–22 Oct, (6) TRAIN_FULL_v1 26–29 Oct. Step 2 checks greek-page-ocr history
(the "O"-series) before the tag; the register table is shown to the owner once in the step-3 report.
Other components' counts are derived the same way in step 2 and recorded with their evidence.

## 2. GitHub `fffoivos/greek-ocr-toolkit`

- **One copy of the training code.** `greekocr/_vendor/train/` and
  `docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/vendor/train/` have diverged (`model.py`,
  `data.py` differ). Consolidate the code that produced v0.6 into `greekocr/train/`; the sealed
  packages stay as dated records referencing commit + SHAs. The Docling plugin
  (`greekocr/deploy/docling_plugin/`) loads v0.6 checkpoints through it (compact arch, codec v2.1,
  266 classes, NFD head) — with a test that loads each released safetensors and reproduces stored
  predictions on a few dev lines.
- **Bulk receipts** (≈630 smoke receipt files under `out/TRAIN_FULL_v1/receipts_*smoke*`) move out
  of git to Clariden; git keeps a manifest (path, bytes, SHA256).
- **`MODELS.json`** registry: model id → HF repo + revision/tag, weights SHA256, training commit,
  dataset tag, scores.
- **README** introduces each artefact in pipeline order with its link (owner item 8): pages and
  boxes (HF), segmenter (git), content gate (git), corrected Google lines (HF), correction tools
  (git), review method (git), latest synthetic lines (HF), training (git), models (HF), Docling use
  (git), known gaps (GitHub issues `gap`), the HF collection. Each with its v0.n.
- **Push:** a new squashed commit on `main` (history has >100 MB blobs), tag `v0.6` = the commit
  whose training code produced the models. Size guard: no tracked file > 5,000,000 bytes.

## 3. HF dataset `fffoivos/greek-ocr-lines` (public, `main` only)

**Repository hygiene (owner item 5).** Final state: everything on `main`, no other branches, tag
= the line dataset's v0.n. To keep the raw Google Document AI responses and old private commits out
of the public repo's history without deleting anything: rename the current repo to
`fffoivos/greek-ocr-lines-archive` (stays private), create a fresh `fffoivos/greek-ocr-lines`,
upload, verify, then make it public. The archive's deletion is the owner's later call.

**Layout**

```
README.md                                   dataset card (v0.n)
data/real/{train,dev,test,seal04_dev,seal04_test}/part-*.parquet   real lines (v4 + harvest-20261025)
synthetic/{train,val,reserved}/part-*.parquet                      synthetic lines, separate config
synthetic/RECIPE.json                       configured generator distribution
pages/pages.parquet, pages/images/part-*.parquet                   page scans + page records
boxes.parquet                               every segmenter box (Google + toolkit) with geometry
decisions/decisions.jsonl.gz                ADMIT/HOLD/DROP + reasons (all observations)
registry/book_registry.parquet              whole-book splits
manifests/{MANIFEST.json,SHA256SUMS,BUILD_RECEIPT.json}
```

Parquet with embedded original image bytes (never decoded/re-encoded); shards ≤ 1,000,000,000 B,
target ≈ 512 MB. HF `configs`: `real` (default), `synthetic`, `pages`, `boxes`.
Raw Google response archives (`staging-v4` `provenance/google/`) are **not** in the public repo:
their boxes and texts are already in `boxes.parquet`/`data/`; the raw dumps stay in the archive repo.

**Real-line fields** (agreed spec, licence removed per owner item 5)

1. Identity: `id`, `page_id`, `book_id`, `canonical_book_id`, `edition_id`, `wave`, `release` (`v4` | `harvest-20261025`).
2. Image: `image` (PNG bytes), `crop_sha256` (original crop), `training_image_sha256` (trainer payload, where it differs).
3. Position on the page: `crop_bbox` px, `polygon_px`, `polygon_norm`, `reading_order`, `top_index`, `segmenter` + version, `coordinate_frame` (incl. the 194 pages whose Google frame ≠ the stored scan).
4. Text: `text`, `label_sha256`, `raw_text_sha256`, `label_version`, `corrections_applied`, per-route status (sf7/ru1/n1/dash/content repair; absent ≠ no change).
5. Split: `split` (whole-book), `book_registry_sha256`, `harvest_protection`.
6. Decision: `decision`, `decision_reasons`, `primary_class`.
7. Features: `length_chars`, `greek_pct`, `latin_pct`, `cyrillic_pct`, `digit_pct`, `punct_pct`, `other_pct`, `polytonic`, `all_caps`, `has_capitals`, `mixed_script`, `language` + method, crop width/height/aspect.
8. **Source (replaces licence):** `provider`, `source`, `item`, `source_title`, `year`, `page` (within item), `catalogue_url`, `manifest_url`, `source_url`, `source_record_sha256` — enough to find the exact book and page.
9. Training: `used_in_ocr_v0_6` (bool) and the component pool it was drawn from.

**Synthetic fields** (owner item 6)

| Group | Fields |
| --- | --- |
| Identity | `line_id`, `reuse_index`, `split`, `factory_build_id` |
| Image | `image`, `image_sha256`, `width`, `height` |
| Text | `text` (NFC), `gt_nfd`, `label_ids`, `codec_version`, `script_class` |
| Text origin | `source_dataset`, `source_doc_id`, `text_sha256` |
| Rendering | `font`, `font_file_sha256`, `polarity`, `bg_type`, `accent_survival` |
| Applied to this line | `severity` (0–3), `applied_ops` (ordered list, incl. variant suffix), `n_ops` |
| Generator | `generator_sha256`, `recipe_name`, `recipe_sha256` |
| Training | `used_in_ocr_v0_6` |

No licence column. The card's synthetic section shows the realised distribution computed from the
files (script, severity, text source, fonts, op frequencies, ops per line) next to `RECIPE.json`
(configured probabilities/ranges, font list, text-source mix).

**Card** states: versions; scripts covered; joins; the seal04 references are reporting-only;
Astra's label-quality sample (33/412 = 8 % labels not matching the print on the base harvest);
known gaps with issue links; how to load each config.

## 4. HF model repo `fffoivos/greek-ocr` — "Greek OCR" (public)

- `main`: `x1/`, `x1.5/`, `x2/`, each with `model.safetensors`, `codec.json` (v2.1), `config.json`
  (arch compact, width multiplier, head nfd, n_classes 266, input height, normalisation),
  per-line dev+test predictions at the selected checkpoint, loss curves CSV, CER table.
- Card (owner item 6): leads with **multiple scripts — Greek, both modern (monotonic) and
  polytonic; Latin; Cyrillic; mixed Greek-Latin; numbers and page furniture**. Per-size scores:
  selection on seal04_dev / pooled dev; test reported only. Speed (ms/line CPU and GPU), parameter
  counts, error analysis summary, known weak spots, how to run (Python + Docling), dataset tag and
  git commit/tag that trained it.
- Branch `training-state` (the one justified extra branch: keeps pickle files off `main`): the 12
  full-state checkpoints (4 per size), SHA manifest, pickle warning. Size ≈ 1.4 GB.
- The 254 weights-only checkpoints per run stay on Clariden with a manifest on HF.
- Tag `v0.6`. Selected checkpoint per size = the CER checkpoint with the lowest seal04_dev CER
  (the run's selection rule; current: 100 % for ×1.5 and ×2).

## 5. Collection

Public HF collection "Greek OCR" with the dataset and the model repo; descriptions point to the
GitHub README; the README links the collection.

## 6. Gap method (owner item 7) — standard from now on

During work, any documentation/provenance gap goes into the checkpoint's `GAPS.md` (what is
missing / where found / impact on users / fix for future versions); it is not fixed mid-task.
At each checkpoint end the coordinator reviews the entries together, merges duplicates, and files
one GitHub issue per real gap on `fffoivos/greek-ocr-toolkit` (label `gap`), then writes the issue
numbers back into `GAPS.md` and the card's "Known gaps". Every Sol/Astra brief carries exactly one
line: *"If you find a documentation or provenance gap, add it to GAPS.md (what / where / impact /
fix); don't fix it here."* First entries: synthetic per-operation parameters and per-line seeds not
recorded (gap). The dropped licence column is an owner decision, recorded on the card, not an issue.

## 7. Steps, gates and checkpoints

| # | Step | Executor | Gate / acceptance |
| --- | --- | --- | --- |
| 0 | ×1 completes; final verification of all three runs (254 loss points, 4 CER evals, COMPLETE.json, accounting `sacct -D`) | coordinator | numbers in ledger |
| 1 | Analysis on Clariden (CPU): per source / script / length / digits-vs-letters CER, top confusions, cross-model error overlap, paired bootstrap between sizes on dev; speed benchmark CPU + GPU. Decisions on dev only; test → cards only. ×1.5/×2 now; ×1 when ready (same scripts) | Sol code, coordinator runs | report + JSON per model |
| 2 | Code consolidation (`greekocr/train/`), Docling load test, `VERSIONS.md`, `MODELS.json`, README, receipts manifest; commit on `train-full-v1` | Sol | tests pass |
| — | **Checkpoint A** (code): Sol xhigh review of step 2 | Sol review | PASS |
| 3 | Squash snapshot → GitHub `main`, tag `v0.6`; file checkpoint-A gap issues | coordinator | push succeeds; size guard |
| 4 | Dataset builder (Clariden CPU job): assemble real + synthetic + pages + boxes + decisions + registry to the layout above; upload to the new private repo; full download + SHA check | Sol code, coordinator runs | manifest SHA check 100 % |
| — | **Checkpoint B** (dataset): Astra review of builder, manifest, card, sample rows | Astra | PASS |
| 5 | Rename old repo → `-archive`; make `greek-ocr-lines` public; tag v0.n; file checkpoint-B gap issues | coordinator | public URL loads; tag set |
| 6 | Model repo build: export safetensors/config/codec, predictions, curves, cards, `training-state` branch; upload; verify | Sol code, coordinator runs | SHA check |
| — | **Checkpoint C** (models): Astra review of cards + numbers vs evidence | Astra | PASS |
| 7 | Make `greek-ocr` public; collection; README links resolve; tag; file checkpoint-C gap issues | coordinator | all links resolve |
| 8 | Next phase (separate plan after step 7): full segmentation → OCR pipeline test incl. the owner's two PDFs (23 + 49 landscape pages) with a review page per PDF — page image with numbered line boxes, crop + text per line, full text per page, dropped lines with reasons (no CER: no transcription); Docling tests; glossAPI integration | — | — |

HOLD/BLOCKER at a checkpoint: fix and re-review; a third cycle on the same object stops for a
decision (programme rule). The Mac is not a processing worker: builds, analysis, exports and
uploads run on Clariden (uploads with the HF token already configured there, never printed).

## 8. Risks and decisions taken in-plan

- **Public test sets.** seal04 dev/test become public; future web-trained models may see them.
  Accepted by the owner's "public" decision; noted on the card.
- **Training-data link.** The model card pins the dataset tag; the dataset carries
  `used_in_ocr_v0_6` per line so the training population is reconstructible.
- **Exact continuation** from the 25/50/75 % full states needs the same data plan
  (`batch_plan_sha256`); documented on the model card.
- **Disk/upload size.** Real lines ≈ 18 GB (harvest) + v4 lines (measured in step 4) + synthetic
  ≈ 5.5 GB + pages (≈ 40 GB incl. rasters; raw Google archives excluded). HF upload from Clariden
  via `upload_large_folder`, resumable.
