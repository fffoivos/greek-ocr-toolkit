# T6i2 locked test strata

Completed and rehashed: (ii) 189 masked / 10 guarded / 1 unmatched / 0 unresolved;
(i-b) 392 masked / 0 guarded / 8 unmatched / 0 unresolved. All workers ran at
actual nice 5, with a two-worker cap. Six locked tests and 27 unchanged T6h
tests passed. See `summary.json` for the final records hash and run receipt.

The T6i source preparation resolved exactly 200 (ii) and 400 (i-b) exclusions.
`preparation.json` and `resolution.jsonl` retain that original evidence;
`BLOCKED.json` records the earlier nice-15 blocker, superseded for this job by
`docs/records/briefs/T6i2_locked_strata_run.md`. It is not a current execution status.

## Execution contract

`run_locked.py` imports the unchanged T6h `page_worker` and phase0 adapter.
The locked wrapper binds only the resource-priority function to its documented
`min_nice=5`; T6h's own file and nice-15 check are unchanged. Actual nice is
recorded in every final line and page result. At most two fresh subprocesses
run concurrently, under the original T6h 10 GB disk watchdog and network-OFF
audit hook. Thread-count environment limits are inherited from T6h.

Each of five T6h mock pages contributes one ID. Each runs in a fresh process;
its final PNG bytes and guard/match/count fields must equal T6h `mock-out`.
A mismatch aborts before any locked-population masking. `mock-comparison.json`
records the IDs, baseline hash, worker binding and result.

The runtime exports Git tree `63c640a3aa4abe08d200258cf24d235dfa4a1625` using
T6h's `code_snapshot`, including its frozen-source and parameter checks
(`801d517e…`). No masking, matcher, guard, source worktree, release manifest,
or training manifest is edited.

## Separate source bindings and custody

Native pages span four source roots. Some (ii) blind cards live in a different
root from their raster. The wrapper makes a separate byte-verified custody
mirror for each native source root, under ignored `work/<root>/source/`.
Each mirror contains raster copies at their source-relative paths and exact
saved-original PNG bytes under `docs/records/harvest/locked-originals/<stratum>/`.
This lets the unchanged worker enforce both raster and original containment
inside its bound HARVEST. It checks native crop pixels, original hashes,
native headers and page hashes exactly as in T6h. No symlink broadens the
worker's allowed input root. Every copy is hash-checked against its original
before and after copying. The wrapper passes `script_class=unknown` as
non-semantic metadata; this is not used for detection, matching or masking.

Each binding includes the source root's per-line custody mapping, frozen code
hashes and wrapper/adapter/runner hashes. Final records retain the worker's
staged original/output paths and binding SHA, while `original_path` points to
the source original and `output_path`/`masked_path` point to the final PNG.
Source raster paths and hashes are also retained. Page failures become
`unresolved` with their explicit traceback and `worker_guard_status` retained;
the wrapper never treats a failed-page fallback as successful masking.

## Outputs and verification

`crops/<stratum>/<id>.png` contains the final outputs. `records.jsonl` uses
T6h fields plus stratum, actual nice, worker custody provenance, and the false
`training_release_allowed` / `train_pool_eligible` flags. `summary.json`
contains separate counts for (ii) and (i-b), record hash, rehash totals,
priority, worker cap and minimum observed free disk space. `masked` is the
frozen worker status, including accepted masks with no changed pixels.

Both exclusion files and every preparation source binding are revalidated.
Every source original, native raster and output is rehashed before aggregate
publication; final originals and outputs receive a further complete pass.
Page records are atomic resume units and must pass T6h validation with both
source and output rehashes to be reused.

Run inline, without networking:

```sh
.venv/bin/python -B docs/records/harvest/recut_v1/v2_full/locked/run_locked.py run
.venv/bin/python -B -m unittest discover -s docs/records/harvest/recut_v1/v2_full/locked -p test_locked.py -v
.venv/bin/python -B docs/records/harvest/recut_v1/v2_full/locked/guarded_commit.py
```

The tests verify the two-worker scheduling cap, job-local priority override,
source/mirror drift rejection, exclusion-population equality, five mock byte
identities and distinct PIDs, and final record/output/source custody hashes.
`test-results.txt` captures the completed verification run.

## Git handoff

PNGs, mirrors, frozen exports, page scratch and run logs are ignored. Final
`records.jsonl`, `summary.json`, mock receipt, code, tests, README and test
results belong to the guarded commit list. The guard validates exact hashes,
HEAD, branch, empty index, modes, frozen dependencies and ignore rules before
an optional explicit `--commit`. The guarded `--commit` attempt passed validation but staging was denied when
Git tried to create `index.lock` in the read-only Git metadata. No commit
was created and no index changes were made. Run the same guarded `--commit`
from a writable coordinator to commit the exact list.
