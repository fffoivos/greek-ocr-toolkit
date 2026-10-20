# N1-S: numeric separator glyph-pass score

Calibration: 82/82 PASS. **4/7 contexts VALID; 319 valid bed slots**. VOID: ctx04, ctx05, ctx07; 239 bed answers excluded and listed in `artifacts/n1/N1S_REREAD.json` for a fresh-order re-read. No reading run or rule fitting was performed.

## Context gate

| Context | Controls | Wrong | Abstain | Bed | Status |
|---|---:|---:|---:|---:|---|
| ctx01 | 9 | 0 | 0 | 80 | VALID |
| ctx02 | 9 | 0 | 0 | 80 | VALID |
| ctx03 | 9 | 1 | 0 | 80 | VALID |
| ctx04 | 9 | 3 | 0 | 80 | VOID |
| ctx05 | 9 | 2 | 0 | 80 | VOID |
| ctx06 | 9 | 1 | 0 | 79 | VALID |
| ctx07 | 9 | 2 | 0 | 79 | VOID |

More than one wrong control voids the context. Unreadable controls abstain; malformed/missing/duplicate answers fail closed before scoring. Historical mapped files count unreadables as errors; they are preserved, and gates are independently decoded from answers and private option keys. No control abstentions occurred here.

Control errors (item, truth → answer):

- ctx03 `k190d2be189`: nothing → baseline dot (`elstat--58f9f02d8162c1c6--s000-l0072:t0:s4`).
- ctx04 `kbd958d163f`: nothing → baseline dot (`gazette_modern--9701a3a500ecbd85--s000-l0041:t0:s1`).
- ctx04 `kd2d31cdefa`: baseline dot → raised dot (`gazette_modern--d2281f8022512d7b--s000-l0277:t0:s3`).
- ctx04 `kce6182eb89`: nothing → space (`gazette_modern--484657f18e4fd09a--s000-l0102:t0:s3`).
- ctx05 `kbaf85380ec`: baseline dot → raised dot (`gazette_modern--d4e7c0bb57264e92--s000-l0027:t0:s3`).
- ctx05 `k26da661515`: nothing → raised dot (`gazette_modern--d2281f8022512d7b--s000-l0093:t0:s7`).
- ctx06 `k4e7c313905`: baseline dot → raised dot (`gazette_modern--d2281f8022512d7b--s000-l0181:t0:s3`).
- ctx07 `k9aa3f05d90`: nothing → space (`gazette_modern--484657f18e4fd09a--s000-l0102:t0:s3`).
- ctx07 `k3ad947be48`: nothing → baseline dot (`elstat--58f9f02d8162c1c6--s000-l0072:t0:s4`).

## Google × ink

Exact Google text gaps form rows (JSON strings preserve spaces and empty gaps). Reader meanings form columns. Only VALID bed answers enter these tables, including low-confidence and unresolved reads; these remain owner-review evidence, not adjudicated truth.

| Google exact gap | raised dot | baseline dot | comma | hyphen or dash | space | nothing | other | unreadable | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `""` | 0 | 0 | 0 | 0 | 6 | 1 | 3 | 0 | 10 |
| `" "` | 1 | 0 | 0 | 0 | 7 | 0 | 3 | 1 | 12 |
| `" -"` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `" - "` | 0 | 0 | 0 | 11 | 0 | 0 | 0 | 0 | 11 |
| `" – "` | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 4 |
| `","` | 0 | 3 | 26 | 0 | 0 | 0 | 1 | 2 | 32 |
| `", "` | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 8 |
| `",-"` | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 2 |
| `",- "` | 0 | 0 | 0 | 2 | 0 | 0 | 1 | 0 | 3 |
| `",-- "` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `",..."` | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"-"` | 17 | 4 | 0 | 111 | 0 | 1 | 1 | 1 | 135 |
| `"- "` | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| `"--"` | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 2 |
| `"-."` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"."` | 0 | 27 | 1 | 0 | 0 | 1 | 0 | 1 | 30 |
| `". "` | 0 | 11 | 0 | 0 | 0 | 0 | 0 | 1 | 12 |
| `". -"` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `". - "` | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 7 |
| `". – "` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `".,"` | 0 | 4 | 2 | 0 | 0 | 0 | 0 | 0 | 6 |
| `".-"` | 0 | 3 | 0 | 3 | 0 | 0 | 1 | 0 | 7 |
| `".- "` | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 9 |
| `".-."` | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| `".."` | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 3 |
| `"..."` | 0 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 3 |
| `"...."` | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| `"......"` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"......."` | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| `"........"` | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| `"........ "` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `".–"` | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| `"·"` | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"–"` | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 3 |

### Highlighted transitions

- **'-' → raised dot: 17**
- **'.' → raised dot: 0**
- **'-' → baseline dot: 4**
- **'.' → comma: 1**
- **',' → baseline dot: 3**
- **empty → any mark: 0**
- **any → unreadable / other: 18**

For semantic agreement only, surrounding whitespace is ignored around a single known mark; empty agrees with nothing, whitespace-only with space, and single dash variants agree with hyphen/dash. Multi-mark gaps are disagreements. Highlight counts use exact glyphs. Unreadable/other/low-confidence cards take precedence over transition groups. Target and dot transition tallies include low-confidence reads; group counts therefore need not equal them.

### Source / era

#### bsb_poly1850

| Google exact gap | raised dot | baseline dot | comma | hyphen or dash | space | nothing | other | unreadable | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `""` | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 2 |
| `" "` | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| `" - "` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `","` | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 7 |
| `"-"` | 1 | 0 | 0 | 17 | 0 | 0 | 0 | 0 | 18 |
| `"--"` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `"-."` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"."` | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| `". "` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `". -"` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `". - "` | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 7 |
| `".-"` | 0 | 1 | 0 | 2 | 0 | 0 | 0 | 0 | 3 |
| `".- "` | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 8 |

#### elstat

| Google exact gap | raised dot | baseline dot | comma | hyphen or dash | space | nothing | other | unreadable | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `" "` | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 2 |
| `" - "` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `","` | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 4 |
| `"-"` | 14 | 2 | 0 | 9 | 0 | 1 | 0 | 0 | 26 |
| `"."` | 0 | 4 | 0 | 0 | 0 | 1 | 0 | 0 | 5 |
| `". "` | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| `".."` | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| `"...."` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"......"` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"......."` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"........ "` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |

#### gazette_1982_1985

| Google exact gap | raised dot | baseline dot | comma | hyphen or dash | space | nothing | other | unreadable | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `""` | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| `" – "` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `","` | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 2 |
| `", "` | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"-"` | 0 | 0 | 0 | 11 | 0 | 0 | 0 | 0 | 11 |
| `"--"` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `"."` | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| `".."` | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"..."` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"......."` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |

#### gazette_1986_1990

| Google exact gap | raised dot | baseline dot | comma | hyphen or dash | space | nothing | other | unreadable | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `" "` | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `" - "` | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 8 |
| `" – "` | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 2 |
| `","` | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 3 |
| `", "` | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| `",..."` | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"-"` | 0 | 1 | 0 | 14 | 0 | 0 | 0 | 0 | 15 |
| `"."` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `". "` | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 1 | 3 |
| `". – "` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `".-"` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `".- "` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `".-."` | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| `"...."` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"......."` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"........"` | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| `".–"` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |

#### ia_greek_latin

| Google exact gap | raised dot | baseline dot | comma | hyphen or dash | space | nothing | other | unreadable | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `""` | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 2 |
| `" "` | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 3 |
| `","` | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 1 | 3 |
| `", "` | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| `",-"` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `"-"` | 0 | 0 | 0 | 18 | 0 | 0 | 0 | 0 | 18 |
| `"."` | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 3 |
| `". "` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `".,"` | 0 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 3 |
| `".-"` | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 2 |
| `".."` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"·"` | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"–"` | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 2 |

#### ia_poly1850

| Google exact gap | raised dot | baseline dot | comma | hyphen or dash | space | nothing | other | unreadable | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `""` | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 3 |
| `" "` | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 2 |
| `" -"` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `" - "` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `" – "` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `","` | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 3 |
| `"-"` | 1 | 0 | 0 | 20 | 0 | 0 | 0 | 0 | 21 |
| `"."` | 0 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 5 |
| `". "` | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| `".,"` | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| `"–"` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |

#### ia_russian

| Google exact gap | raised dot | baseline dot | comma | hyphen or dash | space | nothing | other | unreadable | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `" "` | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| `","` | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| `", "` | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"-"` | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 8 |
| `"."` | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| `". "` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |

#### kosmopolis

| Google exact gap | raised dot | baseline dot | comma | hyphen or dash | space | nothing | other | unreadable | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `","` | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| `", "` | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| `"-"` | 0 | 1 | 0 | 3 | 0 | 0 | 0 | 0 | 4 |
| `"."` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `".–"` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |

#### lekythos

| Google exact gap | raised dot | baseline dot | comma | hyphen or dash | space | nothing | other | unreadable | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `""` | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| `" "` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| `","` | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 2 |
| `", "` | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| `",-"` | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"-"` | 0 | 0 | 0 | 6 | 0 | 0 | 1 | 0 | 7 |
| `"."` | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 1 | 3 |
| `".-"` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"..."` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |

#### nlg

| Google exact gap | raised dot | baseline dot | comma | hyphen or dash | space | nothing | other | unreadable | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `","` | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"-"` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| `"."` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"..."` | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |

#### serbia

| Google exact gap | raised dot | baseline dot | comma | hyphen or dash | space | nothing | other | unreadable | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `""` | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| `" "` | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| `","` | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 4 |
| `",- "` | 0 | 0 | 0 | 2 | 0 | 0 | 1 | 0 | 3 |
| `",-- "` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `"-"` | 1 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 6 |
| `"- "` | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| `"."` | 0 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 4 |
| `". "` | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |

### Grammar position

#### decimal

| Google exact gap | raised dot | baseline dot | comma | hyphen or dash | space | nothing | other | unreadable | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `","` | 0 | 0 | 11 | 0 | 0 | 0 | 1 | 0 | 12 |
| `"."` | 0 | 11 | 1 | 0 | 0 | 0 | 0 | 0 | 12 |

#### other

| Google exact gap | raised dot | baseline dot | comma | hyphen or dash | space | nothing | other | unreadable | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `""` | 0 | 0 | 0 | 0 | 3 | 1 | 1 | 0 | 5 |
| `" "` | 0 | 0 | 0 | 0 | 4 | 0 | 3 | 1 | 8 |
| `" -"` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `" - "` | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 6 |
| `" – "` | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 3 |
| `","` | 0 | 0 | 10 | 0 | 0 | 0 | 0 | 0 | 10 |
| `", "` | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 | 8 |
| `",-"` | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 2 |
| `",- "` | 0 | 0 | 0 | 2 | 0 | 0 | 1 | 0 | 3 |
| `",-- "` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `",..."` | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"-"` | 0 | 3 | 0 | 58 | 0 | 1 | 1 | 1 | 64 |
| `"- "` | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| `"--"` | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 2 |
| `"-."` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"."` | 0 | 10 | 0 | 0 | 0 | 1 | 0 | 1 | 12 |
| `". "` | 0 | 11 | 0 | 0 | 0 | 0 | 0 | 1 | 12 |
| `". -"` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `". - "` | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 7 |
| `". – "` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `".,"` | 0 | 4 | 2 | 0 | 0 | 0 | 0 | 0 | 6 |
| `".-"` | 0 | 3 | 0 | 3 | 0 | 0 | 1 | 0 | 7 |
| `".- "` | 0 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 9 |
| `".-."` | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| `".."` | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 0 | 3 |
| `"..."` | 0 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 3 |
| `"...."` | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| `"......"` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"......."` | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| `"........"` | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| `"........ "` | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `".–"` | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| `"·"` | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `"–"` | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 3 |

#### range

| Google exact gap | raised dot | baseline dot | comma | hyphen or dash | space | nothing | other | unreadable | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `" - "` | 0 | 0 | 0 | 5 | 0 | 0 | 0 | 0 | 5 |
| `" – "` | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| `"-"` | 9 | 0 | 0 | 48 | 0 | 0 | 0 | 0 | 57 |

#### table_boundary

| Google exact gap | raised dot | baseline dot | comma | hyphen or dash | space | nothing | other | unreadable | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `""` | 0 | 0 | 0 | 0 | 3 | 0 | 2 | 0 | 5 |

#### thousands

| Google exact gap | raised dot | baseline dot | comma | hyphen or dash | space | nothing | other | unreadable | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `" "` | 1 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 4 |
| `","` | 0 | 3 | 5 | 0 | 0 | 0 | 0 | 2 | 10 |
| `"-"` | 8 | 1 | 0 | 5 | 0 | 0 | 0 | 0 | 14 |
| `"."` | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 6 |

## Target-fault rate inside the enriched frame

**This is an enriched diagnostic frame, not a population sample.** Only the 600 `step1` slots enter the frame denominator; the 300 locked slots are untouched. Of 600, 42 were dropped for geometry, 239 belong to VOID contexts, and 319 have valid reads.

The frame contains no numeric inclusion probabilities. Its recorded design cells are source/era × primary grammar position × exact Google gap. We use empirical frame weights W_h = N_h/600, not inverse population inclusion probabilities. Within each observed cell, each read receives N_h/n_h (response standardization, assuming the missing reads resemble the observed reads in that cell). No population correction is claimed.

Observed support covers 148/212 cells, representing 500/600 frame slots; 100 frame slots have no valid read in their cell. The **supported-cell standardized rate is 6.225% [3.973, 9.626]**. This is conditional on supported cells, not an identified full-frame point rate. The bracket is an approximate 95% weighted Wilson interval with Kish effective n = 288.871, ignoring line/document clustering and reader error; it is descriptive, not a precision qualification.

Crude VALID-read rate: 5.329% [3.354, 8.368] (ordinary 95% Wilson). Full-frame point identification bounds, retaining within-cell response assumptions but allowing unsupported exact-hyphen cells any rate (all non-hyphen cells are structural target zeros): [5.188, 5.354]%. Weighted target-capable cell-Wilson envelope with unsupported hyphen cells [0,1]: [2.950, 18.061]%; this envelope is not a simultaneous 95% confidence interval. Only 1 unsupported frame slot can carry this exact target transition; other unsupported slots are structural target zeros. Re-reads are required for a complete frame estimate.

All valid slots are the denominator; unreadable/other reads are not target-positive and remain uncertain. The estimate measures recorded reader-positive faults, not the unknown true rate among unresolved answers.

| Source/era | Grammar | Exact gap | Frame N | Read n | Fault k | W_h | N_h/n_h | Rate % | Wilson 95% % |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| bsb_poly1850 | decimal | `","` | 3 | 3 | 0 | 0.00500 | 1.000 | 0.00 | 0.00, 56.15 |
| bsb_poly1850 | decimal | `"."` | 3 | 2 | 0 | 0.00500 | 1.500 | 0.00 | 0.00, 65.76 |
| bsb_poly1850 | other | `""` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| bsb_poly1850 | other | `" "` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| bsb_poly1850 | other | `","` | 2 | 2 | 0 | 0.00333 | 1.000 | 0.00 | 0.00, 65.76 |
| bsb_poly1850 | other | `", "` | 2 | 0 | 0 | 0.00333 | — | — | — |
| bsb_poly1850 | other | `"-"` | 15 | 8 | 0 | 0.02500 | 1.875 | 0.00 | 0.00, 32.44 |
| bsb_poly1850 | other | `"--"` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| bsb_poly1850 | other | `"-."` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| bsb_poly1850 | other | `"."` | 2 | 0 | 0 | 0.00333 | — | — | — |
| bsb_poly1850 | other | `". "` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| bsb_poly1850 | other | `". -"` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| bsb_poly1850 | other | `". - "` | 10 | 7 | 0 | 0.01667 | 1.429 | 0.00 | 0.00, 35.43 |
| bsb_poly1850 | other | `".-"` | 4 | 3 | 0 | 0.00667 | 1.333 | 0.00 | 0.00, 56.15 |
| bsb_poly1850 | other | `".- "` | 11 | 8 | 0 | 0.01833 | 1.375 | 0.00 | 0.00, 32.44 |
| bsb_poly1850 | other | `".-."` | 1 | 0 | 0 | 0.00167 | — | — | — |
| bsb_poly1850 | other | `".\u2014"` | 1 | 0 | 0 | 0.00167 | — | — | — |
| bsb_poly1850 | other | `"\u00b7"` | 1 | 0 | 0 | 0.00167 | — | — | — |
| bsb_poly1850 | range | `" - "` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| bsb_poly1850 | range | `"-"` | 15 | 10 | 1 | 0.02500 | 1.500 | 10.00 | 1.79, 40.42 |
| bsb_poly1850 | table_boundary | `""` | 3 | 1 | 0 | 0.00500 | 3.000 | 0.00 | 0.00, 79.35 |
| bsb_poly1850 | thousands | `","` | 3 | 2 | 0 | 0.00500 | 1.500 | 0.00 | 0.00, 65.76 |
| elstat | decimal | `","` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| elstat | decimal | `"."` | 3 | 2 | 0 | 0.00500 | 1.500 | 0.00 | 0.00, 65.76 |
| elstat | other | `" "` | 3 | 1 | 0 | 0.00500 | 3.000 | 0.00 | 0.00, 79.35 |
| elstat | other | `","` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| elstat | other | `"-"` | 13 | 11 | 0 | 0.02167 | 1.182 | 0.00 | 0.00, 25.88 |
| elstat | other | `"."` | 3 | 3 | 0 | 0.00500 | 1.000 | 0.00 | 0.00, 56.15 |
| elstat | other | `". "` | 2 | 2 | 0 | 0.00333 | 1.000 | 0.00 | 0.00, 65.76 |
| elstat | other | `".."` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| elstat | other | `"..."` | 2 | 0 | 0 | 0.00333 | — | — | — |
| elstat | other | `"...."` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| elstat | other | `"......"` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| elstat | other | `"......."` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| elstat | other | `"........ "` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| elstat | range | `" - "` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| elstat | range | `" \u2013 "` | 1 | 0 | 0 | 0.00167 | — | — | — |
| elstat | range | `"-"` | 14 | 7 | 7 | 0.02333 | 2.000 | 100.00 | 64.57, 100.00 |
| elstat | thousands | `" "` | 3 | 1 | 0 | 0.00500 | 3.000 | 0.00 | 0.00, 79.35 |
| elstat | thousands | `","` | 3 | 2 | 0 | 0.00500 | 1.500 | 0.00 | 0.00, 65.76 |
| elstat | thousands | `"-"` | 15 | 8 | 7 | 0.02500 | 1.875 | 87.50 | 52.91, 97.76 |
| elstat | thousands | `"."` | 1 | 0 | 0 | 0.00167 | — | — | — |
| gazette_1982_1985 | decimal | `","` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| gazette_1982_1985 | decimal | `"."` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| gazette_1982_1985 | other | `""` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| gazette_1982_1985 | other | `" "` | 2 | 0 | 0 | 0.00333 | — | — | — |
| gazette_1982_1985 | other | `" \u2013 "` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| gazette_1982_1985 | other | `","` | 3 | 0 | 0 | 0.00500 | — | — | — |
| gazette_1982_1985 | other | `", "` | 3 | 1 | 0 | 0.00500 | 3.000 | 0.00 | 0.00, 79.35 |
| gazette_1982_1985 | other | `"-"` | 13 | 7 | 0 | 0.02167 | 1.857 | 0.00 | 0.00, 35.43 |
| gazette_1982_1985 | other | `"--"` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| gazette_1982_1985 | other | `"---"` | 1 | 0 | 0 | 0.00167 | — | — | — |
| gazette_1982_1985 | other | `"----"` | 1 | 0 | 0 | 0.00167 | — | — | — |
| gazette_1982_1985 | other | `"."` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| gazette_1982_1985 | other | `". "` | 2 | 0 | 0 | 0.00333 | — | — | — |
| gazette_1982_1985 | other | `".."` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| gazette_1982_1985 | other | `"..."` | 3 | 1 | 0 | 0.00500 | 3.000 | 0.00 | 0.00, 79.35 |
| gazette_1982_1985 | other | `"...."` | 2 | 0 | 0 | 0.00333 | — | — | — |
| gazette_1982_1985 | other | `"....."` | 1 | 0 | 0 | 0.00167 | — | — | — |
| gazette_1982_1985 | other | `"......."` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| gazette_1982_1985 | range | `"-"` | 7 | 4 | 0 | 0.01167 | 1.750 | 0.00 | 0.00, 48.99 |
| gazette_1982_1985 | thousands | `","` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| gazette_1982_1985 | thousands | `"."` | 3 | 1 | 0 | 0.00500 | 3.000 | 0.00 | 0.00, 79.35 |
| gazette_1986_1990 | decimal | `","` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| gazette_1986_1990 | decimal | `"."` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| gazette_1986_1990 | other | `" "` | 2 | 0 | 0 | 0.00333 | — | — | — |
| gazette_1986_1990 | other | `" - "` | 13 | 6 | 0 | 0.02167 | 2.167 | 0.00 | 0.00, 39.03 |
| gazette_1986_1990 | other | `" ... "` | 2 | 0 | 0 | 0.00333 | — | — | — |
| gazette_1986_1990 | other | `" \u2013 "` | 3 | 1 | 0 | 0.00500 | 3.000 | 0.00 | 0.00, 79.35 |
| gazette_1986_1990 | other | `","` | 2 | 0 | 0 | 0.00333 | — | — | — |
| gazette_1986_1990 | other | `", "` | 3 | 1 | 0 | 0.00500 | 3.000 | 0.00 | 0.00, 79.35 |
| gazette_1986_1990 | other | `",..."` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| gazette_1986_1990 | other | `"-"` | 15 | 7 | 0 | 0.02500 | 2.143 | 0.00 | 0.00, 35.43 |
| gazette_1986_1990 | other | `"- "` | 4 | 0 | 0 | 0.00667 | — | — | — |
| gazette_1986_1990 | other | `"--"` | 1 | 0 | 0 | 0.00167 | — | — | — |
| gazette_1986_1990 | other | `"----"` | 1 | 0 | 0 | 0.00167 | — | — | — |
| gazette_1986_1990 | other | `"."` | 2 | 0 | 0 | 0.00333 | — | — | — |
| gazette_1986_1990 | other | `". "` | 3 | 3 | 0 | 0.00500 | 1.000 | 0.00 | 0.00, 56.15 |
| gazette_1986_1990 | other | `". \u2013 "` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| gazette_1986_1990 | other | `".-"` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| gazette_1986_1990 | other | `".- "` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| gazette_1986_1990 | other | `".-."` | 2 | 2 | 0 | 0.00333 | 1.000 | 0.00 | 0.00, 65.76 |
| gazette_1986_1990 | other | `".."` | 3 | 0 | 0 | 0.00500 | — | — | — |
| gazette_1986_1990 | other | `"..."` | 2 | 0 | 0 | 0.00333 | — | — | — |
| gazette_1986_1990 | other | `"...."` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| gazette_1986_1990 | other | `"......"` | 1 | 0 | 0 | 0.00167 | — | — | — |
| gazette_1986_1990 | other | `"......."` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| gazette_1986_1990 | other | `"........"` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| gazette_1986_1990 | other | `".\u2013"` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| gazette_1986_1990 | other | `"\u00b7,"` | 1 | 0 | 0 | 0.00167 | — | — | — |
| gazette_1986_1990 | other | `"\u00b7-"` | 1 | 0 | 0 | 0.00167 | — | — | — |
| gazette_1986_1990 | range | `" - "` | 2 | 2 | 0 | 0.00333 | 1.000 | 0.00 | 0.00, 65.76 |
| gazette_1986_1990 | range | `" \u2013 "` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| gazette_1986_1990 | range | `"-"` | 15 | 8 | 0 | 0.02500 | 1.875 | 0.00 | 0.00, 32.44 |
| gazette_1986_1990 | range | `"- "` | 2 | 0 | 0 | 0.00333 | — | — | — |
| gazette_1986_1990 | table_boundary | `""` | 2 | 0 | 0 | 0.00333 | — | — | — |
| gazette_1986_1990 | thousands | `" "` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| gazette_1986_1990 | thousands | `","` | 2 | 2 | 0 | 0.00333 | 1.000 | 0.00 | 0.00, 65.76 |
| gazette_1986_1990 | thousands | `"-"` | 1 | 0 | 0 | 0.00167 | — | — | — |
| gazette_1986_1990 | thousands | `"."` | 3 | 0 | 0 | 0.00500 | — | — | — |
| ia_greek_latin | decimal | `","` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| ia_greek_latin | decimal | `"."` | 3 | 2 | 0 | 0.00500 | 1.500 | 0.00 | 0.00, 65.76 |
| ia_greek_latin | other | `""` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| ia_greek_latin | other | `" "` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| ia_greek_latin | other | `","` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| ia_greek_latin | other | `", "` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| ia_greek_latin | other | `",-"` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| ia_greek_latin | other | `",."` | 1 | 0 | 0 | 0.00167 | — | — | — |
| ia_greek_latin | other | `"-"` | 15 | 7 | 0 | 0.02500 | 2.143 | 0.00 | 0.00, 35.43 |
| ia_greek_latin | other | `"."` | 2 | 0 | 0 | 0.00333 | — | — | — |
| ia_greek_latin | other | `". "` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| ia_greek_latin | other | `".,"` | 3 | 3 | 0 | 0.00500 | 1.000 | 0.00 | 0.00, 56.15 |
| ia_greek_latin | other | `".,,"` | 1 | 0 | 0 | 0.00167 | — | — | — |
| ia_greek_latin | other | `".,-"` | 1 | 0 | 0 | 0.00167 | — | — | — |
| ia_greek_latin | other | `".-"` | 3 | 2 | 0 | 0.00500 | 1.500 | 0.00 | 0.00, 65.76 |
| ia_greek_latin | other | `".---"` | 1 | 0 | 0 | 0.00167 | — | — | — |
| ia_greek_latin | other | `".."` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| ia_greek_latin | other | `"\u00b7"` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| ia_greek_latin | other | `"\u2013"` | 2 | 2 | 0 | 0.00333 | 1.000 | 0.00 | 0.00, 65.76 |
| ia_greek_latin | range | `"-"` | 14 | 9 | 0 | 0.02333 | 1.556 | 0.00 | 0.00, 29.91 |
| ia_greek_latin | table_boundary | `""` | 3 | 1 | 0 | 0.00500 | 3.000 | 0.00 | 0.00, 79.35 |
| ia_greek_latin | thousands | `" "` | 2 | 2 | 0 | 0.00333 | 1.000 | 0.00 | 0.00, 65.76 |
| ia_greek_latin | thousands | `","` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| ia_greek_latin | thousands | `"-"` | 3 | 2 | 0 | 0.00500 | 1.500 | 0.00 | 0.00, 65.76 |
| ia_greek_latin | thousands | `"."` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| ia_poly1850 | decimal | `","` | 3 | 2 | 0 | 0.00500 | 1.500 | 0.00 | 0.00, 65.76 |
| ia_poly1850 | decimal | `"."` | 3 | 2 | 0 | 0.00500 | 1.500 | 0.00 | 0.00, 65.76 |
| ia_poly1850 | other | `""` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| ia_poly1850 | other | `" "` | 3 | 2 | 0 | 0.00500 | 1.500 | 0.00 | 0.00, 65.76 |
| ia_poly1850 | other | `" -"` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| ia_poly1850 | other | `" \u2013 "` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| ia_poly1850 | other | `","` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| ia_poly1850 | other | `", "` | 3 | 0 | 0 | 0.00500 | — | — | — |
| ia_poly1850 | other | `"-"` | 14 | 12 | 0 | 0.02333 | 1.167 | 0.00 | 0.00, 24.25 |
| ia_poly1850 | other | `"."` | 3 | 2 | 0 | 0.00500 | 1.500 | 0.00 | 0.00, 65.76 |
| ia_poly1850 | other | `". "` | 3 | 2 | 0 | 0.00500 | 1.500 | 0.00 | 0.00, 65.76 |
| ia_poly1850 | other | `".,"` | 3 | 3 | 0 | 0.00500 | 1.000 | 0.00 | 0.00, 56.15 |
| ia_poly1850 | other | `"..."` | 1 | 0 | 0 | 0.00167 | — | — | — |
| ia_poly1850 | other | `"\u00b7"` | 2 | 0 | 0 | 0.00333 | — | — | — |
| ia_poly1850 | other | `"\u2013"` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| ia_poly1850 | other | `"\u2014"` | 2 | 0 | 0 | 0.00333 | — | — | — |
| ia_poly1850 | range | `" - "` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| ia_poly1850 | range | `"-"` | 14 | 5 | 0 | 0.02333 | 2.800 | 0.00 | 0.00, 43.45 |
| ia_poly1850 | range | `"\u2013"` | 1 | 0 | 0 | 0.00167 | — | — | — |
| ia_poly1850 | table_boundary | `""` | 2 | 2 | 0 | 0.00333 | 1.000 | 0.00 | 0.00, 65.76 |
| ia_poly1850 | thousands | `" "` | 2 | 0 | 0 | 0.00333 | — | — | — |
| ia_poly1850 | thousands | `"-"` | 6 | 4 | 1 | 0.01000 | 1.500 | 25.00 | 4.56, 69.94 |
| ia_poly1850 | thousands | `"."` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| ia_russian | other | `""` | 1 | 0 | 0 | 0.00167 | — | — | — |
| ia_russian | other | `" "` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| ia_russian | other | `","` | 3 | 0 | 0 | 0.00500 | — | — | — |
| ia_russian | other | `", "` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| ia_russian | other | `"-"` | 2 | 2 | 0 | 0.00333 | 1.000 | 0.00 | 0.00, 65.76 |
| ia_russian | other | `"--"` | 2 | 0 | 0 | 0.00333 | — | — | — |
| ia_russian | other | `"-\u2014"` | 1 | 0 | 0 | 0.00167 | — | — | — |
| ia_russian | other | `"."` | 3 | 2 | 0 | 0.00500 | 1.500 | 0.00 | 0.00, 65.76 |
| ia_russian | other | `". "` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| ia_russian | other | `"\u2014"` | 1 | 0 | 0 | 0.00167 | — | — | — |
| ia_russian | range | `" \u2014 "` | 1 | 0 | 0 | 0.00167 | — | — | — |
| ia_russian | range | `"-"` | 14 | 6 | 0 | 0.02333 | 2.333 | 0.00 | 0.00, 39.03 |
| ia_russian | range | `"\u2014"` | 1 | 0 | 0 | 0.00167 | — | — | — |
| ia_russian | thousands | `","` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| kosmopolis | other | `""` | 1 | 0 | 0 | 0.00167 | — | — | — |
| kosmopolis | other | `","` | 2 | 2 | 0 | 0.00333 | 1.000 | 0.00 | 0.00, 65.76 |
| kosmopolis | other | `", "` | 3 | 2 | 0 | 0.00500 | 1.500 | 0.00 | 0.00, 65.76 |
| kosmopolis | other | `"-"` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| kosmopolis | other | `"."` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| kosmopolis | other | `".."` | 1 | 0 | 0 | 0.00167 | — | — | — |
| kosmopolis | other | `".\u2013"` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| kosmopolis | range | `"-"` | 3 | 3 | 0 | 0.00500 | 1.000 | 0.00 | 0.00, 56.15 |
| kosmopolis | range | `"\u2013"` | 1 | 0 | 0 | 0.00167 | — | — | — |
| lekythos | decimal | `","` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| lekythos | decimal | `"."` | 2 | 0 | 0 | 0.00333 | — | — | — |
| lekythos | other | `""` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| lekythos | other | `" "` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| lekythos | other | `" -"` | 1 | 0 | 0 | 0.00167 | — | — | — |
| lekythos | other | `","` | 2 | 0 | 0 | 0.00333 | — | — | — |
| lekythos | other | `", "` | 2 | 2 | 0 | 0.00333 | 1.000 | 0.00 | 0.00, 65.76 |
| lekythos | other | `",-"` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| lekythos | other | `"-"` | 7 | 5 | 0 | 0.01167 | 1.400 | 0.00 | 0.00, 43.45 |
| lekythos | other | `"."` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| lekythos | other | `". "` | 1 | 0 | 0 | 0.00167 | — | — | — |
| lekythos | other | `".-"` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| lekythos | other | `"..."` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| lekythos | range | `"-"` | 3 | 2 | 0 | 0.00500 | 1.500 | 0.00 | 0.00, 65.76 |
| lekythos | thousands | `" "` | 2 | 0 | 0 | 0.00333 | — | — | — |
| lekythos | thousands | `","` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| lekythos | thousands | `"."` | 2 | 2 | 0 | 0.00333 | 1.000 | 0.00 | 0.00, 65.76 |
| nlg | decimal | `"."` | 1 | 0 | 0 | 0.00167 | — | — | — |
| nlg | other | `","` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| nlg | other | `", "` | 1 | 0 | 0 | 0.00167 | — | — | — |
| nlg | other | `"-"` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| nlg | other | `"."` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| nlg | other | `". "` | 1 | 0 | 0 | 0.00167 | — | — | — |
| nlg | other | `"..."` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| serbia | decimal | `","` | 2 | 2 | 0 | 0.00333 | 1.000 | 0.00 | 0.00, 65.76 |
| serbia | decimal | `"."` | 3 | 2 | 0 | 0.00500 | 1.500 | 0.00 | 0.00, 65.76 |
| serbia | other | `" "` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| serbia | other | `","` | 2 | 2 | 0 | 0.00333 | 1.000 | 0.00 | 0.00, 65.76 |
| serbia | other | `", "` | 2 | 0 | 0 | 0.00333 | — | — | — |
| serbia | other | `",- "` | 3 | 3 | 0 | 0.00500 | 1.000 | 0.00 | 0.00, 56.15 |
| serbia | other | `",-- "` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| serbia | other | `"-"` | 5 | 3 | 0 | 0.00833 | 1.667 | 0.00 | 0.00, 56.15 |
| serbia | other | `"- "` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |
| serbia | other | `"."` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| serbia | other | `". "` | 3 | 2 | 0 | 0.00500 | 1.500 | 0.00 | 0.00, 65.76 |
| serbia | other | `".- "` | 2 | 0 | 0 | 0.00333 | — | — | — |
| serbia | other | `".."` | 1 | 0 | 0 | 0.00167 | — | — | — |
| serbia | other | `"..."` | 1 | 0 | 0 | 0.00167 | — | — | — |
| serbia | range | `"-"` | 3 | 3 | 1 | 0.00500 | 1.000 | 33.33 | 6.15, 79.23 |
| serbia | table_boundary | `""` | 2 | 1 | 0 | 0.00333 | 2.000 | 0.00 | 0.00, 79.35 |
| serbia | thousands | `"."` | 1 | 1 | 0 | 0.00167 | 1.000 | 0.00 | 0.00, 79.35 |

## Rule readiness: descriptive evidence only

Full per-slot side records, including component height, centre relative to digit band, width, bbox, containment, digit band and gap width, are in `artifacts/n1/N1S_MEASUREMENTS.json`. All components intersecting each gap are retained, including digit fragments and components crossing the gap; none was selected as the true mark. Centre = (component centre y − digit_top)/digit_height, increasing downward. Heights and widths are native pixels. Ranges pool components by reader class. Overlap counts count components within the intersection of the two class ranges; they do not count classification errors. No threshold, classifier, train/test split or rule was fit.

Slots by class: {'hyphen or dash': 157, 'raised dot': 19}; component counts: {'hyphen or dash': 239, 'raised dot': 5}; zero-component slots: {'hyphen or dash': 8, 'raised dot': 14}.

**Readiness limitation:** 14 of 19 raised-dot reads have no saved gap component. The five available components overlap the hyphen/dash ranges on every reported measurement. These records do not establish a separating rule; step 2 must resolve missing component evidence before using it for an ink decision.

| Measurement | Raised-dot range | Hyphen/dash range | Range intersection | Raised components in overlap | Hyphen components in overlap |
|---|---|---|---|---:|---:|
| height | [3, 6] | [1, 43] | [3, 6] | 5 | 146 |
| centre_y_relative_band | [0.5897435897435898, 0.7941176470588235] | [-0.21794871794871795, 1.2777777777777777] | [0.5897435897435898, 0.7941176470588235] | 5 | 72 |
| width | [3, 7] | [2, 756] | [3, 7] | 5 | 62 |

### Per-slot components

| Slot | Read / confidence | Height px, centre/band, width px (all components) |
|---|---|---|
| `ia_poly1850--ed3079bf091f7255--s002-l0034:t0:s3` | hyphen or dash / high | (7, 0.500000, 47) |
| `gazette_modern--5a173b5ea9cc9922--s000-l0083:t0:s4` | hyphen or dash / high | (22, 0.437500, 57) |
| `ia_russian--3ecca278cf0eea22--s001-l0025:t0:s2` | hyphen or dash / high | (43, 0.432203, 25); (6, 0.508475, 61) |
| `gazette_modern--0d828774646bb76b--s000-l0095:t0:s1` | hyphen or dash / low | none |
| `gazette_modern--158b2e0a2843dd81--s000-l0079:t0:s7` | hyphen or dash / high | (5, 0.617647, 11) |
| `bsb_poly1850--767e91eee85d9120--s004-l0040:t0:s2` | hyphen or dash / high | (4, 0.695652, 30) |
| `bsb_poly1850--fccefa9e9f9823aa--s000-l0024:t0:s1` | hyphen or dash / high | (3, 0.690476, 26); (5, 0.928571, 3) |
| `ia_russian--3ecca278cf0eea22--s003-l0012:t0:s1` | hyphen or dash / high | none |
| `bsb_poly1850--767e91eee85d9120--s006-l0039:t3:s3` | hyphen or dash / high | (4, 0.583333, 32) |
| `ia_greek_latin--f42ec9d8d21af31b--s000-l0085:t5:s2` | hyphen or dash / high | (4, 0.562500, 19) |
| `gazette_modern--54f1f0595779ed67--s000-l0018:t0:s2` | hyphen or dash / high | (3, 0.589286, 8) |
| `bsb_poly1850--97801b0bc5afce27--s005-l0044:t1:s2` | hyphen or dash / high | (4, 0.475000, 34) |
| `gazette_modern--2e613d9290dd13d4--s000-l0333:t0:s2` | hyphen or dash / high | (5, 0.772727, 11) |
| `ia_poly1850--a89bd2c9bdb1ca6d--s006-l0014:t0:s4` | hyphen or dash / high | (8, 0.540000, 46) |
| `ia_poly1850--e6e379cb4b1d54af--s007-l0010:t0:s3` | hyphen or dash / high | (7, 0.532787, 55) |
| `gazette_modern--bd4c89f73f9ccfce--s000-l0047:t0:s2` | hyphen or dash / high | (4, 0.633333, 8) |
| `gazette_modern--2e613d9290dd13d4--s000-l0097:t0:s2` | hyphen or dash / high | (4, 0.750000, 10) |
| `elstat--ee37bc488988f1bd--s000-l0818:t0:s3` | raised dot / low | none |
| `ia_poly1850--5aa15e93b2f445b8--s003-l0031:t0:s3` | hyphen or dash / high | (8, 0.484375, 69) |
| `ia_greek_latin--d15eca050847acdb--s005-l0008:t0:s5` | hyphen or dash / high | (5, 0.608108, 12) |
| `ia_poly1850--5aa15e93b2f445b8--s001-l0043:t2:s7` | hyphen or dash / high | (8, 0.516667, 53) |
| `elstat--24e6586813212fd1--s000-l0135:t0:s2` | hyphen or dash / high | (13, 0.472222, 23) |
| `ia_poly1850--36dcee7ce4c29f8b--s007-l0072:t2:s2` | hyphen or dash / high | (3, -0.192308, 6); (3, -0.192308, 5); (4, -0.179487, 39); (8, 0.615385, 35); (9, 1.269231, 11) |
| `bsb_poly1850--fccefa9e9f9823aa--s000-l0096:t0:s1` | hyphen or dash / high | (3, 0.673913, 27); (3, 0.891304, 4) |
| `bsb_poly1850--97801b0bc5afce27--s002-l0026:t0:s4` | hyphen or dash / high | (5, 0.542553, 43) |
| `ia_greek_latin--2b4cfc7c6d70fd98--s000-l0016:t2:s5` | hyphen or dash / low | (26, 0.600000, 44) |
| `ia_russian--3ecca278cf0eea22--s002-l0051:t1:s2` | hyphen or dash / high | (5, 0.500000, 50) |
| `kosmopolis--681a15c3d4a0cd62--s000-l0021:t0:s4` | hyphen or dash / high | (12, 0.517241, 11); (2, 0.482759, 22) |
| `bsb_poly1850--fccefa9e9f9823aa--s000-l0111:t0:s1` | hyphen or dash / high | (8, -0.071429, 4); (2, -0.178571, 8); (2, -0.178571, 6); (4, 0.571429, 27); (4, 0.714286, 4) |
| `bsb_poly1850--91657e0569fe07c8--s004-l0040:t1:s2` | hyphen or dash / high | (4, 0.666667, 33) |
| `bsb_poly1850--fccefa9e9f9823aa--s000-l0019:t0:s2` | hyphen or dash / high | (3, 0.659091, 27); (3, 0.886364, 4) |
| `ia_greek_latin--2b4cfc7c6d70fd98--s000-l0006:t2:s14` | hyphen or dash / high | (6, 0.000000, 15); (26, 0.450000, 29) |
| `serbia--e46187046efbc139--s001-l0029:t1:s1` | hyphen or dash / high | (3, 0.560606, 26) |
| `ia_poly1850--b3d418e8a99d8bec--s004-l0117:t0:s3` | raised dot / high | (6, 0.687500, 7) |
| `ia_poly1850--c39403323b6d5d89--s005-l0058:t0:s7` | hyphen or dash / high | (7, -0.215909, 22); (7, -0.215909, 16); (4, 0.613636, 40) |
| `bsb_poly1850--eded5a16c1b78a01--s008-l0104:t0:s1` | hyphen or dash / high | (4, 0.545455, 11) |
| `ia_greek_latin--f42ec9d8d21af31b--s002-l0014:t0:s3` | hyphen or dash / high | (28, 0.457143, 36) |
| `elstat--24e6586813212fd1--s000-l0019:t0:s2` | hyphen or dash / high | (4, 0.650000, 9) |
| `gazette_modern--edef34f5d914488d--s000-l0064:t0:s6` | hyphen or dash / high | (3, -0.053571, 6); (4, 0.500000, 14); (2, 1.071429, 7) |
| `ia_greek_latin--d94cfff6c5bd6428--s004-l0067:t0:s3` | raised dot / high | none |
| `bsb_poly1850--fccefa9e9f9823aa--s000-l0078:t0:s1` | hyphen or dash / high | (3, 0.690476, 27); (4, 0.904762, 3) |
| `lekythos--e9f314aab488b65f--s003-l0076:t0:s2` | hyphen or dash / high | (2, 0.560000, 5) |
| `bsb_poly1850--767e91eee85d9120--s000-l0042:t0:s4` | hyphen or dash / high | (5, 0.585714, 35); (6, 0.771429, 6) |
| `ia_greek_latin--f42ec9d8d21af31b--s000-l0083:t0:s4` | hyphen or dash / high | (28, 0.515152, 35) |
| `ia_greek_latin--7156a8b65e724719--s000-l0019:t0:s0` | hyphen or dash / high | none |
| `lekythos--3bfc4a385d61b883--s002-l0059:t0:s1` | hyphen or dash / high | (5, 0.550000, 23) |
| `ia_poly1850--174d84a441d69a70--s001-l0004:t0:s2` | hyphen or dash / high | (43, 0.528846, 28); (7, 0.682692, 60) |
| `ia_greek_latin--1214ff90d3c31fcb--s003-l0055:t0:s2` | hyphen or dash / high | (2, 0.512821, 17) |
| `gazette_modern--0d828774646bb76b--s000-l0099:t0:s4` | hyphen or dash / high | (4, 0.714286, 6) |
| `elstat--ee37bc488988f1bd--s000-l0508:t0:s3` | raised dot / high | none |
| `serbia--e46187046efbc139--s001-l0012:t1:s1` | hyphen or dash / high | (2, 0.655172, 30) |
| `bsb_poly1850--fccefa9e9f9823aa--s000-l0034:t1:s1` | hyphen or dash / high | (3, 0.580000, 27); (3, 0.780000, 4) |
| `gazette_modern--7f20c8792129c8f6--s000-l0025:t0:s1` | hyphen or dash / high | (4, 0.517241, 8) |
| `bsb_poly1850--767e91eee85d9120--s000-l0039:t3:s3` | hyphen or dash / high | (6, 0.361111, 4); (4, 0.527778, 36); (7, 0.708333, 6) |
| `serbia--e46187046efbc139--s001-l0002:t0:s4` | hyphen or dash / high | (3, 0.596774, 29) |
| `ia_poly1850--c39403323b6d5d89--s005-l0016:t0:s5` | hyphen or dash / high | (4, 0.608696, 40); (1, 1.097826, 3) |
| `bsb_poly1850--97801b0bc5afce27--s005-l0037:t1:s2` | hyphen or dash / high | (4, 0.500000, 36) |
| `ia_greek_latin--5f5319037ff4b70f--s001-l0106:t1:s2` | hyphen or dash / high | (5, 0.500000, 22); (4, 1.000000, 15) |
| `ia_poly1850--ebcfd6056abfa776--s001-l0021:t0:s4` | hyphen or dash / high | (35, 0.447917, 23); (7, 0.531250, 41) |
| `gazette_modern--bd4c89f73f9ccfce--s000-l0047:t0:s22` | hyphen or dash / high | (4, 0.633333, 8) |
| `serbia--557369d8d117b91a--s000-l0237:t0:s2` | raised dot / high | none |
| `bsb_poly1850--97801b0bc5afce27--s005-l0001:t0:s4` | hyphen or dash / high | (20, 0.461538, 39) |
| `ia_greek_latin--7156a8b65e724719--s002-l0004:t0:s3` | hyphen or dash / high | (1, 0.604167, 3) |
| `gazette_modern--f0839209fcdaf7aa--s000-l0072:t0:s1` | hyphen or dash / high | (4, 0.640000, 9) |
| `bsb_poly1850--fccefa9e9f9823aa--s000-l0066:t0:s1` | hyphen or dash / high | (2, 0.560000, 26); (3, 0.740000, 4); (3, 0.740000, 3) |
| `bsb_poly1850--97801b0bc5afce27--s005-l0050:t0:s4` | hyphen or dash / high | (4, 0.523810, 35) |
| `bsb_poly1850--fccefa9e9f9823aa--s000-l0005:t0:s1` | hyphen or dash / high | (5, 0.704545, 26); (4, 0.954545, 4) |
| `elstat--24e6586813212fd1--s000-l0039:t0:s3` | hyphen or dash / high | (4, 0.590909, 9) |
| `ia_greek_latin--f42ec9d8d21af31b--s000-l0068:t0:s2` | hyphen or dash / high | (28, 0.432432, 56) |
| `kosmopolis--ef37f6cfdd896488--s001-l0012:t0:s1` | hyphen or dash / high | (7, -0.166667, 11); (11, -0.092593, 12); (6, -0.185185, 12); (18, 0.518519, 11); (2, 0.592593, 19); (3, 1.092593, 5); (2, 1.111111, 4) |
| `ia_poly1850--21c15fc15dc17003--s003-l0126:t0:s3` | hyphen or dash / high | (7, 0.671053, 45) |
| `gazette_modern--bd4c89f73f9ccfce--s000-l0047:t0:s10` | hyphen or dash / high | (4, 0.633333, 8) |
| `elstat--ee37bc488988f1bd--s000-l0531:t0:s3` | raised dot / high | none |
| `bsb_poly1850--767e91eee85d9120--s006-l0039:t2:s4` | hyphen or dash / high | (25, 0.445946, 15); (4, 0.513514, 31); (6, 0.675676, 5) |
| `serbia--557369d8d117b91a--s000-l0356:t0:s85` | hyphen or dash / high | (16, 0.464286, 10); (2, 0.535714, 20); (9, 0.767857, 3) |
| `serbia--557369d8d117b91a--s000-l0356:t0:s73` | hyphen or dash / high | (31, 0.410714, 2); (3, 0.589286, 19); (8, 0.785714, 4) |
| `bsb_poly1850--97801b0bc5afce27--s005-l0038:t0:s2` | hyphen or dash / high | (4, 0.550000, 35) |
| `gazette_modern--b12da9e27bc9bf26--s000-l0035:t0:s3` | hyphen or dash / high | (4, 0.555556, 8) |
| `ia_poly1850--ebcfd6056abfa776--s006-l0050:t1:s2` | hyphen or dash / high | (5, 0.521277, 39) |
| `gazette_modern--2e613d9290dd13d4--s000-l0291:t0:s2` | hyphen or dash / high | (13, 0.681818, 63); (4, 0.727273, 9) |
| `ia_greek_latin--7156a8b65e724719--s002-l0041:t0:s2` | hyphen or dash / high | (2, 0.700000, 4) |
| `elstat--ee37bc488988f1bd--s000-l0564:t0:s3` | raised dot / high | (3, 0.694444, 3) |
| `lekythos--a0c4e6327052acfc--s002-l0072:t0:s1` | hyphen or dash / high | none |
| `ia_poly1850--a89bd2c9bdb1ca6d--s006-l0044:t1:s3` | hyphen or dash / high | (8, 0.538462, 44) |
| `gazette_modern--26e789637e8f101b--s000-l0060:t0:s4` | hyphen or dash / high | (4, 0.531250, 9) |
| `ia_russian--3ecca278cf0eea22--s001-l0004:t0:s4` | hyphen or dash / high | (6, 0.450000, 63) |
| `lekythos--dd72392a3777225e--s001-l0061:t0:s2` | hyphen or dash / high | (4, 0.529412, 11) |
| `elstat--ee37bc488988f1bd--s000-l0052:t0:s3` | raised dot / high | none |
| `ia_poly1850--ebcfd6056abfa776--s003-l0011:t0:s4` | hyphen or dash / high | (9, 0.578431, 47) |
| `bsb_poly1850--2032df1e3e983f1d--s002-l0025:t0:s2` | hyphen or dash / high | (4, 0.578947, 28) |
| `gazette_modern--99a7fdc8f55ef76b--s000-l0012:t0:s4` | hyphen or dash / high | (4, 0.575758, 16) |
| `gazette_modern--fa9ff9250edfcd31--s000-l0059:t3:s1` | hyphen or dash / high | (5, 0.564516, 8); (4, 1.032258, 12); (4, 1.032258, 12) |
| `gazette_modern--7f20c8792129c8f6--s000-l0026:t0:s9` | hyphen or dash / high | (3, 0.534483, 8) |
| `ia_poly1850--5aa15e93b2f445b8--s003-l0009:t0:s4` | hyphen or dash / high | (11, 0.574324, 53) |
| `bsb_poly1850--eded5a16c1b78a01--s000-l0110:t1:s2` | raised dot / low | (4, 0.589744, 6) |
| `ia_poly1850--c39403323b6d5d89--s005-l0053:t1:s6` | hyphen or dash / high | (3, 0.544444, 42); (1, 1.277778, 5); (1, 1.277778, 4) |
| `gazette_modern--2e613d9290dd13d4--s000-l0139:t0:s2` | hyphen or dash / high | (4, 0.666667, 11) |
| `bsb_poly1850--fccefa9e9f9823aa--s000-l0045:t1:s1` | hyphen or dash / high | (4, 0.571429, 27); (4, 0.750000, 4) |
| `gazette_modern--edef34f5d914488d--s000-l0094:t0:s3` | hyphen or dash / high | (4, 0.500000, 14) |
| `ia_greek_latin--d15eca050847acdb--s003-l0020:t1:s3` | hyphen or dash / high | (3, 0.561224, 25) |
| `bsb_poly1850--97801b0bc5afce27--s004-l0003:t0:s3` | hyphen or dash / high | (4, 0.520833, 23) |
| `gazette_modern--54f1f0595779ed67--s000-l0047:t1:s1` | hyphen or dash / high | (21, 0.486111, 61) |
| `ia_greek_latin--f42ec9d8d21af31b--s002-l0100:t0:s3` | hyphen or dash / high | (4, 0.513514, 20) |
| `kosmopolis--91040f2da70b9ae0--s000-l0028:t0:s4` | hyphen or dash / high | (3, 0.562500, 22) |
| `elstat--ee37bc488988f1bd--s000-l0943:t0:s3` | raised dot / high | (3, 0.794118, 4) |
| `elstat--24e6586813212fd1--s000-l0020:t1:s2` | hyphen or dash / high | (3, 0.500000, 8) |
| `serbia--81b7d5929109c0ad--s000-l0011:t0:s1` | hyphen or dash / high | none |
| `elstat--ee37bc488988f1bd--s000-l0648:t0:s4` | raised dot / high | (4, 0.722222, 3) |
| `ia_greek_latin--1214ff90d3c31fcb--s003-l0006:t1:s2` | hyphen or dash / high | (24, 0.500000, 37) |
| `elstat--ee37bc488988f1bd--s000-l0705:t0:s2` | raised dot / high | none |
| `bsb_poly1850--515c78c513c1c8c5--s005-l0101:t0:s2` | hyphen or dash / high | (6, 0.558824, 10) |
| `gazette_modern--2e613d9290dd13d4--s000-l0026:t0:s2` | hyphen or dash / high | (4, 0.636364, 10); (3, 1.045455, 3) |
| `gazette_modern--6c02a5264ac1b8a3--s000-l0003:t1:s4` | hyphen or dash / high | (1, -0.113636, 3); (1, -0.113636, 10); (23, 0.613636, 756); (4, 0.636364, 8) |
| `elstat--ee37bc488988f1bd--s000-l0229:t0:s1` | raised dot / high | none |
| `elstat--07520765bc203a33--s000-l0417:t0:s2` | raised dot / high | none |
| `ia_poly1850--5aa15e93b2f445b8--s001-l0016:t0:s4` | hyphen or dash / high | (6, 0.500000, 66) |
| `gazette_modern--7f20c8792129c8f6--s000-l0048:t0:s7` | hyphen or dash / high | (3, 0.558824, 4) |
| `elstat--24e6586813212fd1--s000-l0135:t0:s3` | hyphen or dash / high | (4, 0.500000, 6) |
| `gazette_modern--bd4c89f73f9ccfce--s000-l0045:t0:s1` | hyphen or dash / high | (6, 0.030303, 4); (4, 0.575758, 8); (1, 1.045455, 5) |
| `bsb_poly1850--fccefa9e9f9823aa--s000-l0063:t1:s1` | hyphen or dash / high | (4, 0.636364, 28); (3, 0.886364, 3) |
| `serbia--557369d8d117b91a--s000-l0356:t0:s79` | hyphen or dash / high | (8, 0.068966, 2); (8, 0.551724, 2); (3, 0.568966, 19); (7, 0.741379, 5) |
| `elstat--ee37bc488988f1bd--s000-l0184:t0:s4` | raised dot / high | none |
| `bsb_poly1850--767e91eee85d9120--s004-l0147:t0:s2` | hyphen or dash / high | (4, 0.625000, 32) |
| `elstat--24e6586813212fd1--s000-l0072:t0:s3` | hyphen or dash / high | (13, 0.593750, 38) |
| `ia_poly1850--21c15fc15dc17003--s003-l0057:t0:s3` | hyphen or dash / high | (7, 0.671053, 43) |
| `serbia--557369d8d117b91a--s000-l0185:t0:s27` | hyphen or dash / high | none |
| `ia_greek_latin--f42ec9d8d21af31b--s002-l0005:t0:s3` | hyphen or dash / high | (3, 0.500000, 20) |
| `lekythos--dcfa99599048d352--s000-l0144:t0:s1` | hyphen or dash / high | (2, 0.650000, 6) |
| `bsb_poly1850--767e91eee85d9120--s006-l0039:t1:s3` | hyphen or dash / high | (3, 0.500000, 28) |
| `gazette_modern--0d828774646bb76b--s000-l0065:t0:s4` | hyphen or dash / high | (4, 0.736842, 6) |
| `ia_poly1850--007d7039d12e3816--s007-l0035:t0:s2` | hyphen or dash / high | (7, 0.541667, 53) |
| `gazette_modern--2e613d9290dd13d4--s000-l0290:t0:s2` | hyphen or dash / high | (5, 0.586957, 10) |
| `ia_greek_latin--8e74f3b971703ae0--s007-l0013:t0:s4` | hyphen or dash / high | (7, 0.376923, 14) |
| `gazette_modern--f9ac91c777f49b67--s000-l0009:t0:s2` | hyphen or dash / high | (5, -0.217949, 15); (6, -0.205128, 9); (6, -0.205128, 7); (3, 0.423077, 14); (5, 0.525641, 4) |
| `gazette_modern--edef34f5d914488d--s000-l0097:t0:s4` | hyphen or dash / high | (4, 0.533333, 15) |
| `elstat--24e6586813212fd1--s000-l0075:t0:s2` | hyphen or dash / high | (14, 0.529412, 15); (13, 0.558824, 18) |
| `ia_poly1850--c39403323b6d5d89--s004-l0048:t1:s5` | hyphen or dash / high | (4, 0.685714, 38) |
| `gazette_modern--93b0532cc3deb43d--s000-l0024:t1:s2` | hyphen or dash / high | (3, 0.557692, 7) |
| `bsb_poly1850--fccefa9e9f9823aa--s000-l0073:t0:s1` | hyphen or dash / high | (4, -0.100000, 4); (3, 0.675000, 27); (4, 0.900000, 3) |
| `gazette_modern--0d828774646bb76b--s000-l0051:t0:s1` | hyphen or dash / high | none |
| `gazette_modern--2e613d9290dd13d4--s000-l0344:t0:s2` | hyphen or dash / high | (11, 0.590909, 8); (4, 0.727273, 10) |
| `bsb_poly1850--767e91eee85d9120--s002-l0030:t0:s2` | hyphen or dash / high | (3, 0.559524, 40); (6, 0.738095, 5) |
| `bsb_poly1850--fccefa9e9f9823aa--s000-l0035:t1:s1` | hyphen or dash / high | (4, 0.615385, 27); (3, 0.788462, 4) |
| `ia_poly1850--a89bd2c9bdb1ca6d--s003-l0122:t0:s4` | hyphen or dash / high | (7, 0.008929, 13); (9, 0.544643, 46) |
| `gazette_modern--bd4c89f73f9ccfce--s000-l0047:t0:s20` | hyphen or dash / high | (20, 0.533333, 14); (4, 0.633333, 8) |
| `gazette_modern--bd4c89f73f9ccfce--s000-l0047:t0:s8` | hyphen or dash / high | (4, 0.633333, 8) |
| `elstat--ee37bc488988f1bd--s000-l0725:t0:s1` | raised dot / high | none |
| `bsb_poly1850--767e91eee85d9120--s004-l0082:t0:s2` | hyphen or dash / high | (3, 0.583333, 33) |
| `ia_greek_latin--1214ff90d3c31fcb--s002-l0061:t0:s3` | hyphen or dash / high | (3, 0.562500, 22) |
| `ia_greek_latin--1214ff90d3c31fcb--s000-l0001:t0:s3` | hyphen or dash / high | (3, 0.608108, 22) |
| `bsb_poly1850--fccefa9e9f9823aa--s000-l0052:t0:s1` | hyphen or dash / high | (3, 0.690476, 27); (3, 0.928571, 4) |
| `bsb_poly1850--767e91eee85d9120--s004-l0038:t0:s2` | hyphen or dash / high | (3, 0.660000, 33) |
| `ia_russian--3ecca278cf0eea22--s001-l0004:t1:s4` | hyphen or dash / high | (7, 0.441667, 56) |
| `elstat--ee37bc488988f1bd--s000-l0757:t0:s2` | raised dot / high | none |
| `ia_russian--3ecca278cf0eea22--s003-l0047:t0:s2` | hyphen or dash / high | (26, 0.310345, 22); (3, 0.508621, 50); (4, 0.568966, 3); (12, 0.706897, 22) |
| `elstat--24e6586813212fd1--s000-l0042:t0:s2` | hyphen or dash / high | (3, 0.617647, 6) |
| `gazette_modern--1f7db88d63c02afa--s000-l0072:t0:s3` | raised dot / high | none |
| `ia_russian--3ecca278cf0eea22--s002-l0051:t0:s2` | hyphen or dash / high | (42, 0.403226, 23); (5, 0.475806, 56); (1, 1.137097, 3) |
| `gazette_modern--0d0b2233a81e355c--s000-l0054:t0:s1` | hyphen or dash / high | (3, 0.565789, 13); (3, 0.592105, 15) |
| `ia_greek_latin--7156a8b65e724719--s002-l0013:t0:s3` | hyphen or dash / high | (3, 0.557692, 3) |
| `ia_greek_latin--202a95a447dece04--s000-l0132:t0:s3` | hyphen or dash / high | (23, 0.557143, 55) |
| `ia_poly1850--3bfe0ab3a504d025--s007-l0002:t0:s2` | hyphen or dash / high | (6, 0.636364, 50) |
| `gazette_modern--f375bcf80bc8fca3--s000-l0090:t0:s4` | hyphen or dash / high | (12, -0.028571, 4); (4, 0.542857, 16) |
| `bsb_poly1850--fccefa9e9f9823aa--s000-l0105:t1:s1` | hyphen or dash / high | (3, 0.574074, 26); (4, 0.740741, 4) |
| `elstat--ee37bc488988f1bd--s000-l0449:t0:s1` | raised dot / high | none |
| `bsb_poly1850--767e91eee85d9120--s004-l0074:t0:s2` | hyphen or dash / high | (4, 0.586207, 34) |
| `bsb_poly1850--9342f9a56a4065cd--s001-l0011:t1:s0` | hyphen or dash / high | (17, 0.125000, 60); (31, 0.413462, 26) |
| `gazette_modern--a5a65c413f92193f--s000-l0053:t0:s1` | hyphen or dash / high | (22, 0.514286, 42); (21, 0.528571, 9); (2, 1.057143, 3); (2, 1.057143, 6) |
| `elstat--df38bce62200e7db--s000-l0004:t0:s4` | hyphen or dash / high | (3, 0.625000, 6) |
| `ia_poly1850--ebcfd6056abfa776--s007-l0032:t1:s13` | hyphen or dash / high | (7, 0.510417, 41) |
| `gazette_modern--0d828774646bb76b--s000-l0088:t0:s4` | hyphen or dash / high | (3, 0.704545, 7) |
| `elstat--24e6586813212fd1--s000-l0040:t1:s3` | hyphen or dash / high | (3, 0.520833, 8) |
| `lekythos--40ed3fea207e3d94--s000-l0290:t0:s2` | hyphen or dash / high | (13, 0.568966, 12); (3, 0.534483, 27) |
| `ia_russian--3ecca278cf0eea22--s004-l0033:t0:s4` | hyphen or dash / high | none |
| `ia_poly1850--a89bd2c9bdb1ca6d--s003-l0037:t0:s3` | hyphen or dash / high | (7, 0.548077, 46); (1, 1.067308, 10) |
| `gazette_modern--f9ac91c777f49b67--s000-l0107:t0:s2` | hyphen or dash / high | (3, -0.209677, 3); (10, -0.096774, 4); (8, -0.129032, 10); (4, -0.193548, 15); (3, 0.564516, 14); (5, 0.693548, 4) |

## Owner sheet

`artifacts/n1/owner_sheet/n1_sheet.html`: **5.816 MB**, 123 cards; 12 seeded high-confidence agreement slots. Proposed rows: 15. Printed fields are blank. Every card uses its slot-specific doc ID; only one code point changes in each Proposed row, preserving offsets. All Google rows come from W1 features `text`, checked against frame gap offsets.

The prescribed cleanup renderer was used under the collector interpreter with cleanup PYTHONPATH. Its `slot` argument binds note identity but does not draw numeric gap boxes; this builder overlays a thin box from the saved geometry on each saved line image, leaving the marked 3× zoom unchanged. The cleanup worktree was read only. This HTML is built for coordinator publication; no publication or owner adjudication is claimed.

| Group | Cards |
|---|---:|
| Hyphen printed as raised dot | 15 |
| Dot printed as raised dot | 0 |
| Other mark disagreements | 65 |
| Unreadable or low confidence | 31 |
| Agreement sample | 12 |

Group counts are mutually exclusive. Summary `other disagreements` excludes unreadable/other/low-confidence slots and raised-dot transitions; `unreadable/low` includes other. Thus headline transitions and uncertainty may overlap, while sheet groups do not.

Saved probe evidence (not refreshed; no reading launcher invoked): 38.0% weekly, from ctx07 run receipt. This is historical usage, not a live probe.

Validation: **52 tests passed** (20 new N1-S cases). One existing artifact-closure test was deselected after a broader run returned 51 passed / 1 failed: `tests/test_n1cd.py::test_real_pack_coverage_and_v3_images` compares a frozen pre-reading manifest with external packs that now contain reading-time `answers.jsonl` and `zoom/check*.png`. Those files and the test are preserved. The passing suite covers the new gate (including unreadable abstentions), exact-gap table, one-gap U+00B7 rewrite with preserved offsets, design weighting, structural zeros, real output scope and card contents, plus existing mapper/geometry/control/launcher contracts. Details: `artifacts/n1/N1S_TESTS.json` and JUnit XML.

Browser layout QA was unavailable because neither local Playwright browser executable exists; no browser download or network request was made. Structural HTML validation confirms 123 unique cards, 123 blank Printed fields, Google row presence and the size cap; visible layout is not claimed.
