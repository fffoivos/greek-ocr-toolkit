# L1M2 native ownership panel review

I inspected all four final twelve-panel sheets, including their original grayscale
and tinted native-pixel zooms. I also inspected all thirteen own-census sheets
(100 line thumbnails). These are observations about the supplied crops and maps,
not an independent page-level print or mask-ownership adjudication.

| Panel | Observation |
| --- | --- |
| 1 | Red upper-row strokes and a purple unowned fringe at the top disappear; the current line's green letter bodies remain. The flagged neighbour blob clears. |
| 2 | Orange lower-row crumbs at the bottom disappear; the current green bodies remain above the edge. |
| 3 | Red upper strokes disappear on gray paper. The target epsilon/current line remains; the top predicate clears. |
| 4 | Orange lower-row strokes, surrounded by some purple pixels, disappear. The accented current letters remain green. |
| 5 | The crop cuts across the current green lower letter bodies. Those pixels remain at the bottom after masking. This is old L1M border panel 8. |
| 6 | The green eta's bottom stroke reaches the crop bottom. Removing upper red/purple material leaves that contact intact. This is old L1M border panel 10. |
| 7 | The lower green alpha/body is cut by the crop bottom; small upper unowned material disappears. This is old L1M border panel 12. |
| 8 | A green accent above alpha reaches the top boundary and survives. This is an own mark contact, in addition to the three body-cut examples. |
| 9 | Large diagonal/background ornamental strokes overlap the current text. The source map retains much of this as green class 1; the original border also has class-0 pixels. This is a mixed, persistent counterexample to treating every retained pixel as a clean letter-only padding witness. |
| 10 | The mixed top blob contains a purple part of a pale diagonal stroke and class-0 detector pixels. Purple pixels disappear, but gray diagonal material remains at the top. The predicate persists. |
| 11 | The purple part of a faint top stroke is removed. The mixed blob's original class-0 share does not force the clipping predicate to survive; the saved masked flag clears. |
| 12 | Red and purple portions of the upper-row material both disappear; neither reaches 80% of the original blob. The current text remains green and the mixed flag clears. |

There are no ring-abstained examples: label 5 is absent from all 260 maps, not
just from the chosen panels. Panels 9–12 use the requested mixed alternative.

The own-census thumbnails show many clear top accent/ascender contacts and
bottom body/descender cuts. They also show isolated class-1 dots, pale background
strokes and two all-foreground-class-1 identity fallbacks. In particular, census
29 (round1 `b963a5d59be557e9eef8498b-p000042-l0020`) and census 80 (vouli
`17cbdf94881f-p000002-l0015`) cannot establish ownership from their fallback
maps. Census 27 / panel 9 is an ornamental-background counterexample.

Consequently the automated 100-line / 27-sole-hold result is retained as an exact
query of the supplied class-1 contract, with the 98-line nonambiguous subset
reported separately. I have not relabelled exported pixels or called this a
verified 100-line semantic letter/mark census. Nor do the images prove how many
out-of-crop pixels would restore a cut glyph. The component band extent is an
observed padding proxy, not a measured sufficient new crop margin.

The 100 thumbnails cover one representative flag per candidate line, not every
one of the 290 own-contact flags. Exhaustive flag/pixel accounting is in the
machine-readable ledgers; the twelve requested panels are targeted witnesses.
