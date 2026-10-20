# T1 — Reachability census for the owner's design (16 Oct 2026, Athens evening)

Branch `opus/spellcheck` (worktree `~/Projects/greek-ocr-toolkit-spellcheck`, from `fable/label-correction` 153ff82e).
Command: `python -m greekocr.labelfix.reach --seed 0 --seed 1` (text only, 5 s; no crops, no ink, no model forward pass).
Full tables: `reach.md`; per-error records: `reach_s{0,1}.jsonl`; HOLD false fires: `hold_fp_s{0,1}.jsonl`.
Crop sheet (HOLD fixes and breaks, seed 0): https://claude.ai/artifact/7sVuoSr8wovdyJAoSSCnuY (`python -m greekocr.labelfix.sheet`).

## Universe
189 Google words on the 1,264 three-way lines whose human form differs from Google's in marks only (the old "193" also
counted base-letter / sigma diffs). 4 of them are human-text errors (the human form breaks a hard constraint: ἐδὴλουν,
προσπιπτὸντων …) and are taken out: **universe 185**. The classes are text only, so they are the same for both seeds; only
the "model also wrong" split differs (78 seed 0, 95 seed 1).

## Earliest stage that can reach each error (seed 0 | seed 1 model-wrong)

| stage | errors | % | model also wrong s0 / s1 | what it needs |
|---|---:|---:|---:|---|
| guard (name, caps, hyphen, abbreviation) | 12 | 6.5 | 5 / 6 | policy |
| constraint (Google impossible, human possible) | 12 | 6.5 | 2 / 4 | deterministic + ink |
| grave (final acute → grave, next word on the line) | 8 | 4.3 | 3 / 2 | positional + ink has an accent |
| grave_line_end (same, last word, no punctuation) | 13 | 7.0 | 3 / 1 | positional is NOT enough: 6 correct line-final acutes on the same lines |
| lex_unique (Google unattested, human = only attested 1-cluster variant) | 34 | 18.4 | 12 / 16 | lexicon + ink; **HOLD-reachable** |
| lex_compete (several attested variants) | 5 | 2.7 | 4 / 2 | ink picks |
| lex_miss (no 1-cluster attested variant: count 1–4, two clusters, coinage) | 28 | 15.1 | 11 / 16 | LLM proposal step (task 4) or a lower attestation floor |
| real_word (Google attested and human attested: ἢ/ἦ/ἣ, ὡς/ὧς, οἷος/οἶος, των/τῶν, final acute→grave before punctuation) | 66 | 35.7 | 34 / 42 | ink must read a mark other than Google's AND the lexicon must attest the form (both agree) |
| human_unatt | 7 | 3.8 | 4 / 6 | out of reach of a lexicon design |

**Reachable in principle: 138 / 185 (74.6%)**, including **58 / 78 (74%) and 67 / 95 (71%) of the errors the model also
makes**. The old design's ceiling was the model-right half only (13.5% recall achieved).

## Load on correct Google words (5,728 on these lines)
- Lexicon proposes on 19 correct words (18 unique proposals, i.e. HOLD would fire wrongly 18 times).
- Hard constraints flag 11 correct words.
- 187 correct final acutes mid-line before a word (the acute-everywhere prints) and 6 at a line end: the grave rule must not
  fire on these; the page style detector + ink slope must.
- **HOLD precision, text only: 34 right vs 18 wrong = 65%.** The 18 breaks (sheet, second group) are mostly print
  conventions the ink shows: no dialytika in ἐυσταθέος / ἀυτῇ / ληίδ' (Homeric edition 384c3f89, 7 of 18), no subscript in
  ταύρω / κωμωδία, plain acute in χαίρ', no coronis in τούνεκεν. So HOLD must mean "the ink does not contradict", with
  contradiction defined concretely (subscript blob absent, two dots absent, breathing blob absent, classifier reads Google's
  class at a lower threshold), never "the ink abstains = accept".

## Findings that change the engine (go into the Sol briefs)
- **N1 — acute/grave lookup.** `Lexicon.freq` maps grave→acute but not acute→grave; a correct final acute whose lexicon form is
  mostly grave (τοκετός / τοκετὸς) looked unattested and drew a grave proposal: 11 of the 30 false proposals. Final
  acute↔grave is the grave stage's business; proposals that differ only there are dropped. (Implemented in `reach.py`
  `written_freq` / `spell_props`; must move into `spellink.proposals`.)
- **N2 — initial ρ breathing** is optional in 19th-c. prints (as in `constraints.py`); ρ/ῥ-only proposals are dropped.
- **Biggest class is real-word errors (36%)**, invisible to a "Google unattested" trigger. The owner's rule ("only when they
  agree") reaches them as ink-proposes / lexicon-permits: the mark classifier reads a class ≠ Google's at p ≥ τ and the
  lexicon attests the implied form. This is the third column (INK-CONTRADICTS) of task 3 and its main recall lever.
- **Grave at the line end** and **grave before punctuation** (16 of the real-word cases) cannot be positional; they need
  the slope of the ink mark, per book.
- Dialytika-only proposals are an edition convention; they need the two dots in the ink and never go to HOLD.
