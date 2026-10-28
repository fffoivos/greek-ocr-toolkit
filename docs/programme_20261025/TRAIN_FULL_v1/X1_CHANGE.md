# Standard ×1 and drawn-line loss cadence — focused review

Current payload `385856ea2166d9314d65b67cb0380ba4449e80260101a7f787d95b97638faf16` (ID `385856ea2166d931`), parent `0446ee734d2c867cda056973ce5052f917865f1f53ecc6c2b8301c99d437280f`. [Verbatim brief](OWNER_X1_CORRECTION.md), [current plan/complete recipe](PLAN.md), [exact source diff](evidence/X1_SOURCE.diff), [inventory](evidence/X1_DIFF_INVENTORY.json), [tests](evidence/TESTS_X1_RELEASE.xml).

Changed parent files: `compare.py`, `full_hook.py`, `readout.py`, `recipe.json`, `reuse_audit.py`, `run.py`, `segment.py`, `tests/mock_worker.py`, `tests/test_launch_fix.py`, `verify.py`. Added files: `loss_cadence.py`, `loss_journal.py`, `s1_w1_timing.json`, `tests/test_x1.py`, `x1_parent_payload.json`, `x2_recipe.json`. No parent file was removed.

Model width2→1 in recipe; every other explicit ×1 S1 parameter is unchanged apart from inherited data/full-pass horizon adaptations. Full CER archives stay at 50k/100k/150k/198,312updates. Added loss-only actual-draw cadence50000+final, exact shuffled-tail preflight, journal/pending-eval recovery, smoke2/4/6 with forced requeue3, synchronized smoke-only update timing, and measured254-eval overhead forecast/options. No full-loop/model/optimizer/scheduler/sampler/scorer/native factory changes. `vendor/` and sbatch/runtime scripts are byte-identical to the parent, including SLURM_TIME_FORMAT fix.

Audit/prepared runtime005 are reusable without rewriting only after `verify.data_compatibility()` and exact runtime SHA `21b92bdf2ca2740ee9f3f431a0f79288dc598f40df64a1a49a08f635d9b8b0a4`. Old scientific smoke and reviews are refused; fresh ×1 controls/outputs are mandatory. The cancelled ×2 state is evidence, never a donor/resume source. Preserve all 52,847 harvest-test rows:52,846 is their unique-crop count, not the instrument denominator. Tests assert the retained runtime's exact counts.

Astra review must certify width1, actual-draw cadence254points, RNG/mode/trajectory isolation, loss-only no decoding, complete instrument counts, immutable/journal recovery, unchanged data proof, actual CUDA restart BIT_IDENTICAL, and complete measured overhead/options. The test artifacts prove CPU/mock behavior only. Coordinator supplies real smoke and exact new review; Sol does not assert or fabricate either.

TRAIN_X1 READY (pending fresh CUDA smoke/Astra/owner go).
