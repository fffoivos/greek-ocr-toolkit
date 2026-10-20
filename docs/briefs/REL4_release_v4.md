# REL4: release v4 train = REL3 on census_06 (polytonic in scope); raw labels; sf7 edits as a separate registered overlay file (gpt-6.1-sol, medium, network ON for read-only `ssh clariden` and the final deploy `rsync` only, no spend, no jobs)

The base is REL3 (sol-recut `docs/harvest/collect_v3_admission/release_v3/`; deployed `$W/release_v3/pkg/59d2de21`; job 3704952 ok; 168,637 released, 0 edits). Read `REL3.md`, `INVENTORY.md`, `build_release_v3.py`, `verify_release_v3.py` and the tests.

`W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3`. You submit nothing.

## The coordinator's ruling (with the training lead, per the 17 Oct preregistration)
- **Release v4 keeps the RAW import label per row exactly as v3 did,** so the *add* arm stays raw.
  - Assert, for every released row, that the label equals the raw import text (`raw_text`, sha = `raw_text_sha256`).
  - **Never** export census `final_text` as the label.
- **What changes between v3 and v4 is the ROW SET:** census_06 admission with polytonic in scope. The CENSUS06 brief runs in parallel; its output does not exist yet.
  - Inputs bind `$W/census_06_20261020/attempts/full-split-002/` (CURRENT/summary/admitted_train/admission_records) and its sibling readout. They are **pending** until that run exists.
  - The census_06 schema is the census_05 schema (same code). Test against census_05 rows/fixtures, plus synthetic polytonic edits/holds.
- **sf7's edits go into a separate edits-only file, `release_v4_sf7_edits.jsonl`.**
  - Schema: the one the add_corr overlay reads: `{row_id, parent_id, old text, new text, tool version sha, evidence}`.
  - **Use the exact field names and semantics of the overlay reader.** Find it read-only in `~/Projects/greek-page-ocr-e4w2/bench/e4_wave2_r3.py` (and `e4_wave2.py`, tests `tests/test_e4_wave2_r3.py`; grep `add_corr`), and cite the lines.
  - Content: the REL4 rows where the census_06 polytonic route applied an edit.
    - Old text = the raw label.
    - New text = raw with **only the polytonic edits** applied, at the census's raw-codepoint spans.
    - Evidence = the route record and the sf7 ledger sha/record reference.
  - Cross-check every entry against its sf7 ledger record.
  - If the overlay schema cannot express this, stop and report.
- **`corrections_registry.json`:** sf7 is registered as **released** (ledger shas, file sha, keying, touch counts) beside `ru1_v3_edits` and `n1_v1_w1`. **All three are "registered, not applied"** and are used only by the add_corr overlay.
  - Report each one's touch counts on the v4 rows: changed rows, and rows with any record.
- **Other census-internal edits** on v4 rows (cyrillic / numerics / composer normalisation) also stay out of the label.
  - List them in `release_v4_edits.jsonl` in REL3's edits-only form, with provenance, and report the counts (REL3 had 0).
- **The sf7 ledger shas are pending** (the coordinator sends them). The registry carries a pending placeholder, VERIFY reports `sf7 PENDING`, and the submit refuses while it is pending.

## Unchanged from REL3
- The same exclusions and counts:
  1. dev/test editions (SPLIT2): assert 0;
  2. benchmark keys: assert 0;
  3. exact-pixel duplicates of benchmark rows: drop and count;
  4. a missing byte-exact CROPS4 crop: drop and count.
- **The exposure assertions are the same as REL3's, now against the sealed benchmark seal04:**
  - `$W/benchmark_0.2/seal04/benchmark_v02_{test,dev}.jsonl`, suite `9447f09c…`; key and crop-sha;
  - also keep REL3's candidates_v3/readout checks.
- The same fields, receipts, VERIFY modes, sbatch form (`--account=a0140`, normal partition, sized time) and `$W/venv_l1/bin/python`.

## New in REL4
- **Flips v3 → v4, per parent and source:**
  - added rows (in v4, not v3) and removed rows (in v3, not v4), each with the census_06 decision reason (polytonic hold / polytonic edit / other);
  - bind the REL3 output (`$W/release_v3/<attempt>/release_v3_admission.jsonl` and its receipt sha) as an input.
- **Crop coverage:** CROPS4 only cropped census_05-era selections. Count the **newly admitted rows with no CROPS4 crop** separately (`missing_crop_new_admits`, per parent). They are still dropped under rule 4, but REL4.md must flag any non-zero count as needing a CROPS4 top-up before the release is used.
- **The wave-2 admission gate** needs the census_06 generation files (CURRENT/summary/admission_records/admitted_train) and the v4 receipt. Make `RELEASE_V4_RECEIPT.json` bind those by sha, with the release outputs.

## Package
- `docs/harvest/collect_v3_admission/release_v4/`, deployed to the new `$W/release_v4/pkg/<sha8>/` with every sha read back.
- VERIFY package must pass. The inputs mode reports census_06 and sf7 as PENDING and everything else ok.
- Tests:
  - every REL3 test, ported;
  - label == raw even when the census final_text differs;
  - the sf7 overlay file round-trips through the overlay reader's parsing logic (imported unchanged if side-effect free, otherwise replicated with cited lines);
  - non-sf7 census edits are excluded from the sf7 file;
  - flip counts;
  - missing_crop_new_admits;
  - the seal04 exposure assertions;
  - a pending binding refuses to submit.
- `REL4.md`: the ruling as implemented, the overlay schema citation, the exclusion design, **the exact coordinator command block** (after census_06 full + sf7 binding), and what is pending.
- Touch nothing outside `release_v4/` and this brief; `release_v3/` stays as it is.
- Write a guarded commit list. Do not run `git add` or `git commit`.

The last line must be exactly:
`REL4: done | package <root> VERIFY package ok | inputs <k>/<n> (pending census_06, sf7) | labels raw (asserted) | sf7 overlay file schema = <reader file:lines> | registry <m> versions (sf7 released, ru1_v3_edits, n1_v1_w1 registered-not-applied) | tests <n> passed | no jobs submitted`
