# AU1C — scanner v4.5.5 rebound, rescanned, ready for reads

Canonical scanner **v4.5.5**, SHA-256 `e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1`, matches the live sol-reading `HANDOVER.md`. `scanner_binding.json` pins it, HANDOVER and all three dependencies. `au1c/rebind_receipt.json` records the explicit old-to-new binding; `au1c/scanner/` contains the exact hash-checked canonical bytes. No scanner fork was made. Original build receipts retain their historical v4.5.2 identity.

## Rescan verdicts

| AU1B context | Original v4.5.2 | AU1C v4.5.5 | Controls |
|---|---|---|---|
| `accent_initial_001_au1b` | VALID | **VALID**, zero scanner violations | 1/10 errors; passes ≤1 gate |
| `capital_initial_001_au1b` | VOID | **VOID**, 13 scanner violations | Excluded; scanner failed |

Capital findings: three unsupported view-loop findings at records 17, 45 and 64, plus ten unmatched image-provenance findings at record 79. Exact findings and provenance are in `au1c/capital_initial_001_au1b.scan.json`; accent is in the adjacent scan file. These are scanner adjudications, not new readings. The rollouts' hashes were checked against their original read receipts before scanning.

`au1c/rescan_receipts.json` supplies the effective verdicts to the scorer. Original AU1B receipts, scans, answers, scanner copies and rollouts remain unchanged; effective receipts bind their original receipt hashes, rollout hashes, new scan hashes and canonical binding. The valid accent answer snapshot is separately hashed. No capital answers are admitted.

## Fresh staged contexts

| Context ID | Role | Targets | Verified controls |
|---|---|---:|---:|
| `accent_reread_001_au1c` | Fresh accent re-read | 4 | 10 |
| `capital_initial_001_au1c` | Fresh capital initial retry after VOID | 3 | 10 |

The four accent targets are `RB7-027:13:accent`, `RB7-076:14:accent`, `RB7-032:24:accent`, `RB7-067:20:accent`. The capital retry targets are `RB7-065:17:breathing`, `RB7-053:0:breathing`, `RB7-055:6:breathing`.

All 27 public item IDs are fresh and disjoint from prior packs. Exact isolated pack paths, key and manifest hashes, target head IDs and public IDs are in `reread_contexts.json` and `au1c/context_build_receipt.json`. The earlier `accent_reread_001` pack and its scanner-blocked receipt remain preserved; its old selection is archived in `au1c/previous_reread_contexts.json`. New packs contain no answers, and neither new context has an attempt directory.

`REREAD.sh` now reuses the integrity-checked staged packs, runs the capital initial retry first, builds a fresh capital re-read if its valid answers trigger one, and runs the staged re-reads. It stops on a failed attempt or budget boundary and preserves existing attempts. Accent flags still require human review even after a re-read. Model remains `gpt-6.1-sol`, effort medium, network OFF, web disabled, with the existing blinding, control and weekly budget gates. A failed future attempt needs a fresh context rather than overwriting its receipt.

## Partial score and Opus queue

`SCORE.sh` was run on the v4.5.5-effective VALID evidence: **70/70 resolved Sol-only lines (100%)**. Of 77 Sol-only eligible lines, seven remain unresolved: four accent flags and three capital lines. Another **23 lines / 25 heads** remain Opus-pending and are excluded from this denominator. The all-Sol subset is resolved on 72 lines, including two mixed lines; those mixed lines retain PENDING status. This is a partial score, not a full-audit pass. `score.json`, `lead_queue.jsonl` and `docs/labelfix/spellcheck/SF7_AUDIT_PARTIAL.md` contain the current results.

`OPUS_PENDING.md` lists all **23 line IDs and audit IDs, with all 25 pending head IDs, slots, types and released labels**, awaiting the owner's go. No Opus packs were built.

## Offline validation and next command

Passed: `validate.py`, `check_scoring.py`, `check_au1c.py`, shell syntax, and `git diff --check`. `AU1C_validation.json` records binding, preserved original receipts, rollout/scan hashes, fresh-pack closure/native hashes/controls/disjoint IDs, valid-observation inclusion, and an offline simulated retry → capital re-read → scoring path with VOID/budget-stop checks. `REREAD.sh --build-only` and `SCORE.sh` were executed successfully. Both scripts remain executable.

AU1C launched **zero reads, zero probes, zero nested Codex invocations, zero network calls**. Canonical scanning only replayed recorded confined commands offline. The last recorded weekly meter was 26% in the prior AU1B receipts; it was not refreshed in AU1C. Future reader execution probes it afresh.

```bash
bash artifacts/sf7_rc1/audit/REREAD.sh
bash artifacts/sf7_rc1/audit/SCORE.sh
```

AU1C: done | scanner v4.5.5 bound | rescan: accent VALID capital VOID | reread contexts built: 2 (accent_reread_001_au1c, capital_initial_001_au1c) | partial precision 70/70 | next: bash artifacts/sf7_rc1/audit/REREAD.sh
