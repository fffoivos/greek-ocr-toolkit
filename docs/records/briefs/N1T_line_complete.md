# N1-T: line-complete separator reading, dash typing, owner sheet v2 (phase A build) (gpt-6.1-sol, medium, network OFF; no .git writes; no reading run)

Worktree `~/Projects/greek-ocr-toolkit-secondary`. Read first: `docs/records/labelfix/secondary/PLAN.md` §2, §8 and **§9 (the owner's
feedback, binding)**, `N1S_REPORT.md`, `N1C_REPORT.md` and the new prompt `docs/records/labelfix/secondary/prompts/sep2.md` (do not edit it).
N1-R2 was stopped before finishing; nothing of it is used, and any partial r2 folders it left are kept but ignored.

**Phase A scope.**
- The LINES on the current owner sheet (`artifacts/n1/owner_sheet/summary.json`: every card's line).
- Plus every line carrying a slot read in a VALID r1 context with Google `-` inside a 4+-digit token.
- All lines come from the step1 documents only. Assert with `greekocr.numerics.locks` that no reserved line is touched.

**Do.**
1. **Line-complete enumeration** (in `greekocr/numerics/`, with tests). For every phase-A line, enumerate EVERY numeric token
   (`tokens.py`) and EVERY inner gap and boundary separator slot. Localise each with the existing exact symbol geometry; failures are
   recorded per slot and never guessed. Render the marked zoom for each slot and its side measurement record, reusing the existing
   renderer and v3 markers.
2. **Dash geometry** (no fitting). For every slot whose ink has a horizontal stroke component, record:
   - `dash_len_ratio` = stroke length ÷ the median width of the token's digits;
   - its height and vertical centre relative to the digit band.

   Propose a geometric type: hyphen < 0.75 ≤ en dash < 1.45 ≤ em dash. These are starting thresholds, and are reported, not tuned.
3. **Dash controls.**
   - Render a sheet in the scratchpad `n1_review/dash_controls.png` of the 27 approved "hyphen or dash" controls: marked zoom plus a
     ruler showing one digit width, NO ratio printed, cell numbers continuing the control numbering (49…81).
   - The lead assigns hyphen / en / em on that sheet.
   - Write `artifacts/n1/controls/dash_types_template.jsonl`.
4. **Packs for sep2.**
   - The builder accepts the new meaning set: raised dot, baseline dot, comma, hyphen, en dash, em dash, space, nothing, other,
     unreadable. Options are permuted per item.
   - Calibration pack v2 (`sol_packs/n1cal2/cal01/r1/`) from the 82 approved controls. Dash controls are scored against the lead's
     dash types once those are filled; until then the builder refuses with a clear message.
   - Bed packs for the phase-A slots: r1 and r2 (r2 = exact reverse, fresh ids and permutations), ≤100 items per context with ≈9
     controls, ≥1 raised-dot control each, under `sol_packs/n1t/ctxNN/{r1,r2}/`. Run closure on all of them.
   - `run_n1.sh` gets roots `n1cal2` and `n1t` and uses `sep2.md` for them. Run a dry-run check.
5. **Combiner v2** (with tests). Per slot:
   - two agreeing reads from gate-passing contexts → truth candidate;
   - a void-context read is only ever a second vote;
   - the reader's dash type vs the geometric type: a disagreement → lead_review;
   - everything else → lead_review.

   **Edit rule.** Google `-`/`.` → `·` only on a raised-dot truth candidate in a grammar-thousands slot. Dash types are TAGS ONLY in
   labels (no text edit) per the owner's standing ruling. The "Ours" line, however, shows them typed.
6. **Owner sheet v2** builder (run it only after the readings; test it now on fixtures). Republish target: same file path
   `artifacts/n1/owner_sheet/n1_sheet.html`. One card per LINE, doc id = line id:
   - `image`: the line crop with EVERY slot boxed and numbered (`slots`);
   - `zooms`: one marked zoom per slot that is not "nothing", alt "gap N";
   - `rows`:
     - `Google`: the W1 `text`;
     - `Ours`: the full line with our reading applied: · for raised dots, the reader/geometry dash type as - – —, and Google's
       character kept where we are unsure;
     - `Gaps`: per slot N, Google's character → ours, each named in words ("hyphen (-)", "en dash (–)", "em dash (—)", "raised
       dot (·)", "full stop (.)", "comma (,)", "space", "nothing"), plus agreement/confidence;
   - `printed`: PREFILLED with the Ours line (owner's request), with `data-printed-source="ours-proposal"`;
   - `tags`: changed / unchanged, dash types present, source/era;
   - `group`, in this order: "Raised dot written as hyphen by Google"; "Dash type differs from Google"; "Other disagreements";
     "Needs a look"; "Agreement sample (12)".
   - **intro:** one sentence naming the printed marks; one saying "Ours" is our reading of every gap, prefilled in the editable field
     for you to correct; one saying dashes are only tagged in the training labels for now.
7. **Receipt and report.** Write `artifacts/n1/N1T_RECEIPT.json` and a report `docs/records/labelfix/secondary/N1T_REPORT.md`, with:
   - phase-A lines and slots;
   - geometry status;
   - the dash-ratio distribution per Google glyph (histogram table);
   - pack and context counts;
   - a Codex estimate at 0.2 points per 100 items.

   Run the tests.

**Last line:** `N1T READY: phase-A lines <n>, slots <n> (geometry ok <n>); dash slots <n> (geo hyphen <n>, en <n>, em <n>); dash-control sheet <path>; contexts <n> ×2 readers + calibration; closure <ok>; tests <n> passed`
