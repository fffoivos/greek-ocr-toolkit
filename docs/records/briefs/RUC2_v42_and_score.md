# RUC2: scanner v4.2 for ruc1 c1, then score the ia_russian re-check (gpt-6.1-sol, medium, network OFF, mechanical)

## Coordinator ruling
**Scanner v4.2:** read-only OS resource paths (`/System/Library/Fonts/**`, `/Library/Fonts/**`) are allowed in tool inputs. Every other absolute-path test is unchanged. Accept ruc1 c1 after the usual image-provenance check (exact or v4 downscale). Record v4.2 in HANDOVER §5 with this run as the witness: ruc1 c1, records 194 and 215, `/System/Library/Fonts/Helvetica.ttc`.

## Do
1. **v4.2 on ruc1 c1:**
   - Extend the kosmo2 v4.1 wrapper (`docs/records/harvest/recut_v1/w1_masked/kosmo2/tools/`) with the v4.2 allowance. The Sol-reading `scan_rollout.py` stays unchanged.
   - Re-scan c1 (rollout path in `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/ruc1_run.log`) and write `scan/ruc1/c1.scan_v42.json`.
   - **Any other violation means c1 stays VOID:** report and stop.
   - Tests: the witness passes; a non-font outside path still fails; a font path *written to* still fails (read-only only).
2. **HANDOVER §5:** prepare a hash-guarded patch adding the "v4.2 (coordinator ruling, 17 Oct)" bullet, as KR3 did for v4.1, at `docs/records/harvest/recut_v1/w1_masked/ruc1/handover/HANDOVER.v42.patch`. The lead applies it.
3. **Score** c1 + c2, 100 bed cards:
   - letters and crop_ok (final), marks (pending_opus), controls, the review queue;
   - letters split by repaired-label cards (18) vs unrepaired (82);
   - a comparison with C1 on the old labels (letters 74, crop_ok 97; a different card set, not paired);
   - gate: letters ≥ 90 and crop_ok ≥ 90.
4. Write `docs/records/harvest/recut_v1/w1_masked/ruc1/RESULTS.md` + `results.json`. Leave guarded commit lists.

The last line must be exactly:
`RUC2: <done|c1 VOID> | v4.2 witness: <ok> | letters y: <n> (repaired <a>/18, unrepaired <b>/82) | crop_ok y: <n> | controls: <k>/10 | gate: <pass|fail> | review queue: <n>`
