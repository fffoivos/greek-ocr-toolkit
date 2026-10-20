# Scanner follow-up — AU1D

Bound scanner: v4.5.5 (`e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1`). No scanner change or verdict override was made.

`runs/capital_initial_001_au1c/scan.json` is VOID: unsupported view loops at records 17 and 34 (`const p of paths`) and record 51 (a JS literal-array loop).

P3 does not expand JS `for (const p of [literal array])` loops (record 51) — candidate v4.5.6 rule. Any proposed support must be qualified by the canonical scanner owner; the recorded v4.5.5 VOID remains in force. Returned image matches do not cancel unsupported-loop violations.

Current reader policy requires a separate explicit view call per image with a literal path, including when several explicit calls share one tool orchestration call. AU1D appends the W2C1 tool-use addendum and explicitly prohibits iterating over image paths, including literal arrays. This is a prompt repair, not evidence of a successful read.
