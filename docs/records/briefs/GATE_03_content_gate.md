# Content gate 0.3: foreign-script and mixed-script rows are excluded before segmentation (gpt-6.1-sol, medium, network OFF; no .git writes; no reader runs; no census)

**Worktree:** `~/Projects/greek-ocr-toolkit-segcensus`, branch `opus/seg-census`. The lead commits. Output notes go in
`docs/harvest/line_pipeline/gate03/`. Do not touch:
- `docs/harvest/seg_census/package/`;
- `docs/records/harvest/seg09/`;
- the untracked `segeval1/keys/census02_segmentation_evidence.jsonl` (read only).

**Read first:**
- `~/Projects/greek-ocr-toolkit-secondary/docs/CONTEXT_20261019_segmentation_and_secondary.md`. A tool is EXACTLY the owner's
  rules; never add a guard, test, threshold or heuristic beyond them.
- `greekocr/harvest/line_pipeline.py`: `inventory`, `content_issues` and `Pipeline.evaluate`, lines ~320–352.
- `greekocr/harvest/line_pipeline_census.py`: `prepare()` and the native prefetch, lines ~384–445.
- `docs/records/harvest/line_pipeline_legacy/pipeline.mmd`, `README.md`, `tool_versions.json` and `scripts/harvest/build_filter_versions.py`.

## The defect (owner, 19 Oct)

Witness: `gazette_modern--67dfc161a690ff25--s000-l0029`, Google text "日".

The owner's two gate rules are:
1. each document has expected languages and scripts, and any other script is flagged;
2. any word mixing scripts means the line is dropped automatically.

Lines failing the gate must never reach segmentation or any tool.

The code does something else. `evaluate()` records `content_issues` as `suspicious` in the `content_gate` stage, and the row then
goes to segmentation regardless. In the census, `prepare()` also starts native segmentation for every row before `evaluate()`
runs. `pipeline.mmd` draws `Q "Repairable candidate" --> S`.

## The single change: content gate 0.3

The issues are the existing `content_issues(raw, inv, expected, codec)` on the raw text, with the pipeline's own `inventory`
and `expectations`. Leave the definitions of the issues unchanged.

1. **`mixed_script_word` present → DROP immediately.**
   - Reason: `dict(reason="mixed_script_word", words=[...])`.
   - If `unexpected_script` is also present, add it as a second reason.
2. **Otherwise, `unexpected_script` present → HOLD immediately.**
   - Reason: `dict(reason="unexpected_script", scripts=[...])`, with the evidence: the inventory script counts and the
     offending characters.
3. **Both exclusions:**
   - Run them right after the `content_gate` stage is recorded, before the crop-identity check and before segmentation.
   - Go through the existing `finish()`, so every route is marked `not_run_due_to_prior_exclusion`.
   - Add no `segmentation` stage. Record the gate decision in the `content_gate` stage as `excluded=<reason>`.
4. **The census must not measure these rows either.** In `line_pipeline_census.py`, `prepare()` must return an empty
   `Observation()` for a row the gate excludes, the same way it already does for unresolved expectations and unbound crop
   identity. No native call, no measurement cache entry.
   - Use one shared helper from `line_pipeline.py` so `evaluate` and `prepare` cannot diverge.
5. **What stays repairable:**
   - The `Q → S` route remains ONLY for `unexpected_character` inside the expected scripts (codec-outside marks such as COMBINING
     DOT ABOVE), together with the existing profile-anomaly and `unexpected_language` handling, unchanged.
   - Those rows still go to segmentation and `content_repair` exactly as now.
6. **Versions:**
   - `content_gate` becomes 0.3. Add the iteration "owner gate: mixed-script word drops, unexpected script holds, before
     segmentation" in `build_filter_versions.py`, and regenerate `tool_versions.json` the same way earlier steps did.
   - `PIPELINE_VERSION` stays unchanged unless the README ties it to the gate; if you change it, say why.
7. **Docs:**
   - `pipeline.mmd`: C gets the two new exclusion edges, `"Mixed-script word" --> D` and `"Unexpected script" --> H`. `Q` is
     relabelled "Unexpected character within expected scripts".
   - `README.md`: the versions table and executed-sequence step 2.

Nothing else changes: no segmentation, routing, repair or final-eligibility edits.

## Do

1. **Implement, with tests** in a new `tests/test_content_gate.py`:
   - A row with "日" on a Greek page gives HOLD with `unexpected_script ["other"]`. The segmenter is never called (use a segmenter
     that raises), and every route is `not_run_due_to_prior_exclusion`.
   - A row with a Greek/Latin mixed word (e.g. "Αθηνa") gives DROP with `mixed_script_word`, and the segmenter is never called.
   - A row with both gives DROP with both reasons.
   - A row whose only issue is a codec-outside mark inside the expected scripts still calls the segmenter and schedules
     `content_repair`, as before.
   - A clear row is unchanged. Compare against the pre-change `evaluate` output.
   - The census `prepare()` returns an empty Observation for the two excluded kinds and makes no native call: use a mock
     factory, following the existing census tests' pattern.
2. **Run** the new tests and the four `tests/test_seg_*.py` files.
   - The existing pipeline suite is NOT in this worktree. It is `~/Projects/greek-ocr-toolkit-sol-recut/tests/test_line_pipeline.py`
     (read only), which has the same `line_pipeline*.py` sources as this worktree before your change.
   - Copy it into `tests/test_line_pipeline.py` here and run it against this worktree's code.
   - Report the counts and any failure verbatim, before and after your change.
   - Where an existing test asserts the old behaviour (a foreign or mixed row reaching segmentation), list it with the assertion.
     Update only that assertion to the owner's rule, and show the diff. Change no other test.
3. **Witness:** run `evaluate` on the l0029 row and show the decision JSON, built from whatever local row data exists (a
   synthetic row with its text and source is fine; say which).
4. **Scope guard:** list the changed files with diffs and a stat.
5. **Report** in `docs/harvest/line_pipeline/gate03/REPORT.md`, plus a receipt.

**Last line:** `GATE 0.3 READY: witness l0029 <disposition>; mixed DROP <ok>; foreign HOLD <ok>; codec-mark repair route kept <ok>; census prepare skips <ok>; tests <n> passed <n> failed; files <list>`
