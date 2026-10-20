# Publishing and preserving owner review

This is the repository's publication protocol and a register of the local evidence. Artifact URLs below are recorded publications, not live re-verifications in this documentation task. Building HTML, publishing it, saving owner marks and adopting a tool are separate events.

## Publication procedure

1. Render from saved evidence through `greekocr.adjudicate.owner_sheet.render`. Supply the existing namespace, card IDs, exact input bindings, crop/text rows, tool state, last two versions and saved overlays. Explain KEEP/DROP, the standard, scores, controls/exclusions and uncertainties in the introduction. A builder does not run the tool to fill missing evidence.
2. For an existing artifact, **dump collection `notes` before every republish**, using ArtifactData list → files as specified in `docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md`. Preserve document IDs, fields, timestamps and the association to the artifact/sheet. The dump precedes the publish, not merely the first code edit. Keep a raw dump and any normalized `owner_marks_*.jsonl` export with the replay's input hashes.
3. Verify the generated HTML offline before publishing:
   - All image/style/script content is embedded; no external font/style/script URL, external image, iframe or fetch dependency. Inspect SVG references and CSS URLs as well as HTML attributes.
   - The embedded script is byte-identical to the chosen packaged `owner_sheet.js`; record the renderer/assets hashes. A vendored historical renderer is identified by its recorded hashes, not silently called the current package.
   - Every document ID is unique and uses the intended stable prefix, or the exact documented legacy override. `note_data` and `line_id` agree. Check the actual DOM, not just the input spec.
   - Existing marks are loaded by document read; no preload/seed write, load/hydration/focus/blur write, or prior-mark migration occurs. Mock-DB runtime checks exercise the actual shipped JS and early edits, not a rewritten test approximation.
   - Obtain and inspect headless screenshots at desktop and narrow widths: intro, representative cards, long diagnostics, tall crops, selection/navigation, note access, overlays and zoom. Check page errors and unintended network requests. A parse/runtime pass does not substitute for this visual check.
4. Publish the self-contained HTML as a claude.ai artifact with **`db` and `user` capabilities, no rules**. The renderer uses `window.claude.use('db')`; it does not implement an uploader or a rules configuration. This document specifies the requested publication contract; no live artifact capability/rules state was inspected here.
5. **Check mark reload in the signed-in artifact after publication.** Compare representative existing KEEP/DROP marks, notes, edited Printed fields and stable IDs to the prepublish dump, and reconcile saved-document/mark counts. Merely opening the page must produce no writes. An interaction/save check is a distinct user action; do not manufacture or reset owner judgments as part of loading. Record publication URL, renderer/HTML identity, dump identity and reload result. If reload fails, retain the dump and diagnose identity/persistence before claiming a successful republish.

The dump and reload requirements are explicit in the design and `AGENTS.md`. Existing live artifact marks are authoritative for user actions; exports are snapshots. In code, one merged document contains Note, mark and optional Printed; note edits debounce 900 ms, marks 300 ms, timestamps use Europe/Athens. See [OWNER_SHEETS.md](OWNER_SHEETS.md).

## Mark exports and identity

`greekocr/adjudicate/owner_notes_export.py` reads **supplied documents**, not a live database. It joins `(sheet,db_id)` against cards and demands explicit `no_note_status`/`note_status` conventions. Unknown/duplicate identities fail; a note is flagged for review, never automatically converted to DROP. Its output is write-once JSONL.

The segmentation exports use explicit `owner_mark`. Examples are `docs/records/harvest/collect_v3_admission/segeval1/owner_marks_20261019.jsonl` and `small_segments/owner_marks_smallseg.jsonl`. The latter's adapter `small_segments/tools/ss7_owner_marks.py` accepts a dump directory or its `notes/` child, verifies filename `smallseg:<line_id>.json`, card-manifest membership, uniqueness and KEEP/DROP, then emits normalized rows. It validates every input before opening the output. S4 freezes its own snapshots and resolves repeated marks by latest timestamp then file order. A snapshot is not proof of the current live database contents.

## Sheet register

`E` below abbreviates `docs/records/harvest/collect_v3_admission/segeval1/`. Prefixes are database identities, not tool versions. “Decision” describes the question/recorded ruling; absent evidence of adoption is stated explicitly.

| Sheet / recorded status | DB identity | What was reviewed or decided; evidence |
|---|---|---|
| [SEGEVAL 150](https://claude.ai/artifact/CCD2D9pnygnnLZCxN7ZLns), published | `segeval:<line_id>` | Unseen crop+Google lines; design register describes 0.7→0.8. The archived builder originally framed the baseline check and has stale headline counts. Use `E/SEGEVAL1_RESULT.md` for original four-question scoring, gate2 handoff for later owner-standard replay, and the saved owner marks for user decisions. Publication does not imply acceptance. |
| [Gate mirror](https://claude.ai/artifact/QMMk5RiEnbUAPadhoUGSho), published | `gate:<line_id>` | Same 150, exactly the owner's three-rule 0.8 candidate versus 0.7. Owner rejected the extra target-cut/taller-row vetoes; `E/gate2/HANDOFF.md` records their removal. Early context questions about adopting 0.8 are historical; current segmentation acceptance is in the tool manifest. |
| [De-skew flips](https://claude.ai/artifact/P46d9fCCp5bRKwvzLEiPLC), published | `deskew:<line_id>` | 27 lines selected by 0.5→0.6 changes, later presented with last-two 0.7/0.8 states. It exposes false rejects, newly missed faults and uncertainty rather than proving every flip is correct. Source adapter: `docs/records/review/reference_scratch/build_deskew_flips.py`. |
| [Cells and short crops](https://claude.ai/artifact/3UHaheQNiGry5jz6MNaVNd), published | `cells:<line_id>` | 579 census crops spanning numeric cells, boundary samples, small nonnumeric crops and the Opus study. Whether short/numeric crops need separate treatment was an owner question, not an automatic fit adopted by this sheet. The adapter distinguishes Opus by-eye typology from blind reads. Current short/cell rules are in code and manifest, not the old 0.5 frame. |
| [Small-segment typology](https://claude.ai/artifact/LZ69m33YqGxf3fJHdobMpD), published 19 Oct | `smallseg:<line_id>` | 417 noncontrol cards grouped by type; KEEP usable training line, DROP unusable. Latest saved tool verdict 0.8 where present, otherwise 0.5. `E/small_segments/SMALL_SEGMENTS.md` records coordinator rendered-page inspection before publish; normalized owner dump is retained. Typology labels alone are not owner KEEP/DROP. |
| SEG final sheet, **local/unpublished** | `seg09:<line_id>` | `docs/records/harvest/seg_steps/sheet/seg09_sheet.html`: 279 unique cards, union of 238 changed lines and 59 proposal lines, overlap 18. Changed-set categories: 28 disagree, 77 newly agree, 133 unjudged. Compares 0.8 with 0.9-s4 using saved evidence; owner marks appear as historical text, never seeded. `receipt.json` says `published:false`; screenshot unavailable. No publication URL or later owner decision is claimed. |
| SPLIT1 edition proposal (the `split1` namespace), **local/unpublished** | `split1:<edition_id>` | `docs/records/harvest/collect_v3_admission/split1/OWNER_REVIEW.html`: KEEP accepts edition split proposal; DROP suggests train↔held-out, with DEV/TEST still an owner choice after a TRAIN drop. Forced editions stay locked. Gazette is one year card with independent issue selection/notes, not a bulk year decision. Same `split1`/SPLIT1 artifact, not two publications. `SPLIT_PROPOSAL.md` and `QA_STATUS.md` record no publication/DB change and unverified screenshots. This is a specialized post-processed variant, not a native third `owner_sheet` variant. |

The `seg09` receipt binds its vendor to renderer head `19347b5a8a89bdb36391c2baf03ace3a3b0a4c11` and all 279 embedded crop hashes. Its verifier checks embedded JS against the **vendor** copy. That establishes the recorded historical identity, not equality to whatever package version is now integrated. The frozen card groups and historical-text marks also need comparison with the newer design's prior-border/unjudged-first requirements before republishing.

## Label-fix pages and R2 decks

| Sheet / deck | Identity and publication evidence | Question / recorded outcome |
|---|---|---|
| [SF6 accent corrections checked](https://claude.ai/artifact/6ymjnnYCvJ1yYJfpZ8bXDD), 100 print-checked lines | Legacy `notes/<line_id>`, no prefix; `R2_evidence/page_builders/build_audit_template.py` | Review corrected accents. `R2_evidence/OWNER_REMARKS_20261017.md` records hallucinated capital/ο marks, subscript problems and requests for regression checks; no blanket release acceptance follows. |
| [Substitution page](https://claude.ai/artifact/FEt1TDdCcXdFfjqW1J3W29), 60 lines | Legacy `notes/<line_id>`; `build_subst_page.py` | Owner said the page supported the substitution rule, with a few errors to investigate. Preserve that scoped ruling rather than claiming every correction correct. |
| [Reader errors held-out](https://claude.ai/artifact/75DVJQetceTYHZeNvWJWn2), 39 slots | Legacy `notes/<line_id>:s<slot>`; `build_r1a_errors.py` | Unfixed Google errors, false/missed/misnamed marks and editable printed truth. Owner remarks made recogniser “Only locate”; no recogniser vote to change/delete Google characters. CU4 re-emission preserves identities and pixels. |
| [RU1](https://claude.ai/artifact/VU89E3EqcjjRiLJxAaBJ1m), [N1](https://claude.ai/artifact/VhXv5iEoaUic683vamLk5j), [LQB scoreboard](https://claude.ai/artifact/SpmYUcAYueVUspfsfksQxr) | URLs recorded in `docs/records/labelfix/secondary/HANDOFF_20261018.md`; that handoff does not specify their DB prefixes | RU1 ь→ъ edits, assisted numeric punctuation and label-quality results. Do not invent prefixes, DB schema or a per-page owner adoption decision from the link list. Manifest records the tool scopes separately. |
| R0-ib and R2 T2/T4 blind decks | `items_blind.json`, opaque card IDs; **no owner-sheet DB prefix**. No claude.ai publication URL established by the inspected deck receipts | Independent printed-form/mark-head observations, not KEEP/DROP owner decisions. CU4 re-emitted R0-ib 336 cards/28 controls. R2C initially prepared T2 800+80 proposed controls and T4 800+80 proposed controls, with control pixel checks required before reads. Later resolver/dry-run receipts are separate from that preparation. |
| SHEET1 gate/RU1 demos | `gate:<line_id>` / `sheet1-ru1:<line_id>`; **unpublished**, 12 cards each | Examples of current decision/correction API; no new reader run or owner decision. `docs/records/review/SHEET1_HANDOFF.md`. |

Old pages may predate current interaction/cap requirements. Their archived builders are retained to recover evidence and identities, not to certify compliance with the 19 October design. In particular `greekocr/labelfix/sheet.py` contains an external Fonts link; it cannot satisfy the standalone publication checklist without using the current owner renderer.

## Verification receipts and limits

`docs/records/harvest/seg_steps/sheet/verify.py` is a concrete structural-check example: 279 cards, unique `seg09` IDs, initially empty marks/notes, two version rows, first Google row, embedded crop SHA256s, no external HTML assets and exact vendor JS. It attempts screenshots and records failure rather than fabricating a pass. Its `README.md` records browser launch failures and offline runtime success. SPLIT1's `QA_STATUS.md` similarly distinguishes mocked DB tests from screenshots and publication. SHEET1's two demos also lack screenshot confirmation in their handoff.

Those scripts can write receipts/screenshots and are documented here only; none ran in this documentation task. No live artifact was created, republished, queried or changed, and no mark-reload success is asserted.

## Sources read

- `AGENTS.md`
- `docs/records/review/{HUMAN_REVIEW_SHEETS.md,SHEET1_HANDOFF.md}`
- `greekocr/adjudicate/{README.md,owner_sheet.py,owner_sheet.js,owner_notes_export.py}`
- `greekocr/labelfix/sheet.py`
- `docs/records/review/reference_scratch/{build_segeval_sheet.py,build_gate_sheet.py,build_deskew_flips.py,build_cells_sheet.py,README.md}`
- `docs/harvest/line_pipeline/tool_versions.json`
- `docs/records/harvest/collect_v3_admission/segeval1/{SEGEVAL1_RESULT.md,owner_marks_20261019.jsonl}`
- `docs/records/harvest/collect_v3_admission/segeval1/gate2/HANDOFF.md`
- `docs/records/harvest/collect_v3_admission/segeval1/small_segments/{SMALL_SEGMENTS.md,owner_marks_smallseg.jsonl,tools/ss7_owner_marks.py}`
- `docs/records/harvest/seg_steps/sheet/{README.md,verify.py,receipt.json}`
- `docs/records/harvest/collect_v3_admission/split1/{SPLIT_PROPOSAL.md,QA_STATUS.md,HUMAN_REVIEW_SHEETS_SPLIT1.md,build_sheet.py}`
- `docs/records/labelfix/spellcheck/R2_evidence/{OWNER_REMARKS_20261017.md,page_builders/build_audit_template.py,page_builders/build_subst_page.py,page_builders/build_r1a_errors.py}`
- `docs/records/labelfix/secondary/HANDOFF_20261018.md`
- `docs/records/labelfix/spellcheck/R2/R2C_REPORT.md`
- `docs/records/cleanup_20261017/CLEANUP_STEP4_REPORT.md`
