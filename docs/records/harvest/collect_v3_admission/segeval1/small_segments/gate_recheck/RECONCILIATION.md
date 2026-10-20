# Supplied gate ID reconciliation

| scope | rows | foreign | mixed | overlap | gate_failed |
| --- | --- | --- | --- | --- | --- |
| census | 592466 | 1006 | 1698 | 63 | 2641 |
| key | 59002 | 672 | 37 | 3 | 706 |
| bed | 417 | 17 | 3 | 0 | 20 |
| controls | 20 | 1 | 0 | 0 | 1 |
| key_opus | 179 | 7 | 2 | 0 | 9 |
| owner_marks | 185 | 0 | 1 | 0 | 1 |

Mismatches: [{"scope": "bed", "expected": [18, 3], "actual": [17, 3], "foreign_ids": ["bsb_poly1850--027215cc6d2a7e8a--s027-l0003", "gazette_modern--49b793056935d163--s000-l0043", "gazette_modern--5d05d04d136ea2c2--s000-l0120", "gazette_modern--67dfc161a690ff25--s000-l0029", "gazette_modern--70dafa4f769a0d6a--s000-l0067", "gazette_modern--b0dc765920f41797--s000-l0119", "gazette_modern--b21451311e269f58--s000-l0001", "gazette_modern--c694a4568affabd6--s000-l0130", "ia_poly1850--26e14cb9c90b750f--s003-l0009", "ia_poly1850--26e14cb9c90b750f--s003-l0047", "ia_poly1850--26e14cb9c90b750f--s003-l0077", "ia_poly1850--26e14cb9c90b750f--s003-l0102", "ia_poly1850--26e14cb9c90b750f--s005-l0016", "ia_poly1850--6a9e5e4676cec552--s000-l0039", "ia_poly1850--c3f3a531e277da9a--s038-l0006", "ia_russian--06528548147a3a3d--s005-l0029", "nlg--3d6bd7bd688acb61--s029-l0031"], "mixed_ids": ["ia_poly1850--5aa15e93b2f445b8--s005-l0001", "ia_poly1850--a89bd2c9bdb1ca6d--s008-l0021", "serbia--b6450341d87fb144--s007-l0002"]}]

IDs absent from census: []

{"message": "Expected 18 foreign matches counts all sample rows including one control; bed alone has 17.", "control_foreign_ids": ["gazette_modern--fd0c55b5cf1557ca--s000-l0042"]}

| line_id | control | final_type | final_class | Google_text | gate_failed | gate_reason |
| --- | --- | --- | --- | --- | --- | --- |
| gazette_modern--49b793056935d163--s000-l0043 | False | cut_fragment | segmentation_fault | דוד דר | True | foreign |
| gazette_modern--b21451311e269f58--s000-l0001 | False | punctuation | printed_nonletter | سے | True | foreign |
| gazette_modern--fd0c55b5cf1557ca--s000-l0042 | True | cut_fragment | segmentation_fault | لارن | True | foreign |
| ia_poly1850--26e14cb9c90b750f--s003-l0047 | False | foreign_script | out_of_scope_script | 頂 硬 | True | foreign |
| ia_poly1850--26e14cb9c90b750f--s003-l0102 | False | foreign_script | out_of_scope_script | 滑 | True | foreign |
| ia_poly1850--26e14cb9c90b750f--s005-l0016 | False | foreign_script | out_of_scope_script | 推而凹兒—五法凹 | True | foreign |
| ia_poly1850--6a9e5e4676cec552--s000-l0039 | False | punctuation | printed_nonletter | وو | True | foreign |
| ia_poly1850--a89bd2c9bdb1ca6d--s008-l0021 | False | abbrev_label | legit_text | vἱῷ om. C | True | mixed |
| serbia--b6450341d87fb144--s007-l0002 | False | caps_display | legit_text | ВИЉЕМ БУE | True | mixed |
| gazette_modern--67dfc161a690ff25--s000-l0029 | False | marker | legit_text | 日 | True | foreign |
| gazette_modern--b0dc765920f41797--s000-l0119 | False | cut_fragment | segmentation_fault | द | True | foreign |
| gazette_modern--70dafa4f769a0d6a--s000-l0067 | False | handwriting | non_text | 21 .وند | True | foreign |
| ia_poly1850--c3f3a531e277da9a--s038-l0006 | False | noise | non_text | カ | True | foreign |
| ia_poly1850--26e14cb9c90b750f--s003-l0077 | False | foreign_script | out_of_scope_script | 厚點 | True | foreign |
| ia_poly1850--26e14cb9c90b750f--s003-l0009 | False | foreign_script | out_of_scope_script | 必兜 | True | foreign |
| ia_russian--06528548147a3a3d--s005-l0029 | False | punctuation | printed_nonletter | و | True | foreign |
| nlg--3d6bd7bd688acb61--s029-l0031 | False | noise | non_text | یہ | True | foreign |
| bsb_poly1850--027215cc6d2a7e8a--s027-l0003 | False | show_through | non_text | م٦١٦ | True | foreign |
| gazette_modern--c694a4568affabd6--s000-l0130 | False | number | legit_text | 3.13.の機 | True | foreign |
| gazette_modern--5d05d04d136ea2c2--s000-l0120 | False | cut_fragment | segmentation_fault | 3つに | True | foreign |
| ia_poly1850--5aa15e93b2f445b8--s005-l0001 | False | caps_display | legit_text | PRAEFATΙΟ | True | mixed |
