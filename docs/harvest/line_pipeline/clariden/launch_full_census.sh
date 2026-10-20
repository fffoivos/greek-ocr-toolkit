#!/usr/bin/env bash
# Superseded launch command; failed job3693052 is preserved.
# Repaired run is already submitted as3693110; see census_02-plan.json.
printf "%s\n" "Already submitted: job 3693110. Inspect Slurm and its ledger; do not submit another census blindly." >&2
exit 1
