# N1: numeric separators, plan (17 Oct 2026, spell-check track lead)

**Owner, 17 Oct:** "the dots replaced by hyphens for numbers are the most serious; create a model for punctuation in numbers the same way
we did for accents."

**Owner rulings that apply:**
- Dashes are tagged only; there is no track for them.
- Opus reading stays paused, but Sol one-reader is qualified for glyph questions.
- Sol builds; the lead plans and reviews.

## The fault

Measured on the C1 numerics cards (ELSTAT, 100 cards):
- separator faults were 3 of 100 cards, while digits were right on 98 of 100;
- examples: `4·547·331` (mid-height dots) → `4-547-331`; `555,6` → `555.6`.

**Today's handling:**
- rows Google tagged `separator_ambiguous` are held;
- the text-only rule was rejected, because Google's hyphens also stand for real ranges (`0-499`).

**Why it matters:** the label teaches the recogniser to write hyphens and dots that change a number's meaning, and the digits around them
are clean. The recogniser codec already has `·` (U+00B7), `.`, `,`, `-`, en dash and em dash, so no codec change is needed. The decision
of which atom to use for a raised dot (U+00B7 vs U+0387) is settled in step 0.

## Design (R1 pattern: grammar proposes, ink decides)

| Part | Choice |
|---|---|
| **Token** | A maximal run of digits joined by separator candidates (`·` `.` `,` `-` `–` space, or a gap), from Google text aligned to the recogniser's located letters. |
| **Slot** | Each gap between two digits inside the token, plus the two token boundaries (a leading sign, and a trailing separator before space or punctuation). |
| **Head** | One printed glyph class per slot: raised dot · baseline dot · comma · hyphen/dash · space · none. Plus `unknown`; never a fabricated `none`. |
| **Candidates** | A number-format grammar per source and era: thousands grouping in 3s with a raised or baseline dot; a decimal comma before 1–2 trailing digits; year ranges and page ranges with a hyphen; table cell boundaries. The grammar only proposes candidates and never decides. |
| **Ink decides** | Per slot: the vertical position of the ink blob relative to the digit x-height band (raised vs baseline), its width and height (dot vs hyphen vs comma tail), and gap width (space vs none). This is a detector on the S6 pattern, built from the existing `ink.py` primitives on a digit-band profile. |
| **Correction rule** | One-directional: Google never invents a raised dot. Replace Google's `-` or `.` with `·` only when the ink says raised dot AND the grammar admits a thousands position. Otherwise keep Google's text; on conflict, HOLD. Never touch ranges where ink shows a hyphen-length stroke. |

## Labels and model

1. **Step 0, Sol bed (no model).** Census of numeric tokens and separator slots on ELSTAT plus Gazette numerics:
   - counts per source and era;
   - Google glyph distribution per grammar position;
   - the U+00B7 vs U+0387 convention check against the codec and the existing labels.
2. **Step 1, the Sol glyph pass.** Sol one-reader reads each sampled slot on a 3× zoom: "which mark is printed between these digits?"
   - Six options plus unknown, with controls planted at 10% from slots I pixel-verify.
   - Sample about 600 slots stratified by source, grammar position and Google glyph. Oversample Google `-` inside 4+ digit tokens, the
     hyphen ↔ raised dot confusion.
   - Gate: at most 1 control error per 60 cards. Otherwise the batch is void.
3. **Step 2, the ink-rule detector.**
   - Thresholds are fit on half of the glyph-pass slots and evaluated on the other half.
   - If raised-vs-hyphen precision is ≥ 99% at useful recall, the rule alone ships. No neural model is needed.
4. **Step 3, an R1-style separator reader,** only if step 2 falls short and volume justifies it. That means at least 5,000 confusable
   slots per release.
   - A small CNN on the slot crop, trained on glyph-pass labels plus grammar-consistent agreement slots (Google, ink and grammar all
     agree).
   - Same seed and regression discipline as R1/R2.

## Evaluation

- **A locked numerics stratum,** drawn before any tuning: ELSTAT + Gazette numeric lines from documents never used for fitting, about 300
  slots. Truth comes from the Sol glyph pass plus my pixel check of every disagreement.
- **Metrics:**
  - per-class precision and recall, with the hyphen → raised dot correction as the primary;
  - false edits on true hyphens or ranges, which must be zero on the stratum;
  - HOLD rate.
- **Regression:** the release gate digest and the mark checks are unchanged (N1 adds a separate numeric composer), and the existing
  numerics cards are re-scored.

## Steps and gates

| Step | Owner of work | Gate to proceed |
|---|---|---|
| 0 census + convention | Sol | counts + convention ruling by the lead |
| 1 glyph pass (about 600 slots) | Sol reader, lead controls | control gate; disagreement pixel check |
| 2 ink rule | Sol | ≥ 99% precision on raised-vs-hyphen on the held-out half; 0 false edits on ranges |
| 3 reader (conditional) | Sol + cluster | only if step 2 fails and the volume test passes |
| release composer | Sol | locked stratum + regression, lead review, then owner |

**Cost:** steps 0–2 are Sol and Mac CPU on small crops, about 600 glyph-pass items at about 1.2k tokens each on the Codex meter. There
is no Opus reading and no cluster work unless step 3 triggers.

## Coordinator conditions (17 Oct, plan PASS)

1. The locked evaluation stratum (≈ 300 slots) comes from documents disjoint from the 600-slot glyph-pass frame. Its line ids go into
   `release_exclusions` BEFORE step 1 runs.
2. The raised-dot vs hyphen ink rule is built from the toolkit's existing helpers (`glyphs.components`, the x-height and baseline
   estimates), not a new heuristic. Every slot keeps a decision record (component height, vertical position relative to the x-height
   band, width), so the owner can audit it on a sheet.
3. Steps 0–2 proceed. Step 3 (the reader) needs the coordinator's go after the step-2 numbers.
