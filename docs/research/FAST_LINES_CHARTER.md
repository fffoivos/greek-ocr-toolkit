# Fast line finding: project charter

Status: draft agreed in conversation with the owner, 10 Oct 2026. Not yet sent to any agent.
All work under this charter stays as **prototypes and open projects**, separate from the `greekocr/pages` API.

## 1. Starting point: two detectors that fail differently

| | Small detector (PaddleOCR PP-OCRv6 small, 0.07 s/page via ONNX, Apache 2.0) | Our detector (`greekocr/pages`, ~5 s/page) |
|---|---|---|
| Stronger at | tables; general reliability; keeps the first letters of lines | faint letters; curved pages |
| Weaker at | faint letters; curved pages (on warped pages a box straddles two lines, e.g. s2-3229) | tables ("basically unreliable"); misses early letters of some lines on some pages; takes slices of table rules for lines |
| Seen in tests | missed ~100 lines ours found on the 53 upright dev pages; boxes some ornaments, initials, stamps | took tall slivers of table rules for lines (prototype comparison) |

Each one's weaknesses are roughly the other's strengths. Speed is folded into the problem from the start, not a later
phase. The question is how far our initial ideas can carry a combination that has the strengths of both at close to
the small detector's speed.

## 2. Features of the page (not of any algorithm)

These are properties of printed pages. No algorithm gets them perfectly, ours included. The owner's list:

- **Faintness and inkiness**, to ignore back-page letters, or to know which letters are unreadable. Two different
  properties:
  - **faintness**: mostly back-page letters showing through (also watermarks);
  - **inkiness**: the condition of a letter's strokes, under-inked (broken, thin) or over-inked (thick, filled).
  Either can make a letter unreadable. Today's statistics separate the two only weakly: "broken/faint" still feeds "under-inked"
  (`docs/reviews/PAGE_LINES_Q2_STATISTICS.md`; the report calls under-inking "an intensity proxy").
- **Tables**: recognise them and let the small detector handle them.
- **Images**: ignore them.
- **Curvature from book binding**: recognise it to correct the geometry of the line segments. A very important
  contribution to line segmentation in general if it can be done efficiently, but no less important than not matching
  back-page words or images.
- **Skew**: recognise it to fix the geometry, for the same reason.
- **Separation**: lines at the same height but in a different column or page stay separate.
- **Font properties**: typeface, size, letter spacing and so on, relative to the page and the book.
- **Font geometry**: how many lines are required to express the font's geometry, and whether the script has accents,
  and so on, without necessarily using them.

## 3. Our model as a skeleton

Our detector is a deterministic model, but the way we developed it was stochastic: review round after review round,
case by case, fixes driven by whatever pages and failures came up. We kept all of these features in mind while
developing it, but did not pursue them all with the same fervour:
- **worked out in depth:** line geometry, guide lines, letter height, darkness against the page's own print, gutters,
  ink classes;
- **pursued less:** tables (handed to Docling), letter spacing, how many guide lines a script needs, the split
  between faintness and under-inking.

Because it is explicit, it can render what it does know (each line's guides, letter height, darkness, column, and
whether a value was measured or borrowed from a neighbour). That makes it a skeleton for the new work: concepts and
reference measurements to reason with. Its depth is uneven, its thresholds were tuned on the 54 development pages,
and in places it takes shortcuts of its own. So it is neither ground truth nor a design to copy, and at 5 s/page it is
not part of the fast pipeline.

## 4. The job: correct the small detector's errors

1. **Geometry**: boxes that do not skew properly, or stay rectangular where the line curves.
2. **False negatives**: missed lines.
3. **False positives**: watermarks, faint back-page letters and the like boxed as text.

**Cost follows need.** The work must be efficient, and better still, it must not run at a constant cost when it is
not required. When a page needs no corrections, the time should drop as close as possible to the small detector's own
time. Extra work is spent only where something needs correcting. How that is achieved is open: efficient checking
heuristics, our algorithm taking over where a check fires, or something else.

**The shape of a good result** (owner): for pages where the small detector has no errors, negligible overhead; for
pages where it needs fixes, corrections in under 1 second.

**Test pages beyond the 54** (owner): measure many more pages where our model and the small detector disagree
seriously. A 496-page run of both detectors (10 Oct) picks those pages, plus agreement pages for measuring overhead,
before the prototype phase.

**Both detectors may be wrong** (owner): a disagreement only says which detector covered more of the page; on some
pages both are wrong. The disagreement pages are a testing ground for the prototypes, judged by looking at the page.

**Segment shapes** (owner, 10 Oct, after reviewing round 4): segments should change shape to fit their line and be
smooth, because many contain parts of other lines. The less a segment holds of other lines, the better. This is a
goal for the shape of every segment, not only for boxes that are visibly wrong.

**The three issues after the round-5 review** (owner, 11 Oct):
1. **Faintness, including watermarks**: a relative faintness analysis, judged against the page's own print. A faint
   line is discounted; a line that merely has something faint about it is not. Watermarks belong here: they are made
   not to interfere with the text.
2. **Curvature at the end of pages, as a page-level geometry**: a heuristic that looks at the page edge. Where the
   page curves, many parallel lines curve together as they pass through the curved part, but they stay roughly
   parallel. That shared geometry lets us compute the segments for the whole page at once instead of line by line,
   and shows how many parallel lines a curvature would change. It is also a warning that the small detector has
   probably missed lines there.
3. **Segments that contain more than one line vertically** (two rows stacked in one segment). This is judged per
   segment, not per page, and has barely been reviewed.

## 5. Method

**Level 1, the same spirit as before.** Iterate component by component, each capturing one real feature of the page
that we have already modelled.

**Level 2, a different way of building it.** Start from the small detector, not from scratch, and add heuristics. Each
heuristic rests on our understanding of what can be on a page and answers to an explicit rendering of its feature:
- first a **slow, explicit rendering** of the feature drawn on the page, from our current algorithm where it models the
  feature well, or from a new slow tool built for that feature. The owner or Astra checks it **visually**;
- then the **fast heuristic is checked against that rendering**, page by page and line by line.

Example: a slow per-line curvature rendering is checked by eye; the fast "bend from Paddle's map" heuristic is then
checked against it.

**Not done:** statistical tools that win on our test pages in the hope they generalise. A heuristic is accepted only
if it rests on a feature we can make explicit on the page, and its agreement with that rendering is shown visually.

**Two routes, for every feature:**
- **Route 1: render the feature differently, so the rendering itself is fast.** Much of today's 5 s is *searching*
  for lines (line finding 1.66 s, pixel preparation 1.04 s; `docs/reviews/PAGE_LINES_Q4_SPEED.md`). With the small
  detector's localisation some renderings may already be cheap (the guide fit costs ~0.3 s/page today). Rendering at a
  different level may be both explicit and fast, e.g. page-level models: one bend model per curled page, one skew
  angle, one font per book. If a route-1 rendering is fast enough, it is the product.
- **Route 2: a fast, innovative heuristic standing in for the rendering**, where the explicit rendering stays
  expensive (mainly per-character features: faintness, inkiness), e.g. one measurement per line checked against the
  per-character rendering.
- Both questions are asked side by side for every feature.

## 6. Ideas already on the table

The owner's earlier ideas: just ideas, which may or may not work out. The research considers them alongside its own:
1. **The small detector as a starting point** (under 0.1 s), plus some extra work to find missed lines.
2. **Lightweight heuristics that decide when our algorithm takes over** the process (one way to make cost follow need,
   see section 4): for example when a page curves at
   the side, or when there are too many faint letters from the back page. The owner: one of these two approaches
   "must balance speed with accuracy much better than our current approach".
3. **Check the box edges for curvature**: the 1/5 or 1/3 of a line closest to the page edge, and whether something
   can then be done to improve the line.
4. **Compute the mean line of each box and check, cheaply, whether it actually tracks the text**, and whether there is
   curvature at the end of the page.
## 7. Material already available

- **Local comparison app:** `http://127.0.0.1:8790/`, all ten detectors on the 54 pages, plus `stages.html` with the
  Paddle-first stages (map, boxes, weak areas, uncovered ink, curvature, ours vs Paddle). The files live in the
  session scratchpad (`…/scratchpad/detector_app/`).
- **For agents** (`~/Projects/greek-ocr-toolkit-astra-lines4/.astra/fast_lines/`): the ONNX models (v6 small, v5
  mobile, v6 medium), all nine detectors' outputs, our line outputs for the 54 pages, the stage prototype
  (`prototype/build_stages.py`, `summary.json`).
- **What the small detector provides** (checked on our pages): a text-likelihood map at the network's input size
  (960 px on the long side by default, about 4×4 page pixels per cell on a 2,181 × 3,773 page), one tilted rectangle
  per line, and a score per line. No baselines, letter-height lines, character boxes or darkness. Its inner layers are
  learned features with no readable meaning.
- **Environment:** `onnxruntime` 1.31.0 installed in the repo venv on 10 Oct.
- **First prototype findings** (stages page, 53 upright pages):
  - uncovered ink flagged 84 of the 102 lines ours found and Paddle missed;
  - weak map areas flagged 40, all also flagged by uncovered ink;
  - about 17 flags per page, mostly grey ink (show-through, speckle);
  - curvature flags were near zero on straight pages; s2-3229 got 11, where Paddle's boxes straddle two lines;
  - Paddle 0.056 s/page, all checks 0.31 s/page in unoptimised Python.

## 8. The owner's words (verbatim, 10 Oct)

> we cant deploy a 5 second per page pipeline

> (1) can we build a much faster version of our algo if we use small detector as a starting point (less than 0.1s) and
> then try to do some extra to figure out missed lines? (2) can we use some lightweight heuristics to check if a page
> curves at the side, or if there are too many faint letters from the back page so we can take over the process? There
> must be some easy heuristics for this. One of the two approaches must balance speed with accuracy much better than
> our current approach

> (1) what can we get from the model internals and outputs, that we can use in terms of our model, so that we dont do
> duplicate work? that is for: -character intentensity and ink-ness? -lines detection? / or alternatively, what can we
> do by just checking the boxes + their edges (e.g. the 1/5 or 1/3 of the line closest to the page edge) to understand
> if their is curvature and their is something we can do to improve it? -other internal features our algo needs?

> the other is simply search heuristics that might be required to apply; i.e. dont apply our algo fully; figure out
> much simpler way to take what small detector gives us and for example compute hte mean line you got, and then then
> compute in a lightweight way if there is curvature at the end of the page or if the line actually tracks the text.

> Leave them all as prototypes and open projects.

> Our is better on faint letters and curved pages you are right, and much weaker in tables (basically unreliable) and
> also slightly less reliable in terms of general use (for unclear reasons we miss some early chars of some lines in
> some pages). Maybe we could build a hybrid that is strong in everything?

> because eg running on only the detected boxes might not guarantee finding missed lines — that is it might help with
> false positives but not false negatives -- we might need another heuristic for those

> I am also having a feeling that our previous framing of speeding up but retaining exactly the same output was wrong
> for optimization; because there might other classes of algorithms very near our current own, that could be found by
> radically or somewhat different approaches, that are way faster but basically ahve the same results.

> Ideas don't come from adding some retarded percentage gates. Ideas come from divine insight about hte working of
> nature, and relentlessly pursuing the image of your dreams until it becomes reality. Simply put in the language of
> prompt: you have to research the different approaches that are possible in this case, and then explore them

> I feel like we should set right what the small detector is meant to do, and what are the possible fail cases we might
> find in advance -- we are inherently folding speed up into this -- and the question is how far our initial ideas
> might go. So we don't want the model to get stuck in our previous algo but instead use our discoveries as anchors and
> theoretical tools of analysis of what it might do; and then find heuristics and shortcuts that might get us there
> much faster.

> These are we could say features [...] we should be keeping in mind, not to replicate them exactly anymore because we
> have already done that to a good degree, but to keep them in mind as we build our heuristics that respect these, but
> are much faster computationally and more practical.

> Are features not facts of the algo, no algo gets them perfectly. So we should clearly distinguish faintness (mostly
> back page letters) from inkness - that is the lines of the char or over or under inked.

> Now we want to use these as a skeleton [...] To be able to correct the small detector erros: -these are boxes that
> might not skew properly, or that are always rectangual when they should be curving -also missed lines (false
> negatives) -matched watermarks, or faint letters from the back page and so on (false positives)

> I meant the method of developing it as a model is stochastic, not that it is a probabilistic model. And these are
> features we kept in mind while developing it we didnt persue modelling all of them with the same fervor

> well, "take over the process" idea is one way to do it; the important thing is that what we do is efficient, and it
> would be even better if it doesnt run constant time even when not required. So the spirit here is more like "drop to
> as close to small detector time when no corrections are required"; these could be by efficient checking heuristics
> ro soemting else.

> Right although another thing I forgot about is that we might want to measure way more pages were there is a
> serious discrepancy between our model and small detector. So maybe you need to run 500 pages or whatever and pick
> the difference before you continue to prototype phase. Also for example a good result we could see is something
> like: for pages where small detector has no errors we add negligable overhead, and for pages where it needs fixes
> we have sub 1 second corrections.

> Well we should always keep in mind that both models might be wrong but this is a good testing ground for the
> prototypes

> We want the research project to be in the same spirit: we iterate on some components while trying to capture some
> aspect of real features on the page we have already modelled. But we want to do it with a different implementation
> method; a quicker starting point: the small detector; and using heuristics but heuristics that are measured against
> features that can be explicitly rendered on teh page with a slow-modelling method first. Our current algo to teh
> extent that it models these features, or another tool you can develop and I our astra will verify visually, but then
> a heuristic will be verified against explcit rendering.

> We don't want to just build statistical tools that win on our test set and we hope they will generalize. We want to
> build heuristics that are based on features that we can make explicit with a model on the page, and are built on
> our understanding of what things might be on a page.

> can we take a different approach to rendering (which this might be fast and accurate already), or find a heuristic
> for the renderings that might be fast and innovative?

> We should also be thinking about changing segment spaces and making them smooth, because many contain parts of other
> lines in, the less this is the case the better

> apparently small detector misses a lot when curvature is there, which is interesting

> what is clear is also that the faintness analysis is not good / is relative faintness used to discount faint lines
> (without discounting lines that have something faint about them)?

> the major 3 issues that we need to think about are: (1) fiantness; this probably needs a relative faintness analysis
> to work out (2) a heuristic for detecting curvature at the end of pages, and deciding on a way this might help to
> reorganize all segments efficiently i.e. consider how many parallel lines would change if this curvature would be
> applied (3) some segments contain more than one line and we need to fix that!

> you misunderstood (3), I am talking about vertically contained now not horizontally. this is something we havent
> talked much about and I havent reviewed much because it's per segment not per page

> I think watermarks should be part of faintness because generally watermarks are made to not interfere with teh text

> also yes, if we solve the curvature heuristic, this should serve as a warning that probably lines are missed by small
> detector as well. But I want to emphasize the model we need to think, curvature implies that a many parallel lines
> would curve as they go through the curved page, but they would roughly stay parallel. This is a geometry that would
> help as calculate segments for the hwole page instead fo trying to figure it for eveyr line.

## Organiser notes (not sent to agents)

How the playground around the agents is run. This is the coordinator's design, not part of any agent's brief.

The owner's ideal: 
> my ideal would be running astra agents in parallel and have them both compete and cooperate on the different
> approaches found by the research agent. The economical approach would be to rank the approaches and do the topmost
> one first and see how it goes. but neither really satsfy me


### Plan: a tournament that narrows down (the owner: "a good shape")

1. **Research (one Astra run):** for each feature, whether a slow explicit rendering exists or must be built; route-1
   possibilities; route-2 heuristics that follow from understanding the page; how each will be checked against its
   rendering; the failure cases to expect in advance. Read the Codex meter before and after to learn the cost of one
   run.
2. **Round 1: cheap sketches of every approach in parallel**, split between Astra at lower effort and Claude Opus agents
   (separate budget). A shared board (findings, failures, reusable parts) that every later run reads first.
3. **Round 2: the best two or three get deep Astra xhigh runs.** They compete on the same pages and may borrow working
   parts from each other and from round-1 losers.
4. **The owner or Astra verifies each round visually** in the local app. No percentage gates decide what goes
   forward.

Budget at the time of writing: Codex weekly usage 9% (probe 10 Oct 14:11 Athens), resets Sat 17 Oct 07:24. The
owner's dashboard number wins over the probe.

