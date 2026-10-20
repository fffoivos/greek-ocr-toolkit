# Agent readers — packs, binding, scoring and VOID

This document separates the recorded Sol-reading protocol from the newer shared `greekocr.adjudicate` API. Historical task exceptions stay attached to their receipts. Neither a model's answer nor a clean control score alone establishes an accepted reading.

## Package only the assigned evidence

The recorded Sol handover uses `PACK_ROOT/<bed>/<reader>/`, outside repositories and away from keys. Each context has only its public item file (`items.jsonl` or `cards.jsonl`), `img/` or `crops/`, and where specified a public README/schema. The reader may add **only `answers.jsonl` and `zoom/**`**. `MANIFEST.<reader>.json` is outside the reader folder beside assignments; keys, contact sheets, other answers and reports never belong in the pack root handed to a reader.

Items have fresh opaque `k`+10-hex IDs; images are copied, never linked, stripped of metadata and named by encoded-content SHA256. Data/controls are shuffled with a fixed seed; reader 2 is exact reverse order, and tiebreaks get fresh order/options/maps. The private key connects opaque ID to original line/slot, source, truth/control meaning and option mapping. Preserve it outside the readable assignment. Public fields vary by protocol: the line check intentionally shows the proposed Google text to compare against pixels; the accent pass must not expose Google text. Never expose source IDs, expected answers, stratum labels, private notes or tool verdicts.

`docs/records/harvest/sol_reading/tools/build_packs.py` records input hashes, builds pixel-derived content-hash images and task-specific fields. `tools/scan_packs.py` checks exact fields, IDs/order, private-assignment membership, exact expected file set, safe relative references, no symlinks/hardlinks, RGB PNG metadata/hash constraints and reader-2 reversal; it writes the closure manifest only after success. R2/Opus card packs also include a public protocol/schema and native-derived word/line images; their private options/provenance stay outside.

The shared package has a different concrete format: `build_deck` emits `items_blind.json`, `reader_2.json`, `img/`, viewer/schema/instructions and sibling private evidence, with `item00000`-style opaque IDs. `deal_batches` copies only allowed public fields and referenced images to `bNNN/rN`, with all-file SHA receipts. Its default batch size is **110**, whereas the Sol HANDOVER operational limit is **≤100 total items/context** (≤90 study items plus roughly 10% controls). Do not use the generic default to override the Sol context limit.

For immutable dealt assignments, answers belong outside the assignment tree because `batch_check` compares the exact original file set. That is not the Sol pack's allowed-added-files convention. State which contract the run uses.

## Reader assignment and launch binding

The historical Sol settings in `HANDOVER.md` are `gpt-6.1-sol`, reasoning **medium**, CLI **0.159.2**, cwd the reader folder, `--sandbox workspace-write`, network off, web disabled, multi-agent/apps/remote plugins disabled, `project_doc_max_bytes=0`, approvals never, prompt on stdin. These are recorded settings, not a claim about the installed CLI today. The launcher checks the model from the actual rollout and captures usage. The run chain is limit probe → read → leak scan → mapping/scoring → limit probe → ledger. The recorded driver refuses at ≥78% weekly used and the owner stop rule is 80%; no current quota is inferred from old percentages.

The sandbox **does not restrict reads**: the blinding audit and handover record an outside canary being readable. Isolation therefore depends on a clean assigned folder, instructions, verified closure and rollout audit, not the workspace-write flag alone. Do not start a reader with repository history, parent keys, earlier judgments or another reader's output in context.

| Work | Recorded assignment / limitation |
|---|---|
| Masked ъ/ь glyph reading | Sol qualified one-reader historical task; source text is masked at target positions |
| Whole-line letters and crop | Sol qualified; marks field is not qualified evidence for decisions |
| Final-word grave/acute type | Separate Sol word question plus fresh-context re-read of every flag and lead/human eye |
| Four-head R2 marks | Opus per coordinator ruling; Sol's whole-line mark checks and R2 variance did not qualify it |
| New shared-package decks | Two independent readers plus independent tiebreak; do not relabel old one-reader checks as two-reader gold |

`docs/records/harvest/sol_reading/HANDOVER.md` reports 64/65 yer slots, bsb letters 99/100 and crop 98/100, but missed 3/3 printed-grave errors inside whole-line marks and variable R2 results. These are small historical beds; not release-scale guarantees or proof of recall among unflagged lines. Independent Opus reads remain subject to their own controls, coverage and resolution checks.

## Canonical scanner identity and proofs

Execute the canonical scanner by verified hash on the recorded rollout, original reader manifest and actual pack. The inspected source is `docs/records/harvest/sol_reading/tools/scan_rollout.py`, **VERSION='4.5.5'**, SHA256:

```text
e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1
```

`HANDOVER.md` and `out/scan2f/HANDOFF.md` agree. `tools/SCANNER_CANONICAL.json` still distributes **v4.4**, SHA `dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547`; `SCANNER_V45_NOTES.md` describes v4.5. Code/current qualification win over those older labels. Retain their receipts as historical evidence; do not rewrite an old scan to look newly accepted.

The scan covers:

1. **Images returned to the model.** Each must bind to an assigned file by exact bytes/pixels, an allowed common non-upscaling return, or chronological reconstruction from verified originals. Scaled returns need common scale within one pixel on both axes, RGB MAD **strictly <2/255**, a named standard Pillow filter and opaque alpha. Native same-size comparisons retain exact mode/pixels. Crops, distortion, upscales and unproven returned images fail.
2. **Tool-input paths and strings.** External absolute paths, parent/home traversal, keys/truth/verdicts/other-reader/manifest access fail. The own reader root is allowed; `.keys()` is not itself a leak. Pwd templates require exact recorded successful pwd output. Literal stored bases/concatenations need the supported preceding bindings. Font reads have narrowly proven operand rules, not a global external-path exception.
3. **Manifest closure.** Originals stay intact, with only permitted answer/zoom additions. Do not skip this check to obtain a clean result.
4. **Chronological helper authority.** Finite statically provable templates and confined helpers can be replayed; dynamic bounds or unsafe helpers fail. P1 masks only closed answer atoms to the recorded AST-pinned recorder with current-source byte proof. V4.5.5 applies a write barrier before every execution-unit admission/replay; unknown effects revoke all cached scripts. Final restored bytes do not prove that earlier helper invocations were safe. Only a new literal definition restores authority.

Use simple literal relative image paths and avoid path-building loops in reader prompts. Supported finite-template reconstruction is not a reason to rely on arbitrary code. The SF7 context pack records a remaining JS literal-array loop issue and follow-up v4.5.6; no 4.5.6 adoption is inferred from that note. A scanner change/rescan is a new, separately hashed audit record, not a license to ignore a violation.

## Map, score, bind

Before scoring, bind opaque answers through the correct private option/slot map. Check unique IDs, exact assigned order and complete coverage; retain confidence, uncertainty, raw answers and per-item image-view evidence. An answered item is not automatically a viewed item, and a derived montage qualifies only through proved command/image ancestry. A scan's aggregate returned-image count is not automatically item coverage.

Bind the result to source/crop hashes, public manifest/closure, prompt/protocol identity, model/effort, rollout, answers, scanner executable/dependencies, scan outcome, control gate and timestamp. SEGEVAL's `scan/v4.5.5/*/r1.custody.json` is a concrete receipt pattern: command/executable, scanner hashes, handover, manifest/original closure, unchanged answer/rollout hashes and no skipped manifest. `scan/verdicts.json` compares old/new scans without overwriting the original v4.4 records.

For shared adjudication, `batch_check` gates one immutable assignment without producing truth; `resolve` requires two genuine assigned reads, controls first, then agreement/tiebreak; `write_truth` preserves UNKNOWN and writes exclusively. `score.py` estimates weighted outcomes against truth; it does not validate a rollout or adjudicate print. For line-check studies use their actual scoring function and rubric, not an unrelated generic control threshold.

Examples of bound evidence:

- `docs/records/harvest/collect_v3_admission/segeval1/SEGEVAL1_RESULT.md`: both existing study contexts pass v4.5.5; 10/10 controls; same original answers and FP 29/50, FN 5/100 under the four-question rubric. These two contexts partition the sample; they are not two reads of each line.
- `docs/records/harvest/collect_v3_admission/segeval1/gate2/HANDOFF.md`: later full-answer owner-state rubric gives different counts on the same frozen lines; do not replace it with the original four-question rates.
- `out/scan2f/HANDOFF.md`: 107 scanner tests, six witnesses, 15/15 CQ4 rescans valid, 22 protected hashes unchanged; expressly no reader run or answer scoring.
- `docs/records/labelfix/spellcheck/R2/R2C_REPORT.md`: preparation, private key/geometry custody and later resolver validation are separate from accepted reader truth.

## VOID and unresolved evidence

| Failure | Required treatment |
|---|---|
| Any unresolved canonical leak/provenance violation | VOID the run under the Sol handover; preserve raw answers/rollout/scan and do not score as valid |
| Tampered/missing original manifest or hash mismatch | Fail custody; missing evidence is not a pass; do not disable the check |
| Missing/duplicate/out-of-order/malformed answers | Fail assignment/schema coverage; unresolved positions are not silently dropped from study denominators |
| Required image coverage missing | Apply the task's explicit coverage gate; historical CAPS/SRK briefs void the run below complete coverage |
| Control failure | Use that protocol's gate, never a convenient universal threshold. Sol handover flags >1 error; shared resolver defaults to zero errors/no shared misses; track-specific abstention/raised-control rules differ |
| Matching answers but unknown/unreadable/ownership failure | Preserve UNKNOWN/HOLD and route to independent tiebreak or lead pixel review; agreement cannot create missing observations |
| Replacement reader | Fresh context/assignment with its own key/scan/custody; retain the VOID predecessor and explicit replacement relationship |

Track-specific historical rules must remain visible. RU1's historical combiner allowed a VOID hard vote only as corroboration when at least one gate was VALID, while other numeric/train finalizers exclude invalid/VOID votes entirely. That RU1 exception is not the new shared resolver's rule and is not permission to use a provenance-VOID run. `docs/records/labelfix/secondary/RU10_REPORT.md` explicitly excludes ctx04/r2 permanently for **15 unresolved provenance findings** despite its historical control-score VALID. Its accepted replacement is ctx04/r3. Do not confuse control validity with scan clearance.

Fresh scans may change a custody verdict only under an explicitly accepted scanner version and retained comparison receipt. Old VOID answers are never silently promoted because a later headline says “15 valid.” Do not rerun a reader solely to replace inconvenient content or count multiple views from one context as independent readers. Remaining failures/unreadables stay in the lead/owner residual queue or HOLD according to the specific tool contract.

## Tests and execution boundary

Read tests: `tests/adjudicate/test_deck_protocol.py` (shuffling, profiles, controls, tiebreak maps, UNKNOWN), `test_sr1.py` (custody/batches/exports), `test_score.py` (statistics); scanner qualification in `out/scan2f/HANDOFF.md` and scanner test sources. Real historical scans require their original packs/rollouts; unavailable witnesses cannot be represented as executed passes. This documentation run launched no reader, scanner, test, export, pipeline or compute job.

## Sources read

- `docs/records/harvest/sol_reading/{HANDOVER.md,SCANNER_V45_NOTES.md,tools/SCANNER_CANONICAL.json,tools/scan_rollout.py,tools/build_packs.py,tools/scan_packs.py}`
- `greekocr/adjudicate/{README.md,deck.py,protocol.py,deal_batches.py,batch_check.py,artifact_custody.py,score.py}`
- `docs/records/cleanup_20261017/CLEANUP_PLAN_20261017_blinding.md`
- `docs/records/contexts/CONTEXT_20261019_spellcheck.md`
- `out/scan2f/HANDOFF.md`
- `docs/records/harvest/collect_v3_admission/segeval1/{SEGEVAL1_RESULT.md,SEGEVAL2_HANDOFF.md,prompts/owner_rubric.md}`
- `docs/records/harvest/collect_v3_admission/segeval1/gate2/HANDOFF.md`
- `docs/records/labelfix/spellcheck/R2/R2C_REPORT.md`
- `docs/records/labelfix/secondary/RU10_REPORT.md`
- `docs/records/briefs/{CAPS2_score.md,SRK2_kosmo_poly1850_score.md,RU11b_second_reader.md}`
- `tests/adjudicate/{test_deck_protocol.py,test_sr1.py,test_score.py}`
