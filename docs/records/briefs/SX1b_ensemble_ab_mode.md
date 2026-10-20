# SX1b: add the ENSEMBLE_AB release mode to the SX1 extract (gpt-6.1-sol, medium; network ON for Clariden only, READ-ONLY; no .git writes)

**Why:** SX1 extracted the PRESENCE and FULL modes only. The owner-audited release (audit100, L1A2: "100 of the 155 ENSEMBLE_AB sf6 real
mark-correction lines", L1R3 3680729) is the **ENSEMBLE_AB** mode. Without it, audit100 looks like 71/99 held.

Repeat SX1's procedure (`artifacts/sx1/extract.py` and RECEIPT; the same truth input, sha d2cdc75c…) with the ENSEMBLE_AB status, label
and HOLD reasons added per id, next to PRESENCE and FULL. Name the ENSEMBLE_AB files used, with their shas.

- **Output:** `artifacts/sx1/sf6_release_extract_lqb_v2.jsonl`. Keep v1 unchanged.
- **Receipt:** `RECEIPT_v2.json`.
- **Report:** update SX1_REPORT.md with the per-mode counts per set.
- **Check:** audit100 ENSEMBLE_AB must show 99 released corrections (the audited lines were all corrected releases). Otherwise STOP
  and report.

The cert is valid until 18 Oct 18:39; never refresh it.

Last line: `SX1b READY: ENSEMBLE_AB released <n> / held <n>; audit100 released 99/99 <yes|no>; extract v2 sha <12>`.
