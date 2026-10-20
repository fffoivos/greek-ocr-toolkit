# LF2: LF1 production prep on the census_05 benchmark draw (gpt-6.1-sol, medium; network ON for Clariden READ-ONLY; no .git writes; BUILD ONLY: no reading, no crop fetch, no submission)

Night plan step P6. The accepted tool is `artifacts/lf1/` (LF1_REPORT.md, DRYRUN_PLAN.md). Reuse it; change it only where production
plumbing needs it, and add no rule, guard, threshold or heuristic of your own (owner rule). The lead runs the readers later.

## Inputs (read-only, other worktree)

- Draw: `~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/bench02/census05/candidates.jsonl`, sha256
  `70a29c202691584a3382e77505ef56db7b9a0d1347fa5ac2eccc95ac8e9acfe5`, 3,341 rows (test 2,808, dev 533; parents W1 2,099 / W2 1,242).
  Its draw rules: `draw_plan.json`, `DRAW_CENSUS05_V2.md`, code `../bench02_draw.py` (selection ~l.418–535, readout ~l.587–610).
- Readout (NOT yet present): `candidates_readout.jsonl`, written by `bench02_draw.py readout` (job 3704844); it will land at
  `.../bench02/census05_readout/`. Take its schema from the readout code (`parent_id`, `row_id`, `final_text`, `crop_sha256`,
  `crop_source_image`, `crop_bbox`, …). Build and test against fixtures in that schema.
- Crops on Clariden: `W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`; W1 rows at `$W/collection_w1_originals/<source>/<row_id>.png`
  (present now), W2 rows at `$W/collection_w2_originals/<source>/<row_id>.png` (after CROPS4 job 3704831; may be absent now).

## Build

1. **Adapter** `artifacts/lf1/tools/prod_adapter.py`: join candidates and readout on (parent_id, row_id), in candidates order; write the
   `build_candidates.py` input JSONL. `label` = readout `final_text` verbatim; `source_crop` = the local fetched PNG; `source_sha256` =
   readout `crop_sha256` (the builder's existing hash check then proves crop identity; add no other check). Carry `split`, `rank`,
   `parent_id`, `edition_id` through. `class` must keep test and dev apart for the hook: if the class field alone would let a test line be
   replaced by a dev line, encode it as `<split>|<class>` (plumbing only). Pick `line_id` = `row_id` if unique across the draw, else
   `parent_id/row_id`; say which. A candidate with no readout row, or a readout row not in the draw, is an error (report counts).
2. **Fetch list** `artifacts/lf1/prod/fetch_list.tsv` (row_id, tranche W1/W2 from parent_id, remote path, local path) and
   `artifacts/lf1/prod/FETCH.sh`: ONE batch for all 3,341 PNGs into
   `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/lf1_prod/crops/`
   (one ssh stream, e.g. `tar -T list` piped back; then a local sha256 manifest). Do NOT run it. Read-only on Clariden now: cert check
   (`ssh clariden true`; on any auth error STOP, never refresh the cert), then stat the listed paths: W1 present/missing and bytes, W2
   present/missing. **The Mac has about 1.7 GiB free**: report the measured W1 bytes, the W2 estimate, and the total Mac footprint
   (crops + pack copies + typical zoom files from the dry run) so the lead can judge it before fetching.
3. **Pack build**: `build_candidates.py` as delivered (50 bed + 6 frozen controls per context, seeded) on the adapter output; packs under
   the existing pack root `.../scratchpad/lf1_packs/candidates/`. Prove the full chain adapter → build → scanner layout check on a
   synthetic fixture in a temp BASE (do not write `candidate_contexts.json` in the real BASE now). State the expected production numbers:
   contexts, bed cards, control cards. If ≤100 cards/context with ~10% controls needs anything other than 50+6, say why; do not change it.
4. **Fleet plan** `artifacts/lf1/prod/PROD_PLAN.md`: exact lead commands in order (fetch → verify manifest → adapter → build →
   `bash artifacts/lf1/RUN_ALL.sh --jobs 24 --contexts artifacts/lf1/candidate_contexts.json` → map → finalize), the limit probes before
   and after each context, refusal at ≥90% weekly, one fresh re-read per VOID context, and the cost forecast from the dry-run ledger
   (tokens per 100 cards × production cards; weekly pp per 100 cards from the dry-run probe readings, stated at the meter's resolution).
5. **Replacement hook on the overdraw** `artifacts/lf1/tools/prod_finalize.py`: from the draw's OWN definitions (cite the code lines),
   split each (split, class) into the in-quota selection and the ordered overdraw (draw = ceil(1.2 × quota); credited = min(drawn, quota)).
   If the draw code does not define which lines are in-quota and the overdraw order, STOP this part and report what is defined.
   After reading: a line passes only with verdict `OK`. Flagged in-quota lines (any other verdict; unresolved and VOID-twice counted
   separately) go to `replace_flagged` unchanged; overdraw lines without `OK` are passed as `--used` so they are never picked. Output the
   final benchmark line list + receipt (flagged, REPLACED, UNFILLED per split/class/source). Test on synthetic fixtures, including that a
   test line is never replaced by a dev line.

Tests: add to `artifacts/lf1/tools/test_lf1.py` (adapter join and errors, fetch list complete and unique, tranche paths, end-to-end
fixture build, finalize). All existing tests must still pass.

Write nothing outside this worktree and the scratchpad pack root. Report `docs/labelfix/spellcheck/LF2_PROD_PREP.md` (with a
LEAD_COMMIT_PATHS list) and the Codex weekly reading (`$S/meter/launchers/limit_probe.sh lf2` pattern, if it runs in your sandbox).
Final line: `LF2 READY: tests N passed; fetch list 3341 (W1 present a/2099, W2 present b/1242; est. MB m); contexts c (cards d+e)` or
`LF2 STOPPED: <reason>`.
