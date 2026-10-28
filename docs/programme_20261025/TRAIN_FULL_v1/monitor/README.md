# Stage C dashboard CSV exporter

`export_full.py` is a standalone Python 3.6 standard-library script. It reads
the full-v1-013-stage-c-sel run tree without importing or changing the sealed
package. Run locally against the captured smoke tree:

```sh
python3 -B docs/programme_20261025/TRAIN_FULL_v1/monitor/export_full.py --runs out/TRAIN_FULL_v1/receipts_stage_c_sel_smoke/smoke_tree/runs --out /tmp/train-full-monitor-smoke
```

Coordinator command from the repository root (script supplied over SSH stdin;
no deployment into the sealed package is needed):

```sh
ssh clariden '/usr/bin/python3 - --runs /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-013-stage-c-sel/full/runs --out /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/train_full/attempts/full-v1-013-stage-c-sel/full/monitor' < docs/programme_20261025/TRAIN_FULL_v1/monitor/export_full.py
```

This command is provided for the coordinator; it has not been run remotely.
`clariden` is the coordinator's SSH host alias.

Each invocation replaces `full_loss.csv`, `full_cer.csv`, and `full_status.csv`
through a flushed/fsynced temporary file and `os.replace` in `--out`. Each CSV
is individually atomic; the three files are not a transactional set. Input
files can change while being read, so a snapshot can contain different instants.
Malformed JSON is reopened once, then skipped. Unterminated JSONL and CSV tails
are ignored. An output directory inside the input runs tree is rejected,
including paths resolving there through symlinks.

Loss points are deduplicated by step across the journal and per-point JSON;
the per-point JSON takes precedence. All emitted loss points use the actual
draw count, including the final partial 50k interval. Checkpoint SHA is the
checkpoint file SHA, not the model-state SHA. Only `eval/step-*.json` contributes
CER evaluations. CER draw counts are joined by exact step with loss/cadence,
LIVE, or the segment trace; no estimate from step times batch size is made.
Unknown values are blank. `pooled_dev.nfd_atom_cer` sums edits and reference
units over `harvest_dev` and `seal04_dev` exactly as Stage B. Its `rows` sums
those two panels; other pooled metrics are blank.

Run names and sibling `configs/` and `PLAN.json` identify queued runs before
they have output files. Copied PLAN references are resolved against local
`configs/`, rather than following the captured remote paths. Horizon values
prefer `LOSS_CADENCE.json`, then config, then the Stage C full-plan defaults:
12,691,632 drawn lines, 254 loss points, eight epochs of 1,586,454 rows, batches
256/256/64, and 49,584/49,584/198,312 updates for widths 1/1.5/2. Smoke inputs
use their own smaller cadence/horizon. `pct_complete` is drawn lines / target
drawn lines times 100; COMPLETE presence is reported independently.

`epoch_rows` counts complete rows in `train_log.csv`; `last_epoch` and `val_cer`
are its last row's epoch and validation CER. `segment_count` counts
`STARTUP_*.json` receipts (invocations reaching their first update), `yield_count`
counts `YIELD_*.json`, and `segment_trace_rows` counts trace entries, which can
be empty when production tracing is disabled. `last_update_utc` is the newest
mtime among usable loss records, using individual JSON mtimes where available
and the journal mtime for journal-only records. It is blank before any loss.

Local verification:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider docs/programme_20261025/TRAIN_FULL_v1/monitor/tests
```
