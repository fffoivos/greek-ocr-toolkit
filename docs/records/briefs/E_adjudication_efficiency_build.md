# E-build: item packs for the adjudication-efficiency experiment (gpt-6.1-sol, xhigh, network OFF, nice, ≤ 60 min)

This is build work only: no readers run here. I run the Opus readers afterwards.

**Where you may write:** only under `docs/records/harvest/collect_v3/c1/efficiency/` in this worktree (`sol/collect-v3`). A live W2 collection imports `collect_v3/*.py` from this checkout, so **never modify, format or touch anything under `collect_v3/`** or any other existing file. Read-only inputs:
- `~/Projects/collect-v3-data/run/` (W1 pages, responses, crops, `W1/features.jsonl`, `W1/c1/`). Never write there and never take its locks.
- The scratchpad packs named below.

## Purpose
The owner's rule is that the reader count per item never drops. An efficiency change is adopted only if an experiment shows no quality loss. The arms differ in one factor each, against the control E0.

## Test beds (fixed truth)
1. **BSB:** C1 stratum `bsb_poly1850__poly1850`, 100 cards: `~/Projects/collect-v3-data/run/W1/c1/bsb_poly1850__poly1850/cards.jsonl` plus `crops/`. Do not open the key; the line ids are not needed for the packs. The reference verdicts are `docs/records/harvest/collect_v3/c1/verdicts/bsb_poly1850__poly1850__{a,b}.jsonl`. Do not copy verdicts into any reader pack.
2. **Yer:** 59 items with 65 masked positions: `docs/records/harvest/collect_v3/c1/yer_adjudication/items_{a,b}.jsonl`. The crop paths inside point to `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/{c1,v2}/...`. The ink truth is `table.json` + `ink_*.jsonl`. The control protocol for this bed is `yer_adjudication/INK.md`.

## Build, per arm, per bed
Make self-contained reader folders `efficiency/packs/<bed>/<arm>/<reader>/`. Each holds only what that reader may see: its items file, the crops it needs **copied in** (never symlinked), and its protocol file. **No key, truth or verdict file may be reachable from a reader folder** (not in it, not one level up). Put the keys in `efficiency/keys/`.

| arm | factor changed vs E0 | readers per bed (each item read once per run) |
|---|---|---|
| E0a, E0b | none. Control: BSB = LABEL_CHECK_v2 unchanged, 50 cards per reader; yer = INK.md unchanged, about 30 items per reader. Run twice: E0a and E0b, same items, different random order. | 2 + 2 |
| E1 | one context for all items (BSB 100 cards; yer 59 items). Protocol unchanged. | 1 |
| E2 | the reader gets **no full-line crop**: per word, a word crop (from the Google token boxes in the saved response, mapped into crop coordinates, upscaled 3x) and per letter of interest a close-up (8x). BSB: every word of the line. Yer: the word holding each masked slot, plus a close-up of its final letter. Protocol = E0's text with only the sentence about the input image(s) changed; state exactly what the reader no longer gets. 50 / ~30 per reader as E0. | 2 |
| E3 | compact prompt: the instructions once, then each item as a minimal line (id, image path(s), text); remove repeated examples and boilerplate, keep every rule. 50 / ~30 per reader. | 2 |
| E4 | E1 + E3 combined (one context, compact prompt). | 1 |

- **Order:** for each arm, a fresh random item order with seed `eff:<bed>:<arm>`, recorded in the key.
- **IDs:** keep the original card and item ids, so verdicts align across arms.
- **E2 mapping:**
  - Use the W1 response tokens whose boxes fall inside the row's crop box. The row id comes from the key, which you may read for the build but never place in a pack.
  - For yer v2 cards, take the boxes from the earlier v2 import if they exist. If token boxes are missing for any item, list it and fall back to an even split of the line box by character count, marked `approx_box=true` in the key.
  - Report the share of approximated items.

## Output
- `efficiency/packs/...` and `efficiency/keys/...`.
- `efficiency/MANIFEST.json`: every pack file with sha256, items per reader, the arm factor, and the copied-crop hashes.
- `efficiency/score.py`. It reads the verdict files (paths given as arguments) and computes, per arm:
  - agreement with truth: BSB letters/crop_ok/marks per card vs the C1 reference verdicts; yer = slot call vs ink truth;
  - agreement with E0a, and the E0a–E0b agreement (reader-reader variance, the bar to beat);
  - unresolved counts (u / other);
  - the confidence distribution where reported;
  - wall time and tokens per card, taken from a usage JSON I supply (`--usage file`; fields per reader: total_tokens, tool_uses, duration_ms). Never estimate tokens.
- Unit tests for the folder isolation (no key reachable), id alignment and the scorer.

## Hand-off
Commit only files under `docs/records/harvest/collect_v3/c1/efficiency/`, excluding copied images (git-ignore `*.png` there; the manifest binds their hashes). Your sandbox cannot write `.git`; leave a guarded commit list. The last line must be exactly:
`E-build: done | packs: bsb <n> readers, yer <n> readers | E2 approx boxes: <x>% | isolation test: <ok> | tests: <n> passed`
