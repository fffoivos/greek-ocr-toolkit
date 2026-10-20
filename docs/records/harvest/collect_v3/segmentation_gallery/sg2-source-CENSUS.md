# G1d missed detector rows census

All **1,195 planned pages** (995 test + 200 sampled training) have page records. The cached detector failed on **1 page**; its missing count is unknown. Among **76,154 addressed detector rows** on measured pages, **6,514 (8.55%)** meet the missed-row criterion.

This is a census of detector row addresses, not human-verified printed rows: **70,305 fitted delivery rows + 5,849 unfitted structural rows** (including discounted rows), deduplicated by row ID. It does not re-estimate the pilot's 19% printed-row miss rate. Detector omissions, false rows and component ownership errors affect this denominator. Training counts describe the selected 200 pages, without population weighting.

**Source limits:** 416 locally inverted extraction ribbons are retained using their component ink. 380 archived raw responses have a byte hash differing from the frozen reader receipt, including the previously documented G1 witness. Actual/expected hashes and native-layout replay results are preserved in metrics/pages. Context candidates on mismatched responses require a matching native geometry/text replay against the frozen assignment; otherwise the label check is unknown. The mismatch is not repaired or represented as byte-exact custody.

## Reproducible definition

A missed row has at least 30% of its occupied native ink columns outside the union of **all archived Google line boxes**, including boxes not admitted to training. A column counts as covered when any assigned row-ink pixel lies inside a box. This includes partially uncovered rows; it does not mean zero geometric overlap. Frozen native assignments supply boxes where available; wikisource uses every raw response line in the native frame. No admitted crop, cache, source response, or manifest was changed.

Fitted rows use their component ink, even when the extraction ribbon is inverted. Unfitted structural records have no cached component custody/font curves: they use all foreground inside their structural box and x-height = 0.6 times box height (minimum 1px). The row JSONL marks geometry_source and xheight_source explicitly. These box/size proxies can include show-through, rules or neighbour ink; they are census candidates, not repair or recognition evidence. The page-median comparison uses fitted x-heights where available.

Positions use the ink centre: header <12% of page height, footer >=90%, margin when X centre is outside 10%-90% and width <18% page width; otherwise body. Types are mutually exclusive proxies, in order: page number (header/footer, width <=6 xh); table cell (>=2 disjoint peers within 0.6 xh baseline, width <30% page width); heading (xh >=1.25 page median, or header width >=8 xh); one-word line (width <=14 xh, no occupied-column gap >=0.6 xh); otherwise body text. Numeric content and true word identity are **not** verified. Each row records the measurements.

## Full-text label check

For the **368 body-text proxy rows**, **14 (3.80% of all body-text misses)** have an inferred candidate line in the raw response's **document.text**, bracketed by uniquely matching same-column neighbour texts. There are **18** empty intervals and **336 unknowns**. The candidate share among assessable intervals is **43.75%**.

Neighbour strings are NFC/casefold/whitespace normalized, >=8 characters and unique in full text. The nearest >=70%-covered peers above/below must occur in that order. Intervening nonblank page-text lines must match the count of unlabelled detector peers in the interval; each gets a candidate in vertical order. Merely matching the neighbours is insufficient. Missing, shared, reordered or ambiguous anchors stay unknown. A candidate is **context evidence that a label may exist**, not pixel-verified transcription or proof that only box mapping failed. Empty intervals do not prove Google failed to recognize the row: merged neighbour text may contain it. JSONL retains anchors, candidate, reason and raw-text hash for review.

## Counts per wave

| Wave | Pages | Detector rows | Missed | Missed % | Body text | Text candidates | Candidate % of body | Unknown |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
|cyrillic|50|2706|237|8.76|34|0|0.00|24|
|mixed|96|6110|606|9.92|157|0|0.00|156|
|openarchives|183|6476|133|2.05|27|8|29.63|19|
|parliament|128|21742|1473|6.77|8|1|12.50|7|
|round1|216|12449|1067|8.57|44|1|2.27|41|
|round2|103|6389|574|8.98|44|1|2.27|43|
|vouli|77|5144|547|10.63|14|2|14.29|10|
|wikisource|342|15138|1877|12.40|40|1|2.50|36|

## Position counts per wave

|Wave|body|footer band|header band|margin|
|---|---:|---:|---:|---:|
|cyrillic|197|3|22|15|
|mixed|176|92|90|248|
|openarchives|92|23|16|2|
|parliament|8|198|172|1095|
|round1|297|161|236|373|
|round2|84|92|137|261|
|vouli|26|125|84|312|
|wikisource|461|479|384|553|

## Type counts per wave

|Wave|body text|heading|one-word line|page number|table cell|
|---|---:|---:|---:|---:|---:|
|cyrillic|34|57|19|15|112|
|mixed|157|140|78|135|96|
|openarchives|27|39|22|33|12|
|parliament|8|293|50|299|823|
|round1|44|307|192|301|223|
|round2|44|186|103|154|87|
|vouli|14|255|45|151|82|
|wikisource|40|465|199|739|434|

Machine-readable: [missed row records](rows.jsonl), [all 1,195 page dispositions and input hashes](pages.jsonl), [metrics including split/wave counts](metrics.json).

Offline reproduction: `PYTHONPATH=. /path/to/python scripts/labelfix/census_missed_rows.py --source-root /read-only/harvest-repository`. No network, recognition inference or detector rerun.
