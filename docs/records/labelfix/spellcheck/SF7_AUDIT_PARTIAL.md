# SF7 AU1 partial audit — build and lead-run results

Status: PARTIAL; 4 reader contexts run. Release A, uniform 100-line frame, seed 20261017. No full-audit result or pass is asserted. AU1C rescans, when present, supersede original scanner verdicts while preserving original receipts. Current bound scanner: v4.5.5.

Routing covers all 107 released edits in all 100 frame lines. Sol lowercase accent: **79 heads**; Sol capitals: **3 heads** (3 breathing edits, no capital accent edits); Opus later: **25 heads** (21 lowercase breathing and 4 subscript; no dialytika). Each changed head has its own entry in `artifacts/sf7_rc1/audit/routing.json`; combined-letter edits stay separate. Capital cards ask both heads, but only changed heads count in the audit.

Initial packs: **2 contexts**, 82 bed cards plus 20 verified controls. Each context is at most 90 bed cards + 10 controls. Opaque IDs, seed-shuffled order, clean RGB content-hash PNGs, full native line strips and 3× word zooms; the accent pass also has an 8× letter zoom. The grave prompt's required bare letters identify the target; no marked release or Google text is exposed. Capital option mappings are independently shuffled. Keys, source bindings and reports stay outside pack root.

Packs: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/sf7_audit`. Prompt files are byte-for-byte copies of HANDOVER grave.md and CQ1 cap1.md. Accent controls reuse lead-reviewed SR-G1 Lekythos/Kosmopolis pixels (all 58 SR-G1 items were lead-reviewed; NLG controls excluded); capital controls use only CQ4 verified=true entries. Saved recogniser slot spans and physical body/mark bounds locate bed targets; no inference was run during building. Full native height and horizontal overhang are retained. Control provenance and native hashes are in private keys. Build input hashes are in build_receipt.json.

Lead commands (from any cwd):

```bash
bash /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/artifacts/sf7_rc1/audit/RUN.sh
bash /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/artifacts/sf7_rc1/audit/REREAD.sh
bash /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/artifacts/sf7_rc1/audit/SCORE.sh
```

RUN binds the canonical scanner from the live HANDOVER hash, copies exact bytes and records scanner/dependency hashes; a mismatch stops before probes/readers. Each reading uses gpt-6.1-sol, medium, network off, web disabled, apps/plugins/multi-agent disabled, project documents disabled, cwd confined to its pack. Sequence: weekly limit probe → read → canonical rollout scan → strict answer validation and controls gate (≤1 wrong control) → probe → receipt. It reads the codex 10080-minute bucket, refuses ≥78%, and stops at ≥80%. Failures after read start are recorded VOID and excluded. Original attempts cannot be overwritten. Live budget: [26.0, 26.0, 26.0, 26.0, 27.0, 27.0, 27.0, 27.0].

REREAD reuses staged fresh contexts after integrity and binding checks; if none exist it builds them. It runs any staged initial retry first, builds its triggered re-read if necessary, then runs the staged re-reads. Existing failed attempts are preserved and require fresh contexts. On capitals, every breathing-only answer (conservative trigger when preposed ink is not independently classified) and every unreadable tuple is re-read; agreement keeps the reading, disagreement or unreadable goes to the lead queue. Every lowercase accent mismatch, unreadable or low-confidence flag is re-read and still requires a human eye. `REREAD.sh --build-only` builds/checks without readers. Any missing/VOID context remains unresolved. For a human decision, supply `lead_review.json` keyed by head_id with `verified: true`, `reviewer`, `reading`, and `note`; SCORE validates it. Opus cards are listed only and are not built.

Current partial result: **70/70** resolved Sol-only lines (1.0). Sol-only eligible lines: 77; unresolved: 7. **23 lines have Opus PENDING heads**, counted separately and never imputed. All-head line correctness requires every changed head; on a partial line, all Sol-scored heads must be correct, but Opus-pending heads prevent a full verdict. Per-head and per-line records, plus Sol-only subset correctness for mixed lines, are in score.json. A 10,000-draw document-cluster bootstrap is reported once the resolved Sol-only subset exists; this is descriptive and does not qualify the full audit. Final preregistered gate remains ≥83/100 plus the line-class constraint; both await the complete audit, including Opus.

Scanner at build: HANDOVER `7b3647162c527426225f26b3c8eba494fb89b52302002594eb0b8246e5642f4e`, file `7b3647162c527426225f26b3c8eba494fb89b52302002594eb0b8246e5642f4e`. MATCH

Validation: pack closure, PNG hashes/metadata, no links, strict public fields, controls provenance, input coverage and prompt byte equality are checked by validate.py. Reader execution remains with the lead.
