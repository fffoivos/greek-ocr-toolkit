# RU1 failed-control review (lead pixel check, 17 Oct 2026 15:55, declared BEFORE r2 results)

**Sheet.** `scratchpad/ru1_review/ru1_failed_controls.png`: 5 failed r1 control slots plus 6 correctly read anchors, each with a
4× word zoom and an 8× final-letter zoom.

| Slot | Control truth | r1 | Lead reading of the ink | Ruling |
|---|---|---|---|---|
| d558bd3e803e7865-s003-l0017 #1 (потужит?) | ъ | ь | A clear flagged ъ, the same shape as the вынесетъ anchor. | Truth stands; Sol error (miss). |
| d558bd3e803e7865-s003-l0032 #2 (хватит?) | ь | ъ | Bold condensed face; a small left serif on the stem top that could be read as a flag. The context "а не хватитъ рыбы" (3sg future) takes ъ, and the C1 checker (card c084) recorded printed ъ. | **Truth disputed.** This slot is excluded from control scoring from now on, in r1 rescoring and r2. |
| 03b43bc5289ad8ce-s007-l0006 #1 (сил?) | ъ | u | Broken print. | An honest abstention. Counted as "u", not as a wrong sign. |
| 4ce4c0e3183ce075-s004-l0017 #1 (…ять) | ь | ъ | An unflagged ь on a grey, low-contrast scan. | Truth stands; **Sol false ъ** (the dangerous direction). |
| 3fd32314d172e951-s006-l0010 #2 (кончит?) | ъ | ь | A clear flagged ъ, although the infinitive spelling would be ь. The ink wins. | Truth stands; Sol error (miss, probably language-guided). |

## Rescored r1 controls

The disputed slot is excluded and u is counted separately: **70/74 correct, 1 u, 3 wrong.**
- Hard missed as soft: 2 of 61 true-ъ reads.
- **Soft read as hard: 1 of 12 true-ь reads.**

## Consequences

- The gate rule is unchanged (>1 wrong sign per context → VOID; u does not count as wrong). Under this rescoring, ctx02 has 1 wrong
  (VALID) and ctx01 has 1 wrong (VALID).
- The two-read edit rule (RU1-1b) stays: a single-read false-ъ rate of about 1 in 12 is too high to edit on one read.
- Every r1/r2 disagreement and every u goes to the lead.
- The combiner must apply this rescoring: the disputed slot is excluded, and u is not counted as an error. A small Sol change follows
  after r2.
