# CP-G3c2 — fix certification

**HOLD. F1 remains HIGH; F2–F9 reproduce as fixed.** [Full report with raw evidence](</Users/foivoskarounos-zamparloukos/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/review_scratch/CP-G3c2/CP-G3c2_review_1.md>).

| Finding | Disposition | Firsthand result |
|---|---|---|
| F1 — faint-letter deletion | **Not fully fixed** | Original undilated example retains 2,419/2,419 pixels. Original heavier probes still fail: dilation-4 `ΘΩΜΒ` retains **0/6,672**. Undilated bold capitals also disappear. |
| F2 — cut-edge attribution | Fixed | Baseline −10 gives top/bottom **1/0**; baseline 40 gives **0/1**. Original owner contradictions fall to zero. |
| F3 — flattened coordinates | Fixed | Right-column letter now **1458..1464**, segment 1. All flattened fields and offsets verified across 40 builder records. |
| F4 — builder crash | Fixed through migration | Full builder: **408 unseen crops in 43.2 s; 40 records written**. |
| F5 — None prior | Fixed | Omitted and None priors both return one segment **0..1484**. |
| F6 — sparse rule | Fixed | Original rule detected at **400..403**; two segments returned. |
| F7 — over-inked capitals | Fixed | Original dilated Μ and Θ each retain one box. |
| F8 — neighbour evaluation | Fixed | **167/199** matched; strict precision **167/189 = 88.36%**. Zero-match probe completes without crashing. |
| F9 — capitals wording | Fixed | Reproduced **118 scored lines, 2,057 capitals, 98 splits: 95 doubles and 3 triples**. |

## New finding — residual F1, HIGH

[components.py:106](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/greekocr/glyphs/components.py:106): the new size/thickness conjunction still classifies legitimate letters as patches.

At gray 195 on paper 235, with three separate dark dots:

| Complete letter | Crop height | Pixels retained | Letter boxes |
|---|---:|---:|---:|
| Undilated Noto Sans Bold **Ε** | 48 | **0/704** | **1 → 0** |
| Undilated Source Serif 4 Bold **Ι** | 45 | **0/451** | **1 → 0** |
| Didot **Ι**, dilation 1 | 49 | **0/424** | **1 → 0** |

Disabling only the rejection block preserves every pixel. Adding paper margin to make each crop 140 pixels high also preserves every pixel under current code.

**Required fix:** preserve supported faint/bold lettering as measurement candidates and distinguish shading using spatial extent and line support. Add tight-crop and actual-bold-font regressions while retaining the owner-shadow test. This and F1 count as **one HIGH**.

## Cleared

- **Committed tests:** `51 passed in 15.67s`.
- **Original independent tests:** `1 failed, 6 passed in 0.48s`. The remaining assertion requires obsolete top-level `baseline`/`second`; both original builder commands now succeed using the migrated schema.
- **Owner shadow:** still removed. First-60-column ink fraction is **7.35%**; **55 boxes**, maximum height **36 px / 1.7143 x-heights**, none beginning in the shadow region.
- **Thickness removal:** no outside-line stain box in the owner fixture or eight controlled rectangle probes. Dark line-sized stains can now receive a bounded box; taller patches remain excluded.
- **Neighbour regression:** original counts and placement reproduce, including median error **0.0470162 x-heights**.
- **Page:** JavaScript/DOM structure passes with 40 figures and correct segment translations. **Actual browser layout/paint remains unverified** because browser execution is unavailable here.
- All **26 scoped tracked files** match `b5a639d`; the repository remained read-only.

VERDICT: HOLD Fix residual faint-letter deletion before S3; F2–F9 cleared, browser paint unverified. | BLOCKERS: 0 | HIGH: 1