# Component version register — 28 October 2026

A generation is **one completed round producing a new component version that was evaluated or used as incumbent** (release PLAN §1). Arms, widths, seeds, restarts and scoring reruns within that round count once. External-teacher bake-offs and preparation/smoke qualification do not count. Rejected but evaluated method generations remain in history. Version numbers do not imply adoption or accuracy. Beta ends only when the owner declares v1.

Git tags are component-qualified (`ocr-v0.n`, `lines-v0.n`, `synth-v0.n`, `segmenter-v0.n`, `crop-v0.n`, `gate-v0.n`, `repair-v0.n`, `composer-v0.n`, `eligibility-v0.n`, `census-v0.n`, `inventory-v0.n`, `sf7-v0.n`, `ru1-v0.n`, `n1-v0.n`, `dashes-v0.n`, `builder-v0.n`). HF repositories use plain `v0.n`. Never move a published tag. No tags were created in REL0-S2.

## OCR model

`OCR_VERSION=v0.10`: **n=10 supported rounds**, counting the incumbent lineage once and each completed experimental round separately. This replaces the plan's provisional six. Historical identity uncertainties below remain explicit; v0.10 is the evidence-backed working value, **not permission to create an immutable tag before those uncertainties are settled**. `MODELS.json` carries this parameter; consumers should read its `OCR_VERSION`, not infer a version from an old experiment name. ×1, ×1.5 and ×2 are widths within TRAIN_FULL_v1, not generations.

`PAGE` below means repository evidence root `scripts/release_v0_publish/evidence/PAGE/`, containing copies of the cited sibling records; review-artifact URLs are withheld in two public copies as bound by `scripts/release_v0_publish/PUBLIC_EVIDENCE_RECEIPT.json`. The publication inventory includes these repository paths; no sibling checkout is required. Source SHA inventory follows below. Dates are dates stated by the records; ranges/unknowns are not reconstructed from filesystem mtimes.

| Date (2026) | Candidate / aliases | Counted | Evidence and reason |
|---|---|---|---|
| Before 7 Oct; exact training date uncertain | T1 compact/NFD incumbent, later described as the C1 recognizer | **1 → v0.1** | PAGE `docs/ocr_program_2026-10-06/O5_NOTES.md`: incumbent `out/prime_checkpoints/t1_compact_nfd_s2/best.pt`, SHA `512553499587306769cac792baf9de7b52399e1aac8374618c24ab0adccaa976`, measured base. A trained, evaluated incumbent exists. C1's deployment alone is not a second training round. |
| Historical July date in preregistration; completion uncertain | T1′ multilingual pilot; earlier T1/S-series training | **Uncertain; no extra count** | PAGE `docs/prereg_t1prime_pilot.md` describes the Greek-only incumbent and planned multilingual training; `docs/reviews/fable_t1prime_result_cert.md` contains only reviewer assertions, no results. Need completion/checkpoint lineage tying this to, or distinguishing it from, the O5/C1 incumbent; earlier S15/S16 architecture/head labels alone cannot establish independent completed rounds. |
| 6–7 Oct | O1 / O1b / O1c / O1d / O4 policy replay | No | PAGE `O1_NOTES.md`: extraction/admission; explicitly no recognizer training. |
| 7 Oct | O2 | No | PAGE `O2_NOTES.md`: machine subset seal and review preparation, human verification pending; no trained model. |
| 6–7 Oct | O3 | Uncertain; no count | No O3 completion/training record in the sibling programme inventory. Need a result/checkpoint record, not a task number. |
| 6–7 Oct | O4a / O4b / O4b Anemi / O4c | No | PAGE corresponding NOTES: sourcing/adapters/discovery; no new recognizer training. |
| 7 Oct | O5 paired real/synthetic | No full-round count | PAGE `O5_NOTES.md`: paired one-epoch smoke, 27 updates, final verdict `incomplete`; full three-seed result remains unmeasured. Preparation/smoke does not count. Base checkpoint is already v0.1. |
| 7 Oct | O6-prep | No | PAGE `O6_NOTES.md`: geometry/layout diagnostic, explicitly no recognizer training. |
| 7 Oct | E1 runs 1–3 and run4 | **2 → v0.2**, run4 once | PAGE `E1_REPORT_run4.md`: 15 arms × 8 epochs / 2,464 updates; code `2e3cf6f`. Earlier run numbers are preparation/recovery in the E1 experiment; no separate completed scientific round established. |
| 8 Oct onward | E2 retrain / teacher bake-off / donor parity | No separate count | PAGE `E2_NOTES.md`: E1 teacher re-executions and external teacher/donor qualification. They are excluded by the rule. Any independent completed E2 model-training round would need its results/binding; not inferred from the implemented runner. |
| 16 Oct | E3 / E3a–g | **3 → v0.3** | PAGE `E3_RESULTS.md`: 10 completed scaling/warm-start arms, report `32e93f48…63bf0`; internal stages/readback count once. |
| By 17 Oct (exact completion date not stated in digest) | E4 wave 1a | **4 → v0.4** | PAGE `E4_WAVE1A_RESULTS.md`: 18 completed eight-epoch arms. Aggregate PARTIAL and readback 189 pass/4 fail remain disclosed; evaluated models still count. Deferred grave arm does not. |
| By 18 Oct (exact completion date not stated in digest) | E4 wave 1b | **5 → v0.5** | PAGE `E4_WAVE1B_RESULTS.md`: 12/12 complete; jobs 3679498/3679500/3679506/3679511, aggregate 3679513; readback 193/0. New codec/recovery/width round; not folded into wave 1a. |
| 18 Oct | E4 wave 1c / RU1 round | **6 → v0.6** | PAGE `HANDOFF_20261018_coordinator.md` explicitly records DONE, deployment `e4_wave1c_reg2_20261018`; later task-2 report reuses three-seed wave-1c hypotheses. Detailed E4_WAVE1C_RESULTS.md is absent from this sibling checkout; counted on these two independent retained reports, not on its prep brief. |
| 17–18 Oct | E4 wave 1d / 1d2 / 1e | Uncertain; no count | PAGE has wave1d_prep/wave1e_prep and preparation/readback briefs, but no retained completed training result here. B masked-admission rows do not prove OCR training completed. Need completion and evaluated output receipts. |
| 21–22 Oct | E4 wave 2 on v4 / ctrl, add, add_corr | **7 → v0.7** | `docs/programme_20261019/SIMPLIFICATION/wave2/RESULTS.md`: nine completed runs; jobs 3714399–3714401, aggregate retry05 3716860. Restarts/aggregate retries do not count again. |
| 22 Oct | Task 2 corrected initial recipe / ctrl_corr04 | **8 → v0.8** | `…/SIMPLIFICATION/task2/TASK2_RESULTS.md`: new corrected-control training, job 3719761, 3 seeds × 8 epochs / 53,616 updates. Reused as-is/wave-2 models and rescoring are not extra rounds. |
| 23–25 Oct; exact terminal date in retained readback needed | S1 / post-E3 scaling ladder | **9 → v0.9** | `…/SIMPLIFICATION/s1/S1_RESULTS.md`: 24 completed models / eight cells; aggregate 3721146, rescore 3721578. “post-E3” is an umbrella alias, not an additional unnamed round. |
| 25–28 Oct; ×1 still running in local ledger | TRAIN_FULL_v1 Stage A/B/C, attempts 013 and 014 | **10 → v0.10** | `docs/programme_20261025/TRAIN_FULL_v1/EXECUTION_STATE.md`: ×2 and ×1.5 complete on 28 Oct, 254/254 loss and 4/4 CER points. Stage B tunes the same experiment; Stage C evaluates its selected recipes. h14 ×1 is the replacement lane, not a new generation; final three-model publication remains pending. |
| 27 Oct | Retired attempt013 ×1 h13 | No extra count / excluded from release | Partial lane, replaced by attempt014 h14. Does not become an independently released generation. |

## Other components

| Component | Current working version / aliases | Count and qualification |
|---|---|---|
| A segmenter lineage | **v0.3**; pixel-first / small-Paddle R7 / R8 | Three evaluated project generations, not B crop-policy iterations. R8 remains partial. |
| B crop policy | **v0.13**; segmentation 0.13 / 0.9-s5 | 13 documented evaluated/used method generations; history below. |
| Content gate | **v0.3**; gate 0.3 | Three documented generations. |
| Content repair | **v0.2**; content_repair_0.2 | Two documented generations; missing external evidence HOLDs. |
| Composer | **v0.3**; composer_0.3 | Three documented generations. |
| Final eligibility | **v0.3**; final_eligibility 0.3 | Three documented generations. |
| Census | **v0.7**; census tool 0.7 | Seven documented tool generations; census_05/06 data runs and generation-2 ledger are not seven additional tools. |
| Inventory | **v0.1**; inventory 0.1 | One documented generation. |
| SF7 | **v0.7**; S1–S5 / SF6 / SF7 / sf7-rc1 A | Seven documented rounds; candidate_pre_audit status is retained. |
| RU1 | **v0.3**; ru1_v1 / ru1_v2_train / ru1_v3_edits | Three evaluated rounds. |
| N1 | **v0.3**; automatic / assisted / census03 integration | Three rounds, including the rejected automatic candidate; assisted use only. |
| Dashes | **v0.1**; dash tags | One tag-only round, no general correction release. |
| Synthetic generator code | **v0.n, n unresolved**; Rust linefactory, captured source `b7818f3f4bfcd9353bd894038fa589459a8e4d2f` | One captured code state is proven; recipe numbers are not generator-code rounds. Missing chronological build/evaluation/code ledger prevents a justified n. Do not map recipe.v8 to generator v0.8. |
| Synthetic line set | **v0.n, n unresolved**; strips_v4a/v5, v5, v7, v8, codec-v2.1 clone | Distinct training/evaluation builds exist; no complete chronology/deduplication of aliases. E1 v5 train 203,693; v7 reserved 2,399; E2 v8 is evaluation; current clone has 190,486 train. Need original build receipts for val/reserved and earlier sets to settle n; no regeneration. |
| Line dataset | **v0.4 established legacy alias v4; next union generation not final**; collection-v2 / v2-asis / v2-codec / v3 / v4 / harvest-20261025 | Legacy release numbers are preserved, not blindly counted. Candidate dispositions below; v4's numbering predates this rule, so exact n remains uncertain. Public prepared005 union will be a new completed generation only after step 4 verification. |
| Release builder | **v0.n, n unresolved**; REL3 / REL4 / harvest release / release_v0 | At least REL3 and REL4 completed with distinct code; release_v0 is being implemented in another run. Need earlier release-builder lineage and harvest-builder equivalence before assigning n; fixture tests alone do not prove a population build. |

The orchestration identifier `0.3.2` (and later census-bound `0.3.3`) is retained as an alias, not silently equated with a component generation. Frozen consumers use their own bound manifest, which can be newer than the root manifest.

### A segmenter rounds

| Date (2026) | Generation | Counted / evidence |
|---|---|---|
| 9 Oct | Pixel-first | Yes, v0.1; `docs/A_ocr_development/MODEL_GENERATIONS.md`, `f405fe38bc19febc7600c61a49cca05740fde73d`; Q3/Q4 are later packaging/optimization, not new project generations. |
| 10–11 Oct | Small detector + heuristics / R7 | Yes, v0.2; same record, `932027e210debf0e63b152894d2bdd727770579b`, review `52cee3bcc882e7426bdc1018d892cd9b1bf9feac`. |
| 12–19 Oct | R8 | Yes, v0.3; evaluated revision; runtime `046bd52dddeea7ada7727971f1038d34328ba5b7`, audit `2f1c91a09b844c87696b95b6c89cd5c3ff7beede`. Partial goals remain; feature experiments and integration commits are not new project generations. |

### B tools: every registered generation

The authoritative root evidence is `docs/harvest/line_pipeline/tool_versions.json`. Each row below is counted because that register identifies a completed evaluated/used method generation. It records source/component hashes and digest. **Dates for individual early rounds are not retained in that manifest**; the ranges below are bounded by its 18–20 October integration and the dated records under `docs/records/harvest/seg_steps/`, `docs/records/labelfix/` and `docs/harvest/line_pipeline/`. Exact per-round dates require the corresponding original evaluation/adoption receipts. No dates or patch rounds are invented. Reruns, reverted attempts and “census_06 generation 2” do not increment these tool counts.

| Component | v0.n | Date / alias / reason (all counted) | Evidence digest |
|---|---|---|---|
| polytonic | v0.1 | ≤20 Oct; exact date uncertain. S1 | `de1a9a8bc6b0598f5b28ac213faa13ce00ced95aa2754291fc183373f60c60c5` (component hashes in manifest) |
| polytonic | v0.2 | ≤20 Oct; exact date uncertain. S2 | `de1a9a8bc6b0598f5b28ac213faa13ce00ced95aa2754291fc183373f60c60c5` (component hashes in manifest) |
| polytonic | v0.3 | ≤20 Oct; exact date uncertain. S3 | `de1a9a8bc6b0598f5b28ac213faa13ce00ced95aa2754291fc183373f60c60c5` (component hashes in manifest) |
| polytonic | v0.4 | ≤20 Oct; exact date uncertain. S4 | `de1a9a8bc6b0598f5b28ac213faa13ce00ced95aa2754291fc183373f60c60c5` (component hashes in manifest) |
| polytonic | v0.5 | ≤20 Oct; exact date uncertain. S5 | `de1a9a8bc6b0598f5b28ac213faa13ce00ced95aa2754291fc183373f60c60c5` (component hashes in manifest) |
| polytonic | v0.6 | ≤20 Oct; exact date uncertain. SF6 | `de1a9a8bc6b0598f5b28ac213faa13ce00ced95aa2754291fc183373f60c60c5` (component hashes in manifest) |
| polytonic | v0.7 | ≤20 Oct; exact date uncertain. SF7 | `de1a9a8bc6b0598f5b28ac213faa13ce00ced95aa2754291fc183373f60c60c5` (component hashes in manifest) |
| cyrillic | v0.1 | ≤20 Oct; exact date uncertain. ru1_v1 | `f63e1ba8696adb47dfc07b283c615fe83deb3f1d2fd28acbf0300de495235123` (component hashes in manifest) |
| cyrillic | v0.2 | ≤20 Oct; exact date uncertain. ru1_v2_train | `f63e1ba8696adb47dfc07b283c615fe83deb3f1d2fd28acbf0300de495235123` (component hashes in manifest) |
| cyrillic | v0.3 | ≤20 Oct; exact date uncertain. ru1_v3_edits | `f63e1ba8696adb47dfc07b283c615fe83deb3f1d2fd28acbf0300de495235123` (component hashes in manifest) |
| numerics | v0.1 | ≤20 Oct; exact date uncertain. N1 automatic ink candidate (rejected 0/5) | `f1b5c0aa990b76dac5f757af9fdf16bc0374dc3fc1dd98f64979c021b5bed2b9` (component hashes in manifest) |
| numerics | v0.2 | ≤20 Oct; exact date uncertain. N1 assisted two-reader and lead-pixel release | `f1b5c0aa990b76dac5f757af9fdf16bc0374dc3fc1dd98f64979c021b5bed2b9` (component hashes in manifest) |
| numerics | v0.3 | ≤20 Oct; exact date uncertain. census_03 integration: digit/separator/digit adjacency for automatic candidate negatives | `f1b5c0aa990b76dac5f757af9fdf16bc0374dc3fc1dd98f64979c021b5bed2b9` (component hashes in manifest) |
| dashes | v0.1 | ≤20 Oct; exact date uncertain. dash tags; no general repair release | `a3c42b877f00e3798909213e43ef5f2f0682571b1fa04a33b284aa198ebef2fb` (component hashes in manifest) |
| B crop policy | v0.1 | ≤20 Oct; exact date uncertain. 29fa466 crop guides | `86c85a6f1d9eb8e7b8327d0e84a77f58403fa9259c0743e5421b995abe46c1a6` (component hashes in manifest) |
| B crop policy | v0.2 | ≤20 Oct; exact date uncertain. 5d664bf font normalized | `86c85a6f1d9eb8e7b8327d0e84a77f58403fa9259c0743e5421b995abe46c1a6` (component hashes in manifest) |
| B crop policy | v0.3 | ≤20 Oct; exact date uncertain. cad8709 target-box normalization | `86c85a6f1d9eb8e7b8327d0e84a77f58403fa9259c0743e5421b995abe46c1a6` (component hashes in manifest) |
| B crop policy | v0.4 | ≤20 Oct; exact date uncertain. b2f8d95 whole-word tolerance | `86c85a6f1d9eb8e7b8327d0e84a77f58403fa9259c0743e5421b995abe46c1a6` (component hashes in manifest) |
| B crop policy | v0.5 | ≤20 Oct; exact date uncertain. 405d4f1 padding 1.5 heights | `86c85a6f1d9eb8e7b8327d0e84a77f58403fa9259c0743e5421b995abe46c1a6` (component hashes in manifest) |
| B crop policy | v0.6 | ≤20 Oct; exact date uncertain. 0.5 + row-frame text box | `86c85a6f1d9eb8e7b8327d0e84a77f58403fa9259c0743e5421b995abe46c1a6` (component hashes in manifest) |
| B crop policy | v0.7 | ≤20 Oct; exact date uncertain. crop-only line inventory and cut-off gate before length | `86c85a6f1d9eb8e7b8327d0e84a77f58403fa9259c0743e5421b995abe46c1a6` (component hashes in manifest) |
| B crop policy | v0.8 | ≤20 Oct; exact date uncertain. owner's three rules; remove target-cut veto and taller-than-upright guard | `86c85a6f1d9eb8e7b8327d0e84a77f58403fa9259c0743e5421b995abe46c1a6` (component hashes in manifest) |
| B crop policy | v0.9 | ≤20 Oct; exact date uncertain. every letter body >=95% visible for a whole neighbour word | `86c85a6f1d9eb8e7b8327d0e84a77f58403fa9259c0743e5421b995abe46c1a6` (component hashes in manifest) |
| B crop policy | v0.10 | ≤20 Oct; exact date uncertain. every h > w crop turns 90 degrees right before all detection and measurement | `86c85a6f1d9eb8e7b8327d0e84a77f58403fa9259c0743e5421b995abe46c1a6` (component hashes in manifest) |
| B crop policy | v0.11 | ≤20 Oct; exact date uncertain. main-row ink measured along its existing base curve | `86c85a6f1d9eb8e7b8327d0e84a77f58403fa9259c0743e5421b995abe46c1a6` (component hashes in manifest) |
| B crop policy | v0.12 | ≤20 Oct; exact date uncertain. small segments use every ink component in the processed crop frame | `86c85a6f1d9eb8e7b8327d0e84a77f58403fa9259c0743e5421b995abe46c1a6` (component hashes in manifest) |
| B crop policy | v0.13 | ≤20 Oct; exact date uncertain. length band 0.30–2.00 (coordinator decision under the owner's end-to-end mandate, 19 Oct 21:34; fitted on owner marks, s5) | `86c85a6f1d9eb8e7b8327d0e84a77f58403fa9259c0743e5421b995abe46c1a6` (component hashes in manifest) |
| content_gate | v0.1 | ≤20 Oct; exact date uncertain. first integrated graph implementation | `244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20` (component hashes in manifest) |
| content_gate | v0.2 | ≤20 Oct; exact date uncertain. Astra review: composed coverage, producer binding and atomic exports | `244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20` (component hashes in manifest) |
| content_gate | v0.3 | ≤20 Oct; exact date uncertain. owner gate: mixed-script word drops, unexpected script holds, before segmentation; short ordinary lines excluded before segmentation (letters); cells and numeric lines exempt with more than one letter-or-digit | `244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20` (component hashes in manifest) |
| content_repair | v0.1 | ≤20 Oct; exact date uncertain. first integrated graph implementation | `244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20` (component hashes in manifest) |
| content_repair | v0.2 | ≤20 Oct; exact date uncertain. Astra review: composed coverage, producer binding and atomic exports | `244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20` (component hashes in manifest) |
| composer | v0.1 | ≤20 Oct; exact date uncertain. first integrated graph implementation | `244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20` (component hashes in manifest) |
| composer | v0.2 | ≤20 Oct; exact date uncertain. Astra review: composed coverage, producer binding and atomic exports | `244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20` (component hashes in manifest) |
| composer | v0.3 | ≤20 Oct; exact date uncertain. PIPE032: declared routes_out_of_scope bypass correction lookup and automatic results; retain explicit non-success route evidence | `244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20` (component hashes in manifest) |
| final_eligibility | v0.1 | ≤20 Oct; exact date uncertain. first integrated graph implementation | `244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20` (component hashes in manifest) |
| final_eligibility | v0.2 | ≤20 Oct; exact date uncertain. Astra review: composed coverage, producer binding and atomic exports | `244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20` (component hashes in manifest) |
| final_eligibility | v0.3 | ≤20 Oct; exact date uncertain. cells: alnum > 1 is the only length/shape check, consistent with the gate | `244d2b2e9dd48b145d480773e77126d25e154561edbc8319d56b4796870dea20` (component hashes in manifest) |
| census | v0.1 | ≤20 Oct; exact date uncertain. first integrated graph implementation | `03e6d58369f88019bc6d64ea53ecd55ad19445c7d9a079770422529f40ebfbc3` (component hashes in manifest) |
| census | v0.2 | ≤20 Oct; exact date uncertain. Astra review: composed coverage, producer binding and atomic exports | `03e6d58369f88019bc6d64ea53ecd55ad19445c7d9a079770422529f40ebfbc3` (component hashes in manifest) |
| census | v0.3 | ≤20 Oct; exact date uncertain. bounded parallel native workers for CSCS | `03e6d58369f88019bc6d64ea53ecd55ad19445c7d9a079770422529f40ebfbc3` (component hashes in manifest) |
| census | v0.4 | ≤20 Oct; exact date uncertain. profiled CSCS throughput tuning with bounded queue lookahead and node-scale worker qualification | `03e6d58369f88019bc6d64ea53ecd55ad19445c7d9a079770422529f40ebfbc3` (component hashes in manifest) |
| census | v0.5 | ≤20 Oct; exact date uncertain. parent-confirmed collection-v2 legacy evaluation split aliases with retained lineage | `03e6d58369f88019bc6d64ea53ecd55ad19445c7d9a079770422529f40ebfbc3` (component hashes in manifest) |
| census | v0.6 | ≤20 Oct; exact date uncertain. census_03 integration: union configured heldout_crop_sha256 with observed held-out crops | `03e6d58369f88019bc6d64ea53ecd55ad19445c7d9a079770422529f40ebfbc3` (component hashes in manifest) |
| census | v0.7 | ≤20 Oct; exact date uncertain. PIPE032: bind release correction scope; export corrections_not_applied and count routed rows by tool and disposition | `03e6d58369f88019bc6d64ea53ecd55ad19445c7d9a079770422529f40ebfbc3` (component hashes in manifest) |
| inventory | v0.1 | ≤20 Oct; exact date uncertain. first integrated graph implementation | `a3c42b877f00e3798909213e43ef5f2f0682571b1fa04a33b284aa198ebef2fb` (component hashes in manifest) |

### Dataset, synthetic and builder candidates

| Date (2026) | Component / candidate | Counted / not counted / uncertainty | Evidence |
|---|---|---|---|
| Before 7 Oct; exact date uncertain | Synthetic recipe.v1 / smoke / transfer-smoke | Uncertain set lineage; smoke excluded; recipe file existence alone is not a completed full build | `greekocr/_vendor/factory/recipe.*.json`, `greekocr/_vendor/origins.json`. |
| 7 Oct | Synthetic recipe.v5 training build | Completed evaluated set; counted once when n is settled | PAGE E1 report: 203,693 rows, audit true, deficits disclosed; source recipe SHA `2f228950e9a508b5e130e82ce5b89de2b911be4a23872c3acc7f53e83c59dce7`. |
| By 7 Oct | Synthetic recipe.v6 | Uncertain; retained recipe is not completion proof | Captured SHA `24c243ecd24c7f74ad8031a1feb6092523d21788d37379c8795b0cf1f53ebec6`; build/evaluation receipt needed. |
| 7 Oct | Synthetic recipe.v7 held-out | Completed evaluated set; separate evaluation-only generation | PAGE E1 report: 2,399 reserved rows; recipe SHA `4fbf257172cab1255fd068e37b1a6cac11b5f2fb84ecce83da0136a9150fb87f`. |
| By 16 Oct | Synthetic recipe.v8 | Evaluated set, exact original build identity still needed | PAGE E2 notes; source SHA `ba6faace28b1cd3ecd019ae00a43cc7a9ae79bcca0c75f75ce7b89e1214b7351`. |
| 20–25 Oct | Synthetic recipe-v5 codec-v2.1 clone / MIX1D-8d25940f-export-001 | Current train build used; val/reserved may be different builds; do not add nominal counts as verified shards | TRAIN_FULL package and release PLAN §0: prepared005 train 190,486 rows / 47 shards. Need original BUILD identities for a complete generation count. |
| 7 Oct | O1d/import-real/o5-docs-v1 | Completed used real dataset candidate | PAGE E1_REPORT_run4: train19,657/dev359/test3,600; later collection lineage may include these observations. |
| By 16 Oct | collection-v2 / v2-asis | Completed used dataset; release alias continuity | PAGE E3_RESULTS and E4_WAVE1A_RESULTS, release `af1ff90200e8ad897e246192da9a420a15fec2793fbc987649dbf2ff77d81621`. |
| By 18 Oct | v2-codec / recovered rows | Completed used dataset; distinct representation, needs component-generation convention reconciled with old v2 alias | PAGE E4_WAVE1B_RESULTS, release `ef64d8b70f5bc946201a0d082c8ca0b711f0abefe1c1b12b46c82473f840175d`. |
| 20 Oct | release v3 / REL3 | Completed dataset + builder round | `docs/harvest/collect_v3_admission/release_v4/inputs/RELEASE_V3_RECEIPT.json`, status ok; package `59d2de211ef8864df7517f9cba1d986a773bccb07ba3017561047700222ed148`. Earlier REL3.md is a pre-execution handoff, not the terminal record. |
| 21 Oct | release v4 / REL4 | Completed dataset + builder round; preserved v4 alias | `docs/programme_20261019/SIMPLIFICATION/v4/RELEASE_CHECK.md`: 3713178 completed, receipt `dbc99bdc7fd9c770e25880139ef3bd3184392bfe65e1eb2baf89544c8e390f32`, source `b083574d4e71ddaf771f2152d6ee19741526fc6d`. |
| 24 Oct | staging-v4 HF snapshot | No extra generation for upload/rename of same population | `docs/programme_20261019/registry/HF_REPO_SPEC.md`: `8ee9cb2e4c880f450c69b9c45cd683765d4da755`; contains pages/raw responses, not v4 line images. |
| 25 Oct | harvest-20261025 (+ Gennadius), prepared005 union | Harvest used; union runtime used; public combined build still pending. Exact builder/set count uncertain | release PLAN §0, TRAIN_FULL package/runtime `21b92bdf…`; step 4 must reconcile identities, not infer them from the branch name. |
| 28 Oct | release_v0 public builder | Not yet a completed full-population round | Other Sol run owns `scripts/release_v0/`; retain as candidate until its completed build/evaluation receipt. |

Historical generator code revisions are **not** derived from recipe names or from dataset build count. A captured commit proves source identity at one point, not the number of prior evaluated generator revisions. These uncertainties, including C1/T1′ and wave1d/e identity, are grouped in `docs/programme_20261028/RELEASE_v0/GAPS.md` with what would settle them.

## Evidence byte identities read for this register

These SHA256 values bind repository records used here; PAGE copies preserve reviewed results; two URL-redacted public copies and their original source SHA256s are bound by `scripts/release_v0_publish/PUBLIC_EVIDENCE_RECEIPT.json`. The mutable execution ledger is bound at publication, after the coordinator commits its final bytes.

| Record | SHA256 |
|---|---|
| `docs/A_ocr_development/MODEL_GENERATIONS.md` | `1e34e87c3d82f7db6f8281c28e117c3c87d79cf406a3ddea2a281c5933e24b19` |
| `docs/harvest/line_pipeline/tool_versions.json` | `ed81e3a1b7389c3dd4d29706e5e2ff2b6d0d34fa0648a9587388a25be2725831` |
| `docs/programme_20261019/SIMPLIFICATION/wave2/RESULTS.md` | `9ab804cf7a55f43664bcd22a5c97e5548a62b614142bb6af0f7ad3ea473266a9` |
| `docs/programme_20261019/SIMPLIFICATION/task2/TASK2_RESULTS.md` | `183fef83d45d9811ddebdb7036b6bb1d617595a45fb932484936eb518c04209c` |
| `docs/programme_20261019/SIMPLIFICATION/s1/S1_RESULTS.md` | `723bde57b4b570725e9a0f6873c33c501152bd228876fa73246cd2a683a42ef4` |
| `docs/programme_20261025/TRAIN_FULL_v1/EXECUTION_STATE.md` | hash recorded at publication; `MODELS.json.execution_evidence.publication_sha256` (coordinator fills) |
| `scripts/release_v0_publish/evidence/PAGE/docs/ocr_program_2026-10-06/O1_NOTES.md` | `f80ddbfd77ac5a4ab68552b4f2a70711ea3975ed4af08a754c667a37a53592eb` |
| `scripts/release_v0_publish/evidence/PAGE/docs/ocr_program_2026-10-06/O2_NOTES.md` | `7c994b0849edfe97555f8386a31c2ef02cb75431544075ad5b8f4a29f8aee4a4` |
| `scripts/release_v0_publish/evidence/PAGE/docs/ocr_program_2026-10-06/O4a_NOTES.md` | `30d730877b7f5d9459e27807897f2aca9ed59c9262554d74badce282adb59409` |
| `scripts/release_v0_publish/evidence/PAGE/docs/ocr_program_2026-10-06/O4b_NOTES.md` | `c4c21432bef4619c28eda46c854f97419414dce8acfc549275c2f7990bcce677` |
| `scripts/release_v0_publish/evidence/PAGE/docs/ocr_program_2026-10-06/O4b_ANEMI_NOTES.md` | `45d5586264ce5c15038ea462424e0d16c8f84f68fcc2e66974273fee9a34271f` |
| `scripts/release_v0_publish/evidence/PAGE/docs/ocr_program_2026-10-06/O4c_NOTES.md` | `a1da4f689622b6ea2fafb1782edd87029245a2efa4fa003bc4eb892968a652f1` |
| `scripts/release_v0_publish/evidence/PAGE/docs/ocr_program_2026-10-06/O5_NOTES.md` | `6200f96e6d12518fd479bc28f63c79fa52b0ace7d324849fcc91608bbda9acb0` |
| `scripts/release_v0_publish/evidence/PAGE/docs/ocr_program_2026-10-06/O6_NOTES.md` | `767bcb69896255a32968cf043f668cd024cfecdf5171517c1d7b7edf3ee6ef69` |
| `scripts/release_v0_publish/evidence/PAGE/docs/ocr_program_2026-10-06/E1_REPORT_run4.md` | `3b7920ea7cf056006cce7d4fd1952d0136f315b640810e83adfb063e6439a59b` |
| `scripts/release_v0_publish/evidence/PAGE/docs/ocr_program_2026-10-06/E1_NOTES.md` | `4f39cc437ea6c0bbf656b3ba481a7545bad1235d1a6883227f3bc9604a56ab5c` |
| `scripts/release_v0_publish/evidence/PAGE/docs/ocr_program_2026-10-06/E2_NOTES.md` | `4de7f2d7685837f7d92d9b94014e38e348c1a4b1bef2107af1e80ed7f08d2a60` |
| `scripts/release_v0_publish/evidence/PAGE/docs/ocr_program_2026-10-06/E3_RESULTS.md` | `94b7f7acf036f34fe0069c2b70efc7361ebc153ecf8291b57806cebd2aaa35cd` |
| `scripts/release_v0_publish/evidence/PAGE/docs/ocr_program_2026-10-06/E4_WAVE1A_RESULTS.md` | `b879bf71687495ebb750ccb1d39fe1f8170a85d825b63f20b5eb6fac2a07d887` |
| `scripts/release_v0_publish/evidence/PAGE/docs/ocr_program_2026-10-06/E4_WAVE1B_RESULTS.md` | `ce791ba4f454b5164a74e709e255b09f30dc2dbca990ef29c453fd6d693115fc` |
| `scripts/release_v0_publish/evidence/PAGE/docs/ocr_program_2026-10-06/HANDOFF_20261018_coordinator.md` | `38e4379e9222d97cf233048294df0b503e5538f58bf5ac17d5f3ecde993b44c7` |
| `scripts/release_v0_publish/evidence/PAGE/docs/ocr_program_2026-10-06/PLAN_GLOSSAPI_v3_20261007.md` | `076df3eef3efed18519849e76e073201f0354c76a7ee376133dcaaa81f3a66fd` |
| `scripts/release_v0_publish/evidence/PAGE/docs/prereg_t1prime_pilot.md` | `a9a6f9cba49532b961ca06a78a6b83ca990a43bee71a46d5c1d4d82e9674c945` |
| `scripts/release_v0_publish/evidence/PAGE/docs/reviews/fable_t1prime_result_cert.md` | `78078bd1799a2f3b90a0eafadba3c20e4721a397aa22c9af4f18e8e22beb91c1` |

Publication evidence closure: `scripts/release_v0_publish/EVIDENCE_PATHS.txt` enumerates retained files, including both PAYLOAD-bound sealed packages and the local attempt013/014 config/CLAIM/PLAN bindings in MODELS.json. `scripts/release_v0_publish/REQUIRED_EVIDENCE.txt` names cited files absent from the current commit; the coordinator must commit them before building the publication candidate. The mutable execution ledger SHA is recorded at publication, never inferred from an earlier snapshot.
