# SF5 — Release gate: elision marks are never deleted when Google and the recogniser both have them (gpt-6.1-sol, xhigh, network OFF)

Workspace: `~/Projects/greek-ocr-toolkit-spellcheck` (branch `opus/spellcheck`, head = this brief's commit on c6064650 = frozen SF4). No `.git`
writes. Do not touch other worktrees (read-only use of files named below is fine). Python `/Users/foivoskarounos-zamparloukos/Projects/
greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`. Mac CPU; no detector/R1/CTC inference — decisions from saved evidence only. All labelfix
tests green, none weakened; every rule change gets a witness test that fails on c6064650 and passes after. **Change exactly the two rules below
and the alias accounting; nothing else in the gate** (coordinator: this reopens review; the same reviewer thread verifies SF5 only).

## The defect (track lead, L1A audit, `~/Projects/greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/L1A_AUDIT_REPORT.md`)
In `v2-corrected-ensemble-ab-sf4` (L1R 3679725) 714 of 2,107 corrected lines delete a printed elision apostrophe (753 deletions); PRESENCE
354/1,003 lines (373 deletions), FULL 323/903 (339). Mechanism: under ENSEMBLE_AB the detector supplies apostrophes; where it finds none, the
composer drops Google's elision mark although the recogniser's text has it (`κ' ἡ`, `μ' αὐτά`). Separately, Google's spacing ᾿ before a capital
(one breathing, `-᾿Αλλά`) was kept while the combining breathing was added from the recogniser (`-'Ἀλλά`) → two marks where the print has one.
431 AB lines (216 PRESENCE, 200 FULL) are alias-only (᾿/᾽/' → ’) and were counted as corrections. `greekocr/labelfix/text.py: ELISION` treats
U+1FBF/U+1FBD as elision in every position — the context-blind root.

## Rules (coordinator ruling, exact)
1. **Never delete an elision mark that Google and the recogniser both have.** Elision = a word-final ' ’ ʼ ᾽ ᾿ after a letter (incl. after
   combining marks), aliases as one atom. Detector absence of an apostrophe is not evidence of absence here (C2-B01 principle). Where only one
   of Google/recogniser has it, keep current behaviour but record it in the elision census below.
2. **A spacing ᾿/᾽ before a capital** (or word-initial before a vowel) is a breathing, not an apostrophe: when the release attaches the
   combining breathing to that letter, the spacing mark is removed **in the same edit**; it is never kept alongside. If the breathing is not
   attached (held/uncertain), the spacing mark stays as Google has it. Do not fold it to ’.
3. **Alias-only changes are not corrections.** A line whose only differences are elision-alias codepoints gets status `unchanged` (the codec v2.1
   fold to U+2019 happens at training time, not in the release); per-line and manifest counts report them separately as `alias_only`.

## Witnesses (all become repository tests)
- The 6 wrong L1A corrections (`…-s8/docs/labelfix/spellcheck/L1A_AUDIT_REPORT.md`; saved evidence under
  `~/Projects/greek-ocr-toolkit-spellcheck-l1/docs/labelfix/spellcheck/L1M_evidence/200/details.jsonl.gz`): κ᾿→κ and μ᾿→μ must keep the mark;
  `-᾿Αλλά` / `-᾿Ανεξιχνίαστοι` must give one breathing (`-Ἀλλά` form, no extra apostrophe) or stay as Google has it. **ἐν→ἑν and διορίσῃ→διορίση
  are reader naming errors, not elision**: SF5 must NOT add rules for them; record them as known-wrong precision witnesses (expected to stay wrong).
- A seeded 50 of the 714 (`docs/records/labelfix/spellcheck/SF5_witness/witness_50_ids.txt`, full saved AB overlay records with evidence in
  `SF5_witness/sf5_witness_50_ab_records.jsonl.gz`, original labels from `docs/records/harvest/collection/v2/import_real_v2_train.jsonl`): after SF5,
  zero elision deletions where Google and the recogniser both have the mark; report what else changes on those lines.
- Recompose those 56 lines from their saved runtime under SF5 (dry run, local) and show before/after labels.

## Elision row in every held-out table (coordinator, binding from SF5 on)
The 666 instrument never scored elision. Add to the held-out evaluation (all modes PRESENCE / FULL / ENSEMBLE_AB / ENSEMBLE_AE, before = SF4,
after = SF5) an **elision row**: printed apostrophes kept / deleted / added (truth = the human Wikisource text where it is pixel-adjudicated,
else the R0 adjudications; aliases as one atom; state the truth source and its coverage). Also add it to the M2 dev-pool table (never the
locked stratum (ii)). The mark rows stay as they are; any change in mark rows must be explained per slot.

## Report
`docs/records/labelfix/spellcheck/SF5_REPORT.md`: rule diffs, witness table (56 lines before/after), held-out tables with the elision row, M2 dev table,
alias accounting, and the policy id `sf5-release-v1`. Last line:
`SF5 RESULT: policy sf5-release-v1; witnesses elision-kept <k>/<n>, double-breathing fixed <d>/2, known reader errors unchanged 2/2; held-out AB corrected <..>, wrong <..>, new <..>, elision deleted <a>→<b>; alias-only lines no longer counted; tests <n> passed`.
