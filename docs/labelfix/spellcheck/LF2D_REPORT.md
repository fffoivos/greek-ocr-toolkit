# LF2d report — READY

Completed 20 October 2026. Implements the coordinator's ~06:05 replacement ruling, superseding the source-fallback sentence in LF2b/LF2c. Network remained off. No .git writes, reader runs, crop display, label judgment, production finalization, pack rebuild, transfer or submission occurred. Batch 2 remains unread. Sourcing files were read-only.

## Replacement ruling

`prod_finalize.py` retains explicit `in_quota` membership and exact `quota_scope` isolation. Each flagged original gets only the next unused reserve of the same source, ordered by `overdraw_order`, with literal `OK`. Exhaustion is `UNFILLED`, even when another source has available OK reserves. Every non-OK reserve, including a missing verdict, is marked used and never promoted. `FALLBACK_SOURCE` is removed from the implementation and tests. No rule, guard, threshold or heuristic was added. The LF1 replacement hook is unchanged.

Existing original-slot iteration is retained. Side receipts preserve each flag's verdict, reasons, locations and state, replacement source/order, blocked reserves and scoped counters, including unresolved and VOID_TWICE separately.

## Seal02 interface

Read sourcing's `FINAL_LIST.schema.json`, `SEAL02.md`, `build_suite02.py` and `test_seal02.py` under `~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/seal02/`. The schema SHA was verified as `ec430f1460fa9d35ccc581ee9408efdf6be03a69e73d14765563520d7ebf972f`; sourcing commit `e6365239b` is the coordinator-provided identity.

CLI output rows now contain exactly `parent_id`, `row_id`, `split`, `quota_scope`, `lf1_verdict: "OK"`, `replaces`, `lf1_receipt_ref` and `mock: false`. `replaces` identifies the original flagged parent/row, or is null for retained originals. Receipt references bind the selected line ID to the merged ledger SHA. Raw candidate fields and labels are omitted.

The companion receipt contains exactly `status: "FINALIZED"`, `mock: false`, `final_list_sha256`, `verdicts_sha256`, `candidates_sha256`, and `counts: {flagged, REPLACED, UNFILLED}`. Flagged equals REPLACED + UNFILLED. Candidate SHA is computed from input bytes; the production v3 draw identified in LF2c yields the requested `0432c56f75ed1efded00b76e7aeabcc0a2bf9441bfad00e825e4e105006134c2`. Production candidates were not finalized to demonstrate this. The synthetic receipt correctly binds its synthetic draw instead of claiming the production hash.

The schema agrees with the summarized fields and forbids additional properties. Two details are broader than the coordinator's production summary: `mock` permits either Boolean value, and `candidates_sha256` is any lowercase 64-hex digest. Emission uses false and the actual input digest. LF1 flag reasons are therefore retained in a separate side receipt. Optional CLI arguments `--details` and `--bindings` select those output paths; defaults are RECEIPT.details.json and RECEIPT.bindings.json. The latter binds exactly the final list, companion receipt and unchanged merged verdict ledger, each with an absolute path and SHA-256.

## Synthetic validation and sourcing checks

**69 tests passed:** 64 LF1/production regression tests and 5 new offline integration tests. Logs: `artifacts/lf1/prod/tests_lf2d.log` and `artifacts/lf1/prod/seal_checks_lf2d.log`.

The persistent end-to-end fixture is isolated under `artifacts/lf1/prod/lf2d_synthetic/`. All candidate identities and verdicts are invented. Its `mock: false` values exercise the requested production-shaped interface; these files are synthetic evidence, never production results. Four originally flagged slots produce one REPLACED and three UNFILLED; two rows survive. A non-OK reserve is recorded used; a foreign-source OK reserve is left unpromoted.

Executed locally with sourcing unchanged:

- Draft 2020-12 schema self-check and validation of every emitted row and the receipt definition, plus pinned schema SHA verification.
- Sourcing's actual `build_suite02.final_checked` on CLI-produced fixture files: complete ledger, exact row/receipt interfaces, hashes, OK verdict references, replacements and UNFILLED accounting accepted.
- Sourcing's same checker rejects a foreign-source promotion and a non-OK final verdict.
- A contradictory-order witness checks the boundary described below. Three-file SHA bindings and LF1 side-receipt reasons are also verified.

**Sourcing discrepancy:** `build_suite02.final_checked` sorts reserves by `scope_rank` and original slots by `scope_rank`; its test suite likewise selects reserves by that rank. LF2d must use `overdraw_order` for reserves, and keeps the existing original-slot iteration. The main fixture has aligned ranks/orders and passes sourcing. A second fixture deliberately reverses the two reserve orders: LF2d correctly selects by `overdraw_order`, the row schema accepts that format, and sourcing rejects the selection. This is a documented compatibility limitation when those orders disagree, not a new selection rule or a claim of universal seal acceptance. No sourcing code was modified. `SEAL02.md` also describes a rank-derived membership boundary, while LF2c/LF2d retain explicit `in_quota` as instructed.

The full sourcing `test_seal02.py` suite, image verification, package build and deployment checks were not executed. The checks above directly call its read-only final-list validation function and use synthetic files; no real candidate labels or PNGs are needed.

Synthetic three-file seal bind:

| File under `artifacts/lf1/prod/lf2d_synthetic/` | SHA-256 |
|---|---|
| `final_list.SYNTHETIC.jsonl` | `95cc09eda58498d1a9e024206f678ec680caed0c1df0c3cce138492050863c4b` |
| `final_receipt.SYNTHETIC.json` | `ab2d5b1a4240cd694b8c903f24bbe8dbe0b43bb9c48609a7d8302bfea704e1e5` |
| `line_verdicts_merged.SYNTHETIC.jsonl` | `37ea8d0395a9243b86516b50b287620a572c92a2f32b65c4ae05d6437d26a24f` |

Reproduce offline from this checkout:

```bash
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B artifacts/lf1/tools/test_lf1.py
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B artifacts/lf1/tools/test_lf2d.py
GIT_OPTIONAL_LOCKS=0 git diff --check
```

Both test runs passed; whitespace validation passed. The existing regression suite rewrites its legacy synthetic scanner receipts; these are fixture outputs, not reader results. `PROD_PLAN.md` now records the revised ruling, seal interface, side receipt and three-file bindings, prepared finalization commands and the sourcing discrepancy. Its production commands were not executed.

## LEAD_COMMIT_PATHS

Exact LF2d handoff paths; no staging or commit performed:

- `artifacts/lf1/tools/prod_finalize.py`
- `artifacts/lf1/tools/test_lf1.py`
- `artifacts/lf1/tools/test_lf2d.py`
- `artifacts/lf1/prod/PROD_PLAN.md`
- `artifacts/lf1/prod/tests_lf2d.log`
- `artifacts/lf1/prod/seal_checks_lf2d.log`
- `artifacts/lf1/prod/lf2d_synthetic/candidates.SYNTHETIC.jsonl`
- `artifacts/lf1/prod/lf2d_synthetic/line_verdicts_merged.SYNTHETIC.jsonl`
- `artifacts/lf1/prod/lf2d_synthetic/final_list.SYNTHETIC.jsonl`
- `artifacts/lf1/prod/lf2d_synthetic/final_receipt.SYNTHETIC.json`
- `artifacts/lf1/prod/lf2d_synthetic/final_receipt.SYNTHETIC.json.details.json`
- `artifacts/lf1/prod/lf2d_synthetic/final_receipt.SYNTHETIC.json.bindings.json`
- `artifacts/lf1/prod/lf2d_files.sha256`
- `docs/labelfix/spellcheck/LF2D_REPORT.md`

All pre-existing LF2c and unrelated paths are outside this handoff. The hash manifest covers the listed files except itself.

LF2d READY: tests 69 passed; fallback removed; seal schema valid on fixture (seal checks ran: build_suite02.final_checked acceptance, foreign-source/non-OK rejection, ordering-discrepancy witness)
