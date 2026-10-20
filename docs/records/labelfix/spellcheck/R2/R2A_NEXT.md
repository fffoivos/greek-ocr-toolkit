# R2a: next options (17 Oct 2026, prep only, no run)

**Recorded result** (R2A_DIGEST.md, 8896ab792): FAIL on the preregistered criteria, and R1-A stays.
- The one clear effect: capital positive recall on the T4 witnesses rose from 47.2% to 87.5% (all three seeds), and net wrong target
  slots fell from 104 to 42.
- The checkpoints, readings and T4 scoring are kept unchanged.

## (a) R2a-2: Sol capitals top-up, capital-mark recall as the primary

- **Recipe:** identical to R2a. The only change is the overlay: the capitals slice is completed to the plan's 1,300 slots (800
  negative / 500 positive; today 214 / 127).
- **Labels:** a Sol one-question pass, "which breathing and accent are printed on this capital?", using the grave-pass pattern.
- **Qualification first.** Sol is qualified on grave vs acute (25/26 recall, 0/26 false), but NOT yet on capital breathings and their
  compounds. Before any labels are used, run a capitals qualification set: about 60 slots from the T2 resolved capitals, where two-reader
  truth exists. It must reach ≥ 95% exact-tuple agreement with 0 invented breathings; otherwise (a) falls back to (b).
- **Primary metric:** capital-mark recall (exact tuple) on capital positives, with noninferiority on everything else (the same margins,
  common-class and owner protection).
- **Statistical caveat.** We chose this primary after seeing R2a's T4 numbers, so the T4 witnesses cannot confirm it. R2a-2 needs a
  FRESH capitals witness set from documents in neither T2 nor T4 (about 150 positives + 150 negatives). That set needs reading
  (Sol-qualified pass + my pixel check of disagreements).
- **Cost:** the Sol pass (about 1,200 + about 300 items at about 1.2k Codex tokens each), one cluster job (about 25 min), and no Opus
  reading.
- **What it can show:** whether capital marks are learnable from native print without harming the rest. It does not address
  false additions.

## (b) Wait for the Claude reset; complete every slice with Opus two-reader tranches

- **Labels:** the plan's original method (two blind readers + tiebreak) tops up all five slices to 4,000 slots. The deficits are
  894 negative and 1,577 positive (B6_RESOLVE_REPORT.md).
- **Cost:** about 3,000 cards at about 160k Opus tokens per 100-card context, so about 4.8 M tokens. This is exactly the usage the owner
  paused. Plus one cluster job.
- **Primary:** the original false-addition criterion. It is underpowered on T4 (BASE makes only 26 false additions in 831
  seed-observations), so it also needs witnesses enriched for the hallucination contexts from the release audit (capitals in ALL-CAPS,
  ο/οι monotonic, -η subscripts), where BASE actually errs.

## Regressions to show the owner

These go into the next failure-modes sheet, as a "what moved in R2a" group:
- `384c3f89-p000053-l0021:s8` (s16): subscript invented;
- `177b717d-p000054-l0004:s4` (s17): subscript invented;
- `177b717d-p000017-l0012:s24` (s17): dialytika invented;
- `22fda82b-p000063-l0039:s10` (s18): subscript dropped;
- owner witness `602cc72e-p000167-l0027:s10` (s18): grave-only became psili+grave.

**Lead view:** run (a)'s qualification set first. It is cheap and decides whether (a) is viable at all. (b) is the only route for
false additions, and it waits for the reset and the owner's go on Opus reading.
