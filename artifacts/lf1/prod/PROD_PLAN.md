# LF3 production plan — lead commands, not executed by LF3

Coordinator ruling, 20 October ~06:20: only `candidate_w2_00004` and `candidate_w2_00013` have authorization for one further fresh read (attempt 3). Default fleet behavior remains at most two attempts. Attempt 3 records `authorised_by: "coordinator 20 Oct (VOID is a reader-process failure)"`; attempts 1–2 and any existing attempt 3 remain in the ledger. A third VOID has no verdict, with receipt text `no verdict (reader VOID x3)`; other twice-VOID contexts retain `no verdict (reader VOID x2)`.

`vertical_turned` is printed vertically by design. Its re-read decides; first-read and re-read records both remain. No re-read verdict permits no OK promotion. The vertical packs copy exact sealed first-pack PNG bytes and labels, use new seeded opaque IDs, and contain at most 50 bed cards plus the frozen five controls. Only `lf1-control-turned` is omitted: its turned-horizontal expectation is undefined under the vertical statement. Control scoring is unchanged. Per-context `prompt` and `prompt_sha256` bind `lf1_vertical.md`; other contexts retain the original prompt.

W1a + W2 contain **102 vertical bed cards** (W1a 0, W2 102), including seven in `candidate_w2_00004` and three in `candidate_w2_00013`. LF3 built `candidate_contexts_vert_w1a_w2.json`: three contexts with 50+5, 50+5 and 2+5 cards. No reader or meter probe ran during LF3. The commands below start readers only when the lead executes them. Existing budget checks, scanner, model `gpt-6.1-sol`, medium effort, network-OFF flags, literal paths and pack write restrictions remain.

All commands run from the spellcheck worktree. No command writes `.git` or submits a seal.

## 1. Authorized attempt 3

```bash
bash artifacts/lf1/RUN_ALL.sh --jobs 2 \
  --contexts artifacts/lf1/candidate_contexts_w2.json \
  --extra-attempt candidate_w2_00004 candidate_w2_00013
```

Only the named contexts are selected by `--extra-attempt`; a VALID or REFUSED terminal attempt does not trigger another read. Fresh attempt 3 uses a new `_retry3` directory populated from the original sealed manifest, with no prior answers or zooms.

## 2. Vertical build + run for W1a + W2

LF3 already built this roster. The conditional allows the same exact command sequence in a checkout where the packs have not yet been built; it does not rebuild existing packs.

```bash
PY=/Library/Frameworks/Python.framework/Versions/3.11/bin/python3
if [ ! -f artifacts/lf1/candidate_contexts_vert_w1a_w2.json ]; then
  /usr/bin/arch -x86_64 "$PY" -B artifacts/lf1/tools/build_vertical.py \
    --rosters artifacts/lf1/candidate_contexts_w1a.json artifacts/lf1/candidate_contexts_w2.json \
    --batch w1a_w2
fi
bash artifacts/lf1/RUN_ALL.sh --jobs 3 \
  --contexts artifacts/lf1/candidate_contexts_vert_w1a_w2.json
```

The vertical fleet writes `artifacts/lf1/prod/vertical_reread_verdicts.jsonl` separately, pairing each line's full `first_verdict` and `reread_verdict` records. Later vertical batches update their own line IDs and preserve earlier batches. The primary fleet verdict file is not overwritten by vertical runs.

## 3. W1b, after its first read

Once the lead has supplied and read `candidate_contexts_w1b.json`, use its sealed packs directly:

```bash
PY=/Library/Frameworks/Python.framework/Versions/3.11/bin/python3
/usr/bin/arch -x86_64 "$PY" -B artifacts/lf1/tools/build_vertical.py \
  --rosters artifacts/lf1/candidate_contexts_w1b.json --batch w1b
bash artifacts/lf1/RUN_ALL.sh --jobs 24 \
  --contexts artifacts/lf1/candidate_contexts_vert_w1b.json
```

The builder selects only `draw_class == vertical_turned`, including cards whose first context was VOID. An empty vertical roster requires no reader work. W1b count remains unknown until that roster exists.

## 4. Map, finalize and the three seal files

After W1a, W2, W1b and both vertical rosters have terminal receipts, reconstruct the merged line verdicts from all historical attempts. This also reconstructs the separate paired vertical file; original receipts and first verdicts remain intact.

```bash
PY=/Library/Frameworks/Python.framework/Versions/3.11/bin/python3
DRAW="$HOME/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/bench02/census05/candidates_v3.jsonl"
/usr/bin/arch -x86_64 "$PY" -B - <<'PY'
import json,sys
sys.path.insert(0,'artifacts/lf1/tools')
from lf1 import BASE,dump
contexts=[]
for batch in ('w1a','w2','w1b'):
    contexts.extend(json.loads((BASE/f'candidate_contexts_{batch}.json').read_text()))
dump(BASE/'candidate_contexts_merged.json',contexts)
PY
/usr/bin/arch -x86_64 "$PY" -B artifacts/lf1/tools/prod_map.py \
  --contexts artifacts/lf1/candidate_contexts_merged.json \
  --vertical-contexts artifacts/lf1/candidate_contexts_vert_w1a_w2.json artifacts/lf1/candidate_contexts_vert_w1b.json \
  --vertical-output artifacts/lf1/prod/vertical_reread_verdicts.jsonl \
  --output artifacts/lf1/prod/line_verdicts_merged.jsonl
/usr/bin/arch -x86_64 "$PY" -B artifacts/lf1/tools/prod_finalize.py \
  --candidates "$DRAW" \
  --verdicts artifacts/lf1/prod/line_verdicts_merged.jsonl \
  --vertical-verdicts artifacts/lf1/prod/vertical_reread_verdicts.jsonl \
  --output artifacts/lf1/prod/final_list.jsonl \
  --receipt artifacts/lf1/prod/finalize.receipt.json \
  --details artifacts/lf1/prod/finalize.details.json \
  --bindings artifacts/lf1/prod/finalize.bindings.json
shasum -a 256 artifacts/lf1/prod/final_list.jsonl \
  artifacts/lf1/prod/finalize.receipt.json \
  artifacts/lf1/prod/line_verdicts_merged.jsonl
```

The three seal inputs are `final_list.jsonl`, `finalize.receipt.json`, and `line_verdicts_merged.jsonl`. `finalize.bindings.json` binds their absolute paths and SHA-256 values. `finalize.details.json` holds reasons, VOID text/counters and both vertical records; the separate paired vertical file remains available. Nothing here submits or runs the sourcing suite.

Only literal OK passes. Replacement uses the next unused OK reserve by explicit `overdraw_order` within the same exact `quota_scope` AND source, otherwise UNFILLED. `in_quota` alone defines membership. No first-read OK can substitute for a missing vertical re-read. VOID x2/x3 retain null verdicts and separate states/counters; `verdict_flags` and `no_verdict` distinguish them in the side receipt. The seal schema's historical `flagged` count remains total replaced/unfilled slots, so `flagged == REPLACED + UNFILLED` still holds.

Production draw SHA-256: `0432c56f75ed1efded00b76e7aeabcc0a2bf9441bfad00e825e4e105006134c2`. Seal02 schema SHA-256: `ec430f1460fa9d35ccc581ee9408efdf6be03a69e73d14765563520d7ebf972f`. LF2d's schema and three-file handoff remain unchanged. Its documented sourcing discrepancy also remains: sourcing's checker uses `scope_rank` for reserve order, whereas this authorized implementation uses `overdraw_order`. See `docs/labelfix/spellcheck/LF2D_REPORT.md`. No sourcing files were changed.
