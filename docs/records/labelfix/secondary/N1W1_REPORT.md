# N1-W1 preparation

Prepared on the exact **1,312 passing ADM5c ELSTAT numerics_tables rows**. No model readings, usage probes, visual glyph classification, browser/computer use, network calls, `.git` writes, production apply, or LQB registration were executed.

## Admission and custody

Exact admission: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/w1_originals_v3_admitted.jsonl`.

SHA-256: `b6d13fa8bb4b07be632e299fd650cd75dd80348ecf0e0fd9e5cb34bdb6c72bfe`. The sol-recut directory's README.md documents this output of the ADM5c admission command on sol/collect-v3's original admission. Its receipt records 28,798 passing rows from 30,114 originals, including **1,312 ELSTAT numerics_tables rows**. All selected rows have `admission.passed=true`; the pipeline preserves every admission field and diagnostics in [parent.jsonl](../../../../artifacts/n1/n1w1/parent.jsonl), adding exact W1 ID/document metadata. Labels, page IDs, original crop boxes and crop hashes must match W1 exactly. No labels differ in this selected population.

All registered release-exclusion classes, including n1_locked_eval, are applied and hash-checked before localisation; **0 selected rows** overlap the current union. The stronger local N1 reserved-document/line guard also applies. Full W1 features, admission, receipt, original input, README, exclusion registry/class files, local locks, page receipts, exact responses, required crops, controls and all dedicated helpers are hash-bound. Collector/admission inputs remain read-only.

The exact file was found by a wider local search in sol-recut. An initial preparation from the earlier 2,519-row ADM4 population was superseded **without running readings**. That preparation is preserved under scratchpad/n1w1_superseded_pre_adm5c/, labelled NEVER RUN; active packs/keys/report/receipt use only the exact ADM5c population above.

## Candidate census and exact geometry

**1109 candidates** on **891 rows**: 1102 periods and 7 ASCII hyphens. The inherited N1-TR tokenizer enumerates every interior single Google `-` or `.` slot within maximal numeric tokens containing at least four ASCII digits. Ranges remain in the census for provenance but are never eligible for edits.

**1069 localised; 40 held**. Localisation uses the N1-C collector text anchors and exact W1 DocAI digit symbol geometry, with no projection/proportional fallback, new OCR or pixel classification. Every nonreserved candidate localised successfully. The **40 N1_reserved slots** remain in [candidates.jsonl](../../../../artifacts/n1/n1w1/candidates.jsonl), [unlocalised.jsonl](../../../../artifacts/n1/n1w1/unlocalised.jsonl) and [reserved_holds.jsonl](../../../../artifacts/n1/n1w1/reserved_holds.jsonl); they enter neither geometry/pixel processing nor packs.

All 857 required line crops match frozen SHA-256s, with no unavailable crops. Crop regeneration uses an explicit arm64 collector Python/Pillow 12.3.0 launch and scratch-only row copies; rendering/verification use the prescribed x86 Python. The initial architecture mismatch was corrected before the active build. No real image was opened for inspection.

## Packs and estimate

Root: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/n1w1`.

**14 contexts ×2** use sep2, 76–77 candidates and nine approved controls per context, **85–86 items total**, with **10.47–10.59% controls** and at least one raised-dot control each. R2 is the exact reverse with disjoint opaque IDs and a fresh derangement of all ten options. Private keys stay in artifacts/n1/n1w1/keys/. All **28 packs** have sealed manifests and passing [closure checks](../../../../artifacts/n1/n1w1/closure.json).

Estimated **2390 item reads / 4.78 Codex points** using the inherited 0.2 points per 100 item reads. This is a preparation estimate, not observed usage or a live account quote; probe/retry costs are outside that estimate.

## Driver

```sh
scripts/secondary/reading/run_n1w1_all.sh --dry-run
# Run only after readings are explicitly authorised:
scripts/secondary/reading/run_n1w1_all.sh
```

The driver validates bound inputs and sealed packs, takes a process lock, probes before each context and stops at weekly usage >=70%. Permanent attempt claims prevent automatic retries, including after crashes. It pins **gpt-6.1-sol / medium / network OFF**, disables web/apps/multi-agent, probes after contexts, records usage, and archives answers under artifacts/n1/n1w1/answers/. The active **28-context [dry-run](../../../../artifacts/n1/n1w1/driver_dry_run.jsonl)** passed without probes or readings.

## Finaliser and lead review

```sh
# After authorised readings exist:
scripts/numerics/n1w1_finalize.sh
# Lead completes scratchpad/n1_review/n1w1/lead_template.jsonl from pixels:
scripts/numerics/n1w1_finalize.sh --apply-lead
```

The first invocation re-audits independent rollouts with the dedicated canonical-v4.4 scanner copy, checks model/effort and image ancestry, decodes sep2 and gates viewed controls. More than one wrong viewed control, no correct viewed raised control, or fewer than two viewed controls makes a context VOID. Invalid/malformed/missing contexts and unviewed items cannot supply usable votes. Partial finalisation requires STOPPED_AT_70.json, and preserves the full selected population.

Every two-valid-read raised-dot agreement gets a lead sheet cell and initially unfilled template entry, including range proposals. Each cell shows target zoom, line, parent text/offset, and **approved same-document raised-dot controls where possible**. Four approved raised controls share the document of **465/1069** localised candidates. Actual lead-sheet coverage depends on future agreements. Same-document peer agreements may be shown only as **NOT adjudicated**; missing references are explicitly unavailable. Review/index/sheet/crop hashes bind the apply step.

Only two valid agreeing raised-dot reads **and** the lead's completed raised-dot pixel check permit a one-character Google `-`/`.` → **U+00B7** replacement. Tokenizer range proposals and lead range rulings always hold. Every other outcome is a recorded hold with offsets, reads, confidence and context status; no ink classifier participates.

`--apply-lead` writes **artifacts/n1/n1_v1_w1.jsonl**, its manifest and SHA sidecar, retaining all 1312 selected rows, parent labels, edits, holds and per-slot provenance. It registers `n1_v1_w1` in docs/records/labelfix/lqb/versions.json under the exact snapshot parent `n1w1_admitted_elstat`. Registration is implemented and fixture-tested; it was not executed on production data. No paired benchmark re-score is claimed for this admitted population.

## Helper isolation and validation

Mutable workflow helpers are dedicated **n1w1_*** copies: pack/closure scanners, canonical rollout scanner, literal replay/coverage, common/ledger, launcher/read/probe, tokenizer/locks/geometry, renderer, lead presentation, answer decoding and crop regeneration/storage. Their own copies and sep2 prompt are hash-bound; another pipeline's helper edits cannot change this pipeline. Approved controls, exclusions and locks remain explicit bound data inputs.

**38 tests passed**. Coverage includes a complete synthetic two-read → lead → apply → LQB registration flow; exact admission selection and nonpassing/excluded-row rejection; exact symbol geometry; range vetoes; lead enforcement; approved same-document reference selection; malformed answers, invalid/VOID/unviewed contexts, rollout reuse and model/effort mismatch; image ancestry; partial holds; stop-at-70 and retry prevention; reverse/fresh packs and tamper rejection; network-off launch construction; full active-population/pack accounting. Synthetic rollout fixture records invoke no reader. These tests establish workflow/custody, not glyph truth.

Evidence: [build.json](../../../../artifacts/n1/n1w1/build.json), [TESTS.xml](../../../../artifacts/n1/n1w1/TESTS.xml), [N1W1_RECEIPT.json](../../../../artifacts/n1/n1w1/N1W1_RECEIPT.json).

N1W1 READY: rows 1312; candidates 1109, localised 1069; contexts 14 ×2; est 4.78 pts; closure ok; driver dry-run ok; tests 38 passed

## N1W1F2 — replacement combine and edits-only release (18 October 2026)

This section supersedes the earlier full-population, post-convention-label apply specification. The F2 output uses **raw W1 Google `text`**, with only the 22 lead-confirmed separator substitutions. No reader, probe, network, browser/computer-use action or `.git` write was performed. Original sealed helper and pack bindings were preserved; the separate [F2 materialiser](../../../../scripts/numerics/n1w1_f2.py) implements the coordinator's revised output contract.

The replacement-aware finaliser re-ran canonical **v4.4** rollout scans, model/medium provenance, viewed-control gates, image ancestry/coverage and logical two-reader routing. **20/44 physical contexts were VALID** (13/28 original; 7/16 replacement); 21 were VOID and 3 INVALID. The effective routed context count is **19/28 VALID**, 7 VOID, 2 INVALID. Physical context counts include superseded evidence; only valid, viewed votes on the selected logical route contribute. Context statuses and evidence hashes are retained in the receipt.

The exhaustive, mutually exclusive census over **1,109 slots** is:

| Outcome | Slots |
| --- | ---: |
| Agreed raised | 63 |
| Agreed hyphen/dash | 2 |
| Agreed baseline dot | 365 |
| Agreed other | 0 |
| Two usable reads disagree | 105 |
| Still missing two usable reads | 574 |

Still-missing includes the 40 reserved/unlocalised slots. These counts compare exact decoded meanings from two valid, viewed logical votes; confidence remains recorded as in the inherited W1 combine. Different dash meanings count as disagreements. No missing, VOID, invalid or unviewed vote was promoted.

All **22 original sheet slots remain agreed raised**. Their identities and crop hashes were checked against the original sheet index and the [lead ruling](N1W1_LEAD_RAISED.md); all original contact-sheet hashes were verified. The **41 new raised agreements** are pending lead review on **seven sheets**, six cells per sheet except the last five. The sheets repeat the exact same two approved raised and two approved baseline references as the original sheets. Targets, references and generated PNGs were hash/decoder-checked; no fresh pixel ruling was made.

Scratch review directory: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/n1_review/n1w1/sheets2/`. It contains `raised_01.png` through `raised_07.png`, `index.json`, `index.md`, and unfilled `lead_template.jsonl`. [Pending slots](../../../../artifacts/n1/n1_v1_w1_pending.json) list those same 41 slots with crop hashes and the sheet-index binding; none was edited.

The [output](../../../../artifacts/n1/n1_v1_w1.jsonl) contains **629 rows: 22 edited rows plus 607 explicitly marked hold-only rows**. There are **22 confirmed edits and 720 held slots** (41 pending raised + 105 disagreements + 574 still-missing). Rows with only settled baseline/dash outcomes are omitted. An edited row can also carry unresolved held slots. Each included row records `text`, `parent_text`, explicit status, edits, holds and read provenance; no post-convention `label` is emitted.

Raw W1 text was read directly from `collect-v3-data/run/W1/features.jsonl`. All 1,312 admitted parent labels were byte-equal to raw text, establishing exact candidate-offset correspondence without remapping. For every emitted row, the full character diff equals exactly its listed edits, each original is `-` or `.`, each replacement is U+00B7, and every unchanged UTF-8 segment is byte-identical. An independent serialized readback repeated the exact-diff, unique-ID and explicit-hold checks on all 629 rows.

Output SHA-256: `ceacc5d580cc1522dcf55ffb98b844b928de4a3ca357481b19a69dd20debf0a1`.

LQB registration is **`n1_v1_w1` → `google_raw_w1`**, an exact-ID overlay with raw `text` inheritance outside this file. `google_raw_w1` binds the complete frozen W1 feature-file hash and reads only `text`. The frozen **truth_v1_1** benchmark and its training flags were re-scored using the existing scorer. **Zero edited rows overlap truth**. The 103 tier-B separator items retain **33 errors**, classified as **in-sample** for N1 under the scorer's existing `n1_*` contamination rule; there are zero eligible paired separator headline items. No held-out separator improvement or new glyph truth is claimed. [Re-score](../../../../artifacts/n1/n1w1/r3/finalization/f2_lqb_rescore.json).

Evidence: [manifest](../../../../artifacts/n1/n1_v1_w1_manifest.json), [SHA sidecar](../../../../artifacts/n1/n1_v1_w1.sha256), [receipt](../../../../artifacts/n1/n1w1/r3/finalization/N1W1F2_RECEIPT.json), [per-row verification](../../../../artifacts/n1/n1w1/r3/finalization/f2_row_verification.json), [replacement decisions](../../../../artifacts/n1/n1w1/r3/finalization/decisions.jsonl). Receipt and output both have SHA-256 sidecars.

Reproduce offline with `scripts/numerics/n1w1_r3_finalize.sh`, then `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B -s scripts/numerics/n1w1_f2.py`. The second command preserves an existing unfilled matching sheets2 template and refuses to overwrite completed lead work.

N1W1F2 READY: contexts valid 20/44; agreed raised 63 (new beyond the 22: 41); n1_v1_w1 rows 629 edits 22 holds 720 sha256 ceacc5d580cc1522dcf55ffb98b844b928de4a3ca357481b19a69dd20debf0a1; new raised sheets 7


## N1-W1-F3: final 63 lead-confirmed edits (18 October 2026)

This section supersedes F2's pending status. The [lead rulings](N1W1_LEAD_RAISED.md) confirm all 22 original cells and all 41 replacement-read cells. Both review templates are filled with `pixel_checked: true` and the raw Google line with the individual confirmed slot replaced by U+00B7. Crop and sheet hashes match the bound indexes. No fresh glyph reading was performed.

The final [overlay](../../../../artifacts/n1/n1_v1_w1.jsonl) has **629 rows: 63 edited rows and 566 hold-only rows**, with **63 edits and 679 held slots**. A total of 582 rows carry holds, including 16 edited rows. Edited documents: `daec83cb9a364cd1`, `ee37bc488988f1bd`. Every included row was independently read back and compared directly with W1 raw Google `text`: its character diff equals exactly its listed edits, and all untouched UTF-8 segments are byte-identical. Settled baseline/dash-only rows are omitted.

Output SHA-256: `94fb67c1aab9f2ec3bf5d47bc36508b7e700508cd27391f70ebfc26f8d73230e`.

LQB re-registration is **`n1_v1_w1` → `google_raw_w1`**, retaining raw-text inheritance. The existing scorer re-scored frozen `truth_v1_1` and its flags. Zero edited rows overlap truth; all 103 separator truth items remain in-sample, with 33 errors and zero eligible paired separator headline items. No held-out improvement is claimed. The [pending record](../../../../artifacts/n1/n1_v1_w1_pending.json) is resolved, retaining the 41 completed rulings and index binding.

Evidence: [manifest](../../../../artifacts/n1/n1_v1_w1_manifest.json), [output SHA](../../../../artifacts/n1/n1_v1_w1.sha256), [F3 receipt](../../../../artifacts/n1/n1w1/r3/finalization/N1W1F3_RECEIPT.json), [per-row verification](../../../../artifacts/n1/n1w1/r3/finalization/f3_row_verification.json), [LQB re-score](../../../../artifacts/n1/n1w1/r3/finalization/f3_lqb_rescore.json).

Reproduce locally with `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B -s scripts/numerics/n1w1_f3.py`. The isolated interpreter avoids incompatible user-site SciPy. Network calls are disabled by the materialiser; no readers, browser/computer-use, or `.git` writes were used.
