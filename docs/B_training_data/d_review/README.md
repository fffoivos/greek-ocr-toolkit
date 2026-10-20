# B.d — revision of training-data tools

Documentation for `docs/B_training_data/d_review/`, read against the integrated cleanup branch on 19 October 2026. This directory describes review and evidence, not a pipeline execution. Current tool identities come from `docs/harvest/line_pipeline/tool_versions.json`: segmentation **0.13 (label 0.9-s5)**, content gate **0.3**, polytonic **0.7** (SF7 `candidate_pre_audit`), Cyrillic **0.3**, numerics **0.3** (assisted; automatic candidate rejected), dashes **0.1** (tags only). Older handoffs describe their recorded generations; they do not override this manifest.

## The loop as practised

1. **Change the tool under the owner's stated rule.** Keep the method/version, source hashes, inputs and scope guard with the change. `AGENTS.md` says owner-accepted tools implement the owner's rules; additional measurements belong in diagnostics and owner questions. A review-sheet builder consumes saved evidence and does not rerun a detector or reader.
2. **Replay the frozen sets.** Compare the same crop bytes, Google labels and saved judgments across versions. For segmentation, gate2 replayed 150 SEGEVAL lines and 888 calibration lines; only 135 of the 888 had explicit owner ratings. S1–S4 also used 250 cell samples, without inventing labels for them. Save per-row evidence, old/new verdicts, failures, flips, input hashes and readback checks.
3. **Build an owner sheet.** Crop and Google text stay together, with saved overlays, the last two available tool versions, a tool verdict, an independent owner mark and a note. Put unjudged lines first and prior marks last. Explain exactly what KEEP/DROP mean. See [OWNER_SHEETS.md](OWNER_SHEETS.md).
4. **Publish and preserve marks.** The signed-in claude.ai artifact saves user actions to collection `notes`. Before every republish, dump that collection; retain stable document IDs and check saved marks reload. Local HTML without the artifact DB does not persist marks. See [PUBLISHING.md](PUBLISHING.md).
5. **Score against the recorded marks.** Join by stable line identity, preserve notes and source sheet, and state how repeats were resolved. Count unmarked/unresolved lines separately. Reader-derived labels, historical owner ratings and new explicit owner marks are different evidence populations.
6. **Adopt or hold by the recorded decision.** Report score changes and counterexamples to the owner; a lower error count alone is not an adoption decision. The current manifest explicitly records segmentation `accepted_as_is`; the cleanup owner brief says the segment filter is good enough and the owner does not want further review. Historical open-cell/0.8-adoption questions in the early 19 October context packs are not the current instruction to reopen qualification. SF7's manifest status remains `candidate_pre_audit`.

## Roles

| Role | Responsibility evidenced in this branch |
|---|---|
| Owner | Defines usable crops and literal labels; marks cards and notes; decides tool rules and acceptance |
| Coordinator/lead | Freezes evidence and controls, supplies briefs, assembles review sheets, dumps artifact marks before republishing, checks reload and records decisions |
| Sol implementation/replay worker | Implements the brief and produces hash-bound replay, scoring and verification receipts; reports uncertainty and scope limits |
| Independent readers (Sol/Opus as assigned) | Read only their blind assignments and their pixels, record literal observations and uncertainty; never substitute a tool prediction for truth |
| Lead pixel eye / owner residual review | Checks controls and unresolved/disputed cases; preserves holds where evidence remains insufficient |

These are workflow roles, not permission to run a reader, publish, train or submit compute. The standing context packs reserve launches to explicit owner authorization and verified coordinator submission.

## Owner standards

The segmentation standard is recorded in `docs/records/contexts/CONTEXT_20261019_segmentation_and_secondary.md`:

> (a) exactly one central line; (b) the Google text matches the visible line exactly, neither more nor less; (c) no other line shows completely and at most 2 WHOLE words from other lines, where whole = 100% visible — a readable but cut word is a cut-off word and does not count. Partial neighbour letter bodies alone are fine.

That is the owner standard, not a claim that every historical implementation measured it exactly. Gate2's old inventory used a ≥60%-visible-body proxy; S1 changed whole-word evidence to every letter body ≥95% visible. The manifest retains those method generations. Do not silently equate these proxies with the quoted 100% standard, or add a clipping veto the owner rejected.

For labels the rule is **“transcribe what is printed”**: retain printed misprints, case, script, punctuation and marks rather than normalizing to expected spelling. `docs/records/briefs/S2_mark_detector_print_truth.md` quotes: “For training OCR we need to transcribe what we see, not what we would like to see.” `docs/records/briefs/R2C_card_decks.md` explicitly includes misprints. The shared independent-reader instructions in `greekocr/adjudicate/protocol.py` require literal printed forms and allow unreadable/uncertain answers.

## Evidence and mark locations

All paths below are repository-relative evidence paths, not a new storage migration.

| Evidence | Location / interpretation |
|---|---|
| Live owner marks | Artifact DB collection `notes`, usually `<sheet_prefix>:<line_id>`; legacy line/slot IDs remain supported |
| Combined 19 Oct mark dump | `docs/records/harvest/collect_v3_admission/segeval1/owner_marks_20261019.jsonl`: `sheet`, `line_id`, `owner_mark`, `note`, `updated` |
| Small-segment marks | `docs/records/harvest/collect_v3_admission/segeval1/small_segments/owner_marks_smallseg.jsonl`; strict dump-to-card validation in `small_segments/tools/ss7_owner_marks.py` |
| Replay mark snapshots | `docs/records/harvest/seg_steps/s1/owner_marks_snapshot.jsonl`, `s4/owner_marks_snapshot.jsonl`, `s4/typology_owner_marks_snapshot.jsonl`; keep the particular snapshot bound to each replay |
| Version comparison | `docs/records/harvest/collect_v3_admission/segeval1/gate2/{HANDOFF.md,replay_segeval1.jsonl,replay_calibration.jsonl}` |
| Current segmentation replay | `docs/records/harvest/seg_steps/s4/{REPORT.md,replay.jsonl,flips.jsonl}` |
| Offline note export API | `greekocr/adjudicate/owner_notes_export.py`: joins a supplied dump, never contacts a live DB; requires explicit sheet conventions, rejects unknown/duplicate identities, writes exclusively |

`owner_notes_export` flags nonempty notes or edited Printed fields according to the supplied convention; it does not interpret every note as a rejection or every absent note as acceptance. Explicit KEEP/DROP scoring uses the actual marks.

S4's report deduplicates 240 explicit entries to 235 line IDs by latest timestamp, then file order. Agreement rises from 155/235 (0.8) to 189/235 (0.9-s4); the 135 rated calibration subset rises 94→109/135. The 150-line gate2 rubric gives FP/FN/UNC 18/14/11→16/15/0. These are different denominators and evidence types. The original SEGEVAL four-question scorer instead reports 29/50 false rejects and 5/100 misses; its rubric and sampled decision strata must stay attached to those figures. The early context pack's 0.8 FN=11 and the archived sheet builder's baseline headline are superseded by the specific saved scoring records, not copied into the current comparison.

## Reading map and validation limits

- [OWNER_SHEETS.md](OWNER_SHEETS.md): rendering, interaction, persistence and tests.
- [PUBLISHING.md](PUBLISHING.md): publication checks, mark preservation and sheet register.
- [BLIND_REVIEW.md](BLIND_REVIEW.md): independent pixel adjudication, custody, truth and statistics.
- [AGENT_READERS.md](AGENT_READERS.md): isolated reader packs, scanner binding and VOID handling.

This documentation pass did not execute tests, replays, readers or publications. Test outcomes cited in these documents are historical receipts. Structural/runtime success is not a screenshot or a successful live database reload.

## Sources read

- `docs/cleanup_20261019/OWNER_BRIEF.md`
- `docs/cleanup_20261019/PLAN.md`
- `AGENTS.md`
- `docs/harvest/line_pipeline/tool_versions.json`
- `docs/records/contexts/CONTEXT_20261019_segmentation_and_secondary.md`
- `docs/records/briefs/S2_mark_detector_print_truth.md`
- `docs/records/briefs/R2C_card_decks.md`
- `greekocr/adjudicate/{README.md,protocol.py,owner_sheet.py,owner_sheet.js,owner_notes_export.py}`
- `docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md`
- `docs/records/harvest/collect_v3_admission/segeval1/{SEGEVAL1_RESULT.md,owner_marks_20261019.jsonl}`
- `docs/records/harvest/collect_v3_admission/segeval1/gate2/HANDOFF.md`
- `docs/records/harvest/collect_v3_admission/segeval1/small_segments/{owner_marks_smallseg.jsonl,tools/ss7_owner_marks.py}`
- `docs/records/harvest/seg_steps/s1/REPORT.md`
- `docs/records/harvest/seg_steps/s4/REPORT.md`

The HTML files under `demo/` are frozen historical design fixtures (including 0.7/0.8 policy and 0.50–1.50 band labels). Their displayed tool versions and retained hashes describe those snapshots. Use the current B.c graph and tool manifest for current policy.
