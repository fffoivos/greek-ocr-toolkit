# RUC2 ia_russian re-check

c1 is accepted under v4.2: **27 exact + 54 v4-downscale = 81/81 returned images**, no violations, manifest check enabled. The only waived findings are read-only Helvetica `-font` operands at records 194 and 215. The original c1 VOID scan is retained as historical evidence. A fresh c2 v4 scan matches its existing scan (55/55 images, no violations); see scan/c2_recheck_receipt.json. The Sol-reading scanner remains unchanged.

| Sample | Cards | Letters y | Crop_ok y | Marks y | Controls |
|---|---:|---:|---:|---:|---:|
| RUC1 c1 + c2 | 100 | 87 | 83 | 99 | 10/10 |
| C1, old labels, different card set | 100 | 74 | 97 | — | — |

Letters: repaired-label cards **17/18**; unrepaired **70/82**. Repaired means actual label text changed; it does not include unchanged RU1-ok labels.

**Gate: FAIL** (letters ≥90 and crop_ok ≥90). Letters and crop_ok are final Sol verdicts; marks remain **pending_opus**. Admission state was not updated.

Against C1, letters change by +13 percentage points and crop_ok by -14. These are different card sets: this is a descriptive, unpaired comparison and does not establish a causal repair effect.

Controls: 10/10. Context details: c1: 5/5, 0 errors, flagged=False; c2: 5/5, 0 errors, flagged=False. Marks are excluded from control pass/fail.

The [review queue](review_queue.jsonl) contains **37 unique cards** (34 bed, 3 controls). It retains every negative/unreadable verdict, nonempty error list, and control disagreement, including expected-negative controls. IDs, crop hashes/paths, original detail and reasons are preserved. Review remains pending.

Eight wrapper tests pass, including both real witnesses, non-font outside paths, parent escapes, both font roots, font writes, and v4 downscale boundaries. The v4.2 read proof is conservative: known ImageMagick `-font` argv operands and standalone cat/stat/ls reads are accepted; unknown uses fail closed. No rollout code is executed by the allowance check.

[HANDOVER.v42.patch](handover/HANDOVER.v42.patch) adds the §5 ruling after the existing v4.1 bullet. Before/after hashes, patch hash and a separate guarded commit list are prepared for the lead; the patch has not been applied.

RUC2_COMMIT_FILES.txt and RUC2_COMMIT_GUARD.json bind this change set. Require matching HEAD/branch, empty index, input and output hashes; stage only listed paths and verify the exact staged set. Stop on mismatch. No staging or commit was attempted.

RUC2: done | v4.2 witness: ok | letters y: 87 (repaired 17/18, unrepaired 70/82) | crop_ok y: 83 | controls: 10/10 | gate: fail | review queue: 37
