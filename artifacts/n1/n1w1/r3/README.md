# N1-W1-R3 replacement handoff

Prepared offline. No reader or account probe was launched. Network, browser and computer-use were not used; no .git writes.

16 replacement reader-contexts in 11 parent contexts: 11 r3 and 5 r4 packs. There are 1,218 missing candidate-reader positions plus 144 fresh controls, totaling 1,362 items. Estimated cost: 2.724 weekly points at the original preparation rate of 0.002 points/item, not measured usage.

The original finalisation has 13/28 VALID reader-contexts. `ctx04/r2` is VALID but leaves 72 candidate items unviewed; these are included. r4 supplies the second missing reader in ctx02, ctx05, ctx10, ctx12 and ctx14. Original packs, read evidence, review and decisions remain bound and preserved.

See `VOID_CAUSES.txt` for one line per affected reader-context. `routing.json` lists the exact logical reader positions covered by each replacement. For a partial VALID context, the finaliser retains its already viewed votes. A replacement supplies only the listed logical reader position; VOID, invalid, missing or unviewed replacement evidence remains HOLD. Original and replacement rollout reuse is rejected.

The new entry points are:

- `scripts/secondary/reading/run_n1w1_r3_all.sh --dry-run`: closure and schedule validation, no probes or reads.
- `scripts/secondary/reading/run_n1w1_r3_all.sh`: operator launch only, probes before each context, stops at weekly usage >=70%, permanent claim before launch, never reruns an attempted context.
- `scripts/numerics/n1w1_r3_finalize.sh --dry-run`: offline routing validation.
- `scripts/numerics/n1w1_r3_finalize.sh`: replacement-aware offline finalisation, staged under `r3/finalization` and scratch review `n1_review/n1w1/r3`. This is the finaliser entry point for replacements. It requires every replacement to have been attempted or an explicit 70% stop receipt.
- `scripts/numerics/n1w1_r3_finalize.sh --apply-lead`: the same routing plus the existing complete, pixel-checked lead requirements. Not executed during this preparation.

The scratch `n1_review/n1w1/sheets/index.md` and `index.json` index four contact sheets: 6/6/6/4 cells. Every cell contains the retained marked zoom, the smaller marked line, slot ID, and both saved reads. Each sheet repeats two approved raised-dot and two approved baseline-dot controls. References are approved controls, not necessarily from the candidate document. No candidate was adjudicated. Sheets were decoded and checked mechanically; no visual reading was performed.

All 16 replacement packs have sealed manifests and private keys under this directory. Closure checks enforce public schema, exact assignment order, fresh IDs and answer-letter permutations, distinct controls from earlier readers, content-hash image names, clean decodable PNGs, regular independent files and no extra public files. New code and routing are hash-bound in `build.json`.

The original pre-read accounting test is deselected because it asserts that `answers/` and `review.json` do not yet exist; F1 has already created both. Other original N1W1 tests and the new offline replacement tests are included in `TESTS.xml`.
