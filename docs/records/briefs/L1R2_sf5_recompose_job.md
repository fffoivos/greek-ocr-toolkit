# L1R2 — Recompose under sf5-release-v1 + census + deletion census: Clariden job package (gpt-6.1-sol, xhigh, network ON for Clariden only)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck-l1r2`, branch `opus/spellcheck-l1r2`, head 39f7dedd = SF5 05f2dafb
(verification pass CLOSED) merged with the L1R/L1C package from `opus/spellcheck-l1r`). No `.git` writes; no other worktree writes. **The gate
code is frozen at SF5** — do not change `greekocr/labelfix/release_gate.py`, `text.py`, `reading.py` or the composer semantics in
`l1_common.py`; only job/packaging/analysis code. **DO NOT SUBMIT**: prepare, mock, deploy, sha-check, `sbatch --test-only`. SSH transient
errors retry ≤ 3; auth/cert STOP; never refresh the cert (valid to 19:18). Read `~/.claude/skills/optimize-apertus-cscs/SKILL.md` and
`docs/records/labelfix/spellcheck/clariden/L1R_REPORT.md` + `L1C_REPORT.md` (the previous, successful packages: job 3679725 ran 7 min; L1C 33 s).

## Job 1 — L1R2 recompose (as L1R, policy sf5-release-v1)
Same inputs as L1R (L1-v0 `output_3679313/`, L1E `l1e_20261017/output_3679545/`, verified against their receipts), same entry point
`scripts/labelfix/clariden/l1r_recompose.py`, outputs `…/labelfix_l1_20261017/l1e_20261017/l1r_sf5_<jobid>/` (beside L1R's sf4 outputs,
which stay untouched and are marked NOT USABLE by the coordinator). Releases `v2-corrected-{presence,full,ensemble-ab}-sf5` + ctrl-subsets;
manifests carry `alias_only` counts, the elision census, and the ensemble caveat verbatim.

## Job 2 — census (afterok Job 1), analysis only
(a) The L1C per-wave HOLD census (update its policy checks `l1c_census.py:161,190` to accept sf5-release-v1 — no other logic change).
(b) **Deletion / change census of every corrected line** (coordinator ruling), per mode × wave: label diff original v2 label vs released
label (NFD, `difflib`, as in `~/Projects/greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/L1A_AUDIT_REPORT.md`), classifying every
edit: real combining-mark change; elision alias (word-final AND word-initial aliases such as ᾿στὸν → 'στὸν count as aliases, not corrections);
consensus elision deleted (must be 0); **single-source deletions by character class — numeral keraia (U+0374/U+0384/U+02B9 or an apostrophe
after a numeral letter such as Ι'), elision apostrophe, quote (incl. opening quotes, cf. ASTRA-SC1c3v2 note), other mark**; insertions by class.
Report lines and edits per class and the share of corrected lines with any single-source deletion; list up to 20 example ids per class.
Line counts: corrected lines with ≥ 1 real mark change ("real mark-correction lines") — this is the number reported from now on.

## Before submission
Mock both jobs on the 64-line verification runtime (as L1R did) with parity to SF5's full composer (`scripts/labelfix/sf5_measure.py`) on all
mode/line and slot decisions; synthetic fixture for the deletion census incl. one keraia, one quote, one alias, one consensus elision; tests
(all labelfix green); deploy to `…/labelfix_l1_20261017/l1r_sf5/`, `L1R2_DEPLOY_SHA256.txt` remote vs local; `sbatch --test-only` for both.

## Deliverables
`docs/records/labelfix/spellcheck/clariden/L1R2_REPORT.md` with both submit commands (job 2 with `--dependency=afterok:<job1>`), pull commands for
the manifests/census; last line:
`L1R2 READY: policy sf5-release-v1; inputs verified <ok>; mock parity <k>/<k>; deploy sha256 <a>/<a>; test-only <job1>/<job2>; est <min> min`.
