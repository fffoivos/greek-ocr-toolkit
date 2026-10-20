# LF1 — benchmark last-filter builder and dry-run packs

Built 2026-10-20 00:02:45 EEST. **BUILD ONLY. No model reads, crop-pixel adjudication, probes, network calls, remote launches or .git writes were performed.** All other worktrees were read-only inputs. New writes are confined to this worktree and the requested external pack root. Synthetic tests decode/copy/transform pixels mechanically; no line was newly read or adjudicated.

## Deliverables and receipts

- [Lead run plan](../../../artifacts/lf1/DRYRUN_PLAN.md) (workspace path `artifacts/lf1/DRYRUN_PLAN.md`); entrypoint `artifacts/lf1/RUN_ALL.sh`.
- Packs: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/lf1_packs/dryrun/ctx01/` and `ctx02/`, each containing only `items.jsonl` + `img/`; **50 bed + 6 controls = 56 cards each**. All 112 opaque IDs are unique, k + 10 lowercase hex. Crops are independent file copies, content-hash PNG names, with metadata removed; 100/100 native bed crops retain exactly the same mode, dimensions and pixels as the source PNG.
- `artifacts/lf1/receipts/build.json`: source paths/hashes, seed 20261019, allocation, sealed key and manifest hashes. `artifacts/lf1/keys/ctx*.json`: private ID → line ID/label/source/control bindings. No crop image was written in the repository.
- `artifacts/lf1/prompts/source_bsb.md`, `GUIDE_NOTES.md`, `lf1.md`; `receipts/prompt_receipt.json`: unchanged qualified protocol-body hash and source/prompt hashes; `receipts/prompt_lines_added.json`: every new nonblank line and provenance.
- `tools/lf1.py`: deterministic mapping table and literal replacement hook. `tools/run.py`: lead fleet, limit probes, scanner, one VOID retry, answer mapping, run receipts and ledger. `tools/build_candidates.py`: accepts a primary-class-bound corrected draw without selecting/relabeling it. `tools/score_dryrun.py`: scoring.
- `receipts/tests.log`: 37 passed. `receipts/synthetic_positive_replay.json`: confined literal heredoc ImageMagick replay passes. `receipts/synthetic_ss4c_void.json`: SS4c-shaped items-driven montage heredoc with overwritten final zoom cannot be replayed and remains VOID. The scanner was copied by hash and **not changed**. Its dependencies were copied verbatim and pinned in the build receipt.

Scanner v4.5.5 SHA256: `e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1`. Scanner tests and real-pack synthetic audits ran offline under the handover's x86_64 Python/Pillow interpreter. No canonical live-reader rollout was rescored; no reader contexts were spawned.

## Qualified prompt and owner standard

Read: Sol `HANDOVER.md` §§2–7 and its unresolved routing in §8; `prompts/bsb.md` with `GUIDE_NOTES.md`; main-next SEGEVAL1 `prompts/owner_rubric.md`; `SEGMENTATION_FILTER.md`; local `CONTEXT_20261019_spellcheck.md` rule 1; main-next `NIGHT_PLAN.md` P6 and `POST_CLEANUP_PROGRAMME.md` §§3.2–3.4.

The bsb body from “You are a blind label checker” through its final “Never open key files or anything else” is **verbatim**, including its marks/crop_ok fields and output example. Its GPT-6 non-interactive header and completion wrapper are retained/adapted only for the items/img paths and extra answer fields. The preserved cards.jsonl references are explicitly aliased to items.jsonl; no duplicate cards file is created.

The original crop_ok rejects readable neighbour characters/letter bodies, which conflicts with the current owner's allowance. SEGEVAL1 already separated independent owner questions from this stricter field, but its old single-neighbour-word question cannot implement the current >2 whole-word standard. All five current requirements are therefore explicit independent owner questions. No detector proxies (95% visibility, x-height, padding, length predictor or height guard) enter the LF1 crop verdict. The five quoted owner wordings come from this LF1 brief and are corroborated by the context rule/programme §3.4; the current brief's 100% visibility governs over SEGMENTATION_FILTER's historical detector tolerance.

Marks are recorded because the qualified body is preserved, but ignored exactly as requested. This is the qualified letters-and-crop check, not a new claim of whole-line accent qualification. Reading is evidence only; labels are never replaced. One stored label contains Hebrew letters: the input wrapper explicitly names this script-data extension beyond bsb's listed script examples, rather than mislabelling it as Greek/Latin/Cyrillic or changing the stored text. No reading qualification on Hebrew is claimed.

### Every added nonblank prompt line, with source

Line numbers refer to `artifacts/lf1/prompts/lf1.md`. Existing body lines were neither rewritten nor removed. Formatting-only blank lines are excluded from this table.

| Line | Added line | Source |
|---:|---|---|
| 4 | - Your working folder holds only items.jsonl and img/ before reading. | LF1 user brief: Pack and run rules; HANDOVER sections 2-5; CONTEXT spellcheck scanner no path loops |
| 5 | - CARDS means ./items.jsonl, OUT means ./answers.jsonl, ZOOM means ./zoom/; cards.jsonl in the preserved protocol is an alias for items.jsonl, not another file to create. | LF1 user brief: Pack and run rules; HANDOVER sections 2-5; CONTEXT spellcheck scanner no path loops |
| 6 | - See every crop with view_image. Use literal relative paths only in every view_image call; write each call explicitly, with no path loops or computed paths. Batch about 5 to 10 explicit calls per tool call. | LF1 user brief: Pack and run rules; HANDOVER sections 2-5; CONTEXT spellcheck scanner no path loops |
| 7 | - ImageMagick (magick) is installed. Write every zoom once under a new name in zoom/; use only -filter point, -resize, montage/append. No -rotate, no font paths. | LF1 user brief: Pack and run rules; HANDOVER sections 2-5; CONTEXT spellcheck scanner no path loops |
| 8 | - Create only answers.jsonl and zoom/**. Write answers with shell commands. No network or web search. | LF1 user brief: Pack and run rules; HANDOVER sections 2-5; CONTEXT spellcheck scanner no path loops |
| 9 | - Input clarification: one stored label word has Hebrew letters; its word_scripts entry is Hebrew. The label is unchanged. | bsb Unicode-script input definition; frozen selected label Unicode names (HEBREW LETTER YOD / FINAL NUN); LF1 stored-label rule |
| 12 | The following qualified protocol body is preserved verbatim. Resolve its CARDS/OUT/ZOOM and cards.jsonl aliases using Environment above. | bsb.md / GUIDE_NOTES.md verbatim protocol and alias wrapper |
| 71 | # LF1 owner questions (independent of the historical crop_ok) | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 72 | Keep all protocol answer fields, but ignore marks for LF1 decisions. Historical crop_ok is evidence only because it is stricter about neighbour ink than the owner standard. | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 73 | Answer every following question in owner_crop using yes, no, or uncertain. A yes records the named fault, not a replacement label. | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 75 | ## one_central_line | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 76 | Owner wording: "there is exactly one central line of text". | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 77 | Question: Does the crop violate this requirement? | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 79 | ## text_ne_visible_line | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 80 | Owner wording: "the label matches the visible line exactly, neither more nor less (text running past the crop, omitted visible spans, letters cut through, merged lines = fault)". | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 81 | Question: Does the crop violate this extent/segmentation requirement? Record character substitutions separately in letters/errors/where. | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 83 | ## other_complete_line | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 84 | Owner wording: "no other line shows completely". | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 85 | Question: Does another line show completely? | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 87 | ## gt2_whole_neighbour_words | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 88 | Owner wording: "other lines show at most 2 WHOLE words (100% visible); cut neighbour words and partial letter bodies are allowed". | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 89 | Question: Do other lines show more than 2 WHOLE words (100% visible)? | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 91 | ## turned_or_clipped | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 92 | Owner wording: "Turned (rotated) or clipped crops fail." | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 93 | Question: Is this crop turned (rotated) or clipped? | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 95 | For a base-letter/digit/script/punctuation/hyphen text difference, add where as a list of {"label": "literal differing label substring", "printed": "what is printed"}. Use an empty string for an insertion/deletion side. Otherwise where is []. Do not use the marks field to decide a verdict. | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 96 | You may add reading as evidence only; it never replaces google_text and never decides the verdict by itself. | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 97 | Use segmentation_detail for crop evidence. Do not infer a crop fault solely from a character substitution. | LF1 user brief: five owner rules and evidence-only reading; CONTEXT_20261019_spellcheck rule 1; POST_CLEANUP_PROGRAMME section 3.4 |
| 100 | - answers.jsonl has exactly one valid JSON line per items.jsonl card, in the same order, with all preserved protocol fields and owner_crop/where. | bsb.md GPT-6 wrapper / GUIDE_NOTES.md; LF1 items.jsonl field additions |
| 101 | - You have checked count and order once with a command. | bsb.md GPT-6 wrapper / GUIDE_NOTES.md; LF1 items.jsonl field additions |
| 102 | - Reply with the protocol's short plain-text summary. | bsb.md GPT-6 wrapper / GUIDE_NOTES.md; LF1 items.jsonl field additions |

## Deterministic mapping (implemented and tested)

| Reader field / condition | Result |
|---|---|
| Any `owner_crop` field = yes | CROP_VIOLATES; collect every yes in table order: one_central_line, text_ne_visible_line, other_complete_line, gt2_whole_neighbour_words, turned_or_clipped |
| No positive crop fault, but uncertain crop answer or letters=u / incomplete answer | No invented verdict: unresolved receipt and lead/human routing (HANDOVER §8); never auto-OK |
| All owner crop answers no; letters=n, or errors contains wrong_letter / lookalike_script_letter / missing_word_or_span / extra_text / punctuation / hyphen / digits | TEXT_DIFFERS, with validated literal label-substring + printed span in where |
| All owner crop answers no; letters=y; no listed textual error | OK |
| marks, mark-only error types, historical crop_ok, optional reading | Evidence only; no independent verdict effect |

Crop faults take precedence over text differences. A crop extent mismatch (text beyond crop, omitted visible span, cut letters or merged lines) is the `text_ne_visible_line` question; a character substitution within the same extent is letters/errors/where. Positive crop faults take precedence over uncertainty, following gate2's saved scoring order; remaining uncertain cards require the lead. Schema/coverage checks are data-integrity checks, not extra segmentation rules.

The replacement hook consumes exactly the flagged IDs and the draw's ordered overdraw list. For each flag in supplied order it takes the next unused line of the same class and source; every outcome is recorded, including UNFILLED. Replacements are not automatically accepted or relabelled. No benchmark is sealed by LF1.

## Dry-run sample and controls

The 888 calibration crop hashes are bound to `main-next/docs/records/harvest/seg_steps/s1/crop_bindings.jsonl`. Labels and ratings are taken from the frozen review-site `box-length-experiment.json`, predicted-rows, and bound population detail chunks in the same way S1's replay loads them. All 135 explicit rating objects were found: 78 KEEP /57 DROP. The proportional seeded sample selects **100 rated lines**, 58 KEEP /42 DROP. The 753 unrated lines were not needed. The owner truth file preserves the complete rating object; KEEP → OK and DROP → not OK, independently of historical reference_verdict or segmenter output.

The benchmark-0.2 scheme **is defined** in `docs/cleanup_20261019/POST_CLEANUP_PROGRAMME.md` §3.2 (16 rows despite its older nearby “15” prose). It is used as available overlapping quota facets; source × script fallback is not used. Because primary precedence and several tag definitions are absent, sampling strata are quota-facet signatures; four selected lines are UNASSIGNED. We do not infer Cyrillic language from source or invent confidence/degradation thresholds. This is explicitly a calibration dry run, not a class-complete benchmark draw or a new primary allocation policy. The production adapter requires P5's primary class unchanged.

| Available quota-facet sampling stratum | Selected |
|---|---:|
| `UNASSIGNED` | 4 |
| `caps_headings|greek_monotonic_ordinary` | 2 |
| `caps_headings|greek_monotonic_ordinary|long` | 1 |
| `caps_headings|greek_monotonic_ordinary|long|vertical_turned` | 2 |
| `caps_headings|greek_monotonic_ordinary|short_noncell` | 3 |
| `caps_headings|greek_monotonic_ordinary|short_noncell|vertical_turned` | 2 |
| `caps_headings|greek_polytonic_ordinary` | 1 |
| `caps_headings|greek_polytonic_ordinary|long` | 1 |
| `caps_headings|greek_polytonic_ordinary|short_noncell` | 1 |
| `greek_monotonic_ordinary` | 4 |
| `greek_monotonic_ordinary|long` | 4 |
| `greek_monotonic_ordinary|long|short_noncell` | 1 |
| `greek_monotonic_ordinary|long|vertical_turned` | 2 |
| `greek_monotonic_ordinary|short_noncell` | 10 |
| `greek_monotonic_ordinary|vertical_turned` | 1 |
| `greek_polytonic_dictionary_journal|greek_polytonic_ordinary|long` | 1 |
| `greek_polytonic_dictionary_journal|greek_polytonic_ordinary|short_noncell` | 1 |
| `greek_polytonic_ordinary|long` | 2 |
| `greek_polytonic_ordinary|short_noncell` | 6 |
| `latin` | 14 |
| `latin|long` | 2 |
| `latin|numeric_table_cells` | 1 |
| `latin|short_noncell` | 13 |
| `latin|short_noncell|vertical_turned` | 1 |
| `long` | 2 |
| `numeric_table_cells` | 2 |
| `numeric_table_cells|vertical_turned` | 1 |
| `short_noncell` | 15 |

Six frozen constructed controls are copied into both contexts. Together they cover OK, all five crop fault codes, and TEXT_DIFFERS. Pool keys and constructions are in `artifacts/lf1/keys/control_pool.json`; the complete native paths and expected outcomes for the lead's mandatory pixel check are listed in `DRYRUN_PLAN.md`. **Lead pixel review is pending by design.** The runner will not start until it is recorded. Existing saved SEGEVAL evidence justifies the base line; the transformations do not constitute a new owner rating or a live reader qualification.

## Lead execution and measurement

The run plan supplies the exact commands and review-file schema. The fleet accepts ≤24 concurrent reader contexts, probes before and after each start, refuses ≥90% weekly usage, runs the canonical scanner on every located reader rollout, and gives a VOID context one fresh-context retry only. A second VOID is left in the ledger. A control error count >1 is flagged as the handover requires; no additional control threshold was introduced. Prompt, key, manifest, scanner and dependency hashes are checked for custody. Network/web, plugins/apps and delegation are disabled for future readers.

Scoring reports per-class flag rate, owner binary agreement and confusion table, explicit unresolved count, plus a crop-only comparison because owner marks judge segmentation rather than label spelling. Tokens and weekly pp are normalized by all actually read cards (including controls and retries). Weekly deltas remain shared, coarse observations; concurrent intervals overlap. Use the serial dry-run command to avoid overlap, and do not interpret zero displayed movement as zero cost. No live budget/quality figures are claimed: `dryrun_score.json` is NOT_RUN and token/weekly measures are null.

LF1 READY: tests 37 passed; packs 2 (cards 56+56, controls 12); dry-run lines 100 (owner-rated 100)
