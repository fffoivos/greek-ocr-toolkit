ADMW2 completed on the existing geometry with the coordinator-accepted screens from aa3d9067. The six admission/geometry consumers are byte-identical to that commit; no history was rewritten. W2 and Gazette files are ready, and the separately named W1 screened files are ready. The existing W1 admitted file remains byte-identical.

W2: **75,244 → 8,139 admitted**, with 65,245 geometry-unavailable rows (86.71%). Gazette W2: **40,804 → 5,411**. W1 screened: **32,205 → 3,280**, with 28,314 unavailable.

Staging verified **3,102 existing admitted crops / 37,400,966 bytes (0.037 decimal GB)**. New crop images written: **0**. The 10 GB floor deferred **8,317** crops (178 W1 and 8,139 W2). These are explicit deferred rows, not staging verification failures. Both staging runs returned the expected disk-deferred status 2 with zero failures. The shared manifest retains 28,798 original entries; no crops were deleted. W2 staging began with 1.763 GB free and ended with 1.753 GB free. Admission outputs are not reduced to staged-only rows.

The shared Git index is outside the writable sandbox: ordinary git add failed with Operation not permitted. The additive commit is packaged in [ADMW2.bundle](ADMW2.bundle), with parent HEAD 914c5ce62; this task did not update the shared branch or index. Coordinator review/brief commits advanced HEAD from 464283eae during the run, and the bundle preserves them. The external [commit list](ADMW2_COMMIT_LIST.json) records its actual commit, parent, file hashes, and bundle verification. A [code patch](ADMW2_CODE.patch) is also supplied. Existing pending manifest-retention changes in stage_crops.py were preserved and extended; unrelated working-tree edits and geometry caches are excluded.

Both read-only snapshot hashes match SHA256_20261018_0524.txt: W1 c85b407a724f4a17dfbe659cc9e2dfd171660de5e29baf1fd86b291f7cbd9c4c; W2 4954a94cc3c051aeb36e367101bc3448233448422bb05834d3276e090de987b4. Every registered line-level exclusion file was hash/count verified. All ten registered classes are removed, including crop-rejection classes. W1 removes 1,096 qualified rows; W2 removes zero. There is no W1/W2 row-ID or page-key overlap. See [population audit](admw2/population_audit.json) and [accepted-code verification](admw2/input_verification.json).

W2 follows W2C1 ed074681: the seven listed C1 source/class pairs and measured_1986_1990 Gazette modern_scanned, plus headings_caps across those sources under the carried CAPS4 W1 ruling. This snapshot has zero eligible W2 headings_caps rows. W1 retains ADM4’s additional qualified kosmopolis/lekythos strata and CAPS4 headings. Candidate_usable must be the boolean true. Registered primary classes drive release text variants; page medians use every snapshot row before population/exclusion drops. Historical screen flags are not reused as fresh decisions.

The builder combines admission text/metadata checks with unchanged CP3/CP4 structural evidence and CP5 regional orientation/crossing composition. Unknown orientation admits for that screen; missing caches are reported as orientation not_run, not falsely horizontal or measured unknown. Geometry unavailable fails closed. Only a definite composed KEEP admits. W1 also has three unresolved composition drops; crossing drops are zero. CP5pb edge_clip_candidate is diagnostic only. Column separators are measured in memory from existing geometry; no detector, OCR, OSD, recognizer, reader, geometry-preparation run, live-feature read, or live-root write ran. Network was disabled by the builder audit guard.

The geometry index covered CP3 (24 receipts), CP4 (1), shared CP7 r1/r2 (187), optional geometry_prep (absent), and read-only live g1b (76). Cache candidates were bound by full source path/hash and passed through CP2, including payload hashes, detector identity/options, frame, masks/labels, and row geometry. Invalid caches were rejected rather than repaired or silently used. Chosen full bindings and all rejected attempts are in each receipt. No (b) full-population geometry run was launched.

Rule counts below overlap. Each JSON receipt also records disjoint first_drop counts, so pre-screen = admitted + first-drop sum. Orientation unknown and edge candidates are diagnostics, not drop counts. Unavailable share uses the entire pre-screen denominator.

**W2: source × registered primary class**

| source | class | pre-screen | text | merged | neighbour | orientation | unavailable | admitted | unavailable % | orient. unknown | edge candidate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bsb_poly1850 | poly1850 | 6775 | 0 | 1 | 0 | 0 | 6326 | 448 | 93.37 | 14 | 7 |
| elstat | numerics_tables | 7250 | 3529 | 6 | 5 | 212 | 4365 | 1182 | 60.21 | 2655 | 15 |
| gazette_modern | modern_scanned | 40804 | 957 | 136 | 126 | 125 | 35238 | 5411 | 86.36 | 333 | 55 |
| ia_poly1850 | poly1850 | 9321 | 67 | 0 | 0 | 0 | 8684 | 637 | 93.17 | 24 | 12 |
| nlg | greek_poly | 702 | 0 | 0 | 0 | 0 | 702 | 0 | 100.00 | 0 | 0 |
| nlg | poly1850 | 3230 | 4 | 0 | 0 | 0 | 3116 | 114 | 96.47 | 17 | 1 |
| nlg | poly1900 | 2108 | 13 | 0 | 0 | 0 | 2064 | 44 | 97.91 | 13 | 3 |
| serbia | cyrillic | 5054 | 30 | 0 | 0 | 0 | 4750 | 303 | 93.98 | 3 | 1 |

[Per-row decisions](w2_originals_v3_admission.jsonl.gz) · [Admitted rows](w2_originals_v3_admitted.jsonl) · [Receipt](w2_originals_v3_receipt.json)

**Gazette W2: source × registered primary class**

| source | class | pre-screen | text | merged | neighbour | orientation | unavailable | admitted | unavailable % | orient. unknown | edge candidate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| gazette_modern | modern_scanned | 40804 | 957 | 136 | 126 | 125 | 35238 | 5411 | 86.36 | 333 | 55 |

[Per-row decisions](gazette_w2_originals_v3_admission.jsonl.gz) · [Admitted rows](gazette_w2_originals_v3_admitted.jsonl) · [Receipt](gazette_w2_originals_v3_receipt.json)

**W1 screened: source × registered primary class**

| source | class | pre-screen | text | merged | neighbour | orientation | unavailable | admitted | unavailable % | orient. unknown | edge candidate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| bsb_poly1850 | headings_caps | 46 | 0 | 0 | 0 | 0 | 43 | 3 | 93.48 | 2 | 0 |
| bsb_poly1850 | poly1850 | 3823 | 0 | 0 | 0 | 0 | 3401 | 422 | 88.96 | 28 | 3 |
| elstat | headings_caps | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0.00 | 1 | 0 |
| elstat | numerics_tables | 2552 | 1215 | 6 | 6 | 23 | 1104 | 904 | 43.26 | 1407 | 0 |
| gazette_modern | headings_caps | 1789 | 81 | 2 | 2 | 0 | 1583 | 192 | 88.49 | 70 | 2 |
| gazette_modern | modern_scanned | 7783 | 22 | 7 | 6 | 0 | 7179 | 596 | 92.24 | 132 | 4 |
| ia_greek_latin | headings_caps | 6 | 1 | 0 | 0 | 0 | 6 | 0 | 100.00 | 0 | 0 |
| ia_poly1850 | headings_caps | 61 | 7 | 0 | 0 | 0 | 60 | 0 | 98.36 | 1 | 0 |
| ia_poly1850 | poly1850 | 1967 | 17 | 1 | 1 | 0 | 1884 | 82 | 95.78 | 0 | 0 |
| kosmopolis | headings_caps | 63 | 1 | 0 | 0 | 0 | 58 | 5 | 92.06 | 1 | 0 |
| kosmopolis | poly1850 | 473 | 0 | 1 | 0 | 0 | 323 | 149 | 68.29 | 10 | 0 |
| kosmopolis | poly1900 | 2692 | 0 | 7 | 4 | 0 | 2487 | 198 | 92.38 | 21 | 0 |
| lekythos | headings_caps | 209 | 14 | 1 | 1 | 0 | 176 | 29 | 84.21 | 12 | 0 |
| lekythos | poly1900 | 8072 | 2 | 29 | 25 | 0 | 7413 | 628 | 91.84 | 61 | 3 |
| nlg | greek_poly | 196 | 0 | 0 | 0 | 0 | 173 | 23 | 88.27 | 0 | 0 |
| nlg | headings_caps | 33 | 2 | 0 | 0 | 0 | 33 | 0 | 100.00 | 0 | 0 |
| nlg | poly1850 | 782 | 0 | 0 | 0 | 0 | 782 | 0 | 100.00 | 0 | 0 |
| nlg | poly1900 | 430 | 0 | 0 | 0 | 0 | 382 | 48 | 88.84 | 14 | 1 |
| serbia | cyrillic | 1227 | 11 | 0 | 0 | 0 | 1227 | 0 | 100.00 | 0 | 0 |

[Per-row decisions](w1_originals_v3_screened_admission.jsonl) · [Admitted rows](w1_originals_v3_screened_admitted.jsonl) · [Receipt](w1_originals_v3_screened_receipt.json)

Files larger than 50,000,000 uncompressed bytes are deterministically gzipped. Both W2 and Gazette decision files meet that threshold; other release files are below it. Each receipt records stored SHA-256 and uncompressed SHA-256/byte count.

**Builder and validation**

[build_release_admission.py](build_release_admission.py) supports --tranche W1|W2|all --geometry <dirs…>. Default roots include future geometry_prep when present. Rerunning after owner-authorized (b) regenerates the same file names; staging is then rerun with --extend --minimum-free-gb 10. Exact offline commands are in [RERUN.md](admw2/RERUN.md).

532 distinct tests passed: 496 admission/SEG regressions, 31 builder/staging tests, and 5 full real-artifact tests. The 526-test earlier run includes the previous 30 builder tests; it is not double-counted. See [test summary](admw2/test_summary.json), [regression log](admw2/tests.log), [final builder tests](admw2/builder_tests.log), [artifact tests](admw2/artifact_tests.log), and [full verification](admw2/verification.json). Full artifact checks compare exact population IDs, all stored/uncompressed hashes, Gazette row equality, overlapping/disjoint counts, staged crop bytes and deferred coverage. The protected original W1 admitted SHA-256 remains b6d13fa8bb4b07be632e299fd650cd75dd80348ecf0e0fd9e5cb34bdb6c72bfe.

ADMW2: done | W2 pre-screen 75244 -> admitted 8139 (geometry_unavailable 65245, 86.71%) | gazette W2 40804 -> 5411 | W1 screened 32205 -> 3280 (unavailable 28314) | staged 3102 crops (0.037 GB) | builder ready | tests: 532 passed
