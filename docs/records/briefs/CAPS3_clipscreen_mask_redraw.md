# CAPS3: headings_caps: edge-clip screen, frozen masking, fresh 100-card Sol packs (gpt-6.1-sol, medium, network OFF)

**Coordinator ruling after CAPS2** (letters 99, crop_ok 89: a fail by one; that result stands as recorded).

## 1. Row-level edge-clip screen
- Applies to the CAPS1 pool: W1 headings_caps candidate rows, rotated_crop excluded (2,211 rows).
- Flag a row when its ink touches the **left or right crop edge beyond the existing clip tolerance**, in the same spirit as screen_merged.
- **Build it from the toolkit's existing readability/clip helpers.** Find them read-only, e.g. `greekocr/` readability or crop-edge / clip checks, or the geometry-audit clip measure, and name the function used. **No new heuristics and no new thresholds:** use the helper's existing tolerance.
- Report the rows removed per source.
- Validate it on the CAPS2 verdicts: of the 6 crop_clipped cards, how many does the screen flag, and how many of the 89 crop_ok=y cards does it flag (false positives)? This is a report, not a gate.

## 2. Mask the remaining rows with the frozen T6b tool
- Use `docs/records/harvest/recut_v1/w1_masked/run.py` code paths: params 801d517e, the T6b guard (original-crop dark ink, >0.30 → byte-exact original with wrong_line_risk), the T6c2 matcher.
- Caps/heading rows were excluded from T6b only by its row filter: lift that filter for this population. Change no masking code.
- Run inline, ≤2 workers. A live T6h run uses 4 workers on this Mac.
- Outputs go to `docs/records/harvest/recut_v1/w1_masked/caps_masked/` (records.jsonl as in T6b, crops git-ignored).
- Report masked / guarded / unmatched / changed per source.

## 3. Fresh draw and packs, per the Sol-reading HANDOVER (as in CAPS1)
- 100 uniform masked cards, seed `caps3:headings_caps:masked`, over the screened and masked pool. Masked rows plus guarded originals; unmatched rows excluded. **No card from CAPS1's 100.**
- **Reuse the 10 lead-approved controls** from CAPS1/CAPS1b (c057, c009, c013, c026, c046, c041, c029, c072, c035, c066) with their approved truth: 5 per context, re-seeded order, fresh opaque ids. No new contact sheet is needed.
- Bed `caps3`, contexts c1 and c2 (55 items each), at PACK_ROOT `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs`. Keys go outside. The prompt is the verbatim `prompts/bsb.md`. Closure uses the CAPS1 adapter.
- Launchers: the existing `sol_packs/launchers/`. Give the two launch lines.
- Tests: screen reproducibility, masking identical to the T6b code path (re-mask 3 T6b rows byte-identically), draw seed, closure, control placement.

## Hand-off
README at `docs/records/harvest/recut_v1/w1_masked/caps3/README.md`. Leave a guarded commit list. The last line must be exactly:
`CAPS3: done | clip screen removed: <n> (<per source>) [CAPS2 clipped flagged <k>/6, fp <m>/89] | masked: <m>/<g>/<u> | cards: 100 | controls: 10 reused | launch lines: 2 | tests: <n> passed`
