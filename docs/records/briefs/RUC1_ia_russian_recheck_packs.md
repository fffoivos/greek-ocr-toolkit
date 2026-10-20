# RUC1: ia_russian re-check after the RU1 label repair: Sol-reader packs per HANDOVER (gpt-6.1-sol, medium, network OFF, mechanical)

The secondary-corrections lead repaired the word-final ъ/ь labels.
- File: `~/Projects/greek-ocr-toolkit-secondary/artifacts/ru1/ru1_v1.jsonl` (branch opus/secondary-corrections), sha256 `1fb0a9f5bde4a166fd480ffb414d5e376596b600fd728b6e099b6b1803af2db0`, manifest `ru1_v1_manifest.json`.
- 314 rows keyed by W1 id: 311 ok, 3 hold.

**The admission re-check is the sourcing lead's:** 100 fresh uniform cards, letters ≥ 90 and crop_ok ≥ 90 (Sol final; marks pending Opus). C1 on the old labels was letters 74, crop_ok 97.

## Do
1. **Verify** the sha256, and that every `label_parent` equals the W1 `label` for its id (`~/Projects/collect-v3-data/run/W1/features.jsonl`, read-only).
2. **Pool:** W1 `ia_russian` rows with `primary_class == cyrillic` and `candidate_usable == true`.
   - Each card's label = `label_ru1_v1` where the row is in ru1_v1 with status ok, else the W1 `label`.
   - Exclude: the 3 hold rows; the 100 C1 ia_russian card lines (`run/W1/c1/ia_russian__cyrillic_key.json`, read only for ids); rotated_crop; every release-exclusion class.
   - Report the pool size and how many pool rows carry a repaired label.
3. **Draw:** 100 uniform cards, seed `ruc1:ia_russian:cyrillic`. Report how many drawn cards have repaired labels.
4. **Crops:** regenerate byte-exactly with the collector's `storage.ensure_crop` path, **only** with `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`. That is the only byte-exact interpreter; the x86_64 Python re-encodes PNGs differently. Each crop's sha256 must equal the row's `crop_sha256`.
5. **Packs:** as in CAPS3/KR1.
   - Bed `ruc1`, contexts c1 and c2 (50 bed + 5 controls each).
   - The 10 lead-approved controls are reused (CAPS1/CAPS1b list).
   - PACK_ROOT `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs`; keys outside, at `docs/records/harvest/recut_v1/w1_masked/ruc1/keys/`.
   - The prompt is `prompts/bsb.md` verbatim. Its old-Cyrillic letter checks, including ъ, apply.
   - Closure uses the CAPS1 adapter; launchers `sol_packs/launchers/`. Give two launch lines.
6. **Tests:** label substitution exactly from ru1_v1; exclusions; crop sha equality; closure; seed.

README at `docs/records/harvest/recut_v1/w1_masked/ruc1/README.md`. The last line must be exactly:
`RUC1: done | pool: <n> (repaired labels <k>) | cards: 100 (repaired <r>) | controls: 10 reused | closure: clean | launch lines: 2 | tests: <n> passed`
