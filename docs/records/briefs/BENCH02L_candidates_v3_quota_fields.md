# BENCH02L: candidates v3, adding in_quota and overdraw_order per row (gpt-6.1-sol, medium, network OFF, no spend)

The BENCH02K candidates (`bench02/census05/candidates.jsonl`, 3,341 lines, sha `70a29c202691584a3382e77505ef56db7b9a0d1347fa5ac2eccc95ac8e9acfe5`, commit 9dcd27103) are the readout input on Clariden.
- **Do not change that file or re-run the draw.**
- The coordinator has ruled how the overdraw is used: **rank ≤ quota per split/class[/subgroup] is in quota; the reserve is used in rank order; a replacement must share split, class and source.**
- The spell-check lead applies this tonight. Emit the fields so nobody re-derives them.

## Do
1. Write a small deterministic derivation script, `bench02/derive_candidates_v3.py`, using stdlib only. It reads `census05/candidates.jsonl` and the quotas/subgroup quotas exactly as recorded in `census05/counts.json`/`draw_plan.json` (do not re-type them). It writes `census05/candidates_v3.jsonl`:
   - **the same rows in the same order**, with every existing field byte-for-byte unchanged in value;
   - `quota_scope`: `"<split>:<class>"`, or `"<split>:<class>:<subgroup>"` where the draw has subgroup quotas (e.g. modern_cyrillic by language; check `draw_plan.json` for any other class with subgroup quotas, e.g. fonts small/large);
   - `scope_rank`: the row's rank within that scope. If subgroups exist, derive it from the draw's recorded rank order restricted to the subgroup; say exactly how in the output receipt;
   - `in_quota`: `scope_rank ≤ scope quota`;
   - `overdraw_order`: null if in quota; otherwise 1, 2, … in rank order among that scope's reserve rows.
2. Invariants. Assert them in the script and report them:
   - per split × class, the in-quota count equals `credited` in counts.json;
   - the reserve count equals `drawn − credited`, or explain any difference caused by subgroup quotas;
   - no duplicate keys;
   - the row order and set equal candidates.jsonl;
   - deterministic: a second run is byte-identical.
3. Tests: one test per invariant on a small synthetic file, including one subgroup case. Re-run the existing bench02 suite (49 tests) to confirm nothing else changed.
4. Write `census05/CANDIDATES_V3.md`:
   - the sha, bytes and line count of candidates_v3.jsonl;
   - the input sha (70a29c20…);
   - a per-scope table: quota, in-quota, reserve;
   - the exact derivation rules.

   Numbers only. Do not stage anything to Clariden.

Guarded commit list: the script, the test, `census05/candidates_v3.jsonl` (≤ 5 MB, otherwise out of git with its sha), `CANDIDATES_V3.md`, and this brief. Do not run `git add` or `git commit`.

The last line must be exactly:
`BENCH02L: done | candidates_v3 <lines> sha <sha8> | in_quota test <a> dev <b> = credited | reserve test <c> dev <d> | scopes <n> (subgroup <m>) | deterministic yes | tests <k> passed`

## Execution receipt (2026-10-20)

- Script: `docs/harvest/collect_v3_admission/bench02/derive_candidates_v3.py` (stdlib only).
- Tests: `docs/harvest/collect_v3_admission/bench02/test_candidates_v3.py` (8 tests).
- Output: `docs/harvest/collect_v3_admission/bench02/census05/candidates_v3.jsonl`.
- Receipt: `docs/harvest/collect_v3_admission/bench02/census05/CANDIDATES_V3.md`.
- Output: 3,341 lines; 4,102,669 bytes; SHA-256 `0432c56f75ed1efded00b76e7aeabcc0a2bf9441bfad00e825e4e105006134c2`.
- Input SHA-256 remains `70a29c202691584a3382e77505ef56db7b9a0d1347fa5ac2eccc95ac8e9acfe5`.
- Scopes: 40, including 12 subgroup scopes and all empty scopes.
- In quota: test 2,340; dev 453. Reserve: test 468; dev 80.
- Recorded credited: test 2,348; dev 455.
- Exact exception: test:modern_cyrillic has 48 drawn/credited but Serbian quota 40, so 40 in quota and 8 reserve. dev:modern_cyrillic has 12 drawn/credited but Serbian quota 10, so 10 in quota and 2 reserve. Other Cyrillic language scopes are empty. All other split/class counts equal credited.
- The requested unqualified `in_quota = credited` invariant and final status text conflict with the subgroup rule and preserved counts. The script asserts exact subgroup reconciliation instead: in_quota = credited - subgroup_gap; reserve = drawn - credited + subgroup_gap. No quota or input accounting was changed.
- Determinism: two complete file-producing runs byte-identical for JSONL and Markdown; independent derivations also checked within every run.
- Full suite: `python3 -B -m unittest discover -s docs/harvest/collect_v3_admission/bench02 -v`: 57 passed (49 existing + 8 new), 0 skipped, 0 failures. Final receipt-only change followed by 8/8 new tests passing.
- No network, spend, production redraw, Clariden staging, git add or git commit.

Guarded commit list (5 files; not staged):

1. `docs/harvest/collect_v3_admission/bench02/derive_candidates_v3.py`
2. `docs/harvest/collect_v3_admission/bench02/test_candidates_v3.py`
3. `docs/harvest/collect_v3_admission/bench02/census05/candidates_v3.jsonl`
4. `docs/harvest/collect_v3_admission/bench02/census05/CANDIDATES_V3.md`
5. `docs/briefs/BENCH02L_candidates_v3_quota_fields.md`
