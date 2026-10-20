# SS5 agreement

Bed rows: 417; untyped: 0. Controls excluded: 20.
Flagged under amended expectations (>1 erroneous control): t02, t05.

## Controls

| Context | v1 errors | Amended errors | Flagged |
|---|---:|---:|---|
| t01 | 2/8 | 1/8 | False |
| t02 | 2/8 | 2/8 | True |
| t03 | 2/8 | 1/8 | False |
| t04 | 1/8 | 0/8 | False |
| t05 | 4/8 | 4/8 | True |

### t01: v1
- ia_poly1850--26e14cb9c90b750f--s005-l0044 (k3cc68b97d9): errors type, text; actual `{"type": "abbrev_label", "text": "minor", "crop": "ok", "rotated": "no", "detail": "it′. → it."}`; expected `{"type": "word", "accept": [], "text": ["match"], "crop": ["ok"], "rotated": "no"}`
- gazette_modern--98dfb00fa203c6d5--s000-l0048 (kc8f9695a00): errors text; actual `{"type": "punctuation", "text": "minor", "crop": "ok", "rotated": "no", "detail": "» » → 《 《"}`; expected `{"type": "punctuation", "accept": [], "text": ["wrong"], "crop": ["ok"], "rotated": "no"}`

### t01: amended
- ia_poly1850--26e14cb9c90b750f--s005-l0044 (k3cc68b97d9): errors type; actual `{"type": "abbrev_label", "text": "minor", "crop": "ok", "rotated": "no", "detail": "it′. → it."}`; expected `{"type": "word", "accept": [], "text": ["match", "minor"], "crop": ["ok"], "rotated": "no"}`

### t02: v1
- gazette_modern--aeb6eb76fc7057f0--s000-l0050 (k3886628074): errors type, text, crop; actual `{"type": "punctuation", "text": "match", "crop": "ok", "rotated": "no", "detail": ""}`; expected `{"type": "noise", "accept": [], "text": ["not_text"], "crop": ["na"], "rotated": "no"}`
- gazette_modern--fd0c55b5cf1557ca--s000-l0042 (k6310aa5428): errors type, text, crop; actual `{"type": "cut_fragment", "text": "unreadable", "crop": "clipped", "rotated": "no", "detail": ""}`; expected `{"type": "noise", "accept": ["handwriting"], "text": ["not_text", "wrong"], "crop": ["na", "ok"], "rotated": "no"}`

### t02: amended
- gazette_modern--aeb6eb76fc7057f0--s000-l0050 (k3886628074): errors type, text, crop; actual `{"type": "punctuation", "text": "match", "crop": "ok", "rotated": "no", "detail": ""}`; expected `{"type": "noise", "accept": [], "text": ["not_text"], "crop": ["na"], "rotated": "no"}`
- gazette_modern--fd0c55b5cf1557ca--s000-l0042 (k6310aa5428): errors type, text, crop; actual `{"type": "cut_fragment", "text": "unreadable", "crop": "clipped", "rotated": "no", "detail": ""}`; expected `{"type": "noise", "accept": ["handwriting"], "text": ["not_text", "wrong"], "crop": ["na", "ok"], "rotated": "no"}`

### t03: v1
- ia_greek_latin--e3dff0a8a9829e59--s006-l0026 (k3a5b10141e): errors type, text, crop; actual `{"type": "cut_fragment", "text": "unreadable", "crop": "clipped", "rotated": "no", "detail": ""}`; expected `{"type": "noise", "accept": [], "text": ["not_text"], "crop": ["na"], "rotated": "no"}`
- elstat--2b5780c7c9896a54--s000-l0051 (k94bd334c7a): errors text; actual `{"type": "caps_display", "text": "minor", "crop": "ok", "rotated": "no", "detail": "S o m m a i r e → Sommaire"}`; expected `{"type": "caps_display", "accept": ["word"], "text": ["match"], "crop": ["ok"], "rotated": "no"}`

### t03: amended
- ia_greek_latin--e3dff0a8a9829e59--s006-l0026 (k3a5b10141e): errors type, text, crop; actual `{"type": "cut_fragment", "text": "unreadable", "crop": "clipped", "rotated": "no", "detail": ""}`; expected `{"type": "noise", "accept": [], "text": ["not_text"], "crop": ["na"], "rotated": "no"}`

### t04: v1
- gazette_modern--98dfb00fa203c6d5--s000-l0048 (k7b880ceb20): errors text; actual `{"type": "punctuation", "text": "minor", "crop": "ok", "rotated": "no", "detail": "» » → 《 《"}`; expected `{"type": "punctuation", "accept": [], "text": ["wrong"], "crop": ["ok"], "rotated": "no"}`

### t04: amended
No errors.

### t05: v1
- gazette_modern--aeb6eb76fc7057f0--s000-l0050 (kbfbdf53b58): errors type, text, crop; actual `{"type": "punctuation", "text": "minor", "crop": "ok", "rotated": "no", "detail": "„ → \""}`; expected `{"type": "noise", "accept": [], "text": ["not_text"], "crop": ["na"], "rotated": "no"}`
- gazette_modern--fd0c55b5cf1557ca--s000-l0042 (ka8b8b4e4ff): errors type, text, crop; actual `{"type": "cut_fragment", "text": "unreadable", "crop": "clipped", "rotated": "no", "detail": ""}`; expected `{"type": "noise", "accept": ["handwriting"], "text": ["not_text", "wrong"], "crop": ["na", "ok"], "rotated": "no"}`
- ia_poly1850--36dcee7ce4c29f8b--s003-l0004 (k208a87850b): errors text; actual `{"type": "abbrev_label", "text": "wrong", "crop": "ok", "rotated": "no", "detail": "61 → 51"}`; expected `{"type": "abbrev_label", "accept": [], "text": ["match"], "crop": ["ok"], "rotated": "no"}`
- ia_greek_latin--e3dff0a8a9829e59--s006-l0026 (k36eaa1c1e7): errors type, text, crop; actual `{"type": "punctuation", "text": "minor", "crop": "ok", "rotated": "no", "detail": "two upper marks and one lower dot → '."}`; expected `{"type": "noise", "accept": [], "text": ["not_text"], "crop": ["na"], "rotated": "no"}`

### t05: amended
- gazette_modern--aeb6eb76fc7057f0--s000-l0050 (kbfbdf53b58): errors type, text, crop; actual `{"type": "punctuation", "text": "minor", "crop": "ok", "rotated": "no", "detail": "„ → \""}`; expected `{"type": "noise", "accept": [], "text": ["not_text"], "crop": ["na"], "rotated": "no"}`
- gazette_modern--fd0c55b5cf1557ca--s000-l0042 (ka8b8b4e4ff): errors type, text, crop; actual `{"type": "cut_fragment", "text": "unreadable", "crop": "clipped", "rotated": "no", "detail": ""}`; expected `{"type": "noise", "accept": ["handwriting"], "text": ["not_text", "wrong"], "crop": ["na", "ok"], "rotated": "no"}`
- ia_poly1850--36dcee7ce4c29f8b--s003-l0004 (k208a87850b): errors text; actual `{"type": "abbrev_label", "text": "wrong", "crop": "ok", "rotated": "no", "detail": "61 → 51"}`; expected `{"type": "abbrev_label", "accept": [], "text": ["match"], "crop": ["ok"], "rotated": "no"}`
- ia_greek_latin--e3dff0a8a9829e59--s006-l0026 (k36eaa1c1e7): errors type, text, crop; actual `{"type": "punctuation", "text": "minor", "crop": "ok", "rotated": "no", "detail": "two upper marks and one lower dot → '."}`; expected `{"type": "noise", "accept": [], "text": ["not_text"], "crop": ["na"], "rotated": "no"}`

## Stratum 1 (opus)

Exact agreement: 114/159 = 71.6981%.

Rows = mapped Opus; columns = Sol.

| Opus / Sol | abbrev_label | caps_display | cut_fragment | figure_ornament | foreign_script | handwriting | marker | multi_line | part_of_line | punctuation | roman_lower | show_through | watermark | word |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| abbrev_label | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| caps_display | 2 | 33 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| cut_fragment | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| figure_ornament | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| foreign_script | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| handwriting | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| noise | 0 | 0 | 2 | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 2 | 0 | 0 |
| part_of_line | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 22 | 5 | 0 | 0 | 0 | 0 | 0 |
| punctuation | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 12 | 0 | 0 | 0 | 0 |
| roman_lower | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 |
| show_through | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| watermark | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| word | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 39 |

### Disagreements

| line_id | Opus | Sol | Google text |
|---|---|---|---|
| bsb_poly1850--027215cc6d2a7e8a--s009-l0001 | word | caps_display | Kede |
| bsb_poly1850--2032df1e3e983f1d--s005-l0029 | caps_display | figure_ornament | PAEONIA |
| bsb_poly1850--3496ab66cde251ee--s005-l0112 | part_of_line | multi_line | deles |
| bsb_poly1850--91657e0569fe07c8--s004-l0039 | abbrev_label | word | 68. For- |
| bsb_poly1850--b05b8313ad5d52e2--s007-l0015 | abbrev_label | word | data 1660. |
| bsb_poly1850--d7db5a3b1eb289a3--s006-l0029 | cut_fragment | word | νὴ τοὺς δ. |
| elstat--df38bce62200e7db--s000-l0029 | word | cut_fragment | Καλλιερ |
| gazette_modern--2f132c63d32e7b5a--s000-l0110 | caps_display | cut_fragment | ΘΥΝΗΣ». |
| gazette_modern--37ed2e85ffdd5592--s000-l0067 | part_of_line | multi_line | γ & β, |
| gazette_modern--37ed2e85ffdd5592--s000-l0073 | part_of_line | multi_line | γ & β. |
| gazette_modern--49b793056935d163--s000-l0043 | noise | cut_fragment | דוד דר |
| gazette_modern--5d57a0a85aede133--s000-l0015 | part_of_line | handwriting | " του |
| gazette_modern--6c02a5264ac1b8a3--s000-l0231 | caps_display | abbrev_label | ΕΠΕ |
| gazette_modern--9a06f5aaa5be314f--s000-l0379 | part_of_line | multi_line | πιθανη |
| gazette_modern--affc069208f11f21--s000-l0038 | caps_display | cut_fragment | ΥΛΙΚΑ |
| gazette_modern--b21451311e269f58--s000-l0001 | noise | punctuation | سے |
| gazette_modern--b7877bdaa2fcf7f5--s000-l0029 | part_of_line | multi_line | ΕΤΑΙ- |
| gazette_modern--c90fa267aa2e4dd4--s000-l0083 | part_of_line | multi_line | Γεωργίου |
| gazette_modern--dc95e9d95cc9cb8e--s000-l0107 | part_of_line | multi_line | κόστους |
| gazette_modern--f4a16fe9302ade1e--s000-l0171 | caps_display | figure_ornament | ΟΔΟΣ |
| gazette_modern--f4a16fe9302ade1e--s000-l0297 | noise | handwriting | - Sarkeds a |
| gazette_modern--fd6caa884236f7dc--s000-l0118 | noise | cut_fragment | A |
| ia_poly1850--36dcee7ce4c29f8b--s000-l0061 | noise | marker | t |
| ia_poly1850--3cbcc415675468a9--s003-l0065 | noise | show_through | CA |
| ia_poly1850--3cbcc415675468a9--s034-l0001 | noise | show_through | MELA OF 10 |
| ia_poly1850--63f57af8d450f3e8--s034-l0019 | part_of_line | multi_line | ἐστιν |
| ia_poly1850--a89bd2c9bdb1ca6d--s008-l0021 | word | abbrev_label | vἱῷ om. C |
| kosmopolis--86098eebf5207e79--s003-l0041 | part_of_line | multi_line | στὴν |
| kosmopolis--91040f2da70b9ae0--s004-l0004 | part_of_line | multi_line | ᾿Απὸ |
| kosmopolis--9a17c86798d2c74a--s000-l0030 | part_of_line | multi_line | , ποῦ |
| kosmopolis--9a17c86798d2c74a--s003-l0012 | part_of_line | multi_line | ” καὶ |
| kosmopolis--9a17c86798d2c74a--s007-l0035 | part_of_line | multi_line | νὰ ξε- |
| kosmopolis--acb323b6cb8d169d--s004-l0035 | part_of_line | multi_line | Σιγά- |
| kosmopolis--ecc23d7812913d0a--s006-l0039 | part_of_line | multi_line | ...» |
| lekythos--0fc3672826ddd6b3--s001-l0023 | part_of_line | multi_line | βιβλία |
| lekythos--3bfc4a385d61b883--s002-l0012 | figure_ornament | multi_line | Longine |
| lekythos--456def1ccfc2283e--s002-l0164 | part_of_line | multi_line | , τὸ πρό- |
| lekythos--49c082ba27aa27da--s000-l0046 | part_of_line | multi_line | Η του |
| lekythos--49c082ba27aa27da--s000-l0241 | part_of_line | multi_line | μὲ τὰ |
| lekythos--7f67b784930deef5--s004-l0020 | part_of_line | multi_line | σας μία |
| lekythos--dcfa99599048d352--s000-l0001 | show_through | caps_display | HVED !!-8 |
| lekythos--dcfa99599048d352--s000-l0105 | part_of_line | multi_line | Κάτω ΒΟΛΟΥ |
| nlg--1144074169f43992--s021-l0010 | part_of_line | multi_line | τί ἄλλο |
| nlg--6146c0455e0103d2--s003-l0011 | caps_display | abbrev_label | Ν. Φ. |
| serbia--b6450341d87fb144--s000-l0005 | cut_fragment | handwriting | Mi |

## Opus mapping

- word_or_phrase → word
- heading_caps_display → caps_display
- abbreviation_reference_label → abbrev_label
- roman_numeral_lowercase → roman_lower
- punctuation_only → punctuation
- noise_non_text → noise
- handwriting → handwriting
- foreign_script_printed → foreign_script
- map_figure_ornament_logo → figure_ornament
- scan_watermark → watermark
- show_through_mirrored → show_through
- cut_fragment → cut_fragment
- multi_line_crop → multi_line
- text_covers_part_of_crop → part_of_line
Unmapped types (kept verbatim): []

## Prompt provenance

- t01: `prompts_rendered/t01.md` SHA256 `e5eea978d0c9bef0076f88c21d819d2450fcea1a1f615d02b18f14236b37fcb9`
- t02: `prompts_rendered/t02.md` SHA256 `e5eea978d0c9bef0076f88c21d819d2450fcea1a1f615d02b18f14236b37fcb9`
- t03: `prompts_rendered/t03.md` SHA256 `e5eea978d0c9bef0076f88c21d819d2450fcea1a1f615d02b18f14236b37fcb9`
- t04: `prompts_rendered/t04.md` SHA256 `f13912640ad39a5f0ea03007f80279a57df6516bb5b498cddc194f2efe838ccb`
- t05: `prompts_rendered/t05.md` SHA256 `e5eea978d0c9bef0076f88c21d819d2450fcea1a1f615d02b18f14236b37fcb9`

t04 rerun adds only the environment restrictions shown below. Original and amended prompts are preserved.
```diff
--- prompts_rendered/type2/t04.md (original)
+++ prompts_rendered/t04.md (environment amendment)
@@ -5,9 +5,10 @@
 - See an image with the view_image tool. View cards in small groups (about 5 to 10 images per tool call) rather than one per call.
 - Give view_image literal relative paths only, written out in full (e.g. `zoom/group01.png`, `img/<name>.png`). Never build an image path from `pwd`, an absolute path, a variable or a loop.
 - Write every zoom image once, under a new name; never overwrite or delete a file in ./zoom/.
+- Use only these ImageMagick operations: `-filter point`, `-resize`, and `montage` / `-append` / `+append` to tile crops. Do not use `-rotate` or any other transform: judge rotation by eye.
 - Use no absolute path anywhere, fonts included: if you label a montage, give ImageMagick a font name (e.g. `-font Helvetica`), not a font file path.
 - ImageMagick (`magick`) is installed. Put enlargements only in ./zoom/.
-- Write files with shell commands (a heredoc or a short Python script that writes text), only inside this folder.
+- Write files with shell commands (a heredoc or a short Python script that writes text), only inside this folder. The only files you may create are ./answers.jsonl and images under ./zoom/; run any helper code inline (heredoc), never save it as a file.
 - There is no network and no web search.
 
 # Protocol
```

## Control amendments

[
  {
    "date": "2026-10-19 16:05",
    "by": "lead",
    "line_id": "gazette_modern--98dfb00fa203c6d5--s000-l0048",
    "change": "text ['wrong'] -> ['wrong','minor']",
    "reason": "the prompt defines minor as letters right but a punctuation sign differs; printed » » read as 《 《 is minor under that definition"
  },
  {
    "date": "2026-10-19 16:05",
    "by": "lead",
    "line_id": "ia_poly1850--26e14cb9c90b750f--s005-l0044",
    "change": "text ['match'] -> ['match','minor']",
    "reason": "re-checked pixels: a small tick between t and the full stop is visible; minor is defensible. type stays word"
  },
  {
    "date": "2026-10-19 16:12",
    "by": "lead",
    "line_id": "elstat--2b5780c7c9896a54--s000-l0051",
    "change": "text ['match'] -> ['match','minor']",
    "reason": "letter-spaced 'S o m m a i r e' read as 'Sommaire': the prompt defines a differing space as minor"
  }
]

## Void evidence (never merged)

- answers/t01.run1_VOID.jsonl
- answers/t01.run1_VOID.scan.json
- answers/t01.run2_VOID.jsonl
- answers/t01.run2_VOID.scan.json
- answers/t04.run1_VOID.check.json
- answers/t04.run1_VOID.jsonl
- answers/t04.run1_VOID.mapped.jsonl
- answers/t04.run1_VOID.scan.json
- answers/t04.run2_VOID.jsonl
- answers/t04.run2_VOID.scan.json

## Method notes

No reading runs or crop judgments performed.
sample.jsonl includes 20 distinct controls: excluded from bed output.
Sol rotated replaces the sample rotated field; original sample value preserved as sample_rotated.
Opus types in typing.jsonl are mapped codes; originals also preserved.
Group C: ceil(10% of remainder), random.Random(20261019), candidates sorted by line_id.
