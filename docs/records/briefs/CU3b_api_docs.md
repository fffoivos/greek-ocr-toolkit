# CU3b: document greekocr.recogniser in the public API docs (gpt-6.1-sol, medium, network OFF)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-cleanup`, branch `opus/cleanup-1`; CU3's uncommitted work is present, so keep it).
- No `.git` writes.
- Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`.
- The same hard constraints as `docs/records/briefs/CU3_recogniser_api_phase1.md` (no pinned byte changes).

## Problem

`tests/test_provenance_cli_api.py::test_public_callables_typed_and_documented` now fails first on `greekocr.recogniser.run_shard`: it is
missing from `docs/API.md`. `scripts/generate_api_docs.py` raises `KeyError: 'run_shard'`, because its `CALLS` example table has no
entries for the new public callables.

On opus/spellcheck this test (and `test_all_vendored_files_are_in_inventory`) already failed for pre-existing reasons, `assert 4 == 2`
and `parliament_resolution.json`. Those are NOT yours to fix, but CU3 must not add new failure causes.

## Do

1. Add `CALLS` examples, following the generator's existing two-line example convention, for every public callable in
   `greekocr.recogniser` that `api_entries()` reports.
2. Give every public function return and argument annotations, as the test requires.
3. Regenerate the `greekocr.recogniser` part of `docs/API.md` with the generator. If the generator rewrites the whole file, keep its
   output, but confirm that every non-recogniser section is byte-identical to before, apart from ordering the generator itself imposes.
   Show the diff stat.
4. Re-run:
   - `tests/test_provenance_cli_api.py`: the remaining failures must be exactly the pre-existing ones (state them);
   - `tests/recogniser` and `tests/labelfix`.

   The frozen fixtures `artifacts/labelfix_sf6/frozen_sf5_05f2dafb` and `artifacts/labelfix_l1e/fixture_v4` are now present untracked in
   this worktree, copied by the lead. Report the full-suite counts, and compare them with opus/spellcheck's pre-existing failures:
   `tests/test_collection_outputs.py` (3), `tests/test_provenance_cli_api.py` (2), `tests/test_apply_clean.py` (5 errors). These are
   environmental/data and are not yours.
5. Update `docs/records/cleanup_20261017/CLEANUP_STEP3_REPORT.md`: test section and last line.

Last line:
`CU3 READY: …; tests <n> passed, failures only pre-existing <list>`
(or NOT READY with the reason).
