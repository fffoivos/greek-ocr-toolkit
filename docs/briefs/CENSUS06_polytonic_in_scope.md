# CENSUS06: census_06 = census_05 with polytonic (sf7, released) IN scope, sf7 ledger binding pending (gpt-6.1-sol, medium, network ON for read-only `ssh clariden` and the final deploy `rsync` only, no spend, no jobs)

**Owner ruling (20 Oct 10:47):** the polytonic tool sf7 is released and goes into the pipeline. The coordinator asked for a CENSUS_06 package: the census_05 package with polytonic in scope and **everything else identical**. The spell-check lead is producing the full sf7 run (all polytonic-routed rows, all parents). The coordinator will send the sf7 ledger paths + shas later; until then the sf7 binding is **pending**. You submit nothing; the coordinator submits.

`W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`.

## Base (read-only)
- **census_05 package:**
  - source, prep scripts, records and hand-off are in the worktree `~/Projects/greek-ocr-toolkit-segcensus` (branch `opus/seg-census`), under `docs/harvest/census05/`. Read `HANDOFF_CENSUS05.md` first, then `build_package.py`, `census05_config.json`, `INPUTS.json`, `FOLLOW_UP.md`, `final_checks.py`, the audits, `c_evidence/verify.py` and `docs/briefs/CENSUS05_{A,B,C,D}*.md`.
  - That worktree is another lead's: **read only, write nothing there.**
- **Deployed:** `$W/census_05_20261020/code/997b7d2ab5a8775b/` (manifest DEPLOY_SHA256SUMS sha `997b7d2a…`), inputs `$W/census_05_20261020/inputs/`; completed attempt `attempts/full-split-001`.
- **Pins:** pipeline 0.3.2, gate 0.3, segmentation 0.13 (label 0.9-s5, policy `5888fe70…`), census 0.7.
- **The main checkout `~/Projects/greek-ocr-toolkit` is read-only, and it is currently checked out on another branch.**
  - Read `main` only via `git -C ~/Projects/greek-ocr-toolkit show main:<path>` or `git archive main <paths> | tar -x -C <scratch>`.
  - Never run checkout, switch, stash or any write there.

## Amendment (coordinator, ruled with the spell-check lead): read this first; it overrides the steps below where they conflict
**Why:** sf7 cannot verify about 86% of polytonic lines. Its HOLD means "could not verify", not a detected fault. Under the current code, a missing or unresolved result HOLDs the row (`greekocr/harvest/line_pipeline.py` on `main`, sha `9c6f8ead…`, lines 454–466: `required_evidence_unresolved` → `correction_unresolved` → HOLD).

1. **Pipeline 0.3.3.** Add the line-tool-result status **`kept_unverified`**:
   - **Validation** (`validate_result`, around lines 288–295):
     - it is a known status;
     - it must carry **no edits**;
     - it requires `evidence` carrying the flag and the tool's reason.
     - Qualify it for **polytonic only**, mirroring the `tag_only`/dashes restriction. State this as a lead choice in CENSUS06.md.
   - **Routing** (lines 464–467): `kept_unverified` does **not** produce `correction_unresolved`, so the row can be admitted.
     - It contributes **no edit** to `merge_edits`: the polytonic route leaves the raw text untouched.
     - Other tools' successful edits and the existing composer normalisation behave **exactly as in 0.3.2**.
     - The route record keeps the flag + reason, so the evidence shows the row was kept unverified.
   - **Unchanged:** `applied`, `verified_no_change`, `tag_only` and every other status. `required_evidence_unresolved`/`failed`/`proposal_only`/missing still HOLD.
   - Bump `PIPELINE_VERSION` to `"0.3.3"`. The readout runs with `--expect-pipeline-version 0.3.3`.
   - **The code change:**
     - make it in the census06 package source copy, as an additive/modified file listed with its patch against CODE_SHA (`census06/pipeline_033.patch`), for the coordinator to merge into `main` later;
     - never write to the main checkout;
     - the package is CODE_SHA-identical except this module + version + readout/tests. List every changed file.
2. **tool_versions.json** is regenerated from `main` with **polytonic 0.7 status released** (owner ruling 10:47). Otherwise the corrector loader downgrades `applied` to `proposal_only` (the coordinator cites loader line ~297; find and cite the exact line).
3. **The sf7 binding:** the spell-check lead emits a **full per-row `line-tool-result-v1` file per parent**, covering every polytonic-routed row: `applied` / `verified_no_change` / `kept_unverified` / `unresolved`.
   - **Bind those files, not an edits-only ledger.** `bind_sf7.py` takes one path + sha per parent.
   - It checks **completeness**: every polytonic-routed row of that parent has exactly one record. Check it against the census_05 decisions' polytonic route rows, by streaming in a job if the data is large.
   - It reports the status counts per parent.
   - Add a real-head-sample test (`test_sf7_head_sample`) that, once the files exist, loads the first N records of each file through the loader + `validate_result`. Until then it is skipped as PENDING.
4. **Tests:**
   - The packaged regression + mocks must be **identical to census_05's except for rows/tests that exercise the new status**. Show the diff of results: the expected answer is zero changes on existing fixtures.
   - Add unit tests:
     - kept_unverified admits with raw text for polytonic;
     - kept_unverified with edits is rejected;
     - kept_unverified for cyrillic is rejected;
     - a missing evidence reason is rejected;
     - unresolved still HOLDs;
     - applied/verified_no_change are unchanged.
   - The mocks include kept_unverified rows.
5. **Readout:**
   - count polytonic route statuses (applied / verified_no_change / kept_unverified / unresolved / other) **per parent and per class**;
   - report polytonic admits by status;
   - add an invariant: every kept_unverified admitted row's final_text has no polytonic edit.
   - The census_05 → census_06 **admit/hold flip report per parent** (step 5 below, `flip_report.py`) stays.

Parity 150/888 must stay exact. If it does not, stop and report.

## Do
Work in a new directory, sol-recut `docs/harvest/census06/`.

1. **Package = census_05 + exactly these changes:**
   - **(a) Config:**
     - remove `polytonic` from `routes_out_of_scope` (the list becomes empty, or the key is dropped; follow what the PIPE032 code treats as "in scope");
     - bind the sf7 ledgers in the `corrections` section, beside the cyrillic/numerics bindings and in the same form (path, sha, parent, tool version/digest).
     - These are **pending placeholders** until the coordinator sends the shas; see step 3.
   - **(b) `tool_versions.json`:** regenerate it from `main` with its generator (`build_filter_versions.py`; find the right one on `main`).
     - Component keys keep the **`greek-ocr-toolkit-pipe032/` component prefix**, as on main and in the census_05 package (the "pipe032 component-prefix note").
     - Register polytonic **sf7 as released**: change the scope from `candidate_pre_audit` to released, and record the owner ruling 20 Oct 10:47 in `owner_decisions`.
     - Replace the census_05 coordinator note `polytonic_release_scope`; keep it in history if the schema has a history.
     - **Version:**
       - if the released sf7 components hash-equal the 0.7 components (`release_gate_sf7.py` `2f7a777a…`, digest `de1a9a8b…`), the version stays **0.7**;
       - if the released components differ, **stop and report the diff**. Do not invent a version.
     - Every other tool's entry and digest must be byte-identical to census_05's.
   - **(c) Names:**
     - root `$W/census_06_20261020/`, code `$W/census_06_20261020/code/<package id>/`, inputs `$W/census_06_20261020/inputs/`;
     - attempts `smoke-split-002` and `full-split-002`.
   - **(d) Unchanged:** the same split2 ledger (`7b27ab9b…8b82`), the same parents, metadata, native settings, held-out policy, frozen_05, cyrillic/numerics ledgers (by sha), verifier invariants and readout. Any byte change outside (a)–(c) must be listed and justified in `config_diff.json` / `CHANGES.md`; the expected answer is none.
   - The readout runs with `--expect-pipeline-version 0.3.2`.
   - **Polytonic coverage check:** before packaging, list every parent the polytonic route can touch in census_05 decisions/config, so that the sf7 ledgers can be checked for complete coverage when they arrive. Read a small sample only, or the summary route totals.
2. **Qualification, as for census_05, with polytonic in scope:**
   - the packaged regression;
   - parity 150/888, which must stay exact;
   - mocks for smoke-mode i/ii and full-mode ii.
   - **The mocks must exercise the polytonic route in scope.** Use the existing 605-row SF7 candidate ledger (polytonic / collection-v2-train, 714,568 bytes, `51dae7b4…`) or synthetic polytonic fixtures as **mock-only** stand-ins, labelled as such.
   - Show that:
     - a polytonic edit lands in final_text with tool provenance;
     - a polytonic hold HOLDs;
     - a missing in-scope result HOLDs;
     - the invariants pass, and "pending polytonic" is reported.
   - Load every bound ledger through the full CODE_SHA `ArtifactCorrector.load`. For the real sf7 ledgers, this runs in the binding step.
3. **Pending binding:** write `bind_sf7.py <ledger path> <sha256> [...]`. It:
   - verifies each remote ledger's sha and size on Clariden, read-only;
   - copies it into `$W/census_06_20261020/inputs/`, which must not already exist; never overwrite;
   - fills the config and `INPUTS.json`;
   - runs `ArtifactCorrector.load` on every record against the registered parents. Run it on Clariden, on the login node, if it is light (state its size), or say that it needs a job;
   - checks that the coverage matches the parent list from step 1;
   - rebuilds the package id and redeploys to a **new** code directory.

   VERIFY gains an `sf7-binding` check that reports `PENDING` until the binding is done and fails if any placeholder remains at submit time. The submit script refuses while pending.
4. **Deploy now (pre-binding)** to `$W/census_06_20261020/code/<id>/`:
   - read every sha back;
   - run the unchanged census_05 verifier on all four kinds. Every check except sf7-binding must be OK, and sf7-binding must be PENDING.
   - Also run the scheduler test-only checks (`sbatch --test-only`), as census05-B did.
   - Check every sbatch for `--account=a0140`, partition and time.
   - Size the census time from census_05's measured runtime, from `full-split-001` logs/summary timing, plus the polytonic ledger load. State the arithmetic.
5. **`CENSUS06.md`:**
   - the diff to census_05;
   - the tool_versions change;
   - qualification results;
   - the pending binding procedure;
   - **the exact coordinator block** (bind → smoke chain → review → full chain, afterok; readout as a sibling of the attempt, as for census_05);
   - **a flip report procedure:** after the full run, a small CPU job (or a readout extension) counts, **per parent**, the rows whose admission (ADMIT vs not, and admitted_train membership) flips between census_05 `full-split-001` and census_06 `full-split-002`, with a reason breakdown (polytonic hold / polytonic edit / other). Package this as `flip_report.py` + sbatch with tests; the coordinator submits it after the full run.

## Rules
- Touch nothing outside `docs/harvest/census06/` and this brief.
- Write a guarded commit list. Do not run `git add` or `git commit`.
- Do not write under `$W/census_05_20261020`.
- No `sbatch` except `--test-only`; no `srun`.

The last line must be exactly:
`CENSUS06: done | package <id> at <root> (pre-binding) | pipeline 0.3.3 kept_unverified (existing fixtures 0 changes) | diff vs census_05: routes_out_of_scope polytonic removed + sf7 per-row binding + tool_versions (polytonic 0.7 released) | parity 150/150 888/888 | mocks <k>/<n> invariants PASS (polytonic in scope) | VERIFY <k>/4 OK, sf7-binding PENDING | tests <n> passed | no jobs submitted`

## Lead ruling on the CENSUS06 block (20 Oct, after the first run): continue from the retained draft in `docs/harvest/census06/`
**The block:** the 0.3.3 change to `line_pipeline.py` (`9c6f8ead…` → `a78e6a83…`) changes the fingerprint of the eight tools that bind it. The numerics ledgers carry the old numerics digest `f1b5c0aa…`. This is a direct consequence of the coordinator's 0.3.3 ruling, and it is resolved **by the census_05 precedent**: census_05 regenerated the five N1 ledgers under a new numerics digest with zero status moves (segcensus `docs/harvest/census05/regenerate_n1.py`, `corrections/report.json`, HANDOFF §Corrections).

1. **New fingerprints, same versions.**
   - Regenerate `tool_versions.json` from the amended bytes. All eight digests change; their **version numbers do not** ("exact source hashes identify patches within a named generation").
   - The pipeline version is 0.3.3.
   - Cyrillic and polytonic entries must stay byte-identical: they do not bind `line_pipeline.py`. Assert it, and state the polytonic digest the sf7 per-row files must carry.
2. **Regenerate the five numerics ledgers** with census_05's `regenerate_n1.py` method, unchanged except that the active numerics digest is now the new one. Use the same producer inputs (hash-checked) and the same original producer path identities.
   - **Acceptance, exactly as census_05:** zero status moves, zero edit/hold changes, identical record membership and order for every ledger, and no content change beyond `tool_digest` (and `tool_version` if it is stamped).
   - Produce `corrections/report.json` with per-ledger transition matrices and old/new bytes + sha.
   - Load every regenerated ledger through the full 0.3.3 `ArtifactCorrector.load`.
   - Do **not** hand-restamp digests with sed or a script. Re-run the converter.
   - If any record differs beyond the digest, stop and report.
   - The five cyrillic ledgers stay bound by their census_05 shas, unchanged.
   - The regenerated ledgers are new inputs under `$W/census_06_20261020/inputs/`; the B step deploys them. Keep gz archives out of git, as census_05 did; record the archive path.
3. **Commits: split the work into CENSUS06-A (this run) and CENSUS06-B**, as census05 A/B did.
   - **This run (A)** finishes everything up to and including qualification:
     - fingerprints, ledgers, binding script, readout, flip report;
     - mocks (polytonic in scope + kept_unverified) and full tests, parity;
     - the final package file set with DEPLOY_PATHS/DEPLOY_SHA256SUMS and the package id;
     - the runtime sizing.
   - It then stops with a guarded commit list. **The lead commits.**
   - **B** (a separate brief) deploys the committed bytes, reads them back, and runs the unchanged verifier + scheduler `--test-only`.
   - Do not create temporary repositories or verifier bypasses.
   - Pre-existing unrelated tracked changes in the worktree (`greekocr/harvest/geometry_observations.py`, `row_inclusion.py`, `pyproject.toml`, `segeval1/launchers/limit_probe.log`) are not yours. Leave them alone, and state whether the verifier's dirty-path check covers only payload paths or the whole tree.

The last line for this run must be exactly:
`CENSUS06-A: READY | package <id> (<n> files, not deployed) | pipeline 0.3.3 kept_unverified (existing fixtures 0 changes) | 8 fingerprints regenerated, cyrillic+polytonic entries unchanged (polytonic digest <8>) | numerics ledgers 5 regenerated, 0 status moves | parity 150/150 888/888 | mocks <k>/<n> invariants PASS | tests <n> passed | sf7-binding PENDING | commit list <k> paths | no jobs submitted`
