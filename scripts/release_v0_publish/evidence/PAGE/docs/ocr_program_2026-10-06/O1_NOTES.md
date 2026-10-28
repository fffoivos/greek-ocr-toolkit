# O1 execution notes — 6 October 2026

**Cycles 1–3 are archived below. Current Cycle 4 results and inspection, followed by the O4-fix LABEL-policy replay, are appended at the end.**

**Executed candidate tooling, not a sealed real-document benchmark.** Owner transcription verification, source-disjoint train/dev/test selection, and O2 sealing remain pending. No recogniser training, network access, installs or git history changes.

Full final extraction processed **177 repaired PDFs / 18,662 pages** and **3 scans / 268 pages**, at 200 dpi. Every page has a coverage receipt. Native candidates: **697,350**, admitted **418,143**, rejected **279,207**. Unlabelled scan candidates: **8,939**, all rejected with `no_text`; scan text-layer character count: **0**. Pages with no projection/native candidates: native 57, scans 0.

Final extraction wall time: 372.67 seconds with four worker processes. Source PDF, source-manifest, code and records hashes are in `bench/runs/O1_20261006/final/`. Intermediate debug runs do not contribute to these counts.

## Admission accounting

Counters overlap; their sum is not the rejected-row count. All rejected rows and crops remain in the coverage denominator.

| Named rule | Native candidates | Scan candidates | Overall |
|---|---:|---:|---:|
| pua | 20,630 | 0 | 20,630 |
| control | 11,248 | 0 | 11,248 |
| replacement | 9,015 | 0 | 9,015 |
| tounicode_residue | 0 | 0 | 0 |
| ligature_artifact | 0 | 0 | 0 |
| letter_run | 144 | 0 | 144 |
| dictionary_collapse | 0 | 0 | 0 |
| crop_height | 4,860 | 524 | 5,384 |
| aspect_ratio | 149,571 | 36 | 149,607 |
| overlapping_lines | 78,608 | 837 | 79,445 |
| rotated_text | 42,071 | 0 | 42,071 |
| ink_bbox_mismatch | 51,484 | 0 | 51,484 |
| multiline_ink | 132 | 7 | 139 |
| near_duplicate | 119,871 | 0 | 119,871 |
| no_text | 4,496 | 8,939 | 13,435 |
| invalid_char_geometry | 0 | 0 | 0 |
| blank_ink | 5,445 | 27 | 5,472 |

The dictionary-collapse path was unit-tested but no dictionary was supplied to this corpus pass. Its zero counter is not a spacing-quality result. The long-letter-run and compatibility-ligature rules were active.

Astra replay: 300 original text-run unions re-rendered at 200 dpi; 49 rejected. It reproduces all **17 PUA** and **6 control** cases, and rejects all seven named geometry counterexamples. The coordinate conversion is explicit: Astra's `bbox_pt` is top-left, PDFium's boxes are bottom-left. This replay is diagnostic and separate from the newly grouped line pools.

| Astra counterexample | O1 rejection reasons |
|---|---|
| R023 | control, multiline_ink |
| R081 | control, multiline_ink |
| R171 | control, crop_height |
| R058 | crop_height, aspect_ratio, rotated_text |
| R118 | crop_height, rotated_text |
| R159 | crop_height, aspect_ratio, rotated_text |
| R277 | crop_height, aspect_ratio, rotated_text |

## Candidate pools

Strata overlap. The 2% cap is enforced on actual pool size, with no duplication. Empty compliant pools have a separate `.supply.jsonl` diagnostic inventory. Polytonic presence does not establish historical era.

| Stratum | Raw admitted supply | Supply documents | Capped pool | Pool documents | Largest doc share |
|---|---:|---:|---:|---:|---:|
| modern_greek | 372,551 | 177 | 5,000 | 177 | 0.58% |
| polytonic_historical_greek | 3,507 | 12 | 0 | 0 | 0.00% |
| european_latin | 781 | 86 | 402 | 86 | 1.99% |
| mixed_script | 64,256 | 177 | 5,000 | 177 | 0.58% |
| headings | 34,150 | 177 | 5,000 | 177 | 0.58% |
| footnotes_small | 3,695 | 91 | 1,517 | 91 | 1.98% |
| short_lines | 43,203 | 177 | 5,000 | 177 | 0.58% |
| cyrillic | 125 | 8 | 0 | 0 | 0.00% |

Host counts for raw supply and capped pools are recorded separately:

| Stratum | Raw supply by host | Capped pool by host |
|---|---|---|
| modern_greek | apothesis.eap.gr: 33,099; dspace.lib.ntua.gr: 81,041; dspace.lib.uom.gr: 2,658; hellanicus.lib.aegean.gr: 47,011; ktisis.cut.ac.cy: 6,015; pergamos.lib.uoa.gr: 124,266; repository.edulll.gr: 6,430; repository.ihu.gr: 69,024; users.sch.gr: 3,007 | apothesis.eap.gr: 473; dspace.lib.ntua.gr: 1,109; dspace.lib.uom.gr: 29; hellanicus.lib.aegean.gr: 598; ktisis.cut.ac.cy: 84; pergamos.lib.uoa.gr: 1,508; repository.edulll.gr: 58; repository.ihu.gr: 1,113; users.sch.gr: 28 |
| polytonic_historical_greek | apothesis.eap.gr: 98; hellanicus.lib.aegean.gr: 1; pergamos.lib.uoa.gr: 3,375; repository.ihu.gr: 33 | none |
| european_latin | apothesis.eap.gr: 103; dspace.lib.ntua.gr: 47; hellanicus.lib.aegean.gr: 40; ktisis.cut.ac.cy: 8; pergamos.lib.uoa.gr: 529; repository.edulll.gr: 5; repository.ihu.gr: 42; users.sch.gr: 7 | apothesis.eap.gr: 73; dspace.lib.ntua.gr: 44; hellanicus.lib.aegean.gr: 35; ktisis.cut.ac.cy: 8; pergamos.lib.uoa.gr: 207; repository.edulll.gr: 5; repository.ihu.gr: 23; users.sch.gr: 7 |
| mixed_script | apothesis.eap.gr: 4,353; dspace.lib.ntua.gr: 16,044; dspace.lib.uom.gr: 418; hellanicus.lib.aegean.gr: 6,461; ktisis.cut.ac.cy: 1,317; pergamos.lib.uoa.gr: 21,933; repository.edulll.gr: 548; repository.ihu.gr: 13,076; users.sch.gr: 106 | apothesis.eap.gr: 479; dspace.lib.ntua.gr: 1,091; dspace.lib.uom.gr: 29; hellanicus.lib.aegean.gr: 599; ktisis.cut.ac.cy: 84; pergamos.lib.uoa.gr: 1,519; repository.edulll.gr: 58; repository.ihu.gr: 1,112; users.sch.gr: 29 |
| headings | apothesis.eap.gr: 2,813; dspace.lib.ntua.gr: 8,661; dspace.lib.uom.gr: 214; hellanicus.lib.aegean.gr: 3,781; ktisis.cut.ac.cy: 678; pergamos.lib.uoa.gr: 10,612; repository.edulll.gr: 414; repository.ihu.gr: 6,888; users.sch.gr: 89 | apothesis.eap.gr: 487; dspace.lib.ntua.gr: 1,119; dspace.lib.uom.gr: 29; hellanicus.lib.aegean.gr: 589; ktisis.cut.ac.cy: 87; pergamos.lib.uoa.gr: 1,472; repository.edulll.gr: 58; repository.ihu.gr: 1,130; users.sch.gr: 29 |
| footnotes_small | apothesis.eap.gr: 344; dspace.lib.ntua.gr: 677; hellanicus.lib.aegean.gr: 482; ktisis.cut.ac.cy: 65; pergamos.lib.uoa.gr: 1,375; repository.edulll.gr: 178; repository.ihu.gr: 574 | apothesis.eap.gr: 92; dspace.lib.ntua.gr: 389; hellanicus.lib.aegean.gr: 192; ktisis.cut.ac.cy: 43; pergamos.lib.uoa.gr: 399; repository.edulll.gr: 60; repository.ihu.gr: 342 |
| short_lines | apothesis.eap.gr: 3,700; dspace.lib.ntua.gr: 10,106; dspace.lib.uom.gr: 148; hellanicus.lib.aegean.gr: 5,515; ktisis.cut.ac.cy: 793; pergamos.lib.uoa.gr: 14,043; repository.edulll.gr: 620; repository.ihu.gr: 8,113; users.sch.gr: 165 | apothesis.eap.gr: 476; dspace.lib.ntua.gr: 1,100; dspace.lib.uom.gr: 29; hellanicus.lib.aegean.gr: 595; ktisis.cut.ac.cy: 84; pergamos.lib.uoa.gr: 1,500; repository.edulll.gr: 57; repository.ihu.gr: 1,131; users.sch.gr: 28 |
| cyrillic | dspace.lib.ntua.gr: 2; hellanicus.lib.aegean.gr: 37; pergamos.lib.uoa.gr: 5; repository.ihu.gr: 81 | none |

## Codec v1 coverage

| Group | Raw NFD atoms absent (capped pools) | Probe raw atoms absent (before v1 folds; not corpus) |
|---|---|---|
| Greek polytonic | U+0023 #, U+0024 $, U+003C <, U+003E >, U+005F _, U+0060 `, U+007B {, U+007C |, U+007D }, U+007E ~, U+00B1 ±, U+00BD ½, U+00D7 ×, U+02D9 ˙, U+02DA ˚, U+0338 ̸, U+0384 ΄, U+1FBD ᾽, U+2016 ‖, U+2032 ′, U+2070 ⁰, U+207B ⁻, U+2103 ℃, U+2116 №, U+2190 ←, U+2194 ↔, U+2202 ∂, U+2208 ∈, U+2212 −, U+2217 ∗, U+2219 ∙, U+2220 ∠, U+222A ∪, U+2248 ≈, U+25A1 □, U+25E6 ◦, U+27F9 ⟹ | U+03F2 ϲ |
| Latin marks | U+0023 #, U+0024 $, U+003C <, U+003E >, U+0040 @, U+005E ^, U+005F _, U+007B {, U+007C |, U+007D }, U+007E ~, U+00A2 ¢, U+00A8 ¨, U+00A9 ©, U+00AC ¬, U+00AE ®, U+00B2 ², U+00B4 ´, U+00B9 ¹, U+00BC ¼, U+00BD ½, U+00D7 ×, U+00D8 Ø, U+00F8 ø, U+0110 Đ, U+0111 đ, U+0131 ı, U+0141 Ł, U+0142 ł, U+0272 ɲ, U+0286 ʆ, U+028E ʎ, U+02A4 ʤ, U+02D9 ˙, U+0307 ̇, U+030B ̋, U+0328 ̨, U+0384 ΄, U+2009  , U+2011 ‑, U+2016 ‖, U+207B ⁻, U+2103 ℃, U+2190 ←, U+2191 ↑, U+2192 →, U+2193 ↓, U+2202 ∂, U+2207 ∇, U+2208 ∈, U+2212 −, U+2217 ∗, U+2219 ∙, U+222A ∪, U+222B ∫, U+2261 ≡, U+2264 ≤, U+2265 ≥, U+2286 ⊆, U+25C4 ◄ | U+00F0 ð, U+00F8 ø, U+00FE þ, U+0111 đ, U+0131 ı, U+0140 ŀ, U+0142 ł, U+014B ŋ, U+0307 ̇, U+030B ̋, U+0326 ̦, U+0328 ̨ |
| Cyrillic incl Serbian Macedonian | none | U+0402 Ђ, U+0405 Ѕ, U+0408 Ј, U+0409 Љ, U+040A Њ, U+040B Ћ, U+040F Џ, U+0452 ђ, U+0455 ѕ, U+0458 ј, U+0459 љ, U+045A њ, U+045B ћ, U+045F џ |

Unique lines across capped pools: **18,514**. Strict NFD/whitespace probe rejects **601**; actual v1 normalization (parsed Greek folds plus whitespace policy) rejects **565** whole lines. These are character representability probes, not the factory's complete ingest gate. Sparse-supply diagnostics contain 3,632 unique lines, of which 39 fail v1 normalization/encoding.

The table inventories raw NFD atoms before codec folds; carrier-script groups can include punctuation/symbols and modern Greek. For example, the Greek lunate-sigma probe is encodable after the existing v1 fold and does not establish a Greek orthographic gap. Atom inventory: 247 atoms, loaded from `factory/src/codec.rs`; SHA256 `2598774dc8efdc056265280a9b4b4c043c4eb73c5494faf9c98840ccda670632`. Full precomposed-character and NFD-atom frequency/support tables, per-stratum counts and separate language probes are in `bench/runs/O1_20261006/codec_coverage.json`. Absent corpus scripts are missing coverage, not support certification.

## Owner verification pack

Draw seed 20261006; 259 unique candidates; 13 contact sheets (up to twenty rows each). All statuses remain pending; **no real reference was sealed**.

- Sample: `bench/runs/O1_20261006/verification/sample.jsonl`
- CSV: `bench/runs/O1_20261006/verification/verify_template.csv`
- Sheet: `/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/bench/runs/O1_20261006/verification/sheets/sheet-001.png`
- Sheet: `/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/bench/runs/O1_20261006/verification/sheets/sheet-002.png`
- Sheet: `/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/bench/runs/O1_20261006/verification/sheets/sheet-003.png`
- Sheet: `/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/bench/runs/O1_20261006/verification/sheets/sheet-004.png`
- Sheet: `/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/bench/runs/O1_20261006/verification/sheets/sheet-005.png`
- Sheet: `/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/bench/runs/O1_20261006/verification/sheets/sheet-006.png`
- Sheet: `/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/bench/runs/O1_20261006/verification/sheets/sheet-007.png`
- Sheet: `/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/bench/runs/O1_20261006/verification/sheets/sheet-008.png`
- Sheet: `/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/bench/runs/O1_20261006/verification/sheets/sheet-009.png`
- Sheet: `/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/bench/runs/O1_20261006/verification/sheets/sheet-010.png`
- Sheet: `/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/bench/runs/O1_20261006/verification/sheets/sheet-011.png`
- Sheet: `/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/bench/runs/O1_20261006/verification/sheets/sheet-012.png`
- Sheet: `/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/bench/runs/O1_20261006/verification/sheets/sheet-013.png`

Sheets 003 and 004 were visually inspected for crop/transcript layout. This is not owner transcription verification.

## Apple Vision / Live Text comparator

Public `VNRecognizeTextRequest` via the existing Swift batch harness: attempted 50 crops; process exit 0; 50 prediction rows, 50 row failures, 0 nonempty outputs. OCR process wall time including Swift startup: 4.011 seconds. macOS 26.5.1, arm64, request revision 3.

Configuration: `{"recognitionLevel": "accurate", "usesLanguageCorrection": true, "automaticallyDetectsLanguage": false, "recognitionLanguages": ["en-US", "fr-FR", "de-DE", "it-IT", "es-ES", "pt-BR"], "maxCandidates": 1}`. Raw outputs, capabilities, crop hashes, exact command, per-line timings and errors are beside `bench/runs/O1_20261006/livetext_predictions.jsonl`. This is public Vision API output; UI Live Text equivalence was not tested.

No real CER/WER is reported: candidate PDF text remains unverified and the scorer refuses it. Failed engine rows require a successful runtime rerun before any sealed-set score.
Observed engine errors: Vision request failed: nilError. Root cause is unconfirmed; process success does not mean successful OCR.
A bounded single-crop RGB probe with the existing simpler Swift harness, en-US only and correction disabled, also failed with Foundation._GenericObjCError.nilError (exit 133). Its stderr is retained; no recovery or root-cause claim is made.
Sum of per-crop Vision request times: 2.868 seconds; these exclude Swift startup and are not full-page latency.

## Validation and limitations

Final receipt reconciliation: `bench/runs/O1_20261006/validation.json` verified all 180 source/code/record hashes, all 706,289 rows and per-document PNG counts, and decoded/verified the first and last PNG of each document (360 PNGs). Pool caps were independently checked. This is artifact integrity validation, not transcription validation.

Tests actually executed: `bench/runs/O1_20261006/tests.txt`:

```text
.......................................                                  [100%]
39 passed in 0.35s
```

The suite covers every named admission rule, Astra PUA/control examples, bad pixel crops, accents versus multiple baselines, dictionary collapse, near-duplicates, short-line retention, exact cap feasibility, codec missing atoms, strict mark order, script confusion, reference/crop tampering, incomplete prediction IDs, pending verification refusal, a rendered real PDFium extraction fixture, and the scan float/Otsu contract.

The corpus is overwhelmingly native modern typography; U+1Fxx quotations do not certify historical scan supply. Sparse Cyrillic/polytonic strata require deliberate sourcing. Geometry/spacing are conservative heuristics and may both reject legitimate content and miss label/crop failures. Scan projections have no human labels or char boxes and do not certify single baselines, cells, rotation, completeness or reading order. Crops are native 200-dpi candidates, not 48-pixel factory strips. Rights/genre/era and document-family holdouts remain owner tasks; manifests do not authenticate these automatically. Reference seal hashes attest integrity, not reviewer identity. Read [O1_FORMATS.md](O1_FORMATS.md) for precise rules, proxies, metric denominators, adapters and limitations.

## Exact executed commands

Run from `~/Projects/greek-page-ocr`. The supplied GlossAPI Python was used; the repo primary environment lacked pypdf. The wrapper invoked all source pages; no page sampling was used for final counts.

```sh
#!/bin/zsh
# Executed from /Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr.
PY=/Users/foivoskarounos-zamparloukos/Projects/glossapi-development/.venv-exp/bin/python
RUN=bench/runs/O1_20261006
CAMPAIGN=/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/compute_reduction_20261006
SCANS=/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/reports/artifacts-20260407-ocr-box/pdfs
AUDIT=/Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/ASTRA-program/audit
"$PY" -m bench.run_corpus --repaired "$CAMPAIGN/e1_final/repaired" --manifest "$CAMPAIGN/data/sample_manifest.csv" --scans "$SCANS/VJM_898.pdf" "$SCANS/VZE_306.pdf" "$SCANS/XEK_118.pdf" --out "$RUN/final" --workers 4 > "$RUN/final.log" 2>&1
"$PY" -m bench.audit_probe "$AUDIT" --out "$RUN/astra_replay" > "$RUN/astra_replay.log" 2>&1
"$PY" -m bench.pools "$RUN/final/native/records" --out "$RUN/pools" > "$RUN/pools.log" 2>&1
"$PY" -m bench.sheets "$RUN/pools" --out "$RUN/verification" --include-sparse-supply > "$RUN/sheets.log" 2>&1
"$PY" -m bench.codec_coverage "$RUN/pools" --out "$RUN/codec_coverage.json" > "$RUN/codec_coverage.log" 2>&1
"$PY" -m bench.livetext_runner --sample "$RUN/verification/latin_sample.jsonl" --out "$RUN/livetext_predictions.jsonl" --limit 50 > "$RUN/livetext.log" 2>&1
"$PY" -m bench.scorer_smoke --out "$RUN/scorer_fixture"
"$PY" -m bench.score "$RUN/scorer_fixture/predictions.jsonl" "$RUN/scorer_fixture/reference.jsonl" --out "$RUN/scorer_fixture/results.json" --checkpoint synthetic-fixture-no-model --decoder literal --runtime "$RUN/scorer_fixture/runtime.json"
# Expected refusal, exit 2. This is not a scored result.
"$PY" -m bench.score "$RUN/livetext_predictions.jsonl" "$RUN/verification/latin_sample.jsonl" --out "$RUN/forbidden_real_score.json" --checkpoint apple-vision-public --decoder public-accurate-correction --runtime "$RUN/livetext_predictions.runtime.json" > "$RUN/unsealed_refusal.txt" 2>&1
PYTHONDONTWRITEBYTECODE=1 "$PY" -m pytest bench/tests -q -p no:cacheprovider > "$RUN/tests.txt" 2>&1
"$PY" -m bench.validate_run "$RUN" > "$RUN/validation.log" 2>&1
"$PY" -m bench.report "$RUN" --out docs/ocr_program_2026-10-06/O1_NOTES.md

# Read-only public API capability probe (executed before the OCR sample).
swift -module-cache-path "$RUN/swift-module-cache" /Users/foivoskarounos-zamparloukos/Projects/livetext-ocr-re/scripts/vision_capabilities.swift > "$RUN/vision_capability_probe.json" 2> "$RUN/vision_capability_probe.stderr.txt"
# Bounded single-crop probe: RGB, English only, correction off; observed exit 133.
"$PY" - <<'PY'
from bench.common import read_rows
from PIL import Image
r = next(read_rows("bench/runs/O1_20261006/verification/latin_sample.jsonl"))
Image.open(r["crop_path"]).convert("RGB").save("bench/runs/O1_20261006/vision_rgb_probe.png")
PY
swift -module-cache-path "$RUN/swift-module-cache" /Users/foivoskarounos-zamparloukos/Projects/livetext-ocr-re/scripts/vision_ocr.swift "$RUN/vision_rgb_probe.png" accurate no-language-correction --languages en-US > "$RUN/vision_rgb_probe.json" 2> "$RUN/vision_rgb_probe.stderr.txt"
```

Scorer refusal output:

```text
reference is unsealed: missing .seal.json
```

Positive scorer execution used only synthetic test-fixture references; no trained recogniser or sealed real benchmark accuracy is claimed.

## Cycle 2 — CP-O1 repair, completed 7 October 2026

**Current output: `bench/runs/O1b_20261007/`. The Cycle 1 counts above and the first repair attempt `O1b_20261006` are superseded for admission/pools. All artifacts remain unsealed.**

Physical-baseline association now precedes ordering and admission. PDF-generated CR/LF do not split printed lines. Larger glyphs anchor bands, raised/lowered glyphs attach by baseline/size/x proximity, and all glyph boxes determine the crop extent. Each baseline sorts left-to-right. Eight median page glyph widths is the gap threshold; per-page x-histograms identify persistent empty gutters (at least eight bins and six baselines on each side). Unconfirmed wide same-baseline splits reject both pieces. Sparse table/column layouts may therefore reject conservatively. The full thresholds and record diagnostics are in [O1_FORMATS.md](O1_FORMATS.md).

The label is compared with the spatial NFC union of **all page PDF characters intersecting the padded crop**, including partial intersections from other groups. `crop_text_mismatch` rejects differences. `missing_baseline_neighbour` rejects omitted nearby glyphs and unconfirmed wide same-baseline pieces. `fragment_short`, `fragment_no_letters`, and `fragment_symbol_dominated` reject leftover fragments. `label_spacing_gap` rejects visible word gaps at run boundaries without a PDF space. These rules reject uncertainty rather than silently editing candidate text.

Reviewer evidence is copied under `bench/tests/fixtures/cp_o1/`: the five original crops, reviewer context/order evidence, five one-page PDF fixtures and original PDFium character metadata. `test_cp_o1.py` exercises all five known cases, the HYI reading-order line, WDO partial-R intersections/bounded disagreements, the column histogram and three additional inspection regressions. Eleven cases failed before the first fix; three newly found cases failed before the second adjustment. The scoped O1 suite passed **57 tests**; the final complete `bench/tests` result (including concurrent Wikisource tests) is retained in `tests.txt`. Final whole suite: **100 passed in 11.27 s**, including concurrently added Wikisource tests. Those concurrent source/test/fixture files were not edited.

| Reviewer case | Final behavior |
|---|---|
| HTH p163 | Raised `*` restored to text/crop; complete question admitted. |
| WDO p150 | Entire prose/formula baseline merged; isolated `r ,2 D` no longer admitted. Partial-R crop counterexample rejects. |
| HYI p33 footnote | Raised `70` restored; adjacent-line intersections cause `crop_text_mismatch` rejection. |
| WLB p44 | Full `(MLSS)…m3), από τον τύπο:` merged; adjacent-line intersections cause rejection. |
| VJC p52 | Raised `121` restored in text and crop. |
| HYI p33 order | `όπου βρίσκεται…`, raised `69`, then `Η λύση…` in a single LTR line. |

All **180 sources** rerendered on the final code: **177 native PDFs / 18,662 pages**, **3 scans / 268 pages**. Native: **603,535 candidates**, **375,530 admitted**, **228,005 rejected**. Scans: **8,939 candidates**, zero admitted. Final full extraction wall time: **593.32 seconds**, four worker processes. Source/page coverage and hashes remain receipt-bound.

The first repair attempt completed after an interruption and hash-checked resume; its initial `final.log` retains exit 130 and `resume.log` records four rebuilt PDFs. It produced a diagnostic inspection that exposed further failures, so the final 7 October run rerendered all sources again. The final extraction does not reuse those earlier records.

### Counts per rule, before and after

Counters overlap. Candidate grouping changed, so these are run-level counters rather than paired per-line rates. A dash means the rule did not exist in Cycle 1.

| Rule | Cycle 1 overall | Cycle 2 native | Cycle 2 scans | Cycle 2 overall |
|---|---:|---:|---:|---:|
| pua | 20,630 | 14,448 | 0 | 14,448 |
| control | 11,248 | 11,032 | 0 | 11,032 |
| replacement | 9,015 | 5,150 | 0 | 5,150 |
| tounicode_residue | 0 | 0 | 0 | 0 |
| ligature_artifact | 0 | 0 | 0 | 0 |
| letter_run | 144 | 169 | 0 | 169 |
| dictionary_collapse | 0 | 0 | 0 | 0 |
| crop_height | 5,384 | 604 | 524 | 1,128 |
| aspect_ratio | 149,607 | 81,464 | 36 | 81,500 |
| overlapping_lines | 79,445 | 33,781 | 837 | 34,618 |
| rotated_text | 42,071 | 28,963 | 0 | 28,963 |
| ink_bbox_mismatch | 51,484 | 23,457 | 0 | 23,457 |
| multiline_ink | 139 | 159 | 7 | 166 |
| near_duplicate | 119,871 | 31,945 | 0 | 31,945 |
| no_text | 13,435 | 2 | 8,939 | 8,941 |
| invalid_char_geometry | 0 | 0 | 0 | 0 |
| blank_ink | 5,472 | 907 | 27 | 934 |
| fragment_short | — | 99,773 | 0 | 99,773 |
| fragment_no_letters | — | 93,425 | 0 | 93,425 |
| fragment_symbol_dominated | — | 105,052 | 0 | 105,052 |
| missing_baseline_neighbour | — | 118,158 | 0 | 118,158 |
| crop_text_mismatch | — | 40,065 | 0 | 40,065 |
| label_spacing_gap | — | 10,252 | 0 | 10,252 |

### Regenerated pools

| Pool | Before raw / capped | After raw / capped | After docs raw / capped | Max doc share |
|---|---:|---:|---:|---:|
| modern_greek | 372,551 / 5,000 | 342,598 / 5,000 | 177 / 177 | 0.58% |
| polytonic_historical_greek | 3,507 / 0 | 3,021 / 0 | 11 / 0 | 0.00% |
| european_latin | 781 / 402 | 716 / 360 | 82 / 82 | 1.94% |
| mixed_script | 64,256 / 5,000 | 61,044 / 5,000 | 177 / 177 | 0.58% |
| headings | 34,150 / 5,000 | 28,217 / 5,000 | 177 / 177 | 0.58% |
| footnotes_small | 3,695 / 1,517 | 1,830 / 608 | 77 / 77 | 1.97% |
| short_lines | 43,203 / 5,000 | 24,388 / 5,000 | 177 / 177 | 0.58% |
| cyrillic | 125 / 0 | 114 / 0 | 8 / 0 | 0.00% |

Host/document marginals, sparse supply, codec inventory and the pending verification pack were regenerated. Polytonic and Cyrillic capped supply remains subject to the unchanged 2% document cap. Neither proxy category certifies historical era or verified language.

### First repair draw: defects found and fixed

Seed 6100627, ten random distinct rows per nonempty capped pool. I viewed all twelve crop/transcript sheets and all twelve full-width context sheets. Sample 59 was an incomplete widely spaced TOC title; samples 25 and 36 lost a visible word gap. These three cases became additional production regressions, rejected by the final code. Samples 11, 14, 24 and 53 had non-text rule-line intrusion; this crop-quality limitation is disclosed separately from missing PDF glyphs. The exact first draw and its complete manual table remain available; it is not a passed final sample.

| # | Crop ID | Pool | Inspection | Evidence |
|---:|---|---|---|---|
| 1 | `LYH_947-p0009-l0009` | european_latin | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-01.png), [context](../../bench/runs/O1b_20261006/inspection/context60-01.png) |
| 2 | `UWM_440-p0082-l0026` | european_latin | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-01.png), [context](../../bench/runs/O1b_20261006/inspection/context60-01.png) |
| 3 | `BPZ_307-p0099-l0015` | european_latin | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-01.png), [context](../../bench/runs/O1b_20261006/inspection/context60-01.png) |
| 4 | `GUK_498-p0115-l0026` | european_latin | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-01.png), [context](../../bench/runs/O1b_20261006/inspection/context60-01.png) |
| 5 | `JNB_151-p0034-l0033` | european_latin | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-01.png), [context](../../bench/runs/O1b_20261006/inspection/context60-01.png) |
| 6 | `NHA_882-p0222-l0015` | european_latin | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-02.png), [context](../../bench/runs/O1b_20261006/inspection/context60-02.png) |
| 7 | `KUK_170-p0047-l0031` | european_latin | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-02.png), [context](../../bench/runs/O1b_20261006/inspection/context60-02.png) |
| 8 | `HPK_012-p0083-l0024` | european_latin | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-02.png), [context](../../bench/runs/O1b_20261006/inspection/context60-02.png) |
| 9 | `PNC_240-p0104-l0009` | european_latin | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-02.png), [context](../../bench/runs/O1b_20261006/inspection/context60-02.png) |
| 10 | `GSA_404-p0061-l0009` | european_latin | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-02.png), [context](../../bench/runs/O1b_20261006/inspection/context60-02.png) |
| 11 | `YWL_143-p0065-l0002` | footnotes_small | crop_artefact: Left vertical table rule intrudes into crop. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-03.png), [context](../../bench/runs/O1b_20261006/inspection/context60-03.png) |
| 12 | `DMB_101-p0105-l0013` | footnotes_small | context_concern: Table/chart/caption/body-bold proxy; no visible transcription/completeness mismatch. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-03.png), [context](../../bench/runs/O1b_20261006/inspection/context60-03.png) |
| 13 | `BPZ_307-p0047-l0011` | footnotes_small | context_concern: Table/chart/caption/body-bold proxy; no visible transcription/completeness mismatch. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-03.png), [context](../../bench/runs/O1b_20261006/inspection/context60-03.png) |
| 14 | `RIA_460-p0073-l0174` | footnotes_small | crop_artefact: Black horizontal table rule at bottom edge. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-03.png), [context](../../bench/runs/O1b_20261006/inspection/context60-03.png) |
| 15 | `XFR_303-p0058-l0015` | footnotes_small | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-03.png), [context](../../bench/runs/O1b_20261006/inspection/context60-03.png) |
| 16 | `WZX_577-p0126-l0038` | footnotes_small | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-04.png), [context](../../bench/runs/O1b_20261006/inspection/context60-04.png) |
| 17 | `KEU_796-p0105-l0011` | footnotes_small | context_concern: Table/chart/caption/body-bold proxy; no visible transcription/completeness mismatch. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-04.png), [context](../../bench/runs/O1b_20261006/inspection/context60-04.png) |
| 18 | `GEM_508-p0022-l0001` | footnotes_small | context_concern: Table/chart/caption/body-bold proxy; no visible transcription/completeness mismatch. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-04.png), [context](../../bench/runs/O1b_20261006/inspection/context60-04.png) |
| 19 | `BPZ_307-p0047-l0033` | footnotes_small | context_concern: Table/chart/caption/body-bold proxy; no visible transcription/completeness mismatch. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-04.png), [context](../../bench/runs/O1b_20261006/inspection/context60-04.png) |
| 20 | `IZL_981-p0103-l0053` | footnotes_small | context_concern: Table/chart/caption/body-bold proxy; no visible transcription/completeness mismatch. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-04.png), [context](../../bench/runs/O1b_20261006/inspection/context60-04.png) |
| 21 | `IUJ_849-p0014-l0050` | headings | context_concern: Table/chart/caption/body-bold proxy; no visible transcription/completeness mismatch. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-05.png), [context](../../bench/runs/O1b_20261006/inspection/context60-05.png) |
| 22 | `YHY_614-p0019-l0003` | headings | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-05.png), [context](../../bench/runs/O1b_20261006/inspection/context60-05.png) |
| 23 | `ARM_366-p0001-l0007` | headings | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-05.png), [context](../../bench/runs/O1b_20261006/inspection/context60-05.png) |
| 24 | `XBN_771-p0057-l0009` | headings | crop_artefact: Black horizontal table rule at bottom edge. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-05.png), [context](../../bench/runs/O1b_20261006/inspection/context60-05.png) |
| 25 | `GTL_441-p0063-l0001` | headings | label_spacing: Visible gap after raised ο omitted: 7οΣυμπεράσματα. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-05.png), [context](../../bench/runs/O1b_20261006/inspection/context60-05.png) |
| 26 | `FIF_505-p0001-l0010` | headings | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-06.png), [context](../../bench/runs/O1b_20261006/inspection/context60-06.png) |
| 27 | `NMR_301-p0035-l0010` | headings | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-06.png), [context](../../bench/runs/O1b_20261006/inspection/context60-06.png) |
| 28 | `FJP_237-p0042-l0057` | headings | context_concern: Table/chart/caption/body-bold proxy; no visible transcription/completeness mismatch. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-06.png), [context](../../bench/runs/O1b_20261006/inspection/context60-06.png) |
| 29 | `GIH_063-p0028-l0048` | headings | context_concern: Table/chart/caption/body-bold proxy; no visible transcription/completeness mismatch. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-06.png), [context](../../bench/runs/O1b_20261006/inspection/context60-06.png) |
| 30 | `EKI_884-p0070-l0002` | headings | context_concern: Table/chart/caption/body-bold proxy; no visible transcription/completeness mismatch. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-06.png), [context](../../bench/runs/O1b_20261006/inspection/context60-06.png) |
| 31 | `GTL_441-p0035-l0014` | mixed_script | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-07.png), [context](../../bench/runs/O1b_20261006/inspection/context60-07.png) |
| 32 | `BSA_056-p0061-l0028` | mixed_script | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-07.png), [context](../../bench/runs/O1b_20261006/inspection/context60-07.png) |
| 33 | `AWU_928-p0032-l0002` | mixed_script | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-07.png), [context](../../bench/runs/O1b_20261006/inspection/context60-07.png) |
| 34 | `AZP_457-p0006-l0020` | mixed_script | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-07.png), [context](../../bench/runs/O1b_20261006/inspection/context60-07.png) |
| 35 | `HBP_109-p0011-l0029` | mixed_script | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-07.png), [context](../../bench/runs/O1b_20261006/inspection/context60-07.png) |
| 36 | `IUJ_849-p0053-l0063` | mixed_script | label_spacing: Visible gap before στο omitted: SO42-στο. All formula glyphs included. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-08.png), [context](../../bench/runs/O1b_20261006/inspection/context60-08.png) |
| 37 | `DJP_069-p0041-l0004` | mixed_script | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-08.png), [context](../../bench/runs/O1b_20261006/inspection/context60-08.png) |
| 38 | `JBB_023-p0054-l0001` | mixed_script | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-08.png), [context](../../bench/runs/O1b_20261006/inspection/context60-08.png) |
| 39 | `WZX_577-p0095-l0027` | mixed_script | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-08.png), [context](../../bench/runs/O1b_20261006/inspection/context60-08.png) |
| 40 | `DCB_873-p0019-l0035` | mixed_script | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-08.png), [context](../../bench/runs/O1b_20261006/inspection/context60-08.png) |
| 41 | `JXI_906-p0071-l0014` | modern_greek | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-09.png), [context](../../bench/runs/O1b_20261006/inspection/context60-09.png) |
| 42 | `COO_642-p0012-l0012` | modern_greek | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-09.png), [context](../../bench/runs/O1b_20261006/inspection/context60-09.png) |
| 43 | `HIZ_845-p0057-l0029` | modern_greek | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-09.png), [context](../../bench/runs/O1b_20261006/inspection/context60-09.png) |
| 44 | `GSA_404-p0051-l0019` | modern_greek | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-09.png), [context](../../bench/runs/O1b_20261006/inspection/context60-09.png) |
| 45 | `EIJ_953-p0014-l0017` | modern_greek | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-09.png), [context](../../bench/runs/O1b_20261006/inspection/context60-09.png) |
| 46 | `ARM_366-p0011-l0014` | modern_greek | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-10.png), [context](../../bench/runs/O1b_20261006/inspection/context60-10.png) |
| 47 | `KEU_796-p0067-l0015` | modern_greek | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-10.png), [context](../../bench/runs/O1b_20261006/inspection/context60-10.png) |
| 48 | `ATF_411-p0022-l0015` | modern_greek | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-10.png), [context](../../bench/runs/O1b_20261006/inspection/context60-10.png) |
| 49 | `VCX_879-p0173-l0007` | modern_greek | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-10.png), [context](../../bench/runs/O1b_20261006/inspection/context60-10.png) |
| 50 | `BHF_655-p0040-l0003` | modern_greek | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-10.png), [context](../../bench/runs/O1b_20261006/inspection/context60-10.png) |
| 51 | `MQF_749-p0001-l0003` | short_lines | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-11.png), [context](../../bench/runs/O1b_20261006/inspection/context60-11.png) |
| 52 | `FZM_258-p0088-l0012` | short_lines | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-11.png), [context](../../bench/runs/O1b_20261006/inspection/context60-11.png) |
| 53 | `NHA_882-p0208-l0035` | short_lines | crop_artefact: Grey horizontal table rule at bottom edge. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-11.png), [context](../../bench/runs/O1b_20261006/inspection/context60-11.png) |
| 54 | `XBN_771-p0084-l0030` | short_lines | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-11.png), [context](../../bench/runs/O1b_20261006/inspection/context60-11.png) |
| 55 | `RIA_460-p0101-l0049` | short_lines | context_concern: Table/chart/caption/body-bold proxy; no visible transcription/completeness mismatch. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-11.png), [context](../../bench/runs/O1b_20261006/inspection/context60-11.png) |
| 56 | `ZRL_809-p0043-l0001` | short_lines | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-12.png), [context](../../bench/runs/O1b_20261006/inspection/context60-12.png) |
| 57 | `GIN_069-p0058-l0015` | short_lines | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-12.png), [context](../../bench/runs/O1b_20261006/inspection/context60-12.png) |
| 58 | `NHA_882-p0210-l0044` | short_lines | context_concern: Table/chart/caption/body-bold proxy; no visible transcription/completeness mismatch. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-12.png), [context](../../bench/runs/O1b_20261006/inspection/context60-12.png) |
| 59 | `ARM_366-p0002-l0009` | short_lines | incomplete_line: Widely spaced TOC title continues at right with ΑΝΤΙΣΤΑΣΗΣ ΣΤΙΣ ΣΥΜΒΑΤΙΚΕΣ; gap split admitted left piece. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-12.png), [context](../../bench/runs/O1b_20261006/inspection/context60-12.png) |
| 60 | `HNR_423-p0050-l0015` | short_lines | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261006/inspection/sample60-12.png), [context](../../bench/runs/O1b_20261006/inspection/context60-12.png) |

### Final 60-crop inspection

Seed **6100628**, ten uniformly random draws without replacement from each of six nonempty capped pools, excluding IDs already selected in another pool. This is a balanced diagnostic sample, not a population error-rate estimate. I inspected **all twelve crop/text sheets and all twelve source-page context sheets**, plus individual crops where indicated. Exact labels/boxes and pool hashes are retained in `inspection/sample60.jsonl` and `inspection/receipt.json`; `sample60_review.csv` records every disposition. Owner verification remains pending.

Observed final sample defects/artefacts: **1** — sample 20 (`XWM_348-p0042-l0010`) has a black legend-border stroke at the crop bottom. **No incomplete baseline, omitted raised marker, missing word gap or visibly wrong text was found in this final 60.** Sample 47 is English prose in the modern-Greek proxy pool because the PDF uses Greek iota in `In`; this is a script/language-label concern, not a visibly different glyph. See every item below; no clean-corpus or sealed-gold claim is made.

| # | Crop ID | Pool | Inspection | Evidence |
|---:|---|---|---|---|
| 1 | `MRS_484-p0052-l0032` | european_latin | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-01.png), [context](../../bench/runs/O1b_20261007/inspection/context60-01.png) |
| 2 | `HNR_423-p0072-l0005` | european_latin | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-01.png), [context](../../bench/runs/O1b_20261007/inspection/context60-01.png) |
| 3 | `RBK_864-p0011-l0030` | european_latin | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-01.png), [context](../../bench/runs/O1b_20261007/inspection/context60-01.png) |
| 4 | `YRQ_018-p0064-l0014` | european_latin | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-01.png), [context](../../bench/runs/O1b_20261007/inspection/context60-01.png) |
| 5 | `VQP_963-p0072-l0022` | european_latin | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-01.png), [context](../../bench/runs/O1b_20261007/inspection/context60-01.png) |
| 6 | `GUK_498-p0112-l0014` | european_latin | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-02.png), [context](../../bench/runs/O1b_20261007/inspection/context60-02.png) |
| 7 | `QHJ_343-p0105-l0010` | european_latin | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-02.png), [context](../../bench/runs/O1b_20261007/inspection/context60-02.png) |
| 8 | `FJP_237-p0132-l0011` | european_latin | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-02.png), [context](../../bench/runs/O1b_20261007/inspection/context60-02.png) |
| 9 | `BZA_238-p0229-l0023` | european_latin | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-02.png), [context](../../bench/runs/O1b_20261007/inspection/context60-02.png) |
| 10 | `BGR_881-p0008-l0020` | european_latin | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-02.png), [context](../../bench/runs/O1b_20261007/inspection/context60-02.png) |
| 11 | `MNC_212-p0020-l0010` | footnotes_small | context_concern: Chart/table/caption/body-bold or typography proxy; no visible text/completeness defect. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-03.png), [context](../../bench/runs/O1b_20261007/inspection/context60-03.png) |
| 12 | `ECL_679-p0042-l0001` | footnotes_small | context_concern: Chart/table/caption/body-bold or typography proxy; no visible text/completeness defect. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-03.png), [context](../../bench/runs/O1b_20261007/inspection/context60-03.png) |
| 13 | `HIZ_845-p0001-l0002` | footnotes_small | context_concern: Chart/table/caption/body-bold or typography proxy; no visible text/completeness defect. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-03.png), [context](../../bench/runs/O1b_20261007/inspection/context60-03.png) |
| 14 | `BPZ_307-p0047-l0010` | footnotes_small | context_concern: Chart/table/caption/body-bold or typography proxy; no visible text/completeness defect. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-03.png), [context](../../bench/runs/O1b_20261007/inspection/context60-03.png) |
| 15 | `XHX_969-p0080-l0089` | footnotes_small | context_concern: Chart/table/caption/body-bold or typography proxy; no visible text/completeness defect. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-03.png), [context](../../bench/runs/O1b_20261007/inspection/context60-03.png) |
| 16 | `RJF_491-p0082-l0004` | footnotes_small | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-04.png), [context](../../bench/runs/O1b_20261007/inspection/context60-04.png) |
| 17 | `JJI_662-p0054-l0057` | footnotes_small | context_concern: Chart/table/caption/body-bold or typography proxy; no visible text/completeness defect. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-04.png), [context](../../bench/runs/O1b_20261007/inspection/context60-04.png) |
| 18 | `YRQ_018-p0062-l0009` | footnotes_small | context_concern: Chart/table/caption/body-bold or typography proxy; no visible text/completeness defect. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-04.png), [context](../../bench/runs/O1b_20261007/inspection/context60-04.png) |
| 19 | `JBV_043-p0001-l0001` | footnotes_small | context_concern: Chart/table/caption/body-bold or typography proxy; no visible text/completeness defect. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-04.png), [context](../../bench/runs/O1b_20261007/inspection/context60-04.png) |
| 20 | `XWM_348-p0042-l0010` | footnotes_small | crop_artefact: Black legend-frame/underline stroke at bottom edge of crop; text is complete. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-04.png), [context](../../bench/runs/O1b_20261007/inspection/context60-04.png) |
| 21 | `WLB_919-p0014-l0001` | headings | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-05.png), [context](../../bench/runs/O1b_20261007/inspection/context60-05.png) |
| 22 | `GRZ_739-p0039-l0019` | headings | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-05.png), [context](../../bench/runs/O1b_20261007/inspection/context60-05.png) |
| 23 | `EWL_199-p0020-l0003` | headings | context_concern: Chart/table/caption/body-bold or typography proxy; no visible text/completeness defect. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-05.png), [context](../../bench/runs/O1b_20261007/inspection/context60-05.png) |
| 24 | `CCF_441-p0022-l0001` | headings | context_concern: Chart/table/caption/body-bold or typography proxy; no visible text/completeness defect. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-05.png), [context](../../bench/runs/O1b_20261007/inspection/context60-05.png) |
| 25 | `KIP_743-p0003-l0005` | headings | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-05.png), [context](../../bench/runs/O1b_20261007/inspection/context60-05.png) |
| 26 | `ZRL_809-p0006-l0001` | headings | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-06.png), [context](../../bench/runs/O1b_20261007/inspection/context60-06.png) |
| 27 | `GSA_404-p0067-l0008` | headings | context_concern: Chart/table/caption/body-bold or typography proxy; no visible text/completeness defect. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-06.png), [context](../../bench/runs/O1b_20261007/inspection/context60-06.png) |
| 28 | `COO_642-p0084-l0005` | headings | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-06.png), [context](../../bench/runs/O1b_20261007/inspection/context60-06.png) |
| 29 | `HPK_012-p0013-l0022` | headings | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-06.png), [context](../../bench/runs/O1b_20261007/inspection/context60-06.png) |
| 30 | `XNA_102-p0001-l0004` | headings | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-06.png), [context](../../bench/runs/O1b_20261007/inspection/context60-06.png) |
| 31 | `GJJ_091-p0050-l0018` | mixed_script | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-07.png), [context](../../bench/runs/O1b_20261007/inspection/context60-07.png) |
| 32 | `CCF_441-p0028-l0021` | mixed_script | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-07.png), [context](../../bench/runs/O1b_20261007/inspection/context60-07.png) |
| 33 | `GLC_224-p0041-l0003` | mixed_script | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-07.png), [context](../../bench/runs/O1b_20261007/inspection/context60-07.png) |
| 34 | `FHG_024-p0012-l0002` | mixed_script | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-07.png), [context](../../bench/runs/O1b_20261007/inspection/context60-07.png) |
| 35 | `EIJ_953-p0014-l0015` | mixed_script | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-07.png), [context](../../bench/runs/O1b_20261007/inspection/context60-07.png) |
| 36 | `LPS_756-p0094-l0008` | mixed_script | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-08.png), [context](../../bench/runs/O1b_20261007/inspection/context60-08.png) |
| 37 | `GPK_368-p0017-l0004` | mixed_script | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-08.png), [context](../../bench/runs/O1b_20261007/inspection/context60-08.png) |
| 38 | `KIP_743-p0028-l0008` | mixed_script | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-08.png), [context](../../bench/runs/O1b_20261007/inspection/context60-08.png) |
| 39 | `GUK_498-p0027-l0006` | mixed_script | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-08.png), [context](../../bench/runs/O1b_20261007/inspection/context60-08.png) |
| 40 | `EMB_049-p0059-l0010` | mixed_script | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-08.png), [context](../../bench/runs/O1b_20261007/inspection/context60-08.png) |
| 41 | `GPK_368-p0013-l0011` | modern_greek | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-09.png), [context](../../bench/runs/O1b_20261007/inspection/context60-09.png) |
| 42 | `AWU_928-p0043-l0009` | modern_greek | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-09.png), [context](../../bench/runs/O1b_20261007/inspection/context60-09.png) |
| 43 | `BPZ_307-p0017-l0018` | modern_greek | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-09.png), [context](../../bench/runs/O1b_20261007/inspection/context60-09.png) |
| 44 | `CFY_722-p0021-l0027` | modern_greek | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-09.png), [context](../../bench/runs/O1b_20261007/inspection/context60-09.png) |
| 45 | `FZM_258-p0005-l0042` | modern_greek | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-09.png), [context](../../bench/runs/O1b_20261007/inspection/context60-09.png) |
| 46 | `FZM_258-p0097-l0004` | modern_greek | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-10.png), [context](../../bench/runs/O1b_20261007/inspection/context60-10.png) |
| 47 | `GJO_184-p0051-l0010` | modern_greek | context_concern: English prose in modern_greek pool: script proxy reflects Greek homoglyphs in PDF text, not verified language. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-10.png), [context](../../bench/runs/O1b_20261007/inspection/context60-10.png) |
| 48 | `KIP_743-p0022-l0028` | modern_greek | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-10.png), [context](../../bench/runs/O1b_20261007/inspection/context60-10.png) |
| 49 | `EWL_199-p0080-l0038` | modern_greek | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-10.png), [context](../../bench/runs/O1b_20261007/inspection/context60-10.png) |
| 50 | `XJP_133-p0013-l0024` | modern_greek | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-10.png), [context](../../bench/runs/O1b_20261007/inspection/context60-10.png) |
| 51 | `YHY_614-p0049-l0007` | short_lines | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-11.png), [context](../../bench/runs/O1b_20261007/inspection/context60-11.png) |
| 52 | `AAI_768-p0089-l0028` | short_lines | context_concern: Chart/table/caption/body-bold or typography proxy; no visible text/completeness defect. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-11.png), [context](../../bench/runs/O1b_20261007/inspection/context60-11.png) |
| 53 | `FHG_024-p0002-l0010` | short_lines | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-11.png), [context](../../bench/runs/O1b_20261007/inspection/context60-11.png) |
| 54 | `EKI_884-p0067-l0021` | short_lines | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-11.png), [context](../../bench/runs/O1b_20261007/inspection/context60-11.png) |
| 55 | `VQR_845-p0035-l0018` | short_lines | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-11.png), [context](../../bench/runs/O1b_20261007/inspection/context60-11.png) |
| 56 | `MEC_098-p0004-l0004` | short_lines | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-12.png), [context](../../bench/runs/O1b_20261007/inspection/context60-12.png) |
| 57 | `FOK_514-p0010-l0011` | short_lines | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-12.png), [context](../../bench/runs/O1b_20261007/inspection/context60-12.png) |
| 58 | `HIZ_845-p0043-l0004` | short_lines | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-12.png), [context](../../bench/runs/O1b_20261007/inspection/context60-12.png) |
| 59 | `WFS_052-p0089-l0009` | short_lines | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-12.png), [context](../../bench/runs/O1b_20261007/inspection/context60-12.png) |
| 60 | `FIF_505-p0074-l0031` | short_lines | no_visible_defect: No visible text or completeness defect in crop and context. | [crop/text](../../bench/runs/O1b_20261007/inspection/sample60-12.png), [context](../../bench/runs/O1b_20261007/inspection/context60-12.png) |

### Actual validation and comparator results

`validate_run` passed for **180 sources**, **612,474 records**, all source/code/record hashes, per-document crop counts, pool caps and **360 endpoint PNG decodes**. `check_invariants.py` checked stored crop/text equality and no omitted-neighbour/spacing-gap flags for every admitted record, and reconciled **17,808 unique capped-pool rows** with their admitted source records. It does not independently OCR all pixels.

The Astra audit replay, synthetic scorer fixture/manifest, codec coverage, verification sheets and public Apple Vision comparator were actually rerun. The Vision comparator produced 50 predictions with **50 request failures**, exited 2, and retained the failure receipt/raw rows; it remains an unsuccessful sandbox runtime, not an accuracy result. The real unsealed scorer refused the reference (exit 2), and no real score or seal was produced.

Commands for post-extraction pipeline stages are retained in `bench/runs/O1b_20261007/post_extract.sh`. Extraction used the identical 177-PDF directory, source manifest and three scan paths shown in Cycle 1, with `--out bench/runs/O1b_20261007/final --workers 4`, without `--resume`. `render_regressions.py`, `check_invariants.py` and `write_reply.py` retain the evidence/report assembly. No network, installs, recogniser training, git history changes or sub-agents were used.

## Cycle 3 — pixel admission and real page columns, 7 October 2026

**Executed candidate repair; independent certification remains pending. No real reference was sealed.**

### Gates and regression evidence

The pixel gate uses inclusive Otsu thresholding and 8-connected components. Non-space valid char boxes expand by **2 pixels at 200 dpi**. Every ink component of **at least 3 pixels** needs **90% ink containment** in their union; every connected unexplained residual of at least 3 pixels also rejects. A second Otsu split on pixels outside the union, capped at grey level 245, catches faint strokes discarded by the dark-text split. Expected non-space char boxes must contain at least one Otsu ink pixel in their floor/ceil raster bounds, otherwise `missing_ink`. Records retain component, residual, faint-component and missing-char counts and thresholds. Named rejection counters are per candidate and overlap.

The rendered audit extends **five median glyph widths** horizontally beyond the saved crop at its original vertical band, clipped at inferred column midpoints. This detects CJN's image-backed bullet outside the original crop; the saved defective crop is rejected, not silently repaired or assigned an invented bullet label. `ink_audit_bbox_pixel` records the inspected band. The finite halo is a conservative local completeness check, not certification of every marker elsewhere on a page.

Columns use baseline x-range clusters with ordinary gaps below **3 median letter widths** filled, and occupancy bins of one-quarter letter width. A gutter spans at least three widths, occupies at most 5% of page baselines (one outlier allowed), and has support on both sides from at least six baselines and 25% of page baselines. This tolerates centered folios and independent column line spacing. Columns constrain baseline assembly before raised/lowered glyph attachment; spaces are assigned within their column. Residual spanning rows reject as `cross_column`. This remains a page geometry heuristic; it is not a general reading-order or language classifier.

Ten reviewer regressions actually failed before the fix and pass afterward: all seven pixel defects, a white-page missing-ink perturbation, real COO page 153, and a forced cross-column merge. Additional tests cover all six unchanged contaminated crop files directly, faint rules, accents/noise, connected intrusion, same-baseline column spaces, COO dotted leaders, and storage reuse. Before-fix output: `bench/runs/O1c_20261007/regressions_before.txt`. Scoped test result: 75 passed in 2.78s. Complete benchmark suite result at capture: 126 passed in 32.47s. No Wikisource source, tests or fixtures were edited by this task.

All seven fresh source-page cases reject with `unexplained_ink`. The final production records confirm all seven pixel rejections. COO p153 now has 80 candidates and 62 admissions; its two formerly merged rows are four separate admitted column lines (l0047/l0048 and l0062/l0063), with a gutter `[284.2931, 307.7021]` PDF points. See `production_regressions.json`, `regressions/cases.json`, `regressions/columns.json` and the source-page overlay.

### Full run and storage

The final full pass rerendered **177 native PDFs / 18,662 pages** and **3 scans / 268 pages**, at 200 dpi, in **818.49 seconds**, using four PDFium worker processes. No extraction resume was used. Native: **628,113 candidates, 358,246 admitted, 269,867 rejected**. Scans: **8,939 candidates, 0 admitted**. Total: **637,052 candidates**.

Only about 3.6 GiB was initially free. The final pass reused storage for **556,276 PNGs** by hard link only after freshly rendered crop pixels matched the previous PNG's mode, dimensions and bytes exactly. Differing images were written to new temporary files and atomically replaced, preserving the previous run's files. All crops and all rows remain present. The reuse root is recorded per receipt. An earlier extraction attempt was interrupted during development; its partial outputs were removed and none contributes to these final counts. The final pass follows the fixed source/code receipts.

Commands: `bench/runs/O1c_20261007/run_pipeline.sh`; result root: `bench/runs/O1c_20261007/`. Regression and extra pixel/invariant checks are retained alongside it. No network, installs, recognizer training, git history changes or sub-agents.

### Rule counts before and after

Counters overlap; do not sum them as rejected-row totals. The prior run is O1b_20261007. Dictionary checks remain disabled; a zero is not lexical verification.

| Rule | Cycle 2 overall | Cycle 3 native | Cycle 3 scans | Cycle 3 overall |
|---|---:|---:|---:|---:|
| pua | 14448 | 14,455 | 0 | 14,455 |
| control | 11032 | 11,068 | 0 | 11,068 |
| replacement | 5150 | 5,155 | 0 | 5,155 |
| tounicode_residue | 0 | 0 | 0 | 0 |
| ligature_artifact | 0 | 0 | 0 | 0 |
| letter_run | 169 | 164 | 0 | 164 |
| dictionary_collapse | 0 | 0 | 0 | 0 |
| crop_height | 1128 | 609 | 524 | 1,133 |
| aspect_ratio | 81500 | 97,255 | 36 | 97,291 |
| overlapping_lines | 34618 | 36,146 | 837 | 36,983 |
| rotated_text | 28963 | 31,193 | 0 | 31,193 |
| ink_bbox_mismatch | 23457 | 26,490 | 0 | 26,490 |
| multiline_ink | 166 | 161 | 7 | 168 |
| near_duplicate | 31945 | 23,797 | 0 | 23,797 |
| no_text | 8941 | 2 | 8,939 | 8,941 |
| invalid_char_geometry | 0 | 0 | 0 | 0 |
| blank_ink | 934 | 941 | 27 | 968 |
| fragment_short | 99773 | 117,798 | 0 | 117,798 |
| fragment_no_letters | 93425 | 111,049 | 0 | 111,049 |
| fragment_symbol_dominated | 105052 | 122,168 | 0 | 122,168 |
| missing_baseline_neighbour | 118158 | 87,031 | 0 | 87,031 |
| crop_text_mismatch | 40065 | 44,101 | 0 | 44,101 |
| label_spacing_gap | 10252 | 8,711 | 0 | 8,711 |
| unexplained_ink | — | 153,610 | 0 | 153,610 |
| missing_ink | — | 1,340 | 0 | 1,340 |
| cross_column | — | 0 | 0 | 0 |

### Pools after stricter admission

| Pool | Cycle 2 raw | Cycle 3 raw | Supply documents | Cycle 2 capped | Cycle 3 capped | Max doc share |
|---|---:|---:|---:|---:|---:|---:|
| modern_greek | 342,598 | 327,873 | 177 | 5,000 | 5,000 | 0.5800% |
| polytonic_historical_greek | 3,021 | 3,274 | 11 | 0 | 0 | 0.0000% |
| european_latin | 716 | 705 | 82 | 360 | 362 | 1.9337% |
| mixed_script | 61,044 | 57,440 | 177 | 5,000 | 5,000 | 0.5800% |
| headings | 28,217 | 23,731 | 177 | 5,000 | 5,000 | 0.6000% |
| footnotes_small | 1,830 | 994 | 61 | 608 | 204 | 1.9608% |
| short_lines | 24,388 | 19,104 | 177 | 5,000 | 5,000 | 0.5800% |
| cyrillic | 114 | 112 | 8 | 0 | 0 | 0.0000% |

Sparse uncapped supply remains quarantined in `.supply.jsonl`; strata overlap and typography/script proxies do not verify language, era or true headings.

### Fresh 60-crop manual inspection

Fresh seed **107202603**: ten uniform draws without replacement from each nonempty capped pool, excluding already selected IDs. This is a balanced diagnostic sample, not a population error estimate. Sample records, pool hashes and selection method are in `inspection/sample60.jsonl` and `inspection/receipt.json`; the draw has zero overlap with the reviewer sample and one ID overlap with the previous implementer sample (JJI_662-p0054-l0057), recorded in `inspection/overlap.json`. No exclusions of previous sample IDs were applied to this new draw.

I personally viewed all 12 combined sheets containing every saved crop, text and full-width source context: **0/60 visible defects**, **20 context/pool concerns**. Every sampled crop also equals a freshly rerendered page crop at its declared bounds. These findings are manual visual observations, not owner transcript verification or independent certification.

| N | ID | Pool | Status and observation | Evidence |
|---:|---|---|---|---|
| 1 | `PXR_091-p0057-l0012` | european_latin | no_visible_defect: Complete bibliography baseline; acute accent and punctuation visible. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-01.png) |
| 2 | `LYH_947-p0009-l0015` | european_latin | no_visible_defect: Complete Italian prose baseline; accented vowel retained. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-01.png) |
| 3 | `JBV_043-p0130-l0021` | european_latin | no_visible_defect: Complete bibliography baseline including German umlaut. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-01.png) |
| 4 | `EWL_199-p0111-l0009` | european_latin | no_visible_defect: Complete reference baseline; printed JR.Emerging adjacency matches label. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-01.png) |
| 5 | `EJC_852-p0096-l0003` | european_latin | no_visible_defect: Complete bibliography baseline; umlaut and italics retained. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-01.png) |
| 6 | `YRQ_018-p0031-l0001` | european_latin | no_visible_defect: Complete grey heading with grave accent; no neighbouring ink. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-02.png) |
| 7 | `BZA_238-p0240-l0032` | european_latin | no_visible_defect: Complete reference baseline with umlaut. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-02.png) |
| 8 | `NMK_294-p0104-l0004` | european_latin | no_visible_defect: Complete reference baseline with umlaut and quotes. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-02.png) |
| 9 | `CYT_755-p0024-l0005` | european_latin | context_concern: Bold source-caption baseline with Greek prefix and French text; complete visible text. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-02.png) |
| 10 | `YCM_048-p0113-l0007` | european_latin | no_visible_defect: Genuine wrapped reference baseline with accented uppercase name. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-02.png) |
| 11 | `ZKG_350-p0069-l0013` | footnotes_small | context_concern: Small figure-caption baseline, not a semantic footnote; no clipped plot frame. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-03.png) |
| 12 | `PMP_227-p0094-l0030` | footnotes_small | context_concern: Genuine wrapped formula baseline Lmax.; subscript max included; font-size proxy. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-03.png) |
| 13 | `NMR_301-p0085-l0052` | footnotes_small | context_concern: Wrapped flowchart-cell baseline, not a semantic footnote; no clipped box or arrow. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-03.png) |
| 14 | `FJP_237-p0157-l0642` | footnotes_small | context_concern: Table total-label cell, not a semantic footnote; no clipped rule in crop. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-03.png) |
| 15 | `NMR_301-p0085-l0024` | footnotes_small | context_concern: Wrapped flowchart-cell baseline; no neighbouring graphic intrusion. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-03.png) |
| 16 | `BPZ_307-p0048-l0005` | footnotes_small | context_concern: Wrapped chart-label baseline; no clipped frame; font-size footnote proxy. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-04.png) |
| 17 | `MNC_212-p0097-l0083` | footnotes_small | context_concern: Complete plot-axis label; no axis/frame stroke in crop; font-size proxy. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-04.png) |
| 18 | `CIG_478-p0073-l0007` | footnotes_small | context_concern: Complete table-cell label Missing; no table border; font-size proxy. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-04.png) |
| 19 | `JJI_662-p0054-l0057` | footnotes_small | context_concern: Complete table-row label; neighbouring shaded rows and divider excluded. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-04.png) |
| 20 | `XFR_303-p0057-l0019` | footnotes_small | context_concern: Small chart-caption baseline; printed parenthesis adjacency matches label. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-04.png) |
| 21 | `TBA_630-p0120-l0024` | headings | no_visible_defect: Complete bold italic program heading. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-05.png) |
| 22 | `LPS_756-p0091-l0001` | headings | no_visible_defect: Complete grey bibliography heading with section number. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-05.png) |
| 23 | `ARM_366-p0015-l0005` | headings | context_concern: Body prose with a bold leading NFkβ term; headings proxy, complete baseline. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-05.png) |
| 24 | `KIP_743-p0071-l0002` | headings | no_visible_defect: Complete appendix heading. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-05.png) |
| 25 | `DBZ_871-p0001-l0006` | headings | no_visible_defect: Complete display-font cover heading. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-05.png) |
| 26 | `COO_642-p0001-l0008` | headings | context_concern: Large cover date line rather than a section heading; complete baseline. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-06.png) |
| 27 | `XHX_969-p0090-l0002` | headings | context_concern: Body-prose baseline with one bold word; headings proxy. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-06.png) |
| 28 | `DQR_373-p0004-l0023` | headings | no_visible_defect: Complete numbered subsection line. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-06.png) |
| 29 | `HTH_449-p0010-l0012` | headings | context_concern: Bold italic wrapped quotation baseline; headings proxy; closing punctuation included. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-06.png) |
| 30 | `VYF_161-p0033-l0005` | headings | no_visible_defect: Complete numbered uppercase section heading. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-06.png) |
| 31 | `JXI_906-p0010-l0014` | mixed_script | no_visible_defect: Complete Greek prose baseline with Latin citation. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-07.png) |
| 32 | `FJP_237-p0036-l0018` | mixed_script | no_visible_defect: Complete bilingual heading; source spelling Redudancy preserved. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-07.png) |
| 33 | `DRP_397-p0024-l0016` | mixed_script | no_visible_defect: Complete prose baseline including numeric prefix and Latin surname. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-07.png) |
| 34 | `NHA_882-p0024-l0013` | mixed_script | no_visible_defect: Complete figure-list row with leader dots and page number. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-07.png) |
| 35 | `BHF_655-p0005-l0017` | mixed_script | context_concern: Source TOC prints a Russian word-processor field error; literal baseline is complete. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-07.png) |
| 36 | `IZS_292-p0042-l0026` | mixed_script | no_visible_defect: Complete prose baseline including italic Latin species name. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-08.png) |
| 37 | `LJU_450-p0083-l0024` | mixed_script | no_visible_defect: Complete prose baseline; printed .Η adjacency matches label. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-08.png) |
| 38 | `CFY_722-p0032-l0017` | mixed_script | no_visible_defect: Complete Greek prose baseline with Latin personal name. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-08.png) |
| 39 | `ATF_411-p0048-l0010` | mixed_script | no_visible_defect: Complete bilingual numbered heading; source word adjacency preserved. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-08.png) |
| 40 | `DAN_649-p0017-l0040` | mixed_script | no_visible_defect: Complete enumerated baseline including raised 2 after m. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-08.png) |
| 41 | `STS_440-p0129-l0007` | modern_greek | no_visible_defect: Complete final wrapped prose baseline. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-09.png) |
| 42 | `IZL_981-p0052-l0029` | modern_greek | no_visible_defect: Complete justified Greek prose baseline. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-09.png) |
| 43 | `JBV_043-p0046-l0004` | modern_greek | no_visible_defect: Complete Greek prose baseline. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-09.png) |
| 44 | `JIZ_109-p0049-l0010` | modern_greek | no_visible_defect: Complete Greek prose baseline with Windows and closing quotes. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-09.png) |
| 45 | `HTH_449-p0104-l0007` | modern_greek | no_visible_defect: Complete wrapped list-continuation baseline; preceding bullet belongs to preceding line. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-09.png) |
| 46 | `JXI_906-p0025-l0008` | modern_greek | no_visible_defect: Complete final prose baseline with percentage. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-10.png) |
| 47 | `DFE_194-p0015-l0028` | modern_greek | no_visible_defect: Complete Greek prose baseline including apostrophe. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-10.png) |
| 48 | `TLW_488-p0016-l0014` | modern_greek | no_visible_defect: Complete Greek prose baseline. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-10.png) |
| 49 | `CGK_278-p0010-l0014` | modern_greek | no_visible_defect: Complete final prose baseline; printed parenthesis adjacency matches label. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-10.png) |
| 50 | `HYI_276-p0024-l0034` | modern_greek | no_visible_defect: Complete dense italic prose baseline; no adjacent-line ink in crop. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-10.png) |
| 51 | `RRA_270-p0010-l0018` | short_lines | no_visible_defect: Genuine wrapped final baseline of a glossary definition. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-11.png) |
| 52 | `DQR_373-p0076-l0002` | short_lines | no_visible_defect: Genuine one-word final prose baseline; marker below belongs to next paragraph. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-11.png) |
| 53 | `JBB_023-p0062-l0006` | short_lines | no_visible_defect: Genuine one-word final prose baseline with colon. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-11.png) |
| 54 | `FJP_237-p0154-l0013` | short_lines | context_concern: Table subject and URL baseline; word-count short-line proxy; no rule or underline in saved crop. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-11.png) |
| 55 | `TLW_488-p0117-l0007` | short_lines | context_concern: Long wrapped percent-encoded URL baseline; short-line word-count proxy. Source underline lies below saved char band. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-11.png) |
| 56 | `OJW_056-p0189-l0041` | short_lines | context_concern: Long wrapped percent-encoded URL baseline; short-line word-count proxy. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-12.png) |
| 57 | `EWL_199-p0009-l0002` | short_lines | no_visible_defect: Complete personal-details heading; nearby table rule excluded from crop. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-12.png) |
| 58 | `YSQ_164-p0094-l0004` | short_lines | no_visible_defect: Genuine wrapped final baseline of bold heading; following bullet is a separate line. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-12.png) |
| 59 | `PNC_240-p0009-l0008` | short_lines | no_visible_defect: Genuine wrapped final prose baseline. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-12.png) |
| 60 | `HBW_692-p0091-l0018` | short_lines | context_concern: Long wrapped percent-encoded URL baseline; short-line word-count proxy; complete visible text. | [sheet](../../bench/runs/O1c_20261007/inspection/combined60-12.png) |

### Verification and remaining limits

`validate_run` passed for **180 sources**, **637,052 rows**, source/code/record hashes, document PNG counts, **360 endpoint PNG decodes**, and pool caps. Full admission replay had **zero disagreements**; all admitted native rows have clear pixel/column/neighbour/spacing flags and matching crop text; **17,677 unique capped-pool rows** reconcile to their admitted source records. All 60 inspection crops independently match fresh renders.

Astra legacy text-run replay, verification sheets, codec coverage, the synthetic scorer smoke fixture and public Apple Vision comparator were rerun. Astra replay is its existing geometry/text diagnostic; it does not supply the new production char-box pixel audit. Vision exit: 2. Unsealed real scoring refusal exit: 2. Vision produced 50 prediction records with 50 request failures and zero successful lines (30.507 seconds including Swift startup); this is an unsuccessful comparator run, not an accuracy result. The scorer refused the unsealed real reference. No real score or real seal was produced.

The gate establishes spatial ink/box agreement, not glyph identity. A wrong Unicode mapping occupying the same pixels, partly missing glyph with some residual ink, marker outside the finite audit halo, regional layout with substantial full-width overlap, and sparse script supply still require review. The sample is evidence for this inspected draw only; another independent reviewer draw remains necessary before sealing.


## Cycle 4 — O1-fix3, 7 October 2026

**The three reported p143 cross-column admissions are repaired in the regenerated run. Independent recertification and O2 owner verification remain pending.** No source PDF/reviewer evidence was modified, older runs deleted, network used, packages installed, training performed, or sub-agents used. Scope: `bench/extract_lines.py`, `bench/admission.py`, regression tests/fixtures, this Cycle 4 entry and `reviews/CP-O1_reply_3.md`, plus run artifacts.

### Diagnosis and detector

p143 has **21** rounded baseline buckets. The old occupancy tolerance `max(1,floor(0.05*N))` allowed only **one** interfering baseline. A continuous full-width note at baseline 303.05 pt and the centered folio at 37.56 pt occupy the gutter on **two** baselines, erasing it. All three physical column gaps (25.65–26.30 pt) are below the eight-glyph fallback threshold (43.72 pt). p153 has **71** baseline buckets and tolerates **three** occupied baselines, so its folio does not erase the gutter. This is sparse-page contamination by genuine spans/folio, rather than unequal column widths.

Whole-page char-box occupancy still uses bins of one quarter of the median letter width, baseline buckets rounded at 3 pt, within-baseline gap filling below three letter widths and a minimum gutter width of three letter widths. It now tolerates `max(2,floor(0.05*N))` occupied baselines. Confirmed gutters require `max(6,ceil(0.25*N))` supporting baselines on **each** side; ambiguous candidate gutters require `max(3,ceil(0.25*N))` per side. Candidate-only structure does not authorize splitting; a row crossing it rejects as `cross_column`.

Before assigning body columns, the assembler identifies full-width baselines from no-gutter physical groups. A span needs at least three visible glyphs on each side, a glyph box intersecting the central third of the gutter, and no gap of three median letter widths through the gutter. A spanning bbox alone never grants the exemption. Both assembly and the admission replay use candidate/confirmed gutter metadata. The pixel audit halo and neighbour checks use the line's local gutters, so continuous notes are preserved across body-column boundaries.

Fresh source render boundaries: p143 **284.620506–307.876572 pt**; p153 remains **284.293098–307.702080 pt**. Personally inspected [p143 before](../../bench/runs/O1d_20261007/columns/COO_642-p0143-before.png), [p143 after](../../bench/runs/O1d_20261007/columns/COO_642-p0143-after.png) and [p157 after](../../bench/runs/O1d_20261007/columns/COO_642-p0157-after.png). Blue lines mark both gutter edges; row boxes are green/red for admission/rejection. Old-boundary renders use Cycle 3 production boxes. [Diagnosis receipt](../../bench/runs/O1d_20261007/columns/diagnosis.json).

### Regressions and all-page column audit

Actual original-source one-page fixtures for p143/p157 render pixel-identically to their whole source pages. Tests protect all three named body merges, exact full-width note text/character membership on both pages, forced-merge rejection, candidate-only fallback, admission geometry replay when the flag is false, sparse/unequal-column support, and explicit justified/leader baseline membership. Existing p153 and all seven pixel regressions still pass. Full benchmark suite: **133 passed, 1 skipped in 19.58s**; the skipped historical Astra replay artifact is absent. [Test output](../../bench/runs/O1d_20261007/tests.txt).

Production p143 now has **29 candidates / 19 document-state admissions** (21 with fresh page-local duplicate state). The original l0001/l0003/l0004 visible character memberships now map to **six separately admitted column-local rows**, with no character loss. p153 retains **80 candidates / 62 admissions** and its four formerly merged target rows admit. p143/p157 full-width notes remain complete and admit in production. [p143 production checks](../../bench/runs/O1d_20261007/p143_production_regressions.json), [seven pixel + p153 production checks](../../bench/runs/O1d_20261007/production_regressions.json), [reviewer-page checks](../../bench/runs/O1d_20261007/columns/reviewer_page_checks.json). Page-local diagnostic admission uses fresh duplicate state; production checks use the document's actual state.

All **18,930 pages** have column inventory receipts, including zero-candidate and scan pages. **807 pages across 124 native documents** have 2+ detected columns; **393 have exactly two detected columns and 414 have three or more**. **217 pages** have only ambiguous candidate gutters. **397 rows reject with cross_column** (overlapping counter, not additional unique rejections). [Every page](../../bench/runs/O1d_20261007/columns/all_pages.json), [2+ column page list](../../bench/runs/O1d_20261007/columns/two_column_pages.csv), [cross_column rejected records](../../bench/runs/O1d_20261007/columns/cross_column_rejections.jsonl).

Uniform 30-line reservoir sample without replacement from **8,072 admitted native lines on exactly two detected column pages**, seed **10720260430**, sorted document/source-row order. Sample spans **11 documents / 27 pages**. I personally inspected all six crop/text/source-context sheets with gutter edges drawn. All 30 saved crops equal independently rerendered source pixels at the recorded bounds. Manual findings: **0/30 visible cross-column merges or crop/text defects**. Individual observations are below; this is diagnostic inspection, not owner transcription certification or a population error rate. [Draw and counters](../../bench/runs/O1d_20261007/columns/summary.json), [sample](../../bench/runs/O1d_20261007/columns/sample30.jsonl), [pixel equality](../../bench/runs/O1d_20261007/columns/sample30_pixel_checks.json), [manual CSV](../../bench/runs/O1d_20261007/columns/manual_review.csv).

### Full pipeline and reconciled accounting

Full rerender at 200 dpi with four PDFium worker processes, no extraction resume: **177 native PDFs / 18,662 pages** and **3 scans / 268 pages**, extraction wall time **773.27 seconds**. Native **628,468 candidates / 358,471 admitted / 269,997 rejected**; scans **8,939 candidates / 0 admitted**; overall **637,407 candidates / 278,936 rejected**. Dictionary admission remains disabled; scans remain unlabelled.

All **637,407 rows**, source/code/record hashes, page candidate counts, all document PNG counts and pool caps reconcile; **360 endpoint PNGs** were decoded. Full admission replay in document order with duplicate state gives **zero disagreements**; all capped-pool rows match admitted production records. Storage reused **587,585 PNGs** by hard link only after fresh pixel equality; changed crops were written atomically, preserving older runs. [Validation](../../bench/runs/O1d_20261007/validation.json), [replay](../../bench/runs/O1d_20261007/invariants.json), [full summary](../../bench/runs/O1d_20261007/final/summary.json), [executed pipeline](../../bench/runs/O1d_20261007/run_pipeline.sh).

Cycle 3 → 4 native admissions: **358,246 → 358,471** (delta **+225**). Exact `(page,line_char_indices)` comparison accounts for it: **−205 lost unchanged +256 gained unchanged −163 old-only admitted +337 new-only admitted = +225**. Full transition counts are in the column audit summary.

| Rule | Cycle 3 native | Cycle 4 native | Cycle 4 scans | Cycle 4 overall |
|---|---:|---:|---:|---:|
| pua | 14,455 | 14,448 | 0 | 14,448 |
| control | 11,068 | 11,057 | 0 | 11,057 |
| replacement | 5,155 | 5,158 | 0 | 5,158 |
| tounicode_residue | 0 | 0 | 0 | 0 |
| ligature_artifact | 0 | 0 | 0 | 0 |
| letter_run | 164 | 164 | 0 | 164 |
| dictionary_collapse | 0 | 0 | 0 | 0 |
| crop_height | 609 | 607 | 524 | 1,131 |
| aspect_ratio | 97,255 | 98,294 | 36 | 98,330 |
| overlapping_lines | 36,146 | 36,200 | 837 | 37,037 |
| rotated_text | 31,193 | 31,198 | 0 | 31,198 |
| ink_bbox_mismatch | 26,490 | 26,540 | 0 | 26,540 |
| multiline_ink | 161 | 160 | 7 | 167 |
| near_duplicate | 23,797 | 24,242 | 0 | 24,242 |
| no_text | 2 | 2 | 8,939 | 8,941 |
| invalid_char_geometry | 0 | 0 | 0 | 0 |
| blank_ink | 941 | 947 | 27 | 974 |
| fragment_short | 117,798 | 118,311 | 0 | 118,311 |
| fragment_no_letters | 111,049 | 112,210 | 0 | 112,210 |
| fragment_symbol_dominated | 122,168 | 123,292 | 0 | 123,292 |
| missing_baseline_neighbour | 87,031 | 83,938 | 0 | 83,938 |
| crop_text_mismatch | 44,101 | 43,062 | 0 | 43,062 |
| label_spacing_gap | 8,711 | 8,714 | 0 | 8,714 |
| unexplained_ink | 153,610 | 153,451 | 0 | 153,451 |
| missing_ink | 1,340 | 1,337 | 0 | 1,337 |
| cross_column | 0 | 397 | 0 | 397 |

Counters overlap; their sum is not the unique rejected-row count.

| Pool | Raw admitted | Raw documents | Capped lines | Largest doc share |
|---|---:|---:|---:|---:|
| modern_greek | 328,025 | 177 | 5,000 | 0.5800% |
| polytonic_historical_greek | 3,292 | 11 | 0 | 0.0000% |
| european_latin | 705 | 82 | 362 | 1.9337% |
| mixed_script | 57,462 | 177 | 5,000 | 0.5800% |
| headings | 23,770 | 177 | 5,000 | 0.6000% |
| footnotes_small | 999 | 61 | 204 | 1.9608% |
| short_lines | 19,237 | 177 | 5,000 | 0.5800% |
| cyrillic | 112 | 8 | 0 | 0.0000% |

Pipeline also reran Astra diagnostic replay, pool generation, owner verification sheets (pending), codec coverage, a separate unreviewed balanced sample60, synthetic scorer smoke/score and the public Vision comparator. Vision attempted **50** crops, Swift subprocess return code **0**, benchmark runner exit **2**, **50** failed rows and **0** successful rows; no real CER/WER is claimed. The scorer refuses unsealed candidate references. See each run log/runtime receipt. No inspection verdict is claimed for the separate sample60.

### Personal 30-line inspection

| # | ID | Observation | Sheet |
|---:|---|---|---|
| 1 | `NLM_694-p0022-l0001` | Complete continuous full-width prose crosses the detected page gutter without splitting; no visible defect. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-01.png) |
| 2 | `WJX_465-p0092-l0026` | Complete widely justified list baseline within the left prose column; right list remains separate. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-01.png) |
| 3 | `TLW_488-p0114-l0024` | Complete Roman reference marker in its own enumeration region; adjacent bibliography text is separate. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-01.png) |
| 4 | `COO_642-p0103-l0032` | Complete right-column mathematical prose baseline including parenthesized citation; no join. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-01.png) |
| 5 | `JZT_969-p0054-l0032` | Complete bullet-body baseline; the bullet occupies a separate detected marker region. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-01.png) |
| 6 | `COO_642-p0040-l0032` | Complete left-column polytonic prose baseline; accents and closing Greek letter retained. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-02.png) |
| 7 | `WJX_465-p0097-l0051` | Complete justified numbered list baseline in left column; independent right item excluded. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-02.png) |
| 8 | `TLW_488-p0112-l0060` | Complete wrapped bibliography final baseline; Roman marker belongs to an earlier baseline. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-02.png) |
| 9 | `COO_642-p0155-l0043` | Complete left-column polytonic prose baseline; right prose excluded. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-02.png) |
| 10 | `WJX_465-p0090-l0021` | Complete widely justified numbered item baseline; no right-column intrusion. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-02.png) |
| 11 | `TLW_488-p0112-l0043` | Complete bibliography first baseline with italic title and quotes; Roman enumeration marker is separate. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-03.png) |
| 12 | `WJX_465-p0089-l0016` | Genuine one-word wrapped final baseline in left column; not a truncated longer baseline. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-03.png) |
| 13 | `XRB_207-p0003-l0039` | Complete TOC title field; printed page number is in a separate detected x region. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-03.png) |
| 14 | `COO_642-p0069-l0023` | Complete indented left-column polytonic baseline; acute and breathing marks visible. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-03.png) |
| 15 | `COO_642-p0020-l0068` | Complete numbered right-column proposition baseline, continuing on the following printed line. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-03.png) |
| 16 | `COO_642-p0063-l0030` | Complete indented left-column polytonic baseline; right translation excluded. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-04.png) |
| 17 | `FJP_237-p0155-l0021` | Complete bold one-word table-header continuation; table rule above lies outside the crop. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-04.png) |
| 18 | `COO_642-p0146-l0029` | Complete left-column hyphen continuation: preceding printed baseline ends with pa- in Greek. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-04.png) |
| 19 | `COO_642-p0124-l0035` | Complete right-column hyphen continuation of parallelogrammon in Greek; no clipped initial glyph. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-04.png) |
| 20 | `COO_642-p0126-l0042` | Complete left-column hyphen continuation of logon in Greek; bracketed word and accents retained. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-04.png) |
| 21 | `JZT_969-p0054-l0010` | Genuine one-word wrapped bullet continuation; bullet is on the preceding baseline. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-05.png) |
| 22 | `COO_642-p0148-l0012` | Complete wrapped right-column mathematical prose baseline; no left-column ink. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-05.png) |
| 23 | `COO_642-p0115-l0016` | Complete left-column polytonic prose baseline; accents and punctuation match visible print. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-05.png) |
| 24 | `PPJ_147-p0004-l0001` | Complete bold TOC chapter heading; page-number region lies to its right. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-05.png) |
| 25 | `HBW_692-p0067-l0010` | Complete italic author-name table cell; neighboring ruling is outside the crop. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-05.png) |
| 26 | `DQR_373-p0124-l0017` | Complete bibliography continuation baseline; preceding author baseline carries the bullet. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-06.png) |
| 27 | `WJX_465-p0089-l0013` | Complete justified numbered baseline within right column; independent left prose excluded. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-06.png) |
| 28 | `BBX_333-p0071-l0096` | Complete body prose baseline; the page gutter lies beyond its right edge and may describe another region. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-06.png) |
| 29 | `FJP_237-p0140-l0035` | Complete small-font right table-cell prose baseline; adjacent left description is separate. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-06.png) |
| 30 | `COO_642-p0144-l0042` | Complete right-column mathematical prose baseline; left polytonic column excluded. | [sheet](../../bench/runs/O1d_20261007/columns/sample30-06.png) |

This remains a heuristic layout detector: tables, ragged lines and short text can look like columns; a candidate gutter is conservative evidence, not semantic layout certification. Continuous glyph geometry cannot prove glyph identity. The review's M01 mixed-contrast/thin-ink loss, M02 inside-box/noise/finite-halo blind spots and M03 pool semantics remain pending for O2. The LOW O1_FORMATS documentation issue remains outside this task's specified file scope; Cycle 4 rules are recorded here. Nothing is sealed.

## O4-fix — admission LABEL policy replay, 7 October 2026

**Certified Cycle 4/O1d inputs preserved; no extraction rerun or pool reselection.** Admission now
stores the original source label as `text_raw`, normalized NFC label as `text`, and version
`label_policy = nfc-separators-lunate/v1`. Unicode whitespace (including NBSP/thin spaces, TAB/LF/CR/NEL,
Zl/Zp) and U+200B/U+FEFF become trimmed single ASCII word boundaries. Other format/control characters
remain literal. Owner lunate folds `ϲ→ς`, `Ϲ→Σ` also belong here. Raw C0/C1 controls still reject;
normalization does not waive geometric multiline/spacing checks. `crop_text` continues to compare
literally with `text_raw`; text-derived features, hashes and duplicate state use `text`.

The codec applies canonical decomposition only, preserving every accepted NFC label literally.
Unsupported raw separators/lunate characters reject instead of being rewritten by the codec.
LABEL policy applies before selection/sealing; existing sealed references must remain literal.

Full document-order replay of **637,407 records** (**628,468 native, 8,939 scans**), with per-document
duplicate state, changed `text` on **9,365 native rows / 899 already-admitted rows**, and zero scans.
**Zero admission/reason disagreements; all rule counters unchanged; 358,471 admissions retained.**
All **357,299 codec-accepted admitted labels** round-trip literally on `text`; **1,172** admitted rows
remain explicit codec exclusions. No extraction, rendering, image inspection or seal is claimed here.

| Frozen O1d pool | Lines whose `text` changed |
|---|---:|
| modern_greek | 24 |
| polytonic_historical_greek | 0 |
| polytonic_historical_greek.supply | 0 |
| european_latin | 0 |
| mixed_script | 17 |
| headings | 5 |
| footnotes_small | 0 |
| short_lines | 2 |
| cyrillic | 0 |
| cyrillic.supply | 0 |
| capped_unique | **43** |
| supply_unique | **0** |
| all_unique | **43** |

Strata overlap. All 43 distinct pool changes are codec-accepted and match the independent review's
43 IDs; capped and overall losses stay **74/17,678** and **106/21,033** after LABEL normalization.
The replay writes separate label projections, changed-label ledger and frozen-membership normalized
pool records under `bench/runs/O4_fix_20261007`. Source record/pool SHA256 checks pass; O1d is unchanged.
[Replay receipt](../../bench/runs/O4_fix_20261007/admission_replay.json),
[script](../../bench/runs/O4_fix_20261007/replay_admission.py),
[current codec audit](../../bench/runs/O4_fix_20261007/codec_audit.json),
[saved-output verification](../../bench/runs/O4_fix_20261007/saved_replay_verification.json),
[CP-O4 reply](reviews/CP-O4_reply_1.md).

**CP-O4-M01 scope decision:** the O1d union's **28 lines / 94 U+0323 underdots** and
**2 lines / 2 U+03D0 ϐ occurrences** are recognized scholarly Greek features, not automatically bad
labels. Keep them in the denominator and preserve the reviewer's complete reject ledger. Retain
whole-line rejection in the fixed 339-atom v2 inventory for this repair; defer image-verified,
separately versioned expansion. Neither underdot removal nor ϐ→β folding is authorized.

Validation: **218 passed, 1 skipped** in the full benchmark suite, plus **1 passed** for the added
exhaustive frozen-raw-label test. The two copied reviewer acceptance cases pass with literal assertions
on admission's `text`, and the raw thin-space/repeated-space cases separately enforce rejection/literal
preservation. Independent recertification remains pending. No network, installs or sub-agents.
