# SR-G5: fix the confirm_full closure check and produce the flag review

Work non-interactively in `~/Projects/greek-ocr-toolkit-sol-reading`, and finish in this turn. The constraints are as in SR-G4. Pillow: `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B`.

`grave_full/tools/confirm_full.py` fails with "Invalid/incomplete reread or lead review: Reader root closure". The p2 reader folder (`PACK_ROOT/grave_full/p2/`) now legitimately contains the reader's `answers.jsonl` and `zoom/**`. The check must apply the same rule as `scan_rollout.py`'s manifest check: originals intact against `MANIFEST.p2.json`, and only `answers.jsonl` and `zoom/**` added.

1. Fix the check, and add a test for a completed reader folder.
2. Run `confirm_full.py`. The p2 answers are at `answers/grave_full/p2.jsonl`; the scan is at `answers/grave_full/p2.scan.json`, and it must be ok. Produce:
   - `grave_full/FLAGS.md`;
   - the review sheets `grave_full/keys/review/flags_<k>.png`;
   - `grave_full/LEAD_EYE.template.json`.

   The p2 controls go in FLAGS.md.

Last line: `SR-G5 READY: flagged=<n> p1/p2 agree=<x>/<n> p2 controls=<x>/<n> sheets=<k>`, or `SR-G5 BLOCKED: <reason>`.
