# CQ4d reading report

Replaced **23 control placements** across 16 contexts, using seed 20261017 and the 33 lead-verified controls. The seven rejected pool controls remain excluded. Every bed-item JSONL line, item order, and prompt stayed byte-identical. Only affected initial packs were rebuilt. No `.git` writes.

Attempted 18 initial and 0 re-read contexts configured for gpt-6.1-sol, medium; **18 VOID**. VOID answers were never scored. The pre/post probes, 78% refusal gate, canonical v4.4 scan and at-most-one-control-error gate remained active.

| Set | Initial slots read | Valid initial slots | Resolved | Quarantined to lead queue | Marked | Bare | Compounds |
|---|---:|---:|---:|---:|---:|---:|---:|
| W-CAP | 0 | 0 | 0 | 300 | 0 | 0 | 0 |
| Top-up | 0 | 0 | 0 | 1205 | 0 | 0 | 0 |

All 18 reader startups failed before producing a rollout or any answers. Confirmed model reads: **0**. Re-read selection is empty because no initial answer is scoreable. All 1505 selected slots are quarantined.

Slots read counts bed slots in launched initial reader contexts; re-read slots are additional. Marked means at least one printed breathing or accent; bare is negative, marked is positive. Compounds are the subset with both breathing and accent. Sampling likelihood labels are not truth.

Re-read agreement: **N/A** (0/0 triggered slots; missing/VOID re-reads stay in the denominator). Agreed unreadables remain quarantined. Re-read trigger: every unreadable and every breathing-only answer, using the preregistered conservative fallback.

Compound counts (breathing + accent):

- wcap: `{}`
- topup: `{}`

VOID contexts and causes:

- `wcap_initial_000`: reader rollout metadata missing. Reader startup log: failed to initialize in-process app-server client: Operation not permitted (os error 1).
- `wcap_initial_001`: reader rollout metadata missing. Reader startup log: failed to initialize in-process app-server client: Operation not permitted (os error 1).
- `wcap_initial_002`: reader rollout metadata missing. Reader startup log: failed to initialize in-process app-server client: Operation not permitted (os error 1).
- `wcap_initial_003`: reader rollout metadata missing. Reader startup log: failed to initialize in-process app-server client: Operation not permitted (os error 1).
- `topup_initial_000`: reader rollout metadata missing. Reader startup log: failed to initialize in-process app-server client: Operation not permitted (os error 1).
- `topup_initial_001`: reader rollout metadata missing. Reader startup log: failed to initialize in-process app-server client: Operation not permitted (os error 1).
- `topup_initial_002`: reader rollout metadata missing. Reader startup log: failed to initialize in-process app-server client: Operation not permitted (os error 1).
- `topup_initial_003`: reader rollout metadata missing. Reader startup log: failed to initialize in-process app-server client: Operation not permitted (os error 1).
- `topup_initial_004`: reader rollout metadata missing. Reader startup log: failed to initialize in-process app-server client: Operation not permitted (os error 1).
- `topup_initial_005`: reader rollout metadata missing. Reader startup log: failed to initialize in-process app-server client: Operation not permitted (os error 1).
- `topup_initial_006`: reader rollout metadata missing. Reader startup log: failed to initialize in-process app-server client: Operation not permitted (os error 1).
- `topup_initial_007`: reader rollout metadata missing. Reader startup log: failed to initialize in-process app-server client: Operation not permitted (os error 1).
- `topup_initial_008`: reader rollout metadata missing. Reader startup log: failed to initialize in-process app-server client: Operation not permitted (os error 1).
- `topup_initial_009`: reader rollout metadata missing. Reader startup log: failed to initialize in-process app-server client: Operation not permitted (os error 1).
- `topup_initial_010`: reader rollout metadata missing. Reader startup log: failed to initialize in-process app-server client: Operation not permitted (os error 1).
- `topup_initial_011`: reader rollout metadata missing. Reader startup log: failed to initialize in-process app-server client: Operation not permitted (os error 1).
- `topup_initial_012`: reader rollout metadata missing. Reader startup log: failed to initialize in-process app-server client: Operation not permitted (os error 1).
- `topup_initial_013`: reader rollout metadata missing. Reader startup log: failed to initialize in-process app-server client: Operation not permitted (os error 1).

Codex weekly: **39% → 39%** (+0 percentage points), from the first before-probe and last after-probe. Probe outputs are retained in the ledgers and `limit_probe.log`.

Truth tier: `C_sol_one_reader_reread`. W-CAP is witness-only; top-up truth is separate. No training or manifest-overlay build ran.

Final offline validation: **14 tests passed**, 68 frozen files verified, zero mismatches. Independent checks confirmed all 1505 queue identities and rechecked 1380 bed JSONL lines against the affected contexts’ pre-swap snapshots. Contact-sheet preview visually inspected.

Evidence: [execution receipt](../../../../../artifacts/cq4/execution_receipt.json), [swap receipt](../../../../../artifacts/cq4/control_swap_receipt.json), [validation](../../../../../artifacts/cq4/validation.json), [aggregate receipt](../../../../../artifacts/cq4/aggregate_receipt.json), [lead queue](../../../../../artifacts/cq4/lead_queue.jsonl), [contact sheet](../../../../../artifacts/cq4/lead_queue.png).

CQ4d READY: swaps 23; contexts run 18 (VOID 18); W-CAP resolved 0/300 (marked 0, bare 0); top-up resolved 0 (neg 0/pos 0); re-read agreement N/A; lead queue 1505; Codex 39%→39%

## Reading results

```json
{
  "scanner_sha256": "e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1",
  "preregistration_sha256": "dbac559fe9792a4f7c879f1fc7b08d03c6a82611bbb42ecce1ffd4ae31ccbebc",
  "counts": {
    "wcap": {
      "resolved": 281,
      "quarantined": 19,
      "classes": {
        "marked": 133,
        "bare": 148
      }
    },
    "topup": {
      "resolved": 1107,
      "quarantined": 98,
      "classes": {
        "marked": 387,
        "bare": 720
      }
    }
  },
  "reread_triggered": 354,
  "reread_agreed": 335,
  "reread_agreement_rate": 0.9463276836158192,
  "lead_queue": 117,
  "codex_before": {
    "weekly_used": 8.0,
    "output": "2026-10-18 07:02:44 wcap_initial_000_before weekly_used=8.0 limit_id=codex primary=8.0%/10080m reset Sat 23:40 secondary=-\n"
  },
  "codex_after": {
    "weekly_used": 28.0,
    "output": "2026-10-19 06:54:17 cq7_ddd097b22ed8_b02_r2_after weekly_used=28.0 limit_id=codex primary=28.0%/10080m reset Sat 23:40 secondary=-\n"
  },
  "cq6_amendment1a_binding": {
    "original_preregistration_sha256": "dbac559fe9792a4f7c879f1fc7b08d03c6a82611bbb42ecce1ffd4ae31ccbebc",
    "current_preregistration_sha256": "7cb5a6fb53a4b5c35a55e85cce9a14961570b4a880cc79a6e4f227b9149f6964",
    "amendment": "1a",
    "timing": "after existing CQ4 reads; consequence note only",
    "authority": "CQ6 coordinator instruction; HANDOFF_20261018_spellcheck.md §2"
  },
  "cq7": {
    "scanner_version": "4.5.5",
    "scanner_sha256": "e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1",
    "ledger_sha256": "8321197f806c1808df60d8b13440ee446d84811a8fd45e70b43f9bcc621f3405",
    "accepted": 98,
    "quarantined": 98,
    "positives": 98,
    "codex_before": {
      "weekly_used": 27.0,
      "output": "2026-10-19 06:34:57 cq7_ddd097b22ed8_b00_r1_before weekly_used=27.0 limit_id=codex primary=27.0%/10080m reset Sat 23:40 secondary=-\n"
    },
    "codex_after": {
      "weekly_used": 28.0,
      "output": "2026-10-19 06:54:17 cq7_ddd097b22ed8_b02_r2_after weekly_used=28.0 limit_id=codex primary=28.0%/10080m reset Sat 23:40 secondary=-\n"
    },
    "reader_runs": 0,
    "network_used": false
  }
}
```
