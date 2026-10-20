# F2-GR evidence bundle

Start with [REPORT.md](REPORT.md). The final cohort has 30 pages per source,
except Anemi's 20. The Google ledger includes all attempts, including the
withdrawn ELSTAT book-only sample; no local reservation is refunded.

- `population_*.jsonl` and `population_government-gazette.jsonl.gz`: catalogue
  frames, with exact overlap exclusions and clear scope/lower-bound limits.
- `draw_*.jsonl`, `verification_*.jsonl`, `survey.jsonl`: seeded A0 draws,
  one-leaf outcomes, Wilson intervals and capped page estimates. OA is sampled
  and estimated per collection. Supplemental items never enter the survey k/n.
- `pages.jsonl`: every final native page and its physical/machine diagnostics.
- `sources.jsonl`, `lines.jsonl`, `class_funnel.jsonl`: disjoint pipeline yield,
  compact line dispositions and conditional quota projections. Full provider
  responses and full derived line records are ignored under `google/` and `bulk/`.
- `blind_pages/` and `label_cards/<source>/cards.jsonl` plus `crops/`: checker
  input. Do not show `blind_pages_key.json` or `label_cards/<source>_key.json`
  to the blind checker. All 40 admitted cards per source retain Google's text;
  codec/geometry status lives only in the separate key.
- `receipts/local-google-review.json`: explicitly unblinded local spot review,
  including residual multi-row candidates cleared by G1b. No training labels
  were admitted or released. The coordinator's independent checks remain pending.
- `receipts/anemi-pacing-audit.json`: retained historical pacing exception and
  the subsequent shared-guard correction. Viewer attempts remain capped at 50.
- `reference/`: hash-identical P1 routines and Git-restored G1b sources.
  They are provenance, not standalone acquisition/read entrypoints.

Offline rebuild, with the ignored local rasters and response caches present:

```sh
PYTHONPATH=. .venv/bin/python docs/records/harvest/sample_v1/gr/enrich_machine.py
PYTHONPATH=. .venv/bin/python docs/records/harvest/sample_v1/gr/handoff.py
PYTHONPATH=. .venv/bin/python docs/records/harvest/sample_v1/gr/report.py
PYTHONPATH=. .venv/bin/python docs/records/harvest/sample_v1/gr/validate.py
```

Paid reads use only `process.py read <source>`, with `google/ledger.jsonl` as a
cross-process, fsync-reserved USD 1.00 lifetime cap for this track. Do not reset,
truncate or remove that ledger. No retry of a reserved/ambiguous attempt is made.
The runner uses ADC and strips embedded response images before writing them.
There is no training, push, publication, account-change or cloud-launch step.

The commit helper checks the exact branch, base HEAD, empty staging area and
all final handoff hashes before staging only this output's non-media files.
If managed permissions block shared Git metadata, its receipt and a source-bound
patch record the handoff; run `commit_gr.py` only from an ordinary owner shell.
