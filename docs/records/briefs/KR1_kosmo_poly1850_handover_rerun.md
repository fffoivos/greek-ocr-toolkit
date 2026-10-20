# KR1: re-run kosmopolis poly1850 under the HANDOVER protocol (gpt-6.1-sol, medium, network OFF, mechanical)

**Coordinator ruling:** kosmopolis poly1850 is a release-v3 candidate, so it must carry the same receipt as the others. Re-run it with controls and scanner v4. The first run (SRK1/SRK2, 87db4392: letters 96, crop_ok 99) is recorded beside it as **"pre-handover, no controls"**.

## Do (as for CAPS1/CAPS3; HANDOVER at opus/sol-reading ad1889bd9)
1. **Cards:** the **same 100 T6g masked cards** (`docs/records/harvest/recut_v1/w1_masked/cards_kosmo_poly1850/reader/`, key `cards_kosmo_poly1850_key.json`), so the two runs are paired on the cards.
2. **Controls:** reuse the 10 lead-approved controls from CAPS1/CAPS1b (c057, c009, c013, c026, c046, c041, c029, c072, c035, c066) with their approved truth, 5 per context.
3. **Packs:** bed `kosmo2`, contexts c1 and c2 (50 bed + 5 controls each), at PACK_ROOT `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs`.
   - Fresh opaque ids and content-hash names; a fresh seeded order (`kr1:kosmo:poly1850`), different from SRK1's.
   - Keys go outside PACK_ROOT, at `docs/records/harvest/recut_v1/w1_masked/kosmo2/keys/`.
   - The prompt is `prompts/bsb.md` verbatim; closure uses the CAPS1 adapter.
   - Use the existing `sol_packs/launchers/`. Give the two launch lines.
   - If a crop is regenerated, use only `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`; that interpreter is the only byte-exact one.
4. **Tests:** the card set equals T6g's 100; control placement; closure; seed.
5. **Scoring** happens later, in a separate brief after the readers run.

README at `docs/records/harvest/recut_v1/w1_masked/kosmo2/README.md`. The last line must be exactly:
`KR1: done | cards: 100 (same as T6g) | controls: 10 reused | closure: clean | launch lines: 2 | tests: <n> passed`
