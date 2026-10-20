# Overnight run 19→20 Oct 2026 — owner summary (coordinator; written 2026-10-20 08:40 Athens, updated at the end of the run)

## Done tonight
- Repo clean-up merged into cleanup/20261019 (main fast-forwarded locally, NOT pushed).
- Content gate 0.3 + segmentation 0.9-s5 + pipeline 0.3.2; census_05 full run: 592,466 rows → ADMIT 457,991 / DROP 56,435 / HOLD 78,040; admitted_train 364,871; leaks 0; Astra: census integrity PASS.
- Release v3 (train export): 168,637 W1+W2 rows, labels = raw Google import (0 edits land), Astra CP3: PASS.
- Benchmark 0.2 SEALED (seal04): test 2,253 / dev 437 rows, 16 classes, drawn from split2 test/dev editions only (zero subtraction from training), last-filtered by Sol (350 flagged = 248 replaced + 102 unfilled); diacritics NOT qualified by the last filter. Coverage: test 16/16 classes non-empty but 2/16 at full quota; dev 14/16 non-empty, 6/16 full; modern Cyrillic = Serbian only.
- Scaling data (SCALE1): ref_208k, ref_364871 (actual max; < the planned 420k), tgt_208k (supply-limited: 11/16 classes exhausted) — all exposure audits 0.
- (Pruned 11:50 on your instruction: the wave-3 part-2 novelty data work I had started — M-family manifests, P1 pool, C2 column, G audit — is stopped and shelved; not part of the mandate.)
- Wave 2 (H7 recipe retest): package built, inventory OK on the 3rd attempt (row-key bug, then a hand-written deploy receipt), benchmark bound with 0 exposure; the first smoke FAILED on a missing linefactory binary (only the inventory job built it). One more smoke is authorised with a subprocess-target check; if it fails again, wave 2 waits for you. Production = ctrl + add × 3 seeds (≈15 GPU-h) after Astra 3b PASS. NOT launched as of 09:30.

## Decisions I took under the mandate (you may override)
1. "degraded" benchmark class = relative (bottom 5% confidence within source) — admission removes every low-confidence line.
2. Benchmark draw: forced editions' non-locked rows drawable; cap 50 per class×edition; deficits reported, never substituted.
3. vertical_turned class: orientation alone is not a crop violation (re-read with the class stated).
4. Replacements: same scope + source only, else UNFILLED; deterministic pairing.
5. Wave 2: the two never-built locked strata (200 mark-enriched, 400 Wikisource) dropped; add_corr arm DROPPED — corrections reach only 167 of 364,864 training rows (RU1 mostly on census HOLD rows; N1: 478 on forced test editions, 151 train rows all census HOLD).
6. Scaling data: option B (natural-frequency reference over release v3 ∪ v_c; targeted only at 208k).
7. M-family rulings Q7–Q10 (see NIGHT_STATE.json decisions).

## Sequence note (honest)
- The overnight census/release were run WITHOUT the polytonic corrections (I kept sf7 as unaudited against your ruling), so release v3 was filtered but barely corrected. Being redone as census 06 / release v4; wave 2 launches on v4 with all three arms. Four failed job attempts on the wave-2 package (two inventory, two smoke; each a defect untested on real data) cost about four hours; the wave-2 lead session was lost when the Mac disk filled and I now drive its passes.

## Owner ruling 10:47
- sf7 (polytonic tool) IS released. Census 06 re-runs with polytonic in scope, release v4 applies the edits, wave 2 launches on v4 with add_corr restored. In progress.

## Timeline (as of 11:45)
- 14:32: sf7 jobs RUNNING (5 parents; longest limit 2:53) → census 06 bind + smoke + full (≈4–6 h) → release v4 → wave-2 inventory/smoke/Astra 3b → launch; realistic wave-2 launch: night of 20→21 Oct. S1 (scaling): package qualified on Clariden (3rd attempt); ×2 cells need resumable 12-h segments and one targeted cell is dropped to fit the 150 GPU-h cap (amendment A1); smoke + Astra 4b next; launches after wave 2.

## Only gate left for you
- main push (I never push).

## Where things are
- State: docs/programme_20261019/NIGHT_STATE.json; ledger: memory post_e3_plans_state.md; reviews: docs/records/reviews/astra_program_review_2026-10-06/ (CENSUS05R, CP3; CP3B/CP4/CP4B briefs ready).
- Clariden $W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3: census_05_20261020, release_v3, benchmark_0.2/seal04, scaling_w3, e4_wave2_rel3_20261020.
