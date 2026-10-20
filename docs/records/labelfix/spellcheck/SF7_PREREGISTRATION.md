# sf7-rc1 gate cycle: preregistration (17 Oct 2026, written before any sf7 build or score)

**Owner GO (via coordinator, 17 Oct):** open the gate cycle. Build release candidate sf7-rc1 on the full polytonic training set, then:
- an Astra verification;
- the LQB delta vs sf6 and raw Google;
- a blind 100-line audit;
- registration in wave 1c as the marks version.

Nothing binds before the audit.

## Rules bundled in both variants

1. **Quote alias before a capital (SQ1).** When Google has a quote or apostrophe alias immediately before a capital and the release adds
   a breathing and/or accent on that capital:
   - one physical mark group → consume the alias (a replacement);
   - two separate groups (a quote + a mark compound) → keep both;
   - otherwise → HOLD.

   The renderer, punctuation compare, composer and deletion/MOVE guards all use the same decision.

   **Regression pair:** `nlg--f4b52df5f8130047--s005-l0015` must give Ἄδεια with no residual quote; `nlg--f4b52df5f8130047--s004-l0008`
   must keep « plus the compound.
2. **Deletions:** unchanged from sf6 (two positive absence signals).
3. **Substitutions:** reader alone (the owner's rule; the substitution review found agree 20/20, other mark 19/20, no ink 17/20).

## The two variants (the only difference is the addition rule)

| Variant | Addition (insertion) of a mark |
|---|---|
| **A** (owner's reader-alone rule) | The reader alone may add a mark. **Exception:** an iota-subscript insertion needs an observed below-mark in the detector's ink (the SF7 subscript clause). |
| **B** (full SF7) | Every inserted mark needs two positive presence signals: reader AND (detector ink OR scored recogniser text). |

**Why B exists** (sf6 release audit, L1A2_AUDIT100_RESULT.md):
- reader additions that had detector ink were right **38/38**;
- the 17 wrong lines were all additions: **13 iota subscripts + 4 breathings/accents on bare forms** (οι→οἱ, ο→ὁ, .Α.→.Ἀ., ΦΡΑΓΚΙΣΚΗ→ΦΡΆΓΚΙΣΚΗ).

A addresses only the subscript part; B addresses all 17.

## Choice rule (fixed now)

- **Selection:** the variant with the higher **LQB marks precision** wins. Use tier A/B truth only, with in-sample items excluded (the
  LQB in-sample guard). Ties go to **A**.
- **The winner gets:** the blind 100-line audit and the wave-1c registration.
- **The loser:** is kept as a file and never released.
- **The audit:**
  - Sol readers where the HANDOVER qualifies them (line letters; the grave/acute word pass; capitals per CQ1 with the compound re-read
    rule);
  - Opus readers after the Claude reset for four-head word-mark cards.
  - Nothing binds before the audit result.
- **Pass bar for the audit:** sf7-rc1 line precision ≥ the sf6 audit's 83/100 on a fresh 100-line sample, with no line class worse
  than sf6 beyond 2 lines. The cluster-bootstrap interval is reported.

## Fixed inputs

- Recomposition from the saved sf6-era reader/detector/recogniser outputs (L1R3 3680729). There is no new inference.
- R2a-2's reader replaces R1-A only if R2a-2 passes its own preregistration (R2A2_PREREGISTRATION.md). In that case sf7-rc1 is
  recomposed with it, and this choice rule is re-applied.
