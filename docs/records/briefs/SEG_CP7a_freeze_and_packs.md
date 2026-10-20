# SEG-CP7a: freeze the candidate and build the fresh uniform 100-card Sol read (gpt-6.1-sol, medium, network OFF, no reading)

**Authority:** CP7 of the ASTRA-SEG1 plan (`docs/records/reviews/astra_program_review_2026-10-06/ASTRA-SEG1_review_1.md`, §"Numbered PLAN", item 7). This brief is **part A**: freeze, carried fixes, draw, and packs. The readers run afterwards under the lead's launcher. Part B (score, adjudicate, staged replay) is a later brief. Read the plan item, CP1–CP6 receipts, and `~/Projects/greek-ocr-toolkit-sol-reading/HANDOVER.md` (the Sol-reading protocol, v4.2 + open checks).

**Owner standard (verbatim):**
- "the important thing is that really there are no full words showing from the top or bottom line, and that we use the tools we have already built for it, and that we also avoid badly segmented horizontal ones as well";
- "In general there has been at least a whole word from one of the other lines to show for it to be even worth considering for filtration".

## 1. Fix the two carried CP6-review mediums first (`docs/records/reviews/SEG_CP6_review.md`)
- **M1:** one named eligibility composition, shared with admission (no hard-coded whitelist in verify_cp5.py). State the height-rule boundary. Add regressions for the reviewer's counterexamples.
- **M2:** the CP5/CP7 acceptance summaries must require a **resolved, passing composed union**: unresolved_required, union KEEP losses and separator coverage all constrained.

## 2. Freeze
Immutable bindings in `seg/CP7_FREEZE.json`:
- code: admission + every SEG module sha;
- params: 801d517e and the thresholds;
- ledger: 76ea2d35…;
- geometry identities;
- codec / Serbian extension / lookalikes shas.

Re-verify the frozen-witness gate on the composed union: 22/22 KEEP, D 9/9 composed, C1 6/6, gallery 6/6.

## 3. Population and draw (pre-screen; both rejected and retained candidates are eligible)
- **Population:** the **pre-screen collector population**, i.e. W1 ∪ W2 rows with `candidate_usable == true` in the release strata (ADM4's included strata, applied to W1 and W2, Gazette included). These are taken **before** screen_merged, rotated_crop or any SEG screen. Exclude only rows in the registered locked/eval classes of `release_exclusions.json`, and the calibration witnesses (fresh-id exclusion).
- **Inputs:** the snapshots in `~/Projects/collect-v3-data/snapshots/` (`W1_features_<ts>.jsonl`, `W2_features_<ts>.jsonl` and `SHA256_<ts>.txt`), written by the lead when the W2 materialize ends (≈ 04:30). **Never read the live run root's features files**: a BSB collector run starts at 04:40 and its finalize removes them.
  - If the W2 snapshot is not there yet, prepare everything else, then poll that directory read-only, at most 60 min.
  - If it never appears, draw from W1 only and state it.
- **Draw:** a uniform 100-card draw, seed `seg-cp7:fresh100`, deterministic. Report the population size per source × class.
- **Crops:** regenerate byte-exactly with `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python` only (the `ensure_crop` logic, output outside the run root) and check crop_sha256.
- **Composed screen decision per drawn row,** computed now and **sealed**: never shown to readers. The fields are merged, neighbour_words, orientation, geometry_unavailable, orientation_unknown, and the text rules.

## 4. Packs (HANDOVER protocol)
- **Contexts:** 2 contexts × (50 bed + 5 controls). The 10 lead-approved controls are c057, c009, c013, c026, c046, c041, c029, c072, c035, c066 (as in CAPS1/W2C1), 5 per context. Use fresh opaque ids.
- **Location:** PACK_ROOT `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs`, beds `segcp7_a` and `segcp7_b`. Keys go outside, under `docs/records/harvest/collect_v3_admission/seg/cp7/keys/`.
- **Canonical scanner** `scan_rollout.py` copied **by hash** (sha256 `dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547`). Record the sha in every receipt.
- **Prompt:** `prompts/bsb.md` verbatim, **plus** an appended owner-standard crop rubric, `prompts/segcp7_crop_rubric.md`, which you write:
  - per card: `neighbour_whole_word: yes/no` (at least one complete word from another printed line visible; half-letters never count);
  - `multi_line: yes/no` (two or more complete lines);
  - `rotated: yes/no`;
  - `horizontally_missegmented: yes/no` (a line split, or crossing a column);
  - each with a one-line reason.
  - The rubric gives the owner's sentences verbatim, and must **not** leak any screen output.
- **Launcher:** write `docs/records/harvest/collect_v3_admission/seg/cp7/launch_cp7.sh`. It runs the 2 contexts sequentially via `launchers/run_bed.sh`, with the `limit_probe.sh` stop at ≥ 78%, and logs to `cp7/run.log`. **Do not run it.** The lead runs it.

## Tests
- deterministic selection; fresh-id exclusion; crop sha equality;
- opaque, public-only packs (no truth, flags or screen outputs reach readers);
- closure per context; scanner hash; 100/100 answer mapping prepared; controls 10/10 present;
- M1/M2 regressions.

No publish actions; nothing is written to the live root. Update `seg/CP7_COMMIT_LIST.json` and `seg/CP7a_RECEIPT.md`. The last line must be exactly:
`SEG-CP7a: done | M1/M2 fixed | freeze: <sha> | frozen gate 22/22, D 9/9, C1 6/6, gallery 6/6 | population: <W1 n + W2 n> | drawn 100 (screen-drop <k> sealed) | packs 2x55 | scanner sha ok | launch_cp7.sh ready | tests: <n> passed`
