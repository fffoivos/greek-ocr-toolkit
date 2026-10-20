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
**The Codex sandbox does NOT restrict reads.** A canary outside the workspace was readable. Blinding therefore rests on the isolation in section 4 plus `tools/scan_rollout.py` **v4**, run on every rollout:
1. **Image provenance.** Every image returned to the model must match a file in its own reader folder:
   - by bytes; or
   - as a `view_image` downscale (long side 2048; aspect within 1 px; pixel mean absolute difference < 2); or
   - **(v4, coordinator-accepted)** as a pixel-exact reproduction. Replay the run's literal, relative-path commands on a fresh copy of the original pack, then compare pixels. This covers a zoom file the reader viewed and later overwrote; the PNG timestamp bytes may differ.

   The replay log is kept in the scan JSON (`reproductions`). Example: `answers/grave_full/p1c1.scan.json`.
2. **Literal strings in every tool input.** Violations:
   - absolute paths outside the reader's own folder;
   - `..` or `~` path components, `$HOME`, `/Users/`;
   - names matching `keys/`, `*key*.json`, `truth`, `verdict`, `opus_reference`, `MANIFEST`, the pack root or a sibling reader.

   Code idioms such as `.keys()` are not violations. The reader's own absolute folder path is not a violation.
3. **Manifest.** Originals intact; only `answers.jsonl` and `zoom/**` added.

- **v4.1 (coordinator ruling, 17 Oct).** Resolve pwd/template paths using the reader's recorded successful `pwd` output before the absolute-path test (including literal base/store/load bindings). Image provenance remains the ordinary v4 rule: exact match or a v4 downscale (long side 2048, aspect within 1 px, RGB MAD < 2); the v4 pixel-exact reproduction route and all other checks remain unchanged. Witness: kosmo2 c2b, record 27; final acceptance 53 exact + 11 v4-downscale matches = 64/64, no violations. Local wrapper: `../greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/kosmo2/tools/scan_rollout_v41.py`; final scan: `../greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/kosmo2/scan/kosmo2/c2b.scan_v41_final.json`.

- **v4.2 (coordinator ruling, 17 Oct).** Read-only OS resource paths under `/System/Library/Fonts/**` and `/Library/Fonts/**` are allowed in tool inputs. Every other absolute-path test is unchanged; font writes remain violations. v4.1 resolution and ordinary v4 image provenance (exact or v4 downscale) remain unchanged. Witness: ruc1 c1, records 194 and 215, `/System/Library/Fonts/Helvetica.ttc` used as ImageMagick `-font` input; 27 exact + 54 v4-downscale matches = 81/81, no violations, manifest check enabled. Local wrapper: `../greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/kosmo2/tools/scan_rollout_v42.py`; final scan: `../greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/ruc1/scan/ruc1/c1.scan_v42.json`.

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
- **Lead:** the "Sol reading experiments" session.
- **Briefs:** `briefs/SR-*.md`.
- **Usage ledger:** `usage_ledger.json`.
- **Launchers:** `launchers/`.
- **Lead pixel reviews:**
  - `keys/control_review/LEAD_REVIEW.md`;
  - `grave/keys/control_review/LEAD_REVIEW.md`;
  - `grave_full/LEAD_EYE.json`.
