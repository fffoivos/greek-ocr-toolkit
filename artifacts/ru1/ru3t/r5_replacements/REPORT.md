# RU3T-R5 preparation receipt

ctx08/r3: 1 × absolute path outside reader_dir; 7 × image provenance: unmatched image provenance; 19 × unresolvable load expression.
ctx12/r3: 2 wrong signs / 19 scored controls; 0 abstentions.
ctx13/r3: 2 wrong signs / 19 scored controls; 0 abstentions.
ctx15/r3: 2 wrong signs / 17 scored controls; 0 abstentions.
ctx18/r3: 17 × unresolvable load expression.

The 5 requested VOID contexts contain 488 missing logical read slots; F2 has 498 total. The other 10 coverage-missing slots are explicitly retained and are not covered by this replacement round.

The recurring dynamic pwd-result store is not covered by the pinned canonical v4.4 rules. The canonical source and local copy have the same required hash. Examples and resolver evidence are in scanner_pattern_review.json; no scanner modification or waiver was made.

ctx08/r3: /Users/foivoskarounos-zamparloukos/.codex/sessions/2026/10/18/rollout-2026-10-18T01-13-13-01a14bed-2004-7083-bc4c-e43a6e202703.jsonl
- record 40 (zero based): `store("base",(await tools.exec_command({cmd:"pwd","max_output_tokens":100})).output.trim());`
- record 46 (zero based): `${load("base")}/zoom/${String(i).padStart(3,"0")}.png`
ctx18/r3: /Users/foivoskarounos-zamparloukos/.codex/sessions/2026/10/18/rollout-2026-10-18T01-27-19-01a14bfa-066a-77f2-ab75-bf3a6eb500fd.jsonl
- record 42 (zero based): `store("base",(await tools.exec_command({cmd:"pwd",max_output_tokens:100})).output.trim());`
- record 55 (zero based): `${load("base")}/zoom/${String(i).padStart(3,"0")}.png`

Five packs: 429 candidate items + 45 fresh control items = 474 items; planning estimate 0.948 weekly percentage points, excluding probes.

Each context has nine controls whose adjudication IDs differ from all its earlier readers. Original item contents and private candidate assignments are preserved; crop bytes are copied, not transformed. Fresh orders and opaque IDs passed closure. The finalizer routes five roles to r5, keeps the other seven r3/r4 replacements, and retains fail-closed gates without fallback.

Residual missing read slots by context: {'ctx10/r1': 3, 'ctx06/r1': 2, 'ctx17/r1': 4, 'ctx05/r2': 1}.

Driver and finalizer dry runs passed. Seven synthetic driver/routing tests passed, including no launch/probe in dry run, exact 70% stop, persistent stop, bad-probe refusal, and no repeat attempts. Original and r3 bound bytes were verified unchanged. No new reading, network, browser, computer use, .git write, training label, or registry write occurred.
