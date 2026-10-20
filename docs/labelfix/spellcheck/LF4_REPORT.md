# LF4 pairing by scope rank

Only the finalizer's in-quota traversal changed: slots are processed in ascending `scope_rank` within each quota scope. The existing same-source filter gives each source its flagged slots in ascending rank. Reserves still use explicit `overdraw_order`; eligibility, non-OK blocking, UNFILLED, vertical override, VOID handling, schema and receipt format are unchanged.

The new synthetic regression reverses slot draw order and reserve order, includes a non-OK reserve, another source, an unchanged OK slot, and reserve exhaustion. All 85 existing LF tests and the new test passed (86 total):

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B -m unittest discover -s artifacts/lf1/tools -p 'test_lf*.py' -v
```

Re-finalization used exactly the PROD_PLAN §4 finalize command below. No mapping, reader, image inspection, network operation, seal submission or `.git` write was performed. The sourcing checkout was read-only, with bytecode writes disabled.

```sh
PY=/Library/Frameworks/Python.framework/Versions/3.11/bin/python3
DRAW="$HOME/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/bench02/census05/candidates_v3.jsonl"
/usr/bin/arch -x86_64 "$PY" -B artifacts/lf1/tools/prod_finalize.py \
  --candidates "$DRAW" \
  --verdicts artifacts/lf1/prod/line_verdicts_merged.jsonl \
  --vertical-verdicts artifacts/lf1/prod/vertical_reread_verdicts.jsonl \
  --output artifacts/lf1/prod/final_list.jsonl \
  --receipt artifacts/lf1/prod/finalize.receipt.json \
  --details artifacts/lf1/prod/finalize.details.json \
  --bindings artifacts/lf1/prod/finalize.bindings.json
```

Input hashes were verified before finalization and remained unchanged afterward:

- candidates_v3: `0432c56f75ed1efded00b76e7aeabcc0a2bf9441bfad00e825e4e105006134c2`
- merged verdicts: `a203509cbd8105f4c7aeeba04f2ecc32fcb43662a26af8a87902c12b142d12e9`
- vertical re-read verdicts: `d914c6676fd4e0416abfb43cfab48f0ebba81a2357da077a5e54fec305c92fc6`

The four original outputs matched v1 byte-for-byte before finalization; v1 remained unchanged. Its final-list SHA-256 is `75fe0dbc396e57a7caa2946aa80f6aa7d85be4af8e41c7b2cef3cb8c29341ba7`.

Checks are recorded in `artifacts/lf1/prod/lf4_checks.json`, including every changed `replaces` value and all group results. The new list contains 2,691 unique `(parent_id,row_id)` keys, exactly equal to v1's set. Counts remain flagged 350, REPLACED 248, UNFILLED 102. Joined by row identity, only `replaces` differs, on 64 rows. Serialized row order also changes because traversal is sorted. The receipt changes only its dependent final-list hash; bindings change only dependent hashes. Side details retain all reasons, vertical records, VOID evidence, summaries and reserve exclusions, with pairing assignments, list order and the final-list hash updated.

An independent reconstruction from the unchanged draw and effective verdicts verified the pairing rule across 159 scope/source groups (91 with flagged slots). It checks sorted slot ranks against sorted eligible reserve orders, same-source membership, literal OK eligibility and exhaustion. The live result differs from the brief's preliminary group figures: 19 groups have changed assignments; no data or policy was adjusted to match the preliminary figures.

The local production seal check **ran and accepted** the new list: `build_suite02.final_checked(config, candidates, False)` returned 2,691 rows and 102 unfilled slots. Only this function was invoked; the sourcing suite was not built or submitted. Checker path: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/seal02/build_suite02.py`; SHA-256 `253921bfcdc72258ff69d80b02341c320f871e49b3ca054463910a09422da24c`.

## Three seal files

- `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/artifacts/lf1/prod/final_list.jsonl`
  SHA-256: `0fa4a1fe747e06dfeb9bdb4e6c1a8f3027140b4b160330c4ce07621a9315a08b`
- `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/artifacts/lf1/prod/finalize.receipt.json`
  SHA-256: `0001652776fd2e45261081bdeffd67b05749edec5a5abadd4162d3d893be6537`
- `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/artifacts/lf1/prod/line_verdicts_merged.jsonl`
  SHA-256: `a203509cbd8105f4c7aeeba04f2ecc32fcb43662a26af8a87902c12b142d12e9`

## LEAD_COMMIT_PATHS

- `artifacts/lf1/tools/prod_finalize.py`
- `artifacts/lf1/tools/test_lf4.py`
- `artifacts/lf1/prod/final_list.jsonl`
- `artifacts/lf1/prod/finalize.receipt.json`
- `artifacts/lf1/prod/finalize.details.json`
- `artifacts/lf1/prod/finalize.bindings.json`
- `artifacts/lf1/prod/lf4_checks.json`
- `artifacts/lf1/prod/tests_lf4.log`
- `docs/labelfix/spellcheck/LF4_REPORT.md`

LF4 READY: tests 86 passed; rows 2691 set-equal v1; REPLACED 248 UNFILLED 102; replaces changed 64; seal check ran yes ok
