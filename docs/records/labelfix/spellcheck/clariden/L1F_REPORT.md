# L1F — E3 recogniser frame-evidence job package

**READY for coordinator submission. No job submitted.** Final verification: 2026-10-17T06:51:55+03:00. The 124,669 training lines have been receipt-verified in place; their GPU forward pass remains for the coordinator's job. The exact sbatch entry point passed its real 64-line CPU mock, all **1,535 labelfix tests pass**, 351/351 deployed files match, and `sbatch --test-only` passed.

Workspace: `greek-ocr-toolkit-spellcheck-l1f`, branch `opus/spellcheck-l1f`, starting HEAD `9cc91746`. No Git writes or other-worktree writes. Network use was limited to Clariden SSH/SCP, with up to three retries and bounded backoff for transient transport errors, immediate stop for authentication/certificate failures, and an 18:30 Athens stop check. No certificate renewal or environment installation occurred. The inspected certificate expires at 19:18:52 Athens today.

Read the requested [Clariden operating rules](/Users/foivoskarounos-zamparloukos/.claude/skills/optimize-apertus-cscs/SKILL.md), [L1E report](L1E_REPORT.md), [L1R2 report](L1R2_REPORT.md), and the supplied L1R3 package. `L1_REPORT.md` was absent from this worktree, the original spellcheck worktree and the original deployed L1 directory. The original L1 sbatch/orchestration, checkpoint binding, inventories and completed alignment/run receipts were inspected directly instead: [original job code](L1F_evidence/l1_original_code.log), [input metadata](L1F_evidence/input_metadata.log).

## Frozen science and identity

These complete files remain byte-identical to `d893a04d`:

| File | SHA-256 |
|---|---|
| `greekocr/labelfix/release_gate.py` | `9ef1d6467229e86c9464f428716c792f2a6fc4ffa1e709b798df82c504120408` |
| `greekocr/labelfix/ctc_align.py` | `3ecb1a208918fdc33b897c00c1848456a9480946a17fb88f7d9f5f400a646068` |

The original L1 model, codec, safe checkpoint loader and CER/codec reader also match the current deployed bytes. AST comparisons establish identical preprocessing, greedy span construction, model initialization, path batching and forward/logit/posterior computation. The only forward-return difference is retaining the already-computed per-frame maximum posteriors. [Original forward hashes](L1F_evidence/original_forward_hashes.log), [equivalence check](L1F_evidence/forward_equivalence.json), [protected files](L1F_evidence/protected_unchanged.json).

The checkpoint is E3 `greek-page-ocr/out/e3b/jobA/runs/full_s0/best.pt`, exactly as L1 used it:

- PT SHA-256: `5f300fdac73d7479769c98e27d068039186ac193c6c4002ddfc8be511d363663`.
- Inference safetensors sibling: `e468155d6130be4b7359d94ec197a357ad55b0dc7947104afc1336c352a6c6df`.
- Codec: `d1b7e2d40565e89e699f748692265e06e2d7028409b78d02d6df6f89b2e82a86`.

The unchanged production interpreter is `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python`: Python 3.12, Torch `2.11.0+cu128`, CUDA `12.8`, SciPy `1.17.1`, NumPy `2.5.4`, Pillow `12.3.0`. The existing 2,398-entry SciPy manifest passed in place; no packages were installed or changed. [Runtime readback](L1F_evidence/remote_readback/preflight/runtime.json).

## Inputs verified before inference

Final deployed `--verify-only` completed in **141.225 s** with no image decoding or recogniser execution. It verified **6,842 receipt-bound input files**, including the complete historical run/step/detector/A-inference DAG, both original alignment sources and their selections, source labels, checkpoint files and the crop-inventory receipt. It then checked **124,669/124,669 native crops**, **4,407,724,367 bytes**, against their individual inventory SHA-256 values. The input map digest is `7b34a352d0a79d65739cd6ece7844fd268e6357fc2a9a0dfa3c48ba087de24d3`; the crop map digest is `5258aa5e83f8eec2d3f61f74c781a10d87950a768aff0cdf5c51bceb3577d859`.

[Production config](../../../../../config/l1f_job.json), [complete input-verification receipt](L1F_evidence/remote_readback/preflight/verified_inputs/input_verification.json), [verification log](L1F_evidence/remote_readback/preflight/input_verification.log), [external SHA list](L1F_evidence/L1F_EXTERNAL_SHA256.txt).

The population is L1-v0 `output_3679313/`: **974 detector shards**, using the exact L1 selection. Its waves are round1 43,869; vouli 23,088; round2 17,026; parliament 27,224; openarchives 235; mixed 13,227. The 235 openarchives rows remain included.

Original alignment sources are C1 job 3678590 (**91,469 lines**) and L1's remaining alignment pass (**33,200 lines**). Each source's original selection order, `rank::4` assignment, 512-line chunks, stable aspect-ratio sort and 16-line batches are preserved. This produces **248 inference-context output shards**, which do not share detector-shard numbering. Saved alignment and detector records are joined through crop keys and selection line IDs, with duplicate/missing/unselected membership rejected.

## Entry point, output and restart

[`l1f_run.py`](../../../../../scripts/labelfix/clariden/l1f_run.py) repeats the complete verification before creating its plan. Each worker hashes the exact crop bytes it decodes, calls the unmodified `Recognizer.align_batch`, and computes native-width regional evidence with the frozen `Alignment.recognition_evidence(slots, image_width)`.

Each JSONL row has exactly `line_id`, `recognition_confidence`, `frame_confidences`, `recognition_evidence`, `image_width`, and `provenance`. Provenance includes both checkpoint hashes, the code-map digest, input-binding digest, and saved/fresh alignment identity hashes. Identity compares **prediction, valid-frame count, scale, strip width and every saved pixel-rounded span**. Newly measured confidence/posteriors are excluded from geometric/text identity. SF6c separately hashes the complete fresh scored alignment in `recognition_evidence.alignment_sha256`.

Any text/geometry mismatch or transferred saved alignment is reported per line. Raw model scores remain available for audit, while regional evidence becomes `scored=false`, `provenance=alignment_identity_mismatch`, `regions=[]`. Saved text is never replaced or transferred onto fresh frames. Such rows cannot certify recogniser absence.

```text
.../labelfix_l1_20261017/l1f_<actual_JOB_ID>/
  input_verification.json, binding.json, code_sources.json
  plan.sqlite, plan_receipt.json
  shards/shard-NNNNN/{frames.jsonl.gz,receipt.json}
  receipt.json
```

The final receipt seals every shard hash and exact line-ID coverage. Per wave it reports lines scored, score-floor coverage, regional/certified slot counts, identity mismatches, lines with certified slots, lines with any failing SF6c slot, and distinct line/slot failure counts by reason. Failure categories include identity mismatch, low line score, missing/out-of-bounds frame coverage, low regional minimum, and source-locator/window contract failure. These are recogniser-predicate counts; physical cleanliness and the rest of the frozen deletion gate still apply.

Atomic sealed shards resume only under the same input/config/code binding; corrupted shards fail. A timeout before the final seal can reuse completed shards. The exact prior output directory can be supplied via `L1F_RESUME_OUT`; no L1-v0, L1E or L1R output is written.

## Real 64-line mock and deletion witnesses

The complete prior saved verification runtime was copied only after matching SF4's pinned SHA-256. The native verification crops and the same E3 checkpoint were used for a real CPU forward pass. The Mac's existing Python 3.11 verification environment has Torch 2.14.1; production retains the E3 environment above. [Fixture binding](L1F_evidence/mock_input_binding.json).

```bash
L1F_MOCK=1 \
L1F_PYTHON=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python \
L1F_CONFIG=config/l1f_mock.json \
L1F_OUT=artifacts/labelfix_l1f/mock_verified \
bash scripts/labelfix/clariden/l1f_job.sbatch

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B \
  scripts/labelfix/clariden/l1f_mock_check.py --config config/l1f_mock.json \
  --out artifacts/labelfix_l1f/mock_verified \
  --evidence docs/records/labelfix/spellcheck/clariden/L1F_evidence/mock_verification.json
```

Use a new mock output path for a fresh run; the retained path demonstrates exact-binding resume. [Exact sbatch mock log](L1F_evidence/mock_verified.log), [independent verification](L1F_evidence/mock_verification.json), [mock receipts](L1F_evidence/mock_receipts/receipt.json).

| Check | Result |
|---|---:|
| Three consumer fields present; actual finite frame/line scores and native widths checked | 64/64 |
| Fresh versus saved text/geometry identity | 62/64 exact |
| Incompatible transferred verification records withheld | 2/2 |
| Regions generated from actual overlapping frames | 1,777/1,905 slots |
| Frozen SF6c `_recogniser_scored` true after `recognition_fields` join | 1,704/1,905 slots |
| Natural deletion checks becoming allowed | 11 |
| Natural deletion checks remaining HOLD | 87 |

The two verification-runtime texts differing from their source cached alignments are `177b717d-p000097-l0007` and `51fe7386-p000024-l0015`. The mock reconstructs those transferred records explicitly and verifies their refusal. All 62 exact matches reproduce the entire frozen evidence object, including its complete alignment hash, from the saved geometry plus new measured frame scores. Production alignment identity remains to be measured by the GPU job.

| Verification line / deleted atom (original NFD offset) | Before → after | Evidence |
|---|---|---|
| `384c3f89-p000059-l0023`, acute U+0301 at 25 (`γήρυς → γῆρυς`) | HOLD → allowed; whole line corrected | reader=true, detector=false, recogniser=true |
| `384c3f89-p000096-l0031`, psili U+0313 at 35 (`ἔθεν → ἕθεν`) | HOLD → allowed; whole line corrected | reader=true, detector=false, recogniser=true |
| `384c3f89-p000053-l0028`, psili U+0313 at 1 | HOLD → HOLD | saved window `[-9,54]` begins outside the native image |
| `384c3f89-p000121-l0024`, dasia U+0314 at 2 | HOLD → HOLD | unnamed detector mark, kind disagreement and K1 flags |

For both allowed examples, adding native width alone still leaves the deletion held. The extra scored recogniser absence is necessary. The whole-line status is stated separately because an allowed deletion does not generally resolve other slot HOLDs. [All four actual before/after checks](L1F_evidence/mock_verification.json), [remaining-HOLD explanations](L1F_evidence/mock_hold_explanations.json).

**1,535 passed in 13.89 s**, no skips/deselections/errors. The fresh worktree lacked the three frozen SF5 baseline test-source fixtures; they were restored byte-for-byte from `05f2dafb`, with equality to the prior package checked. Active policy files and existing tests were unchanged. New tests cover identity mismatch, transferred locations, low regional scores despite a high line mean, native bounds, exact resume after aggregation interruption, output corruption and pre-forward crop corruption. [Final test log](L1F_evidence/tests_labelfix_final.log), [fixture restoration](L1F_evidence/test_fixture_restoration.json), [new tests](../../../../../tests/labelfix/test_l1f.py). Both shell scripts pass `bash -n`; `git diff --check` passes.

## Deployment, resources and scheduler simulation

Deployed root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1f/`.

**351/351** files pass SHA checks before and after test-only. The remote/local `L1F_DEPLOY_SHA256.txt` bytes are identical; manifest SHA-256 is `95d0170693f55eeb5fc05871e7b242829434a0714dfc5b8262e2d308844cc98d`. Every local source-map entry matches the deployed manifest. [Deploy list](L1F_evidence/L1F_DEPLOY_SHA256.txt), [deploy verification](L1F_evidence/deploy_verification.json), [final remote checks](L1F_evidence/remote_readback/preflight/deploy_after.log).

[`l1f_job.sbatch`](../../../../../scripts/labelfix/clariden/l1f_job.sbatch) requests account `a0140`, `debug`, one exclusive node, one task, 32 CPUs, **four GPUs**, and **01:00:00**. Four independent workers require GH200 devices. Live debug was UP with a 01:30:00 cap; this job stays within the requested one-hour limit.

```text
sbatch: Job 3680745 to start at 05:50:25 a using 288 processors on nodes nid006647 in partition debug
```

This is a scheduler simulation, with no submitted job or allocation. [Test-only output](L1F_evidence/remote_readback/preflight/test_only.log), [queue readback](L1F_evidence/remote_readback/preflight/squeue_after.txt).

Estimate: **20 minutes elapsed on the four-GH200 node**, excluding queue delay. Original full-population alignment took 93.241 + 36.806 = **130.047 s**. The estimate allows for the measured crop/receipt checks, allocation-side alignment/detector join, regional scoring, JSON/compression, final rehash/readback and reserve. It is a planning estimate; no full-population GPU timing was run here. Since it is below one hour, no array split is needed. Per-shard resume is retained.

## Coordinator submit command — prepared, never executed here

```bash
set -euo pipefail
L1F_ROOT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1f
cd "$L1F_ROOT"
sha256sum --check L1F_DEPLOY_SHA256.txt
sha256sum --check L1F_EXTERNAL_SHA256.txt
L1F_JOB=$(sbatch --parsable scripts/labelfix/clariden/l1f_job.sbatch)
L1F_JOB=${L1F_JOB%%;*}
printf 'L1F_JOB=%s\n' "$L1F_JOB"
```

For an interrupted job, retain this exact bundle and use `sbatch --export=ALL,L1F_RESUME_OUT=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1f_<OLD_JOB_ID> scripts/labelfix/clariden/l1f_job.sbatch`. The entry point verifies all inputs and sealed shards again before resuming.

## Pull receipts only — after coordinator completion

Run from this worktree on the Mac, using the actual job ID, never the test-only prediction. `rsync` exists on both ends. These filters preserve per-shard directories and exclude frames, images, SQLite data, models and historical inference payloads.

```bash
L1F_JOB=REPLACE_WITH_ACTUAL_JOB_ID
L1F_BASE=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017
L1F_LOCAL="docs/records/labelfix/spellcheck/clariden/L1F_evidence/production_${L1F_JOB}"
mkdir -p "$L1F_LOCAL"
rsync -av --prune-empty-dirs \
  --include='*/' --include='receipt.json' --include='input_verification.json' \
  --include='binding.json' --include='code_sources.json' --include='plan_receipt.json' \
  --exclude='*' "clariden:$L1F_BASE/l1f_${L1F_JOB}/" "$L1F_LOCAL/"
```

## L1R4 join contract

L1R4 must first verify the complete L1F receipt, its shard receipts/payload hashes, checkpoint/code/input provenance and exact 124,669-ID population. **Join by `line_id`**, across all 248 L1F shards; do not pair shard numbers with the 974 detector shards.

For every original L1-v0/L1E runtime line, retain saved recogniser text, detector, predictions and coverage. Check the L1F saved-alignment identity hash against the original alignment's five identity fields; check the saved text hash against NFD runtime text. For matched rows, reconstruct the complete scored alignment using saved geometry plus the new confidence/frames and verify the frozen evidence/hash. Then apply only `runtime.update(recognition_fields(l1f_row))` before invoking the unchanged SF6c composer. A mismatch row carries explicitly unscored evidence and remains unavailable for recogniser absence; never replace saved text, fabricate missing evidence, or infer it from a line mean. Frame arrays remain in L1F for audit.

The recompose writes new L1R4 outputs and reports match/refusal/per-wave counts. No L1R4 recomposition or submission was performed in this package task.

L1F READY: E3 full_s0 frame evidence for 124,669 lines; mock fields verified 64/64; alignment identity ok (62 exact, 2 transferred withheld); deploy sha256 351/351; test-only sbatch: Job 3680745 to start at 05:50:25 a using 288 processors on nodes nid006647 in partition debug; est 20 min GPU
