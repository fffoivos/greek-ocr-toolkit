# CQ1 leak resolution and scoring — PROVISIONAL

Scanner v4.3 is pending the coordinator's ruling, to be reported by the lead.
**The scan fails; no control or bed scoring was run.** This follows the explicit
“if, and only if, v4.3 passes” gate. NOT QUALIFIED here means failure of the scan
gate; it is not a measured failure against the tuple agreement bar.

## Evidence

- New wrapper: `artifacts/cq1/tools/scan_rollout_v43.py`; v4.2 is unchanged.
- Scan: `artifacts/cq1/answers/r1.scan_v43.json`.
- All 16 literal store/load concatenations resolve, with original expression,
  binding record, literal suffix and resolved path in `template_resolutions`.
- All 15 returned images still match reader files by exact bytes. Image matches
  are identical to v4.2. Manifest checks are enabled and passed.
- One violation remains: **record 24**, `/zoom/batch1.png`. Its expression is
  `cwd+"/zoom/batch1.png"`, not a load expression. No literal `cwd` binding exists.
  **Record 27 explicitly reports `ReferenceError: cwd is not defined`.**
- The requested “17 resolved, rollout passes” test therefore cannot pass under
  the requested literal-only rule. The wrapper does not invent a binding or
  waive failed tool inputs. A separate failed-expression rule requires a ruling.
- Original rollout SHA-256: `d77a8ce2268dea20d4d7d6d5502c8449598d982290e6d64bf5fc9c8a5ba589fb`.

## Verification

Nine offline regression tests pass, including both quote forms, cross-record
binding, external `/Users/x` plus `/keys/k.json` rejection, missing store rejection,
dynamic store invalidation, fake bindings inside comments/strings, unbound cwd,
forbidden names/parent escapes, font read/write distinction and manifest checks.
The real scan's 16 resolutions were replay-checked against their original
records without executing reader code. See `answers/v43.tests.json`.

No network calls, new reading, budget probes, or `.git` writes were performed.
The existing answers and v4.2 scanner/scan were preserved.

## Scoring gate

Controls: not scored (/6); exact tuples: not scored (/60); invented breathings,
invented accents, missed marks and unreadables: unmeasured. Positives, negatives
and compounds are all unscored. No disagreements have been computed or cleared.
`artifacts/cq1/score.json` records NOT_SCORED with null metrics to prevent treating
unmeasured counts as zero. Any unreadable must go to review and cannot count as
an exact match.

The prescribed bar remains at least 57/60 exact (95%) with zero invented
breathings; more than one control error voids qualification. The original
`score_cq1.py` also explicitly accepts only scanner version 4.2; any future v4.3
scoring invocation must explicitly account for this version guard, preserving
the control gate and tuple rules. It was not bypassed here.

## Recorded Codex weekly usage

Before: 2026-10-17 18:40:41 before:CQ1/cap1/r1 weekly_used=41.0 limit_id=codex primary=41.0%/10080m reset Thu 09:13 secondary=-

After: 2026-10-17 18:42:28 after:CQ1/cap1/r1 weekly_used=41.0 limit_id=codex primary=41.0%/10080m reset Thu 09:13 secondary=-

Recorded weekly use is **41.0% → 41.0%** for the completed CQ1 read. These are
existing read receipts, not new live probes.

CQ2 READY (PROVISIONAL, scanner v4.3 pending ruling): scan v4.3 fail; controls N/A/6; exact tuple N/A/60 (N/A); invented breathings N/A; invented accents N/A; unreadable N/A; verdict vs bar NOT QUALIFIED

## Final result: fresh-context read r1b (17 Oct, 19:00 Athens). Supersedes the provisional section above.

- **Scanner:** the first read (r1) was VOID under the accepted scanner v4.3. Record 24 had an unbound `cwd` path; the call errored and
  returned nothing. That run is kept as evidence and not scored.
- **The r1b read:** a fresh copy of the frozen pack, the same prompt verbatim. Scanner v4.3: **0 violations**, 19/19 images matched to
  the reader's own files (one by v4 pixel reproduction).
- **Controls:** 6/6 (pixel-verified by the lead before the run).
- **Bed:** **57/60 exact tuple = 95.0%** (bar ≥ 95%). **0 invented breathings**, 0 invented accents, 0 wrong breathing types,
  1 unreadable. → **QUALIFIED, at the bar exactly.**
- **Codex weekly meter:** 41% → 42%.

**Lead pixel check of the three non-exact items. The T2 truth is right in all three.**

| Item | T2 truth | Sol | Pixels |
|---|---|---|---|
| kd5fe8491c8 (Ἕλληνες) | rough + acute | rough | A spacing compound ῝ before Ε; the acute is visible. **Sol missed the accent.** |
| ka595bc1feb (Ὕλλου) | rough + acute | rough | A spacing compound before Υ; the acute is visible. **Sol missed the accent.** |
| k3464c330e5 (Ὁ) | rough | unreadable | The mark is an ink blob; "unreadable" is an honest answer, routed to an eye. |

**Caveat:** both real errors are the same kind, an accent dropped inside a breathing+accent compound before a capital. On the 9
compounds in the bed Sol scores **7/9 exact**. That is the case a capitals top-up most needs.
- No capital grave was available in T2, so it is untested.
- n = 60 gives a wide interval: 57/60 has a Wilson 95% interval of about 86–98%.

If (a) is chosen, every Sol "breathing only" answer on a capital with a spacing mark should get a fresh-context re-read (the HANDOVER
flag re-read). Without that rule, compound accents will be under-labelled. This qualification does not authorise R2a-2; that is the
owner's decision.
