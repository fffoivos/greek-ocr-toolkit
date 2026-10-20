# SS5 — Q3: merge the typing answers, compare with Opus, build the lead's eye sheets (no reading)

You are Sol, executing for the small-segment analysis lead. Merge the five typing contexts, score agreement with the earlier Opus
typology, and build contact sheets for the lead's pixel check. Do not type or judge crops yourself.

Worktree: `~/Projects/greek-ocr-toolkit-sol-recut`. `SS = docs/records/harvest/collect_v3_admission/segeval1/small_segments`.
Python: `~/Projects/greek-ocr-toolkit/.venv/bin/python` (Pillow; if its Pillow cannot draw text, use the x86_64 Python named in the
sol-reading HANDOVER §2). Network off.

## Hard constraints
Write ONLY under `SS/q3/` (new files and folders), `SS/tools/` and `SS/tests/` (new files only). Change nothing else; no git
add/commit; no reading runs; no `codex` calls. Do not touch PACK_ROOT.

## Inputs
`SS/q3/answers/t0{1..5}.mapped.jsonl`, `.check.json`, `.scan.json`; `SS/q3/sample.jsonl`; `SS/q3/key_opus.jsonl`;
`SS/q3/LEAD_CONTROLS.json` (amended; it carries an `amendments` list) and `SS/q3/LEAD_CONTROLS.v1.json` (original);
`SS/q3/usage_ledger.jsonl`. The packs are `type2` (`SS/q3/keys/type2.json`); the `*_VOID.*` files (t01 run1–2, t04 run1–2, and any
t04 run3 VOID) are void evidence: list them, never merge them. If `t04.jsonl` is absent or its scan is not clean, merge t01–t03
and t05 only and report t04's 83 bed rows as untyped (keep them in typing.jsonl with type null). t04 was re-run after the lead
added environment sentences to the prompt (no helper files; allowed ImageMagick operations): record the rendered prompt sha256 per context (`SS/q3/prompts_rendered/`) and show the diff between prompt versions. Stop and report if any context's scan is not clean. Re-score every context's controls under both the
original (v1, as frozen in the key) and the amended expectations, and report both; a context is flagged if it has more than one
error under the AMENDED expectations — list flagged contexts, and continue.

## Outputs
1. `q3/typing.jsonl`: one row per bed crop (controls excluded): every `sample.jsonl` field + `ctx`, `card_id`, Sol `type`, `text`,
   `crop`, `rotated`, `detail`, and `opus_type`/`opus_note` where present.
2. `q3/AGREEMENT.md` + `.json`:
   - control results per context (errors listed);
   - Sol vs Opus on the stratum-1 rows. First map Opus types to the new codes: word_or_phrase→word,
     heading_caps_display→caps_display, abbreviation_reference_label→abbrev_label, roman_numeral_lowercase→roman_lower,
     punctuation_only→punctuation, noise_non_text→noise, handwriting→handwriting, foreign_script_printed→foreign_script,
     map_figure_ornament_logo→figure_ornament, scan_watermark→watermark, show_through_mirrored→show_through,
     cut_fragment→cut_fragment, multi_line_crop→multi_line, text_covers_part_of_crop→part_of_line; any other Opus type is
     listed as is. Then give the confusion matrix, exact agreement, and the list of disagreements (line_id, Opus, Sol, Google text).
3. Lead eye sheets `q3/eye_sheets/eye_NNN.png`, 8 crops per sheet, in this order:
   - (A) every bed row whose Sol type is one of noise, handwriting, figure_ornament, watermark, show_through, cut_fragment,
     multi_line, part_of_line, foreign_script, other, punctuation, marker or number, or whose text is `unreadable` or
     `not_text` (the controls show Sol types tiny specks as punctuation or cut_fragment, so those are all checked);
   - (B) every Sol-vs-Opus disagreement not already in (A);
   - (C) a seeded 10% random sample (seed 20261019) of the remaining bed rows.
   Rendering: each crop scaled to fit 900×200 px, aspect kept, no upscaling beyond 4×, nearest-neighbour, a 1 px red frame at the
   crop edge. Under each crop: a sheet-local index, line_id, `Google: <text>`, `Sol: type / text / crop / rotated`, `Opus: <type>`
   if any, and `detail` if not empty. Use a font that renders Greek, Cyrillic and CJK (search /System/Library/Fonts and
   /Library/Fonts; name the font in the receipt). `q3/eye_index.jsonl` maps sheet + index → line_id, group (A/B/C).
4. `q3/SS5_RECEIPT.json`: inputs and outputs with sha256, counts per group, the font, test results, and usage totals from the
   ledger.

## Tests (`SS/tests/test_ss5_merge.py`)
Merge refuses a missing or duplicated line_id; controls are excluded from typing.jsonl; the Opus mapping covers every Opus type
present or lists it; the group assignment is disjoint and seeded.

Last line exactly: `SS5 READY: typing <n> rows, eye sheets <k> (A <a>, B <b>, C <c>), agreement q3/AGREEMENT.md, receipt
q3/SS5_RECEIPT.json` (or `SS5 FAILED: <reason>`).
