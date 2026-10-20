Run offline from the repository root with the collector's byte-exact interpreter:

```sh
export PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
PY="$HOME/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python"
BASE=docs/records/harvest/collect_v3_admission
"$PY" "$BASE/build_release_admission.py" --tranche all
```

The default geometry roots include CP3, CP4, the shared CP7 r1/r2 cache,
`~/Projects/collect-v3-data/geometry_prep`, and the read-only live g1b cache.
To replace that search list, supply `--geometry <dirs…>`. An explicit empty
`--geometry` is the fail-closed no-geometry case. No geometry is generated.
Only hash-valid source-bound CP2 loads can supply geometry. Work is divided
among four independent local page processes (`--workers`); rows are written
in deterministic source path/hash and row-id order. No agents/readers run.

W1 uses ADM4's W1 qualification scope; W2 uses W2C1 ed074681 and CAPS4
headings carried from W1. Every registered line-level exclusion class is
removed, including registered crop-rejection classes. The primary release
class drives the text rule variant, as in ADM4's release records; collector
script inventory is not substituted for it. Page medians include all snapshot
rows before qualification and exclusions. No historical `screen_merged` or
`rotated_crop` feature flag acts as a new admission screen.

The accepted text consumer deliberately cannot issue a public geometry KEEP
on its own. The builder uses its text/metadata checks and the unchanged
CP3/CP4/CP5 composition, as the accepted CP7 driver does. It applies regional
orientation inheritance, allows orientation_unknown for that screen, records
column crossing drops, and only admits a definite composed KEEP. Missing
geometry is an explicit fail-closed drop. Orientation is `not_run` for those
missing-cache rows; this is distinct from a measured orientation_unknown.
The existing separator preparer runs in memory from cached geometry and
original pixels; it does not detect/refit rows or write cache files. The
CP5pb `component_hits` diagnostic and calibrated tolerance are non-gating.

After building, stage W1 and W2 separately, preserving the shared manifest:

```sh
"$PY" "$BASE/stage_crops.py" \
  --admitted "$BASE/w1_originals_v3_screened_admitted.jsonl" \
  --features "$HOME/Projects/collect-v3-data/snapshots/W1_features_20261018_0524.jsonl" \
  --out "$BASE/crops" --extend --minimum-free-gb 10
"$PY" "$BASE/stage_crops.py" \
  --admitted "$BASE/w2_originals_v3_admitted.jsonl" \
  --features "$HOME/Projects/collect-v3-data/snapshots/W2_features_20261018_0524.jsonl" \
  --out "$BASE/crops" --extend --minimum-free-gb 10
"$PY" "$BASE/admw2/verify_outputs.py"
```

Use `.jsonl.gz` instead if the builder compressed that admitted file. Staging
returns 2 when the disk floor defers rows, 1 on verification failures, and 0
when all requested crops are present and verified. Per-input staging receipts
and deferred-row files accompany the shared manifest. An extension preserves
prior tranche entries and their membership, including earlier withdrawals.
Nothing is deleted from the crops tree. The original W1 admitted file is
never a destination of the builder or staging commands.

Each admission receipt records file hashes (uncompressed and stored), source
and class counts, input bindings, chosen full CP2 bindings, cache rejection
reasons, overlapping rule hits, and disjoint first-drop counts. Files over
50,000,000 uncompressed bytes are deterministically gzipped. A geometry run
changes coverage and admission decisions; rerunning this command regenerates
the same named release views on the new geometry.
