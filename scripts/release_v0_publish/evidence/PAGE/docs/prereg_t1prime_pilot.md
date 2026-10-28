# Pre-registration — T1′ MULTILINGUAL PILOT (scoped; frozen before GPU spend)

**Status:** DRAFT → to be **FROZEN before the A1 GPU launch** (the first spend of this tranche,
owner-gated). This doc + the two graders it pins are the pre-commitment: arms, data, metrics, seeds,
and the pass/fail bars are fixed HERE, before results are seen. No arm, metric, seed, or bar is added
or moved after results (house rule; cf. `docs/prereg_t1.md`).

This is a **scoped pilot**, NOT the full gated T1′ program. It answers ONE question: *does training
the existing recognizer on the full tri-script mix (instead of the Greek-only slice) produce a
genuinely multilingual model that (a) reads Latin/Cyrillic, (b) has no mixed-line cliff, (c) does not
regress Greek, and (d) meets the speed budget* — on the synthetic font-OOD eval. Out of scope
(the "move on" phase): real-image eval (WP-B/Pogretra), GTC teacher branch, capacity widening, the
full T1′ rights/gate. **Every number here is SYNTHETIC-ONLY** (transfer-dev is rendered, font-OOD,
text-disjoint — NOT real images); a real-image confirmation is a separate later gate.

---

## 1. The defect this pilot removes (measured incumbent anchor)

Root cause (`docs/reviews/fable_multilingual_speed_analysis.md`, verified firsthand): every trained
checkpoint used `train.py --greek-only` (`train/train.py:274`), so Latin/Cyrillic output classes
never received a gradient. The pinned incumbent `out/prime_checkpoints/t1_compact_nfd_s0/best.pt`
(sha `d99614b0a15d603d…`, arch compact, head nfd) measured on the FULL transfer-dev
(`out/transfer_dev_v4/reserved`, all scripts, seed 0, this machine, 2026-07-12):

| metric | incumbent (Greek-only) |
|---|---|
| greek_mono CER | 0.0041 |
| greek_poly CER | 0.0078 |
| greek_latin_cs (code-switch) CER | 0.1280 |
| **latin CER** | **0.8833** |
| **cyrillic CER** | **0.8746** |
| overall CER | 0.0546 |
| **no-cliff** (cs − greek) | **delta +0.1229 / ratio 24.71×** |
| **homoglyph accuracy** (389 all-caps L/Cyr tokens) | **0.0000** |

(greek_mono/greek_poly reproduce the S16 ledger 0.0041/0.0078 exactly — the grading harness is sound.)

## 2. Arms (pre-registered — exhaustive)

| arm | `--arch` | `--head` | slice | seeds | role |
|-----|----------|----------|-------|-------|------|
| **T1′-a32** | `a32` | `nfd` | full tri-script mix (drop `--greek-only`) | {0,1,2} | the multilingual baseline |
| T1′-compact (optional control) | `compact` | `nfd` | full mix | {0} | geometry control, diagnostic only |

- **Geometry = `a32`, decided (owner override of the "carry ≥2 finalists" rule, recorded in
  `execution_state.json`).** a32 is 3.77M params (same as compact), 9.905 GMAC (vs 15.275), and
  CER-indistinguishable from compact on the S19 synthetic screen. The choice is **reversible** (one
  cheap retrain); a later real-image eval may reopen it. The compact control is run only to keep that
  reversal cheap — it does NOT gate the baseline.
- Head = `nfd` (the S16 P1 winner; not re-litigated here).
- **From-scratch is the default.** Warm-start from the Greek-only a32 checkpoint (`--resume`) is an
  optional owner accelerator; if used it is DISCLOSED and is not the clean headline.

## 3. Data + custody (SHAs pinned)

- **Train / val:** `out/strips_v4a/{train,val}` — the full realized tri-script set (190,564 / 9,124
  rows; latin 14.97% / cyrillic 8.02% / code-switch 17.98%, recipe-matched <0.1pp; verified green).
  Recipe sha `1b9924840600e099…`. NO `--greek-only` filter (`train/data.py keep_classes=None`).
- **Eval (selection + all metrics):** `out/transfer_dev_v4/reserved` — font-OOD (held-out trio
  Theano­Didot / Libertinus­Serif / IBMPlexSans), text-disjoint reserved band. 7,994 rows: greek_mono
  4636 / greek_poly 2253 / greek_latin_cs 622 / latin 265 / cyrillic 213 / cyrillic_latin_cs 5. Shard
  sha `7aa387cf791309e8…` / `1ad51ed82e6cbc26…` (match `prereg_t1.md`). Its `audit_ok:false` is a
  FALSE ALARM (a training-recipe content_marginals check wrongly applied to a reserved band; the
  non-Greek rows decode to real English/Ukrainian/Russian/Greek+Latin — verified). Foreign slice is
  small (1,105 rows) → wide CIs on latin/cyrillic; disclosed.
- **Graders (frozen SHAs):** `train/grade_t1.py` = `9d022ef12795d5da` (headline+polytonic, unchanged);
  `train/grade_multilingual.py` = `da89c5afa1742c0f` (per-script CER + no-cliff + homoglyph — NEW,
  self-check PASS). Producer `train/dump_preds.py` = `373d56077e5bd1a0` (modified additively to stamp
  `script_class`; not a §7-frozen artifact). Codec `codec/v1.json` = `d1b7e2d40565e89e` (unchanged).

## 4. Metrics (frozen definitions)

From the frozen `grade_t1.py`: `headline_cer`, `polytonic_cer` (selection continuity with S16).
From `grade_multilingual.py` (definitions frozen here):
- **per_script CER** — strict NFD corpus CER within each `script_class`.
- **no_cliff** — `delta = cs_cer − greek_cer`, `ratio = cs_cer / greek_cer`, where `greek_cer` pools
  {greek_mono, greek_poly} and `cs_cer` is greek_latin_cs (`GOAL.md:100` no-cliff contract).
- **homoglyph_acc** — over ALL-CAPS Latin/Cyrillic tokens in the ref, the fraction whose letter-core
  survives verbatim in the hyp (the confident-transliteration probe). Secondary `foreign_token_acc`
  = same over all cased Latin/Cyrillic tokens.
All reported per arm as **mean ± sample sd over the 3 seeds**. `blank_rate` void rule carries from
S16 (a seed whose blank_rate collapses is void, re-run, not graded).

## 5. The "good baseline" gate (pass/fail bars — frozen, report RAW)

Baseline is "good" iff ALL of the following hold on the 3-seed mean (synthetic transfer-dev). Numbers
are pinned now, before results; a miss is reported as a miss (no goalpost move, no green-shading):

| # | bar | threshold | incumbent |
|---|-----|-----------|-----------|
| B1 | reads Latin | latin CER ≤ **0.15** | 0.8833 |
| B2 | reads Cyrillic | cyrillic CER ≤ **0.15** | 0.8746 |
| B3 | no mixed-line cliff | no_cliff delta ≤ **0.02** (abs) | +0.1229 |
| B4 | homoglyph survival | homoglyph_acc ≥ **0.85** | 0.0000 |
| B5 | no Greek regression | greek_mono ≤ **0.006** AND greek_poly ≤ **0.011** | 0.0041 / 0.0078 |
| B6 | speed | a32 fp16 ≤ a few ms/strip on ANE, OR WP-E §6 budget met | (Workstream B) |

**STOP at the gate.** If all pass → the multilingual baseline is achieved; move on to the next phase.
If any fail → report the failing number(s) raw and pick the next lever (more foreign share / capacity
/ warm-start / longer schedule) — do NOT declare the baseline good.

## 6. Geometry / decision rule

- a32 stands as the shipped geometry UNLESS: (i) a32 misses an accuracy bar (B1–B5) that the compact
  control clears → switch to compact; or (ii) the WP-E probe disqualifies a32 on B6 where compact
  passes → switch to compact. Otherwise a32 is final for this phase.
- **Implementer ≠ certifier:** the pilot RESULT is certified by a genuine-Fable review before any
  "baseline achieved" claim leaves this repo; this doc is the implementer's pre-commitment.

## 7. Budget & custody note

GPU is owner-gated; the A1 launch is ONE approval for the parallel batch (a32 × {0,1,2} concurrent on
H100-class, wall-clock ≈ one run). Cost ≈ low tens of $ inside `T1PRIME_planning_envelope` = $80.
Teardown DELETE is the authoritative cost-stop. Never commit shards / pages / `*.pt`.
