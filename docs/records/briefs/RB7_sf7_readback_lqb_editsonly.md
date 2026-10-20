# RB7: sf7-rc1 job 3687228, readback → LQB marks scores for A and B → choice → edits-only release conversion (gpt-6.1-sol, medium; network ON for Clariden only; no .git writes; no submission)

Package: opus/spellcheck 69a00ca13, `docs/records/labelfix/spellcheck/SF7_RC1_PACKAGE.md`.
Root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_20261017`, output `output_3687228/`.

**Binding rules:** `docs/records/labelfix/spellcheck/SF7_PREREGISTRATION.md` (sha 64a84ed0…).

**Cert:** valid until 18 Oct 18:39 Athens. Never refresh it; an auth error means STOP. Read the job state and log first; a FAILED
state is not a failure until the log is read.

## 1. Readback

Pull the receipts, logs, and both release files (A, B) with their manifests and rule traces. Verify every sha against the stage
receipts and write `artifacts/sf7_rc1/output_3687228/READBACK_RECEIPT.json`.

## 2. Release summary per variant (vs sf6 L1R3 3680729, same selection)

Lines corrected / unchanged / HOLD, edits by kind (addition, substitution, deletion, quote-alias consume/keep) and by head, plus
per-wave counts.

## 3. LQB marks scores, using the secondary lead's benchmark READ-ONLY

Use `~/Projects/greek-ocr-toolkit-secondary/docs/labelfix/lqb/`:
- LQB_PLAN.md and SCORE_v2.md for the method;
- `google_truth_v1_1.jsonl` and the latest truth file;
- the in-sample guard;
- the existing score files, as examples of the expected schema.

Score raw Google, sf6 (ENSEMBLE_AB, as in SX1b), sf7-A and sf7-B on the marks rows:
- **tier A and tier B truth only, in-sample items excluded** (the preregistered choice set);
- also all tiers, as a secondary view;
- marks precision and recall per tier, with paired deltas and cluster intervals as in SCORE_v2.

**Apply the choice rule:** higher LQB marks precision on tier A/B, in-sample excluded; ties go to A. State the chosen variant and the
numbers it rests on. If the truth rows that overlap the release are too few for a meaningful comparison, say so with the counts, and
still apply the rule as written.

Write `docs/records/labelfix/spellcheck/SF7_RC1_LQB.md` + `artifacts/sf7_rc1/lqb_scores.json`.

## 4. Edits-only release, chosen variant only (the required form for training overlays)

A version holds ONLY the rows it corrects:
- `text` = the raw v2 Google import, byte-for-byte, except the correction;
- `parent: "google_raw_v2_import"`;
- per-edit provenance: slot, kind, head, rule, signals, variant, policy digest, source job.

**Verify:**
- every row's text differs from the raw import only at the edited positions (a byte diff);
- every edited line is in the selection;
- no row is unchanged.

Find the raw v2 Google import the same way the Cyrillic version did. Ask nothing; search the wave-1c registration docs in the sourcing
worktrees, read-only, and name the path and sha.

Write `artifacts/sf7_rc1/release_edits_only_<variant>.jsonl` + `RELEASE_RECEIPT.json` (sha, row count, edit counts by kind/head/wave,
parent sha). It is NOT bound before the blind audit; mark the receipt `status: candidate_pre_audit`.

## 5. Audit sample (build only)

Build the blind 100-line audit sample from the chosen variant's corrected lines, uniform with seed 20261017. Exclude every LQB truth line
and every line from audit100.
- Write the frame: `artifacts/sf7_rc1/audit100_frame.jsonl`.
- Do NOT build reader packs yet; the lead decides the reader routing.

Last line: `RB7 READY: readback sha ok; A corrected <n> / B corrected <n>; LQB tierA/B marks P A <..> B <..> sf6 <..> google <..> (n=<..>); chosen <A|B>; edits-only rows <n> edits <n> sha <12>; audit frame 100`.
