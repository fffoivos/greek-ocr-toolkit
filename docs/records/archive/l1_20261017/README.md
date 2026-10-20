# L1-v0 package (archived 17 Oct 2026, merge of opus/spellcheck-l1 e3a69415)

Coordinator ruling: opus/spellcheck-l1 is merged for its docs only. This directory keeps, at their original
repo-relative paths, the L1-v0 Clariden package that the L1 job ran with. These files are **not live**:
- root deploy receipts L1_DEPLOY_FILES.txt / L1_DEPLOY_SHA256.txt / L1_EXTERNAL_SHA256.txt (they bind the old bytes);
- scripts/labelfix/clariden/{l1_inventory,l1_prepare,l1_run,l1_runtime,l1_verify}.py and l1_job.sbatch
  (l1_prepare/l1_verify no longer import against the SF6c l1_common; l1_run drives l1_verify, l1_detect, l1_infer);
- tests/labelfix/test_l1.py (pre-SF2 runtime schema; 9/11 fail against the live gate; not collected here);
- l1-branch versions of the policy-hashed l1_common.py, l1_detect.py, l1_infer.py. The live paths keep the SF6c
  versions, so release_gate.policy_binding() is unchanged.
