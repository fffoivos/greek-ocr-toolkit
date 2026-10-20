# ADM3 release-v3 candidate admission

Appended 1,626 screened CAPS3 headings_caps rows: 1,623 masked and 3 guarded_original. All carry `arm = "release-v3-candidate"`, `marks_status = "pending_opus"`, `provenance.sol_reading = "sol/recut-v1 abaa200c"`, CAPS3 build evidence, and bound clip-screen provenance. This is a candidate admission, with marks awaiting Opus.

The difference from 1,629 is **-3**. Two masked rows are excluded by the current `n1_locked_eval` class:

- `gazette_modern--92f4546f78f59945--s000-l0066`
- `gazette_modern--ccdcaa21e55ecf01--s000-l0008`

One additional masked row has `screen_merged = true` in W1 features:

- `gazette_modern--e67886c84188a19a--s000-l0012`

A second W1-features screen_merged row, `lekythos--ff539dec2e1680a7--s000-l0071`, is already unmatched_original. The disjoint selection accounting is 2,211 pool rows minus 544 edge-screen flags, 2 release exclusions, 2 merged-screen flags, and 37 remaining unmatched originals = 1,626. Equivalently, 2,211 - 544 - 38 unmatched - 3 additional masked exclusions = 1,626. Every dropped ID is recorded in the summary.

The 16,562 wave-1d rows and existing 462 kosmopolis/poly1850 candidate rows remain byte-identical. Their SHA256 values are:

- wave-1d: `e16f824c3349f6fa20c4e693964d020096306ebab210c8799020f63b0bdf2b5d`
- kosmopolis/poly1850: `8703ddec7b7c14370f428dd8d9f9cdf8a63c18d3bb45d483661841c30dc5dd5a`

Final admission SHA256: `d9343b74c4eeb61b592257f25f63f9b624e7a83d3ddcb3971d8951998253d064` (18,650 rows).

The preserved literal wave arm is `wave-1d only`; exact `wave-1d` still selects zero. Filters give 16,562 legacy wave rows, 462 candidate poly1850 rows, and 1,626 candidate headings_caps rows. Total release-v3-candidate rows: 2,088. Counts by arm × source × class are in the summary. Headings_caps per source: bsb_poly1850 27, elstat 1, gazette_modern 1,329, ia_greek_latin 5, ia_poly1850 36, kosmopolis 51, lekythos 161, nlg 16.

Clip helper: `greekocr.verify.images.image_checks; greekocr.verify.calibration._predict + RULES[cut_left/cut_right]`. Tolerance: left_fraction > 0.0 or right_fraction > 0.0. Screen removals total 544: bsb_poly1850 19, elstat 0, gazette_modern 433, ia_greek_latin 1, ia_poly1850 25, kosmopolis 12, lekythos 38, nlg 16. CAPS2 validation: 6/6 clipped flagged; 17/89 crop-ok false positives. The summary binds helper source files, receipt, screen, records, W1 inputs, and every current exclusion class, including n1_locked_eval. CAPS3 and CAPS4 files are verified against local commits d8c31c97 and abaa200c. CAPS4 letters 100/100, crop_ok 99/100, marks 98/100 pending Opus are recorded without further adjudication.

Collector metadata comes from crop_tight_page where present (1,546 admissions), otherwise features (80 admissions). Every original_crop_sha256 matches that collector row, and every selected crop on disk matches the correct masked/original output hash. Both W1 files are bound and checked for merged-screen flags. The summary preserves historical wave counts and ADM2 evidence while updating current file and exclusion bindings.

Reproduce offline, with bytecode writes disabled:

```sh
python3 -B docs/records/harvest/collect_v3/release_admissions/append_adm3_headings_caps.py --check-only
python3 -B -m unittest discover -s docs/records/harvest/collect_v3/release_admissions -p test_adm3_headings_caps.py -v
```

`adm3_tests.log` records 12 passing ADM3 tests, covering frozen subsets, exact selection, arm/class filters, row metadata, every crop hash, exclusions, screen evidence, summary bindings, and rejection of bad hashes or unexpected admissions. Historical ADM2 scripts/tests/manifests remain unchanged as their original snapshot evidence; ADM3 has its own verification and bound manifest. No network, collector imports, staging, or commit. All writes are confined to this release_admissions directory.
