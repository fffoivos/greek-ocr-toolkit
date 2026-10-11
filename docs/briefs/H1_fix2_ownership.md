# H1 fix 2 — CP-H1 cycle 2 HIGH 1 + HIGH 2: row ownership from the line's own geometry; column bands per vertical region (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). No network, no Google calls, no `.git` writes. Do not rerun the pilot; offline re-gate only, sidecars as in fix 1.
Reviews: docs/reviews/CP-H1.md (cycle 1), docs/reviews/CP-H1_c2.md (cycle 2 HOLD). Brief of fix 1: docs/briefs/H1_fix1_geometry.md.
STRUCTURAL DIAGNOSIS (coordinator, 03:00; two HOLDs on the same gates): both gates were built from the crop alone instead of from the line's own
geometry that the pipeline already has. (a) The neighbour-sliver gate measures ink above/below the BODY band, so the line's OWN accents, breathings,
ascenders and descenders count as "neighbour ink": 112 of the 126 newly rejected sampled lines were sliver rejections, 39 of them tier-1 lines; two of
them inspected by eye are clean single rows (anemi-ffe26907…p159 l24, anemi-e28081a0…p93 l38; height_fraction 0.057 and 0.139, no visible sliver).
(b) Column bands are computed once per page, so rows that genuinely span both columns (headings, prose above a two-column glossary; reviewer's
`d163abb4… p112`) are split or rejected as cross-column.
Required:
1. Neighbour ownership from the line's own four guide lines: use greekocr.glyphs (line_glyphs / the straightener's fitted baseline, x-height, accent_top,
   font_bottom/descender) to define THIS line's zone = [accent_top − 0.15·xh, descender_bottom + 0.15·xh]. Neighbour ink = connected components whose
   centroid lies OUTSIDE that zone AND whose vertical extent does not overlap the zone by more than 25% of their own height. Reject only if such components
   cover ≥ 12% of the crop height AND ≥ 20% of the crop width together, or if any of them overlaps the zone (i.e. a neighbour's letter actually touches the
   row). A diacritic-bearing clean row must pass: add the two inspected ids above as regression fixtures that MUST pass, plus the reviewer's cycle-1
   sliver example that MUST reject.
2. Column bands per vertical region: segment the page into horizontal regions by the row structure (consecutive rows with the same column pattern form a
   region; a row whose ink spans > 70% of the page width is a full-width row region of its own); compute bands per region; a row that spans the full
   width in a full-width region is NOT cross-column; splitting/rejecting applies only inside multi-column regions. Reviewer example `d163abb4… p112`
   (upper spanning prose + lower two-column glossary) as a fixture: upper rows pass intact, lower fused rows split.
3. MEDIUM (cycle 2): the ruled table on `d80c7cca… p49` escapes the page gate: when long horizontal AND vertical rules form ≥ 2 closed cells, it is a
   table regardless of the lattice test. Fixture.
4. Offline re-gate over the stored 14,200 records (sidecars under docs/harvest/fix2/ like fix1), addendum "Fix 2 (offline re-gate)" in PILOT_v1.md with the
   before/after counts and, for the 500 sampled lines, the number now rejected by each reason; the number of tier-1 lines rejected must be reported
   explicitly (expected: near zero).
5. Tests green: `.venv/bin/python -m pytest tests -q -p no:cacheprovider -k harvest`. INVENTORY.
Last line exactly: `H1FIX2: done | sampled_now_rejected: <n> | tier1_rejected: <n> | tests: <n> passed`.
