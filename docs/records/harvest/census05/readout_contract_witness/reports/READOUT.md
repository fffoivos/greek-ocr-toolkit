1 rows; ADMIT 1 / HOLD 0 / DROP 0; admitted_train 1; gate exclusions 0; invariants FAIL (13/14).

Published generation: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/readout_contract_witness/attempt/generations/g1-61c96b5c21bb4b77a4fbe83e78622683`. Counts use exported dispositions and reasons only. Foreign-script gate reason is `unexpected_script` (the code name). Class is the ledger role, exactly summary.by_stratum.role; script is retained in by_stratum. all_reasons includes distinct reason names/strings from decisions, stages and routes, once per row; all_disposition_reasons contains only final disposition reasons. Held-out protection checks training admissions; dev/test ADMIT rows are evaluation passes. The protected crop list is the writer’s registered dev/test crops; protected editions are policy entries plus registered non-train editions. Root ledger is immutable input provenance, never a verdict source. Only compact identity indexes are retained in memory; JSONL payloads are streamed. Stage attribution uses serialized stages first, then known finish() call sites; missing producers are explicitly labeled. Failure counts in invariants are zero on PASS.

### Totals

Counted from: `decisions.jsonl`.

| disposition | rows |
| --- | --- |
| ADMIT | 1 |

### Disposition reason occurrences

Counted from: `decisions.jsonl`.

(zero rows)

### Route statuses

Counted from: `decisions.jsonl`.

| value | rows |
| --- | --- |
| content_repair:not_applicable | 1 |
| cyrillic:not_applicable | 1 |
| dashes:not_applicable | 1 |
| numerics:verified_no_change | 1 |
| polytonic:not_applicable | 1 |

### Segmentation availability

Counted from: `decisions.jsonl`.

| value | rows |
| --- | --- |
| measured | 1 |

### Gate totals

Counted from: `decisions.jsonl`.

(zero rows)

### V3 splits

Counted from: `decisions.jsonl`.

| value | rows |
| --- | --- |
| dev | 0 |
| test | 0 |
| train | 0 |
| unassigned | 0 |

### Pending totals

Counted from: `pending_<tool>.jsonl`.

| value | rows |
| --- | --- |
| content_repair | 0 |
| cyrillic | 0 |
| numerics | 0 |
| polytonic | 0 |

### Pipeline versions

Counted from: `decisions.jsonl`.

| value | rows |
| --- | --- |
| 0.3.2 | 1 |

### Admission export

Counted from: `admitted_train.jsonl`.

| rows |
| --- |
| 1 |

### Completeness

Counted from: `decisions.jsonl`, ledger binding.

| rows | input_rows | complete |
| --- | --- | --- |
| 1 | 1 | True |

### Invariants

Counted from: `decisions.jsonl`, `admitted_train.jsonl`, `summary.json`, ledger inventory.

| invariant | status | count |
| --- | --- | --- |
| admitted_train_violations | PASS | 0 |
| bound_inventory_counts | PASS | 0 |
| dispositions_sum | PASS | 0 |
| duplicates | PASS | 0 |
| expect_rows | PASS | 0 |
| gate_route_violations | PASS | 0 |
| gate_segmentation_violations | PASS | 0 |
| heldout_leaks | PASS | 0 |
| missing_rows | PASS | 0 |
| no_reason | PASS | 0 |
| pipeline_version_mismatch | FAIL | 1 |
| summary_by_stratum | PASS | 0 |
| summary_dispositions | PASS | 0 |
| unexpected_rows | PASS | 0 |

### all_reasons

Counted from: `decisions.jsonl` + ledger inventory.

| reason | parent | split | disposition | rows |
| --- | --- | --- | --- | --- |
| frozen fixture | parent | train | ADMIT | 1 |

### all_reasons_totals

Counted from: `decisions.jsonl` + ledger inventory.

| reason | disposition | rows |
| --- | --- | --- |
| frozen fixture | ADMIT | 1 |

### by_stratum

Counted from: `decisions.jsonl` + ledger inventory.

| parent | split | source | role | script | disposition | rows |
| --- | --- | --- | --- | --- | --- | --- |
| parent | train | bsb_poly1850 | numerics_tables | nonletter | ADMIT | 1 |

### class

Counted from: `decisions.jsonl` + ledger inventory.

| role | parent | split | disposition | rows |
| --- | --- | --- | --- | --- |
| numerics_tables | parent | train | ADMIT | 1 |

### class_rates

Counted from: `decisions.jsonl` + ledger inventory.

| role | parent | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- | --- |
| numerics_tables | parent | train | 1 | 1 | 1.0 |

### class_totals

Counted from: `decisions.jsonl` + ledger inventory.

| role | split | disposition | rows |
| --- | --- | --- | --- |
| numerics_tables | train | ADMIT | 1 |

### class_totals_rates

Counted from: `decisions.jsonl` + ledger inventory.

| role | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- |
| numerics_tables | train | 1 | 1 | 1.0 |

### deciding_reasons_totals

Counted from: `decisions.jsonl` + ledger inventory.

(zero rows)

### decisions_by_parent_split

Counted from: `decisions.jsonl` + ledger inventory.

| parent | split | disposition | rows |
| --- | --- | --- | --- |
| parent | train | ADMIT | 1 |

### gate_by_class

Counted from: `decisions.jsonl` + ledger inventory.

(zero rows)

### gate_by_parent

Counted from: `decisions.jsonl` + ledger inventory.

(zero rows)

### gate_by_source

Counted from: `decisions.jsonl` + ledger inventory.

(zero rows)

### input_rows

Counted from: `ledger.sqlite` binding/observations.

| parent | rows | registered |
| --- | --- | --- |
| parent | 1 | 1 |

### input_splits

Counted from: `ledger.sqlite` binding/observations.

| parent | split | rows |
| --- | --- | --- |
| parent | train | 1 |

### issue_counts

Counted from: `decisions.jsonl` + ledger inventory.

| issue | parent | rows |
| --- | --- | --- |
| pipeline_version_mismatch | parent | 1 |

### segmentation_reasons

Counted from: `decisions.jsonl` + ledger inventory.

| reason | verdict | parent | split | disposition | rows |
| --- | --- | --- | --- | --- | --- |
| frozen fixture | KEEP | parent | train | ADMIT | 1 |

### segmentation_reasons_totals

Counted from: `decisions.jsonl` + ledger inventory.

| reason | verdict | disposition | rows |
| --- | --- | --- | --- |
| frozen fixture | KEEP | ADMIT | 1 |

### source

Counted from: `decisions.jsonl` + ledger inventory.

| source | parent | split | disposition | rows |
| --- | --- | --- | --- | --- |
| bsb_poly1850 | parent | train | ADMIT | 1 |

### source_class

Counted from: `decisions.jsonl` + ledger inventory.

| source | role | parent | split | disposition | rows |
| --- | --- | --- | --- | --- | --- |
| bsb_poly1850 | numerics_tables | parent | train | ADMIT | 1 |

### source_class_rates

Counted from: `decisions.jsonl` + ledger inventory.

| source | role | parent | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- | --- | --- |
| bsb_poly1850 | numerics_tables | parent | train | 1 | 1 | 1.0 |

### source_class_totals

Counted from: `decisions.jsonl` + ledger inventory.

| source | role | split | disposition | rows |
| --- | --- | --- | --- | --- |
| bsb_poly1850 | numerics_tables | train | ADMIT | 1 |

### source_class_totals_rates

Counted from: `decisions.jsonl` + ledger inventory.

| source | role | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- | --- |
| bsb_poly1850 | numerics_tables | train | 1 | 1 | 1.0 |

### source_rates

Counted from: `decisions.jsonl` + ledger inventory.

| source | parent | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- | --- |
| bsb_poly1850 | parent | train | 1 | 1 | 1.0 |

### source_totals

Counted from: `decisions.jsonl` + ledger inventory.

| source | split | disposition | rows |
| --- | --- | --- | --- |
| bsb_poly1850 | train | ADMIT | 1 |

### source_totals_rates

Counted from: `decisions.jsonl` + ledger inventory.

| source | split | rows | admitted | admit_rate |
| --- | --- | --- | --- | --- |
| bsb_poly1850 | train | 1 | 1 | 1.0 |

### toolchain_versions

Counted from: `decisions.jsonl` + ledger inventory.

| tool | version | rows |
| --- | --- | --- |
| census | 0.7 | 1 |
| composer | 0.3 | 1 |
| content_gate | 0.3 | 1 |
| content_repair | 0.2 | 1 |
| cyrillic | 0.3 | 1 |
| dashes | 0.1 | 1 |
| final_eligibility | 0.3 | 1 |
| inventory | 0.1 | 1 |
| numerics | 0.3 | 1 |
| polytonic | 0.7 | 1 |
| segmentation | 0.13 | 1 |

### Timing

Counted from: readout process wall clock.

| elapsed_seconds |
| --- |
| 0.002414226531982422 |

### Tool version binding

Counted from: `ledger.sqlite` run binding.

| path | sha256 | tools |
| --- | --- | --- |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/package/projects/greek-ocr-toolkit-pipe032/docs/harvest/line_pipeline/tool_versions.json | ed81e3a1b7389c3dd4d29706e5e2ff2b6d0d34fa0648a9587388a25be2725831 | {'polytonic': {'version': '0.7', 'documented_iterations': ['S1', 'S2', 'S3', 'S4', 'S5', 'SF6', 'SF7'], 'iteration_count': 7, 'scope': 'SF7 A; existing detector/readers; exact release candidate_pre_audit', 'components': {'greek-ocr-toolkit-spellcheck/scripts/labelfix/release_gate_sf7.py': '2f7a777a91adae1af5238a9f2092c59326fc6cc7d83d6ad3bf115866455ec208'}, 'digest': 'de1a9a8bc6b0598f5b28ac213faa13ce00ced95aa2754291fc183373f60c60c5'}, 'cyrillic': {'version': '0.3', 'documented_iterations': ['ru1_v1', 'ru1_v2_train', 'ru1_v3_edits'], 'iteration_count': 3, 'scope': 'historical Russian ь→ъ only', 'components': {'greek-ocr-toolkit-secondary/scripts/secondary/ru1_decide.py': 'cc50121e27e90cb4555e0cb98f8ad091f5a4e00c7a410c553ae9d0c7b373d41a', 'greek-ocr-toolkit-secondary/artifacts/ru1/ru1_v3_edits.jsonl': '4f1a51f5eb80788fb1cdc7a01220c90df028e79711cf0eeec2d0ace2ee42d1d0'}, 'digest': 'f63e1ba8696adb47dfc07b283c615fe83deb3f1d2fd28acbf0300de495235123'}, 'numerics': {'version': '0.3', 'documented_iterations': ['N1 automatic ink candidate (rejected 0/5)', 'N1 assisted two-reader and lead-pixel release', 'census_03 integration: digit/separator/digit adjacency for automatic candidate negatives'], 'iteration_count': 3, 'scope': 'assisted separator corrections; failed automatic candidate is disabled', 'components': {'greek-ocr-toolkit-secondary/artifacts/n1/n1_v1_w1.jsonl': '94fb67c1aab9f2ec3bf5d47bc36508b7e700508cd27391f70ebfc26f8d73230e', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline.py': '9c6f8ead156429011d03384e50b37d899bea5ba34df7e807fc1682b1f01bfa68'}, 'digest': 'f1b5c0aa990b76dac5f757af9fdf16bc0374dc3fc1dd98f64979c021b5bed2b9'}, 'dashes': {'version': '0.1', 'documented_iterations': ['dash tags; no general repair release'], 'iteration_count': 1, 'scope': 'tag only', 'components': {'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline.py': '9c6f8ead156429011d03384e50b37d899bea5ba34df7e807fc1682b1f01bfa68'}, 'digest': 'a3c42b877f00e3798909213e43ef5f2f0682571b1fa04a33b284aa198ebef2fb'}, 'segmentation': {'version': '0.13', 'documented_iterations': ['29fa466 crop guides', '5d664bf font normalized', 'cad8709 target-box normalization', 'b2f8d95 whole-word tolerance', '405d4f1 padding 1.5 heights', '0.5 + row-frame text box', 'crop-only line inventory and cut-off gate before length', "owner's three rules; remove target-cut veto and taller-than-upright guard", 'every letter body >=95% visible for a whole neighbour word', 'every h > w crop turns 90 degrees right before all detection and measurement', 'main-row ink measured along its existing base curve', 'small segments use every ink component in the processed crop frame', "length band 0.30–2.00 (coordinator decision under the owner's end-to-end mandate, 19 Oct 21:34; fitted on owner marks, s5)"], 'iteration_count': 13, 'scope': '0.9-s5: one length band 0.30–2.00 for all rows; S4 measurement, small path, mode 2, padding 1.5 and gate unchanged', 'components': {'greek-ocr-toolkit-pipe032/greekocr/glyphs/components.py': 'ffe88b72ae758f49610a0ea0d14b799c147821a899a30abdfb61cf8734be7831', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_native.py': 'e7dbe6c47061529953102b1af93422b593460e7510b22e27dbde69bcfbf052b7', 'greek-ocr-toolkit-pipe032/greekocr/harvest/filtering_assets/segmentation-policy.js': '5888fe704e6170b51081d6fa4200a725d2b29f0c70301f238faf7b32088b5b99', 'greek-ocr-toolkit-pipe032/greekocr/harvest/filtering_assets/crop-tools.py': '0adb60b62bebdb910dfa8cbba56eb64ae0325fe8f14290b4c72dbea866913b97', 'greek-ocr-toolkit-pipe032/greekocr/harvest/filtering_assets/font-models.json': 'fb3f28f7d90c2b638bfe9c72ab42dcf060d59939a7ab410fc2e1cf6d898965de', 'greek-ocr-toolkit-pipe032/greekocr/harvest/filtering_assets/service.mjs': '8a222c1c50550f9ade8250fc3de1e2972e56dae0ce3e6ab915caa0052161b32f', 'greek-ocr-toolkit-pipe032/greekocr/harvest/filtering_assets/collector/collect_v3/vendor/geometry/ownership.py': '1dd618bc2d884cf2490498456653f49b0276944f3bde83d38e26e633031eb641', 'greek-ocr-toolkit-pipe032/greekocr/harvest/filtering_assets/collector/collect_v3/vendor/geometry/magnitude.py': '038bd46af4535e6de6af58e11c4b7496e03e0434094cc8cd6b48668e2199ad77'}, 'digest': '86c85a6f1d9eb8e7b8327d0e84a77f58403fa9259c0743e5421b995abe46c1a6', 'label': '0.9-s5'}, 'content_gate': {'version': '0.3', 'documented_iterations': ['first integrated graph implementation', 'Astra review: composed coverage, producer binding and atomic exports', 'owner gate: mixed-script word drops, unexpected script holds, before segmentation; short ordinary lines excluded before segmentation (letters); cells and numeric lines exempt with more than one letter-or-digit'], 'iteration_count': 3, 'scope': 'existing toolkit primitives with new orchestration', 'components': {'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline.py': '9c6f8ead156429011d03384e50b37d899bea5ba34df7e807fc1682b1f01bfa68', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_census.py': '27fc81b380de5fc60c4edf2110571c8ede38bedc120f9cec1ad15aa33924aad8'}, 'digest': '244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20'}, 'content_repair': {'version': '0.2', 'documented_iterations': ['first integrated graph implementation', 'Astra review: composed coverage, producer binding and atomic exports'], 'iteration_count': 2, 'scope': 'evidence-backed external repair interface; missing evidence holds', 'components': {'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline.py': '9c6f8ead156429011d03384e50b37d899bea5ba34df7e807fc1682b1f01bfa68', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_census.py': '27fc81b380de5fc60c4edf2110571c8ede38bedc120f9cec1ad15aa33924aad8'}, 'digest': '244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20'}, 'composer': {'version': '0.3', 'documented_iterations': ['first integrated graph implementation', 'Astra review: composed coverage, producer binding and atomic exports', 'PIPE032: declared routes_out_of_scope bypass correction lookup and automatic results; retain explicit non-success route evidence'], 'iteration_count': 3, 'scope': 'existing toolkit primitives with new orchestration', 'components': {'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline.py': '9c6f8ead156429011d03384e50b37d899bea5ba34df7e807fc1682b1f01bfa68', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_census.py': '27fc81b380de5fc60c4edf2110571c8ede38bedc120f9cec1ad15aa33924aad8'}, 'digest': '244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20'}, 'final_eligibility': {'version': '0.3', 'documented_iterations': ['first integrated graph implementation', 'Astra review: composed coverage, producer binding and atomic exports', 'cells: alnum > 1 is the only length/shape check, consistent with the gate'], 'iteration_count': 3, 'scope': 'existing toolkit primitives with new orchestration', 'components': {'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline.py': '9c6f8ead156429011d03384e50b37d899bea5ba34df7e807fc1682b1f01bfa68', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_census.py': '27fc81b380de5fc60c4edf2110571c8ede38bedc120f9cec1ad15aa33924aad8'}, 'digest': '244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20'}, 'census': {'version': '0.7', 'documented_iterations': ['first integrated graph implementation', 'Astra review: composed coverage, producer binding and atomic exports', 'bounded parallel native workers for CSCS', 'profiled CSCS throughput tuning with bounded queue lookahead and node-scale worker qualification', 'parent-confirmed collection-v2 legacy evaluation split aliases with retained lineage', 'census_03 integration: union configured heldout_crop_sha256 with observed held-out crops', 'PIPE032: bind release correction scope; export corrections_not_applied and count routed rows by tool and disposition'], 'iteration_count': 7, 'scope': 'existing toolkit primitives with new orchestration', 'components': {'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline.py': '9c6f8ead156429011d03384e50b37d899bea5ba34df7e807fc1682b1f01bfa68', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_census.py': '27fc81b380de5fc60c4edf2110571c8ede38bedc120f9cec1ad15aa33924aad8', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_sources.py': 'd84f024f755d23543bd0b0601f14e2e7adae5d1eaadbc325e636bff3d628788e', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_parallel.py': '52aef74eb01e17669dc068c8532c7008c251e8d1b5308f8e38790c613db0197e', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_native.py': 'e7dbe6c47061529953102b1af93422b593460e7510b22e27dbde69bcfbf052b7', 'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline_runtime.py': '8687f59c0986eff6a3f008c890385724a880c0e6356d6e059d61ec192386d483', 'greek-ocr-toolkit-pipe032/greekocr/harvest/geometry_observations.py': 'ba3ff4c9a6777f4c1c587eaf7ee1770d73ad0b5088d0ff3e333f09671f012570', 'greek-ocr-toolkit-pipe032/scripts/harvest/clariden/worker.py': '8c8109606e50bf6b26f74d95436e555bc3bac0984ed5c584600fa2602b2ea5c7', 'greek-ocr-toolkit-pipe032/scripts/harvest/clariden/bootstrap.py': '7ec4b9ddb4a7ad87631992f834ab9a0f52ce6a42e2f6226103ad9a839695dc18', 'greek-ocr-toolkit-pipe032/scripts/harvest/clariden/filter_crop_paths.py': '04247e96e82db502c7da154f70360f8f4a17b2a9620bb26df9d8bca781ae7110', 'greek-ocr-toolkit-pipe032/scripts/harvest/clariden/filter_worker.sbatch': '3b30cf18b1d72207000d0532afed44cfa9961982dc84dbd950d66de2b716153c', 'greek-ocr-toolkit-pipe032/scripts/harvest/clariden/package.py': 'cd4b9d0ae23e405ed61c81abb1a37029ce43abf456390abd2167df5b9b613da5'}, 'digest': '03e6d58369f88019bc6d64ea53ecd55ad19445c7d9a079770422529f40ebfbc3'}, 'inventory': {'version': '0.1', 'documented_iterations': ['first integrated graph implementation'], 'iteration_count': 1, 'scope': 'existing toolkit inventory primitives', 'components': {'greek-ocr-toolkit-pipe032/greekocr/harvest/line_pipeline.py': '9c6f8ead156429011d03384e50b37d899bea5ba34df7e807fc1682b1f01bfa68'}, 'digest': 'a3c42b877f00e3798909213e43ef5f2f0682571b1fa04a33b284aa198ebef2fb'}} |

### Diagnostics (first 20 in file order)

Counted from: `decisions.jsonl`, `admitted_train.jsonl`, ledger inventory.

| issue | count | first20 |
| --- | --- | --- |
| admitted_train_violations | 0 | [] |
| duplicates | 0 | [] |
| gate_route_violations | 0 | [] |
| gate_segmentation_violations | 0 | [] |
| heldout_leaks | 0 | [] |
| missing_rows | 0 | [] |
| no_reason | 0 | [] |
| pipeline_version_mismatch | 1 | [{"id":"r1","parent":"parent","version":"0.3.2"}] |
| unexpected_rows | 0 | [] |

### File provenance

Counted from: files named below (streamed SHA256).

| path | bytes | sha256 |
| --- | --- | --- |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/readout_contract_witness/attempt/CURRENT.json | 465 | fe538ee3cdd0864486313ef5ef5e1b2ba1e072a348ca2ab1c2d647e342bb631a |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/readout_contract_witness/attempt/generations/g1-61c96b5c21bb4b77a4fbe83e78622683/admission_records.jsonl | 3468 | 61e4172189bf6920bc6d05f115726175fc210c3b5ef0c8877ba26c25b4a728a1 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/readout_contract_witness/attempt/generations/g1-61c96b5c21bb4b77a4fbe83e78622683/admitted_train.jsonl | 3507 | 23c81db92b682d859fab9464164f8807fcd83662ff7113168f16eb097f11badd |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/readout_contract_witness/attempt/generations/g1-61c96b5c21bb4b77a4fbe83e78622683/decisions.jsonl | 3160 | 62d9f5004372ac616b356a20057a220fcb8f435673fa05ababa268d256a8a46e |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/readout_contract_witness/attempt/generations/g1-61c96b5c21bb4b77a4fbe83e78622683/evaluation_diagnostics.jsonl | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/readout_contract_witness/attempt/generations/g1-61c96b5c21bb4b77a4fbe83e78622683/pending_content_repair.jsonl | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/readout_contract_witness/attempt/generations/g1-61c96b5c21bb4b77a4fbe83e78622683/pending_cyrillic.jsonl | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/readout_contract_witness/attempt/generations/g1-61c96b5c21bb4b77a4fbe83e78622683/pending_numerics.jsonl | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/readout_contract_witness/attempt/generations/g1-61c96b5c21bb4b77a4fbe83e78622683/pending_polytonic.jsonl | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/readout_contract_witness/attempt/generations/g1-61c96b5c21bb4b77a4fbe83e78622683/summary.json | 3320 | 5c933ac1099e031825ef775b3b9c5f2b8cee4672c1f26702191e25ecde5e495e |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/readout_contract_witness/attempt/ledger.sqlite | 77824 | ba8b75163eb2f08f72b0c0a33fe85f1969c6458d10e9478edcce19aa3c23f7e1 |
| /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus/docs/harvest/census05/package/projects/greek-ocr-toolkit-pipe032/docs/harvest/line_pipeline/tool_versions.json | 12601 | ed81e3a1b7389c3dd4d29706e5e2ff2b6d0d34fa0648a9587388a25be2725831 |

No baseline supplied; no historical delta inferred. The handoff records 65,900 admissions.

CENSUS READOUT: rows 1 (complete yes); ADMIT 1 HOLD 0 DROP 0; admitted_train 1; gate DROP 0 HOLD 0 (mixed 0 foreign 0 short 0 cell1 0 num1 0 unresolved 0); pending content_repair 0, cyrillic 0, numerics 0, polytonic 0; heldout leaks 0; invariants 13/14 PASS
