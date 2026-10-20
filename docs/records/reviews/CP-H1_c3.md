**HOLD for scale-up. Two HIGH findings remain.**

Independent review of `bda44e1..3eaef30`; the scoped implementation matches `3eaef30`. No network calls, background jobs or tracked-file edits. `.review_tmp` was removed.

1. **HIGH — Local column regions still misclassify real layouts.** [core.py:218](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/harvest/core.py:218), [core.py:230](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/harvest/core.py:230), [core.py:258](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/harvest/core.py:258). `39efef08… p24 l11`, an original cycle-1 cross-column example, now becomes `full_width`, passes every gate and remains unsplit. Its crop visibly combines Greek and German columns. Conversely, fictitious gutters reject two continuous prose rows on `ef44b5f8… p40`; merged facing-page bands wrongly reject `d9831a20… p23 l54` and `d9d705c2… p27 l2`. These account for **4/13 unjustified tier-1 rejections**, meeting the mandated HIGH threshold. **Before scale-up:** preserve established columns through local interruptions and prevent unrelated text blocks from widening one band.

2. **HIGH — Genuine neighbour slivers are released.** [pipeline.py:293](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/harvest/pipeline.py:293), [pipeline.py:303](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/harvest/pipeline.py:303). Randomly selected `0550c3c5… p49 l65` now passes despite preceding-row fragments remaining in the straightened image. Replay identifies **22 neighbour pixels**, occupying **3/34 rows = 8.82%** and spanning **73.61%** of the width. No zone contact is recorded, so the correctly implemented AND threshold admits them. **Before scale-up:** remove these fragments while preserving target ink, or reject the contaminated crop.

**All 13 tier-1 rejections inspected by eye**

I inspected raw crops, straightened output and page context; sliver cases also received enlarged inspection against preceding rows. IDs abbreviate the unique book hash. Exact annotations are in [sampled_post_fix2_gate.json](</Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest/fix2/sampled_post_fix2_gate.json>).

| Line | Current reason | Justified? | By-eye assessment |
| --- | --- | --- | --- |
| `39efef08… p24 l12` | Cross-column/outside band | Yes | Separate Greek and German columns fused together. |
| `460b94bc… p25 l2` | Neighbour sliver | Yes | Preceding-row descender fragment remains above “Μοναστήριον”; distinct from its own accent. |
| `55beb2ad… p32 l37` | Neighbour sliver | Yes | Numerous preceding-row fragments remain across the upper edge. |
| `7d1e0986… p39 l47` | Neighbour sliver | Yes | Preceding-row descender remains above the target breathing mark. |
| `c194db93… p143 l6` | Neighbour sliver | Yes | Retained preceding-row fragment; the target’s accent lies separately below it. |
| `cc5059bc… p26 l38` | Table page | Yes | Text belongs to a visibly ruled financial table. |
| `cc5059bc… p26 l42` | Table page | Yes | Same ruled table. |
| `d9831a20… p23 l54` | Short paragraph boundary | **No** | Complete right-page prose row measured against a band spanning both facing pages: 48.91%. |
| `d9d705c2… p27 l2` | Width under 80% | **No** | Complete left-page verse; the facing title widens its band, reducing coverage to 50.44%. |
| `e28081a0… p92 l11` | Neighbour sliver | Yes | Preceding-row descender remains above “δραχμὴν”; its own accent is separate. |
| `e988c466… p60 l12` | Width under 80% | Yes | Complete but short verse, covering 78.27% of the observed band; exclusion follows the stated 80% sampling rule. |
| `ef44b5f8… p40 l11` | Cross-column/outside band | **No** | One continuous prose row; inferred gutter is a word space. |
| `ef44b5f8… p40 l13` | Cross-column/outside band | **No** | Same fictitious gutter cuts a continuous sentence. |

**Unjustified: 4/13. All five tier-1 sliver rejections are justified.**

**Ten random releases inspected**

Selection: `random.Random(20261012).sample(sorted(ids), 10)`, from **105 sampled lines** rejected by Fix 1 and accepted by Fix 2.

| Released line | Visual result |
| --- | --- |
| `727f1e3f… p65 l3` | No obvious neighbour row; watermark remains. |
| `042c93b2… p155 l5` | No obvious neighbour row; watermark remains over the citation. |
| `fdbb6015… p30 l34` | No obvious retained neighbour row after straightening; watermark remains at the start. |
| `0907df73… p23 l67` | Target’s own diacritic; release justified. |
| `00c322b3… p88 l26` | No obvious neighbour row; watermark remains at the right edge. |
| `0550c3c5… p49 l65` | **Genuine preceding-row fragments retained: release unjustified.** |
| `a38a4960… p3 l16` | Single row with its own marks. |
| `ffe26907… p159 l24` | Clean own-diacritic control passes. |
| `f22ded41… p53 l33` | No definite retained neighbour fragment in replayed straight output. |
| `a30e8286… p20 l9` | Scan grain remains; no definite neighbouring letter identified. |

The requested assurance fails: **at least one definite neighbour sliver was released.**

**Spanning-row checks**

| Page | Independent result |
| --- | --- |
| `d163abb4… p112` | `l30–37` pass intact. Lower fused `l5/l8/l14/l16` each split into two pieces with no dark-pixel loss. Original example corrected. |
| `d163abb4… p113` | Upper prose remains intact; tested interiors pass. Lower fused `l9` splits, preserving all 3,819 dark pixels. |
| `39efef08… p23` | Spanning note `l28–31` passes intact; lower multi-column fused parents split. |
| `39efef08… p24` | Spanning note `l25–30` passes intact; lower `l12` splits. **Lower fused `l11` incorrectly passes unsplit**, exposing HIGH 1. |

**MEDIUM ruled-table finding fixed:** `d80c7cca… p49` reports **two closed cells** and rejects as `table`. Framed prose `0cb3f672… p20` reports **zero cells** and passes. Relevant implementation: [core.py:354](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/harvest/core.py:354), [core.py:400](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/harvest/core.py:400). Earlier unrelated MEDIUM/LOW findings remain logged outside this scope.

Independent recount matches **14,200 records, 6,655 rejects, 37 sampled rejects and 13 tier-1 rejects**. Read-only replay matched page, crop, body-font and ownership annotations for **1,322 distinct originals across 27 pages**, including every audited line. Historical records’ SHA-256 remained unchanged.

Requested tests, with `TMPDIR=$PWD/.review_tmp`, bytecode disabled and cache provider disabled: **143 passed, 2,359 deselected; no failures or errors**.

VERDICT: HOLD fix column-region misclassification and retained neighbour slivers before scale-up | BLOCKERS: 0 | HIGH: 2