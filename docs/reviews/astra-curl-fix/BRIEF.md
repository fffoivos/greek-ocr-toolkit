# Task: make the line tools follow curled line starts (implementer brief)

You are the IMPLEMENTER on this task (not a reviewer). Repository: this git worktree, branch `astra/curl-fix`
(created from `main` at 81641ea). Edit code here, run the tests here, commit on this branch. Do not push. Do not start
background jobs. Python: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, run from
the worktree root (the package `greekocr` is imported from the current directory), with
`PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider` for pytest.

## The owner's algorithm (read first)

`docs/PAGE_LINES_ALGORITHM.md` — the owner's seven-step page-lines algorithm and four-step procedure. The relevant
points for this task: lines on a page share their skew and curvature; every line's curve is followed letter by letter
(step 3); four font lines follow each line's curve (steps 4–5). Keep the solution simple: the owner explicitly asked
for simple, literal methods and fast visual verification, not layers of extra machinery.

## The problem (owner review of page s2-49598b2e848ab1f0ee1e-p00001, 8 Oct)

Crops: `tests/fixtures/page_s2-49598b2e848ab1f0ee1e-p00001/crops/<line_id>.png` (every text-layer segment of one 1850s
Hellenic Parliament page; `index.json` has the boxes). The crop-level tools are `greekocr/glyphs/components.py`
(`line_glyphs`: binarisation, components, band fit — RANSAC → grow → `_track` → model selection → `_smooth_curve`) and
`greekocr/glyphs/columns.py` (`column_segments`, which calls `line_glyphs`). The underline the owner reviews is the
band bottom (`LineGlyphs.band.bottom`, the fitted baseline) of each column segment's main line.

The owner's notes (verbatim) on the left column, where the page curls at the binding so line starts rise steeply
toward the left margin:
- l00017: "undetected curved word to the left (capitalized), and also the line below it"
- l00018: "lines from right column are extending to the left too far / curved text at the left is not connecting with its own line"
- l00021: "curved text at the left is not connecting with its own line / and left column text has wrong lines"
- l00023, l00025, l00029, l00030: "not detected curving upward left text"
- l00032: "the curvature of the text is not detected"
- l00035: "not detected curving upward left text, and disconnect in the left line (column break is faint)"

Scope of THIS task: the curled starts (l00017, l00018, l00021, l00023, l00025, l00029, l00030, l00032, l00035). The
column-split notes (l00037, l00038 "disconnect in the left column") and capitals (l00027) are out of scope unless your
fix resolves them for free.

## Diagnosis so far (verify it yourself)

On l00029 (plain box crop, 2952×78, x-height 23 px) the curled letters ARE detected and ARE in the baseline evidence
(`bx`, `by` in `line_glyphs`): letter bottoms x 222 → y 33, 195 → 31, 144 → 21, 123 → 18, 100 → 14 (rising toward the
margin, about 1 px per 5 px), while the flat part of the line sits near y 38–41. The fitted baseline stays straight at
y 39–40 over x 100–300.

The step that fails is `_track`: it predicts each next point from a straight line through the k = 6 nearest accepted
points — mostly on the flat part — with tolerance 0.25 × x-height + 1 ≈ 7 px. At x 144 it predicts ≈ 38 against an
actual 21, rejects, and stops after a 3 x-height gap. Two smaller quirks: a point between accepted points (x 222) is
never a candidate (only points beyond the outermost accepted ones are), and one component contributed both its bottom
(31) and a top-based estimate (top + x-height = 39) and the wrong one was accepted. Even when tracking does add curl
points, the curve-vs-line model selection (90th-percentile residuals, `SEL_RATIO`) can still pick the straight line
because a curl is a small share of the points.

Already committed on main: the gap test measured from the line's end; 1–2 stray accepted points at the ends set aside
before tracking; a curve is also taken when the straight line leaves ≥ 3 tracked points out of tolerance and the
curve fits ≥ 97 %; `line_glyphs(focus=(row0, row1))` (first fit only on evidence inside those rows). Result: l00023 is
followed; the others not.

Tried and REVERTED (do not repeat without a new idea): (a) a column-shared curl shape (straight + depth × the
column's median bend): the shape is noisy at the far left and produced jagged lines that dipped into the line below —
`.astra/curl_shape2.png`; (b) a quadratic prediction through the 8 nearest accepted points: no effect, 2 regressions;
(c) predicting from the last ≤ 3 accepted points at the line's end (`.astra/end_prediction_attempt.patch`): followed
l00017 but bent l00035 the wrong way (latched onto the line below) and broke 2 regression lines — `.astra/curl_end.png`.
Lesson: greedy letter-by-letter rules are fragile — one wrong early acceptance derails the rest.

A suggestion, not a requirement: replace greedy tracking with a global choice — among the letter-bottom evidence
near the line, pick the smooth path (bounded slope and slope change) that passes through the most points (e.g. a
dynamic programme over evidence sorted by x, or a robust smooth fit with an explicit bending penalty), starting from
the RANSAC core. You may choose any simple method that meets the acceptance criteria.

## Acceptance criteria

1. All existing tests pass: `tests/glyphs` (101 tests, including the owner's regression set
   `tests/glyphs/test_initial_batches.py` — 40 crops from earlier review batches, golden values in
   `tests/fixtures/glyphs_golden/initial_batches.json`) and `tests/test_provenance_cli_api.py` (regenerate
   `docs/API.md` with `scripts/generate_api_docs.py` if you add public names). A golden value may change ONLY when the
   new value is visibly more correct; record the reason in the golden file (as the existing `changed` entry does) and
   update `greekocr/_vendor/origins.json` hashes for that file.
2. On the nine flagged crops, the main line's fitted baseline follows the curled start: report, for each, the
   baseline's residual against the bottoms of the line's own x-height letters in the leftmost 400 px of the crop
   (median and max, px), before and after. Produce one image `.astra/curl_after.png` stacking the left 760 px of each
   of the nine crops with the baseline drawn (as in `.astra/curl_window08.png`), so the owner can verify by eye.
3. No regression on lines that do not curl: run the band fit on all 444 crops of `tests/fixtures/o4d_sample400/crops`
   plus `tests/fixtures/o4d_lines/line*.png` before and after, and report how many main baselines changed by more than
   3 px (mean over the crop) and show a few of the largest changes in `.astra/changed_lines.png` with a sentence each
   on whether the change is right.
4. Simplicity: prefer replacing fragile logic over adding more conditions; explain the method in plain words.

## Deliverable

Commit your change on `astra/curl-fix` (with the attribution lines below at the end of the commit message). Final
message, markdown: what you changed (plain words, then the technical detail), the numbers for criteria 1–3, the image
paths, anything you could not fix and why. Last line exactly:
`RESULT: <FIXED|PARTIAL|NOT FIXED> <one line> | TESTS: <passed>/<total>`

Commit message attribution lines (append verbatim):
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01X3VU3zMmUxSHRDvYfQMczm
