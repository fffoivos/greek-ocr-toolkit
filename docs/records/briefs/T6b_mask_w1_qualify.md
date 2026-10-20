# T6b: apply the frozen foreign-ink masking to W1 rows and emit the qualification card sets (gpt-6.1-sol, xhigh, network OFF, ≤ 90 min)

This continues T6a2 (eacb5c39) in this worktree (`sol/recut-v1`).

**Coordinator ruling (a):**
- **Masking (not T6a tightening)** goes to qualification for **Gazette modern, Kosmopolis and Lekythos**.
- Their own-ink damage is stated per source from T6a2 dev: Gazette 0 px, Kosmopolis 11 px, Lekythos 20 px. The blind check judges it.
- **IA Greek+Latin stays hold-tagged with masking off. Do not process it.**
- The literal "own-ink loss = 0" rule is amended in the record to "own-ink loss stated per source and judged blind". The reason: large paired CER gains, and the crop_ok-y subset improves with no source worse.

**Precondition.** W1 has finished: `~/Projects/collect-v3-data/run/collector.exit` exists, and `W1/state.json` status is `completed_selected_sources`. If it has not finished, stop immediately and report.

**The W1 run root is read-only for you.** Never write to `~/Projects/collect-v3-data/`, and never take its locks.

**Which rows.** These three sources are held at source level, so their rows have `usable_final=false`. The rows to process are the W1 candidates in `~/Projects/collect-v3-data/run/W1/crop_tight_page.jsonl` (`candidate_usable=true`, `crop_tight_page=true`): gazette 16,691, kosmopolis 3,864, lekythos 9,113.

**Merged-line exclusion first (coordinator ruling after C1 stratum 10).** Drop every row with `screen_merged=true` before masking and before the card draw, so the cards measure masking and not merging. Report the removed counts per source (expected: gazette 1,392, kosmopolis 676, lekythos 1,124). C1 found that this flag catches 4 of 7 merged multi-line Gazette crops; report its recall on the T6b cards as `merged_two_lines` verdicts come back, but add no new screen.

**Rotated-crop exclusion (coordinator ruling after C1 stratum 11).** Also drop every row whose `crop_bbox` height is greater than its width and whose label has ≥4 letters (`rotated_crop`: vertical lines stored rotated 90°). No rotation repair and no text rewrite. Expected: gazette 767 rows in total, 669 of them already `screen_merged`, so 98 more; kosmopolis 0; lekythos 0. Rows left to mask: gazette 15,201, kosmopolis 3,188, lekythos 7,989. Report both removal counts per source in the receipt.

## Do
1. **Mask.** For every remaining row of `gazette_modern`, `kosmopolis` and `lekythos`, run the frozen masking (`greekocr/glyphs/foreign_ink.py`, params `801d517e…`, library hash as frozen). Inputs, all from the W1 run root:
   - the retained crop-source raster;
   - the saved Google response;
   - the row's crop box.

   **Exclude lines tagged caps/heading** (this covers drop-caps).

   Write the masked crops and a per-row record (row id, original crop sha, masked crop sha, fill statistics, masked-pixel and component counts, params hash) under `docs/records/harvest/recut_v1/w1_masked/<source>/`. The originals stay untouched.
1b. **Wrong-line guard (coordinator ruling after the v2_test harm diagnostic).**
   - Approved as a **SKIP condition only**.
   - For every row, compute `own_ink_masked_fraction`: the share of the crop's own dark ink (on the original crop) that the mask would change.
   - **If it is >0.30, leave the row unmasked** (a byte-exact original crop) **and flag it `wrong_line_risk=true`.**
   - Run the own-ink audit (T6a2 / T6d `component_audit`) on **every** masked row; it is a prerequisite.
   - Report per source: guarded rows and pages, plus a contact sheet of up to 20 guarded rows (original, the would-be mask in red, label).
   - The "matched curve centre outside the crop's middle band" variant is a new matching rule. **Do not apply it.**

2. **Cards.** Per source, write **100 uniform seeded cards** (seed `t6b:<source>`; never sorted by length) over all usable rows after the guard (masked rows, and guarded rows as their unmasked originals; the key records which). Use the v2 card shape: `card_id`, `crop` (the masked crop), `google_text` (the row's post-convention label), `word_scripts`, with a separate key file (`line_id`, original and masked crop sha).
   - Output: `docs/records/harvest/recut_v1/w1_masked/cards/<source>/cards.jsonl` plus `crops/`, and `<source>_key.json`.
   - Checker instructions: `~/Projects/greek-ocr-toolkit-sol-funnel-gr/docs/harvest/blind_checks_v1/v2/LABEL_CHECK_v2.md`, **unchanged**.
3. **Receipt per source.** Write `docs/records/harvest/recut_v1/w1_masked/<source>_receipt.json` with:
   - rows masked and rows excluded (caps/heading);
   - the share of crops changed;
   - the fill statistics summary;
   - the dev own-ink damage stated (T6a2);
   - the amended rule text;
   - the card paths and hashes.

   **Nothing is admitted here.** The gate is applied by the coordinator's side after the blind checks: crop_ok ≥90% **and letters ≥90%** on the same 100 masked cards (point estimate), own-ink clipping judged as crop_clipped. For Gazette this is also the W2 Gazette probe gate (C1 on the original crops failed: letters 86, crop_ok 70). A pass admits masked rows for the wave-1d arm only.

## Hand-off
Commit with the masking guarded helper. Do not commit images if they are git-ignored; list their hashes instead.

The last line must be exactly:
`T6b: done | masked rows: gazette <n> kosmopolis <n> lekythos <n> | cards: 100/100/100 | changed: <x>% | params: 801d517e`
