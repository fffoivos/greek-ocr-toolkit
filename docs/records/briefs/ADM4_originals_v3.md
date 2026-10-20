# ADM4: release-v3 admission on ORIGINAL crops (gpt-6.1-sol, medium, network OFF, no reading, no spend)

**Owner decision (17 Oct, evening, via the coordinator):** "forget the crop correction". Admission DROPS only:
- crops containing two or more complete lines (`screen_merged`);
- rotated crops (`rotated_crop`).

**Everything else is acceptable, overruns included.** Apply no other crop screen; in particular, the CAPS3 edge-clip screen is **not** applied here.

Write only under `docs/records/harvest/collect_v3/` (release_admissions, ledger). A live W2 imports `collect_v3/`: never touch it. The run root is read-only.

## 1. New file `release_admissions/w1_originals_v3.jsonl`
- **Every W1 row** (`~/Projects/collect-v3-data/run/W1/features.jsonl`) with `candidate_usable == true` in these strata:
  - **c1_pass strata:** bsb_poly1850 poly1850; ia_poly1850 poly1850; nlg poly1850, poly1900, greek_poly; serbia cyrillic; elstat numerics_tables.
  - **masked-qualified strata:**
    - gazette_modern modern_scanned, gazette_stratum `measured_1986_1990` only (the probe stratum failed letters);
    - kosmopolis poly1900;
    - lekythos poly1900;
    - kosmopolis poly1850 (SRK/KR);
    - headings_caps across sources (CAPS4).
  - Not included: ia_poly1850 mixed_greek_latin (c1_pending), ia_russian (c1_fail), every latin stratum, and everything unchecked.
- **On the ORIGINAL crop:** collector crop_bbox and crop_sha256; no masking.
- **Removals, reported per screen and per source × class:**
  - `screen_merged == true`;
  - `rotated_crop` (`release_exclusions/w1_rotated_crop_ids.txt`);
  - every registered line-level class in `release_exclusions/release_exclusions.json`: locked_eval, eval_only_dev, locked_eval_ia/ib_wikisource, separator_ambiguous, n1_locked_eval, mirrored_showthrough, lqb_truth_v1, lqb_truth_v1_1. Do **not** remove the 11 `lqb_truth_v1_wave1d_in_sample_ids` (they are not a class).
- **Row fields:** row_id, source, primary_class, gazette_stratum, page_id, line_index, label (the W1 post-convention `label`, unchanged), crop_bbox, crop_sha256, `arm = "release-v3"`, `crop = "original"`, `marks_status` (`pending_opus` for the strata whose marks were Sol-read: kosmopolis poly1850, headings_caps; `recorded` otherwise), and provenance (the stratum's evidence commit).
- **Summary** `w1_originals_v3_summary.json`: counts per source × class, removals per screen, the input shas (features, exclusions, unchecked_strata), and the owner rule text.

## 2. `w1_masked_1d.jsonl` stays unchanged as the record of the 1d measurement
In `w1_masked_1d_summary.json`, add `superseded_for_admission_by: "w1_originals_v3.jsonl"` and the owner rule. Do not change the jsonl itself.

## 3. Ledger
In `WEAK_CATEGORY_LEDGER.md` and `weak_ledger/ledger.json`, add a note to the crop_ok column/notes: the owner rule is that admission drops only merged and rotated crops, and overruns are acceptable, so the 53–82% original-crop crop_ok rates (gazette, kosmopolis, lekythos, caps) are **not** admission blockers. Recompute the "collected" counts for those categories from w1_originals_v3, and keep the old numbers in a history note.

## Tests
- every included row is candidate_usable in an included stratum;
- no row is in a removal set;
- the counts reconcile (pool − removals = rows);
- every crop_sha256 equals the W1 feature row's;
- the masked file is unchanged.

Leave a guarded commit list. The last line must be exactly:
`ADM4: done | rows: <n> | per stratum: <short> | removed screen_merged <a>, rotated <b>, classes <c> | file sha: <sha> | masked file unchanged`
