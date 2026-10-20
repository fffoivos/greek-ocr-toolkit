# LQB3: scoreboard v2 — baseline for every class, sf6 + N1 proposals registered (gpt-6.1-sol, medium, network OFF; no .git writes)

Worktree `~/Projects/greek-ocr-toolkit-secondary`. Inputs: `docs/records/labelfix/lqb/` (truth_v1, flags sidecar, versions.json, scorer,
SCORE_v1.md).

**Owner reaction to v1:** "you must be joking? is this a benchmark for our experiment? this is all cyrillic".

**Rebuild** `docs/records/labelfix/lqb/scoreboard.html` at the same path. The lead republishes it to the same URL.

1. **BASELINE table first, at the very top, for EVERY class.** Rows, in this order:
   - polytonic marks, by direction (missing / extra / wrong mark, per head: breathing, accent incl. grave↔acute, diaeresis, subscript);
   - capitals; numeric separators; punctuation and dashes; superscripts and rare glyphs; mixed-script lookalikes;
   - Latin; modern monotonic Greek; Cyrillic.

   Each row shows **Google's error rate against truth on the uniform and locked sets only**: errors/n, rate, 95% Wilson CI, sample
   type, tier, and the source set. Where no uniform or locked truth exists, write "not measured" and name what truth would be needed.

   Use every uniform or locked source in truth_v1 and in INPUTS.md:
   - the locked strata;
   - the C1 uniform cards: per-stratum letter / mark / crop verdicts by class. They are tier A (two Opus readers), sample_type
     uniform within their stratum. Map C1 strata to these rows by script class: poly1850/poly1900 → marks + letters; modern_scanned
     → modern monotonic; latin → Latin; cyrillic → Cyrillic; numerics_tables → separators;
   - and so on.

   Show the stratum next to each rate. Never pool strata into one population rate.
2. **Register two more versions** in versions.json and score them:
   - `sf6_release`, from the spell-check lead's SX1 extract (`~/Projects/greek-ocr-toolkit-spellcheck/artifacts/sx1/`, read only;
     verify its receipt and sha). If SX1 has not landed, mark it pending and continue.
   - `n1_proposal_v1` (UNADOPTED): the "Ours" lines from `artifacts/n1/owner_sheet/` (cards.json / decisions), keeping Google's
     character for unsure slots. Score it on the N1 truth; the N1 approved controls are in-sample for it.
3. **Headline** = the marks delta (google_raw → sf6_release), measured on the out-of-sample sets sf6 covers, with the sample type
   stated. If sf6 is pending, the headline says so in one line, and the baseline table stays the lead element.

   The Cyrillic rows stay, below, and are no longer the headline. The "Bottom line" paragraph the lead added in v1 is replaced by
   one generated from the v2 numbers. Keep it to ≤4 plain sentences.
4. Keep the page under 14 MB. Update SCORE_v1.md → SCORE_v2.md, the receipt section and the tests.

**Last line:** `LQB3 READY: baseline rows <n> (measured <n>, not measured <n>); versions <n> (sf6 <scored|pending>, n1_proposal_v1 scored); headline <one line>; scoreboard <MB> MB; tests <n> passed`
