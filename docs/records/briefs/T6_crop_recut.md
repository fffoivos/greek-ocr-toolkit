# T6a: tighter vertical crop recut — reuse list, development, frozen parameters and harm test on F2 lines (gpt-6.1-sol, xhigh, network OFF, ≤ 120 min)

**Split.** This run (T6a) does steps 0, 1 and 3, using F2 data only. Step 2 (qualification on W1 rows) is a separate later run, T6b, which starts after W1 finishes. **Do not do step 2 here.**

**Owner decision, verbatim:** "ok do whatever you think best granted you start from the tools in our ocr repo we have already built not from scratch."

**Coordinator constraints:**
- **Tightening only.** The vertical bound comes from the line's own font band, clipped at the neighbouring lines' token boxes.
- **No new segmentation and no vertical expansion.** The `sol/label-geometry` audit found that an `expand_vertical` repair made things 22% worse.
- **Output.** Recut crops sit **beside** the originals and never replace them. Rows are admitted only after the gate.
- **Reuse.** The cutter must stay callable on any page that has Google geometry. Collection v2 will later use it as a training arm.

**Workspace.** This worktree, `~/Projects/greek-ocr-toolkit-sol-recut`, branch `sol/recut-v1`, from 4e95489d.
- Code goes in `greekocr/glyphs/`. Pick a new module name, or extend `recut.py` behind a flag; do not change existing defaults.
- Outputs go in `docs/records/harvest/recut_v1/`.

**Read-only inputs:**
- the main checkout `~/Projects/greek-ocr-toolkit`, which another agent works in;
- the `sol/label-geometry` branch: read it with `git show`;
- `~/Projects/greek-ocr-toolkit-sol-funnel-{gr,ia,intl}`;
- `~/Projects/greek-ocr-toolkit-sol-collect`;
- the **live W1 run root** `~/Projects/collect-v3-data/run`. W1 is running there; never write to it, never take its locks, and never touch `run.lock` or `collector.pid`.

## Step 0: list reuse before writing code

Write `docs/records/harvest/recut_v1/REUSE.md` before any new code. For each function you reuse, give the file:function, what it does, and why. Cover at least:
- `greekocr/glyphs/recut.py`: `fix_page`, the guide-line fit, and the neighbour-bounded Voronoi `_voronoi_keep`;
- `greekocr/glyphs/lines_api.py`, `line_structure.py`, `page_font.py`, `baseline.py`;
- `greekocr/pages/structure.py`: the four guide lines;
- `greekocr/pages/font.py`;
- the page-lines runtime at 046bd52, merged in 89c2817e;
- the cutter that produced the P1 crops: find it through the F2 tracks' `process_reads.one` and `montage.response_lines`.

Then list **exactly** what you add: the vertical-tightening rule, its parameters, and the clipping at the neighbours' Google token boxes.

The rule:
- top = the line's own ascender / accent line;
- bottom = the descender line, from its fitted guide lines, ± a small margin in x-height units;
- then clip at the nearest neighbour line's token-box edge above and below;
- **never extend beyond the original crop;**
- horizontal extent unchanged.

## Step 1: develop on F2 data only

Dev set: the 2f34ed52 v2 cards with crop_ok verdicts, at `~/Projects/greek-ocr-toolkit-sol-funnel-gr/docs/harvest/blind_checks_v1/v2/`:

| Source | Cards | crop_ok "n" |
|---|---:|---:|
| gazette_modern | 40 | 18 |
| lekythos_poly1900 | 40 | 11 |
| kosmopolis_poly1900 | 40 | 26 |
| ia_greek_latin | 40 | 3 |

There are also T4c and C0 cards for these strata. All of these come with their F2 page rasters and saved Google responses.

Tune the margin parameters on these lines only. Report per source:
- before/after crop height in x-heights;
- the share of crops changed;
- for the crop_ok "n" cards: whether neighbour ink (readable characters / letter bodies) is now outside;
- for the crop_ok "y" cards: whether any of the line's own ink, accents or descenders is now cut. Use an ink-loss measure: own-line component pixels lost.

Freeze the parameters, and record their hash, **before** step 2.

## Step 2: qualify on fresh W1 rows (frozen parameters)

**Wait for W1 to finish:** `~/Projects/collect-v3-data/run/collector.exit` exists and the W1 status is complete. Then, for each of **Gazette modern, Lekythos and Kosmopolis**:
- run the frozen cutter on all W1 rows of that source (hold-tagged, post-fix usable). Write the recut crops and a per-row record (old box, new box, the parameters' hash) to `docs/records/harvest/recut_v1/w1/<source>/`. The W1 tree stays untouched.
- emit **100 uniform seeded cards per source** of recut crops in the v2 card shape: card_id, crop, google_text, word_scripts, with a separate key. Use `LABEL_CHECK_v2.md` unchanged; the crop_ok definition is unchanged.

I run the blind checks. The gate per source:
- recut crop_ok ≥ 90%, **and**
- letters-y not lower than the same source's v2 letters-y, **and**
- no own-ink cut-off seen. The checker's crop_clipped verdicts are the evidence.

**Also IA Greek+Latin:** its v2 crop result was 35/40 = 88%, under the line, so run the same cutter and emit 100 cards for it as well.

## Step 3: harm test (this run, Mac CPU, ≤ 10k crops, network OFF)

**Model.** E4 wave 1a `ctrl_s0`, which uses the same recipe as E3 full: `~/Projects/greek-page-ocr/out/e4/wave1a/job01/runs/ctrl_s0/best.pt` (or `best.safetensors`). It is already on the Mac, sha-verified against Clariden (see `out/e4/wave1a_readback/sha256_comparison.json`). Record its sha256. Do not contact Clariden.

**Lines.** All post-fix usable F2 lines of Gazette modern (years ≥1982), Lekythos poly1900, Kosmopolis poly1900 and IA Greek+Latin, up to 10k, stratified by source. These are the `screen_v1/features.jsonl` rows with the F2 rasters and responses.

**Method.**
- Run the E3/E4 evaluator (`bench.e1_eval.evaluate_run`, or the E3 readout path in `greek-page-ocr`) on the **same lines**, once on the original crops and once on the recut crops.
- The labels are the post-fix Google labels.

**Report, paired** (bootstrap CI on the difference), per source and overall, and also split into:
- (a) lines whose crop the recut **changed**, and (b) lines it left **unchanged**;
- (c) the dev-card subsets: crop_ok `n` vs `y`;
- (d) the geometry-clean subset, where an audit list exists: lines that are G1b-negative and carry no `screen_merged` flag.

This keeps a gain on merged-crop lines from being masked by the clean majority. **The rule: CER must not get worse overall.** Report the per-source numbers either way.

## Hand-off
Under `docs/records/harvest/recut_v1/`:
- `REUSE.md`;
- `REPORT.md`: dev results, then the frozen parameters, the qualification card sets, and the harm test;
- a per-source `receipt.json` with parameters, hashes and both test results, plus the card paths for the blind checks;
- tests for the cutter: tightening never exceeds the original box; neighbour clipping; idempotence; it is callable on any page with Google geometry.

Commit with a guarded helper that excludes git-ignored paths. The last line must be exactly:
`T6a: done | reused: <n> functions added: <n> | dev neighbour-ink removed: <x>% own-ink loss: <y>% | harm CER orig/recut overall: <a>/<b> changed-lines: <c>/<d> | params: <sha12> | model: <sha12>`
