# T14 — Native-pixel montage verification

**Recommended N: none.** Largest N meeting ≥97% exact NFD equality and zero merged/lost crops in **both** readers, on the same frozen 100 lines.

Comparison reference is each reader's cached single-crop **cleaned reading** (`readers.<engine>.text`). This measures preservation, not OCR accuracy. Raw single text, unchanged raw-response hashes and settings are in [sample.json](montage_v1/sample.json). No cached crop was recalled. No production reader defaults were changed.

## Text and assignment

| N | Reader | Identical | Median NFD CER | Merged crops | Lost crops | Split crops | Montages | USD / 1,000 lines | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | vision | 63.0% (63/100) | 0.000000 | 0 | 0 | 2 | 10 | 0.1500 | FAIL |
| 10 | docai | 82.0% (82/100) | 0.000000 | 0 | 0 | 0 | 10 | 0.1500 | FAIL |
| 20 | vision | 63.0% (63/100) | 0.000000 | 0 | 0 | 1 | 5 | 0.0750 | FAIL |
| 20 | docai | 81.0% (81/100) | 0.000000 | 0 | 0 | 0 | 5 | 0.0750 | FAIL |
| 40 | vision | 60.0% (60/100) | 0.000000 | 0 | 0 | 0 | 3 | 0.0450 | FAIL |
| 40 | docai | 76.0% (76/100) | 0.000000 | 0 | 0 | 1 | 3 | 0.0450 | FAIL |

## Symbol confidences

Means are weighted across all reported symbols with confidence, assigned by the same ≥70% height rule for montages. Symbol counts can change with the transcription; this is not paired symbol calibration. Per-crop means/counts are retained in [comparisons.jsonl](montage_v1/comparisons.jsonl).

| N | Reader | Single mean | Montage mean | Delta | Single symbols | Montage symbols | Unassigned montage symbols |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10 | vision | 0.881149 | 0.879437 | -0.001712 | 4795 | 4812 | 0 |
| 10 | docai | 0.942372 | 0.942204 | -0.000168 | 4817 | 4818 | 0 |
| 20 | vision | 0.881149 | 0.879362 | -0.001787 | 4795 | 4803 | 0 |
| 20 | docai | 0.942372 | 0.942395 | 0.000023 | 4817 | 4817 | 0 |
| 40 | vision | 0.881149 | 0.879439 | -0.001710 | 4795 | 4802 | 0 |
| 40 | docai | 0.942372 | 0.942190 | -0.000182 | 4817 | 4816 | 0 |

Confidence deltas are small despite the text differences. A median CER of zero reflects that more than half of the crops are identical; it does not satisfy the 97% preservation gate.

## Method and audit

Selection: sort sampled pilot IDs within tier, `random.Random(14).sample` 40/40/20, then seeded shuffle. This purposive tier-balanced sample is not a population estimate. Exactly the same order is used for every N. [Frozen sample and baseline hashes](montage_v1/sample.json).

Native pixels, no scaling or stretching. Left-aligned crops are padded with white 255 to the widest crop. Between crops: max(60 px, the two adjacent native heights), with a centred 2px grey-153 rule (40% black). No added outer padding. Crop boxes and separator intervals are half-open. Split at 10,000 px height or 8,000,000 encoded PNG bytes; width ≤2,600 px. [All montage maps](montage_v1/manifest.json).

DocAI uses reported line layout boxes/text anchors (paragraph fallback only without lines). Vision uses reported symbol breaks within paragraphs and unions their symbol boxes. A box touching two bands is merged and is never guessed into a crop; otherwise ≥70% vertical height overlap assigns it. Zero assigned lines = lost; ≥2 = split. Flags are independent, so merged and lost can overlap. Side-by-side splits use the pilot list-return rule in x order; stacked splits retain LF-separated text and rejection flags. Unassigned boxes, every line and every symbol assignment are in the per-montage `*.assignment.json` files.

NFD comparison keeps whitespace in the cleaned reading, without substitutions or accent folding. CER = NFD codepoint Levenshtein distance / cached single NFD length (minimum denominator 1). Assignment uses box height, never intersection area. Split crops are permitted by the requested gate, if equality remains ≥97% and merged/lost are both zero.

Vision uses DOCUMENT_TEXT_DETECTION, `el` + `grc`, provider default model (unpinned); DocAI uses the same pilot EU processor, `pretrained-ocr-v2.1-2024-08-07`, `el`, symbols enabled. Context and the unpinned Vision model can both affect readings. The verdict applies to this layout and sample only.

Cost: **34 calls reserved; USD 0.0510** at conservative standard list price; cap USD 1. Rate USD 0.0015 per image/page, checked 12 October 2026: [Vision pricing](https://cloud.google.com/vision/pricing), [Document AI pricing](https://cloud.google.com/products/document-ai/pricing). Monthly free allowances are not deducted; this is a list-price receipt, not a billing invoice. Cost per 1,000 lines uses actual montage count / 100, including partial final batches and any size splits. With full batches, either reader costs $0.1500/$0.0750/$0.0375 per 1,000 lines at N=10/20/40; both readers together cost twice those rates.

17 unique montage PNGs produced 34 calls across 36 reader/N evaluations. The final 20-crop batch at N=40 is byte-identical to the N=20 tail and reuses both responses. At-most-once: persistent budget reservations precede reader invocation; successful raw/parsed responses are reused, and interrupted/failed reservations are not automatically recalled. Only generated montage hashes are eligible for network calls. [Receipt](montage_v1/receipt.json).

Bulk PNGs and Google raw responses are in the repo's ignored `docs/records/harvest/harvest_big/montage_v1/`, inside the writable workspace. Original pilot images/caches remain at the supplied external `glossapi-ocr-local` path. Only maps, baseline hashes, assignments, comparisons, summary and receipt are in the versionable report directory. [100-crop review](montage_review.html).

## Validation

Offline tests cover native pixel conservation, padding/rules/maps, N batching, encoded-size/height splits, oversize refusal, synthetic Vision and DocAI layouts/symbols, 70% boundaries, cross-band merge/lost, side-by-side joins, stacked splits, NFD whitespace/CER, the 97% gate and symbol-weighted means. Final test and gallery QA receipts are linked from receipt.json. The offline validator checks all native montage pixels, every assignment/metric, all 100 gallery cards/images/local links, and unchanged cached single inputs.

Visual inspection of the native first montage confirms the separated crop bands and rules. Browser-rendered desktop/narrow QA is **unverified**: Chromium launch was rejected by the macOS sandbox (`bootstrap_check_in ... Permission denied`); the computer-use tool returned `Computer Use was not approved to use Firefox`. [QA receipt](montage_v1/gallery_qa.json).

Final validation: **247 passed** (32 T14 tests plus existing harvest/reader/API contracts); all 600 comparisons and assignments replayed offline with zero additional API calls. No N qualifies, so final-line identical percentages refer to the largest tested N, **40**.

T14: done | N_adopt: none | identical_vision: 60.0% | identical_docai: 76.0% | calls: 34 | tests: 247 passed

## Controls

**T14b verdict: the readers reproduced every single crop, while montages still changed text. Recommended N for adoption: none.** N=20 remains the tested candidate size; removing the grey rule does not qualify it. The single-vs-single baseline is **100% exact NFD and 100% letters+marks for both readers (30/30)**, including unchanged raw text. This control provides no evidence that reader nondeterminism explains T14's montage differences.

### Frozen sample and fresh calls

30 of T14's 100 crops: **15 with identical Vision N=20 reads and 15 with differing reads**. Sort IDs within strata, use `random.Random(1402)`, retain the one crop containing the reported `*` in the differing stratum, sample the other 14 differing crops, and preserve T14 order after selection. The strata contain 63 identical / 37 differing crops in the original pilot. This outcome-stratified, artifact-inclusive control is not a population agreement estimate; its 50% ruled Vision baseline is fixed by selection. Compare all three modes on this same 30-crop cohort. [Frozen IDs, original crop/raw-response hashes and bindings](montage_v1/determinism/sample.json).

Each native single crop was read **once more by each reader: 60 fresh calls**. Historical caches were deliberately bypassed using the separate `montage_v1/determinism/google/` namespace. Adapter ledgers verify one uncached successful response per image/reader, distinct receipt IDs from the cached single reads, unchanged image bytes and identical reader settings. Vision: DOCUMENT_TEXT_DETECTION, `el` + `grc`, unpinned provider default. DocAI: the same EU processor and `pretrained-ocr-v2.1-2024-08-07`, `el`, symbols enabled. Existing crop-gate context and list-return cleanup were applied to the new single reads. Raw single-vs-single text also matches 30/30 in each reader, so cleanup did not conceal differences. [New singles](montage_v1/determinism/singles.jsonl).

The same 30 crops form two no-rule images, **20 + 10 crops**, read once per reader: **four calls**. Native pixels, alignment, padding, limits and gap formula are unchanged: each gap is `max(60, left native height, right native height)` and entirely white 255. No scaling, no grey pixels added in a gap. The 10-crop tail is a partial N=20 batch. [Images and box maps](montage_v1/determinism/norule/manifest.json). Regrouping the selected crops changes their neighbors relative to the original 100-crop T14 montages. Thus this is not a perfectly paired separator-only ablation; the results support rejection of equivalence, but do not isolate the rule's contribution to the agreement changes.

### Agreement

Exact means equality after NFD decomposition of cleaned readings, with whitespace and punctuation preserved. Letters+marks means apostrophe variants first unified, then NFD Unicode L/M codepoints retained; case, base-letter variants and combining marks remain distinct. Punctuation (including edge punctuation), whitespace, numbers and symbols are ignored in that diagnostic. It does not establish word-boundary or punctuation preservation. The same helper recounts the full original N=20 cohort as **63% exact / 70% letters+marks for Vision and 81% / 89% for DocAI**, matching the coordinator's letters+marks recount.

| Comparison | Reader | Exact vs cached single | Letters+marks vs cached single | Exact vs new single | Letters+marks vs new single |
| --- | --- | --- | --- | --- | --- |
| single-vs-single | Vision | **100.0% (30/30)** | **100.0% (30/30)** | — | — |
| single-vs-single | DocAI | **100.0% (30/30)** | **100.0% (30/30)** | — | — |
| montage(rule)-vs-single | Vision | 50.0% (15/30) | 60.0% (18/30) | 50.0% (15/30) | 60.0% (18/30) |
| montage(rule)-vs-single | DocAI | 70.0% (21/30) | 83.3% (25/30) | 70.0% (21/30) | 83.3% (25/30) |
| montage(no rule)-vs-single | Vision | **53.3% (16/30)** | **60.0% (18/30)** | **53.3% (16/30)** | **60.0% (18/30)** |
| montage(no rule)-vs-single | DocAI | **73.3% (22/30)** | **83.3% (25/30)** | **73.3% (22/30)** | **83.3% (25/30)** |

All cached/new montage-reference metrics agree because the new single texts equal the cached texts. Per-crop text, exact/letters+marks comparisons, minimum-edit alignments and both strata's summaries are retained in [300 comparisons](montage_v1/determinism/comparisons.jsonl) and [summary.json](montage_v1/determinism/summary.json).

| No-rule assignment, N=20 | Merged | Lost | Split | Rejected |
| --- | --- | --- | --- | --- |
| Vision | 0 | 0 | 0 | 0 |
| DocAI | 0 | 0 | 0 | 0 |

### Difference kinds

Counts below are **changed NFD codepoints on both sides** of one minimum-Levenshtein alignment; a substitution contributes two codepoints and an insertion/deletion one. Edit-operation counts are separate. Alignment ties resolve diagonal, deletion, insertion. Cached and new references give the same histograms. Every per-crop operation and kind transition is machine-readable in the comparisons.

| Comparison | Reader | Letters | Marks | Numbers | Punctuation | Symbols | Whitespace | Other | Delete / insert / substitute edits |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| single-vs-single | Vision | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 |
| single-vs-single | DocAI | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 / 0 |
| montage(rule)-vs-single | Vision | 11 | 10 | 2 | 6 | 1 | 4 | 0 | 5 / 11 / 9 |
| montage(rule)-vs-single | DocAI | 7 | 11 | 0 | 6 | 5 | 1 | 0 | 6 / 4 / 10 |
| montage(no rule)-vs-single | Vision | 17 | 12 | 4 | 8 | 3 | 5 | 0 | 10 / 17 / 11 |
| montage(no rule)-vs-single | DocAI | 5 | 11 | 0 | 1 | 5 | 0 | 0 | 6 / 6 / 5 |

The no-rule montage still changes letters and marks. Its exact agreement is only one crop higher per reader than the historical ruled comparison in this selected cohort; letters+marks agreement is unchanged.

### The asterisk control

**The Vision `*` does not disappear.** Crop `anemi-b8b71bfd410ddd2e68429ffe-vda613211-p000022-l0044` has no asterisk in either Vision single read, but one leading `*` in both montage reads. There is exactly one `*` in the complete new Vision montage raw text, so it was not merely dropped during assignment. DocAI emits `**` on this same crop in both single reads and both montage reads.

The original ruled Vision symbol box is `[0, 766, 7, 791]` inside crop band `[765, 793)`. The no-rule box is `[0, 391, 7, 416]` inside band `[390, 418)`. Both map to the same crop-relative box `[0, 1, 7, 26]`, rather than a separator gap. Native visual inspection shows small leading ink at that location; its intended glyph is not adjudicated here. The original claim that this particular asterisk was the grey separator is unsupported by its geometry and its persistence without any rule. [Raw-bound symbol geometry](montage_v1/determinism/asterisk_geometry.json).

### Adoption decision and limits

The conditional proposal is **“no merged/lost and agreement ≥ single-vs-single − 3 points.”** With the observed 100% single-vs-single baseline, its threshold is **97%** for both exact and letters+marks agreement. Both no-rule readers fail by large margins: exact deficits are **46.7 points (Vision)** and **26.7 points (DocAI)**; letters+marks deficits are **40.0** and **16.7 points**. Neither montage layout is equivalent to single reads on this control. There is no basis to relax the adoption gate or promote N=20. The original 97% exact gate remains applicable to these results; no production setting is enabled.

One fresh repeat on 30 crops establishes observed repeatability under the recorded settings, not universal determinism or permanence of Vision's unpinned model. Neither cached nor new single readings are ground truth. N=10 and N=40 were not freshly controlled; their historical T14 results also failed the 97% gate. Therefore the adoption recommendation remains **none**, with **N=20** retained only as the candidate size for any later separately authorized evaluation.

### Cost, custody and validation

**64 successful uncached calls, USD 0.0960 conservative base list-price estimate; cap USD 0.50.** Vision 32 calls and DocAI 32 calls. Rates of USD 1.50 / 1,000 image-feature or page units were checked 12 October 2026 against [Vision pricing](https://cloud.google.com/vision/pricing) and [Document AI pricing](https://cloud.google.com/products/document-ai/pricing). Free allowances and account discounts are not deducted; this is not a billing invoice. A local driver metadata error stopped after the first successful pair; resumption reused both saved responses and introduced no duplicate calls. Persistent reservations prevent automatic retries. The subsequent offline report rebuild and both validators made zero additional service calls.

All new singles, raw and parsed responses, budgets/adapter ledgers, no-rule images/maps, assignments and reports are under `docs/records/harvest/montage_v1/determinism/`. Original pilot crops/records/caches and frozen T14 comparisons are SHA-verified unchanged. Historical T14 source hashes remain in the parent receipt; a separate current replay-source binding records the optional no-rule extension. [Control receipt](montage_v1/determinism/receipt.json), [updated parent receipt](montage_v1/receipt.json), [inventory](../../INVENTORY.md#t14b-montage-controls-12-october-2026).

**277 tests passed**, including 30 new offline T14b cases and the 247 existing montage/harvest/Google-reader/API cases. Tests cover L/RGB native pixels, unchanged bands and gap sizes, all-white padding/gaps, rule coordinates absent, N=20 partial batches/height splits, boolean validation, exact NFD, apostrophe variants, retained accents/case/sigma differences, every character kind, minimum-edit histogram semantics, aggregation, interrupted-attempt refusal, the 64-call budget ceiling, and distinguishing shared other-worktree Git changes from main-worktree metadata. [JUnit results](montage_v1/determinism/tests.xml).

The offline control validator checks 60 distinct fresh single receipts, four fresh montage receipts, all 300 comparisons and both references, raw-response hashes, native pixels and white gaps in both images, line assignment, original input custody and unchanged main-worktree Git metadata. The historical T14 validator also replayed all 600 comparisons and 18 maps with the extended module's unchanged default layout. [Control validation](montage_v1/determinism/validation.json), [T14 replay validation](montage_v1/validation.json). No `.git` writes were performed by this task. A later final audit detected changes to the other `ff-plan` worktree, its `astra/ff-plan` branch/reflog, and shared objects; the reflog records a concurrent commit there. Main HEAD/index/branch metadata remained unchanged. Shared activity is recorded in [Git audit](montage_v1/determinism/git_audit.json), so the final receipt does not claim global `.git` metadata was unchanged.

T14B: done | single_vs_single_exact_vision: 100.0% | single_vs_single_exact_docai: 100.0% | montage_norule_vs_single_vision: 53.3% | montage_norule_vs_single_docai: 73.3% | calls: 64 | tests: 277 passed

## Flush layout

13 October 2026. **Recommended flush N: none.** Same frozen 100 T14 lines and cached single cleaned readings; exact NFD and the unchanged T14b letters+marks helper measure preservation, not accuracy.

Flush uses native pixels, zero gaps, no rules and no outer padding. Left-aligned bands meet exactly; each band's right padding uses its own median of the brightest ceil(50%) pixels (RGB estimation uses L luminance only; pasted colors remain native). Half-integral medians round upward for 8-bit padding. **82/100 crops have a measured median of 255**: those retain their own white shade; there is no unconditional white fallback. The other shades range from 162 to 241. [Per-crop shades, heights, source/sorted indices and groups](montage_v1/flush/grouping.json).

Sort stably by `(background shade, crop height)`, using frozen T14 order for ties, then take consecutive groups of 10 and 20. All batches are full; no size splits. Rule rows reuse the historical 100-line T14 reads. T14b's no-rule control covered only 30 selected lines at N=20, so **30 additional no-rule calls** expand that identical gap/no-rule renderer to the full 100 lines at N=10/20, in original T14 order. Historical T14b results remain above. The expanded rule/no-rule pair shares neighbors; flush changes neighbors as well as layout. This experiment therefore assesses the combined flush-and-grouping hypothesis and does not isolate the effect of gaps alone.

| Layout | N | Reader | Exact NFD identity | Letters+marks identity | Merged crops | Lost crops | Split crops | Merged boxes | Unassigned boxes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rule | 10 | vision | 63.0% (63/100) | 72.0% (72/100) | 0 | 0 | 2 | 0 | 0 |
| rule | 10 | docai | 82.0% (82/100) | 89.0% (89/100) | 0 | 0 | 0 | 0 | 0 |
| rule | 20 | vision | 63.0% (63/100) | 70.0% (70/100) | 0 | 0 | 1 | 0 | 0 |
| rule | 20 | docai | 81.0% (81/100) | 89.0% (89/100) | 0 | 0 | 0 | 0 | 0 |
| no rule | 10 | vision | 63.0% (63/100) | 75.0% (75/100) | 0 | 0 | 1 | 0 | 0 |
| no rule | 10 | docai | 83.0% (83/100) | 89.0% (89/100) | 0 | 0 | 0 | 0 | 0 |
| no rule | 20 | vision | 58.0% (58/100) | 69.0% (69/100) | 0 | 0 | 1 | 0 | 0 |
| no rule | 20 | docai | 82.0% (82/100) | 87.0% (87/100) | 0 | 0 | 1 | 0 | 0 |
| flush | 10 | vision | 56.0% (56/100) | 63.0% (63/100) | 16 | 8 | 3 | 8 | 0 |
| flush | 10 | docai | 58.0% (58/100) | 63.0% (63/100) | 56 | 31 | 0 | 31 | 0 |
| flush | 20 | vision | 59.0% (59/100) | 64.0% (64/100) | 19 | 10 | 1 | 10 | 0 |
| flush | 20 | docai | 53.0% (53/100) | 59.0% (59/100) | 57 | 35 | 0 | 35 | 0 |

All 100 crops remain in every denominator, including merged/lost crops. Assignment is unchanged: a reported box overlapping two adjacent bands marks every touched crop merged even if one overlap is ≥70%; it is never guessed into one band. Otherwise ≥70% of box height assigns it. Zero assigned lines is lost, ≥2 is split; flags are independent, so merged and lost can overlap. Side-by-side splits retain T14 cleanup; stacked splits retain LF and rejection. Every raw-bound line/symbol and overlap is retained in the [assignment audits](montage_v1/flush/manifest.json) and [1,200 crop comparisons](montage_v1/flush/comparisons.jsonl).

![First N=10 flush montage, native pixels](montage_v1/flush/preview_n10.png)

Preview is a byte-identical native copy of the first N=10 flush PNG (149,906 bytes).

**N=10: do not adopt.** Flush reaches 56.0% exact identity for Vision and 58.0% for DocAI; merged/lost are 16/8 and 56/31, respectively. Adoption requires ≥97% exact identity and zero merged/lost in both readers.
vision: not closer to singles than both gap layouts; exact changes vs rule/no rule are -7.0/-7.0 percentage points.
docai: not closer to singles than both gap layouts; exact changes vs rule/no rule are -24.0/-25.0 percentage points.

**N=20: do not adopt.** Flush reaches 59.0% exact identity for Vision and 53.0% for DocAI; merged/lost are 19/10 and 57/35, respectively. Adoption requires ≥97% exact identity and zero merged/lost in both readers.
vision: not closer to singles than both gap layouts; exact changes vs rule/no rule are -4.0/+1.0 percentage points.
docai: not closer to singles than both gap layouts; exact changes vs rule/no rule are -28.0/-29.0 percentage points.

The verdict applies only to these 100 lines, recorded bindings, grouping and layout. Cached single text is not ground truth; Vision remains unpinned. No production default is changed.

**60 successful uncached calls: 30 flush + 30 expanded no-rule, USD 0.0900 conservative list-price estimate; cap USD 0.50.** Rate USD 0.0015 per image/page checked 13 October 2026 against [Vision pricing](https://cloud.google.com/vision/pricing) and [Document AI pricing](https://cloud.google.com/products/document-ai/pricing). Free allowances/discounts are not deducted; this is not an invoice. Persistent reservations precede every invocation, successful parsed/raw responses are reused and failed/interrupted attempts are never automatically retried. Zero single-crop calls; all 200 original single responses are reused and hash-verified.

Bulk PNGs and Google raw/parsed responses, budgets and adapter ledgers are under ignored `docs/records/harvest/harvest_big/montage_v1/t14c/`. Maps, groups, assignments, comparisons, preview, test results and audit are under `montage_v1/flush/`. Original T14/T14b evidence and external pilot records/crops/single raw responses remain hash-verified. [Flush receipt](montage_v1/flush/receipt.json), [updated parent receipt](montage_v1/receipt.json), [offline replay validation](montage_v1/flush/validation.json), [test results](montage_v1/flush/tests.xml), [inventory](../../INVENTORY.md#t14c-flush-montage-13-october-2026).

**304 offline tests passed (27 new flush cases).** Independent replay checks all native bands/padding, stable shade/height grouping, 1,200 comparisons, every line/symbol assignment, 60 unique raw-bound uncached API receipts, budget reservations and unchanged original inputs. All 18 historical rule PNGs and both historical no-rule PNGs regenerate byte-identically. No-flag rebuild and validator use no ADC or service calls. Native preview inspected visually. This task performed no `.git` writes; the [Git audit](montage_v1/flush/git_audit.json) records current metadata.
