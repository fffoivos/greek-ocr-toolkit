# ASTRA-CENSUS05b — scoped re-review of the census_05 package after the H1 fix (before submission)

ROLE: independent fresh-eyes CERTIFIER (gpt-6-astra); implementer ≠ certifier; verify firsthand; raw numbers; local repository read-only; Clariden read-only over `ssh clariden` (ls, cat, sha256sum, sbatch --test-only only); no background jobs.
SCOPE: only what changed since ASTRA-CENSUS05 (docs/records/reviews/astra_program_review_2026-10-06/ASTRA-CENSUS05_full_report.md, your own prior report): the readout fix and its tests. Everything else certified there stands unless the changed files regress it. The "changes since review" map is in docs/records/harvest/census05/REVIEW_INPUTS.md.
1. [H1] census_readout.py: the protected-crop set is now configured final_policy.heldout_crop_sha256 ∪ dev/test-observed crops ∪ protected editions, mirroring deduplicate(); rerun YOUR witness (review_scratch/ASTRA-CENSUS05/readout_witnesses.py) against the deployed reader at $W/census_05_20261020/code/997b7d2ab5a8775b: it must report 1 leak and a nonzero exit; recount 9,119 configured / 6,904 config-only.
2. [L1] invariant admitted_train_equals_eligible: the empty-export witness fails (nonzero exit).
3. The 154 CODE_SHA files are byte-identical to 3b4090bf9 (recount) and the deploy (178 files) matches DEPLOY_SHA256SUMS; VERIFY_OK ×4; `sbatch --test-only` smoke (debug, 00:30:00) and full (normal, 04:00:00) pass; no debug leftovers in the full sbatch.
4. Anything in the C/D changes that would make the run's outputs unusable for release v3 or the benchmark.
DISPOSITION: BLOCKER/HIGH fixed before submission; MEDIUM/LOW logged. Last line exactly `VERDICT: <one line> | BLOCKERS: <n> | HIGH: <n>`.
