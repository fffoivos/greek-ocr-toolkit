# ASTRA-R2design — design review: the second mark-reader training round (R2)

Role: design reviewer (gpt-6.1-sol, xhigh). You design and critique; you do not run training. Read-only repository; evidence paths below. Answer the owner's questions with numbered recommendations, each tied to the evidence you cite (file:line), and with the measurement that would confirm or refute it. Where you cannot decide from the evidence, say what experiment arm settles it. No praise, no summary of the project.

## Context (facts, do not re-derive)

- R1 is a per-slot mark reader (four heads: accent, breathing, dialytika, subscript; names, not just presence) over a window around each recogniser vowel/ρ slot. Arm A (natural sampling, 64-d letter embedding) is the approved naming head. 1.77 M parameters, 15 epochs over ≈2.06 M slot samples, 35 min on one GH200.
- Training labels: C1 selection (91,469 lines, 316 documents; 300 train / 16 validation documents) and only slots where Google's NFD core equals the recogniser's. A shared omission becomes a "no mark" label (Astra SC1 M01).
- Held-out evaluation: 666 lines from 14 Wikisource books (two books supply 76%); truth = three-way agreement (Google = human text = recogniser) plus 189 Google-vs-human words adjudicated blind by two Opus readers with a 2-of-3 tie-break (147 human right, 34 Google right, 6 unresolved).
- Arm A on held-out: slot precision 99.14%, recall 94.20%; per class accent 99.8/99.8, breathing 98.7/99.1, subscript 98.9/94.7, dialytika 100/100. It fixed 66 of 80 Google mark errors and introduced 24 new errors. The owner adjudicated all 39 wrong-slot cards (14 unfixed, 13 false marks, 2 missed, 10 misnamed) and found one scoring error. 12 of the 13 false marks are a breathing or accent placed on a capital in an all-caps word or a lone capital.
- S8 DEV truth: 600 adjudicated lines from the training waves; R1-A mark presence ≈99/99 there, including parliament.
- Owner rulings in force: labels are the ink ("transcribe what is printed"); the reader may act ALONE on additions and substitutions (owner, 17 Oct); the recogniser only locates letters and has no vote on deleting anything Google has; blind two-reader Opus adjudication is the trusted truth method, reader count stays as is; nothing enters training unchecked; synthetic lines only from the line factory with verified font coverage.
- Available data now: collection v2 ≈272k cleaned lines (Google labels); W1 new-source rows 25,920 usable (Google labels, C1-card-checked per stratum with per-stratum pass/fail and a recorded Google mark bias toward monotonic on 20th-century polytonic: 13–16 mark-error cards per 100); locked test strata (ii) 200 mark-enriched new-source lines, (i-a) 133 selection-exposed lines, (i-b) 400 lines from 5 fresh Wikisource books, all pixel-adjudicated and excluded from every release; S8 DEV 600 lines; the C1 cards' adjudicated mark errors (line ids in c1_results.json); the owner's 39 adjudicated cards; the line factory (synthetic lines with known marks per font, atoms of codec v2).
- Google's systematic label errors measured on new sources (C1 cards): grave written acute or dropped, breathings dropped on capitals, subscripts dropped (and sometimes inserted), circumflex written acute, elision marks normalised; superscripts and em dashes lost.

## The owner's two runs (verbatim remarks appended in §Owner)

1. **R2a — same data, same recipe, small fixes.** Targeted repairs of the observed hallucinations (marks on capital A / Ἀ, on small o, all-caps words) and the other categories the owner listed, without changing the recipe otherwise. Purpose: a clean paired comparison with R1-A.
2. **R2b — reader as bootstrap.** Build a larger label set where the label is agreement between the new reader (R1-A or R2a) and Google, optionally also the recogniser; train a new model on it. Purpose: escape Google's shared omissions and scale the slot count.

## Questions for you (answer each; recommend one path per question, alternatives become experiment arms)

1. **Data mixes.** For R2a and R2b: which sources, what proportions, how many slots; whether and how to add (a) the adjudicated truth sets as supervised slots, (b) line-factory synthetic marks for Google's weak classes (capitals with breathings, subscripts, grave at word end, dialytika), (c) hard negatives (capitals, all-caps words, specks, neighbour ink, show-through, cut crops) and at what fraction. Say which sets must stay out of training (locked strata, DEV usage).
2. **Bootstrap label policy for R2b.** Agreement of which voters, at slot level: reader×Google, reader×Google×recogniser, or reader-with-confidence-override. How to avoid training the new model on the old reader's own habits (confirmation loop), what the stop rule is, and how to measure label noise per class before training (blind Opus adjudication of a stratified sample: size, strata, reader count unchanged).
3. **Old + new data.** Mix the R1 training slots with the new sets, or replace; weighting; whether the 316 C1 documents stay.
4. **Recipe and model.** Keep 15 epochs / AdamW / lr 1e-3 / natural sampling? Changes worth an arm: class-balanced or hard-negative quotas (arm E lost to A on held-out: why), window size and baseline-aligned window adapter (Astra SC1 M10), letter embedding, capital-awareness input (case feature or crop-height feature), per-class calibration thresholds, model size, seeds. State which single change you expect to buy most and what would show it.
5. **Evaluation.** The scoring plan: which sets, which metrics per class, what counts as a pass vs R1-A (paired, per class, seed range), the role of the 666 continuity column, and how to attribute each gain to a change (one variable per arm).
6. **Opus graders.** Where more blind Opus adjudication buys the most per card: label-noise audits of bootstrap labels, per-class error sheets, hard-negative mining, or the final test; propose card counts and strata. Reader count per card stays as is.
7. **Risks.** What in this plan could make the reader worse while the numbers look better, and the check that would catch it.

Deliverable: `ASTRA-R2design_review_1.md` with: a table of recommended arms (name, one variable, data, recipe, expected effect, measurement), the bootstrap label policy, the evaluation plan, the grader plan, and the risks. Cite evidence by path.

## Evidence (read these first)

All paths absolute. Read the first four before anything else.
- Owner remarks, verbatim (23, grouped, with category table): ~/Projects/greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/R2_evidence/OWNER_REMARKS_20261017.md
- Owner sheet notes: …/R2_evidence/owner_sheet_notes_20261017.jsonl; 39-slot export …/R2_evidence/reader_errors_39.json; substitution sample …/R2_evidence/substitution_sample_60.json
- R1 outline + report: ~/Projects/greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/clariden/R1_mark_reader_outline.md, …/clariden/R1_REPORT.md
- R1 result: …/clariden/R1_result_3678928/ (RESULT.md, job_RESULT.md, metrics.json, error_types.json, A–E train_log.csv)
- Scored slot mapping: ~/Projects/greek-ocr-toolkit-spellcheck-r1/artifacts/labelfix_r1/score_3678928_K1c_vsS6/ (A/B_mapped_lines.jsonl.gz, RESULT.md)
- Error-type code: ~/Projects/greek-ocr-toolkit-spellcheck/scripts/labelfix/r1_error_types.py; training/extraction code: scripts/labelfix/clariden/r1_*.py, greekocr/labelfix/markshape_train.py
- Frozen print truth (189 words): ~/Projects/greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/print_truth_s0.json (+ print_truth/ answers)
- S8 DEV truth: ~/Projects/greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/S8a6_DEV_TRUTH.md + S8_DEV/evidence/dev_truth.jsonl.gz
- sf6 release audit (100 lines): ~/Projects/greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/L1A2_AUDIT100_RESULT.md + S8_DEV/audit100_private/audit100_final.json
- R0 recogniser audit: ~/Projects/greek-ocr-toolkit-spellcheck-r0/docs/labelfix/spellcheck/R0_REPORT.md
- Astra SC1 label notes: ~/Projects/greek-ocr-toolkit-spellcheck/docs/reviews/astra_program_review_2026-10-06/ASTRA-SC1_review_1.md (M01 line 48, M10 line 145); cycle-2 witness-set advice: ASTRA-SC1c2_review_1.md lines 107–123
- C1 card mark errors (new sources, adjudicated): ~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/c1_results.json (mark_errors), C1_REPORT.md, marks_bias.json
- Release-wide census of substitution holds by class: ~/Projects/greek-ocr-toolkit-spellcheck-l1r3/docs/labelfix/spellcheck/clariden/L1R3_evidence/production_3680729_3680730/census/changes/CHANGES.md
- Data inventory: C1 selection ~/Projects/greek-ocr-toolkit-spellcheck/.cache/labelfix/clariden/C1_selection.jsonl (+ C1_alignments.jsonl.gz, C1_crop_inventory.jsonl.gz); collection v2 ~/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/ (manifest_v2_*.json, CLEAN_REPORT.md); W1 rows ~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/ (W1 build receipts, unchecked_strata.json = stratum gate); locked strata exclusions …/collect_v3/exclusions_manifest.json; synthetic line factory ~/Projects/greek-page-ocr/factory (Rust, recipe.vN.json; codec v2 atoms ~/Projects/greek-page-ocr/codec/v2.json)
- Training-wave lines available for bootstrap inference: 124,669 polytonic train lines (L1 census, …-l1r3 above).

## The track lead's draft design (critique it; it is input, not the answer)
- One fixed recipe (job 3678928 settings), frozen tests, train arms A and B only.
- 0a identical rerun (reproducibility); 0b identical data, new seed (noise floor).
- 1: targeted additions for the owner's categories: agreement words oversampled; more lines from parliament/vouli/openarchives; print-checked letters from books outside every test set; removals only of print-proven mislabels.
- 2: bootstrap, labels = reader∧Google, or reader∧detector vs Google with K1 passing, over C1 plus the 124,669 training-wave lines (needs an inference pass ≈50 min first).
- 3: 2 + 1.
- Tests: the 666, DEV 600, audit100, a new targeted card set from separate books; per-letter old-vs-new diff split target/non-target with pass = non-target changes ≤ the 0b noise floor; for the winner a release rebuild, box regression and a 100-line audit.
- Compute ≈15 min per variant, 1–1.5 GPU-h total.
Specific questions on it: is 0a worth a run; does arm 1 risk teaching the test distribution; does arm 2's reader∧Google label reproduce Google's omissions (both must agree on "no mark" → the shared-omission problem again) and what label rule avoids it; should capitals/all-caps negatives be synthetic, mined, or both; which of the owner's categories need a per-class threshold rather than data.

## Owner (verbatim)

The lead's file OWNER_REMARKS_20261017.md is authoritative. Key lines: "accents tend to be hallucinated on capital A and small o / do you have a ground truth to check that against? / could this be a recurrent error in training data, or something we can correct in the training mix? / after re-training can you test for regressions? or if the fix changed only the intended behaviour?"; "the detector must see ink will lead to other errors, the reader is stronger"; "your reader alone is strong but we should consider how to try to improve it further"; "so presumably now we can rerun this because we have the reader and it will give us stronger agreement data?"; "should definetely run an experiment where we use exactly teh same dataset + recipe plus the changes (additions or removals) that might correct this issue. but we should also plan other ones, eg the bootstrapping experiment I described earlier"; to the coordinator: "Use an astra xhigh review to design experiments: how should the data mixes be? what recipes are likely to yield better results? should we mix previous training data with the new one? what else should we add? should we change something in training / model? Consider using more opus graders."; on the 39-card sheet the owner found one card where truth and reader are both wrong (ἤγε: "this is circumflex actually"); the other 38 cards carry no note and count as unreviewed, not confirmed.
