# KR3: accept kosmo2 c2b under ordinary v4 provenance, then score (gpt-6.1-sol, medium, network OFF, mechanical)

**Coordinator clarification:** "pixel for pixel" meant the **ordinary v4 image-provenance standard**: exact match, or a v4 downscale (long side 2048, aspect within 1 px, MAD < 2). It did not mean strict identity. **c2b passes.**

## Do
1. Re-evaluate `scan/kosmo2/c2b.scan_v41.json` under v4.1 = v4 image provenance (exact or v4 downscale) + resolution of template/pwd paths.
   - Expected: 53 exact + 11 v4-downscale matches = 64/64, and no other violations. Write `c2b.scan_v41_final.json`.
   - Correct the v4.1 wording in the HANDOVER §5 bullet and the local wrapper so that image provenance is the ordinary v4 rule (exact or downscale). Update the tests.
2. Do KR2 step 3: score c1 + c2b, 100 bed cards:
   - letters and crop_ok (final), marks (pending_opus), controls, the review queue;
   - paired against the pre-handover SRK2 (87db4392: 96/99) on the same 100 cards, with agreement and flips.
   - SRK stays recorded as "pre-handover, no controls".
3. Update `RESULTS.md` / `results.json`. Leave guarded commit lists for both worktrees.

The last line must be exactly:
`KR3: done | c2b accepted (v4.1) | letters y: <n> | crop_ok y: <n> | marks y: <n> (pending opus) | controls: <k>/10 | paired agreement letters/crop: <a>/<b> | review queue: <n>`
