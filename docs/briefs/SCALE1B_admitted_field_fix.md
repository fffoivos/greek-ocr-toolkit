# SCALE1B: fix the tags job's admission check against real rows; test on real samples; redeploy (gpt-6.1-sol, medium, network ON for `ssh clariden`/`rsync` only, no spend, no jobs)

**Failure:** tags job 3705047 failed after 13 s, at `scaling_w3/scale.py:81` (`census_row`): `require(r.get('admitted') is True and d.get('admitted') is True and d['disposition']=='ADMIT','non-admitted train row')`.

**Diagnosis (lead, read-only, verified on the first 30,000 rows of the real admitted_train):**
- `row['admitted']` is the **collector's legacy admission flag** from the features file. It is False on 20,525 of those 30,000 rows; the first such row is #20, `bsb_poly1850--027215cc6d2a7e8a--s000-l0025`, with `rejection_reasons: ['short_line']`.
- The census verdict is `decision.admitted` (True) and `decision.disposition` (`ADMIT`) on every row.
- REL3 (`release_v3/build_release_v3.py:217`) checks only the decision fields, which is why it read the same file without error.

## Do
1. **The fix:** in `census_row`, drop the `r.get('admitted')` condition and keep `d.get('admitted') is True and d['disposition']=='ADMIT'`. Change nothing else, unless step 2 proves another real-row assumption wrong. If so, fix it the same minimal way and list each change with its witness row.
2. **Real-sample test (the synthetic fixture missed this).** Read real rows from Clariden, read-only and light on the login node:
   - 1,000 rows from the head of `$W/census_05_20261020/attempts/full-split-001/current/admitted_train.jsonl`;
   - 1,000 complete rows from the middle (e.g. `tail -c +<offset>`, dropping the first partial line);
   - 1,000 from the tail;
   - make sure the sample includes **both W1, W2 and collection-v2-train rows**. Report the per-parent counts. If a parent is missing from all three windows, find a window that contains it.
3. **Run the real tag path end to end on those rows:** `census_row` → `slim` → classifier → the tag record. Run it on Clariden with `$W/venv_l1/bin/python` from the deployed package, or locally on a fetched copy kept outside git (about 3,000 rows is fine).
   - It must pass with no exceptions.
   - Report per-parent primary-class counts and field availability, to show that `unavailable` appears where expected, e.g. bbox fields for v_c rows.
   - Add a test that runs the same path on a small committed real excerpt: 20 rows per parent, label text included. This is our own data, so it is allowed.
4. Check the same assumption class in the subset-job code: any use of `row['admitted']` or other collector-layer fields as census truth. Fix it the same way and say so.
5. Re-run all tests. Regenerate the manifests. Deploy to a **new** `$W/scaling_w3/data_pkg/<sha8>/`, leaving `d14521ee` as it is, and read every sha back. Run `VERIFY.sh package` and `VERIFY.sh inputs-tags` there.
6. Update `SCALE1.md`:
   - a SCALE1B section with the fix and its witness;
   - the real-sample results;
   - **the exact three-line coordinator block** with the new root (VERIFY package; VERIFY inputs-tags; submit_tags), plus the subsets follow-up lines.
   - The previous failed attempt `scale1-c05-001` may have left a directory. Check read-only whether `$W/scaling_w3/tags/scale1-c05-001` exists. If it does, the new attempt name must differ (use `scale1-c05-002`). Do not delete anything.

Write a guarded commit list. Do not run `git add` or `git commit`.

The last line must be exactly:
`SCALE1B: done | fix census_row admitted=decision only | real sample <n> rows (W1 <a>, W2 <b>, v_c <c>) pass | package <root> VERIFY package ok inputs-tags <k>/<n> | tests <n> passed | no jobs submitted`
