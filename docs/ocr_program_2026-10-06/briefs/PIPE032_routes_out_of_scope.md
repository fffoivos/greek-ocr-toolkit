# PIPE032: pipeline 0.3.2 — declared out-of-scope correction routes; segmentation version restored to the iteration invariant (gpt-6.1-sol, medium, network OFF; no .git writes; no reader runs; no census; no Slurm)

**Worktree:** `~/Projects/greek-ocr-toolkit-main-next`, branch `cleanup/20261019`.
- Start on a clean tree at the coordinator's launch head: `git status --porcelain` must be empty apart from ignored files.
- The coordinator commits.
- Output: `docs/records/harvest/pipe032/`.
- Change only what is listed below.

**Read first:**
- `greekocr/harvest/line_pipeline.py`: `routes()`, `automatic_result()`, `validate_result()`, `preserve_holds()`, `Pipeline.evaluate`
  (the routing loop, the `unresolved` check and `finish()`), and `final_eligibility()`;
- `greekocr/harvest/line_pipeline_census.py`: the binding (`config`), `deduplicate()`, the exports (`admission_records`), and the
  version verifier around line 314;
- `scripts/harvest/build_filter_versions.py` and `docs/harvest/line_pipeline/tool_versions.json`;
- `docs/harvest/line_pipeline/README.md`;
- the segcensus evidence, read only: `~/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/HANDOFF_CENSUS05.md`
  ("Blocking runtime findings") and `audit_runtime_contracts.py`.

A tool is EXACTLY the owner's rules: add no guard, threshold or heuristic beyond what is stated here.

## A. Declared out-of-scope routes (coordinator decision under the owner's end-to-end mandate, 20 Oct)

**Why.** SF7, the polytonic corrector, is `candidate_pre_audit`. Today every polytonic-routed row without a released, qualified
polytonic result HOLDs (`correction_unresolved`). Census_03 held 113,176 v2-train rows this way, and every polytonic-routed W1/W2
row has no polytonic ledger at all. Release v3 would then have no polytonic supply.

The coordinator decided that census_05 runs with polytonic OUT OF SCOPE, explicitly recorded: those rows are admitted with the
raw Google label, and SF7 enters when its audit passes. Record this in the README and `tool_versions.json` as a coordinator
decision under the owner's end-to-end mandate, never as an owner ruling.

**The change:**
1. **Config.** `config.routes_out_of_scope`: a list of tool names, default `[]`.
   - It is part of the run binding, so it enters the binding hash.
   - Reject any name that is not in `TOOLS`, and reject `content_repair` (anomaly resolution is never optional).
   - The pipeline receives it the way it receives `final_policy`.
2. **In `Pipeline.evaluate`, for each needed tool that is in `routes_out_of_scope`:**
   - The corrector and `automatic_result` are NOT called. The tool's ledger is not consulted for that row.
   - Record `out["routes"][tool] = dict(tool=tool, status="not_applied_out_of_scope", edits=[], reason="route out of scope for this
     release", release_scope=<the config list>)`.
   - That status is not in `SUCCESS` and is excluded from the `unresolved` check. It contributes no edits to `merge_edits`.
   - It is excluded from the candidate-scope recheck. It is not a resolver for `content_repair`'s `resolved_by`.
3. **Unchanged:** every in-scope route behaves exactly as in 0.3.1.
   - A missing or sparse result for an in-scope route is still `missing qualified tool result`, which HOLDs.
   - `content_repair`, the gate, segmentation, final eligibility, dedup and held-out protection are untouched.
4. **Recorded per row.**
   - In `decisions.jsonl`, through the route record above.
   - In `admission_records.jsonl`: a field `corrections_not_applied` listing the out-of-scope tools that were routed for the row,
     with the status `not_applied_out_of_scope`. It is empty (`[]`) for rows with no out-of-scope route.
   - The census `summary.json` counts rows per out-of-scope tool, by disposition.
5. **Final eligibility** reads nothing new. Say so explicitly, with the line references showing it does not consult the
   polytonic route.

## B. Segmentation version restored to the invariant

The census verifier (`line_pipeline_census.py:314`) requires `version == "0." + str(iteration_count)`. That is the documented
invariant. Segmentation declares `version="0.9-s5"` with 13 documented iterations, so census_05 refuses to start.
- Set the segmentation version to `"0.13"`.
- Keep `"0.9-s5"` as a display label: add `label="0.9-s5"` to the tool entry, if the manifest schema allows an extra field. If
  it does not, say so and put the label in `scope`.
- Do not change the verifier.
- Update the README's version table to "0.13 (0.9-s5)".
- Scan every other tool with the same rule and report each pass or fail. Fix only segmentation.

## C. Versions

- `PIPELINE_VERSION` goes `0.3.1` → `0.3.2`.
- A is an iteration of the tool whose component owns the routing loop in `Pipeline.evaluate`, per the manifest, and of `census`
  for the admission-record field and the summary count.
- Keep the version = iteration-count invariant for every tool you touch. Say which numbers move.
- Regenerate `tool_versions.json` with `build_filter_versions.py`. `version-build-fallbacks` must be empty.

## D. Tests (`tests/test_routes_out_of_scope.py`), plus the existing suite

- A polytonic-routed row with `routes_out_of_scope=["polytonic"]` and a polytonic corrector that raises:
  - it is ADMITTED with the raw text;
  - `routes.polytonic.status == "not_applied_out_of_scope"`;
  - its admission record carries `corrections_not_applied=["polytonic"]`.
- The same row with `[]` HOLDs `correction_unresolved`, exactly as in 0.3.1.
- A row routed to polytonic AND numerics, with no numerics result: it still HOLDs on numerics. Out-of-scope never turns a
  missing in-scope result into a no-change.
- A polytonic + cyrillic row whose cyrillic result is an edit: the edit is applied, polytonic is recorded as not applied, and the
  row is ADMITTED.
- `routes_out_of_scope=["content_repair"]` and an unknown tool name are both rejected at config load.
- The binding hash differs between `[]` and `["polytonic"]`.
- Gate-excluded rows are unaffected: their routes are still `not_run_due_to_prior_exclusion`.
- **Regression, with `[]`:**
  - the native replay of the 150 + 888 gives verdict and reason equal to `docs/records/harvest/seg_steps/s5_adopt/replay.jsonl`;
  - the census_04 200-row whole-pipeline mock gives decisions equal to the 0.3.1 run (`docs/harvest/seg_census/mock_batch.py`);
  - list every differing row (expected: none).
- **The same mock with `["polytonic"]`:** report ADMIT / HOLD / DROP before → after, and the rows that move. Every mover must
  be HOLD → ADMIT or HOLD → DROP with a polytonic-only unresolved reason before.
- **The census verifier** now accepts the regenerated manifest. Run it directly.
- **The full suite:** use the command from `docs/records/harvest/seg_steps/s4/tests_command.txt`, or its current equivalent at
  HEAD. Report the counts verbatim. The target is 0 failed / 0 errors.

## Report

Write `docs/records/harvest/pipe032/REPORT.md` with the diffs, the version table before → after, the test counts, the mock
tables, a scope guard (the changed files with their diffs) and a receipt.

**Last line:** `PIPE032 READY: routes_out_of_scope <ok>; in-scope missing still HOLD <ok>; admission field <ok>; empty-config regression 150/888 <n>/<n> mock 200 identical <yes|no>; polytonic-out mock ADMIT/HOLD/DROP <b> → <a>; segmentation version 0.13 (label 0.9-s5) verifier <ok>; pipeline 0.3.2; versions moved <list>; fallbacks <n>; suite <n> passed <n> failed <n> errors`
