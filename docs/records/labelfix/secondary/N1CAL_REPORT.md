# N1-CAL calibration report

Verdict: **BLOCKED**. The launcher was invoked exactly once on 2026-10-17. The nested reader could not start inside the operator sandbox. No retry or workaround was attempted; no bed contexts were started.

Command (exit status 2):

```sh
scripts/secondary/reading/run_n1.sh n1cal cal01 r1
```

The nested reader log, `artifacts/n1/logs/N1-cal01.r1.codexlog`, contains:

```text
WARNING: proceeding, even though we could not create PATH aliases: Operation not permitted (os error 1)
Error: failed to initialize in-process app-server client: Operation not permitted (os error 1)
```

The launcher subsequently reported `run must identify rollout`. Its run receipt records `rc: 2`, `model: null`, an empty rollout path, `usage: null`, and zero reader tool calls. The exact underlying permission target is not identified in the error.

## Leak scan

**VOID**: scanner version 4 returned `ok: false`, with violation `missing rollout: .`. There is no reader rollout to certify. See `artifacts/n1/answers/cal01.r1.scan.json` and `cal01.r1.run.json`.

## Usage probes

```text
2026-10-17 16:09:39 before:n1cal/cal01.r1 limit_id=codex primary=0.0%/300m reset Fri 20:30 secondary=1.0%/10080m reset Wed 19:18
2026-10-17 16:09:40 after:n1cal/cal01.r1 limit_id=codex primary=0.0%/300m reset Fri 20:30 secondary=1.0%/10080m reset Wed 19:18
```

Weekly use: **1.0% → 1.0%**. The 78% stop threshold was not reached. Tokens per item: **unavailable**, because the reader never started and token usage is null. The launcher's ledger remains `[]`; its ledger validation failed on the missing rollout.

## Calibration and gate

No calibration output was produced. Per-class accuracy, the confusion matrix, low-confidence counts, and disagreements are **unavailable**, not zero.

| Class | Expected items (task specification) | Correct |
| --- | ---: | --- |
| Raised dot | 4 | unavailable |
| Baseline dot | 21 | unavailable |
| Comma | 23 | unavailable |
| Hyphen or dash | 27 | unavailable |
| Nothing | 7 | unavailable |
| Total | 82 | unavailable |

PASS/HOLD cannot be evaluated without answers. There is no disagreement list from which to build `n1_review/cal_disagreements.png`, so no sheet was generated. The operator did not open calibration images, keys, pack contents, or the approved controls.

The lead must run the launcher by hand after resolving the startup block. Existing failed-attempt files may trigger the launcher's overwrite guard; this operator has left them intact.

## Launcher configuration observation

The existing `run_read.sh` pins `gpt-6.1-sol` and medium effort through this invocation, but explicitly sets `sandbox_workspace_write.network_access=false` and disables web search. Thus the supplied launcher does not implement the requested network-ON reader configuration. No launcher files were changed.
