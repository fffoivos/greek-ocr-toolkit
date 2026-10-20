# CN1 — combined system versus S6 on the owner’s notes

Completed offline on `opus/spellcheck`, HEAD `5c71629e175612b199ecd59ea47783b7d4e0e633`, on 2026-10-17 (Europe/Athens). Measurement only: no reader/policy/model changes, `.git` writes, publishing, network use, recognition/R1 forward passes, or training. Both final page builds ran with socket-connect and recognizer-construction guards; neither guard was triggered. The required SF1 detector/shape/case reading path ran on the Mac CPU with cached alignments and saved R1-A predictions.

**Combined does not establish an unheld naming improvement on this instrument.** It has one unheld naming regression. Its one unheld recovered-note line improves two old records, and that recovery is already present in the SF1 detector-only control. HOLD outputs are deferred outcomes, never counted as fixed or wrong.

## Complete-note outcomes

`F / H / U` means fixed / HOLD / unmet. “Unmet” includes unresolved wording or missing targets; it does not by itself prove a pixel-reading error. A complete note is fixed only when every original strict clause passes and no addressed mark output is held. An independent unmet clause keeps a note unmet even if another clause is held. The raw strict column evaluates the unchanged Boolean predicates before this HOLD gate; it is diagnostic and must not be presented as accepted fixes. Old59 retains its 59 slot-record units, rather than deduplicating their shared note lines.

| instrument | combined F / H / U | S6 F / H / U | raw strict combined vs S6 |
|---|---:|---:|---:|
| review_v16 (49) | 26 / 12 / 11 | 35 / 0 / 14 | 32/49 vs 35/49 |
| examples_v10 (57) | 25 / 17 / 15 | 33 / 0 / 24 | 34/57 vs 33/57 |
| old59 (59) | 45 / 8 / 6 | 45 / 0 / 14 | 49/59 vs 45/59 |
| old33 (33) | 18 / 6 / 9 | 17 / 0 / 16 | 21/33 vs 17/33 |
| old56 (56) | 23 / 16 / 17 | 26 / 0 / 30 | 27/56 vs 26/56 |

The hash-bound SF1 detector-only control includes the same print-preserving K1 policy as combined. This separates the one detector recovery and K1 abstentions from R1 naming:

| set | SF1 detector control F/H/U | combined F/H/U | raw strict control vs combined |
|---|---:|---:|---:|
| review_v16 | 27/8/14 | 26/12/11 | 35/49 vs 32/49 |
| examples_v10 | 31/4/22 | 25/17/15 | 33/57 vs 34/57 |
| old59 | 46/2/11 | 45/8/6 | 46/59 vs 49/59 |
| old33 | 18/1/14 | 18/6/9 | 18/33 vs 21/33 |
| old56 | 25/4/27 | 23/16/17 | 26/56 vs 27/56 |

There is **1 combined-worse note record (1 unique line), 2 combined-better records (1 unique line), and 20 S6-fixed → combined-HOLD records**. Excluding the HOLD gate yields 6 worse / 13 better raw-predicate records; these include held displayed names and are not equivalent to accepted corrections.

## Clause split

Each cell is **combined fixed/HOLD/unmet vs S6 fixed/HOLD/unmet, of n clauses**. Facets overlap: an old exact mark clause has a naming facet and a separate S6 physical-evidence facet; a union can test both segmentation and letter identity; an empty-note guard tests both name preservation and physical preservation. Counts are instrument evidence, not new independent print adjudication. Physical facets use the actual detector control evidence, so changing a held displayed name cannot fabricate a recovered blob. Naming keeps strict exact counts and Counter equality where the old instrument requires them.

| set | physical presence | naming | segmentation | punctuation / apostrophe / quote | letter identity |
|---|---|---|---|---|---|
| review_v16 | 43/0/13 vs 43/0/13 (56) | 3/3/3 vs 6/0/3 (9) | 14/0/0 vs 14/0/0 (14) | 1/0/1 vs 1/0/1 (2) | 3/0/0 vs 3/0/0 (3) |
| examples_v10 | 57/0/19 vs 57/0/19 (76) | 1/1/2 vs 2/0/2 (4) | 5/0/0 vs 5/0/0 (5) | 11/0/4 vs 11/0/4 (15) | 4/0/0 vs 4/0/0 (4) |
| old59 | 38/0/12 vs 37/0/13 (50) | 26/6/6 vs 26/0/12 (38) | 0/0/0 vs 0/0/0 (0) | 9/0/0 vs 9/0/0 (9) | 0/0/0 vs 0/0/0 (0) |
| old33 | 38/0/15 vs 37/0/16 (53) | 26/7/7 vs 26/0/14 (40) | 0/0/0 vs 0/0/0 (0) | 7/0/0 vs 7/0/0 (7) | 0/0/0 vs 0/0/0 (0) |
| old56 | 56/0/19 vs 56/0/19 (75) | 44/16/11 vs 47/0/24 (71) | 4/0/0 vs 4/0/0 (4) | 11/0/4 vs 11/0/4 (15) | 4/0/0 vs 4/0/0 (4) |

The current review’s 14 segmentation clauses pass in both systems. The current examples’ five structural segmentation clauses and two base-only letter clauses also pass in both. Current punctuation is unchanged: review 1/2, examples 11/15. There is no letter-identity change: every serialized base, start, component ID and character box matches the detector control.

The mixed complete-note guards (reported separately rather than hidden among physical clauses) are:

| set | combined F/H/U | S6 F/H/U | unresolved owner-uncertainty clauses in both |
|---|---:|---:|---:|
| review_v16 | 3/2/4 | 6/0/3 | 2 |
| examples_v10 | 1/0/2 | 1/0/2 | 1 |
| old59 | 0/0/0 | 0/0/0 | 0 |
| old33 | 0/0/1 | 0/0/1 | 0 |
| old56 | 1/0/2 | 1/0/2 | 2 |

## HOLD outcomes

**87 unique character slots on 53 of the 92 owner lines are HOLD**: 80 mark-kind disagreements and 9 K1 print-preserving flags, with 2 slots in both groups. All 87 slot records, displayed and frozen slot IDs, raw detector parts, displayed combined parts, reasons and K1 receipts are in `CN1_checks.jsonl` (`type=hold_slot`). All printed parts are retained; there are zero constraint deletions. The same slot can appear in multiple note sets.

| set | HOLD slots anywhere on its lines | distinct HOLD slots addressed by its clauses | notes deferred entirely to HOLD |
|---|---:|---:|---:|
| review_v16 | 50 | 21 | 12 |
| examples_v10 | 51 | 27 | 17 |
| old59 | 33 | 8 | 8 |
| old33 | 35 | 10 | 6 |
| old56 | 50 | 27 | 16 |

## Every changed note outcome

One line per note record in the union of (a) raw strict success flips, (b) fixed ↔ unmet outcomes, and (c) S6-fixed → combined-HOLD outcomes. Repeated lines across instruments and repeated old59 slot records remain separate. The clause field identifies every changed clause; the cause distinguishes abstention from an unheld regression.

| note set / line / note | changed clause(s), S6 → combined (raw predicate) | S6 reading | combined reading | cause |
|---|---|---|---|---|
| review_v16 #11 / `2793d64c-p000070-l0014` / [empty, explicitly reviewed] | no_regression [] None: fixed → HOLD (raw True → False) | ηχὼ στενάξασᾶ θρηνῳδός, | ἦχὼ στενάξασα θρηνῳδός, | start 0: none → psili+circumflex; start 15: circumflex → none; addressed output is HOLD, so no fixed/error award for those slots. |
| review_v16 #16 / `384c3f89-p000053-l0021` / [empty, explicitly reviewed] | no_regression [] None: fixed → fail (raw True → False) | ἀμπλακίην ἄμφω· στυγερὸν δ’ ἄχος εἷλεν ἰδόντας | ἀμπλακίην ἄμφω· στυγερὸν δ’ ἄχος εἶλεν ἰδόντας | Unheld R1 names agree on breathing+accent kinds but change dasia+circumflex to psili+circumflex at start 41 / frozen slot 28; frozen truth and owner-approved S4/S6 require dasia. |
| review_v16 #17 / `384c3f89-p000053-l0028` / missed at 32 | mark [32] 1: fixed → HOLD (raw True → True) | ἣ θέμις, άμ πεδίον λειμώνιον, ἔνθ’ ἔτι νὓν περ | ἣ θέμις, ἂμ πεδίον λειμώνιον, ἔνθ’ ἔτι νῦν περ | start 51: dasia+grave → circumflex; addressed output is HOLD, so no fixed/error award for those slots. |
| review_v16 #20 / `384c3f89-p000091-l0011` / fused letters at 3 and missed accent | mark [3] 1: fixed → HOLD (raw True → True) | τὣ νὓν ἥντιν ἐγὼ τῖσαι χάριν ἄρκιός εἰμι, | τῶ νῦν ἥντιν ἐγὼ τῖσαι χάριν ἄρκιός εἰμι, | start 5: dasia+grave → circumflex; addressed output is HOLD, so no fixed/error award for those slots. |
| review_v16 #29 / `51fe7386-p000024-l0015` / [empty, explicitly reviewed] | no_regression [] None: fixed → HOLD (raw True → False) | Ὁ Ὄλυμπος ὲκύτταξε τὴν ὤμορφη τἡν Ὄσσα, | Ὁ Ὄλυμπος ἐκύτταξε τὴν ὤμορφη τὴν Ὄσσα, | start 13: grave → psili; start 39: dasia → grave; addressed output is HOLD, so no fixed/error award for those slots. |
| review_v16 #45 / `9c1dca9b-p000015-l0051` / fused letters at 3 and accent / missed at 26 | mark [3] 1: fixed → HOLD (raw True → True) | Κυθἤροις διαμένων κ. Ἑμμανουὴλ Μόρμορης. | Κυθήροις διαμένων κ. Ἐμμανουὴλ Μόρμορης. | start 3: psili+acute → acute; addressed output is HOLD, so no fixed/error award for those slots. |
| review_v16 #46 / `9c1dca9b-p000015-l0057` / 3 fused letters at 12 and missed accent | mark [12] 1: fixed → HOLD (raw True → True) | καὶ καλὸς ξεφαντωτἡς. | καὶ καλὸς ξεφαντωτής. | start 20: dasia → acute; addressed output is HOLD, so no fixed/error award for those slots. |
| review_v16 #47 / `9c1dca9b-p000015-l0060` / 3 fused letters at 7 and missed accent / missed at 15 | mark [15] 1: fixed → HOLD (raw True → True) | Στοὺς σαράντ’ ἁνθεῖ καἰ δένει | Στοὺς σαράντ’ ἀνθεῖ καὶ δένει | start 26: psili → grave; addressed output is HOLD, so no fixed/error award for those slots. |
| review_v16 #49 / `9c1dca9b-p000015-l0067` / missed at 2 | mark [2] 1: fixed → HOLD (raw True → True) | μὁνο τὰ ψωμιὰ χαλᾷ. | μόνο τὰ ψωμιὰ χαλᾷ. | start 1: dasia → acute; addressed output is HOLD, so no fixed/error award for those slots. |
| examples_v10 #11 / `384c3f89-p000030-l0029` / missed ellipsis or quote at 1 /  / why the questionamrk at 23?  | named [23] None: fixed → HOLD (raw True → True) | “Εἰ μὲν δή μοι κὓδος ἐπιτρωπἁτε μέλεσθαι, |  Εἰ μὲν δή μοι κῦδος ἐπιτρωπᾶτε μέλεσθαι, | start 33: dasia → circumflex; addressed output is HOLD, so no fixed/error award for those slots. |
| examples_v10 #17 / `384c3f89-p000091-l0014` / missed all accents except 1 | whole_marks [] None: fail → HOLD (raw False → True) | αννδρασι, εὖτ αρξωσινν αρειονες αλλοι οελλειν. | ἀννδράσι, εὖτ ἄρξωσινν ἀρείονες ἄλλοι ὀέλλειν. | start 0: none → psili; start 6: none → acute; start 18: none → psili+acute; start 29: none → psili; start 33: none → acute; start 40: none → psili+acute; start 48: none → psili; start 50: none → acute; addressed output is HOLD, so no fixed/error award for those slots. The raw whole_marks predicate reads zones from displayed names; its apparent gain has no detector box gain. |
| examples_v10 #18 / `384c3f89-p000091-l0027` / missed 2 accents at 1, and classified eta as 1-2 | mark [1] 2: fixed → HOLD (raw True → True) | ῆρί γε μὴν ἐπὶ νῆα κατήισαν ἐγκονέοντες· | ἦρί γε μὴν ἐπὶ νῆα κατήισαν ἐγκονέοντες· | start 0: circumflex → psili+circumflex; addressed output is HOLD, so no fixed/error award for those slots. |
| examples_v10 #20 / `384c3f89-p000096-l0004` / missed second aaccent at 15 | mark [15] 2: fixed → HOLD (raw True → True) | δωσέμεναι, ὅ κεν ᾗσι μετὰ φρεσὶν ἰθύσειεν. | δωσέμεναι, ὅ κεν ἧσι μετὰ φρεσὶν ἰθύσειεν. | start 20: dasia+circumflex+subscript → dasia+circumflex; addressed output is HOLD, so no fixed/error award for those slots. |
| examples_v10 #29 / `384c3f89-p000183-l0009` / missed second accent at 9 | mark [9] 2: fixed → HOLD (raw True → True) | ῥόχθεον, ᾓχι πάροιθεν ἀπέπτυεν αἰθομένη φλὸξ | ῥόχθεον, ἧχι πάροιθεν ἀπέπτυεν αἰθομένη φλὸξ | start 11: dasia+grave+subscript → dasia+circumflex; addressed output is HOLD, so no fixed/error award for those slots. |
| examples_v10 #35 / `602cc72e-p000113-l0009` / missed at 1, 9, 10, 12 | mark [1] 1: fixed → HOLD (raw True → True) | *Αρκτος καὶ ἁλώπηξ. | *Ἄρκτος καὶ ἁλώπηξ. | start 1: none → psili+acute; addressed output is HOLD, so no fixed/error award for those slots. |
| examples_v10 #36 / `602cc72e-p000167-l0027` / missed at 6, 10 , 14 | mark [14] 1: fixed → HOLD (raw True → True) | Ηρακλῆς καὶ Πλοῦτος. | Ἡρακλῆς καὶ Πλουτος. | start 18: circumflex → none; addressed output is HOLD, so no fixed/error award for those slots. |
| examples_v10 #37 / `602cc72e-p000353-l0006` / missed at 6, 10, 14 | mark [14] 1: fixed → HOLD (raw True → True) | Χελιδὼν καὶ κορωνη | Χελιδὼν καὶ κορώνη | start 17: none → acute; addressed output is HOLD, so no fixed/error award for those slots. |
| examples_v10 #43 / `8b6b0de9-p000008-l0001` / missed at 7, 12 | mark [12] 1: fixed → HOLD (raw True → True) | Καὶ εἰς τὸν ᾷδην μετὰ σοῦ, | « Καὶ εἰς τὸν ᾅδην μετὰ σοῦ, | start 17: circumflex+subscript → dasia+acute+subscript; addressed output is HOLD, so no fixed/error award for those slots. |
| old33 #9 / `2793d64c-p000070-l0014` / random marks under 10 and 13, and over 12 | no_top [12] 1: fail → HOLD (raw False → True) | ηχὼ στενάξασᾶ θρηνῳδός, | ἦχὼ στενάξασα θρηνῳδός, | start 15: circumflex → none; addressed output is HOLD, so no fixed/error award for those slots. |
| old33 #18 / `384c3f89-p000205-l0005` / 2 accent of 1 missed, 1 ellipsis at 2 and 7 respectively | mark [1] 2: fail → HOLD (raw False → True) | Ἠ ῥ’, ἅμα δ’ εὐχωλῆσιν ἐς ὕδατα λαιμοτομήσας | Ἦ ῥ’, ἅμα δ’ εὐχωλῇσιν ἐς ὕδατα λαιμοτομήσας | start 0: psili → psili+circumflex; addressed output is HOLD, so no fixed/error award for those slots. |
| old33 #20 / `51fe7386-p000024-l0020` / missed at 6, 8, 11, 20, 37, 39 ... and also part of 23 detected as subscript | mark [11] 1: fail → fixed (raw False → True) | Καὶ δὲν ἐπερασε καιρὸς, χρόνοι πολλοὶ καὶ μῆνες | Καὶ δὲν ἐπέρασε καιρὸς, χρόνοι πολλοὶ καὶ μῆνες | SF1 detector recovers source 5 above ε at start 13 / frozen slot 11; also present without R1. Detector drift, not an R1 naming gain. |
| old33 #21 / `602cc72e-p000155-l0009` / missed two at 2, and one at 11, 12, and 16 | mark [12] 1: fail → HOLD (raw False → True) | Εὔνουχος καὶ ἵερεύς. | Εὔνουχος καὶ ἱερεύς. | start 15: dasia+acute → dasia; addressed output is HOLD, so no fixed/error award for those slots. |
| old56 #4 / `02a3a2a6-p000318-l0014` / missed at 1, 17 | mark [1] 1: fail → HOLD (raw False → True) | ει Ορίστε; Τόσο φειδωλοὶ | ει Ὁρίστε; Τόσο φειδωλοὶ | start 3: none → dasia; addressed output is HOLD, so no fixed/error award for those slots. |
| old56 #6 / `177b717d-p000017-l0012` / missed at 11, 12 | mark [12] 1: fail → HOLD (raw False → True) | Ταράζει καὶ ἡ ανάσα σου τὰ μαῦρα τῆς Στυγὸς | Ταράζει καὶ ἡ ἀνάσα σου τὰ μαῦρα τῆς Στυγὸς | start 17: none → psili; addressed output is HOLD, so no fixed/error award for those slots. |
| old56 #11 / `384c3f89-p000030-l0029` / missed ellipsis or quote at 1 /  / why the questionamrk at 23? | named [23] None: fixed → HOLD (raw True → True) | “Εἰ μὲν δή μοι κὓδος ἐπιτρωπἁτε μέλεσθαι, |  Εἰ μὲν δή μοι κῦδος ἐπιτρωπᾶτε μέλεσθαι, | start 33: dasia → circumflex; addressed output is HOLD, so no fixed/error award for those slots. |
| old56 #17 / `384c3f89-p000091-l0014` / missed all accents except 1 | whole_marks [] None: fail → HOLD (raw False → True) | αννδρασι, εὖτ αρξωσινν αρειονες αλλοι οελλειν. | ἀννδράσι, εὖτ ἄρξωσινν ἀρείονες ἄλλοι ὀέλλειν. | start 0: none → psili; start 6: none → acute; start 18: none → psili+acute; start 29: none → psili; start 33: none → acute; start 40: none → psili+acute; start 48: none → psili; start 50: none → acute; addressed output is HOLD, so no fixed/error award for those slots. |
| old56 #35 / `602cc72e-p000113-l0009` / missed at 1, 9, 10, 12 | mark [1] 1: fixed → HOLD (raw True → False) | *Αρκτος καὶ ἁλώπηξ. | *Ἄρκτος καὶ ἁλώπηξ. | start 1: none → psili+acute; addressed output is HOLD, so no fixed/error award for those slots. |
| old56 #36 / `602cc72e-p000167-l0027` / missed at 6, 10 , 14 | mark [14] 1: fixed → HOLD (raw True → False) | Ηρακλῆς καὶ Πλοῦτος. | Ἡρακλῆς καὶ Πλουτος. | start 18: circumflex → none; addressed output is HOLD, so no fixed/error award for those slots. |
| old59 #13 / `2793d64c-p000070-l0014` / random marks under 10 and 13, and over 12 | no_top [12] None: fail → HOLD (raw False → True) | ηχὼ στενάξασᾶ θρηνῳδός, | ἦχὼ στενάξασα θρηνῳδός, | start 15: circumflex → none; addressed output is HOLD, so no fixed/error award for those slots. |
| old59 #24 / `384c3f89-p000205-l0005` / 2 accent of 1 missed, 1 ellipsis at 2 and 7 respectively | mark [1] 2: fail → HOLD (raw False → True) | Ἠ ῥ’, ἅμα δ’ εὐχωλῆσιν ἐς ὕδατα λαιμοτομήσας | Ἦ ῥ’, ἅμα δ’ εὐχωλῇσιν ἐς ὕδατα λαιμοτομήσας | start 0: psili → psili+circumflex; addressed output is HOLD, so no fixed/error award for those slots. |
| old59 #32 / `51fe7386-p000024-l0020` / missed at 6, 8, 11, 20, 37, 39 ... and also part of 23 detected as subscript | mark [11] 1: fail → fixed (raw False → True) | Καὶ δὲν ἐπερασε καιρὸς, χρόνοι πολλοὶ καὶ μῆνες | Καὶ δὲν ἐπέρασε καιρὸς, χρόνοι πολλοὶ καὶ μῆνες | SF1 detector recovers source 5 above ε at start 13 / frozen slot 11; also present without R1. Detector drift, not an R1 naming gain. |
| old59 #39 / `602cc72e-p000155-l0009` / missed two at 2, and one at 11, 12, and 16 | mark [12] 1: fail → HOLD (raw False → True) | Εὔνουχος καὶ ἵερεύς. | Εὔνουχος καὶ ἱερεύς. | start 15: dasia+acute → dasia; addressed output is HOLD, so no fixed/error award for those slots. |
| old59 #41 / `602cc72e-p000167-l0027` / missed 1 at 1, 6, 10, and 14 | mark [1] 1: fail → HOLD (raw False → True) | Ηρακλῆς καὶ Πλοῦτος. | Ἡρακλῆς καὶ Πλουτος. | start 0: none → dasia; addressed output is HOLD, so no fixed/error award for those slots. |
| old59 #44 / `602cc72e-p000167-l0027` / missed 1 at 1, 6, 10, and 14 | mark [14] 1: fixed → HOLD (raw True → False) | Ηρακλῆς καὶ Πλοῦτος. | Ἡρακλῆς καὶ Πλουτος. | start 18: circumflex → none; addressed output is HOLD, so no fixed/error award for those slots. |

## Box regression and detector drift

`box_regression.py` was run on all 92 owner lines, including current review/examples notes for attribution.

| comparison | lines | lost | added | moved | reading-changed lines |
|---|---:|---:|---:|---:|---:|
| saved S6 → combined | 92 | 0 | 1 | 0 | 62 |
| fresh hash-bound SF1 detector → combined | 92 | 0 | 0 | 0 | 61 |

**The requested saved-S6 box identity is not exact.** The only difference is an added `above` box `[370, 8, 386, 28]` on `51fe7386-p000024-l0020`, source component 5, displayed character slot 9, frozen primary slot 11 (source slots `[11,10]`), recognizer start 13, ε in `ἐπέρασε`. Its lossless pixel runs are retained. The old serialized S6 evidence had no box there. The matcher reports the old reviewed owner unassigned because the historical sidecar has no certified two-dimensional mark zones; CN1 does not alias display slot 9 to frozen slot 9.

Both fresh page builds contain the same 578 boxes, all 2,512 character bases/starts/component IDs/boxes, identical raw `LineReading` records, and identical per-character evidence including pixel runs. There are zero presence, segmentation or apostrophe-evidence differences attributable to the combination step. Opening-quote evidence is also identical, but the rendered quote glyphs differ on five lines (see below). R1 changes 92 part sequences on 61 lines. Against saved S6 the one detector recovery makes 62 reading-changed lines. The control isolates this pre-existing SF1 detector drift; it is not evidence of an R1 gain.

## Rendered punctuation limitation of the required builder

**The existing hash-bound combined builder does not fully preserve S6’s displayed opening quotes.** `read_ink` strips recognizer quote glyphs and inserts a quote only when detector evidence exists. `combine` calls `render_reading(LINE_TEXT[lid], slots)` again and skips that final quote step. It therefore drops two detected opening quotes and restores three unsupported recognizer quote glyphs, with unchanged boxes. A sixth line has only an extra space after a retained quote. This is measured output of the requested unchanged path, not a corrected implementation of the intended S6-quote composition.

The strict `quote`/`leading_sign` clauses inspect `opening_quotes`, while `no_regression` compares marks/apostrophes but not rendered opening-quote text; these five display changes are consequently **outside the headline instrument’s combined-worse count of 1**. The punctuation facet table above is an evidence-instrument score and must not be read as proof of displayed-punctuation parity. All five witnesses are also serialized with `type=rendered_punctuation_difference`.

| line / note sets | S6 detector-control reading | actual combined reading | cause |
|---|---|---|---|
| 177b717d-p000097-l0010 / examples_v10, old33, old56, old59, review_v16 | Ὤ, τί ζέστη, Θεέ μου, βράζει !» | «Ὤ, τί ζέστη, Θεέ μου, βράζει !» | combine re-renders LINE_TEXT with render_reading and does not repeat read_ink opening-quote stripping/insertion; opening_quotes boxes remain identical; strict quote clauses score boxes, not displayed glyphs |
| 384c3f89-p000030-l0010 / examples_v10, old56 | “Ἄλλα μὲν ὅσσα τε νηὶ ἐφοπλίσσασθαι ἔοικεν | Ἄλλα μὲν ὅσσα τε νηὶ ἐφοπλίσσασθαι ἔοικεν | combine re-renders LINE_TEXT with render_reading and does not repeat read_ink opening-quote stripping/insertion; opening_quotes boxes remain identical; strict quote clauses score boxes, not displayed glyphs |
| 384c3f89-p000030-l0029 / examples_v10, old33, old56, old59, review_v16 | “Εἰ μὲν δή μοι κὓδος ἐπιτρωπἁτε μέλεσθαι, |  Εἰ μὲν δή μοι κῦδος ἐπιτρωπᾶτε μέλεσθαι, | combine re-renders LINE_TEXT with render_reading and does not repeat read_ink opening-quote stripping/insertion; opening_quotes boxes remain identical; strict quote clauses score boxes, not displayed glyphs |
| 8b6b0de9-p000007-l0021 / examples_v10, old56 | Εἰς σὲ προσπλέκει ἡ Κλωθὠ | » Εἰς σὲ προσπλέκει ἡ Κλωθὼ | combine re-renders LINE_TEXT with render_reading and does not repeat read_ink opening-quote stripping/insertion; opening_quotes boxes remain identical; strict quote clauses score boxes, not displayed glyphs |
| 8b6b0de9-p000008-l0001 / examples_v10, old33, old56, old59, review_v16 | Καὶ εἰς τὸν ᾷδην μετὰ σοῦ, | « Καὶ εἰς τὸν ᾅδην μετὰ σοῦ, | combine re-renders LINE_TEXT with render_reading and does not repeat read_ink opening-quote stripping/insertion; opening_quotes boxes remain identical; strict quote clauses score boxes, not displayed glyphs |

## Instrument and provenance

Current note clauses call `s6_notes.clause` with the S4 reviewed snapshot, reproducing S6 **35/49 and 33/57** exactly. Old33 and old56 use `r1_owner.evaluate`’s saved strict clause transcriptions, then call `r1_owner.clause`; old59 uses its exact unit-count and Counter-equality predicates and frozen v8 overlap mapping. For full-system scoring, `reader_scored` / `prediction_line_present` mean a serialized system output exists and are set symmetrically: the S6 fallback remains available where R1 has no head/prediction. Apostrophe/quote clauses route to `s6_notes.clause`; the old punctuation-dot clause uses the retained frozen slot’s below evidence. This prevents the R1-only “outside four heads” exclusion from incorrectly discarding S6’s punctuation in the combined system. No reader or instrument implementation was edited.

Old strict counts therefore differ from the older permissive S6 legacy evaluator (47/59, 22/33, 32/56): CN1 retains exact count/name equality and the strict approved-name/UNKNOWN guards instead. The missing R1 line in the current 57-example set uses its S6 fallback and is not declared a missing combined prediction.

Targeted held mark clauses are deferred; punctuation, letter identity and segmentation do not depend on R1 mark names. For line-wide guards, held character comparisons are excluded before checking the remaining outputs; a separate unheld failure still fails the note. The Boolean instrument outcome is retained as `raw_fixed`, and all hold-aware decisions and per-facet results remain independently inspectable. For example, the apparent raw `whole_marks` gain at `384c3f89-p000091-l0014` comes from zones derived from held displayed names, despite unchanged physical evidence, and earns no complete-note fix.

The combined config binds the current detector commit, all SF1 reader source hashes, S4 shape and S5 case assets, explicit print constraint policy, actual R1-A `best.pt` SHA256 `719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636`, and both supplied prediction-file hashes. Prediction receipts and actual checkpoint hashes were verified. The cached alignment file, input snapshots, note versions, adapter sources and exact generated HTML/sidecars are hashed in the measurement receipt. Prediction confidence remains UNKNOWN; no detector confidence is borrowed for R1 naming.

Artifacts: [checks](CN1_checks.jsonl), [machine summary](CN1_evidence/summary.json), [verification](CN1_evidence/verification.json), [measurement receipt](CN1_evidence/measurement_receipt.json), [combined configuration](CN1_evidence/combined_config.json), [combined serialized readings and boxes](CN1_evidence/combined_boxes.json), [saved-S6 box diff](CN1_evidence/box_regression_saved_s6_to_combined.json), [detector-control box diff](CN1_evidence/box_regression_control_to_combined.json). The HTML files are local measurement artifacts and were neither published nor opened.

## Reproduction and validation

Use the specified interpreter, `PYTHONPATH=$PWD`, `PYTHONDONTWRITEBYTECODE=1`. Final guarded page-build arguments and elapsed times are saved verbatim in `combined_build_receipt.json` and `control_build_receipt.json`. To reproduce them without retyping their absolute prediction paths:

```python
import json, os, subprocess
from pathlib import Path
py = "/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python"
env = dict(os.environ, PYTHONPATH=os.getcwd(), PYTHONDONTWRITEBYTECODE="1")
e = Path("docs/records/labelfix/spellcheck/CN1_evidence")
for file in ("combined_build_receipt.json", "control_build_receipt.json"):
    r = json.loads((e / file).read_text())
    subprocess.run([py, "-m", "scripts.labelfix.cn1_offline", str(e / file),
                    r["module"], *r["arguments"]], env=env, check=True)
subprocess.run([py, "-m", "scripts.labelfix.cn1_measure"], env=env, check=True)
```

```sh
PYTHONPATH=$PWD PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m scripts.labelfix.box_regression docs/records/labelfix/spellcheck/CN1_evidence/saved_s6_boxes.json docs/records/labelfix/spellcheck/CN1_evidence/combined_boxes.json --notes docs/records/labelfix/spellcheck/owner_notes_review_v16_20261016.jsonl docs/records/labelfix/spellcheck/owner_notes_examples_v10_20261016.jsonl --out docs/records/labelfix/spellcheck/CN1_evidence/box_regression_saved_s6_to_combined.json
# Repeat with s6_control_boxes.json for the detector-control comparison.
PYTHONPATH=$PWD PYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m scripts.labelfix.cn1_report
```

Validation: **12 passed, 30 deselected** in the existing SF1 tests covering missing targets, exact approved/UNKNOWN name preservation, matching/containment/missing-line behavior, reader confidence separation and K1 HOLD propagation. Measurement assertions verify all five denominators, the saved S6 current totals, one-to-one frozen slot identity, page hashes, configuration/checkpoint/prediction receipts, zero print deletions, and identical fresh-control physical evidence. No broad model evaluation or training was run.

CN1 RESULT: complete notes combined vs S6 — review_v16 26/49 vs 35/49; examples_v10 25/57 vs 33/57; old59 45/59 vs 45/59; old33 18/33 vs 17/33; old56 23/56 vs 26/56; clause split (overlapping note-set facets) physical 232/310 vs 230/310, naming 100/162 + 33 HOLD vs 107/162, segmentation 23/23 vs 23/23, punctuation 39/48 vs 39/48, letter identity 11/11 vs 11/11; HOLD slots 87 (80 kind-disagreement, 9 K1, 2 overlap); combined-worse notes 1.
