# DISK1 disk cleanup

Completed 2026-10-17T22:24:53+0300. Network was not used. No `.git` writes were performed.

Removed **8,191 PNG files**, totaling **0.244 GB logical bytes** and **0.261 GB allocated blocks** (decimal GB). The readiness line uses allocated blocks. APFS clones, snapshots, and concurrent activity can make the actual free-space delta differ.

Scope abbreviations: `W = /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-secondary`; `S = /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad`.

Audit/report artifacts created by DISK1 occupy 0.131 GB. Gross removed allocation is 0.261 GB; estimated net allocation reduction after this audit overhead is 0.130 GB. The readiness line reports gross deleted allocation.

## Inventory and method

Initial `du -k` inventory: W 7,043,672 KiB; S 1,182,832 KiB. W/sol_packs was empty. The per-file candidate inventory records sizes, SHA256, delete/keep decisions, and sampled citation evidence in [DISK1_FILES.jsonl](DISK1_FILES.jsonl). The full pre-deletion plans and execution receipt are retained under S as `disk1_inventory.json`, `disk1_final_plan.json`, and `disk1_removed.json`.

Scanned all scratchpad and artifacts text, secondary reports, all worktree receipts/manifests/indexes/provenance/input/source/mapping/build/closure/hash records, and worktree Markdown/code/config text for image paths and SHA256 references. Large corpus payloads that are not receipt/manifest records were excluded. Resolved reader-relative manifest paths and sheet filenames. Read W1/features.jsonl crop metadata without modifying the collector. Every removed crop had a byte-identical source at a recorded collector/cache location; retained anchors were protected from selection and rehashed before and after deletion. Completion required matching item and answer ID coverage. A citation without a retained identical copy forced KEEP. No caches were deleted solely on a claim that ensure_crop could reproduce them.

All 618 preexisting ru2t files remain; observed changed files during the active reading: 1. No ru2t path entered the deletion set. Answers, keys, receipts, manifests, label/decision JSONL, truth, reports, briefs, source, tests, and tracked files were excluded. Every deletion was an individual PNG unlink; only empty image directories were then removed.

## Candidate classification

| Category | Decision | Files | Logical GB | Reason |
|---|---|---:|---:|---|
| cache_crop | delete | 28 | 0.000922 | verified SHA256 duplicate of retained recorded/cited source |
| cache_crop | keep | 1420 | 0.035928 | cited by path or SHA; no identical-sha retained cited copy |
| cache_crop | keep | 361 | 0.016714 | retained cited/source SHA256 anchor for deleted duplicates |
| cache_render | keep | 2786 | 0.055357 | cited by path or SHA; no identical-sha retained cited copy |
| cache_render | keep | 4045 | 0.111450 | retained cited/source SHA256 anchor for deleted duplicates |
| pack_crop | delete | 8162 | 0.242681 | verified SHA256 duplicate of retained recorded/cited source |
| pack_crop | keep | 10720 | 0.259721 | reading completion not proven by matching item/answer IDs |
| pack_zoom | keep | 1240 | 0.242332 | cited by path or SHA; no identical-sha retained cited copy |
| sheet | keep | 396 | 0.126702 | archived runtime/reference image, outside approved contact-sheet category |
| sheet | keep | 40 | 0.030566 | cited by path or SHA; no identical-sha retained cited copy |
| test_png | delete | 1 | 0.000005 | uncited regenerable contact sheet/zoom/test image |

Tracked mock and validation output inventories:

| Path | Files | Logical MB | Decision |
|---|---:|---:|---|
| `W/artifacts/labelfix_l1e/fixture_v4/mock` | 24 | 10.645 | KEEP: 24 tracked files; retain fixtures/evidence. |
| `W/artifacts/ru1/scanner_tmp` | 0 | 0.000 | KEEP: 0 tracked files; retain fixtures/evidence. |
| `W/docs/labelfix/spellcheck/clariden/L1R_evidence/mock` | 35 | 2.383 | KEEP: 35 tracked files; retain fixtures/evidence. |
| `W/docs/labelfix/spellcheck/clariden/L1F_evidence/mock_receipts` | 6 | 0.048 | KEEP: 6 tracked files; retain fixtures/evidence. |
| `W/docs/labelfix/spellcheck/clariden/L1E_evidence/remote_readback/heldout_final/mock` | 1 | 1.051 | KEEP: 1 tracked files; retain fixtures/evidence. |
| `W/docs/labelfix/lqb/validation` | 79 | 8.944 | KEEP: 79 tracked files; retain fixtures/evidence. |
| `W/docs/reviews/astra_program_review_2026-10-06/ASTRA-SC1c3_evidence/recomposed_mock64` | 18 | 0.845 | KEEP: 18 tracked files; retain fixtures/evidence. |

## Removed paths

Rows group only the individually deleted PNGs in each parent directory. A row does not imply removal of the entire directory or its protected metadata; exact deleted paths, sizes, hashes, and retained copies are in DISK1_FILES.jsonl.

| Parent path | Removed PNGs | Logical MB | Allocated MB | Regenerability evidence |
|---|---:|---:|---:|---|
| `S/.` | 1 | 0.005 | 0.008 | uncited regenerable contact sheet/zoom/test image |
| `S/ru1_cache/crops` | 28 | 0.922 | 0.987 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1/ctx01/r1/img` | 178 | 4.049 | 4.424 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1/ctx02/r1/img` | 178 | 3.699 | 4.043 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1/ctx03/r1/img` | 178 | 3.950 | 4.309 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1/ctx04/r1/img` | 178 | 4.343 | 4.710 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1/ctx05/r1/img` | 178 | 3.491 | 3.842 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1/ctx06/r1/img` | 176 | 3.476 | 3.846 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1/ctx07/r1/img` | 176 | 3.597 | 3.949 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1cal/cal01/r1/img` | 164 | 2.286 | 2.621 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1cal2/cal01/r1/img` | 164 | 2.286 | 2.621 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx01/r1/img` | 170 | 5.802 | 6.169 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx01/r2/img` | 170 | 5.802 | 6.169 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx02/r1/img` | 170 | 5.005 | 5.362 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx02/r2/img` | 170 | 5.005 | 5.362 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx03/r1/img` | 170 | 5.595 | 5.931 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx03/r2/img` | 170 | 5.595 | 5.931 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx04/r1/img` | 170 | 4.829 | 5.190 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx04/r2/img` | 170 | 4.829 | 5.190 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx05/r1/img` | 170 | 5.313 | 5.661 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx05/r2/img` | 170 | 5.313 | 5.661 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx06/r1/img` | 170 | 5.126 | 5.476 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx06/r2/img` | 170 | 5.126 | 5.476 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx07/r1/img` | 170 | 4.684 | 5.059 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx07/r2/img` | 170 | 4.684 | 5.059 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx08/r1/img` | 170 | 4.989 | 5.353 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx08/r2/img` | 170 | 4.989 | 5.353 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx09/r1/img` | 170 | 5.030 | 5.349 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx09/r2/img` | 170 | 5.030 | 5.349 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx10/r1/img` | 168 | 5.472 | 5.841 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx10/r2/img` | 168 | 5.472 | 5.841 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx11/r1/img` | 167 | 4.562 | 4.952 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx11/r2/img` | 167 | 4.562 | 4.952 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx12/r1/img` | 168 | 5.145 | 5.513 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx12/r2/img` | 168 | 5.145 | 5.513 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx13/r1/img` | 168 | 4.376 | 4.743 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx13/r2/img` | 168 | 4.376 | 4.743 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx14/r1/img` | 168 | 5.005 | 5.345 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t2/ctx14/r2/img` | 168 | 5.005 | 5.345 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t3/ctx01/r3/img` | 178 | 5.988 | 6.357 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t3/ctx02/r3/img` | 178 | 5.014 | 5.411 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t3/ctx03/r3/img` | 178 | 5.747 | 6.124 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t3/ctx04/r3/img` | 178 | 5.646 | 5.997 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t3/ctx05/r3/img` | 178 | 5.123 | 5.497 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/n1t3/ctx06/r3/img` | 176 | 5.324 | 5.706 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/ru1/ctx01/r1/crops` | 87 | 4.363 | 4.551 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/ru1/ctx01/r2/crops` | 87 | 4.363 | 4.551 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/ru1/ctx02/r1/crops` | 88 | 4.220 | 4.395 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/ru1/ctx02/r2/crops` | 88 | 4.220 | 4.395 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/ru1/ctx03/r1/crops` | 87 | 3.541 | 3.719 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/ru1/ctx03/r2/crops` | 87 | 3.541 | 3.719 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/ru1/ctx04/r1/crops` | 88 | 4.182 | 4.362 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/ru1/ctx04/r2/crops` | 88 | 4.182 | 4.362 | verified SHA256 duplicate of retained recorded/cited source |
| `S/sol_packs/ru1/ctx04/r3/crops` | 88 | 4.182 | 4.362 | verified SHA256 duplicate of retained recorded/cited source |

## Kept candidates with citations

Kept-cited counts 21,008 retained image candidates with at least one path/SHA citation, including unfinished readings and retained source anchors. Each exact path and up to five evidence files appear in DISK1_FILES.jsonl. All sheets_index.json files remain. Archived runtime and reference images were kept because they are outside the approved contact-sheet category.

| Parent path | Kept cited images | Logical MB | Reason | Example evidence |
|---|---:|---:|---|---|
| `S/n1_cache/crops` | 615 | 8.494 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/controls/approved.jsonl` |
| `S/n1_cache/crops` | 8 | 0.317 | retained cited/source SHA256 anchor for deleted duplicates | `W/artifacts/n1/controls/crop_checks_v2.jsonl` |
| `S/n1_cache/n1t2_rendered` | 2 | 0.048 | retained cited/source SHA256 anchor for deleted duplicates | `W/artifacts/n1/N1Tb_RECEIPT.json` |
| `S/n1_cache/n1t_rendered` | 2114 | 45.447 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/n1_cache/n1t_rendered` | 2121 | 66.683 | retained cited/source SHA256 anchor for deleted duplicates | `W/artifacts/n1/N1Cc_GENERATION.json` |
| `S/n1_cache/rendered_cb` | 671 | 9.902 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/N1Cb_GENERATION.json` |
| `S/n1_cache/rendered_cb` | 641 | 17.488 | retained cited/source SHA256 anchor for deleted duplicates | `W/artifacts/n1/N1Cb_GENERATION.json` |
| `S/n1_cache/rendered_cc` | 1 | 0.008 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/N1Cc_GENERATION.json` |
| `S/n1_cache/rendered_cc` | 1281 | 27.231 | retained cited/source SHA256 anchor for deleted duplicates | `W/artifacts/n1/N1Cc_GENERATION.json` |
| `S/n1_ctrl_sheets` | 11 | 4.754 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/N1Cb_GENERATION.json` |
| `S/n1_review` | 1 | 0.592 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/n1_review/raised` | 5 | 3.352 | cited by path or SHA; no identical-sha retained cited copy | `S/n1_review/raised/sheets_index.json` |
| `S/n1_review/t_lead` | 15 | 13.247 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/lead_t.jsonl` |
| `S/ru1_cache/crops` | 805 | 27.434 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/ru1/RU10b_RECEIPT.json` |
| `S/ru1_cache/crops` | 353 | 16.398 | retained cited/source SHA256 anchor for deleted duplicates | `W/artifacts/ru1/RU10b_RECEIPT.json` |
| `S/ru1_review` | 1 | 1.254 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/ru1/RU11b_RECEIPT.json` |
| `S/ru1_review/lead` | 7 | 7.366 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/ru1/RU1L_RECEIPT.json` |
| `S/ru1_review/lead/references` | 20 | 0.096 | archived runtime/reference image, outside approved contact-sheet category | `W/artifacts/ru1/RU1L_RECEIPT.json` |
| `S/ru1_review/r1_runtime/ctx01/zoom` | 88 | 33.176 | archived runtime/reference image, outside approved contact-sheet category | `W/artifacts/ru1/answers/ctx01.scan.json` |
| `S/ru1_review/r1_runtime/ctx02/zoom` | 93 | 32.038 | archived runtime/reference image, outside approved contact-sheet category | `W/artifacts/ru1/answers/ctx02.scan.json` |
| `S/ru1_review/r1_runtime/ctx03/zoom` | 99 | 28.821 | archived runtime/reference image, outside approved contact-sheet category | `W/artifacts/ru1/answers/ctx03.scan.json` |
| `S/ru1_review/r1_runtime/ctx04/zoom` | 96 | 32.570 | archived runtime/reference image, outside approved contact-sheet category | `W/artifacts/ru1/answers/ctx04.scan.json` |
| `S/sol_packs/n1/ctx01/r1/zoom` | 6 | 0.066 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/ctx01.r1.scan.json` |
| `S/sol_packs/n1/ctx01/r2/img` | 178 | 4.049 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1Cb_GENERATION.json` |
| `S/sol_packs/n1/ctx02/r1/zoom` | 3 | 0.021 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/ctx02.r1.scan.json` |
| `S/sol_packs/n1/ctx02/r2/img` | 178 | 3.699 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1Cc_GENERATION.json` |
| `S/sol_packs/n1/ctx03/r1/zoom` | 6 | 0.087 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/ctx03.r1.scan.json` |
| `S/sol_packs/n1/ctx03/r2/img` | 178 | 3.950 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1Cc_GENERATION.json` |
| `S/sol_packs/n1/ctx04/r1/zoom` | 5 | 0.219 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/ctx04.r1.scan.json` |
| `S/sol_packs/n1/ctx04/r2/img` | 178 | 4.343 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1Cb_GENERATION.json` |
| `S/sol_packs/n1/ctx05/r1/zoom` | 5 | 0.041 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/ctx05.r1.scan.json` |
| `S/sol_packs/n1/ctx05/r2/img` | 178 | 3.491 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1Cc_GENERATION.json` |
| `S/sol_packs/n1/ctx06/r1/zoom` | 4 | 0.135 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/ctx06.r1.scan.json` |
| `S/sol_packs/n1/ctx06/r2/img` | 176 | 3.476 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1Cb_GENERATION.json` |
| `S/sol_packs/n1/ctx07/r1/zoom` | 4 | 0.049 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/ctx07.r1.scan.json` |
| `S/sol_packs/n1/ctx07/r2/img` | 176 | 3.597 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1Cc_GENERATION.json` |
| `S/sol_packs/n1cal/cal01/r1/zoom` | 5 | 0.038 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/cal01.r1.scan.json` |
| `S/sol_packs/n1cal2/cal01/r1/zoom` | 5 | 0.036 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1cal2/cal01.r1.scan.json` |
| `S/sol_packs/n1t/ctx01/r1/img` | 175 | 3.911 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx01/r2/img` | 175 | 3.911 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx02/r1/img` | 175 | 4.196 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx02/r2/img` | 175 | 4.196 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx03/r1/img` | 176 | 4.192 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx03/r2/img` | 176 | 4.192 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx04/r1/img` | 176 | 4.317 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx04/r2/img` | 176 | 4.317 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx05/r1/img` | 176 | 4.466 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx05/r2/img` | 176 | 4.466 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx06/r1/img` | 176 | 4.665 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1TS2_RECEIPT.json` |
| `S/sol_packs/n1t/ctx06/r2/img` | 176 | 4.665 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1TS2_RECEIPT.json` |
| `S/sol_packs/n1t/ctx07/r1/img` | 176 | 4.292 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx07/r2/img` | 176 | 4.292 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx08/r1/img` | 176 | 4.204 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx08/r2/img` | 176 | 4.204 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx09/r1/img` | 176 | 4.105 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1Cc_GENERATION.json` |
| `S/sol_packs/n1t/ctx09/r2/img` | 176 | 4.105 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1Cc_GENERATION.json` |
| `S/sol_packs/n1t/ctx10/r1/img` | 176 | 4.714 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1Cb_GENERATION.json` |
| `S/sol_packs/n1t/ctx10/r2/img` | 176 | 4.714 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1Cb_GENERATION.json` |
| `S/sol_packs/n1t/ctx11/r1/img` | 175 | 4.436 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1Cc_GENERATION.json` |
| `S/sol_packs/n1t/ctx11/r2/img` | 175 | 4.436 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1Cc_GENERATION.json` |
| `S/sol_packs/n1t/ctx12/r1/img` | 176 | 4.518 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx12/r2/img` | 176 | 4.518 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx13/r1/img` | 176 | 4.386 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1Cb_GENERATION.json` |
| `S/sol_packs/n1t/ctx13/r2/img` | 176 | 4.386 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1Cb_GENERATION.json` |
| `S/sol_packs/n1t/ctx14/r1/img` | 176 | 4.602 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx14/r2/img` | 176 | 4.602 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx15/r1/img` | 176 | 4.244 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx15/r2/img` | 176 | 4.244 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx16/r1/img` | 176 | 3.901 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx16/r2/img` | 176 | 3.901 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx17/r1/img` | 176 | 4.676 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx17/r2/img` | 176 | 4.676 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx18/r1/img` | 176 | 4.051 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx18/r2/img` | 176 | 4.051 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx19/r1/img` | 176 | 4.410 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx19/r2/img` | 176 | 4.410 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx20/r1/img` | 176 | 4.604 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx20/r2/img` | 176 | 4.604 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx21/r1/img` | 176 | 4.979 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1TS2_RECEIPT.json` |
| `S/sol_packs/n1t/ctx21/r2/img` | 176 | 4.979 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1TS2_RECEIPT.json` |
| `S/sol_packs/n1t/ctx22/r1/img` | 176 | 4.159 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1Cb_GENERATION.json` |
| `S/sol_packs/n1t/ctx22/r2/img` | 176 | 4.159 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1Cb_GENERATION.json` |
| `S/sol_packs/n1t/ctx23/r1/img` | 174 | 3.934 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx23/r2/img` | 174 | 3.934 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx24/r1/img` | 174 | 4.242 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx24/r2/img` | 174 | 4.242 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx25/r1/img` | 174 | 4.201 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1Cb_GENERATION.json` |
| `S/sol_packs/n1t/ctx25/r2/img` | 174 | 4.201 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1Cb_GENERATION.json` |
| `S/sol_packs/n1t/ctx26/r1/img` | 174 | 4.485 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx26/r2/img` | 174 | 4.485 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx27/r1/img` | 174 | 3.668 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t/ctx27/r2/img` | 174 | 3.668 | reading completion not proven by matching item/answer IDs | `W/artifacts/n1/N1T_RECEIPT.json` |
| `S/sol_packs/n1t2/ctx01/r1/zoom` | 2 | 0.011 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx01.r1.scan.json` |
| `S/sol_packs/n1t2/ctx01/r2/zoom` | 8 | 0.066 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx01.r2.scan.json` |
| `S/sol_packs/n1t2/ctx02/r1/zoom` | 1 | 0.010 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx02.r1.scan.json` |
| `S/sol_packs/n1t2/ctx02/r2/zoom` | 8 | 0.124 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx02.r2.scan.json` |
| `S/sol_packs/n1t2/ctx03/r1/zoom` | 7 | 0.361 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx03.r1.scan.json` |
| `S/sol_packs/n1t2/ctx03/r2/zoom` | 3 | 0.025 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx03.r2.scan.json` |
| `S/sol_packs/n1t2/ctx04/r1/zoom` | 4 | 0.038 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx04.r1.scan.json` |
| `S/sol_packs/n1t2/ctx04/r2/zoom` | 6 | 0.056 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx04.r2.scan.json` |
| `S/sol_packs/n1t2/ctx05/r1/zoom` | 6 | 0.099 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx05.r1.scan.json` |
| `S/sol_packs/n1t2/ctx05/r2/zoom` | 5 | 0.037 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx05.r2.scan.json` |
| `S/sol_packs/n1t2/ctx06/r1/zoom` | 5 | 0.150 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx06.r1.scan.json` |
| `S/sol_packs/n1t2/ctx06/r2/zoom` | 2 | 0.082 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx06.r2.scan.json` |
| `S/sol_packs/n1t2/ctx07/r1/zoom` | 7 | 0.088 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx07.r1.scan.json` |
| `S/sol_packs/n1t2/ctx08/r1/zoom` | 8 | 0.418 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx08.r1.scan.json` |
| `S/sol_packs/n1t2/ctx08/r2/zoom` | 4 | 0.142 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx08.r2.scan.json` |
| `S/sol_packs/n1t2/ctx09/r1/zoom` | 6 | 0.073 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx09.r1.scan.json` |
| `S/sol_packs/n1t2/ctx09/r2/zoom` | 6 | 0.041 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx09.r2.scan.json` |
| `S/sol_packs/n1t2/ctx10/r1/zoom` | 6 | 0.055 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx10.r1.scan.json` |
| `S/sol_packs/n1t2/ctx10/r2/zoom` | 4 | 0.136 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx10.r2.scan.json` |
| `S/sol_packs/n1t2/ctx11/r1/zoom` | 3 | 0.112 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx11.r1.scan.json` |
| `S/sol_packs/n1t2/ctx11/r2/zoom` | 5 | 0.053 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx11.r2.scan.json` |
| `S/sol_packs/n1t2/ctx12/r1/zoom` | 3 | 0.089 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx12.r1.scan.json` |
| `S/sol_packs/n1t2/ctx12/r2/zoom` | 3 | 0.030 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx12.r2.scan.json` |
| `S/sol_packs/n1t2/ctx13/r1/zoom` | 5 | 0.046 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx13.r1.scan.json` |
| `S/sol_packs/n1t2/ctx13/r2/zoom` | 4 | 0.039 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx13.r2.scan.json` |
| `S/sol_packs/n1t2/ctx14/r1/zoom` | 11 | 0.489 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx14.r1.scan.json` |
| `S/sol_packs/n1t2/ctx14/r2/zoom` | 11 | 0.095 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t2/ctx14.r2.scan.json` |
| `S/sol_packs/n1t3/ctx01/r3/zoom` | 6 | 0.064 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t3/ctx01.r3.scan.json` |
| `S/sol_packs/n1t3/ctx02/r3/zoom` | 8 | 0.064 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t3/ctx02.r3.scan.json` |
| `S/sol_packs/n1t3/ctx03/r3/zoom` | 7 | 0.048 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t3/ctx03.r3.scan.json` |
| `S/sol_packs/n1t3/ctx04/r3/zoom` | 11 | 0.577 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t3/ctx04.r3.scan.json` |
| `S/sol_packs/n1t3/ctx05/r3/zoom` | 108 | 5.852 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t3/ctx05.r3.scan.json` |
| `S/sol_packs/n1t3/ctx06/r3/zoom` | 6 | 0.225 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/n1/answers/n1t3/ctx06.r3.scan.json` |
| `S/sol_packs/ru1/ctx01/r2/zoom` | 90 | 34.721 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/ru1/RU1S_RECEIPT.json` |
| `S/sol_packs/ru1/ctx02/r2/zoom` | 92 | 32.109 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/ru1/RU1S_RECEIPT.json` |
| `S/sol_packs/ru1/ctx03/r2/zoom` | 97 | 35.575 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/ru1/answers/ctx03.r2.scan.json` |
| `S/sol_packs/ru1/ctx04/r2/zoom` | 539 | 97.070 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/ru1/RU1S_RECEIPT.json` |
| `S/sol_packs/ru1/ctx04/r3/zoom` | 90 | 32.368 | cited by path or SHA; no identical-sha retained cited copy | `W/artifacts/ru1/answers/ctx04.r3.scan.json` |

## Free space before and after

At initial inspection, before any DISK1 deletion, `df -h /` reported 22 GiB available. This rose to 28 GiB during inventory, before DISK1 removed any file. Other activity was therefore affecting free space; the entire df delta must not be attributed to this cleanup. The before reading immediately precedes deletion; the after reading includes the report and per-file audit records.

Before:

```text
Filesystem        Size    Used   Avail Capacity iused ifree %iused  Mounted on
/dev/disk3s1s1   926Gi    12Gi    27Gi    31%    459k  282M    0%   /
```

After:

```text
Filesystem        Size    Used   Avail Capacity iused ifree %iused  Mounted on
/dev/disk3s1s1   926Gi    12Gi    27Gi    31%    459k  284M    0%   /
```

Exact `df -k /` available-space conversion: before 28.834 GB; after 29.041 GB. Both raw df formats are retained as S/disk1_df_before.txt and S/disk1_df_after.txt.

DISK1 READY: freed 0.261 GB (worktree 0.000, scratchpad 0.261); kept-cited 21008; df before 28.834 after 29.041
