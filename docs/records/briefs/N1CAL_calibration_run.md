# N1-CAL: run the calibration reading and score it (gpt-6.1-sol, medium, network ON for the nested reader only; no .git writes)

Worktree `~/Projects/greek-ocr-toolkit-secondary`. The calibration pack is built and closure-checked (N1-Cd). You are the
**operator**, not the reader: never open the calibration images, the keys or the pack contents yourself.

**Do.**
1. **Run** `scripts/secondary/reading/run_n1.sh n1cal cal01 r1` exactly once. It probes the limit, launches the blind reader through
   `run_read.sh` (a nested `codex exec`), leak-scans the rollout, maps the answers, probes again and writes the ledger.
   - If the nested `codex exec` cannot start inside your sandbox (permissions on `~/.codex`, network, keychain), STOP. Report the exact
     error and the command, and do not work around it. The lead will then run the launcher by hand.
   - If the launcher refuses at ≥78% weekly use, stop and report.
2. **Score** with the launcher's calibration output, against `artifacts/n1/controls/approved.jsonl`:
   - per-class accuracy over the 82 items (raised dot 4, baseline dot 21, comma 23, hyphen or dash 27, nothing 7);
   - a confusion matrix;
   - low-confidence counts;
   - the list of every disagreement (slot id, truth, answer, confidence).
3. **Gate** (lead ruling):
   - **PASS** needs all of: raised dot 4/4; no hyphen-or-dash or baseline dot answered as raised dot; and at most 3 disagreements
     overall.
   - Otherwise **HOLD**, with the disagreements listed.
   - Do not start the bed contexts in either case.
4. **Report** `docs/records/labelfix/secondary/N1CAL_REPORT.md`, with the leak scan result, the probes before and after, the tokens per
   item, and the gate verdict.
5. **Contact sheet.** For every disagreement, make a sheet in the scratchpad `n1_review/cal_disagreements.png` (zoom + line + truth
   + answer, built from the existing renders) for the lead's pixel check.

**Allowed writes:** `artifacts/n1/answers/`, `artifacts/n1/usage_ledger.json`, `docs/records/labelfix/secondary/N1CAL_REPORT.md`, the
scratchpad `n1_review/`, plus whatever the launcher itself writes.

**Last line:** `N1CAL <PASS|HOLD|BLOCKED>: scan <ok|VOID>; raised <n>/4; baseline <n>/21; comma <n>/23; dash <n>/27; nothing <n>/7; disagreements <n>; weekly <before>→<after>%`
