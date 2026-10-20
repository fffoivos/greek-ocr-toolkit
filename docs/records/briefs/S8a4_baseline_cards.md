# S8a4 — Complete S8a with the fetched DEV evidence: frozen baseline + DEV print-truth cards (gpt-6.1-sol, xhigh, network OFF)

Workspace/rules: as `docs/records/briefs/S8a_dev_evidence_cards.md` and `S8a2_dev_evidence_resume.md` (read both; they still bind). Head = this commit.
Network OFF (all remote evidence is now local).

## New input
Debug job 3680506 (S8a3) COMPLETED 0:0 in 5 min 12 s. `docs/records/labelfix/spellcheck/S8_DEV/evidence/remote.json.gz` (sha256
fae3140ea1e789ca817d3eec3ec71ae5d47774cf43503b9fa0b25aa54d64e4a2) with receipt `evidence/S8a3/remote_receipt.json` (complete true; runtime
600/600; alignments 166 fetched + 434 local = 600; BE 974 shards; inference_runs 0). Verify the sha and completeness against `request.json`
semantics, then supersede `evidence/extraction_stop.json` with a note citing this receipt (keep the old marker as `…_superseded_S8a3.json`).

## Do
Run `scripts/labelfix/s8_prepare.py` (default, original crops): frozen S6/SF4 baseline on all 600, local AB/PRESENCE recomposition (parity on
the 14 audit lines vs L1M's saved decisions), card census, control review (inspect every planted control yourself before planting), and the
DEV cards. If DEV cards exceed 2,000, STOP before rendering and propose the seeded, wave-stratified subsample (as S8a's rule 4). Masked crops
(`~/Projects/collect-v3-data/v2_masked/s8_dev/`) are still being produced: leave `--masked` pending. Note for the card sources: the frozen-gate
AB form is one candidate source; SF5 (running separately on the main worktree) will change elision handling — mark every DEV card whose only
difference is elision/alias so it can be scored under either policy.

## Deliverables
Update `docs/records/labelfix/spellcheck/S8a_REPORT.md`; last line:
`S8a READY: DEV 600 (masked pending); baseline loc_unknown <a>% seg_uncertain <b>% (per wave …); cards DEV <c> (+controls <k>), audit 48 lines 114 cards (+10); masked rerun <cmd>`.
