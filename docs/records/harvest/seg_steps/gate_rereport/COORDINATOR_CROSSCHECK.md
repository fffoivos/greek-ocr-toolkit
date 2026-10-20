# Coordinator finite-set script cross-check

13 unique finite-pool IDs disagree. Part 2 is excluded from this comparison.

| ID / sets | Coordinator → gate | Why | Words / expected scripts | Raw text |
| --- | --- | --- | --- | --- |
| gazette_modern--5d57e9c685c50ca6--s000-l0073 / segeval1, typology, owner_marks, band_population | None → foreign | Expected-script source policy: Cyrillic is foreign in this Greek/Latin document | [] / ['greek', 'latin'] | Скрирания |
| 252fd568-p000234-l0033 / segeval1 | None → foreign | Expected-script source policy: Cyrillic is foreign in this Greek/Latin document | [] / ['latin', 'greek'] | сродниятъ видъ Anisoplia Segetum Hbst. |
| serbia--557369d8d117b91a--s000-l0319 / calibration | None → foreign | Expected-script source policy: Cyrillic is foreign in this Greek/Latin document | [] / ['cyrillic', 'greek'] | Vignobles endommagés |
| ia_greek_latin--34f544df6c245b5d--s002-l0049 / calibration | None → foreign | Expected-script source policy: Cyrillic is foreign in this Greek/Latin document | [] / ['greek', 'latin'] | (с. 30 в.С.). |
| ia_russian--61f76a57b26f9b13--s001-l0004 / calibration, typology, rated_888, typology_marked, small, band_population, two_by_two | None → foreign | Expected-script source policy: Cyrillic is foreign in this Greek/Latin document | [] / ['cyrillic', 'greek'] | LONDON, |
| ia_russian--61f76a57b26f9b13--s001-l0005 / calibration, rated_888, band_population | None → foreign | Expected-script source policy: Cyrillic is foreign in this Greek/Latin document | [] / ['cyrillic', 'greek'] | TRUBNER & Co. 60, PATERNOSTER ROW, |
| serbia--3ab59a8d4ee49339--s005-l0014 / calibration, typology, owner_marks, rated_888, band_population | None → foreign | Expected-script source policy: Cyrillic is foreign in this Greek/Latin document | [] / ['cyrillic', 'greek'] | INCAII. |
| serbia--e7935cdb3dfeaf10--s006-l0006 / calibration, rated_888, band_population | None → foreign | Expected-script source policy: Cyrillic is foreign in this Greek/Latin document | [] / ['cyrillic', 'greek'] | ,,Drum prüfe, wer sich ewig bindet". |
| ia_russian--4ce4c0e3183ce075--s003-l0030 / calibration | None → foreign | Expected-script source policy: Cyrillic is foreign in this Greek/Latin document | [] / ['cyrillic', 'greek'] | (1) Gadus callaris. |
| 4b2c4367-p000547-l0056 / cells | None → foreign | Expected-script source policy: Cyrillic is foreign in this Greek/Latin document | [] / ['latin', 'greek'] | родъ Aranea |
| serbia--b6450341d87fb144--s000-l0005 / typology, small, sheet | None → foreign | Expected-script source policy: Cyrillic is foreign in this Greek/Latin document | [] / ['cyrillic', 'greek'] | Mi |
| ia_russian--2a45a0561eb05739--s002-l0002 / typology, typology_marked, small, band_population, two_by_two | None → foreign | Expected-script source policy: Cyrillic is foreign in this Greek/Latin document | [] / ['cyrillic', 'greek'] | OREGON |
| serbia--557369d8d117b91a--s000-l0028 / typology, typology_marked, band_population, sheet | None → foreign | Expected-script source policy: Cyrillic is foreign in this Greek/Latin document | [] / ['cyrillic', 'greek'] | En général |

All census differences (including codec and tokenization differences) are in coordinator_census_disagreements.jsonl.