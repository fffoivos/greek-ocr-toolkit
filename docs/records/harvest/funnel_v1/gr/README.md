# F1-GR evidence bundle

Start with [FUNNEL.md](FUNNEL.md), then [funnel.jsonl](funnel.jsonl).
This is access, physical-format and throughput verification only. It does not
perform OCR, admit training data, launch compute, send enquiries, or spend money.

The worker commit was blocked by the managed filesystem policy: shared Git
metadata is outside the writable worktree root. The refusal is recorded in
`receipts/commit-blocker.json`. From a normal shell in this existing worktree,
`python3 docs/records/harvest/funnel_v1/gr/commit_gr.py` verifies the branch, base HEAD,
clean staging area and every handoff digest before staging and committing exactly
these files. It never pushes. `bulk/F1-GR.patch` is the equivalent source-bound
patch for a clean checkout at the recorded base HEAD; bulk media is excluded.

- `candidates_<source>.jsonl`: accessible items, including explicit exclusions,
  fresh metadata bindings, rights records and overlap screening. An empty file
  means no page-access item was established. Counts are enumerated lower bounds.
- `probe_pages.jsonl`: fresh decoded page witnesses and hashes. The original PDF
  hash and page number bind each JPEG; original PDF bodies were discarded.
- `receipts/http.jsonl`: repository HTTP statuses, bytes, timings, hashes and safe
  headers. It contains no cookies, request bodies containing credentials, or tokens.
- `receipts/media.jsonl`: logical media attempts, including refusals, bounded
  failures, the concurrency checks and separate structural rechecks.
- `receipts/oa-projection-rebinding.json`: exact PDF-URL binding to the fresh HF
  table. The cached text projection's title/date/collection assignments are not
  trusted. Fresh catalogue rebinding receipts recover a subset independently.
- `receipts/physical-rechecks.jsonl`: refinement for opaque images covering OCR
  text drawn underneath. Only byte-identical PDFs can refine earlier witnesses.
  EKT-generated cover pages remain separate from original scanned content.
- `receipts/script-review.json`: manual script checks bound to page hashes.
- `receipts/validation.json`: artifact checks and the **retained pacing exception**.
  The exact audit retains 166 starts below the target spacing, with a minimum
  interval of 0.949 seconds. Strict pacing did not pass for the historical ledger;
  the corrected limiter
  and its new bounded concurrency run are recorded separately.
  A diagnostic robots.txt HEAD also omitted the contact User-Agent; see
  `receipts/operator-diagnostics.json`. It fetched no page body.
- `receipts/prior/`: copied inventory assessments, explicitly prior evidence.
  `receipts/input-files.json` binds the read-only source inputs by SHA256.
- `bulk/`: ignored HF table, transient catalogue bodies, grayscale JPEG witnesses
  and contact sheets. These are not committed. No credentials are stored here.

Offline rebuild from this completed evidence:

```sh
PYTHONPATH=. .venv/bin/python docs/records/harvest/funnel_v1/gr/curate.py
PYTHONPATH=. .venv/bin/python docs/records/harvest/funnel_v1/gr/report.py
PYTHONPATH=. .venv/bin/python docs/records/harvest/funnel_v1/gr/validate.py
```

Network probes are deliberately separate scripts. Do not batch rerun them against
this completed ledger: the Anemi budget was exactly 50 page requests for this run.
`anemi_probe.py` reuses the existing in-worktree, memory-only authenticated Anemi
transport; it never calls `pdf_dump.php`. `funnellib.py` adapts P1's acquisition,
rendering and sampling utilities. The copied `reference/` files are provenance
only and are not imported or executed; their original worktree paths are not used.

The page-rate benchmark is the first uninterrupted cohort of at least 50 decoded
pages over five items. Full wall spans, active-segment fallback, amortised page
latencies, PDF rates and concurrency cohorts are separately identified in JSONL.
No usable-row yield is inferred from these measurements. The source quotas remain
for a later pilot and coordinator decision.
