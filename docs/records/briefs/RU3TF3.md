# RU3T-F3: finalise phase 1 with r3/r4/r5 replacements (gpt-6.1-sol, medium, network OFF; no .git writes; NO reading, browser or computer-use)

The r3/r4 (12) and r5 (5) replacement readings ran (`artifacts/ru1/ru3t/r3_replacements/ and the r5 location from RU3TR5_RECEIPT.json`; the attempt files still say CLAIMED, but the launcher
logs show rc 0 for each). First, confirm completion of each from its run json, answers and rollout. Mark any incomplete one
explicitly; never guess.

Then run the replacement-aware `ru3t_finalize.sh` up to the lead material (as in RU3T-F1):
- v4.4 scans, gates, coverage and the combine, with r3/r4 replacing the VOID readers;
- the review sheet ONLY for genuine lead_review positions (disagreements, uncertain reads, and positions still missing a second
  valid read);
- the 60-cell audit sheet (40 edit_hard + 20 keep_soft);

all in the scratchpad `ru1_review/ru3t_f3/`, with templates. Do not write ru1_v3_train yet.

**Last line:** `RU3TF3 READY: replacements done <n>/17 (void <list>); edit_hard <n>, keep_soft <n>, lead_review <n> (<reasons>); review cells <n> on <n> sheets; audit cells 60`
