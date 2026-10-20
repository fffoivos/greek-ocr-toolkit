# L1 — Corrected-label overlays at scale: scripts, mock, deployment check (gpt-6.1-sol, xhigh, network ON for Clariden only)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck-l1`, branch `opus/spellcheck-l1`, head efdf5756 = the S6/SF1 detector
state). No `.git` writes. Do not touch other worktrees (S7 is running in `~/Projects/greek-ocr-toolkit-spellcheck`). Local Python:
`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`. The MacBook is not a bulk worker: local
runs = the 192-line mock only. **DO NOT SUBMIT A JOB**: prepare, mock, deploy, sha-check, `sbatch --test-only`; the coordinator submits.

## Read first
- The approved outline: `docs/records/labelfix/spellcheck/clariden/L1_corrected_labels_outline.md` (input, system, outputs, ctrl-subset rationale).
- R1's Clariden scripts and receipts style: `scripts/labelfix/clariden/r1_*.py`, `r1_job.sbatch`, `docs/records/labelfix/spellcheck/clariden/R1_REPORT.md`;
  C1's alignment job: `scripts/labelfix/clariden/c1_*.py`, `c1_job.sbatch`, `docs/records/labelfix/spellcheck/clariden/C1_REPORT.md`.
- The combined system as run locally: `scripts/labelfix/m2_run.py` (recogniser spans → S6 `reading.read_ink` → R1-A names on the R1 font-size
  windows → K1 print-preserving flags → PRESENCE and FULL agreement), `scripts/labelfix/agreement_mode.py`, `greekocr/labelfix/reading.py`.
- `~/.claude/skills/optimize-apertus-cscs/SKILL.md` "Clariden operating rules" before touching the cluster.

## Coordinator's rulings (binding)
- Detector version is a PARAMETER (`--detector s6` now; `s7` later re-runs as L1b under the same discipline, releases
  `v2-corrected-presence-s7` / `-full-s7`). This run: S6 = the code at efdf5756, hash-bound.
- One job, debug partition, one node, account a0140, ≤ 1 h (estimate ~25–35 min). Steps: (1) C1-style alignment of the 33,200
  greek_poly train lines not in C1 (reuse the C1 code path and staged crops; write the new selection + inventory receipts);
  (2) detector on CPU across the node (many worker processes); (3) R1 window extraction + R1-A inference on GPU (checkpoint
  `~/Projects/greek-ocr-toolkit-spellcheck-r1/artifacts/labelfix_r1/output_3678928/A/best.pt`, sha 719a06…; already on Clariden under
  `labelfix_r1_20261016/output_3678928/A/`); (4) composition of both variants + receipts. Save per-step receipts so a timeout leaves results.
- **Input:** every `greek_poly` row of `docs/records/harvest/collection/v2/import_real_v2_train.jsonl` (124,669: round1 43,869, parliament 27,224,
  vouli 23,088, round2 17,026, mixed 13,227). Monotonic lines (`greek_mono`) and every other script class are OUT OF SCOPE — state it in the
  manifest with counts.
- **Exclusion receipts** (counts, must be 0): the 666 held-out lines, the 3 DEV and 27 non-DEV Wikisource books, v2_test, wikisource_human,
  e1_real_test (as in R1's receipt). The locked R0 fresh-book set is not drawn yet: write `L1_input_documents.txt` (every input doc id)
  and state in the manifest that R0 must draw only from documents outside it (R0 will publish its zero-intersection receipt against it).
- **Outputs**, per variant (`presence`, `full`), keyed by line_id, exactly as the outline: `overlay_<variant>.jsonl.gz` (line_id,
  original_label_sha256, status corrected|unchanged|hold|out_of_scope, label, changes with evidence, hold_slots with reasons
  kind_disagreement|k1_flag|localisation_unknown|recogniser_letter_problem, detector_version, r1_sha, policy_sha) and
  `release_<variant>.json` (release name `v2-corrected-presence` / `v2-corrected-full`, overlay + source sha256, counts by status, **coverage
  per wave and per source**, exclusion receipts, out-of-scope statement, code commit). HOLD lines are dropped from the corrected release;
  also emit `release_ctrl_subset_<variant>.json` = the same kept line_ids with their ORIGINAL labels (the ctrl-subset arm). Original label
  files are never modified.
- **SciPy:** the detector imports the SciPy image stack (`greekocr/glyphs/components.py`); C1 avoided it because the E3 venv may lack it.
  Check on Clariden what is importable (E3 venv; else the confirmed `uenv run pytorch/v2.6.0:v1 --view=default`). If neither has SciPy, STOP
  and report (no package installation).

## ATTEMPT 2 (17 Oct ~01:20) — SciPy runtime: coordinator authorised option A, with these constraints (binding)
Attempt 1 stopped correctly: no SciPy in the E3 venv or in uenv pytorch/v2.6.0:v1, pytorch/v2.9.1:v2, prgenv-gnu/26.3:v1
(`docs/records/labelfix/spellcheck/clariden/L1_REPORT.md`, `L1_remote_runtime.txt`). Now:
1. **Never modify the E3 venv** (`/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv`; wave 1b/1c binds to it). Build
   `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1` as a separate directory: a copy of the E3 venv (`cp -a`, then fix the
   pyvenv.cfg/activate/shebang paths) or a fresh venv from the same base interpreter with the E3 requirements; then
   `pip install scipy==1.17.1` pinned, and NOTHING else. Before and after: sha256 of the E3 venv's file list must be unchanged.
   Record `pip freeze`, the base interpreter path and the venv path in `L1_runtime_receipt.json`; write a sha256 manifest of
   `venv_l1/.../site-packages/scipy` so later jobs can assert it.
2. **Parity gate in the job:** before touching any training line, run the detector (and the full combined composition) on 32 held-out
   instrument lines on the node; readings and HOLD decisions must be byte-equal to the local ones (ship the local expected outputs with
   the deployment); write `parity_receipt.json`; on any difference the job stops with a clear message and no L1 outputs.
3. If `pip install` fails on the login node for network reasons: STOP and report. No proxies, no alternative indexes.
Detector step runs in venv_l1; alignment and R1 steps may stay in the E3 venv (or venv_l1, which contains it) — state which.

## Before the coordinator submits (you do these)
- Mock: the EXACT job entry points on 192 lines on the Mac CPU (include ≥ 32 held-out instrument lines run in a separate verification mode,
  NOT as L1 input, to prove the outputs equal the local combined reading used in M2/CN1 — byte-identical readings/HOLD decisions), plus
  overlay/release generation. Log to `docs/records/labelfix/spellcheck/clariden/L1_mock.log`; print per-line timings for detector and R1.
- Tests `tests/labelfix/test_l1.py` (status logic, ctrl-subset equality of line sets, exclusion failure on a planted overlap, out-of-scope
  monotonic, original labels untouched). All labelfix tests green.
- Deploy to `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/`; verify all needed crops are staged (C1 inventory + the
  33,200; no crop transfer unless missing — then STOP and report); `L1_DEPLOY_SHA256.txt` remote vs local; `sbatch --test-only`.
- CSCS cert: `ssh-keygen -Lf ~/.ssh/cscs-key-cert.pub | grep Valid` (valid to 2026-10-17 19:18). If ssh fails, STOP; never refresh.

## Deliverables
`scripts/labelfix/clariden/l1_*.py` + `l1_job.sbatch`, tests, `docs/records/labelfix/spellcheck/clariden/L1_REPORT.md` (inputs, exclusions, mock
parity, timings + wall-clock estimate, SciPy runtime used, deploy sha list, test-only output, the exact submit command), last line:
`L1 READY: mock ok (<n> lines, parity <k>/<k>); input 124669 greek_poly (out of scope <m>); exclusions all 0; runtime venv_l1 (scipy 1.17.1, E3 venv unchanged); in-job parity gate 32 lines; deploy sha256 <a>/<a>; test-only <output>; est <min> min`.
