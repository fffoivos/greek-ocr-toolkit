# ASTRA-CLEANUP — independent certification review, 20 October 2026

Scope: `cleanup/20261019`, base `ac1c38cf6ebab49ef694fffb2a8b3dc757012f33` → inspected HEAD `9dd7e80fdc823dce6b924a14a4d5843e7590f169`, in `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-main-next`. Standard: the owner's verbatim brief and the seven requirements in the review request. Repository and external data were read only; review artifacts are in the separate ASTRA-CLEANUP scratch directory. No implementation changes, compute launches, publication, or background jobs were performed.

Evidence: source and Git objects, the requested project documents, both layout tables, exhaustive base-file accounting, every external receipt entry hashed, direct reader probes, row-level SEG10 recounts, historical-test AST comparisons, raw earlier JUnit records, and a new full pytest run. The suite ran at `0b8f073de6d5ca1edda597280b0b4eeea25317d3`; subsequent commits through the inspected HEAD changed only `docs/programme_20261019/NIGHT_STATE.json`, so tested code and tests are unchanged. A clean `git status` did **not** reveal the ignored omissions below.

The requested `git log ac1c38cf6..HEAD` and `git diff --stat ac1c38cf6..HEAD` were inspected and saved as `astra-cleanup-log.txt` and `astra-cleanup-stat.txt`. Raw diff stat: **53,451 files changed, 491,151 insertions, 32,433,020 deletions**. Git skipped exhaustive rename detection because of the file count; those deletion totals are not a custody analysis. The object-by-object accounting below supplies that analysis.

**Not certified for merge: four HIGH findings require fixes or an explicit separate disposition and re-review.**

## Findings, most severe first

### H1 — [HIGH] The committed tree omits required metadata and 3,409 unreceipted base files

Locations: `.gitignore:78–89`; `scripts/layout_paths.py:14–18`; `docs/records/INDEX.md:11–13`; `README.md:80`.

The two layout reports describe 170 move mappings, but **3,409 of the 61,533 base files have neither a committed destination nor a receipt**. They total **132,088,160 bytes**. All 3,409 still exist at their mapped local paths and are ignored; none exists under either its old or mapped name at the named external data root. Of these, 3,407 retain the base bytes; two HTML files have navigation edits. Examples include `docs/records/harvest/analysis/B_content_style/test_first20k/book_stats.jsonl`, `docs/records/archive/l1_20261017/L1_DEPLOY_FILES.txt`, and `docs/records/cleanup_20261017/MR_C_evidence/suite_after.log`. The complete list is [unaccounted_base_files.tsv](unaccounted_base_files.tsv), with sizes, hashes, base-byte equality and external-presence checks.

Important new files are also present only as ignored local files: `docs/cleanup_20261019/LAYOUT_ALIASES_2.tsv`, `data_out/MOVE_MANIFEST.tsv`, and `data_out/RECEIPTS/receipt_02.tsv` and `receipt_03.tsv`. The first is opened unconditionally by `scripts/layout_paths.py`, which the test helpers import. An isolated import using exact HEAD source files fails with `FileNotFoundError` for the missing alias TSV: [head_import_probe.log](head_import_probe.log). Thus the current populated worktree conceals a fresh-checkout failure.

The new SEG10 raw `docs/records/harvest/seg_steps/s5_adopt/replay.jsonl` is **42,991,967 bytes**, ignored/untracked and unreceipted, with no corresponding file at either external mirror path. Its locally available rows can support this audit, but another checkout cannot retrieve them from the published custody scheme. This is separate from the 3,409 base-file count.

Failure scenario: a clean checkout cannot load the shared test-path helper, lacks the advertised manifest and two receipt shards, and loses the advertised retrieval paths for substantial evidence. The base blobs remain in history; this finding concerns missing current custody, not history destruction.

Fix: establish explicit tracking exceptions for required small metadata/evidence, commit the required TSVs, and deliberately retain or receipt each omitted base file. Move and receipt the large SEG10 replay rather than forcing it through the size guard. Re-run the exhaustive accounting against a checkout materialized solely from committed objects; require zero unaccounted base files and successful test collection there.

### H2 — [HIGH] External-data and sibling-checkout readers are not behavior preserving

Locations: `scripts/labelfix/sf7_measure.py:24,33`; `greekocr/harvest/collection.py:251–253`; `scripts/labelfix/r2_cards_prepare.py:29,317`; contrary assurance at `docs/cleanup_20261019/TEST_PATHS_AFTER_LAYOUT.md:13`.

Three direct witnesses:

1. With `GREEK_OCR_DATA_ROOT` correctly set, SF7 loads the external overlays through `_data_input` at line 24, then hashes the unresolved old local path at line 33. Data-enabled pytest collection ends with **7,007 tests collected, 1 error, exit 2**, because `selected_overlays.json.gz` is absent locally. The external file exists and passed the custody hash audit. See [astra-cleanup-collect-data.log](astra-cleanup-collect-data.log).
2. `read_wave(repo, "round1")` and `read_wave(repo, "round2")` both raise `ValueError: delivered wave ... missing admitted.jsonl`. Their input paths resolve to existing receipted external files, but local `.is_file()` checks run before the resolver-backed reader.
3. `r2_cards_prepare.HARVEST` explicitly names the unmoved sibling `greek-ocr-toolkit`. Its wave path was nevertheless changed to `docs/records/harvest`. For actual row `db1ed5f902d696fb53656a7d-p000006-l0002`, the base `v2_metadata` function returns **1 admission and 1 record**; HEAD returns **0 and 0**, silently. The comparison executes the original function AST with the same current globals and input. See [reader_regressions.json](reader_regressions.json).

Failure scenario: configuring the advertised data root causes collection failure, collection construction rejects available waves, and review-card preparation silently loses metadata from a source checkout that was never reorganized.

Fix: resolve each input once and consistently use the resolved path for existence checks, reading and hashing. Preserve explicit paths into other checkouts. Re-run these three witnesses and data-enabled collection/full tests, checking restored parameterized evidence rather than merely obtaining additional missing-input skips.

### H3 — [HIGH] The required full-suite gate is red

Locations: `tests/test_r2_cards.py:25–31`; `tests/adjudicate/test_os5_owner_sheets.py:30`; `scripts/review/build_owner_sheets_v2.py:585–587`; `tests/labelfix/test_capture.py:50`; `scripts/labelfix/r2_cards_prepare.py:38–43`.

From the repository root, using the existing project interpreter:

```sh
PYTHONDONTWRITEBYTECODE=1 \
  /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python \
  -m pytest -q -p no:cacheprovider --junitxml=/tmp/astra-cleanup-head.xml
```

Raw result: **2 failed, 6,656 passed, 186 skipped, 9 warnings, 19 errors, 63 subtests passed in 188.48 seconds; exit 1.** [Full log](astra-cleanup-head.log), [JUnit](astra-cleanup-head.xml).

The 19 R2C setup errors create temporary directories inside the read-only repository. The OS5 failure tries to save a raster under repository `artifacts/owner_sheets/v2/r2a/`. The capture-server failure hits `RuntimeError: R2C is offline, saved geometry only` because importing `r2_cards_prepare` globally replaces socket connection functions. That network mutation predates the cleanup; this run exposes it when local server binding succeeds. These are not asserted to be new segmentation-policy regressions, but the requested zero-failure/zero-error gate is unmet.

Fix: put test outputs under the supplied temporary directory and scope the output-root injection while preserving production output guards. Scope/restore the offline socket substitutions so independent tests cannot affect each other. Re-run the entire suite under the requested read-only conditions. These live failures should not become historical-record skips.

### H4 — [HIGH] The comparison includes operational changes beyond the stated SEG10 exception

Locations: `docs/records/harvest/collect_v3_admission/stage_crops.py:44–79,122–125,238`; source commit `ef2598fd6`, integrated through `ce28855d6` after the specified base.

This executable moved under `docs/records` but also changed behavior: the disk floor defaults to **10 GB instead of 0**, a new census adapter changes accepted inputs, and legacy inputs with any joined W2 row are restricted to W2. Executing just the exact selection AST with one W1 and one W2 row yields **[W1, W2] → [W2]**; no staging was performed. This is an intentional CROPS3 feature described in its report, not a path-only cleanup or SEG10. The post-base history also includes BENCH02D tools and other lead additions.

Failure scenario: merging the branch as behavior-preserving cleanup changes which crops a mixed legacy invocation stages and when it defers for disk space. The cleanup certification would implicitly cover operational work that this review's stated exception does not cover.

Fix: separate these operational changes into their own reviewed merge, or explicitly expand and approve the comparison scope and independently qualify the new behavior. This finding does not claim CROPS3 is inherently incorrect; it rejects the assertion that SEG10 is the sole behavior change.

### M1 — [MEDIUM] Current-facing documentation contradicts the implementation

Locations: `docs/B_training_data/b_tools/README.md:9,13,68`; `b_tools/SEGMENTATION_FILTER.md:7–9,54`; `c_pipeline/pipeline.mmd:1,18,28,59–60`; `docs/harvest/line_pipeline/README.md:11–30`; `docs/A_ocr_development/MODEL_GENERATIONS.md` source-equality table; `README.md:78`; `AGENTS.md:75`.

The current tools overview and segmentation guide still assert **0.9-s4, .50–1.50**, with .30–2.00 not wired in. The actual manifest/code use **0.9-s5 and .30–2.00**. The pipeline graph still says pipeline 0.3, census 0.5 and numerics 0.2, and its final comments deny the held-out-crop hook and numeric-adjacency integration that SEG10 added. The compatibility README under `docs/harvest/line_pipeline/` repeats these obsolete implementation claims. Actual identities are pipeline **0.3.1**, census **0.6**, numerics **0.3**. The root README and B.c prose are more current; their presence does not make the contradictory guides accurate.

The generation record's current byte-equality claim for `greekocr/glyphs/baseline.py` is also false after a comment/path edit; runtime equivalence is a different claim. The blanket statement that crops/sheets are never committed needs explicit historical/fixture exceptions: HEAD retains **1,234 PNG, 5 JPG and 18 HTML files**, including owner-review sheets. This is not a recommendation to delete those retained artifacts. Draft/task-report wording such as “This run touches none of those files” also remains in current guidance.

Failure scenario: a reader follows the advertised current graph or tool page and reasons about the wrong policy/version, or applies an overbroad data rule to required fixtures.

Fix: update all current guides and the graph from the same version manifest and implementation; label frozen historical prose as historical. Keep the band adoption explicitly a coordinator decision under the cleanup mandate, not an owner ruling.

### M2 — [MEDIUM] Custody metadata is internally incomplete, despite intact external bytes

Locations: `docs/cleanup_20261019/data_out/RECEIPTS/INDEX.md:9,16–21`; local `MOVE_MANIFEST.tsv`; local `RECEIPTS/receipt_03.tsv:2`.

The index total is **16,888 entries / 9,984,555,912 bytes**. All three local shards actually contain **16,897 / 10,494,028,696**. The nine later receipt entries, totaling **509,472,784 bytes**, are absent from the move manifest. The CP5 entry's producing commit is literally **`merge`**, which cannot resolve to the promised source blob. Of 16,897 producing-commit bindings, **16,896 resolve and match**, and this one does not. See [receipt_provenance_errors.json](receipt_provenance_errors.json). Missing shard tracking is already covered by H1.

Failure scenario: a consumer of the advertised complete manifest or aggregate index misses the later files; provenance lookup fails for CP5 even though its external bytes are intact.

Fix: update aggregate counts and the manifest, use an actual producing commit, and verify each committed shard against its source blob and external hash.

### L1 — [LOW] One historical skip calls a producing-phase anchor “green” without execution evidence

Locations: `tests/test_n1w1_r3.py:68`; `docs/cleanup_20261019/TEST_RECORDS.md:49`.

The decorator says “green at ...@686ec7de7”, while the report correctly admits that this is the ready-phase anchor and that the test first entered Git later at `c609f818d`. Ancestry proves preserved history, not a green execution.

Failure scenario: future reviewers mistake an approximate provenance anchor for a test result.

Fix: label it as a producing-phase anchor with last-green unverified, or attach an actual green test receipt. Preserve the original assertion.

## Cleared and verified-good, with limits

### Owner taxonomy and process

The A/B organization is substantive. A.i points to the actual pixel-first `greekocr/pages` and shared `greekocr/glyphs` implementation. A.iii describes the small-detector R7 lineage; A.ii describes its R8 successor. R7 commits `932027e210` and `52cee3bcc` are ancestors of R8 `cae93fb49`. These are generations sharing the Stack implementation, not three independent current engines. `MODEL_GENERATIONS.md` makes that distinction, so the mapping is defensible as the proposed taxonomy. Detector code identifies PP-OCRv6 small; the Stack defaults remain `bend=False`, `final_export=False`. No fresh physical-quality or speed certification follows from this lineage check.

B.a has real Google page-OCR code; B.b has correction/filter tools; B.c has the coordinating implementation in `greekocr/harvest/line_pipeline.py`; B.d documents owner-sheet artifacts, revision and publication. Root README is a useful entry point, subject to H1/M1. AGENTS covers roles, separate OCR-development/data-creation work, pipeline order, owner review, briefs/runs, Clariden, data/secrets and review responsibilities. Owner-sheet code retains the last-two-tool-versions display and the persisted-note/no-write-on-load logic. No review artifacts were published during this audit.

### Exhaustive file and custody counts

| Base-file disposition | Count |
|---|---:|
| Same path, identical | 8,890 |
| Same path, modified | 410 |
| Moved, identical | 31,291 |
| Moved, modified | 645 |
| Externally receipted | 16,888 |
| Unaccounted | **3,409** |
| Total | **61,533** |

Base tree: **12,856,380,501 bytes**. Inspected HEAD: **41,929 files / 2,797,168,495 bytes**. The 130 first-layout and 40 second-layout mappings were applied by longest matching original prefix, then matched against Git objects and receipts. The underlying accounting is [custody_accounting.json](custody_accounting.json); code is [audit_custody.py](audit_custody.py).

All **16,897 receipted entries / 10,494,028,696 bytes** were hashed, far beyond the requested 50-file sample: **zero missing entries, zero receipt size/SHA256 mismatches**, and all **16,888 base-derived entries match the original Git blob identities**. For 19 symlinks, the receipt contract hashes the link text; this does not certify availability of their targets. [Per-entry results](custody_hashes.json).

The **147,025,055-byte SEGEVAL1.bundle** is present. Its SHA256 is `25c38794aacb89d083b461175471735575551f0acc4d1f612214b3e43fee1e1a`; `git bundle list-heads` identifies `b3b5aaa19835ac626af6576da37e008386b26879 refs/heads/segeval1-artifacts`.

The tracked-file size guard passed. Independent tree inspection finds **zero files over 5,000,000 bytes**; the maximum is **4,992,029 bytes**. This says nothing about ignored omissions, which is why H1 remains severe.

Base history remains reachable. Of 56 inventoried branch tips, 47 branch heads are unchanged and 9 have advanced; all original tips remain ancestors. Therefore the assertion that every old branch name is untouched is not literally true, but the recorded SHA comparison points are preserved. Seven `records/*` tags are present. Use the inventory's immutable SHAs, not moving branch names, for historical comparison.

### Specific factual checks against source and raw records

| Claim checked | Firsthand result |
|---|---|
| Pipeline version | `line_pipeline.py` uses 0.3.1; root table/B.c prose agree. |
| Segmentation | Manifest 0.9-s5; policy defaults .30–2.00; older B.b guide disagrees. |
| Gate and final eligibility | Both manifest identities 0.3. |
| Numerics and census | 0.3 and 0.6, respectively. |
| Other manifest versions | Polytonic 0.7, Cyrillic 0.3, dashes 0.1, inventory 0.1, composer/content repair 0.2. |
| Manifest source bindings | **35 component occurrences, 23 unique files, 11 aggregate digests**, all hash checks pass; iteration counts agree. Some components intentionally resolve in sibling checkouts. |
| Codec | Actual SHA256 `94485f72eac0aaf2324dc60b1c02110b271d362a79c440e2ce6bf6f4604997b9`. |
| Slow Q4 source equality | `pages/lines.py`, `pages/pixels.py`, `pages/font.py` identical to Q4; `baseline.py` differs only in documentation, and components have the declared curve provenance change. |
| Prototype coverage | **41** prototype test files outside default `testpaths = ["tests"]`; default suite success would not certify them. |
| SF7 audit | Saved per-line records recount **70 CORRECT / 30 PENDING**, total 100. This is a saved-status recount, not fresh visual adjudication. |
| LQB truth | External `truth_v1_1.jsonl` contains **61,463** nonblank rows. |
| DocAI configuration | Code default `pretrained-ocr-v2.1-2024-08-07`; code's cost assumption is $1.50/1,000 pages, consistent with 1,500 microdollars/page in the ledger. This verifies configuration, not today's provider tariff. |
| SEG10 cohorts | **1,705 = 150 + 888 + 250 + 417** saved replay rows; **111 verdict flips**, **3 reason-only changes**. |
| SEG10 owner marks | **240 entries → 235 unique IDs** using latest timestamp/input order; **185** marked typology IDs. |
| Changed owner IDs | **59** distinct IDs before the content gate, **38** after it. |

The underlying calculations and source paths are [audit_facts.py](audit_facts.py) and [facts.json](facts.json). The requested collection-v2 manifests were not available at the expected repository or named-data-root paths; I did not independently certify their reported 271,987-row parity.

### SEG10 raw scores, including regressions

These are independent recounts of saved row records and marks, not a fresh native-detector run or independent generalization evidence. The paired before/after evidence dictionaries match for all 1,705 rows; the decision band changes. Integration fixes and coordinator provenance are explicitly documented.

| Panel | s4 | s5 |
|---|---:|---:|
| Unfiltered 150: FP / FN / UNC | **16 / 15 / 0** | **4 / 19 / 0** |
| Rated calibration agreement | 109/135 | 117/135 |
| Owner-mark agreement | 189/235 | 209/235 |
| Typology agreement | 160/185 | 173/185 |
| After content gate, 137: FP / FN / UNC | **11 / 15 / 0** | **2 / 18 / 0** |
| After gate, rated agreement | 77/91 | 82/91 |
| After gate, owner-mark agreement | 157/191 | 170/191 |
| After gate, typology agreement | 153/176 | 165/176 |

False negatives increase **15 → 19** unfiltered and **15 → 18** after the gate. Better aggregate agreement must not conceal those increases or be presented as independent held-out qualification. No additional band tuning is requested by this review.

### Historical-test ruling and collection-count change

The ruling is generally defensible: compare frozen branch-specific evidence with its historical branch@SHA, retaining the old assertions rather than rewriting expected hashes to match integration. Independently compared **41 historical test function bodies: 41 unchanged** across the skip-introduction commit. Four specific vendor parameters were also marked rather than disabling their whole suite. All 17 distinct function-decorator commit anchors, plus the vendor-parameter anchor, are retained ancestors; L1 qualifies the unproven “green” label.

Recounting distinct test node IDs from the raw earlier JUnit files gives **7,329 → 6,823**: **530 IDs removed, 24 added**, net −506. Most of the reduction is the documented collapse of parameterized evidence tests when bulk data is absent: 56 SF5 witnesses, 168 SF6 regressions, 78 SF7 card cases, 200 SF7 audit cases and 26 CP5 cases collapse to seven missing-input nodes. Two ADM5 IDs are renamed and 15 genuinely new cases are added. The second layout adds 40 alias cases, yielding the current **6,863** distinct nodes. The 63 subtests are separate from those counts. See [test_count_delta.json](test_count_delta.json) and the two `prior_*.xml` files.

Thus the count-drop explanation is numerically true; it is **not** evidence of restored execution coverage. The 186 current skips comprise 68 historical, 100 other/absent-input, 2 sandbox and 16 browser cases. H2 shows that enabling the data root does not yet restore the suite end to end.

## Ordered asks

1. Fix committed custody and required metadata (H1); require zero unaccounted base files and successful import/collection from a checkout built only from Git.
2. Repair all three demonstrated reader regressions (H2); verify external-data collection and reads using the advertised data-root setup.
3. Fix test isolation/output roots (H3); produce a new full-suite result with **0 failed / 0 errors** under the review's read-only conditions, without hiding failures as records.
4. Separate or explicitly expand the review scope for CROPS3 and the other post-base operational additions (H4), then qualify that scope before merging.
5. Log and resolve or explicitly defer M1/M2/L1; retain the raw SEG10 false-negative increases and the coordinator-decision attribution in the final handoff.
6. Re-review the fixed committed HEAD. No repository fixes were made by this certifier.

VERDICT: NOT CERTIFIED FOR MERGE — fix and re-review the four HIGH findings | BLOCKERS: 0 | HIGH: 4
