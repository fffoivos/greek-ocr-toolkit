# SRK1 Sol reader handoff

Ready: 100 cards, one reader context, network OFF. The reader has not been launched. Letters and crop_ok from Sol are final after reading; mark verdicts are recorded and remain **pending Opus**.

PACK:

```text
/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/kosmo_poly1850/r1/
```

PACK contains exactly `cards.jsonl` and 100 independent PNG files in `crops/`. It is outside every repository. No protocol, key, truth file, manifest, or link is in PACK. The reader receives the unchanged protocol through the prompt on stdin.

The input is the existing T6g `cards_kosmo_poly1850/reader/cards.jsonl` and its crops. Labels and word_scripts are unchanged. The private key, `cards_kosmo_poly1850_sol_key.json`, records the original order, seeded reordered source IDs, opaque-to-original ID map, line/page mapping, source bindings, and source/pack image hashes. Ordering uses `random.Random('sol-reading:kosmo_poly1850:r1').shuffle`. IDs follow the lead's `k` plus ten SHA256 hex characters convention; all 100 are unique.

The lead pack format uses RGB PNGs without metadata, named by their content SHA256. All 100 T6g grayscale PNGs were losslessly expanded to RGB and re-encoded accordingly. Dimensions and every RGB pixel match the source conversion; each output is an independent file. This changes PNG bytes, so both source and pack hashes are retained in the private key.

## Exact launch line for the lead

```sh
bash /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/run_read.sh SRK-kosmo-r1 /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/kosmo_poly1850/r1/ /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/cards_kosmo_poly1850_sol_prompt.md medium
```

The copied launcher selects `gpt-6.1-sol`, disables multi-agent work, apps, web search and sandbox network access, and limits workspace writes to PACK. Its adjacent `logs/` directory exists. `bash -n` passed. The launch line above is prepared for the lead; it was not executed.

## Byte identity

The read-only source worktree is `~/Projects/greek-ocr-toolkit-sol-reading`, branch `opus/sol-reading`, HEAD `0cf9a7dbea4a4212779d92ad8d413bcc4a2176f9`. Its prompt, scanner, common definitions and builder match that commit's tracked bytes.

| Artifact | Location | SHA256 |
| --- | --- | --- |
| Original prompt | `greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/prompts/bsb.md` | `1b27b5d2fac6491ffa5c84f3d12f762883bbaa0af01de2d91a17576760741f57` |
| Byte-identical prompt copy | `cards_kosmo_poly1850_sol_prompt.md` | `1b27b5d2fac6491ffa5c84f3d12f762883bbaa0af01de2d91a17576760741f57` |
| Original launcher | `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/d11f6140-6320-42d0-9f21-018ca3512d68/scratchpad/run_read.sh` | `71585bfd18fd5cbd44ce710ae1c2bb778d0d83e5263f71bf220135b038d77cf4` |
| Byte-identical launcher copy | `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/run_read.sh` | `71585bfd18fd5cbd44ce710ae1c2bb778d0d83e5263f71bf220135b038d77cf4` |

The prompt is copied verbatim, including its C1 protocol and examples. No wording was changed.

## Leak scan and tests

`cards_kosmo_poly1850_sol_packscan.json` records a clean scan: 100 cards, 101 files, zero hits, and all file hashes. It executes the pinned lead `tools/scan_packs.py` logic in memory, with two explicit adaptations: the private assignment points to the SRK1 key outside PACK, and the reverse r2 requirement is omitted under the coordinator's one-reader ruling. The bsb/C1 field allowlist and remaining lead checks are unchanged. Supplemental checks cover original card, page and line IDs, additional T6g private field names, repository ancestry and root/ancestor links. Short source IDs use the lead's token-boundary rule so incidental hexadecimal substrings are not treated as identifiers.

All 13 checks passed: closure and pixel custody; seeded order, ID opacity and mapping; byte-identical prompt; byte-identical launcher; and nine rejection checks covering a private field, source ID, nonopaque ID, PROTOCOL.md, truth file, key file, parent path escape, external symlink and external hardlink. These checks reject violations; a failed pack scan raises an error and exits nonzero. The initial supplemental substring-check false positives are preserved outside PACK in `srk1_validation/attempt1_packscan.json`.

All preparation and verification used local files only. Nothing was admitted or adjudicated, and no reader answers were generated.

## Guarded commit list

Exactly these four repository paths are in scope; no PNGs, original T6g files, or unrelated changes are included:

```text
docs/records/harvest/recut_v1/w1_masked/cards_kosmo_poly1850_sol_key.json
docs/records/harvest/recut_v1/w1_masked/cards_kosmo_poly1850_sol_prompt.md
docs/records/harvest/recut_v1/w1_masked/cards_kosmo_poly1850_sol_packscan.json
docs/records/harvest/recut_v1/w1_masked/cards_kosmo_poly1850_sol_README.md
```

The SHA256-bound commit list and validation helper live outside PACK and outside the repositories:

```text
/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/srk1_validation/commit-inputs.json
/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/srk1_validation/srk1.py
```

Validate before the coordinator commits:

```sh
/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/srk1_validation/srk1.py check
```

The guard requires branch `sol/recut-v1`, HEAD `4e57c12895a7ecb7b66cf9537a50e4e286b7ac99`, an empty index, exact file/input hashes, a clean live pack scan, crop custody and byte identity. It never stages or commits. The list was prepared and checked; no staging or commit was attempted.

SRK1: done | cards: 100 | pack scan: clean | prompt sha: 1b27b5d2fac6491ffa5c84f3d12f762883bbaa0af01de2d91a17576760741f57 | launch line ready
