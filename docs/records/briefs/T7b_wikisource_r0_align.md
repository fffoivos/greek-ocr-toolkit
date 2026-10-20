# T7b: finish the T7 harvest by reading page geometry and aligning the human text (gpt-6.1-sol, xhigh, network ON, ≤ USD 0.30, ≤ 60 min)

This continues T7 in this worktree (`sol/wikisource-r0`).

**Why the first pass produced no lines.** T7 selected 5 books / 116 pages and showed zero intersection on 8 keys. It produced **0 lines** because `GOOGLE_APPLICATION_CREDENTIALS` was not set in your environment.

**What is reused.** Keep T7's selection, exclusion receipts and drawn pages exactly. Do not re-draw anything.

## Credentials
- Use Application Default Credentials the same way F2 did: `google.auth.default()` finds the existing ADC file at its default location.
- If `GOOGLE_APPLICATION_CREDENTIALS` is set, it takes precedence.
- Never print, copy or log a credential or its path.
- Processor binding (same as F2): project `ocr-ground-truth-20261008`, EU, processor `9a98b7aca3c19561`, `pretrained-ocr-v2.1-2024-08-07`.

## Do
1. **Read the pages.**
   - One Google read per drawn page: 116 pages × USD 0.0015 = USD 0.174.
   - Reserve each read in `docs/records/harvest/wikisource_r0/google/ledger.jsonl` before the call.
   - Hard cap: USD 0.30.
   - Use this task's own limiter directory. Never use the W1 run root or `~/Projects/collect-v3-data/`.
2. **Align.** Use `greekocr/harvest/wikisource.py` (`strip_wikitext`, the conservative line aligner, template handling), exactly as T7 planned.
   - The label is the human proofread text as printed, in literal and NFC forms.
   - An unresolved template excludes the line.
3. **Write outputs.** In `docs/records/harvest/wikisource_r0/`, write `lines.jsonl` (line_id, page, crop path and hash, label literal/NFC, alignment evidence), `crops/` and `pages.jsonl` with the geometry. Update `RECEIPT.md` with lines per book, the alignment rate per page, and spend.

Commit with the guard (`commit_guard.py --commit`).

The last line must be exactly:
`T7b: done | books: 5 pages: <n> lines: <n> | aligned/page: <x> | usd: <y>`
