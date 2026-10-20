# Label Quality Scoreboard v2.4

Marks change: Google → sf6 release falls from 87 to 16 errors on audit100's 2232 known heads on the sample. DEV release coverage is only 2/391 certified lines, so its weighted population change is not measured; substitution60 has no saved release coverage. The DEV Google baseline is 0.202% weighted head errors, using the 976 resolved cards and excluding 671 unread cards and 2 UNKNOWN. DEV is out-of-sample for frozen sf6 and in-sample for S8b; audit results describe sampled decisions.

## Marks headline

DEV (weighted_stratified): population delta not measured (2/391 certified lines covered; covered subset weighted delta -0.044 pp, degenerate document-within-wave bootstrap); audit100 (decision_audit): 87 → 16 errors / 2232 heads on the sample; substitution60 (decision_audit): release delta not measured (0/57 certified lines covered)

## Truth v1.1

61,463 items; SHA256 `b54e238ccfd89df91cabf5255ad8c9b8b26701304fb0bf552f12e4baf435fa5b`. Added DEV 21,892 heads and substitution60 63 heads. Frozen v1 and flags are unchanged. Tier A DEV admission: two blind Opus readers plus third-reader tiebreak, controls 82/84 each with zero shared misses, per lead ruling and [S8a6 source](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck-s8/docs/labelfix/spellcheck/S8a6_DEV_TRUTH.md). No new readers ran.

DEV is `weighted_stratified`, in-sample for S8b and out-of-sample for frozen sf6. The 600 lines were stratified by wave; cards include all disagreement word groups and 5% all-agree words per wave. Only 976 resolved cards enter the card ledger: 671 unadjudicated data cards and 2 UNKNOWN are excluded, as are controls. Eight resolved cards contain no letters and contribute zero mark heads; 968 cards contribute the 21,892 DEV mark heads. All 976 resolved card IDs, printed forms and saved weights are retained in truth_v1_1_dev_cards.jsonl. Substitution60 is a decision audit: 63 certified heads on 57 lines; 3 lines remain UNKNOWN. Only the reviewed heads are certified.

## Weights, population and uncertainty

Population: v2 train greek_poly, training wave; S8 600-line DEV connected-word census (4,942 groups). The estimate is limited to the documented DEV draw; it does not establish performance outside these DEV lines. Every slot inherits its saved S8a6 card weight from `S8_DEV/evidence/dev_truth.jsonl.gz` (inverse card-inclusion × wave-cut weight). Weights are read verbatim, never re-derived, rescaled or redistributed after exclusions. Hájek error ratios use weighted error sums divided by weighted known head opportunities. Unweighted counts are labelled "on the sample".

The weighted Google baseline and every covered version use 4,000 percentile bootstrap replicates, seed 20261017, independently resampling documents with replacement within each wave, retaining fixed card weights and all contributing slots per document. The machine ledger retains weighted numerators, denominators, documents per wave and valid replicates. Reader error and extrapolation beyond the source draw are not included. Generic version tables retain unweighted sample counts and cannot promote weighted_stratified to an unweighted population rate.

**Limited release comparison:** verified SX1 v2 covers only 2/391 certified DEV lines (76 heads in two documents, one per contributing wave) and no substitution60 lines. A weighted paired difference with 4,000 document-within-wave bootstrap replicates is retained for that covered subset; its interval is degenerate because each contributing wave has only one document. It is explicitly not a DEV population estimate. Full-DEV and substitution60 release deltas remain not measured. The saved S8a6 `frozen_AB` values include HOLD proposals and cannot be substituted for released labels. Full-DEV coverage is required to compute the requested population headline offline. Audit100 has 99/99 actual ENSEMBLE_AB releases; its selected decision-audit delta is descriptive, with document-bootstrap intervals in the headline ledger.

## BASELINE — Google against truth

Within each class, measured rows come first: C1 card verdicts (explicit marks_y/n, letters_y/n and crop_y/n), locked strata where certified, other admitted strata and DEV weighted. One collapsed line then lists every unmeasured scope. C1 aggregate verdicts do not imply per-head truth. Head/direction rows are shown only for DEV, audit100 and substitution60, using each known head as the denominator; absent, extra and wrong-positive marks are mutually exclusive errors. Unknown and unavailable heads are excluded. Partial substitution truth does not certify other heads.

| Class / metric | Stratum | Measurement | sample_type | Tier | Source |
|---|---|---|---|---|---|
| polytonic marks / letters / digits / words (strict card verdict) | bsb_poly1850__poly1850 | 4/100; 4.00%; 95% Wilson CI 1.57–9.84%; letters_y/n 96/4 | uniform | A | C1/bsb_poly1850__poly1850 |
| polytonic marks / marks (any head; card verdict) | bsb_poly1850__poly1850 | 8/100; 8.00%; 95% Wilson CI 4.11–15.00%; marks_y/n 92/8 | uniform | A | C1/bsb_poly1850__poly1850 |
| polytonic marks / crop (physical card verdict) | bsb_poly1850__poly1850 | 5/100; 5.00%; 95% Wilson CI 2.15–11.18%; crop_y/n 95/5 | uniform | A | C1/bsb_poly1850__poly1850 |
| polytonic marks / missing_mark (any head; tagged cards) | bsb_poly1850__poly1850 | 4/100; 4.00%; 95% Wilson CI 1.57–9.84% | uniform | A | C1/bsb_poly1850__poly1850 |
| polytonic marks / extra_mark (any head; tagged cards) | bsb_poly1850__poly1850 | 0/100; 0.00%; 95% Wilson CI 0.00–3.70% | uniform | A | C1/bsb_poly1850__poly1850 |
| polytonic marks / wrong_mark (any head; tagged cards) | bsb_poly1850__poly1850 | 4/100; 4.00%; 95% Wilson CI 1.57–9.84% | uniform | A | C1/bsb_poly1850__poly1850 |
| polytonic marks / letters / digits / words (strict card verdict) | ia_poly1850__poly1850 | 7/100; 7.00%; 95% Wilson CI 3.43–13.75%; letters_y/n 93/7 | uniform | A | C1/ia_poly1850__poly1850 |
| polytonic marks / marks (any head; card verdict) | ia_poly1850__poly1850 | 13/100; 13.00%; 95% Wilson CI 7.76–20.98%; marks_y/n 87/13 | uniform | A | C1/ia_poly1850__poly1850 |
| polytonic marks / crop (physical card verdict) | ia_poly1850__poly1850 | 5/100; 5.00%; 95% Wilson CI 2.15–11.18%; crop_y/n 95/5 | uniform | A | C1/ia_poly1850__poly1850 |
| polytonic marks / missing_mark (any head; tagged cards) | ia_poly1850__poly1850 | 6/100; 6.00%; 95% Wilson CI 2.78–12.48% | uniform | A | C1/ia_poly1850__poly1850 |
| polytonic marks / extra_mark (any head; tagged cards) | ia_poly1850__poly1850 | 1/100; 1.00%; 95% Wilson CI 0.18–5.45% | uniform | A | C1/ia_poly1850__poly1850 |
| polytonic marks / wrong_mark (any head; tagged cards) | ia_poly1850__poly1850 | 6/100; 6.00%; 95% Wilson CI 2.78–12.48% | uniform | A | C1/ia_poly1850__poly1850 |
| polytonic marks / letters / digits / words (strict card verdict) | kosmopolis__poly1900 | 2/100; 2.00%; 95% Wilson CI 0.55–7.00%; letters_y/n 98/2 | uniform | A | C1/kosmopolis__poly1900 |
| polytonic marks / marks (any head; card verdict) | kosmopolis__poly1900 | 14/100; 14.00%; 95% Wilson CI 8.53–22.14%; marks_y/n 86/14 | uniform | A | C1/kosmopolis__poly1900 |
| polytonic marks / crop (physical card verdict) | kosmopolis__poly1900 | 47/100; 47.00%; 95% Wilson CI 37.51–56.71%; crop_y/n 53/47 | uniform | A | C1/kosmopolis__poly1900 |
| polytonic marks / missing_mark (any head; tagged cards) | kosmopolis__poly1900 | 7/100; 7.00%; 95% Wilson CI 3.43–13.75% | uniform | A | C1/kosmopolis__poly1900 |
| polytonic marks / extra_mark (any head; tagged cards) | kosmopolis__poly1900 | 0/100; 0.00%; 95% Wilson CI 0.00–3.70% | uniform | A | C1/kosmopolis__poly1900 |
| polytonic marks / wrong_mark (any head; tagged cards) | kosmopolis__poly1900 | 8/100; 8.00%; 95% Wilson CI 4.11–15.00% | uniform | A | C1/kosmopolis__poly1900 |
| polytonic marks / letters / digits / words (strict card verdict) | lekythos__poly1900 | 5/100; 5.00%; 95% Wilson CI 2.15–11.18%; letters_y/n 95/5 | uniform | A | C1/lekythos__poly1900 |
| polytonic marks / marks (any head; card verdict) | lekythos__poly1900 | 16/100; 16.00%; 95% Wilson CI 10.10–24.42%; marks_y/n 84/16 | uniform | A | C1/lekythos__poly1900 |
| polytonic marks / crop (physical card verdict) | lekythos__poly1900 | 43/100; 43.00%; 95% Wilson CI 33.73–52.78%; crop_y/n 57/43 | uniform | A | C1/lekythos__poly1900 |
| polytonic marks / missing_mark (any head; tagged cards) | lekythos__poly1900 | 5/100; 5.00%; 95% Wilson CI 2.15–11.18% | uniform | A | C1/lekythos__poly1900 |
| polytonic marks / extra_mark (any head; tagged cards) | lekythos__poly1900 | 0/100; 0.00%; 95% Wilson CI 0.00–3.70% | uniform | A | C1/lekythos__poly1900 |
| polytonic marks / wrong_mark (any head; tagged cards) | lekythos__poly1900 | 11/100; 11.00%; 95% Wilson CI 6.25–18.63% | uniform | A | C1/lekythos__poly1900 |
| polytonic marks / letters / digits / words (strict card verdict) | nlg__greek_poly | 1/99; 1.01%; 95% Wilson CI 0.18–5.50%; unknown 1; letters_y/n 98/1 | uniform | A | C1/nlg__greek_poly |
| polytonic marks / marks (any head; card verdict) | nlg__greek_poly | 8/100; 8.00%; 95% Wilson CI 4.11–15.00%; marks_y/n 92/8 | uniform | A | C1/nlg__greek_poly |
| polytonic marks / crop (physical card verdict) | nlg__greek_poly | 1/100; 1.00%; 95% Wilson CI 0.18–5.45%; crop_y/n 99/1 | uniform | A | C1/nlg__greek_poly |
| polytonic marks / missing_mark (any head; tagged cards) | nlg__greek_poly | 1/100; 1.00%; 95% Wilson CI 0.18–5.45% | uniform | A | C1/nlg__greek_poly |
| polytonic marks / extra_mark (any head; tagged cards) | nlg__greek_poly | 1/100; 1.00%; 95% Wilson CI 0.18–5.45% | uniform | A | C1/nlg__greek_poly |
| polytonic marks / wrong_mark (any head; tagged cards) | nlg__greek_poly | 6/100; 6.00%; 95% Wilson CI 2.78–12.48% | uniform | A | C1/nlg__greek_poly |
| polytonic marks / letters / digits / words (strict card verdict) | nlg__poly1850 | 5/100; 5.00%; 95% Wilson CI 2.15–11.18%; letters_y/n 95/5 | uniform | A | C1/nlg__poly1850 |
| polytonic marks / marks (any head; card verdict) | nlg__poly1850 | 8/100; 8.00%; 95% Wilson CI 4.11–15.00%; marks_y/n 92/8 | uniform | A | C1/nlg__poly1850 |
| polytonic marks / crop (physical card verdict) | nlg__poly1850 | 7/100; 7.00%; 95% Wilson CI 3.43–13.75%; crop_y/n 93/7 | uniform | A | C1/nlg__poly1850 |
| polytonic marks / missing_mark (any head; tagged cards) | nlg__poly1850 | 5/100; 5.00%; 95% Wilson CI 2.15–11.18% | uniform | A | C1/nlg__poly1850 |
| polytonic marks / extra_mark (any head; tagged cards) | nlg__poly1850 | 0/100; 0.00%; 95% Wilson CI 0.00–3.70% | uniform | A | C1/nlg__poly1850 |
| polytonic marks / wrong_mark (any head; tagged cards) | nlg__poly1850 | 4/100; 4.00%; 95% Wilson CI 1.57–9.84% | uniform | A | C1/nlg__poly1850 |
| polytonic marks / letters / digits / words (strict card verdict) | nlg__poly1900 | 0/99; 0.00%; 95% Wilson CI 0.00–3.74%; unknown 1; letters_y/n 99/0 | uniform | A | C1/nlg__poly1900 |
| polytonic marks / marks (any head; card verdict) | nlg__poly1900 | 15/100; 15.00%; 95% Wilson CI 9.31–23.28%; marks_y/n 85/15 | uniform | A | C1/nlg__poly1900 |
| polytonic marks / crop (physical card verdict) | nlg__poly1900 | 7/100; 7.00%; 95% Wilson CI 3.43–13.75%; crop_y/n 93/7 | uniform | A | C1/nlg__poly1900 |
| polytonic marks / missing_mark (any head; tagged cards) | nlg__poly1900 | 5/100; 5.00%; 95% Wilson CI 2.15–11.18% | uniform | A | C1/nlg__poly1900 |
| polytonic marks / extra_mark (any head; tagged cards) | nlg__poly1900 | 1/100; 1.00%; 95% Wilson CI 0.18–5.45% | uniform | A | C1/nlg__poly1900 |
| polytonic marks / wrong_mark (any head; tagged cards) | nlg__poly1900 | 11/100; 11.00%; 95% Wilson CI 6.25–18.63% | uniform | A | C1/nlg__poly1900 |
| polytonic marks / letters (masked card verdict) | gazette_modern/dialogue_fiction/measured_1986_1990/masked gazette_modern | 0/4; 0.00%; 95% Wilson CI 0.00–48.99% | uniform | A | T6b/gazette_modern |
| polytonic marks / marks (masked card verdict) | gazette_modern/dialogue_fiction/measured_1986_1990/masked gazette_modern | 0/4; 0.00%; 95% Wilson CI 0.00–48.99% | uniform | A | T6b/gazette_modern |
| polytonic marks / crop_ok (masked card verdict) | gazette_modern/dialogue_fiction/measured_1986_1990/masked gazette_modern | 1/4; 25.00%; 95% Wilson CI 4.56–69.94% | uniform | A | T6b/gazette_modern |
| polytonic marks / letters (masked card verdict) | gazette_modern/dialogue_fiction/probe_1982_1985/masked gazette_modern | 0/3; 0.00%; 95% Wilson CI 0.00–56.15% | uniform | A | T6b/gazette_modern |
| polytonic marks / marks (masked card verdict) | gazette_modern/dialogue_fiction/probe_1982_1985/masked gazette_modern | 0/3; 0.00%; 95% Wilson CI 0.00–56.15% | uniform | A | T6b/gazette_modern |
| polytonic marks / crop_ok (masked card verdict) | gazette_modern/dialogue_fiction/probe_1982_1985/masked gazette_modern | 0/3; 0.00%; 95% Wilson CI 0.00–56.15% | uniform | A | T6b/gazette_modern |
| polytonic marks / letters (masked card verdict) | kosmopolis/dialogue_fiction/masked kosmopolis | 0/9; 0.00%; 95% Wilson CI 0.00–29.91% | uniform | A | T6b/kosmopolis |
| polytonic marks / marks (masked card verdict) | kosmopolis/dialogue_fiction/masked kosmopolis | 0/9; 0.00%; 95% Wilson CI 0.00–29.91% | uniform | A | T6b/kosmopolis |
| polytonic marks / crop_ok (masked card verdict) | kosmopolis/dialogue_fiction/masked kosmopolis | 0/9; 0.00%; 95% Wilson CI 0.00–29.91% | uniform | A | T6b/kosmopolis |
| polytonic marks / letters (masked card verdict) | kosmopolis/poly1850/masked kosmopolis | 0/11; 0.00%; 95% Wilson CI 0.00–25.88% | uniform | A | T6b/kosmopolis |
| polytonic marks / marks (masked card verdict) | kosmopolis/poly1850/masked kosmopolis | 0/11; 0.00%; 95% Wilson CI 0.00–25.88% | uniform | A | T6b/kosmopolis |
| polytonic marks / crop_ok (masked card verdict) | kosmopolis/poly1850/masked kosmopolis | 1/11; 9.09%; 95% Wilson CI 1.62–37.74% | uniform | A | T6b/kosmopolis |
| polytonic marks / letters (masked card verdict) | kosmopolis/poly1900/masked kosmopolis | 1/69; 1.45%; 95% Wilson CI 0.26–7.76%; unknown 1 | uniform | A | T6b/kosmopolis |
| polytonic marks / marks (masked card verdict) | kosmopolis/poly1900/masked kosmopolis | 9/70; 12.86%; 95% Wilson CI 6.91–22.66% | uniform | A | T6b/kosmopolis |
| polytonic marks / crop_ok (masked card verdict) | kosmopolis/poly1900/masked kosmopolis | 2/70; 2.86%; 95% Wilson CI 0.79–9.83% | uniform | A | T6b/kosmopolis |
| polytonic marks / letters (masked card verdict) | lekythos/dialogue_fiction/masked lekythos | 0/6; 0.00%; 95% Wilson CI 0.00–39.03% | uniform | A | T6b/lekythos |
| polytonic marks / marks (masked card verdict) | lekythos/dialogue_fiction/masked lekythos | 2/6; 33.33%; 95% Wilson CI 9.68–70.00% | uniform | A | T6b/lekythos |
| polytonic marks / crop_ok (masked card verdict) | lekythos/dialogue_fiction/masked lekythos | 1/6; 16.67%; 95% Wilson CI 3.01–56.35% | uniform | A | T6b/lekythos |
| polytonic marks / letters (masked card verdict) | lekythos/poly1900/masked lekythos | 2/92; 2.17%; 95% Wilson CI 0.60–7.58% | uniform | A | T6b/lekythos |
| polytonic marks / marks (masked card verdict) | lekythos/poly1900/masked lekythos | 9/92; 9.78%; 95% Wilson CI 5.23–17.56% | uniform | A | T6b/lekythos |
| polytonic marks / crop_ok (masked card verdict) | lekythos/poly1900/masked lekythos | 3/92; 3.26%; 95% Wilson CI 1.12–9.15% | uniform | A | T6b/lekythos |
| polytonic marks / all known mark heads | S8 DEV / all five waves | weighted estimate 0.202%; 95% document-within-wave bootstrap CI 0.116–0.336%; 73/21892 on the sample | weighted_stratified | A | S8_DEV |
| polytonic marks / breathing / missing | S8 DEV / all five waves | weighted estimate 0.061%; 95% document-within-wave bootstrap CI 0.018–0.117%; 6/5473 on the sample | weighted_stratified | A | S8_DEV |
| polytonic marks / breathing / extra | S8 DEV / all five waves | weighted estimate 0.056%; 95% document-within-wave bootstrap CI 0.012–0.117%; 5/5473 on the sample | weighted_stratified | A | S8_DEV |
| polytonic marks / breathing / wrong mark | S8 DEV / all five waves | weighted estimate 0.033%; 95% document-within-wave bootstrap CI 0.000–0.078%; 3/5473 on the sample | weighted_stratified | A | S8_DEV |
| polytonic marks / accent / missing | S8 DEV / all five waves | weighted estimate 0.338%; 95% document-within-wave bootstrap CI 0.092–0.784%; 16/5473 on the sample | weighted_stratified | A | S8_DEV |
| polytonic marks / accent / extra | S8 DEV / all five waves | weighted estimate 0.051%; 95% document-within-wave bootstrap CI 0.010–0.103%; 5/5473 on the sample | weighted_stratified | A | S8_DEV |
| polytonic marks / accent / wrong mark | S8 DEV / all five waves | weighted estimate 0.209%; 95% document-within-wave bootstrap CI 0.126–0.317%; 30/5473 on the sample | weighted_stratified | A | S8_DEV |
| polytonic marks / dialytika / missing | S8 DEV / all five waves | weighted estimate 0.000%; 95% document-within-wave bootstrap CI 0.000–0.000%; 0/5473 on the sample | weighted_stratified | A | S8_DEV |
| polytonic marks / dialytika / extra | S8 DEV / all five waves | weighted estimate 0.000%; 95% document-within-wave bootstrap CI 0.000–0.000%; 0/5473 on the sample | weighted_stratified | A | S8_DEV |
| polytonic marks / dialytika / wrong mark | S8 DEV / all five waves | weighted estimate 0.000%; 95% document-within-wave bootstrap CI 0.000–0.000%; 0/5473 on the sample | weighted_stratified | A | S8_DEV |
| polytonic marks / subscript / missing | S8 DEV / all five waves | weighted estimate 0.004%; 95% document-within-wave bootstrap CI 0.000–0.012%; 1/5473 on the sample | weighted_stratified | A | S8_DEV |
| polytonic marks / subscript / extra | S8 DEV / all five waves | weighted estimate 0.056%; 95% document-within-wave bootstrap CI 0.009–0.117%; 7/5473 on the sample | weighted_stratified | A | S8_DEV |
| polytonic marks / subscript / wrong mark | S8 DEV / all five waves | weighted estimate 0.000%; 95% document-within-wave bootstrap CI 0.000–0.000%; 0/5473 on the sample | weighted_stratified | A | S8_DEV |
| polytonic marks / breathing / missing | audit100 / certified heads only | 25/558; 4.48%; 95% Wilson CI 3.05–6.53% on the sample | decision_audit | A | audit100 |
| polytonic marks / breathing / extra | audit100 / certified heads only | 0/558; 0.00%; 95% Wilson CI 0.00–0.68% on the sample | decision_audit | A | audit100 |
| polytonic marks / breathing / wrong mark | audit100 / certified heads only | 0/558; 0.00%; 95% Wilson CI 0.00–0.68% on the sample | decision_audit | A | audit100 |
| polytonic marks / accent / missing | audit100 / certified heads only | 20/558; 3.58%; 95% Wilson CI 2.33–5.47% on the sample | decision_audit | A | audit100 |
| polytonic marks / accent / extra | audit100 / certified heads only | 0/558; 0.00%; 95% Wilson CI 0.00–0.68% on the sample | decision_audit | A | audit100 |
| polytonic marks / accent / wrong mark | audit100 / certified heads only | 0/558; 0.00%; 95% Wilson CI 0.00–0.68% on the sample | decision_audit | A | audit100 |
| polytonic marks / dialytika / missing | audit100 / certified heads only | 1/558; 0.18%; 95% Wilson CI 0.03–1.01% on the sample | decision_audit | A | audit100 |
| polytonic marks / dialytika / extra | audit100 / certified heads only | 0/558; 0.00%; 95% Wilson CI 0.00–0.68% on the sample | decision_audit | A | audit100 |
| polytonic marks / dialytika / wrong mark | audit100 / certified heads only | 0/558; 0.00%; 95% Wilson CI 0.00–0.68% on the sample | decision_audit | A | audit100 |
| polytonic marks / subscript / missing | audit100 / certified heads only | 41/558; 7.35%; 95% Wilson CI 5.46–9.82% on the sample | decision_audit | A | audit100 |
| polytonic marks / subscript / extra | audit100 / certified heads only | 0/558; 0.00%; 95% Wilson CI 0.00–0.68% on the sample | decision_audit | A | audit100 |
| polytonic marks / subscript / wrong mark | audit100 / certified heads only | 0/558; 0.00%; 95% Wilson CI 0.00–0.68% on the sample | decision_audit | A | audit100 |
| polytonic marks / breathing / missing | substitution60 / certified heads only | 0/9; 0.00%; 95% Wilson CI 0.00–29.91% on the sample | decision_audit | A | substitution60 |
| polytonic marks / breathing / extra | substitution60 / certified heads only | 0/9; 0.00%; 95% Wilson CI 0.00–29.91% on the sample | decision_audit | A | substitution60 |
| polytonic marks / breathing / wrong mark | substitution60 / certified heads only | 9/9; 100.00%; 95% Wilson CI 70.09–100.00% on the sample | decision_audit | A | substitution60 |
| polytonic marks / accent / missing | substitution60 / certified heads only | 0/53; 0.00%; 95% Wilson CI 0.00–6.76% on the sample | decision_audit | A | substitution60 |
| polytonic marks / accent / extra | substitution60 / certified heads only | 0/53; 0.00%; 95% Wilson CI 0.00–6.76% on the sample | decision_audit | A | substitution60 |
| polytonic marks / accent / wrong mark | substitution60 / certified heads only | 53/53; 100.00%; 95% Wilson CI 93.24–100.00% on the sample | decision_audit | A | substitution60 |
| polytonic marks / dialytika / missing | substitution60 / certified heads only | 1/1; 100.00%; 95% Wilson CI 20.65–100.00% on the sample | decision_audit | A | substitution60 |
| polytonic marks / dialytika / extra | substitution60 / certified heads only | 0/1; 0.00%; 95% Wilson CI 0.00–79.35% on the sample | decision_audit | A | substitution60 |
| polytonic marks / dialytika / wrong mark | substitution60 / certified heads only | 0/1; 0.00%; 95% Wilson CI 0.00–79.35% on the sample | decision_audit | A | substitution60 |
| polytonic marks / not measured (collapsed) | remaining scopes | not measured — no head-resolved uniform/locked truth / breathing / missing: Uniform or eligible locked print truth with every breathing head certified, absent heads included, and Google-aligned direction. C1 supplies aggregate verdicts only.; no head-resolved uniform/locked truth / breathing / extra: Uniform or eligible locked print truth with every breathing head certified, absent heads included, and Google-aligned direction. C1 supplies aggregate verdicts only.; no head-resolved uniform/locked truth / breathing / wrong mark: Uniform or eligible locked print truth with every breathing head certified, absent heads included, and Google-aligned direction. C1 supplies aggregate verdicts only.; no head-resolved uniform/locked truth / accent (including grave↔acute) / missing: Uniform or eligible locked print truth with every accent (including grave↔acute) head certified, absent heads included, and Google-aligned direction. C1 supplies aggregate verdicts only.; no head-resolved uniform/locked truth / accent (including grave↔acute) / extra: Uniform or eligible locked print truth with every accent (including grave↔acute) head certified, absent heads included, and Google-aligned direction. C1 supplies aggregate verdicts only.; no head-resolved uniform/locked truth / accent (including grave↔acute) / wrong mark: Uniform or eligible locked print truth with every accent (including grave↔acute) head certified, absent heads included, and Google-aligned direction. C1 supplies aggregate verdicts only.; no head-resolved uniform/locked truth / diaeresis / missing: Uniform or eligible locked print truth with every diaeresis head certified, absent heads included, and Google-aligned direction. C1 supplies aggregate verdicts only.; no head-resolved uniform/locked truth / diaeresis / extra: Uniform or eligible locked print truth with every diaeresis head certified, absent heads included, and Google-aligned direction. C1 supplies aggregate verdicts only.; no head-resolved uniform/locked truth / diaeresis / wrong mark: Uniform or eligible locked print truth with every diaeresis head certified, absent heads included, and Google-aligned direction. C1 supplies aggregate verdicts only.; no head-resolved uniform/locked truth / subscript / missing: Uniform or eligible locked print truth with every subscript head certified, absent heads included, and Google-aligned direction. C1 supplies aggregate verdicts only.; no head-resolved uniform/locked truth / subscript / extra: Uniform or eligible locked print truth with every subscript head certified, absent heads included, and Google-aligned direction. C1 supplies aggregate verdicts only.; no head-resolved uniform/locked truth / subscript / wrong mark: Uniform or eligible locked print truth with every subscript head certified, absent heads included, and Google-aligned direction. C1 supplies aggregate verdicts only.; wikisource i-a (selected word scopes) / letters; selected locked scopes: Uniform full-line pixel adjudication and complete Google coverage; existing 24 word scopes are disagreement-enriched, population_eligible=false.; kosmopolis / poly1850 / masked / letters source inventory: Bind class-specific raw Google pixel truth with a benchmark A/B/C reader tier; source records final Sol gate verdicts, which are not silently promoted.; kosmopolis / poly1850 / masked / marks source inventory: Opus mark adjudication is pending in this source.; kosmopolis / poly1850 / masked / crop_ok source inventory: Bind class-specific raw Google pixel truth with a benchmark A/B/C reader tier; source records final Sol gate verdicts, which are not silently promoted. | not measured | not assigned | C1 + locked strata; R0_ia_letters; masked/kosmo2 |
| capitals / not measured (collapsed) | remaining scopes | not measured — no eligible class-specific truth / capitals: Uniform or eligible locked capital-slot print truth, including correct controls.; headings_caps / first masked draw / letters source inventory: Bind class-specific raw Google pixel truth with a benchmark A/B/C reader tier; source records final Sol gate verdicts, which are not silently promoted.; headings_caps / first masked draw / marks source inventory: Opus mark adjudication is pending in this source.; headings_caps / first masked draw / crop_ok source inventory: Bind class-specific raw Google pixel truth with a benchmark A/B/C reader tier; source records final Sol gate verdicts, which are not silently promoted.; headings_caps / remasked fresh draw / letters source inventory: Bind class-specific raw Google pixel truth with a benchmark A/B/C reader tier; source records final Sol gate verdicts, which are not silently promoted.; headings_caps / remasked fresh draw / marks source inventory: Opus mark adjudication is pending in this source.; headings_caps / remasked fresh draw / crop_ok source inventory: Bind class-specific raw Google pixel truth with a benchmark A/B/C reader tier; source records final Sol gate verdicts, which are not silently promoted. | not measured | not assigned | truth_v1 + INPUTS.md; masked/caps1; masked/caps3 |
| numeric separators / letters / digits / words (strict card verdict) | elstat__numerics_tables | 2/100; 2.00%; 95% Wilson CI 0.55–7.00%; letters_y/n 98/2 | uniform | A | C1/elstat__numerics_tables |
| numeric separators / crop (physical card verdict) | elstat__numerics_tables | 1/100; 1.00%; 95% Wilson CI 0.18–5.45%; crop_y/n 99/1 | uniform | A | C1/elstat__numerics_tables |
| numeric separators / separator-error cards (C1 adjudicated list) | elstat__numerics_tables | 3/100; 3.00%; 95% Wilson CI 1.03–8.45% | uniform | A | C1/elstat__numerics_tables |
| numeric separators / letters (masked card verdict) | gazette_modern/numerics_tables/measured_1986_1990/masked gazette_modern | 0/26; 0.00%; 95% Wilson CI 0.00–12.87% | uniform | A | T6b/gazette_modern |
| numeric separators / marks (masked card verdict) | gazette_modern/numerics_tables/measured_1986_1990/masked gazette_modern | 0/1; 0.00%; 95% Wilson CI 0.00–79.35%; na 25 | uniform | A | T6b/gazette_modern |
| numeric separators / crop_ok (masked card verdict) | gazette_modern/numerics_tables/measured_1986_1990/masked gazette_modern | 1/26; 3.85%; 95% Wilson CI 0.68–18.89% | uniform | A | T6b/gazette_modern |
| numeric separators / letters (masked card verdict) | gazette_modern/numerics_tables/probe_1982_1985/masked gazette_modern | 0/2; 0.00%; 95% Wilson CI 0.00–65.76% | uniform | A | T6b/gazette_modern |
| numeric separators / crop_ok (masked card verdict) | gazette_modern/numerics_tables/probe_1982_1985/masked gazette_modern | 0/2; 0.00%; 95% Wilson CI 0.00–65.76% | uniform | A | T6b/gazette_modern |
| numeric separators / letters (masked card verdict) | kosmopolis/numerics_tables/masked kosmopolis | 0/5; 0.00%; 95% Wilson CI 0.00–43.45% | uniform | A | T6b/kosmopolis |
| numeric separators / crop_ok (masked card verdict) | kosmopolis/numerics_tables/masked kosmopolis | 0/5; 0.00%; 95% Wilson CI 0.00–43.45% | uniform | A | T6b/kosmopolis |
| numeric separators / letters (masked card verdict) | lekythos/numerics_tables/masked lekythos | 0/1; 0.00%; 95% Wilson CI 0.00–79.35% | uniform | A | T6b/lekythos |
| numeric separators / crop_ok (masked card verdict) | lekythos/numerics_tables/masked lekythos | 0/1; 0.00%; 95% Wilson CI 0.00–79.35% | uniform | A | T6b/lekythos |
| numeric separators / not measured (collapsed) | remaining scopes | not measured — elstat__numerics_tables / marks (any head; card verdict): Diacritic-bearing uniform cards with marks verdicts.; gazette_modern/numerics_tables/probe_1982_1985/masked gazette_modern / marks (masked card verdict): Applicable certified marks verdicts.; kosmopolis/numerics_tables/masked kosmopolis / marks (masked card verdict): Applicable certified marks verdicts.; lekythos/numerics_tables/masked lekythos / marks (masked card verdict): Applicable certified marks verdicts. | not measured | not assigned | C1/elstat__numerics_tables; T6b/gazette_modern; T6b/kosmopolis; T6b/lekythos |
| punctuation and dashes / cards tagged punctuation / hyphen | bsb_poly1850__poly1850 | 2/100; 2.00%; 95% Wilson CI 0.55–7.00% | uniform | A | C1/bsb_poly1850__poly1850 |
| punctuation and dashes / cards tagged punctuation / hyphen | elstat__numerics_tables | 3/100; 3.00%; 95% Wilson CI 1.03–8.45% | uniform | A | C1/elstat__numerics_tables |
| punctuation and dashes / cards tagged punctuation / hyphen | gazette_modern__modern_scanned__measured_1986_1990 | 1/100; 1.00%; 95% Wilson CI 0.18–5.45% | uniform | A | C1/gazette_modern__modern_scanned__measured_1986_1990 |
| punctuation and dashes / cards tagged punctuation / hyphen | gazette_modern__modern_scanned__probe_1982_1985 | 8/100; 8.00%; 95% Wilson CI 4.11–15.00% | uniform | A | C1/gazette_modern__modern_scanned__probe_1982_1985 |
| punctuation and dashes / cards tagged punctuation / hyphen | ia_poly1850__latin | 2/100; 2.00%; 95% Wilson CI 0.55–7.00% | uniform | A | C1/ia_poly1850__latin |
| punctuation and dashes / cards tagged punctuation / hyphen | ia_poly1850__mixed_greek_latin | 7/100; 7.00%; 95% Wilson CI 3.43–13.75% | uniform | A | C1/ia_poly1850__mixed_greek_latin |
| punctuation and dashes / cards tagged punctuation / hyphen | ia_poly1850__poly1850 | 1/100; 1.00%; 95% Wilson CI 0.18–5.45% | uniform | A | C1/ia_poly1850__poly1850 |
| punctuation and dashes / cards tagged punctuation / hyphen | ia_russian__cyrillic | 7/100; 7.00%; 95% Wilson CI 3.43–13.75% | uniform | A | C1/ia_russian__cyrillic |
| punctuation and dashes / cards tagged punctuation / hyphen | kosmopolis__poly1900 | 3/100; 3.00%; 95% Wilson CI 1.03–8.45% | uniform | A | C1/kosmopolis__poly1900 |
| punctuation and dashes / cards tagged punctuation / hyphen | lekythos__poly1900 | 3/100; 3.00%; 95% Wilson CI 1.03–8.45% | uniform | A | C1/lekythos__poly1900 |
| punctuation and dashes / cards tagged punctuation / hyphen | nlg__greek_poly | 0/100; 0.00%; 95% Wilson CI 0.00–3.70% | uniform | A | C1/nlg__greek_poly |
| punctuation and dashes / cards tagged punctuation / hyphen | nlg__poly1850 | 6/100; 6.00%; 95% Wilson CI 2.78–12.48% | uniform | A | C1/nlg__poly1850 |
| punctuation and dashes / cards tagged punctuation / hyphen | nlg__poly1900 | 6/100; 6.00%; 95% Wilson CI 2.78–12.48% | uniform | A | C1/nlg__poly1900 |
| punctuation and dashes / cards tagged punctuation / hyphen | serbia__cyrillic | 6/100; 6.00%; 95% Wilson CI 2.78–12.48% | uniform | A | C1/serbia__cyrillic |
| punctuation and dashes / not measured (collapsed) | remaining scopes | not measured — outside named strata / class-wide population: Certified probability-sample truth beyond the named measured strata; no class-wide extrapolation. | not measured | not assigned | registered source inventory |
| superscripts and rare glyphs / not measured (collapsed) | remaining scopes | not measured — no eligible class-specific truth / superscripts and rare glyphs: Uniform or eligible locked certified superscript/rare-glyph opportunities; C1 occurrence lists do not certify correctness. | not measured | not assigned | truth_v1 + INPUTS.md |
| mixed-script lookalikes / cards tagged lookalike_script_letter | bsb_poly1850__poly1850 | 0/100; 0.00%; 95% Wilson CI 0.00–3.70% | uniform | A | C1/bsb_poly1850__poly1850 |
| mixed-script lookalikes / cards tagged lookalike_script_letter | elstat__numerics_tables | 0/100; 0.00%; 95% Wilson CI 0.00–3.70% | uniform | A | C1/elstat__numerics_tables |
| mixed-script lookalikes / cards tagged lookalike_script_letter | gazette_modern__modern_scanned__measured_1986_1990 | 0/100; 0.00%; 95% Wilson CI 0.00–3.70% | uniform | A | C1/gazette_modern__modern_scanned__measured_1986_1990 |
| mixed-script lookalikes / cards tagged lookalike_script_letter | gazette_modern__modern_scanned__probe_1982_1985 | 0/100; 0.00%; 95% Wilson CI 0.00–3.70% | uniform | A | C1/gazette_modern__modern_scanned__probe_1982_1985 |
| mixed-script lookalikes / cards tagged lookalike_script_letter | ia_poly1850__latin | 0/100; 0.00%; 95% Wilson CI 0.00–3.70% | uniform | A | C1/ia_poly1850__latin |
| mixed-script lookalikes / letters / digits / words (strict card verdict) | ia_poly1850__mixed_greek_latin | 9/100; 9.00%; 95% Wilson CI 4.81–16.23%; letters_y/n 91/9 | uniform | A | C1/ia_poly1850__mixed_greek_latin |
| mixed-script lookalikes / marks (any head; card verdict) | ia_poly1850__mixed_greek_latin | 11/100; 11.00%; 95% Wilson CI 6.25–18.63%; marks_y/n 89/11 | uniform | A | C1/ia_poly1850__mixed_greek_latin |
| mixed-script lookalikes / crop (physical card verdict) | ia_poly1850__mixed_greek_latin | 3/100; 3.00%; 95% Wilson CI 1.03–8.45%; crop_y/n 97/3 | uniform | A | C1/ia_poly1850__mixed_greek_latin |
| mixed-script lookalikes / cards tagged lookalike_script_letter | ia_poly1850__mixed_greek_latin | 5/100; 5.00%; 95% Wilson CI 2.15–11.18% | uniform | A | C1/ia_poly1850__mixed_greek_latin |
| mixed-script lookalikes / cards tagged lookalike_script_letter | ia_poly1850__poly1850 | 0/100; 0.00%; 95% Wilson CI 0.00–3.70% | uniform | A | C1/ia_poly1850__poly1850 |
| mixed-script lookalikes / cards tagged lookalike_script_letter | ia_russian__cyrillic | 0/100; 0.00%; 95% Wilson CI 0.00–3.70% | uniform | A | C1/ia_russian__cyrillic |
| mixed-script lookalikes / cards tagged lookalike_script_letter | kosmopolis__poly1900 | 0/100; 0.00%; 95% Wilson CI 0.00–3.70% | uniform | A | C1/kosmopolis__poly1900 |
| mixed-script lookalikes / cards tagged lookalike_script_letter | lekythos__poly1900 | 0/100; 0.00%; 95% Wilson CI 0.00–3.70% | uniform | A | C1/lekythos__poly1900 |
| mixed-script lookalikes / cards tagged lookalike_script_letter | nlg__greek_poly | 0/100; 0.00%; 95% Wilson CI 0.00–3.70% | uniform | A | C1/nlg__greek_poly |
| mixed-script lookalikes / cards tagged lookalike_script_letter | nlg__poly1850 | 0/100; 0.00%; 95% Wilson CI 0.00–3.70% | uniform | A | C1/nlg__poly1850 |
| mixed-script lookalikes / cards tagged lookalike_script_letter | nlg__poly1900 | 0/100; 0.00%; 95% Wilson CI 0.00–3.70% | uniform | A | C1/nlg__poly1900 |
| mixed-script lookalikes / cards tagged lookalike_script_letter | serbia__cyrillic | 0/100; 0.00%; 95% Wilson CI 0.00–3.70% | uniform | A | C1/serbia__cyrillic |
| mixed-script lookalikes / letters (masked card verdict) | kosmopolis/mixed_greek_latin/masked kosmopolis | 0/2; 0.00%; 95% Wilson CI 0.00–65.76% | uniform | A | T6b/kosmopolis |
| mixed-script lookalikes / marks (masked card verdict) | kosmopolis/mixed_greek_latin/masked kosmopolis | 0/2; 0.00%; 95% Wilson CI 0.00–65.76% | uniform | A | T6b/kosmopolis |
| mixed-script lookalikes / crop_ok (masked card verdict) | kosmopolis/mixed_greek_latin/masked kosmopolis | 0/2; 0.00%; 95% Wilson CI 0.00–65.76% | uniform | A | T6b/kosmopolis |
| mixed-script lookalikes / not measured (collapsed) | remaining scopes | not measured — outside named strata / class-wide population: Certified probability-sample truth beyond the named measured strata; no class-wide extrapolation. | not measured | not assigned | registered source inventory |
| Latin / letters / digits / words (strict card verdict) | ia_poly1850__latin | 11/99; 11.11%; 95% Wilson CI 6.32–18.81%; unknown 1; letters_y/n 88/11 | uniform | A | C1/ia_poly1850__latin |
| Latin / marks (any head; card verdict) | ia_poly1850__latin | 0/5; 0.00%; 95% Wilson CI 0.00–43.45%; na 95; marks_y/n 5/0 | uniform | A | C1/ia_poly1850__latin |
| Latin / crop (physical card verdict) | ia_poly1850__latin | 17/100; 17.00%; 95% Wilson CI 10.89–25.55%; crop_y/n 83/17 | uniform | A | C1/ia_poly1850__latin |
| Latin / letters (masked card verdict) | gazette_modern/latin/measured_1986_1990/masked gazette_modern | 0/1; 0.00%; 95% Wilson CI 0.00–79.35% | uniform | A | T6b/gazette_modern |
| Latin / crop_ok (masked card verdict) | gazette_modern/latin/measured_1986_1990/masked gazette_modern | 0/1; 0.00%; 95% Wilson CI 0.00–79.35% | uniform | A | T6b/gazette_modern |
| Latin / letters (masked card verdict) | kosmopolis/latin/masked kosmopolis | 0/1; 0.00%; 95% Wilson CI 0.00–79.35% | uniform | A | T6b/kosmopolis |
| Latin / crop_ok (masked card verdict) | kosmopolis/latin/masked kosmopolis | 0/1; 0.00%; 95% Wilson CI 0.00–79.35% | uniform | A | T6b/kosmopolis |
| Latin / not measured (collapsed) | remaining scopes | not measured — gazette_modern/latin/measured_1986_1990/masked gazette_modern / marks (masked card verdict): Applicable certified marks verdicts.; kosmopolis/latin/masked kosmopolis / marks (masked card verdict): Applicable certified marks verdicts. | not measured | not assigned | T6b/gazette_modern; T6b/kosmopolis |
| modern monotonic Greek / letters / digits / words (strict card verdict) | gazette_modern__modern_scanned__measured_1986_1990 | 2/100; 2.00%; 95% Wilson CI 0.55–7.00%; letters_y/n 98/2 | uniform | A | C1/gazette_modern__modern_scanned__measured_1986_1990 |
| modern monotonic Greek / marks (any head; card verdict) | gazette_modern__modern_scanned__measured_1986_1990 | 2/100; 2.00%; 95% Wilson CI 0.55–7.00%; marks_y/n 98/2 | uniform | A | C1/gazette_modern__modern_scanned__measured_1986_1990 |
| modern monotonic Greek / crop (physical card verdict) | gazette_modern__modern_scanned__measured_1986_1990 | 18/100; 18.00%; 95% Wilson CI 11.70–26.67%; crop_y/n 82/18 | uniform | A | C1/gazette_modern__modern_scanned__measured_1986_1990 |
| modern monotonic Greek / letters / digits / words (strict card verdict) | gazette_modern__modern_scanned__probe_1982_1985 | 11/97; 11.34%; 95% Wilson CI 6.45–19.17%; unknown 3; letters_y/n 86/11 | uniform | A | C1/gazette_modern__modern_scanned__probe_1982_1985 |
| modern monotonic Greek / marks (any head; card verdict) | gazette_modern__modern_scanned__probe_1982_1985 | 2/100; 2.00%; 95% Wilson CI 0.55–7.00%; marks_y/n 98/2 | uniform | A | C1/gazette_modern__modern_scanned__probe_1982_1985 |
| modern monotonic Greek / crop (physical card verdict) | gazette_modern__modern_scanned__probe_1982_1985 | 30/100; 30.00%; 95% Wilson CI 21.89–39.58%; crop_y/n 70/30 | uniform | A | C1/gazette_modern__modern_scanned__probe_1982_1985 |
| modern monotonic Greek / letters (masked card verdict) | gazette_modern/modern_scanned/measured_1986_1990/masked gazette_modern | 3/54; 5.56%; 95% Wilson CI 1.91–15.11% | uniform | A | T6b/gazette_modern |
| modern monotonic Greek / marks (masked card verdict) | gazette_modern/modern_scanned/measured_1986_1990/masked gazette_modern | 1/54; 1.85%; 95% Wilson CI 0.33–9.77% | uniform | A | T6b/gazette_modern |
| modern monotonic Greek / crop_ok (masked card verdict) | gazette_modern/modern_scanned/measured_1986_1990/masked gazette_modern | 1/54; 1.85%; 95% Wilson CI 0.33–9.77% | uniform | A | T6b/gazette_modern |
| modern monotonic Greek / letters (masked card verdict) | gazette_modern/modern_scanned/probe_1982_1985/masked gazette_modern | 1/10; 10.00%; 95% Wilson CI 1.79–40.42% | uniform | A | T6b/gazette_modern |
| modern monotonic Greek / marks (masked card verdict) | gazette_modern/modern_scanned/probe_1982_1985/masked gazette_modern | 0/9; 0.00%; 95% Wilson CI 0.00–29.91%; unknown 1 | uniform | A | T6b/gazette_modern |
| modern monotonic Greek / crop_ok (masked card verdict) | gazette_modern/modern_scanned/probe_1982_1985/masked gazette_modern | 1/10; 10.00%; 95% Wilson CI 1.79–40.42% | uniform | A | T6b/gazette_modern |
| modern monotonic Greek / letters (masked card verdict) | kosmopolis/greek_mono/masked kosmopolis | 0/2; 0.00%; 95% Wilson CI 0.00–65.76% | uniform | A | T6b/kosmopolis |
| modern monotonic Greek / marks (masked card verdict) | kosmopolis/greek_mono/masked kosmopolis | 0/2; 0.00%; 95% Wilson CI 0.00–65.76% | uniform | A | T6b/kosmopolis |
| modern monotonic Greek / crop_ok (masked card verdict) | kosmopolis/greek_mono/masked kosmopolis | 0/2; 0.00%; 95% Wilson CI 0.00–65.76% | uniform | A | T6b/kosmopolis |
| modern monotonic Greek / letters (masked card verdict) | lekythos/greek_mono/masked lekythos | 0/1; 0.00%; 95% Wilson CI 0.00–79.35% | uniform | A | T6b/lekythos |
| modern monotonic Greek / marks (masked card verdict) | lekythos/greek_mono/masked lekythos | 1/1; 100.00%; 95% Wilson CI 20.65–100.00% | uniform | A | T6b/lekythos |
| modern monotonic Greek / crop_ok (masked card verdict) | lekythos/greek_mono/masked lekythos | 0/1; 0.00%; 95% Wilson CI 0.00–79.35% | uniform | A | T6b/lekythos |
| modern monotonic Greek / letters (masked card verdict) | gazette_modern/modern_scanned/probe_1982_1985/masked gazette_probe_supplement | 4/29; 13.79%; 95% Wilson CI 5.50–30.56%; unknown 1 | uniform | A | T6b/gazette_probe_supplement |
| modern monotonic Greek / marks (masked card verdict) | gazette_modern/modern_scanned/probe_1982_1985/masked gazette_probe_supplement | 0/30; 0.00%; 95% Wilson CI 0.00–11.35% | uniform | A | T6b/gazette_probe_supplement |
| modern monotonic Greek / crop_ok (masked card verdict) | gazette_modern/modern_scanned/probe_1982_1985/masked gazette_probe_supplement | 4/30; 13.33%; 95% Wilson CI 5.31–29.68% | uniform | A | T6b/gazette_probe_supplement |
| modern monotonic Greek / not measured (collapsed) | remaining scopes | not measured — outside named strata / class-wide population: Certified probability-sample truth beyond the named measured strata; no class-wide extrapolation. | not measured | not assigned | registered source inventory |
| Cyrillic / letters / digits / words (strict card verdict) | ia_russian__cyrillic | 24/98; 24.49%; 95% Wilson CI 17.04–33.86%; unknown 2; letters_y/n 74/24 | uniform | A | C1/ia_russian__cyrillic |
| Cyrillic / marks (any head; card verdict) | ia_russian__cyrillic | 0/20; 0.00%; 95% Wilson CI 0.00–16.11%; na 80; marks_y/n 20/0 | uniform | A | C1/ia_russian__cyrillic |
| Cyrillic / crop (physical card verdict) | ia_russian__cyrillic | 3/100; 3.00%; 95% Wilson CI 1.03–8.45%; crop_y/n 97/3 | uniform | A | C1/ia_russian__cyrillic |
| Cyrillic / letters / digits / words (strict card verdict) | serbia__cyrillic | 4/100; 4.00%; 95% Wilson CI 1.57–9.84%; letters_y/n 96/4 | uniform | A | C1/serbia__cyrillic |
| Cyrillic / marks (any head; card verdict) | serbia__cyrillic | 4/4; 100.00%; 95% Wilson CI 51.01–100.00%; na 96; marks_y/n 0/4 | uniform | A | C1/serbia__cyrillic |
| Cyrillic / crop (physical card verdict) | serbia__cyrillic | 8/100; 8.00%; 95% Wilson CI 4.11–15.00%; crop_y/n 92/8 | uniform | A | C1/serbia__cyrillic |
| Cyrillic / ru1_yer slots | ia_russian / cyrillic; resolved yer positions | 26/49; 53.06%; 95% Wilson CI 39.38–66.30%; uncovered 16 | uniform | A | yer_adjudication |
| Cyrillic / not measured (collapsed) | remaining scopes | not measured — ia_russian / cyrillic / RU1-labelled masked / letters source inventory: Raw Google re-score against printed letters; this uniform audit checks RU1 labels, not raw Google.; ia_russian / cyrillic / RU1-labelled masked / marks source inventory: Opus mark adjudication is pending in this source.; ia_russian / cyrillic / RU1-labelled masked / crop_ok source inventory: Bind class-specific raw Google pixel truth with a benchmark A/B/C reader tier; source records final Sol gate verdicts, which are not silently promoted. | not measured | not assigned | masked/ruc1 |
| locked source inventory / not measured (collapsed) | remaining scopes | not measured — locked_eval / locked source coverage: Class-resolved pixel truth with reader tier and exact Google bindings; ID list is not truth.; locked_eval_ia_wikisource / locked source coverage: Full-line pixel truth; only 24 selected i-a letter scopes certified.; eval_only_dev / locked source coverage: Class-resolved pixel truth with reader tier and exact Google bindings; ID list is not truth.; locked_eval_ib_wikisource / locked source coverage: Two-reader pixel truth; reference transcription, not pixel truth.; n1_locked_eval / locked source coverage: Uniform/locked certified separator slots; approved N1 truth is enriched. | not measured | not assigned | /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/release_exclusions/release_exclusions.json |

## Custody and reproduction

All 7 registered versions were rescored. SX1 v2 SHA, byte size, production receipt, v1 preservation and audit100 membership verified; sf6_release reads only ENSEMBLE_AB release labels. Historical PRESENCE/FULL remains sf6_presence_full. N1 remains UNADOPTED. [Machine scores](score_v2.json), [headline ledger](headline_v2.json), [manifest](truth_v1_1.manifest.json), [receipt](LQB5_RECEIPT.json).

The 60 new exclusion IDs omit registered classes and all 600 DEV IDs under the lead eval_only_dev instruction. The old on-disk DEV class has zero overlap; 600 IDs still require sourcing synchronization. No peer registry was written and nothing was sent.

```sh
PYTHONDONTWRITEBYTECODE=1 ../greek-ocr-toolkit-sol-collect/.venv/bin/python -B scripts/lqb/build_v2_2.py
PYTHONDONTWRITEBYTECODE=1 ../greek-ocr-toolkit-sol-collect/.venv/bin/python -B -m pytest tests/test_lqb.py tests/test_lqb3.py tests/test_lqb4.py tests/test_lqb5.py -q -p no:cacheprovider --basetemp=/private/tmp/lqb5-pytest
PYTHONDONTWRITEBYTECODE=1 ../greek-ocr-toolkit-sol-collect/.venv/bin/python -B scripts/lqb/validate_scoreboard.py
PYTHONDONTWRITEBYTECODE=1 ../greek-ocr-toolkit-sol-collect/.venv/bin/python -B scripts/lqb/finalize_v2_2.py
```

Network OFF; no .git writes, peer writes, inference, publication, browser or computer-use tools. HTML structural checks and native PNG decoding are performed; rendered desktop/narrow layout is unverified by instruction. Historical LQB3 artifacts remain in validation/lqb3/frozen/.

## Completed LQB5 verification

113 tests passed. All 229 embedded native PNGs decoded; baseline precedes headline and begins with measured rows within each class; HTML 9.791 MB. Browser/computer-use tools were not launched; rendered desktop/narrow layout is unverified by instruction.

## RU2TF3 / v2.3

All 9 registered versions rescored offline against frozen truth v1.1. `ru1_v2_train` is registered as a complete exact-ID label file; parent `collection_v2_train`. [Scores](score_v2_3.json), [paired delta](../../../../artifacts/ru1/ru2t/lqb_delta.json).

Coverage and denominators below refer only to frozen-truth overlap; collection-v2 train has different IDs from much of this truth. Uncovered positions are not scored as correct. No population-wide inference.

| Class / tier | Paired items | Parent errors | v2 errors | Delta per 100 | 95% CI |
|---|---:|---:|---:|---:|---|
| marks / A | 45423 | 227 | 227 | None | None |
| marks / A+B | 45423 | 227 | 227 | None | None |
| letters / A+B | 0 | 0 | 0 | None | None |
| n1_separator / A+B | 0 | 0 | 0 | None | None |
| ru1_yer / A+B | 0 | 0 | 0 | None | None |
| ru2_yat / A+B | 0 | 0 | 0 | None | None |
| superscript / A+B | 0 | 0 | 0 | None | None |
| dash / A+B | 0 | 0 | 0 | None | None |
| lunate / A+B | 0 | 0 | 0 | None | None |
| lookalike / A+B | 0 | 0 | 0 | None | None |
| capitals / A | 36 | 0 | 0 | None | None |
| capitals / A+B | 36 | 0 | 0 | None | None |
| crop / A+B | 0 | 0 | 0 | None | None |
| marks/breathing / A | 11349 | 48 | 48 | None | None |
| marks/breathing / A+B | 11349 | 48 | 48 | None | None |
| marks/accent / A | 11393 | 127 | 127 | None | None |
| marks/accent / A+B | 11393 | 127 | 127 | None | None |
| marks/dialytika / A | 11341 | 3 | 3 | None | None |
| marks/dialytika / A+B | 11341 | 3 | 3 | None | None |
| marks/subscript / A | 11340 | 49 | 49 | None | None |
| marks/subscript / A+B | 11340 | 49 | 49 | None | None |

## RU2TF4 / v2.4

All 9 registered versions rescored offline against frozen truth v1.1 after the lead rulings. `ru1_v2_train` retains the exact collection-v2 train IDs. Three edits use `lead_ruling`; 52 edits use `two_reads`. The 20 hard and 10 soft audit positions are `lead_audit_confirmed`. Two positions remain held (`hold_yat`, `hold_uncertain`); their parent labels are retained.

[Scores](score_v2_4.json), [paired delta](../../../../artifacts/ru1/ru2t/lqb_delta_v2_4.json). Coverage refers only to frozen-truth overlap. Uncovered positions are not scored as correct. The RU1 yer paired overlap is zero; these scores do not measure the new edits or establish a population improvement.

| Class / tier | Paired items | Parent errors | v2 errors | Delta per 100 | 95% CI |
|---|---:|---:|---:|---:|---|
| marks / A | 45423 | 227 | 227 | None | None |
| marks / A+B | 45423 | 227 | 227 | None | None |
| letters / A+B | 0 | 0 | 0 | None | None |
| n1_separator / A+B | 0 | 0 | 0 | None | None |
| ru1_yer / A+B | 0 | 0 | 0 | None | None |
| ru2_yat / A+B | 0 | 0 | 0 | None | None |
| superscript / A+B | 0 | 0 | 0 | None | None |
| dash / A+B | 0 | 0 | 0 | None | None |
| lunate / A+B | 0 | 0 | 0 | None | None |
| lookalike / A+B | 0 | 0 | 0 | None | None |
| capitals / A | 36 | 0 | 0 | None | None |
| capitals / A+B | 36 | 0 | 0 | None | None |
| crop / A+B | 0 | 0 | 0 | None | None |
| marks/breathing / A | 11349 | 48 | 48 | None | None |
| marks/breathing / A+B | 11349 | 48 | 48 | None | None |
| marks/accent / A | 11393 | 127 | 127 | None | None |
| marks/accent / A+B | 11393 | 127 | 127 | None | None |
| marks/dialytika / A | 11341 | 3 | 3 | None | None |
| marks/dialytika / A+B | 11341 | 3 | 3 | None | None |
| marks/subscript / A | 11340 | 49 | 49 | None | None |
| marks/subscript / A+B | 11340 | 49 | 49 | None | None |

RU2TF4 verification: all 214,436 exact IDs and parent labels checked; exactly 55 soft-to-hard substitutions, with 214,434 ok rows and 2 held rows. All manifest artifact hashes verified. Focused tests: 119 passed plus 24 subtests. Expanded tests: 175 passed plus 24 subtests, 3 failures in historical LQB3/4/5 custody and exclusion checks against the changed peer exclusion registry. [Test log](../../../../artifacts/ru1/ru2t/tests_RU2TF4.txt). Network, new readings, browser/computer use and .git writes were not used.
