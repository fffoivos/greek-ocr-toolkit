Implemented all nine curled starts. **1,220 tests pass.** Committing was blocked by sandbox permissions on Git’s `index.lock`; nothing was pushed.

The fitter now chooses a smooth bend using all nearby letter evidence. Technically, it scores quadratic endpoint bends, admits tall-letter bottoms after the initial fit, and keeps ruled columns independent.

Residuals are **median / maximum pixels**, before → after:

| Crop | Before | After |
|---|---:|---:|
| l00017* | 16.00 / 34.26 | 0.63 / 1.57 |
| l00018* | 65.13 / 67.68 | 0.37 / 0.54 |
| l00021 | 61.20 / 61.93 | 0.55 / 2.17 |
| l00023 | 0.81 / 4.79 | 0.81 / 4.79 |
| l00025 | 9.56 / 18.15 | 1.03 / 2.05 |
| l00029 | 4.46 / 32.62 | 0.69 / 2.01 |
| l00030 | 8.59 / 25.32 | 0.30 / 0.92 |
| l00032† | 2.02 / 2.02 | 0.70 / 0.70 |
| l00035 | 12.26 / 33.28 | 0.53 / 1.47 |

\* Capital contacts: these starts contain no x-height letters. Three l00018 contacts previously had no baseline because of false splits.  
† One body-letter contact; including capitals: **14.35 / 36.11 → 0.41 / 1.60**.

All **101 original glyph tests**, **9 new curl tests**, and **1,110 provenance/API tests** pass. One visibly improved golden baseline was updated with its reason and provenance hash.

Across **444 crops**, **10 direct fits** and **7 column-aware fits** changed by more than 3 px mean. Six column-aware changes visibly improve alignment; one severely clipped crop remains indeterminate without its document prior.

- [Curled starts image](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-curl/.astra/curl_after.png)
- [Changed lines and assessments](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-curl/.astra/changed_lines.png)
- [Full measurements and verification](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-curl/.astra/verification.txt)

A validated patch and guarded commit script are ready, including the exact attribution. From the worktree in a terminal with Git write access:

```bash
bash .astra/commit_change.sh
```

RESULT: PARTIAL All nine starts fixed; commit blocked and one clipped-crop comparison remains indeterminate. | TESTS: 1220/1220