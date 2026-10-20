# CU3: clean-up step 3. The recogniser as one API, phase 1 (wrapper + golden tests + unpinned callers) (gpt-6.1-sol, medium, network OFF)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-cleanup`, branch `opus/cleanup-1`, from opus/spellcheck ba6d80aa).
- No `.git` writes; never pushed.
- Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`.
- Mac CPU. The only forward passes allowed are the parity check in §3: ≤ 200 crops, CPU, threads ≤ 4.

Spec: `docs/records/cleanup_20261017/CLEANUP_PLAN_20261017.md` §3, and appendix `docs/records/cleanup_20261017/CLEANUP_PLAN_20261017_api.md` Part 1 (§1.1–§1.8). Owner (verbatim): "during
cleanup consider to what extent the recognizer can be constructed as an API from the previous ocr tools, you know as a matter of repo
coherence and no code duplication."

## Hard constraints

1. **Do not change one byte** of any of these:
   - anything in `greekocr/labelfix/`;
   - anything in `greekocr/_vendor/`;
   - the 16 paths hashed by `release_gate.policy_binding()`;
   - any path listed in a `*_DEPLOY_SHA256.txt` receipt.

   **Proof required:**
   - `release_gate.policy_binding()` output before vs after, which must be identical;
   - a sha256 list of every pinned path before vs after;
   - `git diff --stat` showing only new files plus the unpinned callers in §4.
2. Nothing in `CLEANUP_PLAN_20261017.md` §7 is touched.
3. **Phase 1 = wrapper.** `greekocr/recogniser/` IMPORTS from `greekocr.labelfix.ctc_align` (and from `_vendor` for the eval/serve
   profiles). Behaviour is byte-identical. No logic is copied.

## 1. Package `greekocr/recogniser/`

Build it per api appendix §1.6:

| API | Notes |
|---|---|
| `load(checkpoint, codec=None, device='cpu', threads=None) -> Recogniser` | Union of today's checks: codec version + codec sha + n_classes + head. If an existing caller's checkpoint would fail a check the old path did not apply, report it, and keep a `strict=False` path that reproduces the old behaviour exactly. Provenance: checkpoint / safetensors / codec / code sha, device, dtype, torch. |
| `Recogniser.read(images, profile='labelfix'\|'eval'\|'serve', bs=16) -> [Reading]` | `labelfix` = `ctc_align.Recognizer`; `eval` = `E1Reader`; `serve` = the docling plugin Recognizer. Each profile delegates to the existing implementation. Unreadable inputs are reported, never dropped silently. |
| `Recogniser.logits(images, dtype=...)` | |
| `align(reading) -> Alignment`; `Alignment.slots()`; `Alignment.evidence(slots, image_width)` | Re-export or thin delegation of `ctc_align`. |
| `transfer(alignment_or_record, new_text)` | ONE semantics: always NFD, always drops frames, always flags `transferred`. Where the existing `ctc_align.transfer_alignment` or `r1_common.transfer_record` behave differently, the new function documents the difference. The pinned originals are NOT changed. |
| `confidence_matches(frames, confidence)` | float32-aware: recompute in float32, or `abs_tol=1e-6`. Test it on the 17 L1F rows in `artifacts/labelfix_l1r4/l1f_17_tolerance_witnesses.json` (copy the fixture into `tests/`; it is in the l1f worktree `~/Projects/greek-ocr-toolkit-spellcheck-l1f/artifacts/labelfix_l1r4/`). |
| `AlignmentCache(path, recogniser)` | One strict `crop_key`. Round-trips every new result through `to_record`, so first-run and replay agree. |
| `run_shard(...)` | Batch entry. |
| `forbid_forward()` | Context manager replacing the five monkeypatch copies (for new code; the pinned copies stay). |

## 2. Golden tests (`tests/recogniser/`)

1. On the frozen caches `.cache/labelfix/align_s0.jsonl` (and `align_locked_*` if present), the following are byte-identical between the
   old path and the API for every record:
   - `Alignment.from_record(...).to_record()`;
   - `recognition_evidence(...)`;
   - `alignment_sha256` (sha of `json.dumps(to_record(), sort_keys=True)`).
2. Evidence schema strings and the `to_record` key set are pinned as constants.
3. `transfer` behaviour on synthetic cases.
4. `confidence_matches` on the 17 witnesses (pass at 1e-6 or float32 recompute; fail at the old 2e-7 float64 check).

## 3. Parity check (CPU, ≤ 200 crops)

Run 200 crops through:
- `profile='labelfix'`, which must equal `ctc_align.Recognizer.align_batch` exactly: text, spans, `frame_confidences`, confidence;
- `profile='eval'`, which must equal `E1Reader.read`.

Report how often `labelfix` vs `eval` text differs on the same crops (the background-median / halo difference, appendix §1.4.1–2) as a
measured number. Do NOT pick a winner.

Crops: 200 from the local held-out set (`load_three_way(0)` crops), seeded.

## 4. Move the UNPINNED callers to the API

These are the callers not in any deploy receipt and not in `policy_binding`; verify each against every `*_DEPLOY_SHA256.txt` before
touching it:
- `readers/ours.py:load_ours` → `load(...).as_reader(profile='eval')`, ONLY if `readers/ours.py` is unpinned. The L1E receipt pins every
  `greekocr/**/*.py`, so it most likely is pinned. In that case: no change, and the API offers `as_reader` for new code.
- New code only: document in `greekocr/recogniser/README.md` that every new tool must call the API, with a table "old entry → API".

If every candidate caller turns out to be pinned (likely, per inventory §10), **change no caller**. Say so plainly, and list each caller
with its pin. Phase 2 (moving pinned callers) happens only at gate re-certification.

## Report

`docs/records/cleanup_20261017/CLEANUP_STEP3_REPORT.md`:
- the API surface;
- the pinned-path sha table before/after and the policy digest before/after (both identical);
- golden test results;
- parity numbers (labelfix vs old: identical; eval vs old: identical; labelfix vs eval: measured difference rate);
- the callers moved or not moved, each with its reason;
- test counts: all tests green, none weakened.

Last line:
`CU3 READY: greekocr.recogniser phase 1 (wrapper); pinned bytes unchanged <k>/<k>; policy digest identical <yes>; golden <n>/<n>; parity labelfix <ok> eval <ok>, labelfix≠eval on <x>/200; callers moved <m>; tests <n> passed`.

## Appendix: ctc_align.py blob per branch (coordinator ruling: record in the CU3 report)

| branch | blob | commits touching it since merge-base with opus/spellcheck |
|---|---|---:|
| opus/spellcheck | 91217710 | 0 |
| opus/spellcheck-s8 | 91217710 | 0 |
| opus/spellcheck-l1 | ecbdfc18 | 0 |
| opus/spellcheck-l1r | ecbdfc18 | 0 |
| opus/spellcheck-l1r2 | ecbdfc18 | 0 |
| opus/spellcheck-l1r3 | 91217710 | 0 |
| opus/spellcheck-l1f | 91217710 | 0 |
| opus/spellcheck-r1 | ecbdfc18 | 0 |
| opus/spellcheck-r0 | ecbdfc18 | 0 |
| opus/r2-cards | 91217710 | 0 |
| opus/r2-prep | 91217710 | 0 |

Stale blobs with zero commits are not edits (coordinator); CU3 builds on opus/spellcheck's version (blob above; file sha256 3ecb1a20…). Copy this table into CLEANUP_STEP3_REPORT.md.
