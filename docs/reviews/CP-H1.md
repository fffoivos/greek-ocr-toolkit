# CP-H1 — Independent certification of the T13c H1 pilot

**HOLD for scale-up: the numerical recount is correct, but two HIGH geometry failures admit invalid crops.**

Reviewed 12 October 2026, offline, without background jobs or tracked-file edits. Scope: `c699f4d..2bbd00f`. Checkout HEAD was `56551507a9005c549b725d0707f78da08a0d3429`; the scoped harvest package, harvest tests, report and gallery are unchanged from `2bbd00f`. The brief and §H1 were read first. This review independently reparsed the 1,000 raw Google responses and recalculated labels and disagreement statistics; it did not use the stored tiers as the basis for classification.

## Findings, most severe first

1. **HIGH — Separate columns are joined into a labelled line.** `greekocr/harvest/core.py:82`, `core.py:139`, `core.py:79`; evidence in `docs/harvest/pilot_review.html:1782` and `PILOT_v1.md:147`. When detector polygons already span Greek and German parallel columns, column inference treats their combined width as one text band. The crop then passes the width and column gates, and horizontal reader pieces are joined. I inspected page 23 and page 24 and their crops: these are separate physical columns. `anemi-39efef08912bdefa01efa90d-v5c05ae52-p000023-l0038` becomes **tier 2**; page 24 `l0011` is tier 2 and `l0012` is **tier 1**, despite crossing the gutter. Both readers agreeing cannot repair that geometry. **Before scale-up:** split or reject crops crossing a physical column boundary, and re-audit these accepted cards.

2. **HIGH — The straightener admits neighbour slivers.** `greekocr/harvest/pipeline.py:238`, `pipeline.py:249`; evidence in `docs/harvest/pilot_review.html:667` and `PILOT_v1.md:146`. The neighbour filter only rejects a fitted neighbour with `visible >= 0.5`; the clipping check averages top/bottom body cuts. I saw fragments from the preceding row above the main text in `anemi-1697d5cc21fa26717b97e073-v1d3645ab-p000106-l0041`, still present after straightening. It was sent to both readers with empty gate flags and zero reported top/bottom cuts. Its tier-3 disposition prevents a label here, but does not honour the pre-Google single-line gate. **Before scale-up:** exclude retained neighbour ink or remove it while preserving the complete main row; verify against page pixels.

3. **MEDIUM — Relocated bulk artifacts break tests and review paths.** `tests/test_harvest.py:128`, `greekocr/harvest/report.py:29`, `pipeline.py:142`. The exact requested test command initially gives **81 passed, 12 setup errors, 2,359 deselected** because its ignored fetcher fixture is absent at the old repository path. A temporary link to the supplied archive restores **93 passed, 2,359 deselected**; the link was removed. The local gallery also has **1,000 unresolved image references**, and every record's original absolute page-image path is absent. All referenced images and raw responses were found and hash-checked using the explicit mapping `repo/docs/harvest/` → the supplied `pilot_t13c/` archive. Log a portable bulk-root resolver or documented local links; do not describe the repository gallery alone as currently viewable.

4. **MEDIUM — Page borders trigger false table exclusion.** `greekocr/harvest/core.py:103`, `core.py:111`; example `anemi-0cb3f67240837f77ee728005-v02def8a2-p000020`, record `l0001`. I saw two facing pages of body prose, surrounded by a dark scan border, with no table. The rule counter reports three horizontal and four vertical components and excludes the whole page as `table`. This reduces yield and changes which books/lines enter the sample. Log border masking or a requirement that rules form an internal table structure.

5. **MEDIUM — The broader §H1 rare-glyph preservation rule is unqualified.** `greekocr/harvest/core.py:27`, `core.py:191`, `report.py:137`; `docs/harvest/PILOT_v1.md:159`. The pilot implements the brief's explicit substitution agreement rule, but has no CLLG-labelled rare-glyph tier or independent ink-exposure denominator. Both engines emit zero of the eight tabulated rare characters; that does not establish that the sampled ink contains none. This is explicitly disclosed and does not invalidate the substitution recount. Log separate qualification before claiming §H1 rare-glyph coverage or applying this filter to rare-glyph sources.

6. **LOW — Axis-aligned height can reject a single tilted row.** `greekocr/harvest/core.py:136`; example `anemi-00c322b3ee04b419d1979f22-vebd783a7-p000087-l0013`. I saw one row, not two, but its axis-aligned box height is 62 px versus `1.5 × 39.5 = 59.25` px. The arithmetic follows the contract; the tilted-row geometry causes conservative loss. Log this when interpreting yield.

No BLOCKER was found. The two HIGH findings remain open; no implementation fixes were made during certification.

## Independently recomputed numbers

The bulk JSONL SHA-256 is `108c3635a5ffc3a424f5810b9491639fdee047fcd926c7423a731ed415b6cbe4`, matching the delivery receipt. All eight decade yield tables reproduce exactly. Detailed machine-readable results are in [CP-H1_recomputed.json](CP-H1_recomputed.json).

| Measure | Recomputed | Reported |
| --- | ---: | ---: |
| Target books attempted / pages | 150 / 300 | 150 / 300 |
| Middle pages per target book | 2 for all 150 | 2 |
| Books supplying sampled lines / zero yield | 142 / 8 | 142 / 8 |
| Lines found / surviving gates | 14,200 / 8,032 | 14,200 / 8,032 |
| Gate rejects / unsampled lines | 6,168 / 13,700 | 6,168 / 13,700 |
| Sampled lines / unique crop hashes | 500 / 500 | 500 sampled |
| Tier 1 / tier 2 / tier 3 / reader rejected | 188 / 217 / 82 / 13 | 188 / 217 / 82 / 13 |
| Google reservations: Vision / DocAI | 500 / 500 | 500 / 500 |
| List-price reservation cost | USD 1.50 | USD 1.50 |
| Usable pairs / disagreeing pairs | 487 / 299 | 487 / 299 |
| Strict disagreement | 61.3963% | 61.4% |
| Disagreement lines with diacritic differences | 188 | 188 |
| Disagreement lines with punctuation differences | 133 | 133 |
| Disagreement lines with Greek-letter differences | 89 | 89 |
| Vision fewer marks / DocAI fewer marks | 121 / 11 | 121 / 11 |
| Equal total mark count among disagreement lines | 167 | — |
| Identical after stripping all NFD combining marks | 92 / 299 | 92 / 299 |
| Acute differing occurrences | 106 | 106 |
| Grave differing occurrences | 94 | 94 |
| Smooth-breathing differing occurrences | 69 | 69 |
| Circumflex differing occurrences | 44 | 44 |
| Rough-breathing differing occurrences | 36 | 36 |
| Iota-subscript differing occurrences | 23 | 23 |
| Diaeresis differing occurrences | 1 | — |
| Raw NFD marks: Vision / DocAI | 5,055 / 5,218 | 5,055 / 5,218 |
| Exact requested harvest test selection, original paths | 81 passed; 12 errors; 2,359 deselected | 1,275 passed in a broader selection |
| Same test selection, archived fixture temporarily restored | 93 passed; 2,359 deselected | — |

Per-book sample counts are: 79 books with four lines, 60 with three, one with two, two with one, and eight with zero. All records are Anemi; none are Vouli. The minimum sampled width/band ratio is approximately **0.816**, above 0.8. All 500 satisfy the recorded numeric height, neighbour-height, page-edge, column-edge and clipping thresholds; the HIGH findings show that these thresholds do not certify the actual crop geometry.

The USD 1.50 is `1,000 × USD 0.0015`, reconstructed from all budget reservations and bound to exactly the 500 sampled crop hashes. It is a list-price reservation estimate, not an independently verified invoice or refreshed price quote. The report separately discloses two earlier archived calls, USD 0.003; including those gives USD 1.503, still below USD 3.

### Disagreement method and interpretation

I reconstructed both readings from raw per-line boxes, applied the list geometry and explicit whole-word substitution rules, then computed NFD Levenshtein distance with whitespace collapsed. All 500 resulting tiers, label/no-label decisions, parsed pieces and cleaned texts match the saved records. The raw results contain nine obstructed reader outputs, two stacked-band outputs and three garbage-only outputs across 13 rejected pairs; one pair has failures in both readers. Usable side-by-side pieces are joined in x order, and exterior garbage is dropped as specified by the current code.

For the 299 tier-2/3 lines, I used NFD-normalized cleaned readings and `difflib.SequenceMatcher(..., autojunk=False)`. A category counts a line if a non-equal span contains that category. The six per-mark figures count **occurrences on both sides of non-equal spans**, not affected lines. The corresponding affected-line counts are acute 90, grave 82, smooth breathing 62, circumflex 41, rough breathing 34, and iota subscript 21. Categories overlap.

**Supported morning-report wording:** “Vision returns systematically fewer polytonic marks than DocAI in this sample.” Among the 132 disagreement lines with unequal mark totals, Vision has fewer in 121 (91.7%). The 299 lines contain 3,005 Vision marks versus 3,168 DocAI marks. The directional differences particularly favour DocAI for graves, breathings and circumflexes; Vision emits more acute accents. These observations support a relative under-marking tendency, including accent substitutions. Establishing which reader preserves the correct printed marks requires visual gold adjudication; the counts alone cannot establish that every extra DocAI mark is correct.

## Ten page-and-crop decisions checked by eye

Identifiers below are abbreviated to the unique book hash, page and line. I viewed the full page render, the highlighted target, surrounding rows and any available raw/straight crop.

| # | Identifier | Decision and firsthand observation |
| --- | --- | --- |
| 1 | `89e508dc… p63 l1` | Reject rotated/table/non-body: a sideways ruled numeric table; exclusion is appropriate. |
| 2 | `0cb3f672… p20 l1` | Reject table: a body-prose spread with dark border and no table; false positive, MEDIUM above. |
| 3 | `052a7a91… p99 l1` | Reject bend scout plus short width: body rows slope across the page; the target is just “τόπου.” The nonzero scout side is propagated correctly; the short fragment is inappropriate for the sample independently. |
| 4 | `10519e82… p2 l1` | Reject non-body: almost blank page with faint show-through and a corner watermark, no sustained body text. |
| 5 | `00c322b3… p87 l13` | Reject height: one tilted prose row with an oversized axis-aligned box; conservative loss, LOW above. |
| 6 | `95a8decf… p100 l4` | Reject clipping: a rising strip crossed by a watermark, with lower ink cut close to the crop boundary; recorded bottom cut 0.119 exceeds 0.08. No Google call was made for this candidate. |
| 7 | `0550c3c5… p49 l80` | Reject height/neighbour-height: an unusually tall target box over a body row adjacent to a heading/diagram. The numeric decision is consistent; the underlying row looks single. |
| 8 | `00c322b3… p87 l4` | Pass, tier 1: one full-width row within the right text band, with the printed terminal hyphen visible and no obvious retained neighbour ink. |
| 9 | `39efef08… p23 l38` | Pass, tier 2: separate Greek and German columns merged across the gutter; HIGH above. |
| 10 | `1697d5cc… p106 l41` | Pass geometry, tier 3: upper-row fragments remain in the straight strip; HIGH above. |

I additionally inspected page 24 of `39efef08…` and the tier-1 `l0012` crop to confirm that the same cross-column failure can survive exact reader agreement.

## Cleared items

- Exact proposal membership, two contiguous global-middle pages across volumes, 300 saved page PDFs and their hashes; saved PDF bytes **37,296,232**. The sample was limited to 500 Anemi lines, with no reads on the 13,700 unsampled records.
- All **300 page decisions and 14,200 base crop decisions** reproduce from the reviewed code and page renders, with no stored-decision mismatch. Page flags count 18 table, 15 bend-scout, 10 non-body and two rotated decisions; flags overlap. Formal gate replay passes; the two visual false negatives remain HIGH.
- NFD/whitespace tiering, two-edit threshold, explicit substitutions, horizontal joining, stacked-band rejection and garbage handling reproduce the complete sample. Rare substitution tags are zero. Tier 3 and rejected records have no label.
- All **14,200 records** carry the frozen stack commit, six harvest source hashes and gate metadata. Unsampled reader dictionaries are empty by design; all **500 read records** retain both readers' raw responses, boxes, confidences and image hashes. All **1,000 raw receipt hashes, binding metadata and mean/min symbol confidences** reproduce without mismatches.
- All **256 exported stack files** match canonical Git blobs at `52cee3bcc882e7426bdc1018d892cd9b1bf9feac`. The gallery has exactly 500 matching card IDs/tiers and 1,000 matching crop images in the supplied external archive.
- A credential-pattern scan covered 6,826 code/artifact text files. Its two broad-scan hits are pre-existing inert test fixtures; no actual credential material was detected. No Anemi environment credential values were available for literal matching. No network or credential-service calls were made.
- Required tests ran with `TMPDIR=$PWD/.review_tmp`, bytecode writing disabled and pytest's cache provider disabled. Tracked files were unchanged. The temporary fixture link and `.review_tmp` were removed after review.

VERDICT: HOLD numerical recount certified; fix cross-column crops and neighbour slivers before scale-up | BLOCKERS: 0 | HIGH: 2
