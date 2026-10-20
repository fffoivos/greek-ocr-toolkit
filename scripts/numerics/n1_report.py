"""Render the N1S0 Markdown report from the machine-readable census."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
c = json.loads((ROOT/'artifacts/n1/census.json').read_text())
t = c['w1']['total']
training = c['collection_v2']['train']
tr = training['total']
norm = training['codec_v1_normalized_eligible']
positions = ['thousands','decimal','range','table_boundary','other']
parts = ['# N1 step 0: numeric separators census and convention recommendation',
'17 October 2026. Step 0 only; lead convention ruling pending.',
'''Implemented a text-only tokenizer and froze an unrendered frame. No image was opened, decoded, rendered or read; no recognizer or model was run, no network tool was used, and no `.git` command or write was made. Dashes remain tags/proposals only. No labels, codecs or external inputs were modified.''',
'## Scope and counting',
'''W1 is counted on its `text` field (Google text), over all lines regardless of admission/quality gate. Source and year come from W1 metadata. Gazette is split into 1982–85 and 1986–90; ELSTAT spans its supplied historical years. Every other W1 source reaches 100 numeric tokens and is included. Source data and card metadata were read only as text; source pixels remain unread.

Tokens are maximal ASCII-digit runs joined by the specified separator candidates, including U+00B7 and U+0387 separately, and ordinary spaces. All adjacent digit pairs yield an inner slot, including zero-length gaps; each token adds two boundary slots. Thus a token with D digits has D+1 slots. Offsets are half-open Python character offsets into the original line, not pixel coordinates. Boundary glyphs capture adjacent nonspace separators. `NONE_TEXT` means an empty text span, not a fabricated printed `none` verdict.

Grammar labels propose thousands groups (initial 1–3 digits then groups of three), decimal suffixes (comma/period before 1–2 final digits), ascending year/page-style ranges (two groups of 1–4 digits), and text-indicated table boundaries (multiple spaces or an adjacent pipe/tab). Remaining slots are `other`. Range has priority over thousands when both apply; alternative candidates remain in the tokenizer and frame. A space-separated table can be mistaken for grouping; text cannot locate an unprinted gap or prove a table edge. No grammar label authorizes correction.

The hyphen class counts U+002D occurrences in **inner** slots of tokens with at least four **total** digits. It includes true ranges; it is a candidate population, not an error count. Token counts containing such hyphens are also recorded in the census.''',
'## W1 census',
'| Source / era | Lines | Numeric tokens | Slots | Inner / boundary | Hyphens in 4+ digit tokens |',
'|---|---:|---:|---:|---:|---:|']
for source,s in c['w1']['by_source_era'].items():
    parts.append(f"| {source} | {s['lines']} | {s['tokens']} | {s['slots']} | {s['inner_slots']} / {s['boundary_slots']} | {s['hyphen_in_4plus_digit_tokens']} |")
parts.append(f"| **Total** | **{t['lines']}** | **{t['tokens']}** | **{t['slots']}** | **{t['inner_slots']} / {t['boundary_slots']}** | **{t['hyphen_in_4plus_digit_tokens']}** |")


def table(name,s):
    parts.extend([f'### {name}', '| Google/label glyph code points | Thousands | Decimal | Range | Table boundary | Other |', '|---|---:|---:|---:|---:|---:|'])
    for glyph, counts in sorted(s['glyph_by_position'].items()):
        parts.append('| '+glyph+' | '+' | '.join(str(counts.get(p,0)) for p in positions)+' |')


parts.append('All tables count primary grammar labels once per slot. Code-point sequences preserve compound gaps; U+0020 is space. Empty slots and boundaries are included, so table totals equal slot totals.')
for source,s in c['w1']['by_source_era'].items():
    table(source,s)
parts.extend(['## Collection-v2 / E3 label census',
'''Input paths were found through toolkit `docs/records/reviews/ASTRA-R2design_brief.md` and `docs/records/labelfix/candidates_train_sample.md`: `~/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_{train,dev,test}.jsonl`. Each split is read once; `all` is not added again. Train is the training-label population; dev and test are separate convention checks.

E3's `~/Projects/greek-page-ocr/docs/ocr_program_2026-10-06/E3_RESULTS.md` reports 207,851 real training rows after codec, mixed with synthetic data. This census also reconstructs codec eligibility using NFD, the enumerated folds parsed from `factory/src/codec.rs`, whitespace collapse, and the v1 atom inventory, matching `bench/o5_prepare.py` / `bench/codec_coverage.py`. The reconstructed eligible train set has 207,867 rows, 16 more than the 207,851 reported in E3_RESULTS; this mismatch remains unresolved. It has 38,649 numeric tokens, 142,842 slots, 1 raised dot in an inner gap (with a following space), and 1,039 inner hyphens in 4+-digit tokens. This is an input-label/encoding census, not a checkpoint-specific draw ledger or a synthetic-training census. Original source labels and normalized codec-eligible tables are both retained per source/era in `census.json`. Collection-v2 era metadata are used as supplied; E3_RESULTS flags old Open Archives date metadata as unreliable, so those years are not asserted as verified publication dates.''',
'| Split | Source rows | Numeric tokens | Slots | Inner hyphens, 4+ digits | U+00B7 all / between digits | U+0387 all / between digits | Codec-eligible rows |',
'|---|---:|---:|---:|---:|---:|---:|---:|'])
for split, data in c['collection_v2'].items():
    s=data['total']; a=data['unicode']['U+00B7'];b=data['unicode']['U+0387']
    parts.append(f"| {split} | {s['lines']} | {s['tokens']} | {s['slots']} | {s['hyphen_in_4plus_digit_tokens']} | {a['occurrences']} / {a['between_digits']} | {b['occurrences']} / {b['between_digits']} | {data['codec_v1_normalized_eligible']['lines']} |")
table('Training labels: all source rows', tr)
table('Training labels: normalized codec-eligible rows', norm)
parts.extend(['### Training labels by source / era',
'| Source / era | Rows | Tokens | Slots | Hyphens in 4+ digits |', '|---|---:|---:|---:|---:|'])
for source,s in training['by_source_era'].items():
    parts.append(f"| {source} | {s['lines']} | {s['tokens']} | {s['slots']} | {s['hyphen_in_4plus_digit_tokens']} |")
parts.append('The full glyph × grammar tables for every training source/era and all three splits are in `collection_v2` in the census JSON.')
parts.extend(['## Convention recommendation',
'''**Recommend U+00B7 MIDDLE DOT. The lead rules; no convention was changed.** Both inspected codec versions have a U+00B7 atom, no U+0387 atom, and explicitly specify NFD with U+0387 → U+00B7. Python's local Unicode normalization independently produces that decomposition. v1 is the requested toolkit vendor file; no v2 exists beside it, so v2 was checked at `~/Projects/greek-page-ocr/codec/v2.json`. Exact atom records, policies and input hashes are in `census.json`.

Training labels use U+00B7 as prose punctuation (examples with line IDs and character offsets are in `collection_v2.train.unicode`). Neither dot code point occurs directly between digits in train, dev or test. There is one space-adjacent numeric-context exception in both the raw and normalized eligible train set: `6cc7ddf6ed4e-p000005-l0080`, `185· 95 εἶπον ὄχι, 85 εἶπον ναί, 5 ἠρνήθησαν ψῆφον·`. Its inner gap is `· `, classified `other`, not thousands. It may be prose punctuation between numbers; pixels were not checked. Thus no direct digit–dot–digit or grammar-thousands raised-dot supervision was found, but a broader numeric-token census does contain this one dot. Its numeric hyphens include valid ranges and cannot be called wrong without ink. Raised dots should map to U+00B7 under the current codec contract; preserve raw input code points in audit metadata.''',
'## C1 evidence and exclusions'])
for source, entries in c['c1']['separator_entries'].items():
    for entry in entries:
        parts.append(f"- `{source}` / `{entry['card_id']}` / `{entry['line_id']}`: {entry['detail']}")
parts.append(f"Read {c['c1']['verdicts']} existing verdict records. Excluded all {c['c1']['excluded_lines']} line IDs found in W1 C1 key files, including supplemental cards, from both sample partitions. Existing C1 separator entries are evidence anchors only; no new glyph verdicts were produced.")
parts.extend(['## Frozen sampling frame',
'''Seed **20261017**. `frame_step1.jsonl` contains **900 rows**: select `partition == "step1"` for the **600-slot** development frame, and `partition == "locked_eval"` for **300 locked slots**. All truth fields are null and rendered flags false. Frame rows carry crop paths/hashes for future use, token/slot character offsets and Google glyphs; pixel localization/alignment remains step 1 work.

Before development sampling, shuffled document lists reserve a quarter of each target source/era's documents, at least two, expanding only if 100 slots are unavailable. Evaluation draws 100 slots each from ELSTAT, Gazette 1982–85 and Gazette 1986–90, preferentially 90 observed separator/table candidates then 10 remaining slots. All pages/lines of reserved documents are forbidden to N1 fitting, not just the chosen slots.

Development first draws 240 suspected inner-hyphen slots, balances remaining observed separator/table candidates up to 540, then fills to 600 with remaining slots. Allocation uses round-robin source/era × primary grammar × exact glyph cells, shuffling within cells; rare cells are retained and common cells are downweighted. This is an enriched diagnostic sample, not a population-rate sample. The final hyphen count can exceed 240 through other strata. Controls are not fabricated: the lead must pixel-verify and plant the 10% controls in step 1; sampling these slots is not verification.'''])
for partition in ('step1','locked_eval'):
    counts={}
    for key,n in c['sampling']['stratum_counts'].items():
        part, source, position, glyph=key.split(' | ')
        if part==partition:counts[source]=counts.get(source,0)+n
    parts.append(f"{partition} source allocations: "+', '.join(f'{k} {v}' for k,v in sorted(counts.items()))+'.')
parts.append(f"The explicit development list has {len(c['sampling']['development_documents'])} documents; the reserved lock has {len(c['sampling']['locked_documents'])}. Both lists, all locked slot IDs, and all excluded C1 line IDs are in `locked_eval_docs.json`; both lists also appear in `census.json`. Document identity is `source:item`, covering every page. The lock is document-disjoint for N1 development; earlier C1 exposure is not erased or claimed absent.")
parts.extend(['## Validation and reproduction',
'''Run `python3 scripts/numerics/n1_step0.py`, then `python3 scripts/numerics/n1_report.py`. The census binds each data/codec/card input by SHA-256. `python3 -m pytest --noconftest -q tests/test_numeric_tokens.py` passes **17 tests**, covering all requested fixtures plus U+0387, en/em dashes, decimal/grouping combinations, original offsets, empty gaps, signs, boundaries, multiple spaces and ambiguous ranges. The initial ordinary pytest invocation hit the existing autouse Torch fixture's x86_64/arm64 library mismatch before any test body; `--noconftest` runs this pure text suite without importing Torch. No model was loaded.

Artifact verification checks exact slot totals, table sums, 600/300 partition sizes, unique slot IDs, C1 exclusion, document disjointness, per-source locked quotas, null truth and unchanged crop hashes across partitions. Frame and document-lock byte hashes are replayed to check determinism. No tokenizer output is a printed-glyph judgment. Step 1 rendering/reading, control creation, fitting and convention adoption remain unperformed.'''])
gazette=sum(s['hyphen_in_4plus_digit_tokens'] for k,s in c['w1']['by_source_era'].items() if k.startswith('gazette'))
last=f"N1S0 READY: tokens {t['tokens']} slots {t['slots']}; hyphen-in-4+digit {t['hyphen_in_4plus_digit_tokens']} (ELSTAT {c['w1']['by_source_era']['elstat']['hyphen_in_4plus_digit_tokens']}, Gazette {gazette}); training labels raised-dot {tr['raised_dot_between_digits']} vs hyphen {tr['hyphen_in_4plus_digit_tokens']}; convention recommend U+00B7; frame 600 / locked 300; tests 17 passed"
parts.append('Final training-label comparison below uses numeric raised-dot inner occurrences versus the 4+-digit inner-hyphen class on the source train labels, not all prose dots/hyphens.')
parts.append(last)
(ROOT/'docs/records/labelfix/N1_STEP0_REPORT.md').write_text('\n\n'.join(parts).replace('|\n\n|', '|\n|')+'\n')
print(last)
