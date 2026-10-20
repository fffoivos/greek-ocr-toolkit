# SF7 — Insertion symmetry (BRIEF ONLY — not run; for the owner's decision, 18 Oct)

Status: written 17 Oct after the L1A2 audit; the coordinator's hard stop forbids further gate changes tonight. If the owner approves, this
runs as a normal fix round (gpt-6.1-sol, xhigh, network OFF) on `opus/spellcheck` from 90bcc286 (SF6c, gate frozen), followed by a
verification pass in the same reviewer thread.

## Why
The 100-line print audit of the sf6 AB release (L1R3 3680729; `~/Projects/greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/
L1A2_AUDIT100_RESULT.md`) measured precision 83/100 (weighted 82.5%, 95% CI 75–90). 13 of the 17 failing lines are iota subscripts the
release INSERTED where the print has none; 4 are breathings/accents inserted on unmarked forms. In every wrong card Google's original matched
the print. SF6 governs deletions only; insertions pass on reader agreement (A∧B) alone, and A and B share training data and therefore this
bias. Excluding inserted subscripts, precision is 95%: the reader's naming is sound; the gate lacks the symmetric rule.

## The proposed rule (mirror of SF6)
A release may INSERT a mark absent from Google's label only with **two positive presence signals**: reader (A∧B as one) AND detector
(observed mark in the slot's above/below zone, of a compatible family), or reader AND scored recogniser text that contains the mark
(SF6c certification: explicit score > 0.5, regional evidence, window containment). **A subscript insertion additionally requires an observed
below-mark** (detector below-zone component in the slot window; clipped/unseen below-zone → HOLD). Anything less → HOLD. Replacements
count as a deletion (SF6) plus an insertion (SF7). Elision aliases excepted. With today's detector (below-mark recall ≈ 48% held-out) this
holds almost every subscript insertion; L1F's recogniser evidence (job 3680752) is the second presence route once joined (L1R4).

## Witnesses (repository tests; all must HOLD or keep Google's form)
| Wave | Line | Google | Released (sf6) | Print (audit) |
|---|---|---|---|---|
| round1 | `00c322b3ee04b419d1979f22-p000055-l0033` | ὑποχωρήση. | ὑποχωρήσῃ. | ὑποχωρήση. |
| round1 | `043b454a8c255b6690fd3777-p000061-l0030` | περάση. | περάσῃ. | περάση. |
| round1 | `052a7a91dd9752b856b9fd8a-p000188-l0005` | τῆς | τῇς | τῆς |
| round1 | `0bff55647d1c2acd1caa8bf3-p000120-l0015` | τρώγη | τρώγῃ | τρώγη |
| round1 | `1092c25534f45a95669f3d2b-p000030-l0018` | οι | οἱ | οι |
| round1 | `241c524ed5b20f2baadf4b8b-p000119-l0012` | .Α. | .Ἀ. | .Α. |
| round2 | `32aae9fec147d3b483deb96e-p000107-l0033` | δείξη | δείξῃ | UNREADABLE |
| round2 | `39fbbdfd2c8030f211a318b7-p000053-l0008` | 1η | 1ῃ | 1η |
| round2 | `39fbbdfd2c8030f211a318b7-p000063-l0009` | δεσπότη. | δεσπότῃ. | δεσπότη. |
| round2 | `39fbbdfd2c8030f211a318b7-p000090-l0016` | Μεγάλη | Μεγάλῃ | Μεγάλη |
| round1 | `723c450ea9bb07fc4cdf47f9-p000024-l0013` | ΦΡΑΓΚΙΣΚΗ | ΦΡΆΓΚΙΣΚΗ | ΦΡΑΓΚΙΣΚΗ |
| round1 | `8f477fb59c9bc6957aadc800-p000119-l0025` | τρέχη | τρέχῃ | τρέχη |
| openarchives | `a4c40997-p000035-l0036` | ο | ὁ | ο |
| round2 | `b518f9f9b73fe9a3257fe2f0-p000078-l0012` | παληκαριά, | παλῃκαριά, | παληκαριά, |
| round2 | `c0b5231d0f42ddb64c8cc629-p000011-l0013` | Ῥώμη | Ῥώμῃ | Ῥώμη |
| mixed | `c57e3067ed37cedf17f285e6-p000044-l0024` | νύμφη | νύμφῃ | νύμφη |
| round2 | `ee2ae82a5d56b54859d7385b-p000177-l0008` | εὐπορῆς, | εὐπορῇς, | εὐπορῆς, |
Plus: every SF5/SF6/SF6b/SF6c witness keeps its outcome (no regression); the 83 audit lines whose correction matched the print are
listed with their SF7 outcome (released vs newly HOLD) so the cost is visible.

## Report (when run)
Held-out / M2 / witness tables before (SF6c) / after with an **insertion row** (marks inserted by family; lines turned HOLD by SF7);
the L1A2 audit lines re-scored under SF7 (precision of what remains released, with interval). Policy id `sf7-release-v1`.
