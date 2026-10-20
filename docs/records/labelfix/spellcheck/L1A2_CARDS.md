**L1A2 — sf6 100-line precision-audit cards, 2026-10-17**

Ready: **101 changed-word cards + 9 individually pixel-verified planted controls = 110 cards**. Controls are **8.18% of the complete deck**. All 100 selected lines are represented; one round2 line contributes two changed words. This prepares the precision audit; independent answers and release precision remain pending.

Open the [blind deck](S8_DEV/audit100/index.html), or distribute the complete `S8_DEV/audit100/` directory: [blind JSON](S8_DEV/audit100/items_blind.json), `img/`, [blank answers](S8_DEV/audit100/answers_blank.json), and reading instructions. The [coordinator key](S8_DEV/private/audit100/items_key.json), source records, review sheets and receipts are outside that directory. Only the blind directory goes to readers.

| Wave | Population lines N | Selected lines n | Per-line weight N/n | Word cards | Controls | Total cards |
|---|---:|---:|---:|---:|---:|---:|
| round1 | 67 | 41 | 67/41 | 41 | 2 | 43 |
| round2 | 49 | 30 | 49/30 | 31 | 2 | 33 |
| mixed | 28 | 18 | 28/18 | 18 | 1 | 19 |
| vouli | 6 | 6 | 1 | 6 | 1 | 7 |
| openarchives | 2 | 2 | 1 | 2 | 2 | 4 |
| parliament | 3 | 3 | 1 | 3 | 1 | 4 |
| **Total** | **155** | **100** | — | **101** | **9** | **110** |

The [selection](clariden/L1R3_evidence/production_3680729_3680730/audit100_ids.jsonl) matches its [receipt](clariden/L1R3_evidence/production_3680729_3680730/audit100_receipt.json), SHA-256 `71d29153f8aa80b759e9c8975c7e70a26948c0399f065f192f1d46090f24eedc`. Each card key retains the selection's exact floating-point weight, wave, line ID, word index, all forms, candidate sources and original crop hash. Controls are flagged only in the private key and must be excluded from release-precision estimates. Keep the two words from the same line together when analysing line-level precision.

Original labels come from `docs/records/harvest/collection/v2/import_real_v2_train.jsonl`; the complete file's SHA-256 matches the production release manifest. All 100 selected IDs and their waves match the saved 155-line production audit population; the exact weights equal its wave population divided by the selected wave count. All 100 crops resolve under the read-only `../greek-ocr-toolkit/` harvest roots at their referenced relative paths. Every selected overlay's original-label SHA-256 matches the local original label; all have `corrected` status and `sf6-release-v1` policy. The saved recogniser, original and released readings have matching word counts and matching letter skeletons within every word. The [line inventory](S8_DEV/private/audit100/line_inventory.json) retains the complete readings and changed-word indices.

Selection uses the original-versus-released **NFD** word diff. Contextual elision aliases use the release census's single-atom comparison; alias-only differences do not generate cards. This selection has zero alias-only words to exclude. Candidates are the Google and released word, plus the saved recogniser word whenever distinct: **95 cards have two candidates, six have three**. Equal forms share one choice. Deck order and each card's candidate order are independently seeded with `L1A2-cards-20261017`; source names, line IDs, wave, weights, control flags and expected choices are absent from the blind files. Every card includes separate `none of these` and `unreadable` choices.

Word bounds use the saved recogniser offsets, locator spans and physical ink bounds; they retain the complete crop height and side context. Zooms use uniform scaling at most **3×**. All **101 word crops were visually checked against their full lines**, including punctuation and overhang context; existing source damage or source-edge clipping is preserved. The 100 full-line PNGs are pixel-identical to RGB conversions of their original crops. The [visual crop review](S8_DEV/private/audit100/visual_crop_review.json) binds all 17 inspected review sheets.

The nine controls were selected from unchanged words within the same 100 lines. Before planting, I inspected each word zoom and full line and recorded the literal printed form, visible marks, crop hash and sheet hash in the [private pixel-review record](S8_DEV/private/audit100/controls_pixel_review.json). Agreement between sources was only a candidate filter. Every planted answer was verified against the print; none assumes an iota subscript. Each distractor removes one visible combining mark, with no letter substitution. The controls span all six waves and never reuse a changed-word location.

Clariden access read only the requested `l1r_sf6_3680729/release/overlay_ensemble_ab.jsonl.gz`, streamed on the login node. The successful scan selected all 100 records with their complete evidence after **124,412 records / 15.60 seconds**. Three SSH invocations took **37.98 seconds combined**: the first stopped on a record-layout assumption; the second reached extraction but stopped on the login Python's unsupported gzip `mtime` argument; the corrected third succeeded. No transient transport retry, authentication failure or certificate refresh occurred. No remote files were written and no jobs or inference were launched. The [extraction receipt](S8_DEV/private/audit100/extraction_receipt.json) binds the selected payload and source path/size/mtime; the full 658,630,230-byte source gzip hash was not recomputed.

The [offline validation receipt](S8_DEV/private/audit100/validation_receipt.json) passes complete changed-word coverage, wave/weight joins, deterministic ordering, candidate/source mappings, control fraction, distinct locations, all generated image pixels, source-code hashes and blind/key separation. The [blind manifest](S8_DEV/private/audit100/blind_manifest.json) hashes every deliverable file. No gate, detector or reader code changed; no `.git` command or write was performed. Reproduce offline with `PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1 ../greek-ocr-toolkit/.venv/bin/python -B scripts/labelfix/l1a2_cards.py validate`.

L1A2 READY: 100 lines, 101 word cards (+9 controls, all pixel-verified); per wave round1 41 (+2), round2 31 (+2), mixed 18 (+1), vouli 6 (+1), openarchives 2 (+2), parliament 3 (+1).
