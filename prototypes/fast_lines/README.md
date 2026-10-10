# Q7 fast line prototypes

Twelve isolated prototypes, ten shared modules and a shared context/cache adapter.
No imports or edits to `greekocr/pages`; no held-out inputs, PDF text, model training,
network downloads, or background workers. The owner charter remains the specification.

Use this interpreter, from the worktree root, for every command below:

```sh
export PYTHONDONTWRITEBYTECODE=1
PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python
$PY -m pytest prototypes/fast_lines/tests -q -p no:cacheprovider
$PY -m prototypes.fast_lines.run manifest
$PY -m prototypes.fast_lines.run baseline
$PY -m prototypes.fast_lines.run references
$PY -m prototypes.fast_lines.run prototype --approach all --phase 1
$PY -m prototypes.fast_lines.run prototype --approach all --phase 2
$PY -m prototypes.fast_lines.run compose
$PY -m prototypes.fast_lines.run perturb
$PY -m prototypes.fast_lines.run prototype --approach all --phase 3
$PY -m prototypes.fast_lines.run report
```

`--pages` is a manifest-only review filter; algorithms never receive page identity
or selection category. `--limit` is a smoke-test convenience. Successful registered
experiments are reused, including explicit cache-hit receipts. No `--force` switch.
Failed receipts can retry; source/config changes create a new experiment identity.
Intentional warm repeats belong to E00/ET only.

Dependency order: native_contours → layout_barriers → font_guides → local_ribbons →
sheet_lattice → foreground_profiles → image_motifs → ink_condition → residual_ledger
→ map_graph → classical_residual → selective_rerun. The standalone variants all
start from the same small-detector baseline; earlier evidence is imported, not
applied repeatedly to the line output.

Phase 1 builds/inspects the common explicit references. Phase 2 runs each compact
algorithm/variant study once; phase 3 freezes its result without new computation.
Each approach README retains the original finer-grained plan and the build log.
Unfinished finer-grained substeps are explicitly listed in the results report.

Outputs are ignored under `.astra/fast_lines/out/`. Open `shared/index.html` for all
174-page galleries, original-pixel line crops, raw JSON and evidence. The two dense
reference generations are both preserved: `references-v1` is the failed independent
column-maximum experiment; `references` adds continuity and a body-height window.
Neither is truth. `shared/detector_source.json` pins the installed Apache-2.0
PaddleX code and shipped configuration by SHA-256. The adapter does not need Paddle.

Timings distinguish a standalone algorithm's marginal cost on reused dependencies,
full-page offline comparators, shared primitives and fresh composed latency. The
composition deliberately exposes unresolved residuals; it is not a finished hybrid.
See [the results report](../../docs/research/FAST_LINES_ROUND1_RESULTS.md).

After the runs, create the non-inference validation material and report:

```sh
$PY -m prototypes.fast_lines.inspect_outputs
$PY -m prototypes.fast_lines.write_report
$PY -m prototypes.fast_lines.publish_review
```

`publish_review` adds links to saved variants and contact sheets, then checks every
local image/link in the 174 reference pages and all main galleries. It does not
run inference or alter experiment products. It also repairs the baseline gallery's
nested relative reference links. The archived measurements predate this publishing
utility; no experiment is repeated to regenerate a gallery.

The archived round-1 fallback corpus uses the first A02 implementation. A02 v2 was
then run as a separate follow-up and fresh composition uses v2. Its exact v1 source
was recovered and its aggregate hash verified against the recorded experiment;
see `out/shared/source/A02-v1-run.py` and its receipt. Running the current entire
DAG from scratch would propagate v2 and constitute a new dependency configuration,
not reproduce the older frozen fallback results. Preserve those receipts.
