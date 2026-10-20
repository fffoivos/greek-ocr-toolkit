# L1M2 — Border-blob ownership and the padding number for the 260 L1M lines (gpt-6.1-sol, xhigh, network OFF)

Workspace: `~/Projects/greek-ocr-toolkit-spellcheck-l1` (branch `opus/spellcheck-l1`). No `.git` writes; no other worktree writes. Mac CPU,
260 lines, local evidence only; no detector/reader/gate code changes (gate frozen at sf4 semantics for this analysis; SF5 does not touch
clipping). Local Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`.

## Inputs
- L1M evidence: `docs/records/labelfix/spellcheck/L1M_evidence/{200,vouli}/` — `border_flags.jsonl.gz`, `border_blobs.jsonl.gz` (native pixel
  coordinates per blob, flag→blob joins), per-line/slot/details records; `L1M_REPORT.md` for definitions.
- Ownership maps (sourcing lead): `~/Projects/collect-v3-data/v2_masked/l1e_sample_r4/` (200) and `…/l1e_sample_vouli_r2/` (60):
  `ownership/<wave>/<doc>/<crop-stem>.png` 8-bit labels aligned to the crop — 0 background, 1 own ink kept, 2 masked/owner row above,
  3 masked/owner row below, 4 masked/no detector row, 5 Voronoi-foreign but left unmasked (ring abstention); `lines.jsonl` per-component rows;
  `comparison.json` (masked crops byte-identical to r3/vouli). Verify the crop alignment (dimensions + the r3 crop hashes) before use.

## Do
1. **Attribute every border blob** (original crop, every clipped_top/clipped_bottom flag's blob): classify its pixels by the ownership map;
   blob class = majority class with the split recorded (own / neighbour-above / neighbour-below / unowned / ring-abstained / mixed if no class
   ≥ 80%). Report flag counts before → after masking by attribution, per wave and edge (top/bottom). Expect cleared flags to be neighbour /
   unowned and persistent ones to be own or ring-abstained — test it, report exceptions with ids.
2. **Padding number (owner decision input):** lines where this line's OWN ink (class 1) of a letter body or its mark touches the crop top or
   bottom inside an SF4-relevant clipping window, after masking (the persistent own-ink clipping; panels 8/10/12 pattern). Report: lines with
   any such flag; lines for which own-ink clipping is the ONLY remaining AB hold after masking (these are what a larger cut padding would
   rescue beyond masking); per wave; and how many pixels of padding would have been needed (distance to the crop edge is 0 by definition —
   instead report the vertical extent of the touching component beyond the meanline/baseline band, in x-height units, as the padding estimate).
3. Ring-abstention (class 5) at the border: count flags whose blob is class 5 (masking abstained) — these are fixable by masking policy, not by
   padding; report separately.
4. 12 panels (4 neighbour-cleared, 4 own-persistent, 4 ring-abstained/mixed), each with the ownership classes tinted; inspect them yourself.

## Deliverables
Append a section to `docs/records/labelfix/spellcheck/L1M_REPORT.md` (do not regenerate the report; append) + evidence under
`docs/records/labelfix/spellcheck/L1M_evidence/ownership/`. Last line of the appended section:
`L1M2 RESULT: border blobs <n>: neighbour <a>% / unowned <b>% / own <c>% / ring-abstained <d>% / mixed <e>%; own-ink clipping lines <p>/260, sole remaining AB hold <q>/260 (per wave …); padding estimate median <x> x-height`.
