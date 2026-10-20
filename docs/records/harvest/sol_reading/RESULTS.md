# Sol as a blind pixel reader: results (17 Oct 2026, written 13:25 Athens)

gpt-6.1-sol, Codex CLI 0.159.2, effort medium, one `codex exec` context per bed, `view_image` tool. 9 reading runs (r1, r2 and a
tie-break r3 per bed), 455 card-reads. The tables are in `results/SUMMARY.md` (every denominator stated), `results/TABLES.md` and
`results/ERRORS.md` (private). The design is in `PLAN.md`, and the prompt adaptations in `GUIDE_NOTES.md`.

## Integrity
- **Leak scans:** all 9 rollouts are clean under scanner v3. Every image the model saw is byte-identical to a file in its own reader
  folder, or is `view_image`'s downscale of one.
  - Scanners v1 and v2 voided the runs on false positives: computed JavaScript paths, `x.keys()`, the reader's own absolute folder,
    and template splitting. The lead reviewed each by hand before the fix.
  - The Codex sandbox does not restrict reads; a canary file outside the workspace was readable. So blinding rests on isolation
    plus the scan.
- **Controls:** 42/42 planted controls passed (bsb 10+10+1, yer 5+5+1, owner39 4+4+2). No reader was flagged.
- **Limits:** probe-before/probe-after around every run. Model asserted from every rollout.

## Accuracy

| Bed (truth) | Sol r1 | Sol r2 | Sol S2 (2-of-3) | Opus E0a | Opus E0b | Opus E1 |
|---|---|---|---|---|---|---|
| bsb, 100 cards (C1 Opus reference), joint | 93 | 94 | 93 | 95 | 96 | 97 |
| bsb letters / marks / crop_ok | 99 / 96 / 98 | 99 / 97 / 98 | 99 / 96 / 98 | 100 / 96 / 98 | 98 / 99 / 99 | 100 / 98 / 99 |
| yer, 65 slots (ink truth) | 64 | 63 | 64 | 64 | 63 | 64 |
| owner39, 39 anchors (owner truth), joint | 33 | 28 | 33 (3 unresolved) | partial | partial | — |
| owner39, the 33 card-reads Opus answered | 30 | 22 | 30 | pooled 24/33 | | |

- **bsb.** The reference is itself an Opus reading under the same protocol, so the comparison leans toward Opus.
  - **Sol misses printed-grave/label-acute errors: 0 of 3** (στενὴ, ἀκριβὲς, ἰσχυρὸν, in r1, r2 and S2). All three Opus arms caught
    them, although the protocol names "grave vs acute".
  - Sol caught the other 5 reference mark errors, including the reverse case δέ → δὲ.
  - The other differences: one disputed letter card (ἴριδα/ἔριδα, where Opus split 2–1), one extra mark flag (ᾖ/ᾗ), and two
    crop_ok calls.
- **yer.** Sol equals Opus exactly: r1 = E0a = E1 = 64/65, and r2 = E0b = 63/65. The 6 controls included a mixed ъ/ь line on which
  Google was wrong, and both readers got it right.
- **owner39.** On these cards the neural reader R1-A scores 0/39 by construction.
  - Sol S2 has **1 committed wrong anchor** (Πλουτος read without its circumflex). The other 5 misses are abstentions: 3
    unresolved tie-breaks and 2 unknown heads.
  - r2 abstains much more than r1 (11 breathing-unknown against 2). That explains most of the r1–r2 gap.

## One reader vs two (S1 → S2)

| Bed | Sol r1 vs r2 agreement | Opus E0a vs E0b agreement | S2 against r1 as S1 | S2 against r2 as S1 | S2 cost / S1 (total tokens) |
|---|---|---|---|---|---|
| bsb | 95/100 cards | 93/100 | 4 cards change: 2 to correct, 2 to wrong; net 0 | 1 changes, to wrong; net −1 | 2.4× / 1.9× |
| yer | 64/65 slots | 64/65 | 0 changes | +1 slot | 1.7× / 2.9× |
| owner39 | 27/39 anchors | 5/8 (partial overlap) | 4 change, 0 net (3 unresolved) | 9 change: +6, −1; net +5 | 2.8× / 2.1× |

- **Run-to-run variance.** Sol's single-reader spread is the same size as Opus's or smaller: bsb 95 against 93 agreement, yer the
  same.
- **On line checks (bsb, yer), a second Sol reader changes almost nothing,** for about 2× the tokens.
- **On hard word cards (owner39), two readers plus a tie-break remove the luck of the draw.** r1 scored 33 and r2 scored 28; S2 gives
  33 with only 1 committed error. The rest of the misses are flagged unresolved for a human or Opus.

## Cost

| Per item | bsb | yer | owner39 |
|---|---|---|---|
| Sol S1 wall time | 1.6–1.9 s | 1.7–2.2 s | 3.2–3.4 s |
| Opus E1 wall time | 5.3 s | 7.5 s | — (E0 partial 22–57 s) |
| Sol S1 tokens: total / uncached input / output | 9.9–12.3k / 0.7–0.8k / 69–76 | 7.9–13.2k / 0.8–1.2k / 58–67 | 10.8–14.3k / 1.1k / 150–175 |
| Opus E1 Claude tokens (agent total) | 1.33k | 2.23k | — |

- **Codex weekly limit.**
  - 32.0% used at 12:26, before any run.
  - 32.0% before the pilot (12:46).
  - 33.0% after the last tie-break (13:19).
  - 33.0% at the final probe (13:26).

  So all 9 reading runs (5.33M tokens, of which 4.83M cached) plus 5 Sol build briefs (about 7.1M tokens) moved the account's
  meter by at most 1 point, and that meter is shared with other sessions running Sol at the same time. That is ≤ 0.22 weekly
  points per 100 card-reads, as an upper bound. The meter's 1-point resolution means no per-run delta is measurable (every run
  read 0.0).
- **Credits balance:** 59,974.71 throughout; no spend.
- **The two meters are not converted.** Sol's tokens per card are about 8× Opus's because every tool turn re-sends the cached
  context, but about 91% of Sol's tokens are cached input.

## What the prompting guide changed (see GUIDE_NOTES.md)
- A non-interactive, finish-in-this-turn header: no run stopped to ask.
- Batched image views: 12–21 tool calls per 43–110 cards, against Opus's 1.5–2.8 per card. Wall time per item is about 3× lower.
- Explicit "Done when" checks: every run verified its count and order, and all 455 answers mapped with no schema error.
- One contradictory instruction removed.

There is no ablation, so the guide's effect is not measured separately.

## Recommendation
1. **Sol can take over yer-type glyph adjudication now:** one reader, with Opus-equal accuracy on the same 65 slots.
2. **Sol can take over line checks for letters and crop on bsb-type cards with one reader.** It must NOT be the only mark checker
   where printed grave vs label acute matters. It missed 3/3 such cases, and nlg poly1900 and lekythos carry a grave_to_acute bias
   of 9–12 per 100.
   - Before any hand-over of mark checks, test a targeted fix: a per-word grave/acute pass on word crops, scored on the C1
     mark-error cards.
3. **Sol S2 (two readers plus a tie-break) is usable for word-mark cards:** owner39 gave 1 committed error in 39, with 5
   abstentions routed onward. Unresolved and unknown cards still go to Opus or the owner.
4. **Cost is not the constraint.** The whole experiment moved the shared weekly meter by ≤ 1 point.

## Limits of this evidence
- **Small n:** 100, 65 and 39 units; differences of 1–3 units are within the run-to-run spread of either model.
- **Shared-model reference.** The bsb reference and 16 owner39 truth forms come from Opus readers.
- **Owner39 Opus reference** is partial (33 card-reads over 4 readers).
- **No pixel adjudication** was done of the 7 bsb cards where Sol and the reference disagree; they are listed in
  `results/ERRORS.md`.

## Follow-up: targeted grave/acute pass (2026-10-17 13:39 Athens)

**Bed:** 58 items, one Sol reader in one context.
- Positives: all 26 printed-grave/label-acute C1 errors in nlg poly1900 (9), lekythos (11) and kosmopolis (6).
- Negatives: 26 final-syllable acute words from marks=y lines, matched per stratum.
- Controls: 6 (3 circumflex, 3 none).
- The lead checked all 58 by eye (`grave/keys/control_review/LEAD_REVIEW.md`).

**Images and question:** word crop 3× plus anchor-letter zoom 8×. The Google label is never shown. The question is "which accent is printed on this letter": acute / grave / circumflex / none / unreadable. Prompt in `prompts/grave.md`.

| | Result |
|---|---|
| Grave recall on positives | **25/26**; the 1 miss was answered "unreadable" (low confidence), on the faint φιλολογικὲς |
| False "grave" on acute negatives | **0/26** (acute correct 26/26) |
| Controls | 6/6 |
| Words not touching punctuation or a hyphen | grave 23/24, acute 7/7 (so it is not a position heuristic) |
| Cost | 58 items in 67 s; 427k tokens (353k cached; about 1.2k uncached input and 46 output per item); weekly meter 33% → 33% |

**Reading.** The 0/3 grave misses in the bsb line check were a failure of the whole-line comparison task, not of Sol's vision. Asked directly about one letter, Sol separates grave from acute reliably.

**Recommendation.** Sol can take the grave/acute mark check at the stratum level as a separate word-level pass:
- For every label word whose last syllable carries an acute or a grave, ask this single-letter question.
- Flag a disagreement with the label.
- Send "unreadable" to Opus or the owner.

At these numbers, a stratum's grave_to_acute lines (9–12 per 100) would be caught at about 25/26, with no false flags seen in 26 acute words. Geometry built for all 58 items with 0 replacements on these strata.

**Limits.**
- Small n: 26 positives and 26 negatives.
- The positives' truth is the C1 single-reader finding, plus the lead's pixel check.
- The negatives were not chosen as hard cases: many touch punctuation, but the split above shows they are not needed.
- Not yet tested: a full-stratum run on every oxytone word, where the base rate of graves is much higher.

## Scale limit of the grave/acute pass (recorded 2026-10-17 13:41 Athens, coordinator ruling)

Per item, the targeted pass costs about 7.4k tokens: about 1.2k uncached input, 6.1k cached, and 46 output, in 1.2 s.
- **Release scale.** A correction pass over the release (100k+ oxytone words) would be about 740M tokens, 120M of them uncached. That is roughly 40× all the Sol work run today.
- **What the meter shows.** All of today's work stayed within one point of the weekly meter (32 → 33%). Below that 1-point resolution, the cost per point is not measured, so no lower bound can be projected.
- **Ruling.** The coordinator rules release-scale correction out of the Codex budget. This pass is for stratum checks, audits and the marks_bias strata (nlg poly1900, lekythos), not for correcting the release.
- **Not measured.** The cheaper attachment form (codex exec -i, no tool turns) or montage views could lower the per-item cost, but neither is measured.

## Full-stratum grave/acute pass, nlg poly1900 (2026-10-17 14:10 Athens)

**Setup.**
- **Items:** every word on the 100 C1 cards whose last syllable carries an acute or a grave in the label. That gives 316 items, after 10 were dropped for lack of exact geometry.
- **Pass 1:** one Sol reader, 4 contexts (90+10, 90+10, 90+10, 46+6), with controls from lekythos and kosmopolis.
- **Re-read:** every flagged item, in a fresh context (13 items + 2 controls).
- **Lead check:** the lead's eye on every flag (`grave_full/LEAD_EYE.json`, sheet `grave_full/keys/review/flags_1.png`).
- **Leak scans:** all clean.
  - Scanner v4 accepts a viewed zoom montage that the reader later overwrote, but only if replaying the logged literal commands on a fresh copy reproduces it pixel for pixel (p1c1, record 42).
  - The montage differed only in PNG timestamp bytes.

| Measure | Result |
|---|---|
| Items / flagged | 316 / 13 (by Sol's answer: 9 grave, 1 acute, 1 circumflex, 2 unreadable) |
| Pass 1 vs re-read | 13/13 agree; controls 36/36 in pass 1 and 2/2 in the re-read |
| Lead's eye on the 13 flags | **11 confirmed label errors**, 1 false flag, 1 unreadable to the lead as well |
| Confirmed label errors | 9 printed-grave/label-acute (φωνὲς, θερμὸ, Μαριὼ, Γιαννακὸς, ὑποταχτικὸ, στανιὸ, ἀλλὰ, σχεδὸν, καθὼς); κορμιοῦ (printed circumflex, label acute); Τά (printed acute, label grave) |
| False flag | χωρὶς: the lead reads the printed grave the label has; Sol said "unreadable" |
| Unreadable to both | τὴ |
| Against C1 | All 9 C1 grave_to_acute errors and κορμιοῦ re-found; **Τά is new** (C1 missed it); 17/17 agreement with SR-G1 on the overlap items |
| Stratum grave base rate | 274/316 = 86.7% of final-accented words print a grave (lead's eye on flags, label elsewhere) |
| Label grave_to_acute rate | 9/316 words (2.8%), 9/100 cards (C1: 9/100) |
| Cost | 5 contexts, 2.82M tokens (326k uncached input, about 1.0k per item); Codex weekly meter 33% → 34% across the pass (meter shared with other sessions); credits unchanged |

**Reading.** On this stratum, one Sol reader plus a fresh-context re-read of the flags gives:
- the C1 Opus line check's accent findings, plus one more;
- 1 false flag in 316;
- 1 item left undecided, which goes to a human.

The 303 unflagged items are counted as matching the label. That is assumed, not independently verified, so the recall of errors among them is not measured.
