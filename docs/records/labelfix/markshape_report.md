# Mark-shape classifier (ink-decisive variant)

Samples: vowels of words where Google = human = model on the three-way lines (seed 0 alignments), well-localised only: 13312 (4481 dev-book, 8831 held-out-book); classes with ≥ 15 samples: 12.

159 features (counts, sizes, slope, elongation, hook, skew, position + two 8×8 shape thumbnails). Softmax regression: held-out accuracy 94.3 %; one-hidden-layer MLP (96 tanh units, Adam, class-balanced): held-out accuracy 94.9 %. Chosen: **mlp** (dev-fit accuracy 98.5 %, **held-out accuracy 94.9 %**).

**Confidence threshold tau = 0.998**: on held-out samples, predictions with p ≥ tau are 99.05 % correct and cover 29.8 % of the samples (2636).

| tau | held-out predictions with p ≥ tau | precision |
|---|---:|---:|
| 0.8 | 8554 | 96.61% |
| 0.9 | 3330 | 96.52% |
| 0.95 | 3220 | 97.24% |
| 0.98 | 3062 | 98.07% |
| 0.99 | 2949 | 98.44% |
| 0.995 | 2819 | 98.65% |
| 0.999 | 2506 | 99.16% |
| 0.9995 | 2350 | 99.32% |

Mark-vs-mark only (truth and prediction both carry a mark; the mark ↔ none confusions are the extractor losing a blob, which the removal abstentions guard separately):

| tau | n | precision |
|---|---:|---:|
| 0.95 | 2843 | 98.49% |
| 0.99 | 2631 | 99.43% |
| 0.995 | 2524 | 99.48% |

| class | samples (all) | held-out n | recall (argmax) | precision at tau | n at tau |
|---|---:|---:|---:|---:|---:|
| acute | 1867 | 1277 | 92.2% | 99.6% | 1096 |
| circumflex | 536 | 279 | 91.0% | 97.6% | 83 |
| circumflex+subscript | 58 | 36 | 83.3% | 100.0% | 1 |
| dasia | 316 | 194 | 75.8% | 100.0% | 78 |
| dasia+acute | 127 | 93 | 88.2% | 100.0% | 31 |
| grave | 1001 | 587 | 91.0% | 99.6% | 474 |
| none | 8019 | 5396 | 99.1% | 93.5% | 248 |
| psili | 949 | 633 | 88.6% | 99.8% | 493 |
| psili+acute | 324 | 259 | 73.7% | 100.0% | 132 |
| psili+circumflex | 37 | 26 | 61.5% | - | 0 |
| psili+grave | 20 | 10 | 50.0% | - | 0 |
| subscript | 58 | 41 | 90.2% | - | 0 |

## Held-out confusion (truth → predicted, counts ≥ 2)

| truth | predicted | n |
|---|---|---:|
| acute | none | 77 |
| grave | none | 41 |
| psili | none | 37 |
| dasia | none | 30 |
| psili+acute | acute | 22 |
| psili | grave | 15 |
| psili+acute | none | 14 |
| circumflex | none | 14 |
| none | grave | 13 |
| psili+acute | dasia+acute | 11 |
| psili+acute | psili | 10 |
| none | psili | 10 |
| grave | psili | 9 |
| none | circumflex | 9 |
| acute | dasia | 8 |
| psili | dasia | 8 |
| psili+acute | circumflex | 8 |
| dasia+acute | acute | 8 |
| acute | psili+acute | 7 |
| circumflex | acute | 7 |
| psili | acute | 6 |
| circumflex+subscript | circumflex | 6 |
| none | acute | 6 |
| dasia | psili | 5 |
| none | dasia | 5 |
| dasia | grave | 5 |
| subscript | none | 3 |
| acute | psili | 3 |
| psili+circumflex | psili+acute | 3 |
| psili+acute | grave | 3 |
| dasia | psili+acute | 2 |
| psili+circumflex | none | 2 |
| grave | psili+grave | 2 |
| dasia | acute | 2 |
| dasia+acute | none | 2 |
| psili+grave | circumflex | 2 |
| psili | psili+grave | 2 |
| psili | psili+circumflex | 2 |
| acute | psili+grave | 2 |
| none | subscript | 2 |
| psili+circumflex | psili | 2 |
