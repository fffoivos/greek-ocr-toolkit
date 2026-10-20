# Round 5 — ink, faintness, seals and decoration

Working base: merged round4b `0ffe28d`, branch `astra/ff-ink`. The public
`prototypes.fast_lines.stack.Stack()` imports these changes directly. This
report describes **R5 B with the merged R4b A/C**, not the other tracks' still
independent R5 changes. No production `greekocr/pages/` files or tests changed.

The new corrections remove seal-rim lettering and several separated decoration
rows. They do not infer ownership from faintness alone. Missed back-page letters,
vertical frames, generic stains/images, and semantic letter unreadability remain
partial. The existing separator, geometry and recovery dependencies are included
in the final file-to-lines measurements below.

## Evidence, iterations and predictions

All forty owned comments are retained verbatim in
[COMMENTS.md](../../../.astra/fast_lines/out/round5/ink/COMMENTS.md), alongside their
numbered final images. All owner images were inspected, including the mixed
missing-row/watermark comments delegated to C. The ambiguous `7534p18: "6,7,"`
shows front rows; it does not authorize their removal. Five newly supplied curved
pages are included in the exports. Four owned comments (`466p242/p267`,
`7792p154`, `44b5p5`) have annotated review images but no raw input in the
195+5 allowlist. They were inspected, are marked unfixed/review-only, and are
not represented as raw-input experiments. The 44 held-out pages remain unseen.

Artifacts live under `.astra/fast_lines/out/round5/ink/`. Experiment destinations
are immutable generations; no identical experiment was rerun to seek a win.
The final timing protocol deliberately measures two fresh passes, forward and
reverse. Failed generations are retained. One early harness error overwrote the
first seal-generation files during v2; `seal-v1/README.md` records that loss.
No missing original rendering has been reconstructed and presented as observed.

### Seal lettering: observed curved strokes before ownership

Prediction: a thin closed stroke, traced in original pixels, can establish a
seal rim; compact weak lettering tangential to that rim can then be distinguished
from ordinary rows crossing it. Neither the ring interior nor its entire bounding
rectangle is thereby a forbidden region. There is no logo template or page-name
condition in the runtime.

`shared/ink_seal.py` first nominates local circle centres at eight samples per
body-height proxy. Hough voting is only a proposal. Around each proposal it
renders an angle-by-radius image, measuring darkness against both radial flanks
and the observed local noise. A path follows the observed stroke. The maximum
unsupported arc must be shorter than two body heights; fitted-ellipse residual
must be no wider than the measured stroke. These are physical length checks,
not a new percentage-of-page score.

The native renderer samples original pixels radially and angularly. R1 reduces
angular samples to twelve per height while retaining native radial samples. R2
uses 48 sparse spokes and independent radial maxima. The exported polar strips
show the pixels behind every path. Green is the outer observed path; cyan is an
inner diagnostic path; magenta boxes are nominations; red boxes are proposed
rim-letter removals. An inner path is not required for ownership and does not
own any interior text.

Iterations and failures:

* `ring-probe-v1`: contour ellipses fit partial leaves and displaced loops on
  `7792p107`, `1be6p215`, and `dbd045p249`. Such fitted geometry was insufficient.
* `ring-probe-v2`: gradient-centre proposals found real seals but produced over
  a hundred phantom circles and excessive work. Restricting proposals to the
  existing weak-ink scout and compact tilted boxes made the work local.
* `seal-v1/v2`: unconstrained paths followed letter loops; a second path sometimes
  collapsed onto the outer ring. Measured stroke-width residual and disjoint
  radial search exposed these failures. The inner path remains diagnostic.
* `seal-v3`: reduced radial sampling missed genuine rims on `1f8e7p3` and
  `466p323`. R1 v4 restores native radial samples.
* `seal-v4` and `seal-ownership-v5`: blank corners of the detector rectangle
  incorrectly rejected `dbd045p249`. Ownership now checks significant original
  ink **inside the actual polygon**, not padding corners.
* `seal-v6`: all 195 supplied pages have native/R1/R2 records. Native proposes
  21 rim removals; R1 proposes 20. Native-only `c153p56` remains retained. Sparse
  R2 misses the verified seals; it is not promoted as an eraser or a negative
  gate. Extending the legacy weak-ink return to short boxes adds negative work
  but no extra baseline-positive decision.

All twenty baseline R1 removal crops were viewed in
`seal-ownership-v5/review-00..02.jpg`. The actual composed path produces **21**:
Q8's valid reused height differs from an independent baseline height estimate on
`b9d6p255`, giving one additional rim nomination. Its fresh raw/before/after crop
was inspected and contains seal lettering, not a front word. This discrepancy is
reported rather than treating a detector-only study as the final result.

A cheap exact rejection bounds the later path: if even the union of all possible
radial stroke samples leaves an unsupported arc of two heights, no admissible
path can pass. All 195 R1 decisions remain identical in `speed-v2/v3/v4` checks.
The runtime never excludes a ring, disk or annulus. Only the accepted original
line polygon becomes a permanent recovery exclusion.

Limits: pale `1be6p215` has two rim boxes removed but retains its uncertain central
seal lettering. `00f143p192`, `466p242/p267`, `c153p40`, and `d6fdp47` still have
marked watermark boxes. The legacy weak-layer nomination can miss them, and
rings may be occluded or warped. Raising a darkness threshold would not establish
which overlapping ink belongs to the seal. Generic stamps are not solved.

### Decoration: disconnected components, then full spatial support

Prediction: flower borders that failed the connected-band scout can be nominated
by repeated **separate physical components**. Native contours render concavities
relative to measured stroke width, retain component locations, and compare shapes
with bidirectional distance to their actual ink. Matched copies are green;
unexplained components are red. Components are not declared letters or flowers
by their scalar statistics.

`discrete-v1/v2/v3` exposed OpenCV5 defect-array shape, self-intersecting contour,
and JSON boolean errors; these failed experiments were not counted as successful
renderings. `discrete-v4` required every copy to retain deep concavities and missed
filled flowers. V5/v6 use a lobed native seed and allow matching over-inked siblings,
then unite supported groups. Native paths still do not independently own text.

`motifs-v7` falsified the standalone decision: **four true right quotation marks
on `8686p7`, source52, satisfy the repeated-lobed-chain test**. The raw crop was
viewed. No vertical discrete-chain deletion is promoted. Three native-positive
vertical flower fragments on `7792p107`, and one on `7792p104`, therefore remain.

For horizontal candidates, native component evidence nominates the existing full
spatial motif verifier at sixteen samples per height. This retains the existing
residual-glyph safeguard and its existing thresholds; no acceptance percentage
was retuned. The all-cohort comparison (`motifs-v8`) checks all 25 horizontal
native groups: native and R1 agree on the five positive borders and all twenty
negative rows. The positives are `1ba3p12` top border, `7792p59` bottom flowers,
and `fd4p28/p31/p35` flower rows. Purely reduced component topology misses some
native seeds, so R1 keeps the cheap native contour step inside the nominated ROI.
R2's eight-sample component/shape shortcut misses the useful flowers and is not
promoted.

`adjacent-frieze-v2` tests a separate proposal: a same-extent neighbour of an
already verified ornament. Six candidates include the owner-marked upper ivy
strip on `c99p25`. Native and R1 still reject it; R2 alone accepts it. Inspection
shows a genuine ivy strip with tall arches that the existing template sizes do
not fully render. The proposal is retained as a failed diagnostic and does not
become a runtime dependency. The earlier `flower-verifier-v1` tested source24,
which was the **already removed lower** strip; it was not a new correction for
owner line11. That source-index mistake was caught in the composed comparison.

The first composed trial spent too much time measuring ordinary-row contours.
Vectorized equal-spacing checks, lazy contour work with exact depth upper bounds,
and batched shape distances preserve every measured native group across 195
pages, but the census remained costly. `layout-scout-v1` explicitly renders outer
rows or gaps of one body height on both sides. It reduces component nominations
from **1,187 to 92**, preserving all five reviewed positives. Text at page edges
still nominates work; layout never authorizes removal. Inline ornaments can be
missed. Runtime uses this cheap layout check before pixels, then the component
scout, native topology, and full spatial verification. The original continuous
motif route is unchanged.

The heavily damaged top/side flowers on `7792p59/p104/p107/p154` remain incomplete.
Repetition alone is not a generic image classifier; engraving hatching, repeated
letters, table dots and quotation marks remain explicit counterexamples.

### Faintness, inkiness, stains and blobs

The existing darkness-vs-own-print and reflected-glyph witness remains in place.
`weak_indices` exposes the same legacy tone/core nomination even for short boxes;
it is not a back-page label and never licenses recovery as front text. Existing
mirror suppression logic is unchanged.

`back-witness-v1` compares dense/native component enumeration, current R1, and
sampled R2 on eight available owned ghost pages plus the pale-front control. It renders every
weak candidate with front/back vote counts: red supported back, green ordinary
shape hypothesis, amber unknown. Dense enumeration produces no additional
supported removals over current R1. The smaller R2 atlas changes some `0ce9`
choices; it is not interchangeable with R1. More enumeration alone does not fix
these errors.

Inspection explains different failures: `8686p26` has dark ghost strokes that
mostly escape the legacy weak-tone scout, and its nominated row has insufficient
asymmetric evidence; `ef481p150` candidates have only zero to two useful reflected
votes. The bottom of `8314p42` contains a second numeric layer, but many digits
are symmetric or provide too few independent asymmetric shapes per short box.
`8314p39`, `3352p160`, `44b5p5`, and the residual `0ce9` boxes remain unresolved.
A second pitch/phase is not ownership, as A's earlier same-pitch counterexample
already established. The sideways `6419p1` remains parked. No vote threshold was
lowered to fit these pages.

`round5_marks.py` renders 36 regions/components across the owner blob `922ep1`,
stain `ffcccp152`, pale `1be6p215`, and weak `ef481p150`: native pixels, R1 at up
to32 samples per height, R2 at12 with one principal threshold. Each sheet shows
raw pixels, threshold silhouettes, noise-relative contrast, distance-ridge width
and counters. The owner region is explicitly labelled **not a character**;
nearby components are controls, not transcribed reference letters.

The blob is dark, broad filled ink (native contrast0.923, SNR217.3); the stain is
weaker but still well above measured pixel noise (contrast0.328, SNR74.3). Neither
is simply invisible ink. On the blob, internal texture makes median width vary
from1.06h to0.09h to0.27h across thresholds; on the stain it varies0.85h/0.58h/0.12h
and creates counters. R1 changes fine holes; R2 loses genuine letter counters
(e.g. the nearby delta on922e). High SNR on quantized/compressed backgrounds does
not prove readability. Blank noise, loss of a stroke, deliberate punctuation,
and typographic fill cannot be assigned a cause from one scalar measurement.

These diagnostic distinctions are reusable. They do not yet provide safe generic
blob/stain deletion or semantic unreadability labels. The owner-marked two boxes
remain unchanged. Existing R4 counterexamples—including a damaged E becoming a
plausible F with stable topology—still apply. No full-page readability census is
charged to the clean path.

## Composition, timing and validation

Two fresh forward/reverse passes run the frozen image-file entry point, including
image decoding, detector, one Q8 pass, B ownership and motif dependencies, A
geometry/joins and C recovery. Model startup is recorded separately; explicit
untimed warmup is declared. Rendering/JSON writing are outside latency. The raw
receipts and [summary](../../../.astra/fast_lines/out/round5/ink/final/summary.json)
retain every page and stage. “Agreement” is the original 40-page group label;
the owner found actual watermark errors on some of these pages.

Milliseconds, first / second pass:

| Group and metric | Median | p95 | Maximum |
|---|---:|---:|---:|
| Agreement40, new B work |0.971 /0.838|17.029 /21.028|19.304 /33.614|
| Agreement40, entire B |4.558 /4.914|35.621 /42.334|39.856 /57.866|
| Agreement40, entire correction stack |20.019 /22.497|46.997 /55.866|58.219 /79.345|
| Discrepancy101, new B work |1.990 /2.329|99.457 /137.286|229.305 /261.867|
| Discrepancy101, entire B |11.567 /12.672|231.830 /260.211|406.714 /491.993|
| Discrepancy101, entire correction stack |56.613 /63.549|424.242 /522.562|999.713 /1156.024|
| All200, entire correction stack |39.239 /46.487|385.816 /493.202|999.713 /1156.024|

New B work is the charged sum of seal work, layout/component nomination and new
spatial verification, **not** subtraction from an old timing run. Existing
ownership/height costs remain in entire-B and full-stack values. The former
305ms clean-page tail `778p11` now costs15.853/16.762ms in B; the R4 recurrence
fix remains effective. A new negative seal search on `778p17` costs most of the
229.305/261.867ms new-work maximum; the early radial bound does not eliminate all
false proposals. Positive existing ivy verification still dominates B on `c99p25`.

The strict target is **not met throughout**. New work is below1ms at the agreement
median, but seal corrections and remaining negative work have a measurable tail.
One second-pass full-stack discrepancy result exceeds1s: `4959p4`,1156.024ms.
Its stages include690.989ms inherited fragment work,348.804ms inherited type work,
and26.853ms B. The first pass is999.713ms, leaving no useful timing margin.
All B stages themselves remain below0.5s. These are measured local results on a
shared Mac, not a held-out or deployment performance guarantee.

Validation: **149/149 prototype tests pass**; both fresh200-page passes reproduce
the reviewed pilot polygons exactly.44,670 checks validate finite detector-format
exports, bounds,400 source-bound receipts, original removals, recovery exclusions,
and gallery/comment links. All61 back removals and11 old ornaments survive;
21seal-rim and5additional ornament polygons are removed. Known195 totals are
308Q8 cuts,92curved cuts,30geometry envelopes,15joins(reduction16),18C additions,
61back removals,16ornament removals and21seal removals. No old text polygon was
removed by a new B acceptance in any inspected crop. This is observed review,
not proof for unseen pages.

There are200 detector JSONs and200 numbered final images in the
[gallery](../../../.astra/fast_lines/out/round5/ink/final/index.html). All30
raw/before/after crops on23changed known pages were inspected; final outputs are
exactly identical to that inspected pilot. The five new curved-page final images
were also viewed. They retain the inherited A/C limitations; B adds no removal
on those five pages. No regressions were visible in the26new removal crops.
Failed experimental quote suppression and imperfect stroke/seal hypotheses were
kept out of runtime, not counted as successful fixes.

The permanent removal ledger now distinguishes `back print`, `ornament` and
`seal rim`; Stack counts seals separately. Geometry and C receive exactly the
accepted original polygons. Removing flower rows also changes the existing A
first-row envelope on `fd4p28/p31`; both fresh raw/before/after crops were inspected
and retain visible front text. These are reported downstream changes, not new B
geometry ownership. Every other changed crop is a removal.

## Cooperation and next work

A owns all column/gutter and smooth-band changes; its native contacts do not
certify ink ownership. C owns missing real rows in mixed comments. The B
`weak_indices` API was relayed so C can abstain on unresolved weak recovery
hypotheses; C must not treat `front` or `unknown` as certification. C reported
its local component-height misuse of the motif verifier and corrected it to the
documented page/body proxy. Candidate-only full spatial verification is allowed
behind its independent recovery nomination, with cost charged there.

C's real last-row proposal on `1ba3p35` overlaps an existing border footprint.
No validated ink-specific replacement exists yet; the permanent polygon veto
remains. This costs recall but avoids silently recovering rejected ornament ink.
No other track's folder or live runtime implementation was copied or edited.

Next: render an ink-specific border exclusion with source ancestry before
relaxing that overlap veto; full-height/full-period ivy witnesses rather than
partial templates; separate mirrored numeric-layer evidence across independent
cells without inferring ownership from grid pitch; overlapping seal/front
component alternatives; and character/context alternatives for unreadability.
All require another explicit rendering and counterexample study before runtime
suppression. The broad owner goals remain PARTIAL.

## Git handoff

Git staging is blocked by the sandbox on
`.git/worktrees/greek-ocr-toolkit-fl-falsepos/index.lock` (`Operation not permitted`).
No commit or push was made. The requested fallback is
`.astra/commit-Fink-r5.patch` with executable `.astra/commit-Fink-r5.sh` and a
validation receipt. It contains exactly12 code/document files; generated outputs
remain outside git. The script verifies branch/base, an empty staged index and
all12 source hashes, then stages only those files and uses the required trailers.
Forward application to an isolated base copy, reverse application checks against
the finished worktree, and all resulting file hashes are validated.
