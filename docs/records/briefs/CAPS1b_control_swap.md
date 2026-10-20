# CAPS1b: swap one control, then close the CAPS1 packs (gpt-6.1-sol, medium, network OFF, mechanical)

This continues CAPS1 (`docs/records/harvest/recut_v1/w1_masked/caps1/`).

## Lead rulings
1. **Control pixel review** (the lead read `caps1_controls_sheet.png`):
   - 9 controls approved: c057, c009, c013, c026, c046, c041, c029, c072, c035.
   - **Replace C1 card c058** (context c2). Its crop has letter fragments of both neighbouring lines at the edges, so its crop_ok=y reference is borderline.
   - Pick the next candidate in the same seeded order that has letters=y, crop_ok=y and an **empty** reference detail. Re-render the contact sheet with the replacement marked, to the same path, for a second lead look at **that one control only**: write it to `caps1_control_swap.png` beside the full sheet.
2. **Closure scan: use the proposed local adapter.** Apply the Sol-reading scanner's closure checks unchanged in substance:
   - no private fields, source ids or line ids;
   - no keys or truth;
   - no links or hardlinks;
   - originals intact;
   - only `answers.jsonl` and `zoom/**` may be added.

   Drop only the two format assumptions: RGB-only images, and a reversed duplicate reader. Our crops are byte-exact grayscale, and the two contexts hold disjoint cards. Record the adapter, its diff against the reference and the reason in the README. Sol-reading files stay untouched.

## Then
Rebuild c2 with the swapped control (the order is re-seeded for c2 only; c1 is unchanged) and rerun all tests (14/14). The last line must be exactly:
`CAPS1b: done | swapped c058 -> <card> | closure: clean (adapter) | tests: <n>/<n> | launch lines ready`
