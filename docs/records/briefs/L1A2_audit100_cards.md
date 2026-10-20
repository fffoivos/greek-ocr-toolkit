# L1A2 — Cards for the 100-line precision audit of the sf6 release (gpt-6.1-sol, xhigh, network ON for Clariden only)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck-s8`). No `.git` writes; other worktrees read-only. No gate/detector/reader
changes. Clariden only to extract the 100 selected overlay records (with their evidence) from
`/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1e_20261017/l1r_sf6_3680729/release/overlay_ensemble_ab.jsonl.gz`
(streamed on the login node; ≤ a few minutes, else STOP). SSH transient errors retry ≤ 3; auth/cert STOP; never refresh the cert.

## Inputs
- Selection: `docs/records/labelfix/spellcheck/clariden/L1R3_evidence/production_3680729_3680730/audit100_ids.jsonl` (+ receipt): 100 of the 155
  ENSEMBLE_AB sf6 real mark-correction lines; per-line `weight` (N_wave/n_wave).
- Original v2 labels: `docs/records/harvest/collection/v2/import_real_v2_train.jsonl`; crops from the harvest roots it references.

## Do
For every line, every changed WORD (label diff original vs released, NFD; aliases as one atom, not carded): a card with the word zoom
(≤ 3×, no stretching), the full line, and the candidates Google form vs released form (+ the recogniser's form if different) in seeded random
order, sources hidden, plus "none of these / unreadable". ≥ 8% planted controls, each pixel-verified by you on the image before planting
(a control whose "verified" form is not what the print shows is a defect — S8 DEV had one: a Google iota subscript the print lacked).
Write `S8_DEV/audit100/{items_blind.json,img/}` and the key `S8_DEV/private/audit100/items_key.json` (line id, wave, weight, forms, sources);
key out of the blind deck. Report card counts per wave in `docs/records/labelfix/spellcheck/L1A2_CARDS.md`; last line:
`L1A2 READY: 100 lines, <c> word cards (+<k> controls, all pixel-verified); per wave …`.
