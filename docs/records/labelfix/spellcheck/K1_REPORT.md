# K1 — qualified orthographic reading filter

Implemented on `opus/spellcheck`, observed HEAD `4e9d75ee`. No `.git` writes, network, geometry changes, classifier changes, recognition forward passes, training, or owner-page publication. The cached native S6 reread completed in about 30 seconds; the full task stayed within the 20-minute Mac CPU budget.

**Deploy the qualified subset.** Held-out removals: **100 marks = 90 false + 0 printed + 10 unknown**. DEV: **40 = 37 false + 0 printed + 3 unknown**. Unknown print slots are explicitly unscored; these 13 removals across both splits are not certified false. Atomic true positives and recall do not decrease in either scoring instrument. C1 after a consonant start and C3 are implemented, but globally held back because they remove known printed marks. Consequently some impossible-looking owner readings remain flagged; this does not close all owner complaints.

## Runtime and evidence

`greekocr/labelfix/reading.py:apply_constraints(LineReading)` returns a new reading and a list of removal records. Each record retains rule, letter, original recogniser NFD start, source component slot (or character index when unavailable), mark part, occurrence, detector evidence, and conflict alternatives. `removed_by_constraint` and `constraint_flags` are separate from unresolved detector marks. The input, masks, component labels, crop geometry, physical blobs, recogniser base letters, punctuation, and classifier naming evidence are preserved. Output parts retain their original tuple/list type.

`read_ink`, `read_line_details`, and `read_line` filter by default; `filtered=False` selects raw detector output. `read_line_details` exposes receipts and flags. R1 `map_lines(..., filtered=True)` filters predicted parts before frozen-slot scoring and reporting, and returns removal/tie counts separately. R1 classifier code and prediction files are untouched. Existing R1 prediction receipts contain no probabilities; the adapter explicitly clears detector naming confidence rather than treating it as R1 confidence. Optional per-part reader probabilities are accepted when available; otherwise area/distance are used and absent evidence ties. No R1 quality improvement is claimed here.

For competing marks, weaker support means lexicographically lower **classifier probability**, then **blob area / x-height²**, then **negative horizontal distance to letter centre / x-height**. Per-blob names use their actual named blob(s); whole-set names share the whole-set probability and blob support, explicitly labelled `whole_set_shared`. A compound is not assigned invented per-mark confidence. An exact weakest-support tie retains all competing marks and emits `evidence_tie`. C4 singleton illegality has no competing accent to rank: its receipt records the supported mark and the keep-mark alternative. The filter deletes; it cannot turn a grave into an acute or circumflex.

Rules reuse the census syllable, diphthong, coronis/crasis, medial double-rho, all-caps, hyphenated-part and final-enclitic conventions in `constraints.py`. Missing breathings are never inserted. C7 is only Unicode rendering/canonicalisation, with no deletion count. The soft before-antepenult rule is not applied. No added lexicon or Google/human string reaches the filter.

## Qualification and denominators

All **666 held-out lines** and **598 DEV lines** are evaluated. Raw readings, parts and serialized physical evidence were asserted equal to frozen S6 on every line while regenerating classifier support from cached alignments. Support is stored separately in `K1_support.jsonl.gz`, bound to S6, both model files and the alignment cache by `K1_support_receipt.json`.

The brief states both a 99% false-mark gate and that any printed removal must be held back. This implementation uses the stricter second instruction: any known printed conflict on either split disables the complete subrule. It reruns all remaining rules to a fixed point because removing C3 or C1 changes downstream C4 proposals. The runtime allowlist is asserted equal to the qualified set. Zero-proposal subrules have zero observed true removals and remain enabled under that allowance, but have **no empirical removal precision estimate**. This is qualification on the supplied cohort, not an independent future generalisation test.

Proposed individual-mark removals when all rules run, in processing order. Columns are **false / printed / unknown** according to S6 character PRINT truth. Unknown words and base-letter mismatches remain unknown. This is the candidate audit; actual deployed counts follow, because held-back rules change later proposals.

| Rule | Held-out proposals F/P/U | DEV proposals F/P/U | Runtime |
|---|---:|---:|---|
| `C1:breathing_after_consonant_start` | 70 / 0 / 8 | 23 / 1 / 9 | held back |
| `C1:breathing_not_initial` | 26 / 0 / 4 | 5 / 0 / 0 | enabled |
| `C1:smooth_breathing_on_rho` | 0 / 0 / 0 | 0 / 0 / 0 | enabled |
| `C2:breathing_with_dialytika` | 0 / 0 / 0 | 0 / 0 / 0 | enabled |
| `C2:mark_on_consonant` | 7 / 0 / 1 | 7 / 0 / 0 | enabled |
| `C2:two_accents_one_letter` | 0 / 0 / 0 | 0 / 0 / 0 | enabled |
| `C2:two_breathings` | 0 / 0 / 0 | 0 / 0 / 0 | enabled |
| `C3:two_accents` | 21 / 16 / 4 | 20 / 0 / 3 | held back |
| `C4:circumflex_before_penult` | 8 / 0 / 0 | 5 / 0 / 1 | enabled |
| `C4:circumflex_on_short_vowel` | 4 / 0 / 0 | 3 / 0 / 0 | enabled |
| `C4:grave_not_final` | 29 / 0 / 5 | 4 / 0 / 1 | enabled |
| `C5:dialytika_not_on_iota_upsilon` | 0 / 0 / 0 | 0 / 0 / 0 | enabled |
| `C6:subscript_not_under_alpha_eta_omega` | 0 / 0 / 0 | 0 / 0 / 0 | enabled |

Actual qualified removals, **false / printed / unknown**:

| Rule | Held out F/P/U | DEV F/P/U |
|---|---:|---:|
| `C1:breathing_not_initial` | 26 / 0 / 4 | 5 / 0 / 0 |
| `C2:mark_on_consonant` | 7 / 0 / 1 | 7 / 0 / 0 |
| `C4:circumflex_before_penult` | 16 / 0 / 0 | 7 / 0 / 2 |
| `C4:circumflex_on_short_vowel` | 5 / 0 / 0 | 7 / 0 / 0 |
| `C4:grave_not_final` | 36 / 0 / 5 | 11 / 0 / 1 |

All proposals and applied removals, with evidence: [K1_proposals.jsonl](K1_proposals.jsonl), [K1_removals.jsonl](K1_removals.jsonl). Filtered text and held-back flags: [K1_readings.jsonl.gz](K1_readings.jsonl.gz). There are 169 held-back candidate flags and no evidence ties on this S6 cohort; synthetic tests exercise ties.

## Printed-mark conflicts — held back

C1 after a consonant start proposes 93 false, 1 printed, and 17 unknown removals across both splits. The printed DEV witness is a rough breathing in `Ναὕρουν`; the census coronis exception permits psili, not this dasia. C3 proposes 41 false, 16 printed, and 7 unknown removals. Some printed accents belong to words whose other detector accent is false; selecting the weaker classifier score can still delete the printed accent. Existing enclitic exceptions are retained without expanding their word list.

Every known printed proposal is listed below (not applied). Full alternative evidence: [K1_printed_conflicts.jsonl](K1_printed_conflicts.jsonl).

| Line ID | Split | Rule | Letter / source slot | Printed mark proposed for deletion |
|---|---|---|---|---|
| `9c1dca9b-p000015-l0058` | held out | `C3:two_accents` | ε / 17 | acute |
| `02a3a2a6-p000022-l0010` | DEV | `C1:breathing_after_consonant_start` | υ / 3 | dasia |
| `177b717d-p000105-l0009` | held out | `C3:two_accents` | ε / 19 | acute |
| `177b717d-p000104-l0007` | held out | `C3:two_accents` | η / 9 | acute |
| `384c3f89-p000096-l0039` | held out | `C3:two_accents` | ι / 17 | acute |
| `384c3f89-p000142-l0003` | held out | `C3:two_accents` | ο / 26 | acute |
| `384c3f89-p000091-l0011` | held out | `C3:two_accents` | ο / 28 | acute |
| `51fe7386-p000024-l0015` | held out | `C3:two_accents` | υ / 11 | acute |
| `384c3f89-p000096-l0032` | held out | `C3:two_accents` | ο / 24 | acute |
| `384c3f89-p000053-l0027` | held out | `C3:two_accents` | η / 24 | acute |
| `384c3f89-p000179-l0006` | held out | `C3:two_accents` | η / 2 | acute |
| `384c3f89-p000205-l0017` | held out | `C3:two_accents` | ι / 18 | acute |
| `384c3f89-p000121-l0037` | held out | `C3:two_accents` | α / 12 | acute |
| `384c3f89-p000205-l0030` | held out | `C3:two_accents` | ω / 13 | circumflex |
| `4ad622a4-p000024-l0025` | held out | `C3:two_accents` | ε / 31 | acute |
| `4ad622a4-p000024-l0025` | held out | `C3:two_accents` | ο / 43 | grave |
| `4ad622a4-p000024-l0025` | held out | `C3:two_accents` | ω / 48 | circumflex |

## Mark precision and recall

The frozen S2–S6 component instrument keeps the same slots, bounding boxes, truth, and unknown denominators. Atomic scoring separates a compound breathing and accent. Semantic scoring treats a compound as one item, so deleting a false companion can recover an exact semantic true positive without adding any mark. Character atomic scoring uses S6 character truth and exposes fused-letter coverage separately. Apostrophes and unresolved-name penalties retain each instrument’s S6 conventions.

| Split / instrument | Known / unknown slots | TP, FP, FN before → after | Precision before → after | Recall before → after |
|---|---:|---|---:|---:|
| heldout / frozen atomic (primary) | 18229 / 2647 | 4177,297,326 → 4177,213,326 | 93.3616% → 95.1481% | 92.7604% → 92.7604% |
| heldout / frozen semantic | 18229 / 2647 | 3731,245,322 → 3744,196,309 | 93.8380% → 95.0254% | 92.0553% → 92.3760% |
| heldout / character atomic | 19249 / 1176 | 4431,336,423 → 4431,246,423 | 92.9515% → 94.7402% | 91.2855% → 91.2855% |
| dev / frozen atomic (primary) | 9724 / 2105 | 2234,127,243 → 2234,94,243 | 94.6209% → 95.9622% | 90.1897% → 90.1897% |
| dev / frozen semantic | 9724 / 2105 | 2110,120,229 → 2112,92,227 | 94.6188% → 95.8258% | 90.2095% → 90.2950% |
| dev / character atomic | 11149 / 772 | 2546,156,310 → 2546,119,310 | 94.2265% → 95.5347% | 89.1457% → 89.1457% |

## Current owner notes and implicit approvals

Current note files are `owner_notes_review_v16_20261016.jsonl` and `owner_notes_examples_v10_20261016.jsonl`; all clauses use the unchanged S6 owner-note instrument, including its physical-blob checks. No detector evidence is removed, so physical mark-presence clauses are preserved. Complete before/after receipts: [K1_owner_checks.jsonl](K1_owner_checks.jsonl).

| Current set | Fully satisfied notes before → after | Satisfied clauses before → after |
|---|---:|---:|
| review | 36/49 → 36/49 | 59/74 → 59/74 |
| examples | 33/57 → 33/57 | 76/100 → 76/100 |

The original S4→S6 implicit-change receipt contains 94 changed page rows, including 52 implicit-approval rows. K1 reproduces `scripts/labelfix/owner_implicit_changes.py:slot_of_letters` exactly (cached CTC maximum-overlap native-component numbering), rather than conflating it with S6 certified character ownership. All changed rows resolve uniquely; unresolved = 0. These are owner-approval inferences, not new print truth.

Implicit false added mark instances **45 → 40**; affected implicit rows **38 → 35**. Counts preserve the source receipt’s separate review/examples page rows, including duplicates. Deduplicated `(line, character start, mark)` false additions: **45 → 40**. Previously approved but missing mark instances remain **28 → 28**: deletion cannot recover missing marks. Full comparison: [K1_implicit_changes.json](K1_implicit_changes.json).

Concrete owner readings under the qualified default (not proposed all-rule repairs):

| Line | Before | Qualified after |
|---|---|---|
| `51fe7386-p000026-l0016` | Ἐμπρ͂ὂς τρ͂ἰσκότειδο καἶ πἷσω ἐχθροι. | Ἐμπρὸς τρἰσκότειδο καἶ πἷσω ἐχθροι. |
| `177b717d-p000097-l0007` | ὀ Σηκουάνας πὄχεἵ πνίξει, | ὀ Σηκουάνας πὄχεἵ πνίξει, |
| `8b6b0de9-p000021-l0012` | Τί ἂν ὁ βἳος διαρκῇ | Τί ἂν ὁ βἱος διαρκῇ |
| `384c3f89-p000182-l0031` | σχέτλιος. ἣ τέ οἱ αἲψα καταυτόθι νόστον ἀπηύρων, | σχέτλιος. ἣ τέ οἱ αἰψα καταυτόθι νόστον ἀπηύρων, |

`αἶψα` stays unchanged. In `αἲψα`, the breathing on the second vowel of initial αι is legal; the nonfinal grave is removed, yielding `αἰψα`. `κἀγώ`, `Τυῤῥηνῶν`, and initial `ῥ` are preserved. `πὄχει` is preserved under the encoded coronis exception. A breathing in `πὄχεἵ`, and some other consonant-start words, remains with a held-back flag until the track lead decides C1. This is a measured residual, not a claim that every impossible output has been eliminated.

## Verification and reproduction

**181 tests passed; 1 existing test has an environment setup error.** The complete `tests/labelfix` run has no assertion failures after preserving the existing tuple API. `test_capture.py::test_server_appends_each_decision_and_serves_static` cannot create its localhost HTTP fixture: `socket.bind` raises `PermissionError: [Errno 1] Operation not permitted` under this sandbox. No existing tests were edited or weakened, and no network permission was requested. Therefore “all labelfix tests green” cannot be claimed in this environment. The separate runnable-only invocation reports 181 passed, 1 deselected.

New tests cover the requested owner-word cases; impossible consonant/letter marks; double breathing and accent conflicts; shared-blob ties; per-blob probability, area and distance ranking; enclitic and line-final exceptions; copy/physical-evidence preservation; original NFD offsets; selectable public reading; held-back rules; C4 alternatives; and R1 filtering before reporting. Full suite log: [K1_pytest.txt](K1_pytest.txt); runnable subset: [K1_pytest_runnable.txt](K1_pytest_runnable.txt).

Run from this workspace, with the requested Python and `PYTHONPATH=$PWD`:

```sh
PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python
PYTHONPATH=$PWD "$PY" scripts/labelfix/k1_validate.py
# Reuse hash-bound classifier support, with no classifier calls:
PYTHONPATH=$PWD "$PY" scripts/labelfix/k1_validate.py --reuse-support
PYTHONPATH=$PWD "$PY" -m pytest tests/labelfix -q
```

[K1_metrics.json](K1_metrics.json) contains all denominators, rule counts, qualification iterations, owner summaries, source hashes, and runtime-policy equality. Recogniser construction and forward alignment plus socket connections fail closed in the audit. The full cached reread asserted S6 text, parts and physical evidence equality for all 1,264 lines. Tracked differences are confined to the reading module and R1 scoring adapter; geometry/classifier files and existing tests have no tracked differences.

K1 RESULT: removed 100 marks (90 false per print truth, 0 printed; 10 unknown); applied rules C1:breathing_not_initial, C1:smooth_breathing_on_rho, C2, C4:grave_not_final, C4:circumflex_on_short_vowel, C4:circumflex_before_penult, C5, C6; held back C1:breathing_after_consonant_start, C3:two_accents; mark P 93.3616%→95.1481% R 92.7604%→92.7604%; owner implicit false marks 45→40.
