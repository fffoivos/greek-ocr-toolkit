# CQ4: build the Sol packs for (1) the fresh capitals witnesses W-CAP and (2) the capitals repair top-up (gpt-6.1-sol, medium, network OFF; no .git writes). BUILD ONLY; no reading.

**CQ4c correction (17 Oct, authoritative):** BUILD ONLY. The owner has given GO for R2a-2 once these inputs exist; this brief builds its reading inputs and scripts, with no reading, training or manifest build. CQ4b amendment 1 and `CQ4c_build_fix.md` supersede the original inventory rules.
- Preregistration: `~/Projects/greek-ocr-toolkit-spellcheck-r2prep/docs/labelfix/spellcheck/R2/R2A2_PREREGISTRATION.md`, sha256
  dbac559fe9792a4f7c879f1fc7b08d03c6a82611bbb42ecce1ffd4ae31ccbebc. Record it in the receipt.
- Protocol: the CQ1 pack exactly (artifacts/cq1/tools, prompt VERBATIM, HANDOVER §4 blinding, canonical scanner v4.4 (sha256 dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547), ≤100 items per context, about
  10% controls).
- Cost rule: HANDOVER §7. Probe before and after each context; refuse at ≥78% weekly.

## 1. Document inventory (report it before building; STOP if a set cannot reach 70% of its target)

**W-CAP:** the 17 validation-role documents plus the 3 previously unused documents, under preregistration amendment 1. Calibration remains excluded. Locate slots from the SHA-verified saved B-stage recogniser alignments and role-separated teacher exports of job 3681404 at `~/Projects/greek-ocr-toolkit-spellcheck-r2prep/artifacts/labelfix_r2/output_3681404/`, joined to the R2P2 population and native crops. Use `validation_reserve` exports for validation documents. Include the three unused documents only when their alignments exist; otherwise drop them and report why.

**Top-up document exclusions** (write the union and reasons to `artifacts/cq4/excluded_docs.json`):
- every W-CAP and T4 document;
- validation and calibration role documents;
- the old pool's held-out 16 documents;
- DEV (S8), LQB print-truth, 39-card, audit100, substitution-sample, and CQ1 documents.

**Top-up training documents:** supervision-role / T2 documents and the old pool's 316 documents are allowed, subject to those exclusions. Exclude the individual slots already represented on T2 cards and every R2a v2 manifest slot. W-CAP and top-up documents stay disjoint.

**Old identity rule (R2J4):** replace a unique existing R1 target in place; never append an existing identity. Preserve unrelated old rows, including duplicates. A top-up overlay hitting a duplicated old key must STOP with `ambiguous old identity for replacement`.

## 2. Selection (deterministic, seed 20261017; a slot = a capital Greek vowel or Ρ located by the recogniser + case classifier, as in R2C)

**W-CAP:** 150 slots with a likely mark (the Google label or the recogniser shows a breathing or accent on the capital) and 150 likely
bare (none shown). The likely class is a sampling stratum only; truth comes from the read.
- At most 10% per document and at most 5 per page.
- Mix ALL-CAPS words, sentence-initial capitals and numeral-adjacent capitals among the bare ones.

**Top-up:** enough slots to bring the capitals repair slice from its current 214 negative / 127 positive (R2a v2 manifest) to 800 / 500.
- Oversample by 25%, because some will be unreadable or quarantined: about 735 likely-bare and 470 likely-marked.
- The same caps.
- Exclude every slot already in the R2a v2 manifest.

## 3. Packs

- W-CAP: `PACK_ROOT=…/scratchpad/solcap_wcap/`. Top-up: `…/scratchpad/solcap_topup/`.
- Contexts of ≤90 bed items + 10 controls, in seeded order, rendered like CQ1 (word zoom 3× with the capital boxed, plus the native line
  strip). There is NO Google text.
- **Controls:** lowercase vowels with clear marks from T2 resolved (never capitals). Build a pool of 40 and write ONE contact sheet
  `artifacts/cq4/control_review/controls.png` plus a `lead_review.json` (pending), so the lead pixel-verifies them once. Each context
  draws 10 from the verified pool.
- Keys stay outside the packs (`artifacts/cq4/keys/`). Closure scan on every context.

## 4. Run scripts and the re-read rule

- **`artifacts/cq4/RUN_ALL.sh`:** runs the contexts sequentially. Per context: limit probe, read, leak scan v4.4, controls gate (≤1
  error), probe. A failed context is VOID: it is recorded and never scored. Then it continues to the next. It refuses at ≥78% weekly.
- **`artifacts/cq4/BUILD_REREAD.sh`:** after RUN_ALL, it builds the re-read contexts from every answer that gives a breathing with no
  accent on a capital whose ink has a spacing or preposed mark (or every breathing-only answer, if ink isn't available), plus every
  "unreadable".
  - These go into fresh contexts, with fresh order and the same prompt, plus 10 controls.
  - **Resolution:** if the re-read agrees, keep it. If it disagrees, the slot goes to the LEAD pixel queue
    (`artifacts/cq4/lead_queue.jsonl` + a contact sheet). It is not auto-resolved.
- **`artifacts/cq4/AGGREGATE.sh`:** writes the tier-C truth per slot (`truth_tier: "C_sol_one_reader_reread"`), with W-CAP and top-up
  kept separate. Unresolved slots are quarantined.
  - It reports the counts per set and class, the re-read agreement rate, the lead-queue size, and the Codex % before and after.
  - Write `docs/records/labelfix/spellcheck/R2/CQ4_REPORT.md`.

Tests: selection determinism, disjointness (W-CAP vs top-up vs excluded docs), closure, and the re-read trigger on fixtures.

Last line: `CQ4 BUILD READY: W-CAP docs <n> slots <n> (marked-likely <n>/bare-likely <n>); top-up docs <n> slots <n>; contexts <n>; controls pool 40 (sheet <path>); excluded docs <n>; est. Codex <pts>`.
