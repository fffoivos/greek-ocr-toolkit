# R2a-2 preregistration (written 17 Oct 2026, BEFORE any R2a-2 witness or repair label is read)

**Status:** prepared on the coordinator's instruction. It runs only on the owner's go (option (a) in R2A_NEXT.md). If the owner picks
(b), this file and the reads prepared for it are shelved.

## Question

Does completing the capitals repair slice with Sol-read native print labels raise capital-mark recall without harming anything else?

## Arms (3 seeds each: 20261016, 20261017, 20261018)

| Arm | Data | One variable vs parent |
|---|---|---|
| BASE | the frozen old pool (job 3681404 seeds 17/18; R1-A for 16) | — |
| R2a-2 | the old pool + the R2a v2 overlay (1,572 slots) + the capitals top-up to 1,300 capital slots (800 negative / 500 positive) | the overlay, vs BASE |

- The recipe is identical to R2a (job 3683130): epochs, batch, sampler, optimiser, LR, augmentation.
- Overlay corrections replace and never append. The old pool is kept exactly as BASE used it, duplicates included (R2J4).
- **Also reported:** R2a-2 vs R2a, to isolate the top-up's own effect. This is secondary and has no pass criterion.

## Evaluation sets (fixed before reading; documents disjoint from every training and repair document)

- **W-CAP (new):** about 150 marked + 150 bare capitals from documents outside T2, T4, the old pool, validation, calibration and every
  LQB truth set.
  - Truth tier C: Sol one-reader with the compound re-read rule.
  - Every disagreement between arms on a W-CAP slot is pixel-checked by the lead before scoring, blind to arm. Any truth correction is
    recorded and applied symmetrically.
- **The protection sets, as in R2a:** held-out (16 docs), T4 witnesses (791; T4 is in-sample for any capitals claim and is used ONLY
  for protection here), DEV (600 lines), and the owner witnesses (overlay v1.1).

## Primary endpoint

Capital-mark exact-tuple recall on the W-CAP marked capitals (breathing + accent both correct), R2a-2 vs BASE.

**Pass requires all of:**
- (1) pooled recall gain ≥ 10 pp;
- (2) a document-cluster bootstrap 95% interval (50,000 replicates, seed 20261017) excluding 0;
- (3) a gain in ≥ 2 of 3 seeds, with a positive mean;
- (4) on the W-CAP bare capitals, invented marks not increased by more than 2 pooled (a false-addition guard).

## Noninferiority (unchanged from R2a, the same Holm family and margins)

- **Common classes** (≥ 200 support) on held-out: precision lower bound > −0.20 pp, recall lower bound > −0.50 pp.
- **Sparse classes:** no net increase in exact-name errors; every paired regression is listed. Status "unestablished" does not block,
  but a net increase does.
- **Non-target T4 slices:** the same margins.
- **Owner witnesses:** no regression on a named owner slot. Any regression means FAIL, the same rule as in R2a.

## Verdict

PASS only if the primary passes AND every noninferiority family passes or stays inconclusive without a point-estimate breach. Any FAIL,
or an inconclusive primary, means not adopted. Summary sentences may be no stronger than the table rows.

## Fixed before reading

- the W-CAP document list and slot list (with hashes);
- the top-up slot list;
- the Sol prompt (CQ1 verbatim);
- the re-read rule;
- the controls;
- this file's sha256, recorded in the CQ4 receipt.

## Amendment 1 (17 Oct, before any W-CAP or top-up read)

**Why:** the CQ4 inventory found only 3 never-used documents (at most 90 W-CAP slots, against a 210-slot minimum).

**Change:** W-CAP is drawn from the **validation-role documents** (17; `doc_roles.json`).
- These are held out from every training set and from T2/T4/CQ1. Their role is an evaluation reserve (the R2b validation reservation),
  so adding test slots there does not conflict with it.
- The 3 never-used documents are also eligible.
- Calibration-role documents stay excluded, because CAL fits thresholds on them.

Every other rule is unchanged: disjoint from the top-up documents, at most 10% of W-CAP per document, at most 5 per page.

**Scanner:** the canonical v4.4, copied by hash (sol-reading `tools/scan_rollout.py`, sha256 dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547).

## Amendment 1a (19 Oct 2026, CQ6 coordinator consequence note)

The validation documents are now exposed to capitals witness selection, so they
cannot serve as a fresh final capitals readout. The locked (ii)/(i-b) strata are
the only untouched final cohorts. The LQB in-sample guard lists the W-CAP items
against R2a-2. This is an exposure guard, not a claim that W-CAP was trained on:
W-CAP remains an independent evaluation witness and is never training data.

This consequence note is recorded after the existing CQ4 reads, as directed in
HANDOFF_20261018_spellcheck.md §2 and CQ6. It does not claim to predate those reads.
No endpoint, quota, seed, recipe or truth label changes. Historical CQ4 receipts
retain their original freeze hash and acquire a separate current binding.
