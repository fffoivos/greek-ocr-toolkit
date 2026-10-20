# L1R3 — Recompose under sf6-release-v1 (SF6c) + census + deletion census: Clariden job package (gpt-6.1-sol, xhigh, network ON for Clariden only)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck-l1r3`, branch `opus/spellcheck-l1r3`, head 9052b8fd = SF6c d893a04d merged
with the L1R2 package). No `.git` writes; no other worktree writes (the main worktree is under a final Astra pass — read-only). **Gate code
frozen at SF6c** (`greekocr/labelfix/*` must stay byte-identical to d893a04d); change only job/packaging/analysis code. **DO NOT SUBMIT**:
prepare, mock, deploy, sha-check, `sbatch --test-only`. SSH transient errors retry ≤ 3; auth/cert STOP; never refresh the cert (valid to
19:18). Model the package on `docs/records/labelfix/spellcheck/clariden/L1R2_REPORT.md` (jobs 3680629/3680630 ran 7 min + 1 min).

## Do
1. Adapt the L1R2 package to policy `sf6-release-v1` (sha 6f62925a…c406): policy pins in `l1c_census.py`, `l1r2_changes.py`, tests; outputs
   `…/l1e_20261017/l1r_sf6_<job1>/`, deploy dir `…/labelfix_l1_20261017/l1r_sf6/`. 173 labelfix tests currently fail on the merge only
   because of sf5 pins — make all green without weakening.
2. **SF6 evidence availability on the saved L1 runtime (must answer before READY):** SF6c requires an explicitly scored recogniser confidence
   (≥ 0.5, regional provenance) and window-contained spans. Inspect the saved L1-v0/L1E runtime on Clariden (streaming, ≤ a few minutes on the
   login node, else STOP): what fraction of lines/slots carry an explicit score and regional evidence; how missing ones are represented; the
   recompose must treat them as missing (→ no recogniser absence signal), never default. State the expected effect.
3. Job 2 (census + deletion census, afterok job 1) as in L1R2, plus: per mode × wave count of lines held by `sf6:deletion_needs_two_positive_
   absences:*` by class, MOVE exceptions applied, and real mark-correction lines. The 100-line audit will be drawn from job 2's real
   mark-correction list — write that list (line ids, wave) as an output.
4. Mock both jobs on the 64-line verification runtime with parity to SF6c's composer; tests; deploy; `L1R3_DEPLOY_SHA256.txt` remote vs local;
   `sbatch --test-only` for both.

## Deliverables
`docs/records/labelfix/spellcheck/clariden/L1R3_REPORT.md` with the evidence-availability answer, both submit commands (job 2 afterok job 1), pull
commands; last line:
`L1R3 READY: policy sf6-release-v1; gate identical to d893a04d; scored-confidence coverage <x>% lines; mock parity <k>/<k>; deploy sha256 <a>/<a>; test-only <j1>/<j2>; est <min> min`.
