# Owner remarks, 17 Oct 2026 (verbatim, in order; spell-check lead session)

Context: the sf6 release audit page (https://claude.ai/artifact/6ymjnnYCvJ1yYJfpZ8bXDD, 100 print-checked corrected lines), the
substitution page (https://claude.ai/artifact/FEt1TDdCcXdFfjqW1J3W29, 60 lines) and the held-out reader-errors sheet
(https://claude.ai/artifact/75DVJQetceTYHZeNvWJWn2, 39 slots). Times are approximate Athens time.

## Recogniser role
1. "the thing I see here is that you are also doing character recognition which is dangerous, apart from teh fact that it might be very costly"
2. Decision (question answer, ~08:50): recogniser **"Only locate"**: no recogniser vote on deleting/changing any Google character.

## Reader vs detector
3. "why are we addign an accent in 241c524ed5b20f2baadf4b8b-p000119-l0012 when there is no detection shown"
4. "how does that make sense bruv, doesnt the reader see only what is detected"
5. "so now you have added an opus reader as well?"
6. "so now you just detect chars, tehn you send the chars to the reader and you generate without detection? / can we at least detect where there additions without detection from the recognizer?"
7. "also in 39fbbdfd2c8030f211a318b7-p000090-l0035 / I see that you note it is a disagreement between reader and recognzier, but I see a detection there" (my tag bug; fixed)
8. "the detector must see ink will lead to other errors, the reader is stronger"
9. "OK my assessment is that your reader alone is strong but we should consider how to try to improve it further."

## Substitutions
10. "you said there are no deletions, but are there substitutions?"
11. "there must be contradictory substitutions though: i.e. something that we have detected we should add, but there is another accent there that contradicts it already. / you know what I mean? how many such cases are there?"
12. "ook show me some cases of substitution in a new artifact"
13. "I have finished reviewing the second artifact; and it also supports the substitution rule; there are only a few case where it is wrong which is worthwhile considering if we can fix them"

## Error categories, fixes, regression
14. "in your first artifact I think accents tend to be hallucinated on capital A and small o / do you have a ground truth to check that against? / could this be a recurrent error in training data, or something we can correct in the training mix? / after re-training can you test for regressions? or if the fix changed only the intended behaviour?"
15. "ok so to reiterate / what do you need to do to fix this error of hallucination? / do you have regression tests in place to check that we didnt change naythig else?"

## Training runs
16. "describe hte training ytou did for this reader"
17. "so presumably now we can rerun this because we have the reader and it will give us stronger agreement data?"
18. "how long does training take"
19. "ok should definetely run an experiment where we use exactly teh same dataset + recipe plus the changes (additions or removals) that might correct this issue. / but we should also plan other ones, eg the bootstrapping experiment I described earlier"

## Page format
20. "you have changed the artifact again" (I had broken the owner template: word zooms, highlight, Printed row, summary strip)
21. "can you make it so that the chars where accents differ have bg colour in OURS and GOOGLE"
22. "can you make it so that if I click into a line I see zoomed version without the boxes / or even better just create like a magnifying glass effect when I hover over it but there are no boxes there"
23. "yeah can you make it so they are tagged, make the bg colour of the char different colour eg red when they disagree, and add a tag as well. "Differs from google" is not a useful tag by the way, that's the point"

## Categories as discussed with the owner (lead's evidence, for the design review)
| Category | Evidence |
|---|---|
| iota subscript added on -η endings where print has η | audit 13/17 wrong lines; held-out unfixed 4 "subscript dropped" (opposite direction) |
| marks on capitals: ALL-CAPS words, lone capitals, numeral Α΄ / initials .Α. | held-out 12/13 false marks; DEV 2/2 numeral Α΄; audit .Ἀ., ΦΡΆΓΚΙΣΚΗ |
| breathing added in unmarked/monotonic print (ο, οι, εξ-) | audit ο→ὁ (2016 textbook), οι→οἱ; DEV εξασφαλίζεται |
| ΐ (dialytika + tonos) read as circumflex | substitution page πρωΐ (owner note); only 233 training examples |
| missed coronis/breathing in crasis (τὤρθες) | substitution page (owner note); detector saw it |
| clipped tops → wrong or uncertain marks | substitution page ὀχυ- (p=0.49), vouli εἰσάγεται/ἐφημερίς |
| Google breathing errors left unfixed (ἕ/εἷ/ἧ…) | held-out 10 "other" unfixed |

Measured on the audit (corrected tag lookup): above-mark additions with detector ink 38/38 right, without 5 right / 4 wrong;
subscript additions detector-named 33 right / 8 wrong, no ink 8 right / 5 wrong. Substitution page by group (owner review, no note =
right): reader+detector agree 20/20, detector names another 19/20, no ink 17/20. Training labels: articles ο/οι 15,230 with breathing
vs 112 bare; numeral/initial Α 357 bare vs 3 marked.
