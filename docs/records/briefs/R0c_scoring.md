# R0c — Score the recogniser audit with the adjudicated print truth (gpt-6.1-sol, xhigh)

Workspace: `~/Projects/greek-ocr-toolkit-spellcheck-r0` (branch `opus/spellcheck-r0`, head at launch). No `.git` writes. Network OFF. Python:
`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`. Mac CPU, cached alignments only (the 666
cache, `.cache/labelfix/r0/align_locked_ia.jsonl`, the M2 cache for stratum ii). Measurement only; never tune anything on the locked strata.

## Inputs
`docs/records/briefs/R0_recogniser_audit.md` (the measurement plan + coordinator additions) and `R0_REPORT.md` (R0a/R0a2). Truth from R0b, now filled:
`docs/records/labelfix/spellcheck/R0_expected_truth.json` (main deck: 932 AGREED, 14 MAJORITY_OF_3, 2 UNRESOLVED, 83 CONTROL — every reader scored
83/83 on controls) and `R0_expected_truth_ia.json` ((i-a): 24 AGREED, 3 CONTROL); the private keys and raw reader answers are under
`R0_adjudication_private/` (you may read them now: R0b is closed). Transcriptions in truth are diacritic-stripped letter forms / punctuation
forms exactly as the cards asked.

## Do (as the R0 brief's "Measure" and "Classify" sections, with these labels)
1. **State the letter truth first:** which lines/slots have truth (card-level truth + where full lines are certified), per stratum.
2. Letter error (case kept / case folded), by error type, by book/source; case disagreements: who is right (adjudicated 160 cards) and the
   extrapolation to the 753; apostrophe/quote/elision: emitted vs printed rates for recogniser, Google, human; span placement from R0a.
3. **Every failure type DATA or MODEL** with counts, ≥ 3 example line ids, evidence (label frequencies in `import_real_v2_train.jsonl`).
4. **Stratum labels on every table:** the 666 = continuity instrument; stratum (ii) = "mark-enriched, not a population estimate";
   stratum (i-a) = "selection-exposed (v2 val)", reported beside, never pooled. UNRESOLVED cards are UNKNOWN, never guessed.
5. Review page HTML in the owner template style (line id, crop with the recogniser's letter spans boxed, Google line, recogniser line, one
   note field placeholder) for ≤ 60 lines covering each failure type; write it, the track lead publishes.

## Deliverables
`R0_REPORT.md` final sections, `R0_failures.jsonl`, `R0_metrics.json`, the page, last line:
`R0 RESULT: letter truth <n> slots/<m> lines; letter error <x>% (case-folded <y>%) on 666, (ii) <…>, (i-a) <…>; spans outside blob 3.92%; case disagreements recogniser right <a>%; apostrophes emitted <b>% of printed; DATA types …; MODEL types …`.
