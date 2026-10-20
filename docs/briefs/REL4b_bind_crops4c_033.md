# REL4b: REL4 bound to the CROPS4C full receipt, pipeline 0.3.3 and regenerated digests; kept_unverified counts; overlay applied-only (gpt-6.1-sol, medium, network ON for read-only `ssh clariden` and the final deploy `rsync` only, no spend, no jobs)

The base is REL4: commits be85e348f, 0378caf7d and 90b55e49b; `docs/harvest/collect_v3_admission/release_v4/`; deployed `$W/release_v4/pkg/22c3e0ba`. The coordinator accepted it pre-binding and approved this plan. `W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`.

## Facts (lead)
- **census_06 = CENSUS06-A**, commit cf1db4dd4, package `de597753a70a5d6d` (pre-sf7-binding; the final code id changes after the binding).
  - Read `docs/harvest/census06/CENSUS06.md`, `fingerprints.json`, `package/.../tool_versions.json` and `pipeline_033.patch`.
  - **Pipeline 0.3.3** adds the line-tool-result status `kept_unverified` (polytonic only).
  - Evidence carries `kept_unverified: true` and a `reason`; there are no edits. The row is admitted with no polytonic change to the text.
  - 8 tool digests changed (numerics, dashes, content_gate, content_repair, composer, final_eligibility, census, inventory); cyrillic and polytonic did not (polytonic `de1a9a8b…`).
- **CROPS4C** (commit ca949ca31, package `$W/crops4_package/9a3b80c1`).
  - Read `docs/harvest/collect_v3_admission/CROPS4C_RECEIPT.md` §"REL4 binding handoff": the fields and checks REL4 must bind.
  - Attempts: `crops4_c06_smoke_01` and `crops4_c06_full_01` under `$W/crops4_attempts/`. Neither exists yet: **pending**.

## Do
1. **Bind the CROPS4C full receipt** as a required pending input, applying all the checks in that handoff section:
   - status ok, mode full, `context.tranche=all`, `include_heldout=true`;
   - `sha256check_exit=0`, mismatches = failures = 0;
   - byte_exact = selected = written + skipped_valid;
   - per_tranche reconciles with the aggregates;
   - context bound to the census_06 inputs (CURRENT, summary, admitted_train, decisions, evaluation_diagnostics shas).

   REL4's crop rule then uses the union of the CROPS4 c05 manifests and the c06 manifest. Every released row must be byte-exact in one of them, and REL4 still hashes each crop itself.
   - `missing_crop_new_admits` stays as a count; it must be 0 for a release that is ok.
   - Bind the c06 smoke receipt too.
2. **Expect pipeline 0.3.3:**
   - every census_06 decision's `pipeline_version` must equal 0.3.3;
   - the tool-digest pins come from the census_06 `tool_versions.json`, bound at bind time from the final code id;
   - census_05 pins are kept only for the v3 baseline comparison.
3. **kept_unverified accounting:**
   - count the released rows whose polytonic route status is `kept_unverified`, per parent and per class, and the same for `applied` and `verified_no_change`;
   - assert that their exported label equals raw. This is already universal; test it specifically.
4. **The sf7 overlay holds applied rows only:**
   - `release_v4_sf7_edits.jsonl` contains only rows whose polytonic route status is `applied` with non-empty edits;
   - `kept_unverified`, `verified_no_change` and unresolved rows never appear.
   - Test each status.
5. **Tests:** every REL4 test, plus the new ones above (a CROPS4C receipt failing each check; a union crop lookup; a new admit covered by c06; kept_unverified counted and kept out of the overlay; a decision with pipeline 0.3.2 rejected).
   - **Delete your own pytest basetemp after a passing run, keeping only tests.log/tests.xml** (coordinator rule).
   - Delete nothing else.
6. Redeploy to a **new** `$W/release_v4/pkg/<sha8>/`, leaving 22c3e0ba as it is, and read every sha back. Run VERIFY package, which must pass; the inputs mode reports census_06, sf7 and CROPS4C as PENDING.
   - Update `REL4.md` with a REL4b section and **the exact coordinator block**: after census_06 full + readout and CROPS4C full, the bind step, then the REL4 job.
   - Also add **the hand-off list for the wave-2/S1 lead** (the paths + shas they need as arguments):
     - the release v4 admission;
     - corrections_registry + release_v4_sf7_edits;
     - the census_06 CURRENT/summary/admission_records/admitted_train;
     - the v4 receipt.

Write a guarded commit list. Do not run `git add` or `git commit`. Touch nothing outside `release_v4/` and this brief.

The last line must be exactly:
`REL4b: done | package <root> VERIFY package ok | inputs <k>/<n> (pending census_06, sf7, crops4c) | pipeline 0.3.3 expected | kept_unverified counted, overlay applied-only | tests <n> passed | basetemp deleted | no jobs submitted`
