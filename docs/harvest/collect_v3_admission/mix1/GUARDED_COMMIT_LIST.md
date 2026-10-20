# Guarded MIX1D commit list — review only

Do not run git add or git commit. Proposed scope is exactly DEPLOY_FILES.txt
under docs/harvest/collect_v3_admission/mix1/, plus DEPLOYMENT.json, plus the
user-supplied docs/briefs/MIX1D_a12_source_custody.md after inspecting its diff.
DEPLOYMENT.json is excluded from the deployment allowlist to avoid a digest
cycle. Never use git add -A, git add . or broad directory staging.

Review groups:
1. custody.py, crosscheck.py, export.py, pipeline.py, sample.py, generate.py,
   run.py, test_mix1.py and sbatch display names; source/codec and full-chain gates.
2. reference/mix1c/export.py and pipeline.py: immutable predecessor evidence,
   used only to prove real-pool function equivalence and retain the round trip.
3. Current source bindings, 70-input real-sample receipt, fresh sample, GT sample,
   audit, cross-check receipts, test log/receipt, package and deploy manifests,
   loader contract, MIX1.md, this list and deployment readback attestation.

Before any separately authorized staging, inspect each diff against the base.
Require 52 tests passed, old_v2 audit 287 equal with the same per-source ledger,
1122 GT-equal sample rows across 51 shards, pre-export cross-check success,
unchanged real-pool functions and retained 1000-row evidence, all deployed SHAs
read back, and remote VERIFY package + inputs + crosscheck-a12 success.
Full-chain and post-export derivative equality are enforced future job gates;
do not claim they already ran. Preserve all arm arithmetic/filter rules.

New root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/scaling_w3/mix1_pkg/8d25940f`.
Do not submit e87b9e8d, f1384fdb or any earlier package. Preserve them in place.
Exclude all unrelated dirty/untracked files, pycache, MIX1D_PROBE.json and scratch
probe scripts. No staging, commits, jobs, spend or source dataset mutations.
