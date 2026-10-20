# SEG10: port the census_03 integration fixes into the code; adopt the length band 0.30–2.00 as segmentation 0.9-s5 (gpt-6.1-sol, medium, network OFF; no .git writes; no reader runs; no census)

**Worktree:** `~/Projects/greek-ocr-toolkit-main-next`, branch `cleanup/20261019`. Start only on a clean tree, after CLEAN4T is
committed: `git status --porcelain` must be empty apart from ignored files. If it is not, stop and report. The lead or
coordinator commits.
- Output: `docs/harvest/seg_steps/s5_adopt/`.
- Do not touch: `docs/harvest/seg_census/package/`, `census03_baseline/` and `remote_evidence/` (read only).

**Read first:**
- `docs/harvest/seg_census/remote_evidence/integration_fixes.diff` (22 lines), `source_diff_validation.json` and `HANDOFF.md`;
- `docs/harvest/seg_steps/s5/BAND_PROPOSAL.md`, `s5/changed_lines.jsonl` and `gate_rereport/REPORT.md` (the step-5 section);
- `docs/harvest/seg_steps/s4/replay.py`, `validate_report.py` and `tests_command.txt`;
- `greekocr/harvest/filtering_assets/segmentation-policy.js` and `service.mjs`;
- `docs/harvest/line_pipeline/tool_versions.json` and `scripts/harvest/build_filter_versions.py`.

A tool is EXACTLY the owner's rules: add no guard, threshold or heuristic. Change only the three things below.

## A. Port the two census_03 integration fixes

They exist only as a diff applied at deployment. Neither is in `greekocr/harvest/line_pipeline*.py`.

1. **`line_pipeline.py`, `automatic_result()`, numeric adjacency.**
   - Replace `elif tool == "numerics" and not any(c in text for c in ".-·"):` with
     `elif tool == "numerics" and not re.search(r"\d\s*[.\-·]\s*\d", text):`.
   - The effect: a numeric row is a separator candidate only if a separator sits between two digits.
2. **`line_pipeline_census.py`, `deduplicate()`, held-out crops.** After `held_crops={...}`, union in the configured held-out crop
   hashes:
   ```python
   binding=json.loads(self.db.execute("SELECT value FROM run WHERE key='binding'").fetchone()[0])
   held_crops.update(binding.get("config",{}).get("final_policy",{}).get("heldout_crop_sha256",[]))
   ```

**Port check.** After the port, the two hunks must match the diff's `+` lines byte for byte, apart from the line offsets. Show
the `diff` of the hunks.

**Tests.** The census_03 tests `test_fp3_numeric_adjacency.py` and `test_fp3_external_crop_input.py` are not available locally.
Write equivalents in `tests/test_integration_fixes.py`:
- **Numeric adjacency:**
  - `"1.234"`, `"12 - 3"` and `"4·5"` are separator candidates; the route is NOT `verified_no_change` with "no adjacent numeric
    separator candidate".
  - `"Α.Β. 12"`, `"12."` and `"-5"` are not candidates; the result is `verified_no_change`.
- **Held-out crops:** a train row whose crop sha256 is listed only in `final_policy.heldout_crop_sha256`, and not in any dev/test
  observation, is protected by `deduplicate()` exactly as an observed held-out crop is. A row not in the list is unaffected. Use
  the existing mock census harness.

## B. Adopt the length band 0.30–2.00 as segmentation 0.9-s5

**Provenance.** This is a coordinator decision, not an owner ruling. The coordinator took it under the owner's end-to-end mandate
("you don't have to wait for me, resolve these end to end").
- It was recorded in the coordinator ledger on 19 Oct at 21:34.
- It was reported to the owner in writing: "frozen the configuration at 0.9-s4 measurement, gate 0.3, band 0.30–2.00, one band
  for everything". The owner has raised no objection since.
- Record it with this provenance in the report, in `tool_versions.json` and in the README, never as an owner ruling.

The band is one band for everything: numeric, non-numeric, small and non-small.

The band is applied in **both** `boxLengthJudgement` and `combinedBoxJudgement` in `segmentation-policy.js`: change the defaults
`lower=.5, upper=1.5` to `lower=.30, upper=2.00`. There is no other change: padding stays 1.5, mode 2 stays, and the small path
and the gate are unchanged. `service.mjs` hashes this file, so the policy sha256 changes.
- **Record** the old and new policy sha256.
- **Versions:**
  - Segmentation becomes `0.9-s5`, with the iteration "length band 0.30–2.00 (coordinator decision under the owner's
    end-to-end mandate, 19 Oct 21:34; fitted on owner marks, s5)".
  - `PIPELINE_VERSION` goes `0.3` → `0.3.1`.
  - Record the A fixes as iterations of the tools whose components they change: `census` for `line_pipeline_census.py`, and the
    tool that owns `automatic_result()` per the manifest.
  - Keep the manifest's version = iteration-count invariant and say which numbers move.
  - Regenerate `tool_versions.json` with `build_filter_versions.py`. Report any fallback.
- **Replay** 0.9-s5 natively on the 150, the 888, the 250 and the 417 typology crops, with the s4 replay workflow unchanged
  apart from the version label.
  - **Expected:** every verdict change from 0.9-s4 to 0.9-s5 is a length-band change, with `reason` from the length rule.
  - **On the owner-judged lines, the ACCEPTANCE TEST:** the set of changed lines must equal `s5/changed_lines.jsonl` exactly.
    That is 59 lines before the gate exclusions and 38 after, as in `gate_rereport/`.
  - **Scores:** report 0.9-s4 → 0.9-s5, both unfiltered and with the content-gate 0.3 exclusions removed, as in `gate_rereport`:
    the 150 FP/FN/UNC, the 888 /135 (/91), the owner marks /235 (/191) and the typology /185 (/176).
  - **The numbers must equal the s5 report's 0.30–2.00 figures** (overall end-to-end fd/fk 59/16 → 10/24 before the gate;
    5/20 at 0.30–2.00 after the gate). If any number differs, that is a finding: list every differing line with its saved ratio.
    Do not tune.
- **Tests:**
  - Existing band tests are updated only where they assert 0.5–1.5 as the default. Show those diffs.
  - New boundary tests for the length rule, mode 2: (chars+1)/(pred+1) = 0.30 and 2.00 KEEP; 0.2999 and 2.0001 DROP.

## C. Run the full suite

Use the sol-recut `.venv/bin/python` with `PYTHONPATH=.` and `-p no:cacheprovider`, as in `s4/tests_command.txt`. Run:
- `tests/test_content_gate.py` and `tests/test_line_pipeline.py`;
- the four `tests/test_seg_{gate,deskew,curve,small}.py`;
- the new `tests/test_integration_fixes.py`.

The target is 0 failures. Report the counts verbatim.

## Report

Write `docs/harvest/seg_steps/s5_adopt/REPORT.md`, `flips.jsonl`, `replay.jsonl`, `summary.json`, a scope guard listing the
changed files with diffs, and a receipt.

**Last line:** `SEG10 READY: fixes ported numeric-adjacency <ok> heldout-union <ok> (hunks identical <yes/no>); policy sha <old8> → <new8>; segmentation 0.9-s5; pipeline 0.3.1; changed owner-judged lines <n> (= s5 <yes/no>); 150 FP/FN/UNC <s4> → <s5>; 888 <n> → <n>; marks <n> → <n>; typology <n> → <n>; tests <n> passed <n> failed`
