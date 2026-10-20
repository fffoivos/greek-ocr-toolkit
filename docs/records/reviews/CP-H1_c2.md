**HOLD for scale-up. The original examples are corrected, but two HIGH geometry issues remain.**

Independent offline review of `5c8b39d..4af4fc5`. Tracked files and archived records remained unchanged; `.review_tmp` was removed. No network calls or background jobs were launched.

1. **HIGH — Global column bands admit fragments of genuine full-width rows.** [core.py:128](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/harvest/core.py:128), [core.py:158](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/harvest/core.py:158), [pipeline.py:133](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/harvest/pipeline.py:133). On `d163abb4… p112`, the lower glossary has two real columns, while the upper prose spans the page. Applying the glossary’s gutter globally splits `l0037` inside its sentence. The right fragment, “Fifth on his exaltation.”, passes crop, body-font and straightener gates with no flags. On the single-column catalogue page `8e3c482e… p24`, invented bands reject intact `l0026` and admit both artificial pieces of `l0027`. **Before scale-up:** distinguish spanning rows and local column regions before splitting.

2. **HIGH — Neighbour ownership still rejects valid single rows.** [pipeline.py:256](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/harvest/pipeline.py:256), [pipeline.py:264](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/harvest/pipeline.py:264). The measured denominators and strict thresholds are correctly implemented: occupied crop rows **>12%**, or retained ink span **>30%** of crop width. However, `0907df73… p23 l67` counts the target word’s own accent as neighbour ink: **8 pixels, 4/32 rows**, causing rejection. `c6f5e826… p45 l57` counts scattered scan grain: **29 pixels**, spanning **73.16%** of the width. The random audit below finds **3/10 unjustified exclusions**, meeting the mandated HIGH threshold; two concern slivers and one concerns column inference. **Before scale-up:** establish actual neighbouring-row ownership before applying these thresholds.

3. **MEDIUM — A visibly ruled table escapes the revised page gate.** [core.py:236](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/harvest/core.py:236), [core.py:242](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/harvest/core.py:242). `d80c7cca… p49` contains a ruled table on its right page. The detector reports horizontal rules **0**, vertical rules **2**, lattice **true**, and accepts the page. The required AND condition is implemented, but horizontal-rule detection misses this real table. Logged for follow-up.

**Ten randomly selected newly rejected sampled lines**

Selection: `random.Random(20261012).sample(sorted(rejected_sample_ids), 10)`, population **126**. I inspected page context, raw/straight crops and replayed component masks. IDs are abbreviated to their unique book hash and page/line. Visibly retained watermark contamination was counted conservatively as a justified exclusion.

| Line ID | Justified? | By-eye reason |
| --- | --- | --- |
| `6976af7d… p26 l35` | Yes | Retained watermark ink intrudes at the right-hand text. |
| `042c93b2… p155 l5` | Yes | Extraneous watermark pixels remain over the final numeric citation. |
| `d163abb4… p112 l14` | Yes | Separate left/right glossary entries are fused across a real gutter. |
| `0907df73… p23 l67` | **No** | The flagged component is the target word’s own accent. |
| `00c322b3… p88 l26` | Yes | Substantial watermark intrusion remains at the right edge; the mask also wrongly includes an own descender. |
| `ff1a79b2… p45 l30` | Yes | Retained watermark strokes contaminate the final words. |
| `0550c3c5… p49 l65` | Yes | Visible fragments of the preceding row remain above the target. |
| `8e3c482e… p24 l26` | **No** | One continuous printed row; the inferred gutter is fictitious. |
| `d9831a20… p23 l26` | Yes | A retained watermark stroke enters above the opening text. |
| `c6f5e826… p45 l57` | **No** | Scattered scan specks trigger the span threshold; no neighbouring text row intrudes. |

**Unjustified rejections: 3/10.**

**Original examples and five additional two-column pages**

Bands use page-ink gutters and box clusters; extraction splits polygons before gating, and reader joins receive column coordinates. Original p23 `l0038` and p24 `l0011/l0012` reject with `crosses_column`. Their splits preserve **6,196 / 5,497 / 5,846** dark pixels respectively; both stored reader outputs now reject cross-gutter joining.

| Additional page | Page-render observation |
| --- | --- |
| `c20219ef… p48` | Two prose bands preserved; clean passing rows in both. |
| `97da3257… p28` | Facing prose pages correctly separated; body rows preserved. |
| `bf2ce6d1… p30` | Facing commentary pages correctly separated; body rows preserved. |
| `d163abb4… p112` | Lower glossary fusion splits correctly without ink loss; upper spanning prose exposes HIGH 1. |
| `00c322b3… p87` | Facing body text remains separated; clean passing rows in both. |

The original neighbour example `1697d5cc… p106 l41` now rejects correctly: **158 retained upper pixels**, **5/32 rows = 15.625%**, span **572/796 = 71.8593%**.

The cycle-1 bordered prose page `0cb3f672… p20` now passes: **3 horizontal / 4 vertical rules**, no lattice. Portable fetch tests load the repository fixture at [test_harvest.py:144](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/tests/test_harvest.py:144).

Independent recount matched **14,200 records**, **8,074 rejects**, **2,012 added rejects**, **106 releases**, and **126 sampled rejects**. Read-only gate replay matched the sidecars for **507 originals across nine pages**. Historical tiers and labels remain unchanged.

Requested tests: **119 passed, 2,359 deselected, 0 failures/errors**. Earlier rare-glyph/gallery MEDIUM findings and tilted-row LOW remain outside this fix.

VERDICT: HOLD fix spanning-row geometry and neighbour ownership before scale-up | BLOCKERS: 0 | HIGH: 2