# SRK1: Sol-reader pack for kosmopolis poly1850 masked cards (gpt-6.1-sol, network OFF, mechanical)

**Coordinator ruling:** the paused stratum checks resume on Sol as the reader: one reader, 100 cards per context, using the Sol-reading lead's prompt and pack format **verbatim** (`~/Projects/greek-ocr-toolkit-sol-reading`, opus/sol-reading 0cf9a7dbe, read-only).
- Packs live outside every repo.
- The leak scan is mandatory.
- Letters and crop_ok from Sol are final. Mark verdicts are recorded but stay "pending Opus".

## Do
1. **Pack:**
   - Create `PACK=/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/kosmo_poly1850/r1/`.
   - Copy into it the T6g reader cards (`docs/records/harvest/recut_v1/w1_masked/cards_kosmo_poly1850/reader/cards.jsonl` + `crops/`), with **opaque, re-ordered card ids**. The new seeded order and the id map go into a key **outside** PACK: `docs/records/harvest/recut_v1/w1_masked/cards_kosmo_poly1850_sol_key.json`.
   - **No PROTOCOL.md and no key may sit in PACK.** The reader gets its protocol through the prompt only, as in the Sol-reading packs.
2. **Prompt:** take the Sol-reading lead's `docs/records/harvest/sol_reading/prompts/bsb.md` **verbatim**. It is the C1 protocol for this exact card shape. Save a byte-identical copy as `docs/records/harvest/recut_v1/w1_masked/cards_kosmo_poly1850_sol_prompt.md` and record both sha256 values. Change nothing in it.
3. **Leak scan:** run the Sol-reading `tools/scan_packs.py` logic, or its documented checks, over PACK: no source or line ids, no private field names, no key or truth files, and no links out of PACK. Write `docs/records/harvest/recut_v1/w1_masked/cards_kosmo_poly1850_sol_packscan.json`. **Fail loudly** on any hit.
4. **Launch line:** copy `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/d11f6140-6320-42d0-9f21-018ca3512d68/scratchpad/run_read.sh` byte-identically to `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/run_read.sh` (+ `logs/`). In the README, give the exact launch line for the lead:
   `bash <that path> SRK-kosmo-r1 <PACK> <prompt path> medium`
5. **Tests:** pack closure, id opacity, and byte-identical prompt and launcher.

## Hand-off
Leave a guarded commit list (key, prompt copy, pack scan, README; no PNGs). The last line must be exactly:
`SRK1: done | cards: <n> | pack scan: <clean|hits n> | prompt sha: <sha> | launch line ready`
