# SF7 audit Opus preparation — OC1 + OC2

Built 19 October 2026, offline. **BUILD ONLY: zero reader launches, zero Opus reads, zero model invocations, zero network calls, zero `.git` writes.** Both assigned answers.jsonl files are empty. Reads await the owner's go.

## Scope reconciliation

The saved audit state contains **30 pending lines, 32 unresolved edit heads**. OPUS_PENDING.md supplies 23 lines / 25 heads (21 lowercase breathing, four subscript). Contrary to the brief's description, the seven remaining unresolved Sol lines are **three capital breathing heads plus four lowercase accent heads**. Routing, lead_queue.jsonl, score.json, the capital keys and AU1D_HANDOFF.md agree on this distinction. There are no seven unresolved capital heads to list. All seven genuinely unresolved heads are included, so the package completes the intended 30-line coverage without upgrading missing or VOID observations.

| Audit line | Unresolved head | Route / reason |
|---|---|---|
| RB7-027 | `RB7-027:13:accent` | Sol-accent; VALID initial accent context; required reread missing |
| RB7-032 | `RB7-032:24:accent` | Sol-accent; VALID initial accent context; required reread missing |
| RB7-053 | `RB7-053:0:breathing` | Sol-capital; capital context VOID three times |
| RB7-055 | `RB7-055:6:breathing` | Sol-capital; capital context VOID three times |
| RB7-065 | `RB7-065:17:breathing` | Sol-capital; capital context VOID three times |
| RB7-067 | `RB7-067:20:accent` | Sol-accent; VALID initial accent context; required reread missing |
| RB7-076 | `RB7-076:14:accent` | Sol-accent; VALID initial accent context; required reread missing |

The recorded 70/70 is the resolved Sol-only **line subset**, not a claim that every accent head is resolved. The merger preserves 75 scored accent heads, including scored heads on mixed/pending lines, and asks Opus for exactly the remaining 32 of 107 released edit heads. All four anchor heads are asked on every card; only preregistered released edit heads enter precision.

## Assigned folders and custody

Reader 1: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/sf7_audit_opus/r1/`

Reader 2: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/sf7_audit_opus/r2/`

Each folder contains cards.jsonl, img/, README.md, answer_schema.json and an empty answers.jsonl. There are **36 cards per folder: 32 targets + four controls (11.1%)**. Reader 1 uses seed 20261019; reader 2 is the exact reverse of the complete manifest, including the shuffled controls. IDs are opaque. Cards carry a full native line with a red outline around the target, a uniform 3× LANCZOS word crop, unmarked BASE text, anchor index, independently shuffled BASE-derived options, and literal/unreadable alternatives. The schema requires breathing, accent, diaeresis (dialytika), subscript, readability, ownership, confidence and note; every head allows unknown. The full-line outline changes only its border pixels; the word zoom stays unobscured. Target geometry uses the saved recogniser-aligned slot evidence, not a new OCR run or a mark-truth read.

Private keys and the canonical resolver-compatible deck live only in `artifacts/sf7_rc1/audit/opus_keys/`. The assigned folders contain no Google/released text, source IDs, audit IDs or sampling strata. Option words are constructed from BASE text rather than released marked words. Controls reuse lead-pixel-verified T2/T4 evidence; no control truth was newly adjudicated. The selected two-letter controls use a blank full-height inter-letter projection to place the target outline; their print truth remains the upstream verified truth.

| Source deck | Original manifest position | Source card | Document |
|---|---:|---|---|
| T2 | 14 | `6f0f214cc4ba6ef85f6fdd56` | `parliament:f74236d5` |
| T2 | 110 | `b2f19a610706c0d0096a7d21` | `openarchives:a0822ede` |
| T2 | 250 | `706991e457b31f823ef36ecd` | `bsb11367220` |
| T2 | 282 | `647194b3651d56fadeaaf0c2` | `openarchives:57ecc6b2` |

All four controls have `lead_verified: true`, are document-disjoint from **all 100 audit lines**, and exclude T2 #61. Original source/verification hashes are recorded in opus_keys/control_sources.json.

The leak scan uses the vendored adjudicate.deck.leak_scan over **all assigned folder contents**, filenames and PNG metadata, supplemented with every audit ID, line ID and document and private-field names. Images are re-encoded without metadata, named by content hash, and no symlinks are admitted. Both scans pass; every assigned file, including empty answer files, has a SHA-256 in opus_keys/build_receipt.json. This is a data-leak check, not an OS sandbox: printed pixels can intrinsically identify their source.

**Opus readers are Claude subagents. Isolation is by folder plus the explicit file-allowlist instruction used in T2/T4. The Codex rollout scanner does not apply.** No Codex scanner result is fabricated or required for these Claude reads. [READER_PROMPT.md](../../../../artifacts/sf7_rc1/audit/READER_PROMPT.md) contains the exact lead instruction, with only assigned absolute folder and count substituted. Each initial count is 36. It permits only the manifest/schema/README, named PNGs, writing/coverage-checking the reader's own answers.jsonl, and local zoom helpers. Readers transcribe ink, including misprints, independently; they never see keys, previous answers or lead reports.

## Pinned implementation

- Builder: `scripts/labelfix/sf7_opus_prepare.py` (write-once; refuses existing reader/deck trees).
- `scripts/labelfix/r2_cards_resolve.py` is a byte-identical copy of the R2C2 upstream resolver, pinned against its original path and SHA-256.
- `opus_keys/vendor/adjudicate/{deck.py,protocol.py,score.py}` are byte-identical snapshots from `greek-ocr-toolkit-cleanup/greekocr/adjudicate/`, each with source and vendored hashes in sources.json. The minimal package initializer is local. The builder and scorer use deck.leak_scan; the protocol snapshot documents custody, independent readers and UNKNOWN. No checkout or source tree was modified.
- The scoring merge uses a self-contained unweighted document-cluster percentile bootstrap, consistent with the existing AU1 fixed-sample audit estimator: 10,000 seeded draws, whole documents resampled, all their scored lines retained. The vendored general weighted score module is preserved for provenance but is not imported (the local SciPy binary is incompatible with the x86 Python/Pillow runtime). No package installation or environment change was made.

## Final score workflow (after owner-authorized reads)

```bash
bash artifacts/sf7_rc1/audit/FINAL_SCORE.sh
```

The script never launches a reader. With both real answer files empty it emits a preparation snapshot: **70 CORRECT, 0 INCORRECT, 30 PENDING**, final precision/bar verdict null. Each invocation defaults to a fresh timestamped `audit/final_scores/` directory; existing outputs cannot be overwritten. `--out` selects a fresh explicit directory. The historical audit score, lead queue and VOID attempts remain unchanged.

When answers exist, the pinned R2 resolver validates exact coverage/order and gates controls first. The R2 limit is **at most one control error per reader batch**; two errors fail the gate. Invalid non-control votes are excluded per card and do not void the entire batch. Both original readers must pass; a third reader cannot rescue a failed initial gate. UNKNOWN is retained. Two agreeing votes resolve; disagreements or invalid votes receive a third independent reading and require two agreeing votes out of three.

A disagreement run generates only the affected target cards **plus the same four planted controls**, with fresh option order. Resolver private maps stay under that run's `resolution/tiebreak/private/`, outside the reader folders. The lead-ready blind folder is copied write-once to `scratchpad/sf7_audit_opus/r3/`, receives neutral instructions and an empty answers.jsonl, and gets a separate leak/hash receipt. Its count is affected targets + 4. This staging has been tested synthetically; no real tiebreak or third reader is launched during preparation. Use the same READER_PROMPT.md substitutions for that folder and its actual count.

After an authorized third read, resolve into another fresh output directory:

```bash
bash artifacts/sf7_rc1/audit/FINAL_SCORE.sh --reader3 /absolute/path/to/sf7_audit_opus/r3/answers.jsonl
```

The merge maps psili/dasia to the release's smooth/rough and present to subscript/dialytika. It compares each resolved **prespecified edit head** with the released label. Unmarked-anchor ownership is null. A line is CORRECT only when every scored edit head is right; any unresolved head keeps its line PENDING, even if another head is known wrong. Pending lines are reported separately, excluded from the resolved-subset precision and interval, and never imputed. Final precision uses exactly 100 lines and the ≥83/100 gate is populated only when all lines resolve and the reader gates pass. Per-head, per-edit-kind and per-line-kind counts are included. The document-cluster interval is labelled as either resolved-subset or full-audit; a degenerate boundary interval is explicitly flagged.

The preregistration additionally requires no line class worse than sf6 beyond two lines. This package reports the requested precision bar and kind counts; it does **not** infer that separate historical class comparison or authorize release. `full_preregistration_pass` remains null pending that comparison. An Opus agreement result is print truth for the targeted observations, not a release instruction.

## Validation

```bash
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B artifacts/sf7_rc1/audit/check_final_score.py
```

**13 synthetic tests passed**: all agree (100/100); one disagreement → a fresh-option five-card tiebreak → 2-of-3; two control errors fail the gate; one error remains within the R2 allowance; UNKNOWN stays PENDING; an invalid vote affects only its card and triggers a tiebreak; ownership is null when unmarked; exact reverse order and initial leak/empty-answer checks; a wrong head makes its line incorrect; missing coverage fails assignment validation; third-reader control failure blocks the gate; tiebreak copying is blind and preserves existing answers; unresolved wins over a known error on the same line. The real empty-answer scoring path and shell syntax also pass. Synthetic answers/results live only in temporary test directories, which are removed; test_receipt.json records the code hashes and result.

Receipts: `opus_keys/build_receipt.json`, `opus_keys/sources.json`, `opus_keys/control_sources.json`, `opus_keys/test_receipt.json`, and `opus_keys/completion_receipt.json`. No images were opened for model adjudication during preparation.

OC READY: cards 32 (lines 30, heads 32), controls/folder 4, folders r1/r2 leak-scan pass, reader prompt artifacts/sf7_rc1/audit/READER_PROMPT.md, FINAL_SCORE tests 13 passed
