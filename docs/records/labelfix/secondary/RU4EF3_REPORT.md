# RU4EF3 issuance

Sparse test/dev overlay issued from r5 recombination with v4.4 scans, control gates and coverage. The lead audit confirms 30/30 sampled cells. Remaining lead_review positions and all unruled review PNG cells retain Google ь; no further rounds. Per-edit provenance distinguishes individually audited cells from sampled-audit acceptance.

409 edits on 354 rows; 250 held positions on 194 rows. The 1,742-ID wave1c v2_test Cyrillic slice contains 144 edits on 135 rows; all six arms have the same IDs.

Every emitted row was verified against its exact raw Google import; differences equal listed ь→ъ edits, and restoring those edits recovers the original UTF-8 bytes. LQB registration and full parent-population loader readback passed; omitted IDs inherit exact raw text. LQB truth_v1_1 re-score: `docs/records/labelfix/lqb/score_ru1_v3_test_edits.json`, with a same-population raw test/dev baseline. Protocol tests: 34 passed. Network, reader runs, browser, computer use and .git writes: none.

R5 admission outcomes:

- `ctx04/r2/r5`: VOID (2 wrong control signs)
- `ctx11/r1/r5`: FAILED (unclean canonical scan)
- `ctx11/r2/r5`: VOID (3 wrong control signs)

LQB re-score is unchanged on covered truth. No test/dev ru1_yer truth items are covered, so it does not measure the 409 edits.

Receipt: `artifacts/ru1/ru4e2/RU4EF3_RECEIPT.json`. Holds in the final line count positions.

RU4EF3 READY: rows 548 (test 470, dev 78); edits 409 (in wave1c slice 144 on 135 rows); holds 250; sha256 c4b3a248b660ce670e35a2ac9b9c4e5380f357f1ab3ec3c488de67de61a756a1; LQB ok
