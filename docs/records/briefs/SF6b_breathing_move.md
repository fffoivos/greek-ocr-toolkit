# SF6b — One exception to SF6: the spacing-breathing MOVE (gpt-6.1-sol, xhigh, network OFF)

Workspace/rules: as `docs/records/briefs/SF6_two_signal_deletions.md` (read it). Head = this commit on abbd2ec1 (SF6). No `.git` writes; other
worktrees read-only. Saved evidence only. All labelfix tests green, none weakened. **Add exactly one exception; change nothing else.** Policy
id stays `sf6-release-v1` but bump `policy_binding`/policy sha so the release binds the new code (state the new sha).

## Ruling (coordinator, 17 Oct, exact)
`-᾿Αλλά` → `-Ἀλλά` is a **MOVE, not a deletion**, when (a) the combining breathing written is the same kind (psili ↔ ᾿/᾽ psili form,
dasia ↔ ῾ dasia form) as the spacing sign consumed, and (b) the reader (R1, A∧B as one) names that breathing on that capital (observed,
scored, in-window). Then it needs no absence signal, because nothing is removed from the line's content. In every other case SF6's
two-signal rule applies unchanged (a different kind, a reader that does not name it, unscored/uncertain → HOLD as now). This is the ONLY
exception to SF6.

## Do
Implement it in the SF6 deletion check (`release_gate.py`), with witnesses: the two L1A capital lines
(`32aae9fec147d3b483deb96e-p000060-l0057`, `a963b33d02c23d4127f5ec26-p000012-l0029`) release as one breathing when (a)+(b) hold in their saved
evidence (else state why they still HOLD); a synthetic case with a mismatched kind (spacing psili consumed, dasia written) → HOLD; a reader
that does not name the breathing → HOLD. Update the SF6 tests only where this exception changes an expectation (exact checks). Re-run the SF6
held-out/M2/witness measurements and append an "SF6b" section to `docs/records/labelfix/spellcheck/SF6_REPORT.md` (before = SF6, after = SF6b; any
change explained per line). Last line of the appended section:
`SF6b RESULT: breathing-move exception; capital witnesses released <k>/2; mismatched-kind HOLD yes; unnamed HOLD yes; held-out AB corrected <..>, wrong <..>; tests <n> passed; policy sha <..>`.
