# SRK2: audit and score the Sol reading of kosmopolis poly1850 (gpt-6.1-sol, network OFF, mechanical)

The Sol reader SRK-kosmo-r1 finished.
- Answers: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/sol_packs/kosmo_poly1850/r1/answers.jsonl` (100 rows).
- Rollout: `/Users/foivoskarounos-zamparloukos/.codex/sessions/2026/10/17/rollout-2026-10-17T13-34-29-01a1496d-6531-7151-992b-b43d6ea88cb1.jsonl`.
- Launcher JSON: wall 153 s, 881,869 total tokens (801,792 cached input), 17 exec calls, Codex 33.0% weekly.

## Do
1. **Rollout audit**, using the Sol-reading lead's `tools/scan_rollout.py` (read-only, `~/Projects/greek-ocr-toolkit-sol-reading`), or its documented checks:
   - **leak:** no access outside the pack and no key, truth or repo paths;
   - **coverage:** every one of the 100 crops was actually viewed (view_image or an image attachment, counted per crop id). Report how many crops were viewed and how. **If coverage is below 100/100, the run is VOID:** report that and stop, with no scoring.
2. **Map** the answers back through `docs/records/harvest/recut_v1/w1_masked/cards_kosmo_poly1850_sol_key.json` to the T6g card ids and line ids.
3. **Aggregate:** letters y/n/u, crop_ok y/n, marks y/n/na, and error types.
   - **Ruling:** Sol's letters and crop_ok are final. Its marks are recorded as `pending_opus`.
   - Gate: letters ≥ 90 and crop_ok ≥ 90 on n=100. A pass means kosmopolis poly1850 masked rows are eligible for the wave-1d admission (prep only; marks pending Opus).
4. **Usage** from the launcher JSON and the rollout; no estimates.

## Output
`docs/records/harvest/recut_v1/w1_masked/checks/kosmo_poly1850_sol/`, containing:
- `scan.json`;
- `answers_mapped.jsonl`;
- `results.json`;
- `REPORT.md`: a table, failures listed, the coverage proof and usage.

Leave a guarded commit list. The last line must be exactly:
`SRK2: <done|VOID coverage k/100> | letters y: <n> | crop_ok y: <n> | marks y: <n> (pending opus) | gate: <pass|fail> | tokens: <n>`
