# LF1: benchmark last-filter check tool + 100-line dry-run packs (gpt-6.1-sol, medium; network OFF; no .git writes; BUILD ONLY, no reading)

Night plan step P6 (`~/Projects/greek-ocr-toolkit-main-next/docs/programme_20261019/NIGHT_PLAN.md`): every benchmark-0.2 candidate line
(crop + corrected label) gets one Sol card check before the benchmark is sealed. You build the tool and the dry-run packs. The lead runs
the reader contexts (nested Sol readers cannot run from your sandbox).

## The check (owner's rules only; add no rule, guard, threshold or heuristic of your own)

The owner's segmentation standard (19 Oct; `docs/CONTEXT_20261019_spellcheck.md` rule 1): a crop is good only if
(a) there is exactly one central line of text; (b) the label matches the visible line exactly, neither more nor less (text running past
the crop, omitted visible spans, letters cut through, merged lines = fault); (c) no other line shows completely, and other lines show at
most 2 WHOLE words (100% visible); cut neighbour words and partial letter bodies are allowed. Turned (rotated) or clipped crops fail.

Each card has one verdict:
- `OK`
- `CROP_VIOLATES` + one or more of `one_central_line | text_ne_visible_line | other_complete_line | gt2_whole_neighbour_words | turned_or_clipped`
- `TEXT_DIFFERS` + `where` (the differing span: label substring and what is printed)

The reader may record its own reading of the line as **evidence only**. It never replaces the label and never decides the verdict
by itself.

**Prompt: reuse, do not invent.** Start from the Sol-qualified line-check protocol
`~/Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/prompts/bsb.md` (LABEL_CHECK_v2: letters and crop only; ignore its
marks field). Keep its protocol body verbatim with its GPT-6 wrapper (`GUIDE_NOTES.md`). Find the segmentation rubric used for the owner's
sheets and SEGEVAL-1 (`~/Projects/greek-ocr-toolkit-main-next/docs/records/harvest/collect_v3_admission/segeval1/`,
`docs/B_training_data/b_tools/SEGMENTATION_FILTER.md` there). Where bsb lacks one of the five crop rules, add that rule's owner wording
as a separate question block. Then write a DETERMINISTIC mapping table (in code, tested) from the reader's answer fields to the verdicts
above. List in the report every prompt line you added, with its source.

## Pack and run rules (canonical scanner v4.5.5, `~/Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/tools/scan_rollout.py`)

- HANDOVER `~/Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/HANDOVER.md` §2–§7 apply.
- One folder per context with ONLY `items.jsonl` + `img/`. Opaque ids `k`+10 hex; content-hash PNG names, copied (no links, no
  metadata); seeded order.
- ≤100 cards per context: ≤90 bed cards + about 10% controls. Controls come from a frozen pool with keys outside the pack, covering
  OK and each fault type. List the control crops for the lead's pixel check.
- The prompt's Environment section: literal relative `view_image` paths only; each zoom written once under a new name in `zoom/`; only
  `-filter point`, `-resize`, montage/append (no `-rotate`); no font paths; create only `answers.jsonl` and `zoom/**`.
- Pack root outside every repo: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/lf1_packs/`.
  Keys under `artifacts/lf1/keys/` in this worktree.
- The fleet runner (`artifacts/lf1/RUN_ALL.sh`, adapted from the HANDOVER launchers / `artifacts/cq4/RUN_ALL.sh`):
  - ≤24 concurrent contexts;
  - a limit probe before and after each context (`artifacts/tr2/launchers/limit_probe.sh` pattern); refuse to start a context at
    ≥90% weekly (night plan);
  - scanner v4.5.5 on every rollout; a VOID context gets ONE fresh-context re-read, and a second VOID is recorded and left;
  - answer mapping → `verdicts.jsonl`; a ledger with tokens per context and probe readings.
- The replacement hook (`replace_flagged`): given the flagged ids and the draw's ordered overdraw list, take the next unused line of the
  SAME class + source, in draw order. Record every replacement. Do nothing else (no other selection logic). If none is left, record
  `UNFILLED`.
- Receipts: pack build (input shas, ids → line ids sealed in keys), per-context run receipt, scan result, mapping receipt.
- Tests on synthetic fixtures: mapping table, replacement hook, pack layout vs scanner replay (prove a heredoc-overwrite fixture is
  caught, the SS4c pattern), refusal at ≥90%.

## Dry run (build packs only)

- 100 lines from the frozen 888 calibration crops (`accepted-calibration-888`; see `docs/records/harvest/seg_steps/s1/` and
  SEGMENTATION_FILTER.md in main-next).
- Take them from the 135 that carry explicit owner ratings first (all of them if ≤100 fit, else a seeded stratified sample by class).
  Label = the label stored with each crop.
- Class: the benchmark-0.2 quota class scheme if it is defined anywhere (search `docs/programme_20261019/` and the benchmark docs in
  main-next); otherwise source × script. Say which one you used.
- 2 contexts of ≤100 cards with controls. Write `artifacts/lf1/DRYRUN_PLAN.md`: the commands the lead runs, the owner-rating truth file
  for the comparison (owner rating → expected OK / not OK), and the scoring script (`score_dryrun.py`: flag rate per class, agreement
  with the owner ratings, confusion table, tokens and weekly pp per 100 cards).

Read-only inputs from other worktrees; write only inside this worktree and the pack root. Nothing large in git (crops stay in the pack root
and are hashed in the receipt).

Report: `docs/labelfix/spellcheck/LF1_REPORT.md`. Final line: `LF1 READY: tests N passed; packs 2 (cards a+b, controls c); dry-run
lines 100 (owner-rated r)` or `LF1 STOPPED: <reason>`.
