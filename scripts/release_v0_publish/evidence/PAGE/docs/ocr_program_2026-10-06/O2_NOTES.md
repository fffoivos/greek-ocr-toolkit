# O2 verification pack: notes (7 Oct 2026)

Status: **drawn, machine-adjudicated, machine-subset sealed. Human verification has not started.**
The plan's O2 gate (owner-verified 600 test + 200 dev lines) is still open. The review site is ready for it.

Review site (private, owner only until shared): [review artifact URL withheld from public evidence]

## Files

| path | what |
|---|---|
| `bench/o2_select.py` | deterministic draw (seed 20261007) → `out/o2/sample.jsonl` (+ `sample_test.jsonl`, `sample_dev.jsonl`), `verify_template.csv`, `exclusions_test_dev.txt`, `SELECTION.md`, `selection_receipt.json` |
| `bench/o2_adjudicate.py` | two blind vision transcriptions per line → `out/o2/adjudication.jsonl`, `ADJUDICATION.md`, `adjudication_receipt.json`; raw per-call results in `out/o2/adjudication_raw/{opus,sol}/<id>.json` (resumable cache) |
| `bench/o2_export.py` | `machine`: verify CSV from the adjudication + seal of the agreed subset; `human`: seal from the site's CSV export. Both call `python -m bench.seal` unchanged |
| `bench/o2_site.py`, `bench/o2_site_template.html` | review site: crop sprites (pixel-checked against each crop) + page with line data and machine readings |
| `bench/tests/test_o2.py` | 18 tests: homoglyph/Cyrillic rules, tiered round-robin draw, CLI flag order, verdict logic, machine and human sealing |
| `out/o2/reference_machine{,_test,_dev}.jsonl` + `.seal.json` | machine-agreement references (see below) |

Nothing under `bench/o5_*`, `train/`, `factory/` or `bench/runs/O1d_20261007/final` was modified. Nothing was committed.

## What was drawn

Supply: all 358,471 admitted O1d native rows. Strata are recomputed with `bench.pools.strata`, exactly as `bench/pools.py` assigns them, and cross-checked against all 23,970 pool and supply rows. They are identical. The capped pools are too small inside the chosen documents: European Latin has only 58 capped lines in the O5-reserved documents. The draw therefore uses admitted rows with its own per-document caps. Each sample row records `pool_kind` (`capped`, `uncapped_supply_diagnostic` or `admitted_topup`).

**Document split decision.** O5 (running now) already split the 177 documents into reserved/val/train (`out/o5/build_info.json`). To keep the O2 test out of O5's training documents wherever supply allows:
- test = O5 *reserved* documents (modern Greek is drawn only from these), plus O5-*train* documents only where a stratum has no reserved supply (polytonic, Cyrillic, European-Latin top-up);
- dev = O5 *val* documents only.
Test and dev are document-disjoint (56 documents: 47 test, 9 dev). Every row carries `o5_split`. **331 of the 590 test lines come from O5-train documents**: all 200 polytonic, all 90 Cyrillic and 41 European Latin (per-document table in SELECTION.md). An O5 evaluation on the O2 test must report those strata as train-document lines or exclude them. Modern Greek test (200) and dev (200) are clean with respect to O5 training.

Filters before the draw (counts in SELECTION.md):
- `homoglyph_risk`: a look-alike letter of another script inside a word (ПΑΡΑΡΤΗΜΑ, Frӓnkel, Τhey, πρoσβάσιμα), or a lone Cyrillic look-alike in a non-Cyrillic line (с.35). The crop cannot show which codepoint is meant. This removes 2,695 modern Greek, 14 polytonic, 11 Latin and 20 Cyrillic admitted rows (about 1.2% of the modern Greek pool). It is also a training-label defect signal.
- Cyrillic needs a genuine Cyrillic word: at least 2 Cyrillic letters, one of them without a Latin or Greek look-alike. This excludes `сс.54` and `х` used as a multiplication sign.

| split | stratum | requested | drawn | documents | per-document cap | headings / short / footnote-size |
|---|---|---|---|---|---|---|
| test | modern Greek | 200 | 200 | 35 | 10 | 41 / 32 / 24 (all ≥ 10%) |
| test | polytonic/historical Greek | 200 | 200 | 8 | **50 (25%)** | 6 / 26 / 0 |
| test | European Latin | 100 | 100 | 20 | 8 | 4 / 1 / 0 |
| test | Cyrillic | 100 | **90** | 4 | none | 80 / 3 / 0 |
| dev | modern Greek | 67 + 33 reallocated = 100 | 100 | 9 | 12 | 23 / 15 / 12 |
| dev | polytonic | 67 | 67 | 3 | none | 2 / 0 / 0 |
| dev | European Latin | 33 | 33 | 5 | 8 | 2 / 0 / 0 |
| dev | Cyrillic | 33 | **0** | 0 | | |

Totals: test 590 lines in 47 documents (≥ 30 required), dev 200 lines in 9 documents.

## Supply shortfalls

- **Polytonic.** The real supply is 3,292 admitted lines in 11 documents. The brief said 12 documents and 3,296 lines; the report says 11 and 3,292. 97% of it comes from three pergamos documents (COO_642 1,859, VQP_963 810, EJC_852 468). Test polytonic uses 8 documents with a cap of 50 per document. COO_642, VQP_963 and EJC_852 each give about 50 lines, which is 25% of the stratum per document. The plan's diversity intent is not met. These are modern typeset editions with polytonic text, not historical prints. Polytonic supply has no footnote-size lines and only 8 headings, so the ≥ 10% heading and footnote quota is unmet there. Short lines are 13%.
- **Cyrillic.** The supply is 112 lines in 8 documents. After the homoglyph and genuine-word rules, 90 lines in 4 documents remain, and the test takes all of them. **The 100-line target is unmet (90).** 77 of the 90 come from one document (BHF_655): a Word table of contents whose page fields print the Russian error text "Ошибка! Закладка не определена." So the Cyrillic stratum is mostly one repeated phrase and is weak evidence for Cyrillic OCR. The dev set has no Cyrillic, because no O5-val document has any. Deliberate Cyrillic sourcing (O4) is required.
- European Latin within O5-reserved documents: 89 raw lines. Topped up from O5-train documents (41 lines).

## Machine adjudication (substitute, not verification)

Model A is Claude Opus through `claude -p --model opus`; the reported model is `claude-opus-5-5`. Model B is `gpt-6.1-sol` through `codex exec -i`, medium effort, with the reported model echoed. Both models **can see images**. Each was checked on one crop first, then run on all 790 lines with 0 failures after retries. Both transcribe blind; the proposal is never shown to them. Comparison uses NFC and whitespace collapsing, otherwise exact. `verified_machine` means both transcriptions equal the proposal and both models call the crop a single clean line. The reported Claude CLI cost was $153 (plus $0.64 for the smoke test).

| split | stratum | lines | verified_machine | flagged | Opus = P | Sol = P | both models agree, ≠ P |
|---|---|---|---|---|---|---|---|
| test | modern Greek | 200 | 175 (88%) | 25 | 92% | 90% | 10 |
| test | polytonic | 200 | 117 (58%) | 83 | 79% | 66% | 17 |
| test | European Latin | 100 | 90 (90%) | 10 | 96% | 90% | 3 |
| test | Cyrillic | 90 | 29 (32%) | 61 | 48% | 50% | 20 |
| dev | modern Greek | 100 | 90 (90%) | 10 | 96% | 91% | 4 |
| dev | polytonic | 67 | 36 (54%) | 31 | 78% | 63% | 4 |
| dev | European Latin | 33 | 31 (94%) | 2 | 94% | 97% | 1 |
| all | | 790 | **568 (72%)** | **222** | 84% | 77% | 59 |

What the flags are, measured on the diffs of the 222 flagged lines:
- 107 involve letters, marks or digits.
- 49 involve only spacing. These are mostly the gap between leader dots and text in BHF_655, superscript footnote numbers, and letter-spaced headings such as FVA_142.
- 48 involve only punctuation or punctuation plus spacing, mostly dot-leader counts.
- 13 are clean-line objections only.

The models are wrong in many of these. For example, both read a printed acute in περί as a grave, and Opus drops the space after a superscript footnote number. The 59 "both agree, ≠ P" lines are the best candidates for real label defects. They also expose policy questions the owner must settle:
- koronis/psili `᾽ ᾿` versus apostrophe `’` for elision (17 polytonic lines);
- Greek versus Latin capitals that look identical inside the other script (Α/A, Ι/I, Μ/M, H/Η; not caught by the word-internal homoglyph rule);
- compatibility characters `∆` U+2206 versus `Δ` and `µ` U+00B5 versus `μ`;
- Greek numeral sign `͵` versus comma;
- breathing and accent readings (ἁ/ἀ, ὑ/ὐ, ᾖ/ἢ, ἀ/ἄ).
The site shows both readings with highlighted diffs and code points.

Full list: `out/o2/ADJUDICATION.md`.

## Machine-sealed reference (now)

`seal.py` refuses pending rows, as expected; `verify_machine.csv` with flagged rows pending is refused with "unverified row". So the agreed subset is sealed separately with `--verified-by "machine:opus+gpt-6.1-sol agreement"`:

| reference | lines | per stratum |
|---|---|---|
| `out/o2/reference_machine.jsonl` | 568 | both splits |
| `out/o2/reference_machine_test.jsonl` | 411 (46 documents) | modern 175, polytonic 117 (6 documents), Latin 90, Cyrillic 29 |
| `out/o2/reference_machine_dev.jsonl` | 157 (9 documents) | modern 90, polytonic 36, Latin 31 |

Each has `.seal.json`, plus the exact subset sample and CSV that were sealed (`*.sample.jsonl`, `*.verify.csv`). `bench.score.load_sealed` accepts them. Receipt: `out/o2/reference_machine.receipt.json`.

## Re-seal with human verdicts

1. Review on the site. Correct (C) seals the proposed text. Fixed (⌘/Ctrl+Enter) seals your edited NFC text. Bad crop (B) drops the line. Verdicts are shared through the artifact database and start empty.
2. Export tab → Copy CSV (or Save) → `out/o2/verify_human.csv`. It has the same columns as `verify_template.csv`.
3. `.venv/bin/python -m bench.o2_export human --csv out/o2/verify_human.csv --verified-by "owner:<name>"`
   This writes `out/o2/reference_human{,_test,_dev}.jsonl` + seals and `reference_human.receipt.json`, which lists dropped bad crops and corrected lines. It refuses while lines are pending unless `--allow-subset` is given.
   Underneath, it runs `python -m bench.seal <subset sample> <subset csv> --out out/o2/reference_human_test.jsonl --verified-by "owner:<name>"` for each split.
4. Bad crops shrink the sealed sets below 600/200. Refilling them with a top-up draw from the same documents is not implemented yet.

## What "machine-verified" does and does not establish

It establishes three things:
- two independent vision models, from different vendors and run blind, read exactly the PDF text-layer string from the crop pixels;
- both judged the crop a single clean line;
- the sealed bytes, crops and attestation are bound by hashes.

It does not establish human ground truth. Both models share language priors: they "correct" toward the expected word, for example μεγεθῶν for a printed μεγεθών. So agreement with a proposal that has the expected spelling is weaker evidence than it looks, and a shared misreading that happens to equal the proposal would pass. Neither model checks the stratum label or codepoint identity for look-alikes. A Latin `A` in Greek text equals the proposal only because the model happened to choose the same script.

The agreed subset is also **not a representative sample**. It keeps the easy lines and drops most hard ones: 58% of polytonic and 32% of Cyrillic test lines survive, and the dropped lines are exactly the accent, breathing and spacing cases a benchmark most needs. Polytonic loses two documents. Scores on `reference_machine*` are therefore optimistic, and the strata are not comparable to the planned 200/200/100/100. Use it for plumbing and provisional comparisons only. Headline O3 numbers need the human seal.
