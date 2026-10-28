# Separable aspects of the programme — 21 Oct 2026, 10:05 Athens

Owner standard: reasonable, not perfect. Method: I decide, Sol executes, Astra reviews. No other session in the loop.

## A. Census → release v4 (row filtering + correction)
Purpose: clean the 592,466 harvested line rows with the correction tools and admission checks; write release v4 (training set for B).
Current state: bound package 31316332c860d411 (sol-recut 33d28dfc); full census job 3711087 running since 06:50 (Lustre stalls; ~200k rows decided at 10:00; ~0.3% INFRA_ERROR); afterwards: retry of INFRA_ERROR rows (external driver, same ledger), readout, flip_report, CROPS4C, REL4b, handoff receipt.
Machinery around it today: sealed package with code fingerprints, identity bindings per tool file, binder job, regeneration audit, amended verifier ×4 from a clean worktree, scheduler test-only ×8, binding_state guard, head test, smoke chain of 4 jobs, detached chains, data-root custody receipts, clean detached worktrees per commit, cross-session acceptance lists.

## B. Wave-2 recipe retest on v4
Purpose: ctrl / add / add_corr × 3 seeds on release v4 (9 runs; 28.3 GPU-h requested).
Current state: package greek-page-ocr-e4w2v4 at de6ab5b (R4A inputs builder, R4B script_class fix, R4C runtime prologue); still needs the wave-1c environment port (S1-N style) and v4. Planned chain: inputs builder → deploy → VERIFY → load proof → inventory04 → seal04 bind → probe → smoke → REVIEW_INPUTS → Astra CP3B → production → Astra CP4.

## C. Scaling ladder S1
Purpose: 8 cells (widths ×1/×1.5/×2 × ref_208k/ref_364871; ×2 as resumable 12 h segments; 129.6 GPU-h requested).
Current state: package e823b5a8439cc875 (greek-page-ocr-s1, commits through c9ae2f7); Astra CP4B review 1 FAIL fixed in code (epoch-boundary RNG, accounting, qualification job, parity); 12 fix rounds on deploy/qualification (missing receipt, witness timeout, socket path, module shadowing, /iopsstor stalls, capstor move, inventory extras, reused binary). Planned chain: deploy → timing qualification → native witness → probe → smoke → REVIEW_INPUTS → Astra CP4B review 2 → production after B's CP4.

## D. Cross-cutting
Clariden environment (wave-1c env works; uenv torch segfaults), benchmark 0.2 seal04 (fixed), caps (wave 150 / series 120 requested GPU-h), Astra review before each production launch, no benchmark exposure in any training set, sha-verified deploys, one smoke before production.
