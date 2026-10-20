# S1 — Polytonic spell checker: deterministic stage + lexicon-proposes / ink-decides engine, measured on the three-way lines (gpt-6.1-sol, xhigh)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck`, branch `opus/spellcheck`). No `.git` writes (the sandbox cannot write the
git dir): leave all changes in the working tree; the track lead reviews and commits. Never touch other worktrees. Network OFF.
Python: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python` (use it as is; do not pip install).
The MacBook runs this: CPU only. NO new model forward passes are needed: CTC alignments for every three-way crop of both seeds are cached
in `.cache/labelfix/align_s{0,1}.jsonl` (keys are absolute paths of another checkout — match them with `greekocr.labelfix.sheet.crop_key`).
If a handful are missing you may align at most 500 crops with `ctc_align.Recognizer`. The whole validation run must take ≤ 15 min.

## The task (owner, 16 Oct 2026, verbatim intent)
"A spell checker that corrects polytonic accents, and also coordinates with the tools we have already developed for char/accent detection:
if the correct accents do not exist in the label and they are detected in the line, they should be corrected." "Only when they agree we
should add them." Deterministic corrections first. Every correction must be justifiable by the image; when the image is ambiguous it does
not hurt to hold the lexically correct text (HOLD). **The recogniser is NOT a voter: it only LOCATES characters.** Its reading of the word is
a diagnostic column (`model_agrees`), never a gate and never a source of candidates.

## Read first
- `docs/records/labelfix/spellcheck/T1_reachability.md` (+ `reach.md`, `reach_s{0,1}.jsonl`): the census of the 185 Google mark errors by the stage
  that can reach them, and the findings N1–N5 below. `greekocr/labelfix/reach.py` has `written_freq`, `spell_props`, `final_grave_form`.
- `greekocr/labelfix/spellink.py` (the started engine: `proposals`, `locate`, `judge`, `spell_ink_line`) — finish it, do not restart.
- Existing pieces to reuse, not rewrite: `lexicon.py` (regime lexicons, `ATTESTED_MIN`, `RATIO_MIN`), `constraints.py` (`violations(...,
  hard_only=True)`, `ENCLITICS`), `ink.py` (`analyse`, `mark_evidence`, abstentions, `slope_sign`, `dialytika_shape`), `markshape.py`
  (classifier, `tau` = 0.998 at 99% held-out precision, `mark_class`), `ctc_align.py` (`Alignment.window`, `transfer_alignment`),
  `candidates.py` (`pair_tokens`, `acute_house_style`), `validate.py` (`load_three_way`, `truth_map`, `lb95`, `DEV_BOOKS`, regime per doc),
  `sheet.py` (crop-and-text sheet). `rules.py` is the OLD design (model as voter): keep it working and reproducible; do not change its output.
- `docs/records/labelfix/REPORT.md` §2, §9, §12, §13 for method and the policy defaults.

## Owner policy defaults (confirmed by the coordinator 16 Oct)
Strict attestation (leave any Google form attested ≥ `ATTESTED_MIN`) is the default; report `ratio` (alternative ≥ `RATIO_MIN`× more frequent)
as an extra column. Line-initial capitals are correctable when the lower-cased form is attested ≥ 50 and is not a known name. Prints that use
acute everywhere follow the print (no grave correction there). Guards (Latin/digits, all caps, hyphen line end, abbreviation, capitalised
non-initial word) stay, with counts.

## Engine: stages and columns
For every Google word of a line (polytonic regimes only), the first stage that applies:

**D1 constraint** — Google's word breaks a hard constraint. Candidate repairs: forms that differ only in marks, resolve every violation, and are
attested (or, if no attested form exists, the unique constraint-valid minimal mark change). The ink decides via `judge`.
**D2 grave (positional)** — a final-syllable acute, another word follows on the same line, no trailing punctuation, the next word is not an
enclitic (the acute stays before an enclitic). "Follow the print": decide the print's style per BOOK from the INK (the slope of final-syllable
accent blobs over the book's lines, with `slope_sign`), NOT from Google's text, which itself writes acute for grave about 1,000 times per seed on
v2_test. The word is corrected when an accent blob exists over the final vowel and the book prints graves, and the blob's slope does not read acute.
At a line end or before punctuation (T1: 13 + 16 errors, 6 correct line-final acutes on the same lines) position decides nothing: ACCEPT only on a
decisive grave slope; never HOLD.
**L1 lexicon proposes** — Google's word unattested (`written_freq` < `ATTESTED_MIN`, N1 applied) or impossible; proposals = attested forms that
differ in the marks of one cluster (`spell_props`, N1/N2 applied). The ink decides; with competing proposals the ink picks one or abstains.
**L2 ink-contradicts (real-word errors, the biggest class: 66 of 185)** — Google's word IS attested. At each of its mark-bearing clusters
(located by the model's alignment), if the mark-shape classifier reads a class ≠ Google's at p ≥ τ, and the form with that class is attested
(≥ `ATTESTED_MIN`, possible under the hard constraints), propose it; the same blob-count / subscript / two-dots checks as `judge` apply.
Lexicon and ink must both agree. Keep it cheap: only clusters whose Google marks have an attested alternative in `Lexicon.variants`.

Columns, reported separately everywhere, never merged:
- **ACCEPT**: the ink confirms the proposal (`judge` passes: classifier at τ, blob count, subscript, dialytika, attached-breathing guard).
- **HOLD** (owner's ambiguous-image allowance): ONLY for a unique proposal from D1 or L1, when the ink does NOT CONTRADICT it. Define contradiction
  concretely and test it: the proposal needs a subscript and no blob below exists in an unclipped band; the proposal needs two dots and
  `dialytika_shape` finds none; the proposal adds a breathing/accent and the above-blob count is clearly lower; the classifier reads Google's own
  class with p ≥ `tau_contradict` (pick it on DEV_BOOKS only; report it). Abstention (faint, clipped, merged, localisation) is NOT contradiction.
  Never HOLD for L2, for dialytika-only proposals (N5), for competing proposals, or for D2.
- **diagnostic**: `model_agrees`, the old `rules.py` decision on the same word, the ratio-policy decision.

## Findings to implement (from T1)
- **N1** `Lexicon.freq` maps grave→acute but not acute→grave; a correct final acute whose lexicon form is mostly grave looked unattested (11 of 30
  false proposals). Use `written_freq` and drop proposals differing only in final acute↔grave (D2 owns those). Put the fix in `spellink`, not in
  `Lexicon.freq` (so `rules.py` stays reproducible).
- **N2** an initial ρ breathing is optional in 19th-c. prints: no ρ/ῥ-only proposals.
- **N3** L2 above.
- **N4** grave at the line end or before punctuation needs the slope (D2 above).
- **N5** dialytika-only proposals are an edition convention (Homeric edition 384c3f89 prints ἐυ-, ἀυ- without dots): ACCEPT only with the two dots
  in the ink; never HOLD.

## Measurement (both seeds; strict default, ratio column; DEV_BOOKS / held-out books / both)
A runner `python -m greekocr.labelfix.spellcheck_validate --seed 0 --seed 1 --out docs/records/labelfix/spellcheck` writing:
1. Per stage × column: candidates, decided, = human (TP), Google-right (FP: Google = human and we changed it), both-wrong, precision and the exact
   Clopper–Pearson 95% lower bound (`validate.lb95`).
2. Recall over the T1 universe (`reach_s{seed}.jsonl`, 185 errors; human-text errors excluded): recovered by ACCEPT, by ACCEPT+HOLD, split by
   "model also wrong" vs "model right", and by T1 stage. Add the old design's recall on the same universe and the union.
3. False fires on correct Google words, per stage × column, with the words listed.
4. Abstention reasons per stage (counts), and the unreached errors with the reason each was not reached.
5. Thresholds (`tau_contradict`, the book style for D2) are chosen on DEV_BOOKS only; say so in the report and show held-out numbers separately.
6. A crop-and-text sheet per stage for every ACCEPT and every HOLD decision, true or false, in EXACTLY the owner's format
   `docs/records/labelfix/spellcheck/sheet_format_reference_v4.html` (images stripped; same CSS and markup): per card (a) the full line crop;
   (b) a zoom row: the disputed vowel region upscaled, with the marks the detector found drawn on it (green = above the letter, blue = below,
   red = the vowel window, grey = meanline and baseline) and a caption "marks found: N above, M below · shape classifier: <class> p=… (threshold …)
   · ink verdict: supports / contradicts / abstains (<reason>); lexicon: …" plus the decision string; (c) a table Google / Human (test reference) /
   Tool with the word in `<mark>`; (d) pills: stage, column (ACCEPT / HOLD), outcome (= human / Google was right / both wrong). Extend
   `greekocr/labelfix/sheet.py` to render this (it already does crops + word boxes from the cached alignments, theme tokens and page contract);
   write rows jsonl + one self-contained html per stage under `docs/records/labelfix/spellcheck/sheets/`.

## Tests (`tests/labelfix/test_spellcheck.py`; the existing 79 must stay green)
N1 (τοκετός gets no grave proposal), N2, N5, the D2 enclitic and punctuation cases, the contradiction tests on synthetic `MarkEvidence`-like
inputs (no blob below → contradicts a subscript proposal; clipped band → abstain, not contradict), L2 proposing only attested forms, the
locator never deciding (a test where the model reads a different word and the decision does not change).

## Deliverables
Code (`spellink.py` finished; `spellcheck_validate.py`; any small helpers), tests, `docs/records/labelfix/spellcheck/S1_REPORT.md` with the tables above, a
short "what each stage reaches and why the rest is not reached" section with line ids, and a last line: `S1 RESULT: ACCEPT p=…% (LB95 …%) recall …%
(model-wrong …%); HOLD p=…% (LB95 …%) +…% recall; L2 …; D2 …`. Your final message: files changed, that last line, paths, and anything
you could not do.

## Do not
Use the model's reading as a gate or as a candidate source; tune any threshold on held-out books; modify Google labels or the test instrument;
change `rules.py` behaviour; run more than 500 model forward passes; open new tracks (geometry, crop repair, re-OCR). If something blocks you,
write it in the report and stop.
