# CQ6C parameters versus actual R2a job 3683130

19 bound parameters, 0 intended changes. Three seeds: 20261016/17/18. No new training measurement.

| Parameter | Actual R2a | Intended CQ6C | Changes |
|---|---|---|---|
| embedding | `true` | same | 0 |
| left_heights | `1.5` | same | 0 |
| balanced | `true` | same | 0 |
| none_fraction | `0.4` | same | 0 |
| rare_min_fraction | `0.05` | same | 0 |
| epochs | `15` | same | 0 |
| batch_size | `512` | same | 0 |
| optimizer | `"AdamW"` | same | 0 |
| lr | `0.001` | same | 0 |
| weight_decay | `0.01` | same | 0 |
| seed | `{"20261016": 20261016, "20261017": 20261017, "20261018": 20261018}` | same | 0 |
| sampler_seed | `{"20261016": 20261016, "20261017": 20261017, "20261018": 20261018}` | same | 0 |
| steps_limit | `null` | same | 0 |
| precision | `"bf16"` | same | 0 |
| validation | `"natural distribution, unweighted sum of four cross entropies"` | same | 0 |
| parameters | `1766571` | same | 0 |
| forward_flops | `111277568` | same | 0 |
| approximate_train_flops | `333832704` | same | 0 |
| convention | `"conv/linear multiply+add=2; backward about 2x forward"` | same | 0 |

## Effective settings

| Setting | Actual R2a | Intended CQ6C |
|---|---|---|
| training_initialization | `"new MarkReader; seeded from scratch, no parent checkpoint warm start"` | same |
| arm | `"A"` | same |
| training_view | `"wide; grey plus recogniser-span mask, 2 x 64 x 128"` | same |
| embedding_dimension | `64` | same |
| network_channels | `[32, 64, 128, 192]` | same |
| model_MLP | `"256 + ReLU; four factor heads"` | same |
| augmentation | `"none in actual training loop"` | same |
| learning_rate_schedule | `"constant; no scheduler"` | same |
| AdamW_other_options | `"not supplied; same installed torch defaults required"` | same |
| class_weights | `"old targets only; sqrt(N/max(count,1)); capped at 10, normalized to mean 1"` | same |
| loss | `"sum of four weighted cross entropies; overlay per-row weight 1"` | same |
| sampler | `"ArmBatches; replacement; 40% none, >=5% rare/compound, remainder equal head/value pools"` | same |
| rare_definition | `"marked and >=2 heads, or composed class count <1000"` | same |
| sampler_epoch_seed | `"sampler_seed + epoch (1..15)"` | same |
| steps_per_epoch | `"ceil(pool size / 512); final batch truncated"` | same |
| workers | `4` | same |
| torch_threads | `8` | same |
| pin_memory | `true` | same |
| persistent_workers | `true` | same |
| memory_format | `"channels_last"` | same |
| cudnn_benchmark | `true` | same |
| gradient_accumulation | `1` | same |
| gradient_clipping | `"none"` | same |
| GradScaler | `"none"` | same |
| checkpoint_selection | `"strict improvement in natural validation loss; best.pt each improvement"` | same |
| seed_execution | `"three threads, one seed per cuda:0/1/2; fourth GPU not assigned a seed"` | same |
| native_extraction_workers | `8` | same |
| inference_batch_size | `512` | same |
| inference_workers | `4` | same |
| recognizer_alignment_batch_size | `16` | same |
| recognizer_threads | `8` | same |
| OMP_NUM_THREADS | `8` | same |
| OPENBLAS_NUM_THREADS | `1` | same |
| VECLIB_MAXIMUM_THREADS | `2` | same |
| uenv | `"none in parent sbatch; direct venv_l1/bin/python"` | same |
| python_runtime | `"3.12.15"` | same |
| torch_runtime | `"2.11.0+cu128"` | same |
| hardware | `"NVIDIA GH200 120GB"` | same |
| production_partition | `"normal"` | same |
| production_time | `"01:21:00"` | same |
| nodes | `1` | same |
| tasks | `1` | same |
| gpus_per_node | `4` | same |
| exclusive | `true` | same |
| account | `"a0140"` | same |

The pool intervention changes sampler exposure and steps per epoch naturally. No partial-head loss or teacher-label fill is authorized. See HEADS_AND_ADMISSION.md.

| Data/resource surface | R2a | CQ6C |
|---|---|---|
| Old pool | 1,935,016 rows, 5 excess duplicates | identical reference, order and duplicates |
| v2 overlay | 1,572 | byte-identical |
| Capital slice | 214 negative / 127 positive | 800 / 500 assembled |
| Top-up | absent | 959 proposals; UNKNOWN heads retained |
| W-CAP | absent | 281/300, witness only |
| Job kinds | combined normal / 01:21:00 | prepare/train/evaluate explicitly normal / 01:21:00; combined limit inherited, not separately measured |
| Smoke | no parent debug job | debug / 01:21:00; semantic only, explicit partition override |

## Every parent config leaf

| Parent config field | Actual value | CQ6C disposition |
|---|---|---|
| schema | `"r2a-job-v1"` | frozen reference; no new runtime config claimed |
| mock | `false` | frozen reference; no new runtime config claimed |
| source_commit | `"bd8b5b7e5+R2J3-package"` | frozen reference; no new runtime config claimed |
| policy.schema | `"sf6-release-v1"` | frozen reference; no new runtime config claimed |
| policy.sources.greekocr/labelfix/release_gate.py | `"9ef1d6467229e86c9464f428716c792f2a6fc4ffa1e709b798df82c504120408"` | frozen reference; no new runtime config claimed |
| policy.sources.greekocr/labelfix/reading.py | `"6b2838a31e17960a03b2080bc7b23a68d8b58995490ca22e7761406ab8941518"` | frozen reference; no new runtime config claimed |
| policy.sources.greekocr/labelfix/text.py | `"b2fbe9cf6d8c97d1f8e06e149bfe4e11cc58b9b4f2bb323bddc8afce2ca52c92"` | frozen reference; no new runtime config claimed |
| policy.sources.greekocr/labelfix/segmentation.py | `"60fbf9a0252f78326ebad11b9451b722dbee666cd05daa7e3c040dccdbb789fe"` | frozen reference; no new runtime config claimed |
| policy.sources.scripts/labelfix/clariden/l1_common.py | `"2778235994afaf31cd7587c08223c9b2a5d20ff6c6adfca9f37383062895af66"` | frozen reference; no new runtime config claimed |
| policy.sources.scripts/labelfix/clariden/l1r_recompose.py | `"4de0eee56d61a974a33df699cfa6b037af208021578ef6182597ca34cbaa76a0"` | frozen reference; no new runtime config claimed |
| policy.sources.scripts/labelfix/owner_reading.py | `"0915e831115c570bcdeab540e000cb840f2de8d1e80d0f78be9ba49cda6b4b2f"` | frozen reference; no new runtime config claimed |
| policy.sources.scripts/labelfix/owner_pages_build_combined.py | `"843701c1ab7958b476a417740b244a26379768bfb84a61adfcd403bd4e3acea8"` | frozen reference; no new runtime config claimed |
| policy.sources.greekocr/labelfix/ctc_align.py | `"3ecb1a208918fdc33b897c00c1848456a9480946a17fb88f7d9f5f400a646068"` | frozen reference; no new runtime config claimed |
| policy.sources.scripts/labelfix/m2_run.py | `"8e8afc88ae9803f929e566eda39cc06fe76b80b05ffa9934ebd6433b0b27f1af"` | frozen reference; no new runtime config claimed |
| policy.sources.scripts/labelfix/clariden/r1_extract.py | `"e67d72a9ac792c273b56537d34a5dc07d34768322899cd61c4a4814e8dcf5f42"` | frozen reference; no new runtime config claimed |
| policy.sources.scripts/labelfix/clariden/l1_infer.py | `"67ccc5906c8320e45ec5d2670dc9661422b46a097a1ba89e548881d0a930a9b8"` | frozen reference; no new runtime config claimed |
| policy.sources.scripts/labelfix/clariden/l1e_measure.py | `"011cbe122c62dd743bb5fbf57b305e2b23db1bdd7aed5ae89137f479a8118824"` | frozen reference; no new runtime config claimed |
| policy.sources.scripts/labelfix/clariden/l1e_run.py | `"ce7879bdef7dfb0f19b3d40b72685d758dcdba03dffb522f01a079a2bbc02558"` | frozen reference; no new runtime config claimed |
| policy.sources.scripts/labelfix/clariden/l1_detect.py | `"e03915ea58845bca68d4092f42304002bd913e495ffe182757eaca005a3582ce"` | frozen reference; no new runtime config claimed |
| policy.sources.scripts/labelfix/clariden/r1_common.py | `"45aff9154f33a193f55c494e0473caad8eed3236bbeba564171a841a0a047cb6"` | frozen reference; no new runtime config claimed |
| policy.sha256 | `"6f62925a9a25e956ea7585fd3e07b1043cfd36bea018754c92a7fac86330c406"` | frozen reference; no new runtime config claimed |
| data | `"/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016/output_3678928/data"` | frozen reference; no new runtime config claimed |
| heldout | `"/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016/artifacts/labelfix_r1/heldout_font"` | frozen reference; no new runtime config claimed |
| teacher | `"/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016/output_3678928/A/best.pt"` | frozen reference; no new runtime config claimed |
| recognizer | `"/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/greek-page-ocr/out/e3b/jobA/runs/full_s0/best.pt"` | frozen reference; no new runtime config claimed |
| manifest | `"artifacts/r2a_manifest/r2a_slots_v2.jsonl"` | data/overlay_assembled.jsonl is a proposal, not admitted training input |
| inventory | `"artifacts/labelfix_r2a/inputs/inventory.jsonl.gz"` | frozen reference; no new runtime config claimed |
| native | `"artifacts/labelfix_r2a/inputs/native.jsonl"` | frozen reference; no new runtime config claimed |
| native_alignments | `"artifacts/labelfix_r2a/inputs/native_alignments.jsonl.gz"` | frozen reference; no new runtime config claimed |
| witness | `"artifacts/labelfix_r2a/inputs/witness.jsonl"` | frozen reference; no new runtime config claimed |
| witness_key | `"artifacts/labelfix_r2a/inputs/T4_key.jsonl"` | frozen reference; no new runtime config claimed |
| witness_truth | `"artifacts/r2_resolve/T4/final/resolved.jsonl"` | frozen reference; no new runtime config claimed |
| roles | `"artifacts/labelfix_r2a/inputs/doc_roles.json"` | frozen reference; no new runtime config claimed |
| eligible | `"artifacts/labelfix_r2a/inputs/eligible_selected.jsonl"` | frozen reference; no new runtime config claimed |
| dev | `"artifacts/labelfix_r2a/inputs/dev.jsonl"` | frozen reference; no new runtime config claimed |
| dev_alignments | `"artifacts/labelfix_r2a/inputs/dev_alignments.jsonl.gz"` | frozen reference; no new runtime config claimed |
| dev_truth | `"artifacts/labelfix_r2a/inputs/dev_truth.jsonl.gz"` | frozen reference; no new runtime config claimed |
| heldout_truth | `"docs/labelfix/spellcheck/S4_lines.jsonl.gz"` | frozen reference; no new runtime config claimed |
| overlay | `"docs/labelfix/spellcheck/R2/truth_overlay_v1_1.json"` | frozen reference; no new runtime config claimed |
| checkpoints.A16.path | `"/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016/output_3678928/A/best.pt"` | frozen reference; no new runtime config claimed |
| checkpoints.A16.sha256 | `"719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636"` | frozen reference; no new runtime config claimed |
| checkpoints.BASEs17.path | `"/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2_20261017/output_3681404/C/20261017/best.pt"` | frozen reference; no new runtime config claimed |
| checkpoints.BASEs17.sha256 | `"26f6a28f748238769afd6cfa1b28610b7ad606f49ea3cfdf71666b7d29c8f865"` | frozen reference; no new runtime config claimed |
| checkpoints.BASEs18.path | `"/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2_20261017/output_3681404/C/20261018/best.pt"` | frozen reference; no new runtime config claimed |
| checkpoints.BASEs18.sha256 | `"0f34b2e8ea74a22b6b369e22691af5248dd0e082944c50ac2be1972bb23b69e0"` | frozen reference; no new runtime config claimed |
| seeds | `[20261016, 20261017, 20261018]` | unchanged |
| expected_slots | `1572` | frozen reference; no new runtime config claimed |
| expected_dev_lines | `600` | frozen reference; no new runtime config claimed |
| expected_dev_items | `1793` | frozen reference; no new runtime config claimed |
| forecast.native_minutes | `15.9` | frozen reference; no new runtime config claimed |
| forecast.training_minutes | `17.5` | frozen reference; no new runtime config claimed |
| forecast.inference_scoring_minutes | `20` | frozen reference; no new runtime config claimed |
| forecast.total_minutes | `53.4` | frozen reference; no new runtime config claimed |
| forecast.requested_minutes | `81` | frozen reference; no new runtime config claimed |
| sha256./iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016/output_3678928/A/best.pt | `"719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636"` | frozen reference; no new runtime config claimed |
| sha256./iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/greek-page-ocr/out/e3b/jobA/runs/full_s0/best.pt | `"5f300fdac73d7479769c98e27d068039186ac193c6c4002ddfc8be511d363663"` | frozen reference; no new runtime config claimed |
| sha256./iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2_20261017/output_3681404/C/20261017/best.pt | `"26f6a28f748238769afd6cfa1b28610b7ad606f49ea3cfdf71666b7d29c8f865"` | frozen reference; no new runtime config claimed |
| sha256./iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2_20261017/output_3681404/C/20261018/best.pt | `"0f34b2e8ea74a22b6b369e22691af5248dd0e082944c50ac2be1972bb23b69e0"` | frozen reference; no new runtime config claimed |
| sha256.artifacts/labelfix_r2a/inputs/native.jsonl | `"7226a75dbe1ae75ff0cd7a78870b35991c6771349a56e64efbdbcfa24e396521"` | frozen reference; no new runtime config claimed |
| sha256.artifacts/labelfix_r2a/inputs/native_alignments.jsonl.gz | `"084416fc5b6554966527ffd7bcf245ca4e394e3830356afdc6d5117e38192399"` | frozen reference; no new runtime config claimed |
| sha256.artifacts/labelfix_r2a/inputs/witness.jsonl | `"273f0a84a7dee1ba7d2f54850a2fa95c98a4b643923c01d3437f5d84edda9f34"` | frozen reference; no new runtime config claimed |
| sha256.artifacts/labelfix_r2a/inputs/T4_key.jsonl | `"5c4cf1a92ce0572b5bb2e0a33d4ea0fcd7abf1c421f84b0567b046b78b79a984"` | frozen reference; no new runtime config claimed |
| sha256.artifacts/r2_resolve/T4/final/resolved.jsonl | `"3815e244fdc451d4c230a9740ed1da49b8fa5b955cf70903312f811d79a2643c"` | frozen reference; no new runtime config claimed |
| sha256.artifacts/labelfix_r2a/inputs/eligible_selected.jsonl | `"e2f92aba2627173926c5bdaeaa44e9c6898f881f418ff26050d67bae733f396c"` | frozen reference; no new runtime config claimed |
| sha256.artifacts/labelfix_r2a/inputs/doc_roles.json | `"5dac6cb90fda64a0aa1545a5571f686f629a00b59b1618f0d9d0d2c7d7995646"` | frozen reference; no new runtime config claimed |
| sha256.artifacts/labelfix_r2a/inputs/dev.jsonl | `"f12fa3c1eb5018bd5aef82c4005c3048e7e18932850306e22bd2c668cdf62475"` | frozen reference; no new runtime config claimed |
| sha256.artifacts/labelfix_r2a/inputs/dev_alignments.jsonl.gz | `"2669980bad3ee7ec38d37dd4ad94b40855d5f27574218ff24279017047e1ac5a"` | frozen reference; no new runtime config claimed |
| sha256.artifacts/labelfix_r2a/inputs/dev_truth.jsonl.gz | `"bbfba1509215d60517ab651324a44323f6a5cedd8378c97fdcadab48bc78a3ec"` | frozen reference; no new runtime config claimed |
| sha256.docs/labelfix/spellcheck/S4_lines.jsonl.gz | `"be24f3975cd905270dd2010ea969c9e256f57a45ee408e727be4353eb6c93fe1"` | frozen reference; no new runtime config claimed |
| sha256.docs/labelfix/spellcheck/R2/truth_overlay_v1_1.json | `"34691279fb2634b103b42c779aacfec735480727259cfff643205b57deaa7f2a"` | frozen reference; no new runtime config claimed |
| sha256.artifacts/labelfix_r2a/inputs/inventory.jsonl.gz | `"bb92497f83e109f7536452df5dffa1abc059f9708055778265769d0e51e91f99"` | frozen reference; no new runtime config claimed |
| sha256./iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016/output_3678928/data/extraction_receipt.json | `"e89272a7bf18b79eae5e414ee3d7959c8febbcbe005ea3eb3563de5dc3eba58d"` | frozen reference; no new runtime config claimed |
| sha256./iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r1_20261016/artifacts/labelfix_r1/heldout_font/extraction_receipt.json | `"84d3a259a5280a4c18b19e83961755ed1cf4931f288ff82bc9b241bc613a7277"` | frozen reference; no new runtime config claimed |
| sha256.artifacts/r2a_manifest/r2a_slots_v2.jsonl | `"20b24e0fa6831487568d3bf00bac928e0fcd94831db566c520535a8216a855e1"` | frozen reference; no new runtime config claimed |
| readiness.native_width_decision_pending | `false` | frozen reference; no new runtime config claimed |
| readiness.resolution | `"frozen_extractor_width_gate: slot quarantined; no exception"` | frozen reference; no new runtime config claimed |
| readiness.slot_id | `["82e8f64cbca6e513163d4452641a51a215a0e744b8c4a338a6dc0fdf7ec740e8", 46]` | frozen reference; no new runtime config claimed |
| coordinator_accepted_deviation | `"R2a admits 1,572 print-checked slots against the plan's 4,000; per-slice deficits recorded in B6_RESOLVE_REPORT.md; top-up reading paused by the owner (17 Oct)"` | frozen reference; no new runtime config claimed |
