# CAPS4 results

**Gate: pass.** Letters y=100/100; crop_ok y=99/100. Both thresholds are 90/100. Sol letters and crop_ok are final; all marks remain `pending_opus`. No review disposition or dataset admission is made.

## Rollout validity

[c1 scanner-v4 report](scan/caps3/c1.scan.json):

> "scanner_version": 4; "ok": true; "violations": []; "manifest_check_skipped": false; "distinct_images_viewed": 66.

**Coverage: 55/55 original card images viewed.** Positions 45 and 52 were viewed as `zoom/recheck45.png` and `zoom/recheck52.png`, produced directly from the corresponding original crops at 600%; the other 53 positions were viewed as `zoom/NN.png`. Scanner image matches cover both substitute paths. There are 11 additional distinct review images.

[c2 scanner-v4 report](scan/caps3/c2.scan.json):

> "scanner_version": 4; "ok": true; "violations": []; "manifest_check_skipped": false; "distinct_images_viewed": 56.

**Coverage: 55/55 original card images viewed.** All 55 `zoom/01.png` through `zoom/55.png` were viewed, plus one additional review image.

Both contexts are clean; the run is valid. The coverage position-to-path mapping is preserved in `results.json`.

## Bed aggregation (controls excluded)

| Population | n | letters y/n/u | crop_ok y/n | marks y/n/na (pending_opus) | flagged |
|---|---:|---|---|---|---:|
| All | 100 | 100/0/0 | 99/1 | 98/2/0 | 5 |
| c1 | 50 | 50/0/0 | 50/0 | 49/1/0 | 2 |
| c2 | 50 | 50/0/0 | 49/1 | 49/1/0 | 3 |
| bsb_poly1850 | 2 | 2/0/0 | 2/0 | 2/0/0 | 0 |
| gazette_modern | 78 | 78/0/0 | 77/1 | 76/2/0 | 5 |
| ia_poly1850 | 1 | 1/0/0 | 1/0 | 1/0/0 | 0 |
| kosmopolis | 7 | 7/0/0 | 7/0 | 7/0/0 | 0 |
| lekythos | 12 | 12/0/0 | 12/0 | 12/0/0 | 0 |

Errors count card-level occurrences; one card can carry multiple types.

| Population | Error type | Count |
|---|---|---:|
| All | crop_overrun | 1 |
| All | extra_mark | 1 |
| All | hyphen | 1 |
| All | missing_mark | 1 |
| All | punctuation | 1 |
| c1 | hyphen | 1 |
| c1 | missing_mark | 1 |
| c2 | crop_overrun | 1 |
| c2 | extra_mark | 1 |
| c2 | punctuation | 1 |
| bsb_poly1850 | none | 0 |
| gazette_modern | crop_overrun | 1 |
| gazette_modern | extra_mark | 1 |
| gazette_modern | hyphen | 1 |
| gazette_modern | missing_mark | 1 |
| gazette_modern | punctuation | 1 |
| ia_poly1850 | none | 0 |
| kosmopolis | none | 0 |
| lekythos | none | 0 |

## Controls

Only letters and crop_ok determine control agreement; marks are excluded.

| Context | Control | Opaque card | Reference letters/crop_ok | Sol letters/crop_ok | Outcome |
|---|---|---|---|---|---|
| c1 | c009 | kfb6a63cff0 | y/y | y/y | pass |
| c1 | c013 | k1c1b1883e8 | y/y | y/y | pass |
| c1 | c046 | k3c9e5a71a0 | y/y | y/y | pass |
| c1 | c026 | kfde9a4f15e | y/y | y/y | pass |
| c1 | c057 | k512fc5c3f4 | y/n | n/n | error |
| c2 | c041 | kb3cba0a651 | n/n | n/n | pass |
| c2 | c072 | kc8b13c8901 | y/n | y/n | pass |
| c2 | c035 | k9ed3747bac | y/y | y/y | pass |
| c2 | c066 | k5127d027ee | y/y | y/y | pass |
| c2 | c029 | k1dd1bb1690 | y/y | y/y | pass |

**9/10 pass.** c1 has 1 control error (within the ≤1 tolerance; not flagged); c2 has 0 (not flagged).

The c1 error is **c057**, opaque `k512fc5c3f4`, line `bsb_poly1850--515c78c513c1c8c5--s002-l0063`. Reference truth: **letters y; crop_ok n**, error `crop_overrun`; reference detail: “lower halves of previous line’s letters (readable 'ως') at top-left”. Reference marks y is recorded but not scored. Sol returned letters n, crop_ok n, marks y, errors `wrong_letter`, `crop_overrun`, detail “αὐταῖς → αὐτοῖς; preceding-line letter bodies → omitted”. This disagreement remains queued without adjudication.

## Comparison with CAPS2

Different card sets: this comparison is **not paired** and does not establish a per-card masking effect.

| Metric | CAPS2 original crops (n=100) | CAPS4 masked redraw (n=100) |
|---|---:|---:|
| letters y/n/u | 99/1/0 | 100/0/0 |
| crop_ok y/n | 89/11 | 99/1 |
| crop failure type: crop_clipped | 6 | 0 |
| crop failure type: crop_overrun | 5 | 1 |
| crop failure type: merged_two_lines | 1 | 0 |

CAPS2 evidence: [RESULTS.md](../caps1/RESULTS.md), [results.json](../caps1/results.json). Crop failure types are overlapping labels, not disjoint counts.

## Review routing

`review_queue.jsonl` contains 9 unique cards: 5 bed flags and 4 controls; 0 unreadables. Routing includes every negative verdict, nonempty error list (including marks and punctuation), unreadable and control disagreement. Expected-negative controls are distinguished from control errors. Each record preserves card ID, line ID, source, crop path, exact Sol detail, verdicts, errors, and pending review status. All 110 public crop files were checked against key/custody SHA256 values.

HANDOVER §8: “Route every "unreadable" and every flag to a human or Opus eye. Never auto-accept or auto-reject them.” No item is auto-accepted or auto-rejected.

## Ledger usage

| Context | Input | Cached input | Output | Reasoning | Total | Wall seconds | Weekly before/after |
|---|---:|---:|---:|---:|---:|---:|---|
| c1 | 496897 | 450816 | 3867 | 1149 | 500764 | 114 | 36.0% / 36.0% |
| c2 | 356593 | 317824 | 3338 | 751 | 359931 | 85 | 36.0% / 36.0% |

Total: **860695 tokens**, 199 summed reader wall seconds, 110 items including controls. Codex weekly meter: **36% → 36%**. All figures come directly from `usage_ledger.json`; no estimates. Cached input is included in input; reasoning is included in output. Probe tokens are not separately recorded. Credit spend is unknown because before balances are unavailable.

## Guarded commit list

`CAPS4_COMMIT_FILES.txt` lists exactly the three outputs plus the CAPS4 guard and list. `CAPS4_COMMIT_GUARD.json` binds HEAD, branch, aggregation input hashes, and output hashes. Before staging, require matching HEAD/branch, an empty index, and matching input/output hashes; stop on any mismatch. Stage only the five listed paths, and require the staged path set to equal that list before committing. The guard and list are outside their own hash set. Existing CAPS3 handoff lists and unrelated worktree files remain untouched. No staging or commit performed.

CAPS4: done | letters y: 100 | crop_ok y: 99 | marks y: 98 (pending opus) | gate: pass | controls: 9/10 | review queue: 9 | tokens: 860695
