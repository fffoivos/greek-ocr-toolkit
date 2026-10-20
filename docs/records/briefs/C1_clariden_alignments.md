# C1 — Recogniser alignments on Clariden for mark-reader training samples (gpt-6.1-sol, xhigh, network ON)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck-align`, branch `opus/spellcheck-align`). No `.git` writes; leave new files in
the working tree; the track lead commits. Do not touch other worktrees (another Sol run is editing `~/Projects/greek-ocr-toolkit-spellcheck`).
Network ON for ssh/rsync to Clariden only. Local Python: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python` with
`PYTHONPATH=$PWD`. The MacBook is not a bulk worker: local runs ≤ 200 crops (mock test only).

## Why
The mark classifier lacks samples for compound marks (breathing + accent on one vowel, ± subscript): 8 of 12 compound classes have ZERO
fitting samples, yet compound marks are 38% of Google's real mark errors. Free labels exist wherever Google's label and the recogniser agree on
a word, but locating each vowel in the image needs the recogniser's CTC alignment, which we only have for the 1,264 test lines. This task
produces those alignments for the training collection, on Clariden, in one short debug job. It does NOT train anything.

## Inputs
- Recogniser: E3 `full_s0` checkpoint, local copy `~/Projects/greek-page-ocr/out/e3b/jobA/runs/full_s0/best.pt`; the E3 run copies on Clariden
  are documented in `~/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/E3_NOTES.md` / `E3_EXECUTION_STATE.json` (find the Clariden paths,
  environment/uenv and the scratch dir used for E3 there; reuse them, do not build a new environment if E3's works).
- Alignment code: `greekocr/labelfix/ctc_align.py` (`Recognizer(...).align_paths`, `Alignment.to_record`) — produce records in exactly the
  format of `.cache/labelfix/align_s0.jsonl` (`{"crop": <path from docs/records/harvest/... on>, "alignment": ...}`) plus the prediction text.
- Lines: `docs/records/harvest/collection/v2/import_real_v2_train.jsonl` (symlinked; 214,436 rows, 124,669 `greek_poly`). Crops: find them on Clariden
  (E3 staged the collection there); if they are not there, stage only the selected crops (rsync, checksums).
- Selection (write the list and its counts to `docs/records/labelfix/spellcheck/clariden/C1_selection.jsonl` + summary): ALL `greek_poly` train lines
  whose Google label has at least one compound-mark cluster (a breathing and an accent on the same vowel, NFD), plus a seeded random 30,000 of
  the other `greek_poly` lines (seed 20261016). Exclude any line of a held-out Wikisource book or of the v2 test set.

## Rules (read before submitting)
- `~/.claude/skills/optimize-apertus-cscs/SKILL.md`, section "Clariden operating rules": debug partition (`--partition=debug`, confirm live
  limits), one node, wall time ≤ 60 min, account `a0140`. Never `normal`.
- Mock-test the exact job script locally on ≤ 200 crops against the local checkpoint first (same entry point, CPU), and diff its output records
  against `.cache/labelfix/align_s0.jsonl` for any overlapping crop (must match exactly or explain).
- Before `sbatch`: sha256-compare every deployed file (script, code, checkpoint) remote vs local and record it; never edit a script after
  deployment. Run `sbatch --test-only` first.
- CSCS cert: `ssh-keygen -Lf ~/.ssh/cscs-key-cert.pub | grep Valid` (valid to 2026-10-17 19:18). If ssh fails, STOP and report; do not refresh.
- Watch the job to a terminal state (`sacct`), read its log even if it says COMPLETED/FAILED, then rsync the output back (compressed jsonl.gz)
  to `docs/records/labelfix/spellcheck/clariden/` (or `.cache/labelfix/` if > 100 MB, with a manifest + sha256 in docs).
- Report the job id and state in the first line of `C1_REPORT.md` as soon as it is submitted (append updates).

## Deliverables
`scripts/labelfix/clariden/` (job script + selection + runner), `docs/records/labelfix/spellcheck/clariden/C1_REPORT.md` (job id, state, wall time,
lines aligned, failures, sha256 receipts, mock-test diff, counts of compound clusters by class among agreeing words), the alignments file, and
a last line: `C1 RESULT: job <id> <state>, <n> lines aligned in <min> min; agreeing compound clusters by class: …; output <path> (<size>)`.

## Do not
Train or evaluate models; use `normal`; exceed one debug job (one resubmission allowed after a script fix, with the reason); copy data other than
the selected crops; touch the test instruments or Google labels.
