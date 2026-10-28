# ASTRA — one review of the release plan (Greek OCR v0.6 models, line dataset, code), 28 Oct 2026 Europe/Athens

Independent fresh-eyes reviewer of a PLAN (not of results). Adversarial and firsthand. READ-ONLY except your report; no network, SSH, jobs, background processes or test suites.

Read first, in this order:
1. docs/programme_20261028/RELEASE_v0/OWNER_BRIEF.md — the owner's words, verbatim. These are the rules.
2. docs/programme_20261028/RELEASE_v0/PLAN.md — the plan under review.
3. docs/programme_20261019/registry/HF_REPO_SPEC.md — the earlier agreed metadata/layout the plan amends.
4. As needed: AGENTS.md; docs/programme_20261025/TRAIN_FULL_v1/{EXECUTION_STATE.md,STAGE_C.md,OWNER_BRIEF.md}; docs/A_ocr_development/{RECOGNISER_AND_TRAINING.md,MODEL_GENERATIONS.md}; greekocr/deploy/docling_plugin/; greekocr/_vendor/train/; docs/programme_20261025/TRAIN_FULL_v1/stage_c_package/; docs/harvest/line_pipeline/tool_versions.json.

The owner said the plan gets exactly one Astra review, after which the coordinator fixes what it judges right and executes autonomously. So be complete in this single pass.

Check:
(a) Fidelity: does the plan implement every owner sentence, and add no rule the owner did not state? Name any owner sentence that is missing, weakened or contradicted (licence dropped; source detailed enough to find the exact book; main-only dataset unless a good reason; synthetic as a separate file with per-line generator functions/distribution/origin; model repo name and multi-script emphasis; v0.n per component; README wording; gap method and its "don't overdo it" limit; the two PDFs with line detection + per-page/line output; public repos + a collection).
(b) Metadata completeness: against HF_REPO_SPEC and the plan's own claims, is any agreed field lost (especially position on the page, label versions, provenance, split/registry, training membership)? Are any listed fields not actually available from the stated sources (say so as a risk, not a certainty, if you cannot verify)?
(c) Correctness and sequencing risks: public-history leakage (old private commits, raw Google responses), the rename-to-archive approach, test-set selection rule (test never selects anything), model checkpoint selection, the v0.6 count, GitHub squash/size-guard, consolidation of the diverged trainer copies without changing what produced the models, Docling loading test, HF limits (file counts/sizes), credential handling.
(d) Anything the plan should decide now that it leaves open.

If you find a documentation or provenance gap, add it to your report under "GAPS" (what / where / impact / fix); don't fix it here.

Disposition: the coordinator fixes BLOCKER/HIGH before executing; MEDIUM/LOW are logged and may be deferred. Calibrate severity honestly.
Write docs/programme_20261028/RELEASE_v0/ASTRA_PLAN_REVIEW.md: header (scope, inputs read with SHA256 of PLAN.md and OWNER_BRIEF.md), one-line verdict, findings most-severe first (each [BLOCKER]/[HIGH]/[MEDIUM]/[LOW], concrete path/section, failure scenario, fix), GAPS, cleared items. Last line exactly `VERDICT: <PASS|HOLD> | BLOCKERS: <n> | HIGH: <n>`
