# SR-G3: full-stratum grave/acute pass on nlg poly1900 (packs, flagger, re-read builder, review sheets)

Work non-interactively in `~/Projects/greek-ocr-toolkit-sol-reading`, and finish in this turn. Network off. Do not run git or codex. Write only under `docs/records/harvest/sol_reading/grave_full/` and `PACK_ROOT/grave_full/` (PACK_ROOT = `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/d11f6140-6320-42d0-9f21-018ca3512d68/scratchpad/sol_reading_packs`). Reuse the SR-G1 machinery in `docs/records/harvest/sol_reading/grave/` (geometry, rendering, closure scan, manifests, key layout) by import or port; do not modify `grave/`. Pillow: `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B`.

## 1. Items: `grave_full/tools/build_full.py`
- **Scope.** Every card of the 100 C1 cards of `nlg__poly1900`, and every word of each card's Google label (the C1 card's `google_text` / literal label) whose LAST vowel carrying an accent carries U+0301 or U+0300 (after NFD). The accent must be on the word's last syllable: no vowel follows the accented vowel within the word, apart from the second vowel of a diphthong in that syllable, as in καί or αὐτοῦ-type pairs. Words of any length; hyphen-split line-end fragments are excluded.
- **Fields recorded in the private key:** the label accent (`acute`/`grave`), card id, line id, word index, word as labelled, and `touches_punct` (same rule as SR-G2).
- **Geometry.** Exactly as SR-G1. An item without exact aligned geometry is dropped, never approximated. Report the drop count by reason.
- **Overlap.** Mark items that are also in the SR-G1 bed (same line id + word index) with their SR-G1 id, for a consistency check.

## 2. Pass-1 packs
- Split the items in seeded random order (`sol-grave-full:p1`) into contexts of at most 90 bed items each.
- Add about 10% planted controls to each (`⌈n/9⌉` per context): pixel-verified SR-G1 items from **lekythos and kosmopolis only** (never nlg), as a mix of grave, acute, circumflex and none. Use fresh ids and copied images.
- Folders: `PACK_ROOT/grave_full/p1c1/`, `p1c2/`, … Each has `items.jsonl` (same public fields as SR-G1: `item_id, word_image, letter_image, word_bare, anchor_index, anchor_base`), `img/`, and `MANIFEST.<name>.json` beside it.
- Key: `grave_full/keys/key.json`. Run the closure scan on every folder.

## 3. `grave_full/tools/flag_full.py`
Reads `answers/grave_full/p1c*.jsonl`. It validates them with the SR-G2 schema (`item_id, accent, confidence, note`) and maps them to bed items. It then:
- **controls:** reports control passes per context; a context with more than one control error is reported as flagged;
- **flags:** for each bed item, flag = Sol answer ≠ label accent. `unreadable`, `none` and `circumflex` answers are flags too, listed by answer type;
- **counts:** items, flagged by type, Sol-grave share overall, and the label-grave share;
- **consistency:** agreement with SR-G1 answers on the overlap items;
- **outputs:** `grave_full/PASS1.json` and `PASS1.md`.

`--build-reread` builds `PACK_ROOT/grave_full/p2/`: ALL flagged items, with fresh ids and a fresh seeded order (`sol-grave-full:p2`), plus `⌈n/9⌉` (at least 2) controls drawn as in section 2 but different from those in its pass-1 context where possible. Split it if it exceeds 90.

## 4. `grave_full/tools/confirm_full.py`
Reads `answers/grave_full/p2*.jsonl`. For each flagged item it reports:
- pass-1 answer and pass-2 answer, their agreement, and the label;
- the p2 controls.

It writes `grave_full/FLAGS.md`, plus private contact sheets `grave_full/keys/review/flags_<k>.png`: 6 tiles per row, at most 30 tiles per sheet, 1600 px wide. Each tile shows the letter image (at most 300 px high), the word image, the id, the label word, `label=<accent> p1=<x> p2=<y>`, and `touches_punct`.

It also writes `grave_full/LEAD_EYE.template.json`, with one entry per flagged item, for the lead to fill: `printed` ∈ {acute, grave, circumflex, none, unreadable}.

Then `confirm_full.py --final LEAD_EYE.json` produces `grave_full/FINAL.md`. Columns:
- items;
- flagged;
- confirmed (lead's printed ≠ label);
- false flags (lead's printed = label);
- pass-agreement p1 vs p2;
- p2 accuracy against the lead's eye;
- stratum grave base rate: the share of items whose printed accent is grave, using the lead's eye where flagged and the label otherwise, so it carries the assumption that unflagged items match the label;
- label grave_to_acute error rate (confirmed label-acute/printed-grave per item and per card), compared with C1's 9/100 cards.

## 5. Tests and receipt
Add synthetic tests and write `grave_full/TEST_RESULTS.txt` and `grave_full/BUILD_RECEIPT.json` (counts, drops, contexts, controls, manifest shas).

Last line: `SR-G3 READY: items=<n> dropped=<n> contexts=<k> (sizes …) controls=<n> overlap_G1=<n> tests=<p>/<t>`, or `SR-G3 BLOCKED: <reason>`.
