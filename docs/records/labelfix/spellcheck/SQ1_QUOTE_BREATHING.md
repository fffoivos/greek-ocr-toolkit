# SQ1 — Quote standing for a capital's breathing and accent

**The frozen checker does not release a correction for this line: it returns HOLD.** The recogniser reads `Ἄδεια`, with no quote, and R1-A reads psili+acute on Α. The composed proposal is correct at this position, but deleting Google's mid-line `"` fails both the punctuation edit guard and SF6's two-positive-absence requirement. No corrected label is emitted. This is different from the conditional lead prediction: if the recogniser retains `"`, the renderer will retain it while adding the capital's marks, producing `"Ἄδεια`. That conditional behavior is executable and confirmed; it is not what this recogniser actually read.

**The gate cannot distinguish an alias for a compound breathing from a real quote beside a breathing.** It has no mid-line test that assigns distinct physical ink groups to the two proposed symbols. Its current protection on this particular execution is abstention, not successful substitution.

## Single-line execution

Run on 17 October 2026 using the requested `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, CPU, four threads, one line only. Network was used only for the read-only Clariden census/probe. No model or detector ran remotely; no allocation, job submission, authentication refresh, policy edit or `.git` write occurred.

- Crop: `~/Projects/collect-v3-data/run/W1/crops/nlg--f4b52df5f8130047--s005-l0015.png`.
- Original Google: `Κοντεύανε μεσάνυχτα. "Αδεια διανυκτερεύσεως δὲν εἶχαν` (C1 key's original label, not a reconstructed approximation).
- E3 full_s0 recogniser: `Κοντεύανε μεσάνυχτα. Ἄδεια διανυκτερεύσεως δὲν εἶχαν` (NFC display). Local checkpoint exists at `~/Projects/greek-page-ocr/out/e3b/jobA/runs/full_s0/best.pt`, verified SHA-256 `5f300fdac73d7479769c98e27d068039186ac193c6c4002ddfc8be511d363663` before execution. This is a fresh single-line run, not a claim of byte-identical legacy saved confidence fields.
- R1-A: local `artifacts/labelfix_r1/output_3678928/A/best.pt`; digest saved in `line_result.json`. Four factors `[1,1,0,0]`: psili, acute, no dialytika, no subscript. Winning psili probability `0.9999959469`, acute `0.9998722076`.
- Α is display slot **19**, recogniser NFD start **23**, letter body `[465,7,496,39]`; case classifier says capital, probability `0.99999`. Its locator span is `[456.596,476.839]`, detector evidence window `[454.5,506.5]`.

### (a) Ink count and ownership

**One semantic spacing compound `῎`, represented by two detached component blobs, both owned by Α slot 19. There is no additional quote group.** Raw blob count must not be confused with the number of independently printed symbols:

| Source component | Native bbox | Area | Detector source | Owner |
|---|---|---:|---|---|
| 5, curled breathing | `[450,6,458,17]` | 61 | preposed | Α, slot 19 |
| 6, acute stroke | `[459,6,465,17]` | 34 | preposed | Α, slot 19 |

No other slot owns either source component; `opening_quotes=[]`. The S6 detector names the combined evidence `psili+acute`. The enlarged native crop visibly shows the curl and acute, agreeing with the owner's one-compound reading. This is **not** two groups “quote plus breathing/accent.” The frozen runtime exposes these as two blobs in one slot's `above` evidence; it does not expose a separate semantic compound-cluster identifier.

Owner-sheet `page_reading` generated [line_overlay.png](../../../../artifacts/sq1/line_overlay.png), using its actual detection-image renderer. The verifier confirms that its raw serialized evidence equals the executed runtime's raw detector evidence. [Enlarged compound](../../../../artifacts/sq1/compound_detail.png); [full runtime](../../../../artifacts/sq1/runtime.json); [owner sidecar](../../../../artifacts/sq1/owner_side.json).

### (b) Reader and (c) final gate

Both PRESENCE and FULL accept the Α slot's psili+acute. Both compose:

`Κοντεύανε μεσάνυχτα. Ἄδεια διανυκτερεύσεως δὲν εἶχαν`

Both final overlays return **HOLD**, with:

- `sf6:deletion_needs_two_positive_absences:quote`, Google NFD start 23 / letter boundary 18;
- `edit_guard:punctuation_mismatch` for Google versus recogniser and Google versus proposal.

The quote deletion has reader absence **false**, detector absence **false**, recogniser absence **true** on this fresh scored alignment. R1 heads name marks, not punctuation; the quote detector's absence head applies only at letter boundary zero. A scored recogniser alone cannot authorize this mid-line deletion. See [`deletion_guard`, lines 334–340 and 420–453](../../../../greekocr/labelfix/release_gate.py#L334), especially 441–448. The final consumer accumulates these vetoes and returns before emitting a label: [`l1_common.overlay`, lines 56–71](../../../../scripts/labelfix/clariden/l1_common.py#L56).

[Execution script](../../../../artifacts/sq1/run_line.py), [complete result](../../../../artifacts/sq1/line_result.json), [alignment](../../../../artifacts/sq1/alignment.json), [focused verification](../../../../artifacts/sq1/verification.txt). ENSEMBLE_AB was not locally inferred; the requested reader was R1-A. The production census covers AB separately.

## Why the conditional double-marking risk remains

- [`text.spacing_breathing`, lines 50–59](../../../../greekocr/labelfix/text.py#L50) accepts only `᾿᾽`; ASCII `"` is outside that predicate.
- [`_render_reading`, lines 100–113](../../../../greekocr/labelfix/release_gate.py#L100) consumes only that spacing-breathing representation when a slot adds breathing. Other non-slot characters pass through. A direct execution of `_render_reading('"Αδεια', [{start:1, parts:['psili','acute']}])` yields `"Ἄδεια`: [isolated witness](../../../../artifacts/sq1/conditional_renderer.json).
- [`_punctuation`, lines 116–128](../../../../greekocr/labelfix/release_gate.py#L116) strips quote aliases only from the beginning and otherwise compares punctuation; it has no physical symbol-count test.
- [`_compose_reading`, lines 638–640](../../../../greekocr/labelfix/release_gate.py#L638) likewise strips leading quote aliases, optionally restoring a detector opening quote, but retains a mid-line quote from the recogniser.
- [`release_text`, lines 158–199](../../../../greekocr/labelfix/release_gate.py#L158) and SF6b MOVE checks at 353–393 support specified spacing signs, not a general quote-as-breathing interpretation. MOVE includes a `῾` mapping but the spacing attachment predicate itself remains restricted to `᾿᾽`; these paths must not be described as general quote support.
- [`edit_guard`, lines 228–229](../../../../greekocr/labelfix/release_gate.py#L228) rejects the actual mid-line quote deletion as a punctuation mismatch.

Affected alias family for a future cycle: `'`, `’`, `´`, `ʼ`, `"`, `“`, and `῾`-like quote renderings, alongside the other `LEADING_QUOTES` characters. They do not all currently share one canonicalization or deletion path.

**Fix shape, not implemented:** when Google has a quote/apostrophe alias immediately before a capital and release adds breathing and/or accent on that capital, keep both only if native ink supports **two separate symbol groups**, one quote and one breathing/accent compound. With one compound group, consume the quote alias as a replacement; when ownership, grouping or observation is unresolved, HOLD. Coordinate the renderer, punctuation comparison, release composition and deletion/MOVE guard so the same physical decision governs all four. Do not simply count connected components: this positive replacement witness has two components inside its one compound.

Regression sketch: freeze this crop, original Google label, located letters and native source masks. Require `Ἄδεια` with one consumed alias, no residual quote and no duplicated marks once the new gate is deliberately adopted. Include recogniser variants that retain and omit the alias, all listed aliases, incomplete/ambiguous grouping → HOLD, and a separate quote group → preserve both.

A real quote-plus-breathing control was found in the C1 card/key search and visibly checked: **W1 NLG dialogue_fiction c012**, `nlg--f4b52df5f8130047--s004-l0008`, Google `«Ἢ νἄπαιρνε κάνε μαζί του τὴν κοπέλα, νὰ τὴν κουκου-`. Its pixels show a separate opening `«` followed by a compound before Η. Require preservation of both, including a test where Google omitted the capital marks and the reader restores them. [Control crop](../../../../artifacts/sq1/real_quote_control.png), [C1 search and 27 text candidates](../../../../artifacts/sq1/c1_search.json). The other candidates are not asserted as pixel-verified controls.

## Read-only Clariden exposure census

Production run `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1e_20261017/l1r_sf6_3680729` is complete. The census streamed all three overlay files on the login node, with no remote filesystem writes. It checked unique IDs and exact population equality with the selection: **124,669 lines per mode**, including **1,753** original lines with a requested quote alias immediately before a Greek capital. The final scan took **64.57 seconds**. An initial scan was repeated after correcting modifier-apostrophe letter indexing and including word-initial lowercase spacing-breathing sites; total scan time was about 127 seconds. No authentication error occurred and no certificate refresh was attempted.

The production policy binding is `82f8d5423f88fdc05546ea834a878ce07c51399f60b7cb1150597db70be59363`; it binds the merged L1R3 packaging. Its gate SHA matches the frozen local gate; the local 16-path policy remains `6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406`. Packaging bindings are not interchangeable.

A match requires the same alphabetic base sequence and a newly added NFD psili, dasia, acute, grave or circumflex on the matched capital. Elision modifier characters are excluded from letter indexing, as in the frozen gate. Counts below are **actual emitted labels**, excluding HOLD proposals. Sites and unique lines are separately recorded; modes are not summed.

| Mode | (i) Kept quote + added mark, lines | (ii) Removed quote + added mark, lines | Matching HOLD proposals, lines | Google spacing-breathing lines / sites | Released spacing lines / attached sites |
|---|---:|---:|---:|---:|---:|
| presence | 0 | 0 | 54 | 167 / 169 | 0 / 0 |
| full | 0 | 0 | 54 | 167 / 169 | 0 / 0 |
| ensemble_ab | 0 | 0 | 54 | 167 / 169 | 1 / 1 |

**There are no ten example IDs for (i): its measured population is empty.** `examples_i=[]` in every mode. Ten HOLD proposal examples per mode, clearly labeled as HOLD, are retained in the JSON instead. Zero released exposure is an abstention result for this population; it does not establish that the gate has learned the physical distinction, nor cover the collect-v3 W1/W2/W3 population. The selected legacy waves are listed below.

Category (ii) is also empty, so no removal rule actually fired on a released quote-alias-plus-added-mark case. The code's leading-quote stripping and SF5/SF6b spacing MOVE paths are described above; they must not be reported as observed category-(ii) releases.

Per-alias results are identical across the three modes:

| Google alias | (i) lines | (ii) lines | Matching HOLD lines |
|---|---:|---:|---:|
| `“` | 0 | 0 | 9 |
| `”` | 0 | 0 | 0 |
| `«` | 0 | 0 | 17 |
| `»` | 0 | 0 | 1 |
| `„` | 0 | 0 | 0 |
| `"` | 0 | 0 | 17 |
| `'` | 0 | 0 | 10 |
| `’` | 0 | 0 | 0 |
| `´` | 0 | 0 | 0 |
| `ʼ` | 0 | 0 | 0 |

Per-wave results, also identical across modes for (i), (ii), HOLD and original spacing counts:

| Wave | (i) | (ii) | Matching HOLD | Google spacing lines |
|---|---:|---:|---:|---:|
| round1 | 0 | 0 | 29 | 94 |
| vouli | 0 | 0 | 6 | 21 |
| round2 | 0 | 0 | 7 | 26 |
| parliament | 0 | 0 | 7 | 3 |
| openarchives | 0 | 0 | 0 | 0 |
| mixed | 0 | 0 | 5 | 23 |

Per-source results for (i), (ii) and matching HOLD are identical across modes:

| Source | (i) | (ii) | Matching HOLD | Google spacing lines |
|---|---:|---:|---:|---:|
| anemi_round1 | 0 | 0 | 29 | 94 |
| vouli_parliament_1850s | 0 | 0 | 6 | 21 |
| anemi_round2 | 0 | 0 | 7 | 26 |
| parliament_proceedings_1975_2000 | 0 | 0 | 7 | 3 |
| openarchives_Pandemos | 0 | 0 | 0 | 0 |
| openarchives_kallipos | 0 | 0 | 0 | 0 |
| anemi_mixed | 0 | 0 | 5 | 17 |
| openarchives_mixed_ntua | 0 | 0 | 0 | 6 |
| openarchives_mixed_Pandemos | 0 | 0 | 0 | 0 |
| openarchives_mixed_apothesis | 0 | 0 | 0 | 0 |
| openarchives_mixed_ktisis | 0 | 0 | 0 | 0 |
| archive_b28038630 | 0 | 0 | 0 | 0 |

The JSON also includes wave × source cells for each mode. For contrast, the explicit `᾿᾽` spacing path has **167 lines / 169 sites** in the source; **165 lines / 167 sites** precede capitals, and two further sites are word-initial lowercase vowels. These are source candidate counts, not 169 successful MOVEs. Only ENSEMBLE_AB emits an attachment: one released line / one attached site, reported by the saved `spacing_breathings_attached` census. PRESENCE and FULL emit none. This does not claim that every spacing case is physically adjudicated.

[Census JSON](../../../../artifacts/sq1/census.json), [executed census script](../../../../artifacts/sq1/census.py), [script SHA receipt](../../../../artifacts/sq1/census.sha256). Script SHA-256: `d4c0ca595efaa6fc3e9e68584de3b4bae14ce7ab74bf0afabb49e1dcf26a5fda`. Input selection/receipt hashes, exact overlay paths, compressed sizes, policy source map, examples and per-mode cells are in the JSON. The script uses standard-library text/JSON inspection, not inference or gate recomposition, with a 210-second alarm.

## Frozen-scope verification

All **30** local labelfix Python files and the **16 policy paths** were hash-checked before and after (overlapping files counted once in the receipt). No protected bytes changed. [Before](../../../../artifacts/sq1/protected_before.json), [after](../../../../artifacts/sq1/protected_after.json). The one-line executable verification confirms detector/owner-sidecar equality, source-blob ownership, R1 factors, both final HOLD decisions and the isolated quote-retaining renderer witness. No gate fix was implemented.

SQ1 READY: line emits HOLD; clusters 1 compound (2 component blobs); distinguishes no; exposure (i) kept-quote+added-mark 0 lines, (ii) 0; fix shape stated
