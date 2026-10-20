# ADM5c: Serbian codec extension + class rule variants in the standard admission tool (gpt-6.1-sol, medium, network OFF)

These are coordinator rulings after ADM5b (cd9d6ad2). The owner has been informed.

1. **Serbian: admit.**
   - For `serbia` rows, the tool uses the **Serbian-extended codec**: codec v2 plus the collector's Serbian extension atoms (њ ћ љ џ ђ ј and the rest).
   - Find the collector's extension read-only in `~/Projects/greek-ocr-toolkit-sol-collect/collect_v3/` (the `serbian_codec` path) and reproduce exactly the same atom list.
   - List those atoms as expected scripts/characters for that source in the expected table.
   - Record the atom list and its sha256 in every receipt (`serbian_extension_atoms`, `serbian_extension_sha256`).
2. **Class rule variants** in the expected table; all script, foreign-char, mixed-word and language checks stay for both classes:
   - **numerics_tables:** replace short_line and nonletter_frac with **"≥ 4 digits and ≥ 60% of characters are digits or allowed separators (. , · - / space)"**. Use rule id `numeric_shape` for this failure.
   - **headings_caps:** short_line becomes **≥ 4 letters**; keep nonletter_frac.
   - Bump `tool_version` and the expected-table sha.
3. **Rerun:** the W1 admission (`w1_originals_v3`) and the v2 census, with the same schema. Report the new pass counts per source × class next to the ADM5b counts.
4. **Tests:**
   - a Serbian line with њ/ћ passes, and the same characters in a Greek source still fail;
   - a numeric line `4.547.331` passes, and `p. 12` fails numeric_shape;
   - a heading `ΚΕΦΑΛΑΙΟΝ` (8 letters) passes and `ΑΒΓ` fails;
   - all earlier planted cases still behave as before.

Leave a guarded commit list. The last line must be exactly:
`ADM5c: done | tool_version: <v> | w1_originals_v3: 30114 -> <pass> (serbia <a>/<b>, elstat numerics <c>/<d>, headings <e>/<f>) | v2 census: <fail>/<n> | tests: <n> passed`
