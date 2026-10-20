# RU2T-F3: coverage gate counts traced derivatives; item-level loss; finalise (gpt-6.1-sol, medium, network OFF; no .git writes; NO reading, browser or computer-use)

`artifacts/ru1/ru2t/RU2TF_STOP.json`: ctx01/r2 had a clean canonical scan, but the assigned-crop coverage gate failed (73 crops
assigned, 79 images viewed, many crops "missing"). The reader most likely viewed zooms and montages, which the HANDOVER allows.

**Lead ruling.**
1. A crop counts as VIEWED if the reader viewed it directly, OR viewed an image that the v4.4 replay/reproduction log shows was built
   from it: a zoom, crop or montage whose literal command inputs include that crop.
2. A crop still not viewed after (1): only the answers for THAT item are dropped, so the position lacks that read and goes to
   lead_review if no second valid read remains. The context is NOT voided.
3. Apply the same rule to every RU2T reader-context. Report coverage per context: direct / derived / unviewed.

**Do.** Implement the rule in the finaliser, with tests (a direct view, a derived montage, an unviewed crop with item-level drop).
Then run `scripts/secondary/ru2t_finalize.sh` to completion, as in RU2T-F (`docs/records/briefs/RU2TF_finalize.md`): label file, LQB
registration, review and audit sheets.

**Last line:** `RU2TF3 READY: coverage <per ctx direct/derived/unviewed>; rows <n> (ok <n>, hold <n>); edits <n>; keep <n>; lead_review <n>; ru1_v2_train sha256 <hex>; LQB registered <ok>; review cells <n>, audit cells 30`
