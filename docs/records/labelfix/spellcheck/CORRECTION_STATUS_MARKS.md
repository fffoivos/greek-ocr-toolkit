# Correction status: polytonic marks block (17 Oct 2026, spell-check track)

Included by reference in `docs/records/labelfix/CORRECTION_STATUS_20261017.md` (owner: the secondary-corrections lead). Only this track edits
this file.

**Sources for the rates:**
- the C1 quality cards (17 Oct, per 100 cards);
- the sf6 release audit (Audit100);
- the substitution review;
- SQ1;
- R2a digest job 3683130.

**The correctors:**
- the frozen gate `sf6-release-v1` (digest 6f62925a): two-signal deletions, SF5/SF6b spacing-breathing moves, the punctuation guard;
- the R1-A mark reader;
- the S6 ink detector.

**Composition order:** marks release first, on raw Google text. Numeric and punctuation composers come after.

| Fault (print → Google) | Measured rate | Corrects it today | Signal it needs | Next step and gate |
|---|---|---|---|---|
| Grave written as acute, 1850s print (before punctuation) | 3–4 / 100 | Reader names the grave; the gate releases the substitution (owner-reviewed: right 20/20 when the detector agrees, 19/20 when it names another mark, 17/20 with no ink). | Enough already; a Sol word pass (grave 25/26, false 0/26) as a second signal on audits. | None for training. Audit with the Sol word pass when a stratum is re-checked. |
| Grave written as acute or dropped, 1900s print (mid-sentence, systematic) | 9–12 / 100 cards; 87% of final accents print a grave | Reader + gate on released lines; the stratum is flagged `marks_bias: grave_to_acute`. | The Sol word pass (qualified for audits, not release scale). | Measure the released labels on nlg poly1900 against the Sol word pass. No gate change before that. |
| Breathing (± accent) dropped on a capital | 3–5 / 100 | Gate SF5/SF6b for spacing forms (᾿ ᾽); otherwise reader + gate. Capital positive recall on T4 witnesses is 47% for R1-A. | More native capital supervision. R2a (1,572 slots) raised capital recall to 87.5% in all seeds but failed noninferiority, so it was not adopted. | CQ1: Sol capitals qualification (≥ 95% exact tuple, 0 invented breathings) → R2a-2 with fresh capital witnesses, on the owner's go. |
| Quote, asterisk or apostrophe standing for a capital's breathing+accent (e.g. ῎Α → "Α) | 54 held lines in the 124,669-line release; 0 wrong releases | HOLD only: the gate cannot distinguish an alias from a real quote (SQ1). | An ink group count: one compound means replace the alias; two groups (quote + mark) means keep both. | The next gate cycle (with SF7): rule + regression on nlg…s005-l0015 and the real-quote control nlg…s004-l0008. |
| Iota subscript dropped, or inserted where none is printed | 2–3 / 100; insertions = 13 of 17 wrong lines in the release audit | Additions are released by reader + gate; the insertion side is unprotected. | Symmetric evidence for insertions (SF7 rule). | SF7 in the next gate cycle; release-audit rerun as the regression test. |
| Circumflex written as acute | 1–2 / 100 | Reader names it; the gate releases it. | Enough already. | None. |
| Crasis / coronis flattened (θἆταν → θάταν) | 1–2 / 100 (tagged) | Not measured on the release. | Reader exact-name accuracy on coronis (sparse class). | Measure with the exact_names slice when the witnesses are topped up. |
| Elision mark (’ ᾿ ʼ) normalised to ' | Frequent | Never deleted by the gate (SF5 elision rules); representation folded to '. | A codec convention decision (codec v2.1 proposal). | Codec v2.1 ruling (sourcing / codec owner); the gate is unchanged. |
| Marks invented on bare capitals / ο in monotonic print (model-side, release audit) | Release audit 83/100 lines right; R2a target false additions 26 → 23 on T4 (not significant) | Gate two-signal rule; reader. | Witnesses enriched for the hallucination contexts (ALL-CAPS, ο/οι monotonic, -η endings). | Option (b) in R2A_NEXT.md, after the Claude reset and the owner's go on Opus reading. |
| Greek numeral sign (keraia ʹ ͵) | Not measured | Marks gate: category `keraia`; deletion needs detector + recogniser absence. | — | Stays in the marks gate (agreed with the secondary lead); measure when the numeral cards come up. |
| Dialytika, ΐ | Sparse (4 per seed on held-out) | Reader. | More support. | Unestablished; cards on the failure-modes sheet. |
