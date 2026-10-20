# SF5 — elision release rules

Policy **`sf5-release-v1`**. Saved-evidence dry run, 17 October 2026. **59/59 consensus elision atoms retained**, **2/2 doubled breathings repaired**, and both known reader errors remain wrong. The 666 mark outcomes are identical to frozen SF4 in all four modes. Effective AB labels retain **212/213** adjudicated printed apostrophes, versus **187/213** before SF5.

**All-green acceptance remains unmet:** 847 labelfix tests pass; the unchanged HTTP capture test has one environment setup error because the sandbox rejects its loopback `socket.bind` with `PermissionError: [Errno 1] Operation not permitted`. The baseline has the identical error (627 passes). No test was skipped, deselected, weakened or changed to hide it. M2 DEV elision accuracy is **UNKNOWN**, because this pool has no certified punctuation truth; its row and source census are reported explicitly.

Launch HEAD: `f4a9e48cc25601dbb002112032fc3ef5925ffc92`, branch `opus/spellcheck`. All three changed production files at launch match `c6064650` exactly. No network, detector/R1/CTC inference, training, publication, other-worktree writes or `.git` writes. Policy digest: `0f557baafd8531be83ced3613e3899aed60ef5c8b4c17b2230067412e3ef64b9`.

## Exact rule changes

1. `text.word_final_elision` recognizes the five declared aliases after a letter cluster, including its combining marks. `release_gate.release_text` preserves a word-final elision at the same letter boundary when Google and the recogniser both have it, even when the detector supplies no apostrophe. Full letter sequences must agree; a base mismatch retains the existing release HOLD. Single-source presence behavior is retained and recorded in `elision_census`.
2. `text.spacing_breathing` classifies spacing U+1FBF/U+1FBD before a capital, or word-initial before a vowel, as a breathing. The composer consumes it when attaching a combining breathing. At the Google release boundary, a duplicate recogniser prefix apostrophe is consumed in that same label edit; the punctuation guard permits exactly that substitution at the same letter. An unattached spacing mark keeps Google’s codepoint. Uncertain/held lines keep the original Google label.
3. Existing Google word-final elisions keep their original codepoint, including beside real mark edits. A pure alias difference is `status=unchanged`, `changes=[]`, `label=original`, and `alias_only=true`. The release manifest has a separate `alias_only` count, also broken down by wave/source; it is a subset of `unchanged`, never another status or a correction. The codec v2.1 U+2019 fold is left to training.

Production changes are limited to `greekocr/labelfix/text.py`, `greekocr/labelfix/release_gate.py`, and `scripts/labelfix/clariden/l1_common.py`. Observation, agreement, coverage, K1, mark naming and supported-character rules are unchanged. In particular, no rule for **ἐν→ἑν** or **διορίσῃ→διορίση** was added.

## The 56 saved-runtime witnesses

All 56 frozen SF4 labels/statuses were reproduced before applying SF5. The six L1M witnesses use the **masked** saved detector, the runtime that produced the audited wrong corrections. The seeded 50 use the supplied complete AB overlay records and their per-edit evidence. The raw gate inputs are reconstructed from saved detector fields, A predictions/coverage and B predictions/coverage; the six retain the full raw detector. No diagnostic E input was retained in these overlays, and none was invented. A new evidence envelope binds the reconstructed inputs; the original full-envelope evidence digest is not claimed as reproduced. Exact SF4 label parity and identical accepted slot records are checked for every line.

The seeded 50 contain **49 lines / 57 atoms** with Google/recogniser consensus. All survive. **44** lines become unchanged. **Four** keep their existing combining-mark edits and regain their elision; **one** keeps an existing opening-quote change and regains its elision; **one** remains corrected solely because Google has a mark the recogniser lacks (`a300f5e1c3f6a38d97201791-p000442-l0085`). That single-source deletion is intentionally unchanged. Across all 56 lines, the SF4→SF5 combining-mark outputs and every slot decision/reason/physical record are identical; the two capital witnesses lose only the duplicate spacing/prefix sign. Alias spelling beside retained real edits is restored to Google’s spelling.

Inputs and frozen outputs: [witness_inputs.jsonl.gz](SF5_evidence/witness_inputs.jsonl.gz), [source bindings and 56/56 parity](SF5_evidence/witness_inputs_receipt.json). Full labels, recogniser text, edit evidence and source census: [witness_results.jsonl.gz](SF5_evidence/witness_results.jsonl.gz). Every row below is a repository test in `tests/labelfix/test_sf5.py`.

| Line ID | Google original | SF4 label | SF5 label | Result |
| --- | --- | --- | --- | --- |
| 32aae9fec147d3b483deb96e-p000076-l0012 | νετε;», ἐνῷ «τί σκέπτεσθε;» εἶν᾿ ἡ μόνη ἐρώτηση ποὺ κάθε | νετε;», ἐνῷ «τί σκέπτεσθε;» εἶν ἡ μόνη ἐρώτηση ποὺ κάθε | νετε;», ἐνῷ «τί σκέπτεσθε;» εἶν᾿ ἡ μόνη ἐρώτηση ποὺ κάθε | 1/1 elisions kept; unchanged |
| 650670ab271096716888b108-p000033-l0054 | μιλοῦμε γι᾿ αὐτό. | μιλοῦμε γι αὐτό. | μιλοῦμε γι᾿ αὐτό. | 1/1 elisions kept; unchanged |
| 5a69150abb15eb1006f5a3ba-p000947-l0013 | Νὰ τοῦ γρικᾷ ὁ Πολύδωρος μ᾿ εἶντα καημὸ τὰ λέει, | Νὰ τοῦ γρικᾷ ὁ Πολύδωρος μ εἶντα καημὸ τὰ λέει, | Νὰ τοῦ γρικᾷ ὁ Πολύδωρος μ᾿ εἶντα καημὸ τὰ λέει, | 1/1 elisions kept; unchanged |
| a300f5e1c3f6a38d97201791-p000054-l0115 | μ'. Ὅτι οὐ χρὴ ἐχθρικῶς διακεῖσθαι πρὸς τὸν | μ. Ὅτι οὐ χρὴ ἐχθρικῶς διακεῖσθαι πρὸς τὸν | μ'. Ὅτι οὐ χρὴ ἐχθρικῶς διακεῖσθαι πρὸς τὸν | 1/1 elisions kept; unchanged |
| 650670ab271096716888b108-p000006-l0047 | ΣΤΡΑΤΙΩΤΗΣ. Ἄκου, νὰ κι ἄλλοι δυὸ σὰν κ᾿ | ΣΤΡΑΤΙΩΤΗΣ. Ἄκου, νὰ κι ἄλλοι δυὸ σὰν κ | ΣΤΡΑΤΙΩΤΗΣ. Ἄκου, νὰ κι ἄλλοι δυὸ σὰν κ᾿ | 1/1 elisions kept; unchanged |
| fdbb6015b076a41fcf67486b-p000020-l0067 | Ἀλλ᾿ ὁ ὅρος «θάνατος» σημαίνει πράγματι καταστροφὴν καὶ | Ἀλλ ὁ ὅρος «θάνατος» σημαίνει πράγματι καταστροφὴν καὶ | Ἀλλ᾿ ὁ ὅρος «θάνατος» σημαίνει πράγματι καταστροφὴν καὶ | 1/1 elisions kept; unchanged |
| 32aae9fec147d3b483deb96e-p000035-l0070 | Κ᾿ ἔτσι στὴ βιβλιοθήκη του, ὅπως μᾶς τὴν περιγράφει ὁ | Κ ἔτσι στὴ βιβλιοθήκη του, ὅπως μᾶς τὴν περιγράφει ὁ | Κ᾿ ἔτσι στὴ βιβλιοθήκη του, ὅπως μᾶς τὴν περιγράφει ὁ | 1/1 elisions kept; unchanged |
| 2c8742589d947f8d749c7ba2-p000040-l0014 | κι᾿ ὁ Ἅδης λάβα φλογερὴ ἐπάνω σου νὰ βρέχη. | κι ὁ Ἅδης λάβα φλογερὴ ἐπάνω σου νὰ βρέχη. | κι᾿ ὁ Ἅδης λάβα φλογερὴ ἐπάνω σου νὰ βρέχη. | 1/1 elisions kept; unchanged |
| 0bff55647d1c2acd1caa8bf3-p000231-l0006 | Κ᾽ εἰς μίαν ἴσως μόνην τῶν ῥανίδων του | Κ εἰς μίαν ἴσως μόνην τῶν ῥανίδων του | Κ᾽ εἰς μίαν ἴσως μόνην τῶν ῥανίδων του | 1/1 elisions kept; unchanged |
| 0b2cede5e125323a082f684b-p000015-l0028 | αἰσθήματά μου ἀφοσιώσεως δι᾽ Ὑμᾶς καὶ τὴν Πατρίδα, | αἰσθήματά μου ἀφοσιώσεως δι Ὑμᾶς καὶ τὴν Πατρίδα, | αἰσθήματά μου ἀφοσιώσεως δι᾽ Ὑμᾶς καὶ τὴν Πατρίδα, | 1/1 elisions kept; unchanged |
| d9d705c23499ff012aa70783-p000031-l0058 | Κ᾿ ἔστειλε, ὠιμέ, τὰ ξεψυχίσματά σου | Κ ἔστειλε, ὠιμέ, τὰ ξεψυχίσματά σου | Κ᾿ ἔστειλε, ὠιμέ, τὰ ξεψυχίσματά σου | 1/1 elisions kept; unchanged |
| 2c8742589d947f8d749c7ba2-p000022-l0057 | σμένον κατὰ δὲ τὸ μέγεθος καὶ τὸ περίοπτον τῆς θέσεως ἀφ᾿ ἧς ὀρθοῦται εἰς | σμένον κατὰ δὲ τὸ μέγεθος καὶ τὸ περίοπτον τῆς θέσεως ἀφ ἧς ὀρθοῦται εἰς | σμένον κατὰ δὲ τὸ μέγεθος καὶ τὸ περίοπτον τῆς θέσεως ἀφ᾿ ἧς ὀρθοῦται εἰς | 1/1 elisions kept; unchanged |
| b5f8ce187b707837e5669281-p000038-l0033 | πλασία κατ᾿ ἀριθμὸν δύναμις αὕτη μετὰ τὴν παρασχεθεῖ- | πλασία κατ ἀριθμὸν δύναμις αὕτη μετὰ τὴν παρασχεθεῖ- | πλασία κατ᾿ ἀριθμὸν δύναμις αὕτη μετὰ τὴν παρασχεθεῖ- | 1/1 elisions kept; unchanged |
| 5be5bc5b3ea6-p000001-l0002 | βουλευταὶ νὰ πληρόνωνται, ἐφ᾽ ὅσον συνεδριάζωσι, ἐκ τῶν ἰδίων | βουλευταὶ νὰ πληρόνωνται, ἐφ ὅσον συνεδριάζωσι, ἐκ τῶν ἰδίων | βουλευταὶ νὰ πληρόνωνται, ἐφ᾽ ὅσον συνεδριάζωσι, ἐκ τῶν ἰδίων | 1/1 elisions kept; unchanged |
| c57e3067ed37cedf17f285e6-p000049-l0021 | Δί᾿ οὐκ ἄσεμνος τὴν ὄψιν – ἐς τὸ βαρβαρικὸν ἤχθετο | Δί οὐκ ἄσεμνος τὴν ὄψιν – ἐς τὸ βαρβαρικὸν ἤχθετο | Δί᾿ οὐκ ἄσεμνος τὴν ὄψιν – ἐς τὸ βαρβαρικὸν ἤχθετο | 1/1 elisions kept; unchanged |
| dc390fceb64d9bb60a12d6b8-p000118-l0005 | Ἀπὸ τὰ ἄσματ᾿ ἀντηχεῖ εὐθύμως τῶν ὀργίων | Ἀπὸ τὰ ἄσματ ἀντηχεῖ εὐθύμως τῶν ὀργίων | Ἀπὸ τὰ ἄσματ᾿ ἀντηχεῖ εὐθύμως τῶν ὀργίων | 1/1 elisions kept; unchanged |
| a300f5e1c3f6a38d97201791-p000442-l0085 | Ι'. Εἰς τοὺς ἀγῶνας τοῦ ἁγίου Παύλου τοῦ | Ι. Εἰς τοὺς ἀγῶνας τοῦ ἁγίου Παύλου τοῦ | Ι. Εἰς τοὺς ἀγῶνας τοῦ ἁγίου Παύλου τοῦ | Google-only deletion retained |
| bf2ce6d100950eec319cef00-p000010-l0059 | τάσσουσιν εἶναι· θύματος δ᾽ ἐπιστάτης | τάσσουσιν εἶναι· θύματος δ ἐπιστάτης | τάσσουσιν εἶναι· θύματος δ᾽ ἐπιστάτης | 1/1 elisions kept; unchanged |
| e988c46677e75b38c15117fc-p000063-l0015 | τραγούδια ἀπ᾿ ἄκρη σ' ἄκρη | τραγούδια ἀπ’ ἄκρη σ ἄκρη | τραγούδια ἀπ᾿ ἄκρη σ' ἄκρη | 2/2 elisions kept; unchanged |
| 92ab1a099d56dc9022fc4778-p000032-l0025 | Μεγαλειότητος ὡς τέκνον Σου ἀλλ᾽ ἀξίωσόν με νὰ συναριθμηθῶ μετὰ | Μεγαλειότητος ὡς τέκνον Σου ἀλλ ἀξίωσόν με νὰ συναριθμηθῶ μετὰ | Μεγαλειότητος ὡς τέκνον Σου ἀλλ᾽ ἀξίωσόν με νὰ συναριθμηθῶ μετὰ | 1/1 elisions kept; unchanged |
| 39fbbdfd2c8030f211a318b7-p000063-l0005 | ἀνεπίδεκτα καὶ μεταβάσεως ἀφ᾽ ἑτέρου εἰσ ἕτερον, τὰ τῇ Βασιλείᾳ ἀ- | ἀνεπίδεκτα καὶ μεταβάσεως ἀφ ἑτέρου εἰσ ἕτερον, τὰ τῇ Βασιλείᾳ ἀ- | ἀνεπίδεκτα καὶ μεταβάσεως ἀφ᾽ ἑτέρου εἰσ ἕτερον, τὰ τῇ Βασιλείᾳ ἀ- | 1/1 elisions kept; unchanged |
| bb8faba1e9b543fe5a1ce6dd-p000017-l0012 | φαινομένων δι᾿ ἀνευρέσεως μεταξὺ αὐτῶν τῆς σχέσεως αἰ- | φαινομένων δι ἀνευρέσεως μεταξὺ αὐτῶν τῆς σχέσεως αἰ- | φαινομένων δι᾿ ἀνευρέσεως μεταξὺ αὐτῶν τῆς σχέσεως αἰ- | 1/1 elisions kept; unchanged |
| b5f8ce187b707837e5669281-p000038-l0060 | νος δι᾽ ἐπιθετικὴν ἐνέργειαν. Κρῆτες διετέθησαν διάφορα | νος δι ἐπιθετικὴν ἐνέργειαν. Κρῆτες διετέθησαν διάφορα | νος δι᾽ ἐπιθετικὴν ἐνέργειαν. Κρῆτες διετέθησαν διάφορα | 1/1 elisions kept; unchanged |
| d9d705c23499ff012aa70783-p000006-l0049 | Νὰ ξανασάνουν καὶ τὰ ζὰ, κ' οἱ δουλευτάδες πάλι | Νὰ ξανασάνουν καὶ τὰ ζὰ, κ οἱ δουλευτάδες πάλι | Νὰ ξανασάνουν καὶ τὰ ζὰ, κ' οἱ δουλευτάδες πάλι | 1/1 elisions kept; unchanged |
| 1092c25534f45a95669f3d2b-p000041-l0003 | θεμελιοῖ ἐπ᾿ αὐτῶν τὴν ἰδίαν διδασκαλίαν καὶ δι᾿ αὐτῶν, ὡς διὰ σα· | θεμελιοῖ ἐπ’ αὐτῶν τὴν ἰδίαν διδασκαλίαν καὶ δι αὐτῶν, ὡς διὰ σα· | θεμελιοῖ ἐπ᾿ αὐτῶν τὴν ἰδίαν διδασκαλίαν καὶ δι᾿ αὐτῶν, ὡς διὰ σα· | 2/2 elisions kept; unchanged |
| 95a8decfdafb3b75d6549383-p000031-l0010 | ὁ ἕνας μὲ τὸν ἄλλον καὶ δὲν ἤξεραν τὶ ν᾿ ἀπολογη- | ὁ ἕνας μὲ τὸν ἄλλον καὶ δὲν ἤξεραν τὶ ν ἀπολογη- | ὁ ἕνας μὲ τὸν ἄλλον καὶ δὲν ἤξεραν τὶ ν᾿ ἀπολογη- | 1/1 elisions kept; unchanged |
| 5a69150abb15eb1006f5a3ba-p000947-l0007 | Κράζει τονε καὶ σπλαχνικὰ τοῦ λέ᾿ Εἶντα λογιάζεις, | Κράζει τονε καὶ σπλαχνικὰ τοῦ λέ Εἶντα λογιάζεις, | Κράζει τονε καὶ σπλαχνικὰ τοῦ λέ᾿ Εἶντα λογιάζεις, | 1/1 elisions kept; unchanged |
| 453f156dc6352286456a08cb-p000100-l0002 | Ἀκούσατε τι γίνεται ᾿στὸν Πλάταν᾿ ἀπὸ κάτω ; | Ἀκούσατε τὶ γίνεται 'στὸν Πλάταν ἀπὸ κάτω ; | Ἀκούσατε τὶ γίνεται 'στὸν Πλάταν᾿ ἀπὸ κάτω ; | 1/1 elisions kept; corrected |
| 3ae256de8a055af974b9ec8f-p000144-l0026 | πληθυσμοῦ ἀλλ᾽ ἢ πρὸς τὸν τάφον; Τὰ δεινὰ ὅμως δὲν | πληθυσμοῦ ἀλλ ἢ πρὸς τὸν τάφον; Τὰ δεινὰ ὅμως δὲν | πληθυσμοῦ ἀλλ᾽ ἢ πρὸς τὸν τάφον; Τὰ δεινὰ ὅμως δὲν | 1/1 elisions kept; unchanged |
| d9d705c23499ff012aa70783-p000036-l0027 | Σ᾽ ἄρρωστην ὥρα δειλινὴν ἐστάθη | Σ ἄρρωστην ὥρα δειλινὴν ἐστάθη | Σ᾽ ἄρρωστην ὥρα δειλινὴν ἐστάθη | 1/1 elisions kept; unchanged |
| 143e78b5de2e6e784534ee0d-p000061-l0032 | δ᾽ οὗτος περιείχε τοὺς ἀπὸ 18-60 ἐτῶν ἡλικίας πολίτας | δ οὗτος περιεῖχε τοὺς ἀπὸ 18-60 ἐτῶν ἡλικίας πολίτας | δ᾽ οὗτος περιεῖχε τοὺς ἀπὸ 18-60 ἐτῶν ἡλικίας πολίτας | 1/1 elisions kept; corrected |
| 80f0c63471e19f7383fa6f66-p000057-l0016 | γνώμην ἔμελλον ν᾿ ἀποφανθῶ, τῇ ἀληθείᾳ θὰ ἀπέβαλλέ τι | γνώμην ἔμελλον ν ἀποφανθῶ, τῇ ἀληθείᾳ θὰ ἀπέβαλλέ τι | γνώμην ἔμελλον ν᾿ ἀποφανθῶ, τῇ ἀληθείᾳ θὰ ἀπέβαλλέ τι | 1/1 elisions kept; unchanged |
| bf2ce6d100950eec319cef00-p000028-l0081 | ΠΛΜ. κτεῖν᾽, ὡς ἐν Ἄργει φόνια λουτρὰ σ᾽ ἀμμένει. | ΠΛΜ. κτεῖν, ὡς ἐν Ἄργει φόνια λουτρὰ σ ἀμμένει. | ΠΛΜ. κτεῖν᾽, ὡς ἐν Ἄργει φόνια λουτρὰ σ᾽ ἀμμένει. | 2/2 elisions kept; unchanged |
| b518f9f9b73fe9a3257fe2f0-p000041-l0022 | ᾿ποὺ ἔμοιαζ᾽ ἐκκλησιὰ μικρὴ παληὰ χορταριασμένη, | “'ποὺ ἔμοιαζ ἐκκλησιὰ μικρὴ παληὰ χορταριασμένη, | “'ποὺ ἔμοιαζ᾽ ἐκκλησιὰ μικρὴ παληὰ χορταριασμένη, | 1/1 elisions kept; corrected |
| fdcac2103d02191960287381-p000010-l0019 | νυχτερεύοντας κ᾿ ἡ ψυχή μου | νυχτερεύοντας κ ἡ ψυχή μου | νυχτερεύοντας κ᾿ ἡ ψυχή μου | 1/1 elisions kept; unchanged |
| cc0e056392dd2ef4916b3e7d-p000095-l0027 | ποῦ αἴθριον κι᾿ ὡραῖον τὸν διατηρεῖ ! | ποῦ αἴθριον κι ὡραῖον τὸν διατηρεῖ ! | ποῦ αἴθριον κι᾿ ὡραῖον τὸν διατηρεῖ ! | 1/1 elisions kept; unchanged |
| 4c949ab8ae19e68be5a06c43-p000047-l0010 | ον καθ' ὅλου τὰ ἑξῆς. | ον καθ ὅλου τὰ ἑξῆς. | ον καθ' ὅλου τὰ ἑξῆς. | 1/1 elisions kept; unchanged |
| 42c339ce492d83665f00774d-p000049-l0055 | Δὲν ἤρταμε γιὰ φάγ' γιὰ πιεῖ(ν) μόν' ἤρταμ' γιὰ τὴν Κάλλιω. | Δὲν ἤρταμε γιὰ φάγ γιὰ πιεῖ(ν) μόν ἤρταμ γιὰ τὴν Κάλλιω. | Δὲν ἤρταμε γιὰ φάγ' γιὰ πιεῖ(ν) μόν' ἤρταμ' γιὰ τὴν Κάλλιω. | 3/3 elisions kept; unchanged |
| 043b454a8c255b6690fd3777-p000054-l0053 | σ᾿ ἀνταποκρίνεται τὸ κυπαρίσσι ...» | σ ἀνταποκρίνεται τὸ κυπαρίσσι ...» | σ᾿ ἀνταποκρίνεται τὸ κυπαρίσσι ...» | 1/1 elisions kept; unchanged |
| bf2ce6d100950eec319cef00-p000020-l0020 | τίνος γ᾽ ὑπ᾿ ἄλλου; Θρήξ νιν ὤλεσε ξένος. | τίνος γ ὑπ ἄλλου; Θρήξ νιν ὤλεσε ξένος. | τίνος γ᾽ ὑπ᾿ ἄλλου; Θρήξ νιν ὤλεσε ξένος. | 2/2 elisions kept; unchanged |
| d9d705c23499ff012aa70783-p000041-l0008 | Κι᾽ ἁρμονικὸς παλμὸς τοῦ ἐλαιῶνα | Κι ἁρμονικὸς παλμὸς τοῦ ἐλαιῶνα | Κι᾽ ἁρμονικὸς παλμὸς τοῦ ἐλαιῶνα | 1/1 elisions kept; unchanged |
| 916a006055a9d43fdaa4c41b-p000067-l0016 | δὲν ἐκφράζεται καθ' ὅλου ὁριστικῶς, καθ' ὅσον | δὲν ἐκφράζεται καθ ὅλου ὁριστικῶς, καθ ὅσον | δὲν ἐκφράζεται καθ' ὅλου ὁριστικῶς, καθ' ὅσον | 2/2 elisions kept; unchanged |
| 13dcc39a-p000003-l0088 | Γι' αὐτὸ νομίζω ὅτι πρέπει νὰ ἀναφερθεῖ: μὲ τοὺς ὅρους δο- | Γι αὐτὸ νομίζω ὅτι πρέπει νὰ ἀναφερθεῖ: μὲ τοὺς ὅρους δο- | Γι' αὐτὸ νομίζω ὅτι πρέπει νὰ ἀναφερθεῖ: μὲ τοὺς ὅρους δο- | 1/1 elisions kept; unchanged |
| c20219eff76f2fbc39f4c6fd-p000030-l0038 | φὸς ἐπιβουλεύοι' αὐτῷ. | φὸς ἐπιβουλεύοι αὐτῷ. | φὸς ἐπιβουλεύοι' αὐτῷ. | 1/1 elisions kept; unchanged |
| 137e9af6a0045d5746e26efa-p000008-l0008 | μονικῶς καὶ ἀκριβῶς τὰς ἀρχὰς καὶ τὰς αἰτίας, ὑφ᾽ ἂς | μονικῶς καὶ ἀκριβῶς τὰς ἀρχὰς καὶ τὰς αἰτίας, ὑφ ἃς | μονικῶς καὶ ἀκριβῶς τὰς ἀρχὰς καὶ τὰς αἰτίας, ὑφ᾽ ἃς | 1/1 elisions kept; corrected |
| 60b9798cc3e6f9f631070765-p000017-l0001 | Νέα μέθοδος ἀναιμάκτου θεραπείας τῶν πυωδῶν πλευριτίδων δι' αἰθέρος 15 | Νέα μέθοδος ἀναιμάκτου θεραπείας τῶν πυωδῶν πλευριτίδων δι αἰθέρος 15 | Νέα μέθοδος ἀναιμάκτου θεραπείας τῶν πυωδῶν πλευριτίδων δι' αἰθέρος 15 | 1/1 elisions kept; unchanged |
| b4bb45a610fbcbc974b0eb32-p000019-l0016 | Ἤλπιζε κ᾿ ὠνειρεύετο κ᾿ ἐκήρυττε κομπάζων. | Ἤλπιζε κ ὠνειρεύετο κ ἐκήρυττε κομπάζων. | Ἤλπιζε κ᾿ ὠνειρεύετο κ᾿ ἐκήρυττε κομπάζων. | 2/2 elisions kept; unchanged |
| 8961f6bdd6daf004b4a84dfa-p000025-l0051 | πειρίας. Ἀλλ᾿ ἐσωτερικὸν ἐλατήριον πράξεως ἓν μόνον ὑπάρχον | πειρίας. Ἀλλ ἐσωτερικὸν ἐλατήριον πράξεως ἕν μόνον ὑπάρχον | πειρίας. Ἀλλ᾿ ἐσωτερικὸν ἐλατήριον πράξεως ἕν μόνον ὑπάρχον | 1/1 elisions kept; corrected |
| bd99a3200cffaf6bf4d7c23a-p000040-l0009 | μέσ' στὸ χωριὸ τῆς Κηβισσᾶς. | μέσ στὸ χωριὸ τῆς Κηβισσᾶς. | μέσ' στὸ χωριὸ τῆς Κηβισσᾶς. | 1/1 elisions kept; unchanged |
| 6c0a582885e55adc7c535c48-p000136-l0043 | τῇ εὐχαριστίᾳ κοινωνίας, ἀλλ᾽ ἐκ τῶν κοσμητικῶν τούτων | τῇ εὐχαριστίᾳ κοινωνίας, ἀλλ ἐκ τῶν κοσμητικῶν τούτων | τῇ εὐχαριστίᾳ κοινωνίας, ἀλλ᾽ ἐκ τῶν κοσμητικῶν τούτων | 1/1 elisions kept; unchanged |
| 00c322b3ee04b419d1979f22-p000115-l0022 | ειμνήστου Γεωργίου Ζιλμπέρτ, ἐν τῇ τόσῳ σπουδαίᾳ αὐτοῦ μελέτῃ | ειμνήστου Γεωργίου Ζιλμπέρτ, ἑν τῇ τόσῳ σπουδαίᾳ αὐτοῦ μελέτῃ | ειμνήστου Γεωργίου Ζιλμπέρτ, ἑν τῇ τόσῳ σπουδαίᾳ αὐτοῦ μελέτῃ | KNOWN WRONG; unchanged |
| 399d224c580127635c47cd8d-p000019-l0010 | συνδεθῆ μ᾿ αὐτά, καθὼς καὶ πλῆθος λεπτομέρειες τῆς | συνδεθῆ μ αὐτά, καθὼς καὶ πλῆθος λεπτομέρειες τῆς | συνδεθῆ μ᾿ αὐτά, καθὼς καὶ πλῆθος λεπτομέρειες τῆς | 1/1 elisions kept; unchanged |
| 32aae9fec147d3b483deb96e-p000052-l0026 | του περνοῦσε χαϊδευτικὰ ἀπὸ πάνω τους· κ᾿ ἡ ζωὴ βλέποντας | του περνοῦσε χαϊδευτικὰ ἀπὸ πάνω τους· κ ἡ ζωὴ βλέποντας | του περνοῦσε χαϊδευτικὰ ἀπὸ πάνω τους· κ᾿ ἡ ζωὴ βλέποντας | 1/1 elisions kept; unchanged |
| 827d2345ad77e5cdec320e80-p000028-l0019 | πληρεστέραν ἀσφάλειαν νὰ διορίσῃ καὶ φύλακα τῆς ἀπο- | πληρεστέραν ἀσφάλειαν νὰ διορίση καὶ φύλακα τῆς ἀπο- | πληρεστέραν ἀσφάλειαν νὰ διορίση καὶ φύλακα τῆς ἀπο- | KNOWN WRONG; unchanged |
| a963b33d02c23d4127f5ec26-p000012-l0029 | -᾿Ανεξιχνίαστοι αἱ βουλαὶ τοῦ Ὑψίστου, κυρα- | -'Ἀνεξιχνίαστοι αἱ βουλαὶ τοῦ Ὑψίστου, κυρα- | -Ἀνεξιχνίαστοι αἱ βουλαὶ τοῦ Ὑψίστου, κυρα- | one breathing; duplicate removed |
| 32aae9fec147d3b483deb96e-p000060-l0057 | ΕΡΝΕΣΤΟΣ. -᾿Αλλά, συγγνώμην, ἀγαπητέ μου, ποὺ σὲ | ΕΡΝΕΣΤΟΣ. -'Ἀλλά, συγγνώμην, ἀγαπητέ μου, ποὺ σὲ | ΕΡΝΕΣΤΟΣ. -Ἀλλά, συγγνώμην, ἀγαπητέ μου, ποὺ σὲ | one breathing; duplicate removed |

Other Google→released changes on the six still-corrected seeded lines are retained from SF4, without new print-precision claims:

| Line ID | Other retained edit |
| --- | --- |
| a300f5e1c3f6a38d97201791-p000442-l0085 | Google-only word-final apostrophe deleted; no combining-mark edit |
| 453f156dc6352286456a08cb-p000100-l0002 | ι→ὶ; initial ᾿→ASCII apostrophe before στὸν |
| 143e78b5de2e6e784534ee0d-p000061-l0032 | ί→ῖ |
| b518f9f9b73fe9a3257fe2f0-p000041-l0022 | initial ᾿→“' before ποὺ; existing opening-quote/prefix change, no combining-mark edit |
| 137e9af6a0045d5746e26efa-p000008-l0008 | ἂ→ἃ |
| 8961f6bdd6daf004b4a84dfa-p000025-l0051 | ἓ→ἕ |

## Held-out 666 — SF4 → SF5

The existing frozen instrument scores **80 Google combining-mark errors**, **10,046 known** and **300 unknown-truth** mapped/scored slots per mode. Unknown truth is excluded from outcomes. Mark outcomes are slot based; line release additionally requires every slot and both Google edit guards to clear. The mark rows below are reproduced exactly with the same scorer. **81,700 slot/mode records are identical**, including parts, status and reasons. Every wrong/new identity and event is unchanged; there are no mark-slot changes to explain.

This remains a **saved-decision text replay**, because complete 666-line extraction coverage is unavailable locally. It retains the actual SF4 decisions and vetoes and rerenders only the two text rules. Missing coverage is never synthesized. The 56 witnesses and the 273-card DEV pool are actual saved-runtime recompositions.

| Mode | Row | Corrected /80 or elision K/D/A | Wrong | Missed | HOLD errors | New | Lines held /666 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PRESENCE | combining marks | 42 → 42 | 1 → 1 | 2 → 2 | 35 → 35 | 5 → 5 | 348 → 348 |
| PRESENCE | **elision: kept / deleted / added** | **188 / 25 / 1 → 212 / 1 / 1** | — | — | — | — | — |
| FULL | combining marks | 37 → 37 | 0 → 0 | 0 → 0 | 43 → 43 | 3 → 3 | 365 → 365 |
| FULL | **elision: kept / deleted / added** | **189 / 24 / 1 → 212 / 1 / 1** | — | — | — | — | — |
| ENSEMBLE_AB | combining marks | 45 → 45 | 2 → 2 | 6 → 6 | 27 → 27 | 6 → 6 | 274 → 274 |
| ENSEMBLE_AB | **elision: kept / deleted / added** | **187 / 26 / 1 → 212 / 1 / 1** | — | — | — | — | — |
| ENSEMBLE_AE | combining marks | 46 → 46 | 2 → 2 | 6 → 6 | 26 → 26 | 9 → 9 | 261 → 261 |
| ENSEMBLE_AE | **elision: kept / deleted / added** | **187 / 26 / 1 → 212 / 1 / 1** | — | — | — | — | — |

**Elision truth and coverage:** 213 print-positive sites and 5 explicitly absent sites on **180/666 lines**; **0 complete lines** certified. At **212/213 positive sites**, the human Wikisource emission is pixel-adjudicated by R0 and supplies the text; the remaining positive uses the literal R0 adjudication. Across all 218 scored scopes, sources are 214 pixel-supported human sites and 4 R0 fallback sites. Ten adjudicated quote sites are excluded from elision scoring, including two printed closing single quotes; one unresolved site is excluded. The five declared aliases are one presence atom. R0 also adjudicates two **word-initial** elisions (`'ς`, `'φελα`): their emitted signs count as kept, while the SF5 consensus-preservation rule remains restricted to word-final elisions.

The elision rows above score the **effective label**: original Google when held, the proposed label when released. “Deleted” means absent relative to adjudicated print, including an original omission. The residual **1** is `51fe7386-p000024-l0017`, where Google has `ἐς` at the printed `'ς`; the line remains held and unchanged. The residual **1 added** sign is already in Google at the R0 “absent” site `384c3f89-p000179-l0019`; SF5 does not introduce it. Added counts apply only to the five certified absent scopes, not all unadjudicated positions.

For visibility into held proposals, the same printed sites are also scored before line-level fallback:

| Mode | Candidate elision kept | Candidate elision deleted | Candidate elision added |
| --- | --- | --- | --- |
| PRESENCE | 171 → 211 | 42 → 2 | 0 → 0 |
| FULL | 171 → 211 | 42 → 2 | 0 → 0 |
| ENSEMBLE_AB | 171 → 211 | 42 → 2 | 0 → 0 |
| ENSEMBLE_AE | 171 → 211 | 42 → 2 | 0 → 0 |

Candidate residual omissions are the single-source `ἀλλ'` at `384c3f89-p000050-l0037` and a line with recogniser base errors (`384c3f89-p000091-l0014`). Both lines are held; their Google marks survive in the effective labels. These counts are proposal diagnostics, not released deletions.

The release source census below concerns the **608 lines with identical letter sequences**, not print truth. All **201 word-final consensus atoms** are retained after SF5. The 58 base-mismatched lines retain the existing HOLD; their 10 Google/recogniser marks are outside the aligned census. The sole aligned Google-only mark keeps the previous proposal behavior; it occurs on a held line. There are no aligned recogniser-only marks in this cohort.

| Mode | Both kept / deleted | Google-only kept / deleted | Recogniser-only kept / deleted |
| --- | --- | --- | --- |
| PRESENCE | 161 / 40 → 201 / 0 | 0 / 1 → 0 / 1 | 0 / 0 → 0 / 0 |
| FULL | 161 / 40 → 201 / 0 | 0 / 1 → 0 / 1 | 0 / 0 → 0 / 0 |
| ENSEMBLE_AB | 161 / 40 → 201 / 0 | 0 / 1 → 0 / 1 | 0 / 0 → 0 / 0 |
| ENSEMBLE_AE | 161 / 40 → 201 / 0 | 0 / 1 → 0 / 1 | 0 / 0 → 0 / 0 |

Evidence: [metrics and truth coverage](SF5_evidence/heldout/metrics.json), [per-site print outcomes](SF5_evidence/heldout/elision_events.jsonl), [all 81,700 identical slot/mode records](SF5_evidence/heldout/per_slot_proof.jsonl.gz), [before/after release labels and source census](SF5_evidence/heldout/release_labels.jsonl.gz), [source-bound receipt](SF5_evidence/heldout/receipt.json).

## M2 DEV only — SF4 → SF5

The frozen **273-card DEV allowlist** is filtered before cached runtime records are decoded. No locked stratum (ii) runtime or truth row is decoded or composed. There are **43 enumerated Google combining-mark error pairs** and **212 marks-correct reference cards**; the historical blind verdicts remain reference evidence. All paired mark outcomes, control edits, slot records and HOLDs are identical in both phases. AB/AE have no saved B/E predictions here, so their missing-evidence HOLDs remain intact.

| Mode | Row | Corrected /43 or elision K/D/A | Missed | HOLD errors | Accepted changed control slots | Lines held /273 |
| --- | --- | --- | --- | --- | --- | --- |
| PRESENCE | combining marks | 7 → 7 | 6 → 6 | 30 → 30 | 16 → 16 | 257 → 257 |
| PRESENCE | **elision: kept / deleted / added** | **UNKNOWN → UNKNOWN (0 truth sites)** | — | — | — | — |
| FULL | combining marks | 7 → 7 | 6 → 6 | 30 → 30 | 9 → 9 | 258 → 258 |
| FULL | **elision: kept / deleted / added** | **UNKNOWN → UNKNOWN (0 truth sites)** | — | — | — | — |
| ENSEMBLE_AB | combining marks | 0 → 0 | 6 → 6 | 37 → 37 | 0 → 0 | 273 → 273 |
| ENSEMBLE_AB | **elision: kept / deleted / added** | **UNKNOWN → UNKNOWN (0 truth sites)** | — | — | — | — |
| ENSEMBLE_AE | combining marks | 0 → 0 | 6 → 6 | 37 → 37 | 0 → 0 | 273 → 273 |
| ENSEMBLE_AE | **elision: kept / deleted / added** | **UNKNOWN → UNKNOWN (0 truth sites)** | — | — | — | — |

**DEV elision truth coverage is 0/273 lines and 0 positive/negative sites.** All 273 human fields are null, and no DEV line has an R0 punctuation-site adjudication. The locked (ii) truth is excluded. No zero-error or elision-accuracy claim is made. The source-agreement census can still be measured from saved text:

| Mode | Both kept / deleted | Google-only kept / deleted | Recogniser-only kept / deleted |
| --- | --- | --- | --- |
| PRESENCE | 1 / 3 → 4 / 0 | 0 / 1 → 0 / 1 | 0 / 0 → 0 / 0 |
| FULL | 1 / 3 → 4 / 0 | 0 / 1 → 0 / 1 | 0 / 0 → 0 / 0 |
| ENSEMBLE_AB | 1 / 3 → 4 / 0 | 0 / 1 → 0 / 1 | 0 / 0 → 0 / 0 |
| ENSEMBLE_AE | 1 / 3 → 4 / 0 | 0 / 1 → 0 / 1 | 0 / 0 → 0 / 0 |

This is an aligned source census on 173/273 lines, with 100 base-mismatched lines excluded from site matching. It contains four consensus sites and one Google-only site; the other Google sign is on a base-mismatched line. The held-line effective labels remain Google. [DEV metrics](SF5_evidence/m2_dev/metrics.json), [identical per-slot proof](SF5_evidence/m2_dev/per_slot_proof.jsonl.gz), [DEV allowlist, truth-coverage and input receipt](SF5_evidence/m2_dev/receipt.json).

## Alias accounting

The historical production audit identifies **431 AB**, **216 PRESENCE** and **200 FULL** alias-only corrections. Those are frozen SF4 audit counts, not a new full-production recomposition. SF5 preserves Google’s alias bytes and counts such accepted lines under `unchanged`, with a separate overlapping `alias_only` counter. The full training release was not regenerated. The 431 AB IDs remain in `SF5_witness/alias_only_ids_sf4.txt` for review.

The local 666 replay measures the resulting whole-line accounting:

| Mode | Corrected lines | Unchanged lines | Held lines | Alias-only subset of unchanged (SF5) |
| --- | --- | --- | --- | --- |
| PRESENCE | 109 → 24 | 191 → 276 | 366 → 366 | 64 |
| FULL | 98 → 15 | 186 → 269 | 382 → 382 | 62 |
| ENSEMBLE_AB | 133 → 35 | 235 → 333 | 298 → 298 | 75 |
| ENSEMBLE_AE | 136 → 38 | 240 → 338 | 290 → 290 | 76 |

M2 DEV has 0 alias-only accepted lines in each mode in both phases. The 56 elision-deletion witnesses have 0 pure alias-only lines. Synthetic release tests read back the actual manifests, source/wave buckets, overlays and paired original-label controls; status totals remain disjoint and alias counts never inflate them.

## Verification and reproduction

- New SF5 suite: **220 tests**; **213 fail on the frozen c6064650 sources** and all pass on SF5. Positive controls, the single-source residual and the two known reader errors intentionally pass on the baseline. The two text rules and alias accounting each have failing-before/passing-after witnesses. [Baseline witness log](SF5_evidence/witness_tests_before.log).
- Full labelfix suite: **847 passed, 1 environment setup error**, no assertion failures. [Full result](SF5_evidence/tests_after.log), [unchanged baseline socket error](SF5_evidence/tests_before.log). Existing tests were not edited.
- `git diff --check` passes. [Verification receipt](SF5_evidence/verification.json) checks all source/evidence hashes, frozen source identity, the production change scope and unchanged Git metadata. The report makes no full-production precision claim.

Use the requested Python with bytecode and pytest cache disabled:

```bash
export PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 GIT_OPTIONAL_LOCKS=0
PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python
$PY scripts/labelfix/sf5_measure.py prepare
$PY scripts/labelfix/sf5_measure.py witnesses
$PY scripts/labelfix/sf5_measure.py heldout
$PY scripts/labelfix/sf5_measure.py m2
SF5_TEST_BASELINE=1 $PY -m pytest tests/labelfix/test_sf5.py -q -p no:cacheprovider
$PY -m pytest tests/labelfix -q -p no:cacheprovider
$PY scripts/labelfix/sf5_report.py
$PY scripts/labelfix/sf5_verify.py
```

SF5 RESULT: policy sf5-release-v1; witnesses elision-kept 59/59, double-breathing fixed 2/2, known reader errors unchanged 2/2; held-out AB corrected 45, wrong 2, new 6, elision deleted 26→1; alias-only lines no longer counted; tests 847 passed
