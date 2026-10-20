# Google-label correction pipeline (labelfix) — report

Branch `fable/label-correction`, 16 Oct 2026. Code: `greekocr/labelfix/`; tests: `tests/labelfix/`;
reports and artefacts: `docs/records/labelfix/`. Nothing under `docs/records/harvest/collection/` and no existing
label file was modified; no label has been rewritten anywhere — this branch produces evidenced
*proposals* and the instruments to judge them.

## 1. What was built

| piece | file | what it does |
|---|---|---|
| text layer | `greekocr/labelfix/text.py` | NFD tokens with edge punctuation split off; vowel clusters; `classify_diff` (the single allowed difference between two word cores); guards |
| lexicons | `greekocr/labelfix/lexicon.py`, `build_lexicon.py` | three regime lexicons from proofread human text; mark-stripped key → attested marked forms; per-line/per-document regime choice |
| CTC alignment | `greekocr/labelfix/ctc_align.py` | loads the E3 checkpoint through the vendored training stack, replicates the factory strip (`import_real.rs::strip`), maps argmax frames to x ranges in crop pixels (STRIDE 4 × h/48) |
| ink evidence | `greekocr/labelfix/ink.py` | reuses `glyphs.components.line_glyphs` (the component extraction and band fit that `pages/lines.py` consumes); mark blobs above / below the located vowel with bounding boxes, principal-axis angle, elongation, darkness, border contact |
| rule engine | `greekocr/labelfix/rules.py` | pure functions; accepted / rejected / `abstain:*` / `excluded:*` with reasons; lexicon and ink verdicts kept separately |
| candidates | `greekocr/labelfix/candidates.py` | Google-vs-model word pairing through a character alignment; evidence records |
| validation | `greekocr/labelfix/validate.py` | three-way lines, book split, LB95, net edits, ablations, strata, recovery, controls |
| sample run | `greekocr/labelfix/sample.py`, `textstage.py` | candidate run on 5,000 training lines; text-stage counts over all 32,686 non-Wikisource test lines |
| review deck | `greekocr/labelfix/deck.py` | static HTML deck with blinded cards and controls; `--append` adds batches without touching answered ones |
| constraints | `greekocr/labelfix/constraints.py` | hard orthographic constraints of polytonic Greek → rule `constraint` (no lexicon, ink still required) |
| owner decisions | `greekocr/labelfix/ingest_decisions.py` | ingests the deck's decisions JSON → `owner_review_summary.md` |

Unit tests: `tests/labelfix/test_rules.py` (rule engine, guards, abstentions, constraint rule),
`tests/labelfix/test_alignment.py` (token pairing, frame→span mapping, alignment transfer),
`tests/labelfix/test_constraints.py` (each orthographic constraint, positive/negative) and
`tests/labelfix/test_ingest.py` (owner-decision ingestion): **64 passed**
(`.venv/bin/python -m pytest tests/labelfix -q`).

## 2. Method

A training label (Google Document AI) is a candidate for correction at a word position where the
recogniser (E3 `full` arm, seed 0, `out/e3b/jobA/runs/full_s0/best.pt`) reads the word differently.
A candidate is **accepted** only when three independent witnesses agree against Google:

1. **Lexicon** — the model's form is attested (count ≥ 5) in the line's regime lexicon and Google's
   form is not (policy `strict`: a Google form attested ≥ 5 is always left alone, even if rarer;
   a Google form with count 1–4 is treated as corpus noise and must be ≥ 20× rarer, 50× for base
   letters). Policy `ratio` (the literal "≥ 20× rarer" of the brief) is computed for comparison.
2. **Difference type** — the whole difference is either combining marks on one vowel cluster
   (breathing / accent / iota subscript / dialytika; more than one category on the same cluster
   is the rule `marks_multi`) or one base-letter substitution from {ε↔ι, ο↔α, ο↔σ, ν↔υ, π↔τ,
   ρ↔ο, ι↔υ, 0↔ο} (`base_sub`) or σ↔ς at the word end (`final_sigma`). Nothing else: no
   insertions, deletions, multi-letter or multi-cluster changes.
3. **Ink** (mark rules) — in the located vowel's window the blob count above the vowel equals the
   count the model's reading implies (dialytika counts two); a subscript needs a small detached
   blob under the baseline; an accent that *changes* must have a discriminative shape: exactly one
   oblique blob whose slope agrees (acute rises to the right, grave falls), or a non-oblique blob
   for a circumflex. Base-letter rules have no ink check (margin ≥ 50× instead) and additionally
   abstain when Google's letters spell an attested word under other marks (so a mark error is not
   turned into a different word).

`final_grave` (acute ↔ grave on the last mark-bearing cluster) is a separate rule: the lexicon is
position-blind (both forms are attested), so the only admissible evidence is the ink slope. There is
no positional exception — without one readable oblique mark whose slope agrees with the model, the
rule abstains; it also abstains before trailing punctuation.

**Abstentions** (the evidence cannot be read): uncertain regime (the two polytonic lexicons attest
the line about equally); uncertain localisation (the CTC span does not snap to exactly one letter
component, or neighbouring marks sit in the window and the mark count changes); faint blob; a blob
wide enough to be two fused marks when the count disagrees; a wide blob under a mark *removal*;
clipped top when a mark is removed (no "false absence"); clipped bottom when a subscript changes.

**Guards** (never corrected): capitalised words anywhere (proper-name shape; line-initial words
included, conservatively), abbreviations (trailing `.`, ≤ 3 letters), words with Latin letters or
digits, hyphenated line ends, all-caps words for mark rules; polytonic-only marks are never
introduced into a document whose regime is monotonic.

**Regime** per document: majority of per-line choices; a line with a polytonic-only mark in either
reading is polytonic (ancient vs 19th–20th c. by which lexicon attests more of its undisputed
words; ties → `poly19`); otherwise `greek_mono` → `mono`; the script class alone is not trusted
because it is derived from Google's (possibly mark-less) label.

**Localisation**: CTC spikes sit left of the printed glyph and accents on leaning print overhang
the vowel's right edge, so the frame positions only select the letter component they overlap most;
that component's bounding box becomes the vowel body and marks are credited to it only if their
centre lies within [body − 0.1 xh, body + 0.2 xh]. Attached marks (accent fused to its vowel) are
recovered by re-labelling the letter component's ink above the mean line (vowels have no ascender).

### What the spell checker may and may not do

It is a frequency lexicon, not a normaliser. It may only break a tie between two readers of the
same crop: it says whether the model's form exists in proofread text of the right orthographic
regime and whether Google's does. It never proposes a form of its own, never changes a word both
readers agree on, never touches a word whose Google form is attested in the regime (archaic and
dialectal spellings, -ις/-εις, double consonants, ᾑ/ῃ: if both forms are attested, Google's stays),
never acts across regimes (a monotonic Wikisource text cannot attest a polytonic reading or vice
versa — the lexicons are regime-pure by construction), and never overrides the image: a mark
change is applied only when the ink supports it. Its sources are listed with counts in
`docs/records/labelfix/lexicon_report.md`; they contain no Google output and no recogniser output; the
Wikisource works of the evaluation set are excluded by title and any line sharing a 4-word shingle
with an evaluation line is excluded.

## 3. Lexicons

See `docs/records/labelfix/lexicon_report.md` (sources, provenance evidence, per-source counts, exclusions).

| regime | sources on disk | distinct forms | forms ≥ 5 | tokens |
|---|---|---:|---:|---:|
| ancient | First1KGreek, classical literature corpus (`klasikh_arx_ell_grammateia`) | 867,945 | 207,201 | 24.5 M |
| poly19 | Greek Wikisource dump (polytonic lines only) | 692,084 | 161,846 | 14.5 M |
| mono | finewiki (el Wikipedia), EUR-Lex el, Europarl el, Gutenberg el (monotonic transcriptions) | 417,399 | 115,151 | 26.5 M |

Not on disk although listed in `data/sources.json`: Perseus canonical-greekLit, Wikinews el.
Gutenberg el on disk carries 0 lines with a polytonic-only mark (monotonic transcriptions), so it
attests the monotonic regime, not the 19th-century polytonic one the brief assumed. `estianews`
was excluded on purpose: its house style prints acute for grave, which would attest the wrong
final-syllable accent.

## 4. Validation on the three-way lines

Full tables: `docs/records/labelfix/validation_wikisource.md` (per seed × policy: per-rule tables for all /
dev / held-out books, release-candidate verdicts, ablations, agreement rates, per-mark recovery,
reader-agreement strata, direction / regime / book / line-length breakdowns, abstention reasons,
physical controls, every accepted correction that does not match the human text). Per-candidate
evidence: `validation_candidates_s{0,1}_{strict,ratio}.jsonl`; per-line records:
`validation_lines_s{0,1}.jsonl`; machine summary: `validation_summary.json`.

Set: the 1,264 Greek lines of the `wikisource_human` instrument (1,392 minus 128 Russian), 17
books; the brief's "1,186 lines / 15 books" could not be reproduced from the files, so all 1,264
are reported. Dev books (thresholds were set while inspecting their lines): `8b6b0de9` (Διονύσου
πλους, 233), `02a3a2a6` (Ἀτθίδες Αὖραι, 202), `2793d64c` (Ο Κόδρος, 163) = 598 lines; held-out:
the other 14 books = 666 lines, dominated by `384c3f89` (Argonautica, 361, ancient regime). Human
lines carrying a leading `::` (Wikisource indentation markup, 141 lines) were stripped of it.

Seed 0, policy `strict`, all books (the headline numbers):

| rule | candidates | excluded | abstained | rejected | accepted | = human | Google right (FP) | human ≠ both | precision | LB95 | net edits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| breathing | 54 | 14 | 0 | 39 | 1 | 1 | 0 | 0 | 100.0% | 5.0% | +1 |
| accent | 74 | 20 | 0 | 51 | 3 | 3 | 0 | 0 | 100.0% | 36.8% | +3 |
| subscript | 35 | 1 | 0 | 32 | 2 | 2 | 0 | 0 | 100.0% | 22.4% | +2 |
| dialytika | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| marks_multi | 15 | 4 | 0 | 11 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| final_grave | 28 | 5 | 9 | 0 | 14 | 13 | 0 | 1 | 92.9% | 70.3% | +13 |
| base_sub | 7 | 1 | 0 | 6 | 0 | 0 | 0 | 0 | - | 0.0% | +0 |
| constraint | 9 | 0 | 0 | 8 | 1 | 1 | 0 | 0 | 100.0% | 5.0% | +1 |
| **all** | 214 | 46 | 9 | 138 | 21 | 20 | 0 | 1 | 95.2% | 79.3% | +20 |

Seed 1, `strict`: 197 candidates, 20 accepted, 19 = human, 0 Google-right, 1 human ≠ both (the same
word as seed 0), precision 95.0 %, LB95 78.4 %, net +19 (breathing 1/1, accent 3/3, constraint 1/1,
final_grave 15 accepted / 14 = human). Policy `ratio` accepts exactly one candidate more than `strict` on each
seed: `βήμα → βῆμα` (human βῆμα; Google's form has count 5 in poly19, the model's 366), i.e. 21 / 20
correct (seed 0) and 20 / 19 (seed 1).

Held-out books only (seed 0 / seed 1): 7 / 6 accepted, all = human, 0 FP; per rule breathing 1 / 1, accent 2 / 2, final_grave 3 / 2, constraint 1 / 1. **No rule reaches the release-candidate gate** (LB95 ≥ 99 % needs
≥ 299 consecutive correct corrections; the largest rule has 15). Every rule is **proposal-only**:
its corrections can be verified one by one (the deck) but must not be auto-applied.

The single accepted correction that differs from the human text (both seeds) is `φωλεά → φωλεὰ`
(human: `φωλέα`), `docs/records/harvest/harvest_big/wikisource/crops/8b6b0de9/p000016-l0013.png`: the
crop was inspected — the print reads φωλεὰ (grave on the final α); the Wikisource transcription
is wrong there. Counted against the pipeline in every table nonetheless.

Ablations (seed 0 `strict`, all books, known-truth candidates passing the stage; seed 1 in brackets):

| stage | accepted | = human | precision | LB95 | net edits |
|---|---:|---:|---:|---:|---:|
| model only (every allowed difference) | 166 (155) | 91 (77) | 54.8 % (49.7 %) | 48.1 % | +33 (+21) |
| model + lexicon | 39 (34) | 35 (32) | 89.7 % (94.1 %) | 78.0 % | +39 (+35) |
| model + ink | 45 (39) | 37 (31) | 82.2 % (79.5 %) | 70.2 % | +32 (+24) |
| full conjunction | 20 (19) | 19 (18) | 95.0 % (94.7 %) | 78.4 % | +19 (+18) |

Agreement with the human text on mark candidates where both witnesses gave a verdict and the
outcome is model-right or Google-right (seed 0; seed 1): lexicon alone says "model" on 23 (18),
right 95.7 % (100 %); ink alone on 29 (24), right 82.8 % (70.8 %); lexicon AND ink on 6 (4), right
100 % (100 %); neither on 81 (70), the model is right only 35.8 % (27.1 %) of those.

Per-mark recovery (seed 0): the human text exposes 193 recoverable Google errors (single allowed
difference) on these lines; the pipeline recovers 19 (9.8 %) with 0 false corrections — by rule:
final_grave 13 / 49 (26.5 %), accent 3 / 48, subscript 2 / 30, breathing 1 / 45, marks_multi 0 / 16,
base_sub 0 / 4. Recall is deliberately sacrificed: the main losses are the lexicon
(`model_form_unattested`: the correct form is a rare word or inflection absent from the regime
lexicon; `both_attested`: both forms exist, e.g. βήμα/βῆμα across regimes within Wikisource),
the proper-name guard (18 Google-right and 17 model-right candidates excluded), and the ink
abstentions on fused or neighbouring marks. Reader-agreement strata, direction, regime, book and
line-length breakdowns are in the validation file; the agreement control (Google = model on 947
lines, of which 351 still differ from the human text) bounds what any model-vs-Google method can
reach. Physical controls: of 450 lines with a clipped band 7 corrections were accepted, all =
human; specks 0 / 10 candidates; faint ink 0 / 6; neighbouring ink 2 / 43 (both = human); long
lines 5 / 86 (all = human).

Typeface class is not derivable (every real line is `font_style_unknown`); all lines are one wave.

## 5. Candidate run on the training sample

`docs/records/labelfix/candidates_train_sample.jsonl` (564 candidates with every field of evidence) and
`candidates_train_sample.md` (per rule × wave, projection, reasons). 5,000 random admitted rows of
`import_real_v2_train.jsonl` (seed 20261016; the file holds 214,436 admitted rows, 207,851 after
codec per E3_RESULTS): Google = model on 3,510 lines; 502 lines carry a candidate; **67 accepted
corrections (1.34 % of lines)**: final_grave 44, accent 12, breathing 5, base_sub 4, subscript 2,
marks_multi 0, dialytika 0, final_sigma 0. Projected to the 207,851-row train set (per-wave rates):
**≈ 2,815 corrections** (final_grave ≈ 1,839, accent ≈ 508, breathing ≈ 214, base_sub ≈ 169,
subscript ≈ 86). Per wave (accepted per 1,000 lines): parliament 1975–83 polytonic volumes carry
most final_grave corrections (12.7), round1 15.8 for final_grave; openarchives and cyrillic ≈ 0.

A second set, for the deck only: 2,400 non-Wikisource `v2_test` lines whose text-stage candidate
passed the lexicon (`textstage.py` over all 32,686 such lines: 1,044 breathing, 1,862 accent, 364
subscript, 33 dialytika, 368 marks_multi, 915 final_grave, 438 base_sub, 2 final_sigma text-stage
candidates) → `candidates_v2test_extra.jsonl`, 426 accepted (final_grave 299, accent 40, breathing
31, base_sub 29, marks_multi 18, subscript 8, final_sigma 1). These are test-set lines: they feed
the deck, never a label file.

## 6. The review deck

`docs/records/labelfix/review_deck/index.html` (+ `deck_data.js`, `cards/`, `README.md`; static, opens
from disk). Seven batches (plus the appended `constraint` batch, §9): breathing 36 correction/label cards + 18 negative + 1 positive control,
accent 52 + 20 + 3, subscript 10 + 13 + 2, marks_multi 18 + 6 + 0, final_grave 100 (of 343
available, stratified by wave) + 2 + 10, base_sub 33 + 5 + 0, final_sigma 1. Only final_grave has
100 accepted candidates; the other rules show every accepted candidate there is (the accepted
rate is 1.3 % of lines, so 100 per rule would need ~8,000–60,000 more forward passes, i.e. the
Clariden run). Cards show native pixels (CSS zoom, `image-rendering: pixelated`), the disputed
letter boxed, the word underlined, and one reading drawn at random (70 % the correction, 30 % the
Google label), never saying which; negative controls (model form contradicted by the human text)
and positive controls (human form) are mixed in. Keys y / n / u; localStorage; JSON download;
the summary page computes precision and the exact 95 % lower bound on the correction-shown cards,
the yes-rate on label-shown cards and the false-yes rate on negative controls. The README states
that corrected labels are derived, not truth, and that a model-corrected test instrument cannot
judge the proposing model.

## 7. Failure cases seen (crop paths)

- Fused breathing + accent read as one mark: `εὔτ' → εὐτ'` (print εὖτ’),
  `docs/records/harvest/harvest_big/wikisource/crops/384c3f89/p000091-l0014.png` — accepted by the first
  version on a blob count of 1; now `abstain:removal_with_wide_blob`. Fused pairs also cost recall
  (`abstain:merged_marks`, 24 candidates in the sample, 7 model-right ones on the three-way lines).
- Human transcription error counted as our failure: `φωλεά → φωλεὰ`,
  `wikisource/crops/8b6b0de9/p000016-l0013.png` (print has the grave).
- Base letters cannot be checked against ink: `ὁποίοι → ὁποίου`,
  `round1/crops/0907df739607faca673d2169/p000011-l0016.png` — the print does read ὁποίου (a
  true correction), but the same rule could turn a mark error into another word, so base rules now
  abstain whenever Google's letters are attested under other marks (this candidate is lost).
- CTC spans sit left of the glyph; before snapping to the letter component, `τό`
  (`wikisource/crops/8b6b0de9/p000007-l0025.png`), `ᾄδου` (`…/p000008-l0002.png`) and `χῶμα`
  (`02a3a2a6/p000046-l0004.png`) had their marks outside the window and were wrongly "absent".
- Attached accents cut too high lost their slope: `τινές` (`8b6b0de9/p000009-l0029.png`), fixed by
  slicing at the mean line.
- Subscript touching the crop's bottom edge: `ἡσυχάσῃ` (`2793d64c/p000048-l0004.png`) — now
  `abstain:clipped_bottom`.
- Simplified-polytonic house styles (acute for grave everywhere, e.g. `νά μέλψουν … καί νά`,
  `round1/crops/2d29e5e76d90adc4cc1b093a/p000036-l0045.png`): the model's acute is right and the
  slope rule accepts it; a lexicon rule would have called it wrong — the reason final_grave uses
  ink only.
- Re-run predictions differ from the recorded E3 predictions on ~1 line in 40 (PIL vs Rust
  Lanczos): x positions are transferred to the recorded text by character alignment
  (`transfer_alignment`), never re-read.
- Regime: Google Wikisource mixes monotonic and polytonic texts; the first lexicon attested βήμα
  and βῆμα side by side. Regime purity per line (polytonic-only mark present / absent) fixed this;
  the price is that a polytonic line whose every mark Google dropped looks monotonic to the
  regime chooser unless the model's reading carries a polytonic mark.

## 8. Open questions for the owner

1. **Attestation policy.** `strict` leaves any Google form with count ≥ 5 (rule 5) and applies the
   20× / 50× margin only against corpus noise (1–4); `ratio` is the literal rule 1. On the
   three-way lines they differ by one (correct) correction per seed; the train sample was scored
   under `strict` only. Which is binding?
2. **Proper names.** Capitalised words are never corrected, line-initial ones included (we cannot
   tell a sentence start from a name at a line break). This excludes 35 three-way candidates, 17 of
   them model-right. Allow line-initial capitalised words?
3. **final_grave in simplified-polytonic prints** (acute everywhere): the ink says acute, Google
   says grave, the correction follows the ink. Is that the wanted label (the print) or should the
   label normalise to classical grave? The pipeline follows the print.
4. **base_sub without ink.** Keep the new "Google's letters attested under other marks → abstain"
   guard (loses true corrections like ὁποίου) or drop it?
5. **Where the recall is.** 193 recoverable Google mark errors on 1,264 human lines (15 %) and we
   recover 19. The largest reservoir is `model_form_unattested` + `both_attested`: a larger
   polytonic lexicon (Perseus is not on disk) or an inflection-aware lexicon would raise recall;
   the three-way set is too small to certify any rule at LB95 ≥ 99 % — only a human-checked batch
   of ≥ 300 corrections per rule can.
6. **The human transcriptions have errors** (φωλέα). Should "human ≠ both" cases be adjudicated by
   the owner before they count against a rule?

## 9. Orthographic-constraint stage (follow-up A, owner review 16 Oct ~15:40)

`greekocr/labelfix/constraints.py` (10 unit tests in `tests/labelfix/test_constraints.py`, positive
and negative cases per constraint) flags a word core as *impossible* under the hard constraints of
polytonic orthography: C1 one breathing, on the initial vowel / second vowel of an initial
diphthong, none elsewhere (initial ρ: a breathing must be rough; its absence is tolerated — a
deliberate relaxation, 19th-c. prints omit it); C2 ≤ 1 breathing and ≤ 1 accent per letter, no
breathing together with dialytika, dialytika and subscript may co-occur with an accent; C3 one
accent per word unless the next token is an enclitic; C4 accent on the last three syllables,
grave only final, perispomeni only on the last two and only on a long-capable vowel (never bare ε/ο);
C5 dialytika only on ι/υ; C6 subscript only under α/η/ω; C7 accent-before-breathing order is
normalised, not rejected. Rule `constraint` (`rules.py`): Google's form impossible AND the model's
form possible AND a single allowed mark difference → the lexicon is not required; the ink
conjunction for the mark category still is (same abstentions).

Census on the three-way lines (seed 0, polytonic-regime lines, 6,124 Google words), before the
exceptions: 75 "impossible" Google words, of which **47 equalled the human text** — medial ῤῥ
(Τυῤῥηνῶν), crasis / elision with a coronis after an initial consonant (νἄχω, ποὖναι), all-caps
words, hyphenated compounds checked as one word, line-final words whose enclitic is on the next
line, demotic synizesis (ἀταίριαστο) and poetic forms (θάλαμόνδε, ἐθέασατο) defeating the
antepenult count. These are real orthography, so they were encoded as exceptions and
`C4:accent_before_antepenult` was demoted to a soft flag (reported, never used for a correction).
After that: 35 impossible Google words (0.6 %); 14 still equal the human text (10 are
`C3:two_accents` — enclitics outside the list, e.g. Homeric/elided forms in the Argonautica; 4 the
soft antepenult flag); the model's form is possible for 17, of which 14 equal the human text (seed 1:
16 / 11). Rule `constraint` on the three-way lines: **9 candidates, 1 accepted, 1 = human, 0 false
(precision 100 %, LB95 5.0 %, n = 1)**; seed 1: 7 / 1 / 1. Overlap with the lexicon rules: 0 — the
one accepted correction would not have passed the lexicon (the model's form is unattested), so the
stage adds corrections the lexicon cannot make; the other 8 candidates failed the ink conjunction
(localisation, fused marks) exactly as the lexicon rules do. Per-violation table: see
`validation_wikisource.md` → "Orthographic constraints".

Training sample re-scored with the stage: 9 `constraint` corrections among 5,000 lines (the
accepted total rises from 67 to 75 = 1.50 % of lines; some former `breathing` / `marks_multi`
candidates are now classed `constraint`); the v2_test extras give 44 more. The deck got an
appended batch `constraint` (53 correction/label cards + 1 positive control, no negative control
exists yet: no constraint candidate on the three-way lines was contradicted by the human text) —
the seven earlier batches are byte-identical (`deck.py --append constraint` keeps the existing
`deck_data.js` and draws the new batch from its own random stream), so the owner's answers in
localStorage stay valid.

## 10. Owner decisions (follow-up B)

`greekocr/labelfix/ingest_decisions.py`: takes the deck's downloaded `labelfix_decisions*.json`
(newest in `~/Downloads`, or `--decisions`), copies it to `docs/records/labelfix/owner_decisions_<date>.json`
and writes `docs/records/labelfix/owner_review_summary.md`: per rule cards answered / y / n / u, u-rate,
precision with LB95 on correction-shown cards, label-shown y/n/u, negative-control false-yes rate,
positive-control agreement, and the five most common patterns (mark category + cluster change)
among `u` cards. Tested on a synthetic deck + decisions file (`tests/labelfix/test_ingest.py`, 3
tests, including an unknown card id and the "pending" exit). Status at the end of this run:
**pending** — no `labelfix_decisions*.json` in `~/Downloads` (a 25-minute watcher ran); run
`python -m greekocr.labelfix.ingest_decisions --deck docs/records/labelfix/review_deck --out docs/records/labelfix`
once the owner has downloaded it.

## 11. Compute and reproducibility

Model forward passes on this MacBook (CPU, `.venv`): 1,264 (seed 0) + 1,264 (seed 1) + 5,000
(train sample) + 2,400 (v2_test extras) = **9,928 crops** (≤ 10,000); every later re-scoring
(rule changes, constraint stage) reused the cached alignments, no further forward passes. Lexicon build: 202–240 s.
Alignments are cached in the session scratchpad (not committed); every runner recomputes missing
ones. Commands: `python -m greekocr.labelfix.build_lexicon …`, `… .validate --seed 0 --seed 1
--cache-dir <dir>`, `… .sample --records … --n 5000`, `… .textstage …`, `… .deck …` (see each
module's docstring). The bulk application to 207,851 rows belongs on Clariden: the package only
depends on the vendored training stack (`greekocr._vendor.train`, codec sha
`d1b7e2d4…`), `scipy`, `PIL`, `torch`; the checkpoint path is a parameter of `Recognizer`.

Note on the environment: midway through, the session's working directory was switched to another
agent's worktree (`greek-ocr-toolkit-sol-labelfix`, branch `sol/label-geometry`); it was not
touched. All work is on `fable/label-correction` in `~/Projects/greek-ocr-toolkit`.

## 12. Third pass (owner feedback 16 Oct 17:10): capture, bigger lexicon, policy defaults

**Owner's breathing batch** (55 cards, ingested by the coordinator as `owner_decisions_20261016.json`):
correction cards 20 y / 1 n / 2 u → precision 95.2 %, LB95 79.3 %; 1 false-yes on 18 negative
controls; u-rate 27 % (patterns ἷ→ἶ, ἡ→ἠ, ἑ→ἐ: breathing *kind* changes the owner could not settle
by eye). `pull_firefox` re-read the same 55 decisions from the Firefox profile
(`docs/records/labelfix/decisions/firefox_20261016.json`, identical to the ingested file).

**1. Auto-captured decisions.** `python -m greekocr.labelfix.deck_serve docs/records/labelfix/review_deck`
serves the deck on http://127.0.0.1:8765/ and appends every answer, as it is made, to
`docs/records/labelfix/decisions/<date>.jsonl` (`POST /decision`; `GET /decisions` re-syncs the page on
load). The page keeps localStorage as the fallback and shows "server capture on" / "opened from
disk" in its header. `python -m greekocr.labelfix.pull_firefox` reads the deck's localStorage from
the Firefox profile (`storage/default/file++++…review_deck+index.html/ls/data.sqlite`, snappy via
`cramjam`, installed into the venv with `uv`). `ingest_decisions` merges the captured jsonl (newest
record per card wins), Firefox pulls and downloaded files. Tests: `tests/labelfix/test_capture.py`
(live loopback server, raw + snappy sqlite, jsonl ingestion).

**2. Bigger polytonic lexicon.** Fetched with the existing scripts (network on): Perseus
canonical-greekLit @ `0189b9c8d8d1f148133f2f0af309b4ee90ea4332` (814 Greek TEI files, 377,099 body
lines) and First1KGreek @ `03776b39f4047c5cff06f5296fae4b2bae4b08fb` (1,231 files, 471,505 lines);
tarballs under `/tmp/labelfix-raw/` (never in the repo). TEI policy (`tei_extract.py`, recorded in
every record): body only; `<choice>` → `sic`/`orig`/`abbr` (editors' `corr`/`reg`/`expan` dropped);
`<app>` → `<lem>`; notes, refs, foreign, del, gap, supplied dropped. Held-out works: by id for the
ancient editions of the human set (Argonautica `tlg0001.tlg001`, Aesop `tlg0096`), by title stem,
by 4-gram shingle per line, and — new — a whole source document is held out when ≥ 20 lines AND
≥ 30 % of its lines share a 4-gram with an evaluation line (22 Wikisource articles = 3,045 lines,
1 Perseus and 4 First1K files; an absolute threshold alone was wrong — it removed whole Europarl
sessions on generic phrases — and was replaced). Lookup is inflection-aware (`lookup_variants`): a
form counts if it, its grave→acute variant, or — for two-accent words — the form without the
enclitic-induced second accent is attested.

| regime | forms before → after | forms ≥ 5 before → after | tokens before → after |
|---|---:|---:|---:|
| ancient | 867,945 → 1,048,153 | 207,201 → 353,002 | 24.5 M → 55.1 M |
| poly19 | 692,084 → 686,150 (22 held-out articles removed) | 161,846 → 160,364 | 14.5 M → 14.4 M |
| mono | 417,399 (unchanged) | 115,151 | 26.5 M |

Three-way validation re-run (ink conjunction unchanged), seed 0 `strict` / seed 1 `strict`:
candidates 214 / 197, accepted **23 / 22**, = human **22 / 21**, Google right **0 / 0**, human ≠ both
1 / 1 (the φωλεὰ transcription error), precision 95.7 % / 95.5 %, LB95 81.0 % / 80.2 %, net edits
+22 / +21; **recall of the 193 recoverable Google mark errors: 22 / 193 = 11.4 % (seed 0), 21 / 193 =
10.9 % (seed 1)** (9.8 % / 9.3 % two passes ago). Per rule (accepted / = human), seed 0: final_grave
15 / 14, accent 4 / 4, subscript 2 / 2, breathing 1 / 1, constraint 1 / 1, marks_multi, dialytika,
base_sub, final_sigma 0; seed 1: final_grave 16 / 15, accent 4 / 4, breathing 1 / 1, constraint 1 / 1.

Why the bigger ancient lexicon barely moves recall: no three-way line is scored in the ancient
regime — the document chooser classes all 17 books as poly19 (1,213 lines) or mono (51 lines),
Argonautica included, because the Wikisource lexicon attests at least as many of its words as the
ancient one (Homeric vocabulary is spread over many Wikisource texts). The candidates split 212
poly19 / 2 mono. The lexicon rejections that hide model-right corrections are all in poly19:
`both_attested` 21 model-right (+ 15 not), `model_form_unattested` 19 model-right (+ 55 not). The
19th-century polytonic regime has one source on disk (Wikisource): recall there needs more
proofread 19th-c. polytonic text, not more ancient text. The +3 recall came from the
inflection-aware lookup and policy 3a.

**3. Policy defaults** (coordinator decisions, pending owner confirmation): (a) line-initial
capitalised words are corrected when the lower-cased model form is attested ≥ 50 and is not in the
proper-name list (capitalised mid-sentence tokens of the same corpora, ≥ 3 occurrences;
`<regime>.names.tsv.gz`: ancient 58,288 / poly19 31,688 / mono 52,409 keys) — three-way lines:
4 admitted candidates, 1 accepted, 1 = human, 0 false (seed 0; seed 1: 3 / 1 / 1 / 0); training
sample: 4 admitted, 0 accepted; extras: 4 admitted, 1 accepted. (b) acute-everywhere pages
(`acute_house_style`: share of word-final acute > 0.8 over ≥ 10 accented final syllables of the
page's Google text): 0 Wikisource pages, 7 of 2,693 sampled train pages and 1 of 402 extras pages
flagged; final_grave corrections suppressed on them: 0 + 0 (none of the flagged pages carried a
grave proposal in these samples). On such pages the model's grave is treated as contradicting the
print and is not applied; the model's acute against a Google grave stays allowed. The floor of 10
accented words rarely triggers on a random sample (≈ 2 lines per page); the detector is meant for
the full-book run. (c) the base_sub "attested under other marks → abstain" guard is kept.

**4. Training sample re-scored** with the new lexicon and policies: accepted 76 of 5,000 lines
(final_grave 44, accent 13, constraint 9, base_sub 4, breathing 4, subscript 2); extras: 442. Deck refreshed by appending
second batches of never-carded accepted candidates (`deck.py --append …`): `accent#2` 2, `final_grave#2` 100, `base_sub#2` 1
(the other rules have no new accepted candidates); the eight existing batches are byte-identical to
the committed deck, so the owner's answers stay valid.

## 13. Pass 4: ink-decisive variant for lexicon-neutral cases, and the recall ceiling

**Mark-shape classifier** (`markshape.py`, `markshape_train.py`; artefacts `markshape_model.json`,
`markshape_samples.jsonl.gz`, `markshape_report.md`). Samples: the vowels of words where Google =
human = model on the three-way lines, well-localised only: 13,312 (4,481 dev-book, 8,831
held-out-book); 12 mark classes with ≥ 15 samples (`acute`, `grave`, `circumflex`, `psili`,
`dasia`, `psili+acute`, `dasia+acute`, `psili+grave`, `psili+circumflex`, `subscript`,
`circumflex+subscript`, `none`). Features (159): blob counts, sizes, principal-axis slope,
elongation, hook direction (mean x of the middle rows minus the top/bottom rows: `)` vs `(`
tells smooth from rough), x-skew, top-heaviness, position relative to the body and mean line,
and an 8×8 occupancy thumbnail of each of the first two blobs. Models: softmax regression
(held-out accuracy 94.3 %) and a one-hidden-layer MLP (96 tanh units, Adam, class-balanced;
**held-out accuracy 94.9 %**, chosen). Calibration on the held-out books: **tau = 0.998 gives
99.05 % precision on 2,636 predictions (29.8 % coverage)**; the curve (0.9 → 96.5 %, 0.99 →
98.4 %, 0.999 → 99.2 %) and per-class recall / precision-at-tau are in `markshape_report.md`.
Mark-vs-mark only (both truth and prediction carry a mark) precision is 99.4 % already at 0.99:
the confident errors are mark ↔ `none`, i.e. the extractor lost the blob, which the removal
abstentions guard separately. Weakest classes: `psili+acute` (recall 34 % in the linear model,
often read as `dasia+acute`), `grave` vs `circumflex`.

**Rule variant `ink_decisive`** (`rules.lexicon_neutral`, `rules.ink_decisive_verdict`): for a
mark candidate where the lexicon is neutral (both forms attested ≥ 5, or both unattested) and
the ordinary rule rejected it, the variant is true when the ordinary ink conjunction and all
abstentions hold AND the classifier predicts the model's mark class with p ≥ tau AND that class
is not Google's. A breathing-kind change on a fused (sliced) mark is never decisive: the hook is
truncated at the mean line — the first run had exactly one false correction, `ὁ → ὀ` on
`wikisource/crops/8b6b0de9/p000013-l0027.png` (classifier p = 0.9999 for `psili` on a sliced
blob), which this rule removes. The column is separate everywhere (`decision.lexicon_neutral`,
`decision.ink_decisive`, `decision.ink_decisive_reason`); `accept` is unchanged.

Three-way lines, seed 0 / seed 1 (`strict`): lexicon-neutral mark candidates 112 / 117;
**ink-decisive 4 / 4, = human 4 / 4, Google right 0 / 0**, LB95 47.3 % / 47.3 %, net edits +4 / +4
(breathing 2 / 2, accent 2 / 2, none for subscript, marks_multi, final_grave, constraint). Before
the fused-breathing rule it was 5 / 5 with 1 / 1 false. Why the other neutral candidates are not
decisive (seed 0): 50 were already accepted (final_grave is ink-only), excluded or abstained;
merged marks 11, no shape model (not well-localised) 8, blob count 7, clipped bottom 6,
neighbouring marks 6, p below tau 5, wide blob on removal 4, oblique where the model has a
circumflex 4, classifier reads Google's mark 3.

**Recall**: rules 22 / 193 = 11.4 % (seed 0) and 21 / 193 = 10.9 % (seed 1); **rules +
ink_decisive 26 / 193 = 13.5 % and 25 / 193 = 13.0 %**.

**Ceiling analysis of the 193 recoverable Google mark errors** (seed 0 / seed 1):

| class | seed 0 | seed 1 |
|---|---:|---:|
| model wrong — unreachable by any single-crop two-reader method without a better model | 84 (43.5 %) | 100 (51.8 %) |
| model right, accepted by the rules | 22 (11.4 %) | 21 (10.9 %) |
| model right, lexicon neutral, ink decisive | 4 (2.1 %) | 4 (2.1 %) |
| model right, lexicon neutral, ink not decisive | 33 (17.1 %) | 21 (10.9 %) |
| model right, lexicon contradicts (Google's form attested, model's not) | 10 (5.2 %) | 7 (3.6 %) |
| model right, ink conjunction fails (count / shape) | 17 (8.8 %) | 14 (7.3 %) |
| model right, excluded by a guard (proper name, hyphen, caps) | 15 (7.8 %) | 15 (7.8 %) |
| model right, abstained (ink unreadable / regime) | 8 (4.1 %) | 11 (5.7 %) |

Reading: about half of the remaining errors need a better recogniser; of the rest, the largest
reachable block is "lexicon neutral, ink not decisive" (33 / 21) — the classifier's coverage at
tau (30 %) is the lever, i.e. more unambiguous training samples (the full-book run yields
hundreds of thousands) and a less destructive attached-mark slice; the guards and the
contradicting lexicon are owner policy.

**Deck**: batch `ink_decisive` appended (42 correction/label cards from the sample + extras,
blinded as before, plus 20 negative controls — lexicon-neutral candidates the human text
contradicts — and 4 positive controls); the eleven existing batches are byte-identical. Training
sample: 9 ink-decisive candidates (accent 7, breathing 2) besides the 76 accepted; extras 34.

LABELFIX: done | rules: 9 | wikisource_precision: breathing:100% accent:100% subscript:100% final_grave:93% constraint:100%/1 marks_multi:- dialytika:- base_sub:- final_sigma:- | wikisource_precision_lb95: breathing:5.0% accent:47.3% subscript:22.4% final_grave:72.1% constraint:5.0% marks_multi:0% dialytika:0% base_sub:0% final_sigma:0% all:81.0% | recall_of_recoverable: 11.4% | ink_decisive: 4/4/0 recall_total: 13.5% | train_sample_candidates: 76 (1.52% of lines) | deck: docs/records/labelfix/review_deck/index.html | tests: 79 passed | owner_review: present (breathing batch, 55 cards)
