# Fast line finding, rounds 3–4 — B: faintness, inkiness, images

**Round4:** the expensive negative ornament search is replaced by a cheap local
recurrence nomination ahead of the unchanged verifier. The former305ms agreement
tail is now14.126/14.098ms for B in two fresh runs. All195 outputs remain exact.
Local component observability, image/text intersections and unrolled stamp rings
now have explicit and fast renderings, but do not justify new suppression or
semantic unreadability labels. See [round4 evidence](../../../.astra/fast_lines/out/features_ink/round4/index.html)
and the detailed continuation below. The round3 results remain as historical
measurements; they are not the new timing results.

The study now renders darkness separately from stroke condition, reflected glyph
support separately from darkness, and repeated ornaments separately from area
texture. The conditional Q8+B candidate removes **61 mirrored-print boxes and 11
ornament boxes on 13 supplied pages**. All 40 agreement controls stay unchanged.
Every proposed removal was inspected in raw and contrast-stretched crops. These
are observed corrections, not a measured recall/precision claim.

**Partial:** letter unreadability, causal under/over-inking, overlapping stamps,
watermarks and general image exclusion are not solved. The median clean-control
cost is small, but some clean-control tails are not negligible. No production
`greekocr/pages/` code or tests changed. No held-out pages were accessed.

## Evidence and scope

Open [the evidence gallery](../../../.astra/fast_lines/out/features_ink/index.html),
[final corrections and detector JSON](../../../.astra/fast_lines/out/features_ink/study-v2/index.html),
and [per-line comparisons](../../../.astra/fast_lines/out/features_ink/route-comparisons.json).
Legends and commands are in the [prototype README](../../../prototypes/fast_lines/features_ink/README.md)
and [output README](../../../.astra/fast_lines/out/features_ink/README.md).

The full correction cohort is the round-2 allowlist: 54 development plus 141
supplied pages, comprising 40 agreement and 101 discrepancy pages. Orientation
remains parked. Explicit component work covers 12 pages and **793 detector ROIs**:
the eight named anchors/control pages (394 ROIs), plus ef4816 p150, 31f40 p1,
77d1 p1 and 200e p35 (399). Four pages also have fresh existing-model character
statistics and overlays. All 279 ROIs on four faintness pages have actual normal
edge profiles. There is no claim of complete manual glyph adjudication across
195 pages. All 72 changed B boxes, all accepted ornament types, important route
outliers and selected raw page views were inspected; all measured ROI values
remain available, including failures.

`reference-v1/` contains native threshold/width strips, raw mirror comparisons
and the first failed area-texture renderer. `reference-v2/` and `reference-v3/`
contain side-by-side slow/R1/R2 pages. `reference-v4-controls/` adds counterexamples.
`density/` and `density-v2/` explicitly show optical depth outside detector boxes.
`stroke-comparisons/` exposes the largest width disagreements. `cooperation/`
holds C-derived contact/grid hypotheses with copied source and hashes.

The old model and stopped `8e5c522` false-positive work supply operators and
hypotheses, not reference labels. The source images, rather than either line
list, decide whether a removal is plausible. No PDF text layer is used.

## “We want to know faintness and ink-ness, to ignore back page letters, or which letters are unreadable”

### Faintness: explicitly rendered before ownership

Local paper-normalized contrast is independent of stroke geometry. The fresh
existing-model renderings expose its weakness: faint/broken material still feeds
its under-inking category. Native original-pixel measurements at three thresholds
make that conflation visible without copying it into a new class.

The full-page density rendering first used local morphological paper maxima. It
coloured too much paper grain, particularly on 0ce9. The second cycle smooths the
paper estimate and uses a noise floor. It exposes the second printed layer beyond
Paddle boxes, but residual grain and shadows still appear as weak contrast. R1
uses reduced local paper estimation; R2 substitutes a global paper level. R2
strongly colours the dark upper margin on 0ce9 and cannot distinguish faint front
print on `an-1be60011c435-p000215`. Neither mask authorizes suppression.

A separate edge experiment follows actual intensity rays normal to local stroke
edges. Version 1 used discrete 20/80 crossings and admitted tiny paper transitions.
Version 2 interpolates crossings and imposes a contrast-relative amplitude floor.
Controlled attenuation preserves spread; controlled blur increases it. Inspected
pale-front and ghost lines nevertheless both have spreads near 0.05 height units.
The 48-ray R1 and 8-ray R2 measurements are rendered against dense profiles, line
by line. Eight-ray estimates are less stable; softness is not verso ownership.
Corners, touching strokes and the proxy height remain confounders.

Ownership therefore needs an additional spatial feature: asymmetric components
are matched against ordinary and reflected same-page strong-print exemplars.
The reference permits up to256 components per ROI/exemplar line; R1 bounds this
to64 and12 exemplar lines. Shapes retain aspect compatibility, with direct and
reflected correlation witnesses. A tone/core scout nominates work; darkness alone
never removes anything. Four consistent asymmetric votes and a two-to-one margin
support a back hypothesis. A weak row can borrow support only from two independent
nearby back seeds with similar core contrast; propagation is not recursive.
These thresholds are prototype assumptions, not calibrated probabilities.

The first raw query crops were too faint to inspect. Enlarged raw plus separately
contrast-stretched query/reflection/exemplar tiles resolved that display failure.
The display transform does not alter measurements. On all 793 explicitly studied
ROIs, R1 ownership equals the dense reference; agreement between algorithms is
not ground truth. On 0ce9, several actual mirrored glyphs supply the evidence.
One visibly ghost-like row nevertheless obtains an ordinary/front hypothesis:
**front and unknown must never certify a recovered line**.

R2's first sparse vote sample (12 query/24 exemplar glyphs,6 anchor rows) found
16 back boxes on 0ce9 versus56 for dense/R1. Increasing it to24/48 finds54, but
this is not simply two omissions: dense back52,53,56 become unknown, dense
unknown32 becomes back, and dense front40 becomes unknown. Pale-front rows7,9
also change state. The bounded sparse route remains diagnostic; the final stack
keeps R1. Pure tone/global-paper and edge heuristics are rejected as ownership
rules because their rendered counterexamples are visible.

Accepted removals:56 boxes on `s2-0ce9d1025b3f23c7119e-p00001`, box0 on
`s2-93f8070059f938bda524-p00001`, and12,13,45,113 on
`s2-31f40cef90235c91b023-p00001`. On31f40 some crop rectangles include nearby
front letters; inspection of final union coverage shows those letters stay in
retained boxes. The reference gallery retains that coverage check.

Remaining failures include the visible short/overlapping ghost rows on
`an-ef481610a820-p000150` and p151, symmetric glyphs, weak pages without three
strong exemplars, watermarks without mirrored letter evidence, and mixtures
inside a single component. `s2-09f5dfca4af4d74173c6-p00005` receives no back-box
removal; the visible weak layer is not fully separated. This is neither a complete
front/verso segmentation nor a watermark detector.

Ready as an experimental module: `shared/ink_ownership.py`, with
`analyze(gray, items, regions=None, detail=False, route='explicit')`. Requested
rectangles use full-page coordinates. Returned suppress indices refer to those
rectangles. Track C can call it only on proposed gaps; its independent recovery
study did reject a mirrored 0ce9 addition using this interface.

### Inkiness: stroke condition, not merely weak contrast

The explicit renderer measures darkness and, at0.35/0.50/0.70 of local contrast,
distance-ridge width, fill, holes and small fragments. Native raw/support/width
strips show where thresholds break a stroke, fill a counter or join neighboring
print. Components are observed ink fragments, not guaranteed characters.
`readability` stays `unknown`. A dark thick glyph may be intentional typography;
a faint intact glyph need not be under-inked.

Known interventions on one real clean crop in `perturbations/axes.jpg` distinguish
axes without claiming that untouched pages suffered the same damage:

| Intervention | Contrast | Width / height | Holes | Components |
|---|---:|---:|---:|---:|
| Original | 0.843 | 0.129 | 2 | 51 |
| Attenuated | 0.299 | 0.129 | 2 | 50 |
| Thinned | 0.413 | 0.118 | 0 | 60 |
| Thickened | 0.968 | 0.212 | 3 | 50 |
| Broken | 0.827 | 0.118 | 0 | 70 |
| Blurred | 0.551 | 0.212 | 1 | 51 |

Attenuation leaves width intact. Blur resembles thickening in this statistic.
Thickening can increase holes by closing an open shape; “fewer holes means
excess ink” is false even in this controlled example.

R1 reduces pixels before the same distance measurement. The16/body version lost
fine support on an-778 p10; the32/body iteration improves that case and many
others. Where height is already below32 pixels it does no reduction, so equality
is not a speedup. R2 uses one relative threshold and2*area/Crofton perimeter,
replacing the first boundary-pixel estimate. It measures an average ribbon width,
not the median of all distance ridges; those can legitimately differ.

The following absolute errors are in the explicitly declared height proxy. They
are fidelity to the native measurement, not readability/damage accuracy. Every
line, fragment and hole comparison is in `route-comparisons.json`.

| Page (suffix abbreviated here) | ROIs | R1 median / max | R2 median / max |
|---|---:|---:|---:|
| an-1436 p163 | 35 | .0124 / .0327 | .0124 / .0707 |
| an-1be6 p215 | 56 | 0 / 0 | .0143 / .0690 |
| an-1f8e p3 | 22 | .0071 / .1226 | .0129 / .1015 |
| an-778 p10 | 50 | 0 / 0 | .0161 / .1165 |
| an-d600 p58 | 8 | .0161 / .0268 | .0127 / .0377 |
| s2-09f5 p5 | 59 | .0161 / .0284 | .0149 / .0370 |
| s2-0ce9 p1 | 101 | .0274 / .0762 | .0421 / .1142 |
| s2-8686 p5 | 63 | .0127 / .0591 | .0132 / .0608 |
| an-ef4816 p150 | 41 | 0 / 0 | .0145 / .0456 |
| s2-200e p35 | 195 | .0139 / .0694 | .0111 / .1338 |
| s2-31f40 p1 | 124 | .0275 / .0302 | .0222 / .0853 |
| s2-77d1 p1 | 39 | .0074 / .0397 | .0047 / .0401 |

The largest an-1f8e R1 discrepancy is line11, a tiny fragment rather than a
representative body. On0ce9 line54, native paper/threshold noise introduces many
one-pixel ridges: width0.0488 becomes0.125 at reduced resolution. The raw/support
comparison shows why the native number is not automatically truth. On pale1be6,
stamp overlap contaminates a whole-line contrast estimate. C's contact-derived
height was borrowed offline for394 lines, but its later false-clear example
(3229 p4 source24,40.4px against nearby21–23px print) means even `uncertain=False`
does not certify font height.

Ready: callable measurement/rendering modules `ink_strokes.py` and `ink_edges.py`.
Not ready: automatic under/over-inking cause, unreadability labels or corrective
box deletion. No stroke census is charged invisibly to clean pages, and no line
is removed because it looks thin, thick, broken or faint.

## “We want to ignore images”, including ornaments, engravings and stamps

The first dense texture rendering lit up blank paper. Local paper/noise handling
and connected ink support improved it into an area-ink rendering. R1 computes the
same feature at fewer samples; R2 uses occupied rows/columns in coarse tiles.
Actual support masks are stored, not only rectangle IoU. Inspection on an-d600 p58
shows the engraving, initial/vignette and seal; it also includes real letters
beside the initial and last line under the stamp. Clean77d1 p1 exposes clusters
of ordinary words selected as area ink. R2 misses thin frames. **None is a safe
image exclusion mask.** No engraving caption is removed by it.

Ornaments have a narrower usable feature: a spatially recurring non-word unit.
The slow referee searches deskewed/contextual strips without the cheap runtime
nomination. It renders each matched tile and the ink it supports. R1 uses column
continuity and connected support to nominate this same spatial search; removal
requires sufficient repeated support plus a veto from unexplained glyph bodies.
All11 accepted crops show ornament strips. Examples include the bottom frame of
an-1436 p163, leaf headpiece of an-1f8e p3, and small repeated separators on
an-c153 p40/p56/p109/p180 and an-1ba3 p9/p12/p35.

R2 whole-strip autocorrelation was rendered on all93 full-search nominations.
It can nominate regular ornaments but fails the short1436 fragment (correlation
.038): its repeat extends outside the small box. Curved text and stamp overlap
also make a continuity scout wake expensively. The first32 agreement preflight
had a1,029ms B tail on an-778 p11 without any correction. This falsified the first
runtime gate despite unchanged controls.

The next cycle renders contextual spatial repetition at8/body before the16/body
search. Inspection of frame/headpiece and curved text panels showed that a weak
nomination—one-eighth supported ink spanning half the context—retains the frame
and leaf witnesses while rejecting many local text coincidences. It never
suppresses by itself; the original full witness and residual-glyph veto remain.
The all195 rerun is **item-for-item identical** to the initial72-removal study.
Raw failed lag images and both timing generations remain in the output. The tail
improves substantially but is not negligible on all agreement pages.

Stamp ellipses/concentric paths are explicitly drawn on the page. On d600 p58
the fitted ring reaches real front print. Ring shape neither owns the overlapping
letters nor proves the stamp's text should be deleted. The stopped stamp decisions
are preserved only as diagnostic hypotheses; there is no generic stamp correction.

Ready: the narrow `ink_motif_gate.inspect` candidate with witnessed repetition.
Experimental diagnostics only: `ink_images.render`, `ink_motifs.inspect`,
`ink_stamps.analyze`. General images, overlapping seals and watermark removal
remain open.

## Fresh timing against the owner's target

Single-thread CPU ONNX and OpenCV, warm detector session, batches of at most32,
sequential on the shared Mac. Two complete195-page repeats plus a third40-page
agreement pass give430 measurements. Every run freshly decodes, infers,
postprocesses, computes Q8 and B. Cached baseline/final items are read **after**
timing to assert equality. Every assertion passed. Decode, per-batch startup and
warmup are recorded separately; final detector-format `seconds` is the median
warm detector+postprocess+Q8+B time for that page. These are current shared-Mac
measurements, not an isolated-machine capacity guarantee. Whole-study source keys
also include offline helper files added during these runs; the runtime correction
modules remained fixed. Their individual final hashes are in `source-final/`.
A differing whole-study key is not by itself a different correction algorithm.

| Cohort / timed path | Samples | Median ms | p95 ms | Max ms |
|---|---:|---:|---:|---:|
| Agreement: Q8 only | 120 | 11.502 | 14.578 | 25.208 |
| Agreement: B including every dependency | 120 | 3.538 | 43.502 | 305.011 |
| Agreement: Q8+B | 120 | 15.620 | 57.182 | 310.307 |
| Agreement: full warm stack | 120 | 144.450 | 224.140 | 443.649 |
| All101 discrepancy: B | 202 | 10.200 | 243.120 | 589.232 |
| All101 discrepancy: Q8+B | 202 | 30.329 | 254.342 | 594.551 |
| All101 discrepancy: full warm stack | 202 | 169.688 | 386.920 | 727.174 |
| Thirteen B-changed pages: Q8+B | 26 | 211.042 | 452.849 | 534.797 |

Agreement B medians across repeats:3.266,3.788,3.971ms; maxima284.872,305.011,
294.759ms. The previous round's10.9ms median is a historical measurement; this
run measures Q8 again rather than subtracting timings from different sessions.
The worst discrepancy overhead is an-778 p7,554.629/594.551ms across repeats,
mostly an expensive negative ornament search. Actual refinement excluding scouts
has discrepancy median6.805ms/max584.995ms. Quoting total Q8+B above is the more
conservative target comparison.

No measured correction path exceeds1s. The median overhead is small; the strict
“negligible where no correction is needed” target remains unmet in the tails.
Agreement of detectors is not proof that these control pages have no errors.

Optional full feature censuses were separately repeated on12 pages (24 samples),
with existing boxes supplied and all feature computation fresh. They are not
part of the correction timing:

| Diagnostic, ms per page | Slow median / max | R1 median / max | R2 median / max |
|---|---:|---:|---:|
| Stroke condition census | 243.09 / 1206.45 | 233.05 / 940.80 | 30.93 / 132.86 |
| Connected area-ink support | 65.67 / 132.23 | 35.36 / 105.79 | 32.17 / 88.02 |
| Glyph ownership | 8.27 / 326.19 | 8.09 / 335.32 | 5.06 / 196.94 |

R1 is not automatically much faster when most ROIs already fit its budget.
No causal/readability claim is licensed by these speed numbers.

## Cooperation, validation and next work

C's `type_profiles` and `type_lattice` were copied/hashed for offline cooperation.
On0ce9 the measured strong-front pitch is67.0px, the main back groups67.21655 and
67.16699px, and lower back74.12708px. **The main two grids have the same pitch**;
pitch/body ratios differ because estimated body scales differ. This contradicts
a required different-pitch shortcut. Phase/skew help render layers; they do not
establish source ownership. C independently used B4 as a candidate-only veto and
retained its source receipt in `features_type/reuse.json`.

A relayed a continuous back-page rule on93f807 source32. B's glyph witness cannot
certify rule ownership. A has now added a whole-rule crossing/isolation veto that rejects93f807
(and conservatively d12a); neither darkness nor majority-grid membership is a substitute. B does
not merge A's new geometry changes. It retains the exact Q8 separators in this
branch (308 source-box clips across18 pages), with old geometry grey and new
geometry green in the final gallery.

Validation: **59/59 tests** (16 B mechanism checks plus43 existing fast-line
checks);195/195 unchanged decisions after the new motif gate;430/430 fresh
baseline/final equality checks;195 detector-format exports with finite polygons,
null baselines and measured seconds. Protected page code/tests unchanged. No
outputs are tracked in git. Source snapshots, hashes, raw timings and every
failure generation are retained outside git.

Next useful work is local ownership of overlapping strokes and robust component
scale before causal ink/readability labels; a contextual repetition scout that
avoids template enumeration on curved clean print; and explicit caption/initial/
stamp intersections before any generic image eraser. Broad masks and numerical
wins on this cohort are insufficient. No held-out generalisation claim is made.

## Round3 Git handoff (historical)

Staging was blocked by the sandbox at
`.git/worktrees/greek-ocr-toolkit-fl-falsepos/index.lock` (Operation not permitted).
At that handoff the branch remained `astra/ff-ink` at `b5199ad`. The requested fallback was
[commit-Fink.patch](../../../.astra/commit-Fink.patch) and
[commit-Fink-round3.sh](../../../.astra/commit-Fink-round3.sh), with file hashes and both required
trailers. No commit or push is claimed. The patch is validated forward in an
empty temporary repository and in reverse against this worktree. The coordinator
subsequently committed it as `3b9ffe3` and merged all three tracks. Round4 starts
from that committed state in the same owned worktree.

## Round4: recurrence and the clean-page tail

The tail was computation with no correction: on `an-778126cc8c2b-p000011`,
1,802 `matchTemplate` calls accounted for201ms of a305ms profiled B run.
Ownership took less than1ms. Stack independently measured the same negative
searches on source rows10–14 at roughly34–47ms each, before A/C processing.
The cause was repeated reduced-resolution template enumeration in curved prose
and stamp overlap. It was not a need for more mirror evidence.

The rendering iterations are retained under `round4/`:

1. `repeat-field-v1/`: native and8/body two-dimensional autocorrelation, with
   horizontal and vertical displacement shown as a field. Whole-context evidence
   dilutes a short frame and the leaf headpiece with adjacent decoration. A
   projection-only proxy responds strongly to stamp/prose texture.
2. `repeat-field-v2/`, `repeat-field-v3/`: local horizontal bands and their share
   of the actual target ink. All11 ornaments survive, but recurrent letter stems
   also nominate three expensive rows. A high overall repetition score does not
   establish that the repeating part owns the detector box.
3. `targeted-v1/`: using period-sized windows to place templates misses six
   reviewed ornaments. The1436 frame needs local fragments; the1f8e headpiece
   contains two neighboring periods. A period is not a sufficient template width.
4. `recurrence-v1/`: render normalized patch-pair agreement at each displacement,
   then chains of four copies with small positional tolerance. Box-filter means,
   variances and products replace enumerated template search. Border reflection
   fabricated some matches; v2 requires every patch to be observed inside the crop.
5. `recurrence-v3/` and final `recurrence-v4-*`: the review image now shows support
   for the **winning period**, not a union of unrelated periods. That earlier
   display overstated the evidence on prose. Final per-page images retain raw
   pixels and green supported regions. Native evidence covers18 strips: all11
   reviewed motifs and the seven costly p11 negatives. Both fast routes cover all
   93 full-search nominations from round3, with per-line JSON comparisons.

`shared/ink_recurrence.render(gray,item,height, samples=8, route=..., detail=...)`
is the reusable feature. Slow uses native pixels and all displacements. Route1
renders the same local chains at8 samples/body. Route2 tests only the five
strongest two-dimensional FFT peaks and adjacent sample offsets. A nomination
requires a four-copy chain covering at least a quarter of target ink over half
the contextual span. This is deliberately weaker than the old final ornament
support requirement. Neither recurrence route authorizes a deletion.

Native views show broad recurring support on1436's frame,1f8e's leaves andc99's
wide decorative units, while p11 prose has small recurrent fragments. Both fast
routes retain all11 reviewed ornaments; route2 rejects all seven costly p11
negatives. Differences on the other strips remain in `recurrence-comparisons.json`;
they were not reduced to one score. This is observed recall preservation on the
supplied material, not a proof for unseen motifs. Irregular or sparse ornaments
remain a miss: C's new `an-7792…p000107` candidate has separated flower units and
fails the default continuous-band scout. C retained it through another abstention.

The accepted runtime order is coarse connected-band scout → continuity check →
new recurrence nomination → old8/body spatial witness → unchanged16/body spatial
witness and residual-glyph veto. Full195 final-item equality was checked before
handoff; both fresh195 repeats also match. The61 ghost and11 ornament removals,
and all308 Q8 source-box clips, remain exactly the reviewed round3 corrections.

## Round4: faintness versus inkiness and readability

The previous whole-line stroke census cannot answer which letter is unreadable.
This round renders **1,364 localized physical component candidates on seven
pages**, selected from8,237 extracted components: pale1be6p215, mirrored0ce9p1,
stamp/curved778p11, ghost-contaminatedef4816p150, and clean77d1p1/p2/p3. These are
component candidates, not known characters; missing ink can prevent extraction
entirely. C's native atlas extractor is copied with its source hash in
`reuse_round4.json`; its physical-coordinate deduplication prevents an overlapping
box from supplying the same letter twice as supposedly independent evidence.

`shared/ink_observability.measure(gray,box,height,route=...,detail=...,version=4)`
renders local paper-relative depth and noise separately from width, components,
holes and fill at relative thresholds. It also asks whether topology survives
threshold changes of ±2 measured noise units. Every result retains
`readability='unknown'` and an unknown cause. Slow uses native pixels; route1
retains at most32 samples per component height; route2 uses12 and one principal
threshold. None runs in `ink_run`.

`observability-v1/` exposed silhouettes but used a flat paper level. V2 adds a
local illumination plane and the independent noise-topology sweep. The controlled
experiment then falsified the noise estimate: selecting bright **raw** pixels
truncated the distribution whose noise was being measured. Known2DN noise was
reported near1DN. V3 selects paper on smoothed pixels and measures original
differences; the controlled estimate is2.10DN. V4 refuses to call three empty
threshold masks a resolved stable component. All failed generations are retained.

In `observability-controls-v4/`, fixed cells and unchanged added noise separate
amplitude loss from shape change. Original SNR86.6 falls to13.6 at0.15 amplitude,
3.2 at0.03, and1.7 at0.01. Thinning, thickening and blur change different stroke
measurements. Most decisively, removing the lower arm of a known E yields a
perfectly plausible F at SNR86.1 with stable topology. An image-only quality
measure cannot infer that the arm once existed. Semantic readability requires
character alternatives and context; an apparent fragment can also be a legitimate
small character, diacritic or joined form.

Page inspection keeps that distinction concrete. Pale1be6's strokes remain
resolvable even when faint;0ce9 candidates contain reflected or overlapping
silhouettes despite cores above the local noise. On clean77d1, route2 changes
rho/lambda/counter topology. Native detail is evidence, not a reference label:
thresholding can open a visible blurred loop. Full component records and56
largest-disagreement crops are in `observability-review/`. Route1 changes the
noise-topology stable flag on36/1,364 candidates, route2 on222/1,364. These are
measurement disagreements, not error rates or unreadable-letter counts.

The repeated full diagnostic costs include C extraction and sampling afresh for
each route, then every component measurement. Median/max ms across seven pages:
slow462.109/2414.973 and469.250/2245.198; route1469.601/2245.179 and462.556/2325.050;
route2465.011/2121.466 and467.148/2137.285. Extraction dominates. The fast local
measurement is useful on already nominated components, but this full census is
not a cheap clean-page dependency. No new readability-based correction is enabled.

## Round4: generic pictures and stamps

`image-structure-v1/` renders original-pixel line-segment support longer than two
body proxies. Route1 repeats the rendering at16/body; route2 uses mixed gradient
orientations in3h tiles. This shows engraving hatching and frame ink on d600,
but also selects table rules:395 native segments in the engraving page versus299
on200ep35. V2 requires observed cross-edge contrast, reducing d600 to337 while
the table remains299. R1 retains195 and212 respectively. Generic long-edge density
is not image ownership. Route2 is worse: on778p11 it also paints ordinary words
and textured blank paper.

V3/v4 add explicit potential-text intersections with the old connected area-ink
rendering and C's deduplicated component locations. Green means observed component,
amber means an area-ink/component conflict, magenta means extended edge support.
On d600 this exposes letters inside the decorated initial, text touching that
initial, the caption, and front text crossing the stamp. No rectangle or whole
connected component becomes an exclusion. C supplied independent three-route
table conflict renderings for200ep35, copied and hashed under `round4/cooperation/`.
Their regional numeric support helps explain the conflict but is not a complete
table boundary; outside it is not thereby an image.

`shared/ink_stamp_field.render(gray,ring,height,route=...,version=4)` unrolls an
observed ellipse hypothesis into angle × radius. Native and reduced images make
the circular seal lines horizontal and front-text crossings curved. This exposed
a basic R3 failure: the fitted ellipse on09f5p5 is paper grain, not a stamp.
The200ep35 small ring hypothesis is also weak in original pixels. Ring fitting
and nearby edge support were insufficient evidence.

V1 radial mean darkness can be dominated by a dark front word. V2 angular
persistence at relative darkness still calls paper grain support. V4 therefore
requires a thin stroke darker than **both radial flanks**, above measured noise.
R1 renders that field at16/body; R2 uses24 angular spokes at8/body. Native false
09f5 peak support falls to0.294, R1 to0.221; d600's real outer ring has0.529/0.486.
But pale1be6's real ring is only0.418/0.307, and sparse spokes fluctuate. A fixed
ellipse does not follow warped or broken rings accurately enough, and even a
verified ring does not assign overlapping letters to the stamp. All ring peaks
and route failures remain visible. No threshold was promoted to a stamp eraser.

These are reusable diagnostic renderers (`ink_image_structure`, `ink_stamp_field`),
with no runtime dependency or new removal. Generic picture/initial/caption
ownership, irregular ornaments, stamp-only lettering and overlap separation
remain partial. The blue/green disagreement images still represent detector
coverage, not the color or ownership of the original ink.

## Round4 runtime measurements and cooperation

All390 fresh warm executions decode a page, rerun Paddle and postprocessing, then
Q8+B. Baseline and final lists are checked outside the timed interval. Decode and
model startup are recorded separately; every B/Q8 dependency is charged. Runs
were short foreground batches on the shared Mac, with order changes and no jobs
launched in the background. Variation between repeats is retained.

| Cohort / added computation, ms | Repeat1 median / p95 / max | Repeat2 median / p95 / max |
|---|---:|---:|
| 40 agreement, B | 2.982 /16.388 /24.502 | 3.107 /17.225 /24.649 |
| 40 agreement, Q8+B | 15.286 /27.133 /38.465 | 14.777 /27.051 /37.832 |
| 101 new discrepancy, B | 8.466 /140.546 /432.738 | 9.103 /143.762 /611.196 |
| 101 new discrepancy, Q8+B | 23.711 /147.559 /445.894 | 26.612 /154.101 /626.069 |
| 101 new discrepancy, Paddle+Q8+B | 164.169 /281.374 /586.883 | 175.604 /293.562 /778.988 |

The former p11 tail is14.126/14.098ms B in these runs; strictly negligible
agreement overhead is still not achieved on every page. Subsecond corrections
are measured on this cohort, not promised for held-out material. The largest
positive motif verifications remain costly; this change targets negative work.

`ink_run` now accepts optional `height` and `ownership_evidence`, and returns
per-line `motif_costs` plus `ownership_reused`. Supplied height must have
`shared.geometry.height_proxy` semantics for the **current** items; C's body
height is a different measurement. Reused ownership must be from the same pixels,
image size and exact bbox list. Size/rectangles/height are checked, pixel identity
is caller-owned, and an already paid ownership result is not charged twice.
Default calls still compute and charge everything themselves.

Stack snapshotted the five frozen runtime files and source hashes from
`round4/runtime-handoff.json`, placing B removal before A/C and preserving removed
regions as recovery exclusions. It independently reports390 exact combined
replays and all61+11 removals retained; its p11 combined correction cost is
26.301/33.770ms and B16.839/24.438ms. Those are stack's separate measurements,
not mixed into the table above. C also reused the motif veto for candidate regions
and the older reflected-glyph veto; front/unknown never certifies a recovery.

Current validation:72/72 prototype tests,195 exact reviewed outputs,390 fresh
baseline/final reproductions,195 finite detector exports with measured seconds,
and frozen runtime hashes checked. All changes stay in B-owned prototype files
and this report. Production pages/tests and other tracks' source are untouched.

Next work: trace a locally deformable closed ring with original-pixel support;
combine component ownership, table boundaries and decorated-initial continuation
before an image exclusion; use deduplicated repeated-shape alternatives plus
explicitly modeled degradation/context for ambiguous letter readings. Remaining
work must preserve raw uncertainty, including completely missing strokes and
unextracted letters. These diagnostic products should remain conditional on a
real need; their full census costs already falsify putting them on clean pages.

## Round4 Git handoff

The sandbox again rejects `git add` when it tries to create
`.git/worktrees/greek-ocr-toolkit-fl-falsepos/index.lock`. No new commit or push
was made; HEAD remains `3b9ffe3` on `astra/ff-ink`. The requested fallback is
[the round4 patch](../../../.astra/commit-Fink-round4.patch) and
[commit-Fink.sh](../../../.astra/commit-Fink.sh), with the required trailers.
Forward application against the committed base, applied-file hashes, reverse
application, the live reverse check and shell syntax are validated. The script
refuses a wrong branch/base, an already staged index or changed file hashes.
The former round3 script is preserved separately. Outputs remain outside git.
