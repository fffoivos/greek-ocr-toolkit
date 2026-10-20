# SS4 — Q3 blind typing packs, reader launcher, scan + answer mapping (no reading)

You are Sol, executing for the small-segment analysis lead. Build isolated blind reader packs for a one-reader Sol typing pass of
the SS3 sample, plus the launcher and the post-run tools. Do NOT start any reading run: the lead launches the readers.

Worktree: `~/Projects/greek-ocr-toolkit-sol-recut` (branch `sol/recut-v1`). `B = docs/records/harvest/collect_v3_admission/segeval1`,
`SS = B/small_segments`. Python for repo tools: `~/Projects/greek-ocr-toolkit/.venv/bin/python`. Network off.

The procedure is the sol-reading HANDOVER (read it fully first):
`~/Projects/greek-ocr-toolkit-sol-reading/docs/harvest/sol_reading/HANDOVER.md` — §2 settings, §4 pack layout and blinding,
§5 leak scan, §7 budget rule. Reuse its tools by import or by in-place invocation; do not fork them:
- launchers `launchers/run_read.sh`, `launchers/run_bed.sh`, `launchers/limit_probe.sh` (copy and change only `S`/`W`/paths, as
  §2 says);
- pack builder/closure checker `tools/build_packs.py`, `tools/scan_packs.py`, `tools/common.py` (reuse functions where they fit
  the new item fields; where they hard-code beds, write a thin wrapper in `SS/tools/` and say what differs);
- the canonical leak scanner `tools/scan_rollout.py` v4.5.5, **invoked in place** after checking sha256 =
  `e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1` (stop if it differs), with the Python §2 names for Pillow.

## Hard constraints
- Repo writes ONLY under `SS/q3/` (keys, manifests copies, answers, ledgers), `SS/tools/`, `SS/tests/`, `SS/launchers/` (new
  files only). Pack writes ONLY under `PACK_ROOT = /private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/348df0f7-fdb5-4e71-a9ef-0c7b4b33457e/scratchpad/ss_packs`.
  No git add/commit, no network, no reading runs, no `codex` calls.
- Keys, line ids, sources, strata, Opus types, notes and the lead's control verdicts never enter PACK_ROOT.

## Inputs
- `SS/q3/sample.jsonl` (SS3), `SS/q3/key_opus.jsonl`, `SS/q3/LEAD_CONTROLS.json` (the lead's pixel-verified controls under `controls`: line_id →
  expected `type`, `accept` = list of types also accepted, `text` = list of accepted text values, `crop` = list of accepted crop
  values, `rotated`; its `rule` field states the scoring), `SS/prompts/type.md` (the reader prompt,
  verbatim; do not edit it).

## Packs
- **Bed** = every SS3 sample row except the control rows. **Controls** = the rows in LEAD_CONTROLS.json.
- Contexts `t01…tNN`: split the bed in seeded random order (seed 20261019) into the fewest contexts with ≤ 90 bed items each, as
  equal as possible; add to each context 8–10 controls (about 10%), drawn so every control is used at least once and none twice
  in one context. Reader `r1` only. Shuffle bed + controls together per context (seeded).
- Folder per context: `PACK_ROOT/type/<ctx>/r1/` with only `cards.jsonl` and `crops/`. `cards.jsonl` rows have exactly the public
  fields `card_id` (`k` + 10 hex, fresh), `crop` (`crops/<sha256-of-bytes>.png`, a byte copy, no links), `google_text` (the
  census `raw_text`, verbatim). `MANIFEST.r1.json` beside the reader folder as §4 says.
- Private key `SS/q3/keys/type.json`: per context the ordered card ids, and per card: line_id, control flag, expected values for
  controls.
- Run the closure checker (or your wrapper) on every pack and write `SS/q3/PACK_SCAN.json`; any violation = fix and rebuild.

## Launcher `SS/launchers/run_type.sh <ctx>`
Copy of `run_bed.sh` adapted: prompt = `SS/prompts/type.md` copied verbatim to `SS/q3/prompts_rendered/<ctx>.md`; limit probe
before (stop with exit 8 if weekly ≥ 78%); `run_read.sh` copy (model gpt-6.1-sol asserted from the rollout, effort medium,
workspace-write limited to the reader folder, no network, web search disabled, stdin = prompt); canonical scan in place →
`SS/q3/answers/<ctx>.scan.json`; copy `answers.jsonl` → `SS/q3/answers/<ctx>.jsonl`; `map_type.py`; probe after; one ledger line in
`SS/q3/usage_ledger.jsonl` (label, rc, wall, model, usage, probes before/after, items). Exit 2 if the scan fails (run void).
Logs to `SS/launchers/logs/`.

## `SS/tools/map_type.py <ctx>`
Validate answers (one line per card, same order, every field present, values from the prompt's lists); map card ids → line ids;
score controls (a control error = `type` not in {type} ∪ accept, or `text` not in the listed text values, or `crop` not
in the listed crop values, or `rotated` differs); flag the context if
more than one control error; write `SS/q3/answers/<ctx>.mapped.jsonl` (line_id, ctx, card_id, control, answer fields) and
`<ctx>.check.json` (counts, control results, flagged). Exit non-zero on invalid answers.

## Tests (`SS/tests/test_ss4_packs.py`)
Pack rows have exactly the three public fields; no line id / source / key string anywhere under PACK_ROOT (grep the whole tree
in the test); content-hash names match bytes; every control used ≥ 1, never twice in one context; ≤ 100 cards per context;
map_type rejects a missing card, a wrong order and an out-of-list value, and scores a control error; scanner sha check refuses a
different file. Run them; record the results.

## Receipt and report
`SS/q3/SS4_RECEIPT.json`: inputs with sha256, contexts with card counts (bed/controls), pack file hashes, closure-scan result,
scanner path + sha, launcher and tool sha256, test results. Final message: contexts and counts, the exact commands the lead runs
(`bash SS/launchers/run_type.sh t01` …), and the expected wall time per context from HANDOVER §6.
Last line exactly: `SS4 READY: <N> contexts, <bed> bed + <c> controls, launcher SS/launchers/run_type.sh, receipt
q3/SS4_RECEIPT.json` (or `SS4 FAILED: <reason>`).
