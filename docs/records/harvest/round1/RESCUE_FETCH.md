# T18 — owner rescue fetch

51 explicitly rescued books; 693 planned slots. 799 PDFs fetched and gated; 672 accepted; 72 accepted replacements; 21 exhausted slots.

Fetch/gate chunks: **27.96 minutes**, 28.578 fetched pages/minute. Physical gating: 358.35 seconds. Fetch time includes the overlapping gate worker, as in T16.

Only `rescued` was fetched. `stay_out`, `pending_owner_look_1880s` and bad-scan removals were excluded. Owner rescues override the historical type decision; faint/math books remain subject to page gating and later line review. No OCR service calls were made.

The unchanged T16 acquisition loop uses seed 20261014, 8–95% positions, offsets 0–2, pilot exclusions and only physical neighbours +1/+2 (at most two replacement attempts). The frozen T13c page gate and T16 supplemental quality limits are unchanged. Gate SHA-256: `55c2efd673ce5bca8492e4f5a3fda60ec6c6f26f1def1ca3f265c4459ad8a0e1`. The relative-faintness guard remains a proxy for show-through.

Anemi HTTPS is the only permitted network origin. Credentials and cookies stay in memory. The rescue HTTP path links to the existing T16 HTTP directory, sharing its lock, transfer ledger, rate state and throttle backoff. Page receipts and SHA-bound gate results resume locally.

[Combined manifest](manifest_all.json): 1532 accepted rows (860 T16 + 672 rescue), each tagged `origin`. [Rescue manifest](rescue/manifest.json), [summary](rescue/summary.json), [allocation](rescue/selection.json), [Finder image receipts](rescue/look_manifest.json), [offline validation](rescue/validation.json), [tests](rescue/tests.xml).

The original Finder look folder/README was found in the archived pilot workspace, outside this repo. It was read only. New full-page native 200-DPI grayscale images are under `docs/records/harvest/harvest_big/round1_look/accepted/<decade>s/RESCUED_<year>_<title40>_<id6>/`; `_REPL` marks replacements. Existing folders and images are preserved.

Offline tests cover allocation, exact T16 positions/replacements, excluded owner groups, accepted-only union provenance/duplicates and Finder names. The folder-name rule was replayed against all 79 original accepted-book names. Final validation checks every fetch receipt, PDF/PNG hash, source PDF raster, gate source/quality guard, slot chain and combined row. Two native pages were visually inspected (body-text pass and four-column rejection); this does not establish the quality of every accepted page.

| Decade | Books | Planned | Fetched | Accepted | Replacements |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1860s | 3 | 48 | 48 | 48 | 0 |
| 1870s | 7 | 112 | 124 | 109 | 8 |
| 1890s | 8 | 104 | 113 | 104 | 8 |
| 1900s | 13 | 169 | 189 | 165 | 14 |
| 1910s | 8 | 104 | 132 | 98 | 17 |
| 1920s | 12 | 156 | 193 | 148 | 25 |

| Decade | Year | Book (key) | Planned | Fetched | Accepted | Replacements |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| 1860s | 1860 | Athènes moderne ___ =  Αι νέαι Αθήναι, ήτοι περιληπτική περιγραφή της πρωτευούσης της Ελλάδος, μετά των αναχωρήσεων των ατμοπλοίων, της αναλογίας των Ελληνικών προς τα ξένα νομίσματα, της αστυνομικής διατιμήσεως των αμαξών, κ.τ.λ. (`b7a2ad096ab8ab67b203d3cd`) | 16 | 16 | 16 | 0 |
| 1860s | 1868 | Αι περιπέτειαι Ιωάννου Δαβύς /  Υπό Αλεξάνδρου Δουμά εκ του Γαλλικού Εκδιδόντος Α. Βαγογιάννη. (`46241fd09ba5dae869149357`) | 16 | 16 | 16 | 0 |
| 1860s | 1860 | Εγχειρίδιον χριστιανικόν :  περιέχον σύντομον εξήγησιν του θείου ναού, της τε θείας και ιεράς λειτουργίας, και των αγίων Μυστηρίων της Εκκλησίας, ωφέλιμον εις πάντα ορθόδοξον. (`d55d101cb2fa4c91b9e11083`) | 16 | 16 | 16 | 0 |
| 1870s | 1873 | Ανθολόγιον Τεχνολογικόν :  Ή Συλλογή Παραδειγμάτων προς Τεχνολογικήν ¢σκησιν /  Υπό Μιλτιάδου Πανταζή ... (`c20219eff76f2fbc39f4c6fd`) | 16 | 18 | 14 | 0 |
| 1870s | 1877 | Ανώμαλα και ελλιπή ρήματα πεζών συγγραφέων και ποιητών της ελληνικής γλώσσης Εν οις προσετέθησαν και αι αυτών ετυμολογίαι /  υπό Α. Α. Σακελλαρίου ... (`1697d5cc21fa26717b97e073`) | 16 | 20 | 16 | 3 |
| 1870s | 1879 | Βίος και έργα Αριστοτέλους Ι. Βαλαωρίτου /  υπό Βασιλείου Γ. Βυθούκλα. (`ef44b5f8b81d770825ea1475`) | 16 | 16 | 16 | 0 |
| 1870s | 1878 | Δοκίμιον εκκλησιαστικής ιστορίας :  χάριν των περί την θεολογίαν σπουδαζόντων /  υπό Α. Διομήδους Κυριακού ... (`18ed614c7b7c25896c49680b`) | 16 | 19 | 15 | 3 |
| 1870s | 1871 | Λέων Καλλέργης :  Δράμα Διαγωνισθέν εις τον Α' ποιητ. Αγώνα των Ολυμπίων /  υπό Τιμ. Δ. Αμπελά. (`723c450ea9bb07fc4cdf47f9`) | 16 | 19 | 16 | 2 |
| 1870s | 1877 | Ολλενδόρφου μέθοδος εφηρμοσμένη εις την ιταλικήν γλώσσαν /  υπό Μ. Π. Περίδου. (`686431e9a7fe04175e6e9be9`) | 16 | 16 | 16 | 0 |
| 1870s | 1875 | Περί των τριττών ειδών της ψυχής παρά Πλάτωνι :  Εναίσιμος Διατριβή /  Χαρισίου Παπαμάρκου. (`54a124e5cac779ec617e3ace`) | 16 | 16 | 16 | 0 |
| 1890s | 1896 | Εθνικά άσματα της Ελλάδος :  1453-1821 /  Εταιρεία ο "Ελληνισμός". (`3a65f68ff36d911f4ca179e8`) | 13 | 16 | 13 | 3 |
| 1890s | 1890 | Η Εθνογραφία της Πελοποννήσου. :  Απάντησις εις τα υπό του κ. A. Philippson γραφέντα /  Υπό Χ. Π. Κορύλλου. (`99c8dbb018ec2c87af3fdce9`) | 13 | 13 | 13 | 0 |
| 1890s | 1896 | Ιερά Ιστορία της Καινής Διαθήκης :  Προς χρήσιν των Δημοτικών Σχολείων αρρένων τε και θηλέων ... /  υπό Γεωργίου Σ. Κονιδάρη ; εκδότης Γ. Π. Μέμος. (`83df10d25e7c4c1cefe2aed5`) | 13 | 13 | 13 | 0 |
| 1890s | 1899 | Κείμενον και πρακτική ερμηνεία των αναγιγνωσκομένων κατά Κυριακήν Ευαγγελίων /  υπό Ι. Ε. Μεσολωρά καθηγητού του Εθνικού Πανεπιστημίου. (`5e99df8a3f2ecb56ba5c751b`) | 13 | 13 | 13 | 0 |
| 1890s | 1892 | Νεοελληνική Κιβωτός /  Ιωακείμ Βαλαβάνη ___. (`1118b0c89e773062b4cf69f5`) | 13 | 14 | 13 | 1 |
| 1890s | 1898 | Ο αρχαϊκός πολιτισμός της νήσου Θήρας :  Ανακοίνωσις γενομένη την 30 Σεπτεμβρίου 1897 εν τη εν Δρέσδη 44 Συνελεύσει Γερμανών φιλολόγων και παιδαγωγών. /  Υπό του Βαρώνου Hiller von Gaertringen, μεταφρασθείσα υπό Ιερωνύμου Ν. Δελένδα. (`a30e828662f14c20f8994268`) | 13 | 14 | 13 | 1 |
| 1890s | 1890 | Ποιητικά Πρωτόλεια /  Όλγας Θεοδ. Ιωαννίδου. (`928e34aaaa78469aacd6c7ef`) | 13 | 13 | 13 | 0 |
| 1890s | 1899 | Χαλιμά, ήτοι, Χίλιαι και μια νύκτες :  αραβικά διηγήματα /  μετάφρασις εις την ελληνικήν υπό ****. (`10519e82bcdc24b1f02832d3`) | 13 | 17 | 13 | 3 |
| 1900s | 1903 | Ανέκδοτος συλλογή ηθών, εθίμων, δημ. ασμάτων, προλήψεων, δεισιδαιμονιών, παροιμιών, αινιγμάτων κ.τ.λ. των Καρυών (επαρχίας Καβακλή) /  Μιλτιάδου Α. Λουλουδοπούλου. (`42c339ce492d83665f00774d`) | 13 | 15 | 13 | 2 |
| 1900s | 1903 | Γενικόν Τιμολόγιον των παρ' ημίν ευρισκομένων βιβλίων. (`8e3c482e1f6c81bb67f24395`) | 13 | 14 | 12 | 1 |
| 1900s | 1902 | Εκάβη /  Ευριπίδου , Ιακώβου Χ. Δραγάτση ... (`bf2ce6d100950eec319cef00`) | 13 | 14 | 12 | 1 |
| 1900s | 1907 | Μελέτη περί δημοτικής εκπαιδεύσεως :  ήτοι τί θα εκέρδιζεν η κοινωνία εάν ήσαν καλύτερα τα δημοτικά σχολεία. /  Γεωργίου Παπασωτηρίου ... (`d9831a204aac7fccbd19bd58`) | 13 | 14 | 13 | 1 |
| 1900s | 1906 | Ο ελληνοτουρκικός πόλεμος του 1897 εν Θεσσαλία /  Μαυρικίου Γονζάγα, μετ. εκ του ιταλικού υπό Ευγενίου Ρίζου Ραγκαβή. (`18f82018e84dda79e88e0726`) | 13 | 14 | 12 | 1 |
| 1900s | 1905 | Πάρεργα φύλλα :  Από του Σαρωνικού εις τον Αμπρακικόν Η Άρτα Τα Τσουμέρκα /  Σπυρίδωνος Παγανέλη. (`8298db8c50ae1b18df756118`) | 13 | 15 | 13 | 1 |
| 1900s | 1904 | Παναγιοταφικαί εντυπώσεις /  Σεβαστιανού Νικοκάβουρα. (`6976af7d6e1671818ccf9781`) | 13 | 13 | 13 | 0 |
| 1900s | 1902 | Παναθήναια :  Κωμωδία έμμετρος εισ πράξεις τρεις /  Ανδρέου Δ. Νικολάρα. (`cc0e056392dd2ef4916b3e7d`) | 13 | 13 | 13 | 0 |
| 1900s | 1909 | Παραμύθια :  ήτοι αναγνωστικόν Βιβλίον διά το Β΄. εξάμηνον του Α΄ Σχολικού έτους και το Α΄. εξάμηνον του Β΄.Σχολικού έτους κατά τας αρχάς της Ερβαρτιανής Σχολής /  Δ. Μ. Γεωργακάκι ___ και Δ. Γ. Παυλίδου ___ (`2f9e996ffbdaaa3b4a9dfdcf`) | 13 | 18 | 13 | 3 |
| 1900s | 1903 | Περί του κανονιστικού δικαιώματος του βασιλέως και περί αναγκαστικών διαταγμάτων κατά το ημέτερον Σύνταγμα και των ξένων κρατών /  υπό Νικολάου Ν. Σαρίπολου. (`8b231047fdbd96ec30e1eded`) | 13 | 15 | 12 | 0 |
| 1900s | 1909 | Περί των ετησίως τελουμένων εν Κερκύρα Λιτανειών του θ. λειψάνου του Αγίου Σπυρίδωνος και της εν έτει 1716 πολιορκίας της Κερκύρας Ιστορική Επιτομή /  Εξ εκδεδομένων και ανεκδότων εγγράφων ερανισθείσα υπό Λαυρεντίου Σ. Βροκίνη. (`c10815de32006dc7d7354073`) | 13 | 13 | 13 | 0 |
| 1900s | 1905 | Πρόχειρον Νομικόν Εγχειρίδιον περί της εν Τουρκίας περί ακινήτων θεσμοθεσίας /  Υπό Γρηγορίου Κ. Εγγονοπούλου. (`f77a8c0084022edb7981fb15`) | 13 | 14 | 13 | 1 |
| 1900s | 1908 | Το πνεύμα του νεώτερου πολέμου :  Από Ρόσμπαχ μέχρις Ουλμ /  Στρατηγού H. Bonnal ... μεταφρασθέν υπό Ε. Μαρκουλάκη ... (`00c322b3ee04b419d1979f22`) | 13 | 17 | 13 | 3 |
| 1910s | 1911 | Εισαγωγή εις το ελληνικόν εκκλησιαστικόν δίκαιον των ορθοδόξων /  υπο Αλεξάνδρου Β. Βαμβέτσου. (`bb8faba1e9b543fe5a1ce6dd`) | 13 | 13 | 13 | 0 |
| 1910s | 1914 | Η οθωμανική Θράκη :  Μετά γεωγραφικού και ιστορικού χάρτου και καλλιτεχνικών εικόνων /  Αλεξάνδρου Δ. Βασιλοπούλου. (`97da3257b5224e86be9547da`) | 13 | 16 | 13 | 3 |
| 1910s | 1910 | Λύρα :  Ανθολογία της νεωτέρας ελληνικής ποιήσεως /  υπό Ιωάννου Πολέμη. (`6df192e72b10d13c5fc1374a`) | 13 | 14 | 12 | 1 |
| 1910s | 1913 | Ο Ελληνικός Κόσμος :  Λεύκωμα Φιλολογικόν Εικονογραφημένον του έτους 1913-1914 /  Βύρωνος Π. Ιακωβίδου. (`54d0bdd8bd3fb11df9ab0432`) | 13 | 15 | 12 | 2 |
| 1910s | 1912 | Ο κακός δρόμος :  κι άλλα καινούρια διηγήματα (1908-1911) /  Γρ. Ξενόπουλου, πρόλογ. Ιω. Ζερβού. (`55beb2ad05d46b48576a486d`) | 13 | 14 | 13 | 1 |
| 1910s | 1918 | Τα αιθέρια έλαια /  υπο Δημήτριου Ε. Τσακαλώτου. (`51026389607510af823b520a`) | 13 | 21 | 12 | 3 |
| 1910s | 1913 | Τα πολεμικά ανέκδοτα του Βασιλέως μας. (`1c3c81f346537e276486e9fd`) | 13 | 20 | 10 | 3 |
| 1910s | 1915 | Το πρόγραμμα της εξωτερικής αυτού πολιτικής :  Αγορεύσεις κατά τας συνεδριάσεις της Βουλής της 21ης, 28ης Σεπτεμβρίου και 21ης Οκτωβρίου 1915 /  Ελ. K. Βενιζέλου. (`f3cfa262eedab9cd43a9e412`) | 13 | 19 | 13 | 4 |
| 1920s | 1927 | Αντίλαλοι /  Σπήλιος Πασαγιάννης. (`d9d705c23499ff012aa70783`) | 13 | 17 | 12 | 3 |
| 1920s | 1920 | Αραβικά ιστορήματα /  Χ.Α. Νομικού. (`3a469aeb16cd49371b9dfc3d`) | 13 | 17 | 12 | 3 |
| 1920s | 1923 | Διηγήματα της στάνης /  Χ. Χριστοβασίλη. (`95a8decfdafb3b75d6549383`) | 13 | 13 | 13 | 0 |
| 1920s | 1927 | Εθνογραφικαί Σελίδες :  το Πατριαρχείον της Αλεξάνδρειας, το κλίμα και η δικαιοδοσία αυτού: Εκλιπούσαι Εκκλησίαι /  Γεωργίου Κλεάνθους Σκαλιέρη. (`3cb3c1caf7324ded3b11c1e5`) | 13 | 17 | 11 | 2 |
| 1920s | 1922 | Εισαγωγή εις την ηθικήν /  Frank Thilly___. Εξελληνισθείσα και συμπληρωθείσα υπό Γεωργίου Κ. Γρατσιάτου ___. (`8961f6bdd6daf004b4a84dfa`) | 13 | 20 | 12 | 4 |
| 1920s | 1926 | Εκλογή από το ποιητικό του έργο :  Les Syrtes, Les cantil'enes-LeP'el'erin Passion'e-Po'emes et Sylves /  Jean Mor'ean (Ι. Παπαδιαμαντόπουλος), μετάφρ. Τέλλος Αγρας. (`17499e55347a68940e18597f`) | 13 | 13 | 13 | 0 |
| 1920s | 1924 | Ελληνικά δάση και Αρκαδικοί δρυμοί /  Αναστασίου Γ. Στεφάνου. (`0907df739607faca673d2169`) | 13 | 13 | 13 | 0 |
| 1920s | 1928 | Μάρκου Τύλλιου Κικέρωνος Ο υπέρ Τίτου Αννίου Μίλωνος λόγος /  Ερμηνευθείς και μεταφρασθείς εις την νεωτέραν ελληνικήν γλώσσαν υπό Θεοφάνους Α. Κακριδή. (`2b1d2b5340150ddc135a2b1a`) | 13 | 19 | 12 | 3 |
| 1920s | 1920 | Νεοελληνικά αναγνώσματα :  Μετά προσωπογραφιών των συγγραφέων και εικόνων σχετικών προς τα κείμενα, δια τους μαθητάς της Α' τάξεως των Ελληνικών σχολείων /  Ιωάννου Πολέμη. (`161d241aad02594d3c0272e7`) | 13 | 19 | 12 | 5 |
| 1920s | 1925 | Ο έλλην ως πολεμιστής :  (Μάχη Ταμπούρ-Ογλού) /  Δημ. Σπ. Αρχιμανδρίτης. (`2d29e5e76d90adc4cc1b093a`) | 13 | 13 | 12 | 0 |
| 1920s | 1927 | Ο κιθαροθραύστης :  ήτοι βιβλίον, δι'ου αναιρείται ο,τι σατανικόν και ψυχοφθόρον θεωρείται εν τω χιλιαστικώ συγγράμματι τω ακούοντι Η "Κιθάρα του Θεού" /  υπό Δημητρίου Γ. Βασιλόπουλου. (`fdbb6015b076a41fcf67486b`) | 13 | 13 | 13 | 0 |
| 1920s | 1926 | Οικονομικαί μελέται /  Δημοσθένους Σ. Στεφανίδου. (`7cb612112b4f28a4f704a9cb`) | 13 | 19 | 13 | 5 |

Gate failures can carry multiple reasons.

| Reason | Pages |
| --- | ---: |
| bad_darkest_percentile_contrast | 1 |
| bad_faintness_proxy | 1 |
| bad_ink_fraction | 12 |
| bend_scout | 62 |
| faint_components | 13 |
| faint_or_show_through_dominated | 1 |
| more_than_two_columns | 5 |
| non_body_page | 26 |
| rotated | 4 |
| table | 18 |

Verified completion: **63 offline tests passed** (19 rescue + 44 T16). All 799 source PDF rasters and 672 Finder copies passed custody checks. All 803 run requests returned HTTP 200; the minimum observed shared request gap was 1.999815 seconds. A completed-run resume made zero new requests. The credential-pattern scan passed. Main HEAD/index/ref/reflog contents match the initial snapshot; the audit observed one change to the other R8-stack worktree index, which was preserved. T18 performs no Git mutations. [Git audit](rescue/git_audit.json), [resume check](rescue/resume_check.json), [naming replay](rescue/naming_replay.json), [native visual QA](rescue/visual_qa.json), [complete file/hash inventory](rescue/inventory.json).
