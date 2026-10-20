# SEG-CP7c2: fix the r2 runtime's post-read closure check; finish context A; prepare B (gpt-6.1-sol, medium, network OFF, no reading)

`seg/cp7/launch_cp7_r2.sh` ran context `segcp7r2_a/r1`. **The reader completed**: rc 0; mapped 50 plus 5 controls (see `seg/cp7/run_r2.log`). Then `runtime_r2.py` (line 23, the receipt step) called `common.closure()`, the **pre-read** pack check, which asserts that the pack holds only cards.jsonl + crops. It failed on the reader's own outputs (`answers.jsonl`, `zoom/…`). Context B never started.

## Do
1. **Fix `runtime_r2.py`.** The post-read verification must check that the pre-read pack files are **byte-unchanged** against the recorded closure hashes, and must allow only the reader outputs the HANDOVER permits (answers.jsonl, zoom/*). Mirror how the CP7a `runtime.py` handled its receipts.
   - Do **not** weaken the pre-read check.
   - Do **not** change the scanner, the packs, the freeze-bound code (`CP7_FREEZE_r2.json`), or the sealed decisions. If runtime_r2.py is freeze-bound, say so and record the change as a runtime-only amendment with its new sha.
2. **Finish context A without rereading.** Verify that its scan (`seg/cp7/scan/segcp7r2_a/r1.scan.json`, or run the canonical scanner on the logged rollout if it is missing) is ok. Then write its receipt from the logged run values in `run_r2.log`, the same way the lead did for CP7a context A.
3. **Context B:** make `launch_cp7_r2.sh` (or a `launch_cp7_r2_b.sh`) run only `segcp7r2_b/r1`, with the refuse-rerun guard. Do **not** run it.
4. Tests for the post-read check (the pack is unchanged and reader outputs are allowed; a modified card or crop fails), and a dry run of the receipt step on context A.

The last line must be exactly:
`SEG-CP7c2: done | post-read check fixed | context A: scan ok <yes/no>, receipt written | context B launcher ready | tests: <n> passed`
