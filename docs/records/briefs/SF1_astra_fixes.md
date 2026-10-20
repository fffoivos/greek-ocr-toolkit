# SF1 — Fix round for ASTRA-SC1 (gpt-6.1-sol, xhigh)

Workspace: `~/Projects/greek-ocr-toolkit-spellcheck` (branch `opus/spellcheck`, head 6929c738). No `.git` writes. Network OFF. Python:
`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`. Mac CPU, cached alignments, no CTC
forward passes, ≤ 30 min. Read `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SC1_review_1.md` (and its `ASTRA-SC1_evidence/` probes)
in full first; every fix below cites a finding there. Do NOT change detector geometry policy or retrain anything: the toolkit
substitutions (S1–S4) are the next round. Every probe in `review_probes.py` must become a repository test that fails before and passes
after your fix. All existing labelfix tests stay green; never weaken an existing test.

## Fixes
1. **B01 (blocker): print-preserving default.** The owner's rule is "transcribe what is printed". `apply_constraints` must not delete a
   detected mark by default: it FLAGS it (`constraint_flags`, with rule and evidence) and the slot becomes HOLD for labels; the page
   shows the flagged letter with the dotted "reader and detector disagree / impossible by rule" style; a separate, explicitly selected
   `normalised` output may drop flagged marks. `read_line` / `read_ink` default = print-preserving. Report how many held-out marks were
   deleted under the old default and now flagged (expected ≈ 100 + 13 unknown). Keep C1-after-consonant and C3 held back.
2. **M03:** `scripts/labelfix/s6_validate.py` (and any other truth builder) must keep unsupported printed mark sets (`mark_class` →
   None: double accents, macron/breve, other) as UNKNOWN with a reason, never as known "no marks". Recompute the S6 and K1 numbers
   that change and list them before → after.
3. **M04:** blobs carry their source component ID(s) and pixel mask; clipping intersects that mask with the legal zone and never
   rediscovers membership by majority label in the bounding box. Assert: clipped pixels ⊆ original pixels; area never grows; union
   ownership is conserved. Deduplicate by source pixels/identity.
4. **M05:** virtual (union) regions carry the full parent-label set / mask; `case.features` and every width/occupancy/shape consumer use it.
5. **M07:** the owner-page builders (`scripts/labelfix/owner_pages_build.py`, `owner_pages_build_combined.py`) require an explicit,
   hash-bound reading configuration (detector commit, shape model, case model, R1 checkpoint, constraint policy) and record it in the
   page's HTML comment + `--boxes-out` sidecar; default shape model = `markshape_model_S4.json`. Page text and overlays come from the same
   serialized `LineReading` (raw detection, flagged-by-constraint and final reading distinguished). Remove the unused Google-using
   helpers `ours_line` / `reconstructed`. Add a parity test: changing only Google/human fields cannot change "Ours".
6. **M08:** `box_regression.py`: one-to-one maximum-weight matching (no greedy order dependence); report lines missing from either side;
   assign a changed box to a letter only when it lies within that letter's mark zone, else "unassigned"; keep old/new slot namespaces.
   `owner_implicit_changes.py`: bind to the reviewed page snapshot (old sidecar slot geometry), parse slot numbers only from
   slot-shaped clauses ("at 7", "7-8", "slot 7"), no ±1 neighbour widening, missing targets = unresolved. `s6_notes.py` /
   `r1_owner.py`: missing targets unresolved, compare names and multiplicity on approved slots, and use the CURRENT note files
   (`owner_notes_review_v16_20261016.jsonl` 49, `owner_notes_examples_v10_20261016.jsonl` 57) as well as the old sets, labelled.
7. **M09:** `r1_score.py`: baselines passed explicitly by name (`--baseline S4=… --baseline S6=…`), each verified by hash and expected
   totals; score receipt includes baseline, extraction, prediction, scorer and constraint-policy hashes; produce raw and filtered tables
   symmetrically (filter the baselines too). Do not use S4 detector blobs to rank R1 proposals. Regenerate
   `docs/records/labelfix/spellcheck/clariden/R1_result_3678928/` with correct S4/S5/S6 labels (keep the old files as `*_superseded`).
8. **N01:** historical validators pin their behaviour (explicit `filtered=False` / version guard) and serialize the rendered parts.
9. **N03:** missing case model → fail closed (or explicit `unqualified_fallback` flag, never probability 1.0); heuristic mark names carry
   their own provenance, not the rejected model's probability.

## Deliverables
Code + tests, `docs/records/labelfix/spellcheck/SF1_REPORT.md` with one section per finding (fixed how, test name, numbers before → after), last
line: `SF1 RESULT: B01 fixed (<n> deletions now flags); M03 <k> truths now unknown; M04/M05/M07/M08/M09/N01/N03 fixed; tests <n> passed; numbers changed: …`.
