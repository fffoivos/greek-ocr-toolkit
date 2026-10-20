# Three OCR engines on the failed-lines catalogue — T12 v1

Status: **complete**. Transkribus model **148525**, supplied single-line layout, Anemi first. 469/469 crop IDs measured, 396 unique images. Source coverage: `{'Anemi': 174, 'Vouli': 295}`. Stop reason: `None`. Next unmeasured crop: `None`.

No engine is a reference. CER here measures disagreement, not transcription accuracy. Strict pairwise NFD CER preserves case, spaces, punctuation and line breaks; forward denominators are the first named engine. Reverse CER and mean bidirectional CER are in the raw CSV. Empty denominators with nonempty counterparts are null, two empty strings have CER zero. Majority is at least two identical readings and is separately reported raw, NFD, and with only CR/LF removed; spaces are never collapsed.

## Anemi assessment

**docai looks best on Anemi by cross-engine agreement**: the mean of its two pooled bidirectional NFD disagreement rates is lowest. Scores: docai 0.459, vision 0.485, transkribus 0.597. Common cohort: 174/174 Anemi crop IDs. This is a consensus ranking, not measured accuracy. No engine is a reference, two engines can agree on a shared error, and a manual transcription is needed for an accuracy winner.

Anemi output diagnostics (full measured engine coverage): docai: 174 measured, 5 empty, 0 rare-glyph crop IDs; vision: 174 measured, 5 empty, 0 rare-glyph crop IDs; transkribus: 174 measured, 1 empty, 1 rare-glyph crop IDs. Rare-glyph output is complementary evidence to review, not proof of a correct historical transcription.

## Pairwise disagreement and majority agreement

| Source | Three readings / catalogue | DocAI–Vision NFD CER | DocAI–Transkribus NFD CER | Vision–Transkribus NFD CER | Majority raw | Majority NFD | Majority raw without CR/LF | Majority NFD without CR/LF |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Anemi | 174/174 | 0.347 | 0.484 | 0.527 | 9 | 9 | 21 | 21 |
| Vouli | 295/295 | 0.175 | 0.296 | 0.296 | 18 | 18 | 74 | 74 |
| ALL | 469/469 | 0.225 | 0.350 | 0.363 | 27 | 27 | 95 | 95 |

All three-way statistics use the common measured cohort. Existing DocAI–Vision readings for crops without Transkribus remain visible but are excluded from those denominators. Crop-ID weighting follows T10/T11; duplicate SHA images share one charge. The comparison JSON also reports unique-image cohorts, controls, unanimous counts and source agreement rates. Consensus score = the mean of the engine’s two pairwise pooled bidirectional CERs; this ranking is an inference about agreement.

## Controls baseline and treatment by failure type

The same T10/T11 exposure rule is used: multiple returned lines, empty text, or mean/min symbol confidence below that engine’s control p05. PAGE line confidence is preserved separately; it is not treated as character confidence. Missing glyph confidence remains null, so confidence-triggered exposure is unavailable for Transkribus when PAGE has no Glyph objects. Controls are owner-verified geometry, not gold text. Density is descriptive.

| Type | Engine | Measured / total | Lines distribution | Empty rate | Mean symbol median (p05) | Min symbol median | Line confidence median | Chars/100px median (p05–p95) | Exposed / silent |
| --- | --- | ---: | --- | ---: | --- | ---: | ---: | --- | --- |
| control_owner_verified | docai | 181/181 | `{0: 3, 1: 118, 2: 30, 3: 14, 4: 13, 5: 1, 6: 2}` | 0.017 | 0.917 (0.746) | 0.426 | 0.896 | 4.323 (2.703–5.882) | 69/112 |
| control_owner_verified | vision | 181/181 | `{0: 2, 1: 105, 2: 34, 3: 18, 4: 16, 5: 2, 6: 1, 7: 1, 8: 1, 11: 1}` | 0.011 | 0.864 (0.710) | 0.173 | 0.831 | 4.254 (2.703–5.882) | 84/97 |
| control_owner_verified | transkribus | 181/181 | `{1: 181}` | 0.006 | — (—) | — | — | 3.883 (1.835–5.720) | 1/180 |
| missed_line | docai | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| missed_line | vision | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| missed_line | transkribus | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| missed_words_in_row | docai | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| missed_words_in_row | vision | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| missed_words_in_row | transkribus | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| line_start_missed | docai | 2/2 | `{1: 2}` | 0.000 | 0.880 (0.847) | 0.256 | 0.880 | 3.944 (3.811–4.077) | 0/2 |
| line_start_missed | vision | 2/2 | `{1: 2}` | 0.000 | 0.878 (0.814) | 0.314 | 0.878 | 3.944 (3.811–4.077) | 0/2 |
| line_start_missed | transkribus | 2/2 | `{1: 2}` | 0.000 | — (—) | — | — | 3.816 (3.798–3.834) | 0/2 |
| missed_word_after_gap | docai | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| missed_word_after_gap | vision | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| missed_word_after_gap | transkribus | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| curl_end_cut | docai | 7/7 | `{1: 6, 5: 1}` | 0.000 | 0.954 (0.823) | 0.601 | 0.932 | 3.946 (3.749–5.961) | 1/6 |
| curl_end_cut | vision | 7/7 | `{1: 6, 3: 1}` | 0.000 | 0.892 (0.838) | 0.124 | 0.891 | 3.902 (3.748–5.121) | 1/6 |
| curl_end_cut | transkribus | 7/7 | `{1: 7}` | 0.000 | — (—) | — | — | 3.946 (3.677–4.186) | 0/7 |
| multi_line_segment | docai | 272/272 | `{0: 8, 1: 101, 2: 64, 3: 51, 4: 27, 5: 14, 6: 4, 7: 1, 9: 2}` | 0.029 | 0.893 (0.732) | 0.330 | 0.862 | 4.512 (3.186–10.709) | 172/100 |
| multi_line_segment | vision | 272/272 | `{0: 8, 1: 82, 2: 68, 3: 57, 4: 25, 5: 18, 6: 7, 7: 5, 8: 1, 9: 1}` | 0.029 | 0.849 (0.698) | 0.148 | 0.827 | 4.817 (3.182–10.876) | 198/74 |
| multi_line_segment | transkribus | 272/272 | `{1: 272}` | 0.004 | — (—) | — | — | 3.884 (2.321–5.690) | 1/271 |
| misaligned_crop | docai | 1/1 | `{1: 1}` | 0.000 | 0.942 (0.942) | 0.377 | 0.942 | 4.136 (4.136–4.136) | 0/1 |
| misaligned_crop | vision | 1/1 | `{1: 1}` | 0.000 | 0.880 (0.880) | 0.128 | 0.880 | 4.068 (4.068–4.068) | 0/1 |
| misaligned_crop | transkribus | 1/1 | `{1: 1}` | 0.000 | — (—) | — | — | 3.932 (3.932–3.932) | 0/1 |
| faint_ghost_kept | docai | 5/5 | `{0: 1, 1: 4}` | 0.200 | 0.765 (0.550) | 0.455 | 0.765 | 3.030 (0.182–3.332) | 3/2 |
| faint_ghost_kept | vision | 5/5 | `{0: 1, 1: 4}` | 0.200 | 0.703 (0.496) | 0.263 | 0.703 | 3.030 (0.467–3.779) | 3/2 |
| faint_ghost_kept | transkribus | 5/5 | `{1: 5}` | 0.200 | — (—) | — | — | 1.818 (0.182–3.867) | 1/4 |
| crop_extends_over_faint | docai | 3/3 | `{0: 1, 1: 2}` | 0.333 | 0.635 (0.553) | 0.279 | 0.635 | 2.700 (0.270–2.911) | 3/0 |
| crop_extends_over_faint | vision | 3/3 | `{1: 3}` | 0.000 | 0.647 (0.495) | 0.181 | 0.647 | 3.134 (0.617–3.144) | 2/1 |
| crop_extends_over_faint | transkribus | 3/3 | `{1: 3}` | 0.000 | — (—) | — | — | 2.137 (2.101–3.169) | 0/3 |
| crosses_column | docai | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| crosses_column | vision | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| crosses_column | transkribus | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| frame_or_ornament_boxed | docai | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| frame_or_ornament_boxed | vision | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| frame_or_ornament_boxed | transkribus | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| stamp_or_watermark_boxed | docai | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| stamp_or_watermark_boxed | vision | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| stamp_or_watermark_boxed | transkribus | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| blob_boxed | docai | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| blob_boxed | vision | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| blob_boxed | transkribus | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| spread_or_columns_as_one_geometry | docai | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| spread_or_columns_as_one_geometry | vision | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| spread_or_columns_as_one_geometry | transkribus | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| fragment_crop | docai | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| fragment_crop | vision | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| fragment_crop | transkribus | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| unclear_owner_intent | docai | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| unclear_owner_intent | vision | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |
| unclear_owner_intent | transkribus | 0/0 | `{}` | — | — (—) | — | — | — (—–—) | 0/0 |

Google rows above retain their full existing 469-crop treatment baselines; Transkribus coverage is explicitly smaller if credit-limited. Per-engine confidence scales differ. Missing ink without a catalogue crop has no OCR evidence. Bound page-comment coverage is in the JSON; no whole-page substitute was submitted.

## Rare glyphs actually emitted

Counts are raw code points over unique measured image SHA values. They do not prove glyph correctness; no glyph-level reference or exposure denominator is supplied. Each engine’s coverage is shown.

| Source | Character | DocAI count | Vision count | Transkribus count |
| --- | --- | ---: | ---: | ---: |
| Anemi | unique measured images | 160 | 160 | 160 |
| Anemi | ϗ U+03D7 | 0 | 0 | 0 |
| Anemi | ȣ U+0223 | 0 | 0 | 0 |
| Anemi | ϛ U+03DB | 0 | 0 | 1 |
| Anemi | ϲ U+03F2 | 0 | 0 | 0 |
| Anemi | Ϲ U+03F9 | 0 | 0 | 0 |
| Anemi | ϝ U+03DD | 0 | 0 | 0 |
| Anemi | ϙ U+03D9 | 0 | 0 | 0 |
| Anemi | ϡ U+03E1 | 0 | 0 | 0 |
| Anemi | ͅ U+0345 | 0 | 0 | 0 |
| Anemi | ʹ U+02B9 | 0 | 0 | 0 |
| Anemi | ͵ U+0375 | 0 | 0 | 0 |
| Vouli | unique measured images | 236 | 236 | 236 |
| Vouli | ϗ U+03D7 | 0 | 0 | 0 |
| Vouli | ȣ U+0223 | 0 | 0 | 0 |
| Vouli | ϛ U+03DB | 0 | 0 | 0 |
| Vouli | ϲ U+03F2 | 0 | 0 | 0 |
| Vouli | Ϲ U+03F9 | 0 | 0 | 0 |
| Vouli | ϝ U+03DD | 0 | 0 | 0 |
| Vouli | ϙ U+03D9 | 0 | 0 | 0 |
| Vouli | ϡ U+03E1 | 0 | 0 | 0 |
| Vouli | ͅ U+0345 | 0 | 0 | 0 |
| Vouli | ʹ U+02B9 | 0 | 0 | 0 |
| Vouli | ͵ U+0375 | 0 | 0 | 0 |
| ALL | unique measured images | 396 | 396 | 396 |
| ALL | ϗ U+03D7 | 0 | 0 | 0 |
| ALL | ȣ U+0223 | 0 | 0 | 0 |
| ALL | ϛ U+03DB | 0 | 0 | 1 |
| ALL | ϲ U+03F2 | 0 | 0 | 0 |
| ALL | Ϲ U+03F9 | 0 | 0 | 0 |
| ALL | ϝ U+03DD | 0 | 0 | 0 |
| ALL | ϙ U+03D9 | 0 | 0 | 0 |
| ALL | ϡ U+03E1 | 0 | 0 | 0 |
| ALL | ͅ U+0345 | 0 | 0 | 0 |
| ALL | ʹ U+02B9 | 0 | 0 | 0 |
| ALL | ͵ U+0375 | 0 | 0 | 0 |

## DocAI kai-sign readings (`κὶ`)

| Crop | Source | Document AI | Vision | Transkribus |
| --- | --- | --- | --- | --- |
| [an-00f143ecce59-p000258.mark2.r7item1](../../harvest/three_engines_review.html#an-00f143ecce59-p000258.mark2.r7item1) | Anemi | ΕῬρωσο. τῦτο γὰρ ἐγὼ κὶ συωσύχομαι σοι, κὶ ἀκῶσαι<br>ποθῶ πεὶ σὲ · κὰν ὅτι τατὸ ὅτι παρὑμῖν ἐπι<br>.<br>σείλης. ε μικρων ἔχειν δωρεαν ἡ και της τύχης<br> | ET<br>Ἔρωσο. τότο γὰρ ἐγὼ καὶ συνεύχομαι σοι, καὶ ἀκεσαι<br>ποθώ πει σε καν ὅτι τοτὸ ὅτι παρέμεν επι<br>σείλης 2 μικρον ἔχων δωρεαν είναι το πάσης<br>.<br>έναν | ΕΝΙΕΣ ΕΝ τΑ νΑνε υ ζαζατει πρνε |
| [an-2cfe28da5103-p000135.mark40.r7item16](../../harvest/three_engines_review.html#an-2cfe28da5103-p000135.mark40.r7item16) | Anemi | ὁπλιτῶν κὶ τῶν ἱππέων ὄντων. ΙΖ΄<br> | ὁπλιτῶν καὶ τῶν ἱππέων ὄντων ΙΖ&#x27; | ὀπλίφων , των ἐππέων ὅντων. 12΄. |
| [an-7a2b17a3fb0f-p000012.mark2.r7item2](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000012.mark2.r7item2) | Anemi | τέρων, κὶ 6 τρίτων, γράφομεν ὕτω 15°<br> | τέρων, καὶ 6 τρίτων, γράφομεν ὕτω 15° | τέρων, ἢ ὁ τρίτων, γράφομεν ὅτω 15 |
| [an-a73d22211479-p000141.mark69.r7item70](../../harvest/three_engines_review.html#an-a73d22211479-p000141.mark69.r7item70) | Anemi | κορωπι ἐχθροί. κὶ ἐκείνη ἐτάθη Ε΄-<br> | πρώτα εχθροί.<br>εχθροί. ἢ ἐκείνη ἐτάθη Ε- | !κ. πρῶπα ἐχδροί. » ἐκείνη ἐφάβη Ε- |
| [an-a73d22211479-p000301.mark61.r7item59](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark61.r7item59) | Anemi | AA<br>κὶ, τότο (εἶπεν) εἶναι πολὺ διὰ ἕν<br>१<br>10<br> | &gt;<br>7870 (επω) είναι πολύ διὰ | κ, σο ( εἶπον) εἶναι πολὴ δια ἔ- |
| [an-b9d6f9c086e2-p000162.mark81.r7item81](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000162.mark81.r7item81) | Anemi | καις ὅπὸ ταῖς μάσιγες, κὶ ἐγω νὰ ἐ-<br> | μ<br>King<br>καις ἀπὸ ταῖς μάσιγες, καὶ ἐγὼ<br>Al | καὶς Σκῦ ταῖς μάςιγες, ἡ ἔχω νὰ ἔ- |
| [an-b9d6f9c086e2-p000255.mark38.r7item36](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark38.r7item36) | Anemi | πὲ ἦτον τέλειος Θεὸς, κὶ τέλειος ανθρω<br> | &gt;<br>πὲ ἦτον τέλειος Θεός, καὶ τέλειος αἴθρω | πε ἦτον πέλειος Θεὸς, κ, τέλειος αὔδρω- |
| [an-b9d6f9c086e2-p000255.mark38.r7item38](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark38.r7item38) | Anemi | τη, μψώντας δεος<br>ο ανθρωπος ετεω<br>θη, μλύωντας ανθρωπος, κὶ ἐκεῖνος, ὁ<br> | JEW.<br>η μυωντας σας ο ανθρωπος εθεω<br>της μύωντας ανθρωπος, καὶ ἐκεῖνος, ό-<br>31- | δη, Σμθύωνπας αὔδρωπος,  ἔκεινος,ο- |

## Transkribus rare-glyph crops

1 crop IDs; 1 distinct images.

- [an-3352d912f2e9-p000055.mark3.r7item3](../../harvest/three_engines_review.html#an-3352d912f2e9-p000055.mark3.r7item3): `ϛ`; τῷ ἐχδρῶ καπράη οὗ πολῷ δ’ ὕϛερον, αἰγά τιναι.

## Native crop checks

Four native crop images were inspected against the three readings. These are illustrative observations, not complete reference transcripts or a held-out accuracy evaluation. [Hash-bound findings](transkribus_failed_lines/visual_findings.json).

- [an-3352d912f2e9-p000055.mark3.r7item3](../../harvest/three_engines_review.html#an-3352d912f2e9-p000055.mark3.r7item3): Native crop shows the historical st ligature in the word rendered by Transkribus as ὕϛερον; DocAI emits ὕςερον and Vision ὕτερον. This is useful complementary glyph output. Adjacent letters and the cropped neighbour differ, so this is not a reference transcription.
- [an-00f143ecce59-p000258.mark2.r7item1](../../harvest/three_engines_review.html#an-00f143ecce59-p000258.mark2.r7item1): The crop visibly contains several printed rows. The imposed single-line Transkribus reading loses the readable row structure and returns mostly capital fragments, whereas both Google readings preserve several rows. This limits the supplied-line geometry on known multi-line failures.
- [an-2cfe28da5103-p000135.mark40.r7item16](../../harvest/three_engines_review.html#an-2cfe28da5103-p000135.mark40.r7item16): The native kai sign lies between ὁπλιτῶν and τῶν. DocAI writes κὶ, Vision writes καὶ, and Transkribus emits a comma at that position. None preserves ϗ in this example.
- [an-7a2b17a3fb0f-p000012.mark2.r7item2](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000012.mark2.r7item2): The native kai sign after τέρων is returned as κὶ by DocAI, καὶ by Vision, and ἢ by Transkribus. These readings do not preserve the sign as ϗ.

## Supplied whole-crop line mode

The API supports preliminary `content.regions[].lines` with polygon/baseline. One region and one line span the crop with a horizontal baseline at 75% height; native image bytes remain unchanged. Three paired probes explicitly used layout model 49272 from the published legacy API example, with its other detection parameters at defaults; all returned zero lines. Earlier omitted-layout and empty-block probes are retained separately and included in cost, not used to infer detection capability. The main comparison uses supplied single-line layout. This is a geometry hypothesis, especially on curved or multi-line failures; one returned line is imposed and cannot diagnose multiple printed rows. [Request schema](https://transkribus.eu/processing/v1/openapi.json).

| Crop SHA | Default layout | Supplied single line | Credits |
| --- | --- | --- | ---: |
| `a3ca75d07a0fcbca69a2800a7a5977444359589c1d8cc83ffeffe58ba2f71cdb` | (empty) | ρῶ;!. πάρχειν αὐτοὶ κακως ἔξω. | 0.25 |
| `e0dea7008cad50cf8d0816eaf499bc60c044e58a8635374b9c2feb49bd7517b6` | (empty) | », 2’ φὰ φλιὰ, κ τῷ 5 ραρδέματα χεράκια, | 0.25 |
| `ef1faa03315aa9f682cbeae9bdb4f9643a46b8ec7c4643afceeb817bac7a3022` | (empty) | ὑμῖν δὲ τοῖς ἄλλοις τοῖς ἐξω- | 0.25 |

## Credits and calls

Credits before: **200.0**; after: **99.0**; observed consumption: **101.0**. Sum of crop-bound per-page charges: **100.75**, plus **0.25** for an unassigned charged process. 405 submissions, 403 cached pages with verified crop binding (including layout-mode probes), 3048 recorded HTTP calls; roles `{'balance': 819, 'submit': 405, 'poll': 999, 'page': 403, 'page_credit': 396, 'token': 21, 'reconcile_transactions': 2, 'unassigned_poll': 1, 'unassigned_zip': 2}`. Floor **50**; every pending and next page reserves **1.0** credit. Cash cost was not exposed, so no monetary charge is invented. Six one-image jobs maximum; main source cohorts drain in Anemi-first order. Per-page charges use job-matched debit transactions; early sequential pilot charges used before/after balances. Queue snapshots overlap jobs and are not individual charges.

Credit snapshots use `GET /TrpServer/rest/credits?onlyActive=true&includeExpired=false`; only the balance and safe call metadata are retained. Credentials were read from environment only. OAuth access/refresh tokens and account identity fields are never persisted. [Credit API schema](https://transkribus.eu/TrpServer/rest/openapi.json), [processing credit policy](https://docs.transkribus.org/start/credits).

| Mode | Process | Image SHA | Credits before | Credits after | Used per page |
| --- | --- | --- | ---: | ---: | ---: |
| single_line | 31484540 | `002cba8a386bbea08acd7000c9c33b6af185a009050dbeab227ae1273f13c043` | 134.0 | 132.5 | 0.25 |
| single_line | 31483977 | `00a79919e2d439648b20ac526e7569b88fddd2224a6e73a0c58aa8ce385122db` | 164.0 | 162.5 | 0.25 |
| single_line | 31484761 | `00bba22b2dc1823c7c323b6b68f82ebc5ae3055dfc9b36a9c7b428ef2770af6f` | 114.25 | 113.75 | 0.25 |
| single_line | 31484515 | `02932b45d8c04cdf211791656219901a74a94c82bd28a64fcba4d68889b9cfcc` | 136.5 | 135.0 | 0.25 |
| single_line | 31484353 | `02d6ea7fe9321d42a889bb959c343c43caa20e6cd4e5a50b8a4f48a052afd469` | 151.75 | 150.75 | 0.25 |
| single_line | 31484827 | `03063a0889e0d4fa8042cba936601d19244e8eaef795cf06b5feb8d1b6b16aac` | 108.0 | 107.75 | 0.25 |
| single_line | 31484582 | `04eb25805cffc021d16d415717cfbd5c9569ec5e7823c4303addbc42229e0abc` | 130.5 | 129.0 | 0.25 |
| single_line | 31484843 | `05b8f4c88094e095916e61a4d265b9ee62ce0fcb87b94c01e8e06d3cee8dea04` | 106.75 | 106.25 | 0.25 |
| single_line | 31483782 | `072d5c0147f5874aa1c39ab64b758351072197a13cdcc8f570ab230b9415884a` | 191.75 | 190.25 | 0.25 |
| single_line | 31483831 | `07b2e0e54b0cb5ce6167b97979bf8139a9e06a4037012da1a0675cc4a7a9d496` | 186.25 | 185.25 | 0.25 |
| single_line | 31484725 | `07ef84cb0c4b420fddf968c2ad38c075d63c90a12da6c1f58b279148409adf5f` | 117.25 | 117.0 | 0.25 |
| single_line | 31483829 | `086b8cb400b30340b2b32252372228aa349cf486ce380a19cdf90044a6391c7e` | 186.75 | 185.25 | 0.25 |
| single_line | 31484616 | `0ae3c588436ca22d8609cee9dd4f0b11499dfac2048592e2cf60d643fa9d477e` | 127.0 | 126.0 | 0.25 |
| single_line | 31484316 | `0b03e90f7e96daf5e3bcadee5a934f4b122e9fef600c628a0ab1d6f3da2ffa8c` | 153.75 | 152.25 | 0.25 |
| single_line | 31484452 | `0b2a38a37db6ddc009fc3c96c33c6c39c72e79256cf8e4a63f02c57cd60d75e4` | 143.0 | 141.75 | 0.25 |
| single_line | 31484825 | `0e193564be906e729e1869ac94a71f4bb80d36dbba8f7e57c00950aed65be6e6` | 108.5 | 107.75 | 0.25 |
| single_line | 31484881 | `0e766216af5de9ff4657af147de7d984f365d56e25ff4aadd7eaf587b898fae7` | 103.25 | 101.75 | 0.25 |
| single_line | 31483972 | `0f9cce15dc0f521474c4174cf5b2339964d47867fda0b4055ab23bee3a70a3cf` | 165.0 | 164.0 | 0.25 |
| single_line | 31483941 | `0fd1a3fc224103c5dfdbd392bebda223447cec607fefbaa94bcc37fa6aad617d` | 169.75 | 168.5 | 0.25 |
| single_line | 31483968 | `105aa5d674ca7ad18feeb2afab681d65a6db1ef06e28c938341c7690e971b68e` | 165.75 | 164.75 | 0.25 |
| single_line | 31483847 | `112a9c9ec3322ee3f00cb60445ffb63ad0642a5259a06c27200a160470d70a9c` | 183.75 | 182.25 | 0.25 |
| single_line | 31484530 | `11ee4fb8025741de7363df2330bf9019dc90dfffb70bdddb0b1868c4d676d535` | 135.0 | 133.5 | 0.25 |
| single_line | 31483952 | `12b3dbb0d01a55ee540e9724b8964eb7896169720a9a7cf506e3377cf91064a4` | 168.0 | 166.25 | 0.25 |
| single_line | 31484758 | `1474ce4354eb64e08e76cb8a05751ca9d2bb292b9b6afad452d0f75a1c67c166` | 115.0 | 113.75 | 0.25 |
| single_line | 31484590 | `14c4a42208d7d43c52cc39dcb1602448ffb391976df11a05cb71393421275a0b` | 129.5 | 128.0 | 0.25 |
| single_line | 31484352 | `14ebaceb36b672bd38d4c1ce7952bda72607b5cffc82a190f27e929091a3f1fe` | 152.0 | 150.75 | 0.25 |
| single_line | 31484861 | `151e6e433434bf0b5abfa90dff4e4af1d50cc9d1a2083178c8d1088ba2fdc30f` | 105.0 | 104.75 | 0.25 |
| single_line | 31484013 | `154f8c328f740a8d2f749eb0a4faa3a206af6645fafad90595b0525f59ea5aa7` | 157.75 | 156.75 | 0.25 |
| single_line | 31484599 | `159c26f868abb6607d90dac6541b8554325ab7e13adf3f64b14e763121711326` | 129.0 | 127.5 | 0.25 |
| single_line | 31483872 | `15c5416c02935d9a9a9c1811ba8ee2ae0f244f33ee44872008641c79ca3b457d` | 180.0 | 178.75 | 0.25 |
| single_line | 31484539 | `162051c5ec58f3eeacda6c266f2c02d17bbb491530e16a014d4853d4e40f2fe2` | 134.25 | 133.5 | 0.25 |
| single_line | 31484389 | `168e0ed58f39c9a862d75198894b02f8fd2e193e29aabf7ea045002d349c10d1` | 149.5 | 148.5 | 0.25 |
| single_line | 31484432 | `16ce2b89c908cf28a0457c6349500b2b646d0cc0a1e6a9b9f5fa7be0a3e44102` | 145.0 | 144.0 | 0.25 |
| single_line | 31483937 | `1739fd3ce3fa2934ff80e9d4e6886b2270190ef47f6dae5eafb2734c9181dce2` | 170.25 | 170.0 | 0.25 |
| single_line | 31484654 | `17554f5c53f8e6f283ab78dd8609fb9bda3f9e6b5d7192453d8cc04deb93d786` | 124.5 | 123.0 | 0.25 |
| single_line | 31484689 | `17c27c838ae35b5d9cd46357d383a34be63e3afcde5989983253ad139a4ae64e` | 121.25 | 120.0 | 0.25 |
| single_line | 31484310 | `17c4e456564fcbe4da83086b0c82bacf24a228f69567084f4d00721a103dc7aa` | 154.5 | 153.0 | 0.25 |
| single_line | 31483744 | `17c553817d8985a19d798fd9e125f56ef4fb19f09a4835e715f7c1766d29cb7b` | 197.75 | 197.0 | 0.25 |
| single_line | 31484437 | `1820b3cdf68f87bd14c5c963e3046bfa7399a9089ee1744fe40fde7420a93370` | 144.5 | 143.25 | 0.25 |
| single_line | 31484841 | `18c572b1ee256caf11d123c7e465de84a1614bee918898b6ecafb914ff0bf997` | 107.25 | 106.25 | 0.25 |
| single_line | 31484892 | `19ba908135c8b197f31da91e981b65cab1c360c159beca015b1e773c868ab851` | 102.25 | 101.5 | 0.25 |
| single_line | 31484609 | `1a9a77b2ada9755010e01938cd3b8e8a4ef05a8f60386506f14dc89898f64c77` | 127.75 | 126.5 | 0.25 |
| single_line | 31484639 | `1aa3c125bdf29d6d98f9eafcd58d20c8448e770a46ec93dba50178f348295f48` | 125.25 | 124.5 | 0.25 |
| single_line | 31484398 | `1b53f28cc92edf6c7f1d69a15c9612d1513eb308ef070654d21e60fb482e3722` | 149.0 | 147.75 | 0.25 |
| single_line | 31483877 | `1ba79a86acf229335a16ae11cca036f247d68a9c338bd8230475532b28d0b388` | 178.75 | 177.5 | 0.25 |
| single_line | 31483830 | `1c4751aa99d91eadbb26237d56af9329763bb429b34bef8e89da518bce36d9e7` | 186.5 | 185.25 | 0.25 |
| single_line | 31484691 | `1d036b4f94118210c733796c1e508d4491522cc32da974e3eb78b4f37ab6a214` | 120.75 | 120.0 | 0.25 |
| single_line | 31484474 | `1d968dbdd87020313ed093fd9a7d1a17b20f263209c253f8656cffed79e568c7` | 141.0 | 139.5 | 0.25 |
| single_line | 31484569 | `1e192155102c601a85e5af314fab61c5da62b6338d3889f32113879402eaad61` | 131.75 | 130.5 | 0.25 |
| single_line | 31484430 | `1e629266db71256f36996b4e28bb0b0bc7b50f2d649b403d21cdf33cbe5a1d34` | 145.5 | 144.0 | 0.25 |
| single_line | 31484510 | `1f4a0d4be8b405c9b072e491755ae7a4a15da3b902786c3fa54e434ae6c2d800` | 136.75 | 135.75 | 0.25 |
| single_line | 31483933 | `1f6403d7c4a95a38c848afacd43758d642939f95a3540d1c1f39a01cd0848476` | 171.25 | 170.0 | 0.25 |
| single_line | 31484858 | `1ffc9a8677d950a617cf555718c4ca9f6b5aca5874f33805f8d859dad85a338b` | 105.75 | 104.75 | 0.25 |
| single_line | 31483792 | `208d7b97957b93ab9f50c29a0ce7c562fe6433ad346fbf97520002a08391dd8a` | 190.5 | 189.25 | 0.25 |
| single_line | 31484003 | `21494b66cdbfc2e4f4831e39dc91c747e8f787e7efc627746cdd75540f94b578` | 158.75 | 158.0 | 0.25 |
| single_line | 31483996 | `220f448b99e6fc2aa3473ede994af24e6f717914233c56615c00e0050046879b` | 159.75 | 159.5 | 0.25 |
| single_line | 31484571 | `22cfc75bd089151c69f4d935a5593bb013f9e2e4534fd8cc6b24a7c3e35b00e9` | 131.25 | 130.5 | 0.25 |
| single_line | 31483945 | `22f6899f0f52d582c0c35baeaeceb398b68b4362de6d69f32a0c0a3057e42fd8` | 168.75 | 168.5 | 0.25 |
| single_line | 31484854 | `23740ab9cffdec0d5acc46d9bd2eafa563e44abe4e11e0ed2085360572c8b2e5` | 106.25 | 104.75 | 0.25 |
| single_line | 31483993 | `240afc0c1ffbfd79f40be10c82b5e9aa23b3b471417f7481891552d3762c63d9` | 160.5 | 159.5 | 0.25 |
| single_line | 31483746 | `24c12eeb01b57701ffa372ddabfcc9e644286721ec2a601f7850c995a70dbbfc` | 197.25 | 197.0 | 0.25 |
| single_line | 31483909 | `252afc1b6f3f382edf21f57f62d0fd25b22784213c5d43104723c63c0d788293` | 175.25 | 174.5 | 0.25 |
| single_line | 31484877 | `25a1bd0566bfdd7349fe0933275fed72a8073b5624e4c4bbf6ca2fea4b2152e4` | 103.75 | 103.0 | 0.25 |
| single_line | 31483936 | `263af8a0632b47c24f84966850245f1a8aeed4f5b9e4f77f662ad69e990437f1` | 170.5 | 170.0 | 0.25 |
| single_line | 31484776 | `27394dc9d111c9a1133371dc6efe0066829218327d60ae84e7fa8a8788e28943` | 113.5 | 112.25 | 0.25 |
| single_line | 31484946 | `289f1a8844a360377b17b11ded1f3bd5f2d432b2fa40cefc049c78f2dbfbb798` | 99.25 | 99.0 | 0.25 |
| single_line | 31484502 | `2974711dcc045562cd0d6a52cffc8142a8f8462896089ecfb65cc445c6150374` | 138.0 | 136.5 | 0.25 |
| single_line | 31484711 | `2a333ad2e316576be2d08f0790e0aa11e68646680642dcc2dbee95d87df84e95` | 118.75 | 118.5 | 0.25 |
| single_line | 31483973 | `2bac7931393572bc94ee90533d69b96f2d55205b03cf6e75ee1f930efdf0d452` | 164.75 | 163.25 | 0.25 |
| single_line | 31483911 | `2bb62ba00013777015a4db8c68507d3f17867c69684350d166de98aef64e4ecf` | 174.75 | 174.5 | 0.25 |
| single_line | 31484471 | `2bee4aaa4be373ea1be2f4d932289dd6008668e7324a740f5768cf09945ff3cb` | 141.25 | 140.25 | 0.25 |
| single_line | 31484621 | `2caa91e0650806a450078dbec7b946373459ab013ae66d9762b3d35c997a1ef4` | 126.5 | 126.0 | 0.25 |
| single_line | 31483751 | `2e69ec13a10cbb99c6d77e42af1c688cf51337957ac66b6efeb2c0ba0a1e71f1` | 196.25 | 195.25 | 0.25 |
| single_line | 31483965 | `2f7741c1b6ac2fc971604215f21468c2c9a1e4ce4710dc248107e50ff11a58fa` | 166.5 | 165.5 | 0.25 |
| single_line | 31484462 | `2fc0bb7fdd1d74b2c6d1efb31c1b3b77321d12be2efcc8db45832e89ddb3c2bd` | 142.25 | 141.0 | 0.25 |
| single_line | 31484422 | `3172a049126fb4f8887b1fa069e9a6c0d27650ceecbe214abe6d9dc36aceeff8` | 146.25 | 144.75 | 0.25 |
| single_line | 31484485 | `320feff23bfd5592199ad7f63235e699e27ad878b2d61eeba7c170b93ae62a06` | 139.75 | 138.75 | 0.25 |
| single_line | 31484657 | `3359856590d444469103b2a1093bcf52957faffa154bb941058edb2bd2366e62` | 123.75 | 123.0 | 0.25 |
| single_line | 31484742 | `342adc45aeff0d218fb0604263a6efe4d59baf5c79c44b659087ed45c8333765` | 116.0 | 115.25 | 0.25 |
| single_line | 31484655 | `35d6cf2752e3c7708e05872e7f84db7a118fc5996b77edcaeafdc06d9837764d` | 124.25 | 123.0 | 0.25 |
| single_line | 31484311 | `3600df60fa2c06943cbce650306e64cc6378c2e1667a65e6146edaf14dd91e65` | 154.25 | 152.25 | 0.25 |
| single_line | 31484674 | `3826038585daeb2b0e376ebe3e9e8f2cde682d75cd2ef2fac0c2575f309f3f88` | 122.25 | 121.5 | 0.25 |
| single_line | 31484889 | `384ef3918d0a8e27cad596945d069bd17045afbbabb44cde5071eea7f5c005fc` | 103.0 | 101.5 | 0.25 |
| single_line | 31483858 | `38755a8a6ae8c08b65ee68a56e482d46e1a588585a5da4fc345ad27b347e7404` | 182.25 | 181.75 | 0.25 |
| single_line | 31484625 | `38c5f48944d898acaf85e770a3bf810b94f04379005140e0a1c3b73517f4c93c` | 126.25 | 126.0 | 0.25 |
| single_line | 31483861 | `390e7a73c927d160cf33b6e426db12e098682c4362a3660310d810e1303b2c47` | 182.0 | 180.5 | 0.25 |
| single_line | 31483982 | `39c709fd670f209a0fd6a8a993819593c36c196896efb7320e0b06b15ba0f54b` | 162.75 | 161.75 | 0.25 |
| single_line | 31483839 | `39ded6d32efc79428c20a5b2b2ea50f37fa65f1f7ebabaaa90bbf81a3d3c00e1` | 185.0 | 183.5 | 0.25 |
| single_line | 31484525 | `3a064f4855d03a0b6c277810ef005dab78c6ea96ba536c39b21fca4efaebcef8` | 135.75 | 134.25 | 0.25 |
| single_line | 31484739 | `3a998f1a1a9e4d1e58b802ddfc94de3a2d5275eb44f705982ddc7a4799f9385f` | 116.5 | 115.25 | 0.25 |
| single_line | 31484692 | `3c6c396d3db9d9b02da120b3b0180aace2676f25cff5aa6b2d10ad8f99b70f4b` | 120.5 | 120.0 | 0.25 |
| single_line | 31484489 | `3cfe940e71515d468cea43b8be090ebcb153866e2a57934c25843318a93a6071` | 139.5 | 138.0 | 0.25 |
| single_line | 31483818 | `3ec34a9bcb15cb7e5359ca9090a202a1eab2cc6bdf333f34e71d76a9b4f22f66` | 187.75 | 187.0 | 0.25 |
| single_line | 31483953 | `3f4e00ff060a246f702034317831d123e17e941790a4ca2088eeba63d1edf884` | 167.75 | 167.0 | 0.25 |
| single_line | 31484446 | `3f84db0e5020f75425c6efda0c1a4dba6162c228c99bb73f325f1d3c2262f512` | 143.5 | 142.5 | 0.25 |
| single_line | 31483764 | `407590499e3144161a3c0da8a9a17454b8076e4796d10cc79b2c30c38fa6cc95` | 193.75 | 192.25 | 0.25 |
| single_line | 31484796 | `4181d36dd48238be6895cad33d1ad5595da415464ed86c4b6aeff8de6dceb1b0` | 111.0 | 110.75 | 0.25 |
| single_line | 31483878 | `42dbe1cdd85f80621d4f206316ab5941ebc219815b22363e21eaef64a2ac43a2` | 178.5 | 177.5 | 0.25 |
| single_line | 31484602 | `4422f0167f4b6dd00d8672ef5eb8a33a75e10bd503b51a90bda5964a47b74edc` | 128.25 | 127.5 | 0.25 |
| single_line | 31484690 | `44c0bde47405258700713b0a72a3ced9998565cfaace73d084fb16c9edc653b9` | 121.0 | 120.0 | 0.25 |
| single_line | 31484640 | `456cbdf1358cc4736d4e5c5e584478be6c0d72a4c3dbf71e87f5154cd5503b8b` | 125.0 | 124.5 | 0.25 |
| single_line | 31484664 | `4673a1ea096c66dff8955840460cd6cb7e405a53e7b13a93b7dcb1b51481de0d` | 123.25 | 123.0 | 0.25 |
| single_line | 31484710 | `474978afb0946523849c4bebb2a06d2df4688406839be25fa07b01b3a48dc12d` | 119.0 | 118.5 | 0.25 |
| single_line | 31483985 | `4789c92fc14340cd5d7527d7e0956d0379776a5214c4eaff79cb93335c80de8e` | 162.25 | 161.0 | 0.25 |
| single_line | 31483769 | `480bc180d893c7cdb02834bbb441c12f587666a04d7769012ffbbd6957e0f195` | 193.0 | 192.25 | 0.25 |
| single_line | 31484431 | `4824d99678ae6fba8c5c0cf0dbeec2c236c7e6aee7048b4d0996670436595049` | 145.25 | 144.0 | 0.25 |
| single_line | 31484614 | `499f91926b8e071346008e7a2e06e9b8b6dcc2f843318ece93530ba63768d2e5` | 127.5 | 126.0 | 0.25 |
| single_line | 31484381 | `4a69ca6a0e1a16e88a989ac375de05eea51d74a434b41dc914cff8a4ac41f91a` | 150.75 | 149.25 | 0.25 |
| single_line | 31484527 | `4b0c97a7435b3d7fe1f63679f9ba65966bef7064ca99e32e81f54fd1390554fc` | 135.25 | 134.25 | 0.25 |
| single_line | 31484403 | `4c36b7f1a83e9e25c15985baae12d2c41b852cd27ffff7245a3a22728c4f6f63` | 148.5 | 147.0 | 0.25 |
| single_line | 31483841 | `4cad052be94340d306e5c9b5e54c2e560beefa1a190574bf12be2e00d8854b35` | 184.5 | 183.5 | 0.25 |
| single_line | 31484601 | `4cbda457cbf939d57bbfc8ea9f8b1d8fd334fcd1c35eb7452e2c113611e75fdb` | 128.5 | 127.5 | 0.25 |
| single_line | 31484368 | `4d296b5497321e1cc1ddcdc9f975b7563b8b02bdbb3fcd402134dfb9d28ec7f9` | 151.5 | 150.0 | 0.25 |
| single_line | 31483900 | `4d99387734add0b2eaa35a70b400b1b6c10a9ce61fefa04762f1a2f8d4c1d0ef` | 176.75 | 176.0 | 0.25 |
| single_line | 31483755 | `4e27275d78c2fc4d93d5854e004f4bfaca3b89274236c6dd8646dc77b5044a20` | 195.5 | 194.0 | 0.25 |
| single_line | 31484934 | `4e2c48acad46e45a7e0b89fc72fc1a5059de94ac42a87a0a6efe9db019a22488` | 99.5 | 99.25 | 0.25 |
| single_line | 31484700 | `4fe10d2ba49830468f8cb3b8c7c2131faa40bb9147caebdfc3562e1ca2794005` | 120.0 | 118.5 | 0.25 |
| single_line | 31483808 | `50501a3dcfb61848ec15dd276be6eaf05f50bf601dc8d2db866d990c5ed537fd` | 189.0 | 188.5 | 0.25 |
| single_line | 31484277 | `5182dfb68535a303f8d61cb88a26c5a2794998c89fcf258e1b041f15ebba27e5` | 155.75 | 154.5 | 0.25 |
| single_line | 31484425 | `51bc3b8dd9f932403af6d5fc49d6bf0980a17c424096d502d514c8a68cdc7dc4` | 146.0 | 144.75 | 0.25 |
| single_line | 31484860 | `51cc5c254774d681ecf0864032de204d6b1ba4a0045269eb171f6c6f50df8279` | 105.25 | 104.75 | 0.25 |
| single_line | 31483864 | `5237ade60c2059ac9d5379ee1dc6dea48d8f19d6464ba61d418e8190d16a860e` | 181.5 | 180.25 | 0.25 |
| single_line | 31484688 | `53c0799ecc187a82701b30408f2e6f81c651837d1855fc6ec204cb5b090ae9dc` | 121.5 | 120.0 | 0.25 |
| single_line | 31483851 | `541702598d1da327ef2b3587aa28657f108d6300f56ca8bd96462ef148430286` | 183.5 | 181.75 | 0.25 |
| single_line | 31484736 | `54527816f843380dc96089ab92d19ab6ae8e5ab38de37f4c77a7e84ee6a40534` | 116.75 | 115.25 | 0.25 |
| single_line | 31484890 | `5485328e96dac1a391e029a6cbdcfac3c2d7084991efacf76b70105ae0dad3d0` | 102.75 | 101.5 | 0.25 |
| single_line | 31483990 | `54c76d4d6f091d8d3d9e7b2109559d0353e7105ee342be0dc9fe5d4a23d9e0a2` | 161.25 | 160.25 | 0.25 |
| single_line | 31483852 | `5536aa0e81968e45a052681857cb56749617c28a41731b0ba08b3df7de70d256` | 183.25 | 182.0 | 0.25 |
| single_line | 31484278 | `561256de203d8a532af65207bbcd6461fd63211a930ff8b11e5c2cad737d6465` | 155.5 | 154.5 | 0.25 |
| single_line | 31483867 | `57f6fa0769dac7dbd8a2757a195945c62aa5bf6681f723fb7a20b56f6f041ae6` | 181.0 | 179.5 | 0.25 |
| single_line | 31484784 | `58e5a0d8102e4fd7c8bd0e06c44cfbcc31f0074ba32265a42627469bba555626` | 112.5 | 111.0 | 0.25 |
| single_line | 31484583 | `590cbf7b0e7c983c0c940dfb5a64d134ec476bc153e6c643989bba3a17eb764a` | 130.25 | 129.0 | 0.25 |
| single_line | 31483881 | `59a69164137c78bbbc460c716b6be22328dfe8130b04809b7be5dddc5a20e3c3` | 178.0 | 177.5 | 0.25 |
| single_line | 31484824 | `5b3c0b333dbc33a572f0008cd06792a05093d796cf635302a991a663be12fc33` | 108.75 | 107.75 | 0.25 |
| single_line | 31484608 | `5b52c27bc378d633dba3b59083e0fa0933896e244dfa63a7ca1eb3879baaa2c3` | 128.0 | 126.5 | 0.25 |
| single_line | 31484478 | `5b98413892c95153eb7a1479f17d4ccd7531269bb151745bfd3efd744ca14565` | 140.5 | 139.5 | 0.25 |
| single_line | 31483882 | `5beac334b6d432e95511ad71052b35845081f999dfd3fd88c116f310b00dc5c7` | 177.75 | 177.5 | 0.25 |
| single_line | 31483838 | `5c0c84fc8b7de4d5bdb7c7e3b320c3c8b1c2836ae91b1f8527fbea4006de0c47` | 185.25 | 183.75 | 0.25 |
| single_line | 31484702 | `5d38e28f29af59eae78a303b87adf76804a9487fd69f5ecf8f3d10cd7d216899` | 119.75 | 118.5 | 0.25 |
| single_line | 31483942 | `5dfcbf4b763eedc3944102c8db8f0a0fdaadaeb264c8632b5eaa58210d8806c2` | 169.5 | 168.5 | 0.25 |
| single_line | 31484844 | `5eb8aea4bd950070b2e63f94d47748a2fde8c6003c31284b2d84e219ea24781c` | 106.5 | 106.25 | 0.25 |
| single_line | 31483981 | `60d74c02096f1ec64ee64436337014c561ed8ac42ba1683107d5d6e5149e1c0a` | 163.0 | 161.75 | 0.25 |
| single_line | 31484463 | `614545e4efc2dda671c943102000b830e32c0fb7228262803ebea7ab7b8222c3` | 142.0 | 141.0 | 0.25 |
| single_line | 31484870 | `6246db3f8a6210a2a89b8d9b97c147031734f42c817b40c98f11b763820f322b` | 104.75 | 103.25 | 0.25 |
| single_line | 31483779 | `62fc7d9b86fe71be0a28ac43e10e0dd2acc0eb14f74c1050c28f9c7283e78f0c` | 192.25 | 190.75 | 0.25 |
| single_line | 31484496 | `634e4f6072aa134e5339c83d74d1e03693289ebb868c5efc19a4b74c62a75096` | 138.25 | 137.25 | 0.25 |
| single_line | 31484374 | `64049566ec338a37a534ff0b4f7cc82c7deeb1871592c5816efa8830f959e477` | 151.0 | 150.0 | 0.25 |
| single_line | 31483786 | `66cc8722036c22641995225e8a4d3cdcd547ea0bfaeb9ed9a0f60255413a4819` | 191.0 | 190.25 | 0.25 |
| single_line | 31483759 | `66f5ee086f1e049b247c1a243045172c4fc3df9bd1cada982dd68f0c1c8d4226` | 194.5 | 193.75 | 0.25 |
| single_line | 31484675 | `67ab5264f762de1d5bedbe4658039646517408ae75bda65ae3fcbe125b4d0a60` | 122.0 | 121.5 | 0.25 |
| single_line | 31484557 | `6883ed3670c3466308f778f418dcc0e430c135af61bccd5faa4dce79b7d608e2` | 132.5 | 131.0 | 0.25 |
| single_line | 31483873 | `68866ac3135a3bea4c213f6696106454a25fa817a4634d427ea47f76f791bc44` | 179.75 | 178.75 | 0.25 |
| single_line | 31483824 | `688add04b140fe5b3f263909a8885193062948976db3acd273410231dd32f8cc` | 187.25 | 187.0 | 0.25 |
| single_line | 31484741 | `6891d7b0ddb7ec0d40028ae63de62602c1ea940c128197662278bd92ebf93251` | 116.25 | 115.25 | 0.25 |
| single_line | 31484281 | `68ddd3a8cc2903ec46390cfcf614d5b677779cfccd10f44b6565cf66f6869578` | 154.75 | 154.5 | 0.25 |
| single_line | 31484842 | `68e4a834f2df8731289517c34162ea00e4f96d5ed49befe452fa9bc2afb4646c` | 107.0 | 106.25 | 0.25 |
| single_line | 31483781 | `6a595574012c2056fd3a96d38b092d056cbad1d2a54254210778ea8bfd70506b` | 192.0 | 190.75 | 0.25 |
| single_line | 31484477 | `6a93daf2b8ad48922530ab71abc489b42c73243aee8ac679b9ef778065adf24f` | 140.75 | 139.5 | 0.25 |
| single_line | 31483804 | `6af6991e0506caecb505033bef5a6b5effa49f9a97ae01d17195d1d7ded50e59` | 189.75 | 188.5 | 0.25 |
| single_line | 31484893 | `6afc815d0d218903290321526eb5c4f0a2b1238a2371b56203e5bc7c5e0dd536` | 102.0 | 101.5 | 0.25 |
| single_line | 31484672 | `6b6b5ef143f053d07e4bb7f4d272b02f51f59593e97a8a947bc70d5f652c4b8a` | 122.75 | 121.5 | 0.25 |
| single_line | 31484279 | `6ba496520227e175ee13f53cc8170f6a9019d72f14aa1e01b9591765af984286` | 155.25 | 154.5 | 0.25 |
| single_line | 31484338 | `6be638982eb2a622b8f63987bc9d0683b5fb50d671353dc13581cc8f259c2e2b` | 152.75 | 151.5 | 0.25 |
| single_line | 31483934 | `6d8534bd21e33d555fbd68b7832133c6b6140db5211842843c170872985cafe0` | 171.0 | 170.0 | 0.25 |
| single_line | 31484676 | `6dec56b13a700d948a232ce5e38749609b9ffe6aa0943c4564b041db76f6c6fb` | 121.75 | 121.5 | 0.25 |
| single_line | 31484911 | `6e3b111057d92b227f3de6110e6d866dae28187e5009ed9280674e7c70d86e34` | 100.25 | 99.5 | 0.25 |
| single_line | 31483753 | `6ea6255d3bc6e3b4a99747d3437db4a5d73f32a69c343ac368099736ac6d0a94` | 195.75 | 195.25 | 0.25 |
| single_line | 31483910 | `6fba63bbfbac803ee7f18cf1fa89ba1d73966cb523c0f34f0cd42220fb71049c` | 175.0 | 174.5 | 0.25 |
| single_line | 31483855 | `703770d36c08b160d6aecbdcd8d2adf2646d1f5d5d3433d5b9b90093b9a8aea4` | 182.75 | 181.75 | 0.25 |
| single_line | 31484637 | `70407b2ea34e1031a9d0fc607b75b2b5f90d0e4e4ccc5ed8b1aeed8eb97bb676` | 125.75 | 124.5 | 0.25 |
| single_line | 31483963 | `7150a6252f2f3a24bd5e2c243a26ca71a23c70cb077124b00843a54bbb4b180c` | 167.0 | 165.5 | 0.25 |
| single_line | 31484720 | `727f872f9da5238fd37289f17bf8b91028ad23bff7f954cda6cfcdb43cc038e6` | 118.5 | 117.0 | 0.25 |
| single_line | 31483811 | `72e7ffff5a9a081e810815f528937d873fc6a93f8d24a50e8c6e45775be41b9d` | 188.75 | 187.25 | 0.25 |
| single_line | 31484600 | `72fd8b2cf519d54c5a0948a52cac5a132415f862572e75e8d38133a85195fdcf` | 128.75 | 127.5 | 0.25 |
| single_line | 31483947 | `72fe5d92c604e54974f74856ff7ba250998d79a65812d104a8f621c7ebfe0eae` | 168.5 | 167.0 | 0.25 |
| single_line | 31484012 | `730e64a4ae9a1977f8bc743b93bf188f59a13cf8e3fcfaf6795188b90e706c34` | 158.0 | 156.75 | 0.25 |
| single_line | 31484910 | `740693eab2c4d820727593d269fb8e0f383cf9623402da4b92dacd8f1d35a451` | 100.5 | 100.0 | 0.25 |
| single_line | 31483844 | `74929912ed083617ae3914b188d7cc3345a227c275ca27b60916ba0c5eed86f2` | 184.0 | 183.5 | 0.25 |
| single_line | 31483926 | `77063674a8e81e9a8f36b80fb69fabf79b4b59f86e9c20022e32c45bd1855e9b` | 172.25 | 171.5 | 0.25 |
| single_line | 31484807 | `775241567ff798b72f5b4e43c6379127bb9b8bea0058a59a5076863597f465cc` | 110.75 | 109.25 | 0.25 |
| single_line | 31484835 | `799dbde46a02a94f6b73264665fd333c8bda1ba9da11dec713c993ba41718ac4` | 107.75 | 106.25 | 0.25 |
| single_line | 31484435 | `79ccce67f309b0e86e9cfa4373780893b9d2a5b1df11728a112255931e962a00` | 144.75 | 143.25 | 0.25 |
| single_line | 31484461 | `79f3d6c454557b05f5925514eb51c3925581cc6113862527ab8581a9b5717011` | 142.5 | 141.0 | 0.25 |
| single_line | 31483989 | `7ae6d189ee5c58c3a4f5378179749a2d2b1a927651168e02d5ef56182ab94ca2` | 161.5 | 160.25 | 0.25 |
| single_line | 31484568 | `7be03a726f7fded93433acdac41ee5df899013642bfabe19e64641c0500dba3b` | 132.0 | 130.5 | 0.25 |
| single_line | 31484734 | `7c21694d5e3b66e83327664259d69cc135fa194ccac8008322eb2969ccc5e99e` | 117.0 | 115.5 | 0.25 |
| single_line | 31484002 | `7c991651465357ea64116223eb541ce09a4408e9cd503408703e0a7a28c71b76` | 159.0 | 158.0 | 0.25 |
| single_line | 31484897 | `7d60eeb5a9cc699485d3538aa3f0d16b3e441a6f32120a4d7067e2a5732541d0` | 101.75 | 100.25 | 0.25 |
| single_line | 31484386 | `7da7f6917784e13df76bb7dc8a4280d148ea83b6c48131863b42b72028176286` | 150.0 | 148.5 | 0.25 |
| single_line | 31484767 | `7e0e99f167c392091da0a3b19f8a2d0dceae7cf23a7186d93b77f8eca7740c10` | 114.0 | 112.5 | 0.25 |
| single_line | 31483745 | `7e14dcf0e32ce97f99e72ce18ed9361053ef176faaee851d9875ee68dbcd3015` | 197.5 | 197.0 | 0.25 |
| single_line | 31484382 | `7e5223d775ee708cff2c7daa516e169bc0c4e6c00332b693b5bc7890849f23ad` | 150.5 | 149.25 | 0.25 |
| single_line | 31483987 | `7e7e41c3a3f9a9beff7943cb4d863a9603e07e0c0d65cfcc08a19de012a8084b` | 161.75 | 160.25 | 0.25 |
| single_line | 31483742 | `81a6f2ca517b8f7e73b720e66c84bdea0264184a2f31467e5ea3d2fad8170443` | 198.25 | 197.0 | 0.25 |
| single_line | 31484903 | `8259f5a8b5e04bc0d784e85784467d9400844996f61a7cde92d304e9384dee4f` | 101.25 | 100.0 | 0.25 |
| single_line | 31484503 | `82bb82f10fc8c81c0a9e0e3117d3e6bfa1e0e3315244c990f9ef54206cd40b6e` | 137.75 | 136.5 | 0.25 |
| single_line | 31483978 | `83b4d3e1db1fde5b0e5e5356dd6d86c13d6b21a14af9ba508ae86332b5b9a96f` | 163.75 | 162.5 | 0.25 |
| single_line | 31484576 | `85a4a0c80c1c914ee397e35459090093785c77486d90710c2d8505885c4ed5b6` | 131.0 | 129.5 | 0.25 |
| single_line | 31483820 | `876248ea27a4242b949684ee9125123b60cf4cf7f33f4979af4501c8d3cc794b` | 187.5 | 187.0 | 0.25 |
| single_line | 31484619 | `88050d63c5f551ccf21d29135e81963fa4342990e1c85f055662c40db2961bb4` | 126.75 | 126.0 | 0.25 |
| single_line | 31483854 | `886d48fff406e3f024ba57c8e93e9a650401d59a9988507e68a70afc599b7689` | 183.0 | 181.75 | 0.25 |
| single_line | 31483802 | `88a0ad158994d7e66a37b244345dab737495d0b6079ffb94967918c19b02adef` | 190.0 | 188.5 | 0.25 |
| single_line | 31484778 | `88bcd5b846925e949e3cdd0fb265db5c7dd263c369582e956d248e78c2cc3928` | 113.0 | 112.25 | 0.25 |
| single_line | 31483970 | `898e56ef5b383485af1d06eed0d9f3612d4bfb412f4fabca98924e79726a4dca` | 165.25 | 164.0 | 0.25 |
| single_line | 31483840 | `8a2f0cf4ef663071d0dca8af7ea958cb058b78eb3b42060f88354752019c8f25` | 184.75 | 183.5 | 0.25 |
| single_line | 31484491 | `8ab19457e177ce26264176086aefa8596567498c5f730e444400d9ec40e8aac9` | 139.0 | 138.0 | 0.25 |
| single_line | 31483917 | `8acfe86b956435d647d600e9acaaaa1be6d4deba7b275576615ed5ae67c1f694` | 173.5 | 173.0 | 0.25 |
| single_line | 31483828 | `8b472f62e88f07ea6bd54db9c610417edb10c0a3f6c52b20d473e0c66c0cea50` | 187.0 | 185.5 | 0.25 |
| single_line | 31483767 | `8c1880d112d914a094770a0f961abe865dd69a8d0100e55bc7cb19f21c0824e3` | 193.25 | 192.25 | 0.25 |
| single_line | 31483908 | `8e0731f7b20a3be9897514bbf4e1df0c526f4bc46d27806eff6c1c42b1e6419b` | 175.5 | 174.5 | 0.25 |
| single_line | 31483994 | `8f4e6488211cabb9eb16fd3e7e05a5e7988a98ec700941aee81cc91c7ac53a14` | 160.25 | 159.5 | 0.25 |
| single_line | 31483807 | `8f6a5585e9b63132d7446f771df00709b76b035be7d9b1bc73f634913b52a45d` | 189.25 | 188.5 | 0.25 |
| single_line | 31484541 | `9007ecec6877e4a31f1bd64fe123c76eb712d03c10cd728d3ef0837721873f48` | 133.75 | 132.5 | 0.25 |
| single_line | 31484823 | `909c4218bf244b564b8ff891eeab2ec7e2ed9e6eadffdd719e130430905fb3d3` | 109.0 | 107.75 | 0.25 |
| single_line | 31484004 | `90b90d187592645267bb74667679dd4a8bf8669731b0705803f17b55f5694d8f` | 158.5 | 158.0 | 0.25 |
| single_line | 31484793 | `9136d8ee2b424eb506f833cb81bfe7dc23c3bcc14ffb41a28c8c2892da85214b` | 111.25 | 110.75 | 0.25 |
| single_line | 31484721 | `915715bfd6f3ed5d594dd5458a2603fe40be2c8e463dcea848cef8d27697a7fd` | 118.25 | 117.0 | 0.25 |
| single_line | 31484405 | `922c212fce67a05bb9646d7ba5c6286c883ce5e5c78d77a503116354c075af72` | 148.0 | 147.0 | 0.25 |
| single_line | 31484615 | `925e516f5be80bfe7a810eef644a894fde46391a371c365a94a03c0520bfecfa` | 127.25 | 126.0 | 0.25 |
| single_line | 31483842 | `929c7e553ff7027b0cc246d4bcb03132d1d64ed5095aa86d950f5f47b3e0fc4a` | 184.25 | 183.5 | 0.25 |
| single_line | 31483863 | `929cbba606d8a365b9900d0c295b0943a965413fd1fda8c8e2ed61da1c53bb59` | 181.75 | 180.25 | 0.25 |
| single_line | 31484919 | `93810b8abd29b569cc4d24a52cdd42b36d8605ebb0e3b9edf755c9bbf22455b0` | 100.0 | 99.5 | 0.25 |
| single_line | 31484427 | `93c0c8745ca4070964c3a2f42f3d1e8fa91e93eec4b4abe2c42d91202296c809` | 145.75 | 144.75 | 0.25 |
| single_line | 31484709 | `93df21e4d4272017960b24011c5ac35cc68663fa0c90fa54b1851f3a19c74c02` | 119.25 | 118.5 | 0.25 |
| single_line | 31484671 | `93eb6b301ba6339f7193de6682fa82ab12fa783538f4659c42c791de1ccfc4ed` | 123.0 | 121.5 | 0.25 |
| single_line | 31483871 | `93ee3229943fb8b97484f24d6537da7756ae6860ab8c8c7dd352b12079ff57d8` | 180.25 | 178.75 | 0.25 |
| single_line | 31484584 | `9476935414adfb44926d0f69fa67f26e956c594dd052957bc0b3617a215839c1` | 130.0 | 129.0 | 0.25 |
| single_line | 31483916 | `9563553e2e1ad0514378e321ef573b870f6f5ff3864882f7825ceb1809caf273` | 173.75 | 173.0 | 0.25 |
| single_line | 31483924 | `9585bc334527a320ad674ab9b9934eb28d5486f1a40779470a427aff1f60d282` | 172.5 | 171.5 | 0.25 |
| single_line | 31484724 | `95ab0cf9939ae927f145b9f642825fdef270a82dc7edfa1d172652b6a755305d` | 117.5 | 117.0 | 0.25 |
| single_line | 31484638 | `9736d603f7212d7a1e1c64ebad746abfc25f7e9646324c6ca1caa7afcb1af9ac` | 125.5 | 124.5 | 0.25 |
| single_line | 31483901 | `977a5a46fc721bb42d72b6798d002861431f35c3a5824bd594964f361770f5c8` | 176.5 | 176.0 | 0.25 |
| single_line | 31484526 | `97992f44b8a655fa8d9a51f34e458d4536365f0fe88c9da6a96995c37d9400d4` | 135.5 | 134.25 | 0.25 |
| single_line | 31483856 | `97d0a064b8740f928bf26bc896f7586ec6efa7f4942cadc5c35801c5309572fc` | 182.5 | 181.75 | 0.25 |
| single_line | 31484000 | `9837cbb44e213e714fc2685f9bb675f2d69b85809f7a2f287725e050272a1c91` | 159.25 | 158.0 | 0.25 |
| single_line | 31484777 | `98a363ef451d0c00e65f03645a17694123cb372a1c9de069a046a8bccda487e4` | 113.25 | 112.25 | 0.25 |
| single_line | 31484838 | `99cdf4ecf4dc26b983e89f731ba78ef1164f33642a2068b7e6ba4658c0812d52` | 107.5 | 106.25 | 0.25 |
| single_line | 31484792 | `9aaa0f9f28d0e4fa37ed28a6794ab9bbdb5264543e162a437f2d86c5d780c24f` | 111.5 | 110.75 | 0.25 |
| single_line | 31484494 | `9aee45618324fa30e91bcc944a0ac5bbc5286420d072815d58408c029cb6367b` | 138.75 | 137.25 | 0.25 |
| single_line | 31483986 | `9e30aad0f0e7ab20eaf00ebedb95aac3664e44031e367b151a133401a16e46e4` | 162.0 | 161.0 | 0.25 |
| single_line | 31484809 | `9e3555e0b66cad164aa032bd65af2c32008ec1069ad4bc07979011f2e64f1632` | 110.25 | 109.25 | 0.25 |
| single_line | 31483898 | `9e3fad2f653eb3cfb9a8a6486410ce4be1f1c80041741516d1735520574f0a43` | 177.25 | 176.0 | 0.25 |
| single_line | 31484419 | `9ec65af7fe12f2f1923aea9bf0a7f78dfd6335d7751fed97dfc6fffb6cc073b9` | 146.75 | 145.5 | 0.25 |
| single_line | 31483906 | `9f4251499b014717ce2a176f927e08f8f23b77ddfc5e48b9cd95e92f4471309f` | 176.0 | 174.5 | 0.25 |
| single_line | 31483907 | `a0b0c08832d4ab05ac6100fe4de913bad0f893d5dfbefe4dcd3fa188931bd393` | 175.75 | 174.5 | 0.25 |
| single_line | 31484399 | `a11c5859a29eadf310b5f47c05fdf855f3a9828d3f6c1ec53e7ccb6068d8e967` | 148.75 | 147.75 | 0.25 |
| single_line | 31483762 | `a22191bb81c21cbc243740ce75acd425fd7c5d8bdaed143cc199441ffee9bca2` | 194.0 | 192.5 | 0.25 |
| single_line | 31484519 | `a24bdaf5ed68a874cc873d8fab904de192fd433955d18ce2ec1b9e6b0460e0c0` | 136.0 | 135.0 | 0.25 |
| single_line | 31483984 | `a255b6ff859de05845ec71bfbc54c63c329f9cd9225f6c24da0757928ea6f313` | 162.5 | 161.0 | 0.25 |
| single_line | 31483995 | `a3b067fd889fe45a1686bd77cc2bf24726d69a7d1080069a6321c6e56b23c575` | 160.0 | 159.5 | 0.25 |
| single_line | 31483730 | `a3ca75d07a0fcbca69a2800a7a5977444359589c1d8cc83ffeffe58ba2f71cdb` | 198.75 | 198.5 | 0.25 |
| single_line | 31483879 | `a3d5eccad208200ada6f0d0b64348ca32877f9aa0f1f435905c974cbdfc74091` | 178.25 | 177.5 | 0.25 |
| single_line | 31484722 | `a46f1addcef658530a207fdd2d430f19e075e02f043eafff012626eea746c39e` | 118.0 | 117.0 | 0.25 |
| single_line | 31484859 | `a57a82f1a0a32189ab77bf7bf1537acd371dae5ad1e8e5b638cac8e96b0bd449` | 105.5 | 104.75 | 0.25 |
| single_line | 31484410 | `a5957e6a84729f5d84edf4fbd65a3791df6185d9cb5de5c09f4144c1a19d81e2` | 147.75 | 146.25 | 0.25 |
| single_line | 31484902 | `a600261682c4ce07ae6e193a1c6dcf6d33f7c6dbbe577350ddd1b4aa1d4a111e` | 101.5 | 100.0 | 0.25 |
| single_line | 31483870 | `a6dd5a4c4ee4a9261476d16b8d6f4b48ff67c33fe1b3f2cc84e0352a18580632` | 180.5 | 179.5 | 0.25 |
| single_line | 31484444 | `a7f8de9a8d5cd60fdaed8f691bb1a7e05cb5dd4a43da60460ef7b54e333fdbbb` | 144.0 | 142.5 | 0.25 |
| single_line | 31484673 | `a87f698442c452b38e6f2fa84619f6c287e7c63ae194045b44f65e804e9b7b35` | 122.5 | 121.5 | 0.25 |
| single_line | 31483866 | `a8be20cabcb4964e960ebe44ce6196290ca9a696be93dcbc3e39d70f35b963a6` | 181.25 | 180.25 | 0.25 |
| single_line | 31483923 | `a93e39cf86c59cc2b0727421b5c6ccaef47ecf9198b20e63359e2c9a46471139` | 172.75 | 171.5 | 0.25 |
| single_line | 31484723 | `a94080f7947fed249b552e3242fdd34a061331de2098b664cd85212afc4d5222` | 117.75 | 117.0 | 0.25 |
| single_line | 31483756 | `aabc14a997b1f98ed5a71ed5de46f8b7ee46565c9f140210eeb3f28f319a9e05` | 195.25 | 193.75 | 0.25 |
| single_line | 31483927 | `ab14b0afe9efd2379ef597ebae67739167bd09cfcaa3e5afc3b4be661a37fb2a` | 172.0 | 171.5 | 0.25 |
| single_line | 31483743 | `ab5578931e56508278eb771a65c73c04a29de86ef1a3cdfe4e8d07563c0f78f3` | 198.0 | 197.0 | 0.25 |
| single_line | 31484578 | `ac1922cb6b3ec4db0e76a228b64f9fe8e4618759f76ebd4bdfc93a105347a17e` | 130.75 | 129.5 | 0.25 |
| single_line | 31483966 | `ad08892d88f3a11d646b2fbc07b4804f7b1ea5affc3e8035bd98afacc3d7f52a` | 166.25 | 164.75 | 0.25 |
| single_line | 31484904 | `afc95c026ae56d67d4f4104a219fc93016c69f8a174f254c763f54218b993128` | 101.0 | 100.0 | 0.25 |
| single_line | 31483785 | `b0123395c3f486cb3a51d2b64928ea642ba5a92f6a287b307d3eaf87fee84844` | 191.25 | 190.25 | 0.25 |
| single_line | 31484790 | `b0b8e7e50e2c7a33b646bfed60091c1dd1fcfd9b6ec2ba8b90cb5816eef4fbcc` | 112.0 | 110.75 | 0.25 |
| single_line | 31483765 | `b22a8e6d9995f8b07008eb59dae678e72e7736ddfa5bb36e2dddf65d85aaf1e3` | 193.5 | 192.25 | 0.25 |
| single_line | 31484484 | `b245a6c732fb281329cb66c9a4f2d3fb1c5c4d5b6b8a6b2236ce17a11a777c2d` | 140.0 | 138.75 | 0.25 |
| single_line | 31483979 | `b2836857b33e37b889c353b554f80b3af33409b3b64e239dc0cfddb707afeb5a` | 163.5 | 162.5 | 0.25 |
| single_line | 31483950 | `b30bc4d0e1115a7e33049aef53520a73a35a01753558341e694793fac462054d` | 168.25 | 166.25 | 0.25 |
| single_line | 31483741 | `b33e9e1c713e7b00862371b9954e6f93ba9647a085ba0a5de087a2ec85ff38c3` | 198.5 | 195.75 | 0.25 |
| single_line | 31484351 | `b4fdd8b5096f65b3f5d77035dc1493288ff5c5c98171a279f8526fb5f5060215` | 152.25 | 150.75 | 0.25 |
| single_line | 31484757 | `b52b1f62a7f0b598917a6f895f1c7de21c88898b234c8a656a9db168b93517c5` | 115.25 | 113.75 | 0.25 |
| single_line | 31483974 | `b56dc0ee089ca0b37c24ac96d0d1af53a666bd9517eae4c34dd1c5520f4e2813` | 164.5 | 163.25 | 0.25 |
| single_line | 31484810 | `b61f5513aa3d7ce8d9d3ed61963d22df7dc20f1acc144c6b4518417fd0fc1c2a` | 110.0 | 109.25 | 0.25 |
| single_line | 31483749 | `b669f0787e903295729d304ff8813d15ce2d3064d0488f511ffce08e6961e042` | 196.75 | 195.25 | 0.25 |
| single_line | 31483940 | `b6818bacd88b9c4ea829ae2e41c4bc3b04df1d3d3624fa906e11de06edd07cc4` | 170.0 | 168.5 | 0.25 |
| single_line | 31483918 | `b6df007c99684177f34cdd176ac0a7a33a3b3f9056b3912418ca905fc6210934` | 173.25 | 173.0 | 0.25 |
| single_line | 31483944 | `b78864855ef3b0edae717fa21d1ff6c26dc731af2add04ab64f9c27ec925b794` | 169.0 | 168.5 | 0.25 |
| single_line | 31484570 | `b839c04f514d9903f6d44c46dc3158180e872678b17d6a9ad12e5c699f117098` | 131.5 | 130.5 | 0.25 |
| single_line | 31484014 | `bab99d1750e52fb7622bc2224c5b4e03b0565acfaf4cb3c3ec0962bb58463e37` | 157.5 | 156.75 | 0.25 |
| single_line | 31484412 | `baf5d820cb0e10d7346aa68f6553f60dcbf2b1496a2775a3f8c2964ef577d625` | 147.5 | 146.25 | 0.25 |
| single_line | 31484857 | `bb940d7310d332582e24e0a20fb88c0eb6479fe19d64d2da3a89e70e4580cdfb` | 106.0 | 104.75 | 0.25 |
| single_line | 31483902 | `bc2a492f46ee155a3cf80364d66615a658e95bf9a421d6c6b6543b9768f17bbe` | 176.25 | 176.0 | 0.25 |
| single_line | 31483955 | `bc3a90bee534dfe317623f9eaaedfb13388bc0f034381801f4e5dda82d05a844` | 167.25 | 166.25 | 0.25 |
| single_line | 31484518 | `bd0d08d31edd80630849ce249ffd509424423df60971cbc78e237cec8b9a5583` | 136.25 | 135.0 | 0.25 |
| single_line | 31483992 | `bd19eee464f532233aa4ae4191266bbf39193e6a3759a293c339e3136a7b7d67` | 160.75 | 159.5 | 0.25 |
| single_line | 31483915 | `bef618283c54dbe2fb0b1099d6a8fa43024ace126180e9ebbb9405f3c484e6e5` | 174.0 | 173.0 | 0.25 |
| single_line | 31484636 | `c0e1f0cfee5d6bdc42b5b84bf9c833b8a4971af37730416752e67b214c3f789c` | 126.0 | 124.5 | 0.25 |
| single_line | 31484593 | `c13b420919c80f2afdbdfc265ca7b4004b644916eaa7432a82560c84cd33e29f` | 129.25 | 128.0 | 0.25 |
| single_line | 31483833 | `c1c074f13194efb412e16dd1ef037c52cb6be5e840a16cfc3c8921bc169353fd` | 185.75 | 185.25 | 0.25 |
| single_line | 31484791 | `c1ecdbd8dedb253eabbc16bda778ef0935b1f478c58097011b30f521792f79ec` | 111.75 | 110.75 | 0.25 |
| single_line | 31483784 | `c2873a7606cac1aaa20e0b46e4e4f3271dc85beb591a1743cc7b04bdae94538d` | 191.5 | 190.25 | 0.25 |
| single_line | 31484441 | `c2d0b286fba4c5df3484582b47ba1bd752efc2fbd2ad3a114e4df5e36eb79352` | 144.25 | 143.25 | 0.25 |
| single_line | 31484586 | `c319428e29c3d36583f99944ed2689735bba8b3ee94e911b5b9f5b6b2c694767` | 129.75 | 129.0 | 0.25 |
| single_line | 31484445 | `c35e72183011262bb41358ca5051e7ceabee823602a97f600c2a6dbd86a55c8f` | 143.75 | 142.5 | 0.25 |
| single_line | 31483876 | `c45e609caf2c62613bfa5b1d9cbf2e3ac9eae8d9d49783f1f88cb3d77ab6bec7` | 179.0 | 178.0 | 0.25 |
| single_line | 31484660 | `c503ab63db64ac66ad40d4e1d092f995331fd19d6be134c01ac8f64cdf1b7df2` | 123.5 | 123.0 | 0.25 |
| single_line | 31483928 | `c509c72a43fd687e2915ade7dac2b36c5d63e8d3c1344031facf84f8896fb93a` | 171.75 | 171.5 | 0.25 |
| single_line | 31483913 | `c57d446fe05c600534922d9e21ca362c018b36ec7d272323aae7e39dc28dff8e` | 174.5 | 173.0 | 0.25 |
| single_line | 31484508 | `c5d053b86aaba0b2e5250e5e4253c268a40371735ee0fc62eed89cdc9d20cf23` | 137.25 | 135.75 | 0.25 |
| single_line | 31484418 | `c5f36f6b5281805f3e1068978f7c04b9981eca5e351ab471f82be7c83b36dbef` | 147.0 | 145.5 | 0.25 |
| single_line | 31483760 | `c622c68267cbe650ba8e70245a8b7e18e8dd6a3880d0478fb31623394497b697` | 194.25 | 193.75 | 0.25 |
| single_line | 31483874 | `c7077f1d208f49b83e35ece5e047466e0724740ffc6e8aada359edfec7f5c7f0` | 179.5 | 178.0 | 0.25 |
| single_line | 31483875 | `c767fbfaa2d129ea0f6029719d6fabc6b8466d89f6500e432953255fabc8d29f` | 179.25 | 178.0 | 0.25 |
| single_line | 31484280 | `c777bb84509df23873c40eaa747dde12ccf40f8b36398b1ffba5cd01b656f0b7` | 155.0 | 154.5 | 0.25 |
| single_line | 31484404 | `c7913724c37e97e4225f88c4b1eab4391b92142a83a51c2ef861524e19749219` | 148.25 | 147.0 | 0.25 |
| single_line | 31483935 | `c79d7ca18cc512f6f540509a8ff17d128e536c861b84d77206b7069d44c94df5` | 170.75 | 170.0 | 0.25 |
| single_line | 31484490 | `c8637799a77a6d2046bdc2fcef413cda194b2d52d32b465b84c7236a0b771f87` | 139.25 | 138.0 | 0.25 |
| single_line | 31484313 | `c984fc613ab95d8d96d30f57ced30da9befd57e79854b20416c4f1f4ddc2f649` | 154.0 | 153.0 | 0.25 |
| single_line | 31483975 | `ca363221684b61c08dd9982759d38d783f69fe55a0cb2afcf20a5b320ca0676b` | 164.25 | 163.25 | 0.25 |
| single_line | 31483834 | `cbf3788ca051285b025d163ea468ffade8836b63f06eedd6fd7c0b42cc3c20d4` | 185.5 | 184.0 | 0.25 |
| single_line | 31483954 | `cc8556e6e7580a3b60598fab7bbdb55fb5603b642902c96e7c493b595d9074f6` | 167.5 | 167.0 | 0.25 |
| single_line | 31484920 | `cd45f32418b268ca6b02709c722f0e00080f40ff6aee3d0add149dce968a00f1` | 99.75 | 99.5 | 0.25 |
| single_line | 31483922 | `cd7aed2490a6c167aafa62fdf7727e3fce0e7a2b991f68f2e657c8047fbb5482` | 173.0 | 171.5 | 0.25 |
| single_line | 31484743 | `cdce0e24e65cb83ebd88dda4849c29d1a65b30e8be5d12e3dca046e3311998b0` | 115.75 | 115.25 | 0.25 |
| single_line | 31484397 | `ce9cf53d67aaf15210c33a8079c40e9ece0e088f2a13a5ac42bb2e6f105e38ba` | 149.25 | 147.75 | 0.25 |
| single_line | 31483772 | `cf2fd77e6d613ee085bebeda90820c5a204581bf5da4af63c37d10664eb120b5` | 192.5 | 192.25 | 0.25 |
| single_line | 31484820 | `d16dccc6e3a69a536982611711b9c7d4698b2015ffa32540ef98b1521dbeb2aa` | 109.25 | 107.75 | 0.25 |
| single_line | 31484325 | `d1836203593d0ef4dc68c970b044dba94154ecb0c15780cd123303f5b2da4c25` | 153.25 | 152.25 | 0.25 |
| single_line | 31483932 | `d4c4a8352ad7e5a0838851515b9e599b25685cc6f594513e6f5c42f1732a495b` | 171.5 | 170.0 | 0.25 |
| single_line | 31484370 | `d50ab9b9ca12e593a181c3bb091bb34a2e02eb37fbb64e0af16431bf499aae64` | 151.25 | 150.0 | 0.25 |
| single_line | 31484005 | `d51801bb5b2388590f78facaf24a47837becfdc61f10ad4cb8b963c411ae0482` | 158.25 | 158.0 | 0.25 |
| single_line | 31484495 | `d52a644cf3e966383d726679b5dde45af13d9081c19d9713170d6612c875cb79` | 138.5 | 137.25 | 0.25 |
| single_line | 31483899 | `d5a207a3648d2d53def136c3951050183a0ce4aaed1177ed7f52684bac5d7352` | 177.0 | 176.0 | 0.25 |
| single_line | 31483967 | `d645af7ac5dfdc09ecf510bb9edb674c71aad8949fe6d5f5e791cd5ebf355a3c` | 166.0 | 164.75 | 0.25 |
| single_line | 31484826 | `d678a7a41e207d43a455fd2905e19215d0cfa9766051a113342700b7ab6d9c5d` | 108.25 | 107.75 | 0.25 |
| single_line | 31483791 | `d70b73b35e23c765aea8c63002b808eb6907cd0ac7527117eb673549f572f4a2` | 190.75 | 189.25 | 0.25 |
| single_line | 31483815 | `d77e1e2d0670c3105adfdd9549e93acc69c9fd41581d64daaf00a91e2c3af038` | 188.5 | 187.0 | 0.25 |
| single_line | 31483980 | `d7f3c79be974a61718d2b35fe26f18832294a0d5d5cbd2277cd273e91e760a54` | 163.25 | 161.75 | 0.25 |
| single_line | 31484775 | `d8473ee8c06f50212b7f6083ca2a22ac942385987acd89e0fc4c0e0f444413e8` | 113.75 | 112.25 | 0.25 |
| single_line | 31484906 | `d9d3ee6a99bb95ad4ac4671f86bbd3c79f96618fa7011b4cfe2509d287334b6e` | 100.75 | 100.0 | 0.25 |
| single_line | 31484808 | `db831deb17fc1ad62690782e61d41fd03117e1852ff9dd1a74b13fffc8c5ebf0` | 110.5 | 109.25 | 0.25 |
| single_line | 31484420 | `dbc24a8e950666b176d00371e572108a2d3a74aed24b37f962e296074ce70497` | 146.5 | 145.5 | 0.25 |
| single_line | 31484413 | `dc7584704dec14fa30d087c5f8c5c09b8d4cf6e5688a05b6975c1ff6dba3e2ca` | 147.25 | 146.25 | 0.25 |
| single_line | 31484874 | `dd2786e4ca632f13862c64cddb49415683c487551478e1d1ecdbcfb5086ea84c` | 104.0 | 103.0 | 0.25 |
| single_line | 31483914 | `dd4a49a1b845ec5232cc634cb58965cd1496e83bc4267cfa0b2f64c7ab162ac9` | 174.25 | 173.0 | 0.25 |
| single_line | 31484317 | `ddb78707c8a57b873460f260a10f2b3c8b5e42ca2ccc27405e99299003cacf8b` | 153.5 | 153.0 | 0.25 |
| single_line | 31484504 | `de0cf3071e34dd5a4e32fb07084d7d84dbc921be816ef1ae9e8a4ff678197b27` | 137.5 | 136.5 | 0.25 |
| single_line | 31484453 | `dfdc733ba219f57e425d57554f7298d4e7b49643a1a61cf4b5a885d77bb2eb26` | 142.75 | 141.75 | 0.25 |
| single_line | 31483725 | `e0dea7008cad50cf8d0816eaf499bc60c044e58a8635374b9c2feb49bd7517b6` | 199.25 | 199.0 | 0.25 |
| single_line | 31484749 | `e180dd60df2e7b751504a9f0fd75de5193d305c7cdb18e1aacd636040cf380f7` | 115.5 | 114.0 | 0.25 |
| single_line | 31484549 | `e1f00c13e2117ec62cde17fdaf57f58c3d2882b61f4d6af771447542ffa8f74d` | 133.5 | 132.0 | 0.25 |
| single_line | 31483805 | `e452b3534e60b76426fd229ddc3cca1a636c8c80faab3c4eee9ff4b24f2a3c24` | 189.5 | 188.75 | 0.25 |
| single_line | 31484779 | `e49ed749c16bbf4bf6153075b70a8a1ec07c4a5c6876a58e18607921cd240b25` | 112.75 | 112.25 | 0.25 |
| single_line | 31484891 | `e4e69f09bb2e51658bbd6428b2a16fdc88941a2baa820e590531bc5842f5125d` | 102.5 | 101.5 | 0.25 |
| single_line | 31484340 | `e56f534c8da3d3f12bfc9d7225245d26c0c51a3217d3fdd775004b288de7c69d` | 152.5 | 151.5 | 0.25 |
| single_line | 31484641 | `e7ceb005c204c7d822a571115046316983de8d45ba7cf703a8c120b315714c97` | 124.75 | 124.5 | 0.25 |
| single_line | 31484708 | `e8d30a6c983a54f1afc94ca639699473d67f9d8abb93139aae02f10425b22a9d` | 119.5 | 118.5 | 0.25 |
| single_line | 31484872 | `e8d8063a1933bd13919fd87aaf0653421d152f2a74a11210aae3f3adcf3c529f` | 104.25 | 103.0 | 0.25 |
| single_line | 31484535 | `e9d496a824c411c7a7c3a559099328f2eeddd81d8a9683150b0b1d61e73ae1ca` | 134.5 | 133.5 | 0.25 |
| single_line | 31484276 | `eb539947ca80b86e422a841b3f49b0b3734273dea1221381ff9b0b8169513d6c` | 156.0 | 153.25 | 0.25 |
| single_line | 31484759 | `ebbbf27dce8135d0c4044fcd0a465d9f0c6846e4ec6a661c792795a7beb58ed9` | 114.75 | 113.75 | 0.25 |
| single_line | 31484871 | `ebde467f555e1af6729d146acbbfc2d0b66697d2a3b5b9fedd861d28266d03f3` | 104.5 | 103.0 | 0.25 |
| single_line | 31483832 | `ed563b43cc0aaf17669a986d491808faf71c73343d8c0aac1b3343bf094e906b` | 186.0 | 185.25 | 0.25 |
| single_line | 31483770 | `ee8bf92c69c07cd06590c0b0097298ce8af55cc880ff1b2c4a52d74b2b0aef01` | 192.75 | 192.25 | 0.25 |
| single_line | 31484469 | `ee9ba0346d4efdf8bb73124a548b66141cc54bb91e9733e6e9d9f76f1e29530a` | 141.75 | 140.25 | 0.25 |
| single_line | 31484656 | `eed83bb5d0d79a8bf445ad2252fc8aa72b97d2e90472e141a3f95017ae65a4df` | 124.0 | 123.0 | 0.25 |
| single_line | 31483706 | `ef1faa03315aa9f682cbeae9bdb4f9643a46b8ec7c4643afceeb817bac7a3022` | 199.75 | 199.5 | 0.25 |
| single_line | 31483969 | `ef3a97c1213b4c2414484396d33d3aea192775dffa3cc6a249c4e0c880f28d83` | 165.5 | 164.0 | 0.25 |
| single_line | 31483999 | `ef3b5f72b1d4100929a2f0c4d76bd0316cb3425bf89d765e060384332c5a0090` | 159.5 | 158.0 | 0.25 |
| single_line | 31483991 | `ef48c19d3d31a183e534e202e8b6b03f3ee07b67b08dc602cb830079aee2bf44` | 161.0 | 159.5 | 0.25 |
| single_line | 31483747 | `ef5fed404c1311fc27445a5510b80821674a5c8e59dc8f8f157eb79866d744cb` | 197.0 | 195.5 | 0.25 |
| single_line | 31484760 | `ef92ca5659ec20cb927e736621634de6d1a4c93eceb0bbfaf63929cf29170401` | 114.5 | 113.75 | 0.25 |
| single_line | 31484451 | `ef9b03e2c64b2570dec180ad15f6e6c9d4e62b8d5e4210674f969b349a3fe35b` | 143.25 | 141.75 | 0.25 |
| single_line | 31484693 | `f096df42b5869ce937ee60af6955641a082a44553e1e956311f217cd8d2f443b` | 120.25 | 120.0 | 0.25 |
| single_line | 31483897 | `f2183505e7955a8902fb7890095cd2c84e143b66b095ca8cab190dab2cc86fb2` | 177.5 | 176.0 | 0.25 |
| single_line | 31484552 | `f2d24965310b90329b67d8048adb5ae8bd41db7188be91411196d15bcced0042` | 132.75 | 132.0 | 0.25 |
| single_line | 31483868 | `f3dc5afa121eafaa2e25f043911457ac130df06c4e8012242c022d2a75331992` | 180.75 | 179.5 | 0.25 |
| single_line | 31484336 | `f5a641342db4a13bcaa068a35e11c3de07b532f64e119c222697d58c47dcc5ad` | 153.0 | 151.5 | 0.25 |
| single_line | 31483752 | `f5b3baceabad940e16e9179dbc49f75e0892a22e0f3ff4bd4fc4a9c9ca52a4a5` | 196.0 | 195.25 | 0.25 |
| single_line | 31483757 | `f69d68f7a077c4365cd3dc64cbee665eed7917f177044ccc11caadfd9976cf33` | 195.0 | 193.75 | 0.25 |
| single_line | 31484878 | `f6b5a74a1017b645e4224e2781c128ed096fd4620eb80caaff1e5848417af117` | 103.5 | 103.0 | 0.25 |
| single_line | 31484562 | `f6d5cfa324b42160017eddb4489102b02e9fc7802a025206c879c6a6dfcc7013` | 132.25 | 131.0 | 0.25 |
| single_line | 31484551 | `f79fb8b2559931d9dcbb94e43ce89bebe09d133cc0a38905ce2346476a9f0dc2` | 133.0 | 132.0 | 0.25 |
| single_line | 31483758 | `f7c8b6baecdc12b5a4ceff9b5cc56a11098b4b04348937db2a58f0cff10b675c` | 194.75 | 193.75 | 0.25 |
| single_line | 31483816 | `f94d721f79a6481405a7f24119dd5c8d3413e676a5b213096ac0a72238ae17cd` | 188.25 | 187.0 | 0.25 |
| single_line | 31484550 | `f9872e2e5f853c93cbe7ac540b4bda171c8602a2a81001b9999b1f356225eea8` | 133.25 | 132.0 | 0.25 |
| single_line | 31484532 | `f9c11c6ef4d5f337eca322a3f7042efad90656def5c71b93bae53a30788e1e7f` | 134.75 | 133.5 | 0.25 |
| single_line | 31483750 | `f9f0ccc2980d920b8909ed8de99476fb56b4bc1b6311674a475c12fca3b5b066` | 196.5 | 195.25 | 0.25 |
| single_line | 31483817 | `f9fe7d240f5988b769361d8b6277f0eec09acf021bb49d898d8a79e06b2fb04e` | 188.0 | 187.0 | 0.25 |
| single_line | 31484383 | `fa2fe0b72d21f2f5de1bc1e052b8ede36676035f8f3ac96018fa1087f1243fec` | 150.25 | 149.25 | 0.25 |
| single_line | 31484812 | `fa911be121aafb714ba5010ab285f099c1a1a69537f468b86538729d59e8f195` | 109.5 | 109.25 | 0.25 |
| single_line | 31483801 | `fb0fc68784f313cbadb874c313678db9a950e5f5ea311942cbf0bca8aa77c299` | 190.25 | 188.5 | 0.25 |
| single_line | 31484387 | `fc071bd8085999a0e6218fc1b9d8d13f0eb8f3d6179d66fca1d069d03075ad79` | 149.75 | 148.5 | 0.25 |
| single_line | 31483943 | `fc8cead52632bfdc6eef5baadef5328040c7195a793e25132931540d75dcae26` | 169.25 | 168.5 | 0.25 |
| single_line | 31484483 | `fcbe8f2d334a9a14cb8d961a99b7363be85ab5458ca18b316fdc99a3711d0e90` | 140.25 | 138.75 | 0.25 |
| single_line | 31483964 | `fe1adaf011a04f55807463e5047c9c49ef9a4bb63a712485d55706ed8648f347` | 166.75 | 165.5 | 0.25 |
| single_line | 31484509 | `fea97449aed6ca65cd98b208cefc415de1a50d2ffce05099d52899f126752d7d` | 137.0 | 135.75 | 0.25 |
| single_line | 31484470 | `feec2878b98f6a22c0fe34e8000130409bba410229203cda9c1d1555e4bcf465` | 141.5 | 140.25 | 0.25 |
| single_line | 31484811 | `ff1b784b45ef05b621beff476fed69db40fdf297ad13b8ccd0b8682a5ea34e74` | 109.75 | 109.25 | 0.25 |
| single_line | 31484789 | `ff7b5d2c534d6478f0227a68ae8e87d68a8148573febb36d71739c0f35c83a8f` | 112.25 | 110.75 | 0.25 |
| default | 31484180 | `a3ca75d07a0fcbca69a2800a7a5977444359589c1d8cc83ffeffe58ba2f71cdb` | 156.25 | 156.0 | 0.25 |
| default | 31484178 | `e0dea7008cad50cf8d0816eaf499bc60c044e58a8635374b9c2feb49bd7517b6` | 156.5 | 156.0 | 0.25 |
| default | 31484177 | `ef1faa03315aa9f682cbeae9bdb4f9643a46b8ec7c4643afceeb817bac7a3022` | 156.75 | 156.0 | 0.25 |
| omitted_layout_probe | 31483728 | `a3ca75d07a0fcbca69a2800a7a5977444359589c1d8cc83ffeffe58ba2f71cdb` | 199.0 | 198.75 | 0.25 |
| omitted_layout_probe | 31483722 | `e0dea7008cad50cf8d0816eaf499bc60c044e58a8635374b9c2feb49bd7517b6` | 199.5 | 199.25 | 0.25 |
| omitted_layout_probe | 31483705 | `ef1faa03315aa9f682cbeae9bdb4f9643a46b8ec7c4643afceeb817bac7a3022` | 200.0 | 199.75 | 0.25 |
| empty_line_detection_probe | 31484105 | `ef1faa03315aa9f682cbeae9bdb4f9643a46b8ec7c4643afceeb817bac7a3022` | 157.0 | 156.75 | 0.25 |

## Bounded recovery retries

To finish the explicitly authorized catalogue test, the runner made one separately receipted recovery attempt for each submission with no process ID. The service reader never retries implicitly. Original attempts remain in `prior_attempts/`; a second recovery retry is disabled. Extra maximum-charge reservations protect against a late debit from the original unknown submissions. Any originally charged page is included in account reconciliation.

- `an-a73d22211479-p000141.mark11.r7item11`: one recovery attempt; [original attempt](transkribus_failed_lines/prior_attempts/4e2c48acad46e45a7e0b89fc72fc1a5059de94ac42a87a0a6efe9db019a22488.json).
- `s2-200e977f2dab5291c42c-p00035.mark78.r7item78`: one recovery attempt; [original attempt](transkribus_failed_lines/prior_attempts/289f1a8844a360377b17b11ded1f3bd5f2d432b2fa40cefc049c78f2dbfbb798.json).

Account reconciliation: completed-page charges 100.75, unassigned debits 0.25, total 101.0; matches balance change: **True**. There were also 15 exploratory read-only account/authentication calls before durable run receipts (5 token, 8 balance, 1 cost-table, 1 transaction query); no paid submission occurred in those calls.

- Charged process `31484015`: 0.25 credits, 1.0 page. Its JSON result exists, but original image bytes are unavailable from the tested result routes, so it is not assigned to a crop by an unverified text match.

## Verification and review limit

129 offline tests passed. The artifact validator recomputes all three engines’ crop metrics from hash-checked raw responses, recomputes pairwise/majority/source metrics, checks every source and review image hash, all 469 cards and local links, CSV readings and IDs, and the complete credit reconciliation. Offline regeneration made zero network calls. [Validation receipt](transkribus_failed_lines/validation.json).

Four native crop samples were inspected visually. Browser rendering remains unverified: Computer Use denied Firefox access, and the local Playwright browser executable was absent. Source/link/card validation is not a browser layout check.


## Every crop: three readings

[Raw CSV](transkribus_failed_lines/three_engines.csv) · [three-way metrics](transkribus_failed_lines/comparison.json) · [full character CSV](transkribus_failed_lines/three_engine_characters.csv) · [receipt](transkribus_failed_lines/receipt.json) · [review page](../../harvest/three_engines_review.html)

| Crop | Source | Transkribus status | Document AI | Cloud Vision | Transkribus |
| --- | --- | --- | --- | --- | --- |
| [an-00f143ecce59-p000117.mark12.r7item12](../../harvest/three_engines_review.html#an-00f143ecce59-p000117.mark12.r7item12) | Anemi | ok | κησα μλὺ ἐδενα πώπότε αὐθρώπων, ἐδὲ χείρω ἐποίησα.<br> | www.www<br>κησα μου εδεία πώποτε ανθρώπων, ἐδὲ χείρω ἐποίησα. | κησα μὺ ὁδόνα πώχοπ ὠβρώπων, εε χείρω ἐποῖνσα. |
| [an-00f143ecce59-p000192.mark27.r7item23](../../harvest/three_engines_review.html#an-00f143ecce59-p000192.mark27.r7item23) | Anemi | ok | Σμυρναίοις pos<br>70<br>Ο <br>πρόθυμον της υπηκόων διωεκές με ὂν, βεβαιότητα<br>δηλοῖ ορὸς τὸς ἡγεμόνας, ἐλλεῖπον δὲ, καὶ τὸν ὅτε<br>ετοίμως υπύρνει κόνος δὲ ἀπεύειαν ἐλέγνεται τις εαυτό<br> | Σμυρναίοις τοις<br>Το απρόθυμος του υπνικέων διακεκές μας ον, βεβαιότητα<br>δηλοῖ πρὸς τὰς ἡγεμόνας, ἐλλείπον δὲ, καὶ τὸν ὅτε<br>επίμως επέρνει το είαι ελέγχεται των ε<br>δι&#x27; οπού αν<br>το υπο<br>SOUTH | ΤΟνΜΣαμ; ζκαί. ὕκαε. |
| [an-00f143ecce59-p000258.mark2.r7item0](../../harvest/three_engines_review.html#an-00f143ecce59-p000258.mark2.r7item0) | Anemi | ok | σείλης, ε μικρων ἔχειν δωρεαν ἡγῶμαι αυτης τε<br> | δείλης, &amp; μικρών ἔχειν δωρεαν ἡγῆμαι | φείλῃς, ἀ μικρα» ἕνειν δeρε.!... |
| [an-00f143ecce59-p000258.mark2.r7item1](../../harvest/three_engines_review.html#an-00f143ecce59-p000258.mark2.r7item1) | Anemi | ok | ΕῬρωσο. τῦτο γὰρ ἐγὼ κὶ συωσύχομαι σοι, κὶ ἀκῶσαι<br>ποθῶ πεὶ σὲ · κὰν ὅτι τατὸ ὅτι παρὑμῖν ἐπι<br>.<br>σείλης. ε μικρων ἔχειν δωρεαν ἡ και της τύχης<br> | ET<br>Ἔρωσο. τότο γὰρ ἐγὼ καὶ συνεύχομαι σοι, καὶ ἀκεσαι<br>ποθώ πει σε καν ὅτι τοτὸ ὅτι παρέμεν επι<br>σείλης 2 μικρον ἔχων δωρεαν είναι το πάσης<br>.<br>έναν | ΕΝΙΕΣ ΕΝ τΑ νΑνε υ ζαζατει πρνε |
| [an-1be60011c435-p000066.mark17.r7item17](../../harvest/three_engines_review.html#an-1be60011c435-p000066.mark17.r7item17) | Anemi | ok | Ενέγκατε τις Κυρίῳ<br>! מזל<br> | Ενέγκατε τις Κυρίῳ<br>017 | Ἤλεγκαπ τῇ Κυριῳ. |
| [an-1be60011c435-p000120.mark48.r7item48](../../harvest/three_engines_review.html#an-1be60011c435-p000120.mark48.r7item48) | Anemi | ok | Φαίνεται εἰς τὴ Βίβλον τῷ Παραλειπομούων Κεφάλ. ιβ. ὅτι ὅτος<br>αδια cosmoucίκε<br> | Φαίνεται εἰς τὰ Βίβλον εξω Παραλειπομονων Κεφάλ. ιβ&#x27;. ὅτι ἔτος<br>RITMQUCine | Ῥάνεταω εἰς τω Βίβλοι τῇ Παραλεπομούω, Κεράλ. β. ὅτι ἔπς |
| [an-2cfe28da5103-p000084.mark16.r7item16](../../harvest/three_engines_review.html#an-2cfe28da5103-p000084.mark16.r7item16) | Anemi | ok | AIRTOL<br>-3 1012. κναφορ. Σ<br>τέπειτα. (8) τὰ τῆς Σπάρτης δεινά δεδιέναι, ἐμὴ τὰ παρ᾿ αὐτοῖς] προσέθει<br> | 2137<br>ΕΙΡΗΣ 2734<br>τέπειτα. (8) τὰ τῆς Σπάρτης δεινὰ δεδιέναι, τι μὲ τὰ παρ&#x27; αὐτοῖς] προσέθεια<br>ποιειν 35 ασφαλη «πιέναι με<br>34, | ίτετα. (2) τς ξὲ Στάρτς δειὰ δεῥένα; ἄ Κα τᾶ ταρβθαὐθηρεζ ευαε βεέ- |
| [an-2cfe28da5103-p000084.mark16.r7item18](../../harvest/three_engines_review.html#an-2cfe28da5103-p000084.mark16.r7item18) | Anemi | ok | τὴν ἑορτὴν, ἐλεί θερον εἶναι τώτο κοιεῖν, ἡ ἀσφαλή απιέναι με<br> | X<br>•inister es=<br>κειν εἰς τὴν ἑορτὴν, ἐλείθερον εἶναι τότο ποιεῖν<br>A<br>BITIS PERETRI N-<br>· · ἀσφαλῆ ἀπιέναι με | κειν «« Εὐν ἔρπην; ἐλ ξδεξον εἶἴει ζευ ΣωλΕυν! Σ ἀαβαλη ΕΣνεναι· 7 |
| [an-2cfe28da5103-p000084.mark18.r7item16](../../harvest/three_engines_review.html#an-2cfe28da5103-p000084.mark18.r7item16) | Anemi | ok | AIRTOL<br>-3 1012. κναφορ. Σ<br>τέπειτα. (8) τὰ τῆς Σπάρτης δεινά δεδιέναι, ἐμὴ τὰ παρ᾿ αὐτοῖς] προσέθει<br> | 2137<br>ΕΙΡΗΣ 2734<br>τέπειτα. (8) τὰ τῆς Σπάρτης δεινὰ δεδιέναι, τι μὲ τὰ παρ&#x27; αὐτοῖς] προσέθεια<br>ποιειν 35 ασφαλη «πιέναι με<br>34, | ίτετα. (2) τς ξὲ Στάρτς δειὰ δεῥένα; ἄ Κα τᾶ ταρβθαὐθηρεζ ευαε βεέ- |
| [an-2cfe28da5103-p000084.mark18.r7item18](../../harvest/three_engines_review.html#an-2cfe28da5103-p000084.mark18.r7item18) | Anemi | ok | τὴν ἑορτὴν, ἐλεί θερον εἶναι τώτο κοιεῖν, ἡ ἀσφαλή απιέναι με<br> | X<br>•inister es=<br>κειν εἰς τὴν ἑορτὴν, ἐλείθερον εἶναι τότο ποιεῖν<br>A<br>BITIS PERETRI N-<br>· · ἀσφαλῆ ἀπιέναι με | κειν «« Εὐν ἔρπην; ἐλ ξδεξον εἶἴει ζευ ΣωλΕυν! Σ ἀαβαλη ΕΣνεναι· 7 |
| [an-2cfe28da5103-p000084.mark18.r7item19](../../harvest/three_engines_review.html#an-2cfe28da5103-p000084.mark18.r7item19) | Anemi | ok | σόνας εν και εις τον επεκοινιών, απήγγειλών και καις Γληνικαις πολ<br>σε τὸν χρόνον καὶ ἐν ἑώρταζον Αθηναῖοι, ἐκ ἰπισχνώντο, εἶτις βάλεται ή<br> | * * * *<br>&amp; RevozF{WP.<br>σε τὸν χρόνον κατ&#x27; ἐν ἑώρταζον Αθηναῖοι, κι ἐπισχνώντο, εἴτις βέλεται τα<br>απηγγειλων γαρ ταις Γαληνικες πολει<br>d | τι τιν κεύρις, καζ ἐν ξ φξαξὺν υναν!ν  καχθῶστοτ’ ἀια’ μέξλε ατιν ἄ- |
| [an-2cfe28da5103-p000084.mark19.r7item18](../../harvest/three_engines_review.html#an-2cfe28da5103-p000084.mark19.r7item18) | Anemi | ok | τὴν ἑορτὴν, ἐλεί θερον εἶναι τώτο κοιεῖν, ἡ ἀσφαλή απιέναι με<br> | X<br>•inister es=<br>κειν εἰς τὴν ἑορτὴν, ἐλείθερον εἶναι τότο ποιεῖν<br>A<br>BITIS PERETRI N-<br>· · ἀσφαλῆ ἀπιέναι με | κειν «« Εὐν ἔρπην; ἐλ ξδεξον εἶἴει ζευ ΣωλΕυν! Σ ἀαβαλη ΕΣνεναι· 7 |
| [an-2cfe28da5103-p000084.mark19.r7item19](../../harvest/three_engines_review.html#an-2cfe28da5103-p000084.mark19.r7item19) | Anemi | ok | σόνας εν και εις τον επεκοινιών, απήγγειλών και καις Γληνικαις πολ<br>σε τὸν χρόνον καὶ ἐν ἑώρταζον Αθηναῖοι, ἐκ ἰπισχνώντο, εἶτις βάλεται ή<br> | * * * *<br>&amp; RevozF{WP.<br>σε τὸν χρόνον κατ&#x27; ἐν ἑώρταζον Αθηναῖοι, κι ἐπισχνώντο, εἴτις βέλεται τα<br>απηγγειλων γαρ ταις Γαληνικες πολει<br>d | τι τιν κεύρις, καζ ἐν ξ φξαξὺν υναν!ν  καχθῶστοτ’ ἀια’ μέξλε ατιν ἄ- |
| [an-2cfe28da5103-p000084.mark19.r7item21](../../harvest/three_engines_review.html#an-2cfe28da5103-p000084.mark19.r7item21) | Anemi | ok | σπουδὰς ἐν τῇ ἑορτῇ τῶν Ελευσινίων. ἀπήγγελλον γὰρ ταῖς Ελληνικαῖς πόλε<br> | σπουδὰς ἐν τῇ ἑορτῇ τῶν Ελευσινίων. απήγγελλον γὰρ ταῖς Ελληνικαῖς πόλε | σπυδὰ ἐν τῇ ἕορτῇ τᾷ, Ἑλευσωίμν, ἀπήγγελον χὰρ παῖ. Ἑλληνμαῖς τόλι- |
| [an-2cfe28da5103-p000084.mark6.r7item4](../../harvest/three_engines_review.html#an-2cfe28da5103-p000084.mark6.r7item4) | Anemi | ok | τις παρα παοιν. ο οε εείσκης μετέβαλεν is, gui, plur<br>δὲ νῦν πολεμικοί] ὡς ὁ Δημοθένης. εἰρωνικα δὲ ταῦτα. (6) εἰρίνης] άτοι<br>2.<br> | πως τα ζωα παοιν. ο δε Γ εἰσκής μετεβάλεν τις γυ, ωρωνι, μηνασ φευγε<br>δὲ νῦν πολεμικοί] ὡς ὁ Δημοσθένης, εἰρωνικά δὲ ταῦτα. (6) εἰρήνης] στοι<br>&#x27; | δὲ νῦν πολεμικοῇ, ὡς ὁ Δηαοβενης. εἴρων, κα δὲ· ταῦτα. Ἐν εἰρίνης ἀτοι- |
| [an-2cfe28da5103-p000084.mark6.r7item6](../../harvest/three_engines_review.html#an-2cfe28da5103-p000084.mark6.r7item6) | Anemi | ok | હું RRRRR <br>r<br>10<br>ὕτω καρὰ πᾶσιν. ὁ δὲ Ρ&#x27; εἶσκης μετέβαλεν εἰς τὸ, ὁρῶσι, μηδὲν δέϋν. (6) 07<br>2<br>L<br> | 4<br>217th im<br>50.9.<br>.<br>IN<br>3 WEOXINS. 108<br>Sabz 31<br>59<br>Στὰ παρὰ πᾶσιν. ὁ δὲ Ρ&#x27; εἴσκης μετέβαλεν εἰς τὸ, ὁρῶσι, μηδὲν δέον. (6) οι<br>...<br>. | ἔχω καρὰ τᾶσνν.  δὲ φ ἤρκης Μεξεραλεν εἰς φὲ ὑρώσι, μηδὲν δέυν. (Ὁ) οἱ |
| [an-2cfe28da5103-p000135.mark22.r7item46](../../harvest/three_engines_review.html#an-2cfe28da5103-p000135.mark22.r7item46) | Anemi | ok | ὑμῖν δὲ τοῖς ἄλλοις τοῖς ἔξω<br> | ὑμῖν δὲ τοῖς ἄλλοις τοῖς ἔξω | ὑμῖν δὲ τοῖς ἄλλοις τοῖς ἐξω- |
| [an-2cfe28da5103-p000135.mark40.r7item16](../../harvest/three_engines_review.html#an-2cfe28da5103-p000135.mark40.r7item16) | Anemi | ok | ὁπλιτῶν κὶ τῶν ἱππέων ὄντων. ΙΖ΄<br> | ὁπλιτῶν καὶ τῶν ἱππέων ὄντων ΙΖ&#x27; | ὀπλίφων , των ἐππέων ὅντων. 12΄. |
| [an-2cfe28da5103-p000135.mark40.r7item60](../../harvest/three_engines_review.html#an-2cfe28da5103-p000135.mark40.r7item60) | Anemi | ok | ρθ΄, 1. πάχειν αὐτοὶ κακῶς ἔξω<br> | ρθ&#x27;, &#x27;. πάχειν αὐτοὶ κακῶς ἔξω | ρῶ;!. πάρχειν αὐτοὶ κακως ἔξω. |
| [an-2cfe28da5103-p000135.mark68.r7item23](../../harvest/three_engines_review.html#an-2cfe28da5103-p000135.mark68.r7item23) | Anemi | ok | -<br>Λης οικην υπομένει φευγειν. Λ.<br>1<br>μα΄, 6. ἐξέλης ἂν ἔφυγον νῦν,<br> | Λης οικην υπομένει φευγειν. Λ.<br>&quot;<br>μα&#x27;, 6. ἐξέλης ἂν ἔφυγον νῦν,<br>αν | μα, β. ἐξόλης ἂν ἔφυγου νυν, |
| [an-2cfe28da5103-p000135.mark68.r7item24](../../harvest/three_engines_review.html#an-2cfe28da5103-p000135.mark68.r7item24) | Anemi | ok | λης δίκην ὑπομένει φεύγειν. Κ΄.<br> | λης δίκην υπομένει φεύγειν. Κ&#x27; | λης δίκην ὑπομένει θευγει». 4. |
| [an-3352d912f2e9-p000029.mark4.r7item3](../../harvest/three_engines_review.html#an-3352d912f2e9-p000029.mark4.r7item3) | Anemi | ok | 0000<br>διαβαπείς, πάλιν γλώασας ἐπρίατο, καὶ ἑτοιμάσας,<br> | επων 359<br>καζαπείς, πάλιν γλώσσας ἐπείατο, καὶ ἑτοιμάσας | λαβαπεὶς, πάλιν νλώσας ἐπρίαο, νοὶ ἐποιμάσας; |
| [an-3352d912f2e9-p000029.mark4.r7item4](../../harvest/three_engines_review.html#an-3352d912f2e9-p000029.mark4.r7item4) | Anemi | ok | της Σχολαςικῶν σιν αυτις δειπνησόντων. Οἱ δὲ, μηδεν<br> | της Σχολασικών στο αυτω δειπνησόντων. Ο&#x27; δέ, μηδε | Η Σλολαξικων τθ’ αὕῃ δεικννσόνπων. Ο δὲ, μἶδοῦ |
| [an-3352d912f2e9-p000029.mark4.r7item5](../../harvest/three_engines_review.html#an-3352d912f2e9-p000029.mark4.r7item5) | Anemi | ok | .<br>τι φαυλότατόν τε, καὶ χείριςον ὀψωνήσαι κελεύει, ὡς<br> | of genopa<br>1x42<br>το φαυλότατόν τε, καὶ χείρισὸν ὀψωνήσαι κελεύει, ὡς | 4. θαυλόάπθε; Ἡ χείξιζςεν ὀψωνήσαι κελρύει, ὡς |
| [an-3352d912f2e9-p000055.mark1.r7item0](../../harvest/three_engines_review.html#an-3352d912f2e9-p000055.mark1.r7item0) | Anemi | ok | VEOT<br> | VEOT-10 | ν7— |
| [an-3352d912f2e9-p000055.mark1.r7item1](../../harvest/three_engines_review.html#an-3352d912f2e9-p000055.mark1.r7item1) | Anemi | ok | 6402240000<br>καταπτας<br>A<br>παπι<br>θυμάτων στων ἐμπύροις αἴθραξιν ήρπασε, κάπί των<br> | ιοντων<br>καταπτας<br>θυμάτων σων εμπόροις ανθραξιν ήρπασε, καπὶ τῶν | θυμάπω, σωῦ Ἐμπυρίας ἵβραξ, ἤρπασε; καπὶ τίως |
| [an-3352d912f2e9-p000055.mark3.r7item3](../../harvest/three_engines_review.html#an-3352d912f2e9-p000055.mark3.r7item3) | Anemi | ok | TON<br>της ἐχθρῶ κατηρᾶτο. Οὐ πολλῷ δ᾽ ὕςερον, αἰγά τινων<br> | 780<br>τῷ ἐχθρῶ κατηράτο. ου πολλῷ δ᾽ ὕτερον, αἰγά τινων<br>Οὐ | τῷ ἐχδρῶ καπράη οὗ πολῷ δ’ ὕϛερον, αἰγά τιναι. |
| [an-3352d912f2e9-p000055.mark7.r7item6](../../harvest/three_engines_review.html#an-3352d912f2e9-p000055.mark7.r7item6) | Anemi | ok | θανάτῳ, ὅσον ἐπὶ τῷ τῆς ἀμενης απόρῳ χερσαία<br> | μανουσ<br>θανάτῳ<br>του στur<br>ὅσον ὅτι τῷ τῆς ἀρης απόρῳ χερσαία | δαυάτῳ, ὅσον ὅπὶ τῷ ῆς ἀμωης ἐπόρῳ; χερσαία. |
| [an-3352d912f2e9-p000055.mark7.r7item7](../../harvest/three_engines_review.html#an-3352d912f2e9-p000055.mark7.r7item7) | Anemi | ok | うの<br>0<br>Αλλωσης<br>μαθέσα, ἐ τοσέτον ἐπὶ τῷ της τέκνων Ιώτάθη<br> | Α1 Λωπης<br>Ja<br>θα μαθέσα, κ τοσέτον ἐπὶ τῷ δ τέκνων ιάθη<br>ν | θον μαδέσα; « τόσκτον ἔαὶ τῷ τῇ τέκνων ἱωιάθη |
| [an-3352d912f2e9-p000104.mark19.r7item19](../../harvest/three_engines_review.html#an-3352d912f2e9-p000104.mark19.r7item19) | Anemi | ok | E<br>surda.<br>ποις ἐζὶν, ἦχον εἰς Αγαλμάπποις, ἑαυτὸν ει<br>,<br> | E<br>- έμής<br>ιμης γνωναι<br>ποις όξιν, ήταν εἰς Αγαλματοποις, ε<br>ἑαυτὸν | Ἄεποις ὀξιν, ἶκον εἰς Ἀγαλμάπποια, ἑαυὸ ἐ- |
| [an-3352d912f2e9-p000104.mark19.r7item20](../../harvest/three_engines_review.html#an-3352d912f2e9-p000104.mark19.r7item20) | Anemi | ok | ΠῬμῆς γνώναι βελόμμος ἐν τίνι τιμῇ παρ αὐθρώ<br> | - Ρμῆς γνῶναι βελόμβυος εν τίνι τιμῇ παρ&#x27; ανθρ | —Ἐμῆς γκῶναι βελόμβος ἐν τίνι τιμῇ παρ’ αὐδρώ- |
| [an-3352d912f2e9-p000104.mark5.r7item3](../../harvest/three_engines_review.html#an-3352d912f2e9-p000104.mark5.r7item3) | Anemi | ok | 4 ληθής ότι, γνῶναι, κλέψας πὰς ἀυτό βους<br> | 1 ληθής όξι, γνῶναι, κλέψας τὰς αυτή βους | ληδὴς ὄξι, γνῶναι, κλέψας πας αὐτὰ βοῦς |
| [an-3352d912f2e9-p000104.mark5.r7item5](../../harvest/three_engines_review.html#an-3352d912f2e9-p000104.mark5.r7item5) | Anemi | ok | Ῥμῆς βελόμμος τιώ Τειρεσίς μαντικίώ,<br>Ερμής βαλό<br>, εἰ<br> | Ερμής, βαλόμθμος των Τειρεσία μαντικώ,<br>και<br>BULGINT<br>εἰ | Ε λιῖξ, βιλάιωος. κτων ΤερίΣι. μωτκώω, ἐ- |
| [an-778126cc8c2b-p000007.mark19.r7item19](../../harvest/three_engines_review.html#an-778126cc8c2b-p000007.mark19.r7item19) | Anemi | ok | Pour la façon d&#x27;ornement rouge on bleu,<br> | Pour la façon d&#x27;ornement rouge on bleu; | ΡΟΙ Ι ΕΟi cnΜΣΟ |
| [an-778126cc8c2b-p000010.mark21.r7item18](../../harvest/three_engines_review.html#an-778126cc8c2b-p000010.mark21.r7item18) | Anemi | ok | (empty) | 99 | 31 |
| [an-778126cc8c2b-p000010.mark21.r7item19](../../harvest/three_engines_review.html#an-778126cc8c2b-p000010.mark21.r7item19) | Anemi | ok | · Ω τι ασταράδες τιZHIM<br>, το κορμί, τι τζόγαις ποδαράκια:<br> | χερακια<br>Ω τὶ ἀσπράδες,<br>τι κέρμι, τὶ τζόγαις ποδαράκια - | » 2’ τὶ ασπράδες, τ’ «Σρμ,, τι τζόχαις ποδαράκα. |
| [an-778126cc8c2b-p000010.mark21.r7item20](../../harvest/three_engines_review.html#an-778126cc8c2b-p000010.mark21.r7item20) | Anemi | ok | &quot;<br>» Ω γιὰ φιλιά, どう<br>τα τα χαιδέματα γεράκια<br>ποδαράκια<br> | 99<br>Ο<br>Ω γιὰ φιλιά<br>χαιδέματα χεράκια, | », 2’ φὰ φλιὰ, κ τῷ 5 ραρδέματα χεράκια, |
| [an-778126cc8c2b-p000010.mark37.r7item35](../../harvest/three_engines_review.html#an-778126cc8c2b-p000010.mark37.r7item35) | Anemi | ok | 66<br>» Αντζις, ἐγὼ, Σαμεροᾶ, θὲ να σὲ<br>να σε κετοντάρω,<br> | C6<br>την<br>Αντζις, ἐγώ, Σαμεροᾶ, θὲ νὰ σὲ κατεντάρω<br>10 | »» Ἄντζις, ἐχὼ, Σαμεροᾶ, δὲ νὰ σὲ κετουπάρο |
| [an-778126cc8c2b-p000011.mark11.r7item10](../../harvest/three_engines_review.html#an-778126cc8c2b-p000011.mark11.r7item10) | Anemi | ok | ΚΡΗΤΗΣ<br>Eles étaient libérales ausst<br> | Elles étaient libérales auss | ΕΗΝΕΠΒΠΠΕ |
| [an-778126cc8c2b-p000011.mark11.r7item11](../../harvest/three_engines_review.html#an-778126cc8c2b-p000011.mark11.r7item11) | Anemi | ok | Et qui devaient être bien santes,<br>010<br> | 10<br>Et qui devaient être bien y antes | . Ι ΕΗΙΕΕΕΗΝ |
| [an-778126cc8c2b-p000011.mark13.r7item13](../../harvest/three_engines_review.html#an-778126cc8c2b-p000011.mark13.r7item13) | Anemi | ok | Un peu changés, ont encor tant d&#x27;attraits!<br> | 113<br>Un peu changés, ont encor<br>tant<br>attrants! | Η ΡΕu ciΕ, ΟΙΗΚΣΙΗΕΙ |
| [an-7a2b17a3fb0f-p000012.mark2.r7item2](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000012.mark2.r7item2) | Anemi | ok | τέρων, κὶ 6 τρίτων, γράφομεν ὕτω 15°<br> | τέρων, καὶ 6 τρίτων, γράφομεν ὕτω 15° | τέρων, ἢ ὁ τρίτων, γράφομεν ὅτω 15 |
| [an-7a2b17a3fb0f-p000012.mark2.r7item65](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000012.mark2.r7item65) | Anemi | ok | (empty) | (empty) | . . |
| [an-7a2b17a3fb0f-p000200.mark171.r7item171](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark171.r7item171) | Anemi | ok | 2927 3.466423<br> | 2927 3.466423 | 29Α7 ΟΑΟ623 |
| [an-7a2b17a3fb0f-p000200.mark227.r7item227](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark227.r7item227) | Anemi | ok | 39.967268<br> | 9.967268 | ) 3. 3éφa68! |
| [an-7a2b17a3fb0f-p000200.mark228.r7item228](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark228.r7item228) | Anemi | ok | 9.605682<br> | 19.605682 | Ι25Ο5592 |
| [an-7a2b17a3fb0f-p000200.mark229.r7item209](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark229.r7item209) | Anemi | ok | 9.573263<br> | 19.573263 | 19.573268 |
| [an-7a2b17a3fb0f-p000200.mark229.r7item229](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark229.r7item229) | Anemi | ok | 9.572950<br> | 19.572950 | 19.572958 |
| [an-7a2b17a3fb0f-p000200.mark235.r7item235](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark235.r7item235) | Anemi | ok | 57<br>58<br>59<br>160<br> | 157<br>158<br>5 5 5<br>159<br>160 | 159 |
| [an-7a2b17a3fb0f-p000200.mark243.r7item243](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark243.r7item243) | Anemi | ok | 33<br> | 33 | 33 |
| [an-7a2b17a3fb0f-p000200.mark257.r7item257](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark257.r7item257) | Anemi | ok | 34-<br> | 34- | 34 |
| [an-7a2b17a3fb0f-p000200.mark272.r7item272](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark272.r7item272) | Anemi | ok | 55<br>56<br> | 55<br>56 | 156 |
| [an-7a2b17a3fb0f-p000200.mark273.r7item273](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark273.r7item273) | Anemi | ok | 135<br> | 135 | 135 |
| [an-7a2b17a3fb0f-p000200.mark273.r7item288](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark273.r7item288) | Anemi | ok | ---8890<br>99.968976<br>89.968426<br> | 29.968976<br>1.968y26<br>20<br>062277 | 8βΕΣ. |
| [an-7a2b17a3fb0f-p000200.mark278.r7item278](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark278.r7item278) | Anemi | ok | 3-475526<br> | 3.475526<br>- | 8.ΑΦΟΕΔΟ! |
| [an-7a2b17a3fb0f-p000200.mark282.r7item256](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark282.r7item256) | Anemi | ok | 9.967370<br> | 9.967370 | 1235737Ο1 |
| [an-7a2b17a3fb0f-p000200.mark282.r7item282](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark282.r7item282) | Anemi | ok | -<br>79.967471<br> | 79.967471 | «ΙΦΦΕΙΙ |
| [an-7a2b17a3fb0f-p000200.mark282.r7item283](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark282.r7item283) | Anemi | ok | 10222900/2<br>9.967431<br> | 9.9674211<br>06727 | aΙ8Φ5Τ1Α1 |
| [an-7a2b17a3fb0f-p000200.mark287.r7item258](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark287.r7item258) | Anemi | ok | 968877<br> | 968877 | 065877 |
| [an-7a2b17a3fb0f-p000200.mark287.r7item259](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark287.r7item259) | Anemi | ok | 9<br> | (empty) | 4 |
| [an-7a2b17a3fb0f-p000200.mark287.r7item288](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark287.r7item288) | Anemi | ok | ---8890<br>99.968976<br>89.968426<br> | 29.968976<br>1.968y26<br>20<br>062277 | 8βΕΣ. |
| [an-7a2b17a3fb0f-p000200.mark294.r7item295](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark294.r7item295) | Anemi | ok | 19.561824<br> | 19.561824<br>TAC | Ι55βιΣ24 |
| [an-7a2b17a3fb0f-p000200.mark301.r7item302](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark301.r7item302) | Anemi | ok | 53<br> | 53 | 53 |
| [an-7a2b17a3fb0f-p000200.mark322.r7item323](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark322.r7item323) | Anemi | ok | (empty) | (empty) | 139 |
| [an-7a2b17a3fb0f-p000200.mark343.r7item344](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark343.r7item344) | Anemi | ok | 20<br> | 20 | 29 |
| [an-7a2b17a3fb0f-p000200.mark361.r7item362](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark361.r7item362) | Anemi | ok | 499-570120<br> | y 94<br>49 9.570120 | Πῦlο.sτοιαe. |
| [an-7a2b17a3fb0f-p000200.mark374.r7item375](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark374.r7item375) | Anemi | ok | -<br>18<br>L<br> | 18 | 75 |
| [an-7a2b17a3fb0f-p000200.mark412.r7item413](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark412.r7item413) | Anemi | ok | 9.967876<br> | 19.967876 | 19361876 |
| [an-7a2b17a3fb0f-p000200.mark420.r7item421](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark420.r7item421) | Anemi | ok | 15<br> | 15 | 15 |
| [an-7a2b17a3fb0f-p000200.mark426.r7item427](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark426.r7item427) | Anemi | ok | 15<br> | IS | 18 |
| [an-7a2b17a3fb0f-p000200.mark434.r7item435](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark434.r7item435) | Anemi | ok | 14<br> | I | L4 |
| [an-7a2b17a3fb0f-p000200.mark453.r7item454](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark453.r7item454) | Anemi | ok | 9.568222 9.600194<br> | 9.568222 9.600194. | (l3.seaaaa 9,éoorρ4. |
| [an-7a2b17a3fb0f-p000200.mark506.r7item507](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark506.r7item507) | Anemi | ok | 139<br>12<br> | 39 | 129 |
| [an-7a2b17a3fb0f-p000200.mark534.r7item535](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark534.r7item535) | Anemi | ok | 37<br> | 37 | 27 |
| [an-7a2b17a3fb0f-p000200.mark548.r7item549](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark548.r7item549) | Anemi | ok | 36<br> | 36 | 26 |
| [an-7a2b17a3fb0f-p000200.mark563.r7item564](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark563.r7item564) | Anemi | ok | 35<br> | 35 | 25 |
| [an-7a2b17a3fb0f-p000200.mark593.r7item594](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark593.r7item594) | Anemi | ok | 3.472464<br> | 3.472464 | 13. 472464 |
| [an-7a2b17a3fb0f-p000200.mark593.r7item608](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark593.r7item608) | Anemi | ok | 3-472318<br> | 3.472318 | Ι8.4ΦΩ3ΙΣ |
| [an-7a2b17a3fb0f-p000200.mark595.r7item596](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark595.r7item596) | Anemi | ok | 33<br> | 33 | 33 |
| [an-7a2b17a3fb0f-p000200.mark634.r7item635](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark634.r7item635) | Anemi | ok | 59<br>58<br>57<br>156<br> | 76 | 157 |
| [an-7a2b17a3fb0f-p000200.mark635.r7item636](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark635.r7item636) | Anemi | ok | 30<br>31<br>33<br>32<br> | τε<br>-<br>m m<br>30. | 52 |
| [an-7a2b17a3fb0f-p000200.mark642.r7item643](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark642.r7item643) | Anemi | ok | 1301<br> | - | 1381 |
| [an-7a2b17a3fb0f-p000200.mark646.r7item647](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark646.r7item647) | Anemi | ok | τω᾿ ἀριθμῶν.<br> | των αριθμών. | χι ἀριθμων. |
| [an-7a2b17a3fb0f-p000200.mark65.r7item65](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark65.r7item65) | Anemi | ok | 3-468938<br> | 3.468938 | ΙΦΑΦΟΦΟ8 |
| [an-7a2b17a3fb0f-p000200.mark81.r7item81](../../harvest/three_engines_review.html#an-7a2b17a3fb0f-p000200.mark81.r7item81) | Anemi | ok | 3-468790<br> | 3-468 790 | (ΣΕΟ |
| [an-9ea1564fcf4f-p000170.mark98.r7item80](../../harvest/three_engines_review.html#an-9ea1564fcf4f-p000170.mark98.r7item80) | Anemi | ok | δὲ τὶ γὰρ χρὴ ποιεῖν<br>θὰ δείρω· ἐπειδὴ τὸ ἡμα<br>..<br> | δὲ τὶ γὰρ χρή ποιεῖν<br>Θα δείρω ἐπειδὴ τὸ μ<br>5 | δὲ· τὶ φὰρ χρὴ ποιεῖν, δὰ δείρω ἐπειδὴ τὶ μ- |
| [an-9ea1564fcf4f-p000202.mark12.r7item10](../../harvest/three_engines_review.html#an-9ea1564fcf4f-p000202.mark12.r7item10) | Anemi | ok | Διαρροής ἡ Το διὰ τινές τρέξι<br> | Τὸ<br>Διαρροή ή το δια τινες τρέξι | Ἀἱαῤῥοή! ἡ. Τὸ διὰ τινὲς ἐρέξι- |
| [an-9ea1564fcf4f-p000202.mark25.r7item19](../../harvest/three_engines_review.html#an-9ea1564fcf4f-p000202.mark25.r7item19) | Anemi | ok | Διαβάτων, ων· βληκα. Α΄. β. -<br> | Blyzz. A&#x27;. B. i- | Δια κα λιν, ὦ’ ὅληκα. Α. β. ἐ- |
| [an-9ea1564fcf4f-p000202.mark87.r7item67](../../harvest/three_engines_review.html#an-9ea1564fcf4f-p000202.mark87.r7item67) | Anemi | ok | ρομαι, αφανίζομαι<br>Διακονεώ, ω νήσω· Μέσ. Διακο<br> | ρομαι, αίματες μι<br>Διακονέω, ω<br>ω· νήσω· Μέσ. Διακο<br>N | ΔΑ8ϊ4ω; 5 υΕ5ε ερσ. Διακο- |
| [an-9ea1564fcf4f-p000218.mark133.r7item90](../../harvest/three_engines_review.html#an-9ea1564fcf4f-p000218.mark133.r7item90) | Anemi | ok | 684. Ε΄, 545-<br> | 684. E&#x27;, 545- | 58Α Ε 4— |
| [an-a73d22211479-p000047.mark37.r7item37](../../harvest/three_engines_review.html#an-a73d22211479-p000047.mark37.r7item37) | Anemi | ok | ὑπὸ τὸ μανίαν, πῶς θέλει βράζει<br>A<br> | ἀπὸ τὸ μανίων, πως θέλει βράζει | ὀπὸ τὰῳ μαυίαω, πως δέλει βρᾶζεα! |
| [an-a73d22211479-p000047.mark37.r7item39](../../harvest/three_engines_review.html#an-a73d22211479-p000047.mark37.r7item39) | Anemi | ok | οινός δαιμονισμώος, θέλει αφρίζει<br> | οινός δαιμονισμένος θέλει αφρίζει | ρινος δαιμοιισμθύοςὁ δέλει ἀφρίζεα. |
| [an-a73d22211479-p000141.mark11.r7item11](../../harvest/three_engines_review.html#an-a73d22211479-p000141.mark11.r7item11) | Anemi | ok | » ψόμεθα; ἔτζι ἔκαμαν, ἄφηκαν τοὺ<br>66<br> | &quot;<br>y<br>παλιν<br>&quot;<br>ψόμεθα; ἔτζι ἔκαμαν, ἄφηκαν τα<br>,<br>&quot;<br>&quot; | » ψόμεδα; ἔτζε ἔκαμαν ἄφηκαν τύω |
| [an-a73d22211479-p000141.mark11.r7item13](../../harvest/three_engines_review.html#an-a73d22211479-p000141.mark11.r7item13) | Anemi | ok | 66<br>٠٨٢<br>αν το δοκεῖ πάλιν, ἐπανιόντες λη-<br>&quot;<br>&quot;<br>16<br> | &quot;&#x27;<br>&quot;<br>~ δοκεῖ πάλιν, επανιόντες λη<br>&quot;<br>&quot;<br>&quot;1 | », αὐ δὸ δοκεῖ πάλιν, ἐπαυιόντες λη- |
| [an-a73d22211479-p000141.mark12.r7item12](../../harvest/three_engines_review.html#an-a73d22211479-p000141.mark12.r7item12) | Anemi | ok | 1uble mtadswo &#x27;mtads<br>ναι νὰ λάβης συγχώρησιν. ὄχι ένας<br>&gt;<br> | &gt;<br>&quot;<br>Intard<br>oms<br>075 porque • ofgeri<br>.<br>abuwatures<br>ενας<br>ναι νὰ λάβης συγχώρησιν. ὄχι ας | ναι νὰ λάβῃς συγχώρησιν ὄχι ἕνας. |
| [an-a73d22211479-p000141.mark12.r7item14](../../harvest/three_engines_review.html#an-a73d22211479-p000141.mark12.r7item14) | Anemi | ok | τρέψαι, σλάςρεψαι. διατὶ ἀδιύατον εἶ-<br> | Sangvinn mind.<br>τρέψαι, στάσρεψαι. Κατὶ ἀδιύατον εἶ | σρεψαι ὄίςρεψαι. κατὶ ἀδωώαπν εἶ- |
| [an-a73d22211479-p000141.mark50.r7item47](../../harvest/three_engines_review.html#an-a73d22211479-p000141.mark50.r7item47) | Anemi | ok | &quot;<br>&quot;<br>ἀφήσει καὶ ὑμῖν ὁ Πατέρ ἡμῶν ὁ<br>,<br>1<br> | 29<br>ἀφήσει καὶ ὑμῖν ὁ Πατὴρ ἡμῶν<br>101<br>Ο<br>IN | »» αφησεη καὶ ὑμιν ὁ Παπρ νμων οἱ |
| [an-a73d22211479-p000141.mark50.r7item49](../../harvest/three_engines_review.html#an-a73d22211479-p000141.mark50.r7item49) | Anemi | ok | &quot;<br>EW<br>αγιού<br>לישי<br>W<br>θρώποις τὰ παραπτώματα αὐτὸ,<br>κρύσει καὶ ὑμῖοπ<br>2<br>?<br> | &quot;<br>aynes<br>&quot;<br>τα<br>η θρώποις τὰ παραπτώματα αὐτ | »» δρώποις πὰ παραπτώμαπα αὐτῷ; |
| [an-a73d22211479-p000141.mark50.r7item51](../../harvest/three_engines_review.html#an-a73d22211479-p000141.mark50.r7item51) | Anemi | ok | 07<br>(Ματθ. 5΄.), ἐὰν ἀφῆτε τοῖς αν<br>(<br> | (Ματθ. ς&#x27;.) »<br>&quot;<br>ἐαὶ ἀφῆτε τοῖς αυ | (Ματῷ. ς.)., εαὐ ἀφῆτε τοῖς αὐ- |
| [an-a73d22211479-p000141.mark51.r7item48](../../harvest/three_engines_review.html#an-a73d22211479-p000141.mark51.r7item48) | Anemi | ok | ΛΙΛΑ<br>IA A<br>αραθύρι ἔβλεπε τίω θάλαασαν, τὸ<br>&quot;<br> | που αθύρι ἔβλεπε τω θάλασσαν,<br>τὸ<br>&quot; | σΦαδύρι ἔβλεπε τῶῶ δάλαασαν τὰ |
| [an-a73d22211479-p000141.mark51.r7item50](../../harvest/three_engines_review.html#an-a73d22211479-p000141.mark51.r7item50) | Anemi | ok | θεν εἰς τὸ αυῆτί τς, κῷ διατὶ ἀπὸ εκα<br>۲۲۵ ۱<br> | θεν εἰς τὸ αυτί τε, καὶ κατὶ ἀπὸ είναι | δον εἰς τὸ ασντί τα,ιῃ δατὶ ἐπὸ οἴα |
| [an-a73d22211479-p000141.mark69.r7item68](../../harvest/three_engines_review.html#an-a73d22211479-p000141.mark69.r7item68) | Anemi | ok | ξομολόγησις; αργολογία. ἄλλο· ἔχεις<br>८<br> | k<br>ξομολόγησις; αργολογία. ἄλλο ἔχεις | ξομολόφνσις; ἀρφολογία, ἄλο· ἔχεις. |
| [an-a73d22211479-p000141.mark69.r7item70](../../harvest/three_engines_review.html#an-a73d22211479-p000141.mark69.r7item70) | Anemi | ok | κορωπι ἐχθροί. κὶ ἐκείνη ἐτάθη Ε΄-<br> | πρώτα εχθροί.<br>εχθροί. ἢ ἐκείνη ἐτάθη Ε- | !κ. πρῶπα ἐχδροί. » ἐκείνη ἐφάβη Ε- |
| [an-a73d22211479-p000301.mark12.r7item12](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark12.r7item12) | Anemi | ok | 2010<br>λία, διὰ νὰ ὑπανδράθῆ μία πτωχή<br>در<br> | για<br>λία, διὰ νὰ ὑπανδρα η μία πτωχή<br>να<br>ef | λία, διὰ νὰ ὑπαυδροίδη μιὰ πτωχὴ. |
| [an-a73d22211479-p000301.mark12.r7item14](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark12.r7item14) | Anemi | ok | διὰ νὰ κυβερνηθῇ μία πτωχή φαμε<br>2<br> | διὰ νὰ κυβερνηθῇ μία πτωχὴ φαμε<br>nicho ndar<br>2010 | διὰ νὰ κυβερνηδῃ μία πτωχὴ φαμε- |
| [an-a73d22211479-p000301.mark14.r7item12](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark14.r7item12) | Anemi | ok | 2010<br>λία, διὰ νὰ ὑπανδράθῆ μία πτωχή<br>در<br> | για<br>λία, διὰ νὰ ὑπανδρα η μία πτωχή<br>να<br>ef | λία, διὰ νὰ ὑπαυδροίδη μιὰ πτωχὴ. |
| [an-a73d22211479-p000301.mark14.r7item14](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark14.r7item14) | Anemi | ok | διὰ νὰ κυβερνηθῇ μία πτωχή φαμε<br>2<br> | διὰ νὰ κυβερνηθῇ μία πτωχὴ φαμε<br>nicho ndar<br>2010 | διὰ νὰ κυβερνηδῃ μία πτωχὴ φαμε- |
| [an-a73d22211479-p000301.mark14.r7item16](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark14.r7item16) | Anemi | ok | διὰ Ἱερὰ ἄμφια Ιερέων· ὅταν δίδης<br> | pa oras newer,<br>διὰ Ιερὰ ἄμφια Ιερέων· ὅταν δίδης | διὰ Γερὰ ἄμφια Γερέων· ὅταυ δίδῃς |
| [an-a73d22211479-p000301.mark15.r7item13](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark15.r7item13) | Anemi | ok | τὶ ὁ Θεὸς ὑποβλέπει, ὄχι εἰς τιὼ<br> | τὶ ὁ Θεὸς Υποβλέπει, ὄχι εἰς τ<br>τι | τὶ ὁ Θεὸς ὀποβλέπει, ὄχι εἰς τίω |
| [an-a73d22211479-p000301.mark15.r7item15](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark15.r7item15) | Anemi | ok | 7<br>κὰ οἱ δύο ἔχεσιν ἴσιον τὸν μιπόν· δια-<br> | aradoo<br>4m 1 212<br>καὶ οἱ δύο ἔχεσιν ἴσιον τὸν μιθόν δια | οι δύο ἔχεσιν ἴσιον τὸν μιδόν· δια- |
| [an-a73d22211479-p000301.mark15.r7item17](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark15.r7item17) | Anemi | ok | · λὺ, ὁ πτωχὸς ὀλίγον. κὴ ἠξεύρετε πῶς<br>১<br>&quot;<br> | λὺ, ὁ πτωχὸς ὀλίγον. καὶ ἠξεύρετε πῶς<br>&quot; | λὺ, ὁ πτωχὸς ὀλίγον. ῃ ἠξούρετε πως. |
| [an-a73d22211479-p000301.mark16.r7item14](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark16.r7item14) | Anemi | ok | διὰ νὰ κυβερνηθῇ μία πτωχή φαμε<br>2<br> | διὰ νὰ κυβερνηθῇ μία πτωχὴ φαμε<br>nicho ndar<br>2010 | διὰ νὰ κυβερνηδῃ μία πτωχὴ φαμε- |
| [an-a73d22211479-p000301.mark16.r7item16](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark16.r7item16) | Anemi | ok | διὰ Ἱερὰ ἄμφια Ιερέων· ὅταν δίδης<br> | pa oras newer,<br>διὰ Ιερὰ ἄμφια Ιερέων· ὅταν δίδης | διὰ Γερὰ ἄμφια Γερέων· ὅταυ δίδῃς |
| [an-a73d22211479-p000301.mark16.r7item18](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark16.r7item18) | Anemi | ok | mend<br>-<br>να Μονας ήριον, διὰ σκοίύη Εκκλησιῶν,<br>el<br> | Mow<br>τα Μονας ήριον, διὰ σκεύη Εκκλησιῶν,<br>ef | να Μοραςήριον, διὰ σκόύη Ἐκκλησιῶν, |
| [an-a73d22211479-p000301.mark38.r7item36](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark38.r7item36) | Anemi | ok | τὰ Εἴδωλα τζῇ ὀλιθυμιῶν σε, εἰς ξα<br> | τα Είδωλα της επιθυμιων σε, εἰς α<br>ξα | τῇ Εἴδωλα τῇρ ὁπουμιῶν σα, εἰς βα- |
| [an-a73d22211479-p000301.mark38.r7item38](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark38.r7item38) | Anemi | ok | 7<br>2<br>διὰ ἐκεῖνα όπὲ ὀρέγεσαι, ὁπὲ εἶναι<br>،<br> | 7<br>☑<br>εκείνα όπε ορέγεσαι<br>οπός είναι<br>~ | ὀχα ἔκεινα ὅπε ὀρέγεσαι ὅπὸ εἶναι: |
| [an-a73d22211479-p000301.mark55.r7item53](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark55.r7item53) | Anemi | ok | δεν ἔδωκον ενὸς Φιλοσόφε κἂν δύο δη-<br> | δοῦ ἔδωκαν ενὸς Φιλοσόφες κἂν δύο δη- | δοῦ ἔδωκον οὐὸς Φιλοσόφε κἂν δόο δη- |
| [an-a73d22211479-p000301.mark55.r7item56](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark55.r7item56) | Anemi | ok | ὁ μεγαλόδωρος Βασιλὺς) ἀλλὰ τοῦτο.<br>δεν είναι πολύ, διὰ ενα Αλέξανδρον.<br>Εγὼ μέμφομαι τὸν Αντίγονον διατί<br> | ὁ μεγαλόδωρος Βασιλούς) ἀλλὰ τοῦτο.<br>δεν εἶναι πολὺ διὰ ενα Αλέξανδρον<br>Εγώ μέμφομαι τον Αντίγονον, διατί | δΡΖαΛΣΣΟ, Σὰ ὥα. Ἀλέξανδρον; |
| [an-a73d22211479-p000301.mark56.r7item54](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark56.r7item54) | Anemi | ok | πε. διατί. διδοντάς τα δια να χύη ενα<br>Εἴδωλον, τὰ ἀφιέρωσαν τις διαβόλος.<br>el<br> | πες κατά δίδοντας τα δια να γύη ένα<br>Εἴδωλον, τὰ ἀφιέρωσαν τη διαβόλῳ<br>ο | Εἴδωλον, παὶ ἀφιέρωσαυ τῷ αβόλα. |
| [an-a73d22211479-p000301.mark56.r7item55](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark56.r7item55) | Anemi | ok | ἄλλιζω, όταν ἔφερον ὅσα εἶχον γουσα,<br>ἀργυρά, καὶ γαλκώματα, διὰ νὰ λύη<br> | άλλα όταν<br>New<br>ἔφερον ὅσα εἶχον χρυσα,<br>ἀργυρᾶ, καὶ χαλκώματα, δια να λύ | ἀλλίωγ ὅταυ ἔφερον ἄαα, ρῃ 2 σβν. |
| [an-a73d22211479-p000301.mark56.r7item85](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark56.r7item85) | Anemi | ok | (empty) | (empty) | ν |
| [an-a73d22211479-p000301.mark57.r7item56](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark57.r7item56) | Anemi | ok | ὁ μεγαλόδωρος Βασιλὺς) ἀλλὰ τοῦτο.<br>δεν είναι πολύ, διὰ ενα Αλέξανδρον.<br>Εγὼ μέμφομαι τὸν Αντίγονον διατί<br> | ὁ μεγαλόδωρος Βασιλούς) ἀλλὰ τοῦτο.<br>δεν εἶναι πολὺ διὰ ενα Αλέξανδρον<br>Εγώ μέμφομαι τον Αντίγονον, διατί | δΡΖαΛΣΣΟ, Σὰ ὥα. Ἀλέξανδρον; |
| [an-a73d22211479-p000301.mark57.r7item57](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark57.r7item57) | Anemi | ok | να Στρατιώτίω .ναι· ( τὰ ἀπεκρίθη<br> | να<br>Στρατιώτίω. ναί· ( τὰ ἀπεκρίθη | να Στραπιώπίω… αέ· (Ε ἀπεκρίθη. |
| [an-a73d22211479-p000301.mark61.r7item59](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark61.r7item59) | Anemi | ok | AA<br>κὶ, τότο (εἶπεν) εἶναι πολὺ διὰ ἕν<br>१<br>10<br> | &gt;<br>7870 (επω) είναι πολύ διὰ | κ, σο ( εἶπον) εἶναι πολὴ δια ἔ- |
| [an-a73d22211479-p000301.mark61.r7item61](../../harvest/three_engines_review.html#an-a73d22211479-p000301.mark61.r7item61) | Anemi | ok | πέρμεξον χάρισμα ἐκεῖνος ὁ πτωχός .<br>&quot;<br> | πέρμεξον χάρισμα ἐκεῖνος ὁ πτωχός . | πέρμεζον χάρισμα ἔκεῖνος ἔπτωχος. |
| [an-b9d6f9c086e2-p000162.mark15.r7item13](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000162.mark15.r7item13) | Anemi | ok | νον φανῶν, καὶ λαμπάδων· Αὐλάβεια.<br>..<br>،،<br> | &quot;<br>γων<br>νον φανῶν, καὶ λαμπάδων βλάβεια | νον φάνω», τὰ λαμπαδάν. ὠλάβισα. |
| [an-b9d6f9c086e2-p000162.mark15.r7item15](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000162.mark15.r7item15) | Anemi | ok | 77<br>&quot;<br>Επίδειξις ἀγαθῶν ἔργων. ὄχι μό<br> | 77<br>exp<br>&quot;<br>Επίδειξις ἀγαθῶν ἔργων. ὄχι μόν | ), ὀπίδερτις ἀγαθων ἔργων. ὄχι μό- |
| [an-b9d6f9c086e2-p000162.mark15.r7item17](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000162.mark15.r7item17) | Anemi | ok | 77<br>» χῆς εὐλάβεια, πολιτείας ἀκρίβεια,<br>AI<br>&quot;<br> | χῆς συλάβεια, πολιτείας ἀκρίβεια, | »» χης οὐλάβεια, πολιτείας ἀκοιβεία, |
| [an-b9d6f9c086e2-p000162.mark2.r7item2](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000162.mark2.r7item2) | Anemi | ok | Στο πλησιον μα μουυs marion,<br>να <br>ἐσὺ νὰ ἔχης καρφωμλύα χέρια, κ) πό<br> | το πλησιον με μου<br>ἐσὺ νὰ ἔχης καρφωμα χέρια,<br>&quot;<br>770- | ἐσὺ νὰ ἔχῃς καρφωμβίΣ χέρια, » πο- |
| [an-b9d6f9c086e2-p000162.mark2.r7item4](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000162.mark2.r7item4) | Anemi | ok | 2<br>mandre<br>δίαν και το πλησίον με μίσος αἰώνιον;<br>1<br>il<br>&quot;<br> | δίων<br>24<br>231<br>&quot;<br>&quot;<br>γι<br>πλησίον με μίσος αἰώνιον ;<br>το π | δίαν κξι τὰ πλησίου μέρμισος μιωνιον. |
| [an-b9d6f9c086e2-p000162.mark27.r7item27](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000162.mark27.r7item27) | Anemi | ok | σωριμονι σα<br>010<br>ἔπρεπε νὰ λέγωμῳ, μὰ νὰ τὸ λέγω<br> | σωφρονισα<br>au<br>401<br>2/<br>πρεπε να λέγωμεν, μὰ νὰ τὸ<br>λέγω<br>1 | ἔπρεπε νὰ λέγωμῇι, μὰ νὰ τὸ λέγω. |
| [an-b9d6f9c086e2-p000162.mark3.r7item3](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000162.mark3.r7item3) | Anemi | ok | 201<br>ψανόμμα, ry<br>να, ήξεύρετε τι ἦπν καλλίτερον νὰ κά-<br>77<br> | quatroppa, my w<br>αμα<br>να ηξεύρετε<br>TE TI<br>τί ἦν καλλίτερον νὰ κά<br>TX | σα, ἠξούρετε τί ἦτν καπίπρου νὰ κά- |
| [an-b9d6f9c086e2-p000162.mark3.r7item5](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000162.mark3.r7item5) | Anemi | ok | και πὶ φαινόμθμα, κὰ ἀλλὰ τὰ γινόμε<br>...<br>1<br> | και τα φαινόμενα, καὶ ἄλλα τα γινόμε | ναι πὶ φαινομθυα, κ,’ ἄλα τὰ γινόμε-. |
| [an-b9d6f9c086e2-p000162.mark81.r7item81](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000162.mark81.r7item81) | Anemi | ok | καις ὅπὸ ταῖς μάσιγες, κὶ ἐγω νὰ ἐ-<br> | μ<br>King<br>καις ἀπὸ ταῖς μάσιγες, καὶ ἐγὼ<br>Al | καὶς Σκῦ ταῖς μάςιγες, ἡ ἔχω νὰ ἔ- |
| [an-b9d6f9c086e2-p000255.mark38.r7item36](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark38.r7item36) | Anemi | ok | πὲ ἦτον τέλειος Θεὸς, κὶ τέλειος ανθρω<br> | &gt;<br>πὲ ἦτον τέλειος Θεός, καὶ τέλειος αἴθρω | πε ἦτον πέλειος Θεὸς, κ, τέλειος αὔδρω- |
| [an-b9d6f9c086e2-p000255.mark38.r7item38](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark38.r7item38) | Anemi | ok | τη, μψώντας δεος<br>ο ανθρωπος ετεω<br>θη, μλύωντας ανθρωπος, κὶ ἐκεῖνος, ὁ<br> | JEW.<br>η μυωντας σας ο ανθρωπος εθεω<br>της μύωντας ανθρωπος, καὶ ἐκεῖνος, ό-<br>31- | δη, Σμθύωνπας αὔδρωπος,  ἔκεινος,ο- |
| [an-b9d6f9c086e2-p000255.mark38.r7item40](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark38.r7item40) | Anemi | ok | θη, μλύωντας Θεός· ὁ αἴθρωπος ἐθεώ<br> | Θη, μύωντας Θεός· ὁ αἴθρωπος ἐθεώ | 8η· μθύωντας Θεός· ὁ αὔδρωπος ἐΘεω- |
| [an-b9d6f9c086e2-p000255.mark39.r7item39](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark39.r7item39) | Anemi | ok | 125/2 <br>JCHOV, NY ταυτον απειρανορον, α!<br>ἔτζι ἔπορεπον, ὅτι ἐκεῖνος ὁ μονογλωὴς<br> | JCOV και ταυτον απομανδρον, εχατι<br>ἔτζι ἔπρεπεν, ὅτι ἐκεῖνος ὁ μοναιχμής | ἔτζι ἔπρεπου ὅτι ἔκεῖνος ὁ μονευρὴς |
| [an-b9d6f9c086e2-p000255.mark39.r7item41](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark39.r7item41) | Anemi | ok | θείον, καὶ ταύτίω ἀπείρανδρον, εχατί<br> | θεον, καὶ ταύτίω ἀπείρανδρον, χατὶ | δούον, καὶ ταύτίυ ἀπεήρανδρον, ἐατε |
| [an-b9d6f9c086e2-p000255.mark46.r7item45](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark46.r7item45) | Anemi | ok | לי<br>VII<br>Θεὸς ἐξάπη εἰς αὐθρωπον, ὅτε ὁ αν<br>,<br> | &quot;<br>ετε ὁ αν<br>Θεὸς ἐβάπη εἰς ανθρωπον, ἔτε<br>&#x27; | Θεὸς ἔξαπν ες ὤφρωπον, ὅτε ὁ αὔ-! |
| [an-b9d6f9c086e2-p000255.mark46.r7item46](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark46.r7item46) | Anemi | ok | νᾶται ἀλλόνως, εἰς φόπον ὅτι ὅἔτε ὁ<br>/c<br>k<br>১<br> | κᾶται ἀλόνως<br>ἀλλόνως, εἰς τόπον ὅτι ἔτε ὁ<br>3/<br>&quot; | κᾶται ἀχρόνως, εἰς ξόπον ὅτι ἄτε ὁ |
| [an-b9d6f9c086e2-p000255.mark46.r7item48](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark46.r7item48) | Anemi | ok | 7<br>φοραν λυτᾶται χρονικῶς τὰ παύτοτε θυ-<br>&quot;<br>5<br> | φοραν κανᾶται χρονικῶς καὶ παύτοτε κυ<br>7!<br>&quot; | φοραὺ φφναται χρονικως ἡ παύτοτε ὀθυ- |
| [an-b9d6f9c086e2-p000255.mark48.r7item46](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark48.r7item46) | Anemi | ok | νᾶται ἀλλόνως, εἰς φόπον ὅτι ὅἔτε ὁ<br>/c<br>k<br>১<br> | κᾶται ἀλόνως<br>ἀλλόνως, εἰς τόπον ὅτι ἔτε ὁ<br>3/<br>&quot; | κᾶται ἀχρόνως, εἰς ξόπον ὅτι ἄτε ὁ |
| [an-b9d6f9c086e2-p000255.mark48.r7item48](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark48.r7item48) | Anemi | ok | 7<br>φοραν λυτᾶται χρονικῶς τὰ παύτοτε θυ-<br>&quot;<br>5<br> | φοραν κανᾶται χρονικῶς καὶ παύτοτε κυ<br>7!<br>&quot; | φοραὺ φφναται χρονικως ἡ παύτοτε ὀθυ- |
| [an-b9d6f9c086e2-p000255.mark63.r7item63](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark63.r7item63) | Anemi | ok | &quot;<br>ἡ<br>do<br>κὸς, ἡ σύςασις ἐκλύετο της Καρίῳ.<br>&quot;<br> | 37<br>γουιν<br>99<br>κός, ἡ σύςασις εκλύετο της Κυρία. | ), κὸς, ἡ σύφασις ἐνθύεπο τῷ. Κωρίῳ. |
| [an-b9d6f9c086e2-p000255.mark63.r7item65](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark63.r7item65) | Anemi | ok | -<br>77<br>» 2ο &amp; και τιὶ κοινίω φύσιν τῆς σαρ<br>&quot; 1<br> | δε και των κοινω φύσιν τῆς σαρ<br>&quot; | ο, δὸ ἀ χῆ τύει κοινίο φύσιν πης σαρ- |
| [an-b9d6f9c086e2-p000255.mark69.r7item67](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark69.r7item67) | Anemi | ok | 77<br>γῳ εἰς τὸ Γεύνησιν το Χρισ8. „ Καὶ<br> | 77<br>γῳ εἰς τὰ Γεύνησιν το Χρισέ. Καὶ<br>Xess., | ἤῳ εἰς τίω Γούνησιν n Χρχss.» Καὶ |
| [an-b9d6f9c086e2-p000255.mark69.r7item69](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark69.r7item69) | Anemi | ok | » θον, λέγει ὁ μέγας Βασίλειος λό<br> | &quot;<br>&quot;<br>θα, λέγει ὁ μέγας Βασίλειος λό | »» δοὐ, λέγει ὁ μέγας Βασίλειος λό- |
| [an-b9d6f9c086e2-p000255.mark69.r7item71](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark69.r7item71) | Anemi | ok | » ταῖς και μικρὸν διαπλάσεσι μορφω<br>a.!<br>-<br> | &quot;<br>&quot;<br>» ταῖς καὶ μικρὸν διαπλάσεσι μόρφω<br>a.!<br>Βασίλης λε | » ταις φ’ μῖκρὸν δαπλάσεσι μορφω- |
| [an-b9d6f9c086e2-p000255.mark7.r7item5](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark7.r7item5) | Anemi | ok | κει, ὅτι ἡ ενωσις ἐκείνη τὴς δύο φύ-<br> | κει, ὅτι ἡ εἴωσις ἐκείνη τὴν δύο φύ | κει; ὅτη ἡ σὕωσις ἐκείνη τῆῇ δύο φύ- |
| [an-b9d6f9c086e2-p000255.mark7.r7item7](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark7.r7item7) | Anemi | ok | μονάδα<br>ααφορετικών, μόναι<br>προσώπε, κι δυάδα φύσεων. μᾶς διδάσ<br>ὅτι ἡ ενωσις έκεί. 28<br> | καψορες ιπων<br>apopes<br>η μοναδα<br>προσώπε, καὶ δυάδα φύσεων . μᾶς διδάσ<br>ὅτι ἡ οίωσις ἐκείνα τε κα<br>X61. | προσωπο, ἡ δυάδα φύσεων, μᾶς διδάσ- |
| [an-b9d6f9c086e2-p000255.mark70.r7item68](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark70.r7item68) | Anemi | ok | μαρι<br>παρεσιμεβλήθη τοῖς κτιύεσι τοῖς ἀ-<br>2<br>16.<br> | παρεσυνεβλήθη τοῖς κτιώύεσι τοῖς ἀ<br>Τι | »» παρεσιμυεβλήδν τπις κτμώεσι ποις α- |
| [an-b9d6f9c086e2-p000255.mark70.r7item70](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark70.r7item70) | Anemi | ok | 6<br>αἴθρωπος, ὅταν διὰ τὴ ἁμαρτίαν<br>2<br>2<br> | , τις σω<br>ανθρωπος, ὅταν δια των αμαρτίαν | αἴδρωπος, ὅταν ὶ τίυ ἀμαρτίαυ. |
| [an-b9d6f9c086e2-p000255.mark8.r7item11](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark8.r7item11) | Anemi | ok | ἄλλη μία ἄβυπος αδαδόξων θαυμά-<br> | ἄλλη μία ἄβυσος αναδόξων θαυμά | ἄλλη μέα ἄβυσος «Φαδόζων θαυμά- |
| [an-b9d6f9c086e2-p000255.mark8.r7item8](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000255.mark8.r7item8) | Anemi | ok | 2<br>αλλη μια αφυπος ανρφοοζων ταυμα-<br>ὅτι Χρισὸς Γητες ( λέγει ὁ<br>των<br>&quot;<br> | των<br>TT<br>μια αρβυλος ανοισος των θαυμά<br>ὅτι Χριςός Ιησάς ( λέγει ὁ<br>9. | πων κ, ὅτι Χειτὸς 7χοξξ; λέγι ὁ |
| [an-b9d6f9c086e2-p000370.mark15.r7item12](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000370.mark15.r7item12) | Anemi | ok | γιων σ<br>κὰ Θασματαργόν ταύτίω Εἰκόνα· ἔτζε<br>ta<br> | για σ<br>και θαυματαργὸν ταύτων Εἰκόνα· ἔτζι | 2 Θαυμααργὸν παύτῶω Βικόνα· ἔτζε |
| [an-b9d6f9c086e2-p000370.mark15.r7item14](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000370.mark15.r7item14) | Anemi | ok | Αὐλαβῶς ἀσπαζόμεθα τίω Αγίαν σε<br> | βλαβῶς ἀσπαζόμεθα των Αγίων σε | ΑΔΔΕς ΜπΑζόμεΣα ΤΙΗΣ Αφία»σα |
| [an-b9d6f9c086e2-p000370.mark29.r7item26](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000370.mark29.r7item26) | Anemi | ok | ναι ἡ χαρά, ἡ παρηγορία, τὸ καύχη<br>2<br> | και η χαρά, ἡ παρηγορία, το καύχη<br>todown to h<br>TAT<br>201 | ναι ἡ χαρὰ, ἡ παρανορία, τὸ καάχη- |
| [an-b9d6f9c086e2-p000370.mark29.r7item28](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000370.mark29.r7item28) | Anemi | ok | -<br>-<br>γία Παρθείς Μαρία, ὄνομα, ὁπὲ εἶ-<br> | γία Παρθούς Μαρία, ὄνομα, ὑπὲ εἶ | γία Παρῶοζε Μαρία, ἤνομα, ἀπᾶ εἶ- |
| [an-b9d6f9c086e2-p000370.mark5.r7item3](../../harvest/three_engines_review.html#an-b9d6f9c086e2-p000370.mark5.r7item3) | Anemi | ok | τὲς ἀπεραύτες αἰῶνας. Αμιώ.<br> | τις απεραντος αιώνας. Α&#x27;μία. | τὲς ἀπεραύως μώνας. Ἀμείεε- |
| [an-d3237d690aa0-p000138.mark170.r7item170](../../harvest/three_engines_review.html#an-d3237d690aa0-p000138.mark170.r7item170) | Anemi | ok | μάρανον - β΄.<br> | μαμαπ γ.<br>μάρατον. β&#x27;. | μάραυον β΄. |
| [an-d3237d690aa0-p000138.mark170.r7item172](../../harvest/three_engines_review.html#an-d3237d690aa0-p000138.mark170.r7item172) | Anemi | ok | μαρανη. γ.<br> | μαρανη. γ. | μμαραύη. 2. |
| [an-d3237d690aa0-p000138.mark64.r7item64](../../harvest/three_engines_review.html#an-d3237d690aa0-p000138.mark64.r7item64) | Anemi | ok | μαργιανή. γ&#x27;.<br> | μαργιανή . γ.<br>• | μαρφιαυὴ. λ.. |
| [an-d83e7a198ade-p000099.mark13.r7item11](../../harvest/three_engines_review.html#an-d83e7a198ade-p000099.mark13.r7item11) | Anemi | ok | nduvans for Lamen<br>mo<br>• 286 ΤΑ. Οὐ καταπλαγείς, ὁ φοβη- λωθείς τιὺ ὀρμἰὼ τοῦ ἤρωος ὁ Πανδα-<br> | www<br>286 ΤΑ. Οὐ καταπλαγές,<br>φοβη. λωθείς τω όρμω του ήρωος ὁ Πανδα | 2δο ΤΑ. Οὐ καπαπλαζες; Ὁ βορη. λωθᾶς τῶ ὁσμῶω Ὤυ ἤρωος ὁ Παώδα- |
| [an-d83e7a198ade-p000099.mark13.r7item13](../../harvest/three_engines_review.html#an-d83e7a198ade-p000099.mark13.r7item13) | Anemi | ok | δίω εἀφ᾽ ὕψες βεβληκεναι. Η, ότι, δεις<br> | Wye ngu 07 suo paes<br>δω εφ&#x27; ύψος βεβληκεναι. Η, ὅτι, δεν | δίω αφ’ ὕψας βεβληκούα. Ἡ, ὅσι; δε- |
| [an-d83e7a198ade-p000099.mark13.r7item17](../../harvest/three_engines_review.html#an-d83e7a198ade-p000099.mark13.r7item17) | Anemi | ok | · μετεώρο μάχεθαι, ὥσε καὶ τὸν Διομή<br>......... MET<br> | - με ώρες μάχεται, ώςε καὶ τὸν Διομή<br>N... 05 __ MIJ<br>--<br>In | μεπώρᾳ μαχεθαι, ὥςε κα, ῶν Διομή- |
| [an-d83e7a198ade-p000099.mark17.r7item13](../../harvest/three_engines_review.html#an-d83e7a198ade-p000099.mark17.r7item13) | Anemi | ok | δίω εἀφ᾽ ὕψες βεβληκεναι. Η, ότι, δεις<br> | Wye ngu 07 suo paes<br>δω εφ&#x27; ύψος βεβληκεναι. Η, ὅτι, δεν | δίω αφ’ ὕψας βεβληκούα. Ἡ, ὅσι; δε- |
| [an-d83e7a198ade-p000099.mark17.r7item17](../../harvest/three_engines_review.html#an-d83e7a198ade-p000099.mark17.r7item17) | Anemi | ok | · μετεώρο μάχεθαι, ὥσε καὶ τὸν Διομή<br>......... MET<br> | - με ώρες μάχεται, ώςε καὶ τὸν Διομή<br>N... 05 __ MIJ<br>--<br>In | μεπώρᾳ μαχεθαι, ὥςε κα, ῶν Διομή- |
| [an-d83e7a198ade-p000099.mark20.r7item20](../../harvest/three_engines_review.html#an-d83e7a198ade-p000099.mark20.r7item20) | Anemi | ok | TW<br>πρὸς τὸ αὐατείνειν τις πιβάτη.<br> | πρὸς τὸ ανατείνειν την επιβάτη. | φὸς ὰ ὐατείνεν ταἱ λιβάτη. |
| [an-d83e7a198ade-p000099.mark20.r7item23](../../harvest/three_engines_review.html#an-d83e7a198ade-p000099.mark20.r7item23) | Anemi | ok | κλό, τὸ παραπεπηγότος ἐν τῷ ἄρματι<br> | 32<br>κλο, τα παραπεπηγότες ἐν τῷ ἅρματι | κλε; ὰ παραπεπηγόος ὃν τῦ ἄρματι |
| [an-d83e7a198ade-p000099.mark46.r7item42](../../harvest/three_engines_review.html#an-d83e7a198ade-p000099.mark46.r7item42) | Anemi | ok | ποιήσαι. Ἔπειθ&#x27;, ὅτι προσεπινεύσας ὁ<br> | ww<br>ποιῆσαι. Ἔπειθ&#x27;, ἔτι προσεπινεύσας ὁ | ποιλσαι. Ἐπειθ’» δαι προσεπινεύσας ὁ |
| [an-d83e7a198ade-p000099.mark46.r7item46](../../harvest/three_engines_review.html#an-d83e7a198ade-p000099.mark46.r7item46) | Anemi | ok | τιθιιύουσα αὐτὸς ἢ δυνατὸν ἰὦ τοῦτο<br>WK<br>P<br> | &quot;<br>το θεουσα αυτό, ο δυνατόν με τοῦτο<br>ω | τέθθιώουσα αὐτὸς ἱ δεωατὸν αῦ πῦο |
| [an-d83e7a198ade-p000099.mark46.r7item50](../../harvest/three_engines_review.html#an-d83e7a198ade-p000099.mark46.r7item50) | Anemi | ok | 5<br>sww.<br>ه رمد<br>γειν, ὅτι πορῶτον μὲν ᾿Αθίωὰ ζῶ ἡ κα<br> | 746<br>γειν, ὅτι πρῶτον μυ Αθω τ ω ἡ και | γαν, ὅτι φρῶον μᾷ) ἈΦλωᾶ αῶ ἡ κα- |
| [an-e74539ae215c-p000633.mark70.r7item70](../../harvest/three_engines_review.html#an-e74539ae215c-p000633.mark70.r7item70) | Anemi | ok | (empty) | (empty) | (empty) |
| [s2-200e977f2dab5291c42c-p00025.mark14.r7item14](../../harvest/three_engines_review.html#s2-200e977f2dab5291c42c-p00025.mark14.r7item14) | Vouli | ok | 7,821 78<br> | 7,821 78 | 7821 78 |
| [s2-200e977f2dab5291c42c-p00025.mark14.r7item19](../../harvest/three_engines_review.html#s2-200e977f2dab5291c42c-p00025.mark14.r7item19) | Vouli | ok | 3,945 13<br> | 3,945 13 | 3,945 181 |
| [s2-200e977f2dab5291c42c-p00025.mark68.r7item68](../../harvest/three_engines_review.html#s2-200e977f2dab5291c42c-p00025.mark68.r7item68) | Vouli | ok | 16<br> | 16 | 6 |
| [s2-200e977f2dab5291c42c-p00025.mark9.r7item9](../../harvest/three_engines_review.html#s2-200e977f2dab5291c42c-p00025.mark9.r7item9) | Vouli | ok | 30<br> | 30 | 180 |
| [s2-200e977f2dab5291c42c-p00035.mark10.r7item10](../../harvest/three_engines_review.html#s2-200e977f2dab5291c42c-p00035.mark10.r7item10) | Vouli | ok | 38<br> | 38 | 188 |
| [s2-200e977f2dab5291c42c-p00035.mark10.r7item18](../../harvest/three_engines_review.html#s2-200e977f2dab5291c42c-p00035.mark10.r7item18) | Vouli | ok | 36<br>37<br> | 33<br>36<br>37 | 187! |
| [s2-200e977f2dab5291c42c-p00035.mark113.r7item113](../../harvest/three_engines_review.html#s2-200e977f2dab5291c42c-p00035.mark113.r7item113) | Vouli | ok | 17<br> | 17 | 7 |
| [s2-200e977f2dab5291c42c-p00035.mark113.r7item122](../../harvest/three_engines_review.html#s2-200e977f2dab5291c42c-p00035.mark113.r7item122) | Vouli | ok | 15<br>16<br> | 15<br>5C<br>16 | 1181 |
| [s2-200e977f2dab5291c42c-p00035.mark122.r7item122](../../harvest/three_engines_review.html#s2-200e977f2dab5291c42c-p00035.mark122.r7item122) | Vouli | ok | 15<br>16<br> | 15<br>5C<br>16 | 1181 |
| [s2-200e977f2dab5291c42c-p00035.mark18.r7item18](../../harvest/three_engines_review.html#s2-200e977f2dab5291c42c-p00035.mark18.r7item18) | Vouli | ok | 36<br>37<br> | 33<br>36<br>37 | 187! |
| [s2-200e977f2dab5291c42c-p00035.mark73.r7item73](../../harvest/three_engines_review.html#s2-200e977f2dab5291c42c-p00035.mark73.r7item73) | Vouli | ok | 25<br> | 25 | 25 |
| [s2-200e977f2dab5291c42c-p00035.mark78.r7item78](../../harvest/three_engines_review.html#s2-200e977f2dab5291c42c-p00035.mark78.r7item78) | Vouli | ok | 24<br> | 24 | 24 |
| [s2-200e977f2dab5291c42c-p00035.mark83.r7item83](../../harvest/three_engines_review.html#s2-200e977f2dab5291c42c-p00035.mark83.r7item83) | Vouli | ok | 23<br> | 23 | 28 |
| [s2-31f40cef90235c91b023-p00001.mark18.r7item18](../../harvest/three_engines_review.html#s2-31f40cef90235c91b023-p00001.mark18.r7item18) | Vouli | ok | доха ровал ох З ἐπὶ τῶν Ἐξωτερικῶν Ὑπουργός<br>G<br> | 90xA<br>Hyrgos<br>20020<br>ΟΧΑ Φοβολεί τα ἐπὶ τῶν Ἐξωτερικῶν Υπουργός | . . ῶν Ἐξωτερικῶν Ὑπουργός |
| [s2-31f40cef90235c91b023-p00001.mark42.r7item42](../../harvest/three_engines_review.html#s2-31f40cef90235c91b023-p00001.mark42.r7item42) | Vouli | ok | Ο ΣΧΕΔΙΟΝ O Cowor<br> | ΚΕΑ: ΣΧΕΔΙΟΝ ΝΟΜΟΥ TS Toov | ΣΧΕΣΤΟΝ ΝΟΜΟΥ |
| [s2-31f40cef90235c91b023-p00001.mark63.r7item59](../../harvest/three_engines_review.html#s2-31f40cef90235c91b023-p00001.mark63.r7item59) | Vouli | ok | κουσα πρόσθετος Σύμβασις.<br> | κουσα πρόσθετος Σύμβασις. | κουσα πρόσθετος Σύμβασις.» |
| [s2-3229200bf47ca465a42d-p00002.mark0.r7item12](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark0.r7item12) | Vouli | ok | λὴν καὶ τὴν κυβέρνησιν ὅπως λάβη πρόνοιαν περὶ τῶν γεωρ-<br> | Τὴν καὶ τὴν κυβέρνησιν ὅπως λάβη πρόνοιαν περὶ τῶν·<br>γεωρ | ΥΙΝ ΜΕίνησιν ὅπως άβῃ πρόνοιαν περι τῶν γεωρ- |
| [s2-3229200bf47ca465a42d-p00002.mark10.r7item17](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark10.r7item17) | Vouli | ok | νουαρίου 1888 εἰσφορὰ τῶν δήμων θέλει πληρώνεσθαι και<br> | νουαρίου 1888 εἰσφορὰ τῶν δήμων θέλει πληρώνεσθαι | ΣΕΙΟυ 888 εἰσφορὰ τῶν δήμων θέλει πληρῶνεσθαι καὶ |
| [s2-3229200bf47ca465a42d-p00002.mark10.r7item5](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark10.r7item5) | Vouli | ok | 2) Να πληροφορήση την Βουλην αν π<br>nava<br>β΄ τοῦ ἄρθρου 2 τοῦ τροποποιηθέντος νόμου τῆς 9 Ια-<br> | * Να πληροφορήση την Βουλήν αν<br>Β&#x27; τοῦ ἄρθρου 2 του τροποποιηθέντος νόμου τῆς 9 τα | Δ ΣΟΣ ΣΡΙΕΟΝ 2Ρ ΟΣΟΣ ΤΕΟΧΟΡΟΙΝΟΣΝΟΥ ΝμΟυ ΤΗ Α. α- |
| [s2-3229200bf47ca465a42d-p00002.mark17.r7item20](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark17.r7item20) | Vouli | ok | νόμου περί καταργήσεως τῆς προσωπικῆς κρατήσεως.<br> | νόμου περὶ καταργήσεως τῆς προσωπικῆς κρατήσεως. | νμου περὶ καταργήσεως τῆς προσωπικῆς κρατήσεως. |
| [s2-3229200bf47ca465a42d-p00002.mark22.r7item24](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark22.r7item24) | Vouli | ok | Στρατιωτικῶν καὶ Ἐπ. Πετιμεζᾶ ἀντισυνταγματάρχου καὶ<br> | Στρατιωτικῶν καὶ Ἐπ. Πετιμεζά ἀντισυνταγματάρχου κα | ΣΕΕιωτικῶν καὶ Ἐπ. Πετιμεζὰ ἀντισυνταγματάρχου καὶ |
| [s2-3229200bf47ca465a42d-p00002.mark22.r7item25](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark22.r7item25) | Vouli | ok | λέγκου κατὰ Χαριλάου Τρικούπη, πρώην Ὑπουργοῦ τῶν<br> | λέγκου κατὰ Χαριλάου Τρικούπη, πρώην Υπουργού<br>τῶν | ΥyΣου κατὰ Χαριλάου Τρικούπη, πρῶην Ὑπουργοῦ τῶν |
| [s2-3229200bf47ca465a42d-p00002.mark22.r7item9](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark22.r7item9) | Vouli | ok | TA<br>πρώην διευθυντοῦ τοῦ δικαστικοῦ τμήματος τοῦ ἐπὶ τῶν<br> | τικών και<br>176.<br>πρώην διευθυντοῦ τοῦ δικαστικοῦ τμήματος τοῦ ἐπὶ τῶν | ΕΔΝ ΣυΜΟΣαψ οὗ οικαστικοῦ ιήματος Τοῦ ἐπὶ τῶν |
| [s2-3229200bf47ca465a42d-p00002.mark23.r7item25](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark23.r7item25) | Vouli | ok | λέγκου κατὰ Χαριλάου Τρικούπη, πρώην Ὑπουργοῦ τῶν<br> | λέγκου κατὰ Χαριλάου Τρικούπη, πρώην Υπουργού<br>τῶν | ΥyΣου κατὰ Χαριλάου Τρικούπη, πρῶην Ὑπουργοῦ τῶν |
| [s2-3229200bf47ca465a42d-p00002.mark23.r7item26](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark23.r7item26) | Vouli | ok | λειοδικῶν διαβιβάζοντος μήνυσιν τοῦ Παναγιώτου Περ-<br> | λειοδικῶν διαβιβάζοντος μήνυσιν τοῦ Παναγιώτου Περ- | Λειοδικῶν διαβιβάζοντος μήνυσιν τοῦ Παναγιώτου Περ- |
| [s2-3229200bf47ca465a42d-p00002.mark5.r7item1](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark5.r7item1) | Vouli | ok | τινας ἐπαρχίας νὰ ὑπάρχωσι δημοδιδάσκαλοι ἀναλογοῦν<br> | τίνας<br>μαθητών τις απαντο<br>ἐπαρχίας νὰ ὑπάρχωσι δημοδιδάσκαλοι αναλογούν<br>100<br>9 | ΣΝας ΙΧΩΡΧΙΗΥΝΟ ὑάχωσι ΣΜοδιδάσχαλοι ἀναλογοῦν- |
| [s2-3229200bf47ca465a42d-p00002.mark5.r7item15](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark5.r7item15) | Vouli | ok | σκάλων, διανεμηθῶσιν ἅπαντες οἱ ὑπάρχοντες κατ᾿ ἀναλο-<br> | σκάλων, διανεμηθῶσιν ἅπαντες οἱ ὑπάρχοντες κατ&#x27; αναλο | «ᾶλων διανεμηθῶσιν ἄπαντες οἱ ὑπάρχοντες κατ’ ἄναλο- |
| [s2-3229200bf47ca465a42d-p00002.mark5.r7item2](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark5.r7item2) | Vouli | ok | γίαν τῶν μαθητῶν εἰς ἅπαντα τὰ σχολεῖα καὶ οὐχὶ εἴς<br> | γίαν τῶν μαθητῶν εἰς ἅπαντα τὰ σχολεῖα καὶ οὐχὶ εἰς | ΙαΝΤΕμΝΕΕΙ ἀπαΑ ΑΟλΙᾳ καΙ Ουχὶ, εἰς |
| [s2-3229200bf47ca465a42d-p00002.mark6.r7item15](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark6.r7item15) | Vouli | ok | σκάλων, διανεμηθῶσιν ἅπαντες οἱ ὑπάρχοντες κατ᾿ ἀναλο-<br> | σκάλων, διανεμηθῶσιν ἅπαντες οἱ ὑπάρχοντες κατ&#x27; αναλο | «ᾶλων διανεμηθῶσιν ἄπαντες οἱ ὑπάρχοντες κατ’ ἄναλο- |
| [s2-3229200bf47ca465a42d-p00002.mark6.r7item3](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark6.r7item3) | Vouli | ok | 2) Νὰ λάβῃ προνοιαν ὅπως ἔνεκεν ἐλλείψεως δημοδιδα-<br> | 2) Να λάβῃ προνοιαν ὅπως ἕνεκεν ἐλλείψεως δημοδιδα | 2Ι ΝΗΜΟΗ προνθιαν ὅπως ἔνεκεν ἐλλείψεως Σημοδιδα- |
| [s2-3229200bf47ca465a42d-p00002.mark7.r7item3](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark7.r7item3) | Vouli | ok | 2) Νὰ λάβῃ προνοιαν ὅπως ἔνεκεν ἐλλείψεως δημοδιδα-<br> | 2) Να λάβῃ προνοιαν ὅπως ἕνεκεν ἐλλείψεως δημοδιδα | 2Ι ΝΗΜΟΗ προνθιαν ὅπως ἔνεκεν ἐλλείψεως Σημοδιδα- |
| [s2-3229200bf47ca465a42d-p00002.mark7.r7item38](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark7.r7item38) | Vouli | ok | (empty) | (empty) | (empty) |
| [s2-3229200bf47ca465a42d-p00002.mark7.r7item4](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark7.r7item4) | Vouli | ok | λειτουργοῦσι τὰ σχολεῖα ἐλλείψει προσωπικοῦ.<br> | · λειτουργοῦσι τὰ σχολεῖα ἐλλείψει προσωπικοῦ. | ΛΗΟΡΟῦσι ΤΑ ΣχΟλΝα ἐλλείψει πεδσωπικοῦ. |
| [s2-3229200bf47ca465a42d-p00002.mark8.r7item16](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark8.r7item16) | Vouli | ok | εἰς περίστασιν καθ&#x27; ἣν κατὰ τὸ πλεῖστον τοῦ ἔτους δὲν<br> | εἰς περίστασιν καθ᾽ ἣν κατὰ τὸ πλεῖστον τοῦ ἔτους δεν | εςΤΕστασιν καθ’ ἦν κατὰ τὸ πλεῖστον τοῦ ἑτους δὲν |
| [s2-3229200bf47ca465a42d-p00002.mark8.r7item4](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark8.r7item4) | Vouli | ok | λειτουργοῦσι τὰ σχολεῖα ἐλλείψει προσωπικοῦ.<br> | · λειτουργοῦσι τὰ σχολεῖα ἐλλείψει προσωπικοῦ. | ΛΗΟΡΟῦσι ΤΑ ΣχΟλΝα ἐλλείψει πεδσωπικοῦ. |
| [s2-3229200bf47ca465a42d-p00002.mark9.r7item16](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark9.r7item16) | Vouli | ok | εἰς περίστασιν καθ&#x27; ἣν κατὰ τὸ πλεῖστον τοῦ ἔτους δὲν<br> | εἰς περίστασιν καθ᾽ ἣν κατὰ τὸ πλεῖστον τοῦ ἔτους δεν | εςΤΕστασιν καθ’ ἦν κατὰ τὸ πλεῖστον τοῦ ἑτους δὲν |
| [s2-3229200bf47ca465a42d-p00002.mark9.r7item17](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00002.mark9.r7item17) | Vouli | ok | νουαρίου 1888 εἰσφορὰ τῶν δήμων θέλει πληρώνεσθαι και<br> | νουαρίου 1888 εἰσφορὰ τῶν δήμων θέλει πληρώνεσθαι | ΣΕΙΟυ 888 εἰσφορὰ τῶν δήμων θέλει πληρῶνεσθαι καὶ |
| [s2-3229200bf47ca465a42d-p00003.mark13.r7item13](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00003.mark13.r7item13) | Vouli | ok | χρεώθησαν νὰ πληρώνωσι φόρον ἐξαγωγῆς καὶ διὰ τὸν ἐξ<br> | συναρπών εν Πάτραις οι τινες αδίκως<br>χρεώθησαν νὰ πληρώνωσι φόρον ἐξαγωγῆς καὶ διὰ τὸν | χρεώθησαν νὰ πληρώνωσι φόρον ἐξαγωγῆς καὶ διὰ τὸν ἔξ |
| [s2-3229200bf47ca465a42d-p00003.mark13.r7item14](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00003.mark13.r7item14) | Vouli | ok | μένων τὸν σταφιδοκαρπὸν ἐν Πάτραις οἵτινες ἀδίκως ὑπε<br> | ανωμαιωνων των εν<br>μένων τὸν σταφιδοκαρπὸν ἐν Πάτραις οἵτινες ἀδίκως ὑπὲρ | ένων τὸν σταφιδοκαρπὸν ἐν Πάτοαις οἵτινες ἀδίκως ὑπέ- |
| [s2-3229200bf47ca465a42d-p00003.mark4.r7item3](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00003.mark4.r7item3) | Vouli | ok | 2000VV210000<br>τὰς δεούσας ὁδηγίας, φυτὰ καὶ σπόρους καταλλήλους πρὸς<br> | τὰς δεούσας ὁδηγίας, φυτὰ καὶ σπόρους καταλλήλους πρὸς | τὰς δεούσας ὀδηγίας, φυτὰ καὶ σπόρους καταλλήλους πρὸς |
| [s2-3229200bf47ca465a42d-p00003.mark4.r7item4](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00003.mark4.r7item4) | Vouli | ok | 20101100 lione sa<br>madharo sade radiar<br>τῶν γεωργῶν ἐν τῷ ἔργῳ αὐτῶν, ἀποστέλλουσα αὐτοῖς<br>A<br> | madzero sada odiarano l&#x27;es<br>· τῶν γεωργῶν ἐν τῷ ἔργῳ αὐτῶν, ἀποστέλλουσα αὐτοῖς | τῶν γεωργῶν ἐν τῷ ἔργῳ αὐτῶν, ἀποστέλλουσα αὐτοῖα |
| [s2-3229200bf47ca465a42d-p00003.mark4.r7item5](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00003.mark4.r7item5) | Vouli | ok | COι ακαρνανιας συνου<br>τῇ κυβερνήσει ὅπως λάβη σύντονα μέτρα πρὸς διαφώτισιν<br> | ακαρνανίας<br>τῇ κυβερνήσει ὅπως λάβῃ σύντονα μέτρα πρὸς διαφώτισιν | τῇ κυβερνήσει ὅπως λάβῃ σύντονα μέτρα πρὸς διαφώτισιν |
| [s2-3229200bf47ca465a42d-p00004.mark0.r7item0](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00004.mark0.r7item0) | Vouli | ok | κειμένης της λησεως της παρουσι<br>καὶ προέτεινε τὴν ἀναβολὴν τῆς ἐκλογῆς τῆς ἐπιτροπῆς.<br>ال<br> | μένης της λήξεως της πήραν<br>καὶ προέτεινε τὴν ἀναβολὴν τῆς ἐκλογῆς τῆς ἐπιτροπῆς. | καὶ προέτεινε τὴν ἀναβολὴν τῆς ἐκλογῆς τῆς ἐπιτροπῆς. |
| [s2-3229200bf47ca465a42d-p00004.mark0.r7item26](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00004.mark0.r7item26) | Vouli | ok | Εἰς τοῦτο συνεφώνησε, μετά<br>τίνα<br>συζήτησιν, καὶ ὁ Πρόε<br> | Εἰς τοῦτο συνεφώνησε, μετά τινα συζήτησιν, καὶ ὁ Πρόε- | ΕΓΒο σμεφώνησι, μετά Τίνα συζήπωι» καὶ ὁ Πρόξ- |
| [s2-3229200bf47ca465a42d-p00004.mark1.r7item0](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00004.mark1.r7item0) | Vouli | ok | κειμένης της λησεως της παρουσι<br>καὶ προέτεινε τὴν ἀναβολὴν τῆς ἐκλογῆς τῆς ἐπιτροπῆς.<br>ال<br> | μένης της λήξεως της πήραν<br>καὶ προέτεινε τὴν ἀναβολὴν τῆς ἐκλογῆς τῆς ἐπιτροπῆς. | καὶ προέτεινε τὴν ἀναβολὴν τῆς ἐκλογῆς τῆς ἐπιτροπῆς. |
| [s2-3229200bf47ca465a42d-p00004.mark18.r7item17](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00004.mark18.r7item17) | Vouli | ok | ·μοκειμένου είται να εισέχνη η μο<br>διάταξιν εἷς τῶν Βουλευτῶν Μεσσηνίας προέτεινεν ὅπως<br> | οκειμένου είτα να εισέλθη<br>Η διάταξιν εἷς τῶν Βουλευτῶν Μεσσηνίας προέτεινεν ὅπως | ΔΚΣαξΝ ΗΥ ΣΔΟΥ ΚουΧυΗν ΤΗΣΣΜΗ. ΤΡέπειΝ» ὅπως. |
| [s2-3229200bf47ca465a42d-p00004.mark18.r7item27](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00004.mark18.r7item27) | Vouli | ok | προταχθῇ ἐν αὐτῇ τὸ νομοσχέδιον περί τροποποιήσεως τοῦ<br> | προταχθῇ ἐν αὐτῇ τὸ νομοσχέδιον περὶ τροποποιήσεως τοῦ | ΞΕΣΜΜἐν αὐτῇ τὸ ομοσχέδιον περὶ τροποποιήσως τοῦ |
| [s2-3229200bf47ca465a42d-p00004.mark19.r7item17](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00004.mark19.r7item17) | Vouli | ok | ·μοκειμένου είται να εισέχνη η μο<br>διάταξιν εἷς τῶν Βουλευτῶν Μεσσηνίας προέτεινεν ὅπως<br> | οκειμένου είτα να εισέλθη<br>Η διάταξιν εἷς τῶν Βουλευτῶν Μεσσηνίας προέτεινεν ὅπως | ΔΚΣαξΝ ΗΥ ΣΔΟΥ ΚουΧυΗν ΤΗΣΣΜΗ. ΤΡέπειΝ» ὅπως. |
| [s2-3229200bf47ca465a42d-p00004.mark19.r7item28](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00004.mark19.r7item28) | Vouli | ok | Προκειμένου εἶτα·νὰ εἰσέλθῃ ἡ Βουλὴ εἰς τὴν ἡμερησίαν<br> | Προκειμένου εἶπα νὰ εἰσέλθῃ ἡ βουλὴ εἰς τὴν ἡμερησίαν | ΠΕΧεΠίνου εἶτα νὰ εἰσέλθῃ ἡ Βουλὴ εἰς τὴν— |
| [s2-3229200bf47ca465a42d-p00004.mark22.r7item30](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00004.mark22.r7item30) | Vouli | ok | την πρότασιν, ἡ δὲ Βουλή ἐρωτηθεῖσα δι&#x27; ἀναστάσεως δὲν<br> | τὴν πρότασιν, ἡ δὲ Βουλὴ ἐρωτηθεῖσα δι᾿ ἀναστάσεως<br>01<br>Δεν | —ΥΕτασιν, ἡ δὲ Ποῦλὴ ἐρωτηθεῖσα δι’ ἀναστάσεως δὲν |
| [s2-3229200bf47ca465a42d-p00004.mark24.r7item32](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00004.mark24.r7item32) | Vouli | ok | τοῦ Βουλευτοῦ Ζακύνθου περὶ τοῦ προϋπολογισμοῦ τοῦ<br> | τοῦ Βουλευτοῦ Ζακύνθου περὶ τοῦ προϋπολογισμοῦ τοῦ | ΓΒυΕὐτοῦ Ζανλθ. |
| [s2-3229200bf47ca465a42d-p00004.mark27.r7item18](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00004.mark27.r7item18) | Vouli | ok | περι ναυτικου απομαχικ<br>T<br>γραφὰς καὶ δύο τῶν Βουλευτῶν Λαρίσης. Η τροπολογία<br> | αναρι ναυτικου απομα<br>γραφὰς καὶ δύο τῶν Βουλευτῶν Λαρίσης. Η τροπολογία | ΙΑΣΣΤΗ ΜΟΣΤῷ Τοβχύτων ΤΚίσηΓΗ Σοπολογία. |
| [s2-3229200bf47ca465a42d-p00004.mark27.r7item35](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00004.mark27.r7item35) | Vouli | ok | αὕτη παρεπέμφθη εἰς τύπωσιν, ἔχει δὲ ὡς ἑξῆς.<br> | αὕτη παρεπέμφθη εἰς τύπωσιν, ἔχει δὲ ὡς ἑξῆς. | «5Ἡ Ξαρεπέμφθη εἰς τύπωσιν, ἔχει δὲ ὡς ἐξῆ-- |
| [s2-3229200bf47ca465a42d-p00004.mark28.r7item18](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00004.mark28.r7item18) | Vouli | ok | περι ναυτικου απομαχικ<br>T<br>γραφὰς καὶ δύο τῶν Βουλευτῶν Λαρίσης. Η τροπολογία<br> | αναρι ναυτικου απομα<br>γραφὰς καὶ δύο τῶν Βουλευτῶν Λαρίσης. Η τροπολογία | ΙΑΣΣΤΗ ΜΟΣΤῷ Τοβχύτων ΤΚίσηΓΗ Σοπολογία. |
| [s2-3229200bf47ca465a42d-p00004.mark28.r7item36](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00004.mark28.r7item36) | Vouli | ok | νόμων περί ναυτικοῦ ἀπομαγικοῦ ταμείου φέρουσαν τὰς ὑπο-<br> | νόμων περὶ ναυτικοῦ ἀπομαχικοῦ ταμείου φέρουσαν τὰς ὑπο- | ν πΕι ναυτικοῦ... |
| [s2-3229200bf47ca465a42d-p00004.mark30.r7item19](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00004.mark30.r7item19) | Vouli | ok | ς των Βουλευτων Αργολιους<br>20%<br>τροπολογίαν ἐπὶ τοῦ νομοσχεδίου περὶ τροποποιήσεως τῶν<br> | των Βουλευτών Αργολίους<br>231<br>τροπολογίαν ἐπὶ τοῦ νομοσχεδίου περὶ τροποποιήσεως τῶν | Τοπολογίαν ἐπὶ τοῦ νομοσχεδίου περὶ τροποποιήσεως τῶν |
| [s2-3229200bf47ca465a42d-p00004.mark30.r7item20](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00004.mark30.r7item20) | Vouli | ok | Γεωργιάδης.<br>Εἰς τῶν Βουλευτῶν ᾿Αργολίδος καὶ Κορινθίας ὑπέβαλε<br>2<br> | ωργιάδης.<br>Εἷς τῶν Βουλευτῶν ᾿Αργολίδος καὶ Κορινθίας ὑπέβαλε | Εἰς τῶν Βουλευτῶν Ἀργολίδος καὶ Κορινθίας ὑπέβαλε |
| [s2-3229200bf47ca465a42d-p00005.comment.r7item17](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00005.comment.r7item17) | Vouli | ok | λήλων ἰδίων καὶ διὰ λογαριασμὸν τοῦ Κράτους,<br> | λήλων ἰδίων καὶ διὰ λογαριασμὸν τοῦ Κράτους, | λήλων ἰδίων καὶ διὰ λογασιασμὸν τοῦ Κράτους, |
| [s2-3229200bf47ca465a42d-p00005.comment.r7item19](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00005.comment.r7item19) | Vouli | ok | ποιήσηται τὰς ἀναγκαίας ἐπιστημονικὰς μελέτας περὶ<br> | ποιήσηται τὰς ἀναγκαίας επιστημονικὰς μελέτας περὶ | ποιήσηται τὰς ἀναγκαίας ἐπιστημονικὰς μελέτας περὶ |
| [s2-3229200bf47ca465a42d-p00005.comment.r7item20](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00005.comment.r7item20) | Vouli | ok | προηγουμένῃ ἀποφάσει τοῦ Ὑπουργικοῦ Συμβουλίου<br> | προηγουμένῃ ἀποφάσει τοῦ Ὑπουργικού Συμβουλίου | προηγουμένη ἀποφάσει τοῦ Ὑπουργικοῦ Συυβουλίου, |
| [s2-3229200bf47ca465a42d-p00005.mark0.r7item28](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00005.mark0.r7item28) | Vouli | ok | ἐν Πειραιεῖ ἐργοστασιάρχας Τζών Μάκ Δουάλ καὶ Γουλ.<br> | ἐν Πειραιεῖ ἐργοστασιάρχας Τζων Μακ Δουάλ καὶ<br>Γουλ., | Πειραιεῦ Ργοστασιάχας Τζῶν Μᾶκ Δουἀλ καΙ ΓΟυἈ |
| [s2-3229200bf47ca465a42d-p00005.mark0.r7item44](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00005.mark0.r7item44) | Vouli | ok | ζήτησιν τοῦ νομοσχεδίου περὶ χορηγήσεως ἀδείας εἰς τοὺς<br> | ζήτησιν τοῦ νομοσχεδίου περὶ χορηγήσεως ἀδείας εἰς τοὺς | Τῆσιν Σοῦ νομοσχεδίου περὶ χορηγήσεως ἀδείας εἰς ου. |
| [s2-3229200bf47ca465a42d-p00005.mark13.r7item31](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00005.mark13.r7item31) | Vouli | ok | ἄρθρον καὶ σύνολον εἰς δευτέραν συζήτησιν μὲ τὸ κατὰ τὴν<br> | ἄρθρον καὶ σύνολον εἰς δευτέραν συζήτησιν μὲ τὸ κατὰ τὴν | ἄρθρον καὶ σύνολον εἰς δευτέραν συζήτησιν μὲ τὸ κατῖ Σ |
| [s2-3229200bf47ca465a42d-p00005.mark13.r7item32](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00005.mark13.r7item32) | Vouli | ok | ᾿Ανεγνώσθη ἀκολούθως καὶ ἐγένετο δεκτὸν κατ᾿ ἀρχὴν,<br> | ᾿Ανεγνώσθη ἀκολούθως καὶ ἐγένετο δεκτὸν κατ&#x27; ἀρχὴν | Τνεγνώσθη ἀκολοῦθως καὶ ἐγένετο δεκτὸν κατ ΣΗ |
| [s2-3229200bf47ca465a42d-p00005.mark14.r7item32](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00005.mark14.r7item32) | Vouli | ok | ᾿Ανεγνώσθη ἀκολούθως καὶ ἐγένετο δεκτὸν κατ᾿ ἀρχὴν,<br> | ᾿Ανεγνώσθη ἀκολούθως καὶ ἐγένετο δεκτὸν κατ&#x27; ἀρχὴν | Τνεγνώσθη ἀκολοῦθως καὶ ἐγένετο δεκτὸν κατ ΣΗ |
| [s2-3229200bf47ca465a42d-p00005.mark23.r7item13](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00005.mark23.r7item13) | Vouli | ok | μελέτας πρὸς προσδιορισμὸν ὡς ἔγγιστα τῆς τε συστάσεων<br>2<br> | και μειζων της αναγκαιουση<br>μελέτας πρὸς προσδιορισμὸν ὡς ἔγγιστα τῆς τε συστάσεως | μελέτας πρὸς προσδιορισμὸν ὡς ἔγγιστα τῆς τε συστάσεως |
| [s2-3229200bf47ca465a42d-p00005.mark6.r7item29](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00005.mark6.r7item29) | Vouli | ok | περὶ προβιβασμοῦ ὑπαξιωματικῶν εἰς τὸν βαθμὸν τοῦ ἀνθυ<br> | περὶ προβιβασμοῦ ὑπαξιωματικῶν εἰς τὸν βαθμὸν τοῦ ἀνθυ | ἱ προβιβασμοῦ ὑπαξιωματικῶν εἰς τὸν βαθμὸν τοῦ ἄνυυ- |
| [s2-3229200bf47ca465a42d-p00005.mark6.r7item4](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00005.mark6.r7item4) | Vouli | ok | Ὑπουργείου, τῆς δευτέρας συζητήσεως τοῦ νομοσχεδίου<br>περί προβι<br>Au<br> | Υπουργείου, τῆς δευτέρας συζητήσεως τοῦ νομοσχεδίου<br>..<br>Αυτ | Ὑπουργείου, τῆς δευτέρας συζητήσεως τοῦ νομοσχεδίου- |
| [s2-3229200bf47ca465a42d-p00005.mark7.r7item4](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00005.mark7.r7item4) | Vouli | ok | Ὑπουργείου, τῆς δευτέρας συζητήσεως τοῦ νομοσχεδίου<br>περί προβι<br>Au<br> | Υπουργείου, τῆς δευτέρας συζητήσεως τοῦ νομοσχεδίου<br>..<br>Αυτ | Ὑπουργείου, τῆς δευτέρας συζητήσεως τοῦ νομοσχεδίου- |
| [s2-3229200bf47ca465a42d-p00005.mark7.r7item45](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00005.mark7.r7item45) | Vouli | ok | (empty) | (empty) | ―   . |
| [s2-3229200bf47ca465a42d-p00005.mark7.r7item5](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00005.mark7.r7item5) | Vouli | ok | Αναβληθείσης κατόπιν, προτάσει τοῦ Προέδρου τοῦ<br> | Αναβληθείσης κατόπιν, προτάσει τοῦ Προέδρου<br>τοῦ | Ἠναβληθείσης Κατόπιν, Κροτάσει Τοῦ Πoέδρου Οd |
| [s2-3229200bf47ca465a42d-p00006.mark13.r7item11](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00006.mark13.r7item11) | Vouli | ok | των νόμων καὶ ἐγένετο δεκτον και<br>wwexan<br>Ὁ Ὑπουργὸς τῶν Ἐξωτερικῶν προέτεινεν εἶτα ὅπως ἐν<br> | των νόμων καὶ ἐγένετο δεκτον και<br>Ο Υπουργὸς τῶν Ἐξωτερικῶν προέτεινεν εἶτα ὅπως ἐν | Σ ΥΒθργοα ὠΥ ΚΤωΡεΙΠΟν Τοξτείνϊν εἶτα ὅπως ἐν |
| [s2-3229200bf47ca465a42d-p00006.mark14.r7item12](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00006.mark14.r7item12) | Vouli | ok | τοῦ νομοσχεδίου περὶ τροποποιήσεως τῶν περὶ προξενικῶν<br>άου<br> | του<br>Ο νομοσχεδίου περὶ τροποποιήσεως τῶν περὶ προξενικῶν | ΜΜΣσχεδίου περὶ Τοποποιήσεως τῶν περὶ προξινικῶν |
| [s2-3229200bf47ca465a42d-p00006.mark14.r7item22](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00006.mark14.r7item22) | Vouli | ok | Προέβη κατόπιν ἡ Βουλὴ εἰς τὴν δευτέραν συζήτησιν<br> | Προέβη κατόπιν ἡ Βουλή εἰς τὴν δευτέραν συζήτησιν | ΠΕβῃ κατόπιν ἡ Βουλὴ εἰς τὴν δευτέραν συζήτησιν. |
| [s2-3229200bf47ca465a42d-p00006.mark17.r7item23](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00006.mark17.r7item23) | Vouli | ok | σωσιν ὁριστικῶς λειτουργοῦντα».<br> | σωσιν ὁριστικῶς λειτουργοῦντα». | Σν ειστικῶς λειτουργοῦντα». |
| [s2-3229200bf47ca465a42d-p00006.mark17.r7item38](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00006.mark17.r7item38) | Vouli | ok | Τὴν προσθήκην ταύτην ἡ Βουλὴ ἐρωτηθεῖσα παρεδέχθη,<br> | Τὴν προσθήκην ταύτην ἡ Βουλὴ ἐρωτηθεῖσα παρεδέχθη, | ΤΝ οσθήκην ταύτην ἡ Βουλὴ ἐρωτηθεῖσα παρεδέχθη, |
| [s2-3229200bf47ca465a42d-p00006.mark18.r7item23](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00006.mark18.r7item23) | Vouli | ok | σωσιν ὁριστικῶς λειτουργοῦντα».<br> | σωσιν ὁριστικῶς λειτουργοῦντα». | Σν ειστικῶς λειτουργοῦντα». |
| [s2-3229200bf47ca465a42d-p00006.mark18.r7item24](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00006.mark18.r7item24) | Vouli | ok | θησόμενα νεωλκεῖα καὶ ναυπηγεῖα ἀρθῶσιν ἐκεῖθεν ἢ παύ-<br> | θησόμενα νεωλκεῖα καὶ ναυπηγεῖα ἀρθῶσιν ἐκεῖθεν ἢ παύ | (ΠσΜενα νεωλκεῖα καὶ ναυπηγεῖα ἀρθῶσιν ἐκεῖθεν ἡ παύ- |
| [s2-3229200bf47ca465a42d-p00006.mark20.r7item14](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00006.mark20.r7item14) | Vouli | ok | ται τὰ ὑπ᾿ αὐτοῦ παραχωρηθέντα γήπεδα ὅταν τὰ ἱδρυ-<br>πως την κυριότητα ώσαύτως του<br>θησί<br>AN<br>Σμαΐλου ή παύ-<br> | · καὶ τὰ ὑπ᾽ αὐτοῦ παραχωρηθέντα γήπεδα ὅταν τὰ ἱδρυ-<br>τας την κυριότητα ὡσαύτως του<br>Ona<br>INSTACY | Δ Σ Τ αὐτεοβ ΤαβαλοαψῆεντΣ ψήχεδα ὅταχ. τὰ ίδρυ- |
| [s2-3229200bf47ca465a42d-p00006.mark20.r7item15](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00006.mark20.r7item15) | Vouli | ok | «Εἰς τὴν κυριότητα ὡσαύτως τοῦ δημοσίου ἐπανέρχον-<br> | «Εἰς τὴν κυριότητα ὡσαύτως τοῦ δημοσίου ἐπανέρχον | «Εἰς τὴν κυριότητα ὡσαύτως τοῦ δημοσίου ἐπανέρχον- |
| [s2-3229200bf47ca465a42d-p00006.mark25.r7item31](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00006.mark25.r7item31) | Vouli | ok | Ἐπὶ τοῦ ἄρθρου 3 εἷς τῶν Βουλευτῶν Λαρίσης καὶ ἕτερος<br> | Ἐπὶ τοῦ ἄρθρου 3 εἷς τῶν Βουλευτῶν Λαρίσης καὶ ἕτερος | Ἐπ τοῦ ἀρθρου 3 εἰς τῶν Βουλευτῶν Λαρίσης καὶ ἕτερος |
| [s2-3229200bf47ca465a42d-p00006.mark26.r7item19](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00006.mark26.r7item19) | Vouli | ok | 1. Yanadny 10% 2025220dasr<br>τὰ ἄρθρα αὐτοῦ 1 καὶ 2 ὡς ἔχουσιν.<br> | τα<br>τερατζινι και παρουσι<br>ἄρθρα αὐτοῦ 1 και 2 ὡς ἔχουσιν. | Σ ΖὐΡΕ αὐτοῦ Υκαὶ «ως ἔχουσιν. |
| [s2-3229200bf47ca465a42d-p00006.mark7.r7item29](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00006.mark7.r7item29) | Vouli | ok | ποποίησις τοῦ ἄρθρου 31.<br> | ποποίησις τοῦ ἄρθρου 31. | ΣΕΗΕς ΤΟΗ ἀρθρου 3Ι. |
| [s2-3229200bf47ca465a42d-p00006.mark7.r7item36](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00006.mark7.r7item36) | Vouli | ok | τῆς χθὲς ὑποβληθείσης τροπολογίας<br>του<br>προτεινομένη τρο-<br> | τῆς χθὲς ὑποβληθείσης τροπολογίας<br>του<br>προτεινομένη τρο- | ΣΣΗς ποβληθείσης τροπολογίας του προτεινομένη τρο- |
| [s2-3229200bf47ca465a42d-p00008.mark1.r7item0](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark1.r7item0) | Vouli | ok | γησιν της θεσσ<br>Ἡ Βουλὴ ἐρωτηθεῖσα παρεδέχθη τὴν χορηγία, τῶν ἐκ<br> | της νευτων<br>Η Βουλὴ ἐρωτηθεῖσα παρεδέχθη τὴν χορηγίαν τῶν ἐκ | Ἡ Βουλὴ ἐρωτηθεῖσα παρεδέχθη τὴν χορηγίαν τῶν ἐκ |
| [s2-3229200bf47ca465a42d-p00008.mark1.r7item1](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark1.r7item1) | Vouli | ok | made suxιτίι το xi..<br>κατάργησιν τῆς θέσεως τοῦ λογιστοῦ.<br>SlAm<br> | της και ταμιακής π<br>· κατάργησιν τῆς θέσεως τοῦ λογιστοῦ.<br>A | ΣΕΗΕΝ τῇξΗΙκηςυη. |
| [s2-3229200bf47ca465a42d-p00008.mark11.r7item21](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark11.r7item21) | Vouli | ok | νοδον τοῦ 1890, ἀνεγνώσθη δὲ ἡ ἐπ᾿ αὐτοῦ ἔκθεσις τῆς<br> | νάδον τοῦ 1890, ἀνεγνώσθη δὲ ἡ ἐπ᾿ αὐτοῦ ἔκθεσις τῆς | ΣΣΣΕΙΙΕ9Ο — 3ὲ ἡ π αὐτοῦ ἔπθεσις τῆς. |
| [s2-3229200bf47ca465a42d-p00008.mark11.r7item6](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark11.r7item6) | Vouli | ok | ἐπὶ τοῦ λογιστικοῦ ἐπιτροπῆς, καὶ μηδενὸς ἀντειπόντος, ἡ<br>B<br> | B<br>ἐπὶ τοῦ λογιστικοῦ ἐπιτροπῆς, καὶ μηδενὸς ἀντειπόντος, ἡ | ΗΠΜὐΕΙΕκΟῦ πιτοπῆς, α! Μηδενὰ ἀντιπόντος, ἤ- |
| [s2-3229200bf47ca465a42d-p00008.mark13.r7item22](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark13.r7item22) | Vouli | ok | ἀπολογισμοῦ τῶν ἐξόδων τῆς Βουλῆς διὰ τὴν ἔκτακτον σύ-<br> | ἀπολογισμοῦ τῶν ἐξόδων τῆς Βουλῆς διὰ τὴν ἔκτακτον ούτ | «ΕΙΟΙσμοῦ τῶν ἐξόδων.. |
| [s2-3229200bf47ca465a42d-p00008.mark15.r7item24](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark15.r7item24) | Vouli | ok | σύνολον τοῦ νομοσχεδίου εἰς δευτέραν συζήτησιν.<br> | σύνολον τοῦ νομοσχεδίου εἰς δευτέραν συζήτησιν. | «ΣΝ τοῦ νομσσχευίου εἰς δευτέραν συζήτησιν. |
| [s2-3229200bf47ca465a42d-p00008.mark16.r7item25](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark16.r7item25) | Vouli | ok | Υπουργός τῶν Ἐξωτερικῶν· ἐπίσης ἐγένετο δεκτὸν καὶ τὸ<br> | Υπουργὸς τῶν Ἐξωτερικῶν· ἐπίσης ἐγένετο δεκτὸν καὶ τὸ | ΥΣΕς τῶν Ἐξωτερικῶν ἐπίσης ἐγένετο δεκτὸν καὶ τὸ |
| [s2-3229200bf47ca465a42d-p00008.mark19.r7item28](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark19.r7item28) | Vouli | ok | οὕτω δὲ τροποποιηθὲν τὸ κείμενον τοῦ μόνου ἄρθρου άνε<br> | οὕτω δὲ τροποποιηθὲν τὸ κείμενον τοῦ μόνου άρθρου ἀνε | Σ Σπρπόποιηθεν τὸ κείμενον τοῦ μόνου ἄρθρου ἄνε- |
| [s2-3229200bf47ca465a42d-p00008.mark19.r7item7](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark19.r7item7) | Vouli | ok | 23000<br>240.<br>Τὰς προτάσεις ταύτας ἡ Βουλὴ ἐρωτηθεῖσα παρεδέχθη,<br> | Τὰς προτάσεις ταύτας ἡ Βουλὴ ἐρωτηθεῖσα παρεδέχθη, | Τὰς ποοτάσεις ταύτας ἡ Βουλὴ ἐρωτηθεῖσα παρεδέχθη, |
| [s2-3229200bf47ca465a42d-p00008.mark22.r7item29](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark22.r7item29) | Vouli | ok | ἄρθρου τοῦ νομοσχεδίου μνημονευομένων καὶ τῶν διὰ τῶν<br> | ἄρθρου τοῦ νομοσχεδίου μνημονευομένων καὶ τῶν διὰ τῶν | ΔΕ μοσχεδίου μνημονευομένων καὶ τῶν διὰ τῶν |
| [s2-3229200bf47ca465a42d-p00008.mark22.r7item9](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark22.r7item9) | Vouli | ok | ὡς ἄνω τροπολογιών τροποποιουμένων ἄρθρων 31, 143,<br>766<br> | annadund noros Zoorion now<br>ὡς ἄνω τροπολογιών τροποποιουμένων άρθρων 31, 143,<br>766 | θς ἄνον τροπολονιῶν τοποποιουμένων ἄρθρων 51. 145, |
| [s2-3229200bf47ca465a42d-p00008.mark23.r7item29](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark23.r7item29) | Vouli | ok | ἄρθρου τοῦ νομοσχεδίου μνημονευομένων καὶ τῶν διὰ τῶν<br> | ἄρθρου τοῦ νομοσχεδίου μνημονευομένων καὶ τῶν διὰ τῶν | ΔΕ μοσχεδίου μνημονευομένων καὶ τῶν διὰ τῶν |
| [s2-3229200bf47ca465a42d-p00008.mark23.r7item30](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark23.r7item30) | Vouli | ok | Νὰ τροποποιηθῇ τέλος ἡ πρώτη παράγραφος τοῦ μόνου<br> | Να<br>τροποποιηθῇ τέλος ἡ πρώτη παράγραφος του μόνου | Στποποιηθῇ τέλος ἡ πρώτη παράγραφος τοῦ μόνου, |
| [s2-3229200bf47ca465a42d-p00008.mark23.r7item9](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark23.r7item9) | Vouli | ok | ὡς ἄνω τροπολογιών τροποποιουμένων ἄρθρων 31, 143,<br>766<br> | annadund noros Zoorion now<br>ὡς ἄνω τροπολογιών τροποποιουμένων άρθρων 31, 143,<br>766 | θς ἄνον τροπολονιῶν τοποποιουμένων ἄρθρων 51. 145, |
| [s2-3229200bf47ca465a42d-p00008.mark27.r7item32](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark27.r7item32) | Vouli | ok | τοῦ αὐτοῦ νόμου νὰ προστεθῶσιν ἐν τέλει τὰ διὰ τῆς χθὲς<br> | τοῦ αὐτοῦ νόμου νὰ προστεθῶσιν ἐν τέλει τὰ διὰ τῆς χθὲς | —ΣΜτοῦ νόμου νὰ προστεθῶσιν ἐν τέλει τὰ διὰ τῆς χθὲς |
| [s2-3229200bf47ca465a42d-p00008.mark4.r7item16](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark4.r7item16) | Vouli | ok | ἐντολῇ τοῦ Προεδρείου άναλαβόντος τὴν τήρησιν τῆς λο-<br> | ἐντολὴ τοῦ Προεδρείου ἀναλαβόντος τὴν τήρησιν τῆς λο- | «ΟΤΙ Τοῦ Ποοεδσί..ΡΙ. |
| [s2-3229200bf47ca465a42d-p00008.mark4.r7item4](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark4.r7item4) | Vouli | ok | adamy emeanorlody sads 005 30 100<br>μοσχεδίου, ὡς καὶ ἑτέρων δραχ. 600 δι&#x27; ἀποζημίωσιν τοῦ<br> | σε τον προς προμ<br>μοσχεδίου, ὡς καὶ ἑτέρων δραχ. 600 δι&#x27; ἀποζημίωσιν<br>του | μοσχεδίου, ὡς καὶ ἑτέρων δραγ. 600 δι’ ἀποζημίωσιν τοῦ |
| [s2-3229200bf47ca465a42d-p00008.mark6.r7item4](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark6.r7item4) | Vouli | ok | adamy emeanorlody sads 005 30 100<br>μοσχεδίου, ὡς καὶ ἑτέρων δραχ. 600 δι&#x27; ἀποζημίωσιν τοῦ<br> | σε τον προς προμ<br>μοσχεδίου, ὡς καὶ ἑτέρων δραχ. 600 δι&#x27; ἀποζημίωσιν<br>του | μοσχεδίου, ὡς καὶ ἑτέρων δραγ. 600 δι’ ἀποζημίωσιν τοῦ |
| [s2-3229200bf47ca465a42d-p00008.mark6.r7item5](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark6.r7item5) | Vouli | ok | οραχμών μεν 200<br>προς ορώρ<br>δραχμῶν δὲ 400 πρὸς προμήθειαν χάρτου δι᾽ ἐκτύπωσιν νο-<br>000<br>2<br> | 2%<br>δραχμών μεν<br>200<br>δραχμών δε 400 προς προμήθειαν χάρτου δι&#x27; εκτύπωσιν να<br>2 | δραχμῶν δὲ 400 πρὸς προμήθειαν χάρτου δι’ ἐκτύπωσιν νο- |
| [s2-3229200bf47ca465a42d-p00008.mark7.r7item17](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark7.r7item17) | Vouli | ok | σεως ἐκ δραχμῶν μὲν 200 πρὸς προμήθειαν καυσοξύλων,<br> | σέως ἐκ δραχμῶν μὲν 200 πρὸς προμήθειαν καυσοξύλων, | ΕΣΙ δραχμῶν μὲν 200 πρὸς προμήθείιαν καυσοξύλων, |
| [s2-3229200bf47ca465a42d-p00008.mark7.r7item5](../../harvest/three_engines_review.html#s2-3229200bf47ca465a42d-p00008.mark7.r7item5) | Vouli | ok | οραχμών μεν 200<br>προς ορώρ<br>δραχμῶν δὲ 400 πρὸς προμήθειαν χάρτου δι᾽ ἐκτύπωσιν νο-<br>000<br>2<br> | 2%<br>δραχμών μεν<br>200<br>δραχμών δε 400 προς προμήθειαν χάρτου δι&#x27; εκτύπωσιν να<br>2 | δραχμῶν δὲ 400 πρὸς προμήθειαν χάρτου δι’ ἐκτύπωσιν νο- |
| [s2-44b5cf9e0d680b361091-p00002.comment.r7item9](../../harvest/three_engines_review.html#s2-44b5cf9e0d680b361091-p00002.comment.r7item9) | Vouli | ok | &#124;ἐκεῖνοι οἵτινες ἀπεχώρησαν τοῦ Βουλευτηρίου καὶ ἔρριψαν κατὰ<br> | ἐκεῖνοι οἵτινες ἀπεχώρησαν τοῦ Βουλευτηρίου καὶ ἔρριψαν κατὰ | εἶνοι οἵτινες ἀπεχώρησαν τοῦ Βουλευτηρίου καὶ ἔρριψαν κατὰ |
| [s2-49598b2e848ab1f0ee1e-p00001.comment.r7item11](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00001.comment.r7item11) | Vouli | ok | ἥτις εἶναι ἓν ἐκ τῶν εὐγενεστέρων έλα-<br> | ἥτις εἶναι ἓν ἐκ τῶν εὐγενεστέρων έλα- | ἤτις εἶναι ἐν ἐκ τῶν εὐγενεστέρων ἐλα- |
| [s2-49598b2e848ab1f0ee1e-p00001.comment.r7item2](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00001.comment.r7item2) | Vouli | ok | θυπουργός παρεδέ<br> | θυπουργός παρεδέ | πουργὸς παρεδέ- |
| [s2-49598b2e848ab1f0ee1e-p00001.mark65.r7item95](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00001.mark65.r7item95) | Vouli | ok | θείας μεταλλικοῦ ἐκ φράγκων 10,000,000 κατ᾿ ἀρχὴν, ἄρι<br> | θείας μεταλλικοῦ ἐκ φράγκων 10,000,000 κατ&#x27; αρχήν, ἄρτι | θείας μεταλλικοῦ ἐκ φράγκων 10,000,000 κατ’ ἀρχὴν, ἄρ- |
| [s2-49598b2e848ab1f0ee1e-p00001.mark76.r7item28](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00001.mark76.r7item28) | Vouli | ok | Νομοσχέδιον τοῦτο εἰς τὴν ἡμερησίαν διάταξιν καὶ, εἰ δυνα-<br>צי<br> | 8...<br>Νομοσχέδιον τοῦτο εἰς τὴν ἡμερησίαν διάταξιν καί, εἰ δυνατ | Χομοσχέδιον τοῦτο εἰς τὴν ἡμερησίαν διάταξιν καὶ, εἰ δυνα- |
| [s2-49598b2e848ab1f0ee1e-p00001.mark76.r7item30](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00001.mark76.r7item30) | Vouli | ok | Παρακαλῶ λοιπὸν τὴν Βουλὴν, ἵνα ἐπιτρέψῃ νὰ τεθῇ τὸ<br>A<br>A<br> | ν εις τοιούτου<br>Παρακαλῶ λοιπὸν τὴν Βουλήν, ἵνα ἐπιτρέψῃ νὰ τεθῇ τὸ<br>&quot; | » Παρακαλῶ λοιπὸν τὴν Βουλὴν, ἵνα ἐπιτρέψῃ νὰ τεθῇ τὸν |
| [s2-49598b2e848ab1f0ee1e-p00001.mark78.r7item30](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00001.mark78.r7item30) | Vouli | ok | Παρακαλῶ λοιπὸν τὴν Βουλὴν, ἵνα ἐπιτρέψῃ νὰ τεθῇ τὸ<br>A<br>A<br> | ν εις τοιούτου<br>Παρακαλῶ λοιπὸν τὴν Βουλήν, ἵνα ἐπιτρέψῃ νὰ τεθῇ τὸ<br>&quot; | » Παρακαλῶ λοιπὸν τὴν Βουλὴν, ἵνα ἐπιτρέψῃ νὰ τεθῇ τὸν |
| [s2-49598b2e848ab1f0ee1e-p00001.mark80.r7item101](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00001.mark80.r7item101) | Vouli | ok | είναι φυσικόν εἰς τοιούτου είδους διαπραγματεύσεις.<br> | εἶναι φυσικὸν εἰς τοιούτου εἴδους διαπραγματεύσεις. | εἶναι φυσικὸν εἰς τοιούτου εἴδους διαπραγματεύσεις. |
| [s2-49598b2e848ab1f0ee1e-p00001.mark80.r7item30](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00001.mark80.r7item30) | Vouli | ok | Παρακαλῶ λοιπὸν τὴν Βουλὴν, ἵνα ἐπιτρέψῃ νὰ τεθῇ τὸ<br>A<br>A<br> | ν εις τοιούτου<br>Παρακαλῶ λοιπὸν τὴν Βουλήν, ἵνα ἐπιτρέψῃ νὰ τεθῇ τὸ<br>&quot; | » Παρακαλῶ λοιπὸν τὴν Βουλὴν, ἵνα ἐπιτρέψῃ νὰ τεθῇ τὸν |
| [s2-49598b2e848ab1f0ee1e-p00001.mark80.r7item32](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00001.mark80.r7item32) | Vouli | ok | νομοσχέδιον υπέόχλον μετα<br>Τραπεζικῶν Οἴκων, οἱ ὁποῖοι ἔδειξαν πᾶσαν προθυμίαν, ὅπω;<br>...<br>2<br> | Τραπεζικῶν Οίκων, οἱ ὁποῖοι ἔδειξαν<br>μοσχεδιον υπερχλον μετα<br>πᾶσαν<br>προθυμίαν, ὅπως<br>2 | ραπεζικῶν Οἴκων, οἱ ὁποῖοι ἔδειξαν πᾶσαν προθυμίαν, ὅπως! |
| [s2-49598b2e848ab1f0ee1e-p00001.mark82.r7item32](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00001.mark82.r7item32) | Vouli | ok | νομοσχέδιον υπέόχλον μετα<br>Τραπεζικῶν Οἴκων, οἱ ὁποῖοι ἔδειξαν πᾶσαν προθυμίαν, ὅπω;<br>...<br>2<br> | Τραπεζικῶν Οίκων, οἱ ὁποῖοι ἔδειξαν<br>μοσχεδιον υπερχλον μετα<br>πᾶσαν<br>προθυμίαν, ὅπως<br>2 | ραπεζικῶν Οἴκων, οἱ ὁποῖοι ἔδειξαν πᾶσαν προθυμίαν, ὅπως! |
| [s2-49598b2e848ab1f0ee1e-p00001.mark82.r7item33](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00001.mark82.r7item33) | Vouli | ok | ο υπερτιμήσεως<br>700<br>τὸ Νομοσχέδιον ὑπέβαλον μετὰ προηγουμένην συνεννόησιν<br>T<br>C<br> | περτιμήσεως του<br>με<br>Τ<br>τὸ Νομοσχέδιον ὑπέβαλον μετὰ προηγουμένην συνεννόησιν | τὸ Νομοσχέδιον ὑπέβαλον μετὰ προηγουμένην συνεννόησιν! |
| [s2-49598b2e848ab1f0ee1e-p00001.mark86.r7item105](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00001.mark86.r7item105) | Vouli | ok | μίας τῆς ὑπερτιμήσεως τοῦ μεταλλικοῦ νομίσματος. Αὐτὸ<br> | μίας τῆς ὑπερτιμήσεως<br>τοῦ μεταλλικοῦ νομίσματος. Αὐτὸ | μίας τῆς ὑπερτιμήσεως τοῦ μεταλλικοῦ νομίσματος. Αὐτὸ |
| [s2-49598b2e848ab1f0ee1e-p00001.mark86.r7item107](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00001.mark86.r7item107) | Vouli | ok | εἶναι ὠφέλιμον, διότι ἀπαλλάττει τὸ Δημόσιον ἀπὸ τῆς ζη<br> | εἶναι ὠφέλιμον, διότι ἀπαλλάττει τὸ Δημόσιον ἀπὸ τῆς ζη- | εἶναι ὀφέλιμον, διότι ἀπαλλάττει τὸ Δημόσιον ἀπὸ τῆς ζη-! |
| [s2-49598b2e848ab1f0ee1e-p00001.mark86.r7item33](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00001.mark86.r7item33) | Vouli | ok | ο υπερτιμήσεως<br>700<br>τὸ Νομοσχέδιον ὑπέβαλον μετὰ προηγουμένην συνεννόησιν<br>T<br>C<br> | περτιμήσεως του<br>με<br>Τ<br>τὸ Νομοσχέδιον ὑπέβαλον μετὰ προηγουμένην συνεννόησιν | τὸ Νομοσχέδιον ὑπέβαλον μετὰ προηγουμένην συνεννόησιν! |
| [s2-49598b2e848ab1f0ee1e-p00001.mark90.r7item35](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00001.mark90.r7item35) | Vouli | ok | ημέρων υπεοαλον<br>πορούχου۰۰۰ ۲۰۲۰ ٢٢<br>νείου 10,000,000, τὸ ὁποῖον νομίζει τὸ Ὑπουργεῖον, ὅτι<br> | ημέρων υπερχλον νομου χανον<br>νείου 10,000,000,<br>τὸ ὁποῖον νομίζει τὸ Ὑπουργεῖον, ὅτι | νίου 10,000,000, τὸ ὁποῖον νομίζει τὸ Ὑπουργεῖον, ὅτι |
| [s2-49598b2e848ab1f0ee1e-p00001.mark98.r7item42](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00001.mark98.r7item42) | Vouli | ok | ης προηγουμενης συνευρικυom/<br>ΠΡΟΕΔΡΟΣ. Ζητεί τις τὸν λόγον πρὶν εἰσέλθωμεν εἰς τὴν<br>A<br> | προηγούμενης συνευμ<br>ΠΡΟΕΔΡΟΣ. Ζητεί τις τὸν λόγον πρὶν εἰσέλθωμεν εἰς τὴν<br>&#x27; | ΠΡΟΕΔΡΟΣ. Ζητεῖ τις τὸν λόγον πρὶν εἰσέλθωμεν εἰς τὴν |
| [s2-49598b2e848ab1f0ee1e-p00004.comment.r7item0](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.comment.r7item0) | Vouli | ok | τευόμενοι ρήτορες εἰς τὴν ἐπίκρισιν τῆς ἐσωτερικῆς πολιτι-<br> | τευόμενοι ρήτορες εἰς τὴν ἐπίκρισιν τῆς ἐσωτερικῆς πολιτι | τευόμενοι ῥήτορες εἰς τὴν ἐπίκρισιν τῆς ἐσωτερικῆς πολιτι- |
| [s2-49598b2e848ab1f0ee1e-p00004.comment.r7item34](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.comment.r7item34) | Vouli | ok | τούτου, καὶ ἡ πλειοψηφία ἐπεδοκίμασε πληρέστατα τὴν δια-<br> | τούτου, καὶ ἡ πλειοψηφία ἐπεδοκίμασε πληρέστατα τὴν δια- | τούτου, καὶ ἡ πλειοψηφία ἐπεδοκίμασε πληρέστατα τὴν δια- |
| [s2-49598b2e848ab1f0ee1e-p00004.mark105.r7item92](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark105.r7item92) | Vouli | ok | σεως, ἐν ἡ εὑρισκόμεθα; ᾿Αλλ&#x27; ἐγὼ ἐρωτῶ ἡμᾶς, κύριοι, ἐὰν<br>ην κινο<br> | ημα, τη<br>της αυλίας<br>στως,<br>ἐν ᾗ εὑρισκόμεθα; Αλλ&#x27; ἐγὼ ἐρωτῶ ἡμᾶς, κύριοι, ἐὰν | σεῶς, ἐν ᾗ εὐρισκομεθα; Ἀλλ’ ἐγὼ ἐρωτῶ ἡμᾶς, κύριοι, ἐὰν, |
| [s2-49598b2e848ab1f0ee1e-p00004.mark105.r7item94](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark105.r7item94) | Vouli | ok | οικειο<br>10<br>μορφωτὴν, ὅπως ἐξαγάγητε ἡμᾶς ἐκ τῆς ἀθλίας καταστά<br>&quot;<br> | ΑΛΑΓΚ<br>35<br>Είναι γ γαλλυμα<br>μορφωτήν, ὅπως ἐξαγάγητε ἡμᾶς ἐκ τῆς ἀθλίας καταστά<br>.. | Μορφωτὴν, ὅπως ἐξαγάγητε ἡμᾶς ἐκ τῆς ἀθλίας καταστά- |
| [s2-49598b2e848ab1f0ee1e-p00004.mark109.r7item113](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark109.r7item113) | Vouli | ok | τοὺς κατέχοντας τὰ Κυβερνητικὰ ἑδώλια, ἠρώτησαν αὐτούς·<br> | τοὺς κατέχοντας τὰ Κυβερνητικὰ ἑδώλια, ἠρώτησαν αὐτούς | τοὺς κατέχοντας τὰ Κυβερνητικὰ ἐδώλια, ἠρώτησαν αὐτού: |
| [s2-49598b2e848ab1f0ee1e-p00004.mark109.r7item96](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark109.r7item96) | Vouli | ok | καὶ τί λοιπὸν ἐπράξατε σεῖς, οἱ ἐπαγγελλόμενοι τὸν ἀνατ<br> | ανυμνητικα ευωδιά, πρωτησ<br>καὶ τί λοιπὸν ἐπράξατε σεις, οἱ ἐπαγγελλόμενοι τὸν ἀνα | καὶ τί λοιπὸν ἐπράξατε σεῖς, οἱ ἐπαγγελλόμενοι τὸν ἀνα- |
| [s2-49598b2e848ab1f0ee1e-p00004.mark19.r7item19](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark19.r7item19) | Vouli | ok | - ٠٠٠٠٠م, να, κοσμον ως ανύρματα εις<br>κρά παιδία˙ ἀλλὰ μέχρι τῆς ἐποχῆς ἐκείνης ὀφείλομεν ν<br>..<br>V<br>-Ad<br> | κοσμον ως ασυρματα εἰς<br>κρά παιδία ἀλλὰ μέχρι τῆς ἐποχῆς ἐκείνης ὀφείλομεν γ<br>-A Y | (κρὰ παιδία· ἀλλὰ μέχρι τῆς ἐποχῆς ἐκεῖθᾳ Σρείλομξαν |
| [s2-49598b2e848ab1f0ee1e-p00004.mark19.r7item21](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark19.r7item21) | Vouli | ok | DA<br> | va | νὰ |
| [s2-49598b2e848ab1f0ee1e-p00004.mark27.r7item127](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark27.r7item127) | Vouli | ok | (empty) | (empty) | .. |
| [s2-49598b2e848ab1f0ee1e-p00004.mark27.r7item25](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark27.r7item25) | Vouli | ok | ὅπως<br> | ὅπως | σπως. |
| [s2-49598b2e848ab1f0ee1e-p00004.mark27.r7item27](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark27.r7item27) | Vouli | ok | --78<br>δὲν ἔχομεν διδασκάλους, καὶ οἱ διδάσκαλοι δὲν αὐτοσχε<br> | διαγ<br>δὲν ἔχομεν διδασκάλους, καὶ οἱ διδάσκαλοι δὲν αὐτοσχε<br>απων | δὲν ἔχομεν διδασκάλους, καὶ οἱ διδάσκαλοι δὲν αὐτοβΖ. |
| [s2-49598b2e848ab1f0ee1e-p00004.mark4.r7item116](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark4.r7item116) | Vouli | ok | διανύσωσιν εὐκοπώτερον τὸν περὶ τῆς ὑπάρξεως ἀγῶνα,<br> | διανύσωσιν εὐκοπώτερον τὸν περὶ τῆς ὑπάρξεως ἀγῶνα, | διανύσωσιν εὐκοπώτερον τὸν περὶ τῆς ὑπάρξεως ἀγῶνά. |
| [s2-49598b2e848ab1f0ee1e-p00004.mark4.r7item4](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark4.r7item4) | Vouli | ok | ۱۲۰۲۰۰۶ κρινμητικην και διδαχθῶσι τι<br>τρεύουσι; Δὲν θὰ δυνηθῶσιν ἄρα οὕτω παρεσκευασμένα<br>διανύσωσιν εὐκοπάσσο..<br>1<br>مو<br>αναναι<br>V<br> | αριθμητικήν<br>και διδαχθῶσι τί<br>τρεύουσι; Δὲν θὰ δυνηθῶσιν ἄρα οὕτω παρεσκευασμένα ν<br>διανύσωσιν ελυπάσαι.<br>1.<br>2. | τρεύουσι; Ἐἶν’ θὰ ὀὔθηδάσιν ἄρα οὕτω παρεσκευαβμέναν |
| [s2-49598b2e848ab1f0ee1e-p00004.mark44.r7item44](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark44.r7item44) | Vouli | ok | ὡς προνόμιον ὀλίγων τινῶν τάξεων καὶ χωρίων. Καί σᾶς<br>λιδ<br> | ὡς προνόμιον ὀλίγων τινῶν τάξεων καὶ χωρίων. Καί σᾶς<br>818 | ὡς προνόμιον ὀλίγων τινῶν τάξεων καὶ χωρίων. Καὶ σᾷξρ |
| [s2-49598b2e848ab1f0ee1e-p00004.mark51.r7item120](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark51.r7item120) | Vouli | ok | τοὺς στρατευσίμους, τοὺς ὁποίους ἐκεῖ ἐστρατολογήσατε,<br> | τοὺς στρατευσίμους, τοὺς ὁποίους ἐκεῖ ἐστρατολογήσατε. | τοὺς στρατευσίμους, τοὺς ὁποίους ἐκεῖ ἐστρατολογήσατις |
| [s2-49598b2e848ab1f0ee1e-p00004.mark51.r7item121](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark51.r7item121) | Vouli | ok | χωρίων ἐκείνων, ἀποστείλατε πρῶτον εἰς τὰς ἑστίας των<br> | χωρίων ἐκείνων, ἀποστείλατε πρῶτον εἰς τὰς ἑστίας των | χωρίων ἐκείνων, ἀποστείλατε πρῶτον εἰς τὰς ἑστίας τῶν |
| [s2-49598b2e848ab1f0ee1e-p00004.mark57.r7item105](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark57.r7item105) | Vouli | ok | τησαν τὴν κατάργησιν αὐτῶν. ᾿Αλλά ποὶν, κύριοι, προτεί-<br> | τησαν τὴν κατάργησιν αὐτῶν. Ἀλλὰ πρὶν, κύριοι, προτεί | ταν τὴν κατάργησιν αὐτῶν. Ἀλλὰ πρὶν, κύριοι, προτεί- |
| [s2-49598b2e848ab1f0ee1e-p00004.mark57.r7item123](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark57.r7item123) | Vouli | ok | νητε τὴν κατάργησιν ταύτην, ἀποδόσατε πρῶτον τοὺς φό-<br> | ινητε τὴν κατάργησιν ταύτην, ἀποδόσατε πρῶτον τοὺς φύ | νητε τὴν κατάργησιν ταύτην, ἀποδόσατε πρῶτον τοὺς φί- |
| [s2-49598b2e848ab1f0ee1e-p00004.mark68.r7item61](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark68.r7item61) | Vouli | ok | ψυσικην<br>αυτων πορειαν. Κατηγορησαν<br>Κυβέρνησιν, διότι συνέστησε μερικά Σχολεῖα εἰς ἀπό κεντρα<br>27<br>αί<br> | μουσικην αυτών πορείαν. Κατηγόρησαν<br>&#124; Κυβέρνησιν, διότι συνέστησε μερικά Σχολεία εἰς ἀπόκεντρα | (Κυβέρνησιν, διότι συνέστησε μερικὰ Σχολεῖα εἰς ἀπόκεντά |
| [s2-49598b2e848ab1f0ee1e-p00004.mark68.r7item63](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark68.r7item63) | Vouli | ok | ۲۲<br>ροῦν καὶ τὴν φυσικὴν αὑτῶν πορείαν. Κατηγόρησαν<br> | A<br>ροῦν καὶ τὴν φυσικὴν αὑτῶν πορείαν. Κατηγόρησαν | ροῦν καὶ τὴν φυσικὴν αὐτῶν πορείαν. Κατηγόρησαν. |
| [s2-49598b2e848ab1f0ee1e-p00004.mark72.r7item108](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark72.r7item108) | Vouli | ok | AR<br>καὶ θέλετε νὰ ἴδητε συντετελεσμένα ἔργα, τῶν ὁποίων ἡ<br> | καὶ θέλετε νὰ ἴδητε συντετελεσμένα ἔργα, τῶν ὁποίων<br>ή | θέλετε νὰ ἴδητε συντετελεσμένα ἔργα, τῶν ὁποίων ἡ |
| [s2-49598b2e848ab1f0ee1e-p00004.mark72.r7item124](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark72.r7item124) | Vouli | ok | συντέλεσις ἀπαιτεῖ μακρὰν σειρὰν ἐνιαυτῶν; Παρῆλθε, κύριοι,<br> | - συντέλεσις ἀπαιτεῖ μακρὰν σειρὰν ἐνιαυτῶν; Παρῆλθε, κύριοι, | συντέλεσις ἀπαιτεῖ μακρὰν σειρὰν ἐνιαυτῶν; Παρῆλθε, κύριθυε |
| [s2-49598b2e848ab1f0ee1e-p00004.mark76.r7item109](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark76.r7item109) | Vouli | ok | τῶν ὁποίων κάθηνται οἱ κυβερνῶντες σήμερον τὸ Κράτος,<br> | τῶν ὁποίων κάθηνται οἱ κυβερνῶντες σήμερον τὸ Κράτος, | τῶν ὁποίων κάθηνται οἱ κυβερνῶντες σήμερον τὸ Κράτοι, |
| [s2-49598b2e848ab1f0ee1e-p00004.mark76.r7item68](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark76.r7item68) | Vouli | ok | κῷ διαστήματι; Εἰσέτι δὲν ἐθερμάνθησαν τὰ ἑδώλια,<br> | και διαστήματι; Εἰσέτι δὲν ἐθερμάνθησαν τὰ ἑδώλια, | κῷ διαστήματι; Εἰσέτι δὲν ἐθερμάνθησαν τὰ ἐδώλια, |
| [s2-49598b2e848ab1f0ee1e-p00004.mark85.r7item110](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark85.r7item110) | Vouli | ok | καλὴν ἢ κακὴν, ἣν ἐξύφανε μακρά σειρὰ ἐνιαυτῶν καὶ πα<br> | καλὴν ἢ κακήν, ἣν ἐξύφανε μακρὰ σειρὰ ἐνιαυτῶν καὶ πα | λὴν ἡ κακὴν, ἣν ἐξύφανε μακρὰ σειρὰ ἐνιαυτῶν καὶ πᾶ- |
| [s2-49598b2e848ab1f0ee1e-p00004.mark85.r7item111](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00004.mark85.r7item111) | Vouli | ok | παρελθόντος; ἢ νομίζετε, κύριοι, ὅτι οἱανδήποτε κατάστασιν<br> | παρελθόντος; ἢ νομίζετε, κύριοι, ὅτι οἱανδήποτε κατάσταση | παρελθόντος; ἡ νομίζετε, κύριοι, ὅτι οἱανδήποτε κατάσταθν |
| [s2-49598b2e848ab1f0ee1e-p00005.comment.r7item112](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.comment.r7item112) | Vouli | ok | κεντρωθῆ εἰς τὰς χεῖρας τῶν ἀδελφοποιητῶν σας χαυβιαρο-<br> | κεντρωθῆ εἰς τὰς χεῖρας τῶν ἀδελφοποιητῶν<br>χαβιαρο | κεντοωθῆ εἰς τὰς χεῖρας τῶν ἀδελφοποιητῶν σας χαυβιαρο- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark0.r7item0](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark0.r7item0) | Vouli | ok | χείας καὶ πλήρους συγκοινωνίας; Τί εἶναι τὰ σιδηρὰ ἐλά-<br> | χείας καὶ πλήρους συγκοινωνίας; Τί εἶναι τὰ σιδηρὰ ἐλά | χείᾳς καὶ πλήρους συγκοινωνίας; Τί εἶναι τὰ σιδηρὰ ἐλά- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark0.r7item119](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark0.r7item119) | Vouli | ok | (empty) | (empty) | ) |
| [s2-49598b2e848ab1f0ee1e-p00005.mark0.r7item2](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark0.r7item2) | Vouli | ok | χείας<br>Κυβέρνησις σπουδαίως σκέπτεται περὶ ἀποκαταστάσεως<br>μουσι τὴν Ἑλληνικὴν ταύτην γῆν, ἢ ἀπόδειξις, ὅτι ἡ<br>τα<br>T<br> | ουσι τὴν Ἑλληνικὴν ταύτην γήν, η απόδειξις, ὅτι ἡ<br>Κυβέρνησις σπουδαίως σκέπτεται περὶ ἀποκαταστάσεως<br>χεία,<br>mi<br>r | Κυβέρνησις σπουδαίως σκέπτεται περὶ ἀποκαταστάσεως τα- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark1.r7item1](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark1.r7item1) | Vouli | ok | αυτό<br>ως<br>ὅταν κερδίζῃ φεύγων ἀφίνει καί τινα κέρματα διὰ τοὺς ὑ-<br> | αυτοπροσω<br>ὅταν κερδίζῃ φεύγων ἀφίνει καί τινα κέρματα διὰ τοὺς ὑ- | ὅταν κερδίζῃ φεύγων ἀφίνει καί τινα κέρματα διὰ τοὺς ὑ- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark1.r7item3](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark1.r7item3) | Vouli | ok | αὐτῶν Κορωνιος, αφου σας<br>&quot;<br>αὐτοπροσώπως νὰ σᾶς εὐχαριστήσῃ, καὶ ὡς ὁ χαρτοπαίκτης<br>BY<br>ἀφίνει καί<br>τινα κέρματα διὰ τοὺς ὡς<br> | αὐτῶν Κορωνιος, αφου σας<br>αὐτοπροσώπως νὰ σᾶς εὐχαριστήσῃ, καὶ ὡς ὁ χαρτοπαίκτης<br>DIY<br>απίνει και<br>...<br>σινα χέρια τα διά τους θα<br>is | αὐτοπροσώπως νὰ σᾶς εὐχαριστήσῃ, καὶ ὡς ὁ χαρτοπαίκτης |
| [s2-49598b2e848ab1f0ee1e-p00005.mark10.r7item11](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark10.r7item11) | Vouli | ok | την τῆς Κυβερνήσεως, δὲν ἀρύεται τὴν πεποίθησιν, ότι<br> | της Κυβερνήσεως, δὲν ἀρύεται τὴν πεποίθησιν, ὅτι | 11ν τῆς Κυβερνήσεως. Δὲν ἄρύεται τὴν πεποιθησιν, 67ι |
| [s2-49598b2e848ab1f0ee1e-p00005.mark10.r7item12](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark10.r7item12) | Vouli | ok | σπουδαίως σκέπτεπαι αὕτη νὰ ἐξαγάγῃ ἡμᾶς ἐκ ἐκ τῆς παν·<br>тоб<br> | σπουδαίως σκέπτεται αὕτη νὰ ἐξαγάγῃ ἡμᾶς ἐκ ἐκ τῆς παν | σπουδαίως σκέπτεπαι αὕτη νὰ ἐξαγάγῃ ἡμᾶς ἐκ ἐκ τῆς παν- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark11.r7item10](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark11.r7item10) | Vouli | ok | σχεσθε ότι αν ἦναι<br>η<br>σητε τὸ κακόν. ᾿Αφοῦ λιμοκτονοῦν, ἂς ζήσωσι τουλάχιστον<br> | σχεσθε στι<br>ναι μακροστο<br>σητε τὸ κακόν. ᾿Αφοῦ λιμοκτονοῦν, ἂς ζήσωσι τοὐλάχιστον | σητε τὸ κακόν. Ἀφοῦ λιμοκτονοῦν, ἃς ζήσωσι τοὐλάχιστον |
| [s2-49598b2e848ab1f0ee1e-p00005.mark11.r7item13](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark11.r7item13) | Vouli | ok | · τούτου ζημίαν οι υπαλλήλοι και ο στρατος,<br>και<br> | τούτου ζημίαν οι υπαλλήλοι και<br>ο στρατός,<br>και | τουτου ζημεαν Οἱ ΔταΛΑηΛΟΙ ΧΑι Ο 5τρατοε» τας |
| [s2-49598b2e848ab1f0ee1e-p00005.mark11.r7item14](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark11.r7item14) | Vouli | ok | σχεσθε ὅτι ἂν ἦναι μακρόβιος ἡ ὑπουργεία σας θὰ θεραπεύ-<br>Δ. Υάσιωσι τουλάχιστον<br> | σχεσθε ὅτι ἂν εἶναι μακρόβιος ἡ ὑπουργεία σας θὰ θεραπεύ<br>* Υάσωση τουλάχιστον | νεσθε ὅτι ἂν ἤναι μακρόβιος ἡ ὑπουργεία σας θὰ θεραπεύ- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark13.r7item16](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark13.r7item16) | Vouli | ok | παουερνήσεως, κανοσύν και η πονομ<br>τὸ πρόγραμμα αὐτῆς. Καὶ σᾶς ἐρωτῶ, κύριοι, ἐὰν τις ἀφα<br>To<br>-<br>1<br> | το<br>ρνήσεως, καυοσυν<br>και η<br>πρόγραμμα αὐτῆς. Καὶ σᾶς ἐρωτῶ, κύριοι, ἐάν τις ἀφα<br>-απλο διαι<br>In<br>] | τὸ πρόγραμμα αὐτῆς. Καὶ σᾶς ἐρωτῶ, κύριοι, ἐάν τις ἀφα-ὶ ἡ |
| [s2-49598b2e848ab1f0ee1e-p00005.mark14.r7item116](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark14.r7item116) | Vouli | ok | νικών συμφερόντων τοῦ Κράτους. Εἴμεθα πιστοὶ ἀκόλουθοι<br> | νικῶν συμφερόντων τοῦ Κράτους. Εἴμεθα πιστοὶ ἀκόλουθοι | νικῶν συμφερόντων τοῦ Κράτους. Εἴμεθα πιστοὶ ἀκόλουθοι |
| [s2-49598b2e848ab1f0ee1e-p00005.mark14.r7item74](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark14.r7item74) | Vouli | ok | ὁμάδος τινὸς ἐκλογέων ὀφείλουσι νὰ ἦναι ἥττονα τῶν γε-<br> | ὁμάδος τινὸς ἐκλογέων ὀφείλουσι<br>νὰ ἦναι ἥττονα τῶν γε- | ὁμάδος τινὸς ἐκλογέων ὀφείλουσι νὰ ἤναι ἤττονα τῶν γε- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark15.r7item115](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark15.r7item115) | Vouli | ok | τῆς παραμάνας σας Ἐθνικῆς Τραπέζης.<br> | τῆς παραμάνας σας Εθνικής Τραπέζης. | τῆς παριμάνας σας Ἐθνικῆς. Τραπέζης. |
| [s2-49598b2e848ab1f0ee1e-p00005.mark15.r7item17](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark15.r7item17) | Vouli | ok | νον, τους υπαλλήλουs, nul<br>πηλιο<br>ὑπεχωρήσατε, ἵνα μὴ ἐπισύρητε τὴν ὀργὴν καὶ τὴν κατάραν<br>۲۵..... T<br> | νον, τους υπαλλήλους, και<br>ὑπεχωρήσατε, ἵνα μὴ ἐπισύρητε τὴν ὀργὴν καὶ τὴν κατάραν<br>ΟΡΑ..... | ὑπεχωρήσατε, ἵνα μὴ ἐπισύρητε τὴν ὀργὴν καὶ τὴν κατάραν |
| [s2-49598b2e848ab1f0ee1e-p00005.mark15.r7item18](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark15.r7item18) | Vouli | ok | νὸν, τοὺς ὑπαλλήλους, καὶ τὸν στρατὸν ἡ ἀγανάκτησις, δὲν<br>ήν κατάραν<br> | νὸν, τοὺς ὑπαλλήλους, καὶ τὸν στρατὸν ἡ ἀγανάκτησις, δὲν<br>&quot;<br>-<br>και ανδοι Αποδες και την κατάραν | νὸν, τοὺς ὑπαλλήλους, καὶ τὸν στρατὸν ἡ ἀγανάκτησις, δὲν |
| [s2-49598b2e848ab1f0ee1e-p00005.mark16.r7item74](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark16.r7item74) | Vouli | ok | ὁμάδος τινὸς ἐκλογέων ὀφείλουσι νὰ ἦναι ἥττονα τῶν γε-<br> | ὁμάδος τινὸς ἐκλογέων ὀφείλουσι<br>νὰ ἦναι ἥττονα τῶν γε- | ὁμάδος τινὸς ἐκλογέων ὀφείλουσι νὰ ἤναι ἤττονα τῶν γε- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark16.r7item75](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark16.r7item75) | Vouli | ok | μεν τοῦτο, κύριοι, καθόσον θεωροῦμεν, ὅτι τὰ συμφέροντα<br> | μὲν τοῦτο, κύριοι, καθόσον θεωροῦμεν, ὅτι τὰ συμφέροντα | μεν τοῦτο, κύριοι, καθόσον θεωροῦμεν, ὅτι τὰ συμφέροντα |
| [s2-49598b2e848ab1f0ee1e-p00005.mark17.r7item17](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark17.r7item17) | Vouli | ok | νον, τους υπαλλήλουs, nul<br>πηλιο<br>ὑπεχωρήσατε, ἵνα μὴ ἐπισύρητε τὴν ὀργὴν καὶ τὴν κατάραν<br>۲۵..... T<br> | νον, τους υπαλλήλους, και<br>ὑπεχωρήσατε, ἵνα μὴ ἐπισύρητε τὴν ὀργὴν καὶ τὴν κατάραν<br>ΟΡΑ..... | ὑπεχωρήσατε, ἵνα μὴ ἐπισύρητε τὴν ὀργὴν καὶ τὴν κατάραν |
| [s2-49598b2e848ab1f0ee1e-p00005.mark17.r7item18](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark17.r7item18) | Vouli | ok | νὸν, τοὺς ὑπαλλήλους, καὶ τὸν στρατὸν ἡ ἀγανάκτησις, δὲν<br>ήν κατάραν<br> | νὸν, τοὺς ὑπαλλήλους, καὶ τὸν στρατὸν ἡ ἀγανάκτησις, δὲν<br>&quot;<br>-<br>και ανδοι Αποδες και την κατάραν | νὸν, τοὺς ὑπαλλήλους, καὶ τὸν στρατὸν ἡ ἀγανάκτησις, δὲν |
| [s2-49598b2e848ab1f0ee1e-p00005.mark17.r7item19](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark17.r7item19) | Vouli | ok | στοιχείων του μου,<br>ἐφαρμογῆς αὐτοῦ τοῦ Νόμου, ἀρκετὰ ἐξεδηλώθη ἀπὸ τὸ κοι<br> | τοιχείων<br>231<br>ἐφαρμογῆς αὐτοῦ τοῦ Νόμου, ἀρκετὰ ἐξεδηλώθη ἀπὸ τὸ κοι | ναρμογῆς αὐτοῦ τοῦ Νόμου, ἀρκετὰ ἐξεδηλώθη ἀπὸ τὸ κοι- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark18.r7item75](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark18.r7item75) | Vouli | ok | μεν τοῦτο, κύριοι, καθόσον θεωροῦμεν, ὅτι τὰ συμφέροντα<br> | μὲν τοῦτο, κύριοι, καθόσον θεωροῦμεν, ὅτι τὰ συμφέροντα | μεν τοῦτο, κύριοι, καθόσον θεωροῦμεν, ὅτι τὰ συμφέροντα |
| [s2-49598b2e848ab1f0ee1e-p00005.mark18.r7item76](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark18.r7item76) | Vouli | ok | κατὰ πολλὰς ἑκατοντάδας χιλιάδας δραχμῶν; Καὶ ἐπράξα-<br> | κατὰ πολλὰς ἑκατοντάδας χιλιάδας δραχμῶν; Καὶ ἐπράξα- | κατὰ πολλὰς ἑκατοντάδας χιλιάδας δραχμῶν; Καὶ ἐπράξα- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark19.r7item19](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark19.r7item19) | Vouli | ok | στοιχείων του μου,<br>ἐφαρμογῆς αὐτοῦ τοῦ Νόμου, ἀρκετὰ ἐξεδηλώθη ἀπὸ τὸ κοι<br> | τοιχείων<br>231<br>ἐφαρμογῆς αὐτοῦ τοῦ Νόμου, ἀρκετὰ ἐξεδηλώθη ἀπὸ τὸ κοι | ναρμογῆς αὐτοῦ τοῦ Νόμου, ἀρκετὰ ἐξεδηλώθη ἀπὸ τὸ κοι- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark19.r7item20](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark19.r7item20) | Vouli | ok | στοιχείων τοῦ βίου, καὶ μολονότι, πρὶν ἢ ἔλθῃ ἡ ἡμέρα τῆς<br>αινία 5 513 1<br> | τον εις ζημίαν μεγάλην ανα<br>στοιχείων τοῦ βίου, καὶ μολονότι, πρὶν ἢ ἔλθῃ ἡ ἡμέρα τῆς<br>VAL | στοιχείων τοῦ βίου, καὶ μολονότι, πρὶν ἢ ἔλθῃ ἡ ἡμέρα τῆς |
| [s2-49598b2e848ab1f0ee1e-p00005.mark2.r7item2](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark2.r7item2) | Vouli | ok | χείας<br>Κυβέρνησις σπουδαίως σκέπτεται περὶ ἀποκαταστάσεως<br>μουσι τὴν Ἑλληνικὴν ταύτην γῆν, ἢ ἀπόδειξις, ὅτι ἡ<br>τα<br>T<br> | ουσι τὴν Ἑλληνικὴν ταύτην γήν, η απόδειξις, ὅτι ἡ<br>Κυβέρνησις σπουδαίως σκέπτεται περὶ ἀποκαταστάσεως<br>χεία,<br>mi<br>r | Κυβέρνησις σπουδαίως σκέπτεται περὶ ἀποκαταστάσεως τα- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark20.r7item21](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark20.r7item21) | Vouli | ok | κύριοι, προχθες τους μουλευτας της<br>030<br>ψηφίζοντας Νομοσχέδιον, ὅπερ ἐζημίου τοὺς ἐκλογεῖς αὐτῶν<br> | τε, κύριοι, προχθες τους βουλευταί<br>2715<br>ψηφίζοντας Νομοσχέδιον, ὅπερ ἐζημίου τοὺς ἐκλογεῖς αὑτῶν | ηφίζοντας Νομοσχέδιον, ὅπερ ἐζημίου τοὺς ἐκλογεῖς αὐτῶν. |
| [s2-49598b2e848ab1f0ee1e-p00005.mark20.r7item76](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark20.r7item76) | Vouli | ok | κατὰ πολλὰς ἑκατοντάδας χιλιάδας δραχμῶν; Καὶ ἐπράξα-<br> | κατὰ πολλὰς ἑκατοντάδας χιλιάδας δραχμῶν; Καὶ ἐπράξα- | κατὰ πολλὰς ἑκατοντάδας χιλιάδας δραχμῶν; Καὶ ἐπράξα- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark21.r7item19](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark21.r7item19) | Vouli | ok | στοιχείων του μου,<br>ἐφαρμογῆς αὐτοῦ τοῦ Νόμου, ἀρκετὰ ἐξεδηλώθη ἀπὸ τὸ κοι<br> | τοιχείων<br>231<br>ἐφαρμογῆς αὐτοῦ τοῦ Νόμου, ἀρκετὰ ἐξεδηλώθη ἀπὸ τὸ κοι | ναρμογῆς αὐτοῦ τοῦ Νόμου, ἀρκετὰ ἐξεδηλώθη ἀπὸ τὸ κοι- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark21.r7item20](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark21.r7item20) | Vouli | ok | στοιχείων τοῦ βίου, καὶ μολονότι, πρὶν ἢ ἔλθῃ ἡ ἡμέρα τῆς<br>αινία 5 513 1<br> | τον εις ζημίαν μεγάλην ανα<br>στοιχείων τοῦ βίου, καὶ μολονότι, πρὶν ἢ ἔλθῃ ἡ ἡμέρα τῆς<br>VAL | στοιχείων τοῦ βίου, καὶ μολονότι, πρὶν ἢ ἔλθῃ ἡ ἡμέρα τῆς |
| [s2-49598b2e848ab1f0ee1e-p00005.mark21.r7item22](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark21.r7item22) | Vouli | ok | τος, υπερQAA<br>MUA<br>5001<br>τὸν εἰς ζημίαν μεγάλην διὰ τῆς ὑπερτιμήσεως τῶν πρώτων<br> | τος, υπερα<br>τὸν εἰς ζημίαν μεγάλην διὰ τῆς ὑπερτιμήσεως τῶν πρώτων<br>Η Δ.. | τὸν εἰς ζημίαν μεγάλην διὰ τῆς ὑπερτιμήσεως τῶν πρώτων |
| [s2-49598b2e848ab1f0ee1e-p00005.mark22.r7item21](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark22.r7item21) | Vouli | ok | κύριοι, προχθες τους μουλευτας της<br>030<br>ψηφίζοντας Νομοσχέδιον, ὅπερ ἐζημίου τοὺς ἐκλογεῖς αὐτῶν<br> | τε, κύριοι, προχθες τους βουλευταί<br>2715<br>ψηφίζοντας Νομοσχέδιον, ὅπερ ἐζημίου τοὺς ἐκλογεῖς αὑτῶν | ηφίζοντας Νομοσχέδιον, ὅπερ ἐζημίου τοὺς ἐκλογεῖς αὐτῶν. |
| [s2-49598b2e848ab1f0ee1e-p00005.mark25.r7item24](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark25.r7item24) | Vouli | ok | πουτοι, καθόσον την εν τω ποινσου<br>τὴν ἐρρυθμίσαμεν μὲ τὰ ἀτομικὰ ἡμῶν συμφέροντα ἢ τῶν<br>έκλ<br> | τοι, καθόσον την εν τῷ και<br>τὴν ἐρρυθμίσαμεν μὲ τὰ ἀτομικὰ ἡμῶν συμφέροντα ἢ τῶν | Τν ἐρρυθμίσαμεν μὲ τὰ ἀτομικὰ ἡμῶν συμφέροντα ἡ τῶν) |
| [s2-49598b2e848ab1f0ee1e-p00005.mark27.r7item24](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark27.r7item24) | Vouli | ok | πουτοι, καθόσον την εν τω ποινσου<br>τὴν ἐρρυθμίσαμεν μὲ τὰ ἀτομικὰ ἡμῶν συμφέροντα ἢ τῶν<br>έκλ<br> | τοι, καθόσον την εν τῷ και<br>τὴν ἐρρυθμίσαμεν μὲ τὰ ἀτομικὰ ἡμῶν συμφέροντα ἢ τῶν | Τν ἐρρυθμίσαμεν μὲ τὰ ἀτομικὰ ἡμῶν συμφέροντα ἡ τῶν) |
| [s2-49598b2e848ab1f0ee1e-p00005.mark27.r7item27](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark27.r7item27) | Vouli | ok | Οτι ειναι<br>τύμπα<br>Κυβερνήσεως καὶ πιστοὶ ἀκόλουθοι αὐτῆς. Ναὶ, κύριοι, εἴμε-<br>A..<br> | γιας,<br>ότι είναι<br>52<br>Κυβερνήσεως καὶ πιστοὶ ἀκόλουθοι αὐτῆς. Ναί, κύριοι, εἴμε<br>A.. | βυβερνήσεως καὶ πιστοὶ ἀκόλουθοι αὐτῆς. Ναὶ, κύριοι, εἴμε- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark27.r7item77](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark27.r7item77) | Vouli | ok | θα τοιοῦτοι, καθόσον τὴν ἐν τῷ Κοινοβουλίω θέσιν μας δέν<br> | θα τοιοῦτοι, καθόσον τὴν ἐν τῷ Κοινοβουλίῳ θέσιν μας δεν | θα τοιοῦτοι, καθόσον τὴν ἐν τῷ Κοινοβουλίῳ θέσιν μας δὲν |
| [s2-49598b2e848ab1f0ee1e-p00005.mark3.r7item1](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark3.r7item1) | Vouli | ok | αυτό<br>ως<br>ὅταν κερδίζῃ φεύγων ἀφίνει καί τινα κέρματα διὰ τοὺς ὑ-<br> | αυτοπροσω<br>ὅταν κερδίζῃ φεύγων ἀφίνει καί τινα κέρματα διὰ τοὺς ὑ- | ὅταν κερδίζῃ φεύγων ἀφίνει καί τινα κέρματα διὰ τοὺς ὑ- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark3.r7item3](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark3.r7item3) | Vouli | ok | αὐτῶν Κορωνιος, αφου σας<br>&quot;<br>αὐτοπροσώπως νὰ σᾶς εὐχαριστήσῃ, καὶ ὡς ὁ χαρτοπαίκτης<br>BY<br>ἀφίνει καί<br>τινα κέρματα διὰ τοὺς ὡς<br> | αὐτῶν Κορωνιος, αφου σας<br>αὐτοπροσώπως νὰ σᾶς εὐχαριστήσῃ, καὶ ὡς ὁ χαρτοπαίκτης<br>DIY<br>απίνει και<br>...<br>σινα χέρια τα διά τους θα<br>is | αὐτοπροσώπως νὰ σᾶς εὐχαριστήσῃ, καὶ ὡς ὁ χαρτοπαίκτης |
| [s2-49598b2e848ab1f0ee1e-p00005.mark39.r7item82](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark39.r7item82) | Vouli | ok | λαμβάνων μισθὸν ἀστυνομικοῦ κλητῆρος, σπουδάζει τὴν ἰα-<br> | λαμβάνων μισθὸν ἀστυνομικοῦ κλητῆρος, σπουδάζει τὴν ἰα- | λαμβάνων μισθὸν ἀστυνομικοῦ κλητῆρος, σπουδάζει τὴν ἱα- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark4.r7item4](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark4.r7item4) | Vouli | ok | φορίας, τῆς ὁποίας τὰ δεινὰ ἐπακόλουθα τόσον εὐγλώττως<br>περισ...<br> | φορίας, τῆς ὁποίας τὰ δεινὰ ἐπακόλουθα τόσον εὐγλώττως<br>περιέ.. | φθρίας, τῆς ὁποίας τὰ δεινὰ ἐπακόλουθα τόσον εὐγλώττως. |
| [s2-49598b2e848ab1f0ee1e-p00005.mark4.r7item7](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark4.r7item7) | Vouli | ok | προλειαίνει τὴν ὁδὸν πρὸς ἄρσιν τῆς ἀναγκαστικῆς κυκλο-<br>000!<br>A<br>A<br> | προλειαίνει τὴν ὁδὸν πρὸς ἄρσιν τῆς ἀναγκαστικῆς κυκλο-<br>Οπα!<br>Δ | Σβολειαίνει τὴν ὁδὸν πρὸς ἄοσιυ τ6. Α . άστυς |
| [s2-49598b2e848ab1f0ee1e-p00005.mark45.r7item84](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark45.r7item84) | Vouli | ok | δὲ τοῦ μνημονευθέντος ἀριθμοῦ δύνασθε νὰ κρίνητε καὶ περὶ<br> | δὲ τοῦ μνημονευθέντος ἀριθμοῦ δύνασθε νὰ κρίνητε καὶ περὶ | δὲ τοῦ μνημονευθέντος ἀριθμοῦ δύνασθε νὰ κρίνητε καὶ περὶ |
| [s2-49598b2e848ab1f0ee1e-p00005.mark5.r7item5](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark5.r7item5) | Vouli | ok | 11 δευτερα αποστολη του<br>ὑπερτίμησις τῶν Ἑλληνικῶν χρεωγράφων, τὰ ὁποῖα εἶχον συγ-<br>~.. 21.1ῶν σας ναυβιαρο-<br> | Η δευτερα αποστολή του μεσο<br>ὑπερτίμησις τῶν Ἑλληνικῶν χρεωγράφων,τὰ ὁποῖα εἶχον συγ-<br>21.100 πρωτῶν σας χαβιαρο | ὑπερτίμησις τῶν Ἑλληνικῶν χρεωγράφων, τὰ ὁποῖα εἶχον συγ- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark57.r7item45](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark57.r7item45) | Vouli | ok | ρίον Γερλὶ σταθμεύουσιν, ὡς σᾶς εἶπεν ὁ κ. Δηλιγιάννης,<br> | αστυνομικων κλητηρι<br>βίον Γερλὶ σταθμεύουσιν, ὡς σᾶς εἶπεν ὁ Δηλιγιάννης, | βίον Γερλὶ σταθμεύουσιν, ὡς σᾶς εἶπεν ὁ κ. Δηλιγιάννης, |
| [s2-49598b2e848ab1f0ee1e-p00005.mark57.r7item89](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark57.r7item89) | Vouli | ok | 27 κλητῆρες. Τὸ χωρίον τοῦτο, κύριοι, κεῖται μεταξύ Λα-<br> | 27 κλητήρες. Τὸ χωρίον τοῦτο, κύριοι, κεῖται<br>μεταξύ Λα | 27 κλητῆρες. Τὸ χωρίον τοῦτο, κύριοι, κεῖται μεταξὺ Λα- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark6.r7item6](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark6.r7item6) | Vouli | ok | 404<br>ποδύγιον, το όποιον προκειται<br> | λυγιον, το<br>ΑΛΑ<br>119 101010 | ηυχιΟν, τΟ ΟΝΟΙΟΝ πΟΔπΕΙΙΑ..... |
| [s2-49598b2e848ab1f0ee1e-p00005.mark6.r7item7](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark6.r7item7) | Vouli | ok | προλειαίνει τὴν ὁδὸν πρὸς ἄρσιν τῆς ἀναγκαστικῆς κυκλο-<br>000!<br>A<br>A<br> | προλειαίνει τὴν ὁδὸν πρὸς ἄρσιν τῆς ἀναγκαστικῆς κυκλο-<br>Οπα!<br>Δ | Σβολειαίνει τὴν ὁδὸν πρὸς ἄοσιυ τ6. Α . άστυς |
| [s2-49598b2e848ab1f0ee1e-p00005.mark76.r7item61](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark76.r7item61) | Vouli | ok | ἀναμιμνήσκηται ὁ Θεσσαλικός λαὸς τῆς ἐποχῆς ἐκείνης,<br> | αναμιμνήσκηται ὁ Θεσσαλικός λαός τῆς ἐποχῆς ἐκείνης, | ἀναμιμνήσκηται ὁ Θεσσαλικὸς λαὸς τῆς ἐποχῆς ἐκείνης,ἡ |
| [s2-49598b2e848ab1f0ee1e-p00005.mark76.r7item92](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark76.r7item92) | Vouli | ok | καθ᾿ ἂν ἔβλεπε τοὺς Ὑπομοιράρχους κρατοῦντας βούρδουλαν<br> | καθ᾽ ἂν ἔβλεπε τοὺς Ὑπομοιράρχους κρατοῦντας βούρδουλαν | καθ’ ἣν ἔβλεπε τοὺς Ὑπομοιράρχους κρατοῦντας βούρδουλαν. |
| [s2-49598b2e848ab1f0ee1e-p00005.mark8.r7item12](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark8.r7item12) | Vouli | ok | σπουδαίως σκέπτεπαι αὕτη νὰ ἐξαγάγῃ ἡμᾶς ἐκ ἐκ τῆς παν·<br>тоб<br> | σπουδαίως σκέπτεται αὕτη νὰ ἐξαγάγῃ ἡμᾶς ἐκ ἐκ τῆς παν | σπουδαίως σκέπτεπαι αὕτη νὰ ἐξαγάγῃ ἡμᾶς ἐκ ἐκ τῆς παν- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark8.r7item9](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark8.r7item9) | Vouli | ok | τοδαπής καχεξίας, εἰς ἦν εὑρισκόμεθα; Καὶ τί εἶναι, κύριοι,<br>τὸ ἰσο<br> | τοδαπῆς καχεξίας, εἰς ἣν εὑρισκόμεθα; Καὶ τί εἶναι, κύριοι,<br>τὸ ἐποχ | τοδαπῆς καχεξίας, εἰς ἣν εὑρισκόμεθα; Καὶ τί εἶναι, κύριοι, |
| [s2-49598b2e848ab1f0ee1e-p00005.mark82.r7item94](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark82.r7item94) | Vouli | ok | νὰ μένωσιν ἀνατεθειμένα τὰ ἀστυνομικὰ καθήκοντα εἰς τοὺς<br> | νὰ μένωσιν ἀνατεθειμένα τὰ ἀστυνομικὰ καθήκοντα εἰς τοὺς | νὰ μένωσιν ἀνατεθειμένα τὰ ἀστυνομικὰ καθήκοντα εἰς τοὺς |
| [s2-49598b2e848ab1f0ee1e-p00005.mark82.r7item95](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark82.r7item95) | Vouli | ok | καταρτισθῶσι Δημοτικαὶ ᾿Αστυνομίαι ἐν Θεσσαλίᾳ, ἠθέλατε<br> | καταρτισθῶσι Δημοτικαὶ ᾿Αστυνομίαι ἐν Θεσσαλίᾳ, ἠθέλατε | καταρτισθῶσι Δημοτικα! Ἀστυνομίαι ἐν Θεσσαλίᾳ, ἠθέλατε |
| [s2-49598b2e848ab1f0ee1e-p00005.mark84.r7item95](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark84.r7item95) | Vouli | ok | καταρτισθῶσι Δημοτικαὶ ᾿Αστυνομίαι ἐν Θεσσαλίᾳ, ἠθέλατε<br> | καταρτισθῶσι Δημοτικαὶ ᾿Αστυνομίαι ἐν Θεσσαλίᾳ, ἠθέλατε | καταρτισθῶσι Δημοτικα! Ἀστυνομίαι ἐν Θεσσαλίᾳ, ἠθέλατε |
| [s2-49598b2e848ab1f0ee1e-p00005.mark84.r7item96](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark84.r7item96) | Vouli | ok | τάλην καὶ συναλλαγήν. ᾿Αλλ᾿ ἀφοῦ, κύριοι, δὲν ἠδύναντο νὰ<br> | τάλην καὶ συναλλαγήν. ᾿Αλλ᾽ ἀφοῦ, κύριοι, δὲν ἠδύναντο νὰ | τάλην καὶ συναλλαγήν. Ἀλλ’ ἀφοῦ, κύριοι, δὲν ἠδύναντο νὰ |
| [s2-49598b2e848ab1f0ee1e-p00005.mark86.r7item96](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark86.r7item96) | Vouli | ok | τάλην καὶ συναλλαγήν. ᾿Αλλ᾿ ἀφοῦ, κύριοι, δὲν ἠδύναντο νὰ<br> | τάλην καὶ συναλλαγήν. ᾿Αλλ᾽ ἀφοῦ, κύριοι, δὲν ἠδύναντο νὰ | τάλην καὶ συναλλαγήν. Ἀλλ’ ἀφοῦ, κύριοι, δὲν ἠδύναντο νὰ |
| [s2-49598b2e848ab1f0ee1e-p00005.mark86.r7item97](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark86.r7item97) | Vouli | ok | νομίαν τῆς Θεσσαλλίας, καὶ ἐδῶ ἀνεῦρον τὴν φοβερὰν σπα-<br> | νομίαν τῆς Θεσσαλλίας, καὶ ἐδῶ ἀνεῦρον τὴν φοβερὰν<br>σπα | νομίαν τῆς Θεσσαλλίας, καὶ ἐδῶ ἀνεῦρον τὴν φοβερὰν σπα- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark9.r7item10](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark9.r7item10) | Vouli | ok | σχεσθε ότι αν ἦναι<br>η<br>σητε τὸ κακόν. ᾿Αφοῦ λιμοκτονοῦν, ἂς ζήσωσι τουλάχιστον<br> | σχεσθε στι<br>ναι μακροστο<br>σητε τὸ κακόν. ᾿Αφοῦ λιμοκτονοῦν, ἂς ζήσωσι τοὐλάχιστον | σητε τὸ κακόν. Ἀφοῦ λιμοκτονοῦν, ἃς ζήσωσι τοὐλάχιστον |
| [s2-49598b2e848ab1f0ee1e-p00005.mark9.r7item14](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark9.r7item14) | Vouli | ok | σχεσθε ὅτι ἂν ἦναι μακρόβιος ἡ ὑπουργεία σας θὰ θεραπεύ-<br>Δ. Υάσιωσι τουλάχιστον<br> | σχεσθε ὅτι ἂν εἶναι μακρόβιος ἡ ὑπουργεία σας θὰ θεραπεύ<br>* Υάσωση τουλάχιστον | νεσθε ὅτι ἂν ἤναι μακρόβιος ἡ ὑπουργεία σας θὰ θεραπεύ- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark94.r7item100](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark94.r7item100) | Vouli | ok | νὰ συστήσῃ γραμματοδιδασκαλεῖα καὶ εἰς τὰ μικρότερα χω-<br> | νὰ συστήση γραμματοδιδασκαλεῖα καὶ εἰς τὰ μικρότερα χω | νὰ συστήσῃ γραμματοδιδασκαλεῖα καὶ εἰς τὰ μικρότερα χω- |
| [s2-49598b2e848ab1f0ee1e-p00005.mark94.r7item101](../../harvest/three_engines_review.html#s2-49598b2e848ab1f0ee1e-p00005.mark94.r7item101) | Vouli | ok | λιστα ἤθελον παρακαλέσει τὸν κ. Ὑπουργὸν τῆς Παιδείας<br> | λιστα ήθελον παρακαλέσει τον και<br>Ὑπουργὸν τῆς Παιδείας | λιστα ἤθελον παρακαλέσει τὸν κ. Ὑπουργὸν τῆς Παιδείας |
| [s2-74cdb23a34ca4a6cd01e-p00007.mark1.r7item1](../../harvest/three_engines_review.html#s2-74cdb23a34ca4a6cd01e-p00007.mark1.r7item1) | Vouli | ok | ΔΡΑΓΟΥΜΗΣ (Υπουργός τῶν Ἐξωτερικῶν.) ΔενΥ ΛΙ,<br>αὐτό· λέγει, καθ&#x27; ἣν ἐποχὴν εἶχε τὴν πρὸς στρατοισιν νό<br> | ΔΡΑΓΟΥΜΗΣ (Υπουργός τῶν Εξωτερικών.) ΔεΥ ΛΕ<br>αὐτό· λέγει, καθ᾿ ἣν ἐποχὴν εἶχε τὴν πρὸς στρατου σιν νο | αὐτό· λέγει, καθ’ ἣν ἐποχὴν εἶχε τὴν πρὸς στόλι σιν νό- |
| [s2-74cdb23a34ca4a6cd01e-p00007.mark1.r7item3](../../harvest/three_engines_review.html#s2-74cdb23a34ca4a6cd01e-p00007.mark1.r7item3) | Vouli | ok | ۲۸۰۱۲°γραμμένος;<br>ΔΡΑΓΟΥΜΗΣ (Ὑπουργὸς τῶν Ἐξωτερικῶν.) Δὲν λέγει<br> | : Sonardrbodlalla surden.<br>ΔΡΑΓΟΥΜΗΣ (Υπουργός των Εξωτερικών.) Δεν λέγει | ΔΡΑΓΟΥΜΗΣ (Ὑπούργος τῶν Ἐξωτερικῶν.) Δὲν λέγι |
| [s2-74cdb23a34ca4a6cd01e-p00007.mark11.r7item11](../../harvest/three_engines_review.html#s2-74cdb23a34ca4a6cd01e-p00007.mark11.r7item11) | Vouli | ok | Judo sua su d<br>τῶν ἀρρένων ὑπηρέτησεν ὡς κληροῦχος καὶ ὡς ἐπίστρατος,<br> | 1. 02. Sva sudo<br>τῶν ἀρρένων ὑπηρέτησεν ὡς κληροῦχος καὶ ὡς ἐπίστρατο, | τῶν ἀρρένων ὑπηρέτησεν ὡς κληροῦχος καὶ ὡς ἐπίστρατος |
| [s2-74cdb23a34ca4a6cd01e-p00007.mark11.r7item13](../../harvest/three_engines_review.html#s2-74cdb23a34ca4a6cd01e-p00007.mark11.r7item13) | Vouli | ok | σεις», ἐπειδὴ ὁ ἐγγεγραμμένος ἀπ᾿ ἀρχῆς εἰς τὸ μητρῷον<br> | σεις», ἐπειδὴ ὁ ἐγγεγραμμένος ἀπ&#x27; ἀρχῆς εἰς τὸ μητρῷον | Τοῦ, ἐπειδὴ ὁ ἐγγεγραμμένος ἀπ’ ἄρχῆς εἰς τὸ μητρῷον |
| [s2-74cdb23a34ca4a6cd01e-p00007.mark11.r7item9](../../harvest/three_engines_review.html#s2-74cdb23a34ca4a6cd01e-p00007.mark11.r7item9) | Vouli | ok | όσάκις ἐκλήθη ἐπιστρατεία, εἰς τὸ διάστημα, καθ&#x27; ὁ ὁ μη<br> | ὁσάκις ἐκλήθη ἐπιστρατεία, εἰς τὸ διάστημα, καθ᾽ ὁ ὁ μὴ | τάκις ἐκλήθη ἐπιστρατεία, εἰς τὸ διάστημα, καθ’ ὃ ὁ μὴ |
| [s2-74cdb23a34ca4a6cd01e-p00007.mark13.r7item108](../../harvest/three_engines_review.html#s2-74cdb23a34ca4a6cd01e-p00007.mark13.r7item108) | Vouli | ok | ἄρθρον τοῦτο, τὸ ὁποῖον λέγει «εἰς ἀπάσας τὰς ὑποχρεώ<br> | ἄρθρον τοῦτο, τὸ ὁποῖον λέγει «εἰς ἀπάσας τὰς ὑποχρεώ | ἄρθρον τοῦτο, τὸ ὁποῖον λέγει «εἰς ἁπάσας τὰς ὑποχριώ- |
| [s2-74cdb23a34ca4a6cd01e-p00007.mark13.r7item11](../../harvest/three_engines_review.html#s2-74cdb23a34ca4a6cd01e-p00007.mark13.r7item11) | Vouli | ok | Judo sua su d<br>τῶν ἀρρένων ὑπηρέτησεν ὡς κληροῦχος καὶ ὡς ἐπίστρατος,<br> | 1. 02. Sva sudo<br>τῶν ἀρρένων ὑπηρέτησεν ὡς κληροῦχος καὶ ὡς ἐπίστρατο, | τῶν ἀρρένων ὑπηρέτησεν ὡς κληροῦχος καὶ ὡς ἐπίστρατος |
| [s2-74cdb23a34ca4a6cd01e-p00007.mark13.r7item13](../../harvest/three_engines_review.html#s2-74cdb23a34ca4a6cd01e-p00007.mark13.r7item13) | Vouli | ok | σεις», ἐπειδὴ ὁ ἐγγεγραμμένος ἀπ᾿ ἀρχῆς εἰς τὸ μητρῷον<br> | σεις», ἐπειδὴ ὁ ἐγγεγραμμένος ἀπ&#x27; ἀρχῆς εἰς τὸ μητρῷον | Τοῦ, ἐπειδὴ ὁ ἐγγεγραμμένος ἀπ’ ἄρχῆς εἰς τὸ μητρῷον |
| [s2-74cdb23a34ca4a6cd01e-p00007.mark23.r7item21](../../harvest/three_engines_review.html#s2-74cdb23a34ca4a6cd01e-p00007.mark23.r7item21) | Vouli | ok | των αρρενων, επειοη συν<br>γράφη ἐγκαίρως, θὰ ὑπηρετήσῃ εἰς τὸν ἐνεργὸν στρατόν· θὰ<br> | αμμένων, επειση<br>&#124; γράφη εγκαίρως, θὰ ὑπηρετήσῃ εἰς τὸν ἐνεργὸν στρατόν θα | γράφη ἐγκαίρῶς, θὰ ὑπηρετήσῃ εἰς τὸν ἕνεργον στρατόν· θὰ |
| [s2-74cdb23a34ca4a6cd01e-p00007.mark37.r7item111](../../harvest/three_engines_review.html#s2-74cdb23a34ca4a6cd01e-p00007.mark37.r7item111) | Vouli | ok | καὶ θέλει διαμένει ὑπηρετῶν, μέχρις οὐ συμπληρώσει τὸ<br> | καὶ θέλει διαμένει ὑπηρετῶν, μέχρις οὐ συμπληρώσει το<br>ου | καὶ θέλει διαμένει ὑπηρετῶν, μέχρις οὐ συμπληρώσει τὸ |
| [s2-74cdb23a34ca4a6cd01e-p00007.mark37.r7item112](../../harvest/three_engines_review.html#s2-74cdb23a34ca4a6cd01e-p00007.mark37.r7item112) | Vouli | ok | τὴν ἐνεργὸν ὑπηρεσίαν· μεθ᾽ ὅ θέλει ταχθῆ εἰς τὴν ἐφεδρείαν<br> | τὴν ἐνεργὸν ὑπηρεσίαν μεθ&#x27; ὅ θέλει ταχθῆ εἰς τὴν ἐφεδρείαν | ἐν ἐνεργὸν ὑπηρεσίαν· μεθ’ ὃ θέλει ταχθῆ εἰς τὴν ἐφεδρείαν. |
| [s2-74cdb23a34ca4a6cd01e-p00007.mark7.r7item7](../../harvest/three_engines_review.html#s2-74cdb23a34ca4a6cd01e-p00007.mark7.r7item7) | Vouli | ok | ἐγγεγραμμένος δὲν ὑπηρέτησεν, θὰ ὑπηρετήσῃ ὅσον καὶ ὁσά-<br> | ἐγγεγραμμένος δὲν ὑπηρέτησεν, θὰ ὑπηρετήσῃ ὅσον καὶ ὁσά- | ἐγγεγραμμένος δὲν ὑπηρέτησεν, θὰ ὑπηρετήσῃ ὅσον καὶ ὀσά- |
| [s2-74cdb23a34ca4a6cd01e-p00007.mark9.r7item11](../../harvest/three_engines_review.html#s2-74cdb23a34ca4a6cd01e-p00007.mark9.r7item11) | Vouli | ok | Judo sua su d<br>τῶν ἀρρένων ὑπηρέτησεν ὡς κληροῦχος καὶ ὡς ἐπίστρατος,<br> | 1. 02. Sva sudo<br>τῶν ἀρρένων ὑπηρέτησεν ὡς κληροῦχος καὶ ὡς ἐπίστρατο, | τῶν ἀρρένων ὑπηρέτησεν ὡς κληροῦχος καὶ ὡς ἐπίστρατος |
| [s2-74cdb23a34ca4a6cd01e-p00007.mark9.r7item7](../../harvest/three_engines_review.html#s2-74cdb23a34ca4a6cd01e-p00007.mark9.r7item7) | Vouli | ok | ἐγγεγραμμένος δὲν ὑπηρέτησεν, θὰ ὑπηρετήσῃ ὅσον καὶ ὁσά-<br> | ἐγγεγραμμένος δὲν ὑπηρέτησεν, θὰ ὑπηρετήσῃ ὅσον καὶ ὁσά- | ἐγγεγραμμένος δὲν ὑπηρέτησεν, θὰ ὑπηρετήσῃ ὅσον καὶ ὀσά- |
| [s2-74cdb23a34ca4a6cd01e-p00007.mark9.r7item9](../../harvest/three_engines_review.html#s2-74cdb23a34ca4a6cd01e-p00007.mark9.r7item9) | Vouli | ok | όσάκις ἐκλήθη ἐπιστρατεία, εἰς τὸ διάστημα, καθ&#x27; ὁ ὁ μη<br> | ὁσάκις ἐκλήθη ἐπιστρατεία, εἰς τὸ διάστημα, καθ᾽ ὁ ὁ μὴ | τάκις ἐκλήθη ἐπιστρατεία, εἰς τὸ διάστημα, καθ’ ὃ ὁ μὴ |
| [s2-831443dc5e6f1ccfbaf5-p00007.mark273.r7item273](../../harvest/three_engines_review.html#s2-831443dc5e6f1ccfbaf5-p00007.mark273.r7item273) | Vouli | ok | κατὰ τὸ ἄρθρον<br> | κατὰ τὸ ἄρθρον | καπὰ τὸ ἄσθοον. |
| [s2-831443dc5e6f1ccfbaf5-p00020.mark138.r7item138](../../harvest/three_engines_review.html#s2-831443dc5e6f1ccfbaf5-p00020.mark138.r7item138) | Vouli | ok | んん<br>23<br>124<br>25<br>26<br>27<br>28<br>29<br>20<br> | 23<br>24<br>125<br>126<br>27<br>28<br>29 | 128) |
| [s2-831443dc5e6f1ccfbaf5-p00020.mark138.r7item71](../../harvest/three_engines_review.html#s2-831443dc5e6f1ccfbaf5-p00020.mark138.r7item71) | Vouli | ok | 30<br> | 30 | 180 |
| [s2-831443dc5e6f1ccfbaf5-p00020.mark154.r7item154](../../harvest/three_engines_review.html#s2-831443dc5e6f1ccfbaf5-p00020.mark154.r7item154) | Vouli | ok | 21<br>22<br> | 21<br>22<br>122 | 122 |
| [s2-831443dc5e6f1ccfbaf5-p00020.mark188.r7item188](../../harvest/three_engines_review.html#s2-831443dc5e6f1ccfbaf5-p00020.mark188.r7item188) | Vouli | ok | 62<br> | 62 | 79 |
| [s2-831443dc5e6f1ccfbaf5-p00020.mark203.r7item203](../../harvest/three_engines_review.html#s2-831443dc5e6f1ccfbaf5-p00020.mark203.r7item203) | Vouli | ok | 16<br> | 16 | 16. |
| [s2-831443dc5e6f1ccfbaf5-p00020.mark226.r7item226](../../harvest/three_engines_review.html#s2-831443dc5e6f1ccfbaf5-p00020.mark226.r7item226) | Vouli | ok | 14<br> | 14 | 14. |
| [s2-831443dc5e6f1ccfbaf5-p00020.mark273.r7item273](../../harvest/three_engines_review.html#s2-831443dc5e6f1ccfbaf5-p00020.mark273.r7item273) | Vouli | ok | 72<br> | 72 | 72 |
| [s2-831443dc5e6f1ccfbaf5-p00039.mark134.r7item133](../../harvest/three_engines_review.html#s2-831443dc5e6f1ccfbaf5-p00039.mark134.r7item133) | Vouli | ok | Μονάς δρ της επ<br>νῦν ὁ δημοτ. δασμός·<br> | νῦν ὁ δημοτ, δασμός·<br>exemains Sh<br>SPAO | 8 |
| [s2-831443dc5e6f1ccfbaf5-p00039.mark134.r7item134](../../harvest/three_engines_review.html#s2-831443dc5e6f1ccfbaf5-p00039.mark134.r7item134) | Vouli | ok | Μονὰς ἐο᾿ ἧς ἐπιβάλλετα<br>Σαμός<br> | βρ<br>Μονὰς ἐ&#x27; ἧς ἐπιβάλλετα | ) 285 |
| [s2-831443dc5e6f1ccfbaf5-p00039.mark93.r7item92](../../harvest/three_engines_review.html#s2-831443dc5e6f1ccfbaf5-p00039.mark93.r7item92) | Vouli | ok | 35<br> | 35 | 35 |
| [s2-831443dc5e6f1ccfbaf5-p00042.mark195.r7item157](../../harvest/three_engines_review.html#s2-831443dc5e6f1ccfbaf5-p00042.mark195.r7item157) | Vouli | ok | Μονὰς ἐφ᾿ ἧς ἐπιβάλ-<br>λεται νῦν ὁ δημοτικὸς<br>δασμός<br> | Μονὰς ἐφ᾿ ἧς ἐπιβάλ<br>λεται νῦν ὁ δημοτικός<br>δασμός | 9 — |
| [s2-86865c33eef5932c013b-p00023.mark2.r7item2](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00023.mark2.r7item2) | Vouli | ok | διατάξεις· ὁ Ὑπουργὸς τῶν Οἰκονομικῶν ἐπέφερεν ὅτι τὸ Ὑπουρ<br> | διατάξεις· ὁ Ὑπουργὸς τῶν Οἰκονομικῶν ἐπέφερεν ὅτι τὸ Υπουρ | διατάξειξ ὁ ππουργος τῶν οικονομικῶν ἐπέφέρεν ὅτι τὸ Ὑπουρ- |
| [s2-86865c33eef5932c013b-p00023.mark6.r7item6](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00023.mark6.r7item6) | Vouli | ok | JUODAVOURC3<br>ἐξετάσεως ψήφισιν τῆς ἐκ τῶν ἐρημονή των προσόδου ὤφειλε τὸ<br> | 730<br>ἐξετάσεως ψήφισιν τῆς ἐκ τῶν ἐρημονήσων προσόδου ὤφειλε τὸ<br>VOLEUM | ἐξετάσεως ψήφισιν τῆς ἐκ τῶν ἐρημονήτῶν προσόδου ὠφειλετὸ |
| [s2-86865c33eef5932c013b-p00025.mark10.r7item10](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00025.mark10.r7item10) | Vouli | ok | χιλ. δραχ. οἱ δὲ ἀυαζηλάται εὐχαρίστως ὑποβάλλονται εἰς τὸν<br> | 1301<br>χιλ. δραχ. οἱ δὲ ἁμαξηλάται εὐχαρίστως ὑποβάλλονται εἰς τὸν | χελ. δραχνοὶ δὲ ἀμαξήλάται εὐχαρίστως ὑποδάλλονται εἰς τὸν |
| [s2-86865c33eef5932c013b-p00025.mark25.r7item25](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00025.mark25.r7item25) | Vouli | ok | και είναι πραγματικώς, κασο<br>100<br>30<br>τῆς θαλάσσης, καὶ δι᾿ αὐτὴς μὲ τὸ μένι ον<br>την πρωτευουσαν,<br>ον μέρος τοῦ Κράτους,<br> | και είν<br>καθα<br>προ<br>τῆς θαλάσσης, καὶ δι&#x27; αὐτῆς μὲ τὸ μέγι ον μέρος του Κράτους, | τῆξ θαλάσσης, καὶ δι’ αὐτὴς μὲ τὸ μέγι ὃν μέρος τοῦ Κρατουξκ |
| [s2-86865c33eef5932c013b-p00025.mark25.r7item26](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00025.mark25.r7item26) | Vouli | ok | καὶ εἶναι πραγ<br>πραγματικῶς, καθὸ συνδέουσα τὴν πρωτεύουσαν μετα<br> | 30 VIDAVO VO<br>καὶ εἶναι πραγματικῶς, καθὸ συνδέουσα τὴν πρωτεύουσαν μετά | καιὶ’ εἶναι πραςματικως, καθὸ σύνδέουσα τὴν πρωτεύουσαν, μετὰ |
| [s2-86865c33eef5932c013b-p00025.mark28.r7item27](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00025.mark28.r7item27) | Vouli | ok | ρίσασα ὁριστικῶς τὴν ὁδὸν Πειραιῶς ὡς ὁδὸν ἁ. τάξεως, ὁποία<br> | ρίσασα ὁριστικῶς τὴν ὁδὸν Πειραιῶς ὡς ὁδὸν ά. τάξεως, ὁποία | ρἰσασαξδριςτικῶς τὴν ὁδὸν Πειραιῶς ὡς ὁδὸν ἀ τάξεως, ὁποία, |
| [s2-86865c33eef5932c013b-p00025.mark36.r7item35](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00025.mark36.r7item35) | Vouli | ok | θωτος, μὴ δυναμένου τοῦ δημοτικοῦ ταμείου νὰ δαπανᾷ μεν<br> | θωτος, μὴ δυναμένου τοῦ δημοτικού ταμείου νὰ δαπανᾷ μὲν | θῶτος, μῇ δυναμένου τοῦ δημοτικοῦ ταμείου νὰ δαπανᾷ μεια |
| [s2-86865c33eef5932c013b-p00025.mark7.r7item7](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00025.mark7.r7item7) | Vouli | ok | ἐξαρτᾶται ἡ μᾶλλον ἢ ἦττον διάρκεια τῶν τε ἀμαξῶν καὶ τῶν<br> | ἐξαρτᾶται ἡ μᾶλλον ἢ ἧττον διάρκεια τῶν τε ἁμαξῶν καὶ τῶν | ἐξαρτᾶπας μᾶλλον ἢ ἦττον διάρκεια τῶν τε ἅμαξῶν καὶ τῶν |
| [s2-86865c33eef5932c013b-p00025.mark9.r7item9](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00025.mark9.r7item9) | Vouli | ok | TO<br>ἐλαφρὸν τοῦτον φόρον, καθὸ προωρισμένον νὰ δαπάνᾶται πρὸς<br> | 5150<br>ἐλαφρὸν τοῦτον φόρον, καθό προωρισμένον νὰ δαπανᾶται προς | ἐλαφρὸν τοῦτον φόρον, καθο προωρισμένον νὰ δαπανᾶται πρς |
| [s2-86865c33eef5932c013b-p00026.comment.r7item36](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00026.comment.r7item36) | Vouli | ok | Αχ Ελαια Ενθύϊνώς κατύο.<br> | Evo | . ... Ε ΛιΦΩΦΕΟΤ... |
| [s2-86865c33eef5932c013b-p00026.comment.r7item41](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00026.comment.r7item41) | Vouli | ok | (empty) | της Κυβερνήσεως των Ο | τῆς Κυβερνήσεως....... |
| [s2-86865c33eef5932c013b-p00026.mark24.r7item17](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00026.mark24.r7item17) | Vouli | ok | τῶν ἐν ἐνεργεία ἀξιωματικῶν τοῦ στρατοῦ, καὶ ὅλα τὰ διερχό<br> | 16715/<br>τῶν ἐν ἐνεργεία αξιωματικῶν τοῦ στρατοῦ, καὶ ὅλα τὰ διερχό | ῶν ἐκ ενεεζείᾳ ἀξιωματικ α τοῦ στρατῷ, καὶ ὅλα τὰ διερχό- |
| [s2-86865c33eef5932c013b-p00026.mark24.r7item18](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00026.mark24.r7item18) | Vouli | ok | συνοδίας των, τῆς χωροφυλακῆεεὶ τοῦ ἱππικοῦ, τῶν ζευγιτῶν,<br>- αν δισοκά<br> | υκης, των αντισταμι<br>συνοδίας των, τῆς χωροφυλακής του ιππικοῦ, τῶν ζευγιτῶν,<br>1 2 ενώ διεθνής<br>2 | συνοδίας των. της χῶροφυζακῆς τοῦ ἱππικοῦ, τῶν ζευγιτῶν, |
| [s2-86865c33eef5932c013b-p00026.mark24.r7item19](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00026.mark24.r7item19) | Vouli | ok | ταμούνται της αιωιμονημον τ<br>τῆς αὐλῆς, τῶν ἀντιπροσώπων, τῶν ξένων Δυνάμεων καὶ τῆς<br>A.<br>2<br> | των μώνται της ανακοινων<br>τῆς αὐλῆς, τῶν ἀντιπροσώπων των ξένων Δυνάμεων<br>καὶ τῆς | τῆς αὐλῆς, τῶν ἀντιπροσώπων, τῶν ἔένων ευνάμεων, αἰξῆς |
| [s2-86865c33eef5932c013b-p00026.mark25.r7item18](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00026.mark25.r7item18) | Vouli | ok | συνοδίας των, τῆς χωροφυλακῆεεὶ τοῦ ἱππικοῦ, τῶν ζευγιτῶν,<br>- αν δισοκά<br> | υκης, των αντισταμι<br>συνοδίας των, τῆς χωροφυλακής του ιππικοῦ, τῶν ζευγιτῶν,<br>1 2 ενώ διεθνής<br>2 | συνοδίας των. της χῶροφυζακῆς τοῦ ἱππικοῦ, τῶν ζευγιτῶν, |
| [s2-86865c33eef5932c013b-p00026.mark25.r7item19](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00026.mark25.r7item19) | Vouli | ok | ταμούνται της αιωιμονημον τ<br>τῆς αὐλῆς, τῶν ἀντιπροσώπων, τῶν ξένων Δυνάμεων καὶ τῆς<br>A.<br>2<br> | των μώνται της ανακοινων<br>τῆς αὐλῆς, τῶν ἀντιπροσώπων των ξένων Δυνάμεων<br>καὶ τῆς | τῆς αὐλῆς, τῶν ἀντιπροσώπων, τῶν ἔένων ευνάμεων, αἰξῆς |
| [s2-86865c33eef5932c013b-p00026.mark25.r7item20](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00026.mark25.r7item20) | Vouli | ok | *· ἐξαιροῦνται τῆς πληρωμῆς τοῦ δικαιώματος τούτου οἱ ίπποι<br> | Εξαιρούνται τῆς πληρωμής του δικαιώματος τούτου οἱ ἱ<br>οἱ ίπποι | — Ἐξαιραῶνται τῆς πληρωμιῆς τοῦ δικαιώματος τούτου ὀμίπποι |
| [s2-86865c33eef5932c013b-p00026.mark31.r7item24](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00026.mark31.r7item24) | Vouli | ok | νας εἰς Πειραιᾶ, καὶ ἀπὸ Πειραιά εἰς Αθήνας, θέλουν πληρό-<br>مدون<br> | παντος εισους γυρνώ γι<br>νας εἰς Πειραιά, καὶ ἀπὸ Πειραιά εἰς Αθήνας, θέλουν πληρό | νας εἰς Πειραιᾶ, καὶ ἀπὸ Πειραιᾶ. εἰς Ἀθήνας, θέλουν πληρό- |
| [s2-86865c33eef5932c013b-p00026.mark31.r7item25](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00026.mark31.r7item25) | Vouli | ok | γίων καὶ παντὸς εἶδους φορτηγοῦ ζώων, μεταβαίνοντος ἀπὸ Αθή-<br>٨/<br> | γίων καὶ παντὸς εἶδους φορτηγού ζώου, μεταβαίνοντος ἀπὸ Αθή | Τωνκαὶπαιτὸς εἶδους φορτηγοῦ ξωυ’μεταβαίνοντος ἀπὸ Ἀθή- |
| [s2-86865c33eef5932c013b-p00026.mark7.r7item5](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00026.mark7.r7item5) | Vouli | ok | δεχθεὶς ὑποβάλλω καὶ αὖθις αὐτὸ εἰς τὴν ὑμετέραν ἐπιψήφισιν.<br> | και της ενυ<br>δεχθεὶς ὑποβάλλω καὶ αὖθις αὐτὸ εἰς τὴν ὑμετέραν ἐπιψήφισιν,<br>30300 | δέχθεὶς ὑποξάλλω καί αὕδις αὐτὸ εἰς τὴν ὑμετέραν· ἐπιψήφισιν. |
| [s2-86865c33eef5932c013b-p00026.mark7.r7item6](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00026.mark7.r7item6) | Vouli | ok | (empty) | νου<br>διὰ τῆς ἐνόπλου δυνάμεως α τὴν τροποποίησιν ταύτην παρα- | ψου διὰ τᾷς ἔκόπλου δυνάμεωςιε την σροποποίησιν παύτεν παρα- |
| [s2-86865c33eef5932c013b-p00029.mark12.r7item10](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00029.mark12.r7item10) | Vouli | ok | Sunaidu Shasaanded amarindange amoun<br>1. Πρὸς δὲ ὁ τελευταίος· τοῦ Νομοσχεδίου παράγραφος ὁ ὑπὸ<br> | πρὸς δὲ ὁ τελευταίος τοῦ Νομοσχεδίου παράγραφος διακό<br>LA | ηρὸς Σξ ο ἀξελευταιοξα τῦ Ἐδμσσξεδιου παράγράφος· ὁ θῆῦ |
| [s2-86865c33eef5932c013b-p00029.mark12.r7item11](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00029.mark12.r7item11) | Vouli | ok | τῶν Γάλλων,<br>Γάλλων κατεχομένων μερῶν τῆς Αφρικῆς<br> | τραν το<br>τις υρανών<br>των Γάλλων κατεχομένων μερών της Αφρικής. Τα εκ σε 15<br>45 48 18 | τῶν πάλῃῳ, ατιχομένων μερένετςς ἐορξκπρνν.. |
| [s2-86865c33eef5932c013b-p00029.mark12.r7item12](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00029.mark12.r7item12) | Vouli | ok | 30<br>Οἱ ἐν Ὑποπροξενείον έχον τὴν ἔδραν του εἰς ὀράνων τῶν ὑ<br>υπό<br>C<br> | εις τρικαλιν της<br>σε εν αποπροξενεῖον ἔχον τὴν ἕδραν του εἰς ὀράνην τῶν ὑπὸ | Νφεοπροξένεῖόν ἔἐχον τὴν ἔλραν του εἰς ὀράνην τῶν ὑπὸ |
| [s2-86865c33eef5932c013b-p00029.mark13.r7item11](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00029.mark13.r7item11) | Vouli | ok | τῶν Γάλλων,<br>Γάλλων κατεχομένων μερῶν τῆς Αφρικῆς<br> | τραν το<br>τις υρανών<br>των Γάλλων κατεχομένων μερών της Αφρικής. Τα εκ σε 15<br>45 48 18 | τῶν πάλῃῳ, ατιχομένων μερένετςς ἐορξκπρνν.. |
| [s2-86865c33eef5932c013b-p00029.mark13.r7item12](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00029.mark13.r7item12) | Vouli | ok | 30<br>Οἱ ἐν Ὑποπροξενείον έχον τὴν ἔδραν του εἰς ὀράνων τῶν ὑ<br>υπό<br>C<br> | εις τρικαλιν της<br>σε εν αποπροξενεῖον ἔχον τὴν ἕδραν του εἰς ὀράνην τῶν ὑπὸ | Νφεοπροξένεῖόν ἔἐχον τὴν ἔλραν του εἰς ὀράνην τῶν ὑπὸ |
| [s2-86865c33eef5932c013b-p00029.mark13.r7item13](../../harvest/three_engines_review.html#s2-86865c33eef5932c013b-p00029.mark13.r7item13) | Vouli | ok | ἐν Προξενεῖον ἔχον τὴν ἔδραν του εἰς Τρίπολιν τῆς Βαρβαρίας.<br> | ἂν προξενεῖον ἔχον τὴν ἕδραν του εἰς Τρίπολιν τῆς Βαρβαρίας, | Ἐν Προξενεῖον ἔχον τὴν ἔδραν του εἰς Τρίπολιν τῆς Βαρβαρίας. |
| [s2-93f8070059f938bda524-p00001.comment.r7item0](../../harvest/three_engines_review.html#s2-93f8070059f938bda524-p00001.comment.r7item0) | Vouli | ok | (empty) | (empty) | .... |
| [s2-93f8070059f938bda524-p00001.comment.r7item1](../../harvest/three_engines_review.html#s2-93f8070059f938bda524-p00001.comment.r7item1) | Vouli | ok | 1003<br> | 1003 | ..... |
| [s2-93f8070059f938bda524-p00001.comment.r7item121](../../harvest/three_engines_review.html#s2-93f8070059f938bda524-p00001.comment.r7item121) | Vouli | ok | 1ο Βουλευτὴς ἐκ Γόρτυνος<br> | Για το Βουλευτής ἐκ Γόρτυνος | Βουλευτὴς ἐκ Τόρτυνος. |
| [s2-93f8070059f938bda524-p00001.comment.r7item125](../../harvest/three_engines_review.html#s2-93f8070059f938bda524-p00001.comment.r7item125) | Vouli | ok | χος &quot;Άρθρον 10<br> | Εκτός Αρθρον 10 | Ἄρθρον 10. |
| [s2-93f8070059f938bda524-p00001.comment.r7item126](../../harvest/three_engines_review.html#s2-93f8070059f938bda524-p00001.comment.r7item126) | Vouli | ok | ТОПИАХН<br> | TOONMAXHM ZIZMYеTI | ....... |
| [s2-93f8070059f938bda524-p00001.comment.r7item7](../../harvest/three_engines_review.html#s2-93f8070059f938bda524-p00001.comment.r7item7) | Vouli | ok | 08,8<br> | 08,3 | (empty) |
| [s2-c3ccfa3cea1347d7ad54-p00002.mark1.r7item0](../../harvest/three_engines_review.html#s2-c3ccfa3cea1347d7ad54-p00002.mark1.r7item0) | Vouli | ok | οὕτω δὲ καὶ ὁ ἔφορος Λεβαδείας προσεκάλεσε μὲν πέντε τοιαῦτα<br> | οὕτω δὲ καὶ ὁ ἔφορος Λεβαδείας προσεκάλεσε μὲν πέντε τοιαῦτα | Οἴτω δὲ καὶ ὁ ἔφορος λεβαδείας προσεκάλεσε μὲν πέντε τοιαῦτα |
| [s2-c3ccfa3cea1347d7ad54-p00002.mark1.r7item31](../../harvest/three_engines_review.html#s2-c3ccfa3cea1347d7ad54-p00002.mark1.r7item31) | Vouli | ok | μέλη, ἐπειδὴ ὅμως δὲν παρῆσαν ἐν τῇ πόλει, δὲν ἠδυνήθησαν νὰ<br> | μέλη, ἐπειδὴ ὅμως δὲν παρῆσαν ἐν τῇ πόλει, δὲν ἠδυνήθησαν νὰ | μέλη, ἐπειδὴ ὅμως δὲν παρῆσαν ἐν τῇ πόλει, δὲν ἠδυνήθησαν νὰ |
| [s2-c3ccfa3cea1347d7ad54-p00002.mark19.r7item11](../../harvest/three_engines_review.html#s2-c3ccfa3cea1347d7ad54-p00002.mark19.r7item11) | Vouli | ok | μνιαυθα παρετήρηος τις,<br>ἀπέτεινε παράκλησιν τινα εἰς τὸ ὑπουργεῖον, ἀλλ᾽ ὁ ἀγορεύων<br>V<br> | amaleven and soudu±3d<br>ἀπέτεινε παράκλησίν τινα εἰς τὸ ὑπουργεῖον, ἀλλ᾽ ὁ ἀγορεύων<br>7111 | ἀπέτεινε· «πᾶμᾶπλησίν τινα εἰς τὸ ὑπουρεῖον, ἀλλ’ ὁ ἀγορεύων |
| [s2-c3ccfa3cea1347d7ad54-p00002.mark19.r7item12](../../harvest/three_engines_review.html#s2-c3ccfa3cea1347d7ad54-p00002.mark19.r7item12) | Vouli | ok | ς, πρέπε<br>04<br>ἐνταῦθα παρετήρησέ τις, ὅτι ἀληθῶς μὲν ὁ βουλευτής Θήρας<br> | πρέπει<br>Ενταῦθα παρετήρησε τις, ὅτι ἀληθῶς μὲν ὁ βουλευτής Θήρας | Ἐνταῦθα παρετήρησέ τις, ὅτι ἀληθῶς μὲν ὁ βουλευτὴς Θήρας |
| [s2-c3ccfa3cea1347d7ad54-p00002.mark2.r7item0](../../harvest/three_engines_review.html#s2-c3ccfa3cea1347d7ad54-p00002.mark2.r7item0) | Vouli | ok | οὕτω δὲ καὶ ὁ ἔφορος Λεβαδείας προσεκάλεσε μὲν πέντε τοιαῦτα<br> | οὕτω δὲ καὶ ὁ ἔφορος Λεβαδείας προσεκάλεσε μὲν πέντε τοιαῦτα | Οἴτω δὲ καὶ ὁ ἔφορος λεβαδείας προσεκάλεσε μὲν πέντε τοιαῦτα |
| [s2-c3ccfa3cea1347d7ad54-p00002.mark2.r7item1](../../harvest/three_engines_review.html#s2-c3ccfa3cea1347d7ad54-p00002.mark2.r7item1) | Vouli | ok | , πενταμελής וייי<br>τοῦ ἐφόρου καὶ τοῦ ἐπάρχου, ἐνεργεῖ τὴν ἐκτίμησιν τῶν ἀμπέλων·<br> | πενταμελης<br>Son<br>τοῦ ἐφόρου καὶ τοῦ ἐπάρχου, ἐνεργεῖ τὴν ἐκτίμησιν τῶν ἀμπέλων· | τοῦ ἐφόρου καὶ τοῦ ἐπάρχου, ἐνεργεῖ τὴν ἐκτίμησιν τῶν ἀμπέλων· |
| [s2-c3ccfa3cea1347d7ad54-p00002.mark2.r7item46](../../harvest/three_engines_review.html#s2-c3ccfa3cea1347d7ad54-p00002.mark2.r7item46) | Vouli | ok | (empty) | (empty) | .... |
| [s2-d12a9a4feb23254f4080-p00006.mark10.r7item10](../../harvest/three_engines_review.html#s2-d12a9a4feb23254f4080-p00006.mark10.r7item10) | Vouli | ok | κανὲν ἔξοδον, δὲν θὰ ἐπιβαρύνῃ ποσῶς τὸν προϋπολογισμόν· εἰς<br>١١٩٧٩٨<br>TT<br> | venet<br>κανὲν ἔξοδον, δὲν θὰ ἐπιβαρύνῃ ποσῶς τὸν προϋπολογισμόν· εἰς | κανὲν ἐξοδο, ξεν θα ἐπιξξζ. . Αν γύρ.. .... |
| [s2-d12a9a4feb23254f4080-p00006.mark10.r7item12](../../harvest/three_engines_review.html#s2-d12a9a4feb23254f4080-p00006.mark10.r7item12) | Vouli | ok | Τον χαζευρετε, πως την εννοώ; τουν πως θα εκλεχυ<br>ἕνας στρατιωτικὸς ἀστυνόμος. Η ᾿Αστυνομία αὐτὴ δὲν θέλει<br> | πλευρετε, πως την εν<br>α<br>εκλεχε<br>ἕνας στρατιωτικὸς ἀστυνόμος. Η Αστυνομία αὐτὴ δὲν θέλει | ἕνας στραξιωδξιἘστυθμος. Α Ἀστυνοκία αὐτῃ δὲν’ θχει |
| [s2-d12a9a4feb23254f4080-p00006.mark10.r7item8](../../harvest/three_engines_review.html#s2-d12a9a4feb23254f4080-p00006.mark10.r7item8) | Vouli | ok | τὸν ᾿Αστυνόμον αὐτὸν, Κύριοι, θὰ δοθῇ τὸ δικαίωμα νὰ ἐκλέξῃ<br> | τὸν ᾿Αστυνόμον αὐτὸν, Κύριοι, θὰ δοθῇ τὸ δικαίωμα νὰ ἐκλέξῃ | τὸν Ἀστυνόμον αὐτὸν, Κχεῖε. Ζηγζχην· τυ. τντι.. |
| [s2-d12a9a4feb23254f4080-p00006.mark12.r7item10](../../harvest/three_engines_review.html#s2-d12a9a4feb23254f4080-p00006.mark12.r7item10) | Vouli | ok | κανὲν ἔξοδον, δὲν θὰ ἐπιβαρύνῃ ποσῶς τὸν προϋπολογισμόν· εἰς<br>١١٩٧٩٨<br>TT<br> | venet<br>κανὲν ἔξοδον, δὲν θὰ ἐπιβαρύνῃ ποσῶς τὸν προϋπολογισμόν· εἰς | κανὲν ἐξοδο, ξεν θα ἐπιξξζ. . Αν γύρ.. .... |
| [s2-d12a9a4feb23254f4080-p00006.mark12.r7item12](../../harvest/three_engines_review.html#s2-d12a9a4feb23254f4080-p00006.mark12.r7item12) | Vouli | ok | Τον χαζευρετε, πως την εννοώ; τουν πως θα εκλεχυ<br>ἕνας στρατιωτικὸς ἀστυνόμος. Η ᾿Αστυνομία αὐτὴ δὲν θέλει<br> | πλευρετε, πως την εν<br>α<br>εκλεχε<br>ἕνας στρατιωτικὸς ἀστυνόμος. Η Αστυνομία αὐτὴ δὲν θέλει | ἕνας στραξιωδξιἘστυθμος. Α Ἀστυνοκία αὐτῃ δὲν’ θχει |
| [s2-d12a9a4feb23254f4080-p00006.mark12.r7item14](../../harvest/three_engines_review.html#s2-d12a9a4feb23254f4080-p00006.mark12.r7item14) | Vouli | ok | Συνέλευσιν, ἠξεύρετε, πῶς τὴν ἐννοῶ; ἰδοὺ πῶς. Θὰ ἐκλεχθῇ<br> | συνυμικ<br>Συνέλευσιν, ἠξεύρετε, πῶς τὴν ἐννοῶ; ἰδοὺ πῶς. Θὰ ἐκλεχθῇ | Συνέλευσιν, ἠξεύρετε. πν.Α! ήνιν. τι. η... |
| [s2-d12a9a4feb23254f4080-p00006.mark14.r7item12](../../harvest/three_engines_review.html#s2-d12a9a4feb23254f4080-p00006.mark14.r7item12) | Vouli | ok | Τον χαζευρετε, πως την εννοώ; τουν πως θα εκλεχυ<br>ἕνας στρατιωτικὸς ἀστυνόμος. Η ᾿Αστυνομία αὐτὴ δὲν θέλει<br> | πλευρετε, πως την εν<br>α<br>εκλεχε<br>ἕνας στρατιωτικὸς ἀστυνόμος. Η Αστυνομία αὐτὴ δὲν θέλει | ἕνας στραξιωδξιἘστυθμος. Α Ἀστυνοκία αὐτῃ δὲν’ θχει |
| [s2-d12a9a4feb23254f4080-p00006.mark14.r7item14](../../harvest/three_engines_review.html#s2-d12a9a4feb23254f4080-p00006.mark14.r7item14) | Vouli | ok | Συνέλευσιν, ἠξεύρετε, πῶς τὴν ἐννοῶ; ἰδοὺ πῶς. Θὰ ἐκλεχθῇ<br> | συνυμικ<br>Συνέλευσιν, ἠξεύρετε, πῶς τὴν ἐννοῶ; ἰδοὺ πῶς. Θὰ ἐκλεχθῇ | Συνέλευσιν, ἠξεύρετε. πν.Α! ήνιν. τι. η... |
| [s2-d12a9a4feb23254f4080-p00006.mark2.r7item0](../../harvest/three_engines_review.html#s2-d12a9a4feb23254f4080-p00006.mark2.r7item0) | Vouli | ok | savedu<br>TW<br>γιατι της<br>ἐκλογῆς του, διὰ νὰ δύναται νὰ φέρῃ ἀποτέλεσμα τοῦτο φρονῶ<br> | κυμαινου<br>6715<br>ἐκλογῆς του, διὰ νὰ δύναται νὰ φέρῃ ἀποτέλεσμα· τοῦτο φρονῶ | ἐκλογῆς τοῦ, διὰ νὰ δύναται νὰ ΣΕι πύγινι. νυτμτ.. |
| [s2-d12a9a4feb23254f4080-p00006.mark2.r7item2](../../harvest/three_engines_review.html#s2-d12a9a4feb23254f4080-p00006.mark2.r7item2) | Vouli | ok | M<br>mundra παλη<br>τῶν ἐξ ὅλων τῶν Σωμάτων, ἀλλ᾿ αὐτοὶ πρέπει νὰ ἦναι τῆς<br> | _mands man<br>άμου μου<br>τῶν ἐξ ὅλων τῶν Σωμάτων, ἀλλ᾽ αὐτοὶ πρέπει νὰ εἶναι τῆς | τῶν ἔξ ὅλων τῶν εωμάτων. Ἔεουχή. τ. κννκ.. |
| [s2-d12a9a4feb23254f4080-p00006.mark2.r7item4](../../harvest/three_engines_review.html#s2-d12a9a4feb23254f4080-p00006.mark2.r7item4) | Vouli | ok | baandama<br>προσλάβῃ εἰς τὴν ὑπηρεσίαν· θὰ ἐκλέξῃ ἕνα ἀριθμὸν στρατιω-<br> | προσλάβῃ εἰς τὴν ὑπηρεσίαν· θὰ ἐκλέξῃ ἕνα ἀριθμὸν στρατιω | προσλάβῃ εἰς τὴν ὑπηρεαιαν μζ! υν. ..ν.. |
| [s2-d12a9a4feb23254f4080-p00006.mark4.r7item2](../../harvest/three_engines_review.html#s2-d12a9a4feb23254f4080-p00006.mark4.r7item2) | Vouli | ok | M<br>mundra παλη<br>τῶν ἐξ ὅλων τῶν Σωμάτων, ἀλλ᾿ αὐτοὶ πρέπει νὰ ἦναι τῆς<br> | _mands man<br>άμου μου<br>τῶν ἐξ ὅλων τῶν Σωμάτων, ἀλλ᾽ αὐτοὶ πρέπει νὰ εἶναι τῆς | τῶν ἔξ ὅλων τῶν εωμάτων. Ἔεουχή. τ. κννκ.. |
| [s2-d12a9a4feb23254f4080-p00006.mark4.r7item4](../../harvest/three_engines_review.html#s2-d12a9a4feb23254f4080-p00006.mark4.r7item4) | Vouli | ok | baandama<br>προσλάβῃ εἰς τὴν ὑπηρεσίαν· θὰ ἐκλέξῃ ἕνα ἀριθμὸν στρατιω-<br> | προσλάβῃ εἰς τὴν ὑπηρεσίαν· θὰ ἐκλέξῃ ἕνα ἀριθμὸν στρατιω | προσλάβῃ εἰς τὴν ὑπηρεαιαν μζ! υν. ..ν.. |
| [s2-d12a9a4feb23254f4080-p00006.mark4.r7item6](../../harvest/three_engines_review.html#s2-d12a9a4feb23254f4080-p00006.mark4.r7item6) | Vouli | ok | ἀριθμόν τινα υπαξιωματικῶν κατωτάτου βαθμοῦ, νὰ τοὺς<br> | ἀριθμόν τινα υπαξιωματικών κατωτάτου βαθμοῦ, νὰ τοὺς | ἀριθμόν τινα Ἐπαξωμᾶκῶν κατωτάτου βαθμοῦ, νὰ τοῦξ |
| [s2-d12a9a4feb23254f4080-p00006.mark8.r7item6](../../harvest/three_engines_review.html#s2-d12a9a4feb23254f4080-p00006.mark8.r7item6) | Vouli | ok | ἀριθμόν τινα υπαξιωματικῶν κατωτάτου βαθμοῦ, νὰ τοὺς<br> | ἀριθμόν τινα υπαξιωματικών κατωτάτου βαθμοῦ, νὰ τοὺς | ἀριθμόν τινα Ἐπαξωμᾶκῶν κατωτάτου βαθμοῦ, νὰ τοῦξ |
| [s2-d12a9a4feb23254f4080-p00006.mark8.r7item8](../../harvest/three_engines_review.html#s2-d12a9a4feb23254f4080-p00006.mark8.r7item8) | Vouli | ok | τὸν ᾿Αστυνόμον αὐτὸν, Κύριοι, θὰ δοθῇ τὸ δικαίωμα νὰ ἐκλέξῃ<br> | τὸν ᾿Αστυνόμον αὐτὸν, Κύριοι, θὰ δοθῇ τὸ δικαίωμα νὰ ἐκλέξῃ | τὸν Ἀστυνόμον αὐτὸν, Κχεῖε. Ζηγζχην· τυ. τντι.. |
| [s2-d12a9a4feb23254f4080-p00008.mark9.r7item11](../../harvest/three_engines_review.html#s2-d12a9a4feb23254f4080-p00008.mark9.r7item11) | Vouli | ok | ٢٠٢٠١<br>יייייייייי<br>Κυβέρνησις, ὅπως εἶναι συγκεκροτημένη, δύναται νὰ ἐγγυηθῇ<br> | Κυβέρνησις, ὅπως εἶναι συγκεκροτημένη, δύναται νὰ ἐγγυηθῇ | Κυβέρνησις, ὅπως εἶναι συγκεκροτημένη, δύναται νὰ ἐγγυηθῇ! |
| [s2-d12a9a4feb23254f4080-p00008.mark9.r7item8](../../harvest/three_engines_review.html#s2-d12a9a4feb23254f4080-p00008.mark9.r7item8) | Vouli | ok | μπαλκονョン1の<br>Unkalla<br>ἀπέναντι παντὸς τὴν διατήρησιν τῆς τάξεως, τὴν πρόληψιν<br>4<br> | Sarwandavinn<br>να<br>Εγγύηση<br>ἀπέναντι παντὸς τὴν διατήρησιν τῆς τάξεων, τὴν πρόληψιν | ἀπέναντι παντὸς τὴν διατήρησιν τῆς τάξεως, τὴν πρόληψιθε |
