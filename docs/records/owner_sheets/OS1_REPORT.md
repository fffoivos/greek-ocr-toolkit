# OS1 owner-sheet receipt

Both self-contained HTML sheets are produced by `greekocr.adjudicate.owner_sheet.render` and its packaged CSS/JS. No network calls, input edits, or `.git` writes were used. Sheet A was built first. Sizes below use decimal MB.

Rebuild with the specified Python: `python scripts/review/build_failure_modes_per_class.py` and `python scripts/review/build_segmentation_failures.py`. Selection regeneration: `PYTHONPATH=. python scripts/review/prepare_os1_specs.py`. Selection uses seed 20261017, explicit fault-to-checker-evidence candidate pools in that script, sorted IDs, and seeded shuffling. Scarce pools are allocated first to keep one card and one note document per line within each sheet. Each subsection takes up to three examples. The specs freeze the selected IDs and every candidate pool.

T6b location: the collect-v3 SG1 `build_gallery.py` points to the actual verdict directory in the sibling checkout: `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/`. The six main verdict files and three corresponding `cards/*_key.json` files for Gazette, kosmopolis and lekythos are bound below. The requested collect-v3 directory contains the pointer rather than those verdict files.

## Format conformance

Reference: `docs/records/labelfix/spellcheck/sheet_format_reference_v4.html`. Its static cards share `div.card`, image crops, `table.w` with named rows, `div.row` and `span.pill`. Both sheets use those same elements and class names through the standard renderer. The reference is stripped (its images contain `STRIPPED`) and does not itself contain line-ID, note, Printed-input, or magnifier markup. Those OS1 requirements use the existing renderer classes: `.lid`, `.notes[data-line]`, `.pr`, `.printed`, `.note`, `.nrow`, `.status`, `.zw`, `.lens`. There is one Google row and one editable Printed field in each card, one note textarea initialized with the checker detail, and doc ID exactly equal to the line ID. The existing runtime saves Printed and Note together and restores persisted values. The runtime tests exercise DB loading, edits and saving. No new card layout or summary strips were added.

The renderer gained data-driven section/subsection headings and initial note text; existing card structure and CSS/JS are retained. One header paragraph appears at the top of each sheet; each A section has one header block. Images use proportional `height:auto`; every crop has the standard hover lens. B strips use `.zoomrow` / `.zoom`. All image data is embedded; no external assets are loaded. Owner-facing text contains no model names or question-mark placeholders. One uncertain checker glyph placeholder in B was expanded from `?` to `[uncertain]`; its exact original detail remains in spec provenance.

## Evidence and limits

Printed is populated only when a source supplies a complete print, or every clause of its checker detail can be applied as an exact unique substitution to the full Google label. It is empty for incomplete, uncertain, or non-substitutable details. Each card records the rule used in `provenance.printed_basis`. This is reconstruction from existing adjudication, not a new transcription.

Some checked crop PNGs are absent from the requested W1 crop directory. They were reconstructed locally from cached page rasters and recorded crop bounds, without resizing, rotation, masking, or recutting. Reconstructed PNG bytes do not match the historical crop hashes; the report does not claim original-byte parity. Tests establish equality to the cached raster at the recorded bounds. Both historical and recovered hashes are retained in spec provenance. T6b checker detail refers to its masked-card audit, while the displayed crop is the original W1 Google geometry as requested.

The cross-cutting character rows are not extra class sections: A mirrors the nine coordinator class tables, splitting the Cyrillic fault rows into Russian and Serbian, giving ten sections and forty subsections. Prose examples also illustrate capital faults; Greek words in mixed-script lines can illustrate the same Greek mark faults. The original stratum is recoverable from each card key and candidate mapping.

The 19% figure is copied from the coordinator. Current `counts.json` identifies the underlying pilot as 501 missed admitted boxes among 2,624 printed rows (19.09298780487805%), with archived visual adjudication and admitted-box scope; it is not a census of absence from all raw boxes. C1 and T6b overrun rates are unpaired samples with different admission mixes, so the header makes no causal masking-fix claim.

## Sheet A: Failure modes per class

Cards: 97; sections: 10; subsections: 40; gaps: 15; Printed prefilled: 54.

### polytonic 1850s — 15 cards

E3 CER 1.58% , 78% of all edits label mark errors 8–13 / 100 lines coverage vs plan on track

- **Grave written as acute before punctuation · 3–4 / 100**: 3 cards; 5 matching checked candidates.
  - `bsb_poly1850--e2115ba0deaf6a07--s003-l0039`
  - `nlg--3d71f4f87abea186--s002-l0017`
  - `bsb_poly1850--eded5a16c1b78a01--s005-l0055`
- **Breathing dropped on a capital · 3–5 / 100**: 3 cards; 7 matching checked candidates.
  - `bsb_poly1850--e18cacecef3b4590--s000-l0057`
  - `nlg--9aff599c7fffc574--s006-l0008`
  - `nlg--9aff599c7fffc574--s003-l0007`
- **Iota subscript dropped, or inserted where none is printed · 2–3 / 100**: 3 cards; 6 matching checked candidates.
  - `ia_poly1850--ca4f3983c96b6334--s001-l0026`
  - `ia_poly1850--2d02eaf0f19a649a--s005-l0015`
  - `ia_poly1850--231a44f61c5268e0--s001-l0026`
- **Circumflex written as acute · 1–2 / 100**: 3 cards; 3 matching checked candidates.
  - `ia_poly1850--2d02eaf0f19a649a--s007-l0032`
  - `ia_poly1850--df8f2267db2b7275--s002-l0037`
  - `ia_poly1850--41e90f3ba967f920--s006-l0022`
- **Elision and quotation marks normalised · frequent**: 3 cards; 3 matching checked candidates.
  - `ia_poly1850--3cbcc415675468a9--s006-l0037`
  - `bsb_poly1850--2fdb06c3a8566781--s003-l0023`
  - `ia_poly1850--41e90f3ba967f920--s002-l0022`

### polytonic 1900s — 11 cards

E3 CER in the 1.58% pool label mark errors 13–16 / 100 lines coverage vs plan thin , masking now admits three sources

- **Grave written as acute or dropped, mid-sentence · 9–12 / 100 cards; 87% of final accents print a grave**: 3 cards; 36 matching checked candidates.
  - `lekythos--0fc3672826ddd6b3--s000-l0033`
  - `lekythos--36e76126a4edbc72--s001-l0077`
  - `kosmopolis--acb323b6cb8d169d--s000-l0020`
- **Crasis and coronis flattened · 1–2 / 100**: 3 cards; 3 matching checked candidates.
  - `kosmopolis--ef37f6cfdd896488--s002-l0036`
  - `lekythos--25feca8f4ab34ba0--s003-l0302`
  - `kosmopolis--681a15c3d4a0cd62--s004-l0027`
- **Breathing dropped on capitals, or turned into a quote or asterisk · 3–5 / 100**: 3 cards; 13 matching checked candidates.
  - `kosmopolis--ef37f6cfdd896488--s005-l0008`
  - `nlg--7870403c3df244ea--s000-l0016`
  - `kosmopolis--8f8439af940ad55b--s006-l0010`
- **Misprint silently corrected to the dictionary form · 1 / 100**: 2 cards; 2 matching checked candidates. Gap: fewer than 3 cards (2).
  - `lekythos--e9f314aab488b65f--s001-l0199`
  - `nlg--3d6bd7bd688acb61--s000-l0025`

### capitals/headings — 7 cards

E3 CER 4.12% , the weakest line type coverage vs plan 4% , no rows admitted

- **Breathings and accents dropped on capitals · 3–5 / 100 in prose**: 3 cards; 5 matching checked candidates.
  - `nlg--9aff599c7fffc574--s002-l0015`
  - `ia_poly1850--36dcee7ce4c29f8b--s003-l0110`
  - `ia_poly1850--41e90f3ba967f920--s001-l0025`
- **Case error: capital labelled as lowercase, or a lowercase word in capitals · 1 / 100**: 2 cards; 2 matching checked candidates. Gap: fewer than 3 cards (2).
  - `ia_russian--2a45a0561eb05739--s006-l0009`
  - `gazette_modern--1f7db88d63c02afa--s000-l0287`
- **Small capitals read as digits or Latin · seen on Latin cards**: 1 cards; 1 matching checked candidates. Gap: fewer than 3 cards (1).
  - `ia_poly1850--f806d3f10b2ecf9c--s006-l0123`
- **Vertical headings stored rotated 90° · 20 / 100 rows**: 1 cards; 1 matching checked candidates. Gap: fewer than 3 cards (1).
  - `gazette_modern--83c3182a4175392a--s000-l0259`
- **Whole stratum never checked · —**: 0 cards; 0 matching checked candidates. Gap: no card in the checked sets.

### numerics — 11 cards

E3 CER 2.71% digits right 98 / 100 coverage vs plan on track via ELSTAT

- **Raised thousands dot written as a hyphen · 2 / 100**: 2 cards; 2 matching checked candidates. Gap: fewer than 3 cards (2).
  - `elstat--ee37bc488988f1bd--s000-l0445`
  - `elstat--ee37bc488988f1bd--s000-l0457`
- **Decimal comma written as a dot, changing the number · 1 / 100**: 1 cards; 1 matching checked candidates. Gap: fewer than 3 cards (1).
  - `elstat--c5f7ea1f26d39839--s000-l0367`
- **Vertical table numbers stored rotated · 14 / 100 Gazette cards**: 3 cards; 3 matching checked candidates.
  - `gazette_modern--ebdc4d07ff8c4122--s000-l0265`
  - `gazette_modern--b9f59878fb904d91--s000-l0034`
  - `gazette_modern--8213d28643843855--s000-l0144`
- **Crop spanning two table cells across a column rule · 1–2 / 100**: 2 cards; 2 matching checked candidates. Gap: fewer than 3 cards (2).
  - `gazette_modern--9a7f184282a21b5e--s000-l0036`
  - `elstat--df38bce62200e7db--s000-l0191`
- **Superscript footnote numbers dropped or garbled · 7 cards in 1,400**: 3 cards; 7 matching checked candidates.
  - `ia_poly1850--36dcee7ce4c29f8b--s000-l0055`
  - `ia_poly1850--34543d92a48213e7--s001-l0026`
  - `ia_poly1850--36dcee7ce4c29f8b--s001-l0067`

### punctuation/dialogue — 14 cards

E3 CER 3.25% dotted leaders 2.97% , no true leader lines in the test coverage vs plan none admitted

- **Em dash dropped, or written as a hyphen or en dash · 20 cards in 1,400, up to 6 / 100 in Serbian and Latin**: 3 cards; 15 matching checked candidates.
  - `serbia--8fd9a36edc06b7f9--s001-l0004`
  - `ia_russian--3fd32314d172e951--s001-l0005`
  - `serbia--46c745f49e7507f4--s001-l0015`
- **Ellipsis shrunk or dropped; ano teleia lost · 6 / 100 on 1900s print**: 3 cards; 4 matching checked candidates.
  - `kosmopolis--aaa124307e36f113--s001-l0062`
  - `nlg--f4b52df5f8130047--s003-l0030`
  - `nlg--7870403c3df244ea--s004-l0023`
- **Opening low quotation mark read as a comma · 1 / 100**: 2 cards; 2 matching checked candidates. Gap: fewer than 3 cards (2).
  - `kosmopolis--86098eebf5207e79--s006-l0027`
  - `ia_russian--03b43bc5289ad8ce--s005-l0011`
- **Line-end hyphen dropped · 3 / 30 on the Gazette probe**: 3 cards; 9 matching checked candidates.
  - `lekythos--49c082ba27aa27da--s000-l0317`
  - `lekythos--e9f314aab488b65f--s001-l0335`
  - `lekythos--793fb44fdc7e1aa6--s000-l0247`
- **Ink speck read as a full stop or colon · 1–2 / 100**: 3 cards; 4 matching checked candidates.
  - `gazette_modern--b4c2554fa74331a6--s000-l0089`
  - `nlg--6ae0ac01064a587e--s003-l0013`
  - `nlg--6146c0455e0103d2--s004-l0024`

### mixed Greek+Latin — 7 cards

E3 CER 1.64% recogniser letter error on disputed words 26–39% , its weakest population coverage vs plan 16%

- **Latin sigla and page letters labelled with Greek lookalikes · 5 / 100**: 3 cards; 5 matching checked candidates.
  - `ia_poly1850--174d84a441d69a70--s002-l0040`
  - `ia_poly1850--36dcee7ce4c29f8b--s004-l0061`
  - `ia_poly1850--a89bd2c9bdb1ca6d--s004-l0025`
- **Latin words misread · 2 / 100**: 2 cards; 2 matching checked candidates. Gap: fewer than 3 cards (2).
  - `ia_poly1850--e6e379cb4b1d54af--s003-l0025`
  - `ia_poly1850--ebcfd6056abfa776--s003-l0099`
- **Margin-column text pulled into the line · 1 / 100**: 1 cards; 1 matching checked candidates. Gap: fewer than 3 cards (1).
  - `ia_poly1850--36dcee7ce4c29f8b--s004-l0032`
- **Handwritten marginalia transcribed as text · 1 / 100**: 1 cards; 1 matching checked candidates. Gap: fewer than 3 cards (1).
  - `ia_poly1850--df8f2267db2b7275--s002-l0041`

### Latin — 7 cards

E3 CER 1.55% IA stratum failed at 89 letters / 100 10,800 rows excluded

- **Damaged heavy type misread · 5 / 100**: 3 cards; 3 matching checked candidates.
  - `ia_poly1850--a89bd2c9bdb1ca6d--s007-l0044`
  - `ia_poly1850--f806d3f10b2ecf9c--s005-l0058`
  - `ia_poly1850--f806d3f10b2ecf9c--s003-l0018`
- **Ligatures dropped · 2 / 100**: 3 cards; 3 matching checked candidates.
  - `ia_poly1850--b3d418e8a99d8bec--s005-l0023`
  - `ia_poly1850--2d02eaf0f19a649a--s001-l0042`
  - `ia_poly1850--f806d3f10b2ecf9c--s005-l0092`
- **Small-capital roman numerals as digits · 1 / 100**: 1 cards; 1 matching checked candidates. Gap: fewer than 3 cards (1).
  - `ia_poly1850--f806d3f10b2ecf9c--s004-l0129`

### Cyrillic Russian — 8 cards

E3 CER 1.87% full-coverage Cyrillic 3.19% → 1.63% with codec v2 and the recovered rows coverage vs plan 30% , Russian out

- **Word-final hard sign flattened to a soft sign · 26 of 49 positions; 19 / 100 cards; Google's ъ never wrong**: 3 cards; 18 matching checked candidates.
  - `ia_russian--3fd32314d172e951--s006-l0010`
  - `ia_russian--61f76a57b26f9b13--s002-l0017`
  - `ia_russian--4ce4c0e3183ce075--s007-l0003`
- **Hard sign dropped or garbled outright · 2 cards**: 2 cards; 2 matching checked candidates. Gap: fewer than 3 cards (2).
  - `ia_russian--03b43bc5289ad8ce--s000-l0026`
  - `ia_russian--03b43bc5289ad8ce--s007-l0016`
- **Italic т (shaped like ш) read as ш or п · 2 / 100**: 3 cards; 3 matching checked candidates.
  - `ia_russian--d83b48ac6a21756e--s003-l0006`
  - `ia_russian--03b43bc5289ad8ce--s003-l0028`
  - `ia_russian--d83b48ac6a21756e--s005-l0019`

### Cyrillic Serbian — 6 cards

E3 CER 1.87% full-coverage Cyrillic 3.19% → 1.63% with codec v2 and the recovered rows coverage vs plan 30% , Russian out

- **Serbian prosodic accents dropped or substituted · 4 of 4 marked lines**: 3 cards; 4 matching checked candidates.
  - `serbia--27b182bf4116728f--s001-l0026`
  - `serbia--42fedee06e6cb85a--s000-l0022`
  - `serbia--27b182bf4116728f--s001-l0002`
- **Letter confusions on damaged type · 3 / 100**: 3 cards; 3 matching checked candidates.
  - `serbia--92821dc521ddd9fd--s001-l0031`
  - `serbia--1bf6b218b99d4dbb--s001-l0025`
  - `serbia--90015698e9ce2250--s000-l0033`

### modern monotonic Gazette — 11 cards

E3 CER 0.72% on monotonic letters on clean crops 93–98 / 100 coverage vs plan 58% , parliament-heavy

- **Neighbouring-line ink inside the crop · 27–46 / 100 before masking; 2–4 after**: 3 cards; 37 matching checked candidates.
  - `gazette_modern--73e4d3191f16b5e2--s000-l0091`
  - `gazette_modern--49b793056935d163--s000-l0112`
  - `gazette_modern--9aa572190ac3f790--s000-l0015`
- **Two or three lines in one crop, label covers one · 7 / 100**: 3 cards; 7 matching checked candidates.
  - `gazette_modern--2e613d9290dd13d4--s000-l0209`
  - `gazette_modern--0020420cfe156a73--s000-l0228`
  - `gazette_modern--0020420cfe156a73--s000-l0039`
- **Faded typewriter line with invented accents · 1 / 100**: 2 cards; 2 matching checked candidates. Gap: fewer than 3 cards (2).
  - `gazette_modern--c1b2194696b35bb5--s000-l0077`
  - `gazette_modern--5ede709b65bee305--s000-l0016`
- **Short words misread · 2–3 / 100**: 3 cards; 3 matching checked candidates.
  - `gazette_modern--5ede709b65bee305--s000-l0098`
  - `gazette_modern--e49d2191ace06863--s000-l0041`
  - `gazette_modern--0d0b2233a81e355c--s000-l0073`

## Sheet B: Segmentation failures

C1 selection contains all eight merged witnesses: seven `merged_two_lines` tags plus probe c098, whose detail explicitly says a full previous line is inside the crop. Four fragment witnesses use SG1’s existing classification; that classification is a crop-clipped witness, without an independent annotation of full printed-row extent. The five clipped cards are the five Gazette C1 clipped witnesses. Probe c053 is also merged and appears once in the merged group with an additional clipped pill. The column card is ELSTAT c068. Twelve overruns are seeded and spread round-robin across strata. Four rotated Gazette crops have height greater than width. All 24 SG1 examples remain present.

After line-ID deduplication the six primary groups contain:

### merged — 9 cards

- `gazette_modern--0020420cfe156a73--s000-l0028`
- `gazette_modern--0020420cfe156a73--s000-l0039`
- `gazette_modern--0020420cfe156a73--s000-l0138`
- `gazette_modern--0020420cfe156a73--s000-l0141`
- `gazette_modern--0020420cfe156a73--s000-l0146`
- `gazette_modern--0020420cfe156a73--s000-l0162`
- `gazette_modern--0020420cfe156a73--s000-l0228`
- `gazette_modern--2e613d9290dd13d4--s000-l0209`
- `gazette_modern--5af16c5d518d2ebb--s000-l0128`

### fragment — 4 cards

- `ia_poly1850--f806d3f10b2ecf9c--s005-l0010`
- `lekythos--49c082ba27aa27da--s002-l0081`
- `nlg--3d6bd7bd688acb61--s006-l0005`
- `nlg--df6ccc87357b61b6--s000-l0013`

### overrun — 18 cards

- `bsb_poly1850--515c78c513c1c8c5--s002-l0063`
- `bsb_poly1850--e18cacecef3b4590--s007-l0061`
- `gazette_modern--54876940c2de96c3--s000-l0062`
- `gazette_modern--73e4d3191f16b5e2--s000-l0153`
- `gazette_modern--b6928cabb92b6656--s000-l0123`
- `ia_poly1850--36dcee7ce4c29f8b--s004-l0032`
- `ia_poly1850--630348c9d2867dfc--s006-l0036`
- `ia_poly1850--63f57af8d450f3e8--s003-l0021`
- `ia_poly1850--f806d3f10b2ecf9c--s006-l0165`
- `ia_russian--2a45a0561eb05739--s004-l0017`
- `kosmopolis--62ca52b56ebe780a--s005-l0034`
- `kosmopolis--62ca52b56ebe780a--s005-l0051`
- `kosmopolis--ef37f6cfdd896488--s000-l0010`
- `lekythos--7f67b784930deef5--s003-l0071`
- `lekythos--dd72392a3777225e--s001-l0089`
- `nlg--1144074169f43992--s007-l0025`
- `nlg--df6ccc87357b61b6--s003-l0029`
- `serbia--65619613641f9c5c--s001-l0008`

### column — 1 cards

- `elstat--df38bce62200e7db--s000-l0191`

### clipped — 8 cards

- `gazette_modern--54f1f0595779ed67--s000-l0071`
- `gazette_modern--5bca118bfbabb811--s000-l0052`
- `gazette_modern--73e4d3191f16b5e2--s000-l0026`
- `gazette_modern--929e10adc3109aab--s000-l0052`
- `ia_russian--6cfc00f06e0f7241--s007-l0003`
- `kosmopolis--aaa124307e36f113--s001-l0085`
- `kosmopolis--addc07a6b4eaefef--s002-l0002`
- `nlg--7870403c3df244ea--s007-l0025`

### rotated — 4 cards

- `gazette_modern--8213d28643843855--s000-l0144`
- `gazette_modern--83c3182a4175392a--s000-l0259`
- `gazette_modern--b9f59878fb904d91--s000-l0034`
- `gazette_modern--ebdc4d07ff8c4122--s000-l0265`

All 44 B cards have page strips. Gaps: none in crop/strip availability after local recovery. Four rotated cards are verified by native image dimensions. B includes 24 SG1 cards; remaining cards are C1 additions.

The seventh `missing_box` group is a disabled data hook in B’s spec. Although the current examples file now includes three SG2 records, OS1 explicitly excludes that group, so none were built. Enabling it requires a separate scope decision and page-strip evidence of the stated absent-box scope.

## Crop recovery ledger

### failure_modes_per_class: 14 reconstructed crops

- `bsb_poly1850--2fdb06c3a8566781--s003-l0023`; bounds `[176, 1248, 1227, 1303]`; historical `9abf49ac806c1b9b1f4fb35cf6e1453788d012db04473aa7b1b099dc1ace2572`; recovered `ca724d276b82ea0cf5c6aa9edbfa78ec43eb9ec949eb13c57e7b429ad18a2d0d`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/bb2f9c3c2faef17b12d2e6f59990f196e4c2cb9b3eb65254630ec86e64a312ad.jpg`
- `lekythos--0fc3672826ddd6b3--s000-l0033`; bounds `[304, 1436, 750, 1469]`; historical `5066944082050b58862f59d07f0ff76f33d4f84a735a5ac56d142857ff6e2b8d`; recovered `d9b16e1066924e8c944802db900fc49f421826080dc5e55456f94e35b528675a`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/c8debe4a722169688711dccf9535059ea13f17844d67f97f98ec1c9537ac06e4.jpg`
- `kosmopolis--ef37f6cfdd896488--s002-l0036`; bounds `[174, 1170, 825, 1204]`; historical `7bdd4ec6a17f41be54f881fd66356ee5371a37c85b7ec280539f3807dd3487b8`; recovered `4fcfb630f3a7a8cb84580da9630b54cd018a6527b8981d747dbd629e216d5d8d`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/badfbc45cc81942ae2e013038b150c7a13cbc3fc5188c42503c614ea4c365da5.jpg`
- `lekythos--25feca8f4ab34ba0--s003-l0302`; bounds `[2239, 1914, 2668, 1947]`; historical `96d0634c82daf07544515a2487d91edc90c2c8ceb7d2d03b133a0b721705a1b1`; recovered `448a4cda08681906c77e215213398f8d81f83bec57a708d9a4a6b6658633e562`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/c7666c1bda35c37fcf57acd07e670c1a221bfbded382c02ba8a890a4f8ebb3cf.jpg`
- `kosmopolis--681a15c3d4a0cd62--s004-l0027`; bounds `[145, 882, 794, 926]`; historical `90bb080aa54b8de8dd9cdd4eddf1e226fe787e708d37c555b60b82c1d3530e37`; recovered `241cc8e1b90f2c418db83d5c6c5ba862bcaf58fb6aee7cd985bee4b9a318c77d`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/d4d2e3123dfebbb69b9cd709ea8f5e9c41ad9d399bcf8d441d426dc7996d315e.jpg`
- `kosmopolis--ef37f6cfdd896488--s005-l0008`; bounds `[73, 248, 785, 283]`; historical `d77392dd88778f92552acf617f58eba0a3679ce770a4099f64655dc78cacf9e2`; recovered `2d670d28672e2b55f17a93a64e526ad23fad6fc8c758056f0729514d4d27a764`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/21d023cdf46cd31add8bcf9f459c57461a8417d64476ecaa26e7919c2b236a8f.jpg`
- `gazette_modern--ebdc4d07ff8c4122--s000-l0265`; bounds `[1450, 1132, 1471, 1211]`; historical `2fc702cf3e727e7c12158465833935b535a2058f961a1759d200330208e5bd82`; recovered `265aca6ba29dcef55f921195d162157ed4f1b5835873303cedc39a821b373099`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/b68684f4ab5a677b1bc46fb44430543ac3bbec562baa8c1e2c819b278db39b37.jpg`
- `gazette_modern--b9f59878fb904d91--s000-l0034`; bounds `[523, 1428, 545, 1516]`; historical `540be47138a2df75096f2de8a62650ccf5ab23b8bd68f5bb44a0f27ec305e553`; recovered `68ecd9dc5bc20e786106915c84e7a7e5db82feabb8070cc470019fb1c7527158`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/325c5d05ce532fe7fd2badacd97c8611a9fa1061d31a3ddee19c91872e63d577.jpg`
- `gazette_modern--8213d28643843855--s000-l0144`; bounds `[684, 1916, 705, 2001]`; historical `46c93df9d8476ed5ebcee62b166a5b67098d6cf5f421bdbc531b4bd27e202de5`; recovered `ed8ddb498282423ac44030fb5a3a464c37783c6220cd9393676d0ccfeab88275`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/f6f0e3177fcfb10d71754bf4bbd4363d6c68348b3f8b6cf1513cb43c48c4d184.jpg`
- `gazette_modern--9a7f184282a21b5e--s000-l0036`; bounds `[201, 1005, 219, 1163]`; historical `5306f5db64f69c1d90052486d969f524da50695b936ec39f733d4153f682d518`; recovered `da8eb9276cd17dc8c5aff9e4735979573ae454434e1f293b854fd20a8b831e7f`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/3d9870f9c41fc1aca340930a03ad655a7303ed4c02f876abc8e6e9408a1eee53.jpg`
- `kosmopolis--aaa124307e36f113--s001-l0062`; bounds `[669, 584, 1237, 625]`; historical `96231577ffea33248ba106d8bae97e9902487c5d18ba7a79424de85b8bbfb852`; recovered `fdecf37750bd9c5daf0d5ac2e3b415de517c6dce9c3457ef0615b934db3a960b`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/f059908b2f8f7a3ac2f7cf4462fa45b0d14883037adc379aaf5940a032df63ec.jpg`
- `gazette_modern--73e4d3191f16b5e2--s000-l0091`; bounds `[78, 1580, 760, 1632]`; historical `f4612a509db3cf7ac5f2fde3665e9b51421c7eb0b990ebde9598263349bf7aec`; recovered `e27fdf19080b495db96f2d349df631fc79f94f92f41c1d2c0471f4ec615ad0e1`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/c30c4b62800b3dc6aea36285247ac7249f51f4533bce2ae2141a77c97bff62fc.jpg`
- `gazette_modern--c1b2194696b35bb5--s000-l0077`; bounds `[865, 1451, 1561, 1484]`; historical `3bda4e07fb435f6c806939c33f2ed4ee5c83c5e8e762b770d6c451d5c9a19336`; recovered `397549260bf041cdac6a09522d7e1f18de50f2939c90436378df61dcb4aab689`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/7fb630cf841ec1f5d7cd151dfe93aa4424ec52e6e9dfbeea45563a5296e70a2c.jpg`
- `gazette_modern--5ede709b65bee305--s000-l0098`; bounds `[786, 1125, 1523, 1167]`; historical `56d0ccf3636dd2a051730b2a56b619b4669a83b9570ecc81bb69a524692aeab3`; recovered `1907ba3ce3b454d35385e8d867b6cdc0fbcc160518ec9b667b3584fc3d5b897a`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/d4637de868d75f9e8b037e443243bc55060232f1dbdd7fbe0ecd63444f10dc67.jpg`

### segmentation_failures: 8 reconstructed crops

- `gazette_modern--0020420cfe156a73--s000-l0146`; bounds `[880, 526, 1605, 597]`; historical `15dc3e30db51b74fab197f2b2c6fbfa3b6a1c6adeacaa9cc134e02679c22e635`; recovered `dd88311411b6bb08bd66513b70cd8b216e3528d6898e95c2bb801ae4330e818d`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/d3ed0b1fc1fcd310867252bc091a1e669bb5c97f23ddd4af168845c6af683d24.jpg`
- `bsb_poly1850--515c78c513c1c8c5--s002-l0063`; bounds `[208, 2250, 1001, 2308]`; historical `ade53ca2316283f951135edcb6de133218e04c6342d3e86ac8185a3ccb587bd2`; recovered `2b24344b0c64bdc56c7abdcebe7b66e5a39fcbe2d3eb619d7ca221b3d3d10dca`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/93801adc8e75160cdc18e79a2a0b77a679177a7ca05a9cbb12cad258dcabaf0a.jpg`
- `kosmopolis--62ca52b56ebe780a--s005-l0034`; bounds `[117, 880, 830, 919]`; historical `c835bd824c7a2a93ced80fbf03a3059b3a019e57bbacd4398c6124286da04587`; recovered `464c03ee72bc682f6531f28134e9aee3d1e4dbf958a123c883891c9935a7105a`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/94f3dbc71bd0c7417d8f54cfd7086fba6331ee2cae515c09f6068d40cf84ec51.jpg`
- `lekythos--7f67b784930deef5--s003-l0071`; bounds `[697, 1237, 1198, 1273]`; historical `221cec1e11675825ab2481786030a90819b9f6f5ce51a00c65da04a41f1a250a`; recovered `257aebd25363bbe5cfd29a77a7745cd6798e3f7d32dca784f0cbd97496fb0bab`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/724365fd3ddd2e73bd09a8b062c9f446d58b261ed8ed65806b91ebe444b78fbd.jpg`
- `kosmopolis--addc07a6b4eaefef--s002-l0002`; bounds `[165, 176, 651, 216]`; historical `cd1f459e19076266dbebfb1d5285786235373ea5836b977ed04bedf382a8a71c`; recovered `bac923a713ba9b216e15f218f57114e7d21c07afcc8fc975614a7181b0a9de55`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/18142555ec0a971f6e9975db2a0ec6a96d67130130198d8bd038902b8429f9b2.jpg`
- `gazette_modern--8213d28643843855--s000-l0144`; bounds `[684, 1916, 705, 2001]`; historical `46c93df9d8476ed5ebcee62b166a5b67098d6cf5f421bdbc531b4bd27e202de5`; recovered `ed8ddb498282423ac44030fb5a3a464c37783c6220cd9393676d0ccfeab88275`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/f6f0e3177fcfb10d71754bf4bbd4363d6c68348b3f8b6cf1513cb43c48c4d184.jpg`
- `gazette_modern--b9f59878fb904d91--s000-l0034`; bounds `[523, 1428, 545, 1516]`; historical `540be47138a2df75096f2de8a62650ccf5ab23b8bd68f5bb44a0f27ec305e553`; recovered `68ecd9dc5bc20e786106915c84e7a7e5db82feabb8070cc470019fb1c7527158`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/325c5d05ce532fe7fd2badacd97c8611a9fa1061d31a3ddee19c91872e63d577.jpg`
- `gazette_modern--ebdc4d07ff8c4122--s000-l0265`; bounds `[1450, 1132, 1471, 1211]`; historical `2fc702cf3e727e7c12158465833935b535a2058f961a1759d200330208e5bd82`; recovered `265aca6ba29dcef55f921195d162157ed4f1b5835873303cedc39a821b373099`; page `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/b68684f4ab5a677b1bc46fb44430543ac3bbec562baa8c1e2c819b278db39b37.jpg`

## Inputs and SHA-256

The following shared source ledger covers both sheets. Per-card verdict/key/crop/page paths in each spec bind individual cards to this ledger; A additionally uses the coordinator, aggregate results and yer table, while B additionally uses SG1 examples, strips and counts. Local recovered crops are identified above; generated strips are derived outputs rather than source inputs. The ledger is also machine-readable in `docs/records/owner_sheets/input_sha256.json`.

| Path | SHA-256 |
| --- | --- |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/c1/bsb_poly1850__poly1850_key.json` | `72093dfaac33f009a66f9b805ad620e922a3c5519056e640879174721965cbc1` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/c1/elstat__numerics_tables_key.json` | `0024fb23f9f46ab0a7066e7ec347593917623ad12c6de7bf4d980e00532a3c2b` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/c1/gazette_modern__modern_scanned__measured_1986_1990_key.json` | `a259721f1002ec8d4f40639a2d0621ac67fefd936449e401f4fbfdca14d5323f` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/c1/gazette_modern__modern_scanned__probe_1982_1985_key.json` | `645debcfd2a5cfb7d10a1321939b9f9b2bf73795d1243a0219ebed81e93f3262` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/c1/ia_poly1850__latin_key.json` | `34b00e31716eddcfd56a7d6e729b409b3378ec63c4bdff1155d4a9598616dd8a` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/c1/ia_poly1850__mixed_greek_latin_key.json` | `b587d050d8c205a4e451fd2ba786d07b7fd8334de028ff49954f87233ffc4c15` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/c1/ia_poly1850__poly1850_key.json` | `541986452464bf1c077fa794221019e596ccfc7300d497a00d6aeb1accec9d1b` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/c1/ia_russian__cyrillic_key.json` | `e3e7465eaaafcb936be993553de1bc5eebd3c45958fe217173dfc3f4fb1e5f4a` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/c1/kosmopolis__poly1900_key.json` | `1788e056ed9fd6dd2167e8aec74970a98e60c1a29c49f588065f18139b997eb7` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/c1/lekythos__poly1900_key.json` | `f910e68e3effc680fcea43fa3a70658490048f1e483aebc7b52d99adb4fe4506` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/c1/nlg__greek_poly_key.json` | `e8b8d0329f51d78eaad269f66b12061136e35d7e8b4c5b8b305ef5b58b1e3432` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/c1/nlg__poly1850_key.json` | `539d7dc56f1d7084c66a192e87ef44f638cbdecc609646b9f6ae34fad70acb6a` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/c1/nlg__poly1900_key.json` | `b3471ea910219c8412900af80b8de201b785284704b4869bff062cb7f2e3e603` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/c1/serbia__cyrillic_key.json` | `7b85a61c7619f2f697d84d593ef42d2e49d25ba393f1e726432022c59461b30b` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/bsb_poly1850--e18cacecef3b4590--s000-l0057.png` | `c2114a2f68cae678d7e12b37951b0d6011cbcf3dbc1b3d7d22bef31f54338666` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/bsb_poly1850--e18cacecef3b4590--s007-l0061.png` | `35ee18fe29ddf9047f1b7ba205b43ce3e8df23298d8d8ecc38e2cb966bfe7486` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/bsb_poly1850--e2115ba0deaf6a07--s003-l0039.png` | `08eb3564665d9a758bc5f8c9141ca7983114ed6663fb76ea777c27889ffc76c9` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/bsb_poly1850--eded5a16c1b78a01--s005-l0055.png` | `b9892296baba22cd94f8a76b03d068db5d53dec22072dc450b6a40344c86f84e` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/elstat--c5f7ea1f26d39839--s000-l0367.png` | `3b233bcb64195aee9b422cca8db0c7cf398849edfa1c16d106e356ec9072c470` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/elstat--df38bce62200e7db--s000-l0191.png` | `5546102dcb04f2d330c8f406ca4903a6c5582f0be36b099ee43abb48339e3f98` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/elstat--ee37bc488988f1bd--s000-l0445.png` | `fc2514235a50c104794662f97c42b9bc9c8b0d1f1135ee3acfa5adf9a21e4cfb` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/elstat--ee37bc488988f1bd--s000-l0457.png` | `46ee440fbd9cbe5cb4e67b26f6442bc3077f8fb6450c5401b2b986e1c92d4bee` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--0020420cfe156a73--s000-l0028.png` | `4c5bd6a870974d59d60f6180b4b07d50cf437686dd196e9c578970fdaaf4adcb` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--0020420cfe156a73--s000-l0039.png` | `d6ee915877f9129a8287171bf43057ef0bf505723201faf4d0376c6c072d914f` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--0020420cfe156a73--s000-l0138.png` | `ae7ff6dcca613640e1d36d8f3464ebb56ac23afe8dd3becb2e30b745a80f07f8` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--0020420cfe156a73--s000-l0141.png` | `ae7ff6dcca613640e1d36d8f3464ebb56ac23afe8dd3becb2e30b745a80f07f8` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--0020420cfe156a73--s000-l0162.png` | `bf8bc0e6ec4f754955e59274a3729fadf47e22d9e5488eefed3de50c07dc2508` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--0020420cfe156a73--s000-l0228.png` | `e32e79e69f95577cceb57d70378fdb722b17e8c9121f7eeebfac705977cb9a66` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--0d0b2233a81e355c--s000-l0073.png` | `aa03767bb92b74b71c2203cec88ef61fe4aaac5c59f4ef2b96e24082faa8edce` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--1f7db88d63c02afa--s000-l0287.png` | `02069a114edebcc1290d48235037ea4db58a369ad85a5808718e4ec9c7002fbd` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--2e613d9290dd13d4--s000-l0209.png` | `cfc88e318869666d84f7c2e23807171e51fbc1835266c5977f3454c938e382ec` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--49b793056935d163--s000-l0112.png` | `badb86311fe6cc2aa5d932cdde3b4ae2e5940f01903e751fb831dbb50040dfce` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--54876940c2de96c3--s000-l0062.png` | `bd85e5310df3f4bbc3236d305989294dfdd9363d0e4dac119b0418e87e5a7d6a` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--54f1f0595779ed67--s000-l0071.png` | `86aabacfa33670fb7c5f5946e5420b177320f251a60dae62e31e037bab482366` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--5af16c5d518d2ebb--s000-l0128.png` | `96624f256e8b122dfc8a177009a4888da917b789c163c11ed3175ff954f3be0c` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--5bca118bfbabb811--s000-l0052.png` | `73b43a5cf0c72124e911e5e7786c3311dac05f47305b7086680a2fca56e2107c` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--5ede709b65bee305--s000-l0016.png` | `89992b40be8f07300a77a117c12814ae8eb0d462beccf80a8d229c4dbf199698` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--73e4d3191f16b5e2--s000-l0026.png` | `e326c99e9051dafdd358bc27fca4a6c6ab06803d1979377bc0b06e40c9ce43ad` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--73e4d3191f16b5e2--s000-l0153.png` | `1eff766aac6bf98746743b4f6cd93d2e7fcb93c23f2e8cd2236e500c4fa2defd` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--83c3182a4175392a--s000-l0259.png` | `408095dcaafa9b8bcf70ab488a73363180d0048b304d762b0d4b876c8299ee72` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--929e10adc3109aab--s000-l0052.png` | `316f5b1c36fbbd6a99460ec4002b4bf2062cd970a0a50dad7c87a589aff5db1b` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--9aa572190ac3f790--s000-l0015.png` | `65daef36eaefc2e2470e278e179de6891704d70e24cdf1fc52bc691741fdd190` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--b4c2554fa74331a6--s000-l0089.png` | `7493b2eeb32bc888ca97af0933b7bec7cc8fed90c0911b6622ce80472d79a3a0` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--b6928cabb92b6656--s000-l0123.png` | `3d8bdb78ffa3b3ec21f5e5a3eeb50c18159cbeae2a28a9db43d9668408e09c96` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/gazette_modern--e49d2191ace06863--s000-l0041.png` | `53dd372a05a8e35b7f8db66dc95ab9e12edbb3fb8a9273251b00f85006a72d63` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--174d84a441d69a70--s002-l0040.png` | `dc7ab54c90e012ae15b023cbdf6bf2168b20461511181621731bf8c684f40d22` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--231a44f61c5268e0--s001-l0026.png` | `543da02c465fae431c8f5615904e039ca4f1472c6557bd2100196362ece1c03e` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--2d02eaf0f19a649a--s001-l0042.png` | `0dd45ac235a4e8f137b8aaa4dd2f1c2ac4abb590c8b569722719efff90bc2c31` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--2d02eaf0f19a649a--s005-l0015.png` | `101b57fb08e5e5d30634d196d50193244e54f04908e079b7eeac0dd25124a0c7` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--2d02eaf0f19a649a--s007-l0032.png` | `eb617427aaf94c8a2556548888126a27df3db55ce48ba39eecb4e39c936edd6d` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--34543d92a48213e7--s001-l0026.png` | `e7eeb0a0699eff8a9253401511046c6bc298f310f21e5afc537d890e5b22e550` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--36dcee7ce4c29f8b--s000-l0055.png` | `6ccd68364fdb42079d478a84e83161d25fcc94d6beb38bea008bbd0118c2fa30` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--36dcee7ce4c29f8b--s001-l0067.png` | `3de5c6e8639ff0b07a12637567aafdfec02c1c6d35d22bcecb30e57ca8c80b10` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--36dcee7ce4c29f8b--s003-l0110.png` | `1965512c4b7c95529652442c4a9704dd18f6864ad761a3aae3e70d2fac69deb9` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--36dcee7ce4c29f8b--s004-l0032.png` | `647a917900d56382ba26aca9c6241bd47e706f9c083044bbb517ab2120c30c54` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--36dcee7ce4c29f8b--s004-l0061.png` | `1ac30bc8246ba93e360135b8ff42316046d332cf494deec2e8a289d11d960926` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--3cbcc415675468a9--s006-l0037.png` | `172e59dc980051283a6d9c705f04a1b833724545270b1088a8a41b616457c2fd` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--41e90f3ba967f920--s001-l0025.png` | `de4d1e13f1ac6c8f0b4599585cf2504028aeaed4c6143a7a456c034af65b9e5a` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--41e90f3ba967f920--s002-l0022.png` | `23ed860f215d0a55df3877fa76b676612d561e59be843c78415485d01d4d4244` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--41e90f3ba967f920--s006-l0022.png` | `c84ca8ac55372dfb7c12461dad217bc366e5ce6ad9bbe7c96a75879512de9c7c` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--630348c9d2867dfc--s006-l0036.png` | `d4f1b113172029f19a3b7d5a60bcdc8d0f8f13f7fcec3e811d5d7861f682900c` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--63f57af8d450f3e8--s003-l0021.png` | `4dc04e20b064ea01db6dd76685d3268d1944ee8b4da20be957277bce23c9e3b3` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--a89bd2c9bdb1ca6d--s004-l0025.png` | `e67a02bbca5d90ed9e51f59bac4fe890731049166eaeccc92fd2da9abfd55108` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--a89bd2c9bdb1ca6d--s007-l0044.png` | `5edfb5d33169d255e83ee85e3801634fa12a76bf8a57e5521a5b0cee65b720b1` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--b3d418e8a99d8bec--s005-l0023.png` | `63ccb474123db9039561353748db30f63dd33d73d1a87ed1058f717eb16912d1` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--ca4f3983c96b6334--s001-l0026.png` | `f1b01a1275647cb131074ddd88d3111f1c8554903b51ca29447266ab59518b22` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--df8f2267db2b7275--s002-l0037.png` | `f9b7478b3c50dd4358051dcd7e15dd90600b8ed9d68200ac4cd2e0c2583ed275` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--df8f2267db2b7275--s002-l0041.png` | `02f0d7e8d0c249373dec79c691ed9638bca1b800e0eba7894bcd8e6de957d07a` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--e6e379cb4b1d54af--s003-l0025.png` | `b3c04d8db97a76118c781b30109da323e4c3a303384f507deabd900dca7dffbc` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--ebcfd6056abfa776--s003-l0099.png` | `aee77dafb49d96644c4c20a2297cd7041614497a66341fbb2001765b6a1ae4b8` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--f806d3f10b2ecf9c--s003-l0018.png` | `1374e43bbcbe968c7a077d1320cbf3ee4f50e58d4e446d7ed8471aa066e51fa8` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--f806d3f10b2ecf9c--s004-l0129.png` | `c45c278d2f1cf08fe60033f49eec1fe12a09d8b638fdac13669a1e4a2b20cbc7` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--f806d3f10b2ecf9c--s005-l0010.png` | `f9dbb6b583fbafe7188860a1008b57f08b85b2844a188f5126c9ef25d04db9c9` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--f806d3f10b2ecf9c--s005-l0058.png` | `190eb41cb9473f8e1689401412522f0b7128704849cf0b0f3c54eb942c484962` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--f806d3f10b2ecf9c--s005-l0092.png` | `d930e888e1626f15c401c6a364dda72bedec2a50e61913b29d9df812d96ff69e` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--f806d3f10b2ecf9c--s006-l0123.png` | `87cc822699632aeaa4506cfc4a8d579957a38504c363789a56d7d51d6bfe69bf` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_poly1850--f806d3f10b2ecf9c--s006-l0165.png` | `faf671b2c389dd96a6fdd157edd43fa987fde45dacfa59391b3d1dc3e1239363` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_russian--03b43bc5289ad8ce--s000-l0026.png` | `b48d26ba507e6cf865a19f2921e4bf69fd8a8a8c0bfebee753272e68d5244421` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_russian--03b43bc5289ad8ce--s003-l0028.png` | `95c8326885b7e548b941950edc38f27dd100a6c35ec0bd6fb84e1529ee92e853` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_russian--03b43bc5289ad8ce--s005-l0011.png` | `73fbc1cf523b1cdac707d1f10c71bcdc9ccbef6d37e4163faa94a1a3f201b9a2` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_russian--03b43bc5289ad8ce--s007-l0016.png` | `7174c309c668a76bae93a451263f5e91a11d161eb2a71869350abfe187235c86` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_russian--2a45a0561eb05739--s004-l0017.png` | `7712eda23becaa4c2cbc3410a9e6a73838e7769c56b929889e6bb25d61ec73e9` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_russian--2a45a0561eb05739--s006-l0009.png` | `df01ea10ae52d9c0bd43ab205078f85e967ea3c8f79c7005a9dca2c91120032d` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_russian--3fd32314d172e951--s001-l0005.png` | `86f682e5094e3a9cc108da803c3d2df3e56bceeeb4548fd7cdf64ee54cb9a165` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_russian--3fd32314d172e951--s006-l0010.png` | `eb1081b62bfd6b795f80c52d7a1cb21461b55549c3bdcdd8c28f37503594ee6e` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_russian--4ce4c0e3183ce075--s007-l0003.png` | `a86403d58c8bcc59e145cd1f4689287f754fc97fe8f076f3b7007027e2797a26` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_russian--61f76a57b26f9b13--s002-l0017.png` | `5b1f386b01ee6614706c67d95fb90a9920a5626c4401071612fb7f0642086ca7` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_russian--6cfc00f06e0f7241--s007-l0003.png` | `15516eaddaa4fbf4d7e80a14911849cb92c11280eb5d7b8850260c2a83cf86c1` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_russian--d83b48ac6a21756e--s003-l0006.png` | `71bf0a5e5aa7ee2f61af65430a671df806f50afeb77286c7b0338bec17fbb5b4` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/ia_russian--d83b48ac6a21756e--s005-l0019.png` | `e98b9a30f5492435bfe0c21fc30d983ea3724c0e1d6aee0d1d7b1fdf1d022da0` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/kosmopolis--62ca52b56ebe780a--s005-l0051.png` | `edb52701d4fcf5cfac6b861fe638275fbc9ef812067631a6e20d6725daaa90c6` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/kosmopolis--86098eebf5207e79--s006-l0027.png` | `e11e4d7345016c5cfe21a6253a7546604e64350255811b55b5abcc5893fadfa4` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/kosmopolis--8f8439af940ad55b--s006-l0010.png` | `ee6a1ab8c8fa64f17b468287913c33ef54638e58d1f018bb096a6230fa11e42b` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/kosmopolis--aaa124307e36f113--s001-l0085.png` | `a0497ecd2249e32b68027abab11498ad2d5954f145914062607e6dc570757a76` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/kosmopolis--acb323b6cb8d169d--s000-l0020.png` | `266ad220599251393fc24a7efb0788a116adc1b0d08eb40002fa79476c2a3c68` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/kosmopolis--ef37f6cfdd896488--s000-l0010.png` | `a7a47842284178a91e0786b5cb8fbcd30a44ee412a5203a84d82c942dea6966f` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/lekythos--36e76126a4edbc72--s001-l0077.png` | `23fd072c6f170e0c0d848b2bc825a6aa17c9f8450cea7e8ba087b6b1abe60713` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/lekythos--49c082ba27aa27da--s000-l0317.png` | `d96274c5614f32f279391d8b5d8110cb946ceff7b0e1c53d10d11c02194e49bc` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/lekythos--49c082ba27aa27da--s002-l0081.png` | `39f229691c43f2fe502c0dc891c42d7e116111689e870c14539beed2ea3cd33e` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/lekythos--793fb44fdc7e1aa6--s000-l0247.png` | `0a786f9730ee324c7b3c85db3f69abb067e1cb6f314131241aa1cdfb9d788213` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/lekythos--dd72392a3777225e--s001-l0089.png` | `ea50aa01b8fad8d1f342e03e5313cae84aeed8f9da068a6ff819cbdf9edcdbd9` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/lekythos--e9f314aab488b65f--s001-l0199.png` | `3d6c49a9f8424b71e0ed795d24bbc7d3cead90a59d09e22ce1be7d02a2622e94` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/lekythos--e9f314aab488b65f--s001-l0335.png` | `64a2aeb18a782167fc908dec8520ea429be430a70ea3b9953ca22649d72ee2ec` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/nlg--1144074169f43992--s007-l0025.png` | `568c3205252e6da070a463756f8a6f77dcb80beebfc9184ef54e089d772ac0b5` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/nlg--3d6bd7bd688acb61--s000-l0025.png` | `15194deb0ab19ab4f1968bdc8686568864f00d37376fb39072faa34c1a4b97c5` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/nlg--3d6bd7bd688acb61--s006-l0005.png` | `3c85e7120fbf95e616238deb742e2f12b91d7a07860924489957f6ecb1266652` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/nlg--3d71f4f87abea186--s002-l0017.png` | `f6bbad0a95e51b9654a0dbf618f61d84caf4e36bb562c5f4ce2fc19f42ca5ae3` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/nlg--6146c0455e0103d2--s004-l0024.png` | `7779a1fd9231b61a903a8a031226551e25b387996ac6075663561aaf5fa457d2` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/nlg--6ae0ac01064a587e--s003-l0013.png` | `c54ac07ecbfb0443e8c0e58b019ab2dc750aab5c00c93cb73ac5103f301cbc49` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/nlg--7870403c3df244ea--s000-l0016.png` | `b1fbe9cc4b3efaf6b66fbddd3cbcd69b4afe84a71523edc899dbc217f03c0f4b` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/nlg--7870403c3df244ea--s004-l0023.png` | `6f26434d40e62a2d3f4387d50f8b8f3047a7b5bbee9c25a9a2f9672d4c3fac56` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/nlg--7870403c3df244ea--s007-l0025.png` | `7648ec25d251fc36cf23fbbfe58a444013a219056819cfdeed77a965df90e1c3` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/nlg--9aff599c7fffc574--s002-l0015.png` | `c6ab3e22376339455bc7ba0a0f256f13fb2220858937f947e1888ea39a24bec7` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/nlg--9aff599c7fffc574--s003-l0007.png` | `9ee28abc39f896353954c6faf8a6c9b473ef00c9d8cd744ac57f02b1ed40d9f3` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/nlg--9aff599c7fffc574--s006-l0008.png` | `024a668c8adc2a3c74c48784cb89d659ac9d247145e4b53d9aa847ddd0a320db` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/nlg--df6ccc87357b61b6--s000-l0013.png` | `6fe925e30dca3986ef3926b3add26199589decf0a0d0690ec1ef0ecfe91f79b3` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/nlg--df6ccc87357b61b6--s003-l0029.png` | `829656a3410e954815b1e3bf51fb3c9bdc0f796c0ec49792238c976b1022c423` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/nlg--f4b52df5f8130047--s003-l0030.png` | `0d30930ec6946301fcbad7100cc3494fd20c6b263b08d6c21371cdda2205e366` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/serbia--1bf6b218b99d4dbb--s001-l0025.png` | `be1ea625173f7f184ac2a662d0fed2c89449aa55e0ecc10b42626218bbfff19f` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/serbia--27b182bf4116728f--s001-l0002.png` | `cdfe853c4c75ea898fcfef4e4d92ef59d56a9d2f45ea101e272e9c1fbd221bbd` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/serbia--27b182bf4116728f--s001-l0026.png` | `1ecb03e931332ae4ec2ff6afe3f2ef0e5af40ac3107ee6dfcb7178f354cfe08b` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/serbia--42fedee06e6cb85a--s000-l0022.png` | `d7d9fe395b434e819a9aee9f562978852336f2dbc3c0a07977737af7a77c014d` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/serbia--46c745f49e7507f4--s001-l0015.png` | `5b44a835fd5679991d8ddbe926214946c99f2a3d14d9cf8fdc00bc02a4fba21d` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/serbia--65619613641f9c5c--s001-l0008.png` | `4750e1327276c74f2ad353f034e4a4d5d1a5c20d5dd74ccbbf197fcdd0f4ede3` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/serbia--8fd9a36edc06b7f9--s001-l0004.png` | `f30eb27892ca798620b9487eedaecbdd7c1b2ea49a70820c89a918cf156dc368` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/serbia--90015698e9ce2250--s000-l0033.png` | `180c40040efd770412a2ad9a91768ae6fec76bd5ccd5c2ba6162d58849f27b1e` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/crops/serbia--92821dc521ddd9fd--s001-l0031.png` | `7851dc8e58757c926afd7a141736e83322d56899042b0e59e2e699709c79f775` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/W1/features.jsonl` | `c85b407a724f4a17dfbe659cc9e2dfd171660de5e29baf1fd86b291f7cbd9c4c` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/04bb094abd3d0b2f07b5bab2701d32259b616ac0f7f302371e37eb229ba211df.jpg` | `04bb094abd3d0b2f07b5bab2701d32259b616ac0f7f302371e37eb229ba211df` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/18142555ec0a971f6e9975db2a0ec6a96d67130130198d8bd038902b8429f9b2.jpg` | `18142555ec0a971f6e9975db2a0ec6a96d67130130198d8bd038902b8429f9b2` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/21d023cdf46cd31add8bcf9f459c57461a8417d64476ecaa26e7919c2b236a8f.jpg` | `21d023cdf46cd31add8bcf9f459c57461a8417d64476ecaa26e7919c2b236a8f` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/266336daf491dfeb0badc94d0a75c599658be09370a8399dbf8329b2fecfb4a7.jpg` | `266336daf491dfeb0badc94d0a75c599658be09370a8399dbf8329b2fecfb4a7` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/26702a2f0c8545d7e1d1c59fc562c911eae660be6b406c64e817fc7cc3bf7d8f.jpg` | `26702a2f0c8545d7e1d1c59fc562c911eae660be6b406c64e817fc7cc3bf7d8f` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/2b6ef5f8ab2e4101f0c2b9d7484af568c60ec185f1bc719289ed9a19543c2435.jpg` | `2b6ef5f8ab2e4101f0c2b9d7484af568c60ec185f1bc719289ed9a19543c2435` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/325c5d05ce532fe7fd2badacd97c8611a9fa1061d31a3ddee19c91872e63d577.jpg` | `325c5d05ce532fe7fd2badacd97c8611a9fa1061d31a3ddee19c91872e63d577` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/34aed545a04477fdad3e23ee4d071491f0ee1282bdab0b3ec8dadbcd20842af3.jpg` | `34aed545a04477fdad3e23ee4d071491f0ee1282bdab0b3ec8dadbcd20842af3` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/3d9870f9c41fc1aca340930a03ad655a7303ed4c02f876abc8e6e9408a1eee53.jpg` | `3d9870f9c41fc1aca340930a03ad655a7303ed4c02f876abc8e6e9408a1eee53` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/477f382af7bc3cd6826ce0bc12077c4597e66bfff3f1a920a7029e2420d0463c.jpg` | `477f382af7bc3cd6826ce0bc12077c4597e66bfff3f1a920a7029e2420d0463c` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/47dd4a1bae8360b229b8340fea316a3f72dc33f054f5345369852da1c15c6007.jpg` | `47dd4a1bae8360b229b8340fea316a3f72dc33f054f5345369852da1c15c6007` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/643a484d7271ff9823534a9b77b9410d7357ef941aeb0c393b70e5f93c0aa216.jpg` | `643a484d7271ff9823534a9b77b9410d7357ef941aeb0c393b70e5f93c0aa216` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/651efabfa8ca730cc601e688a12b6075216b0e30d1406d33be6f4730a0ca9fe2.jpg` | `651efabfa8ca730cc601e688a12b6075216b0e30d1406d33be6f4730a0ca9fe2` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/6aa0f93458ae7135695dabfc5279de10d13cdbf88cc0711e4bf9fe30aa10389b.jpg` | `6aa0f93458ae7135695dabfc5279de10d13cdbf88cc0711e4bf9fe30aa10389b` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/724365fd3ddd2e73bd09a8b062c9f446d58b261ed8ed65806b91ebe444b78fbd.jpg` | `724365fd3ddd2e73bd09a8b062c9f446d58b261ed8ed65806b91ebe444b78fbd` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/7fb630cf841ec1f5d7cd151dfe93aa4424ec52e6e9dfbeea45563a5296e70a2c.jpg` | `7fb630cf841ec1f5d7cd151dfe93aa4424ec52e6e9dfbeea45563a5296e70a2c` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/92dd4093205657fe0632252bdcd4a66142bd0c19fac2936a18dab3f73fb06ea7.jpg` | `92dd4093205657fe0632252bdcd4a66142bd0c19fac2936a18dab3f73fb06ea7` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/93801adc8e75160cdc18e79a2a0b77a679177a7ca05a9cbb12cad258dcabaf0a.jpg` | `93801adc8e75160cdc18e79a2a0b77a679177a7ca05a9cbb12cad258dcabaf0a` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/94f3dbc71bd0c7417d8f54cfd7086fba6331ee2cae515c09f6068d40cf84ec51.jpg` | `94f3dbc71bd0c7417d8f54cfd7086fba6331ee2cae515c09f6068d40cf84ec51` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/a62692942f359edf94b4735518f5acc29b9b245539cf5d8736d8344826d13c07.jpg` | `a62692942f359edf94b4735518f5acc29b9b245539cf5d8736d8344826d13c07` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/acbc0c5ce8cab9c4edb8c51eef987acce643a8631a49fba091dbe2b6b3caa0e2.jpg` | `acbc0c5ce8cab9c4edb8c51eef987acce643a8631a49fba091dbe2b6b3caa0e2` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/b68684f4ab5a677b1bc46fb44430543ac3bbec562baa8c1e2c819b278db39b37.jpg` | `b68684f4ab5a677b1bc46fb44430543ac3bbec562baa8c1e2c819b278db39b37` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/badfbc45cc81942ae2e013038b150c7a13cbc3fc5188c42503c614ea4c365da5.jpg` | `badfbc45cc81942ae2e013038b150c7a13cbc3fc5188c42503c614ea4c365da5` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/bb2f9c3c2faef17b12d2e6f59990f196e4c2cb9b3eb65254630ec86e64a312ad.jpg` | `bb2f9c3c2faef17b12d2e6f59990f196e4c2cb9b3eb65254630ec86e64a312ad` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/c0f352df7e8492d2d6614aeb5f797bfa8f5770b06c29a801c46285eb138e8a23.jpg` | `c0f352df7e8492d2d6614aeb5f797bfa8f5770b06c29a801c46285eb138e8a23` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/c30c4b62800b3dc6aea36285247ac7249f51f4533bce2ae2141a77c97bff62fc.jpg` | `c30c4b62800b3dc6aea36285247ac7249f51f4533bce2ae2141a77c97bff62fc` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/c7666c1bda35c37fcf57acd07e670c1a221bfbded382c02ba8a890a4f8ebb3cf.jpg` | `c7666c1bda35c37fcf57acd07e670c1a221bfbded382c02ba8a890a4f8ebb3cf` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/c8debe4a722169688711dccf9535059ea13f17844d67f97f98ec1c9537ac06e4.jpg` | `c8debe4a722169688711dccf9535059ea13f17844d67f97f98ec1c9537ac06e4` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/d36b9449e6ac9e6127aae1cb268f388b329df59a8054d7ad704cecce33b8d270.jpg` | `d36b9449e6ac9e6127aae1cb268f388b329df59a8054d7ad704cecce33b8d270` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/d3ed0b1fc1fcd310867252bc091a1e669bb5c97f23ddd4af168845c6af683d24.jpg` | `d3ed0b1fc1fcd310867252bc091a1e669bb5c97f23ddd4af168845c6af683d24` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/d4637de868d75f9e8b037e443243bc55060232f1dbdd7fbe0ecd63444f10dc67.jpg` | `d4637de868d75f9e8b037e443243bc55060232f1dbdd7fbe0ecd63444f10dc67` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/d4d2e3123dfebbb69b9cd709ea8f5e9c41ad9d399bcf8d441d426dc7996d315e.jpg` | `d4d2e3123dfebbb69b9cd709ea8f5e9c41ad9d399bcf8d441d426dc7996d315e` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/d6c94a4d75b558e5a70a53dcac905acb98ac06b56e3a03f82f3dc1c5c97101b5.jpg` | `d6c94a4d75b558e5a70a53dcac905acb98ac06b56e3a03f82f3dc1c5c97101b5` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/f059908b2f8f7a3ac2f7cf4462fa45b0d14883037adc379aaf5940a032df63ec.jpg` | `f059908b2f8f7a3ac2f7cf4462fa45b0d14883037adc379aaf5940a032df63ec` |
| `/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/run/cache/pages/f6f0e3177fcfb10d71754bf4bbd4363d6c68348b3f8b6cf1513cb43c48c4d184.jpg` | `f6f0e3177fcfb10d71754bf4bbd4363d6c68348b3f8b6cf1513cb43c48c4d184` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/artifacts/owner_sheets/recovered_crops/bsb_poly1850--2fdb06c3a8566781--s003-l0023.png` | `ca724d276b82ea0cf5c6aa9edbfa78ec43eb9ec949eb13c57e7b429ad18a2d0d` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/artifacts/owner_sheets/recovered_crops/bsb_poly1850--515c78c513c1c8c5--s002-l0063.png` | `2b24344b0c64bdc56c7abdcebe7b66e5a39fcbe2d3eb619d7ca221b3d3d10dca` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/artifacts/owner_sheets/recovered_crops/gazette_modern--0020420cfe156a73--s000-l0146.png` | `dd88311411b6bb08bd66513b70cd8b216e3528d6898e95c2bb801ae4330e818d` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/artifacts/owner_sheets/recovered_crops/gazette_modern--5ede709b65bee305--s000-l0098.png` | `1907ba3ce3b454d35385e8d867b6cdc0fbcc160518ec9b667b3584fc3d5b897a` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/artifacts/owner_sheets/recovered_crops/gazette_modern--73e4d3191f16b5e2--s000-l0091.png` | `e27fdf19080b495db96f2d349df631fc79f94f92f41c1d2c0471f4ec615ad0e1` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/artifacts/owner_sheets/recovered_crops/gazette_modern--8213d28643843855--s000-l0144.png` | `ed8ddb498282423ac44030fb5a3a464c37783c6220cd9393676d0ccfeab88275` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/artifacts/owner_sheets/recovered_crops/gazette_modern--9a7f184282a21b5e--s000-l0036.png` | `da8eb9276cd17dc8c5aff9e4735979573ae454434e1f293b854fd20a8b831e7f` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/artifacts/owner_sheets/recovered_crops/gazette_modern--b9f59878fb904d91--s000-l0034.png` | `68ecd9dc5bc20e786106915c84e7a7e5db82feabb8070cc470019fb1c7527158` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/artifacts/owner_sheets/recovered_crops/gazette_modern--c1b2194696b35bb5--s000-l0077.png` | `397549260bf041cdac6a09522d7e1f18de50f2939c90436378df61dcb4aab689` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/artifacts/owner_sheets/recovered_crops/gazette_modern--ebdc4d07ff8c4122--s000-l0265.png` | `265aca6ba29dcef55f921195d162157ed4f1b5835873303cedc39a821b373099` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/artifacts/owner_sheets/recovered_crops/kosmopolis--62ca52b56ebe780a--s005-l0034.png` | `464c03ee72bc682f6531f28134e9aee3d1e4dbf958a123c883891c9935a7105a` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/artifacts/owner_sheets/recovered_crops/kosmopolis--681a15c3d4a0cd62--s004-l0027.png` | `241cc8e1b90f2c418db83d5c6c5ba862bcaf58fb6aee7cd985bee4b9a318c77d` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/artifacts/owner_sheets/recovered_crops/kosmopolis--aaa124307e36f113--s001-l0062.png` | `fdecf37750bd9c5daf0d5ac2e3b415de517c6dce9c3457ef0615b934db3a960b` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/artifacts/owner_sheets/recovered_crops/kosmopolis--addc07a6b4eaefef--s002-l0002.png` | `bac923a713ba9b216e15f218f57114e7d21c07afcc8fc975614a7181b0a9de55` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/artifacts/owner_sheets/recovered_crops/kosmopolis--ef37f6cfdd896488--s002-l0036.png` | `4fcfb630f3a7a8cb84580da9630b54cd018a6527b8981d747dbd629e216d5d8d` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/artifacts/owner_sheets/recovered_crops/kosmopolis--ef37f6cfdd896488--s005-l0008.png` | `2d670d28672e2b55f17a93a64e526ad23fad6fc8c758056f0729514d4d27a764` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/artifacts/owner_sheets/recovered_crops/lekythos--0fc3672826ddd6b3--s000-l0033.png` | `d9b16e1066924e8c944802db900fc49f421826080dc5e55456f94e35b528675a` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/artifacts/owner_sheets/recovered_crops/lekythos--25feca8f4ab34ba0--s003-l0302.png` | `448a4cda08681906c77e215213398f8d81f83bec57a708d9a4a6b6658633e562` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/artifacts/owner_sheets/recovered_crops/lekythos--7f67b784930deef5--s003-l0071.png` | `257aebd25363bbe5cfd29a77a7745cd6798e3f7d32dca784f0cbd97496fb0bab` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-cleanup/docs/owner_sheets/inputs/label_failure_modes_coordinator.html` | `83949c6d939e4ecadfcf63dd3e1dd31e6b1a3b9d8673ce4f4f1c510018ebbf42` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/c1_results.json` | `70ebebc6aeabe20082d0df120b17899905875bb520ded6e554c85019e7b3a369` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/bsb_poly1850__poly1850__a.jsonl` | `bb34b0155a2fedb5ecf16119ff3b0c9259704209b82921b309d94dbfdcfd619c` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/bsb_poly1850__poly1850__b.jsonl` | `a305ff0cb1c528f3cf874a44b8ca646ddc81dfdf3528b45ba2e568d5585c8c6f` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/elstat__numerics_tables__a.jsonl` | `24ec030c58601212346aca2ad0430e0bc92510f51675d1db9bb65ff74c29b056` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/elstat__numerics_tables__b.jsonl` | `68b2fbcf52419bac97e20e8ee29d692750a22cf7fff2818c6bb8a708405c4e07` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/gazette_modern__modern_scanned__measured_1986_1990__a.jsonl` | `1e7ee8aa2b5d8eb9997b74d47fe1820c1492d45bdb8256005b70533af2e5dcbf` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/gazette_modern__modern_scanned__measured_1986_1990__b.jsonl` | `80cba684d944bc32f39aa399ea9cb4fcf8f0a2a6f6c756cb11aea2268c8b0bc8` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/gazette_modern__modern_scanned__probe_1982_1985__a.jsonl` | `00285a073d2b0761f2ef9e68e67bfd7c5f1a3ad573eb9a6057d927b0b0799f19` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/gazette_modern__modern_scanned__probe_1982_1985__b.jsonl` | `a46da71464637d7d9882f9d451b51e29cafc3e4b98e13337462720ef92415925` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__latin__a.jsonl` | `065638a21af405be8eb01155aec25ef4029b353761b776d3bb53a590cd092477` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__latin__b.jsonl` | `381e2fc04e277fecfa0106283faa24aebd0eb4daf10d0daee2aeb0ae6f3d8b0e` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__mixed_greek_latin__a.jsonl` | `143a990842205a9eb0abcfc2789de526447783e833e5cc74a91fdb184051ec1d` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__mixed_greek_latin__b.jsonl` | `65d71a93552edd2a47e2f3a430d98b4f1744819320e01b089718c45f1070cd69` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__poly1850__a.jsonl` | `03c25b56a08ec09dbff55f772f9e2e32f513c32324cd6af176daeda56ffe7a55` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_poly1850__poly1850__b.jsonl` | `66911e8ba2efe5ee95157fc03dc1442794802f24cd03389ad1cc3f42b38a939f` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_russian__cyrillic__a.jsonl` | `1bbd27166786ba7cef4db88d1de63c89af7ba1055f0ab27c174f5f98b0a65024` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/ia_russian__cyrillic__b.jsonl` | `bbe7f64eee81c8e449d712c0b61be89d36993771786710fee3ad6b8b5dd6f184` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/kosmopolis__poly1900__a.jsonl` | `df666004e1372da49492d956ccd58dc249909f832552e9bf36de5213ba703f00` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/kosmopolis__poly1900__b.jsonl` | `1d9706bf53dcab01815dec60f5b4d00641c5e249db47385d2aefc415adae3c9e` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/lekythos__poly1900__a.jsonl` | `6b56da235f41379f047f42fc661d00cb6a9b5a778130f2a7d55396cbf5e14f97` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/lekythos__poly1900__b.jsonl` | `38a4ac6dece9ee9db85e81e4efc137e6a91761488c82eaf1de4dee276cd3eeec` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__greek_poly__a.jsonl` | `6bdefdfa6e39ea30569141b5090d9fcac004b318827404ece1151897226181f3` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__greek_poly__b.jsonl` | `bd7148554b68746b06c9147d44ea896a16730fb4058d430bf9aab5d6434da2dd` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1850__a.jsonl` | `f6f6827e52f24dac10d20fbdb263b066bd8d0e5d5e3a208f9f980cb0a219025c` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1850__b.jsonl` | `1acb26fd507b0207146dea162e1fed32c536ccb102d78c4a99afaa5144308717` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1900__a.jsonl` | `02c100e7f289b0b6a9875a04734d2c508a8001d91328a0ceb57d8233019e16c7` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/nlg__poly1900__b.jsonl` | `0f65439b68fbcc4fc4988b4f629a70355a3f413c6bd39f3ed280914d738e6777` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/serbia__cyrillic__a.jsonl` | `68503455fd89fa5077b134913ebdde7b77e56bb419b4a9c115a06b89ccf1996b` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/verdicts/serbia__cyrillic__b.jsonl` | `283cd4026975950426f72810fe062f9b52fb2a45585ff6f0a1f25d843125066a` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/c1/yer_adjudication/table.json` | `8fdee46d91a090573896ed70755b63cf813667e101033e7cef7401a7a2a60722` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/counts.json` | `225bfeb07a1343e66caf6bfad82d46ce3a86b5121ee8e204578c848c014c356e` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/examples.jsonl` | `1eb315bf57114d79b77835bd6d218bd4a728e2c2f7ee185ec4a996ce6ce418ca` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-01-strip.png` | `e78bf4a1cbb2668b8e6900142d43d0d50d0e8c4f0020fae799ed32ffd7e684ed` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-02-strip.png` | `2f5a1a2f33a62d7bafa32142e41a585bd63bf0ec473f73bc1ccbbbf1ce489c97` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-03-strip.png` | `f0c32b6307c5e3fbe6014a5fe590a0caa670c54b2a5e2b4a44f8b0283994f893` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-04-strip.png` | `744f7948bf5716ca21d45379ed7f111a05b2a320936b959439d3b0420465ea17` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-05-strip.png` | `7e4756e3ef19ccb11e9a8effda7c7bb16fd30732ab820b6bd752524976ec30ea` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-06-strip.png` | `e28880a2d6bb8d53eb5ce386a9426ab620a3d0e91d74a802ab94cd99165aee6b` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-07-strip.png` | `0da017b9ce9aaf29126989c42184ebac2f8cb2129faff458668e9f213cad92c3` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-08-strip.png` | `9edfb4e2f270df76fee1e0a3b785275bd0edc050ac556246f5894f0fed0cbbb9` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-09-strip.png` | `3e5c7fe0406f5d14c21f4fd302de922e1641e6242eb319b4110381f1a8e82126` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-10-strip.png` | `7d2ebc3d499d75ed7140d2e419ded937741d5d6fa628604a2957b06c1c8636bb` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-11-strip.png` | `f1917d8086e272dd704f38463e63bc09be18925e4b529f30c7ec82253bef5b24` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-12-strip.png` | `f88175acc482cb1e706f5d37ea1520675354ecd7f70d3ce6c7c2e06d2ef80e74` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-13-strip.png` | `4c5c35beff8afd6118d8b8b31e1bc34955d513ddcf0988dbad6c9aa03a90e57c` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-14-strip.png` | `31a956f192a6fdc07d8ddec9be4b1d42d1716c5cef4f940ebf09a4009532015b` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-15-strip.png` | `e85b1ef25fa10ee0533db0100ff53471f510d6fa6d2cc8c148696c99bdaf6c85` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-16-strip.png` | `1f53be806f10885dcd7852e378bc57878bbb490522fe60ba867d351cfa3524a1` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-17-strip.png` | `aabc260ed49502cc3ed95cfa33cb7175e48ae798f387fd3ed89e3c5e573dc258` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-18-strip.png` | `2609a190e890b23c18dc03f4dabda35669e3e9857a7c8ba25e4bce6e32e75132` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-19-strip.png` | `01320130bc0c0f0132a8b26a8d1d795a5393ae69f93b27484532b9b45b16a2fb` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-20-strip.png` | `b633464577d8211e9d8e5fb01e6ab49c04e7e861137b5212b57ab1ab33d5d47a` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-21-strip.png` | `121829c02b53b314d39001664dceceb0d80be48bfa2881da3de14d9858e11f97` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-22-strip.png` | `4b47d030e8beedc345a9422a24b0c417472b8c0e0de2698d58c2ec9016c45281` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-23-strip.png` | `62086371c285a49b928f1d7e68f66033f9e8c12ce030a720f6ed86aee9c99ef4` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/segmentation_gallery/sg1-24-strip.png` | `94cbbec182216641a269c3bd904a09750bc1c61a1c03901c9d8e476d9e96527d` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/cards/gazette_modern_key.json` | `aa2b8abd26246e606b895722ce9790e7b01dbe1d765a71db9382cb7549b36672` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/cards/kosmopolis_key.json` | `7afa476162c5d5f1da33507d4fdbe5be007256f7fbe6f90c82242bce2b560288` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/cards/lekythos_key.json` | `248f19c167168b01def2ba6ca5c8e5c90e34ec7314615c7d854b20cbb82982ca` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/cards_kosmo_poly1850_sol_key.json` | `e9eb4a4bdf725bddd979edb97045724b39fe199f32aaeade207f6b7b7ba2231d` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/cards_probe_supplement_key.json` | `95bd614ea82cae34ed5dfd46ec897a1178a0f9d99698fbe0ab46582154ee122b` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/kosmo_poly1850_sol/answers_mapped.jsonl` | `6516a46e22ad3a3708f7ef542584da4541e04dd5f6c22b5015961a63d68d4f6c` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/gazette_modern__a.jsonl` | `952d3b0ea163c95a2b027ca56ec8ab04c471a446525b7ef1c4215d701da0945a` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/gazette_modern__b.jsonl` | `bf15d7e3283f84fc3983aa9273aacc0c26aaffb65412fc1d72b48a6353be6686` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/gazette_probe_supplement__b.jsonl` | `590a9b3a7e145be705a831d5d7e9d84fd85aff4b1fa0605aeaecd1de002663ec` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/kosmopolis__a.jsonl` | `c53ee21b25a51a2e1567f5ca1d5fdd3633a15f29b8f307b622a98d6f4eabccc3` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/kosmopolis__b.jsonl` | `593f63ef12c26abfb21a2fde2f4830b2b420d0d2cbf66994cf8da46c310f10ec` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/lekythos__a.jsonl` | `bc14ab9e16e2af8a529cdfe4660a60076b02cffc583c1452d3bc420c95e4293c` |
| `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/checks/verdicts/lekythos__b.jsonl` | `ed841f3a61d42816f77e6360ec3af735291eabb82744b37f56876b131fb19563` |

### Renderer and frozen artifacts

| Path | SHA-256 |
| --- | --- |
| `docs/records/labelfix/spellcheck/sheet_format_reference_v4.html` | `de583e3effc37a2fa299b90c0d39738480b811c27d2af5b2bc05d35b685368b6` |
| `greekocr/adjudicate/owner_sheet.py` | `e7571726007be765c1d8ae7d5db5dae4d51f53c985a02e26e7d7475bce52ac12` |
| `greekocr/adjudicate/owner_sheet.css` | `7a5524b227708925eee5c7548f053ec44e012334d5dcca7be22d2f0986913f0a` |
| `greekocr/adjudicate/owner_sheet.js` | `2f1c9b83592526f179703bdba487c299186be51786408dfc4161125b4fad65a5` |
| `docs/records/owner_sheets/failure_modes_per_class/spec.json` | `5643bf9c382f3f31af14c9aa621d5cae78c7b32cf763af495848912ff3a0b26d` |
| `docs/records/owner_sheets/segmentation_failures/spec.json` | `e38b96cc65279b962b75952fadc88b69834920040a1bc10c7e86768de2e8128f` |
| `artifacts/owner_sheets/failure_modes_per_class.html` | `56ac031155b045b764e8791e372028dc58f60f4a53747395c94fb268aa4f025b` |
| `artifacts/owner_sheets/segmentation_failures.html` | `0ce08e2538f465c72670cc7d9754c48eadb56ab7ab38c1c4c8fdcc3373464ede` |

## Validation

`/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m pytest tests/adjudicate -q`: **29 passed**. Test output: `artifacts/owner_sheets/qa/pytest.txt`. Checks cover exact re-rendering, card/spec counts, note identity, checker-detail text, printed prefill, embedded-image decoding, all image paths, reference class conformance, class/fault/rate fidelity, gap labels, selection counts, SG1 preservation, six-group order, all B strips, rotated dimensions, input hashes and recovered raster pixels. Existing adjudication and JavaScript runtime tests pass.

Live browser screenshot QA was attempted offline but unavailable: the installed Playwright package expects uncached browser revisions, and system Chrome terminates during sandboxed launch. No browser download or network fallback was used. Visible browser layout and live signed-in DB operation are therefore not claimed. The shipped CSS and runtime acceptance checks remain the format and interaction evidence.

OS1 READY: A cards 97 (sections 10, subsections 40, gaps 15); B cards 44 (groups 6); size A 7.17 MB, B 11.62 MB; tests 29 passed
