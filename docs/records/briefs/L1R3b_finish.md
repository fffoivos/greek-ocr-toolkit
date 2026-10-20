# L1R3b — Finish the L1R3 package: evidence inventory inside job 2, deploy, test-only (gpt-6.1-sol, xhigh, network ON for Clariden only)

Workspace/rules: as `docs/records/briefs/L1R3_sf6_recompose_job.md` (read it, and `L1R3_REPORT.md`). Head = this commit. **DO NOT SUBMIT.** Gate
frozen (byte-identical to d893a04d). SSH transient errors (connection closed, banner/read timeouts) retry ≤ 3 with backoff per step; auth/cert
STOP; never refresh the cert.

## Change (track lead)
Do not run the evidence-availability scan on the login node. Move `l1r3_evidence.py`'s full-population inventory INTO job 2 (or a job-2
stage that runs first), so the census reports: lines/slots with omitted / null / invalid / explicit recogniser confidence, regional evidence,
image width, and how many pass SF6c's exact certification predicate — per wave. Expected (first records, code history: SF6c added these fields
tonight): ~0% — state that as the expectation, measured by the job. Then: remote deploy, `L1R3_DEPLOY_SHA256.txt` remote vs local, `sbatch
--test-only` for both jobs, exact submit + pull commands.

Update `L1R3_REPORT.md`; last line:
`L1R3 READY: policy sf6-release-v1; gate identical to d893a04d; scored-confidence coverage measured in job 2 (expected ~0% from first records); mock parity <k>/<k>; deploy sha256 <a>/<a>; test-only <j1>/<j2>; est <min> min`.
