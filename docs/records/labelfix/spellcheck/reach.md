# Reachability census (text only)

    python -m greekocr.labelfix.reach --seed 0 --seed 1 --out docs/records/labelfix/spellcheck

Text only (no crops, no ink): for every Google mark error the human text reveals on the three-way
Wikisource lines, the earliest stage of the owner's design that could reach it, and for every Google
word that is CORRECT, whether the same stages would propose a change (the load the ink must reject).

Stages, in order (the first that applies wins):
  guard         the word is excluded by policy (Latin/digits, all caps, hyphen line end, abbreviation,
                capitalised non-initial word)
  constraint    Google's form violates a hard orthographic constraint and the human form does not
  grave         Google writes an acute on the final syllable where the human writes a grave, and
                another word follows on the line (positional; deterministic)
  lex_unique    Google's form is unattested (< ATTESTED_MIN) and the human form is the ONLY attested
                one-cluster mark variant
  lex_compete   Google's form is unattested, the human form is one of several attested variants
  lex_miss      Google's form is unattested but the human form is not among the one-cluster proposals
                (two clusters differ, or the human form is unattested)
  real_word     Google's form is attested and so is the human form (needs the ink to contradict Google)
  human_unatt   Google's form is attested, the human form is not (out of reach of a lexicon design)
The model's reading is recorded only to split each class by "model also wrong".


### Seed 0: 189 Google mark errors (human differs from Google in marks only); 4 are human-text errors, universe 185

| stage | all | % of universe | model right | model also wrong | HOLD-reachable | mark kinds |
|---|---:|---:|---:|---:|---:|---|
| human_error | 4 |  | 0 | 4 | 0 | accent 2, accent+breathing 2 |
| guard | 12 | 6.5% | 7 | 5 | 0 | accent 6, accent+breathing 3, breathing 3 |
| constraint | 12 | 6.5% | 10 | 2 | 0 | breathing 4, accent+breathing 3, accent+breathing+dialytika 3, accent 2 |
| grave | 8 | 4.3% | 5 | 3 | 0 | accent 8 |
| grave_line_end | 13 | 7.0% | 10 | 3 | 0 | accent 13 |
| lex_unique | 34 | 18.4% | 22 | 12 | 34 | accent 12, breathing 12, subscript 10 |
| lex_compete | 5 | 2.7% | 1 | 4 | 0 | breathing+subscript 2, breathing 2, accent 1 |
| lex_miss | 28 | 15.1% | 17 | 11 | 0 | subscript 10, breathing 8, accent 7, multi 2, dialytika 1 |
| real_word | 66 | 35.7% | 32 | 34 | 0 | accent 44, breathing 13, subscript 6, accent+breathing 2, breathing+subscript 1 |
| human_unatt | 7 | 3.8% | 3 | 4 | 0 | breathing 3, subscript 3, multi 1 |

Reachable in principle (constraint + grave + grave_line_end + lex_unique + lex_compete + real_word): 138 of 185 (74.6%); of the 78 the model also gets wrong: 58 (74.4%).
Reachable when the image is ambiguous (HOLD: Google unattested, the human form the unique attested one-cluster variant): 34 (18.4%).
Load on the 5728 correct Google words: lexicon proposes on 19 (unique proposal, i.e. HOLD would fire wrongly: 18); hard constraints flag 11; final acute kept correctly mid-line before a word: 187, at the line end without punctuation: 6 (the grave rule must not fire on these: acute-everywhere prints and words that end the sentence).
HOLD text-only precision on this set: 34 right vs 18 wrong = 65.4% before any ink.

### Seed 1: 189 Google mark errors (human differs from Google in marks only); 4 are human-text errors, universe 185

| stage | all | % of universe | model right | model also wrong | HOLD-reachable | mark kinds |
|---|---:|---:|---:|---:|---:|---|
| human_error | 4 |  | 0 | 4 | 0 | accent 2, accent+breathing 2 |
| guard | 12 | 6.5% | 6 | 6 | 0 | accent 6, accent+breathing 3, breathing 3 |
| constraint | 12 | 6.5% | 8 | 4 | 0 | breathing 4, accent+breathing 3, accent+breathing+dialytika 3, accent 2 |
| grave | 8 | 4.3% | 6 | 2 | 0 | accent 8 |
| grave_line_end | 13 | 7.0% | 12 | 1 | 0 | accent 13 |
| lex_unique | 34 | 18.4% | 18 | 16 | 34 | accent 12, breathing 12, subscript 10 |
| lex_compete | 5 | 2.7% | 3 | 2 | 0 | breathing+subscript 2, breathing 2, accent 1 |
| lex_miss | 28 | 15.1% | 12 | 16 | 0 | subscript 10, breathing 8, accent 7, multi 2, dialytika 1 |
| real_word | 66 | 35.7% | 24 | 42 | 0 | accent 44, breathing 13, subscript 6, accent+breathing 2, breathing+subscript 1 |
| human_unatt | 7 | 3.8% | 1 | 6 | 0 | breathing 3, subscript 3, multi 1 |

Reachable in principle (constraint + grave + grave_line_end + lex_unique + lex_compete + real_word): 138 of 185 (74.6%); of the 95 the model also gets wrong: 67 (70.5%).
Reachable when the image is ambiguous (HOLD: Google unattested, the human form the unique attested one-cluster variant): 34 (18.4%).
Load on the 5728 correct Google words: lexicon proposes on 19 (unique proposal, i.e. HOLD would fire wrongly: 18); hard constraints flag 11; final acute kept correctly mid-line before a word: 187, at the line end without punctuation: 6 (the grave rule must not fire on these: acute-everywhere prints and words that end the sentence).
HOLD text-only precision on this set: 34 right vs 18 wrong = 65.4% before any ink.
