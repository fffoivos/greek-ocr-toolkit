# T6g: 100 masked qualification cards for kosmopolis poly1850 (gpt-6.1-sol, network OFF, nice, ≤ 30 min, mechanical)

This runs in this worktree (`sol/recut-v1`). It is a draw and pack only; no masking is re-run and nothing is admitted.

**Why.** The wave-1d admission (sol/collect-v3 65faa5f4) holds out kosmopolis poly1850 (473 rows), because C1 checked only poly1900. The coordinator ruled that it may enter with its own 100 masked cards.

## Do
1. **Pool:** the T6b kosmopolis outputs, `docs/records/harvest/recut_v1/w1_masked/kosmopolis/records.jsonl` (kept local), joined with `~/Projects/collect-v3-data/run/W1/crop_tight_page.jsonl` (read-only) on row id. Keep rows with `primary_class == poly1850` and output_kind `masked` or `guarded_original`. Exclude:
   - screen_merged;
   - rotated_crop (the ids in `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_exclusions/w1_rotated_crop_ids.txt`);
   - the 100 T6b kosmopolis cards already drawn (`cards/kosmopolis_key.json`).
   - Report the pool size; about 470 is expected.
2. **Draw:** 100 uniform cards, seeded `t6g:kosmopolis:poly1850`, over the line-id-ordered pool. Never sort by length. If the pool is below 100, take all of it and say so.
3. **One reader folder** (the adopted E1 practice: one reader context for all 100 cards): `docs/records/harvest/recut_v1/w1_masked/cards_kosmo_poly1850/reader/`, containing:
   - `cards.jsonl` in the v2 card shape (card_id, crop, google_text, word_scripts), the same as the T6b cards;
   - `crops/`, **copied** from the masked crop (or the byte-exact original for guarded rows);
   - `PROTOCOL.md`, a byte-identical copy of `docs/records/harvest/recut_v1/w1_masked/cards/LABEL_CHECK_v2.md`.
   - The key goes to `docs/records/harvest/recut_v1/w1_masked/cards_kosmo_poly1850_key.json`. It must **not** be inside or directly above the reader folder: keep it at the w1_masked level, two levels up. Add an isolation check that nothing key-like is in the reader folder or its parent.
4. **Tests:** pool filter, seed reproducibility, the isolation check, and crop sha equal to the record's sha.

## Hand-off
Leave a guarded commit list (PNGs git-ignored, hashes in the key). The last line must be exactly:
`T6g: done | pool: <n> | cards: <n> | isolation: <ok> | tests: <n> passed`
