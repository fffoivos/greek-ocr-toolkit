# T4b — assembly repair and admission-only merged-crop screen

## 1. Duplicate-interleave repair

Reassembled **all 52,658 lines** from the saved Google responses. **427 labels changed (0.811%) on 87 pages**. No provider calls, network access, or spend. The shipped code and all input tracks remain unchanged. The new opt-in function is [assembly_fix.py](assembly_fix.py); the offline pipeline is [screen.py](screen.py).

The root-cause trace corrects the working hypothesis: P1 does not interleave two separately returned lines itself. `montage.response_lines()` slices each Google line text anchor, and P1 `process_reads.one()` passes it through normalization. The **saved Google line anchor already contains the overlapping alternative readings**. The missing assembly safeguard is box suppression. On OpenArchives c014, Google line index 211, anchor [8189,8250), already reads the entire bad label. The page record confirms `text_object_count=0` and `scanned_image_no_text_operators`; hidden PDF text is not the source.

**Final rule:** native token AABB IoU > **0.10**, vertical intersection ≥80% of the shorter token height, vertical-center separation ≤45% of that height, and horizontal intersection ≥60% of the shorter width. A geometric overlap component must contain a base-text substring pair or SequenceMatcher ratio ≥0.40. Within that component, choose the nonconflicting token set maximizing Σ(base letters/digits × saved token confidence). This allows two genuine short words to defeat one combined hallucination. Punctuation competes only with identical punctuation and ties prefer the earliest anchor. No word is removed merely because its spelling repeats.

The low IoU is needed for a one-character suffix inside a much longer full token; 0.20 misses ELSTAT `σεις` and short OA tails. The vertical and text-compatibility guards protect stacked marginal notes and ordinary punctuation. The horizontal guard preserves adjacent numeric date fields: an earlier prototype changed `1/1-30/6` to `/1-30/6`; the final function leaves it intact. Actual negative witnesses include IA poly1850 c032 (two stacked marginal readings) and BSB c020 / Pleias c021 (two printed rows). They remain intact. Prototype rules that removed punctuation or stacked-row words were rejected.

**Twenty actual interleave witnesses: 16/20 now have correct base letters relative to the supplied printed readings.** The duplicate defect and whole-card correctness are separate: ELSTAT retains its Y/Υ and digit errors; Pleias retains Κα!/Καὶ and Latin O/Greek Ὁ errors. The requested source count 7+4+3+3+3 is not supported by the files: only ELSTAT c026/c030 show duplicate interleave; c001/c009 are other OCR errors. Therefore the core twenty are OA 7, ELSTAT 2, Gazette 4, Pleias 3, Anemi 4. Both ELSTAT controls and every additional changed card are also traced below and in the receipt.

The table reports **base-letter agreement**, not a fresh blind verdict. Literal agreement is shown separately; `unverified` means the old `marks=na` or partial detail cannot certify every mark. Blind `letters`, `marks`, errors and detail remain unchanged in [card_eval.jsonl](card_eval.jsonl); `letters_fixed` is the explicitly documented analyst comparison. [Full token IDs, native boxes, anchors, confidence, retained/dropped IDs and raw-response hashes for every witness](receipts/interleave_witnesses.jsonl).

| Source/card | Old label → fixed label | Base letters now match? | Literal/marks | Dropped token IDs → retained IDs |
|---|---|---|---|---|
| openarchives/c014 | τῶφλι τῆς τῆς μυ μυστικῆς κυστικῆς ἀνεμόσκαλας τοῦ οῦ Ἰακώβ. → **τῶφλι τῆς μυστικῆς ἀνεμόσκαλας τοῦ Ἰακώβ.** | yes | True | 1644→1643 (IoU 0.778); 1645→1646 (IoU 0.254); 1647→1646 (IoU 0.816); 1650→1649 (IoU 0.562) |
| openarchives/c015 | νέαν Ἑλληνική Δημοτική γλῶσσα, καὶ Δημοτικὴ γλῶσσα, καὶ δέχτηκε → **νέαν Ἑλληνική Δημοτική γλῶσσα, καὶ δέχτηκε** | yes | False | 460→464 (IoU 0.750); 461→457 (IoU 0.762); 462→458 (IoU 0.778); 463→459 (IoU 0.433) |
| openarchives/c025 | νόμενος νος τὸν τὸν ἀστυνομικόν, ζητεῖ εῖ νὰ νὰ κάμῃ μίαν → **νόμενος τὸν ἀστυνομικόν, ζητεῖ νὰ κάμῃ μίαν** | yes | unverified | 1369→1368 (IoU 0.314); 1370→1371 (IoU 0.733); 1375→1374 (IoU 0.206); 1377→1376 (IoU 0.717) |
| openarchives/c026 | τηκεν. οὔτε γὰρ ἔχει χώραν ὁ ἐν λίτεμ ὅρκ ὁἰν όρκος, τοῦ οῦ οἰκέτου \|que enim iusiurandum in litem locum habet, si servus → **τηκεν. οὔτε γὰρ ἔχει χώραν ὁ ἐν λίτεμ όρκος, τοῦ οἰκέτου \|que enim iusiurandum in litem locum habet, si servus** | yes | False | 500→502 (IoU 0.484); 501→497,498 (IoU 0.345); 505→504 (IoU 0.476) |
| openarchives/c028 | Ὅπωςδήποτε, ἡ κριτικὴ δὲν δὲν πρέπει πρέπει νὰ νὰ στρέ- σ΄ → **Ὅπωςδήποτε, ἡ κριτικὴ δὲν πρέπει νὰ στρέ-** | yes | unverified | 1964→1963 (IoU 0.905); 1966→1965 (IoU 0.900); 1968→1967 (IoU 0.911); 1970→1969 (IoU 0.289) |
| openarchives/c036 | εἶναι ἡ γνώ ἡ γνώμη καὶ τοῦ Γερμανοῦ του Γερμανού λογίου → **εἶναι ἡ γνώμη καὶ τοῦ Γερμανοῦ λογίου** | yes | unverified | 1228→1230 (IoU 0.676); 1229→1231 (IoU 0.512); 1235→1233 (IoU 0.748); 1236→1234 (IoU 0.766) |
| openarchives/c040 | καία γιὰ ἕν ἕνα ποίημα σὰν σὰν αὐτὸ τοῦ Barbusse, → **καία γιὰ ἕνα ποίημα σὰν αὐτὸ τοῦ Barbusse,** | yes | unverified | 1719→1720 (IoU 0.408); 1722→1723 (IoU 0.806) |
| elstat/c026 | 1) Μετὰ χρυσοῦ. - Υ compris lingots. - 2) Δεδηλωμέναι ἀξίαι. - Valeurs déclarées. 3) Ἐκτὸς τῶν δι' ἐπανορθώσεις σεις ἐξαγομένων. - Non compris livraisons pour ré- → **1) Μετὰ χρυσοῦ. - Υ compris lingots. - 2) Δεδηλωμέναι ἀξίαι. - Valeurs déclarées. 3) Ἐκτὸς τῶν δι' ἐπανορθώσεις ἐξαγομένων. - Non compris livraisons pour ré-** | no | False | 1254→1253 (IoU 0.193) |
| elstat/c030 | parations. - *) Μετὰ τῶν ταχυδρομικῶν δεμάτων τῆς ἑξαμηνίας. - Y compris compris les colis postaux pour le semestre. 5) Μετὰ τῆς ἐλευθέρας πόλεως τοῦ Δάντζικ. - Pologne → **parations. - *) Μετὰ τῶν ταχυδρομικῶν δεμάτων τῆς ἑξαμηνίας. - Y compris les colis postaux pour le semestre. 5) Μετὰ τῆς ἐλευθέρας πόλεως τοῦ Δάντζικ. - Pologne** | no | False | 1277→1278 (IoU 0.925) |
| government-gazette/c014 | διὰ τῆς νομιμοποιήσεως ὑπαρχούσης ῆς νομιμοποιή αρχούσης ἀνωνύμου ὁδοῦ ἔμπροσθεν → **διὰ τῆς νομιμοποιήσεως ὑπαρχούσης ἀνωνύμου ὁδοῦ ἔμπροσθεν** | yes | unverified | 154→151 (IoU 0.400); 155→152 (IoU 0.517); 156→153 (IoU 0.613) |
| government-gazette/c026 | κρατορίας, τὰ προ τὰ προσωρινῶς ἔχοντα νόμιμον κυκλοφορίαν ἐν ταῖς → **κρατορίας, τὰ προσωρινῶς ἔχοντα νόμιμον κυκλοφορίαν ἐν ταῖς** | yes | unverified | 411→413 (IoU 0.755); 412→414 (IoU 0.221) |
| government-gazette/c030 | πάγον πάγον εἰς εἰς τὰς πόλεις τοῦ Βόλου καὶ Νέας Ιωνίας καὶ τὰς → **πάγον εἰς τὰς πόλεις τοῦ Βόλου καὶ Νέας Ιωνίας καὶ τὰς** | yes | False | 1054→1055 (IoU 0.788); 1057→1056 (IoU 0.681) |
| government-gazette/c035 | REGISTER OF SHIPPING, BUREAU VERITAS' VERITAS' → **REGISTER OF SHIPPING, BUREAU VERITAS'** | yes | unverified | 834→832 (IoU 0.675); 835→833 (IoU 0.236) |
| pleias/c014 | μεγαλειτέρας εἰ εἰς τὴν χώραν. Κα! αἱ ἀληθὲς μὲν ἐν εἶναι εἶναι ὅτι ὅτι τινὰς το → **μεγαλειτέρας εἰς τὴν χώραν. Κα! ἀληθὲς μὲν εἶναι ὅτι τινὰς το** | no | False | 150→151 (IoU 0.493); 157→155 (IoU 0.256); 160→159 (IoU 0.382); 161→162 (IoU 0.720); 164→163 (IoU 0.714) |
| pleias/c019 | νον. Ὁ ὑπηρέ ὑπηρέτης ἐκεῖνος ἐξηφανίσθη καὶ δὲν ἀνεφάνη → **νον. Ὁ ὑπηρέτης ἐκεῖνος ἐξηφανίσθη καὶ δὲν ἀνεφάνη** | yes | unverified | 382→383 (IoU 0.426) |
| pleias/c040 | ἑλληνικοῦ θεάτρου τοῦ διασήμου Paul de Saint-Vi Saint-Victor, O → **ἑλληνικοῦ θεάτρου τοῦ διασήμου Paul de Saint-Victor, O** | no | False | 934→937 (IoU 0.313); 935→932 (IoU 0.731); 936→933 (IoU 0.724) |
| anemi/c005 | εἰς μάτην. ᾿Αλλ᾿ ἡ μεγίστη τρικυμία κατέλαβε τέλαβε τὸν τὸν παναγιώτατον πατέρα → **εἰς μάτην. ᾿Αλλ᾿ ἡ μεγίστη τρικυμία κατέλαβε τὸν παναγιώτατον πατέρα** | yes | unverified | 333→332 (IoU 0.506); 334→335 (IoU 0.750) |
| anemi/c025 | Κιλία εἰρήνῃ, καθ νῃ, καθ᾿ ἣν ἡ Νορβεγία παρεχωρήθη εἰς τὴν Σουηδίαν (μ. Χ. → **Κιλία εἰρήνῃ, καθ᾿ ἣν ἡ Νορβεγία παρεχωρήθη εἰς τὴν Σουηδίαν (μ. Χ.** | yes | False | 129→132 (IoU 0.668); 130→127 (IoU 0.252); 131→128 (IoU 0.589) |
| anemi/c032 | φυλαί. Καὶ οἱ μὲν Τεύτονες, θέλοντες νὰ διαφύγωσι τοὺς ῾Ῥα Ῥωμαίους, ους, έξω- → **φυλαί. Καὶ οἱ μὲν Τεύτονες, θέλοντες νὰ διαφύγωσι τοὺς Ῥωμαίους, έξω-** | yes | False | 292→293 (IoU 0.221); 295→293 (IoU 0.255); 296→294 (IoU 0.485) |
| anemi/c033 | καὶ συνηγωνίσθη εἰς τὰς μάχας τὰς ἐν Γροσσοβηρία, Δεννεβίκῳ Δεννεβίκῳ καὶ Λειψία → **καὶ συνηγωνίσθη εἰς τὰς μάχας τὰς ἐν Γροσσοβηρία, Δεννεβίκῳ καὶ Λειψία** | yes | False | 93→94 (IoU 0.928) |

All additional changed cards and non-interleave controls:

| Source/card | Old → fixed | Base letters now | Reason from original blind detail |
|---|---|---|---|
| gr/elstat/c001 | Οκτωβρίου του 1940 δεν περιλαμβάνονται τὸ στρατιωτικά εἰσιτήρια. – A partir du mois d'octobre de 1onnée 1940 les billete militaires ne sont pas compris. –7) Λόγω → Οκτωβρίου του 1940 δεν περιλαμβάνονται τὸ στρατιωτικά εἰσιτήρια. – A partir du mois d'octobre de 1onnée 1940 les billete militaires ne sont pas compris. –7) Λόγω | n | ⁶Ὀκτωβρίου → Οκτωβρίου (footnote mark/breathing dropped); τοῦ → του; δὲν → δεν; στρατιωτικὰ → στρατιωτικά; l'année → 1onnée; billets → billete; Λόγῳ → Λόγω (iota subscript); crop includes parts of lines above and below |
| gr/elstat/c009 | 3070 1893 Σιδηροδρόμου Θεσσαλονίκης - Κων/πόλεως . → 3070 1893 Σιδηροδρόμου Θεσσαλονίκης - Κων/πόλεως . | n | 3 ⁰/₀ → 3070; crop includes parts of lines above and below |
| gr/government-gazette/c016 | βιβλίων ων καὶ λογαριασμῶν τῆς ἑταιρίας· γ') ἐγκρίνει ἢ μεταρρυθμίζει τὸν καταρτισθέντα ὑπὸ τοῦ Διοικητικοῦ Συμ- → βιβλίων καὶ λογαριασμῶν τῆς ἑταιρίας· γ') ἐγκρίνει ἢ μεταρρυθμίζει τὸν καταρτισθέντα ὑπὸ τοῦ Διοικητικοῦ Συμ- | n | (none) → duplicated 'ων' after βιβλίων; line ends at 'ἐγκρίνει ἢ' → appended next line 'μεταρρυθμίζει τὸν καταρτισθέντα ὑπὸ τοῦ Διοικητικοῦ Συμ-' |
| gr/government-gazette/c025 | ὡς καὶ οἱ ἰδιῶται οἱ ἔχοντες ἀποθηκευμένα να κα καπνοβιομηχανικά → ὡς καὶ οἱ ἰδιῶται οἱ ἔχοντες ἀποθηκευμένα κα καπνοβιομηχανικά | n | (none) → 'να κα' inserted before καπνοβιομηχανικὰ |
| gr/government-gazette/c038 | ψηφίας τῶν παρόντων μελῶν. “Αν ἐπὶ ἐκλογῆς τινος κατὰ τὴν ψηφοφορίας, ς, διὰ ψηφοδελτίων καὶ δι᾽ ἀπολύτου πλειονο → ψηφίας τῶν παρόντων μελῶν. “Αν ἐπὶ ἐκλογῆς τινος κατὰ τὴν ψηφοφορίας, ς διὰ ψηφοδελτίων καὶ δι᾽ ἀπολύτου πλειονο | n | two lines read in reverse order; (none) → stray 'ς,' added; Ἂν → “Αν |
| gr/lekythos/c023 | Donacz, ὁ νεαρὸς καὶ καὶ ἤδη διάσημος ἐθνι- → Donacz, ὁ νεαρὸς καὶ ἤδη διάσημος ἐθνι- | y | καὶ ἤδη → καὶ καὶ ἤδη (duplicated word) |
| gr/nlg-digital/c027 | ρεν οἰκόσημον εἰς τὴν σφραγίδα του.῎Αλλοι του. Α ἀνεδεικνύοντο Εὐπατρίδαι, καὶ Ἄρχοντες λαμβάνοντες → ρεν οἰκόσημον εἰς τὴν σφραγίδα του.῎Αλλοι . Α ἀνεδεικνύοντο Εὐπατρίδαι, καὶ Ἄρχοντες λαμβάνοντες | n | (none) → 'του. Α' inserted after 'του.῎Αλλοι'; crop includes parts of lines above and below |
| gr/openarchives/c008 | ἐν παντὶ καιρῷ τῆς ζωῆς αὐτοῦ, ῦ, τοῦ τοῦτο δὲ καὶ καὶ ὅτε ὅι τελευτᾷ, → ἐν παντὶ καιρῷ τῆς ζωῆς αὐτοῦ, τοῦτο δὲ καὶ ὅτε τελευτᾷ, | y | ∅ → ῦ, τοῦ; ∅ → καὶ (dup); ∅ → ὅι |
| gr/openarchives/c024 | κανεὶς κανεὶς ὅτι εὑρίσκε εὑρίσκεται ἐν ἐργαστηρίῳ μεγάλου → κανεὶς ὅτι εὑρίσκεται ἐν ἐργαστηρίῳ μεγάλου | y | ∅ → κανεὶς (dup); ∅ → εὑρίσκε |
| gr/openarchives/c027 | τικῶν ἀσκήσεων στὸ μάθημα θημα τῆς γυμναστικῆς, καθὼς καὶ τὴν → τικῶν ἀσκήσεων στὸ μάθημα τῆς γυμναστικῆς, καθὼς καὶ τὴν | n | ∅ → θημα (dup); ∅ → καθὼς καὶ τὴν (next line) |
| gr/openarchives/c039 | ἔλλειψη τῶν τῶν ἀναγκαίων χρημάτων. Τ χρημάτων. Τὴ στιγμὴ → ἔλλειψη τῶν ἀναγκαίων χρημάτων. Τὴ στιγμὴ | y | ∅ → τῶν (dup); ∅ → Τ χρημάτων. (dup) |
| gr/pleias/c004 | οἵτινες εἶχον ἄμεσον συμφέρον νὰ διακαί- \| \| → οἵτινες εἶχον ἄμεσον συμφέρον νὰ διακαί- \| | y | (column rule) → \| \| |
| gr/pleias/c039 | μῶς ηὐχαρίστει τει τοὺς ἀνοσίους ἐκείνους, → μῶς ηὐχαρίστει τοὺς ἀνοσίους ἐκείνους, | y | ηὐχαρίστει → ηὐχαρίστει τει |
| intl/bsb/c008 | sich besänftigen, durch di durch die Passiva, s. beruhigen. → sich besänftigen, durch die Passiva, s. beruhigen. | y | durch die → durch di durch die (neighbouring-line fragment) |
| intl/bsb/c017 | v. 640. Xenoph. de rep. Athen. en. III III, 15. ubi ἄτιμος dicitur, → v. 640. Xenoph. de rep. Athen. III , 15. ubi ἄτιμος dicitur, | y | Athen. III → Athen. en. III III (spurious duplicated text) |

Changes across every input line (denominator includes originally unusable lines):

| Track/source | Changed / all lines | Changed % |
|---|---:|---:|
| gr/anemi | 18/945 | 1.905% |
| gr/elstat | 76/9705 | 0.783% |
| gr/government-gazette | 101/3811 | 2.650% |
| gr/kosmopolis | 2/1331 | 0.150% |
| gr/lekythos | 9/6449 | 0.140% |
| gr/nlg-digital | 2/1246 | 0.161% |
| gr/openarchives | 142/3358 | 4.229% |
| gr/pergamos | 0/1615 | 0.000% |
| gr/pleias | 24/3388 | 0.708% |
| ia/cyrillic | 0/1818 | 0.000% |
| ia/greek_latin | 9/3109 | 0.289% |
| ia/poly1850 | 1/1303 | 0.077% |
| ia/poly1900 | 9/1441 | 0.625% |
| intl/bsb | 30/4704 | 0.638% |
| intl/bulgarian | 2/6799 | 0.029% |
| intl/serbian | 2/943 | 0.212% |
| intl/wikisource_ru | 0/693 | 0.000% |
| **ia total** | **19/7671** | **0.248%** |
| **intl total** | **34/13139** | **0.259%** |
| **gr total** | **374/31848** | **1.174%** |

Ten seeded random changed lines outside all 640 cards (seed 20261016; see [receipt](receipts/random_changed_non_cards.jsonl)):

| Line | Old → fixed |
|---|---|
| gr/elstat--GRESYE_01_0001_00288-9c0e95cc--000013-l0225 | )) → **)** |
| gr/pleias--asty-1724-ebb2596a--000004-l0013 | ἀβίωτος φαίνεται αὐτῷ ἡ ζωὴ ἄνευ ἐργασίας δὲν ἔκρινε ἔκρινε πρέπον ν᾿ ἀρ → **ἀβίωτος φαίνεται αὐτῷ ἡ ζωὴ ἄνευ ἐργασίας δὲν ἔκρινε πρέπον ν᾿ ἀρ** |
| gr/openarchives--hf-1ac7969a077332d2-48a986cf--000019-l0204 | τρὰρ τρὰρ περιτρέχει, πο «γλυστρῶντας», τὴν ὑδρόγειο, → **τρὰρ περιτρέχει, πο «γλυστρῶντας», τὴν ὑδρόγειο,** |
| gr/openarchives--hf-1ac7969a077332d2-48a986cf--000018-l0172 | νομίας, ς, ἀνώτερα καὶ κατώτερα, τὰ πολλαπλά → **νομίας, ἀνώτερα καὶ κατώτερα, τὰ πολλαπλά** |
| gr/openarchives--hf-2db159247291713a-9cb8af81--000023-l0127 | τὸν δωρητήν. ᾿Αλλ' ἐγὼ δὲν ἔβγα ἔβγαλα καμμίαν → **τὸν δωρητήν. ᾿Αλλ' ἐγὼ δὲν ἔβγαλα καμμίαν** |
| gr/openarchives--hf-2db159247291713a-9cb8af81--000023-l0216 | ἀρχηγός ἔγραψε αψε τὴν ἀκόλουθη «φουτουριστική → **ἀρχηγός ἔγραψε τὴν ἀκόλουθη «φουτουριστική** |
| gr/government-gazette--19800201000-da54f14b--000010-l0164 | , ων, λόγω λό → **, ων λόγω** |
| gr/openarchives--hf-1ac7969a077332d2-48a986cf--000019-l0171 | γραφέας ρωτᾶ, δὲν ρωτᾶ, δὲν δογματίζει. → **γραφέας ρωτᾶ, δὲν δογματίζει.** |
| gr/government-gazette--19710400109-4c2fcb91--000003-l0057 | μείου Αρχαιολογικῶν Πόρων καὶ Ἀπα ᾿Απαλλοτριώσεων, ὑπὲρ → **μείου Αρχαιολογικῶν Πόρων καὶ ᾿Απαλλοτριώσεων, ὑπὲρ** |
| ia/india.history.resource.78814--n284-l0021 | 02 2 Tim. iii. 16. → **02 Tim. iii. 16.** |

## 2. Per-source held-out accuracy, marks, removal, and yield

Letters columns use the **held-out 20 cards per source** and only the F2-usable subset at each stage. They show original → assembly-fixed → screen-surviving. Each value is y/n with a Wilson 95% interval; any `u` remains in the denominator and does not count as success. Marks use **all up-to-40 cards**, restricted to surviving usable cards with marks y/n; `na` is excluded and counted in the receipts. The separate test-only marks estimates are in [statistics.json](receipts/statistics.json). No marks verdict is promoted after a letter repair.

Full-line removal is measured over **all original `usable_candidate` rows**, not the card sample. Original P1 admission, codec, G1b and dedup eligibility are frozen: no rejected row is promoted. A fixed label that becomes empty/short/symbol-heavy is withheld as well. The removal column includes that conservative fix gate plus the merged-crop screen. The screen rejects a crop; it never recuts or repairs one.

Yield cells show rows per **successful saved read page** and page-bootstrap 95% intervals (5,000 resamples). Primary classes are disjoint. All successful final-cohort pages, including zero-yield pages, enter the denominator. These intervals describe the F2 page mix; they are not a population-coverage or 40k-supply guarantee. Wikisource RU is an unreviewed alignment reference and contributes **zero training supply**, regardless of its diagnostic pipeline-usable counts.

| Track/source | Letters original → fixed → after screen (test; Wilson 95%) | Marks after screen (all cards; Wilson 95%) | Full usable removed | Rows/read page by primary class after fix + screen [page-bootstrap 95%] |
|---|---|---|---|---|
| gr/anemi | 81.2% (13/16; 57.0–93.4) → 87.5% (14/16; 64.0–96.5) → 100.0% (12/12; 75.8–100.0) | 90.0% (9/10; 59.6–98.2); na=10; full-40: 84.2% (16/19; 62.4–94.5); **marks_correction_required** | 77/628 (12.26%) | ALL: 27.55 [22.05, 33.60]; dialogue_fiction: 1.40 [0.65, 2.25]; greek_mono: 0.15 [0.00, 0.30]; headings_caps: 1.05 [0.60, 1.55]; latin: 0.85 [0.15, 1.75]; mixed_greek_latin: 2.35 [0.55, 5.20]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 0.80 [0.40, 1.25]; poly1850: 20.95 [15.20, 27.25] |
| gr/elstat | 50.0% (1/2; 9.5–90.5) → 50.0% (1/2; 9.5–90.5) → 100.0% (1/1; 20.7–100.0) | 100.0% (2/2; 34.2–100.0); na=0; full-40: 65.5% (19/29; 47.3–80.1); **marks_correction_required** | 138/5798 (2.38%) | ALL: 195.17 [139.34, 259.38]; cyrillic: 0.00 [0.00, 0.00]; dialogue_fiction: 0.24 [0.03, 0.48]; headings_caps: 0.55 [0.21, 0.97]; latin: 7.48 [4.24, 11.72]; mixed_greek_latin: 7.38 [0.66, 17.86]; modern_scanned: 4.31 [2.03, 7.10]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 173.34 [115.72, 239.69]; poly1900: 1.86 [0.59, 3.55] |
| gr/government-gazette | 46.2% (6/13; 23.2–70.9) → 53.8% (7/13; 29.1–76.8) → 100.0% (4/4; 51.0–100.0) | 50.0% (1/2; 9.5–90.5); na=7; full-40: 75.0% (9/12; 46.8–91.1); **marks_correction_required** | 529/2232 (23.70%) | ALL: 56.77 [46.30, 67.17]; cyrillic: 0.00 [0.00, 0.00]; dialogue_fiction: 2.53 [1.67, 3.50]; greek_mono: 0.83 [0.47, 1.20]; headings_caps: 4.17 [2.67, 5.77]; latin: 0.10 [0.00, 0.20]; mixed_greek_latin: 0.70 [0.13, 1.43]; modern_scanned: 16.27 [7.20, 26.73]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 5.63 [1.93, 10.33]; poly1900: 26.53 [17.07, 36.17] |
| gr/kosmopolis | 100.0% (15/15; 79.6–100.0) → 100.0% (15/15; 79.6–100.0) → 100.0% (11/11; 74.1–100.0) | 83.3% (15/18; 60.8–94.2); na=7; full-40: 84.8% (28/33; 69.1–93.3); **marks_correction_required** | 198/987 (20.06%) | ALL: 26.30 [19.87, 33.93]; dialogue_fiction: 2.93 [1.70, 4.30]; greek_mono: 0.40 [0.20, 0.60]; headings_caps: 0.87 [0.53, 1.23]; latin: 0.30 [0.10, 0.57]; mixed_greek_latin: 0.50 [0.17, 0.93]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 0.90 [0.73, 1.07]; poly1850: 7.13 [0.00, 16.27]; poly1900: 13.27 [10.17, 16.43] |
| gr/lekythos | 78.6% (11/14; 52.4–92.4) → 78.6% (11/14; 52.4–92.4) → 90.0% (9/10; 59.6–98.2) | 63.6% (7/11; 35.4–84.8); na=7; full-40: 69.6% (16/23; 49.1–84.4); **marks_correction_required** | 285/4708 (6.05%) | ALL: 147.43 [114.13, 182.50]; dialogue_fiction: 11.50 [7.73, 15.70]; greek_mono: 2.83 [1.70, 4.20]; headings_caps: 3.23 [2.33, 4.23]; latin: 0.57 [0.13, 1.13]; mixed_greek_latin: 1.97 [0.80, 3.43]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 1.20 [0.87, 1.53]; poly1900: 126.13 [95.00, 156.83] |
| gr/nlg-digital | 84.6% (11/13; 57.8–95.7) → 84.6% (11/13; 57.8–95.7) → 91.7% (11/12; 64.6–98.5) | 86.4% (19/22; 66.7–95.3); na=4; full-40: 91.2% (31/34; 77.0–97.0); **marks_correction_required** | 19/915 (2.08%) | ALL: 29.87 [23.90, 36.10]; dialogue_fiction: 1.97 [0.87, 3.33]; greek_mono: 0.20 [0.03, 0.40]; greek_poly: 2.27 [0.03, 4.73]; headings_caps: 0.60 [0.23, 1.07]; latin: 0.20 [0.00, 0.47]; mixed_greek_latin: 0.97 [0.23, 2.07]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 0.60 [0.40, 0.80]; poly1850: 14.13 [7.57, 21.00]; poly1900: 8.93 [4.73, 13.43] |
| gr/openarchives | 50.0% (6/12; 25.4–74.6) → 91.7% (11/12; 64.6–98.5) → 100.0% (9/9; 70.1–100.0) | 81.8% (9/11; 52.3–94.9); na=12; full-40: 85.0% (17/20; 64.0–94.8); **marks_correction_required** | 212/2281 (9.29%) | ALL: 71.34 [52.38, 91.11]; dialogue_fiction: 4.45 [2.48, 6.79]; greek_mono: 0.03 [0.00, 0.10]; greek_poly: 9.14 [3.69, 15.38]; headings_caps: 1.24 [0.72, 1.83]; latin: 8.97 [3.28, 16.00]; mixed_greek_latin: 2.55 [1.38, 3.86]; modern_scanned: 3.24 [0.97, 6.03]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 1.03 [0.72, 1.38]; poly1850: 4.31 [0.93, 8.17]; poly1900: 36.38 [17.03, 57.66] |
| gr/pergamos | 50.0% (6/12; 25.4–74.6) → 50.0% (6/12; 25.4–74.6) → 50.0% (3/6; 18.8–81.2) | 100.0% (4/4; 51.0–100.0); na=9; full-40: 64.7% (11/17; 41.3–82.7); **marks_correction_required** | 164/891 (18.41%) | ALL: 25.96 [18.04, 34.54]; cyrillic: 0.00 [0.00, 0.00]; dialogue_fiction: 0.46 [0.07, 1.00]; greek_mono: 2.86 [0.75, 6.14]; greek_poly: 1.79 [0.00, 4.50]; headings_caps: 0.57 [0.18, 1.04]; latin: 0.04 [0.00, 0.11]; mixed_greek_latin: 0.00 [0.00, 0.00]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 0.93 [0.36, 1.86]; poly1850: 10.18 [4.14, 17.57]; poly1900: 9.14 [2.93, 16.57] |
| gr/pleias | 100.0% (7/7; 64.6–100.0) → 100.0% (7/7; 64.6–100.0) → 100.0% (6/6; 61.0–100.0) | 87.5% (7/8; 52.9–97.8); na=3; full-40: 85.2% (23/27; 67.5–94.1); **marks_correction_required** | 116/2247 (5.16%) | ALL: 71.03 [58.57, 83.43]; cyrillic: 0.00 [0.00, 0.00]; dialogue_fiction: 3.63 [2.20, 5.20]; greek_mono: 0.90 [0.53, 1.33]; greek_poly: 4.90 [0.00, 12.87]; headings_caps: 1.13 [0.50, 1.90]; latin: 0.03 [0.00, 0.10]; mixed_greek_latin: 0.90 [0.17, 1.87]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 2.77 [0.23, 6.73]; poly1850: 51.30 [38.07, 64.83]; poly1900: 5.47 [0.00, 13.67] |
| ia/cyrillic | 85.7% (12/14; 60.1–96.0) → 85.7% (12/14; 60.1–96.0) → 100.0% (12/12; 75.8–100.0) | 100.0% (1/1; 20.7–100.0); na=21; full-40: 100.0% (1/1; 20.7–100.0) | 19/1008 (1.88%) | ALL: 32.97 [21.80, 46.34]; cyrillic: 30.03 [19.53, 43.67]; greek_mono: 0.00 [0.00, 0.00]; greek_poly: 0.03 [0.00, 0.10]; latin: 0.03 [0.00, 0.10]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 2.87 [0.57, 6.67] |
| ia/greek_latin | 68.8% (11/16; 44.4–85.8) → 68.8% (11/16; 44.4–85.8) → 68.8% (11/16; 44.4–85.8) | 87.5% (14/16; 64.0–96.5); na=16; full-40: 80.0% (16/20; 58.4–91.9); **marks_correction_required** | 3/2294 (0.13%) | ALL: 76.37 [60.23, 93.00]; cyrillic: 0.00 [0.00, 0.00]; dialogue_fiction: 0.00 [0.00, 0.00]; greek_mono: 0.87 [0.07, 1.97]; greek_poly: 4.23 [1.50, 7.83]; headings_caps: 0.03 [0.00, 0.10]; latin: 48.23 [35.37, 61.27]; mixed_greek_latin: 22.03 [13.03, 32.57]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 0.97 [0.70, 1.27] |
| ia/poly1850 | 82.4% (14/17; 59.0–93.8) → 82.4% (14/17; 59.0–93.8) → 82.4% (14/17; 59.0–93.8) | 95.0% (19/20; 76.4–99.1); na=10; full-40: 92.9% (26/28; 77.4–98.0) | 4/740 (0.54%) | ALL: 27.26 [22.22, 33.19]; dialogue_fiction: 0.33 [0.11, 0.63]; greek_mono: 0.33 [0.04, 0.81]; headings_caps: 0.33 [0.15, 0.52]; latin: 2.07 [0.93, 3.48]; mixed_greek_latin: 3.04 [1.33, 5.07]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 1.30 [0.81, 1.85]; poly1850: 19.85 [15.56, 24.41] |
| ia/poly1900 | 81.2% (13/16; 57.0–93.4) → 81.2% (13/16; 57.0–93.4) → 81.2% (13/16; 57.0–93.4) | 84.2% (16/19; 62.4–94.5); na=12; full-40: 75.0% (18/24; 55.1–88.0); **marks_correction_required** | 25/1072 (2.33%) | ALL: 38.78 [28.11, 51.30]; dialogue_fiction: 0.19 [0.00, 0.44]; greek_mono: 6.74 [3.22, 10.89]; headings_caps: 0.26 [0.04, 0.56]; latin: 18.52 [7.19, 32.78]; mixed_greek_latin: 2.44 [0.93, 4.33]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 2.30 [0.52, 4.96]; poly1900: 8.33 [4.07, 13.11] |
| intl/bsb | 78.9% (15/19; 56.7–91.5) → 84.2% (16/19; 62.4–94.5) → 88.9% (16/18; 67.2–96.9) | 81.8% (18/22; 61.5–92.7); na=10; full-40: 77.8% (21/27; 59.2–89.4); **marks_correction_required** | 190/2820 (6.74%) | ALL: 35.54 [30.26, 40.97]; cyrillic: 0.76 [0.00, 1.78]; dialogue_fiction: 0.99 [0.24, 2.03]; greek_mono: 0.82 [0.41, 1.42]; greek_poly: 2.36 [1.11, 3.88]; headings_caps: 0.24 [0.03, 0.51]; latin: 9.07 [6.19, 12.41]; mixed_greek_latin: 11.41 [7.69, 15.72]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 1.03 [0.76, 1.35]; poly1850: 7.53 [4.43, 11.28]; poly1900: 1.34 [0.39, 2.65] |
| intl/bulgarian | 40.0% (4/10; 16.8–68.7) → 40.0% (4/10; 16.8–68.7) → 37.5% (3/8; 13.7–69.4) | unmeasured (0); na=19; full-40: unmeasured (0) | 321/2247 (14.29%) | ALL: 66.41 [44.72, 90.24]; cyrillic: 60.59 [40.34, 82.90]; latin: 0.17 [0.00, 0.41]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 5.66 [1.28, 12.17] |
| intl/serbian | 80.0% (4/5; 37.6–96.4) → 80.0% (4/5; 37.6–96.4) → 80.0% (4/5; 37.6–96.4) | unmeasured (0); na=12; full-40: unmeasured (0) | 12/210 (5.71%) | ALL: 6.60 [4.83, 8.50]; cyrillic: 4.57 [3.00, 6.43]; latin: 1.23 [0.30, 2.53]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 0.80 [0.60, 1.00] |
| intl/wikisource_ru | unreviewed | unmeasured (0); na=0; full-40: unmeasured (0) | 14/372 (3.76%) | ALL: 17.90 [13.45, 22.65]; cyrillic: 16.05 [11.95, 20.75]; greek_mono: 0.00 [0.00, 0.00]; latin: 1.20 [0.05, 3.35]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 0.65 [0.30, 1.10] |

**Government Gazette — priority modern-scanned route.** 1,703/2,232 original usable rows survive the fix gate and screen (76.3%). Held-out surviving usable accuracy is **100.0% (4/4; 51.0–100.0)**, compared with 46.2% (6/13; 23.2–70.9) originally; the all-40 diagnostic is **88.9% (8/9; 56.5–98.0)**. The surviving test mix is **latin=2, mixed_greek_latin=1, numerics_tables=1**. Modern-scanned target test accuracy is **unmeasured (0)** and poly1900 target test accuracy is **unmeasured (0)**; numeric and Latin by-products do not establish Greek target accuracy. Conditional yield on the **12 modern read pages** is **40.67 [25.25, 58.58] modern-scanned rows/page**; on the **18 poly1900 read pages**, **44.22 [35.06, 53.83] poly1900 rows/page**. These conditional period rates use their own read-page denominators; the main table uses all Gazette read pages. **The 40k modern-scanned route remains unqualified:** the class-specific card evidence is limited, its Wilson interval cannot establish ≥90% target accuracy, and marks remain a separate requirement (50.0% (1/2; 9.5–90.5)).

| Gazette primary class | Surviving usable letters, all 40 | Surviving usable letters, test only |
|---|---|---|
| modern_scanned | 100.0% (1/1; 20.7–100.0) | unmeasured (0) |
| poly1900 | 50.0% (1/2; 9.5–90.5) | unmeasured (0) |
| greek_mono | 100.0% (1/1; 20.7–100.0) | unmeasured (0) |
| latin | 100.0% (2/2; 34.2–100.0) | 100.0% (2/2; 34.2–100.0) |
| numerics_tables | 100.0% (1/1; 20.7–100.0) | 100.0% (1/1; 20.7–100.0) |
| mixed_greek_latin | 100.0% (2/2; 34.2–100.0) | 100.0% (1/1; 20.7–100.0) |

## 3. Calibration and held-out screen performance

Seed **20261016**, exactly 20 calibration / 20 test cards for each of 16 sources; source-stratified only, not outcome-stratified. The split was written before feature extraction. The global threshold family contains height ratio, token vertical spread, internal x-gap, label/ink density ratio, paragraph count, and projection-peak/height conjunctions. At most three OR branches are allowed. The objective was calibration F1, with fixed tie breaks (precision, fewer calibration rejections, fewer branches); no per-source tuning or test threshold selection.

Frozen selected screen: `[{"token_y_spread_xh": 1.2}, {"projection_peaks": 2, "crop_height_xh": 2.0}]`. Every inequality is strict `>`. [Model, full candidate grid and calibration-card identities](receipts/model.json); [seeded split](receipts/split.jsonl). The screen never consumes a card ID, source identity, or G1b measurement. The assembly guard was settled before this final fit. An earlier discarded prototype used G1b scales and its held-out outcomes were already read; the final features were replaced solely to enforce the requested input contract, and final thresholds were fitted using calibration outcomes only. This is **not a pristine new blind validation** of the final full pipeline. [Protocol and discarded-prototype disclosure](receipts/screen_protocol.json).

Calibration: TP=38, FP=16, FN=25, TN=241; P=70.4%, R=60.3%. Held-out specified endpoint: **TP=34, FP=21, FN=20, TN=245; precision 61.8% (34/55; 48.6–73.5), recall 63.0% (34/54; 49.6–74.6).**

**Screen verdict: experimental, not qualified for automatic admission.** The requested-endpoint performance is reported above; the limited class-specific sample and prior discarded-prototype test exposure prevent a fresh blind production-validation claim. The stored decisions make the observed tradeoff inspectable.

The primary positive is exactly the requested **original blind letters=n AND errors includes merged_two_lines, extra_text, or crop_overrun**. It deliberately retains duplicate-only cards even when assembly has repaired them. A secondary residual endpoint removes only cards whose base letters were repaired: P=54.5%, R=68.2% (TP/FP/FN/TN 30/25/14/251). These are different endpoints, not interchangeable scores. Some specified-endpoint false positives have blind letters=y despite `merged_two_lines` or `crop_overrun`; the physical diagnostic is reported separately in the receipt, without changing the requested positive definition.

| Source | Held-out screen TP / FP / FN / TN | Precision / recall |
|---|---|---|
| gr/anemi | 2 / 2 / 1 / 15 | 50.0% / 66.7% |
| gr/elstat | 1 / 0 / 2 / 17 | 100.0% / 33.3% |
| gr/government-gazette | 9 / 3 / 0 / 8 | 75.0% / 100.0% |
| gr/kosmopolis | 0 / 5 / 0 / 15 | 0.0% / n/a |
| gr/lekythos | 3 / 3 / 1 / 13 | 50.0% / 75.0% |
| gr/nlg-digital | 1 / 0 / 0 / 19 | 100.0% / 100.0% |
| gr/openarchives | 4 / 1 / 4 / 11 | 80.0% / 50.0% |
| gr/pergamos | 4 / 3 / 0 / 13 | 57.1% / 100.0% |
| gr/pleias | 0 / 2 / 4 / 14 | 0.0% / 0.0% |
| ia/cyrillic | 4 / 0 / 0 / 16 | 100.0% / 100.0% |
| ia/greek_latin | 0 / 0 / 1 / 19 | n/a / 0.0% |
| ia/poly1850 | 0 / 0 / 2 / 18 | n/a / 0.0% |
| ia/poly1900 | 1 / 1 / 1 / 17 | 50.0% / 50.0% |
| intl/bsb | 2 / 0 / 2 / 16 | 100.0% / 50.0% |
| intl/bulgarian | 3 / 1 / 2 / 14 | 75.0% / 60.0% |
| intl/serbian | 0 / 0 / 0 / 20 | n/a / n/a |

Pixel features use the exact existing F2 crop rectangle on its stored page raster: fixed dark-ink threshold `(p05+p90)/2`, capped at 200. The x-height scale is a **crop-component median body-height proxy**, not a typographic measurement: connected components with height ≥max(3 px, 12% crop height) and ≤90% crop height, width/height 0.12–3, and width ≤max(6 px, 25% crop width). At least three eligible components are needed; otherwise use half the median saved Google token height. No detector or G1b measurement supplies this scale. The page row height is the median saved Google line-box height on alphabetic lines. Horizontal ink projection is smoothed at 0.12 of the body-height proxy; peaks at ≥20% of maximum with ≥18% prominence and 0.7 proxy-height separation. An internal low-ink x-gap requires ≥10% of ink mass on each side. Density is visible fixed-label characters per crop ink width in proxy x-heights divided by that page’s median. Token centers and paragraph membership come from saved Google geometry. Every F2 row has one Google line anchor, so the Google-line contributor count is one and offers no discrimination; token vertical spread still detects multi-row anchors. G1b flags enter only the frozen original-usability denominator, never the screen decision.

## 4. Marks remain a separate requirement

The marks column above is taken verbatim from the blind marks field on surviving usable cards, with Wilson 95% intervals. Every row from a measured polytonic source below 90% carries `marks_correction_required` in [features.jsonl](features.jsonl), including its Latin/numeric by-products. Conservatively, the source tag is retained if **either** the full blind-40 marks estimate **or** the surviving-usable estimate is below 90%. In particular, ELSTAT 19/29 (65.5%) and Pergamos 11/17 (64.7%) retain their known weak-source evidence even if a tiny selected subset is perfect. This source tag is not a mark repair. A zero measurable surviving denominator is also tagged `marks_unmeasured`, not passed.

Lekythos mark-error types (card counts, not token counts) are derived only from explicit printed → Google pairs in the blind detail. Grave→acute, circumflex→acute and breathing dropped are tabulated in [lekythos_marks.json](receipts/lekythos_marks.json); these include all 40, the usable subset, and the post-screen usable subset. No error type is inferred from `marks=na`. Its large supply therefore remains conditional on mark correction whenever the measured surviving marks point estimate is below 90%.

| Lekythos mark error | All 40 cards | Originally usable | Surviving usable |
|---|---:|---:|---:|
| grave→acute | 3 | 1 | 0 |
| circumflex→acute | 2 | 1 | 1 |
| breathing dropped | 2 | 1 | 1 |
| accent dropped | 2 | 2 | 2 |
| mark plus wrong base letter | 1 | 1 | 1 |

## 5. Text-side conventions and counts

Checks ran over every line; the table counts every usable row **after steps 1–2**, before text exclusions. Original-usable branch counts are also retained in [convention_counts.jsonl](receipts/convention_counts.jsonl). Text-side exclusions are applied in `usable_final`; `fixed_label` remains the assembly output and `label_after_conventions` is the convention-normalized label.

**ſ→s:** accepted as a glyph variant. Count literal ſ in labels and exact blind-detail witnesses. BSB c008 is an additional visually inspected Fraktur witness. The total number of printed long-s lines is **not determinable** from labels already normalized to s; a zero Unicode count is not proof of zero printed ſ.

**Roman look-alikes:** deterministic table `{"Ι": "I", "Χ": "X", "Μ": "M", "Ϲ": "C", "І": "I", "Х": "X", "С": "C", "М": "M", "Ѵ": "V"}`, with Latin I,V,X,L,C,M,D unchanged. Convert only a whole letter token whose complete mapped value matches `^[IVXLCMD]+$`. No Δ→D or Λ→L guess is allowed. A single Greek/Cyrillic letter followed by a period (e.g. Χ. as a person’s initial) has ambiguous numeral intent and excludes the line instead of changing its script. Ambiguous Roman-shaped tokens containing Λ,Δ,Д,Л,П,Ӏ, or mixed Latin-Roman / Greek-Cyrillic tokens that fail the complete map, also exclude the line. The table’s fixed and excluded Roman line branches are disjoint: a line containing both types is counted in exclusion, with overlap recorded separately in the receipt. This candidate grammar is explicit; general all-script capital words cannot reliably be identified as intended Roman numerals from text alone.

**Dropped line-end hyphen:** bind the nearest lower Google row in the same column (≥50% shorter-width overlap, left edges within 1.5 page-median Google row heights, gap ≤2 crop heights). Exclude a no-hyphen final word fragment followed by lowercase only when tail+head is attested on at least two other pages and the tail never appears as a nonfinal corpus word. This is a conservative text-only fragment test; remaining lowercase continuations are explicitly `fragment_unknown`, not silently asserted to be complete words. No pixel-derived feature or ink work is used for this check.

**Em dash→hyphen:** accepted. Exact printed em-dash substitutions are counted only where blind detail establishes them; ordinary hyphens elsewhere cannot distinguish a changed em dash from a true hyphen. Therefore whole-corpus physical substitution counts are **not determinable**. The table also gives label-hyphen candidate lines without asserting their printed glyph.

| Track/source | Usable lines checked | ſ label lines / blind witnesses / visual witnesses | Roman fixed lines (tokens) / excluded lines | Dropped-hyphen exclusions / lowercase-fragment unknown | Em-dash→hyphen blind witnesses, all→surviving / label-hyphen lines |
|---|---:|---|---|---|---|
| gr/anemi | 551 | 0 / 0 / 0→0 | 1 (1) / 34 | 5 / 198 | 1→1 / 117 |
| gr/elstat | 5660 | 0 / 0 / 0→0 | 3 (3) / 15 | 1 / 38 | 0→0 / 455 |
| gr/government-gazette | 1703 | 0 / 0 / 0→0 | 6 (6) / 57 | 11 / 434 | 0→0 / 301 |
| gr/kosmopolis | 789 | 0 / 0 / 0→0 | 0 (0) / 6 | 1 / 274 | 0→0 / 178 |
| gr/lekythos | 4423 | 0 / 0 / 0→0 | 0 (0) / 16 | 15 / 1942 | 2→1 / 1166 |
| gr/nlg-digital | 896 | 0 / 0 / 0→0 | 1 (1) / 6 | 5 / 334 | 0→0 / 287 |
| gr/openarchives | 2069 | 0 / 0 / 0→0 | 6 (7) / 8 | 17 / 860 | 1→1 / 538 |
| gr/pergamos | 727 | 0 / 0 / 0→0 | 1 (1) / 22 | 11 / 314 | 3→1 / 96 |
| gr/pleias | 2131 | 0 / 0 / 0→0 | 2 (2) / 14 | 13 / 838 | 2→0 / 544 |
| ia/cyrillic | 989 | 0 / 0 / 0→0 | 3 (3) / 11 | 1 / 304 | 4→2 / 343 |
| ia/greek_latin | 2291 | 0 / 0 / 0→0 | 3 (3) / 1 | 0 / 1062 | 0→0 / 427 |
| ia/poly1850 | 736 | 0 / 0 / 0→0 | 1 (1) / 3 | 1 / 309 | 0→0 / 122 |
| ia/poly1900 | 1047 | 0 / 0 / 0→0 | 9 (9) / 0 | 0 / 371 | 0→0 / 160 |
| intl/bsb | 2630 | 0 / 0 / 1→0 | 10 (11) / 11 | 3 / 727 | 0→0 / 590 |
| intl/bulgarian | 1926 | 0 / 0 / 0→0 | 9 (9) / 31 | 9 / 706 | 0→0 / 510 |
| intl/serbian | 198 | 0 / 0 / 0→0 | 0 (0) / 1 | 0 / 33 | 0→0 / 45 |
| intl/wikisource_ru | 358 | 0 / 0 / 0→0 | 1 (1) / 2 | 1 / 120 | 0→0 / 110 |

After text exclusions (pipeline counts; RU reference remains excluded from training supply):

| Source | After screen → after text checks | Additional text exclusions | Total original usable removed |
|---|---:|---:|---:|
| gr/anemi | 551→512 | 39 | 18.47% |
| gr/elstat | 5660→5644 | 16 | 2.66% |
| gr/government-gazette | 1703→1635 | 68 | 26.75% |
| gr/kosmopolis | 789→782 | 7 | 20.77% |
| gr/lekythos | 4423→4392 | 31 | 6.71% |
| gr/nlg-digital | 896→885 | 11 | 3.28% |
| gr/openarchives | 2069→2045 | 24 | 10.35% |
| gr/pergamos | 727→694 | 33 | 22.11% |
| gr/pleias | 2131→2104 | 27 | 6.36% |
| ia/cyrillic | 989→977 | 12 | 3.08% |
| ia/greek_latin | 2291→2290 | 1 | 0.17% |
| ia/poly1850 | 736→732 | 4 | 1.08% |
| ia/poly1900 | 1047→1047 | 0 | 2.33% |
| intl/bsb | 2630→2616 | 14 | 7.23% |
| intl/bulgarian | 1926→1886 | 40 | 16.07% |
| intl/serbian | 198→197 | 1 | 6.19% |
| intl/wikisource_ru | 358→355 | 3 | 4.57% |

## 6. Verdict and limits

The requested source verdict, limited to the **descriptive final surviving usable subset of all 40 supplied cards per source**, reaches a ≥90% letters-y point estimate for **anemi, elstat, kosmopolis, nlg-digital, pleias, cyrillic, bsb**. The separate held-out after-screen ≥90% list is **anemi, elstat, government-gazette, kosmopolis, lekythos, nlg-digital, openarchives, pleias, cyrillic**. The denominators and class mix matter; neither list establishes whole-source accuracy. No source has a held-out Wilson lower bound ≥90%. Repaired labels were compared with the existing printed readings, not sent for a new blind check.

All-40 letter counts (descriptive, includes the calibration cards):

| Source | Original → fixed → screen → final usable letters, all 40 (Wilson 95%) |
|---|---|
| gr/anemi | 78.6% (22/28; 60.5–89.8) → 82.1% (23/28; 64.4–92.1) → 95.0% (19/20; 76.4–99.1) → 95.0% (19/20; 76.4–99.1) |
| gr/elstat | 66.7% (2/3; 20.8–93.9) → 66.7% (2/3; 20.8–93.9) → 100.0% (2/2; 34.2–100.0) → 100.0% (2/2; 34.2–100.0) |
| gr/government-gazette | 36.0% (9/25; 20.2–55.5) → 48.0% (12/25; 30.0–66.5) → 88.9% (8/9; 56.5–98.0) → 88.9% (8/9; 56.5–98.0) |
| gr/kosmopolis | 100.0% (32/32; 89.3–100.0) → 100.0% (32/32; 89.3–100.0) → 100.0% (25/25; 86.7–100.0) → 100.0% (25/25; 86.7–100.0) |
| gr/lekythos | 73.9% (17/23; 53.5–87.5) → 78.3% (18/23; 58.1–90.3) → 88.9% (16/18; 67.2–96.9) → 88.9% (16/18; 67.2–96.9) |
| gr/nlg-digital | 92.9% (26/28; 77.4–98.0) → 92.9% (26/28; 77.4–98.0) → 96.2% (25/26; 81.1–99.3) → 96.2% (25/26; 81.1–99.3) |
| gr/openarchives | 50.0% (14/28; 32.6–67.4) → 78.6% (22/28; 60.5–89.8) → 87.0% (20/23; 67.9–95.5) → 87.0% (20/23; 67.9–95.5) |
| gr/pergamos | 36.0% (9/25; 20.2–55.5) → 36.0% (9/25; 20.2–55.5) → 46.2% (6/13; 23.2–70.9) → 50.0% (6/12; 25.4–74.6) |
| gr/pleias | 81.2% (13/16; 57.0–93.4) → 81.2% (13/16; 57.0–93.4) → 90.9% (10/11; 62.3–98.4) → 90.9% (10/11; 62.3–98.4) |
| ia/cyrillic | 84.6% (22/26; 66.5–93.8) → 84.6% (22/26; 66.5–93.8) → 100.0% (22/22; 85.1–100.0) → 100.0% (22/22; 85.1–100.0) |
| ia/greek_latin | 84.4% (27/32; 68.2–93.1) → 84.4% (27/32; 68.2–93.1) → 84.4% (27/32; 68.2–93.1) → 84.4% (27/32; 68.2–93.1) |
| ia/poly1850 | 86.7% (26/30; 70.3–94.7) → 86.7% (26/30; 70.3–94.7) → 86.7% (26/30; 70.3–94.7) → 86.7% (26/30; 70.3–94.7) |
| ia/poly1900 | 71.9% (23/32; 54.6–84.4) → 71.9% (23/32; 54.6–84.4) → 74.2% (23/31; 56.8–86.3) → 74.2% (23/31; 56.8–86.3) |
| intl/bsb | 87.9% (29/33; 72.7–95.2) → 90.9% (30/33; 76.4–96.9) → 93.8% (30/32; 79.9–98.3) → 93.8% (30/32; 79.9–98.3) |
| intl/bulgarian | 50.0% (11/22; 30.7–69.3) → 50.0% (11/22; 30.7–69.3) → 52.6% (10/19; 31.7–72.7) → 50.0% (9/18; 29.0–71.0) |
| intl/serbian | 83.3% (10/12; 55.2–95.3) → 83.3% (10/12; 55.2–95.3) → 83.3% (10/12; 55.2–95.3) → 83.3% (10/12; 55.2–95.3) |

| Source below 90%, or unmeasured (all 40) | Surviving usable letters | Residual errors on all surviving usable cards |
|---|---|---|
| gr/government-gazette | 88.9% (8/9; 56.5–98.0) | extra_text=1, missing_mark=1 |
| gr/lekythos | 88.9% (16/18; 67.2–96.9) | wrong_letter=1, wrong_mark=1, extra_text=1 |
| gr/openarchives | 87.0% (20/23; 67.9–95.5) | wrong_letter=2, extra_text=1, punctuation=1, crop_overrun=1 |
| gr/pergamos | 50.0% (6/12; 25.4–74.6) | wrong_letter=3, missing_mark=3, hyphen=1, punctuation=1, extra_text=1 |
| ia/greek_latin | 84.4% (27/32; 68.2–93.1) | wrong_letter=3, lookalike_script_letter=2, crop_overrun=2, punctuation=1 |
| ia/poly1850 | 86.7% (26/30; 70.3–94.7) | punctuation=3, lookalike_script_letter=2, crop_overrun=2, wrong_letter=1, crop_clipped=1 |
| ia/poly1900 | 74.2% (23/31; 56.8–86.3) | wrong_letter=8, crop_overrun=2, crop_clipped=1, wrong_mark=1 |
| intl/bulgarian | 50.0% (9/18; 29.0–71.0) | wrong_letter=9, crop_overrun=3, hyphen=1, merged_two_lines=1, punctuation=1 |
| intl/serbian | 83.3% (10/12; 55.2–95.3) | wrong_letter=1 |

Measured polytonic sources below 90% in the full blind sample or surviving usable marks-y: **anemi, elstat, government-gazette, kosmopolis, lekythos, nlg-digital, openarchives, pergamos, pleias, greek_latin, poly1900, bsb**. All carry the requested source tag; no marks were corrected by this task.

Overall: 31,450 original pipeline-usable rows → 29,124 after fix+screen → 28,793 after text exclusions. 28,438 are candidate rows after removing reference-only RU. These remain silver candidates, not released or independently revalidated training labels. The final footer removal percentage includes text exclusions; the per-source main table isolates fix+screen removal.

Reproduce offline with the worktree’s existing Python environment (Pillow, NumPy, SciPy):

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/records/harvest/screen_v1/screen.py extract
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/records/harvest/screen_v1/screen.py calibrate
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/records/harvest/screen_v1/evaluate.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/records/harvest/screen_v1/validate.py
```

The manual assembly comparisons are frozen in [assembly_review.jsonl](receipts/assembly_review.jsonl). Native review panels are in [changed-card panel 1](receipts/changed_cards_01.png), [random non-cards 1](receipts/random_changed_01.png), [random non-cards 2](receipts/random_changed_02.png), and [stacked-row/date controls](receipts/negative_controls.png). The random rows expose residual provider errors and crop defects as well as resolved duplicates; they are not ten newly certified labels ([review notes](receipts/random_collateral_review.jsonl)). Source and output hashes, crop-pixel checks, outcome counts, statistical denominators, and commit status are in [receipts/](receipts/). The source-bound [guarded commit helper](commit_helper.py) is left for a writable Git index; it validates input and artifact hashes and stages only the enumerated output files.

For exact calibration replay, `screen.py calibrate` uses the archived final crop/Google feature snapshot and split when those receipts exist. The discarded G1b-scaled prototype is isolated under [prototype_g1b_scaled/](receipts/prototype_g1b_scaled/); none of its metrics or features is the final screen result.

Footer conventions: screen P/R uses the held-out half; source letters and Gazette accuracy use the descriptive all-40 final surviving subset; marks lists sources below 90% in either their full blind marks sample or surviving usable marks subset; Gazette modern rows/page uses the modern-period denominator after fix+screen; total removal includes the text-side exclusions.

T4b: done | interleave fix: 16 cards fixed of 20, lines changed 0.811% | screen P/R test: 61.8%/63.0% | letters ≥90% after: anemi,elstat,kosmopolis,nlg-digital,pleias,cyrillic,bsb | marks <90%: anemi,elstat,government-gazette,kosmopolis,lekythos,nlg-digital,openarchives,pergamos,pleias,greek_latin,poly1900,bsb | gazette letters after: 88.9% rows/page modern 40.67 | usable rows removed: 8.45%
