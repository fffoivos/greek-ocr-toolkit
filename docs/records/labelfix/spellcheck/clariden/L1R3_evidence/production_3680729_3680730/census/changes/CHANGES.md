# L1R3 deletion / change census

Analysis only. The reported correction count is real mark-correction lines:
corrected-status lines with at least one combining-mark insertion or deletion.
NFD difflib, autojunk=False. Mark replacements count two codepoint edits;
an elision alias substitution counts once. Classes and source support describe
labels, not printed truth. Class marginals overlap real-mark totals.

Word-final and lowercase consonant-initial elision aliases are folded for
comparison (including ᾿στὸν → 'στὸν). Spacing breathings before capitals/vowels
are not folded. Explicit U+0374/U+0384/U+02B9 and apostrophes after uppercase
Greek numeral tokens, decimal tokens or Unicode numeral letters are keraia.
Lowercase ASCII-apostrophe numeral/elision ambiguity needs print adjudication.
Single-source means original-label codepoint/alias atom absent from recogniser
at the same letter boundary and occurrence. All deleted classes are counted.

SF6 deletion HOLD classes count each line once per class; checks count atoms.
MOVE applied counts only actual corrected releases. Proposal lines may still HOLD
on another veto. The full audit population is real_mark_correction_lines.jsonl
(line_id, wave, mode); alias-only and punctuation-only changes are excluded.

## PRESENCE

| Wave | Lines | Corrected status | Real mark-correction lines | Real mark lines with single-source deletion | Share of real mark-correction lines |
|---|---:|---:|---:|---:|---:|
| ALL | 124669 | 83 | 58 | 0 | 0.000000% |
| mixed | 13227 | 14 | 9 | 0 | 0.000000% |
| openarchives | 235 | 0 | 0 | 0 | 0.000000% |
| parliament | 27224 | 3 | 2 | 0 | 0.000000% |
| round1 | 43869 | 41 | 28 | 0 | 0.000000% |
| round2 | 17026 | 17 | 14 | 0 | 0.000000% |
| vouli | 23088 | 8 | 5 | 0 | 0.000000% |

### SF6 ALL

Deletion HOLD lines: 33060; MOVE proposal lines: 9; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 20459 | 59885 | 00c322b3ee04b419d1979f22-p000015-l0034, 00c322b3ee04b419d1979f22-p000015-l0039, 00c322b3ee04b419d1979f22-p000015-l0041, 00c322b3ee04b419d1979f22-p000015-l0046, 00c322b3ee04b419d1979f22-p000015-l0068, 00c322b3ee04b419d1979f22-p000015-l0069, 00c322b3ee04b419d1979f22-p000015-l0073, 00c322b3ee04b419d1979f22-p000015-l0076, 00c322b3ee04b419d1979f22-p000028-l0003, 00c322b3ee04b419d1979f22-p000028-l0009, 00c322b3ee04b419d1979f22-p000028-l0010, 00c322b3ee04b419d1979f22-p000028-l0011, 00c322b3ee04b419d1979f22-p000028-l0012, 00c322b3ee04b419d1979f22-p000028-l0013, 00c322b3ee04b419d1979f22-p000028-l0014, 00c322b3ee04b419d1979f22-p000028-l0016, 00c322b3ee04b419d1979f22-p000028-l0018, 00c322b3ee04b419d1979f22-p000028-l0019, 00c322b3ee04b419d1979f22-p000028-l0020, 00c322b3ee04b419d1979f22-p000028-l0021 |
| apostrophe | 1580 | 1685 | 00c322b3ee04b419d1979f22-p000015-l0059, 00c322b3ee04b419d1979f22-p000015-l0079, 00c322b3ee04b419d1979f22-p000028-l0011, 00c322b3ee04b419d1979f22-p000028-l0025, 00c322b3ee04b419d1979f22-p000028-l0027, 00c322b3ee04b419d1979f22-p000103-l0011, 00c322b3ee04b419d1979f22-p000115-l0068, 00c322b3ee04b419d1979f22-p000142-l0005, 00c322b3ee04b419d1979f22-p000142-l0016, 0271e3cae771-p000001-l0036, 0271e3cae771-p000004-l0037, 0271e3cae771-p000006-l0030, 042c93b2591368d437f27678-p000148-l0003, 042c93b2591368d437f27678-p000245-l0022, 043b454a8c255b6690fd3777-p000013-l0053, 043b454a8c255b6690fd3777-p000027-l0033, 043b454a8c255b6690fd3777-p000031-l0006, 043b454a8c255b6690fd3777-p000040-l0051, 043b454a8c255b6690fd3777-p000044-l0062, 043b454a8c255b6690fd3777-p000054-l0063 |
| quote | 1953 | 2000 | 00c322b3ee04b419d1979f22-p000015-l0069, 00c322b3ee04b419d1979f22-p000028-l0054, 00c322b3ee04b419d1979f22-p000028-l0070, 00c322b3ee04b419d1979f22-p000055-l0002, 00c322b3ee04b419d1979f22-p000055-l0003, 00c322b3ee04b419d1979f22-p000055-l0025, 00c322b3ee04b419d1979f22-p000055-l0026, 00c322b3ee04b419d1979f22-p000055-l0027, 00c322b3ee04b419d1979f22-p000055-l0028, 00c322b3ee04b419d1979f22-p000055-l0030, 00c322b3ee04b419d1979f22-p000055-l0043, 00c322b3ee04b419d1979f22-p000055-l0050, 00c322b3ee04b419d1979f22-p000078-l0069, 00c322b3ee04b419d1979f22-p000093-l0006, 00c322b3ee04b419d1979f22-p000093-l0040, 00c322b3ee04b419d1979f22-p000093-l0041, 00c322b3ee04b419d1979f22-p000093-l0042, 00c322b3ee04b419d1979f22-p000093-l0046, 00c322b3ee04b419d1979f22-p000093-l0053, 00c322b3ee04b419d1979f22-p000115-l0024 |
| keraia | 1652 | 1786 | 00c322b3ee04b419d1979f22-p000055-l0006, 00c322b3ee04b419d1979f22-p000055-l0011, 00c322b3ee04b419d1979f22-p000115-l0019, 00c322b3ee04b419d1979f22-p000129-l0037, 00c322b3ee04b419d1979f22-p000166-l0040, 042c93b2591368d437f27678-p000075-l0036, 042c93b2591368d437f27678-p000148-l0011, 043b454a8c255b6690fd3777-p000019-l0042, 043b454a8c255b6690fd3777-p000019-l0063, 043b454a8c255b6690fd3777-p000019-l0079, 0590d5cb-p000007-l0092, 07dc0ec3a36ef8d4433de416-p000083-l0036, 0907df739607faca673d2169-p000033-l0007, 0b33fccd-p000023-l0126, 0b33fccd-p000032-l0044, 0cb3f67240837f77ee728005-p000005-l0042, 0cb3f67240837f77ee728005-p000005-l0044, 0cb3f67240837f77ee728005-p000005-l0049, 0cb3f67240837f77ee728005-p000005-l0050, 0cb3f67240837f77ee728005-p000019-l0052 |
| other | 18993 | 226929 | 00c322b3ee04b419d1979f22-p000015-l0009, 00c322b3ee04b419d1979f22-p000015-l0035, 00c322b3ee04b419d1979f22-p000015-l0037, 00c322b3ee04b419d1979f22-p000015-l0041, 00c322b3ee04b419d1979f22-p000015-l0046, 00c322b3ee04b419d1979f22-p000015-l0051, 00c322b3ee04b419d1979f22-p000015-l0059, 00c322b3ee04b419d1979f22-p000015-l0069, 00c322b3ee04b419d1979f22-p000015-l0073, 00c322b3ee04b419d1979f22-p000015-l0076, 00c322b3ee04b419d1979f22-p000015-l0081, 00c322b3ee04b419d1979f22-p000028-l0003, 00c322b3ee04b419d1979f22-p000028-l0010, 00c322b3ee04b419d1979f22-p000028-l0011, 00c322b3ee04b419d1979f22-p000028-l0012, 00c322b3ee04b419d1979f22-p000028-l0013, 00c322b3ee04b419d1979f22-p000028-l0014, 00c322b3ee04b419d1979f22-p000028-l0016, 00c322b3ee04b419d1979f22-p000028-l0017, 00c322b3ee04b419d1979f22-p000028-l0019 |

### ALL

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 58 | 63 | 043b454a8c255b6690fd3777-p000008-l0020, 043b454a8c255b6690fd3777-p000061-l0030, 052a7a91dd9752b856b9fd8a-p000188-l0005, 143e78b5de2e6e784534ee0d-p000079-l0003, 23e59c57bd30-p000003-l0032, 241c524ed5b20f2baadf4b8b-p000082-l0043, 2c8742589d947f8d749c7ba2-p000040-l0013, 2f9e996ffbdaaa3b4a9dfdcf-p000082-l0007, 2f9e996ffbdaaa3b4a9dfdcf-p000141-l0018, 341f77df7fe3f09264ceee79-p000004-l0017, 39fbbdfd2c8030f211a318b7-p000138-l0003, 3a469aeb16cd49371b9dfc3d-p000015-l0007, 3c4393cb8164c820f7e7b38c-p000032-l0005, 54a124e5cac779ec617e3ace-p000045-l0038, 5e99df8a3f2ecb56ba5c751b-p000156-l0002, 666498b9ed183dc88c1e8716-p000036-l0034, 686431e9a7fe04175e6e9be9-p000091-l0044, 6c0a582885e55adc7c535c48-p000107-l0020, 6d957fa757c72e1408f65dde-p000114-l0026, 7056dabdb0d8a5db4a0976f8-p000132-l0038 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 58 | 63 | 043b454a8c255b6690fd3777-p000008-l0020, 043b454a8c255b6690fd3777-p000061-l0030, 052a7a91dd9752b856b9fd8a-p000188-l0005, 143e78b5de2e6e784534ee0d-p000079-l0003, 23e59c57bd30-p000003-l0032, 241c524ed5b20f2baadf4b8b-p000082-l0043, 2c8742589d947f8d749c7ba2-p000040-l0013, 2f9e996ffbdaaa3b4a9dfdcf-p000082-l0007, 2f9e996ffbdaaa3b4a9dfdcf-p000141-l0018, 341f77df7fe3f09264ceee79-p000004-l0017, 39fbbdfd2c8030f211a318b7-p000138-l0003, 3a469aeb16cd49371b9dfc3d-p000015-l0007, 3c4393cb8164c820f7e7b38c-p000032-l0005, 54a124e5cac779ec617e3ace-p000045-l0038, 5e99df8a3f2ecb56ba5c751b-p000156-l0002, 666498b9ed183dc88c1e8716-p000036-l0034, 686431e9a7fe04175e6e9be9-p000091-l0044, 6c0a582885e55adc7c535c48-p000107-l0020, 6d957fa757c72e1408f65dde-p000114-l0026, 7056dabdb0d8a5db4a0976f8-p000132-l0038 |
| insertions_by_class/numeral_keraia | 1 | 1 | 70e0a3447310acfc3f8dddf3-p000254-l0006 |
| insertions_by_class/elision_apostrophe | 1 | 1 | dc390fceb64d9bb60a12d6b8-p000060-l0005 |
| insertions_by_class/quote | 23 | 23 | 00c322b3ee04b419d1979f22-p000039-l0048, 042c93b2591368d437f27678-p000269-l0010, 12493332097bacc2a62b4d9a-p000036-l0008, 1c13bd49225f6fcf7dcca5a0-p000036-l0007, 2d29e5e76d90adc4cc1b093a-p000020-l0057, 453f156dc6352286456a08cb-p000209-l0034, 69846639273a60b797e93cb9-p000262-l0031, 7aea9867-p000038-l0130, 8b231047fdbd96ec30e1eded-p000019-l0038, 8c926ffa3b1b2be056e56b7e-p000038-l0003, 8c926ffa3b1b2be056e56b7e-p000130-l0011, 971b6ed3092a-p000004-l0002, 9e60fbb6b1fc1da9f26b775e-p000175-l0011, aed4abe1314b-p000002-l0017, b5f8ce187b707837e5669281-p000046-l0039, c57e3067ed37cedf17f285e6-p000044-l0006, cc0e056392dd2ef4916b3e7d-p000039-l0002, d0eda948e5b1f3632f8687fb-p000311-l0038, d9b7dfa900e3-p000003-l0034, dc390fceb64d9bb60a12d6b8-p000082-l0002 |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 mixed

Deletion HOLD lines: 3212; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 1937 | 5388 | 0a4bc4314e492706bcc0bf44-p000008-l0010, 0a4bc4314e492706bcc0bf44-p000008-l0023, 0a4bc4314e492706bcc0bf44-p000008-l0024, 0a4bc4314e492706bcc0bf44-p000008-l0025, 0a4bc4314e492706bcc0bf44-p000011-l0002, 0a4bc4314e492706bcc0bf44-p000011-l0009, 0a4bc4314e492706bcc0bf44-p000011-l0013, 0a4bc4314e492706bcc0bf44-p000011-l0021, 0a4bc4314e492706bcc0bf44-p000011-l0022, 0a4bc4314e492706bcc0bf44-p000011-l0034, 0a4bc4314e492706bcc0bf44-p000011-l0035, 0a4bc4314e492706bcc0bf44-p000011-l0038, 0a4bc4314e492706bcc0bf44-p000011-l0041, 0a4bc4314e492706bcc0bf44-p000014-l0009, 0a4bc4314e492706bcc0bf44-p000014-l0011, 0a4bc4314e492706bcc0bf44-p000014-l0013, 0a4bc4314e492706bcc0bf44-p000014-l0026, 0a4bc4314e492706bcc0bf44-p000014-l0035, 0a4bc4314e492706bcc0bf44-p000019-l0013, 0a4bc4314e492706bcc0bf44-p000019-l0028 |
| apostrophe | 162 | 166 | 0a4bc4314e492706bcc0bf44-p000008-l0023, 0a4bc4314e492706bcc0bf44-p000019-l0012, 0a4bc4314e492706bcc0bf44-p000019-l0013, 0a4bc4314e492706bcc0bf44-p000046-l0035, 12493332097bacc2a62b4d9a-p000026-l0009, 12493332097bacc2a62b4d9a-p000046-l0011, 1c13bd49225f6fcf7dcca5a0-p000036-l0002, 1c13bd49225f6fcf7dcca5a0-p000081-l0009, 1c13bd49225f6fcf7dcca5a0-p000115-l0013, 1c13bd49225f6fcf7dcca5a0-p000125-l0008, 3249d506364999770e38aeef-p000044-l0022, 3249d506364999770e38aeef-p000044-l0026, 3249d506364999770e38aeef-p000099-l0013, 3249d506364999770e38aeef-p000109-l0009, 3249d506364999770e38aeef-p000130-l0052, 341f77df7fe3f09264ceee79-p000006-l0035, 341f77df7fe3f09264ceee79-p000015-l0026, 34d2967a06064249e6ebc895-p000077-l0015, 34d2967a06064249e6ebc895-p000139-l0024, 37a9179b-p000113-l0003 |
| quote | 330 | 332 | 0a4bc4314e492706bcc0bf44-p000046-l0006, 12493332097bacc2a62b4d9a-p000007-l0018, 12493332097bacc2a62b4d9a-p000031-l0031, 12493332097bacc2a62b4d9a-p000046-l0029, 137e9af6a0045d5746e26efa-p000003-l0008, 137e9af6a0045d5746e26efa-p000006-l0022, 137e9af6a0045d5746e26efa-p000008-l0010, 137e9af6a0045d5746e26efa-p000008-l0021, 1c13bd49225f6fcf7dcca5a0-p000115-l0013, 3249d506364999770e38aeef-p000011-l0019, 3249d506364999770e38aeef-p000011-l0020, 3249d506364999770e38aeef-p000011-l0021, 3249d506364999770e38aeef-p000011-l0022, 3249d506364999770e38aeef-p000011-l0023, 3249d506364999770e38aeef-p000011-l0024, 3249d506364999770e38aeef-p000011-l0025, 3249d506364999770e38aeef-p000011-l0026, 3249d506364999770e38aeef-p000011-l0027, 3249d506364999770e38aeef-p000011-l0028, 3249d506364999770e38aeef-p000011-l0029 |
| keraia | 117 | 125 | 12493332097bacc2a62b4d9a-p000024-l0022, 12493332097bacc2a62b4d9a-p000024-l0025, 12493332097bacc2a62b4d9a-p000026-l0029, 12493332097bacc2a62b4d9a-p000026-l0031, 12493332097bacc2a62b4d9a-p000031-l0012, 12493332097bacc2a62b4d9a-p000031-l0017, 12493332097bacc2a62b4d9a-p000041-l0017, 12493332097bacc2a62b4d9a-p000046-l0027, 3249d506364999770e38aeef-p000044-l0022, 3249d506364999770e38aeef-p000044-l0026, 3249d506364999770e38aeef-p000054-l0040, 3249d506364999770e38aeef-p000067-l0044, 3249d506364999770e38aeef-p000099-l0033, 3249d506364999770e38aeef-p000109-l0052, 3249d506364999770e38aeef-p000130-l0034, 341f77df7fe3f09264ceee79-p000004-l0029, 341f77df7fe3f09264ceee79-p000021-l0025, 341f77df7fe3f09264ceee79-p000021-l0028, 4a34388c9884fda746d2a8cd-p000020-l0008, 4a34388c9884fda746d2a8cd-p000020-l0014 |
| other | 1854 | 19982 | 0a4bc4314e492706bcc0bf44-p000008-l0023, 0a4bc4314e492706bcc0bf44-p000008-l0024, 0a4bc4314e492706bcc0bf44-p000008-l0025, 0a4bc4314e492706bcc0bf44-p000011-l0007, 0a4bc4314e492706bcc0bf44-p000011-l0009, 0a4bc4314e492706bcc0bf44-p000011-l0017, 0a4bc4314e492706bcc0bf44-p000011-l0034, 0a4bc4314e492706bcc0bf44-p000011-l0035, 0a4bc4314e492706bcc0bf44-p000011-l0038, 0a4bc4314e492706bcc0bf44-p000011-l0041, 0a4bc4314e492706bcc0bf44-p000014-l0026, 0a4bc4314e492706bcc0bf44-p000019-l0004, 0a4bc4314e492706bcc0bf44-p000019-l0010, 0a4bc4314e492706bcc0bf44-p000019-l0012, 0a4bc4314e492706bcc0bf44-p000019-l0013, 0a4bc4314e492706bcc0bf44-p000019-l0018, 0a4bc4314e492706bcc0bf44-p000019-l0022, 0a4bc4314e492706bcc0bf44-p000019-l0028, 0a4bc4314e492706bcc0bf44-p000019-l0032, 0a4bc4314e492706bcc0bf44-p000019-l0036 |

### mixed

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 9 | 11 | 341f77df7fe3f09264ceee79-p000004-l0017, 8a482dd5cb341a70d157d5c4-p000273-l0024, b5076e8734ba287d549d79b5-p000010-l0026, c57e3067ed37cedf17f285e6-p000009-l0022, c8654864d161aa7fc41f65cb-p000335-l0035, d0eda948e5b1f3632f8687fb-p000620-l0005, d0eda948e5b1f3632f8687fb-p000620-l0016, d0eda948e5b1f3632f8687fb-p000773-l0088, e11826423ecefe41dd940b28-p000057-l0025 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 9 | 11 | 341f77df7fe3f09264ceee79-p000004-l0017, 8a482dd5cb341a70d157d5c4-p000273-l0024, b5076e8734ba287d549d79b5-p000010-l0026, c57e3067ed37cedf17f285e6-p000009-l0022, c8654864d161aa7fc41f65cb-p000335-l0035, d0eda948e5b1f3632f8687fb-p000620-l0005, d0eda948e5b1f3632f8687fb-p000620-l0016, d0eda948e5b1f3632f8687fb-p000773-l0088, e11826423ecefe41dd940b28-p000057-l0025 |
| insertions_by_class/numeral_keraia | 1 | 1 | 70e0a3447310acfc3f8dddf3-p000254-l0006 |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 4 | 4 | 12493332097bacc2a62b4d9a-p000036-l0008, 1c13bd49225f6fcf7dcca5a0-p000036-l0007, c57e3067ed37cedf17f285e6-p000044-l0006, d0eda948e5b1f3632f8687fb-p000311-l0038 |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 openarchives

Deletion HOLD lines: 23; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 7 | 9 | 0fead7c5-p000008-l0061, 0fead7c5-p000008-l0095, 0fead7c5-p000010-l0001, 0fead7c5-p000010-l0011, 0fead7c5-p000010-l0030, 0fead7c5-p000010-l0040, 0fead7c5-p000010-l0047 |
| apostrophe | 1 | 1 | 0fead7c5-p000004-l0038 |
| quote | 0 | 0 |  |
| keraia | 10 | 13 | 0fead7c5-p000004-l0035, 0fead7c5-p000004-l0038, 0fead7c5-p000004-l0041, 0fead7c5-p000004-l0044, 0fead7c5-p000004-l0047, a4c40997-p000007-l0013, a4c40997-p000007-l0018, a4c40997-p000007-l0028, a4c40997-p000017-l0040, a4c40997-p000066-l0013 |
| other | 9 | 52 | 0fead7c5-p000004-l0038, 0fead7c5-p000008-l0003, 0fead7c5-p000008-l0028, 0fead7c5-p000010-l0001, 0fead7c5-p000010-l0040, a4c40997-p000017-l0018, a4c40997-p000023-l0001, a4c40997-p000035-l0010, a4c40997-p000035-l0017 |

### openarchives

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 0 | 0 |  |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 0 | 0 |  |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 parliament

Deletion HOLD lines: 8007; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 5381 | 13124 | 01c618de-p000024-l0060, 0590d5cb-p000003-l0104, 0590d5cb-p000007-l0052, 0590d5cb-p000007-l0092, 0590d5cb-p000009-l0044, 0590d5cb-p000012-l0016, 0590d5cb-p000012-l0020, 0590d5cb-p000012-l0117, 0590d5cb-p000013-l0006, 0590d5cb-p000015-l0045, 0590d5cb-p000017-l0033, 0590d5cb-p000021-l0007, 0590d5cb-p000023-l0021, 0590d5cb-p000024-l0005, 0590d5cb-p000024-l0025, 0b33fccd-p000008-l0006, 0b33fccd-p000008-l0007, 0b33fccd-p000008-l0016, 0b33fccd-p000008-l0021, 0b33fccd-p000008-l0024 |
| apostrophe | 144 | 146 | 0b33fccd-p000008-l0053, 0b33fccd-p000008-l0091, 0b33fccd-p000008-l0092, 0b33fccd-p000010-l0011, 0b33fccd-p000010-l0060, 0b33fccd-p000012-l0094, 0b33fccd-p000017-l0078, 0b33fccd-p000021-l0118, 0b33fccd-p000027-l0063, 133c1ea6-p000003-l0066, 133c1ea6-p000003-l0108, 133c1ea6-p000009-l0113, 133c1ea6-p000010-l0022, 133c1ea6-p000014-l0021, 133c1ea6-p000020-l0119, 13dcc39a-p000008-l0124, 13dcc39a-p000012-l0070, 13dcc39a-p000020-l0059, 13dcc39a-p000023-l0095, 13dcc39a-p000026-l0138 |
| quote | 230 | 236 | 01c618de-p000013-l0134, 0b33fccd-p000008-l0114, 0b33fccd-p000012-l0093, 0b33fccd-p000023-l0113, 133c1ea6-p000003-l0023, 133c1ea6-p000003-l0041, 133c1ea6-p000003-l0094, 133c1ea6-p000003-l0117, 133c1ea6-p000007-l0023, 133c1ea6-p000007-l0053, 133c1ea6-p000007-l0076, 133c1ea6-p000007-l0086, 133c1ea6-p000007-l0102, 133c1ea6-p000007-l0117, 133c1ea6-p000009-l0025, 133c1ea6-p000009-l0038, 133c1ea6-p000009-l0071, 133c1ea6-p000009-l0082, 133c1ea6-p000009-l0106, 133c1ea6-p000009-l0133 |
| keraia | 104 | 110 | 0590d5cb-p000007-l0092, 0b33fccd-p000023-l0126, 0b33fccd-p000032-l0044, 133c1ea6-p000007-l0007, 133c1ea6-p000007-l0121, 133c1ea6-p000009-l0002, 133c1ea6-p000009-l0009, 133c1ea6-p000010-l0105, 133c1ea6-p000010-l0116, 133c1ea6-p000014-l0080, 133c1ea6-p000019-l0114, 1a035976-p000014-l0024, 1a035976-p000014-l0026, 1a035976-p000016-l0087, 1a035976-p000016-l0088, 1a035976-p000022-l0037, 1a035976-p000022-l0083, 3455d0e7-p000023-l0024, 48a58eb5-p000010-l0139, 52b46e46-p000005-l0099 |
| other | 4338 | 45081 | 01c618de-p000013-l0134, 0590d5cb-p000012-l0016, 0590d5cb-p000012-l0020, 0590d5cb-p000015-l0045, 0590d5cb-p000017-l0033, 0b33fccd-p000008-l0006, 0b33fccd-p000008-l0015, 0b33fccd-p000008-l0019, 0b33fccd-p000008-l0023, 0b33fccd-p000008-l0024, 0b33fccd-p000008-l0025, 0b33fccd-p000008-l0031, 0b33fccd-p000008-l0044, 0b33fccd-p000008-l0053, 0b33fccd-p000008-l0058, 0b33fccd-p000008-l0061, 0b33fccd-p000008-l0064, 0b33fccd-p000008-l0067, 0b33fccd-p000008-l0078, 0b33fccd-p000008-l0079 |

### parliament

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 2 | 2 | aac90dd4-p000017-l0024, f36aba38-p000005-l0015 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 2 | 2 | aac90dd4-p000017-l0024, f36aba38-p000005-l0015 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 1 | 1 | 7aea9867-p000038-l0130 |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 round1

Deletion HOLD lines: 12135; MOVE proposal lines: 4; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 7310 | 24346 | 00c322b3ee04b419d1979f22-p000015-l0034, 00c322b3ee04b419d1979f22-p000015-l0039, 00c322b3ee04b419d1979f22-p000015-l0041, 00c322b3ee04b419d1979f22-p000015-l0046, 00c322b3ee04b419d1979f22-p000015-l0068, 00c322b3ee04b419d1979f22-p000015-l0069, 00c322b3ee04b419d1979f22-p000015-l0073, 00c322b3ee04b419d1979f22-p000015-l0076, 00c322b3ee04b419d1979f22-p000028-l0003, 00c322b3ee04b419d1979f22-p000028-l0009, 00c322b3ee04b419d1979f22-p000028-l0010, 00c322b3ee04b419d1979f22-p000028-l0011, 00c322b3ee04b419d1979f22-p000028-l0012, 00c322b3ee04b419d1979f22-p000028-l0013, 00c322b3ee04b419d1979f22-p000028-l0014, 00c322b3ee04b419d1979f22-p000028-l0016, 00c322b3ee04b419d1979f22-p000028-l0018, 00c322b3ee04b419d1979f22-p000028-l0019, 00c322b3ee04b419d1979f22-p000028-l0020, 00c322b3ee04b419d1979f22-p000028-l0021 |
| apostrophe | 737 | 801 | 00c322b3ee04b419d1979f22-p000015-l0059, 00c322b3ee04b419d1979f22-p000015-l0079, 00c322b3ee04b419d1979f22-p000028-l0011, 00c322b3ee04b419d1979f22-p000028-l0025, 00c322b3ee04b419d1979f22-p000028-l0027, 00c322b3ee04b419d1979f22-p000103-l0011, 00c322b3ee04b419d1979f22-p000115-l0068, 00c322b3ee04b419d1979f22-p000142-l0005, 00c322b3ee04b419d1979f22-p000142-l0016, 042c93b2591368d437f27678-p000148-l0003, 042c93b2591368d437f27678-p000245-l0022, 043b454a8c255b6690fd3777-p000013-l0053, 043b454a8c255b6690fd3777-p000027-l0033, 043b454a8c255b6690fd3777-p000031-l0006, 043b454a8c255b6690fd3777-p000040-l0051, 043b454a8c255b6690fd3777-p000044-l0062, 043b454a8c255b6690fd3777-p000054-l0063, 052a7a91dd9752b856b9fd8a-p000114-l0008, 052a7a91dd9752b856b9fd8a-p000140-l0048, 0550c3c52f2b388255690d5a-p000027-l0008 |
| quote | 915 | 934 | 00c322b3ee04b419d1979f22-p000015-l0069, 00c322b3ee04b419d1979f22-p000028-l0054, 00c322b3ee04b419d1979f22-p000028-l0070, 00c322b3ee04b419d1979f22-p000055-l0002, 00c322b3ee04b419d1979f22-p000055-l0003, 00c322b3ee04b419d1979f22-p000055-l0025, 00c322b3ee04b419d1979f22-p000055-l0026, 00c322b3ee04b419d1979f22-p000055-l0027, 00c322b3ee04b419d1979f22-p000055-l0028, 00c322b3ee04b419d1979f22-p000055-l0030, 00c322b3ee04b419d1979f22-p000055-l0043, 00c322b3ee04b419d1979f22-p000055-l0050, 00c322b3ee04b419d1979f22-p000078-l0069, 00c322b3ee04b419d1979f22-p000093-l0006, 00c322b3ee04b419d1979f22-p000093-l0040, 00c322b3ee04b419d1979f22-p000093-l0041, 00c322b3ee04b419d1979f22-p000093-l0042, 00c322b3ee04b419d1979f22-p000093-l0046, 00c322b3ee04b419d1979f22-p000093-l0053, 00c322b3ee04b419d1979f22-p000115-l0024 |
| keraia | 511 | 555 | 00c322b3ee04b419d1979f22-p000055-l0006, 00c322b3ee04b419d1979f22-p000055-l0011, 00c322b3ee04b419d1979f22-p000115-l0019, 00c322b3ee04b419d1979f22-p000129-l0037, 00c322b3ee04b419d1979f22-p000166-l0040, 042c93b2591368d437f27678-p000075-l0036, 042c93b2591368d437f27678-p000148-l0011, 043b454a8c255b6690fd3777-p000019-l0042, 043b454a8c255b6690fd3777-p000019-l0063, 043b454a8c255b6690fd3777-p000019-l0079, 07dc0ec3a36ef8d4433de416-p000083-l0036, 0907df739607faca673d2169-p000033-l0007, 0cb3f67240837f77ee728005-p000005-l0042, 0cb3f67240837f77ee728005-p000005-l0044, 0cb3f67240837f77ee728005-p000005-l0049, 0cb3f67240837f77ee728005-p000005-l0050, 0cb3f67240837f77ee728005-p000019-l0052, 0cb3f67240837f77ee728005-p000019-l0056, 10349bf796b8cd19c7415595-p000121-l0009, 10349bf796b8cd19c7415595-p000157-l0029 |
| other | 7498 | 97421 | 00c322b3ee04b419d1979f22-p000015-l0009, 00c322b3ee04b419d1979f22-p000015-l0035, 00c322b3ee04b419d1979f22-p000015-l0037, 00c322b3ee04b419d1979f22-p000015-l0041, 00c322b3ee04b419d1979f22-p000015-l0046, 00c322b3ee04b419d1979f22-p000015-l0051, 00c322b3ee04b419d1979f22-p000015-l0059, 00c322b3ee04b419d1979f22-p000015-l0069, 00c322b3ee04b419d1979f22-p000015-l0073, 00c322b3ee04b419d1979f22-p000015-l0076, 00c322b3ee04b419d1979f22-p000015-l0081, 00c322b3ee04b419d1979f22-p000028-l0003, 00c322b3ee04b419d1979f22-p000028-l0010, 00c322b3ee04b419d1979f22-p000028-l0011, 00c322b3ee04b419d1979f22-p000028-l0012, 00c322b3ee04b419d1979f22-p000028-l0013, 00c322b3ee04b419d1979f22-p000028-l0014, 00c322b3ee04b419d1979f22-p000028-l0016, 00c322b3ee04b419d1979f22-p000028-l0017, 00c322b3ee04b419d1979f22-p000028-l0019 |

### round1

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 28 | 31 | 043b454a8c255b6690fd3777-p000008-l0020, 043b454a8c255b6690fd3777-p000061-l0030, 052a7a91dd9752b856b9fd8a-p000188-l0005, 143e78b5de2e6e784534ee0d-p000079-l0003, 241c524ed5b20f2baadf4b8b-p000082-l0043, 2c8742589d947f8d749c7ba2-p000040-l0013, 2f9e996ffbdaaa3b4a9dfdcf-p000082-l0007, 2f9e996ffbdaaa3b4a9dfdcf-p000141-l0018, 3a469aeb16cd49371b9dfc3d-p000015-l0007, 54a124e5cac779ec617e3ace-p000045-l0038, 5e99df8a3f2ecb56ba5c751b-p000156-l0002, 666498b9ed183dc88c1e8716-p000036-l0034, 686431e9a7fe04175e6e9be9-p000091-l0044, 723c450ea9bb07fc4cdf47f9-p000083-l0022, 7cb612112b4f28a4f704a9cb-p000081-l0071, 8f477fb59c9bc6957aadc800-p000119-l0025, 96bb7196d840fe7513c2ed43-p000024-l0030, b08a5423fb059fbb291900aa-p000213-l0003, b963a5d59be557e9eef8498b-p000065-l0065, bb8faba1e9b543fe5a1ce6dd-p000017-l0003 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 28 | 31 | 043b454a8c255b6690fd3777-p000008-l0020, 043b454a8c255b6690fd3777-p000061-l0030, 052a7a91dd9752b856b9fd8a-p000188-l0005, 143e78b5de2e6e784534ee0d-p000079-l0003, 241c524ed5b20f2baadf4b8b-p000082-l0043, 2c8742589d947f8d749c7ba2-p000040-l0013, 2f9e996ffbdaaa3b4a9dfdcf-p000082-l0007, 2f9e996ffbdaaa3b4a9dfdcf-p000141-l0018, 3a469aeb16cd49371b9dfc3d-p000015-l0007, 54a124e5cac779ec617e3ace-p000045-l0038, 5e99df8a3f2ecb56ba5c751b-p000156-l0002, 666498b9ed183dc88c1e8716-p000036-l0034, 686431e9a7fe04175e6e9be9-p000091-l0044, 723c450ea9bb07fc4cdf47f9-p000083-l0022, 7cb612112b4f28a4f704a9cb-p000081-l0071, 8f477fb59c9bc6957aadc800-p000119-l0025, 96bb7196d840fe7513c2ed43-p000024-l0030, b08a5423fb059fbb291900aa-p000213-l0003, b963a5d59be557e9eef8498b-p000065-l0065, bb8faba1e9b543fe5a1ce6dd-p000017-l0003 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 13 | 13 | 00c322b3ee04b419d1979f22-p000039-l0048, 042c93b2591368d437f27678-p000269-l0010, 2d29e5e76d90adc4cc1b093a-p000020-l0057, 453f156dc6352286456a08cb-p000209-l0034, 69846639273a60b797e93cb9-p000262-l0031, 8b231047fdbd96ec30e1eded-p000019-l0038, 8c926ffa3b1b2be056e56b7e-p000038-l0003, 8c926ffa3b1b2be056e56b7e-p000130-l0011, 9e60fbb6b1fc1da9f26b775e-p000175-l0011, b5f8ce187b707837e5669281-p000046-l0039, cc0e056392dd2ef4916b3e7d-p000039-l0002, eed91c3c88be77cac51e7629-p000070-l0015, f77a8c0084022edb7981fb15-p000075-l0079 |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 round2

Deletion HOLD lines: 4205; MOVE proposal lines: 5; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 2418 | 6370 | 0efd675a10c9a91816c7a41a-p000020-l0003, 0efd675a10c9a91816c7a41a-p000020-l0004, 0efd675a10c9a91816c7a41a-p000020-l0009, 0efd675a10c9a91816c7a41a-p000020-l0010, 0efd675a10c9a91816c7a41a-p000020-l0016, 0efd675a10c9a91816c7a41a-p000020-l0020, 0efd675a10c9a91816c7a41a-p000020-l0026, 0efd675a10c9a91816c7a41a-p000020-l0033, 0efd675a10c9a91816c7a41a-p000020-l0035, 0efd675a10c9a91816c7a41a-p000032-l0010, 0efd675a10c9a91816c7a41a-p000032-l0028, 0efd675a10c9a91816c7a41a-p000032-l0031, 0efd675a10c9a91816c7a41a-p000032-l0034, 0efd675a10c9a91816c7a41a-p000032-l0035, 0efd675a10c9a91816c7a41a-p000049-l0008, 0efd675a10c9a91816c7a41a-p000049-l0017, 0efd675a10c9a91816c7a41a-p000064-l0012, 0efd675a10c9a91816c7a41a-p000064-l0021, 0efd675a10c9a91816c7a41a-p000064-l0033, 0efd675a10c9a91816c7a41a-p000064-l0035 |
| apostrophe | 258 | 279 | 0efd675a10c9a91816c7a41a-p000049-l0025, 0efd675a10c9a91816c7a41a-p000064-l0015, 0efd675a10c9a91816c7a41a-p000079-l0026, 0efd675a10c9a91816c7a41a-p000079-l0028, 0efd675a10c9a91816c7a41a-p000139-l0007, 0efd675a10c9a91816c7a41a-p000170-l0035, 1182f94b107a4cc4ada574da-p000009-l0015, 1182f94b107a4cc4ada574da-p000009-l0016, 1182f94b107a4cc4ada574da-p000045-l0025, 1182f94b107a4cc4ada574da-p000054-l0014, 1182f94b107a4cc4ada574da-p000054-l0022, 1182f94b107a4cc4ada574da-p000060-l0026, 1182f94b107a4cc4ada574da-p000064-l0013, 32aae9fec147d3b483deb96e-p000042-l0050, 32aae9fec147d3b483deb96e-p000068-l0073, 32aae9fec147d3b483deb96e-p000084-l0049, 32aae9fec147d3b483deb96e-p000093-l0051, 32aae9fec147d3b483deb96e-p000101-l0018, 32aae9fec147d3b483deb96e-p000107-l0046, 3598ebd512fe5593fddcc4ed-p000017-l0082 |
| quote | 233 | 250 | 0efd675a10c9a91816c7a41a-p000079-l0006, 0efd675a10c9a91816c7a41a-p000079-l0016, 0efd675a10c9a91816c7a41a-p000079-l0021, 0efd675a10c9a91816c7a41a-p000186-l0004, 0efd675a10c9a91816c7a41a-p000186-l0011, 0efd675a10c9a91816c7a41a-p000200-l0003, 0efd675a10c9a91816c7a41a-p000200-l0023, 1182f94b107a4cc4ada574da-p000054-l0028, 1182f94b107a4cc4ada574da-p000054-l0039, 1182f94b107a4cc4ada574da-p000054-l0045, 1182f94b107a4cc4ada574da-p000060-l0024, 290a133b0e55593eb4ecdcfd-p000262-l0090, 290a133b0e55593eb4ecdcfd-p000288-l0009, 32aae9fec147d3b483deb96e-p000011-l0056, 32aae9fec147d3b483deb96e-p000019-l0017, 32aae9fec147d3b483deb96e-p000019-l0024, 32aae9fec147d3b483deb96e-p000019-l0063, 32aae9fec147d3b483deb96e-p000042-l0008, 32aae9fec147d3b483deb96e-p000084-l0068, 3598ebd512fe5593fddcc4ed-p000039-l0044 |
| keraia | 402 | 425 | 0efd675a10c9a91816c7a41a-p000049-l0013, 0efd675a10c9a91816c7a41a-p000049-l0016, 0efd675a10c9a91816c7a41a-p000049-l0019, 0efd675a10c9a91816c7a41a-p000049-l0034, 0efd675a10c9a91816c7a41a-p000064-l0033, 0efd675a10c9a91816c7a41a-p000156-l0025, 0efd675a10c9a91816c7a41a-p000156-l0029, 0efd675a10c9a91816c7a41a-p000156-l0032, 0efd675a10c9a91816c7a41a-p000156-l0034, 0efd675a10c9a91816c7a41a-p000170-l0023, 0efd675a10c9a91816c7a41a-p000186-l0019, 0efd675a10c9a91816c7a41a-p000186-l0022, 0efd675a10c9a91816c7a41a-p000200-l0006, 0efd675a10c9a91816c7a41a-p000200-l0013, 0efd675a10c9a91816c7a41a-p000200-l0015, 1182f94b107a4cc4ada574da-p000009-l0010, 1182f94b107a4cc4ada574da-p000017-l0025, 1182f94b107a4cc4ada574da-p000037-l0030, 1182f94b107a4cc4ada574da-p000037-l0042, 290a133b0e55593eb4ecdcfd-p000307-l0139 |
| other | 2395 | 23112 | 0efd675a10c9a91816c7a41a-p000020-l0006, 0efd675a10c9a91816c7a41a-p000020-l0009, 0efd675a10c9a91816c7a41a-p000020-l0014, 0efd675a10c9a91816c7a41a-p000020-l0024, 0efd675a10c9a91816c7a41a-p000020-l0026, 0efd675a10c9a91816c7a41a-p000020-l0034, 0efd675a10c9a91816c7a41a-p000020-l0035, 0efd675a10c9a91816c7a41a-p000032-l0012, 0efd675a10c9a91816c7a41a-p000032-l0013, 0efd675a10c9a91816c7a41a-p000032-l0035, 0efd675a10c9a91816c7a41a-p000049-l0011, 0efd675a10c9a91816c7a41a-p000049-l0013, 0efd675a10c9a91816c7a41a-p000049-l0016, 0efd675a10c9a91816c7a41a-p000049-l0025, 0efd675a10c9a91816c7a41a-p000049-l0034, 0efd675a10c9a91816c7a41a-p000049-l0036, 0efd675a10c9a91816c7a41a-p000079-l0008, 0efd675a10c9a91816c7a41a-p000079-l0010, 0efd675a10c9a91816c7a41a-p000079-l0016, 0efd675a10c9a91816c7a41a-p000079-l0025 |

### round2

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 14 | 14 | 39fbbdfd2c8030f211a318b7-p000138-l0003, 3c4393cb8164c820f7e7b38c-p000032-l0005, 6c0a582885e55adc7c535c48-p000107-l0020, 6d957fa757c72e1408f65dde-p000114-l0026, 7056dabdb0d8a5db4a0976f8-p000132-l0038, 827d2345ad77e5cdec320e80-p000006-l0009, 9dd010d6eb008870ea7c536c-p000050-l0031, 9dd010d6eb008870ea7c536c-p000054-l0008, b3c6afd03a5cab1b09b7d13e-p000036-l0063, b518f9f9b73fe9a3257fe2f0-p000078-l0012, c3468c02b6d929362f6e3fe7-p000176-l0039, dc390fceb64d9bb60a12d6b8-p000098-l0015, ee2ae82a5d56b54859d7385b-p000177-l0006, ee2ae82a5d56b54859d7385b-p000251-l0006 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 14 | 14 | 39fbbdfd2c8030f211a318b7-p000138-l0003, 3c4393cb8164c820f7e7b38c-p000032-l0005, 6c0a582885e55adc7c535c48-p000107-l0020, 6d957fa757c72e1408f65dde-p000114-l0026, 7056dabdb0d8a5db4a0976f8-p000132-l0038, 827d2345ad77e5cdec320e80-p000006-l0009, 9dd010d6eb008870ea7c536c-p000050-l0031, 9dd010d6eb008870ea7c536c-p000054-l0008, b3c6afd03a5cab1b09b7d13e-p000036-l0063, b518f9f9b73fe9a3257fe2f0-p000078-l0012, c3468c02b6d929362f6e3fe7-p000176-l0039, dc390fceb64d9bb60a12d6b8-p000098-l0015, ee2ae82a5d56b54859d7385b-p000177-l0006, ee2ae82a5d56b54859d7385b-p000251-l0006 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 1 | 1 | dc390fceb64d9bb60a12d6b8-p000060-l0005 |
| insertions_by_class/quote | 2 | 2 | dc390fceb64d9bb60a12d6b8-p000082-l0002, dc390fceb64d9bb60a12d6b8-p000127-l0007 |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 vouli

Deletion HOLD lines: 5478; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 3406 | 10648 | 0271e3cae771-p000001-l0002, 0271e3cae771-p000001-l0036, 0271e3cae771-p000002-l0013, 0271e3cae771-p000002-l0019, 0271e3cae771-p000002-l0031, 0271e3cae771-p000003-l0011, 0271e3cae771-p000003-l0017, 0271e3cae771-p000003-l0034, 0271e3cae771-p000004-l0008, 0271e3cae771-p000004-l0010, 0271e3cae771-p000004-l0013, 0271e3cae771-p000005-l0002, 0271e3cae771-p000005-l0012, 0271e3cae771-p000005-l0024, 0271e3cae771-p000006-l0008, 0271e3cae771-p000006-l0016, 0271e3cae771-p000006-l0024, 0271e3cae771-p000006-l0025, 0271e3cae771-p000007-l0024, 0271e3cae771-p000007-l0029 |
| apostrophe | 278 | 292 | 0271e3cae771-p000001-l0036, 0271e3cae771-p000004-l0037, 0271e3cae771-p000006-l0030, 07bc68f92367-p000004-l0004, 0e777453c7a8-p000001-l0073, 0e777453c7a8-p000001-l0091, 0e777453c7a8-p000001-l0095, 0e777453c7a8-p000002-l0077, 0e777453c7a8-p000002-l0104, 0e777453c7a8-p000002-l0109, 0e777453c7a8-p000002-l0111, 0e777453c7a8-p000003-l0007, 0e777453c7a8-p000003-l0017, 0e777453c7a8-p000003-l0028, 0e777453c7a8-p000003-l0115, 1365c8bbb0a8-p000001-l0017, 1365c8bbb0a8-p000012-l0058, 182619a5630d-p000001-l0064, 182619a5630d-p000001-l0081, 182619a5630d-p000001-l0083 |
| quote | 245 | 248 | 0271e3cae771-p000002-l0013, 07bc68f92367-p000003-l0006, 0e777453c7a8-p000001-l0001, 18167bc1e4a8-p000002-l0016, 182619a5630d-p000002-l0065, 182619a5630d-p000005-l0051, 182619a5630d-p000009-l0059, 182619a5630d-p000009-l0060, 182619a5630d-p000009-l0061, 182619a5630d-p000009-l0062, 1f485870372f-p000001-l0002, 1f485870372f-p000003-l0010, 1f485870372f-p000003-l0017, 1f485870372f-p000010-l0016, 1f485870372f-p000010-l0017, 1f485870372f-p000010-l0018, 1ff160a5dd27-p000001-l0008, 1ff160a5dd27-p000001-l0009, 1ff160a5dd27-p000001-l0011, 1ff160a5dd27-p000009-l0026 |
| keraia | 508 | 558 | 0e777453c7a8-p000001-l0020, 0e777453c7a8-p000001-l0030, 0e777453c7a8-p000001-l0072, 0e777453c7a8-p000001-l0075, 0e777453c7a8-p000001-l0078, 0e777453c7a8-p000001-l0084, 0e777453c7a8-p000001-l0091, 0e777453c7a8-p000001-l0094, 0e777453c7a8-p000002-l0009, 0e777453c7a8-p000002-l0010, 0e777453c7a8-p000002-l0014, 0e777453c7a8-p000002-l0019, 0e777453c7a8-p000002-l0022, 0e777453c7a8-p000002-l0026, 0e777453c7a8-p000002-l0028, 0e777453c7a8-p000002-l0032, 0e777453c7a8-p000002-l0041, 0e777453c7a8-p000002-l0043, 0e777453c7a8-p000002-l0047, 0e777453c7a8-p000002-l0056 |
| other | 2899 | 41281 | 0271e3cae771-p000001-l0015, 0271e3cae771-p000001-l0028, 0271e3cae771-p000001-l0030, 0271e3cae771-p000001-l0036, 0271e3cae771-p000002-l0013, 0271e3cae771-p000002-l0015, 0271e3cae771-p000002-l0019, 0271e3cae771-p000002-l0031, 0271e3cae771-p000003-l0011, 0271e3cae771-p000003-l0036, 0271e3cae771-p000003-l0037, 0271e3cae771-p000004-l0013, 0271e3cae771-p000004-l0023, 0271e3cae771-p000004-l0037, 0271e3cae771-p000004-l0040, 0271e3cae771-p000005-l0002, 0271e3cae771-p000005-l0003, 0271e3cae771-p000006-l0009, 0271e3cae771-p000006-l0030, 0271e3cae771-p000006-l0033 |

### vouli

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 5 | 5 | 23e59c57bd30-p000003-l0032, 8cd0e8c1f0e5-p000001-l0025, 91252504a906-p000025-l0013, da9a31d7669d-p000025-l0003, f4e509d76b55-p000004-l0010 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 5 | 5 | 23e59c57bd30-p000003-l0032, 8cd0e8c1f0e5-p000001-l0025, 91252504a906-p000025-l0013, da9a31d7669d-p000025-l0003, f4e509d76b55-p000004-l0010 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 3 | 3 | 971b6ed3092a-p000004-l0002, aed4abe1314b-p000002-l0017, d9b7dfa900e3-p000003-l0034 |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |
## FULL

| Wave | Lines | Corrected status | Real mark-correction lines | Real mark lines with single-source deletion | Share of real mark-correction lines |
|---|---:|---:|---:|---:|---:|
| ALL | 124669 | 76 | 52 | 0 | 0.000000% |
| mixed | 13227 | 13 | 8 | 0 | 0.000000% |
| openarchives | 235 | 0 | 0 | 0 | 0.000000% |
| parliament | 27224 | 3 | 2 | 0 | 0.000000% |
| round1 | 43869 | 38 | 26 | 0 | 0.000000% |
| round2 | 17026 | 14 | 11 | 0 | 0.000000% |
| vouli | 23088 | 8 | 5 | 0 | 0.000000% |

### SF6 ALL

Deletion HOLD lines: 33060; MOVE proposal lines: 9; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 20459 | 59885 | 00c322b3ee04b419d1979f22-p000015-l0034, 00c322b3ee04b419d1979f22-p000015-l0039, 00c322b3ee04b419d1979f22-p000015-l0041, 00c322b3ee04b419d1979f22-p000015-l0046, 00c322b3ee04b419d1979f22-p000015-l0068, 00c322b3ee04b419d1979f22-p000015-l0069, 00c322b3ee04b419d1979f22-p000015-l0073, 00c322b3ee04b419d1979f22-p000015-l0076, 00c322b3ee04b419d1979f22-p000028-l0003, 00c322b3ee04b419d1979f22-p000028-l0009, 00c322b3ee04b419d1979f22-p000028-l0010, 00c322b3ee04b419d1979f22-p000028-l0011, 00c322b3ee04b419d1979f22-p000028-l0012, 00c322b3ee04b419d1979f22-p000028-l0013, 00c322b3ee04b419d1979f22-p000028-l0014, 00c322b3ee04b419d1979f22-p000028-l0016, 00c322b3ee04b419d1979f22-p000028-l0018, 00c322b3ee04b419d1979f22-p000028-l0019, 00c322b3ee04b419d1979f22-p000028-l0020, 00c322b3ee04b419d1979f22-p000028-l0021 |
| apostrophe | 1580 | 1685 | 00c322b3ee04b419d1979f22-p000015-l0059, 00c322b3ee04b419d1979f22-p000015-l0079, 00c322b3ee04b419d1979f22-p000028-l0011, 00c322b3ee04b419d1979f22-p000028-l0025, 00c322b3ee04b419d1979f22-p000028-l0027, 00c322b3ee04b419d1979f22-p000103-l0011, 00c322b3ee04b419d1979f22-p000115-l0068, 00c322b3ee04b419d1979f22-p000142-l0005, 00c322b3ee04b419d1979f22-p000142-l0016, 0271e3cae771-p000001-l0036, 0271e3cae771-p000004-l0037, 0271e3cae771-p000006-l0030, 042c93b2591368d437f27678-p000148-l0003, 042c93b2591368d437f27678-p000245-l0022, 043b454a8c255b6690fd3777-p000013-l0053, 043b454a8c255b6690fd3777-p000027-l0033, 043b454a8c255b6690fd3777-p000031-l0006, 043b454a8c255b6690fd3777-p000040-l0051, 043b454a8c255b6690fd3777-p000044-l0062, 043b454a8c255b6690fd3777-p000054-l0063 |
| quote | 1953 | 2000 | 00c322b3ee04b419d1979f22-p000015-l0069, 00c322b3ee04b419d1979f22-p000028-l0054, 00c322b3ee04b419d1979f22-p000028-l0070, 00c322b3ee04b419d1979f22-p000055-l0002, 00c322b3ee04b419d1979f22-p000055-l0003, 00c322b3ee04b419d1979f22-p000055-l0025, 00c322b3ee04b419d1979f22-p000055-l0026, 00c322b3ee04b419d1979f22-p000055-l0027, 00c322b3ee04b419d1979f22-p000055-l0028, 00c322b3ee04b419d1979f22-p000055-l0030, 00c322b3ee04b419d1979f22-p000055-l0043, 00c322b3ee04b419d1979f22-p000055-l0050, 00c322b3ee04b419d1979f22-p000078-l0069, 00c322b3ee04b419d1979f22-p000093-l0006, 00c322b3ee04b419d1979f22-p000093-l0040, 00c322b3ee04b419d1979f22-p000093-l0041, 00c322b3ee04b419d1979f22-p000093-l0042, 00c322b3ee04b419d1979f22-p000093-l0046, 00c322b3ee04b419d1979f22-p000093-l0053, 00c322b3ee04b419d1979f22-p000115-l0024 |
| keraia | 1652 | 1786 | 00c322b3ee04b419d1979f22-p000055-l0006, 00c322b3ee04b419d1979f22-p000055-l0011, 00c322b3ee04b419d1979f22-p000115-l0019, 00c322b3ee04b419d1979f22-p000129-l0037, 00c322b3ee04b419d1979f22-p000166-l0040, 042c93b2591368d437f27678-p000075-l0036, 042c93b2591368d437f27678-p000148-l0011, 043b454a8c255b6690fd3777-p000019-l0042, 043b454a8c255b6690fd3777-p000019-l0063, 043b454a8c255b6690fd3777-p000019-l0079, 0590d5cb-p000007-l0092, 07dc0ec3a36ef8d4433de416-p000083-l0036, 0907df739607faca673d2169-p000033-l0007, 0b33fccd-p000023-l0126, 0b33fccd-p000032-l0044, 0cb3f67240837f77ee728005-p000005-l0042, 0cb3f67240837f77ee728005-p000005-l0044, 0cb3f67240837f77ee728005-p000005-l0049, 0cb3f67240837f77ee728005-p000005-l0050, 0cb3f67240837f77ee728005-p000019-l0052 |
| other | 18993 | 226929 | 00c322b3ee04b419d1979f22-p000015-l0009, 00c322b3ee04b419d1979f22-p000015-l0035, 00c322b3ee04b419d1979f22-p000015-l0037, 00c322b3ee04b419d1979f22-p000015-l0041, 00c322b3ee04b419d1979f22-p000015-l0046, 00c322b3ee04b419d1979f22-p000015-l0051, 00c322b3ee04b419d1979f22-p000015-l0059, 00c322b3ee04b419d1979f22-p000015-l0069, 00c322b3ee04b419d1979f22-p000015-l0073, 00c322b3ee04b419d1979f22-p000015-l0076, 00c322b3ee04b419d1979f22-p000015-l0081, 00c322b3ee04b419d1979f22-p000028-l0003, 00c322b3ee04b419d1979f22-p000028-l0010, 00c322b3ee04b419d1979f22-p000028-l0011, 00c322b3ee04b419d1979f22-p000028-l0012, 00c322b3ee04b419d1979f22-p000028-l0013, 00c322b3ee04b419d1979f22-p000028-l0014, 00c322b3ee04b419d1979f22-p000028-l0016, 00c322b3ee04b419d1979f22-p000028-l0017, 00c322b3ee04b419d1979f22-p000028-l0019 |

### ALL

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 52 | 57 | 043b454a8c255b6690fd3777-p000008-l0020, 043b454a8c255b6690fd3777-p000061-l0030, 052a7a91dd9752b856b9fd8a-p000188-l0005, 143e78b5de2e6e784534ee0d-p000079-l0003, 23e59c57bd30-p000003-l0032, 241c524ed5b20f2baadf4b8b-p000082-l0043, 2c8742589d947f8d749c7ba2-p000040-l0013, 2f9e996ffbdaaa3b4a9dfdcf-p000082-l0007, 2f9e996ffbdaaa3b4a9dfdcf-p000141-l0018, 341f77df7fe3f09264ceee79-p000004-l0017, 39fbbdfd2c8030f211a318b7-p000138-l0003, 3c4393cb8164c820f7e7b38c-p000032-l0005, 54a124e5cac779ec617e3ace-p000045-l0038, 5e99df8a3f2ecb56ba5c751b-p000156-l0002, 666498b9ed183dc88c1e8716-p000036-l0034, 686431e9a7fe04175e6e9be9-p000091-l0044, 6c0a582885e55adc7c535c48-p000107-l0020, 6d957fa757c72e1408f65dde-p000114-l0026, 723c450ea9bb07fc4cdf47f9-p000083-l0022, 7cb612112b4f28a4f704a9cb-p000081-l0071 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 52 | 57 | 043b454a8c255b6690fd3777-p000008-l0020, 043b454a8c255b6690fd3777-p000061-l0030, 052a7a91dd9752b856b9fd8a-p000188-l0005, 143e78b5de2e6e784534ee0d-p000079-l0003, 23e59c57bd30-p000003-l0032, 241c524ed5b20f2baadf4b8b-p000082-l0043, 2c8742589d947f8d749c7ba2-p000040-l0013, 2f9e996ffbdaaa3b4a9dfdcf-p000082-l0007, 2f9e996ffbdaaa3b4a9dfdcf-p000141-l0018, 341f77df7fe3f09264ceee79-p000004-l0017, 39fbbdfd2c8030f211a318b7-p000138-l0003, 3c4393cb8164c820f7e7b38c-p000032-l0005, 54a124e5cac779ec617e3ace-p000045-l0038, 5e99df8a3f2ecb56ba5c751b-p000156-l0002, 666498b9ed183dc88c1e8716-p000036-l0034, 686431e9a7fe04175e6e9be9-p000091-l0044, 6c0a582885e55adc7c535c48-p000107-l0020, 6d957fa757c72e1408f65dde-p000114-l0026, 723c450ea9bb07fc4cdf47f9-p000083-l0022, 7cb612112b4f28a4f704a9cb-p000081-l0071 |
| insertions_by_class/numeral_keraia | 1 | 1 | 70e0a3447310acfc3f8dddf3-p000254-l0006 |
| insertions_by_class/elision_apostrophe | 1 | 1 | dc390fceb64d9bb60a12d6b8-p000060-l0005 |
| insertions_by_class/quote | 22 | 22 | 00c322b3ee04b419d1979f22-p000039-l0048, 042c93b2591368d437f27678-p000269-l0010, 12493332097bacc2a62b4d9a-p000036-l0008, 1c13bd49225f6fcf7dcca5a0-p000036-l0007, 2d29e5e76d90adc4cc1b093a-p000020-l0057, 453f156dc6352286456a08cb-p000209-l0034, 69846639273a60b797e93cb9-p000262-l0031, 7aea9867-p000038-l0130, 8b231047fdbd96ec30e1eded-p000019-l0038, 8c926ffa3b1b2be056e56b7e-p000038-l0003, 8c926ffa3b1b2be056e56b7e-p000130-l0011, 971b6ed3092a-p000004-l0002, 9e60fbb6b1fc1da9f26b775e-p000175-l0011, aed4abe1314b-p000002-l0017, b5f8ce187b707837e5669281-p000046-l0039, c57e3067ed37cedf17f285e6-p000044-l0006, cc0e056392dd2ef4916b3e7d-p000039-l0002, d0eda948e5b1f3632f8687fb-p000311-l0038, d9b7dfa900e3-p000003-l0034, dc390fceb64d9bb60a12d6b8-p000082-l0002 |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 mixed

Deletion HOLD lines: 3212; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 1937 | 5388 | 0a4bc4314e492706bcc0bf44-p000008-l0010, 0a4bc4314e492706bcc0bf44-p000008-l0023, 0a4bc4314e492706bcc0bf44-p000008-l0024, 0a4bc4314e492706bcc0bf44-p000008-l0025, 0a4bc4314e492706bcc0bf44-p000011-l0002, 0a4bc4314e492706bcc0bf44-p000011-l0009, 0a4bc4314e492706bcc0bf44-p000011-l0013, 0a4bc4314e492706bcc0bf44-p000011-l0021, 0a4bc4314e492706bcc0bf44-p000011-l0022, 0a4bc4314e492706bcc0bf44-p000011-l0034, 0a4bc4314e492706bcc0bf44-p000011-l0035, 0a4bc4314e492706bcc0bf44-p000011-l0038, 0a4bc4314e492706bcc0bf44-p000011-l0041, 0a4bc4314e492706bcc0bf44-p000014-l0009, 0a4bc4314e492706bcc0bf44-p000014-l0011, 0a4bc4314e492706bcc0bf44-p000014-l0013, 0a4bc4314e492706bcc0bf44-p000014-l0026, 0a4bc4314e492706bcc0bf44-p000014-l0035, 0a4bc4314e492706bcc0bf44-p000019-l0013, 0a4bc4314e492706bcc0bf44-p000019-l0028 |
| apostrophe | 162 | 166 | 0a4bc4314e492706bcc0bf44-p000008-l0023, 0a4bc4314e492706bcc0bf44-p000019-l0012, 0a4bc4314e492706bcc0bf44-p000019-l0013, 0a4bc4314e492706bcc0bf44-p000046-l0035, 12493332097bacc2a62b4d9a-p000026-l0009, 12493332097bacc2a62b4d9a-p000046-l0011, 1c13bd49225f6fcf7dcca5a0-p000036-l0002, 1c13bd49225f6fcf7dcca5a0-p000081-l0009, 1c13bd49225f6fcf7dcca5a0-p000115-l0013, 1c13bd49225f6fcf7dcca5a0-p000125-l0008, 3249d506364999770e38aeef-p000044-l0022, 3249d506364999770e38aeef-p000044-l0026, 3249d506364999770e38aeef-p000099-l0013, 3249d506364999770e38aeef-p000109-l0009, 3249d506364999770e38aeef-p000130-l0052, 341f77df7fe3f09264ceee79-p000006-l0035, 341f77df7fe3f09264ceee79-p000015-l0026, 34d2967a06064249e6ebc895-p000077-l0015, 34d2967a06064249e6ebc895-p000139-l0024, 37a9179b-p000113-l0003 |
| quote | 330 | 332 | 0a4bc4314e492706bcc0bf44-p000046-l0006, 12493332097bacc2a62b4d9a-p000007-l0018, 12493332097bacc2a62b4d9a-p000031-l0031, 12493332097bacc2a62b4d9a-p000046-l0029, 137e9af6a0045d5746e26efa-p000003-l0008, 137e9af6a0045d5746e26efa-p000006-l0022, 137e9af6a0045d5746e26efa-p000008-l0010, 137e9af6a0045d5746e26efa-p000008-l0021, 1c13bd49225f6fcf7dcca5a0-p000115-l0013, 3249d506364999770e38aeef-p000011-l0019, 3249d506364999770e38aeef-p000011-l0020, 3249d506364999770e38aeef-p000011-l0021, 3249d506364999770e38aeef-p000011-l0022, 3249d506364999770e38aeef-p000011-l0023, 3249d506364999770e38aeef-p000011-l0024, 3249d506364999770e38aeef-p000011-l0025, 3249d506364999770e38aeef-p000011-l0026, 3249d506364999770e38aeef-p000011-l0027, 3249d506364999770e38aeef-p000011-l0028, 3249d506364999770e38aeef-p000011-l0029 |
| keraia | 117 | 125 | 12493332097bacc2a62b4d9a-p000024-l0022, 12493332097bacc2a62b4d9a-p000024-l0025, 12493332097bacc2a62b4d9a-p000026-l0029, 12493332097bacc2a62b4d9a-p000026-l0031, 12493332097bacc2a62b4d9a-p000031-l0012, 12493332097bacc2a62b4d9a-p000031-l0017, 12493332097bacc2a62b4d9a-p000041-l0017, 12493332097bacc2a62b4d9a-p000046-l0027, 3249d506364999770e38aeef-p000044-l0022, 3249d506364999770e38aeef-p000044-l0026, 3249d506364999770e38aeef-p000054-l0040, 3249d506364999770e38aeef-p000067-l0044, 3249d506364999770e38aeef-p000099-l0033, 3249d506364999770e38aeef-p000109-l0052, 3249d506364999770e38aeef-p000130-l0034, 341f77df7fe3f09264ceee79-p000004-l0029, 341f77df7fe3f09264ceee79-p000021-l0025, 341f77df7fe3f09264ceee79-p000021-l0028, 4a34388c9884fda746d2a8cd-p000020-l0008, 4a34388c9884fda746d2a8cd-p000020-l0014 |
| other | 1854 | 19982 | 0a4bc4314e492706bcc0bf44-p000008-l0023, 0a4bc4314e492706bcc0bf44-p000008-l0024, 0a4bc4314e492706bcc0bf44-p000008-l0025, 0a4bc4314e492706bcc0bf44-p000011-l0007, 0a4bc4314e492706bcc0bf44-p000011-l0009, 0a4bc4314e492706bcc0bf44-p000011-l0017, 0a4bc4314e492706bcc0bf44-p000011-l0034, 0a4bc4314e492706bcc0bf44-p000011-l0035, 0a4bc4314e492706bcc0bf44-p000011-l0038, 0a4bc4314e492706bcc0bf44-p000011-l0041, 0a4bc4314e492706bcc0bf44-p000014-l0026, 0a4bc4314e492706bcc0bf44-p000019-l0004, 0a4bc4314e492706bcc0bf44-p000019-l0010, 0a4bc4314e492706bcc0bf44-p000019-l0012, 0a4bc4314e492706bcc0bf44-p000019-l0013, 0a4bc4314e492706bcc0bf44-p000019-l0018, 0a4bc4314e492706bcc0bf44-p000019-l0022, 0a4bc4314e492706bcc0bf44-p000019-l0028, 0a4bc4314e492706bcc0bf44-p000019-l0032, 0a4bc4314e492706bcc0bf44-p000019-l0036 |

### mixed

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 8 | 10 | 341f77df7fe3f09264ceee79-p000004-l0017, 8a482dd5cb341a70d157d5c4-p000273-l0024, b5076e8734ba287d549d79b5-p000010-l0026, c57e3067ed37cedf17f285e6-p000009-l0022, d0eda948e5b1f3632f8687fb-p000620-l0005, d0eda948e5b1f3632f8687fb-p000620-l0016, d0eda948e5b1f3632f8687fb-p000773-l0088, e11826423ecefe41dd940b28-p000057-l0025 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 8 | 10 | 341f77df7fe3f09264ceee79-p000004-l0017, 8a482dd5cb341a70d157d5c4-p000273-l0024, b5076e8734ba287d549d79b5-p000010-l0026, c57e3067ed37cedf17f285e6-p000009-l0022, d0eda948e5b1f3632f8687fb-p000620-l0005, d0eda948e5b1f3632f8687fb-p000620-l0016, d0eda948e5b1f3632f8687fb-p000773-l0088, e11826423ecefe41dd940b28-p000057-l0025 |
| insertions_by_class/numeral_keraia | 1 | 1 | 70e0a3447310acfc3f8dddf3-p000254-l0006 |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 4 | 4 | 12493332097bacc2a62b4d9a-p000036-l0008, 1c13bd49225f6fcf7dcca5a0-p000036-l0007, c57e3067ed37cedf17f285e6-p000044-l0006, d0eda948e5b1f3632f8687fb-p000311-l0038 |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 openarchives

Deletion HOLD lines: 23; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 7 | 9 | 0fead7c5-p000008-l0061, 0fead7c5-p000008-l0095, 0fead7c5-p000010-l0001, 0fead7c5-p000010-l0011, 0fead7c5-p000010-l0030, 0fead7c5-p000010-l0040, 0fead7c5-p000010-l0047 |
| apostrophe | 1 | 1 | 0fead7c5-p000004-l0038 |
| quote | 0 | 0 |  |
| keraia | 10 | 13 | 0fead7c5-p000004-l0035, 0fead7c5-p000004-l0038, 0fead7c5-p000004-l0041, 0fead7c5-p000004-l0044, 0fead7c5-p000004-l0047, a4c40997-p000007-l0013, a4c40997-p000007-l0018, a4c40997-p000007-l0028, a4c40997-p000017-l0040, a4c40997-p000066-l0013 |
| other | 9 | 52 | 0fead7c5-p000004-l0038, 0fead7c5-p000008-l0003, 0fead7c5-p000008-l0028, 0fead7c5-p000010-l0001, 0fead7c5-p000010-l0040, a4c40997-p000017-l0018, a4c40997-p000023-l0001, a4c40997-p000035-l0010, a4c40997-p000035-l0017 |

### openarchives

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 0 | 0 |  |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 0 | 0 |  |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 parliament

Deletion HOLD lines: 8007; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 5381 | 13124 | 01c618de-p000024-l0060, 0590d5cb-p000003-l0104, 0590d5cb-p000007-l0052, 0590d5cb-p000007-l0092, 0590d5cb-p000009-l0044, 0590d5cb-p000012-l0016, 0590d5cb-p000012-l0020, 0590d5cb-p000012-l0117, 0590d5cb-p000013-l0006, 0590d5cb-p000015-l0045, 0590d5cb-p000017-l0033, 0590d5cb-p000021-l0007, 0590d5cb-p000023-l0021, 0590d5cb-p000024-l0005, 0590d5cb-p000024-l0025, 0b33fccd-p000008-l0006, 0b33fccd-p000008-l0007, 0b33fccd-p000008-l0016, 0b33fccd-p000008-l0021, 0b33fccd-p000008-l0024 |
| apostrophe | 144 | 146 | 0b33fccd-p000008-l0053, 0b33fccd-p000008-l0091, 0b33fccd-p000008-l0092, 0b33fccd-p000010-l0011, 0b33fccd-p000010-l0060, 0b33fccd-p000012-l0094, 0b33fccd-p000017-l0078, 0b33fccd-p000021-l0118, 0b33fccd-p000027-l0063, 133c1ea6-p000003-l0066, 133c1ea6-p000003-l0108, 133c1ea6-p000009-l0113, 133c1ea6-p000010-l0022, 133c1ea6-p000014-l0021, 133c1ea6-p000020-l0119, 13dcc39a-p000008-l0124, 13dcc39a-p000012-l0070, 13dcc39a-p000020-l0059, 13dcc39a-p000023-l0095, 13dcc39a-p000026-l0138 |
| quote | 230 | 236 | 01c618de-p000013-l0134, 0b33fccd-p000008-l0114, 0b33fccd-p000012-l0093, 0b33fccd-p000023-l0113, 133c1ea6-p000003-l0023, 133c1ea6-p000003-l0041, 133c1ea6-p000003-l0094, 133c1ea6-p000003-l0117, 133c1ea6-p000007-l0023, 133c1ea6-p000007-l0053, 133c1ea6-p000007-l0076, 133c1ea6-p000007-l0086, 133c1ea6-p000007-l0102, 133c1ea6-p000007-l0117, 133c1ea6-p000009-l0025, 133c1ea6-p000009-l0038, 133c1ea6-p000009-l0071, 133c1ea6-p000009-l0082, 133c1ea6-p000009-l0106, 133c1ea6-p000009-l0133 |
| keraia | 104 | 110 | 0590d5cb-p000007-l0092, 0b33fccd-p000023-l0126, 0b33fccd-p000032-l0044, 133c1ea6-p000007-l0007, 133c1ea6-p000007-l0121, 133c1ea6-p000009-l0002, 133c1ea6-p000009-l0009, 133c1ea6-p000010-l0105, 133c1ea6-p000010-l0116, 133c1ea6-p000014-l0080, 133c1ea6-p000019-l0114, 1a035976-p000014-l0024, 1a035976-p000014-l0026, 1a035976-p000016-l0087, 1a035976-p000016-l0088, 1a035976-p000022-l0037, 1a035976-p000022-l0083, 3455d0e7-p000023-l0024, 48a58eb5-p000010-l0139, 52b46e46-p000005-l0099 |
| other | 4338 | 45081 | 01c618de-p000013-l0134, 0590d5cb-p000012-l0016, 0590d5cb-p000012-l0020, 0590d5cb-p000015-l0045, 0590d5cb-p000017-l0033, 0b33fccd-p000008-l0006, 0b33fccd-p000008-l0015, 0b33fccd-p000008-l0019, 0b33fccd-p000008-l0023, 0b33fccd-p000008-l0024, 0b33fccd-p000008-l0025, 0b33fccd-p000008-l0031, 0b33fccd-p000008-l0044, 0b33fccd-p000008-l0053, 0b33fccd-p000008-l0058, 0b33fccd-p000008-l0061, 0b33fccd-p000008-l0064, 0b33fccd-p000008-l0067, 0b33fccd-p000008-l0078, 0b33fccd-p000008-l0079 |

### parliament

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 2 | 2 | aac90dd4-p000017-l0024, f36aba38-p000005-l0015 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 2 | 2 | aac90dd4-p000017-l0024, f36aba38-p000005-l0015 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 1 | 1 | 7aea9867-p000038-l0130 |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 round1

Deletion HOLD lines: 12135; MOVE proposal lines: 4; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 7310 | 24346 | 00c322b3ee04b419d1979f22-p000015-l0034, 00c322b3ee04b419d1979f22-p000015-l0039, 00c322b3ee04b419d1979f22-p000015-l0041, 00c322b3ee04b419d1979f22-p000015-l0046, 00c322b3ee04b419d1979f22-p000015-l0068, 00c322b3ee04b419d1979f22-p000015-l0069, 00c322b3ee04b419d1979f22-p000015-l0073, 00c322b3ee04b419d1979f22-p000015-l0076, 00c322b3ee04b419d1979f22-p000028-l0003, 00c322b3ee04b419d1979f22-p000028-l0009, 00c322b3ee04b419d1979f22-p000028-l0010, 00c322b3ee04b419d1979f22-p000028-l0011, 00c322b3ee04b419d1979f22-p000028-l0012, 00c322b3ee04b419d1979f22-p000028-l0013, 00c322b3ee04b419d1979f22-p000028-l0014, 00c322b3ee04b419d1979f22-p000028-l0016, 00c322b3ee04b419d1979f22-p000028-l0018, 00c322b3ee04b419d1979f22-p000028-l0019, 00c322b3ee04b419d1979f22-p000028-l0020, 00c322b3ee04b419d1979f22-p000028-l0021 |
| apostrophe | 737 | 801 | 00c322b3ee04b419d1979f22-p000015-l0059, 00c322b3ee04b419d1979f22-p000015-l0079, 00c322b3ee04b419d1979f22-p000028-l0011, 00c322b3ee04b419d1979f22-p000028-l0025, 00c322b3ee04b419d1979f22-p000028-l0027, 00c322b3ee04b419d1979f22-p000103-l0011, 00c322b3ee04b419d1979f22-p000115-l0068, 00c322b3ee04b419d1979f22-p000142-l0005, 00c322b3ee04b419d1979f22-p000142-l0016, 042c93b2591368d437f27678-p000148-l0003, 042c93b2591368d437f27678-p000245-l0022, 043b454a8c255b6690fd3777-p000013-l0053, 043b454a8c255b6690fd3777-p000027-l0033, 043b454a8c255b6690fd3777-p000031-l0006, 043b454a8c255b6690fd3777-p000040-l0051, 043b454a8c255b6690fd3777-p000044-l0062, 043b454a8c255b6690fd3777-p000054-l0063, 052a7a91dd9752b856b9fd8a-p000114-l0008, 052a7a91dd9752b856b9fd8a-p000140-l0048, 0550c3c52f2b388255690d5a-p000027-l0008 |
| quote | 915 | 934 | 00c322b3ee04b419d1979f22-p000015-l0069, 00c322b3ee04b419d1979f22-p000028-l0054, 00c322b3ee04b419d1979f22-p000028-l0070, 00c322b3ee04b419d1979f22-p000055-l0002, 00c322b3ee04b419d1979f22-p000055-l0003, 00c322b3ee04b419d1979f22-p000055-l0025, 00c322b3ee04b419d1979f22-p000055-l0026, 00c322b3ee04b419d1979f22-p000055-l0027, 00c322b3ee04b419d1979f22-p000055-l0028, 00c322b3ee04b419d1979f22-p000055-l0030, 00c322b3ee04b419d1979f22-p000055-l0043, 00c322b3ee04b419d1979f22-p000055-l0050, 00c322b3ee04b419d1979f22-p000078-l0069, 00c322b3ee04b419d1979f22-p000093-l0006, 00c322b3ee04b419d1979f22-p000093-l0040, 00c322b3ee04b419d1979f22-p000093-l0041, 00c322b3ee04b419d1979f22-p000093-l0042, 00c322b3ee04b419d1979f22-p000093-l0046, 00c322b3ee04b419d1979f22-p000093-l0053, 00c322b3ee04b419d1979f22-p000115-l0024 |
| keraia | 511 | 555 | 00c322b3ee04b419d1979f22-p000055-l0006, 00c322b3ee04b419d1979f22-p000055-l0011, 00c322b3ee04b419d1979f22-p000115-l0019, 00c322b3ee04b419d1979f22-p000129-l0037, 00c322b3ee04b419d1979f22-p000166-l0040, 042c93b2591368d437f27678-p000075-l0036, 042c93b2591368d437f27678-p000148-l0011, 043b454a8c255b6690fd3777-p000019-l0042, 043b454a8c255b6690fd3777-p000019-l0063, 043b454a8c255b6690fd3777-p000019-l0079, 07dc0ec3a36ef8d4433de416-p000083-l0036, 0907df739607faca673d2169-p000033-l0007, 0cb3f67240837f77ee728005-p000005-l0042, 0cb3f67240837f77ee728005-p000005-l0044, 0cb3f67240837f77ee728005-p000005-l0049, 0cb3f67240837f77ee728005-p000005-l0050, 0cb3f67240837f77ee728005-p000019-l0052, 0cb3f67240837f77ee728005-p000019-l0056, 10349bf796b8cd19c7415595-p000121-l0009, 10349bf796b8cd19c7415595-p000157-l0029 |
| other | 7498 | 97421 | 00c322b3ee04b419d1979f22-p000015-l0009, 00c322b3ee04b419d1979f22-p000015-l0035, 00c322b3ee04b419d1979f22-p000015-l0037, 00c322b3ee04b419d1979f22-p000015-l0041, 00c322b3ee04b419d1979f22-p000015-l0046, 00c322b3ee04b419d1979f22-p000015-l0051, 00c322b3ee04b419d1979f22-p000015-l0059, 00c322b3ee04b419d1979f22-p000015-l0069, 00c322b3ee04b419d1979f22-p000015-l0073, 00c322b3ee04b419d1979f22-p000015-l0076, 00c322b3ee04b419d1979f22-p000015-l0081, 00c322b3ee04b419d1979f22-p000028-l0003, 00c322b3ee04b419d1979f22-p000028-l0010, 00c322b3ee04b419d1979f22-p000028-l0011, 00c322b3ee04b419d1979f22-p000028-l0012, 00c322b3ee04b419d1979f22-p000028-l0013, 00c322b3ee04b419d1979f22-p000028-l0014, 00c322b3ee04b419d1979f22-p000028-l0016, 00c322b3ee04b419d1979f22-p000028-l0017, 00c322b3ee04b419d1979f22-p000028-l0019 |

### round1

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 26 | 29 | 043b454a8c255b6690fd3777-p000008-l0020, 043b454a8c255b6690fd3777-p000061-l0030, 052a7a91dd9752b856b9fd8a-p000188-l0005, 143e78b5de2e6e784534ee0d-p000079-l0003, 241c524ed5b20f2baadf4b8b-p000082-l0043, 2c8742589d947f8d749c7ba2-p000040-l0013, 2f9e996ffbdaaa3b4a9dfdcf-p000082-l0007, 2f9e996ffbdaaa3b4a9dfdcf-p000141-l0018, 54a124e5cac779ec617e3ace-p000045-l0038, 5e99df8a3f2ecb56ba5c751b-p000156-l0002, 666498b9ed183dc88c1e8716-p000036-l0034, 686431e9a7fe04175e6e9be9-p000091-l0044, 723c450ea9bb07fc4cdf47f9-p000083-l0022, 7cb612112b4f28a4f704a9cb-p000081-l0071, 8f477fb59c9bc6957aadc800-p000119-l0025, 96bb7196d840fe7513c2ed43-p000024-l0030, b08a5423fb059fbb291900aa-p000213-l0003, b963a5d59be557e9eef8498b-p000065-l0065, bb8faba1e9b543fe5a1ce6dd-p000017-l0003, bb8faba1e9b543fe5a1ce6dd-p000127-l0016 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 26 | 29 | 043b454a8c255b6690fd3777-p000008-l0020, 043b454a8c255b6690fd3777-p000061-l0030, 052a7a91dd9752b856b9fd8a-p000188-l0005, 143e78b5de2e6e784534ee0d-p000079-l0003, 241c524ed5b20f2baadf4b8b-p000082-l0043, 2c8742589d947f8d749c7ba2-p000040-l0013, 2f9e996ffbdaaa3b4a9dfdcf-p000082-l0007, 2f9e996ffbdaaa3b4a9dfdcf-p000141-l0018, 54a124e5cac779ec617e3ace-p000045-l0038, 5e99df8a3f2ecb56ba5c751b-p000156-l0002, 666498b9ed183dc88c1e8716-p000036-l0034, 686431e9a7fe04175e6e9be9-p000091-l0044, 723c450ea9bb07fc4cdf47f9-p000083-l0022, 7cb612112b4f28a4f704a9cb-p000081-l0071, 8f477fb59c9bc6957aadc800-p000119-l0025, 96bb7196d840fe7513c2ed43-p000024-l0030, b08a5423fb059fbb291900aa-p000213-l0003, b963a5d59be557e9eef8498b-p000065-l0065, bb8faba1e9b543fe5a1ce6dd-p000017-l0003, bb8faba1e9b543fe5a1ce6dd-p000127-l0016 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 12 | 12 | 00c322b3ee04b419d1979f22-p000039-l0048, 042c93b2591368d437f27678-p000269-l0010, 2d29e5e76d90adc4cc1b093a-p000020-l0057, 453f156dc6352286456a08cb-p000209-l0034, 69846639273a60b797e93cb9-p000262-l0031, 8b231047fdbd96ec30e1eded-p000019-l0038, 8c926ffa3b1b2be056e56b7e-p000038-l0003, 8c926ffa3b1b2be056e56b7e-p000130-l0011, 9e60fbb6b1fc1da9f26b775e-p000175-l0011, b5f8ce187b707837e5669281-p000046-l0039, cc0e056392dd2ef4916b3e7d-p000039-l0002, f77a8c0084022edb7981fb15-p000075-l0079 |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 round2

Deletion HOLD lines: 4205; MOVE proposal lines: 5; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 2418 | 6370 | 0efd675a10c9a91816c7a41a-p000020-l0003, 0efd675a10c9a91816c7a41a-p000020-l0004, 0efd675a10c9a91816c7a41a-p000020-l0009, 0efd675a10c9a91816c7a41a-p000020-l0010, 0efd675a10c9a91816c7a41a-p000020-l0016, 0efd675a10c9a91816c7a41a-p000020-l0020, 0efd675a10c9a91816c7a41a-p000020-l0026, 0efd675a10c9a91816c7a41a-p000020-l0033, 0efd675a10c9a91816c7a41a-p000020-l0035, 0efd675a10c9a91816c7a41a-p000032-l0010, 0efd675a10c9a91816c7a41a-p000032-l0028, 0efd675a10c9a91816c7a41a-p000032-l0031, 0efd675a10c9a91816c7a41a-p000032-l0034, 0efd675a10c9a91816c7a41a-p000032-l0035, 0efd675a10c9a91816c7a41a-p000049-l0008, 0efd675a10c9a91816c7a41a-p000049-l0017, 0efd675a10c9a91816c7a41a-p000064-l0012, 0efd675a10c9a91816c7a41a-p000064-l0021, 0efd675a10c9a91816c7a41a-p000064-l0033, 0efd675a10c9a91816c7a41a-p000064-l0035 |
| apostrophe | 258 | 279 | 0efd675a10c9a91816c7a41a-p000049-l0025, 0efd675a10c9a91816c7a41a-p000064-l0015, 0efd675a10c9a91816c7a41a-p000079-l0026, 0efd675a10c9a91816c7a41a-p000079-l0028, 0efd675a10c9a91816c7a41a-p000139-l0007, 0efd675a10c9a91816c7a41a-p000170-l0035, 1182f94b107a4cc4ada574da-p000009-l0015, 1182f94b107a4cc4ada574da-p000009-l0016, 1182f94b107a4cc4ada574da-p000045-l0025, 1182f94b107a4cc4ada574da-p000054-l0014, 1182f94b107a4cc4ada574da-p000054-l0022, 1182f94b107a4cc4ada574da-p000060-l0026, 1182f94b107a4cc4ada574da-p000064-l0013, 32aae9fec147d3b483deb96e-p000042-l0050, 32aae9fec147d3b483deb96e-p000068-l0073, 32aae9fec147d3b483deb96e-p000084-l0049, 32aae9fec147d3b483deb96e-p000093-l0051, 32aae9fec147d3b483deb96e-p000101-l0018, 32aae9fec147d3b483deb96e-p000107-l0046, 3598ebd512fe5593fddcc4ed-p000017-l0082 |
| quote | 233 | 250 | 0efd675a10c9a91816c7a41a-p000079-l0006, 0efd675a10c9a91816c7a41a-p000079-l0016, 0efd675a10c9a91816c7a41a-p000079-l0021, 0efd675a10c9a91816c7a41a-p000186-l0004, 0efd675a10c9a91816c7a41a-p000186-l0011, 0efd675a10c9a91816c7a41a-p000200-l0003, 0efd675a10c9a91816c7a41a-p000200-l0023, 1182f94b107a4cc4ada574da-p000054-l0028, 1182f94b107a4cc4ada574da-p000054-l0039, 1182f94b107a4cc4ada574da-p000054-l0045, 1182f94b107a4cc4ada574da-p000060-l0024, 290a133b0e55593eb4ecdcfd-p000262-l0090, 290a133b0e55593eb4ecdcfd-p000288-l0009, 32aae9fec147d3b483deb96e-p000011-l0056, 32aae9fec147d3b483deb96e-p000019-l0017, 32aae9fec147d3b483deb96e-p000019-l0024, 32aae9fec147d3b483deb96e-p000019-l0063, 32aae9fec147d3b483deb96e-p000042-l0008, 32aae9fec147d3b483deb96e-p000084-l0068, 3598ebd512fe5593fddcc4ed-p000039-l0044 |
| keraia | 402 | 425 | 0efd675a10c9a91816c7a41a-p000049-l0013, 0efd675a10c9a91816c7a41a-p000049-l0016, 0efd675a10c9a91816c7a41a-p000049-l0019, 0efd675a10c9a91816c7a41a-p000049-l0034, 0efd675a10c9a91816c7a41a-p000064-l0033, 0efd675a10c9a91816c7a41a-p000156-l0025, 0efd675a10c9a91816c7a41a-p000156-l0029, 0efd675a10c9a91816c7a41a-p000156-l0032, 0efd675a10c9a91816c7a41a-p000156-l0034, 0efd675a10c9a91816c7a41a-p000170-l0023, 0efd675a10c9a91816c7a41a-p000186-l0019, 0efd675a10c9a91816c7a41a-p000186-l0022, 0efd675a10c9a91816c7a41a-p000200-l0006, 0efd675a10c9a91816c7a41a-p000200-l0013, 0efd675a10c9a91816c7a41a-p000200-l0015, 1182f94b107a4cc4ada574da-p000009-l0010, 1182f94b107a4cc4ada574da-p000017-l0025, 1182f94b107a4cc4ada574da-p000037-l0030, 1182f94b107a4cc4ada574da-p000037-l0042, 290a133b0e55593eb4ecdcfd-p000307-l0139 |
| other | 2395 | 23112 | 0efd675a10c9a91816c7a41a-p000020-l0006, 0efd675a10c9a91816c7a41a-p000020-l0009, 0efd675a10c9a91816c7a41a-p000020-l0014, 0efd675a10c9a91816c7a41a-p000020-l0024, 0efd675a10c9a91816c7a41a-p000020-l0026, 0efd675a10c9a91816c7a41a-p000020-l0034, 0efd675a10c9a91816c7a41a-p000020-l0035, 0efd675a10c9a91816c7a41a-p000032-l0012, 0efd675a10c9a91816c7a41a-p000032-l0013, 0efd675a10c9a91816c7a41a-p000032-l0035, 0efd675a10c9a91816c7a41a-p000049-l0011, 0efd675a10c9a91816c7a41a-p000049-l0013, 0efd675a10c9a91816c7a41a-p000049-l0016, 0efd675a10c9a91816c7a41a-p000049-l0025, 0efd675a10c9a91816c7a41a-p000049-l0034, 0efd675a10c9a91816c7a41a-p000049-l0036, 0efd675a10c9a91816c7a41a-p000079-l0008, 0efd675a10c9a91816c7a41a-p000079-l0010, 0efd675a10c9a91816c7a41a-p000079-l0016, 0efd675a10c9a91816c7a41a-p000079-l0025 |

### round2

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 11 | 11 | 39fbbdfd2c8030f211a318b7-p000138-l0003, 3c4393cb8164c820f7e7b38c-p000032-l0005, 6c0a582885e55adc7c535c48-p000107-l0020, 6d957fa757c72e1408f65dde-p000114-l0026, 827d2345ad77e5cdec320e80-p000006-l0009, 9dd010d6eb008870ea7c536c-p000050-l0031, b3c6afd03a5cab1b09b7d13e-p000036-l0063, b518f9f9b73fe9a3257fe2f0-p000078-l0012, dc390fceb64d9bb60a12d6b8-p000098-l0015, ee2ae82a5d56b54859d7385b-p000177-l0006, ee2ae82a5d56b54859d7385b-p000251-l0006 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 11 | 11 | 39fbbdfd2c8030f211a318b7-p000138-l0003, 3c4393cb8164c820f7e7b38c-p000032-l0005, 6c0a582885e55adc7c535c48-p000107-l0020, 6d957fa757c72e1408f65dde-p000114-l0026, 827d2345ad77e5cdec320e80-p000006-l0009, 9dd010d6eb008870ea7c536c-p000050-l0031, b3c6afd03a5cab1b09b7d13e-p000036-l0063, b518f9f9b73fe9a3257fe2f0-p000078-l0012, dc390fceb64d9bb60a12d6b8-p000098-l0015, ee2ae82a5d56b54859d7385b-p000177-l0006, ee2ae82a5d56b54859d7385b-p000251-l0006 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 1 | 1 | dc390fceb64d9bb60a12d6b8-p000060-l0005 |
| insertions_by_class/quote | 2 | 2 | dc390fceb64d9bb60a12d6b8-p000082-l0002, dc390fceb64d9bb60a12d6b8-p000127-l0007 |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 vouli

Deletion HOLD lines: 5478; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 3406 | 10648 | 0271e3cae771-p000001-l0002, 0271e3cae771-p000001-l0036, 0271e3cae771-p000002-l0013, 0271e3cae771-p000002-l0019, 0271e3cae771-p000002-l0031, 0271e3cae771-p000003-l0011, 0271e3cae771-p000003-l0017, 0271e3cae771-p000003-l0034, 0271e3cae771-p000004-l0008, 0271e3cae771-p000004-l0010, 0271e3cae771-p000004-l0013, 0271e3cae771-p000005-l0002, 0271e3cae771-p000005-l0012, 0271e3cae771-p000005-l0024, 0271e3cae771-p000006-l0008, 0271e3cae771-p000006-l0016, 0271e3cae771-p000006-l0024, 0271e3cae771-p000006-l0025, 0271e3cae771-p000007-l0024, 0271e3cae771-p000007-l0029 |
| apostrophe | 278 | 292 | 0271e3cae771-p000001-l0036, 0271e3cae771-p000004-l0037, 0271e3cae771-p000006-l0030, 07bc68f92367-p000004-l0004, 0e777453c7a8-p000001-l0073, 0e777453c7a8-p000001-l0091, 0e777453c7a8-p000001-l0095, 0e777453c7a8-p000002-l0077, 0e777453c7a8-p000002-l0104, 0e777453c7a8-p000002-l0109, 0e777453c7a8-p000002-l0111, 0e777453c7a8-p000003-l0007, 0e777453c7a8-p000003-l0017, 0e777453c7a8-p000003-l0028, 0e777453c7a8-p000003-l0115, 1365c8bbb0a8-p000001-l0017, 1365c8bbb0a8-p000012-l0058, 182619a5630d-p000001-l0064, 182619a5630d-p000001-l0081, 182619a5630d-p000001-l0083 |
| quote | 245 | 248 | 0271e3cae771-p000002-l0013, 07bc68f92367-p000003-l0006, 0e777453c7a8-p000001-l0001, 18167bc1e4a8-p000002-l0016, 182619a5630d-p000002-l0065, 182619a5630d-p000005-l0051, 182619a5630d-p000009-l0059, 182619a5630d-p000009-l0060, 182619a5630d-p000009-l0061, 182619a5630d-p000009-l0062, 1f485870372f-p000001-l0002, 1f485870372f-p000003-l0010, 1f485870372f-p000003-l0017, 1f485870372f-p000010-l0016, 1f485870372f-p000010-l0017, 1f485870372f-p000010-l0018, 1ff160a5dd27-p000001-l0008, 1ff160a5dd27-p000001-l0009, 1ff160a5dd27-p000001-l0011, 1ff160a5dd27-p000009-l0026 |
| keraia | 508 | 558 | 0e777453c7a8-p000001-l0020, 0e777453c7a8-p000001-l0030, 0e777453c7a8-p000001-l0072, 0e777453c7a8-p000001-l0075, 0e777453c7a8-p000001-l0078, 0e777453c7a8-p000001-l0084, 0e777453c7a8-p000001-l0091, 0e777453c7a8-p000001-l0094, 0e777453c7a8-p000002-l0009, 0e777453c7a8-p000002-l0010, 0e777453c7a8-p000002-l0014, 0e777453c7a8-p000002-l0019, 0e777453c7a8-p000002-l0022, 0e777453c7a8-p000002-l0026, 0e777453c7a8-p000002-l0028, 0e777453c7a8-p000002-l0032, 0e777453c7a8-p000002-l0041, 0e777453c7a8-p000002-l0043, 0e777453c7a8-p000002-l0047, 0e777453c7a8-p000002-l0056 |
| other | 2899 | 41281 | 0271e3cae771-p000001-l0015, 0271e3cae771-p000001-l0028, 0271e3cae771-p000001-l0030, 0271e3cae771-p000001-l0036, 0271e3cae771-p000002-l0013, 0271e3cae771-p000002-l0015, 0271e3cae771-p000002-l0019, 0271e3cae771-p000002-l0031, 0271e3cae771-p000003-l0011, 0271e3cae771-p000003-l0036, 0271e3cae771-p000003-l0037, 0271e3cae771-p000004-l0013, 0271e3cae771-p000004-l0023, 0271e3cae771-p000004-l0037, 0271e3cae771-p000004-l0040, 0271e3cae771-p000005-l0002, 0271e3cae771-p000005-l0003, 0271e3cae771-p000006-l0009, 0271e3cae771-p000006-l0030, 0271e3cae771-p000006-l0033 |

### vouli

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 5 | 5 | 23e59c57bd30-p000003-l0032, 8cd0e8c1f0e5-p000001-l0025, 91252504a906-p000025-l0013, da9a31d7669d-p000025-l0003, f4e509d76b55-p000004-l0010 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 5 | 5 | 23e59c57bd30-p000003-l0032, 8cd0e8c1f0e5-p000001-l0025, 91252504a906-p000025-l0013, da9a31d7669d-p000025-l0003, f4e509d76b55-p000004-l0010 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 3 | 3 | 971b6ed3092a-p000004-l0002, aed4abe1314b-p000002-l0017, d9b7dfa900e3-p000003-l0034 |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |
## ENSEMBLE_AB

| Wave | Lines | Corrected status | Real mark-correction lines | Real mark lines with single-source deletion | Share of real mark-correction lines |
|---|---:|---:|---:|---:|---:|
| ALL | 124669 | 236 | 155 | 1 | 0.645161% |
| mixed | 13227 | 44 | 28 | 0 | 0.000000% |
| openarchives | 235 | 2 | 2 | 0 | 0.000000% |
| parliament | 27224 | 6 | 3 | 0 | 0.000000% |
| round1 | 43869 | 112 | 67 | 1 | 1.492537% |
| round2 | 17026 | 59 | 49 | 0 | 0.000000% |
| vouli | 23088 | 13 | 6 | 0 | 0.000000% |

### SF6 ALL

Deletion HOLD lines: 33058; MOVE proposal lines: 12; MOVE applied: 1 checks / 1 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 20456 | 59882 | 00c322b3ee04b419d1979f22-p000015-l0034, 00c322b3ee04b419d1979f22-p000015-l0039, 00c322b3ee04b419d1979f22-p000015-l0041, 00c322b3ee04b419d1979f22-p000015-l0046, 00c322b3ee04b419d1979f22-p000015-l0068, 00c322b3ee04b419d1979f22-p000015-l0069, 00c322b3ee04b419d1979f22-p000015-l0073, 00c322b3ee04b419d1979f22-p000015-l0076, 00c322b3ee04b419d1979f22-p000028-l0003, 00c322b3ee04b419d1979f22-p000028-l0009, 00c322b3ee04b419d1979f22-p000028-l0010, 00c322b3ee04b419d1979f22-p000028-l0011, 00c322b3ee04b419d1979f22-p000028-l0012, 00c322b3ee04b419d1979f22-p000028-l0013, 00c322b3ee04b419d1979f22-p000028-l0014, 00c322b3ee04b419d1979f22-p000028-l0016, 00c322b3ee04b419d1979f22-p000028-l0018, 00c322b3ee04b419d1979f22-p000028-l0019, 00c322b3ee04b419d1979f22-p000028-l0020, 00c322b3ee04b419d1979f22-p000028-l0021 |
| apostrophe | 1580 | 1685 | 00c322b3ee04b419d1979f22-p000015-l0059, 00c322b3ee04b419d1979f22-p000015-l0079, 00c322b3ee04b419d1979f22-p000028-l0011, 00c322b3ee04b419d1979f22-p000028-l0025, 00c322b3ee04b419d1979f22-p000028-l0027, 00c322b3ee04b419d1979f22-p000103-l0011, 00c322b3ee04b419d1979f22-p000115-l0068, 00c322b3ee04b419d1979f22-p000142-l0005, 00c322b3ee04b419d1979f22-p000142-l0016, 0271e3cae771-p000001-l0036, 0271e3cae771-p000004-l0037, 0271e3cae771-p000006-l0030, 042c93b2591368d437f27678-p000148-l0003, 042c93b2591368d437f27678-p000245-l0022, 043b454a8c255b6690fd3777-p000013-l0053, 043b454a8c255b6690fd3777-p000027-l0033, 043b454a8c255b6690fd3777-p000031-l0006, 043b454a8c255b6690fd3777-p000040-l0051, 043b454a8c255b6690fd3777-p000044-l0062, 043b454a8c255b6690fd3777-p000054-l0063 |
| quote | 1953 | 2000 | 00c322b3ee04b419d1979f22-p000015-l0069, 00c322b3ee04b419d1979f22-p000028-l0054, 00c322b3ee04b419d1979f22-p000028-l0070, 00c322b3ee04b419d1979f22-p000055-l0002, 00c322b3ee04b419d1979f22-p000055-l0003, 00c322b3ee04b419d1979f22-p000055-l0025, 00c322b3ee04b419d1979f22-p000055-l0026, 00c322b3ee04b419d1979f22-p000055-l0027, 00c322b3ee04b419d1979f22-p000055-l0028, 00c322b3ee04b419d1979f22-p000055-l0030, 00c322b3ee04b419d1979f22-p000055-l0043, 00c322b3ee04b419d1979f22-p000055-l0050, 00c322b3ee04b419d1979f22-p000078-l0069, 00c322b3ee04b419d1979f22-p000093-l0006, 00c322b3ee04b419d1979f22-p000093-l0040, 00c322b3ee04b419d1979f22-p000093-l0041, 00c322b3ee04b419d1979f22-p000093-l0042, 00c322b3ee04b419d1979f22-p000093-l0046, 00c322b3ee04b419d1979f22-p000093-l0053, 00c322b3ee04b419d1979f22-p000115-l0024 |
| keraia | 1652 | 1786 | 00c322b3ee04b419d1979f22-p000055-l0006, 00c322b3ee04b419d1979f22-p000055-l0011, 00c322b3ee04b419d1979f22-p000115-l0019, 00c322b3ee04b419d1979f22-p000129-l0037, 00c322b3ee04b419d1979f22-p000166-l0040, 042c93b2591368d437f27678-p000075-l0036, 042c93b2591368d437f27678-p000148-l0011, 043b454a8c255b6690fd3777-p000019-l0042, 043b454a8c255b6690fd3777-p000019-l0063, 043b454a8c255b6690fd3777-p000019-l0079, 0590d5cb-p000007-l0092, 07dc0ec3a36ef8d4433de416-p000083-l0036, 0907df739607faca673d2169-p000033-l0007, 0b33fccd-p000023-l0126, 0b33fccd-p000032-l0044, 0cb3f67240837f77ee728005-p000005-l0042, 0cb3f67240837f77ee728005-p000005-l0044, 0cb3f67240837f77ee728005-p000005-l0049, 0cb3f67240837f77ee728005-p000005-l0050, 0cb3f67240837f77ee728005-p000019-l0052 |
| other | 18993 | 226929 | 00c322b3ee04b419d1979f22-p000015-l0009, 00c322b3ee04b419d1979f22-p000015-l0035, 00c322b3ee04b419d1979f22-p000015-l0037, 00c322b3ee04b419d1979f22-p000015-l0041, 00c322b3ee04b419d1979f22-p000015-l0046, 00c322b3ee04b419d1979f22-p000015-l0051, 00c322b3ee04b419d1979f22-p000015-l0059, 00c322b3ee04b419d1979f22-p000015-l0069, 00c322b3ee04b419d1979f22-p000015-l0073, 00c322b3ee04b419d1979f22-p000015-l0076, 00c322b3ee04b419d1979f22-p000015-l0081, 00c322b3ee04b419d1979f22-p000028-l0003, 00c322b3ee04b419d1979f22-p000028-l0010, 00c322b3ee04b419d1979f22-p000028-l0011, 00c322b3ee04b419d1979f22-p000028-l0012, 00c322b3ee04b419d1979f22-p000028-l0013, 00c322b3ee04b419d1979f22-p000028-l0014, 00c322b3ee04b419d1979f22-p000028-l0016, 00c322b3ee04b419d1979f22-p000028-l0017, 00c322b3ee04b419d1979f22-p000028-l0019 |

### ALL

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 155 | 163 | 00c322b3ee04b419d1979f22-p000055-l0033, 043b454a8c255b6690fd3777-p000008-l0020, 043b454a8c255b6690fd3777-p000048-l0011, 043b454a8c255b6690fd3777-p000054-l0047, 043b454a8c255b6690fd3777-p000061-l0012, 043b454a8c255b6690fd3777-p000061-l0030, 052a7a91dd9752b856b9fd8a-p000164-l0030, 052a7a91dd9752b856b9fd8a-p000188-l0005, 0b2cede5e125323a082f684b-p000021-l0002, 0bff55647d1c2acd1caa8bf3-p000120-l0015, 1092c25534f45a95669f3d2b-p000030-l0018, 1182f94b107a4cc4ada574da-p000011-l0011, 1182f94b107a4cc4ada574da-p000021-l0034, 12493332097bacc2a62b4d9a-p000017-l0027, 143e78b5de2e6e784534ee0d-p000055-l0017, 17499e55347a68940e18597f-p000012-l0025, 241c524ed5b20f2baadf4b8b-p000041-l0005, 241c524ed5b20f2baadf4b8b-p000119-l0012, 290a133b0e55593eb4ecdcfd-p000145-l0049, 290a133b0e55593eb4ecdcfd-p000145-l0070 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 1 | 1 | 87010bf6a68a76f0e0eb368f-p000015-l0028 |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 1 | 1 | 87010bf6a68a76f0e0eb368f-p000015-l0028 |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 155 | 163 | 00c322b3ee04b419d1979f22-p000055-l0033, 043b454a8c255b6690fd3777-p000008-l0020, 043b454a8c255b6690fd3777-p000048-l0011, 043b454a8c255b6690fd3777-p000054-l0047, 043b454a8c255b6690fd3777-p000061-l0012, 043b454a8c255b6690fd3777-p000061-l0030, 052a7a91dd9752b856b9fd8a-p000164-l0030, 052a7a91dd9752b856b9fd8a-p000188-l0005, 0b2cede5e125323a082f684b-p000021-l0002, 0bff55647d1c2acd1caa8bf3-p000120-l0015, 1092c25534f45a95669f3d2b-p000030-l0018, 1182f94b107a4cc4ada574da-p000011-l0011, 1182f94b107a4cc4ada574da-p000021-l0034, 12493332097bacc2a62b4d9a-p000017-l0027, 143e78b5de2e6e784534ee0d-p000055-l0017, 17499e55347a68940e18597f-p000012-l0025, 241c524ed5b20f2baadf4b8b-p000041-l0005, 241c524ed5b20f2baadf4b8b-p000119-l0012, 290a133b0e55593eb4ecdcfd-p000145-l0049, 290a133b0e55593eb4ecdcfd-p000145-l0070 |
| insertions_by_class/numeral_keraia | 1 | 1 | 70e0a3447310acfc3f8dddf3-p000254-l0006 |
| insertions_by_class/elision_apostrophe | 3 | 3 | a51f2efdcf758c1fa5ab52e6-p000044-l0053, bf2ce6d100950eec319cef00-p000028-l0091, dc390fceb64d9bb60a12d6b8-p000060-l0005 |
| insertions_by_class/quote | 77 | 77 | 00c322b3ee04b419d1979f22-p000028-l0007, 00c322b3ee04b419d1979f22-p000039-l0048, 042c93b2591368d437f27678-p000269-l0010, 0907df739607faca673d2169-p000021-l0059, 0a4bc4314e492706bcc0bf44-p000038-l0027, 0b2cede5e125323a082f684b-p000040-l0006, 0bff55647d1c2acd1caa8bf3-p000072-l0006, 0bff55647d1c2acd1caa8bf3-p000136-l0006, 0bff55647d1c2acd1caa8bf3-p000136-l0028, 0bff55647d1c2acd1caa8bf3-p000167-l0009, 0bff55647d1c2acd1caa8bf3-p000184-l0029, 0bff55647d1c2acd1caa8bf3-p000184-l0030, 0bff55647d1c2acd1caa8bf3-p000215-l0009, 12493332097bacc2a62b4d9a-p000036-l0008, 12493332097bacc2a62b4d9a-p000041-l0018, 1495fc2311427a558abbfd88-p000014-l0006, 1c13bd49225f6fcf7dcca5a0-p000036-l0007, 241c524ed5b20f2baadf4b8b-p000051-l0047, 241c524ed5b20f2baadf4b8b-p000119-l0016, 2b1d2b5340150ddc135a2b1a-p000140-l0033 |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 mixed

Deletion HOLD lines: 3212; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 1937 | 5388 | 0a4bc4314e492706bcc0bf44-p000008-l0010, 0a4bc4314e492706bcc0bf44-p000008-l0023, 0a4bc4314e492706bcc0bf44-p000008-l0024, 0a4bc4314e492706bcc0bf44-p000008-l0025, 0a4bc4314e492706bcc0bf44-p000011-l0002, 0a4bc4314e492706bcc0bf44-p000011-l0009, 0a4bc4314e492706bcc0bf44-p000011-l0013, 0a4bc4314e492706bcc0bf44-p000011-l0021, 0a4bc4314e492706bcc0bf44-p000011-l0022, 0a4bc4314e492706bcc0bf44-p000011-l0034, 0a4bc4314e492706bcc0bf44-p000011-l0035, 0a4bc4314e492706bcc0bf44-p000011-l0038, 0a4bc4314e492706bcc0bf44-p000011-l0041, 0a4bc4314e492706bcc0bf44-p000014-l0009, 0a4bc4314e492706bcc0bf44-p000014-l0011, 0a4bc4314e492706bcc0bf44-p000014-l0013, 0a4bc4314e492706bcc0bf44-p000014-l0026, 0a4bc4314e492706bcc0bf44-p000014-l0035, 0a4bc4314e492706bcc0bf44-p000019-l0013, 0a4bc4314e492706bcc0bf44-p000019-l0028 |
| apostrophe | 162 | 166 | 0a4bc4314e492706bcc0bf44-p000008-l0023, 0a4bc4314e492706bcc0bf44-p000019-l0012, 0a4bc4314e492706bcc0bf44-p000019-l0013, 0a4bc4314e492706bcc0bf44-p000046-l0035, 12493332097bacc2a62b4d9a-p000026-l0009, 12493332097bacc2a62b4d9a-p000046-l0011, 1c13bd49225f6fcf7dcca5a0-p000036-l0002, 1c13bd49225f6fcf7dcca5a0-p000081-l0009, 1c13bd49225f6fcf7dcca5a0-p000115-l0013, 1c13bd49225f6fcf7dcca5a0-p000125-l0008, 3249d506364999770e38aeef-p000044-l0022, 3249d506364999770e38aeef-p000044-l0026, 3249d506364999770e38aeef-p000099-l0013, 3249d506364999770e38aeef-p000109-l0009, 3249d506364999770e38aeef-p000130-l0052, 341f77df7fe3f09264ceee79-p000006-l0035, 341f77df7fe3f09264ceee79-p000015-l0026, 34d2967a06064249e6ebc895-p000077-l0015, 34d2967a06064249e6ebc895-p000139-l0024, 37a9179b-p000113-l0003 |
| quote | 330 | 332 | 0a4bc4314e492706bcc0bf44-p000046-l0006, 12493332097bacc2a62b4d9a-p000007-l0018, 12493332097bacc2a62b4d9a-p000031-l0031, 12493332097bacc2a62b4d9a-p000046-l0029, 137e9af6a0045d5746e26efa-p000003-l0008, 137e9af6a0045d5746e26efa-p000006-l0022, 137e9af6a0045d5746e26efa-p000008-l0010, 137e9af6a0045d5746e26efa-p000008-l0021, 1c13bd49225f6fcf7dcca5a0-p000115-l0013, 3249d506364999770e38aeef-p000011-l0019, 3249d506364999770e38aeef-p000011-l0020, 3249d506364999770e38aeef-p000011-l0021, 3249d506364999770e38aeef-p000011-l0022, 3249d506364999770e38aeef-p000011-l0023, 3249d506364999770e38aeef-p000011-l0024, 3249d506364999770e38aeef-p000011-l0025, 3249d506364999770e38aeef-p000011-l0026, 3249d506364999770e38aeef-p000011-l0027, 3249d506364999770e38aeef-p000011-l0028, 3249d506364999770e38aeef-p000011-l0029 |
| keraia | 117 | 125 | 12493332097bacc2a62b4d9a-p000024-l0022, 12493332097bacc2a62b4d9a-p000024-l0025, 12493332097bacc2a62b4d9a-p000026-l0029, 12493332097bacc2a62b4d9a-p000026-l0031, 12493332097bacc2a62b4d9a-p000031-l0012, 12493332097bacc2a62b4d9a-p000031-l0017, 12493332097bacc2a62b4d9a-p000041-l0017, 12493332097bacc2a62b4d9a-p000046-l0027, 3249d506364999770e38aeef-p000044-l0022, 3249d506364999770e38aeef-p000044-l0026, 3249d506364999770e38aeef-p000054-l0040, 3249d506364999770e38aeef-p000067-l0044, 3249d506364999770e38aeef-p000099-l0033, 3249d506364999770e38aeef-p000109-l0052, 3249d506364999770e38aeef-p000130-l0034, 341f77df7fe3f09264ceee79-p000004-l0029, 341f77df7fe3f09264ceee79-p000021-l0025, 341f77df7fe3f09264ceee79-p000021-l0028, 4a34388c9884fda746d2a8cd-p000020-l0008, 4a34388c9884fda746d2a8cd-p000020-l0014 |
| other | 1854 | 19982 | 0a4bc4314e492706bcc0bf44-p000008-l0023, 0a4bc4314e492706bcc0bf44-p000008-l0024, 0a4bc4314e492706bcc0bf44-p000008-l0025, 0a4bc4314e492706bcc0bf44-p000011-l0007, 0a4bc4314e492706bcc0bf44-p000011-l0009, 0a4bc4314e492706bcc0bf44-p000011-l0017, 0a4bc4314e492706bcc0bf44-p000011-l0034, 0a4bc4314e492706bcc0bf44-p000011-l0035, 0a4bc4314e492706bcc0bf44-p000011-l0038, 0a4bc4314e492706bcc0bf44-p000011-l0041, 0a4bc4314e492706bcc0bf44-p000014-l0026, 0a4bc4314e492706bcc0bf44-p000019-l0004, 0a4bc4314e492706bcc0bf44-p000019-l0010, 0a4bc4314e492706bcc0bf44-p000019-l0012, 0a4bc4314e492706bcc0bf44-p000019-l0013, 0a4bc4314e492706bcc0bf44-p000019-l0018, 0a4bc4314e492706bcc0bf44-p000019-l0022, 0a4bc4314e492706bcc0bf44-p000019-l0028, 0a4bc4314e492706bcc0bf44-p000019-l0032, 0a4bc4314e492706bcc0bf44-p000019-l0036 |

### mixed

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 28 | 33 | 12493332097bacc2a62b4d9a-p000017-l0027, 3249d506364999770e38aeef-p000022-l0041, 341f77df7fe3f09264ceee79-p000004-l0017, 341f77df7fe3f09264ceee79-p000004-l0024, 37a9179b-p000113-l0006, 4a34388c9884fda746d2a8cd-p000020-l0040, 5165f9e7fe1f3d7053f5adcf-p000003-l0002, 5165f9e7fe1f3d7053f5adcf-p000023-l0005, 82d33c43a02ea862069af4ad-p000166-l0016, 82d33c43a02ea862069af4ad-p000258-l0011, 92ab1a099d56dc9022fc4778-p000012-l0075, 92ab1a099d56dc9022fc4778-p000020-l0076, a51f2efdcf758c1fa5ab52e6-p000071-l0071, b5076e8734ba287d549d79b5-p000010-l0026, b5076e8734ba287d549d79b5-p000047-l0023, b8b6779da9a68fbed0ccdb5b-p000028-l0056, c57e3067ed37cedf17f285e6-p000006-l0013, c57e3067ed37cedf17f285e6-p000009-l0022, c57e3067ed37cedf17f285e6-p000044-l0024, c8654864d161aa7fc41f65cb-p000335-l0035 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 28 | 33 | 12493332097bacc2a62b4d9a-p000017-l0027, 3249d506364999770e38aeef-p000022-l0041, 341f77df7fe3f09264ceee79-p000004-l0017, 341f77df7fe3f09264ceee79-p000004-l0024, 37a9179b-p000113-l0006, 4a34388c9884fda746d2a8cd-p000020-l0040, 5165f9e7fe1f3d7053f5adcf-p000003-l0002, 5165f9e7fe1f3d7053f5adcf-p000023-l0005, 82d33c43a02ea862069af4ad-p000166-l0016, 82d33c43a02ea862069af4ad-p000258-l0011, 92ab1a099d56dc9022fc4778-p000012-l0075, 92ab1a099d56dc9022fc4778-p000020-l0076, a51f2efdcf758c1fa5ab52e6-p000071-l0071, b5076e8734ba287d549d79b5-p000010-l0026, b5076e8734ba287d549d79b5-p000047-l0023, b8b6779da9a68fbed0ccdb5b-p000028-l0056, c57e3067ed37cedf17f285e6-p000006-l0013, c57e3067ed37cedf17f285e6-p000009-l0022, c57e3067ed37cedf17f285e6-p000044-l0024, c8654864d161aa7fc41f65cb-p000335-l0035 |
| insertions_by_class/numeral_keraia | 1 | 1 | 70e0a3447310acfc3f8dddf3-p000254-l0006 |
| insertions_by_class/elision_apostrophe | 1 | 1 | a51f2efdcf758c1fa5ab52e6-p000044-l0053 |
| insertions_by_class/quote | 14 | 14 | 0a4bc4314e492706bcc0bf44-p000038-l0027, 12493332097bacc2a62b4d9a-p000036-l0008, 12493332097bacc2a62b4d9a-p000041-l0018, 1c13bd49225f6fcf7dcca5a0-p000036-l0007, 37a9179b-p000113-l0020, 5165f9e7fe1f3d7053f5adcf-p000003-l0023, 5165f9e7fe1f3d7053f5adcf-p000021-l0042, 5165f9e7fe1f3d7053f5adcf-p000023-l0058, 5165f9e7fe1f3d7053f5adcf-p000023-l0065, 5165f9e7fe1f3d7053f5adcf-p000027-l0062, 5165f9e7fe1f3d7053f5adcf-p000030-l0004, 5165f9e7fe1f3d7053f5adcf-p000032-l0049, c57e3067ed37cedf17f285e6-p000044-l0006, d0eda948e5b1f3632f8687fb-p000311-l0038 |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 openarchives

Deletion HOLD lines: 23; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 7 | 9 | 0fead7c5-p000008-l0061, 0fead7c5-p000008-l0095, 0fead7c5-p000010-l0001, 0fead7c5-p000010-l0011, 0fead7c5-p000010-l0030, 0fead7c5-p000010-l0040, 0fead7c5-p000010-l0047 |
| apostrophe | 1 | 1 | 0fead7c5-p000004-l0038 |
| quote | 0 | 0 |  |
| keraia | 10 | 13 | 0fead7c5-p000004-l0035, 0fead7c5-p000004-l0038, 0fead7c5-p000004-l0041, 0fead7c5-p000004-l0044, 0fead7c5-p000004-l0047, a4c40997-p000007-l0013, a4c40997-p000007-l0018, a4c40997-p000007-l0028, a4c40997-p000017-l0040, a4c40997-p000066-l0013 |
| other | 9 | 52 | 0fead7c5-p000004-l0038, 0fead7c5-p000008-l0003, 0fead7c5-p000008-l0028, 0fead7c5-p000010-l0001, 0fead7c5-p000010-l0040, a4c40997-p000017-l0018, a4c40997-p000023-l0001, a4c40997-p000035-l0010, a4c40997-p000035-l0017 |

### openarchives

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 2 | 2 | a4c40997-p000013-l0029, a4c40997-p000035-l0036 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 2 | 2 | a4c40997-p000013-l0029, a4c40997-p000035-l0036 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 0 | 0 |  |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 parliament

Deletion HOLD lines: 8007; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 5381 | 13124 | 01c618de-p000024-l0060, 0590d5cb-p000003-l0104, 0590d5cb-p000007-l0052, 0590d5cb-p000007-l0092, 0590d5cb-p000009-l0044, 0590d5cb-p000012-l0016, 0590d5cb-p000012-l0020, 0590d5cb-p000012-l0117, 0590d5cb-p000013-l0006, 0590d5cb-p000015-l0045, 0590d5cb-p000017-l0033, 0590d5cb-p000021-l0007, 0590d5cb-p000023-l0021, 0590d5cb-p000024-l0005, 0590d5cb-p000024-l0025, 0b33fccd-p000008-l0006, 0b33fccd-p000008-l0007, 0b33fccd-p000008-l0016, 0b33fccd-p000008-l0021, 0b33fccd-p000008-l0024 |
| apostrophe | 144 | 146 | 0b33fccd-p000008-l0053, 0b33fccd-p000008-l0091, 0b33fccd-p000008-l0092, 0b33fccd-p000010-l0011, 0b33fccd-p000010-l0060, 0b33fccd-p000012-l0094, 0b33fccd-p000017-l0078, 0b33fccd-p000021-l0118, 0b33fccd-p000027-l0063, 133c1ea6-p000003-l0066, 133c1ea6-p000003-l0108, 133c1ea6-p000009-l0113, 133c1ea6-p000010-l0022, 133c1ea6-p000014-l0021, 133c1ea6-p000020-l0119, 13dcc39a-p000008-l0124, 13dcc39a-p000012-l0070, 13dcc39a-p000020-l0059, 13dcc39a-p000023-l0095, 13dcc39a-p000026-l0138 |
| quote | 230 | 236 | 01c618de-p000013-l0134, 0b33fccd-p000008-l0114, 0b33fccd-p000012-l0093, 0b33fccd-p000023-l0113, 133c1ea6-p000003-l0023, 133c1ea6-p000003-l0041, 133c1ea6-p000003-l0094, 133c1ea6-p000003-l0117, 133c1ea6-p000007-l0023, 133c1ea6-p000007-l0053, 133c1ea6-p000007-l0076, 133c1ea6-p000007-l0086, 133c1ea6-p000007-l0102, 133c1ea6-p000007-l0117, 133c1ea6-p000009-l0025, 133c1ea6-p000009-l0038, 133c1ea6-p000009-l0071, 133c1ea6-p000009-l0082, 133c1ea6-p000009-l0106, 133c1ea6-p000009-l0133 |
| keraia | 104 | 110 | 0590d5cb-p000007-l0092, 0b33fccd-p000023-l0126, 0b33fccd-p000032-l0044, 133c1ea6-p000007-l0007, 133c1ea6-p000007-l0121, 133c1ea6-p000009-l0002, 133c1ea6-p000009-l0009, 133c1ea6-p000010-l0105, 133c1ea6-p000010-l0116, 133c1ea6-p000014-l0080, 133c1ea6-p000019-l0114, 1a035976-p000014-l0024, 1a035976-p000014-l0026, 1a035976-p000016-l0087, 1a035976-p000016-l0088, 1a035976-p000022-l0037, 1a035976-p000022-l0083, 3455d0e7-p000023-l0024, 48a58eb5-p000010-l0139, 52b46e46-p000005-l0099 |
| other | 4338 | 45081 | 01c618de-p000013-l0134, 0590d5cb-p000012-l0016, 0590d5cb-p000012-l0020, 0590d5cb-p000015-l0045, 0590d5cb-p000017-l0033, 0b33fccd-p000008-l0006, 0b33fccd-p000008-l0015, 0b33fccd-p000008-l0019, 0b33fccd-p000008-l0023, 0b33fccd-p000008-l0024, 0b33fccd-p000008-l0025, 0b33fccd-p000008-l0031, 0b33fccd-p000008-l0044, 0b33fccd-p000008-l0053, 0b33fccd-p000008-l0058, 0b33fccd-p000008-l0061, 0b33fccd-p000008-l0064, 0b33fccd-p000008-l0067, 0b33fccd-p000008-l0078, 0b33fccd-p000008-l0079 |

### parliament

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 3 | 3 | aac90dd4-p000017-l0024, dd625312-p000010-l0036, dd625312-p000037-l0051 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 3 | 3 | aac90dd4-p000017-l0024, dd625312-p000010-l0036, dd625312-p000037-l0051 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 3 | 3 | 3455d0e7-p000021-l0099, 3455d0e7-p000021-l0115, 7aea9867-p000038-l0130 |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 round1

Deletion HOLD lines: 12134; MOVE proposal lines: 6; MOVE applied: 1 checks / 1 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 7308 | 24344 | 00c322b3ee04b419d1979f22-p000015-l0034, 00c322b3ee04b419d1979f22-p000015-l0039, 00c322b3ee04b419d1979f22-p000015-l0041, 00c322b3ee04b419d1979f22-p000015-l0046, 00c322b3ee04b419d1979f22-p000015-l0068, 00c322b3ee04b419d1979f22-p000015-l0069, 00c322b3ee04b419d1979f22-p000015-l0073, 00c322b3ee04b419d1979f22-p000015-l0076, 00c322b3ee04b419d1979f22-p000028-l0003, 00c322b3ee04b419d1979f22-p000028-l0009, 00c322b3ee04b419d1979f22-p000028-l0010, 00c322b3ee04b419d1979f22-p000028-l0011, 00c322b3ee04b419d1979f22-p000028-l0012, 00c322b3ee04b419d1979f22-p000028-l0013, 00c322b3ee04b419d1979f22-p000028-l0014, 00c322b3ee04b419d1979f22-p000028-l0016, 00c322b3ee04b419d1979f22-p000028-l0018, 00c322b3ee04b419d1979f22-p000028-l0019, 00c322b3ee04b419d1979f22-p000028-l0020, 00c322b3ee04b419d1979f22-p000028-l0021 |
| apostrophe | 737 | 801 | 00c322b3ee04b419d1979f22-p000015-l0059, 00c322b3ee04b419d1979f22-p000015-l0079, 00c322b3ee04b419d1979f22-p000028-l0011, 00c322b3ee04b419d1979f22-p000028-l0025, 00c322b3ee04b419d1979f22-p000028-l0027, 00c322b3ee04b419d1979f22-p000103-l0011, 00c322b3ee04b419d1979f22-p000115-l0068, 00c322b3ee04b419d1979f22-p000142-l0005, 00c322b3ee04b419d1979f22-p000142-l0016, 042c93b2591368d437f27678-p000148-l0003, 042c93b2591368d437f27678-p000245-l0022, 043b454a8c255b6690fd3777-p000013-l0053, 043b454a8c255b6690fd3777-p000027-l0033, 043b454a8c255b6690fd3777-p000031-l0006, 043b454a8c255b6690fd3777-p000040-l0051, 043b454a8c255b6690fd3777-p000044-l0062, 043b454a8c255b6690fd3777-p000054-l0063, 052a7a91dd9752b856b9fd8a-p000114-l0008, 052a7a91dd9752b856b9fd8a-p000140-l0048, 0550c3c52f2b388255690d5a-p000027-l0008 |
| quote | 915 | 934 | 00c322b3ee04b419d1979f22-p000015-l0069, 00c322b3ee04b419d1979f22-p000028-l0054, 00c322b3ee04b419d1979f22-p000028-l0070, 00c322b3ee04b419d1979f22-p000055-l0002, 00c322b3ee04b419d1979f22-p000055-l0003, 00c322b3ee04b419d1979f22-p000055-l0025, 00c322b3ee04b419d1979f22-p000055-l0026, 00c322b3ee04b419d1979f22-p000055-l0027, 00c322b3ee04b419d1979f22-p000055-l0028, 00c322b3ee04b419d1979f22-p000055-l0030, 00c322b3ee04b419d1979f22-p000055-l0043, 00c322b3ee04b419d1979f22-p000055-l0050, 00c322b3ee04b419d1979f22-p000078-l0069, 00c322b3ee04b419d1979f22-p000093-l0006, 00c322b3ee04b419d1979f22-p000093-l0040, 00c322b3ee04b419d1979f22-p000093-l0041, 00c322b3ee04b419d1979f22-p000093-l0042, 00c322b3ee04b419d1979f22-p000093-l0046, 00c322b3ee04b419d1979f22-p000093-l0053, 00c322b3ee04b419d1979f22-p000115-l0024 |
| keraia | 511 | 555 | 00c322b3ee04b419d1979f22-p000055-l0006, 00c322b3ee04b419d1979f22-p000055-l0011, 00c322b3ee04b419d1979f22-p000115-l0019, 00c322b3ee04b419d1979f22-p000129-l0037, 00c322b3ee04b419d1979f22-p000166-l0040, 042c93b2591368d437f27678-p000075-l0036, 042c93b2591368d437f27678-p000148-l0011, 043b454a8c255b6690fd3777-p000019-l0042, 043b454a8c255b6690fd3777-p000019-l0063, 043b454a8c255b6690fd3777-p000019-l0079, 07dc0ec3a36ef8d4433de416-p000083-l0036, 0907df739607faca673d2169-p000033-l0007, 0cb3f67240837f77ee728005-p000005-l0042, 0cb3f67240837f77ee728005-p000005-l0044, 0cb3f67240837f77ee728005-p000005-l0049, 0cb3f67240837f77ee728005-p000005-l0050, 0cb3f67240837f77ee728005-p000019-l0052, 0cb3f67240837f77ee728005-p000019-l0056, 10349bf796b8cd19c7415595-p000121-l0009, 10349bf796b8cd19c7415595-p000157-l0029 |
| other | 7498 | 97421 | 00c322b3ee04b419d1979f22-p000015-l0009, 00c322b3ee04b419d1979f22-p000015-l0035, 00c322b3ee04b419d1979f22-p000015-l0037, 00c322b3ee04b419d1979f22-p000015-l0041, 00c322b3ee04b419d1979f22-p000015-l0046, 00c322b3ee04b419d1979f22-p000015-l0051, 00c322b3ee04b419d1979f22-p000015-l0059, 00c322b3ee04b419d1979f22-p000015-l0069, 00c322b3ee04b419d1979f22-p000015-l0073, 00c322b3ee04b419d1979f22-p000015-l0076, 00c322b3ee04b419d1979f22-p000015-l0081, 00c322b3ee04b419d1979f22-p000028-l0003, 00c322b3ee04b419d1979f22-p000028-l0010, 00c322b3ee04b419d1979f22-p000028-l0011, 00c322b3ee04b419d1979f22-p000028-l0012, 00c322b3ee04b419d1979f22-p000028-l0013, 00c322b3ee04b419d1979f22-p000028-l0014, 00c322b3ee04b419d1979f22-p000028-l0016, 00c322b3ee04b419d1979f22-p000028-l0017, 00c322b3ee04b419d1979f22-p000028-l0019 |

### round1

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 67 | 69 | 00c322b3ee04b419d1979f22-p000055-l0033, 043b454a8c255b6690fd3777-p000008-l0020, 043b454a8c255b6690fd3777-p000048-l0011, 043b454a8c255b6690fd3777-p000054-l0047, 043b454a8c255b6690fd3777-p000061-l0012, 043b454a8c255b6690fd3777-p000061-l0030, 052a7a91dd9752b856b9fd8a-p000164-l0030, 052a7a91dd9752b856b9fd8a-p000188-l0005, 0b2cede5e125323a082f684b-p000021-l0002, 0bff55647d1c2acd1caa8bf3-p000120-l0015, 1092c25534f45a95669f3d2b-p000030-l0018, 143e78b5de2e6e784534ee0d-p000055-l0017, 17499e55347a68940e18597f-p000012-l0025, 241c524ed5b20f2baadf4b8b-p000041-l0005, 241c524ed5b20f2baadf4b8b-p000119-l0012, 2b1d2b5340150ddc135a2b1a-p000178-l0030, 2c8742589d947f8d749c7ba2-p000040-l0013, 2d29e5e76d90adc4cc1b093a-p000027-l0051, 2f9e996ffbdaaa3b4a9dfdcf-p000013-l0003, 2f9e996ffbdaaa3b4a9dfdcf-p000095-l0013 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 1 | 1 | 87010bf6a68a76f0e0eb368f-p000015-l0028 |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 1 | 1 | 87010bf6a68a76f0e0eb368f-p000015-l0028 |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 67 | 69 | 00c322b3ee04b419d1979f22-p000055-l0033, 043b454a8c255b6690fd3777-p000008-l0020, 043b454a8c255b6690fd3777-p000048-l0011, 043b454a8c255b6690fd3777-p000054-l0047, 043b454a8c255b6690fd3777-p000061-l0012, 043b454a8c255b6690fd3777-p000061-l0030, 052a7a91dd9752b856b9fd8a-p000164-l0030, 052a7a91dd9752b856b9fd8a-p000188-l0005, 0b2cede5e125323a082f684b-p000021-l0002, 0bff55647d1c2acd1caa8bf3-p000120-l0015, 1092c25534f45a95669f3d2b-p000030-l0018, 143e78b5de2e6e784534ee0d-p000055-l0017, 17499e55347a68940e18597f-p000012-l0025, 241c524ed5b20f2baadf4b8b-p000041-l0005, 241c524ed5b20f2baadf4b8b-p000119-l0012, 2b1d2b5340150ddc135a2b1a-p000178-l0030, 2c8742589d947f8d749c7ba2-p000040-l0013, 2d29e5e76d90adc4cc1b093a-p000027-l0051, 2f9e996ffbdaaa3b4a9dfdcf-p000013-l0003, 2f9e996ffbdaaa3b4a9dfdcf-p000095-l0013 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 1 | 1 | bf2ce6d100950eec319cef00-p000028-l0091 |
| insertions_by_class/quote | 44 | 44 | 00c322b3ee04b419d1979f22-p000028-l0007, 00c322b3ee04b419d1979f22-p000039-l0048, 042c93b2591368d437f27678-p000269-l0010, 0907df739607faca673d2169-p000021-l0059, 0b2cede5e125323a082f684b-p000040-l0006, 0bff55647d1c2acd1caa8bf3-p000072-l0006, 0bff55647d1c2acd1caa8bf3-p000136-l0006, 0bff55647d1c2acd1caa8bf3-p000136-l0028, 0bff55647d1c2acd1caa8bf3-p000167-l0009, 0bff55647d1c2acd1caa8bf3-p000184-l0029, 0bff55647d1c2acd1caa8bf3-p000184-l0030, 0bff55647d1c2acd1caa8bf3-p000215-l0009, 1495fc2311427a558abbfd88-p000014-l0006, 241c524ed5b20f2baadf4b8b-p000051-l0047, 241c524ed5b20f2baadf4b8b-p000119-l0016, 2b1d2b5340150ddc135a2b1a-p000140-l0033, 2d29e5e76d90adc4cc1b093a-p000020-l0057, 42c339ce492d83665f00774d-p000049-l0035, 453f156dc6352286456a08cb-p000209-l0034, 453f156dc6352286456a08cb-p000209-l0036 |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 round2

Deletion HOLD lines: 4204; MOVE proposal lines: 6; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 2417 | 6369 | 0efd675a10c9a91816c7a41a-p000020-l0003, 0efd675a10c9a91816c7a41a-p000020-l0004, 0efd675a10c9a91816c7a41a-p000020-l0009, 0efd675a10c9a91816c7a41a-p000020-l0010, 0efd675a10c9a91816c7a41a-p000020-l0016, 0efd675a10c9a91816c7a41a-p000020-l0020, 0efd675a10c9a91816c7a41a-p000020-l0026, 0efd675a10c9a91816c7a41a-p000020-l0033, 0efd675a10c9a91816c7a41a-p000020-l0035, 0efd675a10c9a91816c7a41a-p000032-l0010, 0efd675a10c9a91816c7a41a-p000032-l0028, 0efd675a10c9a91816c7a41a-p000032-l0031, 0efd675a10c9a91816c7a41a-p000032-l0034, 0efd675a10c9a91816c7a41a-p000032-l0035, 0efd675a10c9a91816c7a41a-p000049-l0008, 0efd675a10c9a91816c7a41a-p000049-l0017, 0efd675a10c9a91816c7a41a-p000064-l0012, 0efd675a10c9a91816c7a41a-p000064-l0021, 0efd675a10c9a91816c7a41a-p000064-l0033, 0efd675a10c9a91816c7a41a-p000064-l0035 |
| apostrophe | 258 | 279 | 0efd675a10c9a91816c7a41a-p000049-l0025, 0efd675a10c9a91816c7a41a-p000064-l0015, 0efd675a10c9a91816c7a41a-p000079-l0026, 0efd675a10c9a91816c7a41a-p000079-l0028, 0efd675a10c9a91816c7a41a-p000139-l0007, 0efd675a10c9a91816c7a41a-p000170-l0035, 1182f94b107a4cc4ada574da-p000009-l0015, 1182f94b107a4cc4ada574da-p000009-l0016, 1182f94b107a4cc4ada574da-p000045-l0025, 1182f94b107a4cc4ada574da-p000054-l0014, 1182f94b107a4cc4ada574da-p000054-l0022, 1182f94b107a4cc4ada574da-p000060-l0026, 1182f94b107a4cc4ada574da-p000064-l0013, 32aae9fec147d3b483deb96e-p000042-l0050, 32aae9fec147d3b483deb96e-p000068-l0073, 32aae9fec147d3b483deb96e-p000084-l0049, 32aae9fec147d3b483deb96e-p000093-l0051, 32aae9fec147d3b483deb96e-p000101-l0018, 32aae9fec147d3b483deb96e-p000107-l0046, 3598ebd512fe5593fddcc4ed-p000017-l0082 |
| quote | 233 | 250 | 0efd675a10c9a91816c7a41a-p000079-l0006, 0efd675a10c9a91816c7a41a-p000079-l0016, 0efd675a10c9a91816c7a41a-p000079-l0021, 0efd675a10c9a91816c7a41a-p000186-l0004, 0efd675a10c9a91816c7a41a-p000186-l0011, 0efd675a10c9a91816c7a41a-p000200-l0003, 0efd675a10c9a91816c7a41a-p000200-l0023, 1182f94b107a4cc4ada574da-p000054-l0028, 1182f94b107a4cc4ada574da-p000054-l0039, 1182f94b107a4cc4ada574da-p000054-l0045, 1182f94b107a4cc4ada574da-p000060-l0024, 290a133b0e55593eb4ecdcfd-p000262-l0090, 290a133b0e55593eb4ecdcfd-p000288-l0009, 32aae9fec147d3b483deb96e-p000011-l0056, 32aae9fec147d3b483deb96e-p000019-l0017, 32aae9fec147d3b483deb96e-p000019-l0024, 32aae9fec147d3b483deb96e-p000019-l0063, 32aae9fec147d3b483deb96e-p000042-l0008, 32aae9fec147d3b483deb96e-p000084-l0068, 3598ebd512fe5593fddcc4ed-p000039-l0044 |
| keraia | 402 | 425 | 0efd675a10c9a91816c7a41a-p000049-l0013, 0efd675a10c9a91816c7a41a-p000049-l0016, 0efd675a10c9a91816c7a41a-p000049-l0019, 0efd675a10c9a91816c7a41a-p000049-l0034, 0efd675a10c9a91816c7a41a-p000064-l0033, 0efd675a10c9a91816c7a41a-p000156-l0025, 0efd675a10c9a91816c7a41a-p000156-l0029, 0efd675a10c9a91816c7a41a-p000156-l0032, 0efd675a10c9a91816c7a41a-p000156-l0034, 0efd675a10c9a91816c7a41a-p000170-l0023, 0efd675a10c9a91816c7a41a-p000186-l0019, 0efd675a10c9a91816c7a41a-p000186-l0022, 0efd675a10c9a91816c7a41a-p000200-l0006, 0efd675a10c9a91816c7a41a-p000200-l0013, 0efd675a10c9a91816c7a41a-p000200-l0015, 1182f94b107a4cc4ada574da-p000009-l0010, 1182f94b107a4cc4ada574da-p000017-l0025, 1182f94b107a4cc4ada574da-p000037-l0030, 1182f94b107a4cc4ada574da-p000037-l0042, 290a133b0e55593eb4ecdcfd-p000307-l0139 |
| other | 2395 | 23112 | 0efd675a10c9a91816c7a41a-p000020-l0006, 0efd675a10c9a91816c7a41a-p000020-l0009, 0efd675a10c9a91816c7a41a-p000020-l0014, 0efd675a10c9a91816c7a41a-p000020-l0024, 0efd675a10c9a91816c7a41a-p000020-l0026, 0efd675a10c9a91816c7a41a-p000020-l0034, 0efd675a10c9a91816c7a41a-p000020-l0035, 0efd675a10c9a91816c7a41a-p000032-l0012, 0efd675a10c9a91816c7a41a-p000032-l0013, 0efd675a10c9a91816c7a41a-p000032-l0035, 0efd675a10c9a91816c7a41a-p000049-l0011, 0efd675a10c9a91816c7a41a-p000049-l0013, 0efd675a10c9a91816c7a41a-p000049-l0016, 0efd675a10c9a91816c7a41a-p000049-l0025, 0efd675a10c9a91816c7a41a-p000049-l0034, 0efd675a10c9a91816c7a41a-p000049-l0036, 0efd675a10c9a91816c7a41a-p000079-l0008, 0efd675a10c9a91816c7a41a-p000079-l0010, 0efd675a10c9a91816c7a41a-p000079-l0016, 0efd675a10c9a91816c7a41a-p000079-l0025 |

### round2

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 49 | 50 | 1182f94b107a4cc4ada574da-p000011-l0011, 1182f94b107a4cc4ada574da-p000021-l0034, 290a133b0e55593eb4ecdcfd-p000145-l0049, 290a133b0e55593eb4ecdcfd-p000145-l0070, 290a133b0e55593eb4ecdcfd-p000145-l0100, 32aae9fec147d3b483deb96e-p000011-l0043, 32aae9fec147d3b483deb96e-p000011-l0070, 32aae9fec147d3b483deb96e-p000068-l0020, 32aae9fec147d3b483deb96e-p000101-l0042, 32aae9fec147d3b483deb96e-p000107-l0033, 395473997d50a60416fa3684-p000051-l0001, 39fbbdfd2c8030f211a318b7-p000053-l0008, 39fbbdfd2c8030f211a318b7-p000063-l0009, 39fbbdfd2c8030f211a318b7-p000090-l0016, 39fbbdfd2c8030f211a318b7-p000090-l0035, 39fbbdfd2c8030f211a318b7-p000138-l0003, 3c4393cb8164c820f7e7b38c-p000032-l0005, 43de3c6e6a7113a4e661bb7d-p000040-l0004, 68ab53260960cbdd8d047570-p000016-l0031, 6c0a582885e55adc7c535c48-p000068-l0017 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 49 | 50 | 1182f94b107a4cc4ada574da-p000011-l0011, 1182f94b107a4cc4ada574da-p000021-l0034, 290a133b0e55593eb4ecdcfd-p000145-l0049, 290a133b0e55593eb4ecdcfd-p000145-l0070, 290a133b0e55593eb4ecdcfd-p000145-l0100, 32aae9fec147d3b483deb96e-p000011-l0043, 32aae9fec147d3b483deb96e-p000011-l0070, 32aae9fec147d3b483deb96e-p000068-l0020, 32aae9fec147d3b483deb96e-p000101-l0042, 32aae9fec147d3b483deb96e-p000107-l0033, 395473997d50a60416fa3684-p000051-l0001, 39fbbdfd2c8030f211a318b7-p000053-l0008, 39fbbdfd2c8030f211a318b7-p000063-l0009, 39fbbdfd2c8030f211a318b7-p000090-l0016, 39fbbdfd2c8030f211a318b7-p000090-l0035, 39fbbdfd2c8030f211a318b7-p000138-l0003, 3c4393cb8164c820f7e7b38c-p000032-l0005, 43de3c6e6a7113a4e661bb7d-p000040-l0004, 68ab53260960cbdd8d047570-p000016-l0031, 6c0a582885e55adc7c535c48-p000068-l0017 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 1 | 1 | dc390fceb64d9bb60a12d6b8-p000060-l0005 |
| insertions_by_class/quote | 9 | 9 | 399d224c580127635c47cd8d-p000053-l0051, 39fbbdfd2c8030f211a318b7-p000138-l0017, 43de3c6e6a7113a4e661bb7d-p000059-l0006, 6d957fa757c72e1408f65dde-p000114-l0005, 6d957fa757c72e1408f65dde-p000114-l0015, c0b5231d0f42ddb64c8cc629-p000028-l0025, dc390fceb64d9bb60a12d6b8-p000030-l0025, dc390fceb64d9bb60a12d6b8-p000082-l0002, dc390fceb64d9bb60a12d6b8-p000127-l0007 |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |

### SF6 vouli

Deletion HOLD lines: 5478; MOVE proposal lines: 0; MOVE applied: 0 checks / 0 lines.

| Deletion HOLD class | Lines | Checks | Example IDs |
|---|---:|---:|---|
| mark | 3406 | 10648 | 0271e3cae771-p000001-l0002, 0271e3cae771-p000001-l0036, 0271e3cae771-p000002-l0013, 0271e3cae771-p000002-l0019, 0271e3cae771-p000002-l0031, 0271e3cae771-p000003-l0011, 0271e3cae771-p000003-l0017, 0271e3cae771-p000003-l0034, 0271e3cae771-p000004-l0008, 0271e3cae771-p000004-l0010, 0271e3cae771-p000004-l0013, 0271e3cae771-p000005-l0002, 0271e3cae771-p000005-l0012, 0271e3cae771-p000005-l0024, 0271e3cae771-p000006-l0008, 0271e3cae771-p000006-l0016, 0271e3cae771-p000006-l0024, 0271e3cae771-p000006-l0025, 0271e3cae771-p000007-l0024, 0271e3cae771-p000007-l0029 |
| apostrophe | 278 | 292 | 0271e3cae771-p000001-l0036, 0271e3cae771-p000004-l0037, 0271e3cae771-p000006-l0030, 07bc68f92367-p000004-l0004, 0e777453c7a8-p000001-l0073, 0e777453c7a8-p000001-l0091, 0e777453c7a8-p000001-l0095, 0e777453c7a8-p000002-l0077, 0e777453c7a8-p000002-l0104, 0e777453c7a8-p000002-l0109, 0e777453c7a8-p000002-l0111, 0e777453c7a8-p000003-l0007, 0e777453c7a8-p000003-l0017, 0e777453c7a8-p000003-l0028, 0e777453c7a8-p000003-l0115, 1365c8bbb0a8-p000001-l0017, 1365c8bbb0a8-p000012-l0058, 182619a5630d-p000001-l0064, 182619a5630d-p000001-l0081, 182619a5630d-p000001-l0083 |
| quote | 245 | 248 | 0271e3cae771-p000002-l0013, 07bc68f92367-p000003-l0006, 0e777453c7a8-p000001-l0001, 18167bc1e4a8-p000002-l0016, 182619a5630d-p000002-l0065, 182619a5630d-p000005-l0051, 182619a5630d-p000009-l0059, 182619a5630d-p000009-l0060, 182619a5630d-p000009-l0061, 182619a5630d-p000009-l0062, 1f485870372f-p000001-l0002, 1f485870372f-p000003-l0010, 1f485870372f-p000003-l0017, 1f485870372f-p000010-l0016, 1f485870372f-p000010-l0017, 1f485870372f-p000010-l0018, 1ff160a5dd27-p000001-l0008, 1ff160a5dd27-p000001-l0009, 1ff160a5dd27-p000001-l0011, 1ff160a5dd27-p000009-l0026 |
| keraia | 508 | 558 | 0e777453c7a8-p000001-l0020, 0e777453c7a8-p000001-l0030, 0e777453c7a8-p000001-l0072, 0e777453c7a8-p000001-l0075, 0e777453c7a8-p000001-l0078, 0e777453c7a8-p000001-l0084, 0e777453c7a8-p000001-l0091, 0e777453c7a8-p000001-l0094, 0e777453c7a8-p000002-l0009, 0e777453c7a8-p000002-l0010, 0e777453c7a8-p000002-l0014, 0e777453c7a8-p000002-l0019, 0e777453c7a8-p000002-l0022, 0e777453c7a8-p000002-l0026, 0e777453c7a8-p000002-l0028, 0e777453c7a8-p000002-l0032, 0e777453c7a8-p000002-l0041, 0e777453c7a8-p000002-l0043, 0e777453c7a8-p000002-l0047, 0e777453c7a8-p000002-l0056 |
| other | 2899 | 41281 | 0271e3cae771-p000001-l0015, 0271e3cae771-p000001-l0028, 0271e3cae771-p000001-l0030, 0271e3cae771-p000001-l0036, 0271e3cae771-p000002-l0013, 0271e3cae771-p000002-l0015, 0271e3cae771-p000002-l0019, 0271e3cae771-p000002-l0031, 0271e3cae771-p000003-l0011, 0271e3cae771-p000003-l0036, 0271e3cae771-p000003-l0037, 0271e3cae771-p000004-l0013, 0271e3cae771-p000004-l0023, 0271e3cae771-p000004-l0037, 0271e3cae771-p000004-l0040, 0271e3cae771-p000005-l0002, 0271e3cae771-p000005-l0003, 0271e3cae771-p000006-l0009, 0271e3cae771-p000006-l0030, 0271e3cae771-p000006-l0033 |

### vouli

| Class | Lines | Edits | Example IDs (up to 20) |
|---|---:|---:|---|
| real_mark_change_edits | 6 | 6 | 8cd0e8c1f0e5-p000001-l0025, 8cd0e8c1f0e5-p000004-l0049, 91252504a906-p000025-l0013, d2e1fea00fc5-p000001-l0035, da9a31d7669d-p000025-l0003, f4e509d76b55-p000004-l0021 |
| elision_alias | 0 | 0 |  |
| consensus_elision_deleted | 0 | 0 |  |
| deletions_by_class/combining_mark | 0 | 0 |  |
| deletions_by_class/numeral_keraia | 0 | 0 |  |
| deletions_by_class/elision_apostrophe | 0 | 0 |  |
| deletions_by_class/quote | 0 | 0 |  |
| deletions_by_class/other_mark | 0 | 0 |  |
| deletions_by_class/base_letter | 0 | 0 |  |
| deletions_by_class/whitespace | 0 | 0 |  |
| deletions_by_class/other | 0 | 0 |  |
| single_source_deletions_by_class/combining_mark | 0 | 0 |  |
| single_source_deletions_by_class/numeral_keraia | 0 | 0 |  |
| single_source_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| single_source_deletions_by_class/quote | 0 | 0 |  |
| single_source_deletions_by_class/other_mark | 0 | 0 |  |
| single_source_deletions_by_class/base_letter | 0 | 0 |  |
| single_source_deletions_by_class/whitespace | 0 | 0 |  |
| single_source_deletions_by_class/other | 0 | 0 |  |
| shared_deletions_by_class/combining_mark | 0 | 0 |  |
| shared_deletions_by_class/numeral_keraia | 0 | 0 |  |
| shared_deletions_by_class/elision_apostrophe | 0 | 0 |  |
| shared_deletions_by_class/quote | 0 | 0 |  |
| shared_deletions_by_class/other_mark | 0 | 0 |  |
| shared_deletions_by_class/base_letter | 0 | 0 |  |
| shared_deletions_by_class/whitespace | 0 | 0 |  |
| shared_deletions_by_class/other | 0 | 0 |  |
| insertions_by_class/combining_mark | 6 | 6 | 8cd0e8c1f0e5-p000001-l0025, 8cd0e8c1f0e5-p000004-l0049, 91252504a906-p000025-l0013, d2e1fea00fc5-p000001-l0035, da9a31d7669d-p000025-l0003, f4e509d76b55-p000004-l0021 |
| insertions_by_class/numeral_keraia | 0 | 0 |  |
| insertions_by_class/elision_apostrophe | 0 | 0 |  |
| insertions_by_class/quote | 7 | 7 | 535ad352d7a7-p000017-l0023, 971b6ed3092a-p000004-l0002, aed4abe1314b-p000002-l0017, aeef1e4e6d36-p000005-l0025, d9b7dfa900e3-p000003-l0034, d9b7dfa900e3-p000008-l0023, f723eb9e115a-p000003-l0021 |
| insertions_by_class/other_mark | 0 | 0 |  |
| insertions_by_class/base_letter | 0 | 0 |  |
| insertions_by_class/whitespace | 0 | 0 |  |
| insertions_by_class/other | 0 | 0 |  |
