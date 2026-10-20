# SYNC2: make the frozen-greekocr test additive-aware on opus/cleanup-1 (gpt-6.1-sol, medium, network OFF; no .git writes)

SYNC1 merged opus/spellcheck into opus/cleanup-1 (merge commit b4234ee0e). The full suite then failed one new test,
`tests/labelfix/test_policy_frozen_after_merge.py::test_greekocr_sha256_list_matches_spellcheck`:
- that test requires ALL of `greekocr/` to equal the SF6c reference;
- cleanup-1 deliberately ADDS `greekocr/recogniser/` (CU3) and `greekocr/adjudicate/` (CU4);
- the cleanup rule is that nothing EXISTING in `greekocr/labelfix/` or the 16 policy paths changes.

**Lead ruling:** change the test, not the packages. The new test asserts:
- (a) every file in the reference `greekocr/` tree is present and byte-identical;
- (b) any extra file lies under a subpackage directory that does not exist in the reference (allowlist:
  `greekocr/recogniser/`, `greekocr/adjudicate/`). An extra file inside an existing reference directory fails.

List every extra file and which rule admits it. If CU3/CU4 changed any EXISTING reference file (e.g. `greekocr/__init__.py`), STOP and
report it; do not widen the rule for it.

**Tests:** a synthetic case for each rule (modified existing file fails; new file inside `greekocr/labelfix/` fails; new subpackage passes).
Then run the full suite: pre-existing failures only (test_collection_outputs 3, test_provenance_cli_api 2, test_apply_clean 5 errors).
Report the digest 6f62925a.

Last line: `SYNC2 READY: extra files <n> under <dirs>; existing reference files unchanged <yes>; suite <passed>/<pre-existing only>`.
