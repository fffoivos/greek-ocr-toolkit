# SEG-CP7d: score the r2 fresh 100 (gpt-6.1-sol, medium, network OFF, no reading, no tuning)

Both r2 contexts are read and scanned clean (`seg/cp7/r2/scan/segcp7r2_{a,b}/r1.scan.json`, ok, 0 violations); receipts are in `seg/cp7/r2/receipts/`.

**Blocker in score_r2.py:** its `verify()` fails with "freeze drift: seg/cp7/runtime_r2.py", because CP7c2 amended that runtime-only file (the post-read closure fix). Make verify honour **exactly** that recorded runtime-only amendment:
- runtime_r2.py must match the amended sha recorded by CP7c2;
- **every other** freeze-bound file must still match `CP7_FREEZE_r2.json` (dd2e7234…);
- the screen/admission code and the sealed decisions must be unchanged.

If no amendment record exists, write one (`CP7_FREEZE_r2_amendment.json`: the file, the old and new sha, the reason, the CP7c2 commit 1eea5e9b) and state it.

Then run `score_r2.py` exactly as CP7c designed it:
- DROP-truth = neighbour_whole_word ∨ multi_line ∨ rotated ∨ horizontally_missegmented. `end_clip` is a separate known-class rate, reported with its agreement with `edge_clip_candidate`.
- Report: controls 10/10; mapped 100/100; confusion per screen and composed; geometry_unavailable reported as policy; rotated-miss; orientation_unknown verdicts.
- **The gate:** screen FP 0 and FN 0, controls 10/10, mapped 100/100, scans ok.
- Write the adjudication sheet plus contact sheet for every FP, FN, flag or unreadable.

Write `seg/CP7d_RECEIPT.md` and the commit list. The last line must be exactly:
`SEG-CP7d: done | amendment: <recorded|written> | controls <c>/10 | mapped 100/100 | screens TP <a> FP <b> FN <c> TN <d> | policy geometry_unavailable <g> (reader keep <k>) | end_clip known class <e> (candidate agreement <x>) | rotated-miss <m> | gate: <PASS|FAIL> | to adjudicate <n> | tests: <n> passed`
