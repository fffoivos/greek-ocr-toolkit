# N1 gate: FAIL (17 Oct 23:34)

**Rule.** The frozen ink rule (sha 90080b5a) called 5 locked-eval slots "raised dot" (`n1_review/gate/gate_01.png` cells 4, 5, 6, 8
and 9). The lead's pixel check found **all 5 are baseline dots** (9. / 31. / 1.21 / 11.04 / 11.23), and the readers agree where
valid. **Raised-dot precision is 0/5**, far below the ≥ 99% gate. False edits on ranges: 0. The rule is NOT applied to training rows.

**Cause.** The dev raised-dot positives come almost entirely from one ELSTAT document (ee37…). The held-out split had none (N1R:
"held-out precision N/A, n 0"), so the vertical-position threshold was never validated on other faces.

**Alternative, a reading-based correction** (the coordinator's decision). The cost estimates are 0.2 points per 100 reads plus
controls.
- Read every Google `-` or `.` inside 4+-digit tokens in the v2 training rows: about 1,074 hyphen candidates per the step-0
  census.
- Two blind Sol reads plus a lead check of every agreed raised dot, the pattern that measured 12/12 + 18 lead-verified in N1-T.
- About 2,200 reads, roughly 4.5 points.
- The rule stays as a tag-only diagnostic.
