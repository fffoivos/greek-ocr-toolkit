# Offline adjudication

This package is additive. No old builder/scorer is redirected. Historical replay
is explicitly labelled and never silently upgrades earlier reader results.

`owner_sheet.render(cards, spec)` returns standalone HTML using packaged CSS/JS.
`spec` has `title`, `intro`, and optional ordered `groups: [{id, heading}]`,
`sections: [{id, heading, header}]` (referenced by a group's `section`),
`variant: decision|correction` (default `decision`), and `sheet_prefix`.
Each card has `line_id`, `image`, `rows: [{name, text|segments}]`, and optional
`group`, `tags: [{text, class}]`, `slot`, `printed`, `zooms: [{image, alt}]`,
`clean_image`, `slots`, `opening_quotes`, `tool_verdict`, `versions`, `overlay_svg`,
and `display`. Segments have `text` and optional
`kind: changed|no_ink|muted`. Saved slot evidence is drawn without inference.
Omit `slots` when supplying a previously drawn raster. The clean magnifier crop
must be supplied separately. The default note document is `line_id`, or
`line_id:s{slot}`; `doc_id` with matching `note_data` can bind an existing sheet.
With `sheet_prefix`, the default document is `<prefix>:<line_id>`; an explicit
`doc_id` still wins. Without a prefix, all legacy identities remain unchanged.
Matching `note_data` must identify both that document and the card's `line_id`.
One note/document per card is enforced. DOM data attributes are explicit data.

The package implements [the owner's sheet design](../../docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md).
No HTML post-processing is needed. `tool_verdict` sets `data-tool`, the tool pill,
and the 3 px inner frame inset 6 px. The outer 3 px border is the owner's mark;
selection only tints the background. Decision states are KEEP (green), DROP
(red), UNCERTAIN (amber). Correction states are CHANGED (amber), UNCHANGED
(green), UNCERTAIN (grey). Both variants explain KEEP/DROP in the intro;
correction means accept/reject the proposal and always supplies a Printed input.

`versions: [{name, verdict?, text|segments}]` is ordered oldest to newest. Only
the last two entries render, with `(latest)` added to the newest name. They
follow the measurement rows and precede `Text vs crop` / `Owner standard` rows
when those are present. Supply those rows from the tool's saved evidence, not a
fresh tool run. Correction versions can be `Before` / `After` with
`segments: [{text}, {text, kind: changed}]` to highlight the changed span.

`overlay_svg` is trusted, ready SVG (including a crop-coordinate `viewBox`),
placed over the crop and scaled with it. It is never inferred or recomputed.
Packaged overlay classes include `tbox`, `rframe`, `asc`, `base`, `mean`, `desc`,
`nasc`, `nbase`, `wmain`, `wwhole`, `wpart`, `wunres`, `cutspan`, `cutspan2`,
and `cross`. Existing raster `slots` drawing, supplemental `zooms`, and a
caller-supplied `clean_image` lens remain supported.

Default display scale is `min(3, 940 / width, 300 / height)`, bounded further by
the available card width. Optional `display: {scale, max_width, max_height}` can
reduce these caps; it cannot exceed them. Embedded native pixels are preserved.
Hover or click opens a 3× lens; `z` toggles a native 3× crop with sideways
scrolling, and `b` toggles SVG overlays. ↑/↓ moves between cards and transfers
note focus even from within a note. SPACE and the badge toggle KEEP ↔ DROP
(first press KEEP, no empty state); SPACE also marks from an empty note. Esc
leaves the note box. A fixed tally shows KEEP / DROP / unmarked.

Autosave uses one `notes/<doc_id>` document per card containing `note`,
`verdict`, optional `printed` / `printed_edited`, Athens `updated`
(`YYYY-MM-DD HH:MM`), `line_id`, and optional legacy `slot`. Notes and Printed
debounce at 900 ms, marks at 300 ms; blur flushes pending edits. Live value
snapshots and an explicit user-edit guard prevent **all writes on load**,
including after database hydration or a blur without input. Listeners attach
before the database connection resolves. Early edits survive loading, untouched
fields reload from the saved document, and concurrent writes retain the newest
edit. Without the artifact database, the page remains usable and states that
saving requires the signed-in view; local HTML demos do not persist marks.

The historical builders now live in
[`docs/review/reference_scratch/`](../../docs/review/reference_scratch/README.md).
Rebuild the two unpublished, self-contained 12-line demos with
`PYTHONPATH=. ~/Projects/greek-ocr-toolkit/.venv/bin/python scripts/review/build_sheet1_demos.py`.
They use local gate2 replay evidence and RU1 v3 edits with parent-referenced
crops. Before republishing an existing artifact, the coordinator must dump its
notes collection and verify marks reload afterwards; this renderer does not
publish or modify the live database during a build.

`build_deck(spec)` writes a fresh blind tree, a sibling private tree and a private
receipt. `spec` has `blind_dir`, optional sibling `private_dir`, `items`,
`controls`, `seed`, `profile` and `control_fraction` (default .08). A tagged private directory may sit beneath the sibling private tree. New decks always
use two readers plus an independent tiebreak. Each record supplies a native local
`image`, optional `line_image`, target `bbox` or an exact `crop_box`, literal
`options` (list or mapping), and private provenance in `private`. `free_text: true`
allows no candidate options. Controls additionally require `pixel_verified: true`
and `known_answer`; optional `expected_fields` gate structured observations.
Images are re-encoded without metadata, named by encoded-content SHA256, and
scanned with all public files for private identifiers/paths. `forbidden` extends
the text scan. Printed source content itself can identify a book; this is not an
access-control sandbox. Readers must only receive the blind folder and their own
output location. Full filesystem access still permits explicit sibling-key reads.

Profiles `letter`, `word`, `mark` use the R0 full-height target window, horizontal
padding .6× native height, <=3× LANCZOS, 900-pixel width cap. `line` and `page`
retain native size. Explicit `crop_box` uses sealed geometry without adding pad.
Zooms are pre-rendered, so reader tools need no separate enlargement algorithm.
Historical replay additionally uses `protocol: historical`, `preserve_order: true`,
`position`, opaque `id`, and optional R0 `schema: r0`. The R0 fixture regenerates
target pixels from full-line native rasters, not from old target PNGs.

The blind viewer uses `?reader=2` for reverse order; reader 1 is the default.
It exports the common answer schema. The separate `reader_2.json` manifest is
also generated by code. `deal(cards, 2)` returns the same order.
`adapt_answer` handles R0/S8/R2C field aliases; S8 `uncertain` maps to low/high
when confidence is absent. Numeric legacy confidence is rejected rather than
silently reinterpreted. R2C explicit head/readability/ownership observations are
validated and retained; unknown heads never become negative evidence.

`resolve(cards, keys, reader1, reader2, ...)` requires full assigned order/coverage,
gates controls first, then resolves agreement or two of three. Unknown literal
readings remain UNKNOWN. `gate_spec` supports `max_errors` (default 0),
`min_correct`, `expected_controls`, and `no_shared_misses` (default true).
A third batch must include exactly the disagreements and controls, and must use
its own key/map from `tiebreak_deck`. Distinct multi-option orders are guaranteed.
Both initial readers must pass before a tiebreak can affect truth. Control
failures are never rescued by discarding a reader and counting another view.

`controls_gate(..., readers=1)` can describe the two historical C1 gates through
`n`, `exact_n`/`min_n`, `minimum_rates` and `rates`, with
`allow_no_controls: true`. These descriptions do not authorize one-reader new
decks. Structured truth includes reader observations, verdict, status and
`control: false`. `write_truth` writes JSONL or deterministic gzip once and returns
its summary, preserving UNKNOWN.

`protocol.score` re-exports the one estimator in `score.py`: the S8 weighted
document/line-cluster bootstrap with its Wilson-Kish boundary fallback (4000
replicates). `wilson` uses z=1.959963984540054; `clopper_pearson_lb95` is the exact
one-sided 95% lower bound. These are offline statistics, not truth generation.
