# Lexicon report (labelfix)

Built by `python -m greekocr.labelfix.build_lexicon`. Forms are NFD, lower-cased, edge punctuation
stripped; all-caps words dropped; tokens with Latin letters or digits dropped. Only born-digital,
human-typed or human-proofread text; no Google Document AI output and no recogniser output.
Regime purity: polytonic regimes admit only lines that carry a polytonic-only mark (breathing,
varia, perispomeni, ypogegrammeni); the monotonic regime admits only lines without one.

## Held-out exclusion

Lines of a source that share a 4-word shingle with an evaluation line are excluded: 220010 shingles
from:

- `docs/records/harvest/collection/v2/import_real_v2_test.jsonl`: 44029 lines
- `/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr/out/e3b/predictions/full_s0_wikisource_human.jsonl`: 1392 lines

Whole works are excluded by title stem (25 stems from the eval records' Wikisource URLs):

- apollonii rhodii argonautica (1900)
- athides aurai georgios vizyinos
- ésope - fables - émile chambry
- αριστοτέλης βαλαωρίτης - υπό ε. δ. ροϊδου
- αττικά ή περί δήμων αττικής εν οις και περί τινων μερών του άστεως
- βίοι πελοποννησίων ανδρών
- διήγησις ακριβής όπως εβαπτίσθη το των ρώσσων έθνος
- διηγήματα (αξιώτης)
- διονύσου πλους
- ελεγεία και σάτιρες
- εστία αριθμός 658
- εστία αριθμός 659
- η α. θ. παναγιότης ο άνθιμος ο ζ. εν καλύμνω
- λόγια της πλώρης (1924)
- περί νομίσματος και της κτητικής δυνάμεως των πολύτιμων μετάλλων κατά τους βυζαντινούς χρόνους
- περί του ανατολικού ζητήματος δημήτριος αινιάν
- анна каренина part 1-4
- аркадий аверченко - синее съ золотомъ (пбг 1917)
- бальмонт. полное собрание стихов. том 04
- березин - ледяной плен
- война ; аринушка ; на передовых позициях ; вблизи перемышля (петров-скиталец, 1916)
- горнфельд а. г. новые словечки и старые слова. 1922
- дарвин - биографический очерк ребёнка
- дарвин - о происхождении видов, 1864
- дешевая юмористическая библиотека нового сатирикона, выпуск 23

## Regimes and sources

| regime | source | evidence of human provenance | lines read | lines used | excluded (held-out work) | excluded (eval overlap) | excluded (other regime) | tokens | cap |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| ancient | first1k_greek | OpenGreekAndLatin First1KGreek TEI editions (scholarly, corrected); CC-BY-SA-4.0 | 1022385 | 1007553 | 0 | 7677 | 7155 | 13817039 | none |
| ancient | klasikh_arx_ell_grammateia | classical Greek literature editions, born-digital; CC-BY-SA-4.0 | 889828 | 872597 | 0 | 3646 | 13585 | 10716932 | none |
| ancient | perseus_greeklit_tei | Perseus canonical-greekLit TEI body text @ 0189b9c8 (choice->sic/orig); CC-BY-SA-4.0 | 377099 | 362008 | 5901 | 3077 | 6113 | 9006747 | none |
| ancient | first1k_greek_tei | First1KGreek TEI body text @ 03776b39 (choice->sic/orig); CC-BY-SA-4.0 | 471505 | 426366 | 3008 | 12613 | 29518 | 21593990 | none |
| poly19 | wikisource_el | Greek Wikisource human transcriptions (dump); CC-BY-SA | 651876 | 639633 | 3045 | 9198 | 0 | 14361729 | none |
| mono | gutenberg_el | Project Gutenberg Greek ebooks, Distributed Proofreaders human-keyed; PD-US; the copies on disk are monotonic transcriptions (0 lines with a polytonic-only mark), so they attest the monotonic regime | 129601 | 127285 | 0 | 2311 | 5 | 1181308 | none |
| mono | finewiki_el | Greek Wikipedia (finewiki), born-digital; CC-BY-SA-4.0 | 931643 | 897756 | 0 | 29829 | 4058 | 9028444 | none |
| mono | eurlex_el | EUR-Lex Greek legislation, born-digital; EUPL-1.2 | 748925 | 701605 | 0 | 44217 | 3103 | 6616428 | none |
| mono | europarl_el | European Parliament Greek data, born-digital | 1000307 | 927776 | 0 | 71473 | 1058 | 9669074 | none |

| regime | distinct forms | forms with count >= 5 | tokens | proper-name keys (>= 3 mid-sentence capitalised) |
|---|---:|---:|---:|---:|
| ancient | 1048153 | 353002 | 55134708 | 58288 |
| poly19 | 686150 | 160364 | 14361729 | 31688 |
| mono | 417399 | 115151 | 26495254 | 52409 |

Lookup is inflection-aware: a form counts if it, its grave->acute variant, or (for two-accent words) the
form without the enclitic-induced second accent is attested. Held-out ancient works excluded from the TEI
sources by id: tlg0001.tlg001, tlg0096.

## Sources considered and excluded

- estianews: house style prints acute for grave (no varia): would attest the wrong final-syllable accent
- parliament_dl: provenance=ocr
- openbook_gr: provenance=ocr (OCR-mixed)
- Ekklisiastika_Keimena: liturgical register with many all-caps rubrics and doc greek_badness ~29; not needed
- Wikisource_Greek_texts (nanochat copy): same source as wikisource_el_lines; avoid double counting
- Sxolika_vivlia / greek_legal_code / HPLT / greek_phd: provenance uncertain or web-crawled; not proofread
- perseus_greeklit: listed in data/sources.json but not on disk
- wikinews_el: listed in data/sources.json but not on disk

Source files live under `~/Projects/greek-page-ocr/data/raw/` (see `data/sources.json` there).
