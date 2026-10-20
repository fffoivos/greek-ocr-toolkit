# SEG-CP7a2: finish CP7a — draw and packs, now that the snapshots exist (gpt-6.1-sol, medium, network OFF, no reading)

Continue `docs/records/briefs/SEG_CP7a_freeze_and_packs.md` **from step 3**; every constraint there still applies. Steps 1–2 are committed in 44601f08 (M1/M2 fixed, `seg/CP7_FREEZE.json`, frozen gate 22/22, D 9/9, C1 6/6, gallery 6/6), and `CP7a_RECEIPT.md` recorded the blocker: missing snapshots.

- **Snapshots:** they now exist in `~/Projects/collect-v3-data/snapshots/` (`W1_features_<ts>.jsonl`, `W2_features_<ts>.jsonl`, `SHA256_<ts>.txt`). Verify the shas, then use only these; never the live run root.
- **First,** confirm that the frozen code still hashes to `CP7_FREEZE.json`. If anything drifted, stop.
- **Then do steps 3–4 exactly:**
  - population sizes per source × class (W1 + W2, pre-screen);
  - the uniform 100 with seed `seg-cp7:fresh100`;
  - byte-exact crops;
  - the sealed composed decisions;
  - 2 × 55 packs with the 10 controls, the canonical scanner by hash, `prompts/bsb.md` verbatim plus `prompts/segcp7_crop_rubric.md`;
  - `cp7/launch_cp7.sh` written and **not run**;
  - tests.

Update `seg/CP7a_RECEIPT.md` and `seg/CP7_COMMIT_LIST.json`. The last line must be exactly:
`SEG-CP7a: done | M1/M2 fixed | freeze: <sha> | frozen gate 22/22, D 9/9, C1 6/6, gallery 6/6 | population: <W1 n + W2 n> | drawn 100 (screen-drop <k> sealed) | packs 2x55 | scanner sha ok | launch_cp7.sh ready | tests: <n> passed`
