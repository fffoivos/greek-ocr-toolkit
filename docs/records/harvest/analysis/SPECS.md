# Analysis specs for the collected pool (15 Oct 2026) — defined by the coordinator, executed by Opus agents

Pool: docs/records/harvest/collection/admitted_all.jsonl (293,439 admitted lines; fields: id, wave, source, book/doc key, year, decade, script_class, split, label,
confidence, bbox, crop path (relative to the repo), crop sha/width/height). Page context: docs/harvest/<wave>/records.jsonl (every Google line incl. rejected)
and rejected.jsonl; page PNGs and crops under docs/records/harvest/harvest_big/<wave>/ (round 1 = docs/records/harvest/harvest_big/round1/).
Python: use the repo venv `.venv/bin/python` (Pillow, numpy, pyarrow available). Stream the jsonl; never load all crops into memory. Write ONLY under
docs/records/harvest/analysis/<aspect>/ (your aspect folder). No git commands. No network. No Google calls.

Principle: every detector reports a measured distribution and flags outliers relative to the right reference group — the line's script class, and for
per-book scores the population of books of the same script class — never a hand-picked constant unless the spec states one. Every flag carries a `reason`
string with the measured value and the reference quantile. Output per aspect: `line_flags.jsonl.gz` (id → features + flags), `book_stats.jsonl` (per source
key: medians/p10/p90 of each feature, counts of flagged lines, hard flags, z-scores vs same-class books), `REPORT.md` (distributions as tables, flag rates per
wave and class, 20 example lines per flag type with label + crop path, what you judged and why).

## Aspect A — language and script
Per line: letter shares per script (Greek / Latin / Cyrillic / other) and any residual other-script characters; mixed-script words (words whose letters come
from ≥2 scripts; split on space = - / and punctuation; Roman numerals excluded) — should be zero after admission, count anyway; language guess of the line:
el (Greek letters majority) / for Latin-script lines la, fr, de, en, it by small function-word lists / for Cyrillic ru, bg, sr by function words / unknown;
for Greek lines: polytonic mark density (combining breathings/perispomeni/iota-subscript/grave per Greek letter after NFD), tonos-only share, katharevousa vs
demotic cues (ἐν, εἰς, ὑπό, τοῦ/τῆς genitives in -εως, verb endings -ουσι, final -ν on articles vs demotic σε, στον, -ουν). Hard flags: line language ≠ the
book's majority language (except in the mixed wave); other-script residue; polytonic-class book with mark density below the class p5; Greek book with > 2 %
lines guessed as another language.

## Aspect B — content and style
Per line: digit share, punctuation share, symbol share, all-caps share, token count, mean word length, longest token, repeated-character runs (≥4 identical),
numeric-table pattern (≥3 numbers separated by spaces/tabs), bibliographic pattern (year in parentheses, "pp.", "Bd.", "vol.", "σ." + number), running-title /
page-number pattern (short line, all-caps or digits, bbox in the top or bottom 8 % of the page), final-sigma errors (σ at word end; ς inside a word), spacing
apostrophes (U+1FBF, U+1FBD, U+0384, U+2019 standing alone), hyphen at line end, verse-like books (short lines with capital initials), dictionary-like lines
(headword + dash/colon). Hard flags per book: > 30 % digit-heavy lines, > 30 % running-title/page-number lines, final-sigma error rate above class p95,
all-caps share above class p95.

## Aspect C — length, geometry and label-quality proxies
Per line: label length (chars), crop width/height, chars per 100 px of width, box height relative to the page's median counted-line height, box width relative
to the page's text width, vertical position, box aspect; Google symbol count vs label length mismatch (from records.jsonl); mean and min confidence; two
out-of-vocabulary rates: (1) the pool's own vocabulary — word support = number of DISTINCT books across all waves containing the NFC-lowercased word, OOV =
support ≤ 1; (2) for polytonic lines, the vocabulary of the Wikisource human transcriptions under docs/records/harvest/wikisource/. Hard flags: chars-per-100-px outside
[class p2, class p98]; confidence median of a book below the class p5; OOV share of a book above the class p95; box height ratio > 1.7 or < 0.5 for > 10 % of
a book's lines.

## Aspect D — duplicates and page structure
Exact duplicate labels across different books (list pairs; expected for running titles and short formulae, suspicious for sentences ≥ 25 chars); within-book
duplicate labels across pages; near-duplicate pages (same source, adjacent page numbers, label-set Jaccard ≥ 0.6 — two-page spreads read twice or the same
scan fetched twice); per page: admitted/rejected ratio, rejection-reason mix, line count vs the wave median, column count (from bbox clustering), share of
lines whose box crosses two columns (width > 0.8 of the page text width on a two-column page). Hard flags: any near-duplicate page pair; page line count above
the wave p99 or below p1; > 10 % column-crossing lines in a two-column book.

## Aggregation (after A–D) — book profiles, ranking, dossiers
Merge the four book_stats files per source key; per aspect one score = number of features beyond 2σ vs same-class books; `suspicion` = aspects beyond 2σ + hard
flags; rank. Outputs under docs/records/harvest/analysis/: book_profiles.jsonl, ANOMALIES.md (per-aspect distributions, top-60 suspicious books with reasons, per-wave
anomaly rates), and dossiers/<rank>_<source>_<key>/ for the top-60 plus every hard-flag book (cap 120): dossier.json (metadata, scores, reasons, 40 sample
lines = 20 random admitted + 20 most anomalous: label, confidence, features, crop path), sheet.jpg (those 40 crops stacked with labels under them, one type
size, numbered), page.jpg (one compiled page image of that book copied from the wave's compiled folder), question.md (asks for KEEP / DROP_BOOK /
DROP_PATTERN with a rule / RELABEL with what is systematically wrong, plus a confidence; the adjudicator sees sheet.jpg and page.jpg).

## Adjudication (LLM pass over the dossiers)
One decision per dossier, as decision.json {decision, confidence, rule_or_pattern, evidence (line numbers on the sheet), notes}; the coordinator compiles the
decisions table for the owner.
