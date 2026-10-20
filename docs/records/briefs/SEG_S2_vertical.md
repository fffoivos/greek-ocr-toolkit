# SEG step 2: vertical crops are turned 90° right; rotation check (gpt-6.1-sol, medium, network OFF; no .git writes; no reader runs)

**Worktree:** `~/Projects/greek-ocr-toolkit-segcensus`, branch `opus/seg-census`. The lead commits. HEAD contains step 1 (0.9-s1:
cdab7a724, aa72ce4bf). Use the new output directory `docs/records/harvest/seg_steps/s2/`. Do not touch:
- `docs/harvest/seg_census/package/`;
- the stray `docs/records/harvest/seg09/`;
- the untracked `docs/records/harvest/collect_v3_admission/segeval1/keys/census02_segmentation_evidence.jsonl` (read only).

**Read first:**
- `~/Projects/greek-ocr-toolkit-secondary/docs/CONTEXT_20261019_segmentation_and_secondary.md`. The owner's standing rules are
  binding: a tool is EXACTLY the owner's rules; never add a guard, test, threshold or heuristic; extras are diagnostics only.
- `docs/records/harvest/seg_steps/s1/REPORT.md` and its `replay.py`, `prepare.py` and `validate_report.py`. Reuse the step-1 replay and
  scoring workflow unchanged.
- `docs/records/harvest/seg_steps/NOTES_FOR_LATER_STEPS.md`.

## The single change (owner, 19 Oct; decided)

This is version **0.9-s2**, built on 0.9-s1.
- **If a crop's height > width, turn it 90° RIGHT (clockwise) before ALL measurement and detection.** That covers the line
  inventory, the gate, the row frame, the length and the padding.
- No threshold, no exception, no aspect band: every crop with h > w is turned, including near-square 1–2-glyph crops (e.g. a "1"
  at 22×24).
- Crops with h ≤ w are processed exactly as in 0.9-s1.
- Nothing else changes.

## Do

1. **Implement the change, with tests:**
   - h = w + 1 is turned and h = w is not;
   - the turn is clockwise: a known asymmetric synthetic image maps pixel (x, y) → (H−1−y, x);
   - every h ≤ w crop gives a byte-identical 0.9-s1 result.
2. **Witnesses: the four vertical owner-KEEP crops on the gate sheet** (69×252, 26×166, 32×265, 19×156 on the 150; find their ids
   from the 150 inputs and `segeval1/owner_marks_20261019.jsonl` in sol-recut, read only). Per witness, report:
   - 0.9-s1 vs 0.9-s2: rows, box long side / height, ratio, padding, verdict and reason;
   - an overlay PNG of the turned crop under `s2/overlays/`.
3. **Rotation check (diagnostic only; it changes no verdict).** Run the 0.9-s2 line detector and measurement on every crop of the
   **150**, each turned 90° left, 90° right and 180° and fed in AS GIVEN. Compare each orientation with the upright 0.9-s2 run:
   - Inputs: the turned image goes through the full 0.9-s2 tool, so the h > w turn applies to it as the tool would.
   - Report, per orientation:
     - agreement counts for the main-row detection (same row count; main-row box within ±1 px after mapping back);
     - box long side / height;
     - ratio, padding and verdict.
   - List every disagreement, with the crop id, both values and the owner label.
4. **Near-square 1–2-glyph diagnostic.** Never a threshold.
   - **(a) On the replay sets (150 + 888 + 250):** every crop with h > w and Google chars ≤ 2. Give:
     - the count;
     - the aspect h/w distribution (h ≤ 1.25w, ≤ 1.5w, ≤ 2w, > 2w);
     - the 0.9-s1 → 0.9-s2 verdicts;
     - the owner marks where present.
   - **(b) The census population, ~2,540 by the Small segment analysis (h > w, chars 1–2):**
     - Reproduce the count from the local evidence files only, with the same aspect bins.
     - If the crop images for some of them are already present locally, or can be regenerated with the existing local crop
       tooling and source pages already on disk, run 0.9-s1 and 0.9-s2 on those, cap 600, sampled uniformly with seed 20261019.
       Report the verdict transition table.
     - Do NOT fetch anything, use Clariden, or touch the census.
     - If no crops are available, say so and give the count only.
   - **(c)** Pick 24 examples spread over the aspect bins, at least 6 of them with owner marks if available. Give each one an
     overlay (upright and turned) under `s2/near_square/`.
5. **Replay** 0.9-s2 natively on the **150**, the **888** and the **250 cell sample crops**, scored exactly as in step 1:
   - the 150: FP/FN/UNC;
   - the 888: agreement on the 135 rated rows;
   - all owner marks: latest mark wins.

   Show 0.9-s1 → 0.9-s2 side by side with the 0.8 column kept, plus flip tables: every changed verdict with the owner label or
   mark, and the crop aspect.
6. **Readback:** every h ≤ w crop replays byte-identical to step 1, both verdict and evidence. Include a scope guard listing the
   changed source files.
7. **Report** in `docs/records/harvest/seg_steps/s2/REPORT.md`, plus `flips.jsonl`, `rotation_check.jsonl`, `near_square.jsonl`,
   `summary.json` and a receipt. Update `tool_versions.json` as step 1 did.

**Last line:** `SEG S2 READY: turned <n> of 1288 replay crops; vertical witnesses <4 verdicts 0.9-s1→0.9-s2>; rotation agree L/R/180 verdict <a/b/c>/150; near-square replay <n> (flips <n>), census count <n>, run <n|none>; 150 FP/FN/UNC <s1> → <s2>; 888 rated agree <n> → <n>/135; owner marks agree <n> → <n>/235; flips <n>; tests <n> passed`
