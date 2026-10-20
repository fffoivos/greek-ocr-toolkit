# L1R4 — SF6c recomposition with L1F recogniser fields

**READY for coordinator submission; no jobs submitted.** Verified 2026-10-17T07:09:12+03:00. The package joins L1F **3680752** by line ID, runs the frozen `sf6-release-v1` composer, and compares its releases with completed L1R3 jobs **3680729/3680730**. Both exact batch entry points passed the complete 64-line mock; the deployment and scheduler checks below are verified.

## Scope and frozen bytes

This worktree is `greek-ocr-toolkit-spellcheck-l1f`, branch `opus/spellcheck-l1f`, HEAD **`0afe7838e91ba1bc142cee6a532808c5d0c04648`**. The difference from the brief's `c79910e9` is the single L1R4-brief commit; no code difference preceded this work. All **30 tracked files in `greekocr/labelfix/` are byte-identical to `d893a04d`**. `release_gate.py` remains `9ef1d6467229e86c9464f428716c792f2a6fc4ffa1e709b798df82c504120408`; `ctc_align.py` remains `3ecb1a208918fdc33b897c00c1848456a9480946a17fb88f7d9f5f400a646068`. No Git-writing commands or other-worktree writes were made. All seven Git metadata files specific to this worktree are unchanged. Concurrent shared metadata changes belonging to the unrelated S8 worktree are recorded separately, without attributing them to this task. [Protection receipt](L1R4_evidence/protected_verification.json).

Policy schema: **`sf6-release-v1`**. Packaging-bound policy digest: `734158eb7555bf7efcfc4f67dad170bcf074c8749542f114011b6e5e6547406d`. The digest changes because the recomposition adapter is source-bound; the gate and scientific modules remain frozen. Saved text, detector evidence, coverage, reader predictions, selection, original labels, paired controls, HOLD exclusion, MOVE rules, consensus-elision zero requirement and ensemble caveat retain their L1R3 contracts.

The [Clariden operating rules](/Users/foivoskarounos-zamparloukos/.claude/skills/optimize-apertus-cscs/SKILL.md) were applied. Network use was limited to Clariden SSH and its configured gateway. No submission, allocation, recognition, detector run, credential refresh or environment installation occurred. The existing certificate expires at **19:18:52 Athens today**. The bounded coordinator stops before the 18:30 READY deadline and allows at most three transient SSH retries; authentication/certificate failures stop immediately.

## Completed L1F receipt verified first

L1F job **3680752** was initially running. Packaging waited for its complete final receipt. The final receipt SHA-256 is **`54fc6d2847088a8f938e1e0de9fd61d95b3f9b2c34232b01c8bb1fc71f51dbaf`**. The remote preflight verifies its complete flag, job identity, approved configuration/code map, input/crop binding digest, checkpoint identities, sealed plan, all **248/248 shard receipts and compressed payload SHA-256 values**, contiguous tasks, shard-file population, per-shard identity totals and exact aggregate population. The approved L1F source map matches the retained original deployment manifest. [Upstream bindings](L1R4_evidence/upstream_binding.json), [complete hash verification](L1R4_evidence/remote/verified/preflight/l1f_final_verification.json).

The following is **L1F's hash-verified per-wave evidence availability**, before the independent L1R4 row reconstruction. It establishes available scored evidence, not production correction yield. Job 1 and job 2 will measure the joined runtime independently.

| Wave | Lines | Exact alignment identity | Withheld identity | Lines with certified slot | Certified slots |
|---|---:|---:|---:|---:|---:|
| mixed | 13,227 | 13,227 | 0 | 13,216 | 491,923 |
| openarchives | 235 | 235 | 0 | 235 | 9,777 |
| parliament | 27,224 | 27,224 | 0 | 26,954 | 837,720 |
| round1 | 43,869 | 43,869 | 0 | 43,847 | 1,675,393 |
| round2 | 17,026 | 17,026 | 0 | 17,018 | 652,449 |
| vouli | 23,088 | 23,088 | 0 | 23,066 | 918,304 |

L1F's alignment identities compare prediction, valid-frame count, scale, strip width and every pixel-rounded saved span. The final receipt reports `124,669` exact identities and `0` mismatches. L1F output shard numbers are inference contexts and are never paired with the **974 detector shard numbers**.

## Job 1 — validated join, then unchanged composition

[`l1r4_join.py`](../../../../../scripts/labelfix/clariden/l1r4_join.py) verifies the final seal before consuming frames. Inside the allocation it verifies exact selected IDs/waves/crops and task membership; compares every sealed-plan saved alignment with the original receipt-bound alignment source; checks saved-text and checkpoint/code/input provenance; and reconstructs the frozen `Alignment.recognition_evidence` object from saved geometry plus actual frame scores. The full fresh scored-alignment hash must reproduce exactly for an accepted identity. Duplicate, missing, unselected, changed, falsely matched or incompatible records fail before composition.

An indexed, receipt-bound join is built by **`line_id`**. Every saved runtime record must match its original text and slot geometry/window anchor. Identity-approved rows receive only `recognition_confidence`, `recognition_evidence`, `image_width`, plus `recognition_provenance`. Frame arrays remain in L1F. A withheld identity has **all three optional consumer keys omitted**, rather than zero, null or synthetic evidence. The two transferred mock records verify this omission explicitly. Low measured confidence remains a measured value and does not become certification.

[`l1r_recompose.py`](../../../../../scripts/labelfix/clariden/l1r_recompose.py) retains the original input checks before joining and passes the saved joined shard to the same `l1_common.release` and frozen composer. Joined runtimes, index, join receipt and every release payload are hash-bound. Restart reuses only exact bindings and rejects a changed index or sealed input. Job 1's join receipt reports certified lines/slots, joined/refused lines and optional-field presence **per wave**; job 2 rechecks actual saved joined records. Full-population frame decoding/reconstruction is allocation-only. The login preflight hashes sealed files and verifies receipts without decoding production frames or composing lines.

Output:

```text
.../l1e_20261017/l1r_sf6f_<JOB1>/
  input_verification.json, l1f_join.sqlite, l1f_join_receipt.json
  shards/shard-NNNNN/selection.jsonl
  shards/shard-NNNNN/joined-runtime.jsonl.gz
  shards/shard-NNNNN/release/*, receipt.json
  release/*, receipt.json
```

## Job 2 — actual releases, L1R3 delta and audit population

[`l1r4_census.py`](../../../../../scripts/labelfix/clariden/l1r4_census.py) first inventories both original saved populations and the actual joined runtime, then runs the existing HOLD and SF6 deletion/change censuses. It verifies the completed L1R3 release DAG and census outputs against pinned receipts and requires the same original input population. Original-label, per-wave, paired-release and consensus-elision checks remain active.

For every mode and wave, `L1R3_DELTA.json` reports baseline/new/delta for real mark-correction lines, corrected status, SF6 deletion HOLD lines and per-class distinct lines/blocked checks (**mark, apostrophe, quote, keraia, other**; classes overlap). The original censuses also retain MOVE, elision and deletion inventories. `changes/real_mark_correction_lines.jsonl` remains the complete new release population.

**`newly_real_mark_correction_lines.jsonl`** is the exact `(mode, line_id)` set difference versus L1R3, retaining `wave` and all new rows without an example cap. It detects replacements even when aggregate counts are equal. Both audit populations are deduplicated and checked against overall/per-wave correction counts; malformed or changed baseline receipts fail the combined seal.

```text
.../l1r_sf6f/census/output_<JOB1>_<JOB2>/
  evidence_availability_original.json
  evidence_availability.json
  hold/{CENSUS.json,CENSUS.md,receipt.json,...}
  changes/{CHANGES.json,CHANGES.md,real_mark_correction_lines.jsonl,receipt.json,...}
  L1R3_DELTA.json, L1R3_DELTA.md
  newly_real_mark_correction_lines.jsonl, receipt.json
```

## Complete 64-line mock and checks

Both exact sbatch entry points ran in explicit verification mode against the complete saved 64-line runtime and L1F's retained real CPU-mock outputs. The historical fixture's 15 files were copied into **this** worktree after matching the previous SHA-256 map; no production frames, models, crops or runtime payloads were transferred here. [Job 1 log](L1R4_evidence/mock_job1_ready.log), [job 2 log](L1R4_evidence/mock_job2_ready.log).

Independent direct joining from L1F outputs gives exact frozen-composer parity **256/256 mode/line decisions**, **7,620/7,620 slot/mode decisions**, and actual release parity over **192 mode/line records and 5,715 slot decisions**, including labels, HOLD exclusion, aliases, deletion checks and elision serialization. Both local batch mocks use the same code map and policy as the deployed package. Job 1 took **3.019 s**, job 2 **0.736 s**. [Parity receipt](L1R4_evidence/mock_parity_ready.json), [combined census seal](L1R4_evidence/mock_ready_receipt.json).

The joined fixture has **62/64 certified lines**, **1,704/1,905 certified slots**, and zero predicate errors. Its two refused identities (`177b717d-p000097-l0007`, `51fe7386-p000024-l0015`) retain all three consumer fields missing. This differs deliberately from L1F's raw audit rows, which retain raw scores even for identity refusal. [Joined inventory](L1R4_evidence/mock_ready_evidence_availability.json).

Both required demo lines change from whole-line **HOLD → corrected**, and their relevant deletion checks become allowed:

- `384c3f89-p000059-l0023`: acute at original NFD offset 25, `γήρυς → γῆρυς`.
- `384c3f89-p000096-l0031`: psili at offset 35, `ἔθεν → ἕθεν`.

Native width alone leaves both held; scored recogniser absence is necessary. Existing bounds, reader/detector disagreements and other gate refusals still apply.

| Mode | Real mark lines L1R3 → L1R4 | Newly real lines | SF6 deletion HOLD L1R3 → L1R4 | Mark HOLD lines L1R3 → L1R4 |
|---|---:|---:|---:|---:|
| PRESENCE | 2 → 7 | 5 | 39 → 30 | 36 → 27 |
| FULL | 2 → 6 | 4 | 39 → 30 | 36 → 27 |
| ENSEMBLE_AB | 2 → 10 | 8 | 39 → 27 | 36 → 24 |

These rows are all `heldout-verification`. Other class line counts remain apostrophe **1 → 1**, quote **3 → 3**, keraia **0 → 0**, other **3 → 3**, in each mode. Mark blocked-check counts change **47 → 36 / 36 / 32** respectively; other class checks are unchanged. The new audit list contains **17 mode/line rows, 8 unique IDs**. [Per-wave/class deltas](L1R4_evidence/mock_ready_L1R3_DELTA.json), [new audit list](L1R4_evidence/mock_ready_newly_real_mark_correction_lines.jsonl). These are fixture effects; production correction/HOLD deltas remain for the authorized jobs.

**1,556 labelfix tests passed in 13.90 s**, without skips or deselections. New coverage includes final/shard corruption, missing shards, wrong job/population/config/code pins, exact saved/fresh identity, text/span/region/score forgery, transferred omission, ID/order joins, geometry mismatch, index corruption on resume, allocation/output guards and equal-count audit replacements. Existing frozen gate, MOVE, deletion, consensus-elision and restart tests remain green. [Suite log](L1R4_evidence/tests_labelfix_final.log), [new tests](../../../../../tests/labelfix/test_l1r4.py). All packaged Python files parse; the three new shell files pass `bash -n`; `git diff --check` passes.

## Deployment, scheduler simulation and estimate

Root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1r_sf6f/`.

**342/342 files match locally, in the archive, and remotely before and after preflight.** Returned `L1R4_DEPLOY_SHA256.txt` bytes equal the local manifest; SHA-256 **`2544d9759f4fa1561bf7c85c9a2216179f5c4129bba7db933bbe5179a1665e43`**. The returned source map and packaging policy exactly match the mock and local source tree. All 14 external pins and the existing SciPy manifest pass; the original input verifier covers **124,669 lines / 974 shards**. No runtime installation changed. [Local deployment](L1R4_evidence/deployment_local.json), [remote verification](L1R4_evidence/deployment_remote.json), [manifest](L1R4_evidence/L1R4_DEPLOY_SHA256.txt).

Both scripts use account `a0140`, partition `debug`, one node/task. Job 1 retains **64 CPUs, 32 shard workers, exclusive, 01:00:00**. Job 2 retains **16 CPUs/workers, 00:30:00**. The live debug partition is UP with a 01:30:00 cap. These are scheduler tests, not submitted jobs or reservations.

Exact dependency-bearing tests:

```bash
sbatch --test-only --dependency=afterok:3680752 scripts/labelfix/clariden/l1r4_job.sbatch
sbatch --test-only --dependency=afterok:3680729 scripts/labelfix/clariden/l1r4_census_job.sbatch 3680729
```

Job 2 uses the completed L1R3 job only as a test payload/dependency stand-in. Its real dependency will be the newly submitted L1R4 job 1. Dry-run results:

**job1:** dependency-test exit `0`.

```text
sbatch: Job 3680761 to start at 06:08:27 a using 288 processors on nodes nid007048 in partition debug
```

**job2:** dependency-test exit `1`.

```text
allocation failure: Job dependency problem
```

The scheduler could not resolve the historical dependency during test-only; a separate resource/payload-only dry run passed:

```text
sbatch: Job 3680763 to start at 06:08:28 a using 288 processors on nodes nid007048 in partition debug
```

No dry-run number is a submitted job ID. [Preflight logs and queue readback](L1R4_evidence/remote/verified/preflight/), [bounded SSH step receipts](L1R4_evidence/remote/).

Planning estimate: **40 minutes after allocation starts, excluding queue delay** (about 25 minutes job 1, 15 minutes job 2). Actual L1R3 jobs took 7:27 and 5:42. The 64-line join alone took 0.188 s on the Mac; its simple serial extrapolation is about 6.1 minutes and is **not** a measured Clariden production runtime. The estimate adds full-frame decoding/reconstruction, joined output/inventory, repeated hashing, baseline verification and reserve. Full-population L1R4 runtime remains unmeasured. [Join timing scope](L1R4_evidence/join_timing.json).

## Coordinator submit commands — prepared, NOT executed

Run on Clariden only after separate submission authorization:

```bash
set -euo pipefail
L1R4_ROOT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1r_sf6f
cd "$L1R4_ROOT"
sha256sum --check L1R4_DEPLOY_SHA256.txt
sha256sum --check L1R4_EXTERNAL_SHA256.txt
JOB1=$(sbatch --parsable --dependency=afterok:3680752 scripts/labelfix/clariden/l1r4_job.sbatch)
JOB1=${JOB1%%;*}
JOB2=$(sbatch --parsable --dependency=afterok:"$JOB1" scripts/labelfix/clariden/l1r4_census_job.sbatch "$JOB1")
JOB2=${JOB2%%;*}
printf 'L1R4_JOB1=%s\nL1R4_JOB2=%s\n' "$JOB1" "$JOB2"
```

## Pull results after successful completion

Run from this worktree using actual submitted IDs. This returns small receipts/manifests and the two complete audit lists, without frames, joined runtime, crops or models:

```bash
set -euo pipefail
JOB1=REPLACE_WITH_ACTUAL_JOB1
JOB2=REPLACE_WITH_ACTUAL_JOB2
L1R4_BASE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017
L1R4_LOCAL="docs/records/labelfix/spellcheck/clariden/L1R4_evidence/production_${JOB1}_${JOB2}"
mkdir -p "$L1R4_LOCAL/release" "$L1R4_LOCAL/census"
ssh -o BatchMode=yes -o ConnectTimeout=20 clariden \
  "cd '$L1R4_BASE/l1e_20261017/l1r_sf6f_$JOB1' && tar -cf - receipt.json input_verification.json l1f_join_receipt.json release/release_*.json" \
  | tar -xf - -C "$L1R4_LOCAL/release"
ssh -o BatchMode=yes -o ConnectTimeout=20 clariden \
  "cd '$L1R4_BASE/l1r_sf6f/census/output_${JOB1}_${JOB2}' && tar -cf - receipt.json evidence_availability.json evidence_availability_original.json L1R3_DELTA.json L1R3_DELTA.md newly_real_mark_correction_lines.jsonl hold/receipt.json hold/CENSUS.json hold/CENSUS.md changes/receipt.json changes/CHANGES.json changes/CHANGES.md changes/real_mark_correction_lines.jsonl" \
  | tar -xf - -C "$L1R4_LOCAL/census"
```

L1R4 READY: policy sf6-release-v1 + L1F 3680752 fields; gate identical to d893a04d; mock parity 256/256; demo lines allowed 2/2; deploy sha256 342/342; test-only PASS/PASS (dependency unresolved; resources passed); est 40 min
