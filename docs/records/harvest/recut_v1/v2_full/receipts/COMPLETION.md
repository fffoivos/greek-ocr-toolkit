# T6h v2 masking completion

Verified all 258,465 outputs and originals across 5,585 pages; zero failures. Network OFF. Run host `192.168.1.13`, PID 82255, tree `63c640a3aa4abe08d200258cf24d235dfa4a1625`.

Run: 2026-10-17T12:41:58.412011+03:00 to 2026-10-17T15:27:13.523606+03:00 (9915.112 s); 29.894 masking pages/min across 4,940 non-parliament pages. Session timer bounds reconstructed from the final summary; launch receipt gives 12:41:35 EEST.

Verification requested nice 5; the sandbox rejected setpriority and the matching probe reported actual nice 5. Production summary reports nice 20.

| Wave | Split | Total | Masked | Changed | Guarded | Unmatched | Parliament skipped | Failed |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| cyrillic | test | 658 | 658 | 122 | 0 | 0 | 0 | 0 |
| cyrillic | train | 12023 | 11967 | 7316 | 2 | 54 | 0 | 0 |
| mixed | test | 2203 | 2096 | 1168 | 38 | 69 | 0 | 0 |
| mixed | train | 27583 | 27214 | 20791 | 54 | 315 | 0 | 0 |
| openarchives | test | 4680 | 4615 | 88 | 2 | 63 | 0 | 0 |
| openarchives | train | 19625 | 19263 | 299 | 0 | 362 | 0 | 0 |
| parliament | test | 11942 | 0 | 0 | 0 | 0 | 11942 | 0 |
| parliament | train | 64521 | 0 | 0 | 0 | 0 | 64521 | 0 |
| round1 | test | 8115 | 8030 | 6119 | 7 | 78 | 0 | 0 |
| round1 | train | 46964 | 46638 | 36090 | 128 | 198 | 0 | 0 |
| round2 | test | 3689 | 3632 | 2469 | 39 | 18 | 0 | 0 |
| round2 | train | 18782 | 18658 | 13595 | 30 | 94 | 0 | 0 |
| vouli | test | 1742 | 1725 | 1585 | 12 | 5 | 0 | 0 |
| vouli | train | 24938 | 24404 | 22754 | 94 | 440 | 0 | 0 |
| wikisource | test | 11000 | 10944 | 5767 | 17 | 39 | 0 | 0 |
| **Total** | | 258465 | 179844 | 118163 | 423 | 1735 | 76463 | 0 |

Records: 258,465 lines, SHA256 `5cc07e5e12b1724dbe30df831638d604004057ab1d721c0e1e16e8dbd2925c68`. Records remain ignored; the JSON receipt binds records, summary and verification by SHA256.

Mock gate: 50/50 identical, baseline `c9bf83b077d3893e34d7eced2d2dd66826c9f98557a9d093f9f8e58b11cd0c4d`. Full params and library hashes are in [the completion receipt](COMPLETION_RECEIPT_20261017.json).
