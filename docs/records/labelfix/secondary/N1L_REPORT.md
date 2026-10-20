# N1-L evaluation lock

Frozen frame and document-lock SHA256s match step-0 validation. W1 also matches the step-0 SHA256. All checks pass: 300 slots (100 each ELSTAT, Gazette 1982–85, Gazette 1986–90), 248 unique locked W1 lines, 62 reserved documents and 8540 fitting-excluded lines across all pages. No locked or reserved line or document enters step1; no C1 card line enters the lock.

Original locked-line SHA256: `786e4a0ddce0ef9b95da6bd9ede49b309f14ba61516eefa3c523a557e9d1b07b`.

| Overlap with original lock | Lines |
|---|---:|
| wave_1d | 14 |
| r0_dev_eval_only_ids.txt | 0 |
| r0_ib_spellcheck_subset_ids.txt | 0 |
| r0_locked_eval_ia_wikisource_ids.txt | 0 |
| r0_locked_eval_ib_wikisource_ids.txt | 0 |
| r0_locked_eval_ids.txt | 0 |
| w1_elstat_separator_ambiguous_ids.txt | 0 |
| w1_rotated_crop_ids.txt | 4 |

Other exclusions contain 4 distinct locked lines (union; file counts may overlap). Alternative: written. When written, it uses seed `20261017:N1L:alt`, the same reserved documents, row schema and 100-slot quotas, draws 90 observed separator/table candidates plus 10 remaining per source, and excludes wave-1d and C1 lines. Remaining slots follow step-0 semantics and may themselves contain observed marks. The receipt records deterministic replay, pool sizes and alternative overlaps.

The original files remain unchanged. The sourcing lead must choose the original or alternative evaluation lock and register it; registration and step1 have not been performed. `load_locks` reads the original named lock and all reserved lines; the document-wide fitting exclusion covers both draws. Call `assert_fit_rows(ids)` before reading fitting data.

Tests: **29 passed**, using `python3 -m pytest --noconftest -q -p no:cacheprovider tests/test_numeric_locks.py tests/test_numeric_tokens.py` with bytecode disabled. Includes nonselected reserved lines, generators, allowed batches, missing/malformed files, inconsistent locks and immutability.

Local CPU and text metadata only. No network, image opening/decoding/rendering, collector writes, `run.lock` access, `.git` writes or exclusion registration. Live usage probe was not run under network OFF.

Full input/output hashes, counts, overlap IDs and check results: `artifacts/n1/N1L_RECEIPT.json`. Receipt SHA256 is not included in itself. `artifacts/n1/build_n1l.py` records the deterministic build and refuses to overwrite deliverables.
