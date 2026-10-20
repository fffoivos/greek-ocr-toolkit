# T14c — Flush montage: crops stacked with NO gaps and NO rule, grouped by background shade, padded with their own background (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network ON (Google Vision + Document AI; ADC). No `.git` writes. Cost cap USD 0.50.
Context: T14/T14b (docs/records/harvest/MONTAGE_v1.md): readers are deterministic on single crops (100%), but montages with white gaps (+ rule or not) change 20–47% of
readings. Owner's hypothesis (13 Oct): the gap layout makes the recogniser look at a strip inside a box; a stack that looks like a natural page column
(lines directly under each other, uniform paper shade) should read like the page and preserve the single-crop readings.
Required:
1. New layout `flush` in greekocr/harvest/montage.py (keep the existing layouts untouched): crops pasted directly one under another, y advances by the crop
   height, zero gap, no rule, no outer padding. Left-aligned; each crop's right-hand padding to the group width is filled with THAT crop's own background
   shade (median of its brightest 50% pixels), never white 255. Native pixels, no scaling.
2. Grouping: over the SAME frozen 100 T14 lines (docs/records/harvest/montage_v1/sample.json, same order source), order by (background shade, crop height) so that
   neighbours in a montage share paper shade and type size; then cut consecutive groups of N=10 and N=20. Record per crop: background shade, height, group.
3. Read every flush montage with both readers (≈ 30 calls), same cache/budget discipline as T14 (reservations, raw responses under
   docs/records/harvest/harvest_big/montage_v1/, assignments/maps/comparisons under docs/records/harvest/montage_v1/flush/). Assignment: the existing ≥70% height rule;
   report merged/lost/split exactly as T14 did (adjacent bands make straddling possible — count it, do not hide it).
4. Compare with the cached single-crop reads: exact NFD identity % and letters+marks identity % (T14b helper), per reader, per N; same for the T14 (rule) and
   T14b (no-rule) layouts on the same lines so the table has rows {rule, no rule, flush} × {N=10, N=20} × readers × {exact, letters+marks}.
5. Report addendum "Flush layout" in docs/records/harvest/MONTAGE_v1.md: the table, merged/lost/split counts, one PNG preview of the first N=10 flush montage copied
   to docs/records/harvest/montage_v1/flush/preview_n10.png (small file), and a verdict: adopt flush at N if no merged/lost and exact identity ≥ 97% for both readers;
   else state the identity reached and whether flush is closer to single reads than the gap layouts. receipt.json updated.
6. Tests (no network) for the flush renderer (zero gaps, own-background padding, band map) and grouping. INVENTORY.
Last line exactly: `T14C: done | flush_exact_vision_n10: <pct> | flush_exact_docai_n10: <pct> | flush_exact_vision_n20: <pct> | flush_exact_docai_n20: <pct> | merged_lost: <n>/<n> | calls: <n> | tests: <n> passed`.
