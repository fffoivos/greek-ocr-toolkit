# T22 — Wave 2 Anemi round 2

**50 new books; 781 pages fetched, 613 gate accepted, 613 read; 29,943 DocAI lines, 24,430 admitted native crops.**

50 books yielded fetched pages; **49 yielded accepted/read pages**. A selected book whose sampled pages all fail the unchanged gate remains visible with zero reads in the book table; it is not silently replaced by a different book after the seeded draw.

Selection seed 20262: 6 books each in the 1860s–1900s and 1920s; 7 each in the 1910s and 1930s. All 150 round-1 books and the 57 early-print books with saved receipts are excluded. [SELECTION.md](SELECTION.md) reports the full draw, eligibility, round-1 place/publisher counts and diversity weighting.

Exactly 13 initial slots/book spread 8–95%, with seeded 0–2 offsets. Failed pages can use +1/+2 neighbours only. **Accepted-page target shortfall: 37.** 63 accepted replacements. Exhausted slots are retained in [slots.json](slots.json); no extra page search weakens the frozen gate or replacement bound.

The unchanged T16 page gate SHA `55c2efd673ce5bca8492e4f5a3fda60ec6c6f26f1def1ca3f265c4459ad8a0e1` and calibrated photometric guards were used. pypdfium2 renders source-bound single-page PDFs to 200 dpi grey PNG. Source original page/volume positions, PDF/image hashes and fetch receipts are in [manifest.json](manifest.json). Two-page spreads remain whole pages. No owner look was applied, as authorized on 15 October.

DocAI uses the pinned T19 EU binding, Greek hint, symbol option and ADC. Provider line layouts, anchored symbol mean/min confidence and inverse transforms follow T21. Source is `anemi_round2`, licence `anemi-research-internal`, batch `round2`. All T20 rules are reused byte-for-byte, including bad_page. Native bboxes and labels remain automatic OCR evidence for later owner review.

| Class | Train | Dev | Test | Total |
|---|---:|---:|---:|---:|
| greek_poly | 17869 | 617 | 3825 | 22311 |
| greek_mono | 612 | 7 | 114 | 733 |
| greek_latin_cs | 362 | 21 | 33 | 416 |
| latin | 850 | 58 | 62 | 970 |
| cyrillic | 0 | 0 | 0 | 0 |

| Rejection reason | Lines (overlapping) |
|---|---:|
| short_line | 3660 |
| low_confidence | 2005 |
| tall_box | 593 |
| symbol_heavy | 2233 |
| foreign_script | 32 |
| mixed_word | 48 |
| bad_page | 236 |
| label_in_holdout | 7 |
| crop_geometry | 0 |

Seed 20261015 freezes 8 held-out books before reads, one per decade: 6 test / 2 dev. O5 drops 7 round-2 train labels equal to **any round-1, Vouli or round-2 hold-out label**. The combined [train_pool.jsonl](train_pool.jsonl) also excludes 3 earlier train rows with matching hold-out labels. Earlier admitted artifacts remain frozen. Vouli provides 31.83% of the combined polytonic train pool (limit 40%).

Crops: unchanged spatial-neighbour >15% overlap midpoint trim, 4 px horizontal / 2 px vertical padding, native grey PNG; 10884 trimmed. Paths use the requested `<id6>/p<page6>-l<line4>.png`. 3 bad pages are excluded after the read and remain in compiled JPEGs with a red `REJECTED: bad_page` header. All 613 read pages are compiled under `<decade>s/<year>_<title40>_<id6>/pNNNN.jpg`. Five class sheets show 60 seeded unique examples per populated class, or all available when fewer than 60.

Cost: 613 unique reserved DocAI calls, **USD 0.9195** (cap USD 1.50), at the same T19 list-price estimate of USD 1.50/1,000 pages; this is not invoice readback. Ledger: `docs/records/harvest/harvest_big/round2/google/budget.jsonl`. Zero Vision calls. Reservations precede requests under SHA locks. Offline replay of every cache invoked no provider and changed no ledger hashes.

Reads began on frozen snapshots of permanently accepted slots while acquisition continued. `read_snapshots/` binds each early page/image set to the already frozen books and hold-outs. The final plan contains every earlier reserved image SHA; the final run reuses those responses. Validation checks exact equality between final unique image hashes and the one-reservation-per-image ledger.

Fetch failures: 0 page attempts; read failures: 0 lost coordinate frames, 0 empty, 0 without line layouts; 0 uncuttable crop geometries. [fetch_failures.json](fetch_failures.json) contains source-bound failed page receipts. [prefetch_transport_failures.json](prefetch_transport_failures.json) records the corrected initial pre-page login bookkeeping; those unattempted pages were returned to their original slots before resume. [transport_issues.json](transport_issues.json) records 29 unusable short or error responses, including a later viewer-only pause that resumed from its public source-bound descriptor. These interruptions are separate from page-fetch failures and successful PDF receipts.

| Cost / acquisition measure | Value |
|---|---:|
| Unique DocAI calls reserved | 613 |
| Estimated USD / cap | 0.9195 / 1.50 |
| Fetch/gate total wall minutes, including interruption/resume | 60.30 |
| Fetched pages per wall minute | 12.95 |
| Page-fetch failures | 0 |
| Unusable short / error transport responses | 29 |
| Exhausted page slots | 37 |

| Page gate flag | Pages (overlapping) |
|---|---:|
| bad_darkest_percentile_contrast | 6 |
| bad_faintness_proxy | 6 |
| bad_ink_fraction | 15 |
| bend_scout | 34 |
| faint_components | 22 |
| more_than_two_columns | 5 |
| non_body_page | 17 |
| rotated | 18 |
| table | 71 |

| Book | Year | Split | Fetched | Accepted | Read | Lines | Admitted |
|---|---:|---|---:|---:|---:|---:|---:|
| [[Περί του εν Ελλάδι αρμοδίου πολιτεύματος :  υπό φυσικήν έποψιν /  Παρά Ιωάννου Π. Πύρλα.](https://anemi.lib.uoc.gr/metadata/7/7/9/metadata-ak3kg8br7foajuepfqvd66m3d5_1314866645.tkl) (`0efd67`) | 1867 | train | 14 | 13 | 13 | 513 | 457 |
| [Ιστορία της αλώσεως του Βυζαντίου υπό των Φράγκων και της αύτοθι εξουσίας αυτών. :  1204-1261 μ. Χ. /  υπό Επαμ. Ι. Σταματιάδου, εκδίδοντος Κ. Τεφαρίκη.](https://anemi.lib.uoc.gr/metadata/0/b/0/metadata-247-0000115.tkl) (`b88422`) | 1865 | train | 13 | 13 | 13 | 456 | 401 |
| [Κατήχησις :  ή Ορθόδοξος διδασκαλία της χριστιανικής πίστεως /  Εκδοθείσα υπό Κωνσταντίνου Πρεσβυτέρου και Οικονόμου του εξ Οικονόμων.Εις χρήσιν του της Σμύρνης φιλολογικού Γυμνασίου τω 1813.](https://anemi.lib.uoc.gr/metadata/c/4/b/metadata-264-0000187.tkl) (`43de3c`) | 1868 | train | 13 | 13 | 13 | 489 | 411 |
| [Οι Έλληνες συγγραφείς εξηγημένοι εις την καθομιλουμένην γλώσσαν. /  Δαπάνη Αποστόλου Ναδίρη Βιβλιοπώλου και Εκδότου. Ισοκράτους Αρχίδαμος, Ευαγόρου Εκγώμιον[sic], Παραίνεσις προς Δημόνικον.](https://anemi.lib.uoc.gr/metadata/6/5/7/metadata-247-0000138.tkl) (`402b37`) | 1864 | test | 15 | 13 | 13 | 440 | 396 |
| [Περί της σχέσεως της αγγλικής εκκλησίας προς την ορθόδοξον. /  υπό Νικολάου Μ. Δαμαλά.](https://anemi.lib.uoc.gr/metadata/4/5/5/metadata-173-0000010.tkl) (`916a00`) | 1867 | train | 13 | 13 | 13 | 385 | 344 |
| [Φυσική Προπαιδεία :  ήτοι στοιχειώδεις και βιωφελείς γνώσεις εκ της Φυσικής, Χημείας και Γεωλογίας εις χρήσιν των διδασκομένων. /  υπό Αναστασίου Κωνσταντινίδου.](https://anemi.lib.uoc.gr/metadata/4/f/d/metadata-94-0000017.tkl) (`e85d2d`) | 1861 | train | 15 | 13 | 13 | 796 | 666 |
| [Ακολουθία βίος και πολιτεία του Νέου Ιερομάρτυρος Γρηγορίου του Πέμπτου Πατριάρχου Κωνσταντινουπόλεως απαγχονισθέντος κατά τη 10 Απριλίου 1821 ημέραν Κυριακήν του Πάσχα, υπέρ πίστεως και πατρίδος /  συνταχθείσα και πλουτισθείσα υπό εκκλησιαστικών λογίων. Εκδίδεται επιμελεία και δαπάνη Α. Σ. Αγαπητού.](https://anemi.lib.uoc.gr/metadata/6/c/a/metadata-212-0000073.tkl) (`1182f9`) | 1871 | train | 15 | 13 | 13 | 532 | 440 |
| [Δοκίμιον περί του βίου και των συγγραμμάτων Μητροφάνους του Κριτοπούλου πατριάρχου Αλεξανδρείας /  υπό Ανδρονίκου K.Δημητρακοπούλου αρχιμανδρίτου.](https://anemi.lib.uoc.gr/metadata/7/0/e/metadata-7ec714ec11d6be7319c03fa7bbf065d5_1223361549.tkl) (`34e56b`) | 1870 | dev | 14 | 13 | 13 | 421 | 366 |
| [Ιερά Κατήχησις /  Συλλεγείσα υπό Ν. Ζαννουβίου Κρητός...](https://anemi.lib.uoc.gr/metadata/2/9/a/metadata-1346223947-911557-28197.tkl) (`b19c8b`) | 1873 | train | 16 | 13 | 13 | 392 | 287 |
| [Κλείς πατρολογίας και βυζαντινών συγγραφέων :  ήτοι ευρετήριον πάντων των συγγραμμάτων των θείων ημών πατέρων, διδασκάλων και συγγραφέων των περιεχομένων εν τη εν Παρισίοις εκδοθείση πατρολογία εις τόμους εκατόν εξήκοντα και ένα (1857-1866) υπό Μιγνίου (Migne) εν η προσετέθησαν και τα συγγράμματα επτά βυζαντινών συγγραφέων εκ της Βόννη εκδόσεως, αυτών μόνον μη συμπεριλαμβανομένων εν τη του Μιγνίου έκδοσει /  Υπό Δωροθέου Σχολαρίου ___.](https://anemi.lib.uoc.gr/metadata/8/5/0/metadata-01-0001289.tkl) (`a300f5`) | 1879 | train | 14 | 13 | 13 | 1352 | 859 |
| [Ο προμαχών των Ιερέων... /  Θεοκρίτου Χ. Μυριανθούση.](https://anemi.lib.uoc.gr/metadata/6/7/c/metadata-468-0000012.tkl) (`592f08`) | 1870 | train | 14 | 13 | 13 | 487 | 401 |
| [Φιλοσοφικά και φιλολογικά /  Θ. Καΐρη, επιμ. Β.Π. Σεκοπούλλου.](https://anemi.lib.uoc.gr/metadata/d/5/b/metadata-265-0000213.tkl) (`811cf3`) | 1875 | train | 13 | 13 | 13 | 544 | 410 |
| [Βίοι επιφανών ανδρών της Αρχαίας Ελλάδος :  Προς χρήσιν των Ελληνικών Σχολείων /  Γεωργίου Τσαγρή.](https://anemi.lib.uoc.gr/metadata/9/1/5/metadata-1589780849-939972-28645.tkl) (`986661`) | 1889 | dev | 16 | 11 | 11 | 389 | 337 |
| [Διατριβαί και υπομνήματα περί Ηπείρου :  Από του έτους 1874 μέχρι του έτους 1879 /  Δημητρίου Χασιώτου.](https://anemi.lib.uoc.gr/metadata/0/f/8/metadata-438-0000053.tkl) (`68ab53`) | 1887 | train | 15 | 12 | 12 | 435 | 374 |
| [Ελλάς :  βίος των αρχαίων Ελλήνων /  κατά το γερμανικόν του Ιακώβου Φάλκε, υπό Ν. Γ. Πολίτου.](https://anemi.lib.uoc.gr/metadata/c/a/2/metadata-403-0000004.tkl) (`ee2ae8`) | 1887 | train | 14 | 13 | 13 | 502 | 464 |
| [Μ. Τ. Κικέρωνος Ο πρώτος κατά Αντωνίου :  Είτε Φιλιππικός λόγος προς χρήσιν των ανωτέρων γυμνασιακών τάξεων. /  Μετά συντομωτάτου βίου του συγγραφέως, εισαγωγής εις τους Φιλιππικούς, γενικών παρατηρήσεων εις τον α΄ Φιλιππικόν, συντόμου υποθέσεως και μεταφράσεως υπό Μάρκου Βιαγκίνη ...](https://anemi.lib.uoc.gr/metadata/6/8/f/metadata-1714456403-598544-26801.tkl) (`80f0c6`) | 1888 | train | 18 | 12 | 12 | 369 | 332 |
| [Περιληπτικόν εγχειρίδιον φυσιολογίας του ανθρώπου επί τη βάσει διαφόρων δοκίμων συγγραφέων μετά εικόνων. /  Πέτρου Β. Περίδου Διδάκτορος της Ιατρικής.](https://anemi.lib.uoc.gr/metadata/3/2/7/metadata-1523617868-98181-14547.tkl) (`6dd672`) | 1882 | train | 13 | 13 | 13 | 439 | 352 |
| [Συζύγου εκλογή και Πανεπιστήμιον ... :  Κωμωδίαι φιλοσοφικαί και αλληγορικαί /  Δ. Παπαρρηγοπούλου ; εκδοθείσαι υπό Ηλία Ωρολ. Δασσαρήτου ...](https://anemi.lib.uoc.gr/metadata/1/d/3/metadata-1365411561-83581-597.tkl) (`9dd010`) | 1884 | train | 24 | 11 | 11 | 328 | 224 |
| [Έγγραφα μεταξύ της Υψηλής Πύλης και του Οικουμενικού Πατριαρχείου αφορώντα εις την λύσιν των δύο εκκλησιαστικών ζητημάτων του τε προνομιακού και του βουλγαρικού :  (Από 22 Ιουν. 1890 μέχρι 31 Ιαν. 1891).](https://anemi.lib.uoc.gr/metadata/8/8/c/metadata-413-0000104.tkl) (`5e26b4`) | 1891 | train | 13 | 13 | 13 | 310 | 273 |
| [Έκθεσις του Διοικητικού Συμβουλίου και της Εξελεγκτικής Επιτροπής της Εταιρίας των Μεταλλουργείων Λαυρίου και των Σιδηροδρόμων Αττικής προς την Γενικήν Συνέλευσιν των μετόχων 10 Μαρτίου 1891.](https://anemi.lib.uoc.gr/metadata/3/9/0/metadata-181-0000218.tkl) (`3c4393`) | 1891 | train | 20 | 9 | 9 | 315 | 181 |
| [Ο Γιάννης /  Paul de Kock ; Μετάφρασις Κλεάνθους Τριανταφύλλου ...](https://anemi.lib.uoc.gr/metadata/d/8/e/metadata-466-0000002.tkl) (`a5d06b`) | 1896 | test | 14 | 13 | 13 | 486 | 376 |
| [Παιάνες, στόνοι, γέλωτες :  Εθνικών ποιήσεων /  Π. Σ. Συνοδινού.](https://anemi.lib.uoc.gr/metadata/6/7/e/metadata-181-0000005.tkl) (`b518f9`) | 1892 | train | 17 | 13 | 13 | 710 | 621 |
| [Τοκολόγιον :  ήτοι τοκοφόροι πίνακες απασών των ημερών του εμπορικού έτους επί ωρισμένων χρόνων, κεφαλαίων και επιτοκίων περί διαφόρων ωφελίμων πινάκων και οδηγιών /  Υπό Σεργίου Χ. Ραφτάνη ___.](https://anemi.lib.uoc.gr/metadata/6/1/9/metadata-141-0000402.tkl) (`e15043`) | 1897 | train | 37 | 0 | 0 | 0 | 0 |
| [Τράπεζα Κρήτης. Σύμβασις Καταστατικόν Νόμοι περί εκδόσεως τραπεζικών γραμματίων.](https://anemi.lib.uoc.gr/metadata/e/0/c/metadata-1534839828-314683-8774.tkl) (`827d23`) | 1899 | train | 14 | 13 | 13 | 405 | 325 |
| [Βιογραφία Κ. Κανάρη :  ης εν αρχή μεν προτάσσεται και η εικών του ήρωος εν τέλει δ'επιτάσσονται : αι περί αυτού ποίησεις των Αχιλλέως Παράσχου, Αλεξ. Βυζαντίου και Γεωργ. Μαρτινέλη.](https://anemi.lib.uoc.gr/metadata/1/1/3/metadata-1537867252-709777-30953.tkl) (`dc390f`) | 1902 | train | 16 | 13 | 13 | 324 | 282 |
| [Δικαστικοί νόμοι :  Πολιτική δικονομία μετά των σχετικών ταύτη νόμων, διαταγμάτων κλπ.](https://anemi.lib.uoc.gr/metadata/7/b/7/metadata-1621315799-838155-15667.tkl) (`6d957f`) | 1903 | train | 14 | 12 | 12 | 426 | 364 |
| [Δοκίμιον συμβολικής :  Εξ' απόψεως Ορθοδόξου /  Υπό Χρήστου Ανδρούτσου.](https://anemi.lib.uoc.gr/metadata/d/e/6/metadata-184-0000062.tkl) (`6c0a58`) | 1901 | train | 17 | 11 | 11 | 830 | 779 |
| [Παγκόσμιος γενική ιστορία :  από των αρχαιοτάτων μέχρι των καθ' ημάς χρόνων εν η εκτενέστερον εκτίθεται η ελληνική ιστορία /  υπό Αγαθοδ. Παπαγεωργοπούλου.](https://anemi.lib.uoc.gr/metadata/6/4/4/metadata-4hcvrkl9au1qs2h7jrirh1rt57_1296117312.tkl) (`385811`) | 1906 | test | 15 | 13 | 13 | 1122 | 1032 |
| [Πραγματεία περί της παρ' Έλλησι και Ρωμαίοις χρονολογίας /  υπό Ν. Δανίκα.](https://anemi.lib.uoc.gr/metadata/3/e/5/metadata-1341826889-82680-30554.tkl) (`c0b523`) | 1903 | train | 16 | 13 | 13 | 440 | 362 |
| [Ταμπουράς και κόπανος :  τραγούδια /  Αλεξ. Πάλλη.](https://anemi.lib.uoc.gr/metadata/6/7/e/metadata-416-0000013.tkl) (`bd99a3`) | 1907 | train | 14 | 13 | 13 | 484 | 390 |
| [Γνώμαι και περικοπαί /  Φριδερίκου Νίτσε ... Κατ' εκλογήν Ερρίκου Λιχτεμπερζέ Μετάφρασις Ιωάννου Σ. Ζερβού.](https://anemi.lib.uoc.gr/metadata/1/e/2/metadata-1327580535-647206-22500.tkl) (`8b1c7b`) | 1910 | train | 15 | 13 | 13 | 605 | 517 |
| [Εγχειρίδιον της Χριστιανικής Αρχαιολογίας /  υπό Γεωργίου Ι. Δέρβου __.](https://anemi.lib.uoc.gr/metadata/3/b/2/metadata-56630005568d15b086714c8b00e5dfb1_1240556464.tkl) (`7056da`) | 1913 | train | 16 | 12 | 12 | 819 | 708 |
| [Ερωτόκριτος /  Βιτζέντζου Κορνάρου, έκδοσις κριτική γενομένη επί τη βάσει των πρώτων πηγών μετ' εισαγωγής, σημειώσεων & γλωσσαρίου υπό Στεφάνου Α. Ξανθουδίδου; η επισυνάπτονται πραγματεία του καθηγητού της γλωσσολογίας Γεωργίου Ν. Χατζιδάκι περί της γλώσσης και γραμματικής του Ερωτόκριτου και οκτώ φωτοτυπικοί πίνακες εκ του χειρογράφου.](https://anemi.lib.uoc.gr/metadata/2/3/2/metadata-01-0002569.tkl) (`5a6915`) | 1915 | train | 13 | 13 | 13 | 564 | 459 |
| [Η θεατρίνα /  Γ. Β. Τσοκοπούλου.](https://anemi.lib.uoc.gr/metadata/e/b/b/metadata-cebaf0c8426d3af9cabd1235e6d2709e_1266493843.tkl) (`3598eb`) | 1912 | train | 14 | 13 | 13 | 1190 | 1052 |
| [Στοχασμοί /  Oscar Wilde, μετάφρ. Αλεξ. Γ. Μαρπουτζόγλου.](https://anemi.lib.uoc.gr/metadata/8/e/c/metadata-446-0000032.tkl) (`32aae9`) | 1915 | train | 13 | 13 | 13 | 930 | 858 |
| [Τα ποιήματα /  Κώστα Κρυστάλλη, μετά προλόγου υπό Ι. Ζερβού.](https://anemi.lib.uoc.gr/metadata/7/c/b/metadata-453-0000001.tkl) (`cbdbe3`) | 1916 | test | 13 | 13 | 13 | 1163 | 854 |
| [Του οσίου πατρός ημών Αββά Ησαΐου Λόγοι ΚΘ΄...](https://anemi.lib.uoc.gr/metadata/a/7/2/metadata-448-0000003.tkl) (`adc48c`) | 1911 | train | 13 | 13 | 13 | 447 | 386 |
| [Διάττοντες /  Εμμανουήλ Στυλιανού Λυκούδη, ; προοίμιον Δ. Γρ. Καμπούρογλου.](https://anemi.lib.uoc.gr/metadata/d/4/d/metadata-069fd9b1f45820a6031053a1ada21307_1268313201.tkl) (`399d22`) | 1929 | train | 14 | 13 | 13 | 735 | 671 |
| [Διαλέξεις /  Βλασ. Γαβριηλίδου.](https://anemi.lib.uoc.gr/metadata/a/e/a/metadata-u8tqkv4hba1klhmif81f0t75l2_1300777707.tkl) (`c569ee`) | 1921 | train | 13 | 12 | 12 | 847 | 570 |
| [Διαλεχτές ιστορίες / :  Διηγήματα /  Γρ. Ξενοπούλου, Αιμιλίας Δάφνη, Στ. Δάφνη, Δ. Βουτυρά, Ναπ. Λαπαθιώτη [κ.ά].](https://anemi.lib.uoc.gr/metadata/a/c/c/metadata-1402978819-146843-13640.tkl) (`a963b3`) | 1926 | train | 14 | 13 | 13 | 400 | 349 |
| [Εκ βαθέων /  έγραψε Μ. Τσιριμώκος.](https://anemi.lib.uoc.gr/metadata/c/5/2/metadata-1532089743-248659-13308.tkl) (`a0b5d8`) | 1927 | train | 13 | 13 | 13 | 210 | 168 |
| [Ελληνικό σχέδιο Kοινωνίας Εθνών :  Διεθνικού θεσμού ικανού δίχως βία και στρατό να απονέμει το δίκαιο και να διατηρεί την ειρήνη /  Κ. Φ.](https://anemi.lib.uoc.gr/metadata/6/e/4/metadata-443-0000012.tkl) (`0807bc`) | 1928 | test | 13 | 13 | 13 | 962 | 882 |
| [Τα τελευταία άρθρα του Βλάσιου Γαβριηλίδου /  με πρόλογον του κ. Εμμ. Ρέπουλη.](https://anemi.lib.uoc.gr/metadata/5/7/b/metadata-362ecb2a177c94b0ab44442fc85b203f_1287568090.tkl) (`6a7f05`) | 1920 | train | 13 | 13 | 13 | 1026 | 604 |
| [Α. Παπαδιαμάντη Γράμματα /  Με πρόλογο και σημειώσεις Octave Merlier.](https://anemi.lib.uoc.gr/metadata/f/0/f/metadata-1dfc629f32ab0f595f17e2cac84cd299_1240473576.tkl) (`066ab2`) | 1934 | test | 13 | 13 | 13 | 641 | 494 |
| [Αλφαβητάρι :  τα παιδάκια /  Δ. Δεληπέτρου, Δ. Δούκα, Ρ. Ιμβριώτη ; ζωγραφίες : Γιάννη Κεφαλληνού.](https://anemi.lib.uoc.gr/metadata/a/5/0/metadata-1401435205-188081-30070.tkl) (`395473`) | 1932 | train | 20 | 10 | 10 | 206 | 93 |
| [Βρύλλειον-Τρίγλεια :  Ιστορική και γεωγραφική μελέτη από του Ε' αιώνος π.Χ. μέχρι των καθ' ημάς /  Τρύφωνος Ε. Ευαγγελίδου.](https://anemi.lib.uoc.gr/metadata/d/0/6/metadata-1501223664-862216-15366.tkl) (`39fbbd`) | 1934 | train | 13 | 12 | 12 | 440 | 395 |
| [Η Βενετοκρατούμενη Ανατολή, Κρήτη και Επτάνησος /  [υπό] Αγαθαγγέλου Ξηρουχάκη ; μετά προλόγου υπό Γ. Ν. Χατζιδάκι και κριτικού σημειώματς υπό Ν. Βέη.](https://anemi.lib.uoc.gr/metadata/7/6/8/metadata-a1dbced599b67edc173c57950376808a_1240993018.tkl) (`b3c6af`) | 1934 | train | 15 | 13 | 13 | 1157 | 908 |
| [Η χλωρίς της Μάνης :  Μελέτη βραβευθείσα υπό της Ακαδημίας Αθηνών /  Δημ. Ν. Ζαγανιάρη.](https://anemi.lib.uoc.gr/metadata/c/d/7/metadata-1651834577-454286-23879.tkl) (`f3d08a`) | 1934 | train | 28 | 9 | 9 | 603 | 305 |
| [Λεύκωμα Θράκης - Μακεδονίας.](https://anemi.lib.uoc.gr/metadata/3/3/5/metadata-af340222a27b394b4ad81dc14cedc1a1_1218179594.tkl) (`290a13`) | 1932 | train | 20 | 13 | 13 | 1295 | 1168 |
| [Οι νεκροί των εθνικών αγώνων μας :  Ο επίσημος πίναξ των ονομάτων των φονευθέντων κατά τους εθνικούς αγώνας από της ανεξαρτησίας της Ελλάδος μέχρι του 1922.](https://anemi.lib.uoc.gr/metadata/5/e/9/metadata-a4d97c8bdcc87d2efe5dbed8cb8ce298_1271143020.tkl) (`c3468c`) | 1932 | train | 19 | 12 | 12 | 582 | 483 |

Sample visual QA found retained crop defects despite exact T20 geometry/pixel parity. `80f0c63471e19f7383fa6f66-p000006-l0030` (confidence 0.898548304) is trimmed to an upper slice of its printed row; `a5d06b8220b096b83beccb73-p000291-l0024` retains preceding-row ink and clips the target row. Both remain admitted under the explicitly unchanged T20 rules. [visual_qa.json](visual_qa.json) links native crops and source-context images. The four populated class sheets were sampled at three examples each; all three bad-page rejection headings were visually checked in the final JPEGs. Extraction fidelity does not establish glyph ownership or human transcription accuracy; owner accuracy review remains pending.

**214 offline tests passed.** Full admission decisions, native pixels, compiled rasters, selection exclusions, quotas and at-most-once replay are checked in [validation.json](validation.json). [tests](tests.xml), [summary](admission_summary.json), [hold-outs](holdout_books.json), [inventory](inventory.json).

T22: done | books: 50 | pages: 781/613/613 | lines: 29943 | admitted: 24430 | poly: 22311 | train: 19693 | dev: 703 | test: 4034 | usd: 0.92 | tests: 214 passed
