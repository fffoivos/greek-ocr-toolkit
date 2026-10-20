# LF3 — authorized third attempt and vertical re-read tooling

Build only, offline. No reader, meter probe, network operation, sourcing submission, or `.git` write ran. The lead runs readers using the exact commands in `artifacts/lf1/prod/PROD_PLAN.md`. Existing production ledger and first-read keys/manifests remain intact; both authorized contexts still have two VOID attempts. No production re-read verdict is claimed.

## Delivered behavior

`RUN_ALL.sh` forwards `--extra-attempt candidate_w2_00004 candidate_w2_00013` to `run.py`. Only those two names are authorized, and only named contexts are selected by that option. Defaults still launch at most two attempts. The extra attempt gets a distinct `_retry3` directory copied from the original manifest, without prior answers or zooms. Attempt 3 records `authorised_by: "coordinator 20 Oct (VOID is a reader-process failure)"`. Historical receipts survive subsequent invocations, including a default invocation after attempt 3.

A third VOID maps to null verdict, `VOID_THREE`, and `no verdict (reader VOID x3)` in the attempt receipt, mapped record and finalization side receipt. Twice-VOID elsewhere remains `VOID_TWICE` and `no verdict (reader VOID x2)`. Neither can pass as OK. Finalization retains same-quota_scope AND same-source reserve selection by explicit overdraw_order, otherwise UNFILLED. The side receipt distinguishes `verdict_flags`, `no_verdict`, VOID_TWICE and VOID_THREE. The existing seal receipt's `flagged` field retains its schema meaning: all replaced/unfilled slots, equal to REPLACED + UNFILLED.

`build_vertical.py --rosters ... --batch ...` selects every sealed bed card with `draw_class == vertical_turned`, even from first-read VOID contexts. It copies the exact first-pack PNG bytes and literal labels, assigns fresh seeded opaque IDs, and packs at most 50 bed cards per context. Its only control omission is `lf1-control-turned`, whose turned-horizontal expectation is undefined under the vertical statement. The other five frozen controls and scoring are unchanged. The roster seals each context's vertical prompt path/hash and first-roster provenance. The default prompt remains unchanged.

Vertical fleet runs write the separate `artifacts/lf1/prod/vertical_reread_verdicts.jsonl`; each line contains full `first_verdict` and `reread_verdict` records plus the effective decision. Later vertical batches preserve earlier batch records. The original fleet verdict file is preserved by vertical runs. `prod_map.py --vertical-contexts ...` can reconstruct the paired file and merged effective verdicts from the ledger. `prod_finalize.py` uses the re-read decision for vertical lines, including reserves, keeps both records in its side receipt, and cannot promote a first-read OK when the re-read is missing or VOID. The seal list and receipt schema remain unchanged.

## Prompt addition — one block only

`artifacts/lf1/prompts/lf1_vertical.md` is the original `lf1.md` byte-for-byte followed by one blank separator (line 103) and this one added block (line 104):

> This class is printed vertically. Judge after mentally reading along the text direction. Flag only clipping, more than one line, more than 2 whole neighbour words, or text that differs from the ink.

No original line changed. The no-rotate rule, no zoom overwrite, literal relative image paths, and only `answers.jsonl` plus `zoom/**` write rules remain. Original prompt SHA-256: `9b0bdec141963b974baa5fb730c73f08bd323297580434a19af5a68952a081fd`. Vertical prompt SHA-256: `752abcf23b43e0019c2a7d29770831505ef9c63b236a775f650eb4e2a1c9e9dd`.

## Built packs and validation

W1a has **0** vertical bed cards; W2 has **102**. Those 102 include seven in `candidate_w2_00004` and three in `candidate_w2_00013`, so the two pending third reads do not change pack membership. The new roster is `artifacts/lf1/candidate_contexts_vert_w1a_w2.json`, containing `candidate_vert_w1a_w2_00001` through `00003`: 50+5, 50+5, 2+5 cards, respectively, 117 total cards. W1b is deferred until its first-read roster exists.

`LF3_evidence/custody.json` records verification of all 37 original contexts, all three new contexts, the unchanged scanner/dependencies, original roster/key/manifest custody, and exact bytes and labels for all 102 selected cards. All new packs contain only `items.jsonl` and `img/` initially. All 102 IDs are unique and differ from their source card IDs. The build receipt records the seed, original rosters, frozen pool hash and omission. PNGs and manifests remain at the external scratch paths listed in the roster; no production images were copied into the worktree.

Validation command:

```bash
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B -m pytest \
  artifacts/lf1/tools/test_lf1.py artifacts/lf1/tools/test_lf2d.py artifacts/lf1/tools/test_lf3.py \
  -q -p no:cacheprovider
bash -n artifacts/lf1/RUN_ALL.sh
```

Result: **85 passed, 16 subtests passed**. All 69 existing LF1/LF2d tests pass; 16 new LF3 tests cover named authorization, default two-attempt behavior, existing third-attempt history, original-only fresh directories, authorization/VOID receipt text, exact prompt append and per-roster prompt custody, vertical class/control selection, byte/label/ID preservation, VOID x2/x3 mapping, same-source replacement versus UNFILLED, override in both directions, missing re-read rejection, separate paired-file output, cross-batch preservation and nonvertical behavior. Existing sourcing schema and synthetic seal integration checks pass. The repository's unrelated OCR/training suites were not run.

Evidence: `docs/labelfix/spellcheck/LF3_evidence/pytest.txt`, `docs/labelfix/spellcheck/LF3_evidence/custody.json`, and `artifacts/lf1/receipts/candidate_contexts_vert_w1a_w2_build.json`. Existing LF1 tests regenerate their scanner synthetic receipts, and LF2d regenerates its synthetic side receipt; these are test outputs, not production readings. The lead commit list below excludes these incidental regenerated fixtures. LF2d's documented sourcing scope_rank/overdraw_order discrepancy remains unchanged.

## LEAD_COMMIT_PATHS

```text
artifacts/lf1/RUN_ALL.sh
artifacts/lf1/tools/run.py
artifacts/lf1/tools/build.py
artifacts/lf1/tools/build_vertical.py
artifacts/lf1/tools/prod_map.py
artifacts/lf1/tools/prod_finalize.py
artifacts/lf1/tools/test_lf3.py
artifacts/lf1/prompts/lf1_vertical.md
artifacts/lf1/prod/PROD_PLAN.md
artifacts/lf1/candidate_contexts_vert_w1a_w2.json
artifacts/lf1/keys/candidate_vert_w1a_w2_00001.json
artifacts/lf1/keys/candidate_vert_w1a_w2_00002.json
artifacts/lf1/keys/candidate_vert_w1a_w2_00003.json
artifacts/lf1/receipts/candidate_contexts_vert_w1a_w2_build.json
docs/labelfix/spellcheck/LF3_evidence/custody.json
docs/labelfix/spellcheck/LF3_evidence/pytest.txt
docs/labelfix/spellcheck/LF3_REPORT.md
```

LF3 READY: tests 85 passed; extra-attempt plumbing; vertical prompt +1 block; vertical cards now 102 (contexts 3)
