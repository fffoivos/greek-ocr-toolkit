# SEAL02D: pixel-overlap checks for seal04, local package only (gpt-6.1-sol, medium, network OFF, no spend, no deploy, no jobs)

Benchmark 0.2 was sealed as seal03 (job 3705072, package `benchmark_0.2/pkg/253921bf`, suite `33e7fe9f…`; record at `seal02/seal03_record/SEAL03_RECORD.md`).
- **Finding:** one pixel-identical crop appears in both panels: `image_sha256` `4b22b2ff40ca5b79195fd9e735a7d15c25f56bb3dac2d8eb904a16d02ff0dafb` ("НБС", the National Bank of Serbia masthead).
  - test row `serbia--d6030713c8d88c96--s005-l0006` (test:font_extremes:small);
  - dev row `serbia--27b182bf4116728f--s009-l0006` (dev:font_extremes:small);
  - they come from different editions.
- **Coordinator ruling:** seal04 drops the dev row and test keeps its row. The seal gains two checks.

**The package is prepared now but NOT deployed.** Deploying waits for the ASTRA-CP3 review of seal03, so that any CP3 HIGH lands in the same package. Do not run `ssh`, `rsync` or any remote command.

## Do (in `seal02/`, minimal changes; every existing check stays)
1. **Cross-panel pixel overlap.** After the final selection is validated and before emitting the panels:
   - for every `image_sha256` present in both the test and dev selections, **drop the dev row(s)**; test keeps its rows;
   - record each drop in `SEAL_RECEIPT.json` under the new explicit key `cross_panel_pixel_duplicates_dropped`: a list of `{image_sha256, dropped: {parent_id,row_id,split:"dev",quota_scope}, kept: [{parent_id,row_id,split:"test",quota_scope}]}`;
   - count each drop as a dev deficit in its scope: `scope_counts[scope].sealed` −1, `deficit` +1, with a per-scope `pixel_duplicate_drops` count. No replacement is drawn for it, by the ruling: "count it as a dev deficit";
   - `rows` and `images` in the receipt must then agree.
2. **Within-panel uniqueness.** No `image_sha256` may repeat within a panel. A repeat **fails** the build with `SEAL02_FAIL: duplicate image within panel <panel>`, naming the rows. It fails rather than drops: the ruling asks for a check, and within-panel duplicates would mean the selection itself is wrong.
3. **Tests:**
   - a fixture with one cross-panel duplicate: the dev row is dropped, the receipt key is exact, scope_counts are adjusted, and test is unchanged;
   - a fixture with two dev rows sharing one test image: both are dropped;
   - a within-panel duplicate in test, and another in dev: each fails;
   - no duplicates: output identical to before, except the new receipt key, which is present as an empty list;
   - all 21 existing tests pass, or are updated only for the new receipt key; list each update.
4. **Real-data replay, local only.** The real seal03 panels are at `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/seal03/benchmark_v02_{test,dev}.jsonl` (read-only). Run the new overlap/uniqueness logic, as a function, on those rows. It must report exactly one cross-panel duplicate (the pair above) and zero within-panel duplicates. The result is dev 437, test 2,253, and dev:font_extremes:small sealed 11 with deficit 2. Quote the output.
5. Regenerate DEPLOY_PATHS/DEPLOY_SHA256SUMS/COMMIT_LIST locally and **state the new package sha8 that a deploy would produce**. Add a SEAL02D section to `SEAL02.md` covering:
   - the change and the test list;
   - the replay result;
   - the expected seal04 numbers;
   - "deploy pending ASTRA-CP3".

   Do not write a coordinator block yet.

Write a guarded commit list. Do not run `git add` or `git commit`. Do not touch `scaling_w3/`.

The last line must be exactly:
`SEAL02D: done | cross-panel dup → drop dev, receipt key cross_panel_pixel_duplicates_dropped | within-panel dup fails | real replay 1 cross / 0 within (dev 437) | local package <sha8> NOT deployed | tests <n> passed`
