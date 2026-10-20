# LQB1: truth_v1, version registry, scorer, first scoreboard (gpt-6.1-sol, medium, network OFF; no .git writes; NO reading)

Worktree `~/Projects/greek-ocr-toolkit-secondary`. The plan is `docs/records/labelfix/lqb/LQB_PLAN.md`, binding, and the inputs are listed
by reference in `docs/records/labelfix/lqb/INPUTS.md`. Read both first, then the two peer reference files they point to. Everything outside
this worktree is read only: never write into another worktree or the collector root, and never take `run.lock`. Any remote path
(the sf6 release) is NOT fetched in this brief; record it as `remote_unfetched` with its receipt sha.

**Do.**
1. **Truth set** `docs/records/labelfix/lqb/truth_v1.jsonl` (via `scripts/lqb/build_truth.py`, with tests).
   - **Record:** `{truth_id, line_id, slot|null, class, printed, provenance{set, file, sha256, commit}, readers, tier (A|B|C),
     used_by[], exclude_from_training, doc_id}`.
   - **Classes:** marks (per head), letters, n1_separator (with dash type), ru1_yer, ru2_yat, superscript, dash, lunate, lookalike,
     capitals, crop.
   - **Tiers:** A = the owner, or two blind Opus readers; B = a lead pixel ruling; C = two agreeing Sol reads. Map every set to one
     tier from the provenance in the peer files. If a set's tier is unclear, list it in the report; never guess.
   - `used_by` comes from the in-sample maps (spell-check map in INPUTS.md; this track: the RU1 review rows are in-sample for
     ru1_v1, the RU1 audit rows are not; the N1 approved controls are in-sample for any N1 rule).
   - `exclude_from_training`: per INPUTS.md (T2 = false).
   - Deduplicate by (line_id, slot, class). A conflict between two truth sources goes to `conflicts.jsonl` and never into truth.
   - Freeze with a sha into `truth_v1.manifest.json`, with counts per class × tier × set. Also write
     `truth_v1_exclusion_ids.txt` (the line ids where exclude_from_training is true) for the sourcing lead to register.
2. **Version registry** `docs/records/labelfix/lqb/versions.json`, each entry with path, sha256, population, parent and how a line's text is
   read from it:
   - `google_raw` (W1 features `text`);
   - `w1_label` (W1 `label`);
   - `ru1_v1`, which overlays `w1_label`;
   - `w1_masked_1d` (label = w1_label for its rows);
   - `sf6_release` (`remote_unfetched`, scored only where a local copy exists).
3. **Scorer** in `greekocr/labelfix/lqb.py` (new module; do not modify existing labelfix modules), CLI
   `python -m greekocr.labelfix.lqb score --truth T --version A [--version B]`. Per class and tier:
   - errors / items;
   - errors per 100 items;
   - **paired A→B delta** on the items both versions cover, with a document-cluster bootstrap 95% interval (reuse
     `greekocr.adjudicate.score` where it has Wilson/bootstrap; otherwise implement and test it);
   - in-sample items reported in a separate column, never in the headline;
   - "not measured" where a version does not cover the class population.

   Comparison per class: marks via the existing union scorer for the four heads if importable; n1 by gap glyph class; ru1/ru2 by the
   letter at the offset; letters by edit distance on the aligned line; and so on. Document each.

   Add a `trend` subcommand across all registered versions. Tests cover: a paired delta on a toy truth set, a cluster bootstrap with
   a fixed seed, in-sample separation, and not-measured handling.
4. **First run:** `google_raw` → `w1_label` → `ru1_v1` (and sf6 if a local copy exists). Write `docs/records/labelfix/lqb/SCORE_v1.md` and
   `score_v1.json`.
5. **Scoreboard page** `docs/records/labelfix/lqb/scoreboard.html`, built with `greekocr.adjudicate.owner_sheet.render`, run under
   `~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python` with `PYTHONPATH=~/Projects/greek-ocr-toolkit-cleanup`. Contents:
   - **title** "Label Quality Scoreboard";
   - **intro:** a summary table rendered as the intro HTML (class | version | errors per 100 | change vs previous | 95% interval | in
     words: "fewer / more / no clear change"), tier A+B only, plus a "not measured" list;
   - **cards:** every truth line whose correctness CHANGED between consecutive versions, with rows Google / each version / Truth,
     Printed prefilled with the truth form (it is adjudicated), and tags class / tier / changed-direction;
   - under 14 MB.
6. Write the receipt `docs/records/labelfix/lqb/LQB1_RECEIPT.json` and a report section in `SCORE_v1.md`. Run the tests.

**Last line:** `LQB1 READY: truth <n> items (A <n>, B <n>, C <n>; classes <n>; conflicts <n>); exclusion ids <n>; versions <n> (<k> scored); headline <one line per class>; scoreboard <MB> MB cards <n>; tests <n> passed`
