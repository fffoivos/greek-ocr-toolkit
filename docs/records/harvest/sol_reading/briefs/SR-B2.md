# SR-B2: tie-break packs, 2-of-3 resolver, scorer and results tables

Work non-interactively in `~/Projects/greek-ocr-toolkit-sol-reading`, and finish in this turn. Read `docs/records/harvest/sol_reading/PLAN.md` (sections Arms and Measures), `README_B1.md`, and the tools you built in SR-B1/B1b. Network off. Do not run git or codex. Write only under `docs/records/harvest/sol_reading/` and PACK_ROOT (`/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/d11f6140-6320-42d0-9f21-018ca3512d68/scratchpad/sol_reading_packs`).

Inputs per bed, as they exist:
- `answers/<bed>/{r1,r2}.jsonl`: raw Sol answers with opaque ids;
- `.mapped.jsonl`, `.controls.json`, `.scan.json`;
- `usage_ledger.json`;
- `opus_reference/`.

Some beds may have only r1 when you run. Every tool must work with whatever is present and report what is missing; never invent anything.

## 0. Scanner v2 (do this first): `tools/scan_rollout.py`
The pilot rollout `~/.codex/sessions/2026/10/17/rollout-2026-10-17T12-46-05-01a14941-1aa1-7462-9527-abe489c72a54.jsonl` (reader dir `PACK_ROOT/owner39/r1`, scan in `answers/owner39/r1.scan.json`) was voided by two false positives. The lead reviewed it by hand and found it clean:
- **Computed paths.** Sol views images in JS loops, for example ``for (const p of ["<hash>",…]) image((await tools.view_image({path:`img/${p}.png`})).image_url)``, so a static parse cannot resolve the path.
- **"key".** The substring hit Python's `x.keys()`.

Replace both rules:
1. **Image provenance (primary check).** Decode every `input_image` in every `custom_tool_call_output`/`function_call_output`. Each must either byte-match a PNG inside the reader folder (pack `img/`/`crops/` or anything under `zoom/` at scan time), or be a downscale of one: `view_image` caps the long side at 2048. For example `zoom/line33.png` at 3372×292 arrives as 2048×177. Match a downscale by aspect ratio within 1 px, plus a pixel comparison after resizing the candidate with Pillow (mean absolute difference below a small stated threshold). An unmatched image is a violation.
2. **Literal strings.** Scan every string literal and template-literal text in tool inputs, and every shell command. Violations:
   - an absolute path outside the reader folder;
   - `..` or `~` path components, `$HOME`, `/Users/`;
   - path components or names matching `keys/`, `*key*.json`, `truth`, `verdict`, `opus_reference`, `MANIFEST`, `sol_reading_packs`, or another reader folder's name.

   Code idioms (`.keys()`, `key=`, variable names) are not violations. Computed arguments are no longer violations by themselves; they are covered by rule 1 for images and by the literal-string rule for commands.
3. **Manifest check.** Unchanged: originals intact; only `answers.jsonl` and `zoom/**` added. Report what is under `zoom/`.

Add tests:
- a synthetic downscale match;
- a synthetic outside image, which must flag;
- a `.keys()` idiom, which must not flag;
- an outside absolute path inside a template literal, which must flag.

Re-scan the pilot (it should pass) and the canary probe (it must still flag), and save the new pilot scan over `answers/owner39/r1.scan.json`. Keep the old one as `r1.scan.v1.json`.

## 1. `tools/build_tiebreak.py <bed>`
Find the disagreements between r1 and r2 on bed items (controls are excluded from the disagreement set):
- **bsb:** a card disagrees if letters, marks or crop_ok differ.
- **yer:** a slot disagrees if the calls differ. The tie-break item is the whole line, with only those slots masked. The other slots are revealed as the bed's Google letter: use the same masking rule, restricted to the disputed slots, and renumber them 1..k.
- **owner39:** a card disagrees if the anchor tuples differ (base, breathing, accent, diaeresis, subscript, after the head/transcription rule, with `unknown` as a value).

Build `PACK_ROOT/<bed>/r3/` with the same closure, public fields and rendering as r1:
- fresh opaque ids;
- a fresh seeded random order (`sol-reading:<bed>:r3`);
- for owner39, a fresh option permutation;
- planted controls at ⌈10%⌉ of the disputed items (at least 1), drawn seeded from that bed's controls.

The key goes to `keys/<bed>_r3.json`. Write `MANIFEST.r3.json` beside the folder and run `scan_packs.py` on it. Extend `map_answers.py` so it handles r3, including the yer sub-masking back to the original slot numbers. If there are 0 disagreements, write no pack and say so.

## 2. `tools/resolve.py <bed>`
S2 = 2-of-3 per unit (bsb per field per card, yer per slot, owner39 per anchor tuple).
- Where r1 and r2 agree, take their answer.
- Otherwise take r3's answer if it matches r1 or r2, else mark the unit `unresolved`.
- For owner39, the resolved card is the full answer object of the majority reader.

Write `answers/<bed>/S2.mapped.jsonl` in the scorer's input format. Unresolved units carry the scorer's undecided value (bsb `u`, yer `u`, owner39 `unknown` heads) and are also listed in `answers/<bed>/S2.unresolved.json`.

## 3. `tools/score_all.py`
Use `collect_v3/c1/efficiency/score.py` (import or subprocess; do not modify it) as the per-reader scorer against truth. Then compute, per bed:
- **Accuracy against truth for each reader:**
  - Sol r1, r2, r3 (disputed items only), S2;
  - Opus E0a, E0b and E1 (bsb, yer);
  - owner39 Opus partial E0 readers, on their answered cards only, with n stated.

  bsb: letters, marks, crop_ok, joint. yer: slot and item accuracy. owner39: per head and joint anchor, with breathing excluded on the noted card. Always state the denominators.
- **Agreement matrix:** Sol r1, Sol r2, S2, Opus E0a, E0b, E1 (bsb/yer), on the same units.
- **Variance yardsticks:** Sol r1 vs r2, and Opus E0a vs E0b.
- **S1→S2:** for each of r1 and r2 as "S1", the units whose verdict changes in S2, split by changed-to-correct, changed-to-wrong and changed-between-wrong, plus the net accuracy change.
- **Undecided counts:** `u`/`unknown`/`unreadable`/`unresolved` per reader.
- **Controls:** pass/fail per reader, and `flagged`.
- **Leak scans:** ok per run. A run with `ok=false` is excluded from every table and shown as VOID.
- **Cost table** from `usage_ledger.json`:
  - per run: items, wall, input, cached input, output, reasoning, tool calls;
  - weekly percent before, after and delta;
  - credits before and after;
  - tokens per item and weekly points per 100 items;
  - S2 cost = r1 + r2 + r3, and the ratio S2/S1.

  Add the Opus columns from `opus_reference/usage_log.tsv` (total tokens, tool uses, duration per item; E1 and E0 separately; owner39 partial runs marked partial). Keep the two meters apart and do not convert between them.
- **Disagreement listing:** every unit where Sol (r1, r2 or S2) and the Opus reference or truth disagree, with item ids. For bsb, add the printed-vs-google `detail` strings of both sides, so the lead can pixel-check a sample later.

Output `results/results.json` and `results/TABLES.md` (plain tables, denominators in every cell, no prose conclusions).

## 4. Tests and receipt
- Add unittest cases with synthetic answers, labelled synthetic and kept under `validation/`: disagreement detection, yer sub-masking round trip, 2-of-3 resolution including unresolved, S1→S2 accounting, and the void exclusion.
- Run all tests and write `TEST_RESULTS_B2.txt`.
- Write `REPORT_B2.md` with the commands to run after each stage:
  - after r1 and r2 of a bed: `build_tiebreak`;
  - after r3: `map_answers r3`, then `resolve`, then `score_all`.
- If real answers already exist, run `score_all.py` once on them and include the output.

Last line: `SR-B2 READY: tests=<pass>/<total>`, or `SR-B2 BLOCKED: <reason>`.
