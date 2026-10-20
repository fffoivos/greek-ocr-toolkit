# LF1 production finalize, benchmark 0.2 draw census_05 (20 Oct 2026, 06:55 Athens)

Draw `candidates_v3.jsonl` (0432c56f…34c2), 3,341 lines; batches W1a 576 / W2 1,242 / W1b 1,523; all crops sha-matched to the readout
`crop_sha256`. Rulings applied (coordinator, 20 Oct): explicit in_quota/overdraw_order; replacement only within the same quota_scope AND
source, else UNFILLED; attempt 3 for w2_00004, w2_00013, w1b_00008 (all VALID); vertical_turned re-read with the vertical statement
(re-read decides, first verdict kept, `prod/vertical_reread_verdicts.jsonl`).

Seal files (absolute paths in `prod/finalize.bindings.json`).

Current (v2, LF4: flagged slots paired by scope_rank; same 2,691 rows and counts as v1, 64 `replaces` changed; `LF4_REPORT.md`):

| File | sha256 |
|---|---|
| `artifacts/lf1/prod/final_list.jsonl` (2,691 rows) | `0fa4a1fe747e06dfeb9bdb4e6c1a8f3027140b4b160330c4ce07621a9315a08b` |
| `artifacts/lf1/prod/finalize.receipt.json` | `0001652776fd2e45261081bdeffd67b05749edec5a5abadd4162d3d893be6537` |
| `artifacts/lf1/prod/line_verdicts_merged.jsonl` (3,341 rows) | `a203509cbd8105f4c7aeeba04f2ecc32fcb43662a26af8a87902c12b142d12e9` |

Superseded v1 (rejected by SEAL02: slot pairing; copies in `artifacts/lf1/prod/v1/`):

| File | sha256 |
|---|---|
| `artifacts/lf1/prod/v1/final_list.jsonl` | `75fe0dbc396e57a7caa2946aa80f6aa7d85be4af8e41c7b2cef3cb8c29341ba7` |
| `artifacts/lf1/prod/v1/finalize.receipt.json` | `40ebcabbdf7b05352d2e52ae4d9a2d3132f8a641d49a05a9330ea5f1aa13660f` |

Receipt: FINALIZED, mock false, flagged 350 = REPLACED 248 + UNFILLED 102 (test 298 = 211 + 87; dev 52 = 37 + 15).
Contexts: 68 main + 4 vertical, all VALID at their last attempt; 86 attempts, 14 VOID attempts. Unresolved cards: 2 (no verdict, not OK).
Controls: main 405/408; vertical 16/20, and `candidate_vert_w1a_w2_00003` is control-flagged (3 errors: the OK, textdiff and multiline
controls called CROP_VIOLATES turned_or_clipped; horizontal controls read under the vertical statement; the errors over-flag).
Tokens 37,947,978; Codex weekly 41% → 44%.

Per-class not OK and in-quota/reserve: `artifacts/lf1/prod/final_summary.txt`. A first finalize ran at ~06:47 before w1b_00008's attempt 3
had been authorised (`run.py` refused it); its outputs were overwritten and never sent.

Scope note (Astra checkpoint 3, M1): LF1 OK does not certify diacritics; the prompt and mapper exclude marks by design, so the benchmark is
diacritics-unqualified. The 97 diagnostic mark flags (83 test / 14 dev) stay in the evidence.
