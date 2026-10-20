# E-build2: third bed (owner 39-card sheet) for the adjudication-efficiency experiment (gpt-6.1-sol, xhigh, network OFF, nice, ≤ 45 min)

This continues E-build (b8658ae0) in this worktree. It is build work only. **Write only under `docs/records/harvest/collect_v3/c1/efficiency/`.** A live W2 collection imports `collect_v3/*.py` from this checkout: never touch `collect_v3/` or any other existing file outside that folder. Do not modify the bsb or yer packs, keys or the scorer behaviour for those beds; extend them.

## The bed
- **Truth:** `~/Projects/greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/R2_evidence/reader_errors_39_owner_final.json` (read-only). There are 39 cards; the owner confirmed his pass:
  - 38 cards are `left_as_shown`, meaning the shown truth form stands;
  - 1 card is `noted`: `384c3f89-p000059-l0013:s33`, ἤγε, "this is circumflex actually". Its breathing is UNKNOWN until v1.1, so exclude that card from breathing scoring and score its accent as circumflex.
  - This is exposed evaluation material. It must never appear in any reader folder.
- **Inputs:** `.../R2_evidence/reader_errors_39_card_inputs.json`, which gives per card the absolute line-crop path, letter_bbox, word_index, letter_in_word and word_bbox.
- **The E0 protocol is the spell-check track's current practice:** `.../R2_evidence/READER_PROTOCOL_R2.md`. Use its verbatim reader prompt (the T4 version) and the files readers receive (README.md and answer_schema.json from `~/Projects/greek-ocr-toolkit-spellcheck-r2cards/docs/labelfix/spellcheck/R2/decks/T2/blind/`).
  - Card images: render them the way the R2 deck does, using `~/Projects/greek-ocr-toolkit-spellcheck-r2cards/scripts/labelfix/r2_cards_prepare.py` (word zoom at integer ≤3× plus the native line). Port it or call its functions **read-only**, and state which.
  - Strip from the reader items everything the R2 deck strips. No truth form, section, owner note or Google/reader "error" framing may reach a reader. Give the reader exactly what an R2 deck card gives.
  - All three spell-check paths are read-only. Never write in those worktrees.

## Arms (practice: every card is read by 2 readers, reader 2 in reverse order)

| arm | per reader | readers |
|---|---|---|
| E0a, E0b | all 39 cards, E0 protocol unchanged, R2 deck images; r1 in seeded order `eff:owner39:<arm>`, r2 in its reverse | 2 + 2 |
| E2 | no native-line image: only the word crop (3x) and the letter close-up (8x) over letter_bbox, as build_r1a_errors.py renders them (word: word_bbox x-range ±6 px at full height, 3× LANCZOS; letter: letter_bbox ± max(6, w/2) at full height, 8× NEAREST). Prompt = E0 with only the input-image sentence changed; state what the reader lost. | 2 |
| E3 | compact prompt (instructions once, minimal item lines, every rule kept), R2 deck images | 2 |

E1 and E4 do not apply: the bed is smaller than one practice batch. Record that in the README.

- Pack folders: `efficiency/packs/owner39/<arm>/<r1|r2>/`, with crops **copied**, never symlinked. Keys go in `efficiency/keys/`.
- Extend the isolation test to this bed: no truth, key, owner note or verdict may be reachable.
- Extend `score.py` with an `owner39` bed: per-card agreement with the owner truth on the fields the R2 answer schema shares with the truth (base letter and mark tuple per slot, and unknown handling as the protocol defines). Also report agreement with E0a, E0a–E0b agreement, unknown counts, and usage per card from the supplied usage JSON (never estimated).
- Update `MANIFEST.json`, the usage and verdict templates, and the README.

## Hand-off
Tests pass, including the existing 33. Leave a guarded commit list as before (PNGs git-ignored). The last line must be exactly:
`E-build2: done | owner39: <n> cards, <n> readers | E0 protocol: R2 T4 verbatim <yes|no> | isolation test: <ok> | tests: <n> passed`
