# CAPS2 results

**Gate: fail.** Letters y=99/100; crop_ok y=89/100. Both thresholds are 90/100. Sol letters and crop_ok are final for this check; all marks are `pending_opus`. No dataset admission or review disposition is made.

## Rollout validity

[c1 scanner-v4 report](scan/caps1/c1.scan.json):

> "scanner_version": 4; "ok": true; "violations": []; "manifest_check_skipped": false;
> "distinct_images_viewed": 67.

Original coverage: **55/55** (`zoom/01.png` through `zoom/55.png`). Additional viewed review images: 12. Both contexts are clean; the run is valid.

[c2 scanner-v4 report](scan/caps1/c2.scan.json):

> "scanner_version": 4; "ok": true; "violations": []; "manifest_check_skipped": false;
> "distinct_images_viewed": 55.

Original coverage: **55/55** (`zoom/01.png` through `zoom/55.png`). Additional viewed review images: 0. Both contexts are clean; the run is valid.

## Bed aggregation (controls excluded)

| Population | n | letters y/n/u | crop_ok y/n | marks y/n/na (pending_opus) | flagged |
|---|---:|---|---|---|---:|
| All | 100 | 99/1/0 | 89/11 | 100/0/0 | 12 |
| c1 | 50 | 50/0/0 | 44/6 | 50/0/0 | 7 |
| c2 | 50 | 49/1/0 | 45/5 | 50/0/0 | 5 |
| bsb_poly1850 | 2 | 2/0/0 | 1/1 | 2/0/0 | 1 |
| gazette_modern | 80 | 80/0/0 | 73/7 | 80/0/0 | 8 |
| ia_poly1850 | 7 | 6/1/0 | 5/2 | 7/0/0 | 2 |
| kosmopolis | 2 | 2/0/0 | 2/0 | 2/0/0 | 0 |
| lekythos | 8 | 8/0/0 | 7/1 | 8/0/0 | 1 |
| nlg | 1 | 1/0/0 | 1/0 | 1/0/0 | 0 |

Errors count card-level occurrences; multiple types can occur on one card.

| Source | Error type | Count |
|---|---|---:|
| All | crop_clipped | 6 |
| All | crop_overrun | 5 |
| All | digits | 1 |
| All | merged_two_lines | 1 |
| All | missing_word_or_span | 1 |
| All | punctuation | 1 |
| bsb_poly1850 | crop_clipped | 1 |
| gazette_modern | crop_clipped | 4 |
| gazette_modern | crop_overrun | 3 |
| gazette_modern | punctuation | 1 |
| ia_poly1850 | crop_clipped | 1 |
| ia_poly1850 | crop_overrun | 1 |
| ia_poly1850 | digits | 1 |
| ia_poly1850 | missing_word_or_span | 1 |
| kosmopolis | none | 0 |
| lekythos | crop_overrun | 1 |
| lekythos | merged_two_lines | 1 |
| nlg | none | 0 |

## Controls

Letters/crop_ok alone determine control agreement; marks are excluded.

| Context | Original control | Opaque card | Expected letters/crop_ok | Sol letters/crop_ok | Outcome |
|---|---|---|---|---|---|
| c1 | c046 | k0f7d4b492b | y/y | y/y | pass |
| c1 | c026 | kde68e16523 | y/y | y/y | pass |
| c1 | c009 | kd4607e67fa | y/y | y/y | pass |
| c1 | c013 | k49748b6bf8 | y/y | y/y | pass |
| c1 | c057 | k8549e9793b | y/n | y/n | pass |
| c2 | c041 | kafb2637982 | n/n | n/n | pass |
| c2 | c072 | k9cc7b70e04 | y/n | y/n | pass |
| c2 | c066 | k1464d1a274 | y/y | y/y | pass |
| c2 | c029 | k2de26b03e2 | y/y | y/y | pass |
| c2 | c035 | kfa592c06e1 | y/y | y/y | pass |

**10/10 pass; 0 errors in each context; neither context flagged.**

## Review routing

`review_queue.jsonl` contains 15 unique cards: 12 bed flags and 3 expected-negative control flags; 0 unreadables. Every negative verdict or nonempty error list is routed, including the punctuation flag whose letters/crop_ok remain y/y. Expected-negative controls are explicitly identified and are not control errors. Each record includes opaque card ID, line ID, source, original detail (including empty strings), errors, crop path, and pending review status. Crop files were checked against key SHA256 values.

HANDOVER §8: “Route every "unreadable" and every flag to a human or Opus eye. Never auto-accept or auto-reject them.” No queue item receives a disposition.

## Ledger usage

| Context | Input | Cached input | Output | Reasoning | Total | Wall seconds | Weekly before/after |
|---|---:|---:|---:|---:|---:|---:|---|
| c1 | 451529 | 397440 | 4596 | 1278 | 456125 | 109 | 34.0% / 34.0% |
| c2 | 416845 | 385536 | 4443 | 1109 | 421288 | 106 | 34.0% / 35.0% |

Total: **877413 tokens**, 215 summed reader wall seconds, 110 items including controls, weekly 34% → 35%, directly from `usage_ledger.json`. Cached input is part of input; reasoning is part of output and neither is added again. Probe tokens are not separately recorded in this ledger. Before credit balances are unavailable; credit spend is unknown.

## Guarded commit list

`CAPS2_COMMIT_FILES.txt` lists exactly the three outputs plus the CAPS2 guard and list. `CAPS2_COMMIT_GUARD.json` binds the current HEAD, branch, all aggregation inputs, and the three output hashes. Verify these bindings and require an empty index before staging only those five paths; stop on any mismatch. The guard/list are intentionally outside their own hash set. Existing CAPS1 commit lists and unrelated worktree files remain untouched. No staging or commit performed.

CAPS2: done | letters y: 99 | crop_ok y: 89 | marks y: 100 (pending opus) | gate: fail | controls: 10/10 | review queue: 15 | tokens: 877413
