# Sol blind reading: handover to the sourcing and spell-check leads (17 Oct 2026, 14:11 Athens)

From the Sol-reading lead (Opus), with the coordinator's rulings applied. Evidence is in `RESULTS.md`, `results/SUMMARY.md`, `grave/RESULTS_TABLE.md` and `grave_full/FINAL.md`, all on branch `opus/sol-reading`.

## 1. What Sol takes, and what stays with Opus

| Check | Reader | Evidence |
|---|---|---|
| Glyph adjudication of masked letters from the ink (yer ъ/ь type) | **Sol, one reader** | 64/65 slots, identical to Opus E0a and E1; 63/65 = Opus E0b. Controls 11/11. |
| Line label check, **letters and crop_ok only** (LABEL_CHECK_v2 protocol) | **Sol, one reader** | bsb: letters 99/100, crop 98/100 (Opus 98–100 and 98–99). A second Sol reader changed nothing net. |
| **Grave/acute (and accent type) on final-accented words**, as a separate single-letter question | **Sol, one reader**, plus a fresh-context re-read of every flag, plus a human eye on the flags | SR-G1: grave 25/26, false grave 0/26. nlg poly1900 full pass: 316 words, 13 flags, 11 confirmed (incl. 1 that C1 missed), 1 false flag, p1/p2 13/13. |
| Marks inside the whole-line label check | **Not Sol.** Sol missed 3/3 printed-grave/label-acute errors in that task. Use the separate word pass above for accents; other mark types stay with Opus. | RESULTS.md, bsb |
| Four-head word-mark cards (R2-type: breathing/accent/diaeresis/subscript) | **Opus** (coordinator ruling) | Sol r1/r2 33/28 of 39; S2 33/39. The single-reader variance is too high. |
| Bootstrap audit | **Opus, until the owner rules** | — |

## 2. Settings
- **Model and flags:** `gpt-6.1-sol`, `model_reasoning_effort=medium`, Codex CLI 0.159.2, `codex exec`. The flags are:
  - `--sandbox workspace-write`, with cwd = the reader folder;
  - `sandbox_workspace_write.network_access=false`, `web_search="disabled"`;
  - `features.multi_agent=false`, `features.remote_plugin=false`, `features.apps=false`;
  - `project_doc_max_bytes=0`, `approval_policy=never`;
  - stdin = the prompt.

  Launcher: `launchers/run_read.sh`. It asserts the model from the rollout and prints token usage.
- **Items per context:** all items of a batch in one context. Use **≤100 items per context** (≤90 bed items plus about 10% controls).
- **Images:** the reader uses the `view_image` tool on files in its own folder, and makes zooms or montages with ImageMagick under `./zoom/`. It batches views (10–20 tool calls per 50–110 items).
- **The pipeline per run** is `launchers/run_bed.sh`, `run_grave.sh` or `run_full.sh`:
  1. limit probe;
  2. reading run;
  3. rollout leak scan;
  4. answer mapping or scoring;
  5. limit probe;
  6. ledger entry.

  The scripts hard-code this session's scratchpad PACK_ROOT and the `opus/sol-reading` worktree. Copy them and change `S`/`W` for your own track.
- **Python:** Pillow tools need `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B`. The default `python3` is arm64 and cannot load that Pillow.
- **stdin:** `codex exec` must get `< /dev/null` when no prompt is piped, or it waits forever.

## 3. Prompts (verbatim files)
- `prompts/yer.md`: glyph adjudication.
- `prompts/bsb.md`: line check. Use it for letters and crop only, and ignore its marks field for decisions.
- `prompts/grave.md` (identical to `prompts/grave_full.md`): the single-letter accent question.
- `prompts/owner39.md`: R2 word cards, for reference only; that check stays with Opus.

Each prompt is the Opus protocol verbatim plus a GPT-6-guide wrapper (`GUIDE_NOTES.md`). The wrapper adds:
- a non-interactive "do not ask, finish this turn" header;
- `view_image` and shell-write tool names;
- batched views;
- a "Done when" block (count, order and coverage checked once by a command).

Do not edit a protocol body without re-running a comparison.

## 4. Pack layout and blinding
- **Location.** One folder per reader context: `PACK_ROOT/<bed>/<reader>/`, OUTSIDE every repository and away from keys. PACK_ROOT holds only bed folders and `MANIFEST.<reader>.json` files beside them. Never put contact sheets, keys or reports there.
- **Folder contents.** Only the item file (`cards.jsonl` or `items.jsonl`), `img/` or `crops/`, and for R2-type packs `README.md` and `answer_schema.json`. The reader may add only `answers.jsonl` and `zoom/**`.
- **Items.**
  - Opaque fresh ids (`k` + 10 hex).
  - Content-hash PNG names; copied, with no links and no metadata.
  - Seeded random order; reader 2 gets the exact reverse; a tie-break gets a fresh order.
  - Option letters permuted per card.
- **Public fields only.** Never the Google text in the accent pass. Never source ids, strata, truth or notes.
- **Controls, about 10% per context.**
  - Pixel-verified by a lead on a contact sheet before any reader starts.
  - Indistinguishable from bed items: same option count, same fields, same rendering.
  - Never drawn from the stratum under test.
  - A context with more than one control error is flagged.
- **Builders and checkers.** Builders are `tools/build_packs.py`, `grave/` (SR-G1) and `grave_full/tools/build_full.py`. Closure checker: `tools/scan_packs.py`.

## 5. Leak scan (mandatory; any violation voids the run)
**The Codex sandbox does NOT restrict reads.** A canary outside the workspace was readable. Blinding therefore rests on the isolation in section 4 plus `tools/scan_rollout.py` **v4.5**, run on every rollout (original v4 retained byte-for-byte as `tools/scan_rollout_v4.py`):
1. **Image provenance.** Every image returned to the model must match a file in its own reader folder:
   - by bytes; or
   - as a proven `view_image` return at a common non-upscaling scale (each axis within 1 px; RGB mean absolute difference strictly < 2/255 under a named standard filter; fully opaque alpha); or
   - **(v4, coordinator-accepted)** as a pixel-exact reproduction. Replay the run's literal, relative-path commands on a fresh copy of the original pack, then compare pixels. This covers a zoom file the reader viewed and later overwrote; the PNG timestamp bytes may differ.

   The replay log is kept in the scan JSON (`reproductions`). Example: `answers/grave_full/p1c1.scan.json`.
2. **Literal strings in every tool input.** Violations:
   - absolute paths outside the reader's own folder;
   - `..` or `~` path components, `$HOME`, `/Users/`;
   - names matching `keys/`, `*key*.json`, `truth`, `verdict`, `opus_reference`, `MANIFEST`, the pack root or a sibling reader.

   Code idioms such as `.keys()` are not violations. The reader's own absolute folder path is not a violation.
3. **Manifest.** Originals intact; only `answers.jsonl` and `zoom/**` added.

### Scanner versions

| version | rule | witness rollout + expected result | test name |
|---|---|---|---|
| v4 (archived) | Original provenance, literal-path and manifest rules; literal-command pixel-exact reproduction | Synthetic overwrite clean; altered pixel/mode/alpha and unsafe replay VOID | `ReproductionTests.test_synthetic_overwrite`; `test_one_pixel_difference_fails`; all 11 original v4 tests retained |
| v4.1 | Resolve the exact pwd template from recorded successful pwd output equal to reader_dir; literal const-base/store/load templates before path checks | `rollout-2026-10-17T16-05-06-01a149f7-4d1e-7f80-ad8d-aff3b314a204.jsonl` (kosmo2 c2b), clean; record 27; 53 exact + 11 downscales | `test_witness_v41_kosmo2`; `test_pwd_positive`; `test_pwd_missing_output_fails`; `test_literal_base_templates`; `test_store_template_positive_and_negative` |
| v4.2 | Only statically proven read operands below `/System/Library/Fonts/` or `/Library/Fonts/`; unknown use/writes fail; other checks retained | `rollout-2026-10-17T16-49-41-01a14a20-1ea7-73a3-b472-2ff79d7093dc.jsonl` (ruc1 c1), clean; records 194/215; 27 exact + 54 downscales | `test_witness_v42_ruc1`; `test_font_read_both_roots`; `test_font_magick_proof`; `test_font_write_or_ambiguous_fails` |
| v4.3 | Resolve `load(NAME) + "literal"` (either quote) only from the same rollout's preceding literal `store(NAME, "…")`; unresolved concatenations fail | `rollout-2026-10-17T18-40-41-01a14a85-bfd9-75e3-b20f-a79f924d6dbf.jsonl` (CQ1 r1), VOID: record 24 still has unresolved outside path `/zoom/batch1.png`; `rollout-2026-10-17T18-57-48-01a14a95-6a88-7932-b4be-e126741b7e28.jsonl` (CQ1 r1b), clean | `test_witness_cq1_r1`; `test_witness_cq1_r1b`; `test_both_quotes_and_cross_record_binding`; `test_external_keys_still_fail`; `test_missing_store_fails_even_relative_suffix` |
| secondary pwd + // fixes | Exact literal pwd template base; Python `(j+1)//4` is not an absolute `/4` path | `rollout-2026-10-17T15-54-40-01a149ed-c0e3-7143-9bc9-11ac09eebd4d.jsonl` (RU1 ctx01/r2), clean; `rollout-2026-10-17T16-03-16-01a149f5-9e87-7a20-a543-62a90d71e078.jsonl` (ctx04/r2), VOID with exactly 15 provenance findings | `test_witness_ru1_ctx01_r2`; `test_witness_ru1_ctx04_r2`; `test_floor_division_positive`; `test_slash_outside_path_negative` |
| secondary exact pixels | Same mode, size and exact pixels permit PNG re-encoding; no downscale envelope change | Same RU1 witnesses: ctx01/r2 clean; ctx04/r2 remains VOID | `test_reencoding_positive_and_negative`; both RU1 witness tests |
| v4.4-canonical | One implementation combining the sourced rules above | All six external witnesses replayed with their recorded outcomes; none skipped | `test_scan_rollout_canonical.py` (42 tests including all 11 v4 cases); original v4 suite also run (53 total) |
| v4.5 | Coordinator ruling (18 Oct): P1 closed answer argv; P2 proven common-scale image returns; P3 finite literal view loops and historical confined-helper replay | CQ4E 15 VOID rollouts rescanned separately; original receipts retained | `tests/test_scan_rollout.py`; `tests/fixtures/v45/`; `out/scan2/rescan_v45.json` |
| v4.5.1 | SCAN2R H1–H3: closed independent shell units, helper invalidation before successful replay exits, pre-expansion literal path inspection | Three negative probe families (five concrete rollouts) remain VOID; offline CQ4 rescan compared with preserved v4.5 | `Scan2BProbes`; `out/scan2/rescan_v451.json`; `out/scan2b/HANDOFF.md` |
| v4.5.2 | SCAN2R2 H1: invalidate cached helper sources before expanded literal-argv replay, including helper-to-helper writes and self-overwrites | Both new negative histories remain VOID; offline CQ4 rescan compared with preserved v4.5.1 | `Scan2CProbes`; `out/scan2/rescan_v452.json`; `out/scan2c/HANDOFF.md` |
| v4.5.4 | SCAN2E: P1 uses the replay walker's single script cache, independent execution units and mutation barrier; current recorder bytes must equal its cached heredoc source before the AST-pinned answer exemption | Five SCAN2R4 recorder probes remain VOID; missing/changed current source and nonexecuting contexts also fail | `Scan2EProbes`; `out/scan2/rescan_v454.json`; `out/scan2e/HANDOFF.md` |
| v4.5.5 | SCAN2F: unconditional per-execution-unit write barrier, independent of integer argv and restricted-parser admission; unknown writes revoke all cached scripts; replay checks exact script bytes in its historical temporary filesystem | Both SCAN2R5 overwrite/rejection/final-restoration probes remain VOID; a new literal definition is required to regain authority | `Scan2FProbes`; `out/scan2/rescan_v455.json`; `out/scan2f/HANDOFF.md` |

Canonical v4.5.5 file sha256 = e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1; copy by hash, do not fork. Previous v4.4 sha256 = dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547; retained in the unchanged CQ4 receipts.

**Sources found, inspected read-only (SCAN1, 17 Oct).** v4.1 and v4.2 are in `../greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/kosmo2/tools/scan_rollout_v41.py` and `scan_rollout_v42.py`. Their witness reports are respectively `kosmo2/scan/kosmo2/c2b.scan_v41_final.json` and `ruc1/scan/ruc1/c1.scan_v42.json` under the same `w1_masked/` root. No v4.1/v4.2 source was found in sol-collect. The sourcing scratchpad launcher at `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/launchers/run_bed.sh` dispatches kosmo2/ruc1 to the sourcing worktree launchers; no separate scratchpad `scan_rollout*.py` source was found.

CQ1's wrapper and tests are in `../greek-ocr-toolkit-spellcheck-r2cards/artifacts/cq1/tools/scan_rollout_v43.py` and `test_scan_rollout_v43.py`; saved outcomes are `artifacts/cq1/answers/r1.scan_v43.json` and `r1b.scan.json`. Secondary's source is `../greek-ocr-toolkit-secondary/scripts/secondary/reading/scan_rollout.py`; `docs/labelfix/secondary/RU10_REPORT.md` §RU1-S and §RU1-R3 disclose both path fixes and the exact-pixel re-encoding delta. Exact secondary rollout identities are recorded in `artifacts/ru1/logs/RU1-ctx01.r2.codexlog` and `RU1-ctx04.r2.codexlog`.

The v4.3 literal-store restriction applies to concatenations. Ordinary non-concatenated loads with a preceding store, such as ctx04's `load("rows")` retain v4 behavior; a load with no preceding store still fails. Applying a path-resolution failure to those data loads would add 11 unsupported findings. v4.1's witnessed `${base}` / `${load("base")}` template idiom retains literal `const base` resolution; a const alone does **not** authorize a v4.3 `load(...) + ...` concatenation. Pwd resolution requires the successful recorded output; it never executes pwd during scanning. Font allowances use the sourced v4.2 operand proofs, not a global font-path exemption. Reproduction uses a fresh OS temporary directory rather than a session-specific scratchpad. The v4.4 image envelope was 2048 long side. The v4.5 envelope follows the coordinator rulings below; native same-mode pixel checks remain exact.

All six witness rollouts were found under `~/.codex/sessions/2026/10/17/`. Missing rollout files cause explicit unittest skips naming the missing file; present rollouts with missing packs fail. `tools/SCAN1_TEST_RESULTS.txt` records the full scanner test run. `tools/SCANNER_CANONICAL.json` records source/canonical/test hashes and all 11 known external scanner copies or entrypoints: **0/11 currently match**; none was modified. Network, reading runs and .git writes were not used.


### Canonical v4.5 coordinator rulings (18 Oct; SCAN2 qualification 19 Oct)

- **P1 — answer atoms are data only in confined-helper argv.** The closed shorthand grammar is `[nsru]\??/[nagcu]\??` for breathing/accent, `[yn]\??/[yn]\??` for yes/no heads, and decimal numeric ids. `?` denotes low confidence. Mask only complete argv to the historically recorded, AST-pinned `zoom/record.py`; the pin verifies its IO and category mapping. Real `/n`, `/tmp/outside`, `../truth.json`, mixed invalid atoms, shell additions and forbidden names retain their path checks. The helper filename alone grants no authority.
- **P2 — proven image returns.** Admit a common non-upscaling scale within one pixel on each axis, RGB MAD strictly below 2/255 under a named Pillow standard filter, and opaque alpha (including RGB to opaque RGBA for scaled returns). A new zoom scale requires reconstruction seeded only from verified manifest originals; final zoom files cannot seed it. Historical reconstructions use the same comparison. Native same-size comparisons retain exact mode/pixel behavior; crops, distortion, upscales, partial alpha and MAD >= 2/255 fail.
- **P3 — finite templates and recorded history.** Expand only literal arrays or constant integer ranges (at most 1,000 views), bind concrete requested paths in returned-image order, and reconstruct overwritten views at their historical point. Inline only recorded confined zoom helpers with literal integer argv through the existing restricted AST/API worker and IO audit hook. Isolate literal `mkdir zoom` / `mkdir -p zoom` and independently safe image heredocs from rejected imports or answer code. Dynamic bounds, unsafe helpers, traversal and unproven extra images fail.

Source: read-only `../greek-ocr-toolkit-spellcheck-r2cards/docs/labelfix/spellcheck/R2/CQ4E_VOIDS.md` and its 15 recorded rollouts. `out/scan2/rescan_v45.json` is a new scanner adjudication record, not an edit of the CQ4 ledger or acceptance/scoring of answers. Full scans, test log and deliverable details are in `out/scan2/`.

## 6. Measured cost
| Task | Wall per item | Tokens per item (total / uncached input / output) |
|---|---|---|
| Glyph adjudication (yer) | 1.7–2.2 s | 7.9–13.2k / 0.8–1.2k / 58–67 |
| Line check (bsb) | 1.6–1.9 s | 9.9–12.3k / 0.7–0.8k / 69–76 |
| Accent word pass (grave) | 1.2 s | 7.4k / 1.2k / 46 |
| Accent full-stratum pass (nlg, 4 contexts + re-read, 367 reads) | 1.3 s | 7.7k / 0.9k / 49 |
| R2 word cards (reference; stays Opus) | 3.2–3.4 s | 10.8–14.3k / 1.1k / 150–175 |

**Codex weekly meter.** Every Sol run today fits within 32% → 34% of the weekly bucket:
- 880 card-reads across 15 reading runs;
- plus 11 build and scoring briefs.

That is **≤ 0.2 weekly points per 100 card-reads**, as an upper bound. The meter has 1-point resolution and is shared with other sessions, so no run moved it measurably on its own (each read 0.0).

The meter resets Thu 22 Oct 09:13. Credits stayed at 59,974.71; credits must never be spent.

**Scale limit (coordinator ruling).** About 0.9–1.2k uncached and 7.4–13k total tokens per item puts release-scale correction (100k+ words) out of the Codex budget. Sol reading is for stratum checks, audits and the marks_bias strata.

## 7. Codex budget rule
- Probe before and after every run (`launchers/limit_probe.sh`): a one-word non-ephemeral `gpt-6.1-sol` call whose rollout carries `rate_limits`. Read `limit_id=codex` at the 10080-minute window.
- **Stop when weekly used reaches 80%**; the drivers refuse to start at ≥ 78%. Report the live percentage in every report.
- The owner's dashboard number wins over any probe.

## 8. Known gaps
- **Recall among unflagged items is not measured.** In the accent pass the 303 unflagged nlg words are assumed to match the label. Line checks have the same gap. Budget an occasional blind audit sample if a stratum's numbers matter.
- **"Unreadable" routing.**
  - Sol answers "unreadable" honestly. In the grave pass: 1/26 positives, 2/316 in the full pass. One of those 2 was readable to the lead (a grave, matching the label).
  - Route every "unreadable" and every flag to a human or Opus eye. Never auto-accept or auto-reject them.
- **Shared-model references.** The bsb reference and 16 owner39 truth forms are Opus readings. Sol-vs-Opus gaps of 1–3 items are within either model's run-to-run spread.
- **Small beds.** 65, 100, 39, 58 and 316 units. Re-measure on a new stratum before relying on these rates there.
- **Untested:** a full-stratum accent pass on lekythos and kosmopolis. The cheaper attachment form (`codex exec -i`, no zoom) is also unmeasured.
- **Open check (17 Oct, coordinator): Sol crop strictness on Cyrillic line ends.** On the ia_russian re-check (ruc1, sol/recut-v1 50147b93), Sol marked 15/100 crops `crop_clipped`. Opus C1 found 2/100 on the same source; the card sets differ, the crops are byte-exact regenerations, and Sol matched Opus on bsb crops. The 15 cards (in `ruc1/review_queue.jsonl`) go to an Opus eye after the Claude reset, before any conclusion about ia_russian crops or about Sol's crop_ok on Cyrillic.

## 9. Contacts and files
- **Owner / lead:** the secondary-corrections lead (coordinator ruling, 17 Oct). Canonical scanner changes belong in this worktree; other leads copy by hash and do not fork.
- **Briefs:** `briefs/SR-*.md`.
- **Usage ledger:** `usage_ledger.json`.
- **Launchers:** `launchers/`.
- **Lead pixel reviews:**
  - `keys/control_review/LEAD_REVIEW.md`;
  - `grave/keys/control_review/LEAD_REVIEW.md`;
  - `grave_full/LEAD_EYE.json`.
