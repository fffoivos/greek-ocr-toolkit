# N1-S: score the glyph pass, Google-vs-ink table, owner sheet HTML (gpt-6.1-sol, medium, network OFF; no .git writes; no reading run)

Same worktree, constraints and interpreters as the N1 briefs. Inputs:
- `artifacts/n1/answers/ctxNN.r1.*` (7 contexts) and `cal01.r1.calibration.json` (82/82, PASS);
- keys under `artifacts/n1/keys/`;
- the geometry/measurement records (`step1_rendered_v3.jsonl` and side records);
- the frame `artifacts/n1/frame_step1.jsonl`;
- `docs/records/labelfix/secondary/PLAN.md` §2 and §8.

**Do.**
1. **Gate per context.** More than 1 wrong control answer → VOID (unreadable is an abstention, not wrong). Do not use VOID contexts'
   bed answers; list them for a re-read.
2. **Google-vs-ink table** over the bed slots of VALID contexts: rows = Google glyph (text gap), columns = reader meaning. Also give
   it per source/era and per grammar position. Highlight:
   - **Google `-` → raised dot** (the target fault);
   - Google `.` → raised dot;
   - Google `-` → baseline dot;
   - Google `.` → comma, and Google `,` → baseline dot (decimal/grouping confusion);
   - Google empty → any mark (a missed mark);
   - any → unreadable / other.
   Estimate the target-fault rate inside the frame strata, with Wilson intervals and the frame's design weights, and say clearly that
   the frame is enriched and not a population sample.
3. **Rule-readiness note** (no fitting yet). For the slots read as raised dot vs hyphen-or-dash, list the side-record measurements
   (component height, centre relative to the digit band, width). Report only descriptive separation statistics (ranges, overlap
   count) as input to step 2, and fit nothing.
4. **Owner sheet** `artifacts/n1/owner_sheet/n1_sheet.html`.
   - Build it with `greekocr.adjudicate.owner_sheet.render` from `~/Projects/greek-ocr-toolkit-cleanup`, run under
     `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python` with that PYTHONPATH. Do not modify the cleanup worktree.
   - **One card per SLOT** where the reader's meaning disagrees with Google's glyph, or the answer is unreadable/other/low
     confidence. Doc id = `<line_id>:s<slot>`, passing `slot` so the renderer draws the gap box. Contents:
     - `image`: the line crop;
     - `zooms`: the marked 3× zoom;
     - `rows`: `Google` (W1 features `text`, never empty); `Proposed` (only for Google `-`/`.` → reader raised dot in a
       grammar-thousands slot: the line with that one gap changed to U+00B7; otherwise omit the row); `Reader` (meaning +
       confidence);
     - `tags`: the Google glyph → reader meaning, the grammar position, and the source/era;
     - `printed`: not prefilled;
     - `group`, in this order: "Hyphen printed as raised dot" (Google `-` → raised dot); "Dot printed as raised dot"; "Other
       mark disagreements"; "Unreadable or low confidence".
   - Add one group "Agreement sample": 12 seeded slots where Google and the reader agree, as a sanity view.
   - **spec:** title "N1 Numeric Separators"; intro of at most 4 sentences: Google writes raised thousands dots (4·547·331) as hyphens;
     a blind Sol reader read each gap from the ink; "Proposed" changes only Google `-`/`.` to `·` where the ink shows a raised dot and
     the number grammar allows grouping; please correct anything wrong in the note or Printed.
   - Keep the HTML under 15 MB and report its size. Write `artifacts/n1/owner_sheet/summary.json` (counts per group, hashes).
5. **Receipt and report.** Write `artifacts/n1/N1S_RECEIPT.json` and the report `docs/records/labelfix/secondary/N1S_REPORT.md` (gate table,
   the Google×ink tables, fault rates, the rule-readiness note, sheet counts). Run the tests: add tests for the gate, the table and
   the Proposed rewrite (one gap only, U+00B7, offsets preserved).

**Last line:** `N1S READY: contexts VALID <n>/7 (void <list>); bed slots read <n>; Google '-'→raised <n>, '.'→raised <n>, other disagreements <n>, unreadable/low <n>; target-fault rate in frame <x>% [<lo>,<hi>]; sheet <MB> MB, cards <n>; tests <n> passed`
