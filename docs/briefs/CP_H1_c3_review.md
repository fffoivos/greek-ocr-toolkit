# CP-H1 cycle 3 — re-certification of H1 fix 2 (scoped). Reviewer: gpt-6.1-sol, xhigh.
ROLE: independent certifier; implementer ≠ certifier. No network, no background jobs. SANDBOX workspace-write only for pytest temp (TMPDIR=$PWD/.review_tmp; delete after); no edits to tracked files.
READ FIRST: docs/reviews/CP-H1_c2.md (your cycle-2 HOLD), docs/briefs/H1_fix2_ownership.md (the structural diagnosis and the fix), docs/harvest/PILOT_v1.md §"Fix 2 (offline re-gate)", docs/harvest/fix2/.
SCOPE: git range bda44e1..3eaef30 — greekocr/harvest/{core,pipeline,regate}.py, tests, fixtures under tests/fixtures/harvest_fix2/.
Evidence outside the repo: ~/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/harvest_big/pilot_t13c/ (records.jsonl, pages/, pilot_review_images/).
MANDATE:
1. Cycle-2 HIGH 1 (spanning rows): re-run your example `d163abb4… p112` and three more pages with full-width rows above multi-column regions; spanning rows must pass intact,
   fused rows inside multi-column regions must split.
2. Cycle-2 HIGH 2 (ownership): the gate now defines the line's zone from its own guide lines. Of the 500 sampled lines 37 are now rejected, 13 of them tier-1 (both readers
   agreed exactly), 17 for neighbour_sliver. Inspect ALL 13 tier-1 rejections by eye (list in docs/harvest/fix2/sampled_post_fix2_gate.json; crops under pilot_review_images/)
   and state per line whether the rejection is justified. If ≥ 4 of 13 are unjustified, HIGH. Also inspect 10 random lines the gate now ACCEPTS that fix 1 had rejected,
   to confirm no genuine slivers were let back in.
3. MEDIUM (ruled table `d80c7cca… p49`): closed-cell test fires; a framed prose page still passes.
4. Tests: `.venv/bin/python -m pytest tests -q -p no:cacheprovider -k harvest`.
DISPOSITION: BLOCKER/HIGH fixed before scale-up; MEDIUM/LOW logged. DELIVERABLE: markdown; verdict; findings with path:line; the 13-line by-eye table.
Last line exactly: `VERDICT: <PASS|HOLD> ... | BLOCKERS: <n> | HIGH: <n>`.
