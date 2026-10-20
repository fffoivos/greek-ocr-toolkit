# L1R — Recompose L1 releases under sf4-release-v1 on Clariden: scripts, mock, deploy check (gpt-6.1-sol, xhigh, network ON for Clariden only)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck-l1r`, branch `opus/spellcheck-l1r`, head 47f7b6b0 = SF4 + verification brief).
No `.git` writes. Do NOT touch `~/Projects/greek-ocr-toolkit-spellcheck` (an Astra verification pass is reading it; any write there voids it).
Local Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`. The Mac runs the 64-line mock only;
NO bulk transfer of L1/L1E evidence to the Mac (manifests/overlays only, tens of MB). **DO NOT SUBMIT**: prepare, mock, deploy, sha-check,
`sbatch --test-only`; the coordinator submits after the verification pass. SSH: transient errors retry ≤ 3 with backoff; auth/cert errors STOP;
never refresh the cert (valid to 17 Oct 19:18). Read `~/.claude/skills/optimize-apertus-cscs/SKILL.md` "Clariden operating rules".

## Job
One debug job (a0140, one node, CPU, ≤ 1 h, aim ≤ 20 min), code = this commit's SF4 gate (`greekocr/labelfix/release_gate.py`, policy
`sf4-release-v1`), entry point `scripts/labelfix/clariden/l1r_recompose.py` (extend only as needed: multiprocess over shards, receipts):
- **Inputs, read in place** under `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/`: L1-v0 `output_3679313/` (detector shards,
  A predictions, coverage) and L1E `l1e_20261017/output_3679545/` (B/E predictions + coverage, receipts). Verify every input against its
  receipt hashes first; if 3679545 did not complete its own recomposition, that does not matter (inference outputs are what we use); if B/E
  inference is incomplete for any shard, STOP and report.
- **Outputs**, written beside L1E's: `l1r_sf4_<jobid>/` with releases `v2-corrected-presence-sf4`, `v2-corrected-full-sf4`,
  `v2-corrected-ensemble-ab-sf4` (overlays + kept lists) and the matching ctrl-subset releases; per-wave/per-source coverage; exclusion receipts
  (as L1); original-label sha per line; HOLD lines excluded; code/policy/checkpoint/input hashes; the ensemble caveat VERBATIM in every manifest:
  "A and B share training data (C1 agreement labels) and therefore share errors; agreement measures the reader's stability, not an independent
  pixel signal. Precision on the training waves is unmeasured until the training-wave DEV with print truth exists. Wave 1c on this release is a
  pseudo-label experiment." Per-shard receipts so a timeout leaves results; L1-v0 and L1E outputs are never modified.
- Runtime: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python` (assert its scipy manifest).

## Before submission (you do these)
1. Mock: the exact entry point on the complete saved **64-line verification runtime** (see `docs/records/labelfix/spellcheck/SF4_evidence/` and the
   L1E mock64), with parity to SF4's local full-composer check (all mode/line and slot/mode decisions identical); release-format validation.
2. Tests (all labelfix green). 3. Deploy to `…/labelfix_l1_20261017/l1r_sf4/`, `L1R_DEPLOY_SHA256.txt` remote vs local. 4. `sbatch --test-only`.

## Deliverables
`docs/records/labelfix/spellcheck/clariden/L1R_REPORT.md` (inputs verified, mock parity, estimate, deploy sha list, test-only output, exact submit command),
last line: `L1R READY: policy sf4-release-v1; inputs verified <ok>; mock parity <k>/<k>; deploy sha256 <a>/<a>; test-only <output>; est <min> min`.
