# SQ1: owner question. A Google quote standing in for a capital's breathing+accent; what does the frozen sf6 runtime emit? (gpt-6.1-sol, medium; network ON only for the read-only Clariden census in part 3; no .git writes)

**Owner, verbatim:** "nlg--f4b52df5f8130047--s005-l0015 has an interesting failure; does our spell checker correct it? i.e. detection and
substitution of quote as 2 accents if it does not exist independently of accents e.g. a possible failure case is where "῎Α is written
but only "A is detected and is replaced by "Α -> ῎Α when it should be "῎Α".

**The line:**
- crop `~/Projects/collect-v3-data/run/W1/crops/nlg--f4b52df5f8130047--s005-l0015.png` (W1, NLG poly1900);
- Google: "…μεσάνυχτα. "Αδεια διανυκτερεύσεως…" (the C1 card detail: ῎Αδεια → "Αδεια).

**Lead pixel reading:** the print has ONE spacing compound ῎ (psili+acute) before the capital Α, and NO quotation mark. Truth = ῎Αδεια
(as a combining form: Ἄδεια). Google wrote that compound as an ASCII `"`.

**Lead code reading, to confirm by execution:**
- `greekocr/labelfix/text.spacing_breathing` matches only `᾿᾽`, so the SF5/SF6b rules never treat `"` as a breathing;
- `release_gate._render_reading` keeps a mid-line `"` as text;
- `_punctuation` strips LEADING_QUOTES only at line start.

So if the reader adds psili+acute on Α, the expected output is `"Ἄδεια`: quote kept AND marks added.

**Frozen code only:** `greekocr/labelfix` and the 16 policy paths are untouched (digest 6f62925a), and nothing changes in the gate. Python
`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`. A single line on the Mac is fine; anything heavier
goes to the cluster census only.

## 1. Run the frozen pipeline on this one line, locally

- recogniser located letters (E3 full_s0, as used for sf6; if the checkpoint isn't local, use the saved sf6/L1R3 output for this line
  if it exists in the release overlay, or say exactly what can't run);
- S6 detector clusters (`ink.py`/`segmentation.py`/`case.py`) and their owner slots;
- the R1-A reader heads on the Α slot, plus any slot the quote's ink gets assigned to;
- `release_gate` composition → the emitted line, or HOLD, with the rule that fired.

**Report at that position:**
- (a) how many ink clusters the detector finds left of/above Α (one compound, or two: quote + breathing/accent), and which slot owns them;
- (b) what the reader says for Α;
- (c) what the gate emits: one of `"Αδεια`, `Ἄδεια`, `"Ἄδεια`, or HOLD.

Save a detection overlay PNG of the line (the owner-sheet `detection_image`) at `artifacts/sq1/line_overlay.png`.

## 2. Can the rule tell "a quote Google wrote for a breathing" from "a real quote next to a breathing"?

Answer from the code paths, with line references.
- If it cannot, say so plainly, and give the fix shape for the next gate cycle (NOT implemented now): when Google has a quote/apostrophe
  alias immediately before a capital and the release adds a breathing/accent on that capital, keep both only if the ink shows TWO
  separate mark clusters (a quote and a mark); with one cluster, drop the quote (replace); otherwise HOLD.
- Also name the other aliases this affects: `'`, `’`, `´`, `ʼ`, `"`, `“`, `῾`-like quotes.
- Sketch the regression test: this line, plus a real "quote + breathing" line if you can find one in the C1 cards (search the C1
  verdicts/cards for a printed opening quote before a breathing capital).

## 3. Exposure census (read-only, Clariden login node, ≤ a few minutes; the cert is valid until 19:18 Athens; never refresh; auth error = STOP)

On the L1R3/sf6 release overlay (paths in `docs/records/briefs/L1R3_sf6_recompose_job.md` and `SF6c_evidence_certification.md`), count lines
where Google has a quote alias (any of LEADING_QUOTES + `'’´ʼ`) immediately before a Greek capital AND the release adds a breathing
and/or accent on that capital. Split:
- (i) the quote is kept in the release text: the double-marking risk;
- (ii) the quote is removed: say by which rule;
- (iii) per alias character;
- per wave/source.

Also count spacing-breathing (`᾿᾽`) cases handled by SF5/SF6b, for contrast. Give 10 example line ids for (i).

Write a small JSON to `artifacts/sq1/census.json`. Copy the census script into `artifacts/sq1/` and record its sha.

## Report

`docs/records/labelfix/spellcheck/SQ1_QUOTE_BREATHING.md`: the answers to the owner's question in plain words first, then the evidence.

Last line: `SQ1 READY: line emits <...>; clusters <n>; distinguishes <yes|no>; exposure (i) kept-quote+added-mark <n> lines, (ii) <n>; fix shape stated`.
