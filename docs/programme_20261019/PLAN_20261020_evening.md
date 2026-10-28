# Plan 20 Oct 2026 evening → 21 Oct (pruned scope: corrections+filtering → wave 2 → S1)

Method: every stage is one Sol pass that executes end to end (polls jobs, runs the next steps, writes state + ledger, ends with one line); the coordinator only submits sbatch lines Sol hands back and takes decisions; Astra reviews before every launch.

| # | Stage | Executor | Input | Output / exit line | Checkpoint |
|---|---|---|---|---|---|
| A1 | sf7 train job 3708830 → output check → sf7-bindings.json (5 parents) | Sol RUNNER1 | job 3708830 | `SUBMIT: bind_sf7` | — |
| A2 | bind_sf7 job → CENSUS06-C2 requalification (readback, verifier ×4, test-only ×8, head test) | Sol RUNNER1 | bind job id | `SUBMIT: census_06 smoke` | — |
| A3 | census_06 smoke → CENSUS TIMING → full (limit = projection ×1.5) → readout 0.3.3 → flip report | Sol RUNNER1 | smoke/full ids | `SUBMIT: full` then `SUBMIT: CROPS4C smoke` | — |
| A4 | CROPS4C smoke → full → REL4b run → v4 handoff (paths + shas) | Sol RUNNER1 | job ids | `DONE: V4_HANDOFF.md` | **Astra CP3v4**: release v4 + census_06 results (re-run of checkpoint 3 on the corrected data; brief ASTRA_CP3_release_benchmark_brief.md updated) |
| B1 | wave-2 v4 package: inputs builder (v4 + census_06 + registry with sf7 by sha) → R4D env port (S1-N environment) → helper deploy → VERIFY → load proof → inventory04 | Sol RUNNER2 | V4_HANDOFF.md, R4C/R4D | `SUBMIT: inventory04` | — |
| B2 | seal04 bind → GPU runtime probe → v4 smoke (3 arms) → REVIEW_INPUTS | Sol RUNNER2 | inventory04 | `SUBMIT: probe`, `SUBMIT: smoke`, then `READY FOR ASTRA 3b` | **Astra CP3B**: deployment-ready wave-2 package (brief ASTRA_CP3B_wave2_package_brief.md) — fix-until-clean, Sol applies fixes, re-review scoped |
| B3 | production: preflight → job01 + job02 + job03 → aggregate (9 runs, ctrl/add/add_corr × 3) → registry rows → H7 verdict | Sol RUNNER2 | CP3B PASS | `SUBMIT: production chain`; `DONE: wave-2 results` | **Astra CP4**: wave-2 results (brief ASTRA_CP4_wave2_results_brief.md) |
| C1 | S1 package: S1-N environment (wave-1c parity) → deploy job → GPU probe → smoke (8 cells + split witness + seal04 panels) → REVIEW_INPUTS | Sol RUNNER3 | S1-N | `SUBMIT: deploy job`, `SUBMIT: probe`, `SUBMIT: smoke`, then `READY FOR ASTRA 4b` | **Astra CP4B**: deployment-ready S1 package (brief ASTRA_CP4B_scaling_package_brief.md) |
| C2 | S1 production: series A (×1, ×1.5; 6 cells) → series B (×2 as 12-h segments; 2 cells) → aggregate → registry → verdicts | Sol RUNNER3 | CP4 PASS + CP4B PASS | `SUBMIT: series A`, `SUBMIT: series B`; `DONE: S1 results` | **Astra CP5**: S1 results |

Decision rules already fixed: caps 150 GPU-h/wave, 120/series on requested-GPU accounting; add_corr = add + sf7/RU1/N1 overlays; S1-A1 amendment (w2_tgt_208k dropped); no launch before the Astra PASS of its checkpoint; third failed cycle on one object = stop and decide (coordinator).
Coordinator actions only: run each `SUBMIT:` line, launch each Astra review from a pristine detached worktree, take decisions, keep the owner informed in one line per milestone.
