# Owner review of the page-lines detector, round 3 (9 October 2026)

This is the owner's review of Astra's round-3 output: branch `astra/page-lines-3`, commit 0c08015, review page
https://claude.ai/artifact/7rt1qMCTEkPsvkj3iyrmjz. The cases are numbered after the 25 of round 2
(`OWNER_PAGE_LINES_REVIEW_ROUND2_20261009.md`). Lines marked **Owner:** are the owner's words. The measurements were
taken by the coordinator from the round-3 outputs (`.astra/out/<key>.lines.json`) and the page images.

**Owner, overall:** "ok this is quite good and I think we shouldnt improve on it before we complete the first work
cycle." Before the code's quality is trusted, it is to be run on 50 new, varied pages (owner: "we should run this on
50 diverse new pages though before we are sure of the quality of the code").

## 26. s2-0ce9d1025b3f23c7119e-p00001: still joined across the columns, and the faint letters still detected

**Owner:** "s2-0ce9d1025b3f23c7119e-p00001 is still not solved, we have connections across columns, and the faint
letters are detected."

This is round-2 case 8 (faintness), not fixed, together with a column-crossing case on the same page.

Measured on the round-3 output:
- **The columns.** The page has two columns, with a column gap at x ≈ 1715 that has no ink at all down the page.
- **Lines crossing the gap.** Of the page's 64 lines, 34 are discounted as faint. Of the 30 active lines, **9 run
  across the gap**: lines 3, 4, 9, 11, 13, 19, 21, 23 and 24, each spanning from x ≈ 235–425 to x ≈ 2580–3190.
- **How the faint ink stays in.** In 7 of the 9, one half is faint and the other is printed text from the other column:

  | Line | Baseline y | Left half darkness | Right half darkness |
  |---|---|---|---|
  | 3 | 274 | 185 (faint) | 78 |
  | 4 | 339 | 163 (faint) | 71 |
  | 9 | 551 | 187 (faint) | 75 |
  | 19 | 1000 | 70 | 180 (faint) |
  | 21 | 1065 | 73 | 196 (faint) |
  | 23 | 1131 | 70 | 202 (faint) |
  | 24 | 1194 | 71 | 159 (faint) |

  Darkness is the median grey of the darkest fifth of the pixels between mean line and baseline; 0 is black and 255
  white.

  The faint half rides along with a dark line from the other column. The line as a whole passes the faintness test,
  with contrast 0.87–1.01 against the page's text, so the faint letters are kept.
- **Two dark-to-dark joins.** Lines 11 and 13 join two dark halves across the gap.
- **The checks report 0 rule or gutter crossings.**

What this means for the requirements of round 2:
- Column boundaries (round 2, section 5) must hold before lines are joined. A full-height empty gap is a column
  boundary even without a printed rule.
- Faintness (round 2, section 3) must be judged on each piece of a line, not on the line as a whole. A faint piece is
  discounted even when it is joined to dark text; with the column boundary respected, the two would not be one line.

## 27. s2-93f8070059f938bda524-p00001: a good result, kept as a reference

**Owner:** "while for example s2-93f8070059f938bda524-p00001 is very good, even though it has faint letters in the
background."

Measured on the round-3 output:
- The page has two columns. It has 129 lines, of which 12 are discounted as faint.
- No active line crosses the columns: the widest active lines are 1422–1450 px, about one column's width on a
  3271 px page, and every active line lies in column 1 or 2.

This is how case 26 should come out: the faint background letters are discounted, and every line stays within its
column. Any change made for case 26 must keep this page as good as it is.
