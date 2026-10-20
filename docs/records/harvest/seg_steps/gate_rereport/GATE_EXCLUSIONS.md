# Gate exclusions by evaluation set

Part-1 precedence is preserved. Part-2-only overlaps are separately in row_decisions.jsonl. Text is raw Google text.

## segeval1

| ID | Kind / outcome | Words / scripts / reason evidence | Raw text |
| --- | --- | --- | --- |
| gazette_modern--9701a3a500ecbd85--s000-l0011 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 7, 'minimum': 10}] | 165, πτυχιού- |
| gazette_modern--bd7c91e6a214949b--s000-l0125 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['ハンハンΟΜΙΑΣ']}, {'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'greek': 5, 'other': 4}, 'characters': ['ハ', 'ン']}] | ハンハンΟΜΙΑΣ. |
| lekythos--a0c4e6327052acfc--s002-l0089 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.2}] | / |
| gazette_modern--13a9303cfc83a9d4--s000-l0045 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0625}] | 3 |
| gazette_modern--1456dcb167f23bfe--s000-l0027 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0909090909090908}] | 1 |
| gazette_modern--5158b7bf9def2bab--s000-l0012 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.875}] | - |
| gazette_modern--5d57e9c685c50ca6--s000-l0073 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['cyrillic'], 'script_counts': {'cyrillic': 9}, 'characters': ['С', 'а', 'и', 'к', 'н', 'р', 'я']}] | Скрирания |
| gazette_modern--6d58ca2e2dc41e69--s000-l0067 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1666666666666667}] | 4. |
| gazette_modern--aeb6eb76fc7057f0--s000-l0050 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4}] | " |
| gazette_modern--c90fa267aa2e4dd4--s000-l0083 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 8, 'minimum': 10}] | Γεωργίου |
| ia_poly1850--2d02eaf0f19a649a--s024-l0004 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 8, 'minimum': 10}] | EDITED BY |
| nlg--3d6bd7bd688acb61--s024-l0003 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 4.583333333333333}] | - |
| 252fd568-p000234-l0033 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['cyrillic'], 'script_counts': {'cyrillic': 13, 'latin': 20}, 'characters': ['в', 'д', 'и', 'н', 'о', 'р', 'с', 'т', 'ъ', 'я']}] | сродниятъ видъ Anisoplia Segetum Hbst. |

## calibration

| ID | Kind / outcome | Words / scripts / reason evidence | Raw text |
| --- | --- | --- | --- |
| bsb_poly1850--6f646367ed080533--s006-l0038 | short_line / DROP | [{'reason': 'short_line', 'role': 'mixed_greek_latin', 'letters': 6, 'minimum': 10}] | IV β 1, 4, V 35, 63, VI 46. |
| ia_greek_latin--6886a59734933bc1--s003-l0090 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['οn']}] | Επέκεινα, adv. (ἐπ᾿ ἐκεῖνα), οn |
| ia_russian--06528548147a3a3d--s000-l0001 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | - |
| ia_greek_latin--d15eca050847acdb--s001-l0065 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 6, 'minimum': 10}] | Owens, J., 78, 163 |
| serbia--402f4a74588bffe1--s002-l0013 | short_line / DROP | [{'reason': 'short_line', 'role': 'cyrillic', 'letters': 9, 'minimum': 10}] | оивиченом |
| bsb_poly1850--9f1e10e4cc7f1532--s004-l0084 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['EΕἰς']}] | EΕἰς δὲ τὴν ἀναγωγὴν λεχθείη ἂν τοιαῦτα· ὅτι Ἰησοῦς |
| ia_poly1850--4ab77886725d9e1e--s008-l0041 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 9, 'minimum': 10}] | lol. suppl. 3, p. 585-6.) |
| elstat--996d9f614c928993--s000-l0085 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 3}, 'characters': ['ق', 'م', 'و']}] | قوم |
| ia_poly1850--174d84a441d69a70--s039-l0018 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'latin': 35, 'other': 4}, 'characters': ['ا', 'ب', 'م', 'ه']}] | io in position and ما به in figure, and there is no |
| elstat--ee37bc488988f1bd--s000-l0998 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 2.5}] | x. |
| ia_greek_latin--ef6c2c5c1ba30b47--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.048780487804878}] | 8 |
| ia_greek_latin--e2d30795088743d8--s000-l0022 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['ΚΑΛΟYCIN']}] | tation) oder eigentlich MC.K...Ρ.Λ. ΚΑΛΟYCIN κατη- |
| ia_greek_latin--d94cfff6c5bd6428--s001-l0002 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['εὐεπιβούλευτoc']}] | εὐεπιβούλευτoc, infidiis |
| ia_russian--d558bd3e803e7865--s007-l0031 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 5.0}] | - |
| serbia--557369d8d117b91a--s000-l0319 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 19}, 'characters': ['V', 'a', 'b', 'd', 'e', 'g', 'i', 'l', 'm', 'n', 'o', 's', 'é']}] | Vignobles endommagés |
| bsb_poly1850--fe51c7e60c92453d--s034-l0003 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.5454545454545454}] | A |
| ia_greek_latin--34f544df6c245b5d--s002-l0049 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['cyrillic'], 'script_counts': {'cyrillic': 3}, 'characters': ['С', 'в', 'с']}] | (с. 30 в.С.). |
| ia_poly1850--943cc2df19157a1b--s023-l0037 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['oἷον']}] | ras. 24 ἢ μή] schol. εἰ μὴ libri 27 M in ras. oἷον ὅτι ἑτέρως ἔδει |
| gazette_modern--8757f64ef1908c90--s000-l0003 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4482758620689655}] | (3) |
| bsb_poly1850--2032df1e3e983f1d--s005-l0029 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 7, 'minimum': 10}] | PAEONIA |
| bsb_poly1850--2032df1e3e983f1d--s005-l0217 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 4, 'minimum': 10}] | MEER |
| bsb_poly1850--3496ab66cde251ee--s005-l0112 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 5, 'minimum': 10}] | deles |
| bsb_poly1850--515c78c513c1c8c5--s023-l0094 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 6, 'minimum': 10}] | edidit |
| elstat--2b5780c7c9896a54--s000-l0051 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 8, 'minimum': 10}] | Sommaire |
| gazette_modern--363c5539ff24957e--s000-l0104 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ................................ |
| gazette_modern--37ed2e85ffdd5592--s000-l0067 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 2, 'minimum': 10}] | γ & β, |
| gazette_modern--37ed2e85ffdd5592--s000-l0073 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 2, 'minimum': 10}] | γ & β. |
| gazette_modern--5d57a0a85aede133--s000-l0015 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 3, 'minimum': 10}] | " του |
| gazette_modern--9a06f5aaa5be314f--s000-l0379 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 6, 'minimum': 10}] | πιθανη |
| gazette_modern--dc95e9d95cc9cb8e--s000-l0107 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 7, 'minimum': 10}] | κόστους |
| gazette_modern--df5a370d8f003110--s000-l0015 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 38}, 'characters': ['י', 'ן']}] | ייייייייייייייייייייייייייייייייייייין |
| gazette_modern--e418f19baeb555e0--s000-l0026 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 4, 'minimum': 10}] | τσών |
| ia_greek_latin--54dae6633713c0a0--s005-l0001 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 7, 'minimum': 10}] | HARVARD |
| ia_greek_latin--8af66d4d113847ee--s003-l0001 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 8, 'minimum': 10}] | CONTENTS. |
| ia_greek_latin--8af66d4d113847ee--s003-l0022 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ...................... |
| ia_greek_latin--8af66d4d113847ee--s003-l0107 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ......................... |
| ia_greek_latin--a232aaf9a41fe898--s001-l0012 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.0281030444964872}] | ***** |
| ia_greek_latin--f40a7578d8cd5825--s002-l0112 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ------------ |
| ia_poly1850--63f57af8d450f3e8--s009-l0033 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 8, 'minimum': 10}] | τους υπερ |
| ia_poly1850--63f57af8d450f3e8--s034-l0018 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 6, 'minimum': 10}] | λιππός |
| ia_poly1850--63f57af8d450f3e8--s034-l0019 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1850', 'letters': 5, 'minimum': 10}] | ἐστιν |
| ia_poly1850--a89bd2c9bdb1ca6d--s034-l0035 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | .......... |
| ia_poly1850--c3f3a531e277da9a--s036-l0026 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ..... |
| ia_russian--61f76a57b26f9b13--s001-l0004 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 6}, 'characters': ['D', 'L', 'N', 'O']}] | LONDON, |
| ia_russian--61f76a57b26f9b13--s001-l0005 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 23}, 'characters': ['A', 'B', 'C', 'E', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'W', 'o']}] | TRUBNER & Co. 60, PATERNOSTER ROW, |
| ia_russian--6cfc00f06e0f7241--s004-l0043 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ...... |
| kosmopolis--86098eebf5207e79--s003-l0041 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 4, 'minimum': 10}] | στὴν |
| kosmopolis--8ac130e14e062423--s001-l0026 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 4, 'minimum': 10}] | πᾶνε |
| kosmopolis--91040f2da70b9ae0--s004-l0004 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 3, 'minimum': 10}] | ᾿Απὸ |
| kosmopolis--9a17c86798d2c74a--s000-l0030 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 3, 'minimum': 10}] | , ποῦ |
| kosmopolis--9a17c86798d2c74a--s003-l0012 | short_line / DROP | [{'reason': 'short_line', 'role': 'dialogue_fiction', 'letters': 3, 'minimum': 10}] | ” καὶ |
| kosmopolis--9a17c86798d2c74a--s007-l0035 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 4, 'minimum': 10}] | νὰ ξε- |
| kosmopolis--ecc23d7812913d0a--s006-l0039 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ...» |
| lekythos--0fc3672826ddd6b3--s001-l0023 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 6, 'minimum': 10}] | βιβλία |
| lekythos--456def1ccfc2283e--s001-l0177 | numeric_shape / DROP | [{'reason': 'numeric_shape', 'alnum': 1, 'detail': '<=1 letter-or-digit'}] | -'-'-'-'-'-'-'0 |
| lekythos--49c082ba27aa27da--s000-l0046 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 4, 'minimum': 10}] | Η του |
| lekythos--49c082ba27aa27da--s000-l0241 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 4, 'minimum': 10}] | μὲ τὰ |
| lekythos--7f67b784930deef5--s004-l0020 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 6, 'minimum': 10}] | σας μία |
| lekythos--dcfa99599048d352--s000-l0105 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 9, 'minimum': 10}] | Κάτω ΒΟΛΟΥ |
| nlg--1144074169f43992--s021-l0010 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 6, 'minimum': 10}] | τί ἄλλο |
| serbia--27b182bf4116728f--s008-l0003 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['рѣza']}] | Г. Ана: Гуліани рѣza y Mabmk: 1817, |
| serbia--3ab59a8d4ee49339--s005-l0014 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 6}, 'characters': ['A', 'C', 'I', 'N']}] | INCAII. |
| serbia--b6450341d87fb144--s007-l0002 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['БУE']}] | ВИЉЕМ БУE |
| serbia--e7935cdb3dfeaf10--s006-l0006 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 26}, 'characters': ['D', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'm', 'n', 'p', 'r', 's', 't', 'u', 'w', 'ü']}] | ,,Drum prüfe, wer sich ewig bindet". |
| ia_poly1850--231a44f61c5268e0--s021-l0003 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['ΣΑΚΕΛΛΑΡΟΠoraor']}] | ΚΩΝΣΤΑΝΤΙΝΟΥ ΣΑΚΕΛΛΑΡΟΠoraor |
| elstat--07520765bc203a33--s001-l0643 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['VΠΙ']}] | VΠΙ... 128 107 178 |
| elstat--accf92821da614a0--s001-l0018 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['ΝΑΤIONAL']}] | ΕΘΝΙΚΟΝ ΤΥΠΟΓΡΑΦΕΙΟΝ – ΝΑΤIONAL PRINTING OFFICE |
| ia_russian--4ce4c0e3183ce075--s003-l0030 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 13}, 'characters': ['G', 'a', 'c', 'd', 'i', 'l', 'r', 's', 'u']}] | (1) Gadus callaris. |
| elstat--fa8be8ddafd5c043--s001-l0062 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | )) 3 » 10. )) |

## cells

| ID | Kind / outcome | Words / scripts / reason evidence | Raw text |
| --- | --- | --- | --- |
| nlg--f4b52df5f8130047--s010-l0018 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 2.125}] | 4.- |
| gazette_modern--96035db0434dc980--s000-l0074 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1538461538461537}] | 1 |
| gazette_modern--2e613d9290dd13d4--s000-l0017 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4166666666666667}] | 1 |
| gazette_modern--3134c1c6f0ab2f3e--s000-l0045 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1176470588235294}] | 1. |
| gazette_modern--20d238884fd69747--s000-l0032 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2857142857142858}] | 9 |
| ia_poly1850--36dcee7ce4c29f8b--s039-l0061 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3}] | 9 |
| gazette_modern--2ce16341b1b7b83f--s000-l0073 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3888888888888888}] | 2 |
| gazette_modern--1450bd01ddded5ef--s000-l0062 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.6428571428571428}] | (7) |
| ia_poly1850--36dcee7ce4c29f8b--s005-l0102 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4166666666666667}] | 7 |
| elstat--3b2d88122b3f037c--s000-l0756 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2666666666666666}] | 6 |
| elstat--88112979c8a843cb--s001-l0189 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 7 |
| gazette_modern--af7b153702818d6f--s000-l0015 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0952380952380953}] | 1 |
| elstat--c4d30f00b317e558--s001-l0669 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2}] | 5 |
| gazette_modern--bf3c8b13adae55fa--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3}] | 2 |
| gazette_modern--21ec5b038b7e1422--s000-l0071 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1578947368421053}] | 0 |
| gazette_modern--1955eae0881d5641--s000-l0023 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2857142857142858}] | 3 |
| gazette_modern--126dfaa21bc0e1d5--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1904761904761905}] | 4 |
| gazette_modern--0a788b86a71c8e98--s000-l0142 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.5238095238095237}] | 4. |
| gazette_modern--d6092126b747cac8--s000-l0014 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 1 |
| gazette_modern--5ca206a0dc95767d--s000-l0053 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2380952380952381}] | 9 |
| gazette_modern--6bc7acccf0163698--s000-l0268 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 1 |
| gazette_modern--b590ece7e2d52a5c--s000-l0050 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2307692307692308}] | 1 |
| elstat--3b2d88122b3f037c--s000-l0185 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2}] | 7 |
| elstat--c4d30f00b317e558--s001-l0501 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3333333333333333}] | 1 |
| elstat--3b2d88122b3f037c--s001-l0319 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3}] | 9 |
| elstat--3b2d88122b3f037c--s000-l0454 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.125}] | 5 |
| gazette_modern--f63147c9df54d9d4--s000-l0034 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.263157894736842}] | 8 |
| elstat--0a2c92120843658d--s001-l0216 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4705882352941178}] | 1 |
| gazette_modern--929e10adc3109aab--s000-l0027 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.12}] | 2 |
| elstat--d8fe6ab28d6113ba--s001-l0333 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.9166666666666667}] | 2. |
| gazette_modern--70ef76cb8b8c1897--s000-l0075 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.46875}] | (5) |
| gazette_modern--a8e70ef11baca460--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0714285714285714}] | 1 |
| gazette_modern--00a5942b52d08f1e--s000-l0115 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0476190476190477}] | 1 |
| ia_poly1850--26e14cb9c90b750f--s005-l0061 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1025641025641026}] | I |
| gazette_modern--bf43bbfea6d6754d--s000-l0195 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3863636363636365}] | (१) |
| gazette_modern--0089276875b132d9--s000-l0025 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2982456140350878}] | (5) |
| 4b2c4367-p000547-l0056 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['cyrillic'], 'script_counts': {'cyrillic': 4, 'latin': 6}, 'characters': ['д', 'о', 'р', 'ъ']}] | родъ Aranea |

## typology

| ID | Kind / outcome | Words / scripts / reason evidence | Raw text |
| --- | --- | --- | --- |
| bsb_poly1850--2032df1e3e983f1d--s005-l0029 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 7, 'minimum': 10}] | PAEONIA |
| bsb_poly1850--2032df1e3e983f1d--s005-l0217 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 4, 'minimum': 10}] | MEER |
| bsb_poly1850--3496ab66cde251ee--s005-l0112 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 5, 'minimum': 10}] | deles |
| bsb_poly1850--515c78c513c1c8c5--s023-l0094 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 6, 'minimum': 10}] | edidit |
| gazette_modern--37ed2e85ffdd5592--s000-l0067 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 2, 'minimum': 10}] | γ & β, |
| gazette_modern--37ed2e85ffdd5592--s000-l0073 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 2, 'minimum': 10}] | γ & β. |
| gazette_modern--39bf5b1f2419153f--s000-l0002 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.2105263157894737}] | % |
| gazette_modern--49b793056935d163--s000-l0043 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 5}, 'characters': ['ד', 'ו', 'ר']}] | דוד דר |
| gazette_modern--5d57a0a85aede133--s000-l0015 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 3, 'minimum': 10}] | " του |
| gazette_modern--5d57e9c685c50ca6--s000-l0073 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['cyrillic'], 'script_counts': {'cyrillic': 9}, 'characters': ['С', 'а', 'и', 'к', 'н', 'р', 'я']}] | Скрирания |
| gazette_modern--72a5f511c352e013--s000-l0057 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.2222222222222223}] | » |
| gazette_modern--79750acfeada2565--s000-l0058 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ======== |
| gazette_modern--9a06f5aaa5be314f--s000-l0379 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 6, 'minimum': 10}] | πιθανη |
| gazette_modern--b21451311e269f58--s000-l0001 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 2}, 'characters': ['س', 'ے']}] | سے |
| gazette_modern--c90fa267aa2e4dd4--s000-l0083 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 8, 'minimum': 10}] | Γεωργίου |
| gazette_modern--d2281f8022512d7b--s000-l0232 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4}] | m |
| gazette_modern--dc95e9d95cc9cb8e--s000-l0107 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 7, 'minimum': 10}] | κόστους |
| gazette_modern--e418f19baeb555e0--s000-l0026 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 4, 'minimum': 10}] | τσών |
| gazette_modern--f0839209fcdaf7aa--s000-l0036 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.0}] | " |
| gazette_modern--fd6caa884236f7dc--s000-l0118 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3636363636363635}] | A |
| ia_greek_latin--54dae6633713c0a0--s005-l0001 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 7, 'minimum': 10}] | HARVARD |
| ia_greek_latin--8af66d4d113847ee--s003-l0001 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 8, 'minimum': 10}] | CONTENTS. |
| ia_greek_latin--8af66d4d113847ee--s003-l0110 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 3.6}] | ... |
| ia_greek_latin--a232aaf9a41fe898--s001-l0012 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.0281030444964872}] | ***** |
| ia_poly1850--26e14cb9c90b750f--s003-l0047 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 2}, 'characters': ['硬', '頂']}] | 頂 硬 |
| ia_poly1850--26e14cb9c90b750f--s003-l0102 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 1}, 'characters': ['滑']}] | 滑 |
| ia_poly1850--26e14cb9c90b750f--s005-l0016 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 7}, 'characters': ['五', '兒', '凹', '推', '法', '而']}] | 推而凹兒—五法凹 |
| ia_poly1850--2d02eaf0f19a649a--s024-l0004 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 8, 'minimum': 10}] | EDITED BY |
| ia_poly1850--36dcee7ce4c29f8b--s000-l0061 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1}] | t |
| ia_poly1850--63f57af8d450f3e8--s009-l0033 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 8, 'minimum': 10}] | τους υπερ |
| ia_poly1850--63f57af8d450f3e8--s034-l0018 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 6, 'minimum': 10}] | λιππός |
| ia_poly1850--63f57af8d450f3e8--s034-l0019 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1850', 'letters': 5, 'minimum': 10}] | ἐστιν |
| ia_poly1850--6a9e5e4676cec552--s000-l0039 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 2}, 'characters': ['و']}] | وو |
| ia_poly1850--a89bd2c9bdb1ca6d--s008-l0021 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['vἱῷ']}] | vἱῷ om. C |
| ia_poly1850--c3f3a531e277da9a--s001-l0038 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ...... |
| ia_poly1850--c3f3a531e277da9a--s036-l0026 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ..... |
| ia_russian--03b43bc5289ad8ce--s001-l0026 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 5.857142857142857}] | - |
| ia_russian--06528548147a3a3d--s007-l0002 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 4.875}] | - |
| ia_russian--61f76a57b26f9b13--s001-l0004 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 6}, 'characters': ['D', 'L', 'N', 'O']}] | LONDON, |
| ia_russian--6cfc00f06e0f7241--s004-l0043 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ...... |
| kosmopolis--86098eebf5207e79--s003-l0041 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 4, 'minimum': 10}] | στὴν |
| kosmopolis--8ac130e14e062423--s001-l0026 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 4, 'minimum': 10}] | πᾶνε |
| kosmopolis--91040f2da70b9ae0--s004-l0004 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 3, 'minimum': 10}] | ᾿Απὸ |
| kosmopolis--9a17c86798d2c74a--s000-l0030 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 3, 'minimum': 10}] | , ποῦ |
| kosmopolis--9a17c86798d2c74a--s003-l0012 | short_line / DROP | [{'reason': 'short_line', 'role': 'dialogue_fiction', 'letters': 3, 'minimum': 10}] | ” καὶ |
| kosmopolis--9a17c86798d2c74a--s007-l0035 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 4, 'minimum': 10}] | νὰ ξε- |
| kosmopolis--acb323b6cb8d169d--s004-l0035 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 4, 'minimum': 10}] | Σιγά- |
| kosmopolis--ecc23d7812913d0a--s006-l0039 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ...» |
| lekythos--0fc3672826ddd6b3--s001-l0023 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 6, 'minimum': 10}] | βιβλία |
| lekythos--456def1ccfc2283e--s002-l0164 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 5, 'minimum': 10}] | , τὸ πρό- |
| lekythos--49c082ba27aa27da--s000-l0046 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 4, 'minimum': 10}] | Η του |
| lekythos--49c082ba27aa27da--s000-l0241 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 4, 'minimum': 10}] | μὲ τὰ |
| lekythos--7f67b784930deef5--s004-l0020 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 6, 'minimum': 10}] | σας μία |
| lekythos--dcfa99599048d352--s000-l0001 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 4, 'minimum': 10}] | HVED !!-8 |
| lekythos--dcfa99599048d352--s000-l0105 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 9, 'minimum': 10}] | Κάτω ΒΟΛΟΥ |
| nlg--1144074169f43992--s021-l0010 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 6, 'minimum': 10}] | τί ἄλλο |
| nlg--3d6bd7bd688acb61--s024-l0003 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 4.583333333333333}] | - |
| serbia--3ab59a8d4ee49339--s005-l0014 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 6}, 'characters': ['A', 'C', 'I', 'N']}] | INCAII. |
| serbia--b6450341d87fb144--s000-l0005 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 2}, 'characters': ['M', 'i']}] | Mi |
| serbia--b6450341d87fb144--s007-l0002 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['БУE']}] | ВИЉЕМ БУE |
| elstat--5f85f8679b2fe3c7--s001-l0211 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.2}] | )) |
| gazette_modern--e840cbc49c44b1cd--s000-l0096 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 3.25}] | - |
| gazette_modern--f70f27234322ca16--s000-l0399 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4}] | " |
| gazette_modern--f3a8c61be77ca329--s000-l0017 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4210526315789473}] | $ |
| gazette_modern--559faec5ce2b9384--s000-l0185 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2857142857142858}] | E |
| gazette_modern--308a48b3394afaa0--s000-l0024 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 2.0}] | A |
| gazette_modern--72a2c1114189c5cb--s000-l0021 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3125}] | A |
| gazette_modern--d6a330e5d84cd33e--s000-l0095 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.1578947368421053}] | » |
| gazette_modern--9e1d4c7c0ff8a28e--s000-l0042 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 3.3}] | === |
| gazette_modern--00da5133bc9760e8--s000-l0074 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.3333333333333333}] | « |
| gazette_modern--e63ba848f5efa001--s000-l0042 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.5833333333333333}] | " |
| gazette_modern--7a8694d1e521f23e--s000-l0094 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.0909090909090908}] | , |
| gazette_modern--67dfc161a690ff25--s000-l0029 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 1}, 'characters': ['日']}] | 日 |
| gazette_modern--b0dc765920f41797--s000-l0119 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 1}, 'characters': ['द']}] | द |
| gazette_modern--72a5f511c352e013--s000-l0105 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.2222222222222223}] | » |
| gazette_modern--70dafa4f769a0d6a--s000-l0067 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 3}, 'characters': ['د', 'ن', 'و']}] | 21 .وند |
| gazette_modern--210c5618de6d9b6d--s000-l0039 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1111111111111112}] | Β΄ |
| gazette_modern--15c41c921f3bcb82--s000-l0062 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.2352941176470589}] | » |
| gazette_modern--2d33128074623cb8--s000-l0040 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 2.75}] | » » |
| gazette_modern--92fb735e336d11f5--s000-l0002 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4339622641509433}] | + |
| gazette_modern--210c5618de6d9b6d--s000-l0069 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1153846153846154}] | n) |
| gazette_modern--2c53a696417985d2--s000-l0032 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4705882352941178}] | : |
| gazette_modern--d750387e4a01e942--s000-l0040 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.1875}] | )) |
| ia_greek_latin--8af66d4d113847ee--s003-l0174 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.3846153846153846}] | • |
| ia_greek_latin--e02bf39b0ef9974e--s004-l0114 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.53125}] | Ο |
| ia_greek_latin--e02bf39b0ef9974e--s008-l0006 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 4.25}] | } |
| ia_poly1850--ca4f3983c96b6334--s022-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 4.454545454545454}] | - |
| ia_poly1850--ca4f3983c96b6334--s002-l0002 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 5.454545454545454}] | - |
| ia_poly1850--c3f3a531e277da9a--s038-l0006 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 1}, 'characters': ['カ']}] | カ |
| ia_poly1850--36dcee7ce4c29f8b--s010-l0073 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 2.606060606060606}] | ἱ |
| ia_poly1850--6a9e5e4676cec552--s019-l0043 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 4.454545454545454}] | - |
| ia_poly1850--26e14cb9c90b750f--s003-l0077 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 2}, 'characters': ['厚', '點']}] | 厚點 |
| ia_poly1850--26e14cb9c90b750f--s003-l0009 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 2}, 'characters': ['兜', '必']}] | 必兜 |
| ia_poly1850--34543d92a48213e7--s024-l0007 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 3.5}] | - |
| ia_poly1850--21c15fc15dc17003--s009-l0065 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.3181818181818181}] | " |
| ia_poly1850--36dcee7ce4c29f8b--s025-l0010 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1612903225806452}] | h |
| ia_russian--06528548147a3a3d--s005-l0029 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 1}, 'characters': ['و']}] | و |
| ia_russian--2a45a0561eb05739--s002-l0002 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 6}, 'characters': ['E', 'G', 'N', 'O', 'R']}] | OREGON |
| kosmopolis--86098eebf5207e79--s006-l0031 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.3333333333333333}] | " |
| lekythos--e9f314aab488b65f--s000-l0265 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 3.1}] | - "A |
| lekythos--dcfa99599048d352--s000-l0174 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.5454545454545454}] | > |
| lekythos--dcfa99599048d352--s000-l0161 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.6363636363636365}] | « |
| nlg--3d6bd7bd688acb61--s029-l0031 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 2}, 'characters': ['ہ', 'ی']}] | یہ |
| nlg--6ae0ac01064a587e--s011-l0007 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 5.636363636363637}] | - |
| nlg--7870403c3df244ea--s038-l0008 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3333333333333333}] | G |
| serbia--42fedee06e6cb85a--s005-l0004 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.3125}] | * |
| bsb_poly1850--027215cc6d2a7e8a--s027-l0003 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 1}, 'characters': ['م']}] | م٦١٦ |
| gazette_modern--c694a4568affabd6--s000-l0130 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 2}, 'characters': ['の', '機']}] | 3.13.の機 |
| gazette_modern--5d05d04d136ea2c2--s000-l0120 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 2}, 'characters': ['つ', 'に']}] | 3つに |
| gazette_modern--af3a940b646b3a7d--s000-l0242 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 5.75}] | ----- |
| gazette_modern--7b6b2ad720aaf57d--s000-l0047 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 2.6923076923076925}] | == |
| gazette_modern--52ee6226bb7d4834--s000-l0091 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4705882352941178}] | * |
| gazette_modern--5c36407f5c0b0aa3--s000-l0117 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 2.7142857142857144}] | ...... |
| gazette_modern--c9931c881b131806--s000-l0111 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4230769230769231}] | E |
| gazette_modern--3dc14e0d9926346a--s000-l0020 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 2.727272727272727}] | == |
| gazette_modern--7a8694d1e521f23e--s000-l0144 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.3}] | , |
| serbia--557369d8d117b91a--s000-l0028 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 9}, 'characters': ['E', 'a', 'g', 'l', 'n', 'r', 'é']}] | En général |
| gazette_modern--9a06f5aaa5be314f--s000-l0343 | short_line / DROP | [{'reason': 'short_line', 'role': 'headings_caps', 'letters': 3, 'minimum': 4}] | Α.Τ. Α 585272 |
| ia_poly1850--5aa15e93b2f445b8--s011-l0002 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 9, 'minimum': 10}] | PRAEFATIO |
| ia_poly1850--5aa15e93b2f445b8--s005-l0001 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['PRAEFATΙΟ']}] | PRAEFATΙΟ |
| ia_russian--3ecca278cf0eea22--s004-l0041 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | \| |
| gazette_modern--e1ffcad236d8706c--s000-l0150 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ------- |
| kosmopolis--86098eebf5207e79--s003-l0024 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 7, 'minimum': 10}] | ῾τόνισσα |
| gazette_modern--b9f59878fb904d91--s000-l0156 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ===== |
| serbia--42fedee06e6cb85a--s009-l0001 | short_line / DROP | [{'reason': 'short_line', 'role': 'cyrillic', 'letters': 5, 'minimum': 10}] | ПЕСМЕ |
| ia_russian--06528548147a3a3d--s000-l0001 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | - |
| gazette_modern--00f1483e61cf1864--s000-l0228 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ::::-: |
| gazette_modern--57b18cd8ba2ce4fd--s000-l0163 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ======== |
| ia_poly1850--34543d92a48213e7--s000-l0054 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | - |
| nlg--1144074169f43992--s017-l0006 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 8, 'minimum': 10}] | OF GREECE |
| gazette_modern--6d0a93d9389e859c--s000-l0013 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ------ |
| gazette_modern--5158b7bf9def2bab--s000-l0012 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.875}] | - |
| lekythos--a0c4e6327052acfc--s002-l0089 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.2}] | / |

## owner_marks

| ID | Kind / outcome | Words / scripts / reason evidence | Raw text |
| --- | --- | --- | --- |
| gazette_modern--13a9303cfc83a9d4--s000-l0045 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0625}] | 3 |
| gazette_modern--1456dcb167f23bfe--s000-l0027 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0909090909090908}] | 1 |
| gazette_modern--5158b7bf9def2bab--s000-l0012 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.875}] | - |
| gazette_modern--5d57e9c685c50ca6--s000-l0073 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['cyrillic'], 'script_counts': {'cyrillic': 9}, 'characters': ['С', 'а', 'и', 'к', 'н', 'р', 'я']}] | Скрирания |
| gazette_modern--9701a3a500ecbd85--s000-l0011 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 7, 'minimum': 10}] | 165, πτυχιού- |
| gazette_modern--aeb6eb76fc7057f0--s000-l0050 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4}] | " |
| gazette_modern--bd7c91e6a214949b--s000-l0125 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['ハンハンΟΜΙΑΣ']}, {'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'greek': 5, 'other': 4}, 'characters': ['ハ', 'ン']}] | ハンハンΟΜΙΑΣ. |
| gazette_modern--c90fa267aa2e4dd4--s000-l0083 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 8, 'minimum': 10}] | Γεωργίου |
| lekythos--a0c4e6327052acfc--s002-l0089 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.2}] | / |
| nlg--3d6bd7bd688acb61--s024-l0003 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 4.583333333333333}] | - |
| elstat--0a2c92120843658d--s001-l0216 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4705882352941178}] | 1 |
| elstat--3b2d88122b3f037c--s000-l0185 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2}] | 7 |
| elstat--3b2d88122b3f037c--s000-l0454 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.125}] | 5 |
| elstat--3b2d88122b3f037c--s000-l0756 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2666666666666666}] | 6 |
| elstat--3b2d88122b3f037c--s001-l0319 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3}] | 9 |
| elstat--88112979c8a843cb--s001-l0189 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 7 |
| elstat--c4d30f00b317e558--s001-l0501 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3333333333333333}] | 1 |
| elstat--c4d30f00b317e558--s001-l0669 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2}] | 5 |
| elstat--d8fe6ab28d6113ba--s001-l0333 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.9166666666666667}] | 2. |
| gazette_modern--00a5942b52d08f1e--s000-l0115 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0476190476190477}] | 1 |
| gazette_modern--0a788b86a71c8e98--s000-l0142 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.5238095238095237}] | 4. |
| gazette_modern--126dfaa21bc0e1d5--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1904761904761905}] | 4 |
| gazette_modern--1450bd01ddded5ef--s000-l0062 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.6428571428571428}] | (7) |
| gazette_modern--1955eae0881d5641--s000-l0023 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2857142857142858}] | 3 |
| gazette_modern--20d238884fd69747--s000-l0032 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2857142857142858}] | 9 |
| gazette_modern--21ec5b038b7e1422--s000-l0071 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1578947368421053}] | 0 |
| gazette_modern--2ce16341b1b7b83f--s000-l0073 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3888888888888888}] | 2 |
| gazette_modern--2e613d9290dd13d4--s000-l0017 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4166666666666667}] | 1 |
| gazette_modern--3134c1c6f0ab2f3e--s000-l0045 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1176470588235294}] | 1. |
| gazette_modern--5ca206a0dc95767d--s000-l0053 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2380952380952381}] | 9 |
| gazette_modern--6bc7acccf0163698--s000-l0268 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 1 |
| gazette_modern--70ef76cb8b8c1897--s000-l0075 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.46875}] | (5) |
| gazette_modern--929e10adc3109aab--s000-l0027 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.12}] | 2 |
| gazette_modern--96035db0434dc980--s000-l0074 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1538461538461537}] | 1 |
| gazette_modern--a8e70ef11baca460--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0714285714285714}] | 1 |
| gazette_modern--b590ece7e2d52a5c--s000-l0050 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2307692307692308}] | 1 |
| gazette_modern--bf3c8b13adae55fa--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3}] | 2 |
| gazette_modern--d6092126b747cac8--s000-l0014 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 1 |
| gazette_modern--f63147c9df54d9d4--s000-l0034 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.263157894736842}] | 8 |
| ia_poly1850--36dcee7ce4c29f8b--s005-l0102 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4166666666666667}] | 7 |
| ia_poly1850--36dcee7ce4c29f8b--s039-l0061 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3}] | 9 |
| nlg--f4b52df5f8130047--s010-l0018 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 2.125}] | 4.- |
| lekythos--456def1ccfc2283e--s001-l0177 | numeric_shape / DROP | [{'reason': 'numeric_shape', 'alnum': 1, 'detail': '<=1 letter-or-digit'}] | -'-'-'-'-'-'-'0 |
| serbia--3ab59a8d4ee49339--s005-l0014 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 6}, 'characters': ['A', 'C', 'I', 'N']}] | INCAII. |

## rated_888

| ID | Kind / outcome | Words / scripts / reason evidence | Raw text |
| --- | --- | --- | --- |
| bsb_poly1850--2032df1e3e983f1d--s005-l0029 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 7, 'minimum': 10}] | PAEONIA |
| bsb_poly1850--2032df1e3e983f1d--s005-l0217 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 4, 'minimum': 10}] | MEER |
| bsb_poly1850--3496ab66cde251ee--s005-l0112 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 5, 'minimum': 10}] | deles |
| bsb_poly1850--515c78c513c1c8c5--s023-l0094 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 6, 'minimum': 10}] | edidit |
| elstat--2b5780c7c9896a54--s000-l0051 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 8, 'minimum': 10}] | Sommaire |
| gazette_modern--37ed2e85ffdd5592--s000-l0067 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 2, 'minimum': 10}] | γ & β, |
| gazette_modern--37ed2e85ffdd5592--s000-l0073 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 2, 'minimum': 10}] | γ & β. |
| gazette_modern--5d57a0a85aede133--s000-l0015 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 3, 'minimum': 10}] | " του |
| gazette_modern--9a06f5aaa5be314f--s000-l0379 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 6, 'minimum': 10}] | πιθανη |
| gazette_modern--dc95e9d95cc9cb8e--s000-l0107 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 7, 'minimum': 10}] | κόστους |
| gazette_modern--df5a370d8f003110--s000-l0015 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 38}, 'characters': ['י', 'ן']}] | ייייייייייייייייייייייייייייייייייייין |
| gazette_modern--e418f19baeb555e0--s000-l0026 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 4, 'minimum': 10}] | τσών |
| ia_greek_latin--54dae6633713c0a0--s005-l0001 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 7, 'minimum': 10}] | HARVARD |
| ia_greek_latin--8af66d4d113847ee--s003-l0001 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 8, 'minimum': 10}] | CONTENTS. |
| ia_greek_latin--8af66d4d113847ee--s003-l0022 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ...................... |
| ia_greek_latin--8af66d4d113847ee--s003-l0107 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ......................... |
| ia_greek_latin--a232aaf9a41fe898--s001-l0012 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.0281030444964872}] | ***** |
| ia_greek_latin--f40a7578d8cd5825--s002-l0112 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ------------ |
| ia_poly1850--63f57af8d450f3e8--s009-l0033 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 8, 'minimum': 10}] | τους υπερ |
| ia_poly1850--63f57af8d450f3e8--s034-l0018 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 6, 'minimum': 10}] | λιππός |
| ia_poly1850--63f57af8d450f3e8--s034-l0019 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1850', 'letters': 5, 'minimum': 10}] | ἐστιν |
| ia_poly1850--a89bd2c9bdb1ca6d--s034-l0035 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | .......... |
| ia_poly1850--c3f3a531e277da9a--s036-l0026 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ..... |
| ia_russian--61f76a57b26f9b13--s001-l0004 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 6}, 'characters': ['D', 'L', 'N', 'O']}] | LONDON, |
| ia_russian--61f76a57b26f9b13--s001-l0005 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 23}, 'characters': ['A', 'B', 'C', 'E', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'W', 'o']}] | TRUBNER & Co. 60, PATERNOSTER ROW, |
| ia_russian--6cfc00f06e0f7241--s004-l0043 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ...... |
| kosmopolis--86098eebf5207e79--s003-l0041 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 4, 'minimum': 10}] | στὴν |
| kosmopolis--8ac130e14e062423--s001-l0026 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 4, 'minimum': 10}] | πᾶνε |
| kosmopolis--91040f2da70b9ae0--s004-l0004 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 3, 'minimum': 10}] | ᾿Απὸ |
| kosmopolis--9a17c86798d2c74a--s000-l0030 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 3, 'minimum': 10}] | , ποῦ |
| kosmopolis--9a17c86798d2c74a--s003-l0012 | short_line / DROP | [{'reason': 'short_line', 'role': 'dialogue_fiction', 'letters': 3, 'minimum': 10}] | ” καὶ |
| kosmopolis--9a17c86798d2c74a--s007-l0035 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 4, 'minimum': 10}] | νὰ ξε- |
| kosmopolis--ecc23d7812913d0a--s006-l0039 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ...» |
| lekythos--0fc3672826ddd6b3--s001-l0023 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 6, 'minimum': 10}] | βιβλία |
| lekythos--456def1ccfc2283e--s001-l0177 | numeric_shape / DROP | [{'reason': 'numeric_shape', 'alnum': 1, 'detail': '<=1 letter-or-digit'}] | -'-'-'-'-'-'-'0 |
| lekythos--49c082ba27aa27da--s000-l0046 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 4, 'minimum': 10}] | Η του |
| lekythos--49c082ba27aa27da--s000-l0241 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 4, 'minimum': 10}] | μὲ τὰ |
| lekythos--7f67b784930deef5--s004-l0020 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 6, 'minimum': 10}] | σας μία |
| lekythos--dcfa99599048d352--s000-l0105 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 9, 'minimum': 10}] | Κάτω ΒΟΛΟΥ |
| nlg--1144074169f43992--s021-l0010 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 6, 'minimum': 10}] | τί ἄλλο |
| serbia--27b182bf4116728f--s008-l0003 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['рѣza']}] | Г. Ана: Гуліани рѣza y Mabmk: 1817, |
| serbia--3ab59a8d4ee49339--s005-l0014 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 6}, 'characters': ['A', 'C', 'I', 'N']}] | INCAII. |
| serbia--b6450341d87fb144--s007-l0002 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['БУE']}] | ВИЉЕМ БУE |
| serbia--e7935cdb3dfeaf10--s006-l0006 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 26}, 'characters': ['D', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'm', 'n', 'p', 'r', 's', 't', 'u', 'w', 'ü']}] | ,,Drum prüfe, wer sich ewig bindet". |

## typology_marked

| ID | Kind / outcome | Words / scripts / reason evidence | Raw text |
| --- | --- | --- | --- |
| bsb_poly1850--2032df1e3e983f1d--s005-l0029 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 7, 'minimum': 10}] | PAEONIA |
| bsb_poly1850--2032df1e3e983f1d--s005-l0217 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 4, 'minimum': 10}] | MEER |
| ia_greek_latin--54dae6633713c0a0--s005-l0001 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 7, 'minimum': 10}] | HARVARD |
| ia_greek_latin--8af66d4d113847ee--s003-l0001 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 8, 'minimum': 10}] | CONTENTS. |
| ia_poly1850--2d02eaf0f19a649a--s024-l0004 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 8, 'minimum': 10}] | EDITED BY |
| ia_russian--61f76a57b26f9b13--s001-l0004 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 6}, 'characters': ['D', 'L', 'N', 'O']}] | LONDON, |
| ia_russian--2a45a0561eb05739--s002-l0002 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 6}, 'characters': ['E', 'G', 'N', 'O', 'R']}] | OREGON |
| serbia--557369d8d117b91a--s000-l0028 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 9}, 'characters': ['E', 'a', 'g', 'l', 'n', 'r', 'é']}] | En général |
| ia_poly1850--5aa15e93b2f445b8--s005-l0001 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['PRAEFATΙΟ']}] | PRAEFATΙΟ |

## small

| ID | Kind / outcome | Words / scripts / reason evidence | Raw text |
| --- | --- | --- | --- |
| lekythos--a0c4e6327052acfc--s002-l0089 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.2}] | / |
| gazette_modern--13a9303cfc83a9d4--s000-l0045 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0625}] | 3 |
| gazette_modern--1456dcb167f23bfe--s000-l0027 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0909090909090908}] | 1 |
| gazette_modern--5158b7bf9def2bab--s000-l0012 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.875}] | - |
| gazette_modern--6d58ca2e2dc41e69--s000-l0067 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1666666666666667}] | 4. |
| gazette_modern--aeb6eb76fc7057f0--s000-l0050 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4}] | " |
| nlg--3d6bd7bd688acb61--s024-l0003 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 4.583333333333333}] | - |
| elstat--996d9f614c928993--s000-l0085 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 3}, 'characters': ['ق', 'م', 'و']}] | قوم |
| elstat--ee37bc488988f1bd--s000-l0998 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 2.5}] | x. |
| ia_greek_latin--ef6c2c5c1ba30b47--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.048780487804878}] | 8 |
| ia_russian--d558bd3e803e7865--s007-l0031 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 5.0}] | - |
| bsb_poly1850--fe51c7e60c92453d--s034-l0003 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.5454545454545454}] | A |
| gazette_modern--8757f64ef1908c90--s000-l0003 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4482758620689655}] | (3) |
| ia_greek_latin--a232aaf9a41fe898--s001-l0012 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.0281030444964872}] | ***** |
| ia_russian--61f76a57b26f9b13--s001-l0004 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 6}, 'characters': ['D', 'L', 'N', 'O']}] | LONDON, |
| nlg--f4b52df5f8130047--s010-l0018 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 2.125}] | 4.- |
| gazette_modern--96035db0434dc980--s000-l0074 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1538461538461537}] | 1 |
| gazette_modern--2e613d9290dd13d4--s000-l0017 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4166666666666667}] | 1 |
| gazette_modern--3134c1c6f0ab2f3e--s000-l0045 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1176470588235294}] | 1. |
| gazette_modern--20d238884fd69747--s000-l0032 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2857142857142858}] | 9 |
| ia_poly1850--36dcee7ce4c29f8b--s039-l0061 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3}] | 9 |
| gazette_modern--2ce16341b1b7b83f--s000-l0073 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3888888888888888}] | 2 |
| gazette_modern--1450bd01ddded5ef--s000-l0062 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.6428571428571428}] | (7) |
| ia_poly1850--36dcee7ce4c29f8b--s005-l0102 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4166666666666667}] | 7 |
| elstat--3b2d88122b3f037c--s000-l0756 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2666666666666666}] | 6 |
| elstat--88112979c8a843cb--s001-l0189 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 7 |
| gazette_modern--af7b153702818d6f--s000-l0015 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0952380952380953}] | 1 |
| elstat--c4d30f00b317e558--s001-l0669 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2}] | 5 |
| gazette_modern--bf3c8b13adae55fa--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3}] | 2 |
| gazette_modern--21ec5b038b7e1422--s000-l0071 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1578947368421053}] | 0 |
| gazette_modern--1955eae0881d5641--s000-l0023 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2857142857142858}] | 3 |
| gazette_modern--126dfaa21bc0e1d5--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1904761904761905}] | 4 |
| gazette_modern--0a788b86a71c8e98--s000-l0142 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.5238095238095237}] | 4. |
| gazette_modern--d6092126b747cac8--s000-l0014 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 1 |
| gazette_modern--5ca206a0dc95767d--s000-l0053 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2380952380952381}] | 9 |
| gazette_modern--6bc7acccf0163698--s000-l0268 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 1 |
| gazette_modern--b590ece7e2d52a5c--s000-l0050 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2307692307692308}] | 1 |
| elstat--3b2d88122b3f037c--s000-l0185 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2}] | 7 |
| elstat--c4d30f00b317e558--s001-l0501 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3333333333333333}] | 1 |
| elstat--3b2d88122b3f037c--s001-l0319 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3}] | 9 |
| elstat--3b2d88122b3f037c--s000-l0454 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.125}] | 5 |
| gazette_modern--f63147c9df54d9d4--s000-l0034 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.263157894736842}] | 8 |
| elstat--0a2c92120843658d--s001-l0216 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4705882352941178}] | 1 |
| gazette_modern--929e10adc3109aab--s000-l0027 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.12}] | 2 |
| elstat--d8fe6ab28d6113ba--s001-l0333 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.9166666666666667}] | 2. |
| gazette_modern--70ef76cb8b8c1897--s000-l0075 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.46875}] | (5) |
| gazette_modern--a8e70ef11baca460--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0714285714285714}] | 1 |
| gazette_modern--00a5942b52d08f1e--s000-l0115 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0476190476190477}] | 1 |
| ia_poly1850--26e14cb9c90b750f--s005-l0061 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1025641025641026}] | I |
| gazette_modern--bf43bbfea6d6754d--s000-l0195 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3863636363636365}] | (१) |
| gazette_modern--0089276875b132d9--s000-l0025 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2982456140350878}] | (5) |
| gazette_modern--39bf5b1f2419153f--s000-l0002 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.2105263157894737}] | % |
| gazette_modern--49b793056935d163--s000-l0043 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 5}, 'characters': ['ד', 'ו', 'ר']}] | דוד דר |
| gazette_modern--72a5f511c352e013--s000-l0049 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.1666666666666667}] | » |
| gazette_modern--72a5f511c352e013--s000-l0057 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.2222222222222223}] | » |
| gazette_modern--72a5f511c352e013--s000-l0079 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.1666666666666667}] | » |
| gazette_modern--98dfb00fa203c6d5--s000-l0048 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 2.761904761904762}] | 《 《 |
| gazette_modern--aeb6eb76fc7057f0--s000-l0050 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4}] | " |
| gazette_modern--b21451311e269f58--s000-l0001 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 2}, 'characters': ['س', 'ے']}] | سے |
| gazette_modern--d2281f8022512d7b--s000-l0232 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4}] | m |
| gazette_modern--f0839209fcdaf7aa--s000-l0036 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.0}] | " |
| gazette_modern--fd0c55b5cf1557ca--s000-l0042 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 4}, 'characters': ['ا', 'ر', 'ل', 'ن']}] | لارن |
| gazette_modern--fd6caa884236f7dc--s000-l0118 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3636363636363635}] | A |
| ia_greek_latin--8af66d4d113847ee--s003-l0110 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 3.6}] | ... |
| ia_greek_latin--a232aaf9a41fe898--s001-l0012 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.0281030444964872}] | ***** |
| ia_greek_latin--e3dff0a8a9829e59--s006-l0026 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4166666666666667}] | '. |
| ia_poly1850--26e14cb9c90b750f--s003-l0047 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 2}, 'characters': ['硬', '頂']}] | 頂 硬 |
| ia_poly1850--26e14cb9c90b750f--s003-l0102 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 1}, 'characters': ['滑']}] | 滑 |
| ia_poly1850--36dcee7ce4c29f8b--s000-l0061 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1}] | t |
| ia_poly1850--6a9e5e4676cec552--s000-l0039 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 2}, 'characters': ['و']}] | وو |
| ia_poly1850--a89bd2c9bdb1ca6d--s008-l0021 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['vἱῷ']}] | vἱῷ om. C |
| ia_russian--03b43bc5289ad8ce--s001-l0026 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 5.857142857142857}] | - |
| ia_russian--06528548147a3a3d--s007-l0002 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 4.875}] | - |
| ia_russian--61f76a57b26f9b13--s001-l0004 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 6}, 'characters': ['D', 'L', 'N', 'O']}] | LONDON, |
| nlg--3d6bd7bd688acb61--s024-l0003 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 4.583333333333333}] | - |
| serbia--b6450341d87fb144--s000-l0005 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 2}, 'characters': ['M', 'i']}] | Mi |
| elstat--5f85f8679b2fe3c7--s001-l0211 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.2}] | )) |
| gazette_modern--e840cbc49c44b1cd--s000-l0096 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 3.25}] | - |
| gazette_modern--f70f27234322ca16--s000-l0399 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4}] | " |
| gazette_modern--f3a8c61be77ca329--s000-l0017 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4210526315789473}] | $ |
| gazette_modern--559faec5ce2b9384--s000-l0185 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2857142857142858}] | E |
| gazette_modern--308a48b3394afaa0--s000-l0024 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 2.0}] | A |
| gazette_modern--72a2c1114189c5cb--s000-l0021 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3125}] | A |
| gazette_modern--d6a330e5d84cd33e--s000-l0095 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.1578947368421053}] | » |
| gazette_modern--9e1d4c7c0ff8a28e--s000-l0042 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 3.3}] | === |
| gazette_modern--00da5133bc9760e8--s000-l0074 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.3333333333333333}] | « |
| gazette_modern--e63ba848f5efa001--s000-l0042 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.5833333333333333}] | " |
| gazette_modern--7a8694d1e521f23e--s000-l0094 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.0909090909090908}] | , |
| gazette_modern--67dfc161a690ff25--s000-l0029 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 1}, 'characters': ['日']}] | 日 |
| gazette_modern--b0dc765920f41797--s000-l0119 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 1}, 'characters': ['द']}] | द |
| gazette_modern--72a5f511c352e013--s000-l0105 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.2222222222222223}] | » |
| gazette_modern--70dafa4f769a0d6a--s000-l0067 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 3}, 'characters': ['د', 'ن', 'و']}] | 21 .وند |
| gazette_modern--210c5618de6d9b6d--s000-l0039 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1111111111111112}] | Β΄ |
| gazette_modern--15c41c921f3bcb82--s000-l0062 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.2352941176470589}] | » |
| gazette_modern--2d33128074623cb8--s000-l0040 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 2.75}] | » » |
| gazette_modern--92fb735e336d11f5--s000-l0002 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4339622641509433}] | + |
| gazette_modern--210c5618de6d9b6d--s000-l0069 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1153846153846154}] | n) |
| gazette_modern--2c53a696417985d2--s000-l0032 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4705882352941178}] | : |
| gazette_modern--d750387e4a01e942--s000-l0040 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.1875}] | )) |
| ia_greek_latin--8af66d4d113847ee--s003-l0174 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.3846153846153846}] | • |
| ia_greek_latin--e02bf39b0ef9974e--s004-l0114 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.53125}] | Ο |
| ia_greek_latin--e02bf39b0ef9974e--s008-l0006 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 4.25}] | } |
| ia_poly1850--ca4f3983c96b6334--s022-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 4.454545454545454}] | - |
| ia_poly1850--ca4f3983c96b6334--s002-l0002 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 5.454545454545454}] | - |
| ia_poly1850--c3f3a531e277da9a--s038-l0006 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 1}, 'characters': ['カ']}] | カ |
| ia_poly1850--36dcee7ce4c29f8b--s010-l0073 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 2.606060606060606}] | ἱ |
| ia_poly1850--6a9e5e4676cec552--s019-l0043 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 4.454545454545454}] | - |
| ia_poly1850--26e14cb9c90b750f--s003-l0077 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 2}, 'characters': ['厚', '點']}] | 厚點 |
| ia_poly1850--26e14cb9c90b750f--s003-l0009 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 2}, 'characters': ['兜', '必']}] | 必兜 |
| ia_poly1850--34543d92a48213e7--s024-l0007 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 3.5}] | - |
| ia_poly1850--21c15fc15dc17003--s009-l0065 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.3181818181818181}] | " |
| ia_poly1850--36dcee7ce4c29f8b--s025-l0010 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1612903225806452}] | h |
| ia_russian--06528548147a3a3d--s005-l0029 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 1}, 'characters': ['و']}] | و |
| ia_russian--2a45a0561eb05739--s002-l0002 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 6}, 'characters': ['E', 'G', 'N', 'O', 'R']}] | OREGON |
| kosmopolis--86098eebf5207e79--s006-l0031 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.3333333333333333}] | " |
| lekythos--e9f314aab488b65f--s000-l0265 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 3.1}] | - "A |
| lekythos--dcfa99599048d352--s000-l0174 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.5454545454545454}] | > |
| lekythos--dcfa99599048d352--s000-l0161 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.6363636363636365}] | « |
| nlg--3d6bd7bd688acb61--s029-l0031 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 2}, 'characters': ['ہ', 'ی']}] | یہ |
| nlg--6ae0ac01064a587e--s011-l0007 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 5.636363636363637}] | - |
| nlg--7870403c3df244ea--s038-l0008 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3333333333333333}] | G |
| serbia--42fedee06e6cb85a--s005-l0004 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.3125}] | * |
| bsb_poly1850--027215cc6d2a7e8a--s027-l0003 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 1}, 'characters': ['م']}] | م٦١٦ |
| gazette_modern--c694a4568affabd6--s000-l0130 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 2}, 'characters': ['の', '機']}] | 3.13.の機 |
| gazette_modern--5d05d04d136ea2c2--s000-l0120 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 2}, 'characters': ['つ', 'に']}] | 3つに |
| gazette_modern--af3a940b646b3a7d--s000-l0242 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 5.75}] | ----- |
| gazette_modern--7b6b2ad720aaf57d--s000-l0047 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 2.6923076923076925}] | == |
| gazette_modern--52ee6226bb7d4834--s000-l0091 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4705882352941178}] | * |
| gazette_modern--5c36407f5c0b0aa3--s000-l0117 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 2.7142857142857144}] | ...... |
| gazette_modern--c9931c881b131806--s000-l0111 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4230769230769231}] | E |
| gazette_modern--3dc14e0d9926346a--s000-l0020 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 2.727272727272727}] | == |
| gazette_modern--7a8694d1e521f23e--s000-l0144 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.3}] | , |
| gazette_modern--5158b7bf9def2bab--s000-l0012 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.875}] | - |
| lekythos--a0c4e6327052acfc--s002-l0089 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.2}] | / |

## band_population

| ID | Kind / outcome | Words / scripts / reason evidence | Raw text |
| --- | --- | --- | --- |
| bsb_poly1850--2032df1e3e983f1d--s005-l0029 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 7, 'minimum': 10}] | PAEONIA |
| bsb_poly1850--515c78c513c1c8c5--s023-l0094 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 6, 'minimum': 10}] | edidit |
| elstat--0a2c92120843658d--s001-l0216 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4705882352941178}] | 1 |
| elstat--2b5780c7c9896a54--s000-l0051 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 8, 'minimum': 10}] | Sommaire |
| elstat--3b2d88122b3f037c--s000-l0185 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2}] | 7 |
| elstat--3b2d88122b3f037c--s000-l0454 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.125}] | 5 |
| elstat--3b2d88122b3f037c--s000-l0756 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2666666666666666}] | 6 |
| elstat--3b2d88122b3f037c--s001-l0319 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3}] | 9 |
| elstat--88112979c8a843cb--s001-l0189 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 7 |
| elstat--c4d30f00b317e558--s001-l0501 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3333333333333333}] | 1 |
| elstat--c4d30f00b317e558--s001-l0669 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2}] | 5 |
| elstat--d8fe6ab28d6113ba--s001-l0333 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.9166666666666667}] | 2. |
| gazette_modern--00a5942b52d08f1e--s000-l0115 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0476190476190477}] | 1 |
| gazette_modern--0a788b86a71c8e98--s000-l0142 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.5238095238095237}] | 4. |
| gazette_modern--126dfaa21bc0e1d5--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1904761904761905}] | 4 |
| gazette_modern--13a9303cfc83a9d4--s000-l0045 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0625}] | 3 |
| gazette_modern--1450bd01ddded5ef--s000-l0062 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.6428571428571428}] | (7) |
| gazette_modern--1456dcb167f23bfe--s000-l0027 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0909090909090908}] | 1 |
| gazette_modern--1955eae0881d5641--s000-l0023 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2857142857142858}] | 3 |
| gazette_modern--20d238884fd69747--s000-l0032 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2857142857142858}] | 9 |
| gazette_modern--21ec5b038b7e1422--s000-l0071 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1578947368421053}] | 0 |
| gazette_modern--2ce16341b1b7b83f--s000-l0073 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3888888888888888}] | 2 |
| gazette_modern--2e613d9290dd13d4--s000-l0017 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4166666666666667}] | 1 |
| gazette_modern--3134c1c6f0ab2f3e--s000-l0045 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1176470588235294}] | 1. |
| gazette_modern--37ed2e85ffdd5592--s000-l0073 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 2, 'minimum': 10}] | γ & β. |
| gazette_modern--5158b7bf9def2bab--s000-l0012 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.875}] | - |
| gazette_modern--5ca206a0dc95767d--s000-l0053 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2380952380952381}] | 9 |
| gazette_modern--5d57e9c685c50ca6--s000-l0073 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['cyrillic'], 'script_counts': {'cyrillic': 9}, 'characters': ['С', 'а', 'и', 'к', 'н', 'р', 'я']}] | Скрирания |
| gazette_modern--6bc7acccf0163698--s000-l0268 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 1 |
| gazette_modern--70ef76cb8b8c1897--s000-l0075 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.46875}] | (5) |
| gazette_modern--929e10adc3109aab--s000-l0027 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.12}] | 2 |
| gazette_modern--96035db0434dc980--s000-l0074 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1538461538461537}] | 1 |
| gazette_modern--9701a3a500ecbd85--s000-l0011 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 7, 'minimum': 10}] | 165, πτυχιού- |
| gazette_modern--a8e70ef11baca460--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0714285714285714}] | 1 |
| gazette_modern--aeb6eb76fc7057f0--s000-l0050 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4}] | " |
| gazette_modern--b590ece7e2d52a5c--s000-l0050 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2307692307692308}] | 1 |
| gazette_modern--bd7c91e6a214949b--s000-l0125 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['ハンハンΟΜΙΑΣ']}, {'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'greek': 5, 'other': 4}, 'characters': ['ハ', 'ン']}] | ハンハンΟΜΙΑΣ. |
| gazette_modern--bf3c8b13adae55fa--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3}] | 2 |
| gazette_modern--c90fa267aa2e4dd4--s000-l0083 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 8, 'minimum': 10}] | Γεωργίου |
| gazette_modern--d6092126b747cac8--s000-l0014 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 1 |
| gazette_modern--df5a370d8f003110--s000-l0015 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 38}, 'characters': ['י', 'ן']}] | ייייייייייייייייייייייייייייייייייייין |
| gazette_modern--e418f19baeb555e0--s000-l0026 | short_line / DROP | [{'reason': 'short_line', 'role': 'modern_scanned', 'letters': 4, 'minimum': 10}] | τσών |
| gazette_modern--f63147c9df54d9d4--s000-l0034 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.263157894736842}] | 8 |
| ia_greek_latin--54dae6633713c0a0--s005-l0001 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 7, 'minimum': 10}] | HARVARD |
| ia_greek_latin--8af66d4d113847ee--s003-l0001 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 8, 'minimum': 10}] | CONTENTS. |
| ia_greek_latin--8af66d4d113847ee--s003-l0022 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ...................... |
| ia_greek_latin--8af66d4d113847ee--s003-l0107 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ......................... |
| ia_greek_latin--a232aaf9a41fe898--s001-l0012 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.0281030444964872}] | ***** |
| ia_poly1850--2d02eaf0f19a649a--s024-l0004 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 8, 'minimum': 10}] | EDITED BY |
| ia_poly1850--36dcee7ce4c29f8b--s005-l0102 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4166666666666667}] | 7 |
| ia_poly1850--36dcee7ce4c29f8b--s039-l0061 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3}] | 9 |
| ia_poly1850--5aa15e93b2f445b8--s005-l0001 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['PRAEFATΙΟ']}] | PRAEFATΙΟ |
| ia_poly1850--63f57af8d450f3e8--s009-l0033 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 8, 'minimum': 10}] | τους υπερ |
| ia_poly1850--63f57af8d450f3e8--s034-l0018 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 6, 'minimum': 10}] | λιππός |
| ia_poly1850--63f57af8d450f3e8--s034-l0019 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1850', 'letters': 5, 'minimum': 10}] | ἐστιν |
| ia_poly1850--a89bd2c9bdb1ca6d--s034-l0035 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | .......... |
| ia_poly1850--c3f3a531e277da9a--s036-l0026 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ..... |
| ia_russian--2a45a0561eb05739--s002-l0002 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 6}, 'characters': ['E', 'G', 'N', 'O', 'R']}] | OREGON |
| ia_russian--61f76a57b26f9b13--s001-l0004 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 6}, 'characters': ['D', 'L', 'N', 'O']}] | LONDON, |
| ia_russian--61f76a57b26f9b13--s001-l0005 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 23}, 'characters': ['A', 'B', 'C', 'E', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'W', 'o']}] | TRUBNER & Co. 60, PATERNOSTER ROW, |
| ia_russian--6cfc00f06e0f7241--s004-l0043 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ...... |
| kosmopolis--86098eebf5207e79--s003-l0041 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 4, 'minimum': 10}] | στὴν |
| kosmopolis--8ac130e14e062423--s001-l0026 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 4, 'minimum': 10}] | πᾶνε |
| kosmopolis--91040f2da70b9ae0--s004-l0004 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 3, 'minimum': 10}] | ᾿Απὸ |
| kosmopolis--9a17c86798d2c74a--s000-l0030 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 3, 'minimum': 10}] | , ποῦ |
| kosmopolis--9a17c86798d2c74a--s003-l0012 | short_line / DROP | [{'reason': 'short_line', 'role': 'dialogue_fiction', 'letters': 3, 'minimum': 10}] | ” καὶ |
| kosmopolis--ecc23d7812913d0a--s006-l0039 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ...» |
| lekythos--0fc3672826ddd6b3--s001-l0023 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 6, 'minimum': 10}] | βιβλία |
| lekythos--456def1ccfc2283e--s001-l0177 | numeric_shape / DROP | [{'reason': 'numeric_shape', 'alnum': 1, 'detail': '<=1 letter-or-digit'}] | -'-'-'-'-'-'-'0 |
| lekythos--49c082ba27aa27da--s000-l0046 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 4, 'minimum': 10}] | Η του |
| lekythos--a0c4e6327052acfc--s002-l0089 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.2}] | / |
| lekythos--dcfa99599048d352--s000-l0105 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 9, 'minimum': 10}] | Κάτω ΒΟΛΟΥ |
| nlg--1144074169f43992--s021-l0010 | short_line / DROP | [{'reason': 'short_line', 'role': 'poly1900', 'letters': 6, 'minimum': 10}] | τί ἄλλο |
| nlg--3d6bd7bd688acb61--s024-l0003 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 4.583333333333333}] | - |
| nlg--f4b52df5f8130047--s010-l0018 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 2.125}] | 4.- |
| serbia--27b182bf4116728f--s008-l0003 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['рѣza']}] | Г. Ана: Гуліани рѣza y Mabmk: 1817, |
| serbia--3ab59a8d4ee49339--s005-l0014 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 6}, 'characters': ['A', 'C', 'I', 'N']}] | INCAII. |
| serbia--557369d8d117b91a--s000-l0028 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 9}, 'characters': ['E', 'a', 'g', 'l', 'n', 'r', 'é']}] | En général |
| serbia--b6450341d87fb144--s007-l0002 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['БУE']}] | ВИЉЕМ БУE |
| serbia--e7935cdb3dfeaf10--s006-l0006 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 26}, 'characters': ['D', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'm', 'n', 'p', 'r', 's', 't', 'u', 'w', 'ü']}] | ,,Drum prüfe, wer sich ewig bindet". |

## changed_lines

| ID | Kind / outcome | Words / scripts / reason evidence | Raw text |
| --- | --- | --- | --- |
| bsb_poly1850--2032df1e3e983f1d--s005-l0029 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 7, 'minimum': 10}] | PAEONIA |
| elstat--0a2c92120843658d--s001-l0216 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4705882352941178}] | 1 |
| elstat--2b5780c7c9896a54--s000-l0051 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 8, 'minimum': 10}] | Sommaire |
| elstat--c4d30f00b317e558--s001-l0501 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3333333333333333}] | 1 |
| gazette_modern--00a5942b52d08f1e--s000-l0115 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0476190476190477}] | 1 |
| gazette_modern--1456dcb167f23bfe--s000-l0027 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0909090909090908}] | 1 |
| gazette_modern--2e613d9290dd13d4--s000-l0017 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4166666666666667}] | 1 |
| gazette_modern--3134c1c6f0ab2f3e--s000-l0045 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1176470588235294}] | 1. |
| gazette_modern--5158b7bf9def2bab--s000-l0012 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.875}] | - |
| gazette_modern--6bc7acccf0163698--s000-l0268 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 1 |
| gazette_modern--96035db0434dc980--s000-l0074 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1538461538461537}] | 1 |
| gazette_modern--a8e70ef11baca460--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0714285714285714}] | 1 |
| gazette_modern--aeb6eb76fc7057f0--s000-l0050 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4}] | " |
| gazette_modern--bd7c91e6a214949b--s000-l0125 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['ハンハンΟΜΙΑΣ']}, {'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'greek': 5, 'other': 4}, 'characters': ['ハ', 'ン']}] | ハンハンΟΜΙΑΣ. |
| gazette_modern--d6092126b747cac8--s000-l0014 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 1 |
| ia_greek_latin--8af66d4d113847ee--s003-l0022 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ...................... |
| ia_greek_latin--8af66d4d113847ee--s003-l0107 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ......................... |
| lekythos--456def1ccfc2283e--s001-l0177 | numeric_shape / DROP | [{'reason': 'numeric_shape', 'alnum': 1, 'detail': '<=1 letter-or-digit'}] | -'-'-'-'-'-'-'0 |
| lekythos--49c082ba27aa27da--s000-l0046 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 4, 'minimum': 10}] | Η του |
| lekythos--a0c4e6327052acfc--s002-l0089 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.2}] | / |
| serbia--b6450341d87fb144--s007-l0002 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['БУE']}] | ВИЉЕМ БУE |

## sheet

| ID | Kind / outcome | Words / scripts / reason evidence | Raw text |
| --- | --- | --- | --- |
| serbia--557369d8d117b91a--s000-l0028 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 9}, 'characters': ['E', 'a', 'g', 'l', 'n', 'r', 'é']}] | En général |
| gazette_modern--0a788b86a71c8e98--s000-l0142 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.5238095238095237}] | 4. |
| gazette_modern--2ce16341b1b7b83f--s000-l0073 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3888888888888888}] | 2 |
| elstat--3b2d88122b3f037c--s000-l0185 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2}] | 7 |
| gazette_modern--13a9303cfc83a9d4--s000-l0045 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0625}] | 3 |
| gazette_modern--70ef76cb8b8c1897--s000-l0075 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.46875}] | (5) |
| gazette_modern--b590ece7e2d52a5c--s000-l0050 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2307692307692308}] | 1 |
| ia_poly1850--36dcee7ce4c29f8b--s005-l0102 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4166666666666667}] | 7 |
| nlg--3d6bd7bd688acb61--s024-l0003 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 4.583333333333333}] | - |
| gazette_modern--2c53a696417985d2--s000-l0032 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4705882352941178}] | : |
| gazette_modern--52ee6226bb7d4834--s000-l0091 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4705882352941178}] | * |
| gazette_modern--559faec5ce2b9384--s000-l0185 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2857142857142858}] | E |
| gazette_modern--5c36407f5c0b0aa3--s000-l0117 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 2.7142857142857144}] | ...... |
| gazette_modern--67dfc161a690ff25--s000-l0029 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 1}, 'characters': ['日']}] | 日 |
| gazette_modern--6d0a93d9389e859c--s000-l0013 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ------ |
| gazette_modern--af3a940b646b3a7d--s000-l0242 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 5.75}] | ----- |
| gazette_modern--b0dc765920f41797--s000-l0119 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 1}, 'characters': ['द']}] | द |
| gazette_modern--b9f59878fb904d91--s000-l0156 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ===== |
| gazette_modern--c9931c881b131806--s000-l0111 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4230769230769231}] | E |
| gazette_modern--e1ffcad236d8706c--s000-l0150 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ------- |
| ia_greek_latin--e02bf39b0ef9974e--s008-l0006 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 4.25}] | } |
| ia_poly1850--36dcee7ce4c29f8b--s010-l0073 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 2.606060606060606}] | ἱ |
| nlg--1144074169f43992--s017-l0006 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 8, 'minimum': 10}] | OF GREECE |
| nlg--3d6bd7bd688acb61--s029-l0031 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 2}, 'characters': ['ہ', 'ی']}] | یہ |
| gazette_modern--0089276875b132d9--s000-l0025 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2982456140350878}] | (5) |
| gazette_modern--363c5539ff24957e--s000-l0104 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ................................ |
| elstat--5f85f8679b2fe3c7--s001-l0211 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.2}] | )) |
| elstat--996d9f614c928993--s000-l0085 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 3}, 'characters': ['ق', 'م', 'و']}] | قوم |
| gazette_modern--210c5618de6d9b6d--s000-l0039 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1111111111111112}] | Β΄ |
| gazette_modern--308a48b3394afaa0--s000-l0024 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 2.0}] | A |
| gazette_modern--3dc14e0d9926346a--s000-l0020 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 2.727272727272727}] | == |
| gazette_modern--7a8694d1e521f23e--s000-l0094 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.0909090909090908}] | , |
| gazette_modern--7a8694d1e521f23e--s000-l0144 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.3}] | , |
| gazette_modern--7b6b2ad720aaf57d--s000-l0047 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 2.6923076923076925}] | == |
| gazette_modern--92fb735e336d11f5--s000-l0002 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4339622641509433}] | + |
| gazette_modern--af7b153702818d6f--s000-l0015 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0952380952380953}] | 1 |
| gazette_modern--b21451311e269f58--s000-l0001 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 2}, 'characters': ['س', 'ے']}] | سے |
| gazette_modern--d2281f8022512d7b--s000-l0232 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4}] | m |
| gazette_modern--d750387e4a01e942--s000-l0040 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.1875}] | )) |
| gazette_modern--e63ba848f5efa001--s000-l0042 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.5833333333333333}] | " |
| gazette_modern--e840cbc49c44b1cd--s000-l0096 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 3.25}] | - |
| gazette_modern--f0839209fcdaf7aa--s000-l0036 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.0}] | " |
| gazette_modern--f70f27234322ca16--s000-l0399 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4}] | " |
| ia_greek_latin--e02bf39b0ef9974e--s004-l0114 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.53125}] | Ο |
| ia_poly1850--21c15fc15dc17003--s009-l0065 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.3181818181818181}] | " |
| ia_poly1850--26e14cb9c90b750f--s003-l0102 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 1}, 'characters': ['滑']}] | 滑 |
| ia_poly1850--26e14cb9c90b750f--s005-l0061 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1025641025641026}] | I |
| ia_poly1850--34543d92a48213e7--s024-l0007 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 3.5}] | - |
| ia_poly1850--6a9e5e4676cec552--s019-l0043 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 4.454545454545454}] | - |
| ia_poly1850--c3f3a531e277da9a--s038-l0006 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 1}, 'characters': ['カ']}] | カ |
| ia_poly1850--ca4f3983c96b6334--s002-l0002 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 5.454545454545454}] | - |
| ia_poly1850--ca4f3983c96b6334--s022-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 4.454545454545454}] | - |
| ia_russian--03b43bc5289ad8ce--s001-l0026 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 5.857142857142857}] | - |
| ia_russian--06528548147a3a3d--s005-l0029 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'other': 1}, 'characters': ['و']}] | و |
| ia_russian--06528548147a3a3d--s007-l0002 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 4.875}] | - |
| ia_russian--d558bd3e803e7865--s007-l0031 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 5.0}] | - |
| nlg--6ae0ac01064a587e--s011-l0007 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 5.636363636363637}] | - |
| serbia--42fedee06e6cb85a--s005-l0004 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.3125}] | * |
| serbia--b6450341d87fb144--s000-l0005 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 2}, 'characters': ['M', 'i']}] | Mi |
| elstat--0a2c92120843658d--s001-l0216 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4705882352941178}] | 1 |
| gazette_modern--00a5942b52d08f1e--s000-l0115 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0476190476190477}] | 1 |
| gazette_modern--1456dcb167f23bfe--s000-l0027 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0909090909090908}] | 1 |
| gazette_modern--3134c1c6f0ab2f3e--s000-l0045 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1176470588235294}] | 1. |
| gazette_modern--96035db0434dc980--s000-l0074 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1538461538461537}] | 1 |
| gazette_modern--a8e70ef11baca460--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0714285714285714}] | 1 |
| gazette_modern--d6092126b747cac8--s000-l0014 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 1 |
| lekythos--a0c4e6327052acfc--s002-l0089 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.2}] | / |
| bsb_poly1850--2032df1e3e983f1d--s005-l0029 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 7, 'minimum': 10}] | PAEONIA |
| elstat--2b5780c7c9896a54--s000-l0051 | short_line / DROP | [{'reason': 'short_line', 'role': 'latin', 'letters': 8, 'minimum': 10}] | Sommaire |
| elstat--c4d30f00b317e558--s001-l0501 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3333333333333333}] | 1 |
| gazette_modern--2e613d9290dd13d4--s000-l0017 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4166666666666667}] | 1 |
| gazette_modern--6bc7acccf0163698--s000-l0268 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 1 |
| ia_greek_latin--8af66d4d113847ee--s003-l0022 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ...................... |
| ia_greek_latin--8af66d4d113847ee--s003-l0107 | short_line / DROP | [{'reason': 'short_line', 'role': 'nonletter', 'letters': 0, 'minimum': 10}] | ......................... |
| serbia--b6450341d87fb144--s007-l0002 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['БУE']}] | ВИЉЕМ БУE |
| gazette_modern--5158b7bf9def2bab--s000-l0012 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.875}] | - |
| gazette_modern--aeb6eb76fc7057f0--s000-l0050 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4}] | " |
| gazette_modern--bd7c91e6a214949b--s000-l0125 | mixed / DROP | [{'reason': 'mixed_script_word', 'words': ['ハンハンΟΜΙΑΣ']}, {'reason': 'unexpected_script', 'scripts': ['other'], 'script_counts': {'greek': 5, 'other': 4}, 'characters': ['ハ', 'ン']}] | ハンハンΟΜΙΑΣ. |
| lekythos--456def1ccfc2283e--s001-l0177 | numeric_shape / DROP | [{'reason': 'numeric_shape', 'alnum': 1, 'detail': '<=1 letter-or-digit'}] | -'-'-'-'-'-'-'0 |
| lekythos--49c082ba27aa27da--s000-l0046 | short_line / DROP | [{'reason': 'short_line', 'role': 'greek_mono', 'letters': 4, 'minimum': 10}] | Η του |

## numeric_fit

| ID | Kind / outcome | Words / scripts / reason evidence | Raw text |
| --- | --- | --- | --- |
| gazette_modern--13a9303cfc83a9d4--s000-l0045 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0625}] | 3 |
| gazette_modern--1456dcb167f23bfe--s000-l0027 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0909090909090908}] | 1 |
| gazette_modern--6d58ca2e2dc41e69--s000-l0067 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1666666666666667}] | 4. |
| ia_greek_latin--ef6c2c5c1ba30b47--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.048780487804878}] | 8 |
| gazette_modern--8757f64ef1908c90--s000-l0003 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4482758620689655}] | (3) |
| nlg--f4b52df5f8130047--s010-l0018 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 2.125}] | 4.- |
| gazette_modern--96035db0434dc980--s000-l0074 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1538461538461537}] | 1 |
| gazette_modern--2e613d9290dd13d4--s000-l0017 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4166666666666667}] | 1 |
| gazette_modern--3134c1c6f0ab2f3e--s000-l0045 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1176470588235294}] | 1. |
| gazette_modern--20d238884fd69747--s000-l0032 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2857142857142858}] | 9 |
| ia_poly1850--36dcee7ce4c29f8b--s039-l0061 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3}] | 9 |
| gazette_modern--2ce16341b1b7b83f--s000-l0073 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3888888888888888}] | 2 |
| gazette_modern--1450bd01ddded5ef--s000-l0062 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.6428571428571428}] | (7) |
| ia_poly1850--36dcee7ce4c29f8b--s005-l0102 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4166666666666667}] | 7 |
| elstat--3b2d88122b3f037c--s000-l0756 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2666666666666666}] | 6 |
| elstat--88112979c8a843cb--s001-l0189 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 7 |
| gazette_modern--af7b153702818d6f--s000-l0015 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0952380952380953}] | 1 |
| elstat--c4d30f00b317e558--s001-l0669 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2}] | 5 |
| gazette_modern--bf3c8b13adae55fa--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3}] | 2 |
| gazette_modern--21ec5b038b7e1422--s000-l0071 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1578947368421053}] | 0 |
| gazette_modern--1955eae0881d5641--s000-l0023 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2857142857142858}] | 3 |
| gazette_modern--126dfaa21bc0e1d5--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1904761904761905}] | 4 |
| gazette_modern--0a788b86a71c8e98--s000-l0142 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.5238095238095237}] | 4. |
| gazette_modern--d6092126b747cac8--s000-l0014 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 1 |
| gazette_modern--5ca206a0dc95767d--s000-l0053 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2380952380952381}] | 9 |
| gazette_modern--6bc7acccf0163698--s000-l0268 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 1 |
| gazette_modern--b590ece7e2d52a5c--s000-l0050 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2307692307692308}] | 1 |
| elstat--3b2d88122b3f037c--s000-l0185 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2}] | 7 |
| elstat--c4d30f00b317e558--s001-l0501 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3333333333333333}] | 1 |
| elstat--3b2d88122b3f037c--s001-l0319 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3}] | 9 |
| elstat--3b2d88122b3f037c--s000-l0454 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.125}] | 5 |
| gazette_modern--f63147c9df54d9d4--s000-l0034 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.263157894736842}] | 8 |
| elstat--0a2c92120843658d--s001-l0216 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4705882352941178}] | 1 |
| gazette_modern--929e10adc3109aab--s000-l0027 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.12}] | 2 |
| elstat--d8fe6ab28d6113ba--s001-l0333 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.9166666666666667}] | 2. |
| gazette_modern--70ef76cb8b8c1897--s000-l0075 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.46875}] | (5) |
| gazette_modern--a8e70ef11baca460--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0714285714285714}] | 1 |
| gazette_modern--00a5942b52d08f1e--s000-l0115 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0476190476190477}] | 1 |
| ia_poly1850--26e14cb9c90b750f--s005-l0061 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1025641025641026}] | I |
| gazette_modern--bf43bbfea6d6754d--s000-l0195 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3863636363636365}] | (१) |
| gazette_modern--0089276875b132d9--s000-l0025 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2982456140350878}] | (5) |
| elstat--5f85f8679b2fe3c7--s000-l0045 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2941176470588236}] | 2 |
| elstat--5f85f8679b2fe3c7--s000-l0073 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.263157894736842}] | 3 |
| gazette_modern--062232e99d367ea4--s000-l0019 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.7333333333333334}] | (3) |
| gazette_modern--0f5a30370d9ee296--s000-l0037 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.25}] | 4 |
| gazette_modern--1bf5621384b3760f--s000-l0021 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3846153846153846}] | 2 |
| gazette_modern--2338343111e8514a--s000-l0359 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0454545454545454}] | 7 |
| gazette_modern--2e613d9290dd13d4--s000-l0205 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1538461538461537}] | 1 |
| gazette_modern--2e613d9290dd13d4--s000-l0321 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3333333333333333}] | 3 |
| gazette_modern--306f3db36191aba6--s000-l0033 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0384615384615385}] | 2 |
| gazette_modern--4a4d476b4404c27f--s000-l0022 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1428571428571428}] | 2 |
| gazette_modern--5bca118bfbabb811--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3}] | 8 |
| gazette_modern--6830681df744880b--s000-l0002 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0952380952380953}] | 7 |
| gazette_modern--6874fdf3e55abd26--s000-l0026 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3666666666666667}] | (8) |
| gazette_modern--6874fdf3e55abd26--s000-l0116 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.5357142857142858}] | (9) |
| gazette_modern--a45fae38ac958b40--s000-l0019 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.736842105263158}] | C |
| gazette_modern--a6c088328b5ced3c--s000-l0041 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.6774193548387097}] | (8) |
| gazette_modern--bd4c89f73f9ccfce--s000-l0003 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4827586206896552}] | (2) |
| gazette_modern--d469b2b3acfb2d34--s000-l0026 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0476190476190477}] | 5 |
| gazette_modern--e63ba848f5efa001--s000-l0013 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2727272727272727}] | 3 |
| gazette_modern--f4a16fe9302ade1e--s000-l0287 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0714285714285714}] | L |
| ia_poly1850--1686874575c895ca--s004-l0030 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.15625}] | 4 |
| ia_poly1850--f806d3f10b2ecf9c--s000-l0120 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1875}] | 2 |
| ia_russian--6cfc00f06e0f7241--s006-l0119 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2}] | 8 |

## two_by_two

| ID | Kind / outcome | Words / scripts / reason evidence | Raw text |
| --- | --- | --- | --- |
| lekythos--a0c4e6327052acfc--s002-l0089 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.2}] | / |
| gazette_modern--13a9303cfc83a9d4--s000-l0045 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0625}] | 3 |
| gazette_modern--1456dcb167f23bfe--s000-l0027 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0909090909090908}] | 1 |
| gazette_modern--5158b7bf9def2bab--s000-l0012 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.875}] | - |
| gazette_modern--aeb6eb76fc7057f0--s000-l0050 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.4}] | " |
| nlg--3d6bd7bd688acb61--s024-l0003 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 4.583333333333333}] | - |
| ia_greek_latin--a232aaf9a41fe898--s001-l0012 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 0, 'A': 1.0281030444964872}] | ***** |
| ia_russian--61f76a57b26f9b13--s001-l0004 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 6}, 'characters': ['D', 'L', 'N', 'O']}] | LONDON, |
| nlg--f4b52df5f8130047--s010-l0018 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 2.125}] | 4.- |
| gazette_modern--96035db0434dc980--s000-l0074 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1538461538461537}] | 1 |
| gazette_modern--2e613d9290dd13d4--s000-l0017 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4166666666666667}] | 1 |
| gazette_modern--3134c1c6f0ab2f3e--s000-l0045 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1176470588235294}] | 1. |
| gazette_modern--20d238884fd69747--s000-l0032 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2857142857142858}] | 9 |
| ia_poly1850--36dcee7ce4c29f8b--s039-l0061 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3}] | 9 |
| gazette_modern--2ce16341b1b7b83f--s000-l0073 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3888888888888888}] | 2 |
| gazette_modern--1450bd01ddded5ef--s000-l0062 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.6428571428571428}] | (7) |
| ia_poly1850--36dcee7ce4c29f8b--s005-l0102 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4166666666666667}] | 7 |
| elstat--3b2d88122b3f037c--s000-l0756 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2666666666666666}] | 6 |
| elstat--88112979c8a843cb--s001-l0189 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 7 |
| elstat--c4d30f00b317e558--s001-l0669 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2}] | 5 |
| gazette_modern--bf3c8b13adae55fa--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3}] | 2 |
| gazette_modern--21ec5b038b7e1422--s000-l0071 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1578947368421053}] | 0 |
| gazette_modern--1955eae0881d5641--s000-l0023 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2857142857142858}] | 3 |
| gazette_modern--126dfaa21bc0e1d5--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.1904761904761905}] | 4 |
| gazette_modern--0a788b86a71c8e98--s000-l0142 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.5238095238095237}] | 4. |
| gazette_modern--d6092126b747cac8--s000-l0014 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 1 |
| gazette_modern--5ca206a0dc95767d--s000-l0053 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2380952380952381}] | 9 |
| gazette_modern--6bc7acccf0163698--s000-l0268 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0}] | 1 |
| gazette_modern--b590ece7e2d52a5c--s000-l0050 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2307692307692308}] | 1 |
| elstat--3b2d88122b3f037c--s000-l0185 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.2}] | 7 |
| elstat--c4d30f00b317e558--s001-l0501 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3333333333333333}] | 1 |
| elstat--3b2d88122b3f037c--s001-l0319 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.3}] | 9 |
| elstat--3b2d88122b3f037c--s000-l0454 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.125}] | 5 |
| gazette_modern--f63147c9df54d9d4--s000-l0034 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.263157894736842}] | 8 |
| elstat--0a2c92120843658d--s001-l0216 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.4705882352941178}] | 1 |
| gazette_modern--929e10adc3109aab--s000-l0027 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.12}] | 2 |
| elstat--d8fe6ab28d6113ba--s001-l0333 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.9166666666666667}] | 2. |
| gazette_modern--70ef76cb8b8c1897--s000-l0075 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.46875}] | (5) |
| gazette_modern--a8e70ef11baca460--s000-l0001 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0714285714285714}] | 1 |
| gazette_modern--00a5942b52d08f1e--s000-l0115 | single_character_cell / DROP | [{'reason': 'single_character_cell', 'alnum': 1, 'A': 1.0476190476190477}] | 1 |
| ia_russian--2a45a0561eb05739--s002-l0002 | foreign / HOLD | [{'reason': 'unexpected_script', 'scripts': ['latin'], 'script_counts': {'latin': 6}, 'characters': ['E', 'G', 'N', 'O', 'R']}] | OREGON |
