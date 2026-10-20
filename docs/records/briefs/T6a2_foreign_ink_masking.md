# T6a2: foreign-ink masking inside the original crop with the existing `_voronoi_keep` ownership rule (gpt-6.1-sol, xhigh, network OFF, ≤ 120 min)

This runs in this worktree, `sol/recut-v1`, on top of T6a (6ed722f8).

**T6a's result stands as a recorded negative and is not shipped.** Vertical tightening removed readable neighbour ink on only 2/57 overrun cards, because on tightly set pages the neighbours' descenders and accents lie inside this line's own band.

**Coordinator ruling: masking.**
- Inside the **original** crop rectangle: no expansion, no new segmentation.
- Ink components that `greekocr/glyphs/recut.py:_voronoi_keep` assigns to a **neighbouring** line are painted with the local page background.
- This line's components are kept untouched.

That is the owner's 8 Oct component-ownership rule ("the curve and the distance from the centroid of the letters should define the region"), applied with the built tool.

## Step 0: stop condition. Do this first and write it into REUSE.md

The deployment cutter is ours, so masking must be applicable **identically at inference**. Training crops and deployment crops must get the same treatment.
- Find where the page-lines runtime path (`greekocr/glyphs/lines_api.py`, `page_lines.py`, the 046bd52 runtime) produces line crops at inference.
- State exactly where the same masking call would sit: which function, and with which inputs. At inference there is no Google geometry, so name what supplies the neighbouring lines' centre curves there (the runtime's own detected lines).
- Then show that the **same function**, given equivalent line curves, produces the same mask on a training page and on that page through the runtime path. Use a few F2 pages: run the runtime's detected lines and compare with Google-box-derived curves. Report the agreement.
- **If masking cannot be applied identically at inference, STOP.** Write why in REPORT.md and make no further changes. A train-only pixel edit is a mismatch.

## Step 1: build (only if step 0 passes)

1. **Reuse, not a new algorithm.** Write a thin opt-in function, e.g. `mask_foreign_ink(page, line, neighbours, crop_box) -> masked crop + record`, that calls `_voronoi_keep` (or its existing public wrapper) for ownership. Existing defaults stay unchanged. T6a's `vertical_recut.py` stays as is.
2. **Fill with the local page background,** never flat white: the median of a neighbourhood ring around each masked component, on the page raster. Record the fill statistic per crop: ring median, ring spread, masked-pixel count, masked-component count.
3. **Ownership edge cases**, tested:
   - accents and breathings above the line;
   - descenders;
   - apostrophes and coronis;
   - iota subscripts;
   - a component touching two lines' bodies (cut at the midline, the existing behaviour);
   - punctuation near line ends.

   **This line's own accents, descenders and apostrophes must never be masked.**

## Step 2: develop on F2 data only

Use the same 160 v2 dev cards as T6a, plus T4c/C0 cards of the same strata if useful. Measure:
- readable neighbour ink removed on the crop_ok-n cards (visual plus a component metric);
- **own-ink loss on the crop_ok-y cards: must be 0**, both by component pixels and by inspection of every changed y card;
- the fill statistics.

Tune only the ownership tolerance parameters, if `_voronoi_keep` exposes any. Then freeze and hash the parameters.

## Step 3: harm test

Same as T6a: E4 ctrl_s0 (sha e20cd6cd…), Mac CPU, the same 5,770 F2 lines, paired. Report:
- overall and per-source CER, with bootstrap CIs on the difference;
- changed vs unchanged crops, where **unchanged crops must give identical predictions** (checked exactly);
- crop_ok n vs y dev subsets;
- the geometry-clean subset.

The rule: CER must not get worse overall. Per-source results are reported either way.

## Hand-off
Under `docs/records/harvest/recut_v1/masking/`:
- the REUSE.md addendum, with the step-0 inference placement and agreement;
- REPORT.md;
- params.json;
- per-source receipts;
- tests.

Outputs are masked crops **beside** the originals. Nothing is admitted.

Commit with the guarded helper. The last line must be exactly:
`T6a2: done | inference-applicable: <yes|no> | dev neighbour-ink removed: <x>% own-ink loss: <y>% | harm CER orig/masked overall: <a>/<b> changed: <c>/<d> | params: <sha12>`
