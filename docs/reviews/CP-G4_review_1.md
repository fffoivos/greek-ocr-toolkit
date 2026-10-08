# CP-G4 certification

**HOLD.** [Full report with reproductions, raw failures, tables, and fixes](CP-G4_review_1.md).

Five **HIGH** findings:

1. **Tight cropping corrupts cut fractions:** the same top-clipped source reports **60% → 33.3%** merely by enabling `tight=True`.
2. **Edge-touch gating fails both ways:** completely removed breathing marks receive “readable”; upper-line fragments make an intact main line “unreadable.”
3. **Calibration measures differ from production:** ungated strip averages supply thresholds applied to gated, per-position profiles.
4. **Exported limits violate the stated rule:** E1’s clean band yields no cut/skew limits; CLLG’s measured tail bins never cross the band.
5. **The shipped default is unqualified:** saved m0.2 images match `level_deg=0`; **37/40** level outputs differ under the shipped `level_deg=0.3`.

**Claims re-derived:** saved OCR tables reproduce to rounding. Page counts reproduce **195 / 241 / 8**, with **227 selected cards** and **13.14 MB HTML**. The bootstrap supports the reported point estimate, but does not establish equivalence within +0.005.

**Cleared:** faint-bold regression probes, owner-shadow removal, tested edge-sharpness cases, base interpolation, and page data/DOM checks. Committed tests: **57 passed**. Independent adversarial tests: **5 failed, 1 passed**. Published-page equivalence and browser paint remain unverified because access failed.

VERDICT: HOLD Fix five HIGH API/calibration findings before handoff; residual faint-bold deletion cleared. | BLOCKERS: 0 | HIGH: 5