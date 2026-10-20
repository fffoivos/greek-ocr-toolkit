# SEG-CP8a: ASTRA-SEG2 CP8 plan items 1 and 2 (gpt-6.1-sol, medium, network OFF, no reading)

**Authority:** `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SEG2_review_1.md`, CP8 plan **items 1 and 2, exactly as written**. Read the whole review, especially F3 and its withdrawal/corruption regressions. Items 3–7 wait for the owner's decision on the population geometry run; do no item 3–7 work.

**Constraints:**
- **Do not rewrite history** on sol/recut-v1; ASTRA-SEG2 reviewed a clean checkout of aa3d9067. New commits only.
- **Do not change the accepted screen decisions.** Any change requires separate review and the fresh-gate rule.
- No publish actions; the live run root is read-only (a BSB collector run is live).
- The freeze files stay present. `CP5_verification.json` is restored from its .gz; declare the hash-checked restore procedure, as item 1 asks.

## Item 1: close the evidence package
- Commit r2 B's original answers, mapping, controls and scan (`seg/cp7/r2/…`, `sol_packs/segcp7r2_b/r1`, copied to the repo as evidence).
- Bind the lead's per-row adjudications: `seg/cp7/r2/LEAD_ADJUDICATION_r2.json`, committed, with crop shas and the coordinator ruling (ii).
- Regenerate the final screen/union matrices from those overrides, and keep the raw-reader matrices separately. Account for every flagged, unreadable or ambiguous entry (the 43 from CP7d, and CP7b's 28).
- **Required:** raw mapping 100/100, controls 10/10, canonical scans 0 violations, and **final 2 FP / 0 FN reproducible from the package**. The 2 FP are explicitly accepted, not relabelled.

## Item 2: one evaluator, one run identity
- Route the standard text/metadata rules, merged, neighbour, axis/crossing and fail-closed geometry through **one qualified function**, used for both qualification and replay. Include the non-gating `edge_clip_candidate` in the row ledger, not in DROP.
- **Bind everything in one application manifest/hash** referenced by every output: the transitive code, tables, codec / Serbian / lookalikes, ownership params, proxy params, dependencies, truth/adjudication, qualification.
- Prove **per-row parity** against all frozen witnesses and both committed draws (r1, r2). Allow only explicitly documented qualification/schema additions.
- **Implement and pass F3's withdrawal/corruption regressions** before the stager is used.
- **Note:** ADMW2 (`docs/records/briefs/ADMW2_w2_gazette_admission.md`) wrote `build_release_admission.py` and W2/Gazette/W1-screened outputs just before this. Make that builder call the single evaluator, re-run it, and confirm that the W2/Gazette/W1-screened outputs are **identical** (or explain every delta).

Write `seg/CP8a_RECEIPT.md` and the commit list. The last line must be exactly:
`SEG-CP8a: done | item1: package closed (r1 TP4 FP2 FN4->adjudicated, r2 final FP2 FN0 reproduced) | item2: evaluator <module> manifest <sha> | parity witnesses <a>/<b>, r1 100/100, r2 100/100 | F3 regressions pass | ADMW2 outputs identical: yes/no (<deltas>) | tests: <n> passed`
