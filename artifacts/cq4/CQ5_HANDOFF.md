# CQ5 — aggregate audit and package specification conflict

19 October 2026, Europe/Athens. Status: **insufficient to certify a training package**; **W-CAP coverage itself passes the written minimum**. No deployment, Slurm submission, SSH operation, new reader, training, or data transformation was performed. Package preparation is pending the specification clarification requested from the coordinator.

## Authoritative inputs

Read HANDOFF_20261018_spellcheck.md §2 and the sibling r2prep R2A2_PREREGISTRATION.md. The sibling and CQ4 copies both hash to `dbac559fe9792a4f7c879f1fc7b08d03c6a82611bbb42ecce1ffd4ae31ccbebc` (amendment 1). Scanner bound in the aggregate: v4.5.5, `e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1`.

Read the existing aggregate without rerunning AGGREGATE.sh. Its current JSON is reproduced in CQ4_REPORT.md under “Reading results”; that report's earlier narrative and zero-count tables are historical and stale. Receipt and truth/quarantine rows were independently counted; accepted ledger answers were checked against the existing answer files and control keys.

## Aggregate

| Set | Resolved | Marked | Bare | Quarantined |
| --- | ---: | ---: | ---: | ---: |
| W-CAP | 281/300 | 133 | 148 | 19 |
| Top-up | 1009/1205 | 289 | 720 | 196 |

W-CAP has resolved support in all 20 selected documents, maximum 20 resolved slots per document. Resolved W-CAP and top-up document sets are disjoint. Truth remains tier C, Sol one-reader with the compound re-read rule; no new pixel adjudication is claimed.

The preregistration's amendment 1 states a **210-slot minimum for W-CAP**, total, against a planned approximately 150 marked + 150 bare. The inventory independently records `minimum: 210`. **281 ≥ 210**, by 71: the written coverage gate passes. The preregistration supplies no separate marked-slot power minimum, effect-size power calculation, or rule converting 133 marked slots into a guaranteed statistical power. Do not misread 210 as a marked-slot minimum or assert that statistical power has been demonstrated. The primary still requires ≥10 pp pooled gain, a document-cluster bootstrap 95% interval excluding zero (50,000 replicates, seed 20261017), gain in ≥2/3 seeds and positive mean, plus at most two additional pooled false additions on bare W-CAP.

## Re-read agreement and controls

| Set | Triggered | Agreed | Valid pairs | Missing/VOID | Disagreed | Agreed unreadable |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| W-CAP | 103 | 84 | 90 | 13 | 6 | 0 |
| Top-up | 447 | 256 | 267 | 180 | 11 | 5 |
| Total | 550 | 340 | 357 | 193 | 17 | 5 |

Receipt agreement is **340/550 = 61.82%**: missing/VOID re-reads remain in the denominator. Agreement conditional on valid pairs is **340/357 = 95.24%**, a separate descriptive statistic. The five agreed unreadables count as agreement but remain quarantined. Queue total is 215 = 193 missing/VOID + 17 disagreements + 5 agreed unreadables, partitioned W-CAP 19 + top-up 196.

- Initial phase: 18/18 accepted after the existing rescan overlay; 178/180 control presentations correct. `topup_initial_001` and `topup_initial_013` each have one error, all others zero. Each accepted context satisfies the ≤1-error limit.
- Re-read phase: four VALID, three VOID; all seven existing answer files have 0/10 control errors. Accepted re-read control presentations are 40/40 correct. The other 30 controls belong to rejected contexts and do not validate their target answers.
- VOID re-reads: `topup_reread_001`, `topup_reread_002`, `wcap_reread_001`, each recorded as `reader/closure leak scan failed`. Their 90 + 90 + 13 target answers are excluded. No scanner ruling is overturned here.
- All existing answers together: 248/250 control presentations correct; these are repeated presentations, not 250 distinct control identities.

## Why no package can yet be certified as exactly preregistered

The brief and the frozen preregistration give incompatible training specifications. Clarification was requested; no answer is assumed.

| Parameter | Frozen preregistration / R2a parent | CQ5 brief | Disposition |
| --- | --- | --- | --- |
| Old pool | Preserve exactly as BASE used it, duplicates included (R2J4) | Remove churn duplicates by index | Incompatible; no removal performed |
| W-CAP | Independent evaluation witness; aggregate rows say `witness_only` | Include W-CAP at a preregistered training share | No such training share exists in this file; would contaminate the named endpoint |
| Training addition | R2a v2 overlay, 1572 slots, plus separate capitals top-up to 1300 capital slots (800 negative / 500 positive) | R2a pool plus W-CAP | Separate top-up is the preregistered intervention; current 1009 resolved top-up labels have not been assembled into that final manifest |
| Seeds | 20261016, 20261017, 20261018 | 17/18/19 | Literal seed list conflicts; do not silently substitute 20261017/18/19 |
| Recipe | Identical to R2a job 3683130: epochs, batch, sampler, optimiser, LR, augmentation | Same as R1-A | Requires reconciliation against the actual frozen parent before packaging |

The hand-off §2 also calls for amendment 1a concerning exposed validation documents and the LQB in-sample guard. The supplied dbac559f preregistration ends at amendment 1; no amendment 1a or new binding hash is asserted here.

Next required coordinator decision: follow the frozen preregistration (W-CAP evaluation only, separate top-up, preserved old duplicates, original full seeds), or supply an explicit amendment with a new independent evaluation design and resolved seed/data rules. The 215-slot lead queue remains available for adjudication, especially the 196 unresolved top-up slots. Coverage of W-CAP is not the blocker. A deployable manifest, parameter-equivalence table, actual-job resource verification, verify_deploy closure, smoke script, and coordinator submission commands cannot be certified until the scientific specification is resolved; none is presented as ready.

## Custody

Base checkout HEAD at audit: `9e3f56adfcce1f4d30492d6d4c48103144cffea2`. Existing unrelated untracked files were preserved. `CQ5_REPORT_BUNDLE.tar` is a local report/evidence archive, not a training package or a Git commit; `CQ5_REPORT_BUNDLE.sha256` binds it. No `.git` mutation was attempted.

| Input | SHA256 |
| --- | --- |
| aggregate_receipt.json | ed47ba98f727022970f1d876d35d11792b53176709a949cce62a26504c7f053d |
| truth/wcap.jsonl | 5b4aed01d4dc74d3800ba5191498cfabc496646d1d8d6557569a1dd283de8336 |
| truth/topup.jsonl | f9e363d19ab274d3db3f03c43618d0730a4f2ba742500f9c55e95a6389e1f8f9 |
| quarantine/wcap.jsonl | 10d7a7e41bd0f388214cfbb4a4378bcca33bc58c2c1165fa879f6b639309b901 |
| quarantine/topup.jsonl | 5c7fa44edda1a806c006e0122bc2a0f260be0bb4a9496ade085091b61eeced73 |
| lead_queue.jsonl | 6cfc7e304e2bfc66818b75510aa126fc6a5db9174ce55a748cddbf2d7f95a14c |

In the required status line, `insufficient` describes package readiness owing to unresolved specification, not failure of the W-CAP 210-slot gate.

CQ5: insufficient | W-CAP 281/300 (marked 133) | top-up 1009/1205 | agreement 340/550 | package: none | commit bundle
