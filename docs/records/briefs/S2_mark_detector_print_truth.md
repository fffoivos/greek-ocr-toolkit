# S2 — Mark detector fixes, compound-mark classes, line-level metric against PRINT truth (gpt-6.1-sol, xhigh)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck`, branch `opus/spellcheck`). No `.git` writes: leave changes in the
working tree; the track lead reviews and commits. Never touch other worktrees. Network OFF.
Python: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python` (as is; no pip). CPU only; NO CTC forward passes
(alignments cached in `.cache/labelfix/align_s{0,1}.jsonl`, keys via `greekocr.labelfix.sheet.crop_key`). Whole run ≤ 20 min.

## Binding owner rules (16 Oct 2026)
1. **"For training OCR we need to transcribe what we see, not what we would like to see."** The Wikisource human text is a test reference
   only; where it normalises the print it is wrong. Truth = what is PRINTED. A correction is acceptable only if the proposed form is what
   is printed; lexical correctness never overrides the ink.
2. **Whole visible line, not one word.** The detector and the engine are evaluated per letter slot over the whole line: detected mark set vs
   printed mark set at every slot.
3. The recogniser only LOCATES. Never a voter, never a source of candidates.

## Print truth you will use
- `docs/records/labelfix/spellcheck/print_truth_s0.json`: blind two-reader (+ tiebreak) pixel adjudication of all 189 Google-vs-human mark
  differences on the three-way lines, key `"<line_id>|<google word index>"` → `printed` (the printed word, NFC; null = unresolved), `verdict`
  (`google` = Google read the print and the human normalised it; `human`; `other` = printed form differs from both). Planted controls 20/20.
- `docs/records/labelfix/spellcheck/owner_notes_db_20261016.jsonl`: the owner's 33 notes from the review sheet (supersedes the 15-line
  `docs/records/labelfix/owner_line_notes_20261016.jsonl`). **The `printed_field` is the sheet's unedited prefill (= Google's label) on all 33 lines; it is
  NOT print truth — never use it as such.** The `note` is the owner's per-slot verdict on the DETECTOR (slot numbers = letter components sorted by x
  as in `scripts/labelfix/sheet_build.py`, 1-based): "missed N at k" = N printed marks at slot k not detected (recall); "random dot/mark under k",
  "dot of exclamation mark is detected", "delta detected", "faint eta at k detected as accent", "part of 23 detected as subscript" = false marks
  (precision); "ellipsis at k missed" / "careful on the ellipsis at k" = the ELISION APOSTROPHE (’ after δ τ ρ θ π: μηδ’, ὁ δ’, ἔτ’, ῥ’) — NOT
  three dots. Turn every note into a machine-checkable expectation (`docs/records/labelfix/spellcheck/owner_slot_expectations.jsonl`: line_id, slot,
  expected = {missed: n} | {false: kind} | {apostrophe: true}) and report each one as fixed / not fixed after your changes. Where a note and the
  blind print truth disagree, report it; do not resolve it yourself.
- Elsewhere, per-slot printed marks = the human text where Google, human and the recogniser agree on the word (assume printed), the
  adjudicated `printed` form on the 189 words, and UNKNOWN on other disagreements (excluded, counted).

## Owner-reported detector failures to fix (`greekocr/labelfix/ink.py`, reuse `greekocr/glyphs/components.py` roles)
(a) **Ascenders taken as marks.** The attached path relabels any letter ink above `top − ATTACH_SLICE_XH·xh` as a mark, so δ β λ θ φ ξ ζ,
    capitals and tall punctuation produce "marks" (on the owner's 120-line sheet: 683 detached vs 710 attached blobs). New rule: an attached
    blob counts as a mark only if (i) it is separable from the letter body by a NECK (a local minimum of column-wise ink mass between the body
    band and the blob), (ii) its width ≤ 0.8 xh, and (iii) the component's main body does not itself rise above the meanline by more than
    0.3 xh except through that neck. Otherwise it is ascender ink (keep it as a diagnostic, never as a mark).
(b) **Specks below the baseline** become false iota-subscript evidence ("random dot under 6/9/19", "random mark under lambda"). Reject
    below-baseline blobs by size relative to xh, darkness, shape (a subscript is a short vertical stroke/wedge under the LEFT half of α/η/ω),
    and distance from the vowel body; ink touching the crop's bottom edge or belonging to the next line is never a subscript.
(c) **Punctuation taken as marks**: the dot of "!" and "?" ("dot of exclamation mark is detected", twice). Mask a dot that is vertically
    aligned with a stem below it, and components the glyph pass labels `punct` at baseline level. **The elision apostrophe ’ is NOT to be masked**:
    the owner wants it detected ("ellipsis at 22 missed", "ellipsis after 6 missed", "careful on the ellipsis at 3"). It has the shape of a smooth
    breathing but stands AFTER a word-final consonant (no vowel under it), at x-height top; report it as its own sign ('apostrophe') on the slot of
    the consonant, never as a breathing on the next word, and include it in the line-level metric as a separate kind.
(c2) **Letter parts taken as subscript** ("part of 23 detected as subscript"): descenders of ρ φ ψ χ γ μ ζ ξ ς and of the letter itself are not
    below-baseline marks; a below-baseline blob that is part of a letter component (or of the next line) is never a subscript.
(d) **Faint letters taken as marks** ("faint eta at 18 detected as accent"): a candidate whose component is a faint letter body
    (height ≥ 0.8 xh, sitting in the x-height band) is a letter, not a mark.
(e) **Compound marks (owner case 384c3f89-p000096-l0004, printed ᾗσι):** breathing + accent stacked or fused into ONE component (῍ ῎ ῏ ῝ ῞ ῟,
    breathing under perispomeni). The count check must accept one fused blob where the proposal implies breathing+accent, and the classifier
    must have compound classes (psili+acute, psili+grave, psili+circumflex, dasia+acute, dasia+grave, dasia+circumflex, each ± subscript) with
    enough samples. Compound marks are 3.9% of mark-bearing vowels but ~36% of the error vowels on these lines.

## Classifier
Rebuild `markshape` training samples with the fixed extractor (report how many samples change label/blob composition vs
`docs/records/labelfix/markshape_samples.jsonl.gz`), from the AGREEMENT set (Google = human = recogniser word, DEV_BOOKS only for fitting; the 14
held-out books never used for fitting or thresholds). Add the compound classes; if the three-way lines give too few compound samples, ALSO
harvest agreement samples (Google = recogniser) from the training collection crops on disk (`docs/records/harvest/collection/v2/import_real_v2_train.jsonl`
→ crops; alignments would need forward passes: NOT allowed here, so use only the lines whose alignments are cached, or the clusters you can
locate without the recogniser — e.g. single-vowel words; say what you did). Keep the old model file; write the new one beside it.
Report per class: samples, held-out recall, precision at tau, coverage. Report the **ascender false-mark rate per letter class** on the
agreement set (letters with no printed mark vs ascender letters δ β λ θ φ ξ ζ and capitals), before vs after the fix.

## Line-level metric (new module `greekocr/labelfix/linemetric.py`)
Per line: slots = letter components sorted by x (as `sheet_build.py`); map each slot to a character of the printed line through the
recogniser alignment (locator only); per slot compare detected mark set vs printed mark set → per-line and pooled mark precision / recall /
F1, split by mark kind (accent, breathing, compound, subscript, dialytika) and by failure class (a)–(e). Report:
1. the 33 owner-annotated lines: per line, each owner expectation fixed / not fixed, before vs after, the note next to it (slot truth on these
   lines = blind print truth for adjudicated words, the human text elsewhere where Google = human = recogniser, otherwise unknown);
2. the frozen HELD-OUT set = all lines of the 14 non-DEV Wikisource books (seed-0 crops; ≈ 666 lines with print truth as defined above),
   before vs after.

## Engine re-scoring against print truth
Re-run `spellcheck_validate` (S1 engine, unchanged decisions apart from the new extractor/classifier) scoring every decision against PRINT
truth instead of the human text: a correction is right only if it equals the printed form. Report the S1 tables both ways (human vs print)
and list every decision whose verdict flips. HOLD stays a separate column; report how often HOLD contradicts the print.

## Owner sheet (the track lead publishes it; you only build the HTML)
Extend `scripts/labelfix/sheet_build.py` (keep its format and notes script EXACTLY) with: `--lines <jsonl of line_ids>` input, a header with
the numbers (line-level mark P/R on held-out, before → after; ACCEPT / HOLD / L2 counts; false corrections vs print truth; iteration id = git
HEAD short sha + "dirty"), a "Printed" row from print truth where known, and the iteration's detector output. Notes script fix: the
"What is printed" textarea must be saved only when the owner actually edits it (store `printed_edited: true`); a note typed alone must not
save the prefill as if it were his reading (all 33 current `printed` values are unedited prefills). Keep the existing db collection `notes`
and its documents untouched. Show the owner's existing note under each card where one exists. Produce
`docs/records/labelfix/spellcheck/heldout_sample60.txt` = a FIXED random sample of 60 held-out line ids (seed 20261016, never change it) and build
`docs/records/labelfix/spellcheck/sheets/owner_iter_S2.html` = those 60 + every held-out line whose detection or decision changed in this iteration
(cap 140 cards; list the rest).

## Tests (`tests/labelfix/`; all existing must stay green)
Synthetic components for (a) ascender with/without neck, (b) speck vs subscript wedge, (c) exclamation dot and ellipsis, (d) faint letter,
(e) fused compound accepted by the count check; linemetric on a hand-made 2-line example.

## Deliverables
Code, tests, `docs/records/labelfix/spellcheck/S2_REPORT.md` (tables above + before/after crops listed by line id), the sheet HTML, and a last line:
`S2 RESULT: held-out line mark P …→… R …→… (owner 33-line expectations fixed …/…); ascender false-mark rate …→…; compound recall …; S1 ACCEPT vs print p=…% (LB95 …%), HOLD vs print p=…%`.
Final message: files changed, that line, anything you could not do.

## Do not
Use the recogniser's reading as a gate or a candidate; tune on held-out books; touch Google labels or the test instrument; run CTC forward
passes; widen scope (no geometry, no re-OCR, no LLM step).
