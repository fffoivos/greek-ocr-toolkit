# GC1: build gate sf7 (variants A and B) and the sf7-rc1 recompose package (gpt-6.1-sol, medium; network ON only for the Clariden deploy/sha/test-only/dry-run; no .git writes; NEVER submit)

**Owner GO, 17 Oct.** The preregistration is `docs/records/labelfix/spellcheck/SF7_PREREGISTRATION.md`, sha256
64a84ed0c8799026d44f066570b54075e9b9d1fbca8e2f099cfc9e9451189b2d. Record it in every receipt; the rules there are binding.

**Background:**
- `docs/records/briefs/SF7_insertion_symmetry.md`: the earlier unrun SF7 brief. Reuse its analysis; the variants below supersede its rule.
- `docs/records/labelfix/spellcheck/SQ1_QUOTE_BREATHING.md` (the quote fix shape + regression pair).
- `docs/records/labelfix/spellcheck/L1A2_AUDIT100_RESULT.md`.

Workspace: THIS worktree (`opus/spellcheck`). Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`.

## 1. Gate code: additive and versioned; sf6 stays byte-reproducible

- **Do not edit sf6:** the 16 sf6 policy paths, digest `6f62925a…`. sf6 must still reproduce its release bit for bit.
- **sf7 is a new policy**, `sf7-release-v1`, in NEW modules (e.g. `greekocr/labelfix/release_gate_sf7.py` plus anything it needs),
  reusing the sf6 primitives by import. It has its own `policy_binding()`/digest over its path set, and one config flag
  `addition_rule: "A" | "B"`.
- **Rules:**
  - (1) the quote alias, exactly as in the preregistration;
  - (2) deletions as sf6;
  - (3) substitutions by the reader alone, i.e. the sf6 semantics today. State which these are; if they differ, report BEFORE
    changing anything.
  - Additions:
    - **A** = as sf6 (the reader ensemble alone), except that an iota-subscript insertion needs a detector below-mark owned by that slot;
    - **B** = an insertion needs the reader AND (a detector ink group owned by the slot OR the scored recogniser text carrying the mark).
- **Tests:**
  - the SQ1 pair (both variants);
  - all 17 audit-wrong lines and the 83 audit-right lines, replayed from saved evidence: per variant, how many of the 17 are fixed and how
    many of the 83 are lost;
  - the 39 cards; every existing gate test, unchanged for sf6;
  - a test that sf6 output is identical before and after this change on the saved fixtures.

## 2. Recompose package for the full polytonic training set (template: `docs/records/briefs/L1R3_sf6_recompose_job.md` + the R2J4 lessons)

- **Inputs:** the saved L1R3 3680729 reader, detector and recogniser outputs on Clariden (no new inference) and the same 124,669-line
  selection.
- **Outputs:** two release files (A, B) in the sf6 release schema plus `policy`, `variant` and per-line rule traces. A new remote root
  `…/greek-ocr-e3/labelfix_sf7_20261017`.
- **Before deploy:** a local mock through the exact sbatch entry point, AND a real-input login-node dry run on a 2,000-line slice of
  the real inputs. It must reach the composed output and exit 0.
- **The sbatch:** cds to its own root and checks shas there, with PYTHONPATH = root (the wave-1e lesson).
- **The deploy manifest:** every deployed path is tracked-or-hashed. Deploy, then remote sha = local, then `sbatch --test-only`. Write
  `LEAD_COMMIT_PATHS.txt` and `VERIFY_CMD.sh` (the coordinator's verify_deploy, as in R2J3).
- **Forecast:** from L1R3's measured time.

## Report

`docs/records/labelfix/spellcheck/SF7_RC1_PACKAGE.md`:
- the rule diff vs sf6 per variant;
- the audit replay table (fixed of 17 / lost of 83, per variant);
- tests; the sf6 reproduction check; the new sf7 digest;
- the mock, the dry run and the deploy evidence;
- the submit command.

Last line: `GC1 READY: sf7 digest <12>; sf6 reproduction identical yes; audit replay A fixed <n>/17 lost <n>/83, B fixed <n>/17 lost <n>/83; SQ1 pair pass; tests <n>; dry run exit 0; deployed <n> sha match; test-only ok; lead commit list <path>`.
