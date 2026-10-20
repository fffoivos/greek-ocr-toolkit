# Owner sheets — design and builder contract

The reference is `docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md`; the current implementation is `greekocr/adjudicate/owner_sheet.{py,js,css}`. `render(cards, spec) -> str` returns standalone HTML with packaged inline CSS/JS and embedded PNGs. It does not publish or contact a database while building. Historical scratch builders under `docs/records/review/reference_scratch/` retain old paths and HTML patching; they are evidence adapters, not the supported presentation implementation.

## One card per line

Cards contain, in order: line identity, latest tool pill and owner badge; crop; named text/evidence rows including Google directly beneath the crop; measurements and at most the last two supplied versions; reader “Text vs crop” and “Owner standard” when supplied; tags; Note and, for corrections, Printed. The renderer inserts version rows before those two review rows, otherwise after the other rows. It takes `versions[-2:]` oldest→newest and labels the newest `(latest)`; it does not fabricate a second version when only one exists.

The **outer 3 px border is the owner's mark** (green KEEP, red DROP, neutral unmarked). The **inner 3 px frame, inset 6 px, is the tool verdict**. Selection tints the background without adding an outline. Owner and tool disagreement therefore remains visible. Overlays are saved evidence: upright box blue, row-frame box magenta, main-row guides green, neighbour rows orange dashed, whole neighbour words red, partial words grey dashed, cut spans orange and crossings red. `overlay_svg` is trusted ready SVG with a crop-coordinate `viewBox`; the page does not rerun geometry.

| Variant | Owner KEEP / DROP | Latest tool frame | Changed content |
|---|---|---|---|
| `decision` (default) | Keep / drop the line | KEEP green, DROP red, UNCERTAIN amber | Saved measurements and version decisions |
| `correction` | Accept / reject proposed correction | CHANGED amber, UNCHANGED green, UNCERTAIN grey | Before/After text with changed spans; editable Printed always present |

Both variants explain mark meanings in the generated instructions. A blind read deck is a separate `build_deck` product, with no owner or tool verdict supplied to the reader.

## Fit, ordering and keys

Horizontal display scale is `min(3, requested_scale, min(940, requested_max_width)/w, min(300, requested_max_height)/h)`. Tall crops (`h>w`) use the same calculation with a **640 px** height cap and a left crop/right text grid; below 600 px viewport width CSS stacks them. JS can recognize older tall cards from the SVG viewBox. CSS also bounds the displayed crop to available card width. Native embedded pixels are retained; sizing is presentation only.

Table data cells are clamped to two lines. `d` or a table click opens full text; concise version rows keep the verdict and one clause visible before longer diagnostics. Arrow navigation scrolls the card start into view and transfers Note focus. The layout contract is to keep the crop top and note reachable; the code has no general viewport-height solver guaranteeing every arbitrary row set fits. Validate actual desktop and narrow cards before publication.

Builders must order **unjudged lines first, prior judgments last**. Pass `prior: KEEP|DROP` for an earlier sheet's mark: CSS gives a dashed outer border; a mark on this sheet is solid. Prior marks are not seeded into the current database, are not the current badge and do not count in the current tally. The renderer validates `prior` but does **not sort cards** or create a prior tag; the builder supplies order and explanatory tags/text. This distinction matters when rebuilding old sheets.

| Key/action | Behaviour |
|---|---|
| ↑ / ↓ | Select preceding/following card, including from Note/Printed; focus Note and scroll to card start |
| SPACE / owner badge | First mark KEEP, then KEEP↔DROP; no empty state in the toggle cycle |
| SPACE in text field | Marks only when the field is empty; otherwise ordinary text entry |
| `z` | Toggle native 3× crop with sideways scrolling |
| `b` | Toggle SVG overlays |
| `d` / table click | Expand/collapse full table text |
| Esc in a text field | Blur field |
| Crop hover/click | 3× lens; a separately supplied `clean_image` gives an overlay-free lens |

Letter shortcuts act outside text fields; modifiers/composition are ignored. A fixed tally counts this sheet's KEEP/DROP/unmarked cards even before DB connection.

## Persistence is action driven

The artifact supplies `window.claude.use('db')`. Each card reads its own `notes/<doc_id>` document, avoiding a collection-query limit. A write merges `note`, `verdict`, optional `printed`/`printed_edited`, `updated` (Europe/Athens, minute precision), `line_id`, and optional legacy `slot` into that same document.

**Never write on load.** The JS captures live values, requires an explicit input/mark event, and writes only a changed snapshot after DB readiness. Hydration, selection, focus and blur without an edit cannot write. Listeners attach before awaiting the database: early edited fields survive while untouched fields hydrate. Saves are serialized so edits made during an in-flight write trigger a newer save. Note/Printed debounce **900 ms**, marks **300 ms**; blur flushes pending edits. Without DB the sheet remains readable and reports that saving requires the signed-in view; there is no local persistence fallback.

Identity precedence is explicit `doc_id` → `<sheet_prefix>:<line_id>` → legacy `<line_id>:s<slot>` or `<line_id>`. Custom `note_data` must agree with both document identity and line identity. Duplicate document IDs fail. Preserve existing IDs on republish; changing a prefix changes the lookup namespace. Dump marks first and verify reload afterward.

## Builder input

| Field | Meaning |
|---|---|
| `spec.title`, `spec.intro` | Title and plain-text introduction (escaped; newlines become breaks) |
| `spec.variant`, `spec.sheet_prefix` | Decision/correction and default stable DB namespace |
| `spec.groups` | Ordered `{id,heading,section?,gap?}`; every grouped card must belong to a declared group |
| `spec.sections` | `{id,heading,header}` section headings used by groups |
| Card `line_id`, `image`, `rows` | Required identity, PIL image/path/data URI, and `{name,text}` or `{name,segments}` rows |
| `tool_verdict`, `versions` | Tool state and ordered `{name,verdict?,text|segments}` history; save the evidence, do not rerun in the builder |
| `overlay_svg`, `slots`, `opening_quotes` | Ready SVG or saved slot evidence for raster drawing; omit slots for an already drawn raster |
| `clean_image`, `zooms` | Separate clean lens image and optional `{image,alt}` detail crops |
| `display` | Optional `scale`, `max_width`, `max_height` reducing normal caps |
| `group`, `tags`, `label`, `alt`, `data` | Group assignment, `{text,class?}` pills, display identity/alt and explicit data attributes |
| `prior`, `note`, `printed` | Historical mark presentation, initial text, optional printed truth (always rendered in correction variant) |
| `doc_id`, `note_data`, `slot` | Preserve explicit or legacy persistence identities |

Segments accept `text` and optional `kind: changed|no_ink|muted`; unsupported kinds fail. Supply byte-bound crop inputs and saved evidence from the tool record. `_uri` re-encodes PNGs; native pixel identity and original encoded-file identity are separate checks. `image_path` can resolve an absent archived path through `artifacts/owner_sheets/v2/recovered_crops/<sha256(path)>.png`; that fallback alone does not establish original-byte custody.

Example rendering only (no build or publication was run for this document):

```python
from greekocr.adjudicate.owner_sheet import render
html = render(cards, {
    "title": "Tool revision review", "intro": saved_intro,
    "variant": "decision", "sheet_prefix": existing_prefix,
    "groups": ordered_groups,
})
```

`greekocr/labelfix/sheet.py` remains a historical crop/text report using cached CTC alignment to locate words. Its code includes a Google Fonts external stylesheet and does not implement this autosaving owner-sheet contract. It is not the publication renderer for new sheets.

## Tests and receipts

`tests/test_owner_sheet.py` covers versions, correction states, identity precedence/rejection, escaping, groups/sections, embedded pixels, sizing including tall cards, overlays, frames and standalone demos. `tests/adjudicate/test_owner_runtime.py` invokes `tests/adjudicate/owner_sheet_runtime.cjs`, exercising the packaged JS with a mock DOM/DB: no-load writes, hydration/early-edit races, debounce, combined fields, in-flight saves, keyboard and lens behaviour. `tests/adjudicate/test_reemission.py` covers historical content/pixel preservation.

`docs/records/review/SHEET1_HANDOFF.md` records **20 focused tests passed**, two unpublished 12-card demos and no external assets; it also records unavailable browser screenshots and broader archival failures from missing inputs/old HEAD comparison. `docs/records/cleanup_20261017/CLEANUP_STEP4_REPORT.md` records earlier CU4 re-emission parity (39-card reader errors, 100-card accent audit, 336-card R0-ib) and **24 focused tests passed**, with broader suite failures/errors retained. These historical results do not certify every later stylesheet change or a live DB reload. No tests or screenshots were run in this documentation task.

## Sources read

- `AGENTS.md`
- `docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md`
- `greekocr/adjudicate/{README.md,owner_sheet.py,owner_sheet.js,owner_sheet.css}`
- `greekocr/labelfix/sheet.py`
- `docs/records/review/{SHEET1_HANDOFF.md,reference_scratch/README.md}`
- `tests/test_owner_sheet.py`
- `tests/adjudicate/{test_owner_runtime.py,test_reemission.py}`
- `tests/adjudicate/owner_sheet_runtime.cjs`
- `docs/records/cleanup_20261017/CLEANUP_STEP4_REPORT.md`
- `docs/records/harvest/seg_steps/sheet/{README.md,verify.py,receipt.json}`
