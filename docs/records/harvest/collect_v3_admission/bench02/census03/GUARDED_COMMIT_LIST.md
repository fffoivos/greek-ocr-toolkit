# BENCH02G guarded commit list

Review-only allowlist; no staging, commit or push performed. Stage only these exact paths after checking bytes and hashes. Never use `git add .`, `git add -A`, or a recursive census03 directory add. Preserve all unrelated existing workspace changes.

| Path | Bytes | SHA-256 |
|---|---:|---|
| `docs/briefs/BENCH02G_census03_dry_draw.md` | 2348 | `50fa069de55546dc344192750cee6b8f625014c01cf793b3b3b689aa65dca853` |
| `docs/harvest/collect_v3_admission/bench02/census03/DRYRUN_CENSUS03.md` | 37286 | `8caee1f9fb4583c503f09872c296009831f1d0b420803bb2eb909b2517972851` |
| `docs/harvest/collect_v3_admission/bench02/census03/dryrun/COUNTS.md` | 2300 | `035c84fcfb7786a3705eccc9f8f290cc520e60e5f6749d41866242a24ddf3532` |
| `docs/harvest/collect_v3_admission/bench02/census03/dryrun/candidates.jsonl` | 361224 | `5cd95d9dc07edec2abe63c9ec3a8cc238b8104d79b7cfe4532c4d89de26b48a3` |
| `docs/harvest/collect_v3_admission/bench02/census03/dryrun/counts.json` | 1064225 | `518f44fe33a9b8b9ac187ee6cc6d6b6610db32cbb95d6dab4e22ae80867070a8` |
| `docs/harvest/collect_v3_admission/bench02/census03/dryrun/draw_plan.json` | 7424 | `91456055d3643431e081aef6d7cf9316239433b753f12e0b38c46624a42abffc` |
| `docs/harvest/collect_v3_admission/bench02/census03/status_line.txt` | 712 | `593751f08385b50d173a0debb6ee403354251ceffeb2f72d2dbd5a4cc530493d` |
| `docs/harvest/collect_v3_admission/bench02/census03/tags.jsonl.receipt.json` | 654 | `00ffb31cca553319bed7372a38405f8689158e5c7355ff45f4930f2cc42e3163` |
| `docs/harvest/collect_v3_admission/bench02/census03/verification.json` | 2934 | `8efbe5fcdbde8bfa84f63d4a93f9457215e47b0a9cc4af660464b2094d906672` |

Also include this guarded list itself (self-hash intentionally omitted).

Excluded large file: `docs/harvest/collect_v3_admission/bench02/census03/tags.jsonl.gz` (32,741,890 bytes); leave untracked. Its local SHA-256 is in `DRYRUN_CENSUS03.md` and `verification.json`. Candidates are 361,224 bytes and included. No code files, prior bench02 files, unrelated working-tree changes or external inputs are in scope.
