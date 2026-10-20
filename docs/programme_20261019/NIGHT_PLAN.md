# One cohesive plan — the OCR programme after the clean-up, run autonomously (19→20 Oct 2026)

Owner, 19 Oct 23:40: "turn it into one cohesive plan; run it end to end autonomously over night, after the repo fix is done". Standing gates that stay with the owner: pushing to origin, Opus reader runs, new cloud pods, spend beyond the preset caps (150 GPU-h per wave, 120 GPU-h scaling series), anything irreversible outside this plan. Everything else is decided here and logged in `NIGHT_STATE.json`. Reviews at the four checkpoints are cross-vendor (gpt-6-astra via `docs/records/reviews/harness/run_review_thread.sh`, xhigh, read-only repo, model asserted); BLOCKER/HIGH are fixed and re-reviewed until clean or a stall halts; MEDIUM/LOW are logged. Codex weekly usage is read before every Sol fleet step and the run stops at 90%. Clariden jobs are verified (VERIFY_OK) before submission, smoke before full, monitored every 15 minutes, logs read on FAILED. Times in Europe/Athens, stamped from `date`.

## Step DAG
| id | step | deps | executes | acceptance | gate |
|---|---|---|---|---|---|
| R1 | Clean-up: integration, tests green, data out of git | — | done / running | suite 0 failed; move manifest + receipts committed; size guard passes | — |
| R2 | Layout by taxonomy (CLEAN4L): drafts placed under docs/A_ocr_development, docs/B_training_data/{a,b,c,d}, docs/shared, docs/records; empties and generated trees removed; stale pipeline docs replaced | R1 | Sol (file work) + coordinator commit | tree matches PLAN.md map; links resolve; suite still 0 failed | — |
| R3 | README.md + AGENTS.md from the outline (CLEAN5E) | R2 | Sol + coordinator review | both documents cover every item of the outline; no claim contradicts tool_versions.json | — |
| R4 | SEG10: port census03 integration fixes; band 0.30–2.00 → segmentation 0.9-s5, pipeline 0.3.1 | R1 | Sol + coordinator commit | tests; replay changed set = s5 (59/38); suite 0 failed | — |
| R5 | **Checkpoint 1** — Astra xhigh review of the clean-up against OWNER_BRIEF.md (base = integration commit ac1c38cf6, head = after R4) | R2,R3,R4 | Astra | `VERDICT … BLOCKERS: 0 | HIGH: 0` after fixes | stall → halt |
| R6 | Local merge of cleanup/20261019 into main (no push) | R5 | coordinator | main == cleanup head; suite 0 failed on main | push stays with the owner |
| P1 | SPLIT1 adopted as proposed → `row_split.jsonl` (final `split` field) + edition map | — | sourcing lead (Sol) | every W1/W2 row has train/dev/test; 99 forced-test editions kept; receipt | — |
| P2 | sf7 TR2 test/dev inference on Clariden (≈40 min, 4 GPUs) → audit numbers; sf7 status released only if the preregistered bar passes, else stays candidate (add_corr then uses RU1 + N1 only) | — | spell-check lead (Sol); coordinator submits | TR2 receipt; status decision logged | Clariden spend (within caps) |
| P3 | Census rerun (census_05): deploy main's pipeline 0.3.1 + seg 0.9-s5 + gate 0.3 + corrections; pinned split input from P1; VERIFY_OK → smoke → full | R6,P1 | segmentation lead prepares; coordinator submits | CURRENT.json complete; decisions.jsonl; admitted_train; per-reason counts | census spend (owner go given 19 Oct) |
| P4 | **Checkpoint 2** — Astra review of the census package and results (gate counts, admitted counts per class/source, pending queues) | P3 | Astra | clean | — |
| P5 | Benchmark 0.2 draw: candidates from SPLIT1 TEST editions only (dev from DEV), admitted rows, 16 quota classes, book cap 4/edition, source round-robin; tags from pipeline evidence | P3 | sourcing lead (Sol) | 2,400 test + 600 dev candidates with 20% overdraw; draw plan + counts | — |
| P6 | Sol last-filter checks on every candidate (OK / crop violates rule / text differs); flagged lines replaced from the same class+source; owner sample sheet built (not required for progress) | P5 | spell-check lead (Sol fleet, ≤ 24 workers) | ≤ 3,600 checks; flag rate per class reported; final 2,400/600 sealed | Codex usage < 90% |
| P7 | Seal benchmark 0.2 on Clariden (suite.json v0.2: images sha256, references = corrected labels, tags, draw plan, check receipts); score the wave-1e control on it | P6 | benchmark builder (Sol) ; coordinator submits scorer | qualification receipt; baseline scores per class | — |
| P8 | Release v3 train = admitted − benchmark editions; edits-only corrections registered; admission receipts; W2 original crops uploaded to Clariden with hash receipt | P3,P6 | sourcing lead (Sol) | release_v3_admission file + sha; upload receipt 0 mismatches | — |
| P9 | **Checkpoint 3** — Astra review before wave 2: release v3, benchmark 0.2, exposure audit | P7,P8 | Astra | clean | — |
| W2a | **Checkpoint 3b (owner rule, 20 Oct 00:57)** — Astra xhigh review of the deployment-ready wave-2 package BEFORE launch: deployed bundle + DEPLOY_SHA256SUMS, VERIFY_OK, the package tests and the smoke run on debug, the preregistered hypotheses and driver rules, the exposure audit; fix-until-clean | P9 | Astra | clean | no launch before PASS |
| W2 | E4 wave 2 (H7): ctrl / add / add_corr × 3 seeds; deploy, smoke on debug, submit; readback; registry rows | P9 | training lead (Sol); coordinator submits | 9 runs complete; driver verdict on H7; benchmark 0.2 per-class table | ≈ 27 GPU-h |
| W3 | **Checkpoint 4** — Astra review of wave 2 results | W2 | Astra | clean | — |
| S1a | **Checkpoint 4b** — Astra review of the deployment-ready scaling package (C1 width ladder × size): bundle, VERIFY_OK, tests, smoke, preregistration, budget accounting | W3 | Astra | clean | no launch before PASS |
| S1 | Scaling wave 3 part 1: C1 width ×1/×1.5/×2 × size {208k, 420k or actual} on release v3, 3 seeds, pinned control; then M3/M4 | W3 | training lead (Sol) | runs complete; registry; benchmark per class | ≤ 150 GPU-h; series ≤ 120 GPU-h |
| S2a | **Checkpoint 5b** — Astra review of each novelty family's deployment-ready package before its launch (one review per family: C2, P1, S3, G, M), same contents as 3b | S1 | Astra | clean | no launch before PASS |
| S2 | Wave 3 part 2 (novelties, §5b of the programme doc): C2 semantic guidance, P1 in-domain pretraining with compute-matched control, S3 confidence weighting, G v6 ablations, M1/M2 | S1 | training lead (Sol) | preregistered rows; verdicts | same caps |

## Review rule for experiments (owner, 20 Oct 00:57)
Every experiment family gets an Astra review of its deployment-ready code before launch — the deployed package as it will run (bundle hashes, VERIFY_OK, package tests, smoke run on debug, preregistered hypotheses and decision rules, exposure/leakage audit) — and a fix-until-clean loop; nothing is submitted before PASS. Results get their own review after the run (checkpoints 2, 4).

## Fallbacks
- A Sol run fails or the suite goes red: fix-until-clean with the same brief + the failure log; a repeated identical failure signature = stall → halt and leave a note for the owner.
- Astra harness error (exit 9 / non-numeric verdict): halt that checkpoint; continue independent branches (P1, P2) only.
- Clariden FAILED: read the log before any resubmit; a package defect goes back to its lead; never resubmit blind.
- Codex weekly ≥ 90%: stop Sol fleets; continue with Clariden jobs already queued; report.
- Owner interrupts: stop launching, finish in-flight jobs, report state from NIGHT_STATE.json.
