# LF2b: coordinator's overdraw ruling + fetch and pack the 576 present W1 crops (gpt-6.1-sol, medium; network ON for Clariden READ-ONLY; no .git writes; no reading, no submission)

Continues LF2 (`docs/labelfix/spellcheck/LF2_PROD_PREP.md`, commit 4436fbd05). Add no rule, guard, threshold or heuristic beyond the
ruling below and the delivered LF1 tool.

## A. The overdraw ruling (coordinator, 20 Oct ~05:45, binding tonight) → `artifacts/lf1/tools/prod_finalize.py`

- **In-quota** = rank ≤ quota per (split, class[, subgroup]). **Reserve** = the remaining rows of that (split, class[, subgroup]) in
  rank order. Take quotas and subgroups from the draw's own files (`draw_plan.json` quotas/dev_quotas/subquotas, `bench02_draw.py`
  ~l.418–535; cite lines). If a row's subgroup cannot be derived from the draw files, STOP this part and report which rows.
- A line passes only with verdict `OK`. A flagged in-quota line (any other verdict; unresolved and VOID-twice counted separately) is
  replaced by the next unused reserve line of its own (split, class[, subgroup]) reserve with the **same source**; if that source is
  exhausted, the next unused reserve line of the same (split, class[, subgroup]) of any source, recorded as `FALLBACK_SOURCE` in the
  receipt. If none: `UNFILLED`.
- A reserve line that is not `OK` is marked used and never promoted. Record every replacement with the flag reason (verdict + reasons).
- Keep `lf1.replace_flagged` as is (call it, or wrap it; its tests stay). Output: final benchmark list + receipt per
  split/class[/subgroup]/source: in-quota OK, flagged, REPLACED, FALLBACK_SOURCE, UNFILLED.
- Tests on synthetic fixtures: rank ≤ quota split, rank-order reserve, same-source first, fallback recorded, non-OK reserve never
  promoted, test never replaced by dev, subgroup isolation.

## B. Fetch the 576 present W1 crops and build their packs

1. Cert check (`ssh clariden true`; on any auth error STOP; never refresh). Re-stat; fetch ONLY the W1 rows present now (expect 576) with
   `artifacts/lf1/prod/FETCH.sh` (add a subset/tranche option if needed; one ssh stream) into
   `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad/lf1_prod/crops/`.
   Write the local sha256 manifest. Compare each PNG's sha with the readout `crop_sha256`
   (`~/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/bench02/census05_readout/candidates_readout.jsonl`):
   report matches/mismatches; do not drop, re-cut or substitute any crop.
2. Adapter on the 576 rows (readout = the file above; record its sha). Build packs with the delivered `build_candidates.py`
   (50 bed + 6 frozen controls, seeded). The rest of the draw is built later in a second batch, so the two builds must not collide:
   plumbing only (output roster path and a context-name prefix, e.g. `candidate_w1a_00001`; default behaviour unchanged). Roster
   `artifacts/lf1/candidate_contexts_w1a.json`, packs under the existing pack root `.../lf1_packs/candidates/`.
3. Run the canonical scanner layout check (v4.5.5) on every built pack. List the contexts, cards (bed + controls) and bytes.

Do NOT start readers or `RUN_ALL.sh`. Update `artifacts/lf1/prod/PROD_PLAN.md` (second-batch commands; the finalize step on the merged
verdicts of both batches). Tests: all existing pass plus the new ones. Report `docs/labelfix/spellcheck/LF2B_REPORT.md` with
LEAD_COMMIT_PATHS (nothing large in git: crops and packs stay in the scratchpad, hashed in receipts) and the Codex weekly reading.
Final line: `LF2b READY: tests N passed; ruling implemented; W1 fetched f/576 (sha match m); packs c contexts (cards d+e)` or
`LF2b STOPPED: <reason>`.
