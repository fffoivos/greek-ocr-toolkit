# N1-R: the raised-dot/dash ink rule — fit, freeze, locked-eval packs (gpt-6.1-sol, medium, network OFF; no .git writes; NO reading, browser or computer-use)

Worktree `~/Projects/greek-ocr-toolkit-secondary`. Plan: PLAN §2 (steps 2 and E), §9, §13. The N1 plan's coordinator condition 2:
the rule is built from the toolkit's existing helpers (`greekocr.glyphs.components` and the x-height/baseline estimates) and keeps a
per-slot decision record.

**Fitting truth (development documents only).** Use the line-complete decisions from N1-T/N1-TS3, all of them under
`artifacts/n1/`:
- two/three-read agreements;
- lead rulings (`lead_t.jsonl`, N1T_LEAD_RAISED.md);
- the approved controls with their dash types.

Assert with `greekocr.numerics.locks` that no fitting row is reserved.

**Do.**
1. **The rule**, in `greekocr/numerics/ink_rule.py`, with tests. Per slot, from the side measurement record (computed for any slot
   with the existing renderer helpers):
   - component count, bbox, height relative to digit height, vertical centre relative to the baseline–digit-top band, width relative
     to the median digit width, gap width;
   - output class: raised dot / baseline dot / comma / hyphen / en dash / em dash / space / nothing / unsure.
   - Thresholds are fit on a seeded 50% split by document, and the other 50% is the held-out dev.
   - Report a confusion matrix on the held-out half. The primary is raised-dot precision against hyphen and baseline dot.
   - Freeze the thresholds into a JSON file with its sha (the rule hash).
2. **Edit rule (release).** Google `-` or `.` between digits → `·` ONLY where the ink rule says raised dot with margin ≥ the frozen
   threshold. Nothing else is edited. Dashes stay tag-only per the owner; output the dash type as a TAG.
   - Never edit a slot whose ink shows a hyphen-length stroke.
   - An unsure slot means no edit and a tag.
   - Every slot writes a decision record: measurements, class, margin, rule hash.
3. **Locked eval packs, built only AFTER the rule hash is frozen.**
   - For the 258 `n1_locked_eval` lines (`artifacts/n1/n1_locked_eval_line_ids_alt.txt`), enumerate all numeric gaps
     line-complete.
   - Read set: (a) every gap where Google wrote `-` or `.` between digits; (b) every gap where the frozen rule says raised dot or a
     dash; (c) a seeded 10% of the remaining marked gaps.
   - Build r1/r2 packs with the sep2 prompt, under the scratchpad
     `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/n1e/`
     (NOT in the repo; the builder guard must refuse in-repo roots).
   - Controls as before; launcher root `n1e`; dry-runs.
   - Estimate the Codex cost at 0.2 points per 100 reads.
4. **Gate scorer** (fixture-tested now, run later), comparing the rule's decisions against the two-read truth plus the lead's
   rulings on the locked set:
   - raised-vs-hyphen precision ≥ 99%;
   - 0 false edits on true ranges (hyphen/dash truth);
   - report recall and the unsure rate.
5. **Train applier** `scripts/numerics/n1_apply_train.py` (fixture-tested now, run only after the gate passes):
   - input: all numeric tokens of the v2 training rows (`~/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl`)
     with their crops;
   - output: `artifacts/n1/n1_v1_train.jsonl` (parent label, new label, edits, tags, decision records ref, rule hash), plus a
     manifest and the LQB `versions.json` entry `n1_v1_train`.
6. Write the receipt `artifacts/n1/N1R_RECEIPT.json` and the report `docs/records/labelfix/secondary/N1R_REPORT.md`. Run the tests.

**Last line:** `N1R READY: rule sha <hex8>; held-out raised precision <x> (n <n>), recall <x>; hyphen→raised false <n>; locked read set <n> slots in <n> contexts ×2 (~<pts> pts); gate scorer + applier tests <n> passed`
