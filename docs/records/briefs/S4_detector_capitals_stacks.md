# S4 — Detector iteration 3: marks beside capitals, stacked marks, split letters, per-mark naming (gpt-6.1-sol, xhigh)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck`, branch `opus/spellcheck`, head c651d14c). No `.git` writes; leave changes
in the working tree. Network OFF. Python: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python` with
`PYTHONPATH=$PWD`. CPU only, NO CTC forward passes (cached alignments). Whole run ≤ 20 min.

## The task (owner, 16 Oct 2026)
"An algorithm that fact-checks all accents. It works independently from Google, otherwise how can it correct Google." Our reading of a
line = letters from OUR recogniser + every mark from OUR detector; nothing from Google. Evaluate on whole lines, per letter slot, against
print truth (S2/S3 instruments). S3 is the baseline: do not regress precision; report every regression in the last line.

## Four owner-found failures to fix (greekocr/labelfix/ink.py + markshape)
1. **Marks beside capitals.** A mark is credited to a letter only when its centre lies in [x0 − 0.1 xh, x1 + 0.2 xh] (ink.py ~line 268). On
   a capital the breathing/accent is printed BEFORE the letter at its upper left (Ἦ, Ὅ, Ἄ, Ὡς, Ἡ), so it is dropped or credited to the wrong
   letter (owner lines read "Ηταν" with no marks). For a capital (component height ≥ 1.25 xh, or a capital in our recogniser's reading),
   also search the gap to its LEFT — from the previous letter/word (or the line start) up to the capital's x0, vertically from the capital's
   top to about its mid-height — and credit mark blobs there to the capital. Never take them from the previous word's last letter.
2. **Stacked marks** (owner case 384c3f89-p000096-l0004, ᾗσι): a breathing under a perispomeni prints as two stacked components; the upper
   arch (component #3 at x533–555, y7–19) is labelled `neighbour` (ink of the line above) by the glyph pass and never considered. A blob
   sitting directly above another mark blob, horizontally centred over the same vowel (within the vowel's width), not touching the crop's
   top edge, and within ~1.3 xh above the meanline is a stacked mark of that vowel.
3. **Split letters**: the same η prints as two letter components (#24 left stroke, #29 right stroke with tail); the breathing is credited
   to both slots. Two adjacent letter components that together are ≤ 1.6 xh wide and covered by one recogniser character are one letter;
   marks are credited once, over the union.
4. **Unnamed pairs** (owner case 384c3f89-p000068-l0028, slot 28, ἂσσον): both blobs are found but the classifier cannot name the pair
   (psili+grave, p 0.38 < 0.5) → "unnamed" and the letter gets no marks. When the whole-set class is below threshold and there are ≥ 2
   blobs, classify each blob separately (breathing kind from shape/orientation, accent kind from slope/shape, perispomeni from arch shape)
   and compose the set; keep "unnamed" only when a single blob cannot be named.

## Measure (before = S3, after = S4)
Held-out per-slot P/R/F1 by mark kind; **capitals with printed marks: recall before/after** (new stratum); compound/stacked recall; the
owner's 59 note expectations (v8 slots); ascender false-mark rate; per-book subscript recall. List the owner lines whose reading changed.

## Independent reading for the owner's page
Add `greekocr/labelfix/reading.py`: `read_line(crop, recogniser_text, alignment, model) -> str` = our independent line (letters from the
recogniser text; marks from the detector per slot; an unnamed mark is kept as a flag in a parallel structure, not as "?"). Tests on the two
owner cases (ᾗσι must read with breathing + perispomeni + subscript; ἂσσον must read ἂ), and on two capital cases from the owner's notes
(177b717d-p000013-l0009 "Ἦταν", 51fe7386-p000024-l0015 "Ὁ Ὅλυμπος … Ὅσσα").

## Deliverables
Code, tests (all existing green), `docs/records/labelfix/spellcheck/S4_REPORT.md`, last line:
`S4 RESULT: held-out P …→… R …→…; capitals R …→…; stacked/compound R …→…; owner expectations fixed …/59 (S3 35/59); regressions: …`.
Do not build or publish the owner sheet (the track lead does).

## ADDED before launch: the owner's 33 new notes + compound training samples
- **Owner notes** (`docs/records/labelfix/spellcheck/owner_notes_examples_20261016.jsonl`, written 20:58–21:27 Athens on the examples page
  https://claude.ai/artifact/4bQm77YCsSfe1YMtvxCuq4; slots = letter components sorted by x as drawn by `scripts/labelfix/sheet_build.py`
  with the S2 or S3 detector — resolve each note against both slot lists and record which one matches; ambiguous → report). Almost all
  are DETECTION failures: "missed at k" / "missed 2 at 6" / "missed all accents except 1" (recall), "missed ellipsis at k" = missed ELISION
  APOSTROPHE, "missed quote" = an opening quote mark, "misread εις as one letter" / "missattributed lambda at 6-7" / "misread rho at 7 and
  21" = letter-component segmentation/slot errors, "missed sub at 21" = subscript. An EMPTY note means the line was judged correct (no
  regressions allowed on those lines). Turn every note into a machine-checked expectation (`owner_examples_expectations.jsonl`) and report
  fixed / not fixed before → after, together with the earlier 59.
- **Compound-mark training samples now exist**: Clariden job 3678590 aligned 91,469 training lines (alignments
  `.cache/labelfix/clariden/C1_alignments.jsonl.gz`, selection `.cache/labelfix/clariden/C1_selection.jsonl`; report
  `docs/records/labelfix/spellcheck/clariden/C1_REPORT.md`). Agreeing compound clusters: psili+acute 34,343, dasia+acute 26,360, psili+circumflex
  13,537, psili+grave 5,085, dasia+circumflex 2,285, dasia+grave 1,098, dasia+circumflex+subscript 218. Crops are under
  `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/harvest_big/` (read-only). Retrain the mark classifier on
  agreement samples (word where Google = recogniser) from AT MOST 10,000 of those crops on this MacBook (compound-bearing lines
  oversampled, every class with ≥ 200 samples where available), plus the existing DEV samples; never the 14 held-out books. Report
  per-class held-out recall/precision, compound classes included.
- A partial, interrupted earlier attempt of this brief is saved at
  `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/s4_partial.patch` (+
  `s4_partial_reading_moved.py`); read it if useful, the working tree is clean at the brief's head.
