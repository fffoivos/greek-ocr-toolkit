# SHEET-1 handoff

Implementation and local demos are ready on `coord/review-sheets`. **No commit
was created**: staging failed because the shared Git metadata is outside this
worktree's writable roots. The final receipt uses `BLOCKED` instead of inventing
a commit SHA. HEAD remains `2c0f312eb` (the design-decision commit). No push,
network research, Clariden operation or artifact publication occurred.

## Implementation

`greekocr.adjudicate.owner_sheet.render` now owns the presentation previously
added by scratch HTML post-processing:

- Card fields: `tool_verdict`, `versions` (last two only, newest labelled
  `(latest)`), ready `overlay_svg`, and optional `display` sizing caps.
- Spec fields: `variant: decision|correction` and `sheet_prefix`. Both variants
  state KEEP/DROP meanings; correction provides the editable Printed field and
  changed-span segments, with CHANGED / UNCHANGED / UNCERTAIN frame colours.
- Three-pixel owner border; three-pixel tool frame inset six pixels; selection
  background tint; tool pill; saved-evidence overlay classes and dark variants.
- Native display up to 3×, capped at 940×300 and card width; hover/tap lens;
  native 3× `z` zoom with sideways scrolling; `b` SVG toggle.
- Arrow navigation transfers note focus. SPACE and badge click toggle KEEP ↔
  DROP without cycling through empty. Tally works before database connection.
- One notes document contains verdict, note and optional Printed, with Athens
  timestamps. Input/mark handlers attach before awaiting the connection; fields
  untouched during loading hydrate without replacing an early edit. Writes
  require an explicit edit event and a changed live snapshot. Load, hydration,
  focus and blur without input produce zero writes.
- Legacy `line_id`, `line_id:s{slot}` and explicit `doc_id` identities are retained.
  Prefixing affects defaults only. Notes/doc identity checks, data attributes,
  slots raster drawing, clean-image lens, zoom images, groups and sections remain.

The package README documents the API and persistence contract. The design
checklist now points directly to the packaged implementation. All seven original
scratch files were moved unchanged to `docs/records/review/reference_scratch/`, with a
README identifying them as historical references.

## Demos and provenance

`docs/B_training_data/d_review/demo/` contains only two standalone HTML files; neither was
published. `scripts/review/build_sheet1_demos.py` regenerates them from local
saved evidence, without invoking a tool or reader:

```sh
PYTHONPATH=. ~/Projects/greek-ocr-toolkit/.venv/bin/python scripts/review/build_sheet1_demos.py
```

1. `decision_gate2.html`: 12 lines from sol-recut's
   `docs/records/harvest/collect_v3_admission/segeval1/gate2/replay_segeval1.jsonl`, using
   `scored/owner_rows.jsonl` and its exact `crops/` paths. Selection takes the
   first available cards in rounds across the reference groups, then renders in
   reference group order. Four KEEP, four DROP, four UNCERTAIN. Prefix `gate`
   preserves the corresponding reference document IDs. Each selected crop's
   bytes match the replay's saved SHA256. A read-only capture of the original
   builder's card assembly verified all 12 cards' crop paths, document IDs,
   groups/order, every non-version row, tags, tool verdict and SVG byte-for-byte.
   The old combined 0.7 → 0.8 row is replaced by two version rows using saved
   `previous` (0.7) and `after` (0.8) reasons; no verdicts were recomputed.
2. `correction_ru1.html`: first 12 edited lines in
   `greek-ocr-toolkit-secondary/artifacts/ru1/ru1_v3_edits.jsonl`, all CHANGED.
   The pinned `google_raw_v2_import` parent supplies exact crop paths and parent
   text; both parent and edits hashes match the RU1 manifest. Native referenced
   crops are local under the main checkout's `docs/records/harvest/harvest_big/cyrillic/`.
   **RU1 was used; sf7 was not needed.** Before/After highlight the saved ь → ъ
   positions. Printed starts blank. This edit ledger has no target-slot geometry,
   so the demo supplies no invented overlay. Prefix `sheet1-ru1`.

HTML SHA256:

```text
a61404703841a15c2d8e83c620e056e59a890643cb65b9161836e73d606a65c8  decision_gate2.html
49df86d3f2f688ca480b5e7d5ef115d123307813771b39226c980470a2a89a35  correction_ru1.html
```

Input SHA256:

```text
7e89256c4423779be2af9797364bbee0af81a39d1c6a26641edbab5302d26e22  gate2/replay_segeval1.jsonl
12be67394d516f30f64aeb0568fe706a3070b40299e1be911399d4861b853d87  scored/owner_rows.jsonl
4f1a51f5eb80788fb1cdc7a01220c90df028e79711cf0eeec2d0ace2ee42d1d0  ru1_v3_edits.jsonl
```

## Validation and limits

**20 focused tests passed**:

```sh
~/Projects/greek-ocr-toolkit/.venv/bin/python -m pytest -q \
  tests/test_owner_sheet.py \
  tests/adjudicate/test_owner_runtime.py \
  tests/adjudicate/test_reemission.py::test_owner_escape_groups_identity_and_detection_pixels
```

The 18 new Python cases cover decision/correction rendering, version truncation,
segments, pills, data attributes, prefix/legacy/explicit document identity,
sections, clean lens, supplemental zooms, native image preservation and size
caps, all correction statuses, data URI input, frames/overlays/dark CSS, and both
demo file structures. The shipped-JS runtime test now exercises the
no-write-on-load invariant with missing/existing documents and live values that
differ from HTML defaults; early input, loading and in-flight-write races;
unified note/verdict/Printed saves; Athens timestamps; keyboard navigation,
badge/SPACE toggling, overlays, zoom and the supplied clean lens. The existing
slot/detection-pixel and escaping regression also passes. `node --check` and
`git diff --check` pass. Both demos have 12 unique note IDs, 24 version rows and
no external assets.

The broader archival run encountered seven failures from unavailable inputs:
`artifacts/cleanup_step4` reference specs, old W1 native/recovered crops,
`artifacts/owner_sheets/v2` HTML, and the crop-dependent coordinator replay.
These artifacts were not regenerated or fetched. An eighth diagnostic failure,
`test_os2_renderer_additions_are_optional_and_escaped`, compares new rendering to
`git show HEAD:...`; it currently compares against the old implementation because
this worktree cannot commit. This is separate from the passing legacy identity,
pixels and features checks above.

**Browser screenshots remain unverified.** Playwright's expected Firefox build
is absent; the existing cached Firefox and installed Chrome both aborted at
launch with SIGABRT in this sandbox. Computer Use reported no browser available
and denied native Firefox access. No page screenshot or visible layout success
is claimed. The coordinator should perform the design's screenshot check in a
browser-enabled environment before publication.

## Remaining coordinator action: commit

The attempted `git add` failed before staging any files:

```text
fatal: Unable to create '/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.git/worktrees/greek-ocr-toolkit-review/index.lock': Operation not permitted
```

From a session with write access to this worktree's shared Git metadata:

```sh
git add -- docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md docs/records/review/SHEET1_HANDOFF.md \
  docs/records/review/reference docs/records/review/reference_scratch docs/B_training_data/d_review/demo \
  greekocr/adjudicate/README.md greekocr/adjudicate/owner_sheet.py \
  greekocr/adjudicate/owner_sheet.css greekocr/adjudicate/owner_sheet.js \
  scripts/review/build_sheet1_demos.py tests/test_owner_sheet.py \
  tests/adjudicate/owner_sheet_runtime.cjs
git commit -m "Fold owner review-sheet design into adjudicate"
```

The unrelated pre-existing untracked `docs/ocr_program_2026-10-06/` was untouched
and must remain outside this commit. No push is requested. Before any later
artifact republish, the coordinator must dump its notes collection and verify
marks reload, as required by the design.

SHEET1: done | render fields tool_verdict,versions,overlay_svg,display,variant,sheet_prefix | js: no-write-on-load guarded yes | demos 2 | tests 20 passed | commit BLOCKED
