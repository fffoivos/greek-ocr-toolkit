# N1 step 0: numeric-separator census + convention check (gpt-6.1-sol, medium, network OFF; no .git writes; Mac CPU, no models)

Plan: `docs/records/labelfix/N1_NUMERIC_SEPARATORS_PLAN.md`. Do step 0 only.

**Inputs (read-only):**
- W1 `~/Projects/collect-v3-data/run/W1/features.jsonl` (Google text per line);
- the ELSTAT and Gazette sources;
- the C1 cards and verdicts (`~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/`: c1_results.json `separator`
  entries, verdict files);
- the E3/collection v2 training labels (find the paths in the toolkit docs; read-only);
- the codec `~/Projects/greek-ocr-toolkit/greekocr/_vendor/codec/v1.json` and codec v2 if present.

**Do:**
1. **Tokenizer** (`greekocr/numerics/tokens.py`, new package, with tests): numeric tokens as in the plan (digit runs joined by
   separator candidates `·` U+00B7, `·` U+0387, `.`, `,`, `-`, `–`, `—`, space). Output: slots (inner gaps + 2 boundaries) and a grammar
   position label: thousands (groups of 3), decimal (1–2 trailing digits after `,` or `.`), range (year or page pattern), table boundary,
   or other.
2. **Census per source/era** (ELSTAT, Gazette 1982–85, Gazette 1986–90, plus every other W1 source with ≥ 100 numeric tokens):
   - token and slot counts;
   - Google glyph × grammar position table;
   - the hyphen-inside-4+-digit-token count (the suspected raised-dot → hyphen class);
   - the same table on the E3 / collection v2 training labels, showing what the recogniser has been taught.
3. **Convention check:** where U+00B7 and U+0387 occur in labels and codecs, which of them a raised dot should map to, and whether any
   training label already uses either between digits. Recommend; the lead rules.
4. **Sampling frame** for step 1 (about 600 slots), stratified as in the plan, seed 20261017. Write the frame only; do NOT render or
   read anything yet. Exclude C1 card lines and reserve a locked evaluation stratum of about 300 slots from separate documents.
   Record both document lists.

**Outputs:**
- `artifacts/n1/census.json`, `artifacts/n1/frame_step1.jsonl`, `artifacts/n1/locked_eval_docs.json`;
- report `docs/records/labelfix/N1_STEP0_REPORT.md`.

**Tests:** the tokenizer on fixtures (`4·547·331`, `555,6`, `0-499`, `1985-1990`, `3.652.450`, `12 345`, table `97.400 | 3.652.450`).

Last line: `N1S0 READY: tokens <n> slots <n>; hyphen-in-4+digit <n> (ELSTAT <n>, Gazette <n>); training labels raised-dot <n> vs hyphen <n>; convention recommend <U+00B7|U+0387>; frame 600 / locked <n>; tests <n> passed`.
