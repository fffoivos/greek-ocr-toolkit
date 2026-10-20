# L1F — Recogniser frame evidence for the 124,669 polytonic training lines: Clariden GPU job package (gpt-6.1-sol, xhigh, network ON for Clariden only)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck-l1f`, branch `opus/spellcheck-l1f`, head = SF6c + its CLOSED pass 4
(90bcc286) merged with the L1R3 package). No `.git` writes; no other worktree writes. **Gate frozen**: `greekocr/labelfix/release_gate.py`
and the SF6c certification code (`ctc_align.py` recognition_fields / recognition_evidence) are used as-is, byte-identical to d893a04d — this
job only PRODUCES the fields SF6c consumes. **DO NOT SUBMIT**: prepare, mock, deploy, sha-check, `sbatch --test-only`; the coordinator
submits. SSH transient errors retry ≤ 3 with backoff per step; auth/cert STOP; never refresh the cert (valid to 19:18 today — the package must
be READY well before; if it would slip past ~18:30, stop and report). Read `~/.claude/skills/optimize-apertus-cscs/SKILL.md` "Clariden
operating rules" and the previous successful packages (`docs/records/labelfix/spellcheck/clariden/L1_REPORT.md`, `L1E_REPORT.md`, `L1R2_REPORT.md`).

## Why (coordinator, 17 Oct)
SF6c accepts recogniser absence only with an explicitly scored confidence (> 0.5) and regional frame evidence covering the detector window
(`recognition_confidence`, `recognition_evidence`, `image_width`). The saved L1-v0/L1E runtimes omit these keys (SF6c added them tonight), so
on the training lines the gate is reader+detector only. This job produces them; the recompose then re-runs as L1R4 with the fields present.

## Job
- Inputs: the same 124,669-line selection and crops as L1-v0 (`labelfix_l1_20261017/output_3679313/`, its input receipts and selection), the
  E3 recogniser checkpoint `full_s0` exactly as L1 used it (same codec, same preprocessing, same alignment code), and L1-v0's saved detector
  slots (the windows the regional evidence must cover). Verify every input against its receipt first.
- Per line: run the E3 CTC forward pass, keep the per-frame max posteriors (`frame_confidences`), the line confidence, and compute
  `recognition_evidence(slots, image_width)` with the frozen `ctc_align.Alignment` code; record `image_width` (native). Check that the
  recogniser text/alignment identity matches L1-v0's saved alignment for the same line (SF6c binds evidence to the alignment it came from);
  report mismatches and never silently replace the saved text.
- Output: `…/labelfix_l1_20261017/l1f_<jobid>/` — per-shard JSONL keyed by `line_id` with exactly those fields + provenance (checkpoint sha,
  code sha, alignment identity hash), per-shard receipts, a final receipt with coverage per wave (lines scored, slots with regional evidence,
  lines failing the SF6c predicate and why). Never modify L1-v0/L1E/L1R outputs.
- Resources: debug partition, a0140, GPU (one node, 4 GH200), ≤ 1 h wall (estimate from L1's alignment throughput; if > 1 h, split into
  ≤ 1 h array tasks with per-shard resume). Runtime: the E3 venv used by L1 (unchanged) — state which; no new installs.

## Before submission
64-line mock on the verification runtime with the exact entry point (CPU is fine for the mock), verifying the three fields are present,
scored, regionally certified where expected, and that feeding them to SF6c's `recognition_fields` makes recogniser absence available on those
lines (show 2 lines where a deletion moves from HOLD to allowed and 2 where it stays HOLD). Tests (all labelfix green). Deploy to
`…/labelfix_l1_20261017/l1f/`, `L1F_DEPLOY_SHA256.txt` remote vs local, `sbatch --test-only`.

## Deliverables
`docs/records/labelfix/spellcheck/clariden/L1F_REPORT.md` with the submit command, pull command (receipts only), and the L1R4 note (how the recompose
joins these fields by line_id); last line:
`L1F READY: E3 full_s0 frame evidence for 124,669 lines; mock fields verified <k>/64; alignment identity <ok>; deploy sha256 <a>/<a>; test-only <output>; est <min> min GPU`.
