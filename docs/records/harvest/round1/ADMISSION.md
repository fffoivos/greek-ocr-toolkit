# T20 — Wave 0 line admission

75,061 DocAI lines on 1,532 pages from 130 books. **61,882 admitted, 13,179 rejected, 61,882 native grey crops.** Local, offline; no new Google calls or Git writes.

Admission evaluates every failing rule in order. Confidence is the stored mean of anchored DocAI symbols; the legacy `tier`, Vision reading and `counted` flag do not decide admission. Inventory uses the supplied Unicode code points; label normalization occurs after the gates.

The low-confidence page denominator is all lines with at least 10 letters; the tall-box denominator is all provider lines. Thresholds are strictly greater than 50% and 30%. Greek-majority lines with a whole Latin word of at least two letters take the code-switch class first; letter-count ties resolve Greek, Latin, Cyrillic. Roman tokens using only IVXLC and Greek Ι/Χ are exempt from mixed-word rejection. Unicode decimal digits are counted as digits; shared Greek sentence punctuation is `. , ; : ! ? · ; · … « » ' ’ ‘ ᾽`; other nonspace nonletters are other symbols.

Crop neighbours are the nearest distinct-centre rows above/below sharing at least half the narrower horizontal extent, computed from **all** DocAI lines on the page. Provider-order column jumps and equal-centre fragments are not vertical neighbours. Trimming uses overlap greater than 15% of the original line height, then midpoint cuts, outward pixel rounding, and 2 px vertical / 4 px horizontal padding inside the page. Original `bbox` and actual `crop_bbox` are both retained. No crop is resized. Duplicate DocAI boxes are retained when the stated text gates admit their lines; physical label accuracy remains for owner review.

## Class × split

| Class | Train | Dev | Test | Total |
|---|---:|---:|---:|---:|
| greek_poly | 46596 | 3205 | 8172 | 57973 |
| greek_mono | 1374 | 124 | 223 | 1721 |
| greek_latin_cs | 903 | 22 | 101 | 1026 |
| latin | 1078 | 14 | 70 | 1162 |
| cyrillic | 0 | 0 | 0 | 0 |

## Rejection reasons

A rejected line may occur in several rows.

| Reason | Lines |
|---|---:|
| short_line | 8632 |
| low_confidence | 4786 |
| tall_box | 1112 |
| symbol_heavy | 5560 |
| foreign_script | 93 |
| mixed_word | 117 |
| bad_page | 152 |
| label_in_holdout | 221 |

## Decades

| Decade | Books | Held-out books | Train | Dev | Test | Rejected |
|---|---:|---:|---:|---:|---:|---:|
| 1860s | 12 | 4 | 3767 | 961 | 1023 | 874 |
| 1870s | 13 | 2 | 5944 | 844 | 982 | 2628 |
| 1880s | 18 | 2 | 3594 | 0 | 869 | 679 |
| 1890s | 18 | 2 | 6214 | 0 | 655 | 1577 |
| 1900s | 24 | 3 | 9740 | 0 | 2068 | 2971 |
| 1910s | 19 | 3 | 8547 | 934 | 1211 | 2039 |
| 1920s | 25 | 3 | 12145 | 626 | 841 | 2214 |
| 1930s | 1 | 1 | 0 | 0 | 917 | 197 |

## Held-out books

Seed 20261015; two per decade where capacity allows, then seeded draws from remaining books with ≥300 admitted lines before fallback books. A seeded shuffle assigns five dev and fifteen test books. Counts in this table are after admission and before O5 (O5 drops train only).

**Capacity exception:** 1930s has only 1 round-1 book; selected all 1, so the requested two cannot be supplied.

| Book key | Title | Year | Decade | Split | Admitted lines |
|---|---|---:|---:|---|---:|
| 8a77bd3f3cff4d5e3bec99f0 | Περί Δωδώνης :  πραγματεία μετά λιθογραφικού πίνακος /  Γ. Χ. Χασιώτου. | 1867 | 1860 | dev | 479 |
| db1ed5f902d696fb53656a7d | Σύντομος βιογραφία του αοιδίμου Pήγα Φεραίου του Θετταλού /  Χρ. Περραιβού. | 1860 | 1860 | dev | 482 |
| f07e2d5bdef7328dfb1671bf | Βίος του Αλή πασά εκ Τεπελενίου της Ηπείρου επονομασθέντος Ασλάν ή Λέοντος /  υπό Ρ. Α. Δάβενπορτ, μεταφρασθείς υπό του καθηγητού της ήδη καταργηθείσης εν Αργοστολίω Αγγλικής Σχολής Αναστ. Κ. Μπίτζη και εκδοθείς υπό Κωνσταντίνου Γ. Φιλιππίδου και Θεοδώρου Γ. Πεφάνη. | 1866 | 1860 | test | 522 |
| ffe26907d1e3e9c1f75337e2 | Ζιλβλάς του Σαντιλλάν :  Ιστορία /  υπό Λεσάζ μεταφρασθείσα εκ του γαλλικού υπό κωνστ. Χειμωνίου. Εκδίδεται δε εις τόμους τρείς υπό Σ. Δ. Χάμπα. | 1862 | 1860 | test | 501 |
| 18ed614c7b7c25896c49680b | Δοκίμιον εκκλησιαστικής ιστορίας :  χάριν των περί την θεολογίαν σπουδαζόντων /  υπό Α. Διομήδους Κυριακού ... | 1878 | 1870 | test | 982 |
| a588c9878d5b1197798bb2c5 | Στοιχεία Φυσικής Πειραματικής /  Υπό Αντωνίου Β. Δαμασκηνού... | 1871 | 1870 | dev | 844 |
| cf2272f4329d987f840e81ab | Ορθόδοξος Ιερά Κατήχησις :  (Κατ' ερωταπόκρισιν) /  Συναρμολογηθείσα υπό Β. Δ. Καλλίφρονος, προς χρήσιν και διδασκαλίαν εν τοις ορθοδόξοις εκπαιδευτηρίοις, ... | 1886 | 1880 | test | 414 |
| f0acb2fc3dab2a9bb69f8726 | Μελετήματα ιστολογικά /  Εκδιδόμενα υπό Δημητρίου Χασιώτου ... | 1882 | 1880 | test | 455 |
| 3a65f68ff36d911f4ca179e8 | Εθνικά άσματα της Ελλάδος :  1453-1821 /  Εταιρεία ο "Ελληνισμός". | 1896 | 1890 | test | 305 |
| 4f1e627418cc5d716264fa7d | Αρχαία μνημεία Ναυπλίας και Άργους :  ήτοι οδηγός Ναυπλίου, Ακροναυπλίας, Παλαμηδίου ___ /  Υπό Σπυριδ. Κ. Προφαντοπούλου ___ | 1895 | 1890 | test | 350 |
| 480b788bb2f6e216f3898c02 | Αντιπελαργήσεως Κωνστ. Παγώνη (Μ. αρχιδιακόνου) έλεγχος /  υπό μητροπολ. Θηβαΐδος Γερμανού. | 1900 | 1900 | test | 513 |
| 6976af7d6e1671818ccf9781 | Παναγιοταφικαί εντυπώσεις /  Σεβαστιανού Νικοκάβουρα. | 1904 | 1900 | test | 653 |
| b8b71bfd410ddd2e68429ffe | Το μέλλον των Αθηνών /  υπό A. N. Bερναρδάκη. | 1902 | 1900 | test | 902 |
| 55beb2ad05d46b48576a486d | Ο κακός δρόμος :  κι άλλα καινούρια διηγήματα (1908-1911) /  Γρ. Ξενόπουλου, πρόλογ. Ιω. Ζερβού. | 1912 | 1910 | dev | 934 |
| 97da3257b5224e86be9547da | Η οθωμανική Θράκη :  Μετά γεωγραφικού και ιστορικού χάρτου και καλλιτεχνικών εικόνων /  Αλεξάνδρου Δ. Βασιλοπούλου. | 1914 | 1910 | test | 623 |
| 98d73c3573628c15b861d2ce | Γεωργική έρευνα της Μακεδονίας ήτοι μελέτη της γεωργικής καταστάσεως του κτηνοτροφικού πλούτου, των δασών και της βιομηχανικής παραγωγης κατά περιφερείας Α' της Δυτικής Μακεδονίας Β' της Ανατολικής Μακεδονίας. | 1914 | 1910 | test | 588 |
| 161d241aad02594d3c0272e7 | Νεοελληνικά αναγνώσματα :  Μετά προσωπογραφιών των συγγραφέων και εικόνων σχετικών προς τα κείμενα, δια τους μαθητάς της Α' τάξεως των Ελληνικών σχολείων /  Ιωάννου Πολέμη. | 1920 | 1920 | dev | 626 |
| 73e10362c99c1be82977a983 | Παράλληλοι εικόνες /  Α. Ξ. Καραπαναγιώτου. | 1929 | 1920 | test | 368 |
| c956015742d213237900264d | Η συμβολή των Ελλήνων εις την τομήν της διώρυχος του Σουέζ /  Κ. Ν. Φραγκούλη. | 1924 | 1920 | test | 473 |
| cbe5e7b92d36edf08153017b | Γαλάτη :  Νέον όργανον /  Περικλέους Κ. Άλτηντοπ. | 1930 | 1930 | test | 917 |

O5 removed **221 train lines** equal to an admitted dev/test label. Equality is NFC and whitespace-collapsed, with DOT ABOVE already converted to middle dot; case and other marks are preserved.

## Native crop sizes

| Measure | Min | p05 | Median | Mean | p95 | Max |
|---|---:|---:|---:|---:|---:|---:|
| width px | 52 | 295 | 738.0 | 700.90 | 911 | 1706 |
| height px | 11 | 32 | 40.0 | 40.80 | 49 | 261 |

Trimmed: 28,960. Labels with standalone spacing marks: 6. Spacing U+1FBF/U+1FBD/U+0384 marks between letters remain unchanged; the flag records them for a later label decision.

## Contact sheets

The sheets are seeded after admission and O5, with one 20 px label type size. Crops may be reduced for the sheet only. Owner accuracy review is pending.

| Class | Unique examples | Sheet |
|---|---:|---|
| greek_poly | 60 | `docs/records/harvest/harvest_big/round1/admission_sheet/greek_poly.jpg` |
| greek_mono | 60 | `docs/records/harvest/harvest_big/round1/admission_sheet/greek_mono.jpg` |
| greek_latin_cs | 60 | `docs/records/harvest/harvest_big/round1/admission_sheet/greek_latin_cs.jpg` |
| latin | 60 | `docs/records/harvest/harvest_big/round1/admission_sheet/latin.jpg` |
| cyrillic | 0 | `docs/records/harvest/harvest_big/round1/admission_sheet/cyrillic.jpg` |

## Bad pages

| Page | Eligible lines | Low-confidence lines | Tall / all | Triggers |
|---|---:|---:|---|---|
| 00c322b3ee04b419d1979f22-p000069 | 9 | 7 | 4 / 46 | low_confidence |
| 42c339ce492d83665f00774d-p000080 | 41 | 0 | 24 / 52 | tall_boxes |
| 928e34aaaa78469aacd6c7ef-p000042 | 23 | 13 | 1 / 24 | low_confidence |
| a30e828662f14c20f8994268-p000024 | 29 | 20 | 1 / 30 | low_confidence |

## Ten example mixed words

| Word | Line |
|---|---|
| Δὸr | 66112e132fd96ac8e30e5328-p000016-l0015 |
| ΚΕΦΑΛΑΙΟON | ffe26907d1e3e9c1f75337e2-p000193-l0015 |
| ΚΕΦΑΛΑION | f07e2d5bdef7328dfb1671bf-p000030-l0002 |
| διF | 8a77bd3f3cff4d5e3bec99f0-p000012-l0014 |
| δυτικοβо | 8a77bd3f3cff4d5e3bec99f0-p000081-l0009 |
| μαγνητικὰa | a588c9878d5b1197798bb2c5-p000239-l0083 |
| ποόςㄹ | 292f4a0b4f0dc8e6dddb103d-p000573-l0030 |
| ΛΙΟΘIKT | 4fb1fdd9b2f3f5caa8e0be18-p000035-l0032 |
| αυλιデスメタOY | 727f1e3f8d0a3a622943e9b1-p000077-l0044 |
| πえん | 727f1e3f8d0a3a622943e9b1-p000077-l0049 |

## Rejected examples

Up to 30 actual lines per reason; all available are shown when fewer exist. Text is the original DocAI text, with Markdown delimiters escaped and whitespace displayed.

### short_line (30 examples)

| Line | All reasons | DocAI text |
|---|---|---|
| 66112e132fd96ac8e30e5328-p000113-l0061 | short_line | ΟΤΒΕΡΤΟΣ. |
| 6389d36a8d20c1541b1d4bcb-p000068-l0009 | short_line, low_confidence, symbol_heavy | (Ὁμ. Οδυσ. Α. Ι.) |
| cc0e056392dd2ef4916b3e7d-p000016-l0018 | short_line, low_confidence | Καὶ φαιδ |
| e28081a0d8ed58a169d0b77d-p000175-l0052 | short_line | M |
| 042c93b2591368d437f27678-p000292-l0030 | short_line | αὐτόθι). |
| 0bff55647d1c2acd1caa8bf3-p000247-l0026 | short_line | ΜΑΝΟΥΗΛ |
| 0907df739607faca673d2169-p000039-l0069 | short_line, symbol_heavy | (1) Μαντι- |
| 6296ac8dc850e29e2fa2f0b1-p000179-l0031 | short_line | παραλία: |
| ffe26907d1e3e9c1f75337e2-p000118-l0002 | short_line, low_confidence, symbol_heavy | 120 |
| c10815de32006dc7d7354073-p000057-l0017 | short_line | Ἰωάννης |
| bf2ce6d100950eec319cef00-p000010-l0045 | short_line, symbol_heavy | 215 |
| bb8faba1e9b543fe5a1ce6dd-p000168-l0021 | short_line, symbol_heavy | ** |
| 686431e9a7fe04175e6e9be9-p000112-l0055 | short_line | mes- |
| f07e2d5bdef7328dfb1671bf-p000070-l0001 | short_line, symbol_heavy | 62 |
| 161d241aad02594d3c0272e7-p000027-l0040 | short_line | ἀπὸ τότε. |
| 686431e9a7fe04175e6e9be9-p000153-l0044 | short_line | dare? |
| 55beb2ad05d46b48576a486d-p000017-l0003 | short_line, low_confidence | ῾Ο Κακός |
| 1697d5cc21fa26717b97e073-p000019-l0098 | short_line, symbol_heavy | . Πλατ. Μενεξ. 236, |
| 727f1e3f8d0a3a622943e9b1-p000123-l0026 | short_line | Σ |
| 1697d5cc21fa26717b97e073-p000091-l0110 | short_line, low_confidence, symbol_heavy | Οδ. 0, |
| 99c8dbb018ec2c87af3fdce9-p000046-l0026 | short_line | ἐψόφησαν. |
| 686431e9a7fe04175e6e9be9-p000235-l0040 | short_line | σατε. |
| 727f1e3f8d0a3a622943e9b1-p000077-l0015 | short_line, symbol_heavy | , π |
| b963a5d59be557e9eef8498b-p000091-l0034 | short_line | ΑΡΦΑΝΟΥΛΑ |
| 54d0bdd8bd3fb11df9ab0432-p000006-l0018 | short_line | κανὲν |
| 07dc0ec3a36ef8d4433de416-p000029-l0002 | short_line, symbol_heavy | 25 |
| 10519e82bcdc24b1f02832d3-p000185-l0001 | short_line, symbol_heavy | - |
| 00c322b3ee04b419d1979f22-p000028-l0047 | short_line | ΠΑΝΕ |
| cc0e056392dd2ef4916b3e7d-p000010-l0021 | short_line | ΑΘΗΝΑ |
| c20219eff76f2fbc39f4c6fd-p000021-l0002 | short_line, low_confidence, symbol_heavy | -(40)- |

### low_confidence (30 examples)

| Line | All reasons | DocAI text |
|---|---|---|
| 1c3c81f346537e276486e9fd-p000032-l0018 | short_line, low_confidence, symbol_heavy | • |
| f3cfa262eedab9cd43a9e412-p000049-l0056 | low_confidence | ὁ Θεός! Θ᾽ ἀποφύ- |
| d9831a204aac7fccbd19bd58-p000004-l0016 | low_confidence | ΚΕΦΑΛΑΙΟΝ Α΄ (1) |
| 99c8dbb018ec2c87af3fdce9-p000054-l0036 | short_line, low_confidence | ZHIH |
| ef3cad078cfd452259f5b836-p000055-l0024 | low_confidence | ἤλυθ᾽ ἔχων· τὰ μὲν οὔτι καταθνητοίσιν ἔοικεν |
| 6976af7d6e1671818ccf9781-p000021-l0039 | low_confidence | μενοι. Ὁ δὲ Ἀρχιδιάκονος πάντοτε ἀπὸ τοῦ ᾿Αμβωνος |
| b963a5d59be557e9eef8498b-p000035-l0001 | short_line, low_confidence | ΔΙΗΓΗΜΑΤΑ |
| 3cb3c1caf7324ded3b11c1e5-p000007-l0116 | low_confidence | M. Le Quien, γράψαντος κατὰ τὸν ΙΗ΄ σἰῶνα, ἐν τῷ Συντάγματι ατι |
| 1697d5cc21fa26717b97e073-p000201-l0005 | low_confidence, symbol_heavy | 12, 17, φᾶτὲ ᾿Αριστ. πλ. 200, φᾶσὶ Σου. Φιλ. 89 καὶ δωρ. φαντὶ Πινδ. Π. 1, |
| e28081a0d8ed58a169d0b77d-p000030-l0055 | short_line, low_confidence | ἄλλην· |
| 54d0bdd8bd3fb11df9ab0432-p000040-l0011 | low_confidence | Δὲν θὰ μείνω πλέον ἐδῶ. Α! Ὄχι.-Βλέπω τοὺς ὀφθαλ- |
| e28081a0d8ed58a169d0b77d-p000131-l0072 | low_confidence | "Ὅλην ἐπάνω μου τὴν ὀργὴν σου, |
| 66112e132fd96ac8e30e5328-p000182-l0037 | short_line, low_confidence, symbol_heavy | } |
| 1495fc2311427a558abbfd88-p000059-l0059 | short_line, low_confidence | = ἀπήρχετο. |
| 3a65f68ff36d911f4ca179e8-p000067-l0020 | low_confidence | Μὰ ἐδῶ νὰ μὴ μ᾿ ἀφήσετε 'στὸν ἔρημο τὸν τόπο· |
| 1697d5cc21fa26717b97e073-p000019-l0017 | low_confidence, symbol_heavy | 03. π. 312, εὐκτ. ἀκαγούμην, α, 286, -οτο Ιλ. ν. 44, -οίμεθα, π, 16. Ρίζο |
| 00c322b3ee04b419d1979f22-p000015-l0042 | short_line, low_confidence | T |
| c10815de32006dc7d7354073-p000016-l0022 | short_line, low_confidence, symbol_heavy | 29 |
| 8b231047fdbd96ec30e1eded-p000010-l0041 | short_line, low_confidence | M |
| f3cfa262eedab9cd43a9e412-p000202-l0031 | low_confidence | ξυλλὲς καὶ νὰ τὴν ρίξουν στη φυλακή ὡς ποῦ νὰ ζῇ. -Ἔπειτα έγύρισε |
| 99c8dbb018ec2c87af3fdce9-p000054-l0030 | low_confidence | μελανόφθαλμοι κτλ; «Ποῦ δ᾽ εὐρεν ὁ κ. Ph. ὅτι οἱ ἀρχαῖοι |
| 8c926ffa3b1b2be056e56b7e-p000191-l0041 | short_line, low_confidence, symbol_heavy | ν, |
| 97da3257b5224e86be9547da-p000052-l0065 | short_line, low_confidence, symbol_heavy | > |
| bf2ce6d100950eec319cef00-p000040-l0069 | short_line, low_confidence | ὁ |
| 18ed614c7b7c25896c49680b-p000211-l0074 | low_confidence | συγγραφεύς (probabilismus)· ὁμνίων τις, ἐὰν ὑποβάλλῃ εἰς τοὺς |
| b5f8ce187b707837e5669281-p000032-l0031 | short_line, low_confidence, symbol_heavy | • |
| a588c9878d5b1197798bb2c5-p000030-l0048 | short_line, low_confidence, symbol_heavy | 1, 2, 3, 4, 5, κτλ. |
| 87010bf6a68a76f0e0eb368f-p000015-l0049 | short_line, low_confidence | CHHAY |
| 1697d5cc21fa26717b97e073-p000019-l0008 | low_confidence | Έκαγον Ιλ. π. 822, μτχ. μτχ. ἀκαγών Ησ. θε 868. Μές. ἀκεχίζομαι μτγν. ἀκάν |
| cc0e056392dd2ef4916b3e7d-p000024-l0021 | short_line, low_confidence | SHIHON |

### tall_box (30 examples)

| Line | All reasons | DocAI text |
|---|---|---|
| 723c450ea9bb07fc4cdf47f9-p000088-l0001 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 0907df739607faca673d2169-p000007-l0040 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ |
| ca065d129a9bd4a73ad7a9a2-p000141-l0030 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 480b788bb2f6e216f3898c02-p000010-l0001 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 2c8742589d947f8d749c7ba2-p000005-l0012 | tall_box | λίζετο ἡ πρὸς τὸν Θεὸν τοῦ φωτὸς εὐσέβεια καὶ λατρεία τῶν Ῥοδίων |
| e988c46677e75b38c15117fc-p000011-l0013 | tall_box | Ο ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| f77a8c0084022edb7981fb15-p000083-l0030 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ |
| fdcac2103d02191960287381-p000010-l0015 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ |
| f77a8c0084022edb7981fb15-p000055-l0041 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 928e34aaaa78469aacd6c7ef-p000026-l0021 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 46241fd09ba5dae869149357-p000049-l0038 | low_confidence, tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ |
| d9d705c23499ff012aa70783-p000020-l0028 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡ |
| f3cfa262eedab9cd43a9e412-p000158-l0006 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ |
| b7a2ad096ab8ab67b203d3cd-p000072-l0033 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 18f82018e84dda79e88e0726-p000157-l0001 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 46241fd09ba5dae869149357-p000085-l0038 | short_line, tall_box | ΠΑΝΕΠΙΣ |
| 480b788bb2f6e216f3898c02-p000023-l0001 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 42c339ce492d83665f00774d-p000080-l0006 | tall_box, bad_page | Λύκ. Χρ. Χ΄ Χρήστου |
| 686431e9a7fe04175e6e9be9-p000174-l0076 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 8c926ffa3b1b2be056e56b7e-p000250-l0042 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΙ |
| cbe5e7b92d36edf08153017b-p000206-l0071 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 2f9e996ffbdaaa3b4a9dfdcf-p000082-l0001 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 00c322b3ee04b419d1979f22-p000129-l0056 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 8f477fb59c9bc6957aadc800-p000129-l0025 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ |
| 46241fd09ba5dae869149357-p000078-l0001 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 042c93b2591368d437f27678-p000292-l0001 | tall_box | Ο ΠΑΝΕΠΙΣΤΗΜΙΟ |
| 18f82018e84dda79e88e0726-p000101-l0001 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 98d73c3573628c15b861d2ce-p000090-l0048 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗ |
| 8f477fb59c9bc6957aadc800-p000055-l0001 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| b4bb45a610fbcbc974b0eb32-p000027-l0028 | tall_box | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |

### symbol_heavy (30 examples)

| Line | All reasons | DocAI text |
|---|---|---|
| 3ae256de8a055af974b9ec8f-p000016-l0035 | short_line, symbol_heavy | (15)( |
| 69846639273a60b797e93cb9-p000111-l0002 | short_line, low_confidence, symbol_heavy | - |
| 1697d5cc21fa26717b97e073-p000019-l0046 | low_confidence, symbol_heavy | Πρ. 506, παρατ. ἀκήδεις Ιλ. 4, 4, 70, 70, μ μελ. μτγν. ἀκηδήσω Κ. Σμ. 10, ↵ 20, ἀορ. ἀκήδεσα Ιλ. ξ. 427, |
| 98d73c3573628c15b861d2ce-p000012-l0028 | short_line, low_confidence, symbol_heavy | 20,000 >> |
| b5f8ce187b707837e5669281-p000091-l0046 | short_line, low_confidence, symbol_heavy | >> |
| bf2ce6d100950eec319cef00-p000040-l0007 | short_line, symbol_heavy | 446. |
| 1697d5cc21fa26717b97e073-p000152-l0017 | symbol_heavy | Βρ. ἔρ. 173, ὄφειλον (ἄλλ. ὤφελλον) Ιλ. λ, 688, ὤφελλον, η, 390, ὄφελλον, |
| 42c339ce492d83665f00774d-p000072-l0020 | short_line, symbol_heavy | * |
| 1495fc2311427a558abbfd88-p000040-l0029 | short_line, low_confidence, symbol_heavy | A΄ |
| d9d705c23499ff012aa70783-p000044-l0001 | short_line, symbol_heavy | 84 |
| 54a124e5cac779ec617e3ace-p000112-l0036 | low_confidence, symbol_heavy | 2) Πολιτ. θ΄. 586 Α κ. έξ. 3) Πολιτ. θ΄. 585Β κ. ἐξ. |
| 531766b8df920948582ab436-p000038-l0001 | short_line, symbol_heavy | 70 |
| c956015742d213237900264d-p000028-l0023 | short_line, low_confidence, symbol_heavy | 49 |
| 2c8742589d947f8d749c7ba2-p000043-l0025 | short_line, low_confidence, symbol_heavy | 89 |
| bf2ce6d100950eec319cef00-p000032-l0056 | short_line, symbol_heavy | 72. |
| b8b71bfd410ddd2e68429ffe-p000026-l0034 | short_line, symbol_heavy | 49 |
| 1118b0c89e773062b4cf69f5-p000019-l0005 | short_line, symbol_heavy | . |
| 4f1e627418cc5d716264fa7d-p000043-l0002 | short_line, symbol_heavy | 39 |
| 1697d5cc21fa26717b97e073-p000177-l0087 | symbol_heavy | λοντο Αἰσχ. Πρ. 481, μελ. ἀποσκλήση Αι ᾿Ανθ. 11, 11, 37, καὶ |
| ef3cad078cfd452259f5b836-p000036-l0028 | short_line, low_confidence, symbol_heavy | (Οδ. Α 190). |
| 1697d5cc21fa26717b97e073-p000127-l0095 | symbol_heavy | Α΄. 1086, εὐκτ. ἰων. -εοίατο Ηρ. 1, 99, π. παρκ. λελύπημαι Εὐρ. Ἴων 1311, |
| 1697d5cc21fa26717b97e073-p000055-l0033 | symbol_heavy | Κωμ. ἀποσπ. 4, 230, δωρ. –αμες Θεοκρ. 1, 16, -ατε ↵ ᾿Αριστ. ἐκκλ. 181, ὑποτ. |
| cc5059bc91ca2b178c20008c-p000025-l0024 | short_line, symbol_heavy | γ) |
| 42c339ce492d83665f00774d-p000072-l0045 | short_line, symbol_heavy | * |
| d55d101cb2fa4c91b9e11083-p000058-l0001 | short_line, low_confidence, symbol_heavy | 1 |
| 3cb3c1caf7324ded3b11c1e5-p000022-l0048 | short_line, symbol_heavy | 6) |
| bf2ce6d100950eec319cef00-p000045-l0003 | short_line, symbol_heavy | 683. |
| b5f8ce187b707837e5669281-p000091-l0038 | short_line, low_confidence, symbol_heavy | >> |
| 1697d5cc21fa26717b97e073-p000019-l0017 | low_confidence, symbol_heavy | 03. π. 312, εὐκτ. ἀκαγούμην, α, 286, -οτο Ιλ. ν. 44, -οίμεθα, π, 16. Ρίζο |
| 1697d5cc21fa26717b97e073-p000091-l0033 | symbol_heavy | ἐθάφθην Σιμων. Κ. 170, ἀπαρ. θαφθῆναι Ηρ. 2, 81, μτχ. θαφθείς, 7, 228, |

### foreign_script (30 examples)

| Line | All reasons | DocAI text |
|---|---|---|
| f77a8c0084022edb7981fb15-p000023-l0005 | foreign_script | β'. Πώλησις ἐπὶ ἀντιχρήσει )بيع بالا استغلال λέγεται ή |
| 6df192e72b10d13c5fc1374a-p000149-l0004 | short_line, low_confidence, foreign_script | コ |
| 292f4a0b4f0dc8e6dddb103d-p000573-l0030 | low_confidence, foreign_script, mixed_word | Κατὰ τὴν αὐτὴν στιγμὴν καὶ ἐνῶ ὁ ᾿Αρτανιάν έκυπτε ποόςㄹ |
| 55beb2ad05d46b48576a486d-p000017-l0055 | short_line, foreign_script | 주 |
| b5f8ce187b707837e5669281-p000091-l0033 | short_line, low_confidence, foreign_script | 净 |
| db1ed5f902d696fb53656a7d-p000051-l0032 | short_line, low_confidence, foreign_script | の |
| 666498b9ed183dc88c1e8716-p000122-l0067 | foreign_script, mixed_word | εἶναι ὡς ὁ λόγος τῶν ὑψῶν αὑτῶν에. |
| 650670ab271096716888b108-p000006-l0048 | short_line, low_confidence, foreign_script | コ |
| 1697d5cc21fa26717b97e073-p000046-l0010 | low_confidence, foreign_script, mixed_word | ἀταντῇ παραל .דουκολέεσκες Ιλ. p. 4 448. Ἡ λέξ. εἶνε σύνθ. 19. ἐκ τοῦ βοῦς καὶ |
| 73e10362c99c1be82977a983-p000067-l0001 | short_line, low_confidence, foreign_script | 一点。 |
| 3ae256de8a055af974b9ec8f-p000105-l0031 | short_line, low_confidence, foreign_script | ية |
| 00c322b3ee04b419d1979f22-p000015-l0027 | low_confidence, foreign_script | φωρείωτδιά છે να προσβάλωσι άλωσι τὴν τὴν ἀριστερὰν ἂν ἐχθρικὴν πτέρυγα᾽ διὰ |
| f77a8c0084022edb7981fb15-p000070-l0011 | low_confidence, foreign_script | ή σκιάς ) اصمه چارطاق (, ή ξυλίνη φραγή )تخته برده(, οἱ τοίχοι |
| f77a8c0084022edb7981fb15-p000070-l0010 | low_confidence, foreign_script | ραμιδίων )اقطارمه(, ἡ ἐπισκευὴ τῆς παρωροφίδος )ویلقوغان |
| a588c9878d5b1197798bb2c5-p000030-l0085 | short_line, low_confidence, foreign_script | لي |
| f77a8c0084022edb7981fb15-p000063-l0046 | foreign_script | Κτηματικοὶ φόρο )املاك ويركوسى -Ὁ κτηματικὸς φό- |
| ef3cad078cfd452259f5b836-p000115-l0040 | short_line, low_confidence, foreign_script | 山 |
| 6c82556081bbe4aada41e496-p000019-l0015 | short_line, low_confidence, foreign_script | در |
| 18ed614c7b7c25896c49680b-p000144-l0063 | low_confidence, foreign_script | ἄνιον αὐτῆς ὑπὸ ἡμερομηνίων αν 27 Φεβρουορίε1970 ب |
| 1be3f9227e2b68a2b9974abe-p000078-l0013 | foreign_script, mixed_word | de Rozière, Nº 319-367. Ἐν πᾶσι τοῖς ἐγγράφοις τούτοις μνεία |
| 8961f6bdd6daf004b4a84dfa-p000013-l0026 | foreign_script, mixed_word | Τὸ κυριώτατον εἶναι ὅτι τὰ περὶ ὧν ὁ λόγος φαινόμενα ἐρευνῶνー・ |
| 6389d36a8d20c1541b1d4bcb-p000078-l0023 | short_line, low_confidence, foreign_script | リ |
| 6296ac8dc850e29e2fa2f0b1-p000051-l0002 | foreign_script | τούρκους τῷ 1822 (30 Σ)βρίου.) Νεροχώρι, κώμη ἐφ᾽ ὑ-د |
| b08a5423fb059fbb291900aa-p000022-l0042 | short_line, low_confidence, foreign_script | জ |
| f77a8c0084022edb7981fb15-p000017-l0044 | low_confidence, foreign_script | )قيض امانت( ότε ὁ παραλήπτης, θεωρούμενος ἔμπιστος, ὡς ἐν τῇ πα- |
| 51026389607510af823b520a-p000061-l0013 | short_line, low_confidence, symbol_heavy, foreign_script | an = + 3º ἕως + 7". |
| 8e3c482e1f6c81bb67f24395-p000020-l0008 | low_confidence, symbol_heavy, foreign_script | κονομία. Ἔκδ. Β΄. σελ. 928.۰۰۰.۰۵10 . م. |
| 727f1e3f8d0a3a622943e9b1-p000077-l0049 | low_confidence, foreign_script, mixed_word | φλω, εὐκτ. όρλοιμι, άπκο. όυλεῖν, μετχ. ούλων, πえん、ちんんん |
| 0cb3f67240837f77ee728005-p000023-l0001 | short_line, low_confidence, foreign_script | 类学 |
| 727f1e3f8d0a3a622943e9b1-p000077-l0044 | low_confidence, foreign_script, mixed_word | τι εἰς τὸ δημόσιον, παρτο αυλιデスメタOY。 |

### mixed_word (30 examples)

| Line | All reasons | DocAI text |
|---|---|---|
| b963a5d59be557e9eef8498b-p000009-l0034 | low_confidence, mixed_word | ZA BAKOΥΦΙΚΑ |
| 666498b9ed183dc88c1e8716-p000057-l0051 | mixed_word | ᾿Ανωτέρω ὑπετέθη, ὅτι τὰ τμήματα τῆς εὐθείας ΑΝ ἢ τῆς ΒII |
| 99c8dbb018ec2c87af3fdce9-p000054-l0013 | mixed_word | Ο κ. Ρh. τοποθετήσας τὸν Ελλ. τύπον κατὰ προτί- |
| 8298db8c50ae1b18df756118-p000010-l0023 | mixed_word | Μὲ τάχος ὑπερκόσμιον, γοργοτέρα τοῦ ἱέρακος σχίζουak |
| c10815de32006dc7d7354073-p000057-l0061 | mixed_word | ΑΝΤΩΝΙΟΣ ΛΟΡΕΔΑN |
| 3cb3c1caf7324ded3b11c1e5-p000044-l0027 | mixed_word | Οἴα, ας, Οἴη, ης, (ή), ΟΕa, v. de la Tripolitaine, auj. Tri- |
| 1be3f9227e2b68a2b9974abe-p000078-l0017 | foreign_script, mixed_word | fratrum». Πρβλ. Form, de Rozière, Nº 319 (Sir- |
| 666498b9ed183dc88c1e8716-p000122-l0067 | foreign_script, mixed_word | εἶναι ὡς ὁ λόγος τῶν ὑψῶν αὑτῶν에. |
| 161d241aad02594d3c0272e7-p000058-l0030 | low_confidence, tall_box, mixed_word | λῆς, φύλαξέ τα, διότι εἶναι ἱερά, καὶ ὡς τοιαῦτα τὰ στέλλω εἰς σε ΖΗΤΗdy |
| f77a8c0084022edb7981fb15-p000017-l0047 | foreign_script, mixed_word | )قبض مضمون(Steὁ παραλήπτης εὐθύνεται ἐν πάσῃ περιπτώσει |
| b963a5d59be557e9eef8498b-p000042-l0037 | low_confidence, mixed_word | οί Βάρδας ἀπὸ τὸν Παπαδράκοne wishes |
| 686431e9a7fe04175e6e9be9-p000051-l0035 | foreign_script, mixed_word | Comprarne ancora uว. |
| 1697d5cc21fa26717b97e073-p000046-l0010 | low_confidence, foreign_script, mixed_word | ἀταντῇ παραל .דουκολέεσκες Ιλ. p. 4 448. Ἡ λέξ. εἶνε σύνθ. 19. ἐκ τοῦ βοῦς καὶ |
| 1697d5cc21fa26717b97e073-p000091-l0105 | low_confidence, mixed_word | , θωϋτὰ (=θωF-ετά) θωῦμα, θωυ-μ-άζω, θεωρός (=02F- ↵ ρος), θεωρέω. ᾿Αλλὰ |
| 1092c25534f45a95669f3d2b-p000033-l0043 | short_line, low_confidence, mixed_word | DenΚΗ |
| 3cb3c1caf7324ded3b11c1e5-p000044-l0030 | mixed_word | même que Zάκανθα, Καινή, Νέα Καρχηδών, Καρθαγένα, |
| 686431e9a7fe04175e6e9be9-p000112-l0010 | mixed_word | λου, ἀλλὰ μέρος αὐτοῦ ἐξακολουθεῖ νὰ ἦναι παρὸν, οἷov |
| 1be3f9227e2b68a2b9974abe-p000078-l0013 | foreign_script, mixed_word | de Rozière, Nº 319-367. Ἐν πᾶσι τοῖς ἐγγράφοις τούτοις μνεία |
| 1697d5cc21fa26717b97e073-p000019-l0081 | mixed_word | ῾Ρίζ. κοF, (διότι κοᾷπἀκούει, πεύθεται, καὶ ἔκομεν ↵ εἶνε τὸ ἐφετ. ↵ Ξεἴδομεν, ἑωρῶμεν, ἠσθόμεθα |
| 2b1d2b5340150ddc135a2b1a-p000085-l0043 | mixed_word | ριζόμενος ἱερεὺς ἦτο ὁ flamen Sospitae Junonis, ἧς ἡ ἑορτὴ ἑωρτάζετο Κa- |
| 6296ac8dc850e29e2fa2f0b1-p000163-l0019 | mixed_word | ΔΗΜΟΣ ΣΧΟJNIA. |
| 1697d5cc21fa26717b97e073-p000046-l0087 | mixed_word | Ρίζ. ΕρεF - (ῥέω), βρεχ, βρέχ-w=rigo, ir-rigo λατ. βρέγ-μα βρεκ-τός, βροχή, |
| 686431e9a7fe04175e6e9be9-p000299-l0033 | low_confidence, mixed_word | già, ἤδη, εἰὸ, τοῦτο, ρυὸ, δύναται, piè, ποῦς, giù, κάτω, ρίù, μᾶλ- |
| 1c3c81f346537e276486e9fd-p000019-l0036 | mixed_word | ΤΙ ΕΤΡΩΓΕ ΚΑΤΑ ΤΗΝ ΤΡΙΗΜΕΡΟΝ ΜANIN |
| 727f1e3f8d0a3a622943e9b1-p000077-l0044 | low_confidence, foreign_script, mixed_word | τι εἰς τὸ δημόσιον, παρτο αυλιデスメタOY。 |
| 8961f6bdd6daf004b4a84dfa-p000025-l0070 | low_confidence, mixed_word | 1) Typeς, τομ. ΙΙ, μερ. ΙΙ. Εἰσαγωγή. |
| 686431e9a7fe04175e6e9be9-p000174-l0067 | mixed_word | Ηo tirato parecchie volte sopra |
| ef3cad078cfd452259f5b836-p000082-l0002 | mixed_word | πενθίμου τοῦ εἴδους κλαίουσα ἰτéz salix pendula, |
| 1697d5cc21fa26717b97e073-p000127-l0046 | mixed_word | λου-τ-ρόν, (=λοF-ε-τρόν,), lu-o=λούω, καθαρίζω λατ. |
| 161d241aad02594d3c0272e7-p000054-l0053 | mixed_word | Kαλύτερα ποὺ τὸν ἐπῆρε ἄλλος. Ἔχω μιὰ παλιολαζαρίνα ἐγώ |

### bad_page (30 examples)

| Line | All reasons | DocAI text |
|---|---|---|
| a30e828662f14c20f8994268-p000024-l0018 | low_confidence, bad_page | σωμεν ἐνταῦθα νὰ ἀναμιχθῶμεν εἰς τὸ δυσκολὸν καὶ |
| 928e34aaaa78469aacd6c7ef-p000042-l0001 | short_line, symbol_heavy, bad_page | 42 |
| a30e828662f14c20f8994268-p000024-l0027 | bad_page | Λυκαία Δαμία ἤτοι Λοχαία καὶ Δαμία. Λοχαία ὡς: |
| 00c322b3ee04b419d1979f22-p000069-l0003 | short_line, low_confidence, bad_page | Με Μπλάν |
| 42c339ce492d83665f00774d-p000080-l0052 | short_line, bad_page | ἐγράψαμεν. |
| 928e34aaaa78469aacd6c7ef-p000042-l0006 | bad_page | Εἰς πάντας κ᾿ αἰωνία. |
| 42c339ce492d83665f00774d-p000080-l0035 | bad_page | οὕτως ἢ ἄλλως. |
| 42c339ce492d83665f00774d-p000080-l0014 | tall_box, bad_page | λιεργοῦντο δαψιλῶς τὰ ἑλληνικὰ Γράμματα ὑπὸ προσωπικοῦ κατὰ τε ποσὸν, καὶ δὴ ποιὸν, και |
| a30e828662f14c20f8994268-p000024-l0002 | short_line, symbol_heavy, bad_page | 20 |
| 928e34aaaa78469aacd6c7ef-p000042-l0005 | low_confidence, bad_page | Κι᾿ ἂς γείνῃ λύπη φοβερά |
| a30e828662f14c20f8994268-p000024-l0025 | bad_page | ἄλλως ὁ ἀριθμὸς τῶν Θεῶν οὐδαμῶς εἶναι πλήρης· |
| 00c322b3ee04b419d1979f22-p000069-l0001 | tall_box, bad_page | ΕΚΣΤΡΑΤΕΙΑΙ ΤΗΣ ΙΤΑΛΙΑΣ (1796 ΚΑΙ 1800) |
| 42c339ce492d83665f00774d-p000080-l0011 | tall_box, bad_page | Αστ. Σχολὴ Σκύρου |
| 00c322b3ee04b419d1979f22-p000069-l0005 | short_line, low_confidence, bad_page | ΜΕ Βερναρ |
| 00c322b3ee04b419d1979f22-p000069-l0014 | bad_page | Μιλάνο Ὀρσινάδι |
| 00c322b3ee04b419d1979f22-p000069-l0016 | short_line, bad_page | Βερσέλ |
| 00c322b3ee04b419d1979f22-p000069-l0031 | low_confidence, bad_page | Στραντέλλο |
| 928e34aaaa78469aacd6c7ef-p000042-l0021 | bad_page | Κ᾿ἂς κλαίουν κ᾿ ἂς ὀδύρωνται |
| 928e34aaaa78469aacd6c7ef-p000042-l0007 | low_confidence, bad_page | Κ᾿ ἂς γείνη, να', κατακλυσμός |
| 00c322b3ee04b419d1979f22-p000069-l0024 | low_confidence, bad_page | Πιζζιγκεττον |
| 00c322b3ee04b419d1979f22-p000069-l0028 | short_line, low_confidence, bad_page | Κρεμάνε |
| 42c339ce492d83665f00774d-p000080-l0033 | bad_page | ἕνεκεν πλεισταχοῦ ἐν τῷ βιβλίῳ τούτῳ μετεχειρί- |
| 42c339ce492d83665f00774d-p000080-l0021 | short_line, bad_page | Σ. Σ |
| 00c322b3ee04b419d1979f22-p000069-l0046 | short_line, low_confidence, bad_page | Αλμπέρκα |
| 00c322b3ee04b419d1979f22-p000069-l0037 | short_line, low_confidence, bad_page | Μαρένγκα |
| 00c322b3ee04b419d1979f22-p000069-l0020 | short_line, bad_page | Τρίνο |
| a30e828662f14c20f8994268-p000024-l0015 | low_confidence, bad_page | σῆς καὶ ἐν τοῖς παρωνυμίοις Ικέσιος, Στοιχαῖος |
| a30e828662f14c20f8994268-p000024-l0003 | low_confidence, bad_page | πορὰ τὴν Δήμητρα: Διότι ὄντως εἶναι φυσικὸν ὅτα |
| 928e34aaaa78469aacd6c7ef-p000042-l0022 | bad_page | Κ᾿ ἂς γείνη μέγας θρήνος |
| 42c339ce492d83665f00774d-p000080-l0038 | bad_page | ουα, (λ) ουάχανα, γε(λ)ουά. Τοιοῦτό τι παρατηρεῖται |

### label_in_holdout (30 examples)

| Line | All reasons | DocAI text |
|---|---|---|
| cd71a3283d310fc887e742d5-p000011-l0032 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 6c82556081bbe4aada41e496-p000022-l0057 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 96bb7196d840fe7513c2ed43-p000024-l0033 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ |
| 4fb1fdd9b2f3f5caa8e0be18-p000017-l0034 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 292f4a0b4f0dc8e6dddb103d-p000498-l0035 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 0bff55647d1c2acd1caa8bf3-p000263-l0029 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗ |
| eed91c3c88be77cac51e7629-p000158-l0035 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 460b94bc8e2c58a95074382b-p000023-l0042 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 460b94bc8e2c58a95074382b-p000017-l0044 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 460b94bc8e2c58a95074382b-p000021-l0001 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗ |
| 0bff55647d1c2acd1caa8bf3-p000041-l0002 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ |
| d8dfd78fb29485b6707ae96c-p000023-l0034 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ |
| 8e3c482e1f6c81bb67f24395-p000031-l0001 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 18f05e4e68aadfc094bbe31d-p000068-l0032 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ |
| 10349bf796b8cd19c7415595-p000121-l0041 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ |
| 453f156dc6352286456a08cb-p000073-l0035 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 453f156dc6352286456a08cb-p000047-l0038 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 53e3db8de066783d632e29c5-p000070-l0001 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 9e60fbb6b1fc1da9f26b775e-p002060-l0001 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| cd71a3283d310fc887e742d5-p000092-l0032 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| c194db932e54383910fe40a7-p000107-l0001 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 9e60fbb6b1fc1da9f26b775e-p000443-l0001 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 10349bf796b8cd19c7415595-p000548-l0001 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| e1006e79dabe16c9460ae218-p000107-l0037 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ |
| eed91c3c88be77cac51e7629-p000083-l0036 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| ecadd6f5c84ab0f85c671729-p000111-l0040 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 292f4a0b4f0dc8e6dddb103d-p000200-l0036 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 87010bf6a68a76f0e0eb368f-p000128-l0032 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 18f05e4e68aadfc094bbe31d-p000009-l0034 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |
| 460b94bc8e2c58a95074382b-p000009-l0044 | label_in_holdout | ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ |

## Reproduce and validate

```sh
.venv/bin/python -m pytest tests/test_harvest_admission.py tests/test_round1_admission_outputs.py
.venv/bin/python -m scripts.harvest.admit_round1
.venv/bin/python -m scripts.harvest.validate_round1_admission
```

Input and source hashes, contact-sheet selections and output hashes are in `admission_inventory.json`; full corpus/crop validation is in `admission_validation.json`.

## Verification and visual observations

**353 offline tests passed** (86 new admission/artifact contracts plus 267 existing harvest regressions). Every one of the **61,882** saved crops passed PNG hash, grey mode, dimensions, geometry and exact source-pixel checks. No admitted train label equals an admitted dev/test label. [Full validation](admission_validation.json), [test results](admission_tests.json), [JUnit](admission_tests.xml), and [read-only Git metadata audit](admission_git_audit.json).

All sheet layouts were visually inspected. Native top/bottom regions covered 48 examples. Some source boxes contain neighbouring text or text beyond the supplied label, including `83df10d25e7c4c1cefe2aed5-p000053-l0042` and `18f82018e84dda79e88e0726-p000157-l0060`; university stamp crops also need review. The crops implement the requested DocAI-box rule; these observed cases remain admitted under the specified text gates. [Visual QA examples](admission_visual_qa.json) keep this separate from the owner’s pending accuracy review. Round 1 has zero admitted Cyrillic lines, so its sheet records that empty class rather than sampling unavailable crops.
