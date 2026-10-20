# BENCH02F guarded commit list

Base BENCH02E: `d6d498792d49219cb30a48334377990f15d55ae4`. Prepared locally with network OFF, no spend, no submissions, no staging, no commit and no push. Only the exact paths below belong to this change. Preserve every unrelated tracked/untracked worktree change, including the supplied brief. Historical BENCH02E measurements and census02 draw artifacts are unchanged.

Coordinator rulings 1–5 are implemented: 2,460/615 class quotas; exact gate bbox/script adapter and two Serbian document IDs; confidence <0.89 and punctuation ≥1/3 or N1 leader/dash; density branch unavailable in the inspected producer; dev font quotas 13 small / 12 large; shared extract sbatch with separate census_03 mechanics / census_05 admitted-only command blocks. Class precedence and existing exclusions/caps are unchanged. No filter was added. Both jobs request 01:00:00 on one normal node because Clariden Lustre I/O is unmeasured.

Rounding record: nominal 20% overdraw is 3,690. Applying the existing ceiling separately to 13/12 gives 16/15 font candidates and 3,691 total targets, within P6's 3,700 checks. No class quota is reduced to hide the extra rounding slot.

Gate 0.3 does not emit a standalone cell flag or universal aspect A. The adapter repeats its exact `crop_aspect(row)` calculation from diagnostic `row.crop_bbox`: A=max(w,h)/min(w,h), cell_flag=A<=6. Decision `reasons[].A` is only emitted for single_character_cell. `raw_inventory.scripts` and script counts are emitted; prefer final_inventory when present. The separate numeric_cells.is_cell small-image descriptor is not the gate's flag. Ink density has no emitted field in the inspected producers, so confidence alone applies to census_05. Per-source density p25 computation and plan recording are tested with explicit synthetic density evidence; no physical proxy is substituted.

Read-only Serbian source: `git show sol/census-v2-serbian:greekocr/harvest/admission.py` at `504bdb1e13bed4883bd8d88c1ac3e795952d79c9`, SERBIAN_DOCUMENTS = cyrillic:7235f8d0, cyrillic:975289f3. Corroboration: the branch's `docs/harvest/collection/v2/census2_document_language.json`.

Validation: Python stdlib suite **34 passed** (20 original, six BENCH02E, eight BENCH02F); existing assertions updated only for the ruled behavior. Pinned baseline checks retain unaffected tags, precedence and quotas; full/slim draw parity uses the same new adapter. Filesystem audit: 141 writes checked, zero outside writes. Six shell scripts pass `bash -n`; `git diff --check` passes. No full census_03/census_05 draw, throughput claim or benchmark certification is made.

| Exact allowed path | Bytes | SHA256 |
|---|---:|---|
| `docs/harvest/collect_v3_admission/bench02/BENCH02D.md` | 22692 | `572d5b1fa6ec46ac0a44642183e103b53dd9759a128f32e7dc797fd020a3cd24` |
| `docs/harvest/collect_v3_admission/bench02/GUARDED_COMMIT_LIST.md` | self | review this file |
| `docs/harvest/collect_v3_admission/bench02/bench02_draw.py` | 30849 | `b2f33bfa6bc2f9a8122e348eb058b807a62d354be56143db25fde9f96711da6c` |
| `docs/harvest/collect_v3_admission/bench02/extract.sbatch` | 558 | `077fbfbc120ed205b80abc8e33c6020892621867566f1cff84671521e0174160` |
| `docs/harvest/collect_v3_admission/bench02/readout.sbatch` | 599 | `7fd6e98de83ac3ed696989bbafc54782ad386ab5465ed9f570935f54bd0f2b7a` |
| `docs/harvest/collect_v3_admission/bench02/run_dryrun_census03.md` | 4898 | `e371edebbf8eb290e54b7c5afc1c0878c843e3920cffca98411dc089ac2f9cc7` |
| `docs/harvest/collect_v3_admission/bench02/test_bench02_draw.py` | 10839 | `073dc2208d80aa15c6d9d96009c9d33a8d629fb740b5256021cdecad08fcbd62` |
| `docs/harvest/collect_v3_admission/bench02/test_bench02e.py` | 8915 | `a0ed07c664ecdcd684cd56840d8da19eef3cc59bf4c1f1f80c0130e36c893927` |
| `docs/harvest/collect_v3_admission/bench02/test_bench02f.py` | 6488 | `9349665686b4dd1ce59fa65ace0c052d4a6451539e55c1c36abf39b3bcf1afcc` |
| `docs/harvest/collect_v3_admission/bench02/tests.log` | 4054 | `02910db91e696f66869c314b8b15829f387d302402a6b491e722b80932d19ade` |

Read-only main-next producer/test input hashes (files were not modified):

| Path relative to main-next | SHA256 |
|---|---|
| `greekocr/harvest/line_pipeline.py` | `003b4085a7135d94d87d5d57e40544933f1185585b71bed978bb301884720ae1` |
| `greekocr/harvest/line_pipeline_census.py` | `9f346b5395eb20c75b1446ec0dd5f6d9f33a399495461557d27c6ada8c4af399` |
| `greekocr/harvest/line_pipeline_sources.py` | `d84f024f755d23543bd0b0601f14e2e7adae5d1eaadbc325e636bff3d628788e` |
| `greekocr/harvest/line_pipeline_adapters.py` | `90394534d583f0f93bfc18d83b13f2b35b918266b2794447d3b45a32daff0c63` |
| `greekocr/harvest/line_pipeline_native.py` | `e7dbe6c47061529953102b1af93422b593460e7510b22e27dbde69bcfbf052b7` |
| `greekocr/harvest/numeric_cells.py` | `36c1505fb3611687f4710ecdf1ebf234b1299ad34ff529586b05848a2cf0a8fe` |
| `tests/test_content_gate.py` | `1f448f9240662742a6f7e2c80a075cb60f4230837e48548fc941fa69f71f05e2` |
| `tests/test_numeric_cells.py` | `66652dae887c0f4a1dd58a783580e137e5de4392fcbe654d9da0b002ed5afc5b` |
| `tests/test_line_pipeline.py` | `32d950c2b7ef8b6d6b7758af84417b4d52c907c0ce2c7aa99798a2cc2faa2560` |

Before staging, rerun the tests and shell syntax checks and compare current hashes with the table. Stage only these exact paths individually, never a directory-wide add, `git add -A` or `git commit -a`. Check that the index has no unrelated changes, compare `git diff --cached --name-only` with this allowlist, then review `git diff --cached --check` and the complete staged diff. Stop if unrelated paths are staged. Staging/commit remain coordinator actions.

Suggested title: `BENCH02F: apply coordinator draw rulings and one-hour jobs`.

BENCH02F: done | rulings 1-5 applied | gate0.3 fields row.crop_bbox->A,cell_flag; raw_inventory.scripts | ink density field absent | serbian docs 2 | submit blocks census_03 + census_05 | tests: 34 passed
