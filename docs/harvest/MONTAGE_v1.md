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

Bulk PNGs and Google raw responses are in the repo's ignored `docs/harvest/harvest_big/montage_v1/`, inside the writable workspace. Original pilot images/caches remain at the supplied external `glossapi-ocr-local` path. Only maps, baseline hashes, assignments, comparisons, summary and receipt are in the versionable report directory. [100-crop review](montage_review.html).

## Validation

Offline tests cover native pixel conservation, padding/rules/maps, N batching, encoded-size/height splits, oversize refusal, synthetic Vision and DocAI layouts/symbols, 70% boundaries, cross-band merge/lost, side-by-side joins, stacked splits, NFD whitespace/CER, the 97% gate and symbol-weighted means. Final test and gallery QA receipts are linked from receipt.json. The offline validator checks all native montage pixels, every assignment/metric, all 100 gallery cards/images/local links, and unchanged cached single inputs.

Visual inspection of the native first montage confirms the separated crop bands and rules. Browser-rendered desktop/narrow QA is **unverified**: Chromium launch was rejected by the macOS sandbox (`bootstrap_check_in ... Permission denied`); the computer-use tool returned `Computer Use was not approved to use Firefox`. [QA receipt](montage_v1/gallery_qa.json).

Final validation: **247 passed** (32 T14 tests plus existing harvest/reader/API contracts); all 600 comparisons and assignments replayed offline with zero additional API calls. No N qualifies, so final-line identical percentages refer to the largest tested N, **40**.

T14: done | N_adopt: none | identical_vision: 60.0% | identical_docai: 76.0% | calls: 34 | tests: 247 passed
