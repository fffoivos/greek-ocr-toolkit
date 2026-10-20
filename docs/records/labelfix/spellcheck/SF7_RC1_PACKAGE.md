# GC1 — sf7-rc1 A/B gate and recomposition package

17 October 2026. This is a candidate package; nothing is bound or released before the preregistered LQB comparison, independent verification and fresh blind audit. No job was submitted. No `.git` writes were made. Network use was restricted to Clariden staging, dry-run, deployment, SHA verification and scheduler test-only operations.

Binding preregistration: [`SF7_PREREGISTRATION.md`](SF7_PREREGISTRATION.md), SHA-256 **`64a84ed0c8799026d44f066570b54075e9b9d1fbca8e2f099cfc9e9451189b2d`**. Every SF7 receipt and release manifest records this digest.

## Policy and difference from sf6

The new gate is [`scripts/labelfix/release_gate_sf7.py`](../../../../scripts/labelfix/release_gate_sf7.py). It imports frozen sf6 primitives; sf6 does not import it. The module lives outside `greekocr/` to avoid adding a file to the historically frozen library tree. No existing gate tests were edited.

- Policy: `sf7-release-v1`.
- SF7 digest: **`f41e05636d165f1d15edbdb4f2bb6c1aa46721962a96302be8c4dce7ce305047`**, over 21 paths: the 16 sf6 policy paths plus the sf7 gate, preregistration, recompose consumer, existing recomposition extension and sbatch entry point. The deploy manifest additionally binds every shipped dependency and configuration.
- Sf6 remains **`6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406`**. Its full serialized outputs on **168 saved fixtures** are identical to the before snapshot, including changes, holds, decisions and deletion checks; canonical serialization avoids treating JSON tuple/list encoding as a behavioral difference. See [reproduction receipt](SF7_evidence/sf6_reproduction.json) and [before snapshot](SF7_evidence/sf6_before.json).

**Substitution discrepancy, reported before any source edits:** sf6 does *not* currently implement reader-alone substitutions. Its `google_deletions()` inventories the old atom in a replacement, and its deletion guard can require two positive absence signals. Sf7 follows the binding preregistration's explicit reader-alone substitution rule. This is an intentional behavioral difference, not a claim that sf6 already behaved that way.

| Operation | Sf6 | SF7 A | SF7 B |
|---|---|---|---|
| Quote alias immediately before a capital gaining breathing/accent | Separate renderer/guards can HOLD or retain alias | Shared physical decision: one compound consumes alias; separate quote and compound preserve both; unresolved groups HOLD | Same as A |
| Pure deletion | Frozen two-positive-absence guard, including its existing MOVE exception | Calls the unchanged sf6 guard | Same as A |
| Substitution | Old atom passes deletion guard | Accepted reader alone | Same as A |
| Pure mark addition | Accepted reader alone | Same, except subscript needs observed, uniquely owned detector below-mark ink | Accepted reader AND (owned detector ink in the mark zone OR certified recogniser text carrying the mark) |

Production reader mode is **ENSEMBLE_AB**: A and B readers must agree exactly, and count together as one reader signal. The letters A/B in output filenames identify the **addition-rule variant**, not those reader checkpoints. No reader checkpoint is replaced by R2a-2.

For mark edits, removed/added atoms on the same letter are paired as substitutions, preferring the same mark family; unmatched atoms are pure deletions/additions. Keeping an accent and adding a subscript is always an addition. Sf7 retains sf6 observation, K1, supported-character and reader-agreement vetoes.

Positive detector presence uses saved native blob source IDs uniquely owned by that slot, in `above` or `below`, with finite nonempty geometry, positive area and no relevant clipping/unknown observation. It does not turn a detector's mark name into an independent reader vote. Recogniser presence calls sf6c's exact `_recogniser_scored`: explicit line and regional confidence **strictly greater than 0.5**, saved alignment provenance, text identity, image bounds and whole-window containment. Missing evidence remains missing.

The preregistration supersedes the earlier brief: **B has no additional detector-only subscript requirement**; its scored recogniser route applies to subscripts too. A retains its explicit below-mark requirement.

## Quote regression pair

Both addition variants pass the positive `nlg--f4b52df5f8130047--s005-l0015` saved runtime: the output contains **Ἄδεια**, with no residual quote. Source components **5 and 6** form one adjacent named preposed compound; two component blobs are not counted as two semantic symbols. The same quote decision normalizes the renderer result, punctuation comparisons, release composition and deletion/MOVE inventory.

Both also preserve **« plus Ἢ** on the physical `nlg--f4b52df5f8130047--s004-l0008` control, including restoration when the source fixture omits the capital marks. **Evidence boundary:** this control has a saved native crop but no saved full reader runtime in the workspace. Its regression therefore uses an explicitly constructed reader/recogniser fixture with the actual manually assigned native quote and compound groups (4-connected threshold-130 components: quote ID 3 `[6,18,19,34]`, compound ID 1 `[28,4,43,15]`). It is not represented as a historical model-output replay. The positive SQ1 witness uses its saved runtime and PRESENCE mode; it does not invent a missing B-reader prediction.

An additional [26 retained-alias checks](SF7_evidence/retained_alias_checks.json) pass for both variants when the recogniser itself retains the alias. Tests additionally cover all alias characters, missing/shared/separated/extra groups, clipping, uncertainty, recogniser score certification and both presence routes. Unresolved physical grouping HOLDs; arbitrary connected-component counts alone do not authorize quote deletion.

## Historical audit replay

Every one of the **100** saved sf6 labels is first reproduced from the retained overlay evidence. Original labels come from the saved audit inventory; reader, detector and peer fields come only from accepted overlays. No recogniser confidence, peer E prediction or observation field is invented. Input and result hashes are in [audit receipt](SF7_evidence/audit_receipt.json). The [100-line table](SF7_evidence/audit_replay.md) and [complete traces](SF7_evidence/audit_replay.jsonl.gz) expose every outcome.

| Addition rule | Wrong historical releases prevented | Right corrections lost | Right corrections retained | Wrong historical releases retained |
|---|---:|---:|---:|---:|
| A | **5/17** | **8/83** | 75/83 | 12/17 |
| B | **9/17** | **13/83** | 70/83 | 8/17 |

“Fixed” here means a bad sf6 release is prevented, normally by HOLD, not that sf7 emits a verified replacement. The historically unreadable card remains unknown. Several false subscript insertions already have saved detector below-mark ink, so a presence rule does not remove them. These measurements were not used to tune the preregistered rule. This retrospective replay is not the fresh audit or the held-out LQB selection criterion.

**39 cards:** all 39 owner-final cards, covering 36 unique lines, were replayed under both variants using saved held-out detector slots, A/B/E predictions, extractor metadata and the saved native-header observation recovery. Both give 33 card-associated whole-line HOLDs, 5 unchanged and 1 corrected. See [receipt](SF7_evidence/cards39_receipt.json) and [78 outcomes](SF7_evidence/cards39_replay.jsonl.gz). Whole-line status is not card-level correctness.

**Known substitution cost:** `384c3f89-p000059-l0013:s33` has owner truth **ἤγε**. Both sf7 variants release **ἥγε**; sf6 HOLDs because its old psili lacks two positive absences. This newly admitted wrong substitution follows the preregistered reader-alone rule and is retained as a counterexample.

## Tests and local mock

The final focused suite has **963 passed, 0 failed**: all new sf7 rule/audit/card tests, three package regressions, and the unchanged sf6, sf6c and reviewer suites. [Log](SF7_evidence/final_gate_tests.log), [test receipt](SF7_evidence/test_receipt.json).

The complete `tests/labelfix` invocation was also run, unchanged: **1,944 passed, 3 failed**. This broad suite is **not all green**. A separate recheck reproduced the same three failures (11 passed):

1. `test_greekocr_sha256_list_matches_spellcheck` compares the entire library with `ce2f889d…`, while the supplied checkout already includes four added paths under `greekocr/numerics/` (two source files and two tracked bytecode files). Moving the additive sf7 module outside `greekocr/` leaves exactly those inherited differences. The separate 16-path sf6 binding test passes.
2. S8 `test_exact_job_entrypoint_mock` exceeds its unchanged 45-second subprocess timeout.
3. S8 `test_deadline_terminates_inflight_pool` exceeds its unchanged 30-second subprocess timeout.

These unrelated checks were neither weakened nor edited. [Full log](SF7_evidence/all_gate_tests.log), [recheck](SF7_evidence/existing_failures_recheck.log).

The local mock runs **the exact sbatch entry point** with its manifest verification and root/PYTHONPATH setup, two workers and the complete saved 64-line verification population. It was repeated from the **extracted deploy archive**, eliminating ambient-worktree import dependencies. Both A and B reach complete composed overlays, paired controls and manifests, exit 0; the final extracted-archive mock takes about 2 seconds. [Mock log](SF7_evidence/mock_archive_final.log), [receipt](SF7_evidence/mock_receipt.json). A package regression compares required manifest keys and per-wave/source coverage fields with sf6's release schema, verifies output hashes and paired control membership.

```bash
SF7_MOCK_PYTHON=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python \
  bash scripts/labelfix/clariden/sf7_job.sbatch --mock \
  --config config/sf7_mock.json --out /private/tmp/SF7_NEW_MOCK --workers 2
```

## Recomposition and deployment

Inputs remain L1R3 job **3680729**'s exact source population: **124,669 selected polytonic lines**, saved detector/A output `output_3679313`, and saved B/E combined evidence `l1e_20261017/output_3679545/inference`. The original L1R3 final receipt and its input-verification receipt are hash-checked, and the new verified input map must equal the historical map of **8,784 input hashes**. No inference, detector execution, model training or allocation occurs during preparation or recomposition.

The recompose entry point verifies the historical receipt DAG before output, checks per-shard input hashes before and after composition, rejects duplicate/missing/unselected IDs, verifies all output/control membership, and rehashes the input map before writing `complete: true`. Existing source labels and historical run files are never written. Output directories must be new, separate from the historical inputs.

Final root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_20261017`.

```text
output_<JOB>/
  input_verification.json
  shards/shard-NNNNN/{overlay_A.jsonl.gz,overlay_B.jsonl.gz,
    ctrl_subset_A.jsonl.gz,ctrl_subset_B.jsonl.gz,receipt.json}
  release/{overlay_A.jsonl.gz,overlay_B.jsonl.gz,
    release_A.json,release_B.json,release_ctrl_subset_A.json,release_ctrl_subset_B.json,
    ctrl_subset_A.jsonl.gz,ctrl_subset_B.jsonl.gz,kept_A_line_ids.txt,kept_B_line_ids.txt}
  receipt.json
```

The overlays retain the sf6 release schema with `policy`, `variant` and per-line `rule_traces` added. Every historical HOLD/out-of-scope line remains excluded unless the deliberately changed sf7 rule now accepts it; corresponding original-label controls use exactly the same kept IDs. Both candidate files remain separate; this package chooses no winner.

The sbatch script changes to its own root (the fixed final root under Slurm's spool copy), checks the deployment manifest there and exports **PYTHONPATH=root**. It requests account `a0140`, debug, one node/task, 64 CPUs, 32 workers, exclusive, 30 minutes; `srun` is used only for an eventual separately authorized production submission. `--dry-run` runs CPU-only on the login node without `srun`, using two thousand real saved runtime IDs joined to the unchanged full selection.

Two predeployment failures were retained and repaired before final promotion: a missing transitive `greekocr.glyphs` import, and the assumption that selection order equaled shard order. The payload now includes all library Python dependencies; dry-run IDs are selected from numeric runtime shard order and joined by exact ID. Regressions cover both schema/entrypoint execution and mismatched selection/shard ordering. [Import failure](SF7_evidence/failed_predeploy_missing_glyphs.log), [ordering failure](SF7_evidence/failed_predeploy_slice_order.log).

**Final real-input dry run:** exit **0**, **2,000/2,000 unique IDs per variant**, **141.43 seconds**, complete composed A/B outputs and matching original-label controls. Both variants give 10 corrected, 158 unchanged, 1,832 HOLD and 0 out-of-scope lines on this deterministic slice. These are slice results, not full-population yield. The dry run verifies the complete 124,669-line historical input binding before selecting its slice, then rehashes inputs before completing. Its binding equals the final local policy. [Complete dry-run receipt](SF7_evidence/real_input_dryrun_receipt.json), [execution log](SF7_evidence/real_input_dryrun_attempt1.log), [output hash/membership readback](SF7_evidence/dryrun_readback_attempt1.log).

The successful final dry-run directory is `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_20261017/predeploy/20261017T195306Z/dryrun_2000`. It preceded final promotion. An earlier successful dry run was repeated after tightening the legacy HOLD `reason`/`detail` and edit-evidence letter fields; the schema test now asserts those fields. Intermediate evidence is retained under `SF7_evidence/pre_schema_validation/`. Gateway timeouts during the intermediate transfer used at most three transient retries, with no authentication failure or certificate refresh. All final-payload network steps succeeded on their first attempt.

**Final deployment:** **367/367 manifest entries match** remotely, plus a separately verified SHA-manifest envelope. Every deployed path is hashed; unchanged tracked files and new files are treated identically by the manifest. Manifest SHA-256: `373851267da9508e0c3dca360a6ce1cdbb79bde69e61894bf3161618058e483a`. [Package receipt](SF7_evidence/package_receipt.json), [deployment receipt](SF7_evidence/deploy_receipt.json), [remote checks](SF7_evidence/remote_sha_attempt1.log), [envelope check](SF7_evidence/manifest_sha_attempt1.log).

**Scheduler test-only:** `sbatch --test-only scripts/labelfix/clariden/sf7_job.sbatch` exited **0** from the final root. [Exact command/output](SF7_evidence/test_only_attempt1.log). This was a scheduler dry run, not submission. No job ID is asserted as a submitted job.

## Forecast and handoff

L1R3's actual full-population recomposition receipt reports **435.052 seconds (7.25 minutes)** with 32 workers. For two sf7 variants, allow **8–15 minutes after allocation begins**, excluding queue delay; this is a forecast based on that measured predecessor, not a new production timing claim. The 30-minute request leaves room for additional trace output and input verification. The real-input serial login dry run is a correctness check, not a compute-node throughput qualification.

**LEAD COMMIT NEEDED** for the coordinator's committed-source verifier. No staging/commit was performed. Commit exactly the reviewable [lead path list](SF7_evidence/LEAD_COMMIT_PATHS.txt), then run [VERIFY_CMD.sh](SF7_evidence/VERIFY_CMD.sh). It invokes the coordinator's `greek-page-ocr-wave1e/scripts/ops/verify_deploy.py`, as in R2J3. That committed-source verifier was prepared, not claimed as already passed against uncommitted files.

Submit command, prepared **but never executed**; only after separate authorization and successful coordinator verification:

```bash
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_20261017
sha256sum --check SF7_DEPLOY_SHA256.txt
sbatch --parsable scripts/labelfix/clariden/sf7_job.sbatch
```

GC1 READY: sf7 digest f41e05636d16; sf6 reproduction identical yes; audit replay A fixed 5/17 lost 8/83, B fixed 9/17 lost 13/83; SQ1 pair pass; tests 963; dry run exit 0; deployed 367 sha match; test-only ok; lead commit list docs/records/labelfix/spellcheck/SF7_evidence/LEAD_COMMIT_PATHS.txt
