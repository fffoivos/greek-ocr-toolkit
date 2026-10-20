# MIR1: mirrored ink diagnosis

Cause: **showthrough**. The retained spread contains normal foreground advertising and a reversed text layer. The witness isolates the reversed layer. Neither the whole raster nor crop extraction is horizontally flipped. Here, showthrough describes the visible verso-like ink: the raster alone cannot distinguish optical bleed-through, physical offset, or an upstream compositing defect.

No network calls, collector execution, run-root writes, locks, exclusions, staging or commits. Regenerated crops used only the mandated collector .venv/bin/python, writing to /tmp and this report directory. Existing unrelated working-tree files were left alone.

## Witness

Page lekythos--dcfa99599048d352--s000 is PDF page 23 of 23, item c058c46d-65bc-4cb9-990a-d09ee38d2de5. Native raster: 2630 × 1972.

| Evidence | SHA-256 |
|---|---|
| Retained JPEG, independently verified | 6a2738f7bf0d118fa415da34b54fb44910f1494c9b673806918fb03e29ecddf3 |
| Saved Google response, independently verified | fcf8b0ba79841d1e765df3f1733b4bc23434eeda8945dce0721d2737dcd42c30 |
| Downloaded PDF, receipt only; not retained | 9e52155ae9001c4a0f014fef9b724cd92c49ac3584ccd87a317711442a7e2405 |
| Regenerated witness PNG, equals feature receipt | 3f8ca90c627644f3aded75f6392fbc97d43f603c4695e51cde42f94a7b2817ca |

The line bbox is [1468,1766,1879,1786]; crop_bbox is [1466,1764,1881,1788], exactly two pixels padding. Google dimensions match native dimensions. There is no page transforms field. Page, line and all seven tokens are PAGE_UP. No recorded mirror correction or detection exists for this witness.

Viewed the whole retained raster and rows l0001, l0022, l0050, l0100, l0143, l0144, l0145 and l0146. Normal bank/cognac advertising coexists with reversed lettering across titles and body text. l0143 contains normal foreground ΚΑΜΕΤΟΚΟΝ 5% and reversed background. l0144 is reversed throughout. A diagnostic horizontal reflection reveals the reported opening-hours text, Ἀνοικτόν 8.30-1 καὶ 3-7.30 μ.μ. The reflection is evidence only, not a replacement crop. All eight sampled crops regenerate byte-for-byte from their feature receipts.

![Native row samples](evidence/mir1_witness_rows.png)

![Native witness above; diagnostic reflection below](evidence/mir1_witness_flip.png)

The reported correct Google label is **not present in the supplied saved response**. Raw Google anchor [4003,4037) reads “.٤-٥٤.٢ در بد x 1-08.8 κόσκιον Α΄” plus newline; the W1 label has the same garbling. Google geometry locates the correct reversed-ink region, not a different normally oriented line. The witness already has candidate_usable=false and usable_final=false, with low_confidence, symbol_heavy and foreign_script rejection reasons.

The second signal hit on this page, l0106, has normal target text with strong reversed background. Showthrough affects more of the spread than these two hits; the exact affected-row population is unknown. One mirrored target row and one contaminated normal target row are visually established here.

## Collector route

Read code in /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect. [provenance.json](provenance.json) records code hashes and stored W1/W2 identities. Current pipeline.py and reader.py hashes match both recorded run recipes.

1. collect_v3/routes/providers.py, Routes.pdf/resolve: download and hash the direct Lekythos PDF. Receipt URL: https://lekythos.library.ucy.ac.cy/archive/download/c058c46d-65bc-4cb9-990a-d09ee38d2de5.pdf. No network request was made in MIR1.
2. Routes.fetch: select page 23; PDFium render at min(200/72,3500/max(w,h)), grayscale; convert to L, thumbnail to 3500 maximum, JPEG quality 92. No explicit horizontal flip. A reversed embedded image/PDF matrix or pre-existing scanned ink could enter from the source. The original PDF was evicted, so its image objects were not inspected. A simple whole-render reflection cannot explain simultaneous normal and reversed layers.
3. collect_v3/reader.py: submit the retained JPEG to Document AI. strip_response removes embedded image/content, retaining response geometry and transforms. OCR may garble reflected glyphs/order; it does not rewrite crop pixels.
4. greekocr/harvest/page_reads.py, _response_geometry: invert recorded Google transforms for native boxes, if present. None exist on this witness, so native geometry passes through. This changes coordinates, not ink.
5. collect_v3/pipeline.py, analyse: verify raster hash, open retained image, convert to L, pad bbox, image.crop, PNG encoding. collect_v3/storage.py, ensure_crop uses the same regeneration. Neither reflects pixels. Independent byte-exact regeneration rules out a crop-only flip.

The defect is present before cropping. Evidence favors verso-like showthrough; it does not establish exactly when that physical reversed layer arose upstream.

## Detection signal and limits

Use saved Google tokens overlapping each line's text-anchor intervals, ordered by text-anchor start. Compute token x-centres as mean polygon vertex x. Flag a row when the line and all its tokens are PAGE_UP and **at least two adjacent x-centre decreases** occur. This threshold was calibrated on the witness, not independently qualified.

Witness x-centres: [1542,1511,1484,1658.5,1717,1809,1864], giving two decreases. Most tokens still run left to right: the signal detects an OCR ordering anomaly, not reflected glyph shapes. Duplicate tokens, mixed RTL text and OCR/line assembly errors yield false positives. Single-token mirrors or mirrored text recognized in left-to-right order can be missed. Recall and the total mirrored population are unknown.

Every completed response page in this snapshot is PAGE_UP, including the witness, so page orientation has no discrimination. Transform fields occur on 30 W1 and 56 W2 pages; their presence is not a mirror signal, and the witness has none. Other line orientations are rotations, not proof of reflection. No generic orientation/transform signal tested here detects the witness.

For compacted W2 pages, enumerate raw Google lines using the collector's page_id-lNNNN numbering without calling analyse. Signal geometry is in Google's reported frame. For compacted candidate diagnostic boxes only, invert any recorded transforms and add two pixels padding; these are not claimed byte-exact historical crops. Usability flags are unknown for 29 compacted W2 candidates.


## Snapshot coverage

Frozen filename inventory: 1370 W1 and 2222 W2 page records. Only status=completed records were scanned. Final pass: 2026-10-17T15:39:30.234819+00:00 to 2026-10-17T15:40:33.836920+00:00. This bounds a live-run snapshot, not subsequent W2 progress.

Scanned 101,098 W1 rows on 1354 completed pages and 131,007 W2 rows on 2183 completed pages, including completed textless pages with zero rows. W1 feature counts matched raw Google line counts for every page. All scanned responses matched their page-record SHA-256; no read/parse/hash errors. Noncompleted records (16 W1, 39 W2) and later page files are outside scope.

| Tranche | Source | Scanned pages | Scanned rows | Candidate pages | Candidate rows |
|---|---|---:|---:|---:|---:|
| W1 | bsb_poly1850 | 199 | 12774 | 1 | 1 |
| W1 | elstat | 12 | 5044 | 0 | 0 |
| W1 | gazette_modern | 234 | 29514 | 17 | 18 |
| W1 | ia_greek_latin | 197 | 11755 | 1 | 1 |
| W1 | ia_poly1850 | 315 | 16022 | 4 | 4 |
| W1 | ia_russian | 80 | 2963 | 0 | 0 |
| W1 | kosmopolis | 120 | 5356 | 0 | 0 |
| W1 | lekythos | 58 | 13407 | 1 | 2 |
| W1 | nlg | 80 | 2220 | 0 | 0 |
| W1 | serbia | 59 | 2043 | 0 | 0 |
| W2 | bsb_poly1850 | 298 | 20316 | 1 | 1 |
| W2 | elstat | 47 | 14835 | 1 | 1 |
| W2 | gazette_modern | 276 | 30659 | 31 | 41 |
| W2 | ia_poly1850 | 1008 | 48454 | 14 | 27 |
| W2 | nlg | 320 | 9889 | 0 | 0 |
| W2 | serbia | 234 | 6854 | 0 | 0 |

96 candidate rows on 71 pages: 26 W1 rows on 24 pages; 70 W2 rows on 47 pages. These are review hits, not confirmed mirrors.

## Visual validation

Exactly 10 candidate rows viewed, selected purposively as recorded in validation.json. Mirrored-target precision is **1/10 (10%)**. Including any reversed background changes the endpoint to 2/10. This is not a random sample or a corpus-wide precision estimate.

| # | Candidate ID | Mirrored target? | Observation |
|---:|---|---|---|
| 1 | lekythos--dcfa99599048d352--s000-l0144 | confirmed | Confirmed mirrored target: isolated verso opening-hours line. |
| 2 | lekythos--dcfa99599048d352--s000-l0106 | rejected | Normal target plus reversed background: contamination, not mirrored target. |
| 3 | bsb_poly1850--2fdb06c3a8566781--s006-l0040 | rejected | Normal Greek; duplicated OCR words/order. |
| 4 | ia_greek_latin--7156a8b65e724719--s006-l0032 | rejected | Normal Latin/Greek; duplicated OCR words/order. |
| 5 | ia_poly1850--5aa15e93b2f445b8--s007-l0009 | rejected | Normal Latin with Hebrew sigla; mixed direction and OCR order. |
| 6 | ia_poly1850--63f57af8d450f3e8--s003-l0004 | rejected | Normal Greek; duplicated OCR words/order. |
| 7 | ia_poly1850--63f57af8d450f3e8--s007-l0016 | rejected | Normal Greek; duplicated OCR words/order and multi-row crop. |
| 8 | gazette_modern--0c58c25dc3c24651--s000-l0120 | rejected | Normal Gazette heading; token order anomaly. |
| 9 | gazette_modern--00b75ade31420203--s000-l0066 | rejected | Normal Gazette heading; token order anomaly. |
| 10 | gazette_modern--0443b880ddd5023a--s000-l0005 | rejected | Normal Gazette heading; token order anomaly. |

![Ten viewed candidates, native orientation](evidence/viewed_candidates.png)

## Counts per candidate page and complete IDs

Every other scanned completed page has zero hits under this signal. Full geometry, labels and centres: [scan.json](scan.json). Machine-readable IDs: [candidates.tsv](candidates.tsv).

| Tranche | Source | Page | Rows | Candidate IDs |
|---|---|---|---:|---|
| W1 | bsb_poly1850 | bsb_poly1850--2fdb06c3a8566781--s006 | 1 | bsb_poly1850--2fdb06c3a8566781--s006-l0040 |
| W1 | gazette_modern | gazette_modern--0c58c25dc3c24651--s000 | 1 | gazette_modern--0c58c25dc3c24651--s000-l0120 |
| W1 | gazette_modern | gazette_modern--226fc72ced3f17a7--s000 | 1 | gazette_modern--226fc72ced3f17a7--s000-l0073 |
| W1 | gazette_modern | gazette_modern--3547657ffefe84da--s000 | 1 | gazette_modern--3547657ffefe84da--s000-l0068 |
| W1 | gazette_modern | gazette_modern--39bf5b1f2419153f--s000 | 1 | gazette_modern--39bf5b1f2419153f--s000-l0008 |
| W1 | gazette_modern | gazette_modern--500e57f76200fd06--s000 | 1 | gazette_modern--500e57f76200fd06--s000-l0071 |
| W1 | gazette_modern | gazette_modern--73e4d3191f16b5e2--s000 | 1 | gazette_modern--73e4d3191f16b5e2--s000-l0043 |
| W1 | gazette_modern | gazette_modern--85ae65d5c3623bbc--s000 | 1 | gazette_modern--85ae65d5c3623bbc--s000-l0019 |
| W1 | gazette_modern | gazette_modern--9a14c15a9272a074--s000 | 1 | gazette_modern--9a14c15a9272a074--s000-l0061 |
| W1 | gazette_modern | gazette_modern--9a7f184282a21b5e--s000 | 1 | gazette_modern--9a7f184282a21b5e--s000-l0321 |
| W1 | gazette_modern | gazette_modern--9aa572190ac3f790--s000 | 1 | gazette_modern--9aa572190ac3f790--s000-l0140 |
| W1 | gazette_modern | gazette_modern--a5e1de6186794c51--s000 | 1 | gazette_modern--a5e1de6186794c51--s000-l0011 |
| W1 | gazette_modern | gazette_modern--b45c6f04968613c9--s000 | 1 | gazette_modern--b45c6f04968613c9--s000-l0260 |
| W1 | gazette_modern | gazette_modern--d837e6d93bcd94ad--s000 | 1 | gazette_modern--d837e6d93bcd94ad--s000-l0003 |
| W1 | gazette_modern | gazette_modern--ebdc4d07ff8c4122--s000 | 1 | gazette_modern--ebdc4d07ff8c4122--s000-l0282 |
| W1 | gazette_modern | gazette_modern--f4a16fe9302ade1e--s000 | 2 | gazette_modern--f4a16fe9302ade1e--s000-l0159<br>gazette_modern--f4a16fe9302ade1e--s000-l0276 |
| W1 | gazette_modern | gazette_modern--f95d1e58b1b2e444--s000 | 1 | gazette_modern--f95d1e58b1b2e444--s000-l0071 |
| W1 | gazette_modern | gazette_modern--fa44436c17488653--s000 | 1 | gazette_modern--fa44436c17488653--s000-l0018 |
| W1 | ia_greek_latin | ia_greek_latin--7156a8b65e724719--s006 | 1 | ia_greek_latin--7156a8b65e724719--s006-l0032 |
| W1 | ia_poly1850 | ia_poly1850--5aa15e93b2f445b8--s007 | 1 | ia_poly1850--5aa15e93b2f445b8--s007-l0009 |
| W1 | ia_poly1850 | ia_poly1850--63f57af8d450f3e8--s003 | 1 | ia_poly1850--63f57af8d450f3e8--s003-l0004 |
| W1 | ia_poly1850 | ia_poly1850--63f57af8d450f3e8--s007 | 1 | ia_poly1850--63f57af8d450f3e8--s007-l0016 |
| W1 | ia_poly1850 | ia_poly1850--f806d3f10b2ecf9c--s006 | 1 | ia_poly1850--f806d3f10b2ecf9c--s006-l0243 |
| W1 | lekythos | lekythos--dcfa99599048d352--s000 | 2 | lekythos--dcfa99599048d352--s000-l0106<br>lekythos--dcfa99599048d352--s000-l0144 |
| W2 | bsb_poly1850 | bsb_poly1850--d7db5a3b1eb289a3--s031 | 1 | bsb_poly1850--d7db5a3b1eb289a3--s031-l0025 |
| W2 | elstat | elstat--2b5780c7c9896a54--s000 | 1 | elstat--2b5780c7c9896a54--s000-l0019 |
| W2 | gazette_modern | gazette_modern--00b75ade31420203--s000 | 1 | gazette_modern--00b75ade31420203--s000-l0066 |
| W2 | gazette_modern | gazette_modern--0443b880ddd5023a--s000 | 1 | gazette_modern--0443b880ddd5023a--s000-l0005 |
| W2 | gazette_modern | gazette_modern--04bef514aeb4f76a--s000 | 1 | gazette_modern--04bef514aeb4f76a--s000-l0002 |
| W2 | gazette_modern | gazette_modern--13a9303cfc83a9d4--s000 | 2 | gazette_modern--13a9303cfc83a9d4--s000-l0002<br>gazette_modern--13a9303cfc83a9d4--s000-l0056 |
| W2 | gazette_modern | gazette_modern--18adba05af49e1fa--s000 | 1 | gazette_modern--18adba05af49e1fa--s000-l0077 |
| W2 | gazette_modern | gazette_modern--2930d466114d88f5--s000 | 3 | gazette_modern--2930d466114d88f5--s000-l0206<br>gazette_modern--2930d466114d88f5--s000-l0213<br>gazette_modern--2930d466114d88f5--s000-l0214 |
| W2 | gazette_modern | gazette_modern--323fe973e2a51073--s000 | 1 | gazette_modern--323fe973e2a51073--s000-l0129 |
| W2 | gazette_modern | gazette_modern--47f5faa35e95a12d--s000 | 1 | gazette_modern--47f5faa35e95a12d--s000-l0065 |
| W2 | gazette_modern | gazette_modern--502aff4f6f3bc82f--s000 | 6 | gazette_modern--502aff4f6f3bc82f--s000-l0079<br>gazette_modern--502aff4f6f3bc82f--s000-l0080<br>gazette_modern--502aff4f6f3bc82f--s000-l0081<br>gazette_modern--502aff4f6f3bc82f--s000-l0082<br>gazette_modern--502aff4f6f3bc82f--s000-l0083<br>gazette_modern--502aff4f6f3bc82f--s000-l0091 |
| W2 | gazette_modern | gazette_modern--59d9ae63687ecfed--s000 | 1 | gazette_modern--59d9ae63687ecfed--s000-l0177 |
| W2 | gazette_modern | gazette_modern--5af8ec79636483db--s000 | 1 | gazette_modern--5af8ec79636483db--s000-l0025 |
| W2 | gazette_modern | gazette_modern--6ca6968cbe486c9d--s000 | 1 | gazette_modern--6ca6968cbe486c9d--s000-l0096 |
| W2 | gazette_modern | gazette_modern--768a3c264664aacb--s000 | 1 | gazette_modern--768a3c264664aacb--s000-l0004 |
| W2 | gazette_modern | gazette_modern--82115ca04c55f5b7--s000 | 1 | gazette_modern--82115ca04c55f5b7--s000-l0077 |
| W2 | gazette_modern | gazette_modern--854ed646d8a88ed0--s000 | 1 | gazette_modern--854ed646d8a88ed0--s000-l0006 |
| W2 | gazette_modern | gazette_modern--96001c188e85e2c2--s000 | 2 | gazette_modern--96001c188e85e2c2--s000-l0006<br>gazette_modern--96001c188e85e2c2--s000-l0012 |
| W2 | gazette_modern | gazette_modern--98868444c7c5ea2e--s000 | 1 | gazette_modern--98868444c7c5ea2e--s000-l0039 |
| W2 | gazette_modern | gazette_modern--99b9287917de8ddc--s000 | 1 | gazette_modern--99b9287917de8ddc--s000-l0047 |
| W2 | gazette_modern | gazette_modern--9c87f4f86d30385e--s000 | 1 | gazette_modern--9c87f4f86d30385e--s000-l0081 |
| W2 | gazette_modern | gazette_modern--a426e6eea7b8e321--s000 | 1 | gazette_modern--a426e6eea7b8e321--s000-l0097 |
| W2 | gazette_modern | gazette_modern--b7b28ede97bb63c5--s000 | 1 | gazette_modern--b7b28ede97bb63c5--s000-l0015 |
| W2 | gazette_modern | gazette_modern--bfec7e90c86c19fa--s000 | 1 | gazette_modern--bfec7e90c86c19fa--s000-l0065 |
| W2 | gazette_modern | gazette_modern--c6d7fe0f3b197663--s000 | 1 | gazette_modern--c6d7fe0f3b197663--s000-l0069 |
| W2 | gazette_modern | gazette_modern--d25a07d091eda9ed--s000 | 1 | gazette_modern--d25a07d091eda9ed--s000-l0033 |
| W2 | gazette_modern | gazette_modern--dc5f54c77a3b42b7--s000 | 1 | gazette_modern--dc5f54c77a3b42b7--s000-l0028 |
| W2 | gazette_modern | gazette_modern--dccd3b8f3873e205--s000 | 2 | gazette_modern--dccd3b8f3873e205--s000-l0001<br>gazette_modern--dccd3b8f3873e205--s000-l0082 |
| W2 | gazette_modern | gazette_modern--df5a370d8f003110--s000 | 1 | gazette_modern--df5a370d8f003110--s000-l0064 |
| W2 | gazette_modern | gazette_modern--f167c80b87fe4fd0--s000 | 1 | gazette_modern--f167c80b87fe4fd0--s000-l0069 |
| W2 | gazette_modern | gazette_modern--f58e810550ff9ca9--s000 | 1 | gazette_modern--f58e810550ff9ca9--s000-l0100 |
| W2 | gazette_modern | gazette_modern--f7c662f1f1d38750--s000 | 1 | gazette_modern--f7c662f1f1d38750--s000-l0043 |
| W2 | gazette_modern | gazette_modern--fc7c47be408bb952--s000 | 1 | gazette_modern--fc7c47be408bb952--s000-l0174 |
| W2 | ia_poly1850 | ia_poly1850--09f9190274fc82bd--s024 | 2 | ia_poly1850--09f9190274fc82bd--s024-l0004<br>ia_poly1850--09f9190274fc82bd--s024-l0007 |
| W2 | ia_poly1850 | ia_poly1850--174d84a441d69a70--s022 | 5 | ia_poly1850--174d84a441d69a70--s022-l0026<br>ia_poly1850--174d84a441d69a70--s022-l0027<br>ia_poly1850--174d84a441d69a70--s022-l0028<br>ia_poly1850--174d84a441d69a70--s022-l0038<br>ia_poly1850--174d84a441d69a70--s022-l0039 |
| W2 | ia_poly1850 | ia_poly1850--174d84a441d69a70--s030 | 8 | ia_poly1850--174d84a441d69a70--s030-l0006<br>ia_poly1850--174d84a441d69a70--s030-l0027<br>ia_poly1850--174d84a441d69a70--s030-l0031<br>ia_poly1850--174d84a441d69a70--s030-l0036<br>ia_poly1850--174d84a441d69a70--s030-l0037<br>ia_poly1850--174d84a441d69a70--s030-l0046<br>ia_poly1850--174d84a441d69a70--s030-l0047<br>ia_poly1850--174d84a441d69a70--s030-l0054 |
| W2 | ia_poly1850 | ia_poly1850--36dcee7ce4c29f8b--s024 | 1 | ia_poly1850--36dcee7ce4c29f8b--s024-l0067 |
| W2 | ia_poly1850 | ia_poly1850--36dcee7ce4c29f8b--s031 | 1 | ia_poly1850--36dcee7ce4c29f8b--s031-l0123 |
| W2 | ia_poly1850 | ia_poly1850--36dcee7ce4c29f8b--s037 | 1 | ia_poly1850--36dcee7ce4c29f8b--s037-l0100 |
| W2 | ia_poly1850 | ia_poly1850--5aa15e93b2f445b8--s036 | 1 | ia_poly1850--5aa15e93b2f445b8--s036-l0041 |
| W2 | ia_poly1850 | ia_poly1850--63f57af8d450f3e8--s008 | 1 | ia_poly1850--63f57af8d450f3e8--s008-l0011 |
| W2 | ia_poly1850 | ia_poly1850--63f57af8d450f3e8--s009 | 1 | ia_poly1850--63f57af8d450f3e8--s009-l0010 |
| W2 | ia_poly1850 | ia_poly1850--63f57af8d450f3e8--s019 | 2 | ia_poly1850--63f57af8d450f3e8--s019-l0026<br>ia_poly1850--63f57af8d450f3e8--s019-l0027 |
| W2 | ia_poly1850 | ia_poly1850--63f57af8d450f3e8--s034 | 1 | ia_poly1850--63f57af8d450f3e8--s034-l0039 |
| W2 | ia_poly1850 | ia_poly1850--c3f3a531e277da9a--s025 | 1 | ia_poly1850--c3f3a531e277da9a--s025-l0020 |
| W2 | ia_poly1850 | ia_poly1850--e6e379cb4b1d54af--s025 | 1 | ia_poly1850--e6e379cb4b1d54af--s025-l0005 |
| W2 | ia_poly1850 | ia_poly1850--ebcfd6056abfa776--s019 | 1 | ia_poly1850--ebcfd6056abfa776--s019-l0014 |

## Recommended rule

Recommend row-level class **mirrored_ink**: exclude only a visually confirmed row whose target ink is horizontally reflected, including a showthrough-only line. Use a separate showthrough_contamination review class when normal target text overlaps reversed background. Do not exclude the entire page or automatically exclude token-order candidates: 9/10 viewed fail the mirrored-target criterion. No metadata-only automatic exclusion was qualified. Do not silently flip crops while retaining labels: the witness label is wrong too. No exclusion or production policy was written.

## Guarded commit list

Allow only these nine report/diagnostic files:

- docs/records/harvest/recut_v1/w1_masked/mirror/MIR1.md
- docs/records/harvest/recut_v1/w1_masked/mirror/scan.py
- docs/records/harvest/recut_v1/w1_masked/mirror/scan.json
- docs/records/harvest/recut_v1/w1_masked/mirror/candidates.tsv
- docs/records/harvest/recut_v1/w1_masked/mirror/validation.json
- docs/records/harvest/recut_v1/w1_masked/mirror/provenance.json
- docs/records/harvest/recut_v1/w1_masked/mirror/evidence/mir1_witness_rows.png
- docs/records/harvest/recut_v1/w1_masked/mirror/evidence/mir1_witness_flip.png
- docs/records/harvest/recut_v1/w1_masked/mirror/evidence/viewed_candidates.png

Before a future commit, inspect status and the exact staged path list, stage only the nine paths, reject unrelated pre-existing staged files, and use the repository's guarded commit workflow. No broad staging, run-root files, exclusions, collector code, or unrelated untracked artifacts belong in this commit. No staging or commit attempted.

Reproduce with the mandated collector interpreter and scan.py. It reads the frozen filename inventory from scan.json and rewrites only this directory's scan output. Preserve the current receipt first when rerunning against a changed live run; completed status is evaluated at read time. Existing rows are used when present; compacted W2 rows are enumerated from saved Google responses. No collector materialization is invoked.

MIR1: done | cause: showthrough | candidates: 96 rows on 71 pages | signal precision on viewed: 1/10 | recommended rule: visually_confirmed_mirrored_ink
