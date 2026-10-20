Local unpublished variant table copy. Read-only reference: ~/Projects/greek-ocr-toolkit-review/docs/review/HUMAN_REVIEW_SHEETS.md, coord/review-sheets.

# Human review of tool outputs: the line review sheet

Owner decision, 19 October 2026: the review sheet the owner uses for segmentation decisions is the reference presentation for every tool whose output a human reviews line by line. Other tools vary it minimally, as set out in §6. Implementation: `greekocr/adjudicate/owner_sheet.py` (+ `owner_sheet.css`, `owner_sheet.js`). The original builders and assets that produced the sheets listed in §8 are preserved under `docs/records/review/reference_scratch/`; their presentation behaviour is now folded into the package.

## 1. What a sheet is
A single self-contained HTML page, published as a claude.ai artifact with the `db` and `user` capabilities, holding one **card per line**. The owner reads cards top to bottom, marks each one with the keyboard, and types notes. Marks and notes autosave to the artifact's database and survive republishes. Nothing is ever asked of the owner that the page could compute.

## 2. Card anatomy (top to bottom)
1. **Line id** (monospace), the **tool pill** (`tool: KEEP` / `DROP` / `UNCERTAIN`, the latest version's verdict) and the owner's **mark badge** (`✓ KEEP` / `✗ DROP`).
2. **The crop**, always with the **Google text directly beneath it** in the table (rule: crop and text are judged together). Display size: natural size up to 3×, never wider than the card (940 px) nor taller than 300 px. Hover or click gives a 3× lens; `z` shows the crop at 3× with sideways scrolling.
3. **Evidence overlays** drawn as SVG on the crop, scaled with it, toggled with `b`: blue = upright text box; magenta = de-skewed box; green = detected main row (ascender, base); orange dashed = other rows; red box = whole neighbour word; grey dashed = cut-off word; orange edge bar / red dot = cut diagnostics. Overlays are the tool's saved evidence, never recomputed in the page.
4. **Rows** (label + text): Google text; the tool's inventory/measurements in plain words ("MAIN: 52 letters, complete, covers 98% | ABOVE: 1% visible, 0 whole / 13 cut-off words"); **exactly the last two tool versions** ("0.7" and "0.8 (latest)"), each with verdict, reason and the numbers behind it; "Text vs crop" (the blind reader's codes and detail when a read exists); "Owner standard" (the fault list under the owner's standard, or "fine").
5. **Tags**: source, verdict change, size or skew.
6. **Note** textarea (autosaves) and, on correction sheets, the editable **Printed** field.

## 3. Frames: the two verdicts at a glance
- The card's **outer border is the owner's mark**: green KEEP, red DROP, neutral when unmarked. It is the only outer line; the selected card is shown by a background tint, not by another outline.
- An **inner frame of the same thickness (3 px), inset 6 px**, is the **latest tool verdict**: green KEEP, red DROP, amber UNCERTAIN. Agreement reads as one colour, disagreement as two.

## 4. Keys
`↑` `↓` move between cards (also from inside the note box; focus follows). `SPACE` toggles the owner's mark KEEP ↔ DROP (first press KEEP; there is no empty state to cycle through); it also works inside an empty note box, and clicking the badge does the same. `z` zoom, `b` boxes, `Esc` leaves the note box. A fixed tally top-right shows KEEP / DROP / unmarked.

## 5. Persistence
- Database collection `notes`, one document per card, id = `<sheet prefix>:<line_id>` (e.g. `segeval:gazette_modern--…-l0139`), fields `note`, `verdict` (`KEEP`|`DROP`|``), `printed` (correction sheets), `updated` (Europe/Athens, `YYYY-MM-DD HH:MM`), `line_id`.
- Ids are stable across republishes; a rebuilt sheet reloads the owner's marks.
- **The page never writes on load.** It writes only after a mark or an edit, one document per action, debounced. (A load-time write wiped a day's marks once; the rule is absolute.)
- **Before every republish the coordinator dumps the collection** (ArtifactData list → files) and checks the marks reload afterwards.
- Timestamps come from the clock, in Athens time.

## 6. Variants, with the reference as the fixed point
| kind of tool | what the owner decides | mark | inner frame = tool state | rows that change |
|---|---|---|---|---|
| **Decision tools** (segmentation, admission, census verdicts) — the reference | keep or drop the line | KEEP / DROP | KEEP / DROP / UNCERTAIN | measurements + last two versions |
| **Correction tools** (polytonic marks, Cyrillic ъ/ь, numerics, capitals, lookalikes) | accept or reject the proposed correction; optionally type the printed truth | KEEP = accept the correction, DROP = reject it (same key, same colours) | CHANGED (amber) / UNCHANGED (green) / UNCERTAIN (grey), from the tool's own status | "Before" and "After (latest)" texts with the changed span highlighted (`segments` with `kind: changed`), plus the editable **Printed** field; the overlay marks the target slot and any detected marks (`slots`), nothing else |
| **Edition split proposals (SPLIT1)** | accept proposed edition split or move train ↔ held-out; Gazette issues selected within one year card | KEEP accept / DROP other side; forced side stays locked | TRAIN green / DEV amber / TEST blue | edition metadata, class counts, two sample crops with Google text, issue list; stable edition IDs |
| **Read / adjudication cards** (blind readers, controls) | not an owner sheet | — | — | built by `build_deck`; readers never see a verdict or the release text |

Rules for any variant: crop + text together; last two versions only; same frames, keys, autosave and republish protocol; the only free parameters are the row set, the overlay set and the meaning of KEEP/DROP, stated in the sheet's intro.

## 7. Building a sheet (checklist)
1. Cards from the tool's own evidence records (never re-run the tool in the builder); crop paths byte-exact to the record's hash.
2. Intro: what the sheet shows, the standard being applied, the colour legend, the keys, the scores under the owner standard.
3. Groups in the order the owner wants to read them (false rejects first, then misses, then holds, then correct drops, then a small sample of the fine ones).
4. Render through `owner_sheet.render`, supplying saved `overlay_svg`, `tool_verdict` and `versions`; the package supplies frames, the size cap and lens. Historical data-adapter reference: `docs/records/review/reference_scratch/build_gate_sheet.py`; no HTML post-processing is needed.
5. Headless screenshot check; publish with `db`+`user`; stable ids; dump marks before any republish.

## 8. Sheets built to this design (19 Oct 2026)
- Segmentation, 150 unseen lines, 0.7 → 0.8: https://claude.ai/artifact/CCD2D9pnygnnLZCxN7ZLns
- De-skew flips (27 lines): https://claude.ai/artifact/P46d9fCCp5bRKwvzLEiPLC
- Numeric cells and short crops across the census (579 crops): https://claude.ai/artifact/3UHaheQNiGry5jz6MNaVNd
- Gate sheet (mirror of the 150): https://claude.ai/artifact/QMMk5RiEnbUAPadhoUGSho
