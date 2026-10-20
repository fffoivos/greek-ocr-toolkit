# N1-C: slot renderer, control candidates and glyph-pass pack builder (gpt-6.1-sol, medium, network OFF; no .git writes; Mac CPU; no reading run)

You work in the worktree `~/Projects/greek-ocr-toolkit-secondary` (branch `opus/secondary-corrections`). Read first:
- the plan, `docs/records/labelfix/secondary/PLAN.md` §2;
- the N1 plan, `docs/records/labelfix/N1_NUMERIC_SEPARATORS_PLAN.md`;
- `docs/records/labelfix/N1_STEP0_REPORT.md`;
- `docs/records/labelfix/secondary/N1L_REPORT.md`;
- the reader prompt, `docs/records/labelfix/secondary/prompts/sep.md`. Do not edit it. It defines the item fields the packs must carry.

The reading discipline is
`~/Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/HANDOVER.md` §4–5. Read it, but do not modify that worktree.

**Inputs (read only).**
- `artifacts/n1/frame_step1.jsonl`, the 600 rows with `partition == "step1"`. Do NOT render the `locked_eval` rows or any line in
  `artifacts/n1/n1_reserved_doc_line_ids.txt`: call `greekocr.numerics.locks.load_locks(...).assert_fit_rows(...)` on every id you
  render, and test that it refuses reserved ids.
- W1 rows: `~/Projects/collect-v3-data/run/W1/features.jsonl`. This is a LIVE root: read only, never touch `run.lock`, write nothing
  under `~/Projects/collect-v3-data/`.
- Google symbol-level responses under `~/Projects/collect-v3-data/run/responses/`. Find how a W1 row maps to its response and
  symbols; the collector code in `~/Projects/greek-ocr-toolkit-sol-collect/collect_v3/` shows it.
- **Crops.** Regenerate them with `collect_v3.storage.ensure_crop`, imported read-only from `~/Projects/greek-ocr-toolkit-sol-collect`.
  That function writes to `row['crop']`, which is inside the run root, so ALWAYS pass a shallow copy of the row whose `crop` is
  rewritten to
  `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_cache/crops/<crop_sha256>.png`.
  On a hash mismatch → `crop_unavailable`; never substitute.

**Do.**
1. **Slot localisation** (`greekocr/numerics/slots_geom.py`, with tests). Map a frame slot (character offsets into the W1 `text`/label)
   to pixel boxes in the crop, using Google's symbol boxes for the two flanking digits, transformed into crop coordinates via
   `crop_bbox`.
   - For a boundary slot, use the one digit plus the space up to the next symbol, or 1.5 digit widths.
   - Record `geom_status`: ok / no_symbols / misaligned. Misaligned means the text-to-symbol alignment disagrees.
   - Never fall back to guessing.
2. **Renderer** (`scripts/numerics/n1_render.py`). Per slot:
   - `line` PNG: the whole crop, with two small mid-grey triangles drawn OUTSIDE the ink band, above and below the gap centre. They
     must not overlap any ink pixel; test this.
   - `zoom` PNG: from the left digit's left edge to the right digit's right edge, plus 30% of digit height padding on every side,
     scaled 3× with Lanczos.
   - The digit-band measurements go into a side record, never into the pack: digit top, baseline, digit height, gap width, and the
     ink components inside the gap from `greekocr.glyphs` helpers (bbox, height, centre y relative to the band). This record is the
     raw material for the step-2 rule and the owner audit.
3. **Control candidates.**
   - Draw 96 slots from W1 elstat, gazette_1982_1985 and gazette_1986_1990 documents that are in NEITHER the step1 frame documents NOR
     the reserved documents NOR C1 cards, seed `20261017:N1C:ctrl`.
   - Mix: 24 Google `.` in a grammar thousands slot; 24 Google `,` decimal; 24 Google `-` in a range; 12 Google `-` inside a 4+-digit
     token (the suspected raised dots); 12 empty inner gaps.
   - Also add the three C1 separator cards (`elstat--c5f7ea1f26d39839--s000-l0367`, `elstat--ee37bc488988f1bd--s000-l0445`,
     `elstat--ee37bc488988f1bd--s000-l0457`) as reference sheets only, not as controls: C1 lines are excluded from the frames, but
     they may serve as anchors for my eye.
   - Render them all with the same renderer.
   - Build contact sheets for the lead at
     `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_ctrl_sheets/`.
     Use ≤12 candidates per sheet, each cell showing the zoom image large, the line image small, a cell number, and the
     **Google glyph**. The lead needs the Google glyph to see disagreements. These sheets are NEVER placed in a pack folder.
   - Write `artifacts/n1/controls/candidates.jsonl` with slot ids, cell numbers, Google glyph, grammar, the geometry record and image
     hashes.
4. **Pack builder** (`scripts/numerics/n1_build_packs.py`, with tests). Build it now, but do NOT run it on the real bed. It takes
   the 600 step1 slots plus a lead-approved `artifacts/n1/controls/approved.jsonl` (slot id → truth meaning). It writes:
   - contexts of ≤100 items (≈86 bed + ≈9 controls), seeded order `20261017:N1-1`;
   - item fields per `sep.md`: `item_id` (`k` + 10 hex), `line`, `zoom`, `options`, with the 8 meanings shuffled onto letters A–H per
     item;
   - images copied into `img/` under content-hash names, with no metadata (strip PNG text chunks) and no symlinks;
   - PACK_ROOT
     `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/n1/ctxNN/r1/`,
     containing only `items.jsonl` and `img/`, with `MANIFEST.r1.json` beside each context folder;
   - keys in `artifacts/n1/keys/` (item → slot id, option map, control truth, geometry record ref).

   Add a `--calibration` mode that builds ONE context from the approved controls alone. The lead first runs that context to qualify
   the new prompt against their own pixel reading. Test the builder on a fixture of 30 fake slots with the closure checker: copy the
   sol-reading `tools/scan_packs.py` into `scripts/secondary/reading/` if it is not already there; RU1-0 may have copied it, so reuse
   it and do not duplicate.
5. **Answer mapping** (`scripts/numerics/n1_map_answers.py`, with tests). Option letter → meaning via keys; per-context control score
   (more than 1 control error → VOID); per-slot output joined with the geometry record and the Google glyph. Test it on fixture answers
   covering: a void context, an unreadable, an invalid letter, and a missing item.
6. **Receipt and report.**
   - Receipt `artifacts/n1/N1C_RECEIPT.json`: inputs + outputs with sha256; geometry status counts over the 600 step1 slots (render the
     geometry records for all 600 now; do not build packs); crop_unavailable count; tests.
   - Report `docs/records/labelfix/secondary/N1C_REPORT.md`, listing the contact sheet paths.

**Constraints.**
- Allowed writes: `greekocr/numerics/` (new files only), `scripts/numerics/`, `scripts/secondary/reading/` (new files only),
  `tests/` (new files only), `artifacts/n1/` (new files only; never modify the existing frame/lock files),
  `docs/records/labelfix/secondary/` (new files only), the scratchpad `n1_cache/`, `n1_ctrl_sheets/` and `sol_packs/n1/`.
- Do not touch `greekocr/labelfix/`.
- Pillow and ImageMagick image work runs under
  `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B`. Pure-text tests run with
  `python3 -m pytest --noconftest -q`.
- You may open rendered images only to self-check the renderer on at most 5 slots. Do not classify any glyph.

**Last line:** `N1C READY: step1 geometry ok <n>/600 (no_symbols <n>, misaligned <n>, crop_unavailable <n>); control candidates <n> on <n> sheets; builder + mapper tests <n> passed; calibration mode <ok>`
