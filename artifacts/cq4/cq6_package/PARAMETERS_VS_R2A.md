# Actual R2a recipe: job 3683130

19 fields in the actual `run_binding.parameters` object, all preserved in the intended CQ6 recipe (0 changed). No CQ6 training ran. The additional effective settings below are also disclosed; the field count in the hand-off refers only to that actual binding object.

| Parameter | Actual R2a | Intended R2a-2 | Change |
|---|---|---|---|
| embedding | `true` | `true` | 0; intended unchanged |
| left_heights | `1.5` | `1.5` | 0; intended unchanged |
| balanced | `true` | `true` | 0; intended unchanged |
| none_fraction | `0.4` | `0.4` | 0; intended unchanged |
| rare_min_fraction | `0.05` | `0.05` | 0; intended unchanged |
| epochs | `15` | `15` | 0; intended unchanged |
| batch_size | `512` | `512` | 0; intended unchanged |
| optimizer | `"AdamW"` | `"AdamW"` | 0; intended unchanged |
| lr | `0.001` | `0.001` | 0; intended unchanged |
| weight_decay | `0.01` | `0.01` | 0; intended unchanged |
| seed | `{"20261016": 20261016, "20261017": 20261017, "20261018": 20261018}` | `{"20261016": 20261016, "20261017": 20261017, "20261018": 20261018}` | 0; intended unchanged |
| sampler_seed | `{"20261016": 20261016, "20261017": 20261017, "20261018": 20261018}` | `{"20261016": 20261016, "20261017": 20261017, "20261018": 20261018}` | 0; intended unchanged |
| steps_limit | `null` | `null` | 0; intended unchanged |
| precision | `"bf16"` | `"bf16"` | 0; intended unchanged |
| validation | `"natural distribution, unweighted sum of four cross entropies"` | `"natural distribution, unweighted sum of four cross entropies"` | 0; intended unchanged |
| parameters | `1766571` | `1766571` | 0; intended unchanged |
| forward_flops | `111277568` | `111277568` | 0; intended unchanged |
| approximate_train_flops | `333832704` | `333832704` | 0; intended unchanged |
| convention | `"conv/linear multiply+add=2; backward about 2x forward"` | `"conv/linear multiply+add=2; backward about 2x forward"` | 0; intended unchanged |

## Effective code, environment and resource settings

| Parameter | Actual R2a | Intended R2a-2 | Change |
|---|---|---|---|
| training_initialization | `"new MarkReader; seeded from scratch, no parent checkpoint warm start"` | same | 0 intended |
| arm | `"A"` | same | 0 intended |
| training_view | `"wide; grey plus recogniser-span mask, 2 x 64 x 128"` | same | 0 intended |
| embedding_dimension | `64` | same | 0 intended |
| network_channels | `[32, 64, 128, 192]` | same | 0 intended |
| model_MLP | `"256 + ReLU; four factor heads"` | same | 0 intended |
| augmentation | `"none in actual training loop"` | same | 0 intended |
| learning_rate_schedule | `"constant; no scheduler"` | same | 0 intended |
| AdamW_other_options | `"not supplied; same installed torch defaults required"` | same | 0 intended |
| class_weights | `"old targets only; sqrt(N/max(count,1)); capped at 10, normalized to mean 1"` | same | 0 intended |
| loss | `"sum of four weighted cross entropies; overlay per-row weight 1"` | same | 0 intended |
| sampler | `"ArmBatches; replacement; 40% none, >=5% rare/compound, remainder equal head/value pools"` | same | 0 intended |
| rare_definition | `"marked and >=2 heads, or composed class count <1000"` | same | 0 intended |
| sampler_epoch_seed | `"sampler_seed + epoch (1..15)"` | same | 0 intended |
| steps_per_epoch | `"ceil(pool size / 512); final batch truncated"` | same | 0 intended |
| workers | `4` | same | 0 intended |
| torch_threads | `8` | same | 0 intended |
| pin_memory | `true` | same | 0 intended |
| persistent_workers | `true` | same | 0 intended |
| memory_format | `"channels_last"` | same | 0 intended |
| cudnn_benchmark | `true` | same | 0 intended |
| gradient_accumulation | `1` | same | 0 intended |
| gradient_clipping | `"none"` | same | 0 intended |
| GradScaler | `"none"` | same | 0 intended |
| checkpoint_selection | `"strict improvement in natural validation loss; best.pt each improvement"` | same | 0 intended |
| seed_execution | `"three threads, one seed per cuda:0/1/2; fourth GPU not assigned a seed"` | same | 0 intended |
| native_extraction_workers | `8` | same | 0 intended |
| inference_batch_size | `512` | same | 0 intended |
| inference_workers | `4` | same | 0 intended |
| recognizer_alignment_batch_size | `16` | same | 0 intended |
| recognizer_threads | `8` | same | 0 intended |
| OMP_NUM_THREADS | `8` | same | 0 intended |
| OPENBLAS_NUM_THREADS | `1` | same | 0 intended |
| VECLIB_MAXIMUM_THREADS | `2` | same | 0 intended |
| uenv | `"none in parent sbatch; direct venv_l1/bin/python"` | same | 0 intended |
| python_runtime | `"3.12.15"` | same | 0 intended |
| torch_runtime | `"2.11.0+cu128"` | same | 0 intended |
| hardware | `"NVIDIA GH200 120GB"` | same | 0 intended |
| production_partition | `"normal"` | same | 0 intended |
| production_time | `"01:21:00"` | same | 0 intended |
| nodes | `1` | same | 0 intended |
| tasks | `1` | same | 0 intended |
| gpus_per_node | `4` | same | 0 intended |
| exclusive | `true` | same | 0 intended |
| account | `"a0140"` | same | 0 intended |

The trainer/model/extractor source SHA256 values match all three actual run bindings. `evidence/r2a_run.py` supplies CLI arguments and concurrency; `evidence/r1_train.py` supplies sampler, optimiser, loss and validation behavior. Runtime/library defaults are preserved by requiring the same recorded environment; they are not newly tuned. Sampler exposure and the number of batches naturally depend on the changed training pool.

## Data and package differences (scientific intervention; not hidden recipe changes)

| Surface | Actual R2a | CQ6 |
|---|---|---|
| Old pool | 1,935,016 rows; 1,935,011 keys; 5 excess duplicate rows | Same reference and exact BASE order required; no removal |
| v2 overlay | 1,572 slots; capitals 214 negative / 127 positive | Byte-identical copy |
| Separate top-up | absent | 875 provisional rows (586 negative / 289 positive); partial only |
| Final capital slice | 214 / 127 | 800 / 416; 84 positive shortfall; STOPPED |
| Witness | T4 and protection cohorts | W-CAP 281 resolved, 133 marked; never training |
| Preregistration | amendment 1, dbac559f… | amendment 1a exposure consequence note; current hash below |
| Job kinds | one combined A/B/C/D normal job, 81 minutes | normal 81-minute resource stubs for prepare/train/eval; no independently measured kind times |
| Debug | no debug evidence in this parent sacct | semantic smoke stub explicitly debug, 81 minutes; partition override is not a recipe change |
| Production runner | actual R2a runner | not adapted: frozen quota stop occurs before deployable runtime construction |

## Every parent config leaf

Path/hash/count differences are explicit below. These are custody or data parameters rather than training hyperparameters. Parent config is preserved as evidence, not presented as a runnable CQ6 config.

| Parent config field | Actual value | CQ6 disposition |
|---|---|---|
| schema | `"r2a-job-v1"` | frozen parent reference; requires rebinding for a future ready candidate |
| mock | `false` | frozen parent reference; requires rebinding for a future ready candidate |
| source_commit | `"bd8b5b7e5+R2J3-package"` | frozen parent reference; requires rebinding for a future ready candidate |
| policy.schema | `"sf6-release-v1"` | frozen parent reference; requires rebinding for a future ready candidate |
| policy.sources.greekocr/labelfix/release_gate.py | `"9ef1d6467229e86c9464f428716c792f2a6fc4ffa1e709b798df82c504120408"` | frozen parent reference; requires rebinding for a future ready candidate |
| policy.sources.greekocr/labelfix/reading.py | `"6b2838a31e17960a03b2080bc7b23a68d8b58995490ca22e7761406ab8941518"` | frozen parent reference; requires rebinding for a future ready candidate |
| policy.sources.greekocr/labelfix/text.py | `"b2fbe9cf6d8c97d1f8e06e149bfe4e11cc58b9b4f2bb323bddc8afce2ca52c92"` | frozen parent reference; requires rebinding for a future ready candidate |
| policy.sources.greekocr/labelfix/segmentation.py | `"60fbf9a0252f78326ebad11b9451b722dbee666cd05daa7e3c040dccdbb789fe"` | frozen parent reference; requires rebinding for a future ready candidate |
| policy.sources.scripts/labelfix/clariden/l1_common.py | `"2778235994afaf31cd7587c08223c9b2a5d20ff6c6adfca9f37383062895af66"` | frozen parent reference; requires rebinding for a future ready candidate |
| policy.sources.scripts/labelfix/clariden/l1r_recompose.py | `"4de0eee56d61a974a33df699cfa6b037af208021578ef6182597ca34cbaa76a0"` | frozen parent reference; requires rebinding for a future ready candidate |
| policy.sources.scripts/labelfix/owner_reading.py | `"0915e831115c570bcdeab540e000cb840f2de8d1e80d0f78be9ba49cda6b4b2f"` | frozen parent reference; requires rebinding for a future ready candidate |
| policy.sources.scripts/labelfix/owner_pages_build_combined.py | `"843701c1ab7958b476a417740b244a26379768bfb84a61adfcd403bd4e3acea8"` | frozen parent reference; requires rebinding for a future ready candidate |
| policy.sources.greekocr/labelfix/ctc_align.py | `"3ecb1a208918fdc33b897c00c1848456a9480946a17fb88f7d9f5f400a646068"` | frozen parent reference; requires rebinding for a future ready candidate |
| policy.sources.scripts/labelfix/m2_run.py | `"8e8afc88ae9803f929e566eda39cc06fe76b80b05ffa9934ebd6433b0b27f1af"` | frozen parent reference; requires rebinding for a future ready candidate |
| policy.sources.scripts/labelfix/clariden/r1_extract.py | `"e67d72a9ac792c273b56537d34a5dc07d34768322899cd61c4a4814e8dcf5f42"` | frozen parent reference; requires rebinding for a future ready candidate |
| policy.sources.scripts/labelfix/clariden/l1_infer.py | `"67ccc5906c8320e45ec5d2670dc9661422b46a097a1ba89e548881d0a930a9b8"` | frozen parent reference; requires rebinding for a future ready candidate |
| policy.sources.scripts/labelfix/clariden/l1e_measure.py | `"011cbe122c62dd743bb5fbf57b305e2b23db1bdd7aed5ae89137f479a8118824"` | frozen parent reference; requires rebinding for a future ready candidate |
| policy.sources.scripts/labelfix/clariden/l1e_run.py | `"ce7879bdef7dfb0f19b3d40b72685d758dcdba03dffb522f01a079a2bbc02558"` | frozen parent reference; requires rebinding for a future ready candidate |
| policy.sources.scripts/labelfix/clariden/l1_detect.py | `"e03915ea58845bca68d4092f42304002bd913e495ffe182757eaca005a3582ce"` | frozen parent reference; requires rebinding for a future ready candidate |
| policy.sources.scripts/labelfix/clariden/r1_common.py | `"45aff9154f33a193f55c494e0473caad8eed3236bbeba564171a841a0a047cb6"` | frozen parent reference; requires rebinding for a future ready candidate |
| policy.sha256 | `"6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406"` | frozen parent reference; requires rebinding for a future ready candidate |
| data | `"/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016/output_3678928/data"` | same parent reference required |
| heldout | `"/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016/artifacts/labelfix_r1/heldout_font"` | same parent reference required |
| teacher | `"/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016/output_3678928/A/best.pt"` | same parent reference required |
| recognizer | `"/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/greek-page-ocr/out/e3b/jobA/runs/full_s0/best.pt"` | same parent reference required |
| manifest | `"artifacts/r2a_manifest/r2a_slots_v2.jsonl"` | partial overlay has its own hash; NOT admitted for training |
| inventory | `"artifacts/labelfix_r2a/inputs/inventory.jsonl.gz"` | frozen parent reference; requires rebinding for a future ready candidate |
| native | `"artifacts/labelfix_r2a/inputs/native.jsonl"` | frozen parent reference; requires rebinding for a future ready candidate |
| native_alignments | `"artifacts/labelfix_r2a/inputs/native_alignments.jsonl.gz"` | frozen parent reference; requires rebinding for a future ready candidate |
| witness | `"artifacts/labelfix_r2a/inputs/witness.jsonl"` | frozen parent reference; requires rebinding for a future ready candidate |
| witness_key | `"artifacts/labelfix_r2a/inputs/T4_key.jsonl"` | frozen parent reference; requires rebinding for a future ready candidate |
| witness_truth | `"artifacts/r2_resolve/T4/final/resolved.jsonl"` | frozen parent reference; requires rebinding for a future ready candidate |
| roles | `"artifacts/labelfix_r2a/inputs/doc_roles.json"` | frozen parent reference; requires rebinding for a future ready candidate |
| eligible | `"artifacts/labelfix_r2a/inputs/eligible_selected.jsonl"` | frozen parent reference; requires rebinding for a future ready candidate |
| dev | `"artifacts/labelfix_r2a/inputs/dev.jsonl"` | frozen parent reference; requires rebinding for a future ready candidate |
| dev_alignments | `"artifacts/labelfix_r2a/inputs/dev_alignments.jsonl.gz"` | frozen parent reference; requires rebinding for a future ready candidate |
| dev_truth | `"artifacts/labelfix_r2a/inputs/dev_truth.jsonl.gz"` | frozen parent reference; requires rebinding for a future ready candidate |
| heldout_truth | `"docs/labelfix/spellcheck/S4_lines.jsonl.gz"` | frozen parent reference; requires rebinding for a future ready candidate |
| overlay | `"docs/labelfix/spellcheck/R2/truth_overlay_v1_1.json"` | frozen parent reference; requires rebinding for a future ready candidate |
| checkpoints.A16.path | `"/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016/output_3678928/A/best.pt"` | same parent reference required |
| checkpoints.A16.sha256 | `"719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636"` | frozen parent reference; requires rebinding for a future ready candidate |
| checkpoints.BASEs17.path | `"/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2_20261017/output_3681404/C/20261017/best.pt"` | same parent reference required |
| checkpoints.BASEs17.sha256 | `"26f6a28f748238769afd6cfa1b28610b7ad606f49ea3cfdf71666b7d29c8f865"` | frozen parent reference; requires rebinding for a future ready candidate |
| checkpoints.BASEs18.path | `"/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2_20261017/output_3681404/C/20261018/best.pt"` | same parent reference required |
| checkpoints.BASEs18.sha256 | `"0f34b2e8ea74a22b6b369e22691af5248dd0e082944c50ac2be1972bb23b69e0"` | frozen parent reference; requires rebinding for a future ready candidate |
| seeds | `[20261016, 20261017, 20261018]` | identical full seeds |
| expected_slots | `1572` | frozen parent reference; requires rebinding for a future ready candidate |
| expected_dev_lines | `600` | frozen parent reference; requires rebinding for a future ready candidate |
| expected_dev_items | `1793` | frozen parent reference; requires rebinding for a future ready candidate |
| forecast.native_minutes | `15.9` | historical R2a forecast, not a CQ6 forecast |
| forecast.training_minutes | `17.5` | historical R2a forecast, not a CQ6 forecast |
| forecast.inference_scoring_minutes | `20` | historical R2a forecast, not a CQ6 forecast |
| forecast.total_minutes | `53.4` | historical R2a forecast, not a CQ6 forecast |
| forecast.requested_minutes | `81` | historical R2a forecast, not a CQ6 forecast |
| sha256./iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016/output_3678928/A/best.pt | `"719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636"` | frozen parent reference; requires rebinding for a future ready candidate |
| sha256./iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/greek-page-ocr/out/e3b/jobA/runs/full_s0/best.pt | `"5f300fdac73d7479769c98e27d068039186ac193c6c4002ddfc8be511d363663"` | frozen parent reference; requires rebinding for a future ready candidate |
| sha256./iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2_20261017/output_3681404/C/20261017/best.pt | `"26f6a28f748238769afd6cfa1b28610b7ad606f49ea3cfdf71666b7d29c8f865"` | frozen parent reference; requires rebinding for a future ready candidate |
| sha256./iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2_20261017/output_3681404/C/20261018/best.pt | `"0f34b2e8ea74a22b6b369e22691af5248dd0e082944c50ac2be1972bb23b69e0"` | frozen parent reference; requires rebinding for a future ready candidate |
| sha256.artifacts/labelfix_r2a/inputs/native.jsonl | `"7226a75dbe1ae75ff0cd7a78870b35991c6771349a56e64efbdbcfa24e396521"` | frozen parent reference; requires rebinding for a future ready candidate |
| sha256.artifacts/labelfix_r2a/inputs/native_alignments.jsonl.gz | `"084416fc5b6554966527ffd7bcf245ca4e394e3830356afdc6d5117e38192399"` | frozen parent reference; requires rebinding for a future ready candidate |
| sha256.artifacts/labelfix_r2a/inputs/witness.jsonl | `"273f0a84a7dee1ba7d2f54850a2fa95c98a4b643923c01d3437f5d84edda9f34"` | frozen parent reference; requires rebinding for a future ready candidate |
| sha256.artifacts/labelfix_r2a/inputs/T4_key.jsonl | `"5c4cf1a92ce0572b5bb2e0a33d4ea0fcd7abf1c421f84b0567b046b78b79a984"` | frozen parent reference; requires rebinding for a future ready candidate |
| sha256.artifacts/r2_resolve/T4/final/resolved.jsonl | `"3815e244fdc451d4c230a9740ed1da49b8fa5b955cf70903312f811d79a2643c"` | frozen parent reference; requires rebinding for a future ready candidate |
| sha256.artifacts/labelfix_r2a/inputs/eligible_selected.jsonl | `"e2f92aba2627173926c5bdaeaa44e9c6898f881f418ff26050d67bae733f396c"` | frozen parent reference; requires rebinding for a future ready candidate |
| sha256.artifacts/labelfix_r2a/inputs/doc_roles.json | `"5dac6cb90fda64a0aa1545a5571f686f629a00b59b1618f0d9d0d2c7d7995646"` | frozen parent reference; requires rebinding for a future ready candidate |
| sha256.artifacts/labelfix_r2a/inputs/dev.jsonl | `"f12fa3c1eb5018bd5aef82c4005c3048e7e18932850306e22bd2c668cdf62475"` | frozen parent reference; requires rebinding for a future ready candidate |
| sha256.artifacts/labelfix_r2a/inputs/dev_alignments.jsonl.gz | `"2669980bad3ee7ec38d37dd4ad94b40855d5f27574218ff24279017047e1ac5a"` | frozen parent reference; requires rebinding for a future ready candidate |
| sha256.artifacts/labelfix_r2a/inputs/dev_truth.jsonl.gz | `"bbfba1509215d60517ab651324a44323f6a5cedd8378c97fdcadab48bc78a3ec"` | frozen parent reference; requires rebinding for a future ready candidate |
| sha256.docs/labelfix/spellcheck/S4_lines.jsonl.gz | `"be24f3975cd905270dd2010ea969c9e256f57a45ee408e727be4353eb6c93fe1"` | frozen parent reference; requires rebinding for a future ready candidate |
| sha256.docs/labelfix/spellcheck/R2/truth_overlay_v1_1.json | `"34691279fb2634b103b42c779aacfec735480727259cfff643205b57deaa7f2a"` | frozen parent reference; requires rebinding for a future ready candidate |
| sha256.artifacts/labelfix_r2a/inputs/inventory.jsonl.gz | `"bb92497f83e109f7536452df5dffa1abc059f9708055778265769d0e51e91f99"` | frozen parent reference; requires rebinding for a future ready candidate |
| sha256./iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016/output_3678928/data/extraction_receipt.json | `"e89272a7bf18b79eae5e414ee3d7959c8febbcbe005ea3eb3563de5dc3eba58d"` | frozen parent reference; requires rebinding for a future ready candidate |
| sha256./iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016/artifacts/labelfix_r1/heldout_font/extraction_receipt.json | `"84d3a259a5280a4c18b19e83961755ed1cf4931f288ff82bc9b241bc613a7277"` | frozen parent reference; requires rebinding for a future ready candidate |
| sha256.artifacts/r2a_manifest/r2a_slots_v2.jsonl | `"20b24e0fa6831487568d3bf00bac928e0fcd94831db566c520535a8216a855e1"` | frozen parent reference; requires rebinding for a future ready candidate |
| readiness.native_width_decision_pending | `false` | frozen parent reference; requires rebinding for a future ready candidate |
| readiness.resolution | `"frozen_extractor_width_gate: slot quarantined; no exception"` | frozen parent reference; requires rebinding for a future ready candidate |
| readiness.slot_id | `["82e8f64cbca6e513163d4452641a51a215a0e744b8c4a338a6dc0fdf7ec740e8", 46]` | frozen parent reference; requires rebinding for a future ready candidate |
| coordinator_accepted_deviation | `"R2a admits 1,572 print-checked slots against the plan's 4,000; per-slice deficits recorded in B6_RESOLVE_REPORT.md; top-up reading paused by the owner (17 Oct)"` | frozen parent reference; requires rebinding for a future ready candidate |
