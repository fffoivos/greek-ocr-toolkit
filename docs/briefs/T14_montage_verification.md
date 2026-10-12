# T14 — Montage reads: stack line crops into one image per call, verify against single-crop reads on 100 pilot lines, both Google readers (gpt-6.1-sol, xhigh)
Workspace: this repo (greek-ocr-toolkit, main). Network ON (Google Vision + Document AI; ADC). No `.git` writes. Cost cap: USD 1 (≈ 100 single reads already
cached for the pilot lines + a handful of montage calls per reader; reuse the pilot's cached single-crop responses, never re-call a cached crop).
Owner (12 Oct 10:10): "are we charged per image? maybe it would be better to concatenate the lines" → yes, per image; verify montages before adopting.

## Inputs
- 100 lines from the pilot sample: ~/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/harvest_big/pilot_t13c/pilot_v1/records.jsonl (sampled=true),
  stratified over tiers (40 tier 1, 40 tier 2, 20 tier 3), straightened crops under .../pilot_review_images/<id>.straight.png; their single-crop readings are in the
  records (readers.vision / readers.docai) and the raw responses under .../pilot_v1/google/ (reuse; do not re-call).
## Required
1. `greekocr/harvest/montage.py`: build montages of N crops (N = 10, 20, 40): crops scaled to a common height band? NO — keep native pixels; pad each crop to the montage width
   with paper-white, stack vertically with a gap of max(1 line height, 60 px) and a thin grey rule (2 px, 40% grey) centred in the gap; record a box map (crop id → y0,y1,x0,x1).
   Montage width = max crop width (≤ 2,600 px); if a montage would exceed 10,000 px height or 8 MB PNG, split it. Save montages + maps under
   docs/harvest/montage_v1/ (images to harvest_big, maps in the repo).
2. Read each montage once with BOTH readers (Vision el+grc; Document AI). Assign returned lines to crops by the engines' line/paragraph boxes: a returned line belongs to the crop
   whose band contains ≥ 70% of its box height; lines spanning two bands = `merged`; crops with 0 assigned lines = `lost`; crops with ≥ 2 = `split` (join if side by side as in the
   list-return rule). Record per crop the montage reading and the assignment status.
3. Compare montage reading vs single-crop reading per crop and reader: exact NFD equality, NFD CER, and the three statuses above; report per N (10/20/40) and per reader:
   identical %, median CER, merged/lost/split counts, cost per 1,000 lines (list price), and a verdict per N: ADOPT if ≥ 97% identical and no merged/lost; else the largest N
   that meets it. Also report whether confidences change (mean symbol confidence single vs montage).
4. `docs/harvest/MONTAGE_v1.md` with the tables and the recommended N; a small review page (the 100 crops with single and montage readings side by side where they differ) in
   the existing format; receipt.json with calls and cost.
5. Tests (no network): montage layout + box map, assignment logic on a synthetic response, join/merge/lost classification. INVENTORY; API.md.
Last line exactly: `T14: done | N_adopt: <n|none> | identical_vision: <pct> | identical_docai: <pct> | calls: <n> | tests: <n> passed`.
