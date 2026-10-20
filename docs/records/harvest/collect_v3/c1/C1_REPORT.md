# C1 report: W1 uniform 100-card label checks (17 Oct 2026)

**Method.** 14 strata, 100 uniform seeded cards each (seed `20261016:C1:W1:<source>:<class>[:<stratum>]`), LABEL_CHECK_v2 unchanged. Two Opus readers per stratum (50 cards each), run one stratum at a time. Gate: letters ≥90 and crop_ok ≥90 (point estimate, n=100). Under the coordinator's ruling, a printed lunate ϲ labelled σ counts as wrong_letter (strict). The codec-convention column counts those cards as correct. Verdicts are in `verdicts/`, aggregates in `c1_results.json`, and the aggregator in `c1_agg.py`. The release statuses are in `../release_exclusions/unchecked_strata.json`.

**Blinding label: KEY-IN-REACH (not opened, per transcripts).** In each card folder, `crops` was a symlink to `~/Projects/collect-v3-data/run/W1/c1/<set>/crops`. The `<set>_key.json` files sat one level above that. The two bsb poly1850 readers had that key folder as their working directory, and one reader's `ls -la` printed the link target. The prompts said "Never open key files", and no transcript shows a key read. The yer adjudication carries the same label: its key.json was in the same folder and was printed by one `ls`, not opened. This does not invalidate the results. Evidence: spell-check track audit, `greek-ocr-toolkit-spellcheck/docs/CLEANUP_PLAN_20261017_blinding.md` §7 (C1) and §3 (yer), commit 291f581a. From the T6b lekythos checks on, crops are copied into the checker folder and no key sits within reach.

| # | stratum | letters (strict) | letters (codec conv.) | marks | crop_ok | status | marks_bias |
|---|---|---|---|---|---|---|---|
| 1 | bsb_poly1850 / poly1850 | 96 | 96 | 92/100 | 95 | c1_pass |  |
| 2 | ia_poly1850 / poly1850 | 93 | 95 | 87/100 | 95 | c1_pass |  |
| 3 | ia_poly1850 / mixed_greek_latin | 90 | 91 | 89/100 | 97 | c1_pending |  |
| 4 | nlg / poly1850 | 95 | 95 | 92/100 | 93 | c1_pass | breathing_dropped |
| 5 | nlg / poly1900 | 99 | 99 | 85/100 | 93 | c1_pass | grave_to_acute |
| 6 | nlg / greek_poly | 98 | 98 | 92/100 | 99 | c1_pass |  |
| 7 | ia_russian / cyrillic | 74 | 74 | 20/20 | 97 | c1_fail |  |
| 8 | serbia / cyrillic | 97 | 97 | 0/4 | 92 | c1_pass |  |
| 9 | elstat / numerics_tables | 98 | 98 | na | 99 | c1_pass |  |
| 10 | gazette_modern / modern_scanned / probe_1982_1985 | 86 | 86 | 98/100 | 70 | c1_fail |  |
| 11 | gazette_modern / modern_scanned / measured_1986_1990 | 98 | 98 | 98/100 | 82 | c1_fail |  |
| 12 | kosmopolis / poly1900 | 98 | 98 | 86/100 | 53 | c1_fail |  |
| 13 | lekythos / poly1900 | 95 | 95 | 84/100 | 57 | c1_fail | grave_to_acute |
| 14 | ia_poly1850 / latin | 89 | 89 | 5/5 | 83 | c1_fail |  |

**Passed (7):** bsb poly1850; ia_poly1850 poly1850; nlg poly1850, poly1900 and greek_poly; serbia cyrillic; elstat numerics_tables. All other W1 strata stay excluded from release builds. That covers 63 unchecked strata, including every latin stratum and bsb latin.

**Rulings recorded**
- **ia_poly1850 mixed_greek_latin:** boundary pass at 90 letters. It stays c1_pending until two things happen: the ia_greek_latin lookalike admission rule is extended to it (a rules.py change, after W2), and a fresh 100-card draw passes.
- **ia_russian cyrillic:** fail. Google writes a printed word-final ъ as ь in pre-1918 orthography; see `yer_adjudication/` and the next section. It stays out of W2.
- **Gazette (both strata), kosmopolis and lekythos:** these fail on crop_ok with the original crops. Letters are good where the crop is good: Gazette probe 65/70 on crop-ok cards. Qualification runs only through the T6b masked cards (letters and crop_ok ≥90% on the same 100 masked cards); a pass admits rows to the wave-1d arm only. The same masked cards serve as the W2 Gazette probe gate. Before the T6b draw, rows flagged `screen_merged` or `rotated_crop` (height > width, ≥4 letters) are dropped at the row level:
  - gazette: 1,392 + 98 (767 rotated in all, 669 of them also merged);
  - kosmopolis: 676 + 0;
  - lekythos: 1,124 + 0.
  - Held Gazette candidates: 16,691 (corrects an earlier 20,689).
- **ia_poly1850 latin:** fail at 89. Every latin stratum stays excluded; if latin is admitted later, it is capped at the data-plan quota.
- **elstat:** 75 rows with a digit-hyphen thousands group form a separate line-level exclusion class (`separator_ambiguous`), pending an ink check. There is no text rewrite: the hyphen may be a printed range.

**Label-rule and codec tallies** (for codec v2.1 and the label rules; counted per card):
- superscript: 7
- dash: 21
- separator: 6
- lunate ϲ: 3 cards

**For other tracks**
- Mark-error cards for the spell-check precision sample: 101, with line ids in `c1_results.json` → `mark_errors`, all on the Google-label side.
- Neighbour-ink crop cards for the T6b evidence: 172, under `neighbour_ink`.
- `marks_bias` records strata whose mark errors mostly run one way: grave_to_acute in nlg poly1900 (9/100) and lekythos (12/100); breathing_dropped in nlg poly1850 (5/100). Admission by letters is unaffected.

**Checker-error record (first measured)**
- ia_russian yer adjudication on 59 cards with 65 masked positions, ink truth from two blind Opus readers.
- C1 checker: 1 likely miss in 19 cards (c084, a bold condensed face).
- Earlier v2 checker: 0 misses in 40 cards.
- The v2 sample was modern orthography, which explains its 38/40 pass.

**Later item (not a task), ъ repair:** Google's word-final ъ was never wrong (0 of 26). Only the positions where Google wrote ь need an ink check for the hard sign's flag. The orthographic prior is right on about 96% of decided positions, but the ink decides.

**W2 selection (in the gate request).** IA poly1850 books are ranked by W1 Greek-script rows per page. Books under 1 Greek row per page are dropped (the floor ruling): 8 books, 60 W1 pages. A draft gate for the coordinator is in `c1_gate_draft.json`; it is not in the run root.
