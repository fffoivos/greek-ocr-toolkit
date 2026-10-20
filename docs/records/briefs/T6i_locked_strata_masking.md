# T6i: mask the locked test strata with the frozen tool (gpt-6.1-sol, network OFF, nice 15, medium-sized, inline run)

This runs in this worktree (`sol/recut-v1`), **after T6h completes.** It is test-only material: these lines stay in release_exclusions and are never admitted to training. Purpose: a masked new-source test instrument for the wave-1d arm.

## Population: 600 lines, ids from `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_exclusions/` (read-only)
- **(ii) `r0_locked_eval_ids.txt`:** 200 lines. They come from the F2/T4c/C0 blind-check strata, with keys under `~/Projects/greek-ocr-toolkit-sol-funnel-gr/docs/harvest/blind_checks_v1/{t4c,c0}/<src>_key.json` and the funnel sample pages in the sol-funnel-{gr,ia,intl} worktrees.
- **(i-b) `r0_ib_spellcheck_subset_ids.txt`:** 400 lines, from Wikisource R0 (`~/Projects/greek-ocr-toolkit-sol-wsr0/docs/harvest/wikisource_r0/`).
- For each line, resolve the page raster, the line's crop box and its original crop (sha256), from those read-only sources. **If a page raster or crop box cannot be resolved, record `unresolved` with the reason. Never approximate.**

## Masking: frozen and identical to T6h
Use `docs/records/harvest/recut_v1/v2_clariden/phase0_mask.py` through the T6h runner code paths (tree 63c640a3, params 801d517e, the T6b guard, the T6c2 matcher). Do not change any masking, matching or guard code. Run inline in your session (600 lines is small): nice 15, ≤4 workers.

## Output (git-ignored) under `docs/records/harvest/recut_v1/v2_full/locked/`
- `crops/<stratum>/<id>.png`;
- `records.jsonl`, in the same schema as T6h `out/records.jsonl`: id, stratum (ii | i-b), original sha256, output sha256, guard status (masked / guarded_original / unmatched_original / unresolved / failed_page), match status, counts, params, host, tree sha;
- `summary.json` per stratum;
- verification by re-hashing.

## Test first
Re-run 5 of the T6h mock ids through the same code path; they must be byte-identical to the T6h mock outputs. Only then do the 600.

## Hand-off
Leave a guarded commit list (code, README, records.jsonl and summary are committed; PNGs ignored). The last line must be exactly:
`T6i: done | (ii) <masked>/<guarded>/<unmatched>/<unresolved> of 200 | (i-b) <...> of 400 | records sha: <sha256> | mock-5 identical: <ok>`
