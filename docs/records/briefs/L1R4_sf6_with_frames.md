# L1R4 — Recompose under sf6-release-v1 with the L1F recogniser fields joined: Clariden job package (gpt-6.1-sol, xhigh, network ON for Clariden only)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck-l1f`, branch `opus/spellcheck-l1f`, head c79910e9 = SF6c gate + L1R3
package + L1F). No `.git` writes; no other worktree writes. **Gate frozen** (`greekocr/labelfix/*` byte-identical to d893a04d). **DO NOT
SUBMIT**; prepare, mock, deploy, sha-check, `sbatch --test-only`. SSH transient errors retry ≤ 3; auth/cert STOP; never refresh the cert
(expires 19:18 today; stop and report if READY would slip past 18:30).

## Job
Same as L1R3 (jobs 3680729/3680730, `docs/records/labelfix/spellcheck/clariden/L1R3_REPORT.md`): job 1 recompose under sf6-release-v1 into
`…/l1e_20261017/l1r_sf6f_<job1>/`, job 2 censuses + evidence inventory + real mark-correction list (afterok job 1) — with ONE change: before
composing, join L1F's fields (`recognition_confidence`, `recognition_evidence`, `image_width` + provenance) onto each saved runtime record by
`line_id` from L1F job **3680752**'s output (`…/labelfix_l1_20261017/l1f_3680752/`, see `L1F_REPORT.md` for its layout and receipts).
Verify L1F's final receipt first (complete, all shards, alignment identity); lines L1F withheld (e.g. transferred/mismatched identity) keep
the fields MISSING — never default. Report per wave: lines with certified recogniser evidence, and (job 2) real mark-correction lines and
SF6 deletion HOLD by class vs L1R3 — the delta is what the recogniser evidence buys. Write the list of lines that are newly real
mark-corrected vs L1R3 (for their own audit sample).

## Submission chaining
The submit command must chain on L1F: job 1 `--dependency=afterok:3680752`, job 2 `afterok:<job1>`. Mock both on the 64-line verification
runtime joined with L1F's mock outputs (parity with the frozen composer; show the 2 L1F demo lines HOLD → allowed). Tests green; deploy to
`…/labelfix_l1_20261017/l1r_sf6f/`, `L1R4_DEPLOY_SHA256.txt` remote vs local; `sbatch --test-only` for both (test-only may report the
dependency as unresolved — state it).

`docs/records/labelfix/spellcheck/clariden/L1R4_REPORT.md`; last line:
`L1R4 READY: policy sf6-release-v1 + L1F 3680752 fields; gate identical to d893a04d; mock parity <k>/<k>; demo lines allowed 2/2; deploy sha256 <a>/<a>; test-only <j1>/<j2>; est <min> min`.
