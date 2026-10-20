# Working in the Greek OCR toolkit

## 1. Roles

The **owner decides** the rules and acceptance criteria, and gates push/merge, spending, launches and irreversible actions. The **coordinator plans, briefs, reviews and records** the work. **Sol (gpt-6.1-sol via Codex)** executes code and operations from a brief and produces evidence; Sol cannot write git metadata. Commits, merges and pushes belong to the lead/coordinator sessions, under the owner's gates, never to Sol runs.

**Track leads (Opus sessions)** own one track each, maintain its handoff, and brief Sol. **Astra** reviews packages at checkpoints against the owner's actual brief. No agent adds rules the owner did not state; tools implement the owner's rules exactly.

### Tools are the owner's rules

An owner-accepted tool implements exactly the rules the owner stated; agents never add guards, tests or thresholds on their own. Extra measurements go into the evidence record as diagnostics and onto a sheet as a question for the owner.

## 2. Two aspects, kept apart

**A develops OCR models and segmenters:** the slow pixel segmenter, next-generation R8 and the small-detector R7 lineage, plus recognition, synthetic generation and scoring. A never consumes B's review artifacts as truth.

**B creates training data:** Google OCR on pages (B.a), correction/filtering tools built on A (B.b), their organising line pipeline (B.c), and revision artifacts and human publication (B.d). B uses A's segmenter as a frozen tool version. A segmenter change gets a new version and a replay on the frozen review sets before B adopts it. Keep the two scopes and their evidence separate. The owner's accepted segmentation state does not authorize further tuning or new segmentation qualification.

## 3. The B process

The [B.c pipeline](docs/B_training_data/c_pipeline/README.md) organises B; its [graph](docs/B_training_data/c_pipeline/pipeline.mmd) maps the routes. The stage order, quoted from the pipeline README, is:

> 1. Validate runtime, register and inventory every parent row
> 2. Content gate 0.3, before crop identity and native segmentation
> 3. Native segmentation 0.13 (label 0.9-s5)
> 4. Schedule every relevant corrective route
> 5. Validate and compose qualified raw-parent spans
> 6. Re-inventory, stabilize and recheck coverage
> 7. Split/edition integrity and final eligibility 0.3
> 8. Global train deduplication and evaluation retention
> 9. Publish a complete generation and pending obligations

Bind source, book, edition, page, split, immutable raw-parent text and exact crop bytes/hash. Inventory **every raw row** before filtering. Expected scripts resolve page override → book declaration → source policy. The content gate drops mixed-script words, holds unexpected scripts, and excludes short lines before native work. Cells (aspect ≤6) with more than one letter or decimal digit pass the length branch; non-cell numeric exemptions and final shape requirements follow the pipeline's stated rules.

After crop binding, segmentation turns every taller-than-wide crop 90° clockwise and applies the ordered other-row/whole-word gate, output-versus-box check and padding check. Non-small ink is measured along its baseline curve; the small branch uses all extracted components. The current common length band is 0.30–2.00. The graph, current stage description and `docs/harvest/line_pipeline/tool_versions.json` identify segmentation 0.13 (label 0.9-s5) and pipeline 0.3.2.

After segmentation KEEP, schedule every applicable route (PIPE032 permits explicitly configured `routes_out_of_scope`; those routes retain raw text and report `not_applied_out_of_scope`, while content repair cannot be excluded): SF7 polytonic (including missing-mark candidates), RU1 Cyrillic, N1 numerics, dash tags and content repair. Require exact scoped results; a missing record is not a successful no-change result. SF7 remains `candidate_pre_audit`, N1 is assisted and dashes only tag. Compose only validated, compatible edits against the raw parent; conflicting edits HOLD. Re-inventory, recheck new candidates and coverage, then apply final eligibility. Protect held-out editions and crops, deduplicate train observations, retain non-train diagnostics, and export an immutable generation with its publication receipt.

Every decision carries its reason. HOLD and DROP retain evidence; infrastructure failures remain distinct. Nothing is admitted without a qualified tool result wherever a tool applies. Tool KEEP, completed census and training readiness are separate conclusions.

## 4. The revision pipeline

### Human review of tool outputs

The owner reviews tool outputs line by line on review sheets. The design is fixed and documented in [docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md](docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md): one card per line with the crop and the Google text together, evidence overlays, exactly the last two tool versions, an outer border that is the owner's mark (space toggles KEEP ↔ DROP) and an inner frame that is the latest tool verdict, arrow-key navigation, zoom, and marks/notes that autosave to the artifact database under stable ids. Decision tools use it as is; correction tools use the correction variant (accept/reject the proposed change, editable printed field). Any agent that builds a sheet for the owner builds it to that document: render through `greekocr.adjudicate.owner_sheet`, never write to the database on page load, dump the marks before republishing, and state in the intro what KEEP and DROP mean on that sheet.

Replay each proposed tool version on the frozen evidence before adoption; save input hashes, old/new results, flips, failures and scoring denominators. Build sheets from saved evidence without rerunning the tool in the builder. Show the last two available versions; never fabricate a missing prior version. Owner marks are the standard against which tools are scored, with unmarked and unresolved rows counted separately.

Unjudged lines come first. Previously judged lines come last with their prior mark shown, so the owner is not asked to judge them twice. **Cards must fit the screen:** the crop top and note must remain reachable; keep version text concise and long diagnostics behind details. Put vertical crops on the left and text/notes on the right. Verify actual desktop and narrow layouts before publication.

Keys follow the fixed contract: ↑/↓ navigate; SPACE or the badge marks KEEP then toggles KEEP↔DROP; `z` zooms, `b` toggles overlays, `d` opens details, and Esc leaves a text field. In a nonempty text field, SPACE is ordinary text entry. Marks and edits autosave to the artifact database's `notes` collection under stable IDs. **Never write on load.** Before every republish, dump the marks, store the dump with the tool's evidence, preserve IDs and verify marks reload afterward. See the [revision workflow](docs/B_training_data/d_review/README.md) and [publishing protocol](docs/B_training_data/d_review/PUBLISHING.md).

The owner's segmentation standard, quoted in the revision workflow, is:

> (a) exactly one central line; (b) the Google text matches the visible line exactly, neither more nor less; (c) no other line shows completely and at most 2 WHOLE words from other lines, where whole = 100% visible — a readable but cut word is a cut-off word and does not count. Partial neighbour letter bodies alone are fine.

Implementation proxies such as ≥95% letter-body visibility are not the quoted 100% standard. Keep that distinction visible in evidence. For labels, transcribe what is printed, including misprints, rather than normalizing to expected spelling.

## 5. Briefs and runs

Tests and replay adapters use `greekocr.harvest.predictor_path.predictor_binary`: configure `GREEK_OCR_PREDICTOR` or `GREEK_OCR_BUILD_DIR`; missing builds run offline and locked in scratch with `BUILD_RECEIPT.json` (see README §4).

One brief per Sol run lives under [docs/ocr_program_2026-10-06/briefs/](docs/ocr_program_2026-10-06/briefs/). It names one objective, permitted write scope, inputs by SHA256, outputs by path and the tests to run. Respect the brief's scope when other runs work concurrently. Sol never stages, commits, merges, pushes or otherwise writes git metadata; sessions perform git operations.

Keep receipts for every produced artifact: path, bytes, SHA256 and producing commit. Preserve input identity, run/version binding, outcomes and limitations in the evidence. Return a one-line report identifying the result, output paths, checks and blockers; maintain the track handoff so the next run can continue. Dated completed evidence belongs under [docs/records/](docs/records/INDEX.md); external bulk-data custody receipts belong under [docs/cleanup_20261019/data_out/RECEIPTS/](docs/cleanup_20261019/data_out/RECEIPTS/).

## 6. Clariden operations

Verify the exact deployment with local/remote SHA comparison **before any sbatch**, including the intended job/config/runtime and scheduler dry check. Historical verification does not certify changed source or inputs. **Leads never submit.** The coordinator submits only within the owner's launch authorization.

Use the partition, CPU count and time budget for the actual job kind: regression, parity or census. The [job-kind record](docs/records/harvest/seg_census/JOB_KINDS.md) and [Clariden runbook](docs/B_training_data/c_pipeline/RUNBOOK_CLARIDEN.md) distinguish the archived package from current source and the earlier thin worker. Check exact deployed versions rather than copying an old command's defaults.

Run a bounded smoke first; inspect its logs, coverage, decisions and publication receipt before a full run of the same binding. Monitor jobs through completion; never fire and forget. On **FAILED**, read the actual job/step log and accounting, identify the failing phase and preserve the attempt before deciding a retry. A scheduler success alone does not prove a valid export or a qualified training release.

## 7. Data and secrets

Keep bulk data outside the repository under `GREEK_OCR_DATA_ROOT`. No tracked file may exceed **5 MB (5,000,000 bytes)**; new bulk crops and sheets stay outside Git. Retained small historical evidence and required test/demo fixtures are explicit exceptions under the same size limit. Keep path/bytes/SHA256/producing-commit receipts in [docs/cleanup_20261019/data_out/RECEIPTS/](docs/cleanup_20261019/data_out/RECEIPTS/). Preserve historical custody through the [move manifest](docs/cleanup_20261019/data_out/MOVE_MANIFEST.tsv) and [layout map](docs/cleanup_20261019/LAYOUT_REPORT.md).

Credentials live **only in the macOS Keychain**, injected at launch; never put secrets in code, briefs, logs, receipts or committed files. Nothing from Anemi leaves the project; preserve source-specific rights. Limit requests to **≤1 request/second per host**, using the shared limiter across workers and applicable HTTP hops. Reader concurrency of one is not a rate limiter.

## 8. Reviews

Astra reviews at checkpoints with the owner's brief **verbatim**, the reviewable comparison, exact input/output identities, tests and evidence. For this cleanup, supply [OWNER_BRIEF.md](docs/cleanup_20261019/OWNER_BRIEF.md) unchanged and the comparison prescribed by the [plan](docs/cleanup_20261019/PLAN.md).

The third review cycle on one object means **stop and decide**; do not continue an automatic fix loop. Summaries must never be stronger than their table rows. Separate preparation, execution, historical results, current verification and unresolved questions; tests or clean receipts do not substitute for owner adoption or physical review.

## 9. Where things are

Use [README §2](README.md#2-map-by-the-owners-taxonomy) for the code/documentation taxonomy: [A](docs/A_ocr_development/README.md), [B](docs/B_training_data/README.md), [B.a Google OCR](docs/B_training_data/a_google_ocr/README.md), [B.b tools](docs/B_training_data/b_tools/README.md), [B.c pipeline](docs/B_training_data/c_pipeline/README.md), [B.d revision](docs/B_training_data/d_review/README.md), and [shared infrastructure](docs/shared/README.md).

Use the [records index](docs/records/INDEX.md) for dated track evidence and handoffs, [run briefs](docs/ocr_program_2026-10-06/briefs/) for current assignments, and the [cleanup record](docs/cleanup_20261019/) for organisation and custody decisions. The [layout report](docs/cleanup_20261019/LAYOUT_REPORT.md) maps old paths; historical machine-readable receipts retain their original bindings.

Sources: `docs/cleanup_20261019/OWNER_BRIEF.md`; `docs/cleanup_20261019/AGENTS_README_OUTLINE.md`; `docs/cleanup_20261019/PLAN.md`; `docs/cleanup_20261019/LAYOUT_REPORT.md`; `docs/A_ocr_development/README.md`; `docs/B_training_data/README.md`; `docs/B_training_data/a_google_ocr/README.md`; `docs/B_training_data/b_tools/README.md`; `docs/B_training_data/c_pipeline/README.md`; `docs/B_training_data/d_review/README.md`; `docs/shared/README.md`; `docs/records/INDEX.md`; `docs/harvest/line_pipeline/tool_versions.json`; `README.md` (previous contents); `AGENTS.md` (previous contents); `docs/records/README_public_20261012.md`; `docs/B_training_data/c_pipeline/pipeline.mmd`; `docs/B_training_data/c_pipeline/RUNBOOK_CLARIDEN.md`; `docs/B_training_data/d_review/HUMAN_REVIEW_SHEETS.md`; `docs/B_training_data/d_review/OWNER_SHEETS.md`; `docs/B_training_data/b_tools/LABEL_QUALITY_BENCHMARK.md`; `docs/ocr_program_2026-10-06/briefs/CLEAN5E_readme_agents.md`; `pyproject.toml`; `greekocr/harvest/line_pipeline.py`; `greekocr/harvest/line_pipeline_census.py`; `tests/test_size_guard.py`; `.gitignore`.
