# T6g kosmopolis poly1850 qualification cards

Packed locally on `sol/recut-v1`, starting HEAD `9515ac609bb3ce7084b33f8a485be5e9eb919178`.
The guarded commit list binds HEAD `1a85772173ccae3853a7568319e31729fdfe6127`: two concurrent commits added only the T6h and T6f2 briefs; all T6g source inputs remained unchanged.
Draw and pack only: masking was not rerun and nothing was admitted.

- Pool: 462, from 473 poly1850 T6b outputs minus 11 previously drawn T6b cards. All 3,118 T6b records joined W1. No additional poly1850 rows were removed for output kind, screen_merged, or rotated_crop.
- Draw: 100 without replacement using `random.Random('t6g:kosmopolis:poly1850').sample` over the line-id-ordered pool. No length sorting. All 100 selected outputs are `masked`; the guarded-original branch is covered by tests.
- Reader context: `../cards_kosmo_poly1850/reader/`, with exactly `cards.jsonl`, `PROTOCOL.md`, and 100 independent crop copies in `crops/`. Its parent contains only `reader/`.
- Private key: `../cards_kosmo_poly1850_key.json`, two levels above the reader. It binds pool ids, source-input hashes, per-card original/masked/copied crop hashes, and output kind. Do not give the key or this handoff to the reader.
- Protocol SHA-256: `565423570d7e697ee1b875459302b222e9567128db2053896f124c990fc454e1`, byte-identical to the T6b v2 protocol.
- Execution: local files only, network OFF, inherited nice value 5. Sandbox denied attempts to change priority; the process already had reduced priority. Pack elapsed time: 1.901 seconds; the full task completed within 30 minutes.
- Validation: 16 tests passed (`tests.log`, `tests.xml`), including independent live-pool filtering, exact seeded draw reproduction, short pools, crop custody, frozen protocol, and isolation rejection cases.

`commit-inputs.json` is the guarded commit list. It binds the exact reviewed HEAD/branch and file hashes. All 100 PNGs remain git-ignored; the large input records remain local. Existing unrelated work is excluded. No staging or commit was attempted.

From the repository root, validate the list with:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/records/harvest/recut_v1/w1_masked/t6g/guarded_commit.py --check-only
```

The helper supports `--commit` for the coordinator's later commit, after exact HEAD, empty-index, source-input, crop, isolation, evidence and file-hash checks. A failed git operation is terminal; no retry or alternate index is used.

T6g: done | pool: 462 | cards: 100 | isolation: ok | tests: 16 passed
