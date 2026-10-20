# SEG-CP4c: apply the coordinator's two rulings to close CP4 (gpt-6.1-sol, medium, network OFF)

**Context:** the SEG-CP4 review 2 (`docs/records/reviews/SEG_CP4_review_2.md`) left B1 and part of H1 open. The coordinator ruled on both, as the lead recommended. Implement exactly these rulings; do not reopen anything else.

1. **`geometry_unavailable` (fail closed).**
   - A row whose geometry cannot be measured (invalid/inconsistent planes, inverted/invalid rows, missing or stale binding, unresolved target) is **not admitted**, under the new rule id `geometry_unavailable`. This is the same "drop when undecidable" logic as `lookalike_only_word`.
   - Add the rule to `greekocr.harvest.admission`: bump the version; the schema is unchanged apart from the rule id.
   - The composed admission decision for `nlg--6146c0455e0103d2--s001-l0006` is therefore DROP. Report D under the composed decision (expected 9/9) and also the measured-detection number (8/9), separately and honestly.
   - Unavailable must still **never** be reported as a measured detection or a verified keep. It is its own counted status.
   - Tests: an inconsistent-planes row → `geometry_unavailable` fail; an inverted-row target → fail; a valid row is unaffected.
   - CP7 will report rows lost to this rule per source × class. Add the counting hook now; it is not run on admission files here.
2. **Reclassify witness c068** (`gazette_modern--2e613d9290dd13d4--s000-l0209`).
   - Through the ledger's own builder (`seg/freeze_truth.py`), move it from required C1 merge witness to **"label-error witness, non-gating"**.
   - Record the reasoning verbatim: "The card's verdict is a label error (label appends 'μένης αργίλλου' from the next line, which is only partly inside the crop). The neighbour word is clipped (token box 216–257×1233–1254 vs crop 217–715×1211–1249); under the owner's whole-word standard a clipped neighbour word is not a drop reason. Coordinator ruling 18 Oct."
   - Re-freeze the ledger with a new sha. The C1 denominator becomes 6.
3. **Rerun every CP3 and CP4 acceptance number** on the re-frozen ledger: KEEP 22/22, C1 6/6, gallery 6/6, planted FP 0, D 9/9 composed, fragment controls, short native 3/3, unresolved required witnesses.
4. **Collector known issues.** Write `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/KNOWN_ISSUES.md` (docs only; never touch `collect_v3/` code, because a live materialize imports it). Two entries, each with evidence paths and counts from the CP3b/CP4b receipts, marked "for a later fix":
   - cached foreground/label planes inconsistent on ≈ 4% of cached pages;
   - 181 inverted rows (bottom < top).

Update `seg/CP4_RECEIPT.md` (with a rulings section) and `seg/CP4_COMMIT_LIST.json`, and add a separate commit group for KNOWN_ISSUES.md in the sol-collect checkout. The last line must be exactly:
`SEG-CP4c: done | geometry_unavailable rule: added | ledger sha: <sha> (c068 non-gating) | KEEP 22/22 | C1 <x>/6 | gallery <y>/6 | D composed <a>/9 (measured <b>/9) | fragment union <c>/<n> | short native <d>/3 | unresolved required (non-unavailable) <e> | known issues: written | tests: <n> passed`
