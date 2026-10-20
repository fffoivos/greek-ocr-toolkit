# Toolkit clean-up plan, 17 Oct 2026 (inventory + proposed layout; NOTHING MOVED)

Status: **PLAN.** No file has been moved, renamed or deleted. Sol executes later, only after the coordinator's and the owner's approval,
and only after the in-flight work below has closed.

**Appendices** (full tables, facts from the code):
- `CLEANUP_PLAN_20261017_inventory.md`: every directory and file with size, tracked/untracked state, last commit, group, status and
  proposed action. Also the gate closure, deploy pins, import graph, test map and hazards.
- `CLEANUP_PLAN_20261017_api.md`: the recogniser and card-tooling duplication inventory, with the proposed single APIs.
- `CLEANUP_PLAN_20261017_sourcing.md`: the sourcing lead's input for the harvest/collect/recut areas.

The page builders that existed only in a session scratchpad are now committed under `docs/records/labelfix/spellcheck/R2_evidence/page_builders/`.
They are the only record of how today's owner pages and checks were made.

## 1. What the inventory found (constraints that shape the plan)

1. **Paths are pinned, not just bytes:**
   - All 237 `greekocr/**/*.py` files and 66 `scripts/labelfix` files are listed in the L1E deploy receipt; C1 and R1 pin 18 and 128 paths.
   - `release_gate.policy_binding()` hashes 16 repo-relative paths into the frozen policy digest.
   - SF/R0 evidence JSONs re-check 324 code paths.
   - Renaming any of these breaks receipts or the gate digest.
2. **The proposed package split crosses two import cycles,** `ctc_align ↔ candidates` and `ink ↔ case`, which straddle G2/G3.
3. **"Superseded" is mostly not "unreferenced":**
   - `sf6_measure` imports `sf5_measure` and `sf3_measure`, and the old iteration evidence feeds the live SF6/SF6c replays and tests.
   - Only 12 scripts are free to move.
4. **Untracked but load-bearing:**
   - `artifacts/` (111 MB, including the R1 checkpoints read by the sf* measures);
   - `.cache/labelfix` (188 MB, R1-pinned).

   Neither is deletable.
5. **Git size:** 6.2 GB tracked, 3.9 GB of it in 106 files over 5 MB, all under `docs/`. Moving or archiving frees nothing. Only an
   LFS/history rewrite would, and that changes the SHAs quoted in receipts. That is a separate owner decision.
6. **This branch is incomplete:** the S8/L1R*/L1C/L1F/L1A2 tooling sits on unmerged siblings. `opus/spellcheck-s8` is 37 commits ahead and
   edits the gate-closure files `case.py` and `ink.py`. **Merge first, reorganise second.**

## 2. Target organisation: facades over a frozen core, not file moves

Groups (coordinator's definition):

| Group | Scope | Today | Proposed home (new code + re-export facades) |
|---|---|---|---|
| **G1 review / adjudication** | cards, decks, blind readers, owner sheets + db notes, tie-break, truth files | `greekocr/labelfix/{deck,deck_serve,ingest_decisions,pull_firefox,sheet,owner_slots}.py`, `scripts/labelfix/{r0_*,sheet_build,owner_pages_*,owner_implicit_*,s8_prepare,l1a2_cards,s8_score_truth}`, `docs/records/labelfix/spellcheck/print_truth/*.py`, collect_v3 `cards.py`/`review.py`/`c1_agg.py`, scratchpad builders | `greekocr/adjudicate/` (§4) + `scripts/review/` |
| **G2 recogniser + Google bootstrap → reader data** | C1 selection, agreement labels, CTC alignment, slot extraction | `greekocr/labelfix/ctc_align.py`, `validate/sample/sheet` alignment helpers, `scripts/labelfix/clariden/{c1_*,l1_*,l1e_*,l1f_*,r1_extract,r1_pixels,r1_common}` | `greekocr/recogniser/` (§3) + `greekocr/bootstrap/` (facade) + `scripts/clariden/<job>/` for new jobs |
| **G3 reader training / scoring / gate / audits** | r1_* training/scoring, markshape, detector (ink/segmentation/case/reading), release gate, K1, SF audits | `greekocr/labelfix/{release_gate,reading,segmentation,case,ink,markshape,constraints,…}`, `scripts/labelfix/clariden/{r1_train,r1_model,r1_score,l1r*}`, `sf*_measure/verify` | `greekocr/reader/` + `greekocr/gate/` (facades) |
| **G4** (each its own group) | glyph geometry, page lines / fast lines / O4D, harvest/collection/recut, readers (DocAI/Transkribus/Vision), research, reviews | `greekocr/{glyphs,pages,harvest,real,readers}`, `scripts/{glyphs,pages,harvest}`, `docs/{harvest,research,reviews,tables,verify}` | unchanged locations; archive closed evidence |

**Rules:**
- **`greekocr/labelfix/` stays byte-identical as the frozen implementation.** It is pinned by the gate digest and by every receipt. New
  packages re-export from it (for example `greekocr/reader/__init__.py: from greekocr.labelfix.reading import *`), and **new code goes
  into the new packages from now on**.
- **`scripts/labelfix/` stays where it is.** New Clariden jobs go under `scripts/clariden/<job>/`, which keeps the depth-3 root discovery
  that 127 files rely on.
- **Only the 12 unpinned scripts may move:** `r0_freeze_ia/ib`, `r0_score*`, `r0_wholeline_score`, `sf5_verify`, `sf6_verify`,
  `sf6c_*`. They move to `scripts/review/` or `scripts/reader/` with depth preserved.
- **Pinned code moves only at the next gate re-certification**, under a new POLICY schema, with golden tests on the saved evidence hashes
  (§3, phase 2), and with a written rule that old receipts are historical, re-checkable through `git show <deploy-sha>:<path>`.

## 3. The recogniser as ONE API (owner: "to what extent the recognizer can be constructed as an API from the previous ocr tools … repo coherence and no code duplication")

**Today:** three independent stacks sit over the same vendored training code (`greekocr/_vendor/train`, copied from greek-page-ocr at
b7818f3f):

| Stack | Entry | Differences that change outputs |
|---|---|---|
| A, serve (Docling plugin) + A′ vendored twin | `deploy/docling_plugin/recognizer/inference.Recognizer`, `_vendor/pipeline/recognize.Recognizer` | float strips, float median halo, NFC output, line confidence only; only A checks codec sha + head |
| B, evaluation reader | `readers/ours.load_ours → E1Reader` | uint8 strips, averaged-median background then rint, NFD, no frames, no confidence |
| C, labelfix aligner | `labelfix/ctc_align.Recognizer` (all C1/L1/L1F/R0/M2/R1 paths) | uint8 strips, **upper**-median background, spans + float32 frame confidences; checks codec version and n_classes only |

**Duplicates:**
- `r1_common.transfer_record`, a copy of `transfer_alignment` that keeps frames and sets no flag;
- two `crop_key` functions with different strictness;
- five copies of a "forbid forward" monkeypatch;
- five loaders for the R1 checkpoint, one with `weights_only=False`;
- alignment caches re-implemented in validate/sample/sheet/m2/r0, which round differently on the first run and on replay;
- `align_paths` silently skips unreadable crops;
- float32 vs float64 mean checks. This is the cause of the L1R4 failure (17 rows, gap ≤ 2.48e-7).

**Proposed surface, `greekocr.recogniser`:**
- `load(checkpoint, codec) -> Recogniser`: one loader that enforces codec version + sha + n_classes + head, and records provenance
  (checkpoint/safetensors/codec/code sha, device, dtype, torch).
- `Recogniser.read(images, profile='labelfix'|'eval'|'serve') -> [Reading(text_nfd, frames float32, confidence float32, ids, scale)]`.
  The profiles reproduce stacks C, B and A exactly; the differences become named profiles until a parity measurement picks one. Unreadable
  inputs are reported, not skipped.
- `Recogniser.logits(images)`.
- `align(reading) -> Alignment`; `Alignment.slots()`; `Alignment.evidence(slots, image_width)`: byte-identical to today's
  `recognition_evidence` (schema `ctc-window-score-v1`, `alignment_sha256` frozen).
- `transfer(alignment, new_text)`: always NFD, always drops frames, always flags `transferred`.
- `confidence_matches(frames, confidence)`: one float32-aware predicate.
- `AlignmentCache` (one strict `crop_key`), `run_shard` (cluster entry), `forbid_forward()`.
- Later, in its own validation round: a Viterbi `force_align` ported from greek-page-ocr `bench/o4b_align.forced`, to replace
  nearest-neighbour transfer.

**What replaces what** (full table in the API appendix §1.7):
- `ctc_align` stays as the frozen implementation until phase 2.
- The Docling plugin uses `profile='serve'`. A generated standalone copy is allowed only if it must ship alone, and then with a parity test.
- `load_ours`/E1Reader becomes `load(...).as_reader(profile='eval')`, with a bit-parity test.
- The alignment caches become `AlignmentCache`.
- `transfer_record` becomes an adapter.
- The mean checks become `confidence_matches`.
- The `c1_run`/`l1f_run` forward loops become `run_shard`, but only at phase 2, because they are pinned.

**Phases:**
- **Phase 1:** a wrapper package importing from `ctc_align`, so zero pinned bytes change, plus golden tests (`to_record`,
  `recognition_evidence`, `alignment_sha256` on the frozen caches; CPU re-forward parity on 200 crops). Unpinned callers then move over.
- **Phase 2:** invert the shim at the next gate re-certification.

R2P (in flight) creates teacher-export and scorer code. It should call the phase-1 API once that exists. Until then, R2P adds no new
copies of strip, forward or alignment code beyond calling `ctc_align` as L1 did.

## 4. One card builder, one reader protocol, one owner-sheet renderer (`greekocr.adjudicate`)

**Today:** about 20 builders and scorers.
- The 0.6·h / ≤ 3× crop is copied 4 times.
- There are six different planted-control rules, and three Wilson implementations plus two LB95.
- Two C1 gates disagree (n ≥ 40 vs n == 100).
- **Blinding defects:** `deck.py` ships its key inside the page; print_truth, implicit and yer keep the key next to the blind items;
  implicit appends its controls unshuffled; the whole-line deck's image paths reveal book/page/line.
- **Steps with no code in any repo:** the R0 merge/tiebreak, the S8 cut/tiebreak decks, `audit100_final`, the whole-line deck, the yer
  items, and the owner pages, which are now preserved in `R2_evidence/page_builders`.

**Proposal** (reference implementation: `r0_prepare`'s write-once key and audit hook, plus `l1a2_cards`'s leak scan):

1. **`build_deck(spec) -> receipt`.**
   - Named crop profiles (`letter`, `word`, `mark`, `line`, `page`); controls by spec, shuffled into position.
   - Content-hash image names; a write-once private key in a sibling tree.
   - A leak scan, and schema/zoom/fraction asserts.
2. **Reader protocol.**
   - One instructions template and one answer schema: `{id, answer, printed, confidence: high|medium|low, note}`.
   - `deal(reader=2)` emits the reversed order in code.
   - `tiebreak_deck` re-randomises options; `resolve` takes 2 of 3, with the controls gate applied before resolution.
   - One `score` module: Wilson, document-cluster bootstrap, Clopper-Pearson.
   - One truth writer.
   - C1 becomes `readers=1` under the same gate function.
3. **`owner_sheet.render(lines, spec)`.**
   - The owner's template: full line with detections, Google/Ours rows, tags, one autosaving db note, optional Printed field, optional
     per-slot notes, hover magnifier.
   - CSS and JS as real package files, not `src.split` from other scripts.

**Replacements** (API appendix §2.4): the deck, sheet, R0, print_truth, implicit, S8, L1A2, collect_v3/C1, yer, owner pages and page_reads
builders all become profiles or specs of these three.

**Every blinding fix is a protocol change.** Results from the old decks stay valid only under the protocol they used, and are labelled
that way.

R2C (in flight) builds the R2 decks by copying the S8/L1A2 conventions. It is the first candidate to port onto `build_deck` once that
exists. Its resolve script is a first draft of `protocol.resolve`.

## 5. Archive (`docs/records/archive/<topic>_<date>/`, never deleted)

Leaf items with **no live code references** (marked row by row in the inventory appendix §3–§7):
- SF1–SF5 reports, but **not** their evidence where SF6/SF6c replays read it;
- S2/S3/S5-only files; the v1 labelfix deck; the S1 engine run;
- PAGE_LINES Q1–Q5 plus evidence; the CP-G and CP-H1 reviews; `docs/records/tables/`;
- the root-level `fixes` JSON;
- most closed briefs (T1–T29, S1–S7, SF1–SF5);
- `prototypes/harvest/`.

Blocked items:
- `S7_evidence` (884 MB) is blocked by one file that `test_sf2` reads. Move that file, or leave a stub, first.
- `docs/records/reviews/harness/run_review*.sh` and `docs/records/labelfix/spellcheck/print_truth/*.py` are **live code in docs**. They move to
  `scripts/review/`, with their outputs and sealed keys left in docs.

**Sourcing areas** (sourcing lead):
- Archive the T1–T3 funnel evidence (sol/funnel-gr/ia/intl), the T0 inventory (sol/source-inventory), and `docs/records/harvest/{screen_v1,
  inventory_v2,sample_v1}` in sol/collect-v3.
- `LABEL_CHECK_v2.md` moves only together with T6b/C1.
- `vertical_recut.py` (T6a, a negative result) goes to archive as code; it is not deleted.

## 6. Candidates for deletion (large generated artefacts only; owner approval required; listed with sizes)

| Path | Size | Condition |
|---|---:|---|
| sol-collect `worker/validation/` | 1.6 GB | after W2 closes (collector test fixtures) |
| sol-collect `docs/records/harvest/collect_v3/w1c_verified_replay` | 1.1 GB | after W2 closes |
| `…/rev2_final_replay`, `w1c_parity_replay`, `rev2_verified_replay`, `rev2_replay` | 281 + 269 + 224 + 224 MB | after W2 closes |
| `…/credential_*_replay`, `offline_replay/{W1,cache}` | small to medium | after W2 closes |
| `collect-v3-data/v2_masked/{l1e_sample, _r2, _r3, l1e_sample_vouli}` | 2.3 + 2.4 + 5.8 + 4.4 MB | after the spell-check track confirms no citations |
| toolkit `docs/*pytest-results.xml`, `.pytest_cache/`, `__pycache__/`, `.cache/m2_*.log` | < 1 MB | any time |

**Not deletable**, although they look like caches: `.cache/labelfix/**`, `artifacts/labelfix_r1/output_3678928/**`, the
`artifacts/labelfix_l1e/*.tar*` and `labelfix_sf3/*.tar*` files, and `collect-v3-data/v2_masked/v2_test` (1.3 GB harm-test evidence).

**Separate owner decision** (whole worktrees, not files):
- sol-inventory sparse copies: `pilots_v2` 5.6 GB, `round1` 849 MB, `collection` 738 MB, `oa_rebind_v1` 727 MB;
- sol-funnel-gr `sample_v1` 1.9 GB.

These are removed only by `git worktree remove`. Repository size itself needs an LFS/history-rewrite decision (§1.5).

## 7. In flight / frozen: do not move or edit

| What | Why |
|---|---|
| `greekocr/labelfix/*` | the 16 policy-bound paths + gate closure; sf6-release-v1 frozen (gate d893a04d) |
| sol/recut-v1 (T6b running) | brief 45e674d2 and `foreign_ink.py` hash-bound |
| sol/collect-v3 | W2 reading live since 10:22; pipeline/reader/rules/planner/resolution/vendor identity-hashed; `release_exclusions/` and `c1/` frozen |
| `~/Projects/collect-v3-data/run` | live run root: never write or lock |
| `collect-v3-data/v2_masked/{l1e_sample_r4, l1e_sample_vouli_r2, s8_dev}` | spell-check inputs |
| sol/l1e-mask, sol/wikisource-r0 | idle but cited (T6e, locked_eval_ia/ib) |
| R2 worktrees `-r2cards` (R2C) and `-r2prep` (R2P) | Sol runs in flight |
| every path in a `*_DEPLOY_SHA256.txt` | deploy receipts |

## 8. Order of execution (Sol, after approval)

1. **Done today:** commit the scratchpad builders (`R2_evidence/page_builders/`).
2. Merge the sibling branches into one line after their runs close: s8, l1, l1r*, l1f, r1, r0, and the R2 branches when they finish.
   Resolve the s8 `case.py`/`ink.py` gate-closure edits **explicitly with the coordinator**, because they touch the frozen gate.
3. Recogniser phase 1 (§3): wrapper + golden tests; move the unpinned callers.
4. `greekocr.adjudicate` (§4):
   - `owner_sheet` first;
   - then `build_deck` + protocol, re-emitting one past deck (R0 ib) from its spec and diffing it against the frozen blind files;
   - then S8/L1A2, print_truth, implicit, C1, and R2C.
5. Facade packages `greekocr/{review,bootstrap,reader,gate}` re-exporting the frozen core; move the 12 free scripts.
6. Archive moves (§5), one commit per topic, with no scripted rename over `docs/`: 425 code snapshots under `ASTRA-SC1c3_evidence/before_sf2/`
   must stay untouched.
7. Deletions (§6), only with the owner's explicit approval per row.
8. At the next gate re-certification: recogniser phase 2, and the pinned code moves.
