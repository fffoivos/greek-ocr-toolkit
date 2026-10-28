# ASTRA-CP3B-r2 — scoped wave-2 prelaunch re-review

**PASS scoped prelaunch review: H1 is cleared; no BLOCKER or HIGH remains.**

Reviewed firsthand, read-only, on 21 October 2026. No files written, jobs submitted or background jobs started. Certification covers the reviewed nine-run launch from prep03.

## Findings — most severe first

1. **MEDIUM — review 1 finding 2 retained for CP4.** Duplicated breathing in sf7 row `lekythos--3bfc4a385d61b883--s001-l0106`. Unchanged; not reopened.

2. **MEDIUM — review 1 finding 3 retained for CP4.** Residual raw OCR `Χρξώστες` instead of `Χρεώστες` in `gazette_modern--dacf995fd419bebd--s000-l0113`. Unchanged; not reopened.

   Both remain as documented in [review 1](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next/docs/programme_20261019/SIMPLIFICATION/wave2/ASTRA_CP3B_review_1.md).

3. **LOW — residual handoff status and cap wording is stale.** [REVIEW_INPUTS.md:9](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-e4w2v4/docs/ocr_program_2026-10-06/e4_wave2/REVIEW_INPUTS.md:9) still says the fix awaits commit/preparation/smoke; [HANDOFF.md:43](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-e4w2v4/docs/ocr_program_2026-10-06/e4_wave2/HANDOFF.md:43) retains the 150-hour cap. An operator could follow obsolete state. Refresh these references to prep03, smoke 3714153 and the owner’s **350 requested GPU-hour** cap. This does not block the verified launch.

## Cleared items

**H1 — preregistered numerics preserved.** I read both complete reference views directly on Clariden and applied the deployed evaluation code:

| View | Unique reference rows | E3 numeric rows | Numeric reference atoms | Census numerics_tables |
|---|---:|---:|---:|---:|
| `v2_test` | 42,038 | **221** | 9,103 | 0 |
| `v2_test_full_coverage` | 43,883 | **221** | 9,103 | 0 |

The numeric ID sets are identical. The [fixed reporting assignment](/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr-e4w2v4/bench/e4_wave2.py:746) preserves `by_category['numerics']` and adds `numerics_tables` separately.

Using the deployed summarizer, exact census-category reporting block and production verdict function, an in-memory controlled example containing all 221 numeric references plus category witnesses returned **`H7_ADD_CONFIRMED` and `H7_ADD_CORR_CONFIRMED` in both views**, with seeds 0/1/2. Restoring zero numeric support made the same example pending. These are decision-path checks, not model results.

**Change scope.** The `ceb4a00 → e0735c1` diff changes one executable assignment, adds regression tests and updates documentation. The verdict function, preregistration, trainer, recipe and input builder are unchanged.

**Committed/deployed identity.** Independently compared **573/573 packaged source files** against commit `e0735c125c4d344fd46caf3045a7567e8c140ef5` and live deployment: **zero mismatches**. Archive payload verification also passed.

- Manifest SHA256: `9c20f520fb4462c657a4f23bb7b0452ded9ddcd2a8c5a130965b40bffabd150b`
- Archive SHA256: `0f6d505719e676e6dc523c84f011abdf8340bd7e3f4cdb0cbc884f727f866cc7`

**Inputs unchanged in substance.** Live bound-input SHA256 is `3af51068d7f80aa1fc4b0460fd7a1b87b00ed2c2ad5ae37d3a224375660dbb61`. All three live inventory hashes match review 1’s pins. Independent control recount: **196,227 rows / 196,227 unique IDs**. Bound-configuration differences are deployment-root substitutions and dependent source/parent hashes. Review 1’s identity, overlay and exposure conclusions remain carried forward.

**Smoke exercised the fixed evaluation path.** Live saved accounting records **3714153 COMPLETED 0:0, 1,225 seconds**. Verified all three arms’ four-update completions, **6 checkpoint hashes**, and **30 prediction files × 4 rows** with checkpoint/data bindings. The node binding pins the fixed reporting code and real evaluator; aggregate output contains the new separate category, is complete, and the combined gate is `DONE`. Live log SHA256 matches `f5d841d51c8dfccf608e1b14f5c3c3f638b643cba18c98555fff191feb05cf29`.

Smoke remains `SMOKE_ONLY`; its samples contain no numeric rows. Numeric support and production verdict behavior were checked separately above.

**Budget passes.** Recomputed from the captured ten-allocation ledger, including failed attempts:

| Requested GPU-hour accounting | GPU-h |
|---|---:|
| Spent through smoke 3714153 | 1.180833 |
| Production reservation: 3 allocations × 3 GPUs × 12 hours | 108.000000 |
| Maximum reviewed total | **109.180833** |
| Headroom below owner’s 350 cap | **240.819167** |

Original LOW 4’s superseded v3 instructions and incorrect aggregate-exclusive wording were removed; the remaining documentation qualification is logged above.

VERDICT: PASS scoped nine-run prelaunch; H1 cleared, MEDIUM findings retained for CP4 | BLOCKERS: 0 | HIGH: 0