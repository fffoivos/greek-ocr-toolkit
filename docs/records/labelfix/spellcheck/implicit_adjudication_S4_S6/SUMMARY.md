# S4 → S6 changes at the owner's implicitly approved slots, settled by the print

The scope is every word on a line the owner reviewed on the S4 pages (review v16, examples v10) where S4 and S6 read different marks at a slot his note does not name. That gives 59 words, plus 8 planted controls.

Method:
- Two blind Opus readers (A/B order random, the source of each form hidden).
- Crop zoom ≤ 3×, with the full line for context.
- "neither" allowed, with the printed form given.

Reader quality:
- Planted controls: 7/8 correct for both readers. On item062, πιέζει, both saw an extra tick and answered neither.
- The readers agree on 58/59 words.
- item002 was settled by the track lead from the crop (ἀνανδρίας).
- item001 (πὄχει) is unresolved: the readers disagree on the printed form.

Mark errors against the print on the 58 resolved words:

| | missed | false | total |
|---|---:|---:|---:|
| S4 | 57 | 21 | 78 |
| S6 | 27 | 20 | 47 |

By word:
- S6 is closer to the print on 37 words, further on 16, and equal on 5.
- Of these, both readers chose S6's form outright on 31 words and S4's form on 8. On 19 words neither form matched the print.

The 16 words where S6 regressed fall into three groups:
- Lost marks: Ὠς→Ως, ἀνανδρίας (−1), κραυγὴν, ἐκβάλη (−1), ἐπέρασε, εἶχε→εῖχε, Ἄρκτος (−2), ᾅδην (subscript kept, breathing still wrong).
- False marks: Ἐμπρ͂ὂς and τρ͂ἰσκότειδο (circumflex on ρ, breathing on medial ο/ι), βἳος, νὓν, Δἐν, ξεφαντωτἡς, Κλωθὠ.
- Misnamed: Ἐμμανουὴλ→Ἑ.

Files: `items_key.json` (with the forms and sources), `reader1.jsonl`, `reader2.jsonl`; prep script `scripts/labelfix/owner_implicit_adjudication_prep.py`.
