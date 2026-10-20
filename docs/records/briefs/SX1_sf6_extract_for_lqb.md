# SX1: a local extract of the sf6 release labels for the LQB truth line ids (gpt-6.1-sol, medium; network ON for Clariden only, READ-ONLY; no .git writes; no submission)

**Requester:** the secondary-corrections lead, for the Label Quality Benchmark.

**Truth ids:** `~/Projects/greek-ocr-toolkit-secondary/docs/labelfix/lqb/truth_v1.jsonl` (field `line_id`). Verify that its sha256
starts with `d2cdc75c`, or STOP. Copy it read-only into `artifacts/sx1/truth_v1_input.jsonl`.

**The sf6 release (remote, read-only):**
- `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1e_20261017/l1r_sf6_3680729`;
- selection `…/labelfix_l1_20261017/artifacts/labelfix_l1/binding/selection.jsonl` (sha256 ee6c51bd…);
- receipt sha256 c7cfcc85…;
- policy digest 6f62925a….

The exact files and fields are as SQ1 used them: see `artifacts/sq1/` (census script) and `docs/records/labelfix/spellcheck/SQ1_QUOTE_BREATHING.md`.

**The cert is valid until 18 Oct 18:39 Athens.** Never refresh it; an auth error means STOP. Use the login node only, for a few minutes
of CPU.

**Do:**
1. **On the login node,** filter the release to the truth line ids. For each id in the 124,669 selection, emit:
   - `line_id`;
   - `google_text` (original);
   - the release status per mode: PRESENCE and FULL, each one of released-corrected / released-unchanged / HOLD;
   - the released label text, or null on HOLD;
   - the HOLD reasons;
   - the source and wave.
2. **Pull only that extract back** to `artifacts/sx1/sf6_release_extract_lqb.jsonl` and verify its sha after transfer. Ids NOT in the
   selection are listed in `artifacts/sx1/not_in_selection.jsonl`, each with the truth set it belongs to.
3. **Receipt** `artifacts/sx1/RECEIPT.json` with:
   - the input truth sha;
   - the remote paths and receipt sha, the policy digest and the selection sha;
   - the script copy with its sha (`artifacts/sx1/extract.py`);
   - the extract sha;
   - counts per truth set: in selection, released, held and not covered.
4. **Report** `docs/records/labelfix/spellcheck/SX1_REPORT.md`: one table of the truth sets by coverage. My expectation, to be confirmed or
   refuted:
   - audit100 and the substitution sample: fully in the selection (drawn from the release);
   - DEV: mostly in it (training-wave lines);
   - T4, T2, CQ1 and the 39 held-out cards: NOT in it (outside the training wave).

Last line: `SX1 READY: truth ids <n>; in selection <n>; released PRESENCE <n>/FULL <n>; held <n>; extract sha <12>; coverage by set <...>`.
