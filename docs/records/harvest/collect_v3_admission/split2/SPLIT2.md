# SPLIT2 final W1/W2 row allocation

Decision, owner via coordinator, 19 Oct night: SPLIT1 is adopted exactly as proposed. Every W1/W2 row takes its SPLIT1 proposed_split as its final split, with no changes. The forced editions stay test. This task converts it to the census split input (night plan step P1). It decides nothing.

Built 2026-10-19 23:51:40 EEST. `row_split.jsonl.gz` contains all 320,479 SPLIT1 rows, sorted by
(parent_id, row_id), with `split = proposed_split` and unchanged forced flags.
No admission, usability, class, source, or text filtering is applied.
`edition_map.jsonl` preserves forced reasons and leakage evidence verbatim from SPLIT1.

```json
{"split_input": {"path": "<deploy path>/row_split.jsonl.gz", "sha256": "7b27ab9b6f5c95ddf64c3346564310be76aacaf0f33f2b99b62420ad03a58b82"}}
```

The config hash covers compressed bytes. Gzip: mtime=0, empty filename, level=9.
Uncompressed SHA256: `5852e31bbd7af5e590770b3353c2b8ba3b1087081a3379fd4c5799479e6635d4`.

| Tranche | Source | Train | Dev | Test | Total |
|---|---|---:|---:|---:|---:|
| W1 | bsb_poly1850 | 9,777 | 0 | 2,997 | 12,774 |
| W1 | elstat | 1,839 | 0 | 3,205 | 5,044 |
| W1 | gazette_modern | 19,213 | 799 | 9,502 | 29,514 |
| W1 | ia_greek_latin | 9,752 | 0 | 2,003 | 11,755 |
| W1 | ia_poly1850 | 11,609 | 0 | 4,413 | 16,022 |
| W1 | ia_russian | 0 | 0 | 2,963 | 2,963 |
| W1 | kosmopolis | 4,645 | 226 | 485 | 5,356 |
| W1 | lekythos | 11,601 | 577 | 1,229 | 13,407 |
| W1 | nlg | 1,905 | 0 | 315 | 2,220 |
| W1 | serbia | 1,455 | 118 | 470 | 2,043 |
| W2 | bsb_poly1850 | 14,591 | 0 | 5,725 | 20,316 |
| W2 | elstat | 9,039 | 0 | 5,796 | 14,835 |
| W2 | gazette_modern | 110,207 | 4,992 | 3,834 | 119,033 |
| W2 | ia_poly1850 | 33,420 | 0 | 15,034 | 48,454 |
| W2 | nlg | 8,420 | 0 | 1,469 | 9,889 |
| W2 | serbia | 5,929 | 295 | 630 | 6,854 |
| All | All | 253,402 | 7,007 | 60,070 | 320,479 |

W1: 101,098 rows; W2: 219,381 rows. Editions: 1,359
(train 1159, dev 52, test 148).
Forced: 99 editions / 52,468 rows, all test.

The 436 BSB pages read after 05:24 are not in the 05:24 snapshots, so rows
from any later snapshot have no split entry (they stay unassigned in the census).

Load-through: 320,479/320,479 resolved with `prepare_config.prepare`,
the census04 loader used by the mock stage, the canonical row_splits key, and
census04's integration adapter. Unmapped rows: 0.
The retained package is in main-next's `docs/harvest/seg_census/package/`;
the mock script's relative `docs/records/.../package/` does not exist.
Imports disable bytecode writes; native segmentation is not launched.

Rebuild and test locally (no network):

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/harvest/collect_v3_admission/split2/build_split2.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts= -p no:cacheprovider docs/harvest/collect_v3_admission/split2/test_split2.py
```

See `GUARDED_COMMIT_LIST.md` for the exact staging allowlist. No commit or push is performed.
