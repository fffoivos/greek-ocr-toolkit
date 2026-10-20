# CU4: clean-up step 4. One card builder, one reader protocol, one owner-sheet renderer (`greekocr.adjudicate`) (gpt-6.1-sol, medium, network OFF)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-cleanup`, branch `opus/cleanup-1`, head 7bc40ddc2 = CU3 + this brief).
- No `.git` writes; never pushed.
- Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`.
- Mac CPU, no model inference.

Spec: `docs/records/cleanup_20261017/CLEANUP_PLAN_20261017.md` §4 and appendix `docs/records/cleanup_20261017/CLEANUP_PLAN_20261017_api.md` Part 2 (§2.1–§2.4) and Part 3 step 4.
Blinding audit: `docs/records/cleanup_20261017/CLEANUP_PLAN_20261017_blinding.md`.

## Hard constraints

1. **No byte change to pinned code:** nothing in `greekocr/labelfix/`, nothing in the 16 `policy_binding` paths, no path in any
   `*_DEPLOY_SHA256.txt`. Prove it: pinned sha table before/after, plus the digest `6f62925a…c406`, which must be unchanged.
2. **Additive.** New package `greekocr/adjudicate/` with tests in `tests/adjudicate/`. Existing builders are NOT edited or deleted in
   this step; they become callers in a later step. Exception: unpinned scripts may gain a thin call-through, but only if the re-emission
   tests below prove identity.
3. **Read-only inputs from other worktrees:**
   - `~/Projects/greek-ocr-toolkit-spellcheck-r0` (R0 decks and keys);
   - `~/Projects/greek-ocr-toolkit-spellcheck` (scratchpad page builders committed under
     `docs/records/labelfix/spellcheck/R2_evidence/page_builders/`);
   - `~/Projects/greek-ocr-toolkit-spellcheck-r2cards` (R2C builder/resolver = the first draft).

   **Do NOT touch R2C's decks or any reader folder:** readers are working on them now.

## 1. `greekocr/adjudicate/owner_sheet.py` (FIRST)

`render(lines, spec) -> html`. The owner's template:
- **Page:** title, intro, groups with headings.
- **Per card:**
  - a line-id row;
  - the full line image with our detections (green above / blue below / grey attached, slot numbers);
  - optional extra zooms (word 3×, letter 8×);
  - a table of named rows (Google / Ours / Truth / Reader, …) with optional per-character highlight classes (yellow = changed with
    ink, red = changed without ink);
  - tags (pills);
  - ONE autosaving note per card in the artifact db (`window.claude` db, collection `notes`, configurable doc id: `{line_id}` or
    `{line_id}:s{slot}`, merge write, 900 ms debounce + blur flush);
  - an optional editable `Printed` field saved with the note;
  - the optional hover magnifier (Z=3, 300×130 lens, clean crop, tap toggle).
- **Assets:** CSS and JS ship as real package files (`owner_sheet.css`, `owner_sheet.js`), never `src.split` from other scripts. Light and
  dark tokens as in the current template.

**Re-emission tests (the owner's current template; required):**

(a) The 39-card **"Reader Errors Held-out"** sheet (published 17 Oct).
- Reference HTML: `artifacts/cleanup_step4/reference/reader_errors_heldout.html`, sha256 `9441fca8…cca8`.
- Original builder: `…/R2_evidence/page_builders/build_r1a_errors.py`.
- Write its spec as data, i.e. the 39 card records. The builder's inputs live in `~/Projects/greek-ocr-toolkit-spellcheck-r1` (score
  dir `artifacts/labelfix_r1/score_3678928_K1c_vsS6`) and in main's `docs/records/labelfix/spellcheck/print_truth_s0.json`; re-derive the spec
  from them, read-only.
- Render with `owner_sheet.render`, then **diff against the reference by content**: the same cards in the same order and sections; the
  same text of every row/tag; the same `data-*` / db doc ids (`{line_id}:s{slot}`) and Printed prefill values; the same images (decode
  the base64 and compare pixel arrays).
- Byte-identical HTML is not required. Report every non-identical element and why.

(b) The **"Accent Corrections Checked"** page (`artifacts/cleanup_step4/reference/accent_corrections_checked.html`, builder
`build_audit_template.py`): the same content diff, including highlight classes, tags and the magnifier clean crops.

## 2. `greekocr/adjudicate/deck.py` + `protocol.py`

**`build_deck(spec) -> receipt`:**
- named crop profiles `letter` / `word` / `mark` / `line` / `page`;
- controls inserted by spec and **shuffled into position**;
- content-hash image names;
- a private key written write-once (O_EXCL) to a sibling tree **outside** the blind dir;
- a leak scan (text, paths, image metadata);
- schema / zoom-cap / control-fraction asserts.

Reference implementation: R0's `r0_prepare.py` and `r0_freeze_ib.py` (r0 worktree), plus R2C's `r2_cards_prepare.py` leak scan.

**`protocol.py`:**
- one instructions template and one answer schema `{id, answer|choice, printed|transcription, confidence: high|medium|low, note}`,
  with adapters for the R0, S8 and R2C field names;
- `deal(deck, reader)`: reader 2 = reverse order, emitted by code;
- `tiebreak_deck` (re-randomised options, own private map);
- `resolve` (controls gate BEFORE resolution, 2-of-2 agree else 2-of-3, UNKNOWN preserved);
- `score`: Wilson z=1.959963984540054, document-cluster bootstrap (port from `s8_score_truth.py`), Clopper-Pearson LB95; one
  implementation each;
- one truth writer;
- C1-style single-reader checks described as `readers=1` with their gate spec. That is a **description, not a reduction**: every NEW
  deck uses two readers plus a tiebreak (owner rule).

**Re-emission test (required): the R0-ib deck.**
- Write `R0_cards_ib`'s spec (r0 worktree `docs/records/labelfix/spellcheck/R0_cards_ib` + its private key under `R0_adjudication_private/ib`,
  read-only).
- Re-emit with `build_deck` into a temp dir and diff: the item set and order, the options and their order, control placement, and
  images by pixel array.
- Name-hash differences are expected (old names vs content hashes); map them and report them.
- Any other difference is listed with its cause. A blinding improvement (e.g. a key location) is a *protocol change*: label it, don't
  hide it.

## 3. Report

`docs/records/cleanup_20261017/CLEANUP_STEP4_REPORT.md`:
- the API;
- the three re-emission diffs, item by item (summarised, with the full diff files in `artifacts/cleanup_step4/`);
- the pinned-path table and digest;
- tests: the full suite; the failures must be only the known pre-existing environmental set (test_collection_outputs 3,
  test_provenance_cli_api 2, test_apply_clean 5 errors);
- `docs/API.md` regenerated for the new public callables (generator `CALLS` entries, as in CU3b).

Last line:
`CU4 READY: greekocr.adjudicate (owner_sheet, deck, protocol); re-emit reader-errors <identical|n diffs>, accent-corrections <..>, R0-ib <..>; pinned unchanged <k>/<k>; digest 6f62925a <yes>; tests <n> passed, failures only pre-existing`.
