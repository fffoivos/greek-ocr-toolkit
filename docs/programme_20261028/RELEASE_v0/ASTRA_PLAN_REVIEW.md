# ASTRA — independent release-plan review

Date: 28 October 2026, Europe/Athens. Scope: the proposed public release of Greek OCR models, line data and code; **a review of the plan, not certification of results or publication readiness**. This is the single requested plan review. The coordinator disposes of the findings and fixes BLOCKER/HIGH before execution; MEDIUM/LOW may be logged and deferred. This report does not request another plan-review cycle.

Read-only inspection, except this report: local documents, source, saved receipts, source diffs and Git ref metadata. No network, SSH, jobs, background processes, inference, test suites, credential access or publication. Remote completion, actual remote payload bytes, current Hub state/limits and public URLs were not independently verified. Saved receipts are identified as such below.

## Inputs read and binding

The first three inputs were read in the requested order. Paths below are repository-relative unless explicitly marked otherwise; selected evidence/code sections were read where indicated.

| Input | SHA256 |
| --- | --- |
| `docs/programme_20261028/RELEASE_v0/OWNER_BRIEF.md` | `281f3edeb34a77368d02b611c82bd8680e0f94f6689a1106e3cb5718e5de8d98` |
| `docs/programme_20261028/RELEASE_v0/PLAN.md` | `5c3f56b47258ab41f125eef1bc3fac22ad4a0106b14afa658279d13f86bb5d2e` |

Other inputs:

- `docs/programme_20261019/registry/HF_REPO_SPEC.md`, including its schema, authentication, acceptance and later registry amendments; targeted matches in `HF_BUILDER_PLAN.md` and `HF_PHASE1_PACKAGING.md`.
- Root `AGENTS.md`; `docs/programme_20261025/TRAIN_FULL_v1/{OWNER_BRIEF.md,STAGE_C.md}`; selected execution-ledger entries through 28 October 11:22 EET and population/recipe passages in that programme's `PLAN.md`.
- `docs/A_ocr_development/{RECOGNISER_AND_TRAINING.md,MODEL_GENERATIONS.md}` and `docs/harvest/line_pipeline/tool_versions.json`.
- `greekocr/deploy/docling_plugin/recognizer/{inference.py,model.py,VENDORED_FROM.json}`; diffs of `greekocr/_vendor/train/{model.py,data.py}` against the Stage C copies.
- Selected Stage C package sections: `prepare.py`, `run.py`, `stage_c.py`, `full_hook.py`, `selection_diagnostics.py`, `vendor/train/{train.py,s1_segment.py,eval_cer.py,ckpt_io.py}`, `PAYLOAD.json`, `vendor/UPSTREAM.json`, `adopted/w1-h13.json`, `x1_parent_payload.json`.
- Selected fields and aggregate counts from saved `out/TRAIN_FULL_v1/receipts_005/{data_prepared_runtime.json,data_manifest_AUDIT.json}`; factory schema/build-receipt code in `greekocr/_vendor/factory/src/{shard.rs,build.rs}`; source matches in `line_pipeline_sources.py`; `tests/test_size_guard.py` **read, not run**.
- Local Git identities for `main`, `train-full-v1`, cached `origin/main`; selected O5/O6 notes and E1 report passages in sibling `../greek-page-ocr/docs/ocr_program_2026-10-06/`. Those historical excerpts do not establish a complete generation count.

**Verdict: HOLD — eight HIGH findings must be resolved in the plan before autonomous execution; no BLOCKER is asserted.**

## Findings — most severe first

### H01 [HIGH] The proposed real population does not match the population that trained these models

**Where:** PLAN §0, §3 real-image/training fields, §8 “Training-data link”; owner item 3 (“all the lines, with the metadata we have already agreed”).

**Evidence / failure scenario:** The plan identifies the v4 real input as **364,173**. The actual saved prepared005 audit used by Stage C identifies **364,871 S1 v4 input rows**, retaining **364,870** after one train/eval crop removal. It retains **428,357 harvest train rows**, making **793,227 real train rows**, plus harvest dev **16,350** and test **52,847**; seal04 is an additional **437 dev / 2,253 test** instrument. These counts also appear in the training programme's plan and Stage C reuse contract. The 698-row difference between the two input populations is not explained by calling both “v4.” Publication from the older 364,173-row factory pool can omit training members even if every uploaded file passes SHA verification.

The plan stores one `image`, two image hashes, one text and a `used_in_ocr_v0_6` boolean. A hash of a second image is not its payload or a locator; a boolean does not identify the consumed label/image variant, original-to-factory ID, pool order, sampling configuration or per-model use. “Available,” “eligible,” “drawn for training,” and “used for evaluation/selection” must not collapse into that boolean. The saved runtime distinguishes real component pools and a 50% synthetic mixture; the factory remaps harvest IDs to `harvest:<wave>:<id>`.

**Fix:** Bind the release builder to the exact prepared005 manifest/runtime and the final run bindings, alongside the older registry inventory. Reconcile the 364,173 versus 364,871 populations by keys and exclusion provenance; retain wider dataset observations separately from actual training membership. Publish exact original and trainer image variants, exact trainer labels/codec, portable locators and keyed per-run membership (a convenience boolean may remain). Preserve original pool ordering, mixture/seed/config identities where continuation is claimed. Require keyed population/variant reconciliation, not merely counts or file checksums. Recheck the saved binding against the final remote runs during execution; this review has not done so.

### H02 [HIGH] The claimed “agreed spec, licence removed” drops substantially more than licence

**Where:** PLAN §3 layout, real-line fields and card; step 4/B acceptance. Compare `HF_REPO_SPEC.md` “Schema and joins,” “Repository layout,” “Dataset card draft,” and the 23 October registry amendment. Owner items 3, 4 and 5 preserve agreed metadata and page position while removing licence.

**Failure scenario:** The earlier contract is relational; the new field list is not an equivalent replacement. The following obligations have no explicit destination or retention rule:

| Agreed information | What the plan loses or leaves undefined |
| --- | --- |
| Original observation identity and joins | `(parent_id,row_id)`, stable `row_key`, primary `box_id`/`crop_id`, alias and box-contributor lineage; `id` alone has no declared namespace. Equal payload hashes must not merge editions or observations. |
| Whole-book policy and exact line instruments | `source_book_id`, `source_split`, assignment labels/status/exportability, aliases and split provenance; exact `lqb_row`/`release_excluded_row`, list names/hashes and `row_instruments`. A registry SHA plus `harvest_protection` cannot replace them. Unknown/conflicting assignments must remain explicit and must not default to train. |
| Labels and corrections | Raw text itself and raw field, independently selectable raw/census/overlay/factory label versions, real-line `gt_nfc`, `gt_nfd`, `label_ids`, `codec_version`, correction bindings and label-version relations. `raw_text_sha256` cannot recover the raw text. The enum `release=v4|harvest-20261025` does not even describe the included seal04 rows. |
| Geometry and page coverage | Page acquisition/failure records; raw versus derived box kind; frozen segmenter run/config/model; emitted order versus geometric order; requested-page outcomes `ok/zero_detections/error/not_run`; source-object and response-representation identities. All boxes and failed/excluded pages must survive even without a line crop. |
| Page-frame qualification | Document AI dimensions/transforms, raster frame, mapping status/evidence and valid coordinate transforms. Merely naming `coordinate_frame` does not preserve the evidence removed with the raw responses. The known 194 dimension mismatches are not an exhaustive test: equal dimensions can also have transforms. |
| Feature semantics and versions | Feature records keyed by row + label variant + feature version; bucket counts as well as percentages, raw/NFC lengths, named scripts, scoped provider language/confidence, normalized box centre, crop variant, code/codec/Unicode provenance. The agreed non-whitespace NFC denominator and script/polytonic rules are not restated or explicitly inherited. |
| References and coverage | Raw/corrected seal04, `diagnostic_only` and historical exposure qualification; v2 common/full coverage memberships; validation memberships/payloads; the seven-row census-versus-old-v4 difference; coverage and source-search receipts. These are more than five split directory names. |

This permits a byte-perfect but semantically incomplete dataset, ambiguous overlays on scans, and lost split/exclusion evidence. Keeping all decision reasons in JSONL does not by itself recover omitted images, references, joins or label variants.

**Fix:** Add a field/relation crosswalk from the agreed spec to the new layout, explicitly retaining every non-licence obligation or recording a justified amendment. New filenames and denormalized convenience views are fine. Preserve public, sanitized geometry/provenance tables when raw Google payloads stay private; never advertise private raw locators as publicly loadable evidence. Unresolved frames retain their source coordinates and status without guessed rescaling. Add semantic acceptance: source-key/status/reason coverage, foreign keys, split/instrument reconciliation, exact payload/label identities, reference memberships, and the already-agreed independent feature check. Retain unknown/missing bytes explicitly. Checkpoint B's sample rows and SHA checks alone cannot establish those properties.

### H03 [HIGH] Synthetic source and provenance promises exceed the identified source

**Where:** PLAN §0 synthetic input, §3 synthetic fields/RECIPE and §6 first gaps; owner item 6 (“distribution … particular functions applied … where it originated”).

**Evidence / failure scenario:** `stage_c_package/prepare.py` reads only the synthetic **train** role into prepared005. The saved runtime identifies **190,486 rows / 47 files** in its synthetic pool, not the additional **9,208 val / 3,999 reserved** promised in the release. Its source build is pinned separately under `scaling_w3/mix1_runs/MIX1D-8d25940f-export-001/prep/A12`. The earlier spec names another historical source tree and explicitly requires reconciliation, not substitution by recipe name.

The inspected factory row schema records operation names, font stem, source dataset/doc, etc., but not full font SHA, generator SHA, seed or source-text locator. Its build receipt records font **sha16** and **both** source and effective recipe SHA. The earlier spec explicitly warned that historical details may be unavailable. The new plan drops `recipe_effective_sha256`, generator code/binary distinction, source-text locator, `provenance_completeness` and `historical_unknown_fields`, while presenting the remaining new hash fields as unconditional. A current recipe/font or a hash of the normalized rendered label would not establish historical source-text/font identity. I have not inspected the remote manifests; full hashes may be recoverable there, so their absence globally is a **risk, not a finding of nonexistence**.

**Fix:** Name immutable sources for all three synthetic roles and reconcile their build/codec identities; do not manufacture missing splits. Publish the frozen source and effective recipes/build manifests and an operation-name-to-function/source mapping, preserving operation order and variants. Separate calculated fields (`image_sha256`, dimensions, `n_ops`, label hash) from recovered historical provenance. Allow nulls with specific unknown reasons/search receipts where the historical origin cannot be established. Restore the omitted provenance fields. Compute configured versus realized distributions by split from the actual released files. Keep missing per-operation parameters/seeds as disclosed gaps, with no promise of deterministic regeneration.

### H04 [HIGH] Three incompatible checkpoint-selection descriptions remain

**Where:** PLAN §3 card (“seal04 references are reporting-only”), §4 card (“selection on seal04_dev / pooled dev”), §4 selected checkpoint (“CER checkpoint … the run's selection rule”); owner standing rule: “test sets are reporting only and never select anything.”

**Evidence / failure scenario:** Stage C installs the exact seal04-dev437 loader for `best.pt` (`run.py:41–51`, `stage_c.py`). `vendor/train/train.py:1211–1229` evaluates it **every epoch**, selecting by strict improvement; `STAGE_C.md` explicitly distinguishes **eight epoch selection evaluations** from **four full-panel CER archives**. The latter are 25/50/75/100% reports and use a distinct evaluation/reference path (`full_hook.py:18–55`). Stage B hyperparameters were chosen on **pooled dev**, a third role. Choosing the best of four archives is not automatically the same as the run's best of eight epochs, nor does equality of the selected final checkpoint prove identical selection rules. Calling all seal04 reporting-only is false for seal04_dev.

**Fix:** Decide and record one release-selection contract now: exact candidate checkpoints, exact dev instrument/labels/scorer, tie rule, selected step and weight SHA for each width. Either preserve the trainer's epoch-best rule or explicitly identify a separate four-archive release rule; do not call the latter inherited. Explain pooled dev as the hyperparameter-selection rule where appropriate. Bind every reported prediction/score to the selected weight hash; if predictions are absent for an epoch-best checkpoint, produce them after the dev-only choice is fixed. Correct the dataset card: seal04_dev was used for selection; seal04_test and harvest_test are report-only, with inherited exposure caveats. No test loss/CER, error category, example or outcome may change checkpoint/model choice, stopping, preprocessing, thresholds or the release rule.

### H05 [HIGH] Twelve full-state files plus a batch-plan hash are not a usable continuation package

**Where:** PLAN §4 `training-state`, §8 “Exact continuation.”

**Evidence / failure scenario:** The four CER archives are copied `segment.pt` states (`full_hook.py:244–253`). The frozen loader in `vendor/train/s1_segment.py:25–59` verifies exact argument/code/data bindings and reads content-addressed **`segment_artifacts/<digest>`** for the checkpoint's ancillary epoch files. `save()` records those dependencies at lines 87–108. The plan uploads only the 12 checkpoint files and a SHA manifest; the referenced artifact objects are omitted. Resumption can therefore fail before an optimizer update even with all weights/optimizer/RNG fields present. Re-sharding/reordering data and consolidating source also change bindings checked by this loader. A batch-plan hash cannot reconstruct missing bytes or ordering.

**Fix:** Define the closure of each resume state: all referenced `segment_artifacts`, frozen runner/source seal, authoritative per-run config, codec, runtime/pool manifests and order, data-byte mappings, environment and checkpoint metadata. Preserve that closure without editing the historical checkpoint. If only archival optimizer states will be public, label that limitation and stop implying standalone exact continuation. Keep inference export separate from segment-state conversion, whose metadata shape differs from `best.pt`. Bind `main` and `training-state` by **separate immutable commit IDs** in the release manifest/card: one tag on one branch does not pin the other branch.

### H06 [HIGH] HF rename/create/upload steps cannot execute in their stated order

**Where:** PLAN §3 repository hygiene versus §7 steps 4–5.

**Failure scenario:** §3 correctly says rename old → create fresh → upload → verify → public. Step 4 uploads to “the new private repo” while the old repo still owns `fffoivos/greek-ocr-lines`; step 5 only then renames the old repo. No temporary destination or creation step is specified. An idempotent create/upload against the occupied name can write into the old repository and later expose its private history. Moving branch contents to `main` is not history isolation.

**Fix:** Choose one explicit, non-destructive cutover sequence and use it everywhere. Before moving anything, pin the source branches/commits and verify archive-name availability. Rename the old repo, verify it remains private, create and verify a genuinely fresh private repo under the intended name, then upload only the public manifest-listed payload; or specify a distinct temporary repo and a fully defined later cutover. Verify actual repository identity, redirect/name-reuse behavior, visibility and full ref/history inventory before making public. Do not treat “create if exists” as a fresh-repo guarantee. Hub rename/name-reuse behavior is unverified in this offline review; resolve it at the operational preflight, retaining the private archive on failure. Pin all source reads so the rename cannot silently retarget them.

### H07 [HIGH] “Squash on main” and a tip-size guard do not define a safe public Git history

**Where:** PLAN §2 push/receipt move and §7 step 3; `tests/test_size_guard.py`.

**Evidence / failure scenario:** Local `main` is **`e1d67490f…`**, while the cached public `origin/main` is **`89821975b…`**, whose commit message describes the 20 October public squash. They are not interchangeable starting points. A new squash atop local `main` still carries its old ancestors. The read-only size-guard source inspects **index blobs**, not all newly reachable history. It cannot detect old >100 MB blobs or private content in reachable ancestors. Conversely, squashing history does not sanitize private material present in the new snapshot, including uncommitted files swept into it. No actual leak is claimed by this review.

**Fix:** Explicitly build the publication commit on the freshly verified public main head, without merging private ancestry or pushing private branches/tags. Inspect the candidate commit's parents and newly reachable object set as well as its final tree; apply the 5,000,000-byte guard to the actual publication snapshot. Use a reviewed public-file inventory to exclude raw Google payloads, credentials and private operational material from that snapshot and HF upload roots. Publish only intended refs, then read back the resulting public commit. For receipts, copy and verify destination bytes first and retain a retrievable custody manifest; distinguish untracking from deleting local data, which remains the owner's decision. Do not use a local snapshot-only test as evidence of history hygiene.

### H08 [HIGH] The future squash is incorrectly presented as the commit that trained the models

**Where:** PLAN §2 consolidation, `MODELS.json`, “tag v0.6 = the commit whose training code produced the models”; §4 training-code link; step 2 executor.

**Evidence / failure scenario:** The models predate the proposed consolidation/squash. The inspected Stage C payload records `producing_commit=e1d67490f…` **and** `source_state=UNCOMMITTED_PREPARE_ONLY`; its upstream record separately names trainer commit `71e72bfb…` and a patch. Thus even an old base commit alone is not the complete producing-code identity. The live ×1 replacement also differs from the sealed `adopted/w1-h13.json` still in the listed package; the execution ledger explicitly says attempt014/h14 replaces attempt013/h13. A release assembled from the convenient package defaults can describe or reproduce the retired run.

The source diff confirms substantive width support in the Stage C `model.py`; `data.py` differs only in an import at the inspected point. “Consolidate” does not establish which source wins across the complete trainer/heads/evaluation/continuation paths, or whether sealed packages remain executable records. Changing their imports in place would destroy their seals. Step 2 also assigns a **commit** to Sol, contrary to the owner/AGENTS division of roles.

**Fix:** Separate `training_source` (original base/upstream commit, exact payload/code SHA inventory, patches, run attempt/config and source-state qualification) from `release_code_commit` (the new public squash and consolidation mapping). Preserve frozen packages unchanged in a hash-verifiable, accessible archive; a pointer to an inaccessible private commit is insufficient. Specify that the executed numerical implementation is the source of truth and limit consolidation adaptations to documented packaging/import changes, with numerical/preprocessing/decoding equivalence evidence on dev inputs. Bind attempt013 ×1.5/×2 and final attempt014 ×1 individually; exclude h13. Move the commit action to the coordinator. The new tag can identify the release containing the producing source; it cannot retroactively be the commit used to train.

### M01 [MEDIUM] Docling verification is correctly intended but scheduled before the final artifact exists

**Where:** PLAN §2 load test, §7 steps 2/3 versus 6/7; `recognizer/inference.py:48–57` and `recognizer/model.py`.

**Failure scenario:** The current plugin builds its own fixed-width model and does not pass `width_mult`. The Stage C model supports ×1.5/×2. The plan acknowledges a migration and promises to test every released safetensors, which is the right direction; however, step 2's test precedes step 6's export, while step 6/C only requires SHA/card checks. Testing earlier weights through a helper would not prove the final Hub config/codec/weights load through the real plugin. Serving returns NFC while stored evaluation hypotheses are NFD; preprocessing and precision also have explicit profiles.

**Fix:** Make export → actual plugin load → pinned dev prediction comparison a dependency before publication, or prove that later export is byte-identical to the tested artifacts. Exercise all three width/config/codec combinations through the actual Docling recognizer path, strict state loading and codec binding. Declare comparison normalization, input-byte/preprocessing profile and precision; do not “fix” parity by changing training or selecting examples on test. Keep this bounded loading gate distinct from the owner's later full Docling/pipeline phase. No present loader success is asserted here.

### M02 [MEDIUM] v0.6 and component/tag semantics remain provisional decisions

**Where:** PLAN §1 and hard-coded `v0.6`/`used_in_ocr_v0_6`; owner item 8.

**Failure scenario:** The plan already requires a history check, so the provisional count is not itself a demonstrated error. However, its grouping omits an explicit disposition for completed E4 wave1b, groups unlike rounds together, and treats a deployed C1 recognizer as a distinct pre-E1 training generation without a checkpoint lineage citation. Selected O5 notes contain an incumbent and paired training work; O6 includes segmentation preparation. Counting names alone would overcount nontraining work or double-count checkpoints. The read `MODEL_GENERATIONS.md` is a **segmenter** record, not an OCR generation register; detector generation 3 and B crop policy 0.13 are different components.

“The same string is the git tag” is also ambiguous in a monorepo with independently versioned components. The component list does not explicitly cover existing `content_repair`, `composer`, `final_eligibility`, `census` and `inventory` versions in `tool_versions.json`.

**Fix:** In step 2, settle a documented generation-counting rule and complete the evidence table, including inclusion/exclusion of these rounds and existing components. Parameterize the resulting OCR version throughout fields/tags/cards instead of forcing six after the check. Preserve aliases. Define component-qualified Git refs where needed while retaining the owner's `v0.n` version value; distinguish model, dataset, generator, generated set and pipeline/tool versions. This does not require a new owner approval gate.

### M03 [MEDIUM] Credential handling is weaker than the already agreed process

**Where:** PLAN §7 final sentence (“HF token already configured there, never printed”) versus owner standing credentials rule and `HF_REPO_SPEC.md` authentication section.

**Failure scenario:** “Already configured” may mean an ephemeral environment, which is compatible, or persistent login/token files, which are not. “Never printed” alone does not prevent argv, shell tracing, scheduler export/spooling or credentials entering a build receipt. No credential was read and no existing violation is alleged.

**Fix:** Explicitly inherit the spec's separation: pinned private-source download, credential-free CPU builder, separate foreground upload with ephemeral Keychain/environment injection. No auth-login persistence, token files, `--token`/SSH argv, environment dumps or scheduler token export. Do not inspect/retrieve an HF token on Clariden; use the approved launch-time channel. Check metadata/receipts without logging secrets. If that channel is unavailable, retain the package and resolve the channel rather than persisting a credential.

### M04 [MEDIUM] Exact-book source coverage and several derived fields lack source mappings

**Where:** PLAN §3 real source/geometry/features; owner item 5 (“source as a detailed way to find the exact book”).

**Failure scenario:** The proposed source field names are appropriate, but no source-to-field map proves title/year/item/page/URLs/source-record hashes exist across old v4, all harvest waves, Gennadius and references. The factory schema itself has dataset/doc identities, not complete bibliographic or page geometry records. A title and year may still identify multiple editions/volumes; a source-record hash without a public locator is opaque. New-harvest page scans/boxes also need explicit sources beyond the old staging package. This review cannot establish remote availability or URL validity, so these are coverage risks rather than claims that the fields are absent everywhere.

**Fix:** Bind source adapters/manifests for each population, carry exact provider catalogue/item/edition/volume identity and page-number convention, and give each public record a useful locator plus hash. Derive geometry/features only from their qualified source/label variants. Record nulls and coverage by source where unavailable; distinguish recoverable metadata work from historical gaps. Do not fabricate precise provenance to fill a required column or claim exact-book discoverability without evidence.

### M05 [MEDIUM] The gap process adds a blanket rule and weakens the owner's discretion

**Where:** PLAN §6; owner item 7.

**Failure scenario:** The owner asked to collect gaps, review them together at a checkpoint and avoid overdoing issues. The plan adds “it is not fixed mid-task” for **any** documentation/provenance gap and mandates one issue per real gap. Applied as an execution rule, that could defer H01/H02/H08 defects simply because they involve provenance. This review's explicit “don't fix it here” is appropriate for this review and is not a blanket ban on coordinator-authorized fixes. The owner also explicitly referenced gaps 1–2, including the dropped licence column; the plan silently excludes the latter from issue handling.

**Fix:** Keep collection and checkpoint triage, but distinguish release-critical corrections from future historical improvements; group related gaps and defer/no-issue trivial or resolved entries. State that mandatory report-only reviewer scope does not prevent execution fixes under the coordinator's authority. Record licence removal as intentional and preserve the disposition of the specific gap the owner referenced (including any residual provenance limitation); never restore a licence column or invent a licensing gate against item 5. Do not convert “don't overdo it” into automatic issue creation.

### M06 [MEDIUM] The dependency graph leaves the ×1 handoff and post-release work without an executable endpoint

**Where:** PLAN §7 steps 0–1, 8 and checkpoint-cycle paragraph; owner items 3, 4, 6 and 9.

**Failure scenario:** Step 0 waits for ×1, whereas step 1 says ×1.5/×2 now and ×1 when ready. A literal sequential executor will delay work the owner asked to start. Step 8 records the right PDF outputs but gives no executor or acceptance and calls the whole next phase a separate plan; execution can stop after publication even though the owner said “After all this is done we will start” the pipeline/Docling/glossAPI work. The generic re-review loop could also be misapplied to this one-time plan review.

**Fix:** Make the already-complete model work and shared dataset/code preparation independent of ×1's completion, and specify how ×1 is added without moving an existing release tag. Define the final three-model release barrier. Assign creation and commencement of the next phase to the coordinator, under the existing authorization and applicable launch constraints. Carry the two exact PDF paths from the brief into that handoff, with numbered detection overlays, per-line crops/text, per-page text and failure/drop visibility. Preserve the owner's “.docx is not a transcription” answer. State that later artifact reviews A/B/C are distinct from this single plan review; do not add another plan-approval gate.

### M07 [MEDIUM] Hub byte integrity is specified, but resource/config/ref acceptance is incomplete

**Where:** PLAN §3 sharding/configs, §4 model storage, §7 publication gates and §8 size estimates.

**Failure scenario:** The ≤1,000,000,000-byte shard target is sensible, but a row-count estimate does not enforce closed-file size. Singleton tables, decision logs and manifests can grow independently. There is no total/per-directory file inventory or installed-uploader capability check. The old 40.7 GB staging estimate includes raw Google/metadata archives, so it is not a measurement of public page rasters alone. Full-download verification also needs separate disk/inode/time headroom. “Public URL loads; tag set” does not prove main-only refs, archive privacy, immutable tag targets, working dataset configs or model/collection linkage. Current HF service limits and rename semantics were intentionally not looked up here.

**Fix:** Before execution, inventory closed-file sizes, total/per-directory counts, repository bytes, build/readback scratch and installed Hub client capabilities; check current service limits in the execution session. Retain the agreed shard cap across all applicable artifacts and define overflow paths for single tables, keeping configs/manifests in sync. Verify the exact candidate commit with full path/byte/SHA inventory and semantic gates from H02, then verify public visibility, archive privacy, final refs/tags, config loading/image joins and collection links. Pin model and dataset commits in cross-links; never move an already published release tag. These are completion checks for the promised release, not new scientific thresholds.

## GAPS

This is the requested gap ledger **inside this report**. Nothing listed here was fixed and no GitHub issue was filed. Rows refer to findings above rather than creating additional counted findings. The coordinator should batch related entries; historical unknowns may be deferred, but the associated HIGH plan defects must be resolved before execution.

| Gap / what | Where | Impact | Fix / disposition |
| --- | --- | --- | --- |
| No crosswalk from the agreed relational contract to the new schema | PLAN §3; HF_REPO_SPEC schema/reference sections | Lost labels, geometry, reference memberships and split provenance | H02: publish a complete retention/amendment map and acceptance contract. |
| Old v4 versus S1/prepared005 identity difference is unexplained | PLAN §0; saved005 audit/runtime | Published dataset may not reconstruct the trained population | H01: keyed reconciliation, consumed variants and exact membership. |
| Historical per-operation parameters and per-line seeds not retained in listed rows | Synthetic table and factory shard schema | Exact rendering replay cannot be promised | H03: disclose unknowns; grouped future generator-provenance issue, without regenerating historical pixels. |
| Full font/source-text/generator identities and effective recipe coverage are not demonstrated | Synthetic table; factory build receipts; earlier spec's explicit caveat | Guessed historical provenance or wrong configured distribution | H03: recover from bound manifests if possible; distinguish sha16, full SHA, label hash and source-text identity; null with search receipt otherwise. |
| Synthetic val/reserved source binding omitted | PLAN §0 versus prepared005 train-only pool | Incomplete or mixed-generation synthetic release | H03: bind retained original splits/builds explicitly. |
| Public source-record/geometry evidence after raw-response exclusion is unspecified | PLAN §3; 194 known dimension mismatches | Consumers cannot locate books reliably or place lines correctly on scans | H02/M04: sanitized public metadata, frame status and exact source locators; retain unresolved cases honestly. |
| Selection descriptions and diagnostic/exposure terminology conflict | PLAN §§3–4; Stage C selection/reporting paths | Wrong “best” or misleading holdout claims | H04: distinguish Stage B tuning, Stage C selection, release choice and reporting; preserve historical exposure qualifications. |
| Resume-state dependency closure omitted | PLAN §4/§8; `s1_segment.py` | Optimizer files present but continuation fails | H05: archive dependency closure or narrow the continuation claim. |
| Producing source versus later release commit not separated; ×1 package default is retired h13 | PLAN §2; payload source-state and execution ledger | False reproduction instructions and model provenance | H08: exact run/source seals plus a separately named public release commit. |
| OCR generation register and complete per-tool/tag mapping absent | PLAN §1; existing tool manifest | v0.6 or tool versions may be mislabeled | M02: evidence-based generation ledger and tag namespace before tagging. |
| Credential channel and deployment/export parity contract underspecified | PLAN §7 and §2 | Possible persistent authentication or untested final loader artifacts | M01/M03: explicit existing auth boundary and final-artifact load verification. |
| Licence-gap disposition differs from the owner's referenced gaps 1–2 | OWNER_BRIEF item 7; PLAN §6 | Intentional omission and any future provenance request get conflated | M05: record the intentional removal and triaged residual gap without restoring licence or adding a gate. |

## Cleared items and owner-sentence coverage

“Cleared” here means the **plan expresses the requirement**; it does not certify an implementation or result.

| Owner item | Assessment |
| --- | --- |
| 1 — discuss/finalize the connected GitHub/HF plan, then execute | Present: code, dataset, models and collection cross-links. H06–H08 address execution/provenance defects, not a lack of authorization. |
| 2 — four evenly spread checkpoints and optimizer states | Present: 25/50/75/100% full states for each of three widths; the 254 loss checkpoints remain separately identified. H05 addresses whether the public continuation package is usable. |
| 3 — personal public HF, one dataset, one repo for three models, collection; later pipeline/Docling/glossAPI | Present in §§3–5 and step 8. Agreed metadata is weakened (H01–H03); post-release action assignment remains open (M06). |
| 4 — both specified PDFs, detection and per-page/line output; line position metadata | Step 8 includes numbered boxes, crops/text per line and full page text. The brief retains both exact filenames. Position fields are explicitly present; frame/lineage evidence needs H02. The plan's page counts/orientation were not verified in this review. |
| 5 — drop licence, retain exact-book source, final dataset main-only unless justified | Licence removal is explicit for real and synthetic fields and must remain. Exact-book field intent is present (M04 coverage risk). Fresh public main-only repo plus a separate private archive is a reasonable non-deleting design once H06 is corrected. No licence/Anemi admission gate is reinstated from older documents. |
| 6 — separate synthetic file, generator distribution/operations/origin; “Greek OCR,” multiple scripts, modern/polytonic; .docx is not transcription | Separate synthetic shards/config satisfy the practical separation; no need to force one huge file. Configured and realized distributions are requested. Repo `fffoivos/greek-ocr`, title “Greek OCR,” and script emphasis are present. Synthetic provenance needs H03. No CER is claimed for the two PDFs without transcription. |
| 7 — checkpoint-batched gap issues, prompts, don't overdo it | Ledger, prompt line and duplicate review are present. Blanket non-fixing/automatic issue language and the licence-gap disposition need M05. |
| 8 — each component v0.n, end beta at v1; README introduces actual dataset/tool/model links | Present in principle. README includes corrected Google lines, review code, latest synthetic lines, models and collection in pipeline order. Concrete file/config/revision links and component count/tag semantics must be settled (M02). |
| 9 — exactly one Astra plan review; coordinator fixes and executes autonomously; ×1 when ready | This report fulfills the single plan review. Later implementation-artifact reviews do not inherently violate that instruction. M06 addresses the contradictory wait ordering and handoff. No new blanket permission request is required. |
| Standing rules | Test-only reporting is repeatedly stated; H04 corrects the contradictory selection descriptions. Clariden is designated for processing. Deletion remains owner-controlled. Role/commit assignment needs H08; credentials need M03. |

Other sound choices: preserving original embedded image bytes, splitting synthetic from real data, exposing known label-quality limitations with the sample's base-harvest scope, separating safe inference weights from warned pickle states, retaining the private archive, and conducting model comparisons on dev rather than selecting with test results. The training-state branch is in the **model** repo, so it does not contradict the owner's dataset-main-only rule. No additional benchmark, architecture change, model-quality threshold, licence requirement or second plan review is proposed.

VERDICT: HOLD | BLOCKERS: 0 | HIGH: 8
