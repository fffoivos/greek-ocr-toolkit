# Discarded prototype — outside the final feature-input contract

Historical diagnostic only. This is not the final T4b result; its links retain their original run context. See STATUS.json and the main ../../REPORT.md.

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
| gr/anemi | 81.2% (13/16; 57.0–93.4) → 87.5% (14/16; 64.0–96.5) → 100.0% (11/11; 74.1–100.0) | 88.9% (8/9; 56.5–98.0); na=9; full-40: 84.2% (16/19; 62.4–94.5); **marks_correction_required** | 217/628 (34.55%) | ALL: 20.55 [15.50, 25.75]; dialogue_fiction: 1.20 [0.55, 1.95]; greek_mono: 0.15 [0.00, 0.30]; headings_caps: 1.00 [0.55, 1.50]; latin: 0.65 [0.00, 1.55]; mixed_greek_latin: 1.50 [0.15, 3.70]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 0.75 [0.40, 1.15]; poly1850: 15.30 [10.65, 20.65] |
| gr/elstat | 50.0% (1/2; 9.5–90.5) → 50.0% (1/2; 9.5–90.5) → 100.0% (1/1; 20.7–100.0) | 100.0% (2/2; 34.2–100.0); na=0; full-40: 65.5% (19/29; 47.3–80.1); **marks_correction_required** | 208/5798 (3.59%) | ALL: 192.76 [136.20, 256.49]; cyrillic: 0.00 [0.00, 0.00]; dialogue_fiction: 0.24 [0.03, 0.48]; headings_caps: 0.41 [0.17, 0.69]; latin: 6.31 [3.83, 9.34]; mixed_greek_latin: 6.38 [0.41, 15.55]; modern_scanned: 3.86 [1.79, 6.45]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 174.14 [116.17, 239.94]; poly1900: 1.41 [0.55, 2.48] |
| gr/government-gazette | 46.2% (6/13; 23.2–70.9) → 53.8% (7/13; 29.1–76.8) → 100.0% (2/2; 34.2–100.0) | 0.0% (0/1; 0.0–79.3); na=3; full-40: 75.0% (9/12; 46.8–91.1); **marks_correction_required** | 1061/2232 (47.54%) | ALL: 39.03 [30.13, 48.27]; cyrillic: 0.00 [0.00, 0.00]; dialogue_fiction: 1.50 [0.90, 2.20]; greek_mono: 0.60 [0.30, 0.90]; headings_caps: 4.10 [2.60, 5.67]; latin: 0.07 [0.00, 0.17]; mixed_greek_latin: 0.20 [0.00, 0.57]; modern_scanned: 11.63 [4.97, 19.23]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 5.17 [1.83, 9.43]; poly1900: 15.77 [9.93, 21.93] |
| gr/kosmopolis | 100.0% (15/15; 79.6–100.0) → 100.0% (15/15; 79.6–100.0) → 100.0% (9/9; 70.1–100.0) | 83.3% (10/12; 55.2–95.3); na=7; full-40: 84.8% (28/33; 69.1–93.3); **marks_correction_required** | 427/987 (43.26%) | ALL: 18.67 [12.30, 26.37]; dialogue_fiction: 2.03 [1.00, 3.13]; greek_mono: 0.33 [0.17, 0.53]; headings_caps: 0.87 [0.53, 1.23]; latin: 0.30 [0.10, 0.57]; mixed_greek_latin: 0.40 [0.07, 0.83]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 0.90 [0.73, 1.07]; poly1850: 6.00 [0.00, 13.40]; poly1900: 7.83 [5.03, 10.80] |
| gr/lekythos | 78.6% (11/14; 52.4–92.4) → 78.6% (11/14; 52.4–92.4) → 85.7% (6/7; 48.7–97.4) | 75.0% (6/8; 40.9–92.9); na=6; full-40: 69.6% (16/23; 49.1–84.4); **marks_correction_required** | 1426/4708 (30.29%) | ALL: 109.40 [82.10, 139.20]; dialogue_fiction: 8.90 [5.53, 12.77]; greek_mono: 2.57 [1.53, 3.80]; headings_caps: 3.23 [2.30, 4.27]; latin: 0.53 [0.13, 1.10]; mixed_greek_latin: 1.17 [0.43, 2.10]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 1.17 [0.83, 1.50]; poly1900: 91.83 [66.67, 117.77] |
| gr/nlg-digital | 84.6% (11/13; 57.8–95.7) → 84.6% (11/13; 57.8–95.7) → 91.7% (11/12; 64.6–98.5) | 85.7% (18/21; 65.4–95.0); na=4; full-40: 91.2% (31/34; 77.0–97.0); **marks_correction_required** | 68/915 (7.43%) | ALL: 28.23 [22.23, 34.33]; dialogue_fiction: 1.77 [0.67, 3.10]; greek_mono: 0.17 [0.03, 0.33]; greek_poly: 2.27 [0.03, 4.73]; headings_caps: 0.57 [0.23, 0.97]; latin: 0.20 [0.00, 0.47]; mixed_greek_latin: 0.97 [0.23, 2.07]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 0.60 [0.40, 0.80]; poly1850: 13.20 [6.97, 19.83]; poly1900: 8.50 [4.40, 12.97] |
| gr/openarchives | 50.0% (6/12; 25.4–74.6) → 91.7% (11/12; 64.6–98.5) → 100.0% (5/5; 56.6–100.0) | 80.0% (8/10; 49.0–94.3); na=5; full-40: 85.0% (17/20; 64.0–94.8); **marks_correction_required** | 750/2281 (32.88%) | ALL: 52.79 [37.31, 68.97]; dialogue_fiction: 3.72 [2.14, 5.52]; greek_mono: 0.03 [0.00, 0.10]; greek_poly: 4.86 [1.90, 8.45]; headings_caps: 1.10 [0.66, 1.59]; latin: 4.97 [1.79, 8.90]; mixed_greek_latin: 1.97 [0.97, 3.17]; modern_scanned: 3.14 [0.90, 5.90]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 1.03 [0.72, 1.38]; poly1850: 3.62 [0.76, 7.03]; poly1900: 28.34 [12.34, 46.35] |
| gr/pergamos | 50.0% (6/12; 25.4–74.6) → 50.0% (6/12; 25.4–74.6) → 33.3% (1/3; 6.1–79.2) | 100.0% (1/1; 20.7–100.0); na=7; full-40: 64.7% (11/17; 41.3–82.7); **marks_correction_required** | 390/891 (43.77%) | ALL: 17.89 [11.57, 25.04]; cyrillic: 0.00 [0.00, 0.00]; dialogue_fiction: 0.39 [0.00, 0.93]; greek_mono: 1.29 [0.54, 2.18]; greek_poly: 1.21 [0.00, 3.14]; headings_caps: 0.50 [0.14, 0.93]; latin: 0.04 [0.00, 0.11]; mixed_greek_latin: 0.00 [0.00, 0.00]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 0.89 [0.32, 1.79]; poly1850: 7.18 [2.29, 13.47]; poly1900: 6.39 [1.75, 12.29] |
| gr/pleias | 100.0% (7/7; 64.6–100.0) → 100.0% (7/7; 64.6–100.0) → 100.0% (6/6; 61.0–100.0) | 85.7% (6/7; 48.7–97.4); na=3; full-40: 85.2% (23/27; 67.5–94.1); **marks_correction_required** | 475/2247 (21.14%) | ALL: 59.07 [47.80, 69.27]; cyrillic: 0.00 [0.00, 0.00]; dialogue_fiction: 3.13 [1.93, 4.43]; greek_mono: 0.67 [0.33, 1.07]; greek_poly: 4.27 [0.00, 11.13]; headings_caps: 1.03 [0.47, 1.73]; latin: 0.03 [0.00, 0.10]; mixed_greek_latin: 0.47 [0.03, 1.03]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 2.87 [0.23, 7.07]; poly1850: 41.20 [30.30, 52.00]; poly1900: 5.40 [0.00, 13.53] |
| ia/cyrillic | 85.7% (12/14; 60.1–96.0) → 85.7% (12/14; 60.1–96.0) → 100.0% (11/11; 74.1–100.0) | 100.0% (1/1; 20.7–100.0); na=20; full-40: 100.0% (1/1; 20.7–100.0) | 58/1008 (5.75%) | ALL: 31.67 [21.03, 44.30]; cyrillic: 28.77 [18.67, 41.63]; greek_mono: 0.00 [0.00, 0.00]; greek_poly: 0.03 [0.00, 0.10]; latin: 0.03 [0.00, 0.10]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 2.83 [0.53, 6.67] |
| ia/greek_latin | 68.8% (11/16; 44.4–85.8) → 68.8% (11/16; 44.4–85.8) → 66.7% (10/15; 41.7–84.8) | 86.7% (13/15; 62.1–96.3); na=16; full-40: 80.0% (16/20; 58.4–91.9); **marks_correction_required** | 217/2294 (9.46%) | ALL: 69.23 [55.50, 82.77]; cyrillic: 0.00 [0.00, 0.00]; dialogue_fiction: 0.00 [0.00, 0.00]; greek_mono: 0.53 [0.03, 1.20]; greek_poly: 3.43 [1.33, 6.30]; headings_caps: 0.03 [0.00, 0.10]; latin: 45.23 [33.23, 57.30]; mixed_greek_latin: 19.07 [11.73, 27.60]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 0.93 [0.67, 1.23] |
| ia/poly1850 | 82.4% (14/17; 59.0–93.8) → 82.4% (14/17; 59.0–93.8) → 82.4% (14/17; 59.0–93.8) | 95.0% (19/20; 76.4–99.1); na=10; full-40: 92.9% (26/28; 77.4–98.0) | 9/740 (1.22%) | ALL: 27.07 [22.15, 32.74]; dialogue_fiction: 0.33 [0.11, 0.63]; greek_mono: 0.33 [0.04, 0.81]; headings_caps: 0.33 [0.15, 0.52]; latin: 2.04 [0.89, 3.44]; mixed_greek_latin: 2.89 [1.30, 4.78]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 1.41 [0.85, 2.04]; poly1850: 19.74 [15.44, 24.22] |
| ia/poly1900 | 81.2% (13/16; 57.0–93.4) → 81.2% (13/16; 57.0–93.4) → 80.0% (12/15; 54.8–93.0) | 83.3% (15/18; 60.8–94.2); na=12; full-40: 75.0% (18/24; 55.1–88.0); **marks_correction_required** | 57/1072 (5.32%) | ALL: 37.59 [27.15, 49.49]; dialogue_fiction: 0.15 [0.00, 0.33]; greek_mono: 6.56 [3.07, 10.70]; headings_caps: 0.26 [0.04, 0.56]; latin: 18.04 [7.26, 31.45]; mixed_greek_latin: 2.33 [0.85, 4.19]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 2.37 [0.52, 5.07]; poly1900: 7.89 [3.70, 12.56] |
| intl/bsb | 78.9% (15/19; 56.7–91.5) → 84.2% (16/19; 62.4–94.5) → 94.1% (16/17; 73.0–99.0) | 81.0% (17/21; 60.0–92.3); na=10; full-40: 77.8% (21/27; 59.2–89.4); **marks_correction_required** | 514/2820 (18.23%) | ALL: 31.16 [26.84, 35.69]; cyrillic: 0.76 [0.00, 1.78]; dialogue_fiction: 0.97 [0.23, 2.01]; greek_mono: 0.73 [0.32, 1.31]; greek_poly: 2.15 [1.00, 3.55]; headings_caps: 0.24 [0.03, 0.51]; latin: 7.99 [5.35, 11.08]; mixed_greek_latin: 8.57 [5.82, 11.81]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 1.01 [0.76, 1.31]; poly1850: 7.41 [4.32, 11.18]; poly1900: 1.34 [0.39, 2.65] |
| intl/bulgarian | 40.0% (4/10; 16.8–68.7) → 40.0% (4/10; 16.8–68.7) → 50.0% (3/6; 18.8–81.2) | unmeasured (0); na=13; full-40: unmeasured (0) | 881/2247 (39.21%) | ALL: 47.10 [30.21, 66.14]; cyrillic: 41.28 [26.48, 57.41]; latin: 0.17 [0.00, 0.41]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 5.66 [1.21, 12.38] |
| intl/serbian | 80.0% (4/5; 37.6–96.4) → 80.0% (4/5; 37.6–96.4) → 80.0% (4/5; 37.6–96.4) | unmeasured (0); na=12; full-40: unmeasured (0) | 16/210 (7.62%) | ALL: 6.47 [4.77, 8.33]; cyrillic: 4.40 [2.93, 6.17]; latin: 1.23 [0.30, 2.53]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 0.83 [0.60, 1.07] |
| intl/wikisource_ru | unreviewed | unmeasured (0); na=0; full-40: unmeasured (0) | 50/372 (13.44%) | ALL: 16.10 [12.25, 20.25]; cyrillic: 14.20 [10.90, 17.75]; greek_mono: 0.00 [0.00, 0.00]; latin: 1.20 [0.05, 3.35]; nonletter: 0.00 [0.00, 0.00]; numerics_tables: 0.70 [0.35, 1.15] |

**Government Gazette — priority modern-scanned route.** 1,171/2,232 original usable rows survive the fix gate and screen (52.5%). Held-out surviving usable accuracy is **100.0% (2/2; 34.2–100.0)**, compared with 46.2% (6/13; 23.2–70.9) originally; the all-40 diagnostic is **75.0% (3/4; 30.1–95.4)**. Crucially, the two surviving test cards are **one numeric row and one Latin row**. There are **zero surviving modern-scanned Greek test cards and zero surviving poly1900 test cards**. The 2/2 score therefore does not measure the modern Greek target. Conditional yield on the **12 modern read pages** is **29.08 [16.42, 42.58] modern-scanned rows/page**; on the **18 poly1900 read pages**, **26.28 [19.50, 32.94] poly1900 rows/page**. These conditional period rates use their own read-page denominators; the main table uses all Gazette read pages. **The 40k modern-scanned route remains unqualified:** modern target accuracy is unmeasured after screening, the all-40 surviving accuracy is below 90%, and marks remain weak (0.0% (0/1; 0.0–79.3)).

| Gazette primary class | Surviving usable letters, all 40 | Surviving usable letters, test only |
|---|---|---|
| modern_scanned | unmeasured (0) | unmeasured (0) |
| poly1900 | 0.0% (0/1; 0.0–79.3) | unmeasured (0) |
| greek_mono | 100.0% (1/1; 20.7–100.0) | unmeasured (0) |
| latin | 100.0% (1/1; 20.7–100.0) | 100.0% (1/1; 20.7–100.0) |
| numerics_tables | 100.0% (1/1; 20.7–100.0) | 100.0% (1/1; 20.7–100.0) |

## 3. Calibration and held-out screen performance

Seed **20261016**, exactly 20 calibration / 20 test cards for each of 16 sources; source-stratified only, not outcome-stratified. The split was written before feature extraction. The global threshold family contains height ratio, token vertical spread, internal x-gap, label/ink density ratio, paragraph count, and projection-peak/height conjunctions. At most three OR branches are allowed. The objective was calibration F1, with fixed tie breaks (precision, fewer calibration rejections, fewer branches); no per-source tuning or test threshold selection.

Frozen selected screen: `[{"token_y_spread_xh": 0.65}, {"projection_peaks": 1, "crop_height_xh": 2.5}]`. Every inequality is strict `>`. [Model, full candidate grid and calibration-card identities](receipts/model.json); [seeded split](receipts/split.jsonl). The screen never consumes a card ID or source identity. The numeric-date collateral guard was added after the first test readback, using a non-card witness. Thresholds were held fixed, and the original calibration feature snapshot was archived. The full pipeline therefore has a post-test assembly correction; this is not a pristine new blind validation of that final overlay.

Calibration: TP=51, FP=38, FN=12, TN=219; P=57.3%, R=81.0%. Held-out specified endpoint: **TP=40, FP=53, FN=14, TN=213; precision 43.0% (40/93; 33.4–53.2), recall 74.1% (40/54; 61.1–83.9).**

**Screen verdict: experimental, not qualified for automatic admission.** The requested-endpoint precision is low, and the screen misses roughly a quarter of the defined positives. It also removes many letters-y rows. The stored decisions make that tradeoff inspectable; they do not establish a production quality gate.

The primary positive is exactly the requested **original blind letters=n AND errors includes merged_two_lines, extra_text, or crop_overrun**. It deliberately retains duplicate-only cards even when assembly has repaired them. A secondary residual endpoint removes only cards whose base letters were repaired: P=35.5%, R=75.0% (TP/FP/FN/TN 33/60/11/216). These are different endpoints, not interchangeable scores. Some specified-endpoint false positives have blind letters=y despite `merged_two_lines` or `crop_overrun`; the physical diagnostic is reported separately in the receipt, without changing the requested positive definition.

| Source | Held-out screen TP / FP / FN / TN | Precision / recall |
|---|---|---|
| gr/anemi | 2 / 5 / 1 / 12 | 28.6% / 66.7% |
| gr/elstat | 2 / 2 / 1 / 15 | 50.0% / 66.7% |
| gr/government-gazette | 9 / 5 / 0 / 6 | 64.3% / 100.0% |
| gr/kosmopolis | 0 / 8 / 0 / 12 | 0.0% / n/a |
| gr/lekythos | 3 / 6 / 1 / 10 | 33.3% / 75.0% |
| gr/nlg-digital | 1 / 1 / 0 / 18 | 50.0% / 100.0% |
| gr/openarchives | 7 / 3 / 1 / 9 | 70.0% / 87.5% |
| gr/pergamos | 4 / 10 / 0 / 6 | 28.6% / 100.0% |
| gr/pleias | 1 / 5 / 3 / 11 | 16.7% / 25.0% |
| ia/cyrillic | 3 / 2 / 1 / 14 | 60.0% / 75.0% |
| ia/greek_latin | 0 / 1 / 1 / 18 | 0.0% / 0.0% |
| ia/poly1850 | 0 / 0 / 2 / 18 | n/a / 0.0% |
| ia/poly1900 | 1 / 2 / 1 / 16 | 33.3% / 50.0% |
| intl/bsb | 3 / 0 / 1 / 16 | 100.0% / 75.0% |
| intl/bulgarian | 4 / 3 / 1 / 12 | 57.1% / 80.0% |
| intl/serbian | 0 / 0 / 0 / 20 | n/a / n/a |

Pixel features use the exact existing F2 crop rectangle on its stored page raster: fixed dark-ink threshold `(p05+p90)/2`, capped at 200; horizontal ink projection smoothed at 0.12 x-height; peaks at ≥20% of maximum with ≥18% prominence and 0.7 x-height separation. An internal low-ink x-gap requires ≥10% of ink mass on each side. Density is visible fixed-label characters per crop ink width in x-heights divided by that page’s median. Token centers and paragraph membership come from saved Google geometry. Every F2 row has one Google line anchor, so the Google-line contributor count is one and offers no discrimination; token vertical spread still detects multi-row anchors.

## 4. Marks remain a separate requirement

The marks column above is taken verbatim from the blind marks field on surviving usable cards, with Wilson 95% intervals. Every row from a measured polytonic source below 90% carries `marks_correction_required` in [features.jsonl](features.jsonl), including its Latin/numeric by-products. Conservatively, the source tag is retained if **either** the full blind-40 marks estimate **or** the surviving-usable estimate is below 90%. In particular, ELSTAT 19/29 (65.5%) and Pergamos 11/17 (64.7%) remain tagged even when only 2/2 or 1/1 measured marks survive; this tiny selected subset does not withdraw the known weak-source evidence. This source tag is not a mark repair. A zero measurable surviving denominator is also tagged `marks_unmeasured`, not passed.

Lekythos mark-error types (card counts, not token counts) are derived only from explicit printed → Google pairs in the blind detail. Grave→acute, circumflex→acute and breathing dropped are tabulated in [lekythos_marks.json](receipts/lekythos_marks.json); these include all 40, the usable subset, and the post-screen usable subset. No error type is inferred from `marks=na`. Its large supply therefore remains conditional on mark correction whenever the measured surviving marks point estimate is below 90%.

| Lekythos mark error | All 40 cards | Originally usable | Surviving usable |
|---|---:|---:|---:|
| grave→acute | 3 | 1 | 0 |
| circumflex→acute | 2 | 1 | 1 |
| breathing dropped | 2 | 1 | 0 |
| accent dropped | 2 | 2 | 1 |
| mark plus wrong base letter | 1 | 1 | 1 |

## 5. Text-side conventions and counts

Checks ran over every line; the table counts every usable row **after steps 1–2**, before text exclusions. Original-usable branch counts are also retained in [convention_counts.jsonl](receipts/convention_counts.jsonl). Text-side exclusions are applied in `usable_final`; `fixed_label` remains the assembly output and `label_after_conventions` is the convention-normalized label.

**ſ→s:** accepted as a glyph variant. Count literal ſ in labels and exact blind-detail witnesses. BSB c008 is an additional visually inspected Fraktur witness. The total number of printed long-s lines is **not determinable** from labels already normalized to s; a zero Unicode count is not proof of zero printed ſ.

**Roman look-alikes:** deterministic table `{"Ι": "I", "Χ": "X", "Μ": "M", "Ϲ": "C", "І": "I", "Х": "X", "С": "C", "М": "M", "Ѵ": "V"}`, with Latin I,V,X,L,C,M,D unchanged. Convert only a whole letter token whose complete mapped value matches `^[IVXLCMD]+$`. No Δ→D or Λ→L guess is allowed. A single Greek/Cyrillic letter followed by a period (e.g. Χ. as a person’s initial) has ambiguous numeral intent and excludes the line instead of changing its script. Ambiguous Roman-shaped tokens containing Λ,Δ,Д,Л,П,Ӏ, or mixed Latin-Roman / Greek-Cyrillic tokens that fail the complete map, also exclude the line. This candidate grammar is explicit; general all-script capital words cannot reliably be identified as intended Roman numerals from text alone.

**Dropped line-end hyphen:** bind the nearest lower Google row in the same column (≥50% shorter-width overlap, left edges within 3 x-heights, gap ≤2 crop heights). Exclude a no-hyphen final word fragment followed by lowercase only when tail+head is attested on at least two other pages and the tail never appears as a nonfinal corpus word. This is a conservative text-only fragment test; remaining lowercase continuations are explicitly `fragment_unknown`, not silently asserted to be complete words. No ink is inspected for this check.

**Em dash→hyphen:** accepted. Exact printed em-dash substitutions are counted only where blind detail establishes them; ordinary hyphens elsewhere cannot distinguish a changed em dash from a true hyphen. Therefore whole-corpus physical substitution counts are **not determinable**. The table also gives label-hyphen candidate lines without asserting their printed glyph.

| Track/source | Usable lines checked | ſ label lines / blind witnesses / visual witnesses | Roman fixed lines (tokens) / excluded lines | Dropped-hyphen exclusions / lowercase-fragment unknown | Em-dash→hyphen blind witnesses, all→surviving / label-hyphen lines |
|---|---:|---|---|---|---|
| gr/anemi | 411 | 0 / 0 / 0→0 | 1 (1) / 14 | 3 / 145 | 1→1 / 90 |
| gr/elstat | 5590 | 0 / 0 / 0→0 | 3 (3) / 13 | 1 / 29 | 0→0 / 420 |
| gr/government-gazette | 1171 | 0 / 0 / 0→0 | 3 (3) / 39 | 7 / 240 | 0→0 / 180 |
| gr/kosmopolis | 560 | 0 / 0 / 0→0 | 0 (0) / 6 | 1 / 170 | 0→0 / 116 |
| gr/lekythos | 3282 | 0 / 0 / 0→0 | 0 (0) / 16 | 14 / 1391 | 2→1 / 842 |
| gr/nlg-digital | 847 | 0 / 0 / 0→0 | 1 (1) / 6 | 5 / 309 | 0→0 / 275 |
| gr/openarchives | 1531 | 0 / 0 / 0→0 | 5 (6) / 7 | 15 / 584 | 1→1 / 397 |
| gr/pergamos | 501 | 0 / 0 / 0→0 | 2 (2) / 13 | 6 / 224 | 3→0 / 65 |
| gr/pleias | 1772 | 0 / 0 / 0→0 | 2 (2) / 11 | 13 / 673 | 2→0 / 435 |
| ia/cyrillic | 950 | 0 / 0 / 0→0 | 3 (3) / 11 | 1 / 292 | 4→2 / 328 |
| ia/greek_latin | 2077 | 0 / 0 / 0→0 | 3 (3) / 1 | 0 / 981 | 0→0 / 394 |
| ia/poly1850 | 731 | 0 / 0 / 0→0 | 1 (1) / 3 | 1 / 308 | 0→0 / 121 |
| ia/poly1900 | 1015 | 0 / 0 / 0→0 | 9 (9) / 0 | 0 / 346 | 0→0 / 149 |
| intl/bsb | 2306 | 0 / 0 / 1→0 | 9 (10) / 9 | 3 / 655 | 0→0 / 521 |
| intl/bulgarian | 1366 | 0 / 0 / 0→0 | 7 (7) / 16 | 3 / 440 | 0→0 / 360 |
| intl/serbian | 194 | 0 / 0 / 0→0 | 0 (0) / 1 | 0 / 31 | 0→0 / 43 |
| intl/wikisource_ru | 322 | 0 / 0 / 0→0 | 1 (1) / 2 | 1 / 101 | 0→0 / 97 |

After text exclusions (pipeline counts; RU reference remains excluded from training supply):

| Source | After screen → after text checks | Additional text exclusions | Total original usable removed |
|---|---:|---:|---:|
| gr/anemi | 411→394 | 17 | 37.26% |
| gr/elstat | 5590→5576 | 14 | 3.83% |
| gr/government-gazette | 1171→1125 | 46 | 49.60% |
| gr/kosmopolis | 560→553 | 7 | 43.97% |
| gr/lekythos | 3282→3252 | 30 | 30.93% |
| gr/nlg-digital | 847→836 | 11 | 8.63% |
| gr/openarchives | 1531→1510 | 21 | 33.80% |
| gr/pergamos | 501→482 | 19 | 45.90% |
| gr/pleias | 1772→1748 | 24 | 22.21% |
| ia/cyrillic | 950→938 | 12 | 6.94% |
| ia/greek_latin | 2077→2076 | 1 | 9.50% |
| ia/poly1850 | 731→727 | 4 | 1.76% |
| ia/poly1900 | 1015→1015 | 0 | 5.32% |
| intl/bsb | 2306→2294 | 12 | 18.65% |
| intl/bulgarian | 1366→1347 | 19 | 40.05% |
| intl/serbian | 194→193 | 1 | 8.10% |
| intl/wikisource_ru | 322→319 | 3 | 14.25% |

## 6. Verdict and limits

The requested source verdict, limited to the **descriptive final surviving usable subset of all 40 supplied cards per source**, reaches a ≥90% letters-y point estimate for **anemi, elstat, kosmopolis, nlg-digital, pleias, cyrillic, bsb**. The separate held-out after-screen ≥90% list is **anemi, elstat, government-gazette, kosmopolis, nlg-digital, openarchives, pleias, cyrillic, bsb**; Gazette and OA enter that test-only list on very small surviving samples and do not reach 90% across all 40. Neither list establishes whole-source accuracy. No source has a held-out Wilson lower bound ≥90%. Repaired labels were compared with the existing printed readings, not sent for a new blind check.

All-40 letter counts (descriptive, includes the calibration cards):

| Source | Original → fixed → screen → final usable letters, all 40 (Wilson 95%) |
|---|---|
| gr/anemi | 78.6% (22/28; 60.5–89.8) → 82.1% (23/28; 64.4–92.1) → 100.0% (18/18; 82.4–100.0) → 100.0% (18/18; 82.4–100.0) |
| gr/elstat | 66.7% (2/3; 20.8–93.9) → 66.7% (2/3; 20.8–93.9) → 100.0% (2/2; 34.2–100.0) → 100.0% (2/2; 34.2–100.0) |
| gr/government-gazette | 36.0% (9/25; 20.2–55.5) → 48.0% (12/25; 30.0–66.5) → 75.0% (3/4; 30.1–95.4) → 75.0% (3/4; 30.1–95.4) |
| gr/kosmopolis | 100.0% (32/32; 89.3–100.0) → 100.0% (32/32; 89.3–100.0) → 100.0% (19/19; 83.2–100.0) → 100.0% (19/19; 83.2–100.0) |
| gr/lekythos | 73.9% (17/23; 53.5–87.5) → 78.3% (18/23; 58.1–90.3) → 85.7% (12/14; 60.1–96.0) → 85.7% (12/14; 60.1–96.0) |
| gr/nlg-digital | 92.9% (26/28; 77.4–98.0) → 92.9% (26/28; 77.4–98.0) → 96.0% (24/25; 80.5–99.3) → 96.0% (24/25; 80.5–99.3) |
| gr/openarchives | 50.0% (14/28; 32.6–67.4) → 78.6% (22/28; 60.5–89.8) → 86.7% (13/15; 62.1–96.3) → 86.7% (13/15; 62.1–96.3) |
| gr/pergamos | 36.0% (9/25; 20.2–55.5) → 36.0% (9/25; 20.2–55.5) → 37.5% (3/8; 13.7–69.4) → 42.9% (3/7; 15.8–75.0) |
| gr/pleias | 81.2% (13/16; 57.0–93.4) → 81.2% (13/16; 57.0–93.4) → 90.0% (9/10; 59.6–98.2) → 90.0% (9/10; 59.6–98.2) |
| ia/cyrillic | 84.6% (22/26; 66.5–93.8) → 84.6% (22/26; 66.5–93.8) → 100.0% (21/21; 84.5–100.0) → 100.0% (21/21; 84.5–100.0) |
| ia/greek_latin | 84.4% (27/32; 68.2–93.1) → 84.4% (27/32; 68.2–93.1) → 83.9% (26/31; 67.4–92.9) → 83.9% (26/31; 67.4–92.9) |
| ia/poly1850 | 86.7% (26/30; 70.3–94.7) → 86.7% (26/30; 70.3–94.7) → 86.7% (26/30; 70.3–94.7) → 86.7% (26/30; 70.3–94.7) |
| ia/poly1900 | 71.9% (23/32; 54.6–84.4) → 71.9% (23/32; 54.6–84.4) → 73.3% (22/30; 55.6–85.8) → 73.3% (22/30; 55.6–85.8) |
| intl/bsb | 87.9% (29/33; 72.7–95.2) → 90.9% (30/33; 76.4–96.9) → 96.8% (30/31; 83.8–99.4) → 96.8% (30/31; 83.8–99.4) |
| intl/bulgarian | 50.0% (11/22; 30.7–69.3) → 50.0% (11/22; 30.7–69.3) → 69.2% (9/13; 42.4–87.3) → 69.2% (9/13; 42.4–87.3) |
| intl/serbian | 83.3% (10/12; 55.2–95.3) → 83.3% (10/12; 55.2–95.3) → 83.3% (10/12; 55.2–95.3) → 83.3% (10/12; 55.2–95.3) |

| Source below 90%, or unmeasured (all 40) | Surviving usable letters | Residual errors on all surviving usable cards |
|---|---|---|
| gr/government-gazette | 75.0% (3/4; 30.1–95.4) | extra_text=1, missing_mark=1 |
| gr/lekythos | 85.7% (12/14; 60.1–96.0) | wrong_letter=1, wrong_mark=1, extra_text=1 |
| gr/openarchives | 86.7% (13/15; 62.1–96.3) | wrong_letter=2 |
| gr/pergamos | 42.9% (3/7; 15.8–75.0) | wrong_letter=2, hyphen=1, lookalike_script_letter=1, digits=1, missing_mark=1 |
| ia/greek_latin | 83.9% (26/31; 67.4–92.9) | wrong_letter=3, lookalike_script_letter=2, crop_overrun=2, punctuation=1 |
| ia/poly1850 | 86.7% (26/30; 70.3–94.7) | punctuation=3, lookalike_script_letter=2, crop_overrun=2, wrong_letter=1, crop_clipped=1 |
| ia/poly1900 | 73.3% (22/30; 55.6–85.8) | wrong_letter=8, crop_overrun=2, crop_clipped=1, wrong_mark=1 |
| intl/bulgarian | 69.2% (9/13; 42.4–87.3) | wrong_letter=4 |
| intl/serbian | 83.3% (10/12; 55.2–95.3) | wrong_letter=1 |

Measured polytonic sources below 90% in the full blind sample or surviving usable marks-y: **anemi, elstat, government-gazette, kosmopolis, lekythos, nlg-digital, openarchives, pergamos, pleias, greek_latin, poly1900, bsb**. All carry the requested source tag; no marks were corrected by this task.

Overall: 31,450 original pipeline-usable rows → 24,626 after fix+screen → 24,385 after text exclusions. 24,066 are candidate rows after removing reference-only RU. These remain silver candidates, not released or independently revalidated training labels. The final footer removal percentage includes text exclusions; the per-source main table isolates fix+screen removal.

Reproduce offline with the worktree’s existing Python environment (Pillow, NumPy, SciPy):

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/records/harvest/screen_v1/screen.py extract
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/records/harvest/screen_v1/screen.py calibrate
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/records/harvest/screen_v1/evaluate.py
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/records/harvest/screen_v1/validate.py
```

The manual assembly comparisons are frozen in [assembly_review.jsonl](receipts/assembly_review.jsonl). Native review panels are in [changed-card panel 1](receipts/changed_cards_01.png), [random non-cards 1](receipts/random_changed_01.png), [random non-cards 2](receipts/random_changed_02.png), and [stacked-row/date controls](receipts/negative_controls.png). The random rows expose residual provider errors and crop defects as well as resolved duplicates; they are not ten newly certified labels ([review notes](receipts/random_collateral_review.jsonl)). Source and output hashes, crop-pixel checks, outcome counts, statistical denominators, and commit status are in [receipts/](receipts/). The source-bound [guarded commit helper](commit_helper.py) is left for a writable Git index; it validates input and artifact hashes and stages only the enumerated output files.

For exact calibration replay, `screen.py calibrate` uses the archived pre-collateral-guard features and split when those receipts exist. The frozen thresholds and every card prediction are unchanged after the final assembly guard, as recorded in [post_test_collateral_guard.json](receipts/post_test_collateral_guard.json).

Footer conventions: screen P/R uses the held-out half; source letters and Gazette accuracy use the descriptive all-40 final surviving subset; marks lists sources below 90% in either their full blind marks sample or surviving usable marks subset; Gazette modern rows/page uses the modern-period denominator after fix+screen; total removal includes the text-side exclusions.

T4b: done | interleave fix: 16 cards fixed of 20, lines changed 0.811% | screen P/R test: 43.0%/74.1% | letters ≥90% after: anemi,elstat,kosmopolis,nlg-digital,pleias,cyrillic,bsb | marks <90%: anemi,elstat,government-gazette,kosmopolis,lekythos,nlg-digital,openarchives,pergamos,pleias,greek_latin,poly1900,bsb | gazette letters after: 75.0% rows/page modern 29.08 | usable rows removed: 22.46%
