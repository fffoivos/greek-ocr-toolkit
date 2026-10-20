# R2C: R2 grader decks. Document inventory, validation reservation, tranches (2) and (4) (gpt-6.1-sol, medium, network OFF)

Workspace: THIS worktree (`~/Projects/greek-ocr-toolkit-spellcheck-r2cards`, branch `opus/r2-cards`, head = R2 plan 52f34de9).
- No `.git` writes, and no writes outside this worktree.
- Python `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`, `PYTHONPATH=$PWD`.
- **Mac CPU, saved data only:** no recogniser, reader or detector inference, and no Clariden.
- Read-only inputs, other worktrees included: `~/Projects/collect-v3-data/run` is READ-ONLY (a live collector holds locks there). Never
  write or lock anything inside it.

Spec: `docs/records/labelfix/spellcheck/R2_PLAN_20261017.md` §1–§5, and `docs/records/reviews/astra_program_review_2026-10-06/ASTRA-R2design_review_1.md`
§1, §5 and §6. This task builds the blind decks. The track lead runs the Opus readers afterwards.

## 1. Eligible documents and the deterministic validation reservation (do this FIRST, before any drawing)

**Universe of new documents** (outside every test set, and outside R1's 316 C1 documents):

**(a) W1 rows** from `~/Projects/collect-v3-data/run/W1/candidates.jsonl` (25,920 rows) whose stratum
`(tranche, source, primary_class, gazette_stratum)` has status `c1_pass` in
`~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_exclusions/unchecked_strata.json`.
- Greek strata only: bsb_poly1850/poly1850, ia_poly1850/poly1850, nlg/greek_poly, nlg/poly1850, nlg/poly1900. Skip elstat
  numerics_tables and serbia cyrillic.
- The row must also pass the owner's line-level admission checks: its own `usable_final`/`candidate_usable` fields true, and not listed
  in any `release_exclusions.json` class id file (same dir).
- Document = `item`.

**(b) Collection-v2 train documents outside the 316 C1 documents**: `~/Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl`,
where C1 documents are the `doc` values in `.cache/labelfix/clariden/C1_selection.jsonl`.
- Classes `greek_mono` and `greek_poly` only. These are mostly parliament/openarchives/mixed monotonic; they feed the ο/οι/monotonic
  slices.
- Document = `doc`.

**Exclude everywhere:**
- every line or document in the S8 DEV census, `~/Projects/greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/S8_DEV/S8_DEV_ids.txt`
  (exclude their documents too);
- audit100 lines;
- the 666 held-out lines (`load_three_way(0)` ids) and their documents;
- any v2 dev/test split.
Report every exclusion count.

**Document roles**, assigned before drawing:
- Stratify by source × era (decade of `year`; v2 uses its `wave`/`year`).
- Order documents by `sha256("R2:2026-10-17:" + doc)`.
- Assign: **10% validation reserve** (never drawn by any tranche), **witness** (at least 20 documents and about 20% of the rest),
  **calibration** (about 15%), and **supervision** (the remainder).
- Roles are disjoint.
- Write `docs/records/labelfix/spellcheck/R2/doc_roles.json`: per document its role, source, era and line count, plus the rule and the sha256 of
  every input.

## 2. Word locator (geometry only, never labels)

Cards need the word's position in the line crop.
- **W1:** use the stored Document AI token or symbol geometry. The page JSONs under `run/W1/pages/` point to the saved responses, read
  read-only. Map it to crop coordinates through the row's `crop_bbox`.
- **v2 lines:** look for stored geometry in the harvest data the same way.
- **Lines without trustworthy geometry are not used.** Count them per source. Do not run OCR models to locate words.
- **Sanity check:** the word box must hold ink and must not cut a letter. Show 20 random word boxes per source in a QA strip image for the
  lead.

## 3. Candidate mining (Google text is a selection key only, never shown and never a label)

Mine words in **supervision documents** for tranche (2), and in **witness documents** for tranche (4). The patterns below fix the slices.
Each slice draws both the target-head-absent and the marked counterpart.

| Slice | Absent (negative) candidates | Marked (positive) candidates |
|---|---|---|
| capitals | all-caps words (≥ 2 letters), lone capital vowels, initials (Α. Ν.), numeral-adjacent capitals (Α΄, Β΄) | capitals carrying a breathing/accent (Ἀ Ὁ Ἡ Ἐ Ἄ …), marked capitals inside all-caps words where they exist |
| ο / monotonic | ο, οι, ό, bare word-initial vowels in greek_mono lines, εξ- | ὁ, οἱ, ὅ, word-initial breathings in polytonic lines |
| subscript | words ending -η, -α, -ω where -ῃ/-ᾳ/-ῳ forms exist | -ῃ, -ᾳ, -ῳ (incl. ῇ, ῄ, ᾷ, ῷ, ᾧ …) |
| specks / neighbour ink | words in lines with high `neighbour_body_ink_xh`, `accent_ink_cut_fraction` or near the crop edge (W1 features) | same lines, marked words |
| exact names (positives only) | — | word-final grave vs acute; circumflex; ΐ/ΰ and dialytika forms; psili vs dasia; crasis/coronis (mid-word breathing: κἀγώ, τοὔνομα, τἆλλα …) |

**Diversity caps:** at most 10% of a slice from one document, at most 5 cards per page.

## 4. Card format (reuse `~/Projects/greek-ocr-toolkit-spellcheck-s8/scripts/labelfix/l1a2_cards.py` / `s8_prepare.py` conventions; copy them in, don't import across worktrees)

One card = one word. It shows:
- a word zoom: uniform scale ≤ 3×, no stretching;
- the full line strip at native pixels.

No boxes, no model output, no "Google", no confidence.

**Options:**
- the candidate forms differ only in the target head (for example η / ῃ; ο / ὁ / ὅ; Α / Ἀ / Ἁ; ά / ὰ / ᾶ), generated from the word's
  base letters, never from a model;
- randomised order;
- plus "none of these: transcribe the word exactly as printed" and "unreadable / cut".

The reader answer schema gives:
- the chosen option or a literal transcription;
- for the anchor letter, all four heads (breathing, accent, diaeresis, subscript), each as a value or `unknown`;
- `readable` / `partial` / `unreadable`;
- `ownership_ok` (the mark belongs to this letter, not a neighbour line or a speck);
- confidence high / medium / low;
- a short note.

Reader instructions go in `README.md`: transcribe what is printed, misprints included; do not normalise spelling.

**Blinding:**
- Image file names are content hashes; nothing in a path or the page reveals the book, page, line or source.
- The key lives in a separate private dir.
- Run a leak scan over the blind dir and report it.

## 5. Decks

**Tranche (2), R2a native supervision: 800 cards + 80 controls.**
- Split over the slices in proportion to the plan's §2a totals: capitals ≈ 260, ο/monotonic ≈ 160, subscript ≈ 180, specks ≈ 120,
  exact names ≈ 80.
- About half absent and half marked where the slice has both.
- **C1 mark-error cards first where eligible:** `~/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/` plus the run's
  `W1/c1/*/cards.jsonl`, joined by exact crop/line identity, in supervision documents only.

**Tranche (4), development witnesses: 800 cards + 80 controls, from ≥ 20 witness documents.**
- 400 contrasts: 100 capital/numeral, 100 ο/monotonic, 100 subscript, 100 exact names/crasis, each with marked and absent counterparts.
- 200 uniformly random words with at least one vowel.
- 200 robustness/ownership words: specks, neighbour ink, crop edge.
- **Paired views:** for 50 of the robustness words, add padding-only, mild-skew (±1.5°) and span-jitter views of the SAME source word,
  tagged as repeated views of one witness.

**Controls**, about 10% per deck: unambiguous words drawn from the same deck's documents. Write their expected form into
`controls_proposed.json`, with the images beside it, for the **lead to pixel-verify before any reader starts**. Controls are excluded
from every denominator.

**Tranche (3), calibration:** do NOT build it. It needs teacher outputs. Only reserve its documents (§1).

## 6. Resolve and inventory script (for after the readers)

Write `scripts/labelfix/r2_cards_resolve.py`:
- **Inputs:** two reader answer files per deck (reader 2 sees reverse order).
- **Controls gate:** a reader failing more than one control is reported, and their batch is not used.
- **Tiebreak deck:** built for disagreements, with options re-randomised.
- **Resolution:** 2 of 3.
- **Truth file:** per card, the printed word form and the four-head tuple for every letter whose state is decided. Undecided heads are
  `unknown`.
- **Usable-slot inventory:** per slice and per deck, counting distinct `(crop sha256, letter index)` with complete four-head targets,
  absent vs marked.
- **Opus usage table:** cards, readings, tiebreaks, tokens.

Test it with synthetic answer files.

## Deliverables

- `docs/records/labelfix/spellcheck/R2/` containing: `doc_roles.json`, `decks/T2/{blind/, private/}`, `decks/T4/{blind/, private/}`,
  `controls_proposed.json` per deck, the QA strips, `R2C_REPORT.md` with counts (eligible, excluded, geometry coverage, per-slice
  candidates and drawn cards, caps hit, shortfalls), and the receipts.
- Tests green, none weakened.

Last line:
`R2C READY: docs <n> (val <v> / witness <w> / calib <c> / supervision <s>); T2 <k>+<c> controls; T4 <k>+<c> controls; geometry coverage <..>; shortfalls <..>; tests <n> passed`.
