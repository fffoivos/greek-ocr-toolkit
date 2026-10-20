# P1 pilot evidence

Start with [PILOTS.md](PILOTS.md), [pilots.jsonl](pilots.jsonl), and [FILES.tsv](FILES.tsv).
Bulk downloads, raw Google responses, crops, detector caches and visual sheets
are kept locally in ignored subdirectories. Manifests, reports, scripts, source
receipts and ledger copies are eligible for tracking. The pre-existing P1 brief
is outside the delivery scope.

The report distinguishes measured candidate yield, source qualification and
reference release. The strict Greek-language Gutenberg pairing was not
qualified. The exploratory Blackie edition is explicitly English with Greek;
only proofread Greek-bearing labels enter the target yield. The blind forms
and static two-part sheets remain unadjudicated.

Offline read-back (from the worktree root):

```sh
../greek-ocr-toolkit/.venv/bin/python docs/records/harvest/pilots_v2/validate.py --check
```

The managed environment blocked creation of the worktree Git index lock.
No worker staging, commit or push succeeded. From a normal terminal, the
source-bound handoff checks the branch, HEAD and every manifested file before
staging only tracking-compatible files under this directory:

```sh
../greek-ocr-toolkit/.venv/bin/python docs/records/harvest/pilots_v2/stage_handoff.py --check
../greek-ocr-toolkit/.venv/bin/python docs/records/harvest/pilots_v2/stage_handoff.py --stage
```

Acquisition/read scripts are a reproducibility record, not a request to rerun
paid collection. `read_pilots.py` reserves every new image in one cumulative
P1 ledger and stops before a reservation would exceed USD 5. Ajax is explicitly
excluded from Google reads. Interrupted reservations cannot trigger an implicit
retry. All successful page reads were retained in denominators; unusable source
probes and extra witness leaves are marked in `pages.jsonl`.

`process_reads.py` preserves native geometry and G1b measurements;
`report.py` recomputes final admission/page quality and disjoint allocations.
`ajax_geometry.py` binds GT crops by exact pixels; `ajax_reframe.py` replays
measurements from those bound boxes with actual X/Y raster scales.
`align.py` records NFD spans, transformations and raw-source ownership.
`blind.py` produces reproducible accepted/rejected cards and separate keys.
`sheets.py` produces 20-page contact sheets balanced over documents/issues.
No script modifies the main harvest or the geometry worktree.
