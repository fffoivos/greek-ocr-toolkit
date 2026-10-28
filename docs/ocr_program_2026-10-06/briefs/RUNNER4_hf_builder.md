# RUNNER4 — canonical split rulings and HF CPU plan, 23 October 2026

## Owner/coordinator continuation, verbatim

> RESUME (00:24, book registry committed 3b06a6a87). COORDINATOR RULINGS on the 148 conflicts: (a) LQB (label-quality benchmark) and release_exclusion lists are LINE-level instruments: a book carrying LQB or release-excluded lines keeps split=train for the dataset, with per-row flags lqb_row / release_excluded_row (+ list name, hash); those books stay WHOLE-BOOK protected for NEW harvest pages (harvest_protection=true column, separate from split) — that is what the W3b validator reads; (b) the 1 train+hold_out book: investigate and report which assignment is authoritative (which file made it train, which made it hold-out, dates); do not resolve silently — set split=conflict_hold_out and harvest_protection=true until the coordinator rules; (c) the 309 no-split books: label each with its origin (harvested-not-admitted, superseded wave, W3/W4 pending) as split=unassigned_<reason>. Rebuild + tests + dry run; then NEXT: the HF build plan step 2 for Clariden (rows/crops/features/synthetic/references builder as a CPU job, credential-free; the token only in a separate foreground download step), written and mock-tested end to end on the one-book data — no submission, no upload. STOP "HF BUILDER READY".

## Execution scope and evidence

Sol edits only the RUNNER4 registry/spec/evidence, scripts/line_registry mock,
this brief, out/runner4 handoff and custody receipts. Small data outputs live in
/private/tmp; no sibling-worktree edits, Git metadata writes, jobs or network
transfers. Preserve concurrent RUNNER1 changes. The existing design/HF spec was
reviewed suitable by Astra; this continuation implements the coordinator rulings
and a plan/mock, not the held production build.

Inputs: RUNNER5 protected_registry_v3.json SHA
`a05814d9996b731cacd8fc4d986484a38fbc40d0cbb5359f130b81ab7e6a4c33`,
producer source commit f4795e8b0; SOURCE_MANIFEST.json SHA
`f468812a38687cad4aa025290c207ea9148eac2068aa721f7809f933e78c6578`;
Mac package manifest SHA
`8f2c43ff8d3d102850e7200529d0dab2c4408d490e4df21b0adc40bced0c5548`.
Registry BUILD_RECEIPT binds every other physical input path/size/SHA; the book
probe and HF_BUILDER_MOCK_RECEIPT bind retained remote evidence, code and outputs.

Outputs: book_registry artifacts/README/investigation, HF_REPO_SPEC.md,
HF_BUILDER_PLAN.md, portable exact row instruments, rebuilt book receipt,
offline mock code/tests/receipt, <=5-line STATUS.md and COMMIT_LIST.md.
Checks: registry identity/coverage/conflict and line-list tests; independent
rebuild equality; one-book PK/FK/split/release joins; mock credential rejection,
feature replay, payload preservation, shard cap, SQLite transport, tampering
and interrupted/resumed-versus-clean equality. Payload fixtures are explicitly
mock; no production custody or independent feature qualification is inferred.
