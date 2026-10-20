# S1 — deterministic + lexicon-proposes / ink-decides

Strict attestation is the default. ACCEPT and HOLD are always separate. CTC only locates: its reading is a diagnostic, never a proposal or a voting gate. Human text is used only for scoring and the declared dev calibration.

Run: `python -m greekocr.labelfix.spellcheck_validate --seed 0 --seed 1 --out docs/records/labelfix/spellcheck/S2_engine --shape-model docs/records/labelfix/markshape_model_S2.json --samples docs/records/labelfix/markshape_samples_S2.jsonl.gz --print-truth docs/records/labelfix/spellcheck/print_truth_s0.json --no-sheets`. CPU, network off, **0 CTC forward passes**; {0: {'lines': 1264, 'cached': 1264, 'missing': 0}, 1: {'lines': 1264, 'cached': 1264, 'missing': 0}}. Elapsed including sheets: 20.39 seconds.

T1 is fixed: 185 non-human-text Google mark errors per seed (370 seed/error observations). Both seeds share images and reference text: pooled confidence bounds describe observations and do not imply independent replicated images.

## Frozen thresholds and policies

`tau_contradict = 0.9` selected on DEV_BOOKS only: first threshold in the prespecified grid with ≥99% dev classifier precision and ≥50 samples. The existing shape model and ACCEPT tau=0.998 are reused without retraining. Its original tau was calibrated on the old held-out books; consequently S1 held-out results are book-separated for the new choices, not an untouched classifier calibration test. Dev samples were used to fit the existing classifier, so dev calibration is descriptive.

D2 book style uses only ink slopes over final vowels of midline words (no trailing punctuation, no following enclitic), regardless of Google's written accent. New threshold selected on DEV_BOOKS only: ≥10 readable isolated accents, ≥70% one slope. Other books supply unlabeled ink to this frozen style detector. Mixed/insufficient books are unknown; they require an individual decisive grave slope. Acute books suppress all D2 grave changes.

D1 tries attested constraint-valid mark variants first (including multi-cluster repairs); otherwise only a unique constraint-valid minimum mark edit. Every changed cluster must pass the ink checks. D1 overrides attestation only for impossible forms. D2 is positional only midline before non-enclitics; line ends and punctuation always require a decisive grave slope. In those slope-only contexts D2 applies only when its ink test passes; otherwise the lexical stages may propose a non-grave repair (final-acute/grave-only lexical proposals remain excluded). The failed D2 attempt is retained as a diagnostic. L1 uses written_freq and one-cluster alternatives; final acute/grave and initial-rho-only alternatives are excluded. L2 scans only Google vowel/rho clusters (including unmarked vowels) with an attested constraint-valid alternative, and always needs classifier tau plus physical checks. Ratio is a separate diagnostic policy: an attested alternative ≥20× the Google count can additionally trigger L1; it never changes strict decisions.

HOLD requires exactly one D1/L1 proposal, existing image evidence, and no contradiction. A combined D1/L1 repair that also changes final acute to grave is still slope-only at punctuation or line end and cannot HOLD; acute-book suppression also covers combined repairs. It is forbidden for D2/L2, competing proposals and dialytika-only changes. On a readable, unmerged band, absent subscript, absent required two dots, clearly insufficient added above marks, or a confident classifier reading of Google contradicts. Faint, clipped, merged, neighbour and localisation failures abstain and permit HOLD. With no located image evidence HOLD abstains. All-caps, Latin/digits, hyphen line end, abbreviations and capitalised non-initial words stay guarded. Initial capitals require the proposed lower form ≥50 and name count <3.

Calibration details and full grid: `calibration.json`; book ink counts and resulting style: `book_styles.json`. No held-out human label selects a new threshold.

## Book styles

| seed | book | split | acute slopes | grave slopes | style |
|---|---|---|---:|---:|---|
| 0 | wikisource:02a3a2a6 | dev | 27 | 117 | grave |
| 0 | wikisource:177b717d | held-out | 3 | 164 | grave |
| 0 | wikisource:22fda82b | held-out | 2 | 7 | unknown |
| 0 | wikisource:2793d64c | dev | 1 | 90 | grave |
| 0 | wikisource:384c3f89 | held-out | 24 | 272 | grave |
| 0 | wikisource:4f60b077 | held-out | 0 | 3 | unknown |
| 0 | wikisource:51fe7386 | held-out | 1 | 13 | grave |
| 0 | wikisource:602cc72e | held-out | 0 | 0 | unknown |
| 0 | wikisource:8b6b0de9 | dev | 22 | 86 | grave |
| 0 | wikisource:9c1dca9b | held-out | 0 | 13 | grave |
| 0 | wikisource:c3e12e31 | held-out | 0 | 2 | unknown |
| 1 | wikisource:02a3a2a6 | dev | 27 | 151 | grave |
| 1 | wikisource:177b717d | held-out | 4 | 192 | grave |
| 1 | wikisource:22fda82b | held-out | 3 | 9 | grave |
| 1 | wikisource:2793d64c | dev | 2 | 102 | grave |
| 1 | wikisource:384c3f89 | held-out | 28 | 342 | grave |
| 1 | wikisource:4f60b077 | held-out | 0 | 4 | unknown |
| 1 | wikisource:51fe7386 | held-out | 1 | 18 | grave |
| 1 | wikisource:602cc72e | held-out | 0 | 0 | unknown |
| 1 | wikisource:8b6b0de9 | dev | 26 | 106 | grave |
| 1 | wikisource:9c1dca9b | held-out | 0 | 19 | grave |
| 1 | wikisource:c3e12e31 | held-out | 0 | 2 | unknown |

## Stage × column precision

Candidates are words with lexical/deterministic alternatives before ink, including guarded candidates. L2 is a prefilter workload; only a differing classifier class at tau can decide. A word is counted once per stage; the two column candidate counts share that pool. Unknown references are excluded from precision. LB95 is validate.lb95, the exact one-sided 95% Clopper–Pearson lower bound.

### strict · seed 0 · dev

| stage | column | candidates | decided | = human | Google-right FP | both-wrong | unknown | precision | LB95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D1 | ACCEPT | 2 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| D1 | HOLD | 2 | 1 | 1 | 0 | 0 | 0 | 100.0% | 5.0% |
| D2 | ACCEPT | 45 | 21 | 20 | 0 | 1 | 0 | 95.2% | 79.3% |
| D2 | HOLD | 45 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L1 | ACCEPT | 34 | 1 | 1 | 0 | 0 | 0 | 100.0% | 5.0% |
| L1 | HOLD | 34 | 15 | 10 | 2 | 1 | 2 | 76.9% | 50.5% |
| L2 | ACCEPT | 1035 | 1 | 1 | 0 | 0 | 0 | 100.0% | 5.0% |
| L2 | HOLD | 1035 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| all | ACCEPT | 1116 | 23 | 22 | 0 | 1 | 0 | 95.7% | 81.0% |
| all | HOLD | 1116 | 16 | 11 | 2 | 1 | 2 | 78.6% | 53.4% |

### strict · seed 0 · held-out

| stage | column | candidates | decided | = human | Google-right FP | both-wrong | unknown | precision | LB95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D1 | ACCEPT | 16 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| D1 | HOLD | 16 | 8 | 5 | 0 | 2 | 1 | 71.4% | 34.1% |
| D2 | ACCEPT | 38 | 2 | 2 | 0 | 0 | 0 | 100.0% | 22.4% |
| D2 | HOLD | 38 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L1 | ACCEPT | 55 | 1 | 1 | 0 | 0 | 0 | 100.0% | 5.0% |
| L1 | HOLD | 55 | 23 | 19 | 3 | 1 | 0 | 82.6% | 64.5% |
| L2 | ACCEPT | 1277 | 3 | 2 | 1 | 0 | 0 | 66.7% | 13.5% |
| L2 | HOLD | 1277 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| all | ACCEPT | 1386 | 6 | 5 | 1 | 0 | 0 | 83.3% | 41.8% |
| all | HOLD | 1386 | 31 | 24 | 3 | 3 | 1 | 80.0% | 64.3% |

### strict · seed 0 · both

| stage | column | candidates | decided | = human | Google-right FP | both-wrong | unknown | precision | LB95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D1 | ACCEPT | 18 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| D1 | HOLD | 18 | 9 | 6 | 0 | 2 | 1 | 75.0% | 40.0% |
| D2 | ACCEPT | 83 | 23 | 22 | 0 | 1 | 0 | 95.7% | 81.0% |
| D2 | HOLD | 83 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L1 | ACCEPT | 89 | 2 | 2 | 0 | 0 | 0 | 100.0% | 22.4% |
| L1 | HOLD | 89 | 38 | 29 | 5 | 2 | 2 | 80.6% | 66.6% |
| L2 | ACCEPT | 2312 | 4 | 3 | 1 | 0 | 0 | 75.0% | 24.9% |
| L2 | HOLD | 2312 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| all | ACCEPT | 2502 | 29 | 27 | 1 | 1 | 0 | 93.1% | 79.8% |
| all | HOLD | 2502 | 47 | 35 | 5 | 4 | 3 | 79.5% | 67.0% |

### strict · seed 1 · dev

| stage | column | candidates | decided | = human | Google-right FP | both-wrong | unknown | precision | LB95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D1 | ACCEPT | 2 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| D1 | HOLD | 2 | 1 | 1 | 0 | 0 | 0 | 100.0% | 5.0% |
| D2 | ACCEPT | 46 | 22 | 20 | 1 | 1 | 0 | 90.9% | 74.1% |
| D2 | HOLD | 46 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L1 | ACCEPT | 34 | 1 | 1 | 0 | 0 | 0 | 100.0% | 5.0% |
| L1 | HOLD | 34 | 13 | 10 | 1 | 1 | 1 | 83.3% | 56.2% |
| L2 | ACCEPT | 1035 | 1 | 1 | 0 | 0 | 0 | 100.0% | 5.0% |
| L2 | HOLD | 1035 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| all | ACCEPT | 1117 | 24 | 22 | 1 | 1 | 0 | 91.7% | 76.0% |
| all | HOLD | 1117 | 14 | 11 | 1 | 1 | 1 | 84.6% | 59.0% |

### strict · seed 1 · held-out

| stage | column | candidates | decided | = human | Google-right FP | both-wrong | unknown | precision | LB95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D1 | ACCEPT | 16 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| D1 | HOLD | 16 | 7 | 5 | 0 | 1 | 1 | 83.3% | 41.8% |
| D2 | ACCEPT | 38 | 2 | 2 | 0 | 0 | 0 | 100.0% | 22.4% |
| D2 | HOLD | 38 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L1 | ACCEPT | 55 | 1 | 1 | 0 | 0 | 0 | 100.0% | 5.0% |
| L1 | HOLD | 55 | 22 | 18 | 3 | 1 | 0 | 81.8% | 63.1% |
| L2 | ACCEPT | 1277 | 2 | 2 | 0 | 0 | 0 | 100.0% | 22.4% |
| L2 | HOLD | 1277 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| all | ACCEPT | 1386 | 5 | 5 | 0 | 0 | 0 | 100.0% | 54.9% |
| all | HOLD | 1386 | 29 | 23 | 3 | 2 | 1 | 82.1% | 66.1% |

### strict · seed 1 · both

| stage | column | candidates | decided | = human | Google-right FP | both-wrong | unknown | precision | LB95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D1 | ACCEPT | 18 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| D1 | HOLD | 18 | 8 | 6 | 0 | 1 | 1 | 85.7% | 47.9% |
| D2 | ACCEPT | 84 | 24 | 22 | 1 | 1 | 0 | 91.7% | 76.0% |
| D2 | HOLD | 84 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L1 | ACCEPT | 89 | 2 | 2 | 0 | 0 | 0 | 100.0% | 22.4% |
| L1 | HOLD | 89 | 35 | 28 | 4 | 2 | 1 | 82.4% | 68.1% |
| L2 | ACCEPT | 2312 | 3 | 3 | 0 | 0 | 0 | 100.0% | 36.8% |
| L2 | HOLD | 2312 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| all | ACCEPT | 2503 | 29 | 27 | 1 | 1 | 0 | 93.1% | 79.8% |
| all | HOLD | 2503 | 43 | 34 | 4 | 3 | 2 | 82.9% | 70.3% |

### strict · seed both · dev

| stage | column | candidates | decided | = human | Google-right FP | both-wrong | unknown | precision | LB95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D1 | ACCEPT | 4 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| D1 | HOLD | 4 | 2 | 2 | 0 | 0 | 0 | 100.0% | 22.4% |
| D2 | ACCEPT | 91 | 43 | 40 | 1 | 2 | 0 | 93.0% | 82.9% |
| D2 | HOLD | 91 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L1 | ACCEPT | 68 | 2 | 2 | 0 | 0 | 0 | 100.0% | 22.4% |
| L1 | HOLD | 68 | 28 | 20 | 3 | 2 | 3 | 80.0% | 62.5% |
| L2 | ACCEPT | 2070 | 2 | 2 | 0 | 0 | 0 | 100.0% | 22.4% |
| L2 | HOLD | 2070 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| all | ACCEPT | 2233 | 47 | 44 | 1 | 2 | 0 | 93.6% | 84.3% |
| all | HOLD | 2233 | 30 | 22 | 3 | 2 | 3 | 81.5% | 64.9% |

### strict · seed both · held-out

| stage | column | candidates | decided | = human | Google-right FP | both-wrong | unknown | precision | LB95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D1 | ACCEPT | 32 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| D1 | HOLD | 32 | 15 | 10 | 0 | 3 | 2 | 76.9% | 50.5% |
| D2 | ACCEPT | 76 | 4 | 4 | 0 | 0 | 0 | 100.0% | 47.3% |
| D2 | HOLD | 76 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L1 | ACCEPT | 110 | 2 | 2 | 0 | 0 | 0 | 100.0% | 22.4% |
| L1 | HOLD | 110 | 45 | 37 | 6 | 2 | 0 | 82.2% | 70.2% |
| L2 | ACCEPT | 2554 | 5 | 4 | 1 | 0 | 0 | 80.0% | 34.3% |
| L2 | HOLD | 2554 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| all | ACCEPT | 2772 | 11 | 10 | 1 | 0 | 0 | 90.9% | 63.6% |
| all | HOLD | 2772 | 60 | 47 | 6 | 5 | 2 | 81.0% | 70.6% |

### strict · seed both · both

| stage | column | candidates | decided | = human | Google-right FP | both-wrong | unknown | precision | LB95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D1 | ACCEPT | 36 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| D1 | HOLD | 36 | 17 | 12 | 0 | 3 | 2 | 80.0% | 56.0% |
| D2 | ACCEPT | 167 | 47 | 44 | 1 | 2 | 0 | 93.6% | 84.3% |
| D2 | HOLD | 167 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L1 | ACCEPT | 178 | 4 | 4 | 0 | 0 | 0 | 100.0% | 47.3% |
| L1 | HOLD | 178 | 73 | 57 | 9 | 4 | 3 | 81.4% | 72.1% |
| L2 | ACCEPT | 4624 | 7 | 6 | 1 | 0 | 0 | 85.7% | 47.9% |
| L2 | HOLD | 4624 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| all | ACCEPT | 5005 | 58 | 54 | 2 | 2 | 0 | 93.1% | 84.9% |
| all | HOLD | 5005 | 90 | 69 | 9 | 7 | 5 | 81.2% | 72.8% |

### ratio · seed 0 · dev

| stage | column | candidates | decided | = human | Google-right FP | both-wrong | unknown | precision | LB95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D1 | ACCEPT | 2 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| D1 | HOLD | 2 | 1 | 1 | 0 | 0 | 0 | 100.0% | 5.0% |
| D2 | ACCEPT | 45 | 21 | 20 | 0 | 1 | 0 | 95.2% | 79.3% |
| D2 | HOLD | 45 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L1 | ACCEPT | 41 | 1 | 1 | 0 | 0 | 0 | 100.0% | 5.0% |
| L1 | HOLD | 41 | 22 | 10 | 8 | 2 | 2 | 50.0% | 30.2% |
| L2 | ACCEPT | 960 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L2 | HOLD | 960 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| all | ACCEPT | 1048 | 22 | 21 | 0 | 1 | 0 | 95.5% | 80.2% |
| all | HOLD | 1048 | 23 | 11 | 8 | 2 | 2 | 52.4% | 32.8% |

### ratio · seed 0 · held-out

| stage | column | candidates | decided | = human | Google-right FP | both-wrong | unknown | precision | LB95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D1 | ACCEPT | 16 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| D1 | HOLD | 16 | 8 | 5 | 0 | 2 | 1 | 71.4% | 34.1% |
| D2 | ACCEPT | 38 | 2 | 2 | 0 | 0 | 0 | 100.0% | 22.4% |
| D2 | HOLD | 38 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L1 | ACCEPT | 63 | 1 | 1 | 0 | 0 | 0 | 100.0% | 5.0% |
| L1 | HOLD | 63 | 31 | 20 | 9 | 2 | 0 | 64.5% | 48.2% |
| L2 | ACCEPT | 1192 | 2 | 1 | 1 | 0 | 0 | 50.0% | 2.5% |
| L2 | HOLD | 1192 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| all | ACCEPT | 1309 | 5 | 4 | 1 | 0 | 0 | 80.0% | 34.3% |
| all | HOLD | 1309 | 39 | 25 | 9 | 4 | 1 | 65.8% | 51.2% |

### ratio · seed 0 · both

| stage | column | candidates | decided | = human | Google-right FP | both-wrong | unknown | precision | LB95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D1 | ACCEPT | 18 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| D1 | HOLD | 18 | 9 | 6 | 0 | 2 | 1 | 75.0% | 40.0% |
| D2 | ACCEPT | 83 | 23 | 22 | 0 | 1 | 0 | 95.7% | 81.0% |
| D2 | HOLD | 83 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L1 | ACCEPT | 104 | 2 | 2 | 0 | 0 | 0 | 100.0% | 22.4% |
| L1 | HOLD | 104 | 53 | 30 | 17 | 4 | 2 | 58.8% | 46.3% |
| L2 | ACCEPT | 2152 | 2 | 1 | 1 | 0 | 0 | 50.0% | 2.5% |
| L2 | HOLD | 2152 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| all | ACCEPT | 2357 | 27 | 25 | 1 | 1 | 0 | 92.6% | 78.5% |
| all | HOLD | 2357 | 62 | 36 | 17 | 6 | 3 | 61.0% | 49.5% |

### ratio · seed 1 · dev

| stage | column | candidates | decided | = human | Google-right FP | both-wrong | unknown | precision | LB95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D1 | ACCEPT | 2 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| D1 | HOLD | 2 | 1 | 1 | 0 | 0 | 0 | 100.0% | 5.0% |
| D2 | ACCEPT | 46 | 22 | 20 | 1 | 1 | 0 | 90.9% | 74.1% |
| D2 | HOLD | 46 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L1 | ACCEPT | 40 | 1 | 1 | 0 | 0 | 0 | 100.0% | 5.0% |
| L1 | HOLD | 40 | 19 | 10 | 6 | 2 | 1 | 55.6% | 34.1% |
| L2 | ACCEPT | 961 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L2 | HOLD | 961 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| all | ACCEPT | 1049 | 23 | 21 | 1 | 1 | 0 | 91.3% | 75.1% |
| all | HOLD | 1049 | 20 | 11 | 6 | 2 | 1 | 57.9% | 36.8% |

### ratio · seed 1 · held-out

| stage | column | candidates | decided | = human | Google-right FP | both-wrong | unknown | precision | LB95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D1 | ACCEPT | 16 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| D1 | HOLD | 16 | 7 | 5 | 0 | 1 | 1 | 83.3% | 41.8% |
| D2 | ACCEPT | 38 | 2 | 2 | 0 | 0 | 0 | 100.0% | 22.4% |
| D2 | HOLD | 38 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L1 | ACCEPT | 63 | 1 | 1 | 0 | 0 | 0 | 100.0% | 5.0% |
| L1 | HOLD | 63 | 30 | 19 | 9 | 2 | 0 | 63.3% | 46.7% |
| L2 | ACCEPT | 1192 | 1 | 1 | 0 | 0 | 0 | 100.0% | 5.0% |
| L2 | HOLD | 1192 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| all | ACCEPT | 1309 | 4 | 4 | 0 | 0 | 0 | 100.0% | 47.3% |
| all | HOLD | 1309 | 37 | 24 | 9 | 3 | 1 | 66.7% | 51.7% |

### ratio · seed 1 · both

| stage | column | candidates | decided | = human | Google-right FP | both-wrong | unknown | precision | LB95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D1 | ACCEPT | 18 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| D1 | HOLD | 18 | 8 | 6 | 0 | 1 | 1 | 85.7% | 47.9% |
| D2 | ACCEPT | 84 | 24 | 22 | 1 | 1 | 0 | 91.7% | 76.0% |
| D2 | HOLD | 84 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L1 | ACCEPT | 103 | 2 | 2 | 0 | 0 | 0 | 100.0% | 22.4% |
| L1 | HOLD | 103 | 49 | 29 | 15 | 4 | 1 | 60.4% | 47.5% |
| L2 | ACCEPT | 2153 | 1 | 1 | 0 | 0 | 0 | 100.0% | 5.0% |
| L2 | HOLD | 2153 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| all | ACCEPT | 2358 | 27 | 25 | 1 | 1 | 0 | 92.6% | 78.5% |
| all | HOLD | 2358 | 57 | 35 | 15 | 5 | 2 | 63.6% | 51.7% |

### ratio · seed both · dev

| stage | column | candidates | decided | = human | Google-right FP | both-wrong | unknown | precision | LB95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D1 | ACCEPT | 4 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| D1 | HOLD | 4 | 2 | 2 | 0 | 0 | 0 | 100.0% | 22.4% |
| D2 | ACCEPT | 91 | 43 | 40 | 1 | 2 | 0 | 93.0% | 82.9% |
| D2 | HOLD | 91 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L1 | ACCEPT | 81 | 2 | 2 | 0 | 0 | 0 | 100.0% | 22.4% |
| L1 | HOLD | 81 | 41 | 20 | 14 | 4 | 3 | 52.6% | 38.2% |
| L2 | ACCEPT | 1921 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L2 | HOLD | 1921 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| all | ACCEPT | 2097 | 45 | 42 | 1 | 2 | 0 | 93.3% | 83.7% |
| all | HOLD | 2097 | 43 | 22 | 14 | 4 | 3 | 55.0% | 40.9% |

### ratio · seed both · held-out

| stage | column | candidates | decided | = human | Google-right FP | both-wrong | unknown | precision | LB95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D1 | ACCEPT | 32 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| D1 | HOLD | 32 | 15 | 10 | 0 | 3 | 2 | 76.9% | 50.5% |
| D2 | ACCEPT | 76 | 4 | 4 | 0 | 0 | 0 | 100.0% | 47.3% |
| D2 | HOLD | 76 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L1 | ACCEPT | 126 | 2 | 2 | 0 | 0 | 0 | 100.0% | 22.4% |
| L1 | HOLD | 126 | 61 | 39 | 18 | 4 | 0 | 63.9% | 52.6% |
| L2 | ACCEPT | 2384 | 3 | 2 | 1 | 0 | 0 | 66.7% | 13.5% |
| L2 | HOLD | 2384 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| all | ACCEPT | 2618 | 9 | 8 | 1 | 0 | 0 | 88.9% | 57.1% |
| all | HOLD | 2618 | 76 | 49 | 18 | 7 | 2 | 66.2% | 56.1% |

### ratio · seed both · both

| stage | column | candidates | decided | = human | Google-right FP | both-wrong | unknown | precision | LB95 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D1 | ACCEPT | 36 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| D1 | HOLD | 36 | 17 | 12 | 0 | 3 | 2 | 80.0% | 56.0% |
| D2 | ACCEPT | 167 | 47 | 44 | 1 | 2 | 0 | 93.6% | 84.3% |
| D2 | HOLD | 167 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| L1 | ACCEPT | 207 | 4 | 4 | 0 | 0 | 0 | 100.0% | 47.3% |
| L1 | HOLD | 207 | 102 | 59 | 32 | 8 | 3 | 59.6% | 50.8% |
| L2 | ACCEPT | 4305 | 3 | 2 | 1 | 0 | 0 | 66.7% | 13.5% |
| L2 | HOLD | 4305 | 0 | 0 | 0 | 0 | 0 | — | 0.0% |
| all | ACCEPT | 4715 | 54 | 50 | 2 | 2 | 0 | 92.6% | 83.8% |
| all | HOLD | 4715 | 119 | 71 | 32 | 11 | 5 | 62.3% | 54.2% |

## Recall on fixed T1 universe

Old = unchanged cached rules.py strict ACCEPT; old+ink also includes its separate ink_decisive diagnostic. Union uses old+ink and S1 ACCEPT+HOLD. Corrections count only when they equal the T1 human core.

| seed | split | T1 stage / model stratum | errors | ACCEPT | ACCEPT+HOLD | old | old+ink | union |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 0 | dev | all | 84 | 22 (26.2%) | 33 (39.3%) | 14 (16.7%) | 16 (19.0%) | 36 (42.9%) |
| 0 | dev | model also wrong | 41 | 9 (22.0%) | 11 (26.8%) | 0 (0.0%) | 0 (0.0%) | 11 (26.8%) |
| 0 | dev | model right | 43 | 13 (30.2%) | 22 (51.2%) | 14 (32.6%) | 16 (37.2%) | 25 (58.1%) |
| 0 | dev | constraint | 2 | 0 (0.0%) | 1 (50.0%) | 0 (0.0%) | 0 (0.0%) | 1 (50.0%) |
| 0 | dev | grave | 5 | 2 (40.0%) | 2 (40.0%) | 1 (20.0%) | 1 (20.0%) | 2 (40.0%) |
| 0 | dev | grave_line_end | 12 | 9 (75.0%) | 9 (75.0%) | 9 (75.0%) | 9 (75.0%) | 11 (91.7%) |
| 0 | dev | guard | 3 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| 0 | dev | human_unatt | 5 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| 0 | dev | lex_compete | 1 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| 0 | dev | lex_miss | 10 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 1 (10.0%) | 1 (10.0%) |
| 0 | dev | lex_unique | 11 | 1 (9.1%) | 11 (100.0%) | 4 (36.4%) | 4 (36.4%) | 11 (100.0%) |
| 0 | dev | real_word | 35 | 10 (28.6%) | 10 (28.6%) | 0 (0.0%) | 1 (2.9%) | 10 (28.6%) |
| 0 | held-out | all | 101 | 5 (5.0%) | 29 (28.7%) | 8 (7.9%) | 10 (9.9%) | 33 (32.7%) |
| 0 | held-out | model also wrong | 37 | 1 (2.7%) | 8 (21.6%) | 0 (0.0%) | 0 (0.0%) | 8 (21.6%) |
| 0 | held-out | model right | 64 | 4 (6.2%) | 21 (32.8%) | 8 (12.5%) | 10 (15.6%) | 25 (39.1%) |
| 0 | held-out | constraint | 10 | 0 (0.0%) | 5 (50.0%) | 1 (10.0%) | 1 (10.0%) | 6 (60.0%) |
| 0 | held-out | grave | 3 | 2 (66.7%) | 2 (66.7%) | 2 (66.7%) | 2 (66.7%) | 2 (66.7%) |
| 0 | held-out | grave_line_end | 1 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| 0 | held-out | guard | 9 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| 0 | held-out | human_unatt | 2 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| 0 | held-out | lex_compete | 4 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| 0 | held-out | lex_miss | 18 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 1 (5.6%) | 1 (5.6%) |
| 0 | held-out | lex_unique | 23 | 1 (4.3%) | 20 (87.0%) | 3 (13.0%) | 3 (13.0%) | 20 (87.0%) |
| 0 | held-out | real_word | 31 | 2 (6.5%) | 2 (6.5%) | 2 (6.5%) | 3 (9.7%) | 4 (12.9%) |
| 0 | both | all | 185 | 27 (14.6%) | 62 (33.5%) | 22 (11.9%) | 26 (14.1%) | 69 (37.3%) |
| 0 | both | model also wrong | 78 | 10 (12.8%) | 19 (24.4%) | 0 (0.0%) | 0 (0.0%) | 19 (24.4%) |
| 0 | both | model right | 107 | 17 (15.9%) | 43 (40.2%) | 22 (20.6%) | 26 (24.3%) | 50 (46.7%) |
| 0 | both | constraint | 12 | 0 (0.0%) | 6 (50.0%) | 1 (8.3%) | 1 (8.3%) | 7 (58.3%) |
| 0 | both | grave | 8 | 4 (50.0%) | 4 (50.0%) | 3 (37.5%) | 3 (37.5%) | 4 (50.0%) |
| 0 | both | grave_line_end | 13 | 9 (69.2%) | 9 (69.2%) | 9 (69.2%) | 9 (69.2%) | 11 (84.6%) |
| 0 | both | guard | 12 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| 0 | both | human_unatt | 7 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| 0 | both | lex_compete | 5 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| 0 | both | lex_miss | 28 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 2 (7.1%) | 2 (7.1%) |
| 0 | both | lex_unique | 34 | 2 (5.9%) | 31 (91.2%) | 7 (20.6%) | 7 (20.6%) | 31 (91.2%) |
| 0 | both | real_word | 66 | 12 (18.2%) | 12 (18.2%) | 2 (3.0%) | 4 (6.1%) | 14 (21.2%) |
| 1 | dev | all | 84 | 22 (26.2%) | 33 (39.3%) | 14 (16.7%) | 16 (19.0%) | 36 (42.9%) |
| 1 | dev | model also wrong | 41 | 10 (24.4%) | 14 (34.1%) | 0 (0.0%) | 0 (0.0%) | 14 (34.1%) |
| 1 | dev | model right | 43 | 12 (27.9%) | 19 (44.2%) | 14 (32.6%) | 16 (37.2%) | 22 (51.2%) |
| 1 | dev | constraint | 2 | 0 (0.0%) | 1 (50.0%) | 0 (0.0%) | 0 (0.0%) | 1 (50.0%) |
| 1 | dev | grave | 5 | 2 (40.0%) | 2 (40.0%) | 2 (40.0%) | 2 (40.0%) | 2 (40.0%) |
| 1 | dev | grave_line_end | 12 | 9 (75.0%) | 9 (75.0%) | 10 (83.3%) | 10 (83.3%) | 11 (91.7%) |
| 1 | dev | guard | 3 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| 1 | dev | human_unatt | 5 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| 1 | dev | lex_compete | 1 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| 1 | dev | lex_miss | 10 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 1 (10.0%) | 1 (10.0%) |
| 1 | dev | lex_unique | 11 | 1 (9.1%) | 11 (100.0%) | 2 (18.2%) | 2 (18.2%) | 11 (100.0%) |
| 1 | dev | real_word | 35 | 10 (28.6%) | 10 (28.6%) | 0 (0.0%) | 1 (2.9%) | 10 (28.6%) |
| 1 | held-out | all | 101 | 5 (5.0%) | 28 (27.7%) | 7 (6.9%) | 9 (8.9%) | 31 (30.7%) |
| 1 | held-out | model also wrong | 54 | 0 (0.0%) | 11 (20.4%) | 0 (0.0%) | 0 (0.0%) | 11 (20.4%) |
| 1 | held-out | model right | 47 | 5 (10.6%) | 17 (36.2%) | 7 (14.9%) | 9 (19.1%) | 20 (42.6%) |
| 1 | held-out | constraint | 10 | 0 (0.0%) | 5 (50.0%) | 1 (10.0%) | 1 (10.0%) | 6 (60.0%) |
| 1 | held-out | grave | 3 | 2 (66.7%) | 2 (66.7%) | 2 (66.7%) | 2 (66.7%) | 2 (66.7%) |
| 1 | held-out | grave_line_end | 1 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| 1 | held-out | guard | 9 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| 1 | held-out | human_unatt | 2 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| 1 | held-out | lex_compete | 4 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| 1 | held-out | lex_miss | 18 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 1 (5.6%) | 1 (5.6%) |
| 1 | held-out | lex_unique | 23 | 1 (4.3%) | 19 (82.6%) | 3 (13.0%) | 3 (13.0%) | 19 (82.6%) |
| 1 | held-out | real_word | 31 | 2 (6.5%) | 2 (6.5%) | 1 (3.2%) | 2 (6.5%) | 3 (9.7%) |
| 1 | both | all | 185 | 27 (14.6%) | 61 (33.0%) | 21 (11.4%) | 25 (13.5%) | 67 (36.2%) |
| 1 | both | model also wrong | 95 | 10 (10.5%) | 25 (26.3%) | 0 (0.0%) | 0 (0.0%) | 25 (26.3%) |
| 1 | both | model right | 90 | 17 (18.9%) | 36 (40.0%) | 21 (23.3%) | 25 (27.8%) | 42 (46.7%) |
| 1 | both | constraint | 12 | 0 (0.0%) | 6 (50.0%) | 1 (8.3%) | 1 (8.3%) | 7 (58.3%) |
| 1 | both | grave | 8 | 4 (50.0%) | 4 (50.0%) | 4 (50.0%) | 4 (50.0%) | 4 (50.0%) |
| 1 | both | grave_line_end | 13 | 9 (69.2%) | 9 (69.2%) | 10 (76.9%) | 10 (76.9%) | 11 (84.6%) |
| 1 | both | guard | 12 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| 1 | both | human_unatt | 7 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| 1 | both | lex_compete | 5 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| 1 | both | lex_miss | 28 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 2 (7.1%) | 2 (7.1%) |
| 1 | both | lex_unique | 34 | 2 (5.9%) | 30 (88.2%) | 5 (14.7%) | 5 (14.7%) | 30 (88.2%) |
| 1 | both | real_word | 66 | 12 (18.2%) | 12 (18.2%) | 1 (1.5%) | 3 (4.5%) | 13 (19.7%) |
| both | dev | all | 168 | 44 (26.2%) | 66 (39.3%) | 28 (16.7%) | 32 (19.0%) | 72 (42.9%) |
| both | dev | model also wrong | 82 | 19 (23.2%) | 25 (30.5%) | 0 (0.0%) | 0 (0.0%) | 25 (30.5%) |
| both | dev | model right | 86 | 25 (29.1%) | 41 (47.7%) | 28 (32.6%) | 32 (37.2%) | 47 (54.7%) |
| both | dev | constraint | 4 | 0 (0.0%) | 2 (50.0%) | 0 (0.0%) | 0 (0.0%) | 2 (50.0%) |
| both | dev | grave | 10 | 4 (40.0%) | 4 (40.0%) | 3 (30.0%) | 3 (30.0%) | 4 (40.0%) |
| both | dev | grave_line_end | 24 | 18 (75.0%) | 18 (75.0%) | 19 (79.2%) | 19 (79.2%) | 22 (91.7%) |
| both | dev | guard | 6 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| both | dev | human_unatt | 10 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| both | dev | lex_compete | 2 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| both | dev | lex_miss | 20 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 2 (10.0%) | 2 (10.0%) |
| both | dev | lex_unique | 22 | 2 (9.1%) | 22 (100.0%) | 6 (27.3%) | 6 (27.3%) | 22 (100.0%) |
| both | dev | real_word | 70 | 20 (28.6%) | 20 (28.6%) | 0 (0.0%) | 2 (2.9%) | 20 (28.6%) |
| both | held-out | all | 202 | 10 (5.0%) | 57 (28.2%) | 15 (7.4%) | 19 (9.4%) | 64 (31.7%) |
| both | held-out | model also wrong | 91 | 1 (1.1%) | 19 (20.9%) | 0 (0.0%) | 0 (0.0%) | 19 (20.9%) |
| both | held-out | model right | 111 | 9 (8.1%) | 38 (34.2%) | 15 (13.5%) | 19 (17.1%) | 45 (40.5%) |
| both | held-out | constraint | 20 | 0 (0.0%) | 10 (50.0%) | 2 (10.0%) | 2 (10.0%) | 12 (60.0%) |
| both | held-out | grave | 6 | 4 (66.7%) | 4 (66.7%) | 4 (66.7%) | 4 (66.7%) | 4 (66.7%) |
| both | held-out | grave_line_end | 2 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| both | held-out | guard | 18 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| both | held-out | human_unatt | 4 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| both | held-out | lex_compete | 8 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| both | held-out | lex_miss | 36 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 2 (5.6%) | 2 (5.6%) |
| both | held-out | lex_unique | 46 | 2 (4.3%) | 39 (84.8%) | 6 (13.0%) | 6 (13.0%) | 39 (84.8%) |
| both | held-out | real_word | 62 | 4 (6.5%) | 4 (6.5%) | 3 (4.8%) | 5 (8.1%) | 7 (11.3%) |
| both | both | all | 370 | 54 (14.6%) | 123 (33.2%) | 43 (11.6%) | 51 (13.8%) | 136 (36.8%) |
| both | both | model also wrong | 173 | 20 (11.6%) | 44 (25.4%) | 0 (0.0%) | 0 (0.0%) | 44 (25.4%) |
| both | both | model right | 197 | 34 (17.3%) | 79 (40.1%) | 43 (21.8%) | 51 (25.9%) | 92 (46.7%) |
| both | both | constraint | 24 | 0 (0.0%) | 12 (50.0%) | 2 (8.3%) | 2 (8.3%) | 14 (58.3%) |
| both | both | grave | 16 | 8 (50.0%) | 8 (50.0%) | 7 (43.8%) | 7 (43.8%) | 8 (50.0%) |
| both | both | grave_line_end | 26 | 18 (69.2%) | 18 (69.2%) | 19 (73.1%) | 19 (73.1%) | 22 (84.6%) |
| both | both | guard | 24 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| both | both | human_unatt | 14 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| both | both | lex_compete | 10 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| both | both | lex_miss | 56 | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 4 (7.1%) | 4 (7.1%) |
| both | both | lex_unique | 68 | 4 (5.9%) | 61 (89.7%) | 12 (17.6%) | 12 (17.6%) | 61 (89.7%) |
| both | both | real_word | 132 | 24 (18.2%) | 24 (18.2%) | 3 (2.3%) | 7 (5.3%) | 27 (20.5%) |

### Ratio policy recall (diagnostic, separate from strict)

| seed | split | stratum | errors | ratio ACCEPT | ratio ACCEPT+HOLD |
|---|---|---|---:|---:|---:|
| 0 | dev | all | 84 | 21 (25.0%) | 32 (38.1%) |
| 0 | dev | model also wrong | 41 | 9 (22.0%) | 11 (26.8%) |
| 0 | dev | model right | 43 | 12 (27.9%) | 21 (48.8%) |
| 0 | dev | constraint | 2 | 0 (0.0%) | 1 (50.0%) |
| 0 | dev | grave | 5 | 2 (40.0%) | 2 (40.0%) |
| 0 | dev | grave_line_end | 12 | 9 (75.0%) | 9 (75.0%) |
| 0 | dev | guard | 3 | 0 (0.0%) | 0 (0.0%) |
| 0 | dev | human_unatt | 5 | 0 (0.0%) | 0 (0.0%) |
| 0 | dev | lex_compete | 1 | 0 (0.0%) | 0 (0.0%) |
| 0 | dev | lex_miss | 10 | 0 (0.0%) | 0 (0.0%) |
| 0 | dev | lex_unique | 11 | 1 (9.1%) | 11 (100.0%) |
| 0 | dev | real_word | 35 | 9 (25.7%) | 9 (25.7%) |
| 0 | held-out | all | 101 | 4 (4.0%) | 29 (28.7%) |
| 0 | held-out | model also wrong | 37 | 0 (0.0%) | 8 (21.6%) |
| 0 | held-out | model right | 64 | 4 (6.2%) | 21 (32.8%) |
| 0 | held-out | constraint | 10 | 0 (0.0%) | 5 (50.0%) |
| 0 | held-out | grave | 3 | 2 (66.7%) | 2 (66.7%) |
| 0 | held-out | grave_line_end | 1 | 0 (0.0%) | 0 (0.0%) |
| 0 | held-out | guard | 9 | 0 (0.0%) | 0 (0.0%) |
| 0 | held-out | human_unatt | 2 | 0 (0.0%) | 0 (0.0%) |
| 0 | held-out | lex_compete | 4 | 0 (0.0%) | 0 (0.0%) |
| 0 | held-out | lex_miss | 18 | 0 (0.0%) | 0 (0.0%) |
| 0 | held-out | lex_unique | 23 | 1 (4.3%) | 20 (87.0%) |
| 0 | held-out | real_word | 31 | 1 (3.2%) | 2 (6.5%) |
| 0 | both | all | 185 | 25 (13.5%) | 61 (33.0%) |
| 0 | both | model also wrong | 78 | 9 (11.5%) | 19 (24.4%) |
| 0 | both | model right | 107 | 16 (15.0%) | 42 (39.3%) |
| 0 | both | constraint | 12 | 0 (0.0%) | 6 (50.0%) |
| 0 | both | grave | 8 | 4 (50.0%) | 4 (50.0%) |
| 0 | both | grave_line_end | 13 | 9 (69.2%) | 9 (69.2%) |
| 0 | both | guard | 12 | 0 (0.0%) | 0 (0.0%) |
| 0 | both | human_unatt | 7 | 0 (0.0%) | 0 (0.0%) |
| 0 | both | lex_compete | 5 | 0 (0.0%) | 0 (0.0%) |
| 0 | both | lex_miss | 28 | 0 (0.0%) | 0 (0.0%) |
| 0 | both | lex_unique | 34 | 2 (5.9%) | 31 (91.2%) |
| 0 | both | real_word | 66 | 10 (15.2%) | 11 (16.7%) |
| 1 | dev | all | 84 | 21 (25.0%) | 32 (38.1%) |
| 1 | dev | model also wrong | 41 | 10 (24.4%) | 14 (34.1%) |
| 1 | dev | model right | 43 | 11 (25.6%) | 18 (41.9%) |
| 1 | dev | constraint | 2 | 0 (0.0%) | 1 (50.0%) |
| 1 | dev | grave | 5 | 2 (40.0%) | 2 (40.0%) |
| 1 | dev | grave_line_end | 12 | 9 (75.0%) | 9 (75.0%) |
| 1 | dev | guard | 3 | 0 (0.0%) | 0 (0.0%) |
| 1 | dev | human_unatt | 5 | 0 (0.0%) | 0 (0.0%) |
| 1 | dev | lex_compete | 1 | 0 (0.0%) | 0 (0.0%) |
| 1 | dev | lex_miss | 10 | 0 (0.0%) | 0 (0.0%) |
| 1 | dev | lex_unique | 11 | 1 (9.1%) | 11 (100.0%) |
| 1 | dev | real_word | 35 | 9 (25.7%) | 9 (25.7%) |
| 1 | held-out | all | 101 | 4 (4.0%) | 28 (27.7%) |
| 1 | held-out | model also wrong | 54 | 0 (0.0%) | 11 (20.4%) |
| 1 | held-out | model right | 47 | 4 (8.5%) | 17 (36.2%) |
| 1 | held-out | constraint | 10 | 0 (0.0%) | 5 (50.0%) |
| 1 | held-out | grave | 3 | 2 (66.7%) | 2 (66.7%) |
| 1 | held-out | grave_line_end | 1 | 0 (0.0%) | 0 (0.0%) |
| 1 | held-out | guard | 9 | 0 (0.0%) | 0 (0.0%) |
| 1 | held-out | human_unatt | 2 | 0 (0.0%) | 0 (0.0%) |
| 1 | held-out | lex_compete | 4 | 0 (0.0%) | 0 (0.0%) |
| 1 | held-out | lex_miss | 18 | 0 (0.0%) | 0 (0.0%) |
| 1 | held-out | lex_unique | 23 | 1 (4.3%) | 19 (82.6%) |
| 1 | held-out | real_word | 31 | 1 (3.2%) | 2 (6.5%) |
| 1 | both | all | 185 | 25 (13.5%) | 60 (32.4%) |
| 1 | both | model also wrong | 95 | 10 (10.5%) | 25 (26.3%) |
| 1 | both | model right | 90 | 15 (16.7%) | 35 (38.9%) |
| 1 | both | constraint | 12 | 0 (0.0%) | 6 (50.0%) |
| 1 | both | grave | 8 | 4 (50.0%) | 4 (50.0%) |
| 1 | both | grave_line_end | 13 | 9 (69.2%) | 9 (69.2%) |
| 1 | both | guard | 12 | 0 (0.0%) | 0 (0.0%) |
| 1 | both | human_unatt | 7 | 0 (0.0%) | 0 (0.0%) |
| 1 | both | lex_compete | 5 | 0 (0.0%) | 0 (0.0%) |
| 1 | both | lex_miss | 28 | 0 (0.0%) | 0 (0.0%) |
| 1 | both | lex_unique | 34 | 2 (5.9%) | 30 (88.2%) |
| 1 | both | real_word | 66 | 10 (15.2%) | 11 (16.7%) |
| both | dev | all | 168 | 42 (25.0%) | 64 (38.1%) |
| both | dev | model also wrong | 82 | 19 (23.2%) | 25 (30.5%) |
| both | dev | model right | 86 | 23 (26.7%) | 39 (45.3%) |
| both | dev | constraint | 4 | 0 (0.0%) | 2 (50.0%) |
| both | dev | grave | 10 | 4 (40.0%) | 4 (40.0%) |
| both | dev | grave_line_end | 24 | 18 (75.0%) | 18 (75.0%) |
| both | dev | guard | 6 | 0 (0.0%) | 0 (0.0%) |
| both | dev | human_unatt | 10 | 0 (0.0%) | 0 (0.0%) |
| both | dev | lex_compete | 2 | 0 (0.0%) | 0 (0.0%) |
| both | dev | lex_miss | 20 | 0 (0.0%) | 0 (0.0%) |
| both | dev | lex_unique | 22 | 2 (9.1%) | 22 (100.0%) |
| both | dev | real_word | 70 | 18 (25.7%) | 18 (25.7%) |
| both | held-out | all | 202 | 8 (4.0%) | 57 (28.2%) |
| both | held-out | model also wrong | 91 | 0 (0.0%) | 19 (20.9%) |
| both | held-out | model right | 111 | 8 (7.2%) | 38 (34.2%) |
| both | held-out | constraint | 20 | 0 (0.0%) | 10 (50.0%) |
| both | held-out | grave | 6 | 4 (66.7%) | 4 (66.7%) |
| both | held-out | grave_line_end | 2 | 0 (0.0%) | 0 (0.0%) |
| both | held-out | guard | 18 | 0 (0.0%) | 0 (0.0%) |
| both | held-out | human_unatt | 4 | 0 (0.0%) | 0 (0.0%) |
| both | held-out | lex_compete | 8 | 0 (0.0%) | 0 (0.0%) |
| both | held-out | lex_miss | 36 | 0 (0.0%) | 0 (0.0%) |
| both | held-out | lex_unique | 46 | 2 (4.3%) | 39 (84.8%) |
| both | held-out | real_word | 62 | 2 (3.2%) | 4 (6.5%) |
| both | both | all | 370 | 50 (13.5%) | 121 (32.7%) |
| both | both | model also wrong | 173 | 19 (11.0%) | 44 (25.4%) |
| both | both | model right | 197 | 31 (15.7%) | 77 (39.1%) |
| both | both | constraint | 24 | 0 (0.0%) | 12 (50.0%) |
| both | both | grave | 16 | 8 (50.0%) | 8 (50.0%) |
| both | both | grave_line_end | 26 | 18 (69.2%) | 18 (69.2%) |
| both | both | guard | 24 | 0 (0.0%) | 0 (0.0%) |
| both | both | human_unatt | 14 | 0 (0.0%) | 0 (0.0%) |
| both | both | lex_compete | 10 | 0 (0.0%) | 0 (0.0%) |
| both | both | lex_miss | 56 | 0 (0.0%) | 0 (0.0%) |
| both | both | lex_unique | 68 | 4 (5.9%) | 61 (89.7%) |
| both | both | real_word | 132 | 20 (15.2%) | 22 (16.7%) |

## False fires on correct Google words

| seed | stage | column | word | proposal | line id |
|---|---|---|---|---|---|
| 0 | L1 | HOLD | δρομαία. | δρομαῖα. | 22fda82b-p000083-l0006 |
| 0 | L1 | HOLD | διαρκῇ | διαρκῆ | 8b6b0de9-p000021-l0012 |
| 0 | L1 | HOLD | χαίρ' | χαῖρ' | 02a3a2a6-p000303-l0012 |
| 0 | L2 | ACCEPT | ζῇ | ζῆ | 4f60b077-p000209-l0005 |
| 0 | L1 | HOLD | παιάνας. | παιᾶνας. | 177b717d-p000017-l0008 |
| 0 | L1 | HOLD | δέσμῃ | δέσμη | 602cc72e-p000155-l0030 |
| 1 | L1 | HOLD | διαρκῇ | διαρκῆ | 8b6b0de9-p000021-l0012 |
| 1 | D2 | ACCEPT | ζωηροί, | ζωηροὶ, | 8b6b0de9-p000016-l0030 |
| 1 | L1 | HOLD | κωμωδία | κωμῳδία | 177b717d-p000072-l0001 |
| 1 | L1 | HOLD | παιάνας. | παιᾶνας. | 177b717d-p000017-l0008 |
| 1 | L1 | HOLD | δέσμῃ | δέσμη | 602cc72e-p000155-l0030 |

### False-fire counts (strict / ratio, separate columns)

| seed | policy | stage | ACCEPT FP | HOLD FP |
|---|---|---|---:|---:|
| 0 | strict | D1 | 0 | 0 |
| 0 | strict | D2 | 0 | 0 |
| 0 | strict | L1 | 0 | 5 |
| 0 | strict | L2 | 1 | 0 |
| 0 | ratio | D1 | 0 | 0 |
| 0 | ratio | D2 | 0 | 0 |
| 0 | ratio | L1 | 0 | 17 |
| 0 | ratio | L2 | 1 | 0 |
| 1 | strict | D1 | 0 | 0 |
| 1 | strict | D2 | 1 | 0 |
| 1 | strict | L1 | 0 | 4 |
| 1 | strict | L2 | 0 | 0 |
| 1 | ratio | D1 | 0 | 0 |
| 1 | ratio | D2 | 1 | 0 |
| 1 | ratio | L1 | 0 | 15 |
| 1 | ratio | L2 | 0 | 0 |

Ratio false-fire words (diagnostic):

- s0 L1 HOLD `22fda82b-p000083-l0006` word 1: δρομαία. → δρομαῖα
- s0 L1 HOLD `8b6b0de9-p000021-l0012` word 4: διαρκῇ → διαρκῆ
- s0 L1 HOLD `8b6b0de9-p000004-l0017` word 3: εἷς, → εἰς
- s0 L1 HOLD `8b6b0de9-p000013-l0025` word 2: της → τῆς
- s0 L1 HOLD `8b6b0de9-p000011-l0017` word 1: εἷς → εἰς
- s0 L1 HOLD `8b6b0de9-p000013-l0026` word 2: της → τῆς
- s0 L1 HOLD `8b6b0de9-p000006-l0027` word 2: της → τῆς
- s0 L1 HOLD `02a3a2a6-p000022-l0017` word 2: ταὶς → ταῖς
- s0 L1 HOLD `02a3a2a6-p000303-l0012` word 1: χαίρ' → χαῖρ
- s0 L1 HOLD `384c3f89-p000030-l0012` word 0: τῶ → τῷ
- s0 L1 HOLD `384c3f89-p000096-l0039` word 1: τῶ → τῷ
- s0 L1 HOLD `384c3f89-p000091-l0011` word 0: τῶ → τῷ
- s0 L1 HOLD `384c3f89-p000121-l0005` word 0: τῶ → τῷ
- s0 L2 ACCEPT `4f60b077-p000209-l0005` word 2: ζῇ → ζῆ
- s0 L1 HOLD `177b717d-p000017-l0008` word 9: παιάνας. → παιᾶνας
- s0 L1 HOLD `384c3f89-p000179-l0010` word 2: τῶ → τῷ
- s0 L1 HOLD `602cc72e-p000197-l0030` word 6: ἔν → ἐν
- s0 L1 HOLD `602cc72e-p000155-l0030` word 3: δέσμῃ → δέσμη
- s1 L1 HOLD `8b6b0de9-p000021-l0012` word 4: διαρκῇ → διαρκῆ
- s1 L1 HOLD `8b6b0de9-p000004-l0017` word 3: εἷς, → εἰς
- s1 L1 HOLD `8b6b0de9-p000013-l0025` word 2: της → τῆς
- s1 D2 ACCEPT `8b6b0de9-p000016-l0030` word 2: ζωηροί, → ζωηροὶ
- s1 L1 HOLD `8b6b0de9-p000011-l0017` word 1: εἷς → εἰς
- s1 L1 HOLD `8b6b0de9-p000013-l0026` word 2: της → τῆς
- s1 L1 HOLD `8b6b0de9-p000006-l0027` word 2: της → τῆς
- s1 L1 HOLD `384c3f89-p000030-l0012` word 0: τῶ → τῷ
- s1 L1 HOLD `384c3f89-p000096-l0039` word 1: τῶ → τῷ
- s1 L1 HOLD `384c3f89-p000091-l0011` word 0: τῶ → τῷ
- s1 L1 HOLD `384c3f89-p000121-l0005` word 0: τῶ → τῷ
- s1 L1 HOLD `177b717d-p000072-l0001` word 1: κωμωδία → κωμῳδία
- s1 L1 HOLD `177b717d-p000017-l0008` word 9: παιάνας. → παιᾶνας
- s1 L1 HOLD `384c3f89-p000179-l0010` word 2: τῶ → τῷ
- s1 L1 HOLD `602cc72e-p000197-l0030` word 6: ἔν → ἐν
- s1 L1 HOLD `602cc72e-p000155-l0030` word 3: δέσμῃ → δέσμη

## Guards and abstentions

| seed | stage | reason | words |
|---|---|---|---:|
| 0 | D1 | abstain:localisation_uncertain | 1 |
| 0 | D1 | constraint_no_unique_supported_minimal_repair | 9 |
| 0 | D1 | excluded:initial_capital_unattested_50 | 4 |
| 0 | D1 | excluded:proper_name | 2 |
| 0 | D1 | shape_predicts_acute | 5 |
| 0 | D1 | shape_predicts_psili+acute | 1 |
| 0 | D2 | abstain:acute_slope | 22 |
| 0 | D2 | abstain:grave_accent_not_isolated | 3 |
| 0 | D2 | abstain:localisation_uncertain | 11 |
| 0 | D2 | abstain:neighbouring_marks | 3 |
| 0 | D2 | excluded:abbreviation | 2 |
| 0 | D2 | excluded:all_caps | 2 |
| 0 | D2 | excluded:hyphen_line_end | 1 |
| 0 | D2 | excluded:initial_capital_unattested_50 | 2 |
| 0 | D2 | excluded:known_name | 4 |
| 0 | D2 | excluded:proper_name | 16 |
| 0 | L1 | abstain:clipped_band | 2 |
| 0 | L1 | abstain:locator_unpaired | 1 |
| 0 | L1 | abstain:neighbouring_marks | 5 |
| 0 | L1 | abstain:shape_below_tau | 1 |
| 0 | L1 | excluded:all_caps | 32 |
| 0 | L1 | excluded:hyphen_line_end | 2 |
| 0 | L1 | excluded:initial_capital_unattested_50 | 45 |
| 0 | L1 | excluded:known_name | 3 |
| 0 | L1 | excluded:latin_or_digit | 19 |
| 0 | L1 | excluded:proper_name | 86 |
| 0 | L1 | no_attested_one_cluster_variant | 642 |
| 0 | L1 | shape_predicts_acute | 5 |
| 0 | L1 | shape_predicts_circumflex+subscript | 1 |
| 0 | L1 | shape_predicts_dasia+acute | 1 |
| 0 | L1 | shape_predicts_grave | 2 |
| 0 | L1 | shape_predicts_none | 4 |
| 0 | L1 | shape_predicts_psili | 1 |
| 0 | L2 | abstain:clipped_band | 59 |
| 0 | L2 | abstain:faint_mark | 5 |
| 0 | L2 | abstain:localisation_uncertain | 370 |
| 0 | L2 | abstain:locator_unpaired | 4 |
| 0 | L2 | abstain:neighbouring_marks | 118 |
| 0 | L2 | abstain:shape_below_tau | 113 |
| 0 | L2 | excluded:abbreviation | 13 |
| 0 | L2 | excluded:all_caps | 41 |
| 0 | L2 | excluded:hyphen_line_end | 3 |
| 0 | L2 | excluded:initial_capital_unattested_50 | 53 |
| 0 | L2 | excluded:known_name | 173 |
| 0 | L2 | excluded:proper_name | 179 |
| 0 | L2 | no_attested_mark_alternative | 2417 |
| 0 | L2 | shape_predicts_acute | 85 |
| 0 | L2 | shape_predicts_circumflex | 149 |
| 0 | L2 | shape_predicts_circumflex+subscript | 14 |
| 0 | L2 | shape_predicts_dasia | 127 |
| 0 | L2 | shape_predicts_dasia+acute | 56 |
| 0 | L2 | shape_predicts_grave | 529 |
| 0 | L2 | shape_predicts_none | 333 |
| 0 | L2 | shape_predicts_psili | 114 |
| 0 | L2 | shape_predicts_psili+acute | 40 |
| 0 | L2 | shape_predicts_psili+circumflex | 16 |
| 0 | L2 | shape_predicts_psili+grave | 16 |
| 0 | L2 | shape_predicts_subscript | 4 |
| 1 | D1 | abstain:locator_unpaired | 1 |
| 1 | D1 | abstain:neighbouring_marks | 1 |
| 1 | D1 | constraint_no_unique_supported_minimal_repair | 9 |
| 1 | D1 | excluded:initial_capital_unattested_50 | 4 |
| 1 | D1 | excluded:proper_name | 2 |
| 1 | D1 | shape_predicts_acute | 5 |
| 1 | D1 | shape_predicts_psili+acute | 1 |
| 1 | D2 | abstain:acute_slope | 30 |
| 1 | D2 | abstain:clipped_band | 1 |
| 1 | D2 | abstain:grave_accent_not_isolated | 3 |
| 1 | D2 | abstain:localisation_uncertain | 2 |
| 1 | D2 | abstain:neighbouring_marks | 3 |
| 1 | D2 | excluded:abbreviation | 2 |
| 1 | D2 | excluded:all_caps | 2 |
| 1 | D2 | excluded:hyphen_line_end | 1 |
| 1 | D2 | excluded:initial_capital_unattested_50 | 2 |
| 1 | D2 | excluded:known_name | 4 |
| 1 | D2 | excluded:proper_name | 16 |
| 1 | L1 | abstain:clipped_band | 1 |
| 1 | L1 | abstain:localisation_uncertain | 1 |
| 1 | L1 | abstain:neighbouring_marks | 5 |
| 1 | L1 | abstain:shape_below_tau | 1 |
| 1 | L1 | excluded:all_caps | 32 |
| 1 | L1 | excluded:hyphen_line_end | 2 |
| 1 | L1 | excluded:initial_capital_unattested_50 | 45 |
| 1 | L1 | excluded:known_name | 3 |
| 1 | L1 | excluded:latin_or_digit | 19 |
| 1 | L1 | excluded:proper_name | 86 |
| 1 | L1 | no_attested_one_cluster_variant | 641 |
| 1 | L1 | shape_predicts_acute | 7 |
| 1 | L1 | shape_predicts_circumflex+subscript | 1 |
| 1 | L1 | shape_predicts_dasia | 1 |
| 1 | L1 | shape_predicts_dasia+acute | 1 |
| 1 | L1 | shape_predicts_grave | 3 |
| 1 | L1 | shape_predicts_none | 4 |
| 1 | L1 | shape_predicts_psili | 1 |
| 1 | L2 | abstain:clipped_band | 64 |
| 1 | L2 | abstain:faint_mark | 5 |
| 1 | L2 | abstain:localisation_uncertain | 111 |
| 1 | L2 | abstain:locator_unpaired | 4 |
| 1 | L2 | abstain:neighbouring_marks | 148 |
| 1 | L2 | abstain:shape_below_tau | 139 |
| 1 | L2 | excluded:abbreviation | 13 |
| 1 | L2 | excluded:all_caps | 41 |
| 1 | L2 | excluded:hyphen_line_end | 3 |
| 1 | L2 | excluded:initial_capital_unattested_50 | 53 |
| 1 | L2 | excluded:known_name | 173 |
| 1 | L2 | excluded:proper_name | 179 |
| 1 | L2 | no_attested_mark_alternative | 2417 |
| 1 | L2 | shape_predicts_acute | 103 |
| 1 | L2 | shape_predicts_circumflex | 153 |
| 1 | L2 | shape_predicts_circumflex+subscript | 13 |
| 1 | L2 | shape_predicts_dasia | 138 |
| 1 | L2 | shape_predicts_dasia+acute | 57 |
| 1 | L2 | shape_predicts_grave | 665 |
| 1 | L2 | shape_predicts_none | 348 |
| 1 | L2 | shape_predicts_psili | 119 |
| 1 | L2 | shape_predicts_psili+acute | 43 |
| 1 | L2 | shape_predicts_psili+circumflex | 22 |
| 1 | L2 | shape_predicts_psili+grave | 17 |
| 1 | L2 | shape_predicts_subscript | 4 |

D2 slope-only attempts before stage dispatch (failed attempts may continue to lexical stages):

| seed | reason | attempts |
|---|---|---:|
| 0 | abstain:acute_slope | 133 |
| 0 | abstain:grave_accent_not_isolated | 39 |
| 0 | abstain:localisation_uncertain | 29 |
| 0 | decisive_grave_slope | 19 |
| 0 | abstain:neighbouring_marks | 13 |
| 0 | abstain:clipped_band | 6 |
| 0 | abstain:grave_slope_required | 2 |
| 0 | abstain:locator_unpaired | 1 |
| 1 | abstain:acute_slope | 153 |
| 1 | abstain:grave_accent_not_isolated | 40 |
| 1 | decisive_grave_slope | 20 |
| 1 | abstain:localisation_uncertain | 10 |
| 1 | abstain:neighbouring_marks | 8 |
| 1 | abstain:clipped_band | 5 |
| 1 | abstain:grave_slope_required | 3 |
| 1 | abstain:locator_unpaired | 3 |

## What each stage reaches; every unreached error

D1 reaches hard-invalid spellings; D2 reaches final acute→grave in positional or slope-only contexts; L1 reaches unattested one-cluster spellings with a unique or ink-resolved lexical repair; L2 reaches attested real-word errors whose mark classifier contradicts Google. The following line IDs expose what each stage actually recovered. Guarded names, unattested targets, multi-cluster L1 changes, absent lexical variants and unreadable marks remain visible in unreached.jsonl.

- D1: s0 `8b6b0de9-p000006-l0022` w1 συνεἶχον→συνεῖχον (HOLD); s0 `9c1dca9b-p000015-l0067` w2 ψωμίὰ→ψωμιὰ (HOLD); s0 `384c3f89-p000096-l0010` w0 υΐες,→υἷες, (HOLD); s0 `384c3f89-p000182-l0006` w5 αΐψα→αἶψα (HOLD); s0 `384c3f89-p000182-l0031` w4 αΐψα→αἶψα (HOLD); s0 `384c3f89-p000121-l0023` w4 εἶπετο→εἵπετο (HOLD); s1 `8b6b0de9-p000006-l0022` w1 συνεἶχον→συνεῖχον (HOLD); s1 `9c1dca9b-p000015-l0067` w2 ψωμίὰ→ψωμιὰ (HOLD); s1 `384c3f89-p000096-l0010` w0 υΐες,→υἷες, (HOLD); s1 `384c3f89-p000182-l0006` w5 αΐψα→αἶψα (HOLD); s1 `384c3f89-p000182-l0031` w4 αΐψα→αἶψα (HOLD); s1 `384c3f89-p000121-l0023` w4 εἶπετο→εἵπετο (HOLD)
- D2: s0 `8b6b0de9-p000004-l0011` w2 εὐρύ→εὐρὺ (ACCEPT); s0 `8b6b0de9-p000016-l0019` w3 γλυκύ→γλυκὺ (ACCEPT); s0 `8b6b0de9-p000017-l0006` w2 φρικτά,→φρικτὰ, (ACCEPT); s0 `8b6b0de9-p000008-l0019` w1 στεναγμόν→στεναγμὸν (ACCEPT); s0 `8b6b0de9-p000007-l0012` w2 γλυκύ,→γλυκὺ, (ACCEPT); s0 `8b6b0de9-p000011-l0006` w3 περιστερά,→περιστερὰ, (ACCEPT); s0 `8b6b0de9-p000013-l0026` w3 παρειάς→παρειὰς (ACCEPT); s0 `8b6b0de9-p000006-l0029` w2 παλμοί,→παλμοὶ, (ACCEPT); s0 `8b6b0de9-p000007-l0005` w2 τρυφηλά,→τρυφηλὰ, (ACCEPT); s0 `8b6b0de9-p000021-l0028` w4 ζωή→ζωὴ (ACCEPT); s0 `8b6b0de9-p000018-l0023` w1 πληγή→πληγὴ (ACCEPT); s0 `8b6b0de9-p000018-l0023` w2 αἱματηρά→αἱματηρὰ (ACCEPT); s0 `8b6b0de9-p000016-l0029` w3 χοροί→χοροὶ (ACCEPT); s0 `8b6b0de9-p000017-l0013` w3 σοβαρά→σοβαρὰ (ACCEPT); s0 `8b6b0de9-p000009-l0017` w2 πολλοί,→πολλοὶ, (ACCEPT); s0 `8b6b0de9-p000007-l0011` w3 μουσικοί,→μουσικοὶ, (ACCEPT); s0 `8b6b0de9-p000009-l0024` w4 σκαλμόν→σκαλμὸν (ACCEPT); s0 `8b6b0de9-p000018-l0026` w3 οὐρά→οὐρὰ (ACCEPT); s0 `8b6b0de9-p000016-l0023` w3 χλωρούς,→χλωροὺς, (ACCEPT); s0 `8b6b0de9-p000018-l0006` w2 κραυγήν,→κραυγὴν, (ACCEPT); s0 `51fe7386-p000026-l0016` w0 Ἐμπρός→Ἐμπρὸς (ACCEPT); s0 `51fe7386-p000024-l0016` w5 ντροπαλή→ντροπαλὴ (ACCEPT); s1 `8b6b0de9-p000004-l0011` w2 εὐρύ→εὐρὺ (ACCEPT); s1 `8b6b0de9-p000016-l0019` w3 γλυκύ→γλυκὺ (ACCEPT); s1 `8b6b0de9-p000017-l0006` w2 φρικτά,→φρικτὰ, (ACCEPT); s1 `8b6b0de9-p000008-l0019` w1 στεναγμόν→στεναγμὸν (ACCEPT); s1 `8b6b0de9-p000007-l0012` w2 γλυκύ,→γλυκὺ, (ACCEPT); s1 `8b6b0de9-p000011-l0006` w3 περιστερά,→περιστερὰ, (ACCEPT); s1 `8b6b0de9-p000013-l0026` w3 παρειάς→παρειὰς (ACCEPT); s1 `8b6b0de9-p000006-l0029` w2 παλμοί,→παλμοὶ, (ACCEPT); s1 `8b6b0de9-p000007-l0005` w2 τρυφηλά,→τρυφηλὰ, (ACCEPT); s1 `8b6b0de9-p000021-l0028` w4 ζωή→ζωὴ (ACCEPT); s1 `8b6b0de9-p000018-l0023` w1 πληγή→πληγὴ (ACCEPT); s1 `8b6b0de9-p000018-l0023` w2 αἱματηρά→αἱματηρὰ (ACCEPT); s1 `8b6b0de9-p000016-l0029` w3 χοροί→χοροὶ (ACCEPT); s1 `8b6b0de9-p000017-l0013` w3 σοβαρά→σοβαρὰ (ACCEPT); s1 `8b6b0de9-p000009-l0017` w2 πολλοί,→πολλοὶ, (ACCEPT); s1 `8b6b0de9-p000007-l0011` w3 μουσικοί,→μουσικοὶ, (ACCEPT); s1 `8b6b0de9-p000009-l0024` w4 σκαλμόν→σκαλμὸν (ACCEPT); s1 `8b6b0de9-p000018-l0026` w3 οὐρά→οὐρὰ (ACCEPT); s1 `8b6b0de9-p000016-l0023` w3 χλωρούς,→χλωροὺς, (ACCEPT); s1 `8b6b0de9-p000018-l0006` w2 κραυγήν,→κραυγὴν, (ACCEPT); s1 `51fe7386-p000026-l0016` w0 Ἐμπρός→Ἐμπρὸς (ACCEPT); s1 `51fe7386-p000024-l0016` w5 ντροπαλή→ντροπαλὴ (ACCEPT)
- L1: s0 `8b6b0de9-p000011-l0014` w3 χείλος.→χεῖλος. (HOLD); s0 `8b6b0de9-p000004-l0028` w0 βήμα→βῆμα (HOLD); s0 `8b6b0de9-p000008-l0024` w2 τελετής,→τελετῆς, (HOLD); s0 `8b6b0de9-p000007-l0025` w3 βήμα.→βῆμα. (HOLD); s0 `9c1dca9b-p000015-l0064` w1 ἐξῆντα→ἑξῆντα (HOLD); s0 `8b6b0de9-p000011-l0007` w3 ἀφορᾶ→ἀφορᾷ (ACCEPT); s0 `8b6b0de9-p000011-l0030` w2 ἔκαστος→ἕκαστος (HOLD); s0 `22fda82b-p000063-l0018` w2 ἑσιώπα.→ἐσιώπα. (HOLD); s0 `2793d64c-p000070-l0010` w1 ἀνώμωξεν→ἀνῴμωξεν (HOLD); s0 `8b6b0de9-p000007-l0030` w2 ληστῶν→λῃστῶν (HOLD); s0 `2793d64c-p000056-l0007` w3 καταντᾶ;→καταντᾷ; (HOLD); s0 `2793d64c-p000072-l0007` w3 ἐκβάλη.→ἐκβάλῃ. (HOLD); s0 `602cc72e-p000113-l0009` w2 ἁλώπηξ.→ἀλώπηξ. (HOLD); s0 `02a3a2a6-p000046-l0025` w3 γενῆς→γενῇς (HOLD); s0 `177b717d-p000105-l0010` w2 τάλογο→τἄλογο (HOLD); s0 `384c3f89-p000053-l0022` w3 υἱα→υἷα (HOLD); s0 `384c3f89-p000096-l0004` w3 ᾖσι→ᾗσι (HOLD); s0 `384c3f89-p000068-l0036` w5 υἱα→υἷα (HOLD); s0 `384c3f89-p000068-l0033` w0 οὗτα→οὖτα (HOLD); s0 `384c3f89-p000053-l0023` w2 κονίησι→κονίῃσι (HOLD); s0 `384c3f89-p000182-l0003` w1 εἶλκον→εἷλκον (HOLD); s0 `384c3f89-p000053-l0004` w3 εἶλεν→εἷλεν (HOLD); s0 `384c3f89-p000030-l0033` w4 οἶσι→οἷσι (HOLD); s0 `384c3f89-p000030-l0026` w6 ἤνεον,→ᾔνεον, (HOLD); s0 `384c3f89-p000059-l0023` w4 γήρυς→γῆρυς (ACCEPT); s0 `384c3f89-p000053-l0021` w5 εἶλεν→εἷλεν (HOLD); s0 `384c3f89-p000183-l0020` w2 ναύτησι→ναύτῃσι (HOLD); s0 `51fe7386-p000024-l0020` w7 μήνες→μῆνες (HOLD); s0 `384c3f89-p000091-l0029` w4 υἱα→υἷα (HOLD); s0 `384c3f89-p000030-l0021` w7 ἦστο,→ἧστο, (HOLD); s0 `384c3f89-p000050-l0034` w0 ἰσόν→ἶσόν (HOLD); s1 `8b6b0de9-p000011-l0014` w3 χείλος.→χεῖλος. (HOLD); s1 `8b6b0de9-p000004-l0028` w0 βήμα→βῆμα (HOLD); s1 `8b6b0de9-p000008-l0024` w2 τελετής,→τελετῆς, (HOLD); s1 `8b6b0de9-p000007-l0025` w3 βήμα.→βῆμα. (HOLD); s1 `9c1dca9b-p000015-l0064` w1 ἐξῆντα→ἑξῆντα (HOLD); s1 `8b6b0de9-p000011-l0007` w3 ἀφορᾶ→ἀφορᾷ (ACCEPT); s1 `8b6b0de9-p000011-l0030` w2 ἔκαστος→ἕκαστος (HOLD); s1 `22fda82b-p000063-l0018` w2 ἑσιώπα.→ἐσιώπα. (HOLD); s1 `2793d64c-p000070-l0010` w1 ἀνώμωξεν→ἀνῴμωξεν (HOLD); s1 `8b6b0de9-p000007-l0030` w2 ληστῶν→λῃστῶν (HOLD); s1 `2793d64c-p000056-l0007` w3 καταντᾶ;→καταντᾷ; (HOLD); s1 `2793d64c-p000072-l0007` w3 ἐκβάλη.→ἐκβάλῃ. (HOLD); s1 `602cc72e-p000113-l0009` w2 ἁλώπηξ.→ἀλώπηξ. (HOLD); s1 `02a3a2a6-p000046-l0025` w3 γενῆς→γενῇς (HOLD); s1 `177b717d-p000105-l0010` w2 τάλογο→τἄλογο (HOLD); s1 `384c3f89-p000053-l0022` w3 υἱα→υἷα (HOLD); s1 `384c3f89-p000068-l0036` w5 υἱα→υἷα (HOLD); s1 `384c3f89-p000068-l0033` w0 οὗτα→οὖτα (HOLD); s1 `384c3f89-p000053-l0023` w2 κονίησι→κονίῃσι (HOLD); s1 `384c3f89-p000182-l0003` w1 εἶλκον→εἷλκον (HOLD); s1 `384c3f89-p000053-l0004` w3 εἶλεν→εἷλεν (HOLD); s1 `384c3f89-p000030-l0033` w4 οἶσι→οἷσι (HOLD); s1 `384c3f89-p000030-l0026` w6 ἤνεον,→ᾔνεον, (HOLD); s1 `384c3f89-p000059-l0023` w4 γήρυς→γῆρυς (ACCEPT); s1 `384c3f89-p000053-l0021` w5 εἶλεν→εἷλεν (HOLD); s1 `384c3f89-p000183-l0020` w2 ναύτησι→ναύτῃσι (HOLD); s1 `51fe7386-p000024-l0020` w7 μήνες→μῆνες (HOLD); s1 `384c3f89-p000091-l0029` w4 υἱα→υἷα (HOLD); s1 `384c3f89-p000030-l0021` w7 ἦστο,→ἧστο, (HOLD); s1 `384c3f89-p000050-l0034` w0 ἰσόν→ἶσόν (HOLD)
- L2: s0 `8b6b0de9-p000007-l0025` w0 το→τό (ACCEPT); s0 `177b717d-p000097-l0007` w0 ὁ→ὀ (ACCEPT); s0 `384c3f89-p000183-l0016` w0 δια→δῖα (ACCEPT); s1 `8b6b0de9-p000007-l0025` w0 το→τό (ACCEPT); s1 `177b717d-p000097-l0007` w0 ὁ→ὀ (ACCEPT); s1 `384c3f89-p000183-l0016` w0 δια→δῖα (ACCEPT)

| seed | T1 stage | line id / word | Google → human | engine stage | why unreached |
|---|---|---|---|---|---|
| 0 | real_word | 8b6b0de9-p000013-l0011 / 1 | λαίλαψ → λαῖλαψ | L2 | target proposal: abstain:neighbouring_marks |
| 0 | grave | 8b6b0de9-p000021-l0012 / 0 | Τί → Τὶ | D2 | excluded:known_name |
| 0 | lex_compete | 8b6b0de9-p000008-l0002 / 1 | ἄδου → ᾅδου | L1 | target proposal: shape_predicts_circumflex+subscript |
| 0 | real_word | 9c1dca9b-p000015-l0063 / 0 | ἂν → ἄν | L2 | abstain:clipped_band; target absent from proposals |
| 0 | grave_line_end | 8b6b0de9-p000004-l0029 / 2 | χοροί → χοροὶ | L2 | no_attested_mark_alternative; D2 slope-only attempt: abstain:localisation_uncertain |
| 0 | lex_miss | 8b6b0de9-p000008-l0019 / 2 | διακαή → διακαῆ | L1 | no_attested_one_cluster_variant; D2 slope-only attempt: abstain:grave_accent_not_isolated |
| 0 | human_unatt | 8b6b0de9-p000011-l0008 / 1 | ἐραστοῦ → ἑραστοῦ | L2 | no_attested_mark_alternative |
| 0 | real_word | 8b6b0de9-p000004-l0005 / 2 | βουνόν → βουνὸν | L2 | no_attested_mark_alternative; D2 slope-only attempt: abstain:grave_accent_not_isolated |
| 0 | real_word | 8b6b0de9-p000003-l0016 / 1 | ἂν → ἄν | L2 | shape_predicts_psili+grave; target absent from proposals; contradiction=classifier_reads_google |
| 0 | grave | 02a3a2a6-p000302-l0004 / 0 | Σφραγίς → Σφραγὶς | D2 | excluded:initial_capital_unattested_50 |
| 0 | real_word | 8b6b0de9-p000006-l0013 / 2 | χιών → χιὼν | L2 | no_attested_mark_alternative; D2 slope-only attempt: abstain:neighbouring_marks |
| 0 | real_word | 8b6b0de9-p000016-l0012 / 3 | σκιὰ → σκιά | L2 | shape_predicts_grave; target absent from proposals; contradiction=no_blob_below |
| 0 | lex_miss | 2793d64c-p000048-l0004 / 3 | ἡσυχάση → ἠσυχάσῃ | L1 | decided_other_form: ἡσυχάσῃ,; ambiguous_image;abstain:clipped_band; target absent from proposals |
| 0 | lex_miss | 02a3a2a6-p000046-l0018 / 0 | μοῦρθε → μοὖρθε | L1 | no_attested_one_cluster_variant |
| 0 | real_word | 8b6b0de9-p000008-l0020 / 0 | τίς → τις | D2 | abstain:acute_slope; target absent from proposals; contradiction=classifier_reads_google |
| 0 | lex_miss | 8b6b0de9-p000013-l0029 / 4 | ὠχριᾶς → ὠχριᾷς | L1 | no_attested_one_cluster_variant |
| 0 | real_word | 02a3a2a6-p000022-l0008 / 1 | ἡ → ᾑ | L2 | target proposal: shape_predicts_subscript |
| 0 | real_word | 8b6b0de9-p000021-l0016 / 4 | γλυκὺς → γλυκύς | L2 | no_attested_mark_alternative |
| 0 | real_word | 8b6b0de9-p000009-l0004 / 1 | εἰς → εἷς | L2 | target proposal: shape_predicts_none; contradiction=too_few_above_blobs |
| 0 | grave_line_end | 9c1dca9b-p000015-l0062 / 3 | βουλή → βουλὴ | L2 | shape_predicts_grave; target absent from proposals; D2 slope-only attempt: abstain:grave_slope_required; contradiction=no_blob_below |
| 0 | lex_miss | 2793d64c-p000070-l0014 / 2 | θρηνωδός → θρηνῳδός | L1 | no_attested_one_cluster_variant; D2 slope-only attempt: abstain:acute_slope |
| 0 | lex_miss | 9c1dca9b-p000015-l0066 / 3 | φελᾷ → φελᾳ | L1 | no_attested_one_cluster_variant |
| 0 | real_word | 2793d64c-p000068-l0011 / 0 | καί → καὶ | L2 | abstain:localisation_uncertain; target absent from proposals; D2 slope-only attempt: abstain:localisation_uncertain |
| 0 | real_word | 2793d64c-p000068-l0011 / 3 | των → τῶν | L2 | target proposal: shape_predicts_none; contradiction=too_few_above_blobs |
| 0 | lex_miss | 9c1dca9b-p000015-l0065 / 1 | μαγκούρες → μαγκοῦρες | L1 | no_attested_one_cluster_variant |
| 0 | lex_miss | 8b6b0de9-p000011-l0012 / 2 | σπινθηροβολεί → σπινθηροβολεῖ | L1 | no_attested_one_cluster_variant; D2 slope-only attempt: abstain:grave_slope_required |
| 0 | human_unatt | 8b6b0de9-p000021-l0007 / 3 | δύσης → δύσῃς | L2 | no_attested_mark_alternative |
| 0 | lex_miss | 02a3a2a6-p000318-l0017 / 1 | οἰκονόμησες → οἱκονόμησες | L1 | no_attested_one_cluster_variant |
| 0 | guard | 602cc72e-p000143-l0013 / 2 | Ζεὺς → Ζεύς | L2 | excluded:proper_name |
| 0 | real_word | 2793d64c-p000026-l0013 / 0 | Ὅπως → Ὄπως | L2 | excluded:known_name |
| 0 | grave | 602cc72e-p000353-l0006 / 0 | Χελιδών → Χελιδὼν | D2 | excluded:known_name |
| 0 | real_word | 8b6b0de9-p000004-l0026 / 3 | εὐρύ → εὐρὺ | L2 | no_attested_mark_alternative; D2 slope-only attempt: abstain:grave_accent_not_isolated |
| 0 | grave_line_end | 8b6b0de9-p000012-l0006 / 2 | νυκτός → νυκτὸς | L2 | no_attested_mark_alternative; D2 slope-only attempt: abstain:neighbouring_marks |
| 0 | real_word | 8b6b0de9-p000011-l0030 / 3 | θρασύς → θρασὺς | L2 | no_attested_mark_alternative; D2 slope-only attempt: abstain:grave_accent_not_isolated |
| 0 | human_unatt | 8b6b0de9-p000016-l0013 / 4 | φωλεά → φωλέα | D2 | decided_other_form: φωλεὰ; decisive_grave_slope; target absent from proposals; D2 slope-only attempt: decisive_grave_slope |
| 0 | real_word | 8b6b0de9-p000009-l0024 / 3 | τὸν → τον | L2 | target proposal: shape_predicts_grave; contradiction=classifier_reads_google |
| 0 | real_word | 02a3a2a6-p000022-l0011 / 0 | ἢ → ἤ | L2 | shape_predicts_psili+grave; target absent from proposals |
| 0 | real_word | 2793d64c-p000021-l0017 / 4 | γνωρίση → γνωρίσῃ | L2 | target proposal: abstain:clipped_band |
| 0 | human_unatt | 9c1dca9b-p000015-l0052 / 2 | ὄντες → ὅντες | L2 | no_attested_mark_alternative |
| 0 | real_word | 2793d64c-p000047-l0009 / 0 | οὕτως → οὔτως | L2 | target proposal: shape_predicts_dasia+acute |
| 0 | guard | 8b6b0de9-p000007-l0021 / 5 | Κλωθώ → Κλωθὼ | D2 | excluded:proper_name |
| 0 | real_word | 2793d64c-p000048-l0010 / 5 | φύγη → φύγῃ | L2 | target proposal: abstain:clipped_band |
| 0 | real_word | 2793d64c-p000070-l0021 / 0 | μόνῳ → μόνω | L2 | target proposal: abstain:shape_below_tau |
| 0 | real_word | 8b6b0de9-p000008-l0001 / 4 | ἄδην → ᾅδην | L2 | target proposal: abstain:neighbouring_marks |
| 0 | constraint | 02a3a2a6-p000318-l0020 / 0 | Άγι-Νικόλας → Ἁγι-Νικόλας | D1 | excluded:initial_capital_unattested_50 |
| 0 | lex_miss | 2793d64c-p000033-l0017 / 4 | ὑποκύπτη → ὑποκύπτῃ | L1 | no_attested_one_cluster_variant |
| 0 | human_unatt | 2793d64c-p000031-l0009 / 1 | ἠκολούθησεν → ἡκολούθησεν | L2 | no_attested_mark_alternative |
| 0 | grave | 02a3a2a6-p000178-l0014 / 2 | ἐγώ → ἐγὼ | D2 | target proposal: abstain:acute_slope; contradiction=classifier_reads_google |
| 0 | real_word | 8b6b0de9-p000012-l0005 / 3 | φρικτός → φρικτὸς | L2 | no_attested_mark_alternative; D2 slope-only attempt: abstain:grave_accent_not_isolated |
| 0 | lex_miss | 602cc72e-p000155-l0009 / 0 | Εὔνουχος → Εὐνοῦχος | L1 | excluded:initial_capital_unattested_50 |
| 0 | guard | 2793d64c-p000033-l0022 / 0 | Ω → Ὤ | L2 | excluded:all_caps |
| 0 | lex_miss | 8b6b0de9-p000016-l0023 / 0 | ἐλίσσ → ἑλίσσ | L1 | no_attested_one_cluster_variant; D2 slope-only attempt: abstain:acute_slope |
| 0 | human_unatt | 8b6b0de9-p000018-l0014 / 3 | λῃστὰς → ληστὰς | L2 | no_attested_mark_alternative |
| 0 | grave_line_end | 02a3a2a6-p000318-l0014 / 3 | φειδωλοί → φειδωλοὶ | L2 | no_attested_mark_alternative; D2 slope-only attempt: abstain:grave_accent_not_isolated |
| 0 | lex_miss | 02a3a2a6-p000168-l0005 / 2 | ῥωτήσουν → ρωτήσουν | L1 | no_attested_one_cluster_variant |
| 0 | real_word | 02a3a2a6-p000133-l0015 / 0 | Εἰν → Εἶν | L2 | excluded:initial_capital_unattested_50 |
| 0 | real_word | 22fda82b-p000063-l0039 / 4 | πῆς → πῇς | L2 | target proposal: abstain:shape_below_tau |
| 0 | real_word | 02a3a2a6-p000307-l0003 / 3 | ἁψηλὰ → ἀψηλὰ | L2 | target proposal: shape_predicts_dasia; contradiction=classifier_reads_google |
| 0 | guard | 602cc72e-p000167-l0027 / 2 | Πλούτος → Πλοῦτος | L1 | excluded:proper_name |
| 0 | lex_miss | 384c3f89-p000050-l0016 / 0 | Νηλείδαι → Νηλεΐδαι | L1 | excluded:initial_capital_unattested_50 |
| 0 | real_word | 177b717d-p000013-l0009 / 0 | Ἦταν → Ἤταν | L2 | excluded:known_name |
| 0 | real_word | 02a3a2a6-p000046-l0014 / 0 | Ὡς → Ὠς | L2 | excluded:known_name |
| 0 | real_word | 22fda82b-p000063-l0022 / 6 | σιγὰ → σιγά | L2 | shape_predicts_grave; target absent from proposals; contradiction=no_blob_below |
| 0 | lex_miss | 177b717d-p000067-l0009 / 3 | ἀλληλογραφία → ἀλληλογραφίᾳ | L1 | no_attested_one_cluster_variant |
| 0 | real_word | 384c3f89-p000096-l0005 / 1 | δὲ → δέ | L2 | shape_predicts_acute; target absent from proposals |
| 0 | guard | 177b717d-p000097-l0010 / 0 | Ω → Ὤ | L2 | excluded:all_caps |
| 0 | real_word | 177b717d-p000041-l0008 / 1 | πιο → πιὸ | L2 | target proposal: shape_predicts_psili+acute |
| 0 | lex_miss | 177b717d-p000104-l0012 / 4 | τἄλλοτινά → τἀλλοτινά | L1 | no_attested_one_cluster_variant |
| 0 | real_word | 177b717d-p000041-l0009 / 5 | ἔρμα → ἕρμα | L2 | target proposal: shape_predicts_circumflex |
| 0 | real_word | 177b717d-p000045-l0013 / 3 | ἢ → ἡ | L2 | target proposal: shape_predicts_circumflex |
| 0 | real_word | 384c3f89-p000096-l0006 / 0 | ὡς → ὧς | L2 | target proposal: shape_predicts_dasia+acute |
| 0 | real_word | 384c3f89-p000068-l0036 / 0 | αὕτως → αὔτως | L2 | target proposal: abstain:shape_below_tau |
| 0 | guard | 02a3a2a6-p000041-l0005 / 1 | Καλοκαίρι → Καλοκαῖρι | L2 | excluded:proper_name |
| 0 | real_word | 51fe7386-p000024-l0012 / 2 | βουνά → βουνὰ | L2 | no_attested_mark_alternative; D2 slope-only attempt: abstain:clipped_band |
| 0 | lex_miss | 51fe7386-p000024-l0012 / 3 | ὁλονυχτῆς → ὁλονυχτῇς | L1 | no_attested_one_cluster_variant |
| 0 | lex_miss | 51fe7386-p000024-l0012 / 4 | ῥωτιῶνται → ρωτιῶνται | L1 | no_attested_one_cluster_variant |
| 0 | lex_unique | 384c3f89-p000182-l0008 / 0 | Σειρήνες → Σειρῆνες | L1 | excluded:initial_capital_unattested_50 |
| 0 | lex_miss | 384c3f89-p000182-l0008 / 3 | ἡδείησιν → ἡδείῃσιν | L1 | no_attested_one_cluster_variant |
| 0 | real_word | 384c3f89-p000091-l0017 / 0 | ἢ → ἦ | L2 | target proposal: abstain:shape_below_tau |
| 0 | lex_miss | 384c3f89-p000183-l0022 / 0 | Ἀργώῃ → Ἀργῴῃ | L1 | excluded:initial_capital_unattested_50 |
| 0 | lex_miss | 384c3f89-p000050-l0041 / 1 | ἔδνοισιν → ἕδνοισιν | L1 | no_attested_one_cluster_variant |
| 0 | real_word | 384c3f89-p000142-l0003 / 1 | ἢ → ἣ | L2 | target proposal: shape_predicts_acute |
| 0 | lex_miss | 384c3f89-p000091-l0027 / 0 | ἠρί → ἦρί | L1 | no_attested_one_cluster_variant |
| 0 | lex_miss | 384c3f89-p000170-l0024 / 2 | δήοισιν → δῄοισιν | L1 | no_attested_one_cluster_variant |
| 0 | lex_miss | 384c3f89-p000183-l0005 / 1 | μιξοδίησιν → μιξοδίῃσιν | L1 | no_attested_one_cluster_variant |
| 0 | lex_unique | 22fda82b-p000118-l0008 / 6 | συγχωρήσης → συγχωρήσῃς | L1 | target proposal: shape_predicts_none; contradiction=no_blob_below |
| 0 | real_word | 384c3f89-p000183-l0021 / 0 | ὡς → ὧς | L2 | target proposal: shape_predicts_dasia |
| 0 | guard | 51fe7386-p000024-l0015 / 1 | Ὅλυμπος → Ὄλυμπος | L1 | excluded:proper_name |
| 0 | guard | 51fe7386-p000024-l0015 / 6 | Ὅσσα → Ὄσσα | L2 | excluded:proper_name |
| 0 | real_word | 384c3f89-p000068-l0008 / 2 | οἱ → οἷ | L2 | target proposal: abstain:localisation_uncertain |
| 0 | real_word | 384c3f89-p000068-l0037 / 2 | κορύνη → κορύνῃ | L2 | target proposal: abstain:neighbouring_marks |
| 0 | real_word | 384c3f89-p000091-l0039 / 1 | οἷος → οἶος | L2 | target proposal: shape_predicts_psili+acute |
| 0 | lex_miss | 384c3f89-p000091-l0039 / 6 | τίφος → τῖφος | L1 | no_attested_one_cluster_variant |
| 0 | real_word | 384c3f89-p000182-l0016 / 0 | ἢ → ἦ | L2 | target proposal: abstain:shape_below_tau |
| 0 | lex_miss | 384c3f89-p000142-l0010 / 1 | προβάλησι → προβάλῃσι | L1 | no_attested_one_cluster_variant |
| 0 | constraint | 384c3f89-p000030-l0029 / 0 | Ἑἰ → Εἰ | D1 | decided_other_form: Εἶ; ambiguous_image;abstain:neighbouring_marks; target absent from proposals |
| 0 | lex_compete | 384c3f89-p000059-l0013 / 6 | ἤγε → ἥγε | L1 | target proposal: abstain:shape_below_tau |
| 0 | human_unatt | 384c3f89-p000182-l0014 / 2 | παρθενικῆς → παρθενικῇς | L2 | no_attested_mark_alternative |
| 0 | real_word | 384c3f89-p000183-l0029 / 0 | αἳ → αἵ | L2 | abstain:localisation_uncertain; target absent from proposals |
| 0 | lex_miss | 384c3f89-p000205-l0011 / 0 | ἔσπεται → ἕσπεται | L1 | no_attested_one_cluster_variant |
| 0 | lex_miss | 384c3f89-p000050-l0027 / 1 | εἰσάμενοι → εἱσάμενοι | L1 | no_attested_one_cluster_variant |
| 0 | lex_unique | 384c3f89-p000182-l0023 / 1 | ἀμυδις → ἄμυδις | L1 | target proposal: shape_predicts_psili; contradiction=classifier_reads_google |
| 0 | lex_compete | 384c3f89-p000096-l0031 / 5 | ἔθεν → ἕθεν | L1 | target proposal: abstain:shape_below_tau |
| 0 | real_word | 384c3f89-p000205-l0013 / 0 | ὡς → ὧς | L2 | target proposal: shape_predicts_dasia+acute |
| 0 | constraint | 384c3f89-p000050-l0040 / 1 | ευπλόκαμος → ἐυπλόκαμος | D1 | decided_other_form: ἐϋπλόκαμος,; ambiguous_image;abstain:neighbouring_marks; target absent from proposals |
| 0 | real_word | 384c3f89-p000179-l0019 / 0 | εὐτ → εὖτ | L2 | target proposal: abstain:localisation_uncertain |
| 0 | real_word | 384c3f89-p000121-l0024 / 0 | οἷος → οἶος | L2 | target proposal: abstain:localisation_uncertain |
| 0 | real_word | 384c3f89-p000053-l0028 / 0 | ἢ → ἣ | L2 | target proposal: shape_predicts_psili+grave |
| 0 | lex_compete | 384c3f89-p000183-l0009 / 1 | ἦχι → ᾗχι | L1 | target proposal: abstain:clipped_band |
| 0 | constraint | 384c3f89-p000030-l0010 / 0 | Αλλα → Ἄλλα | D1 | excluded:initial_capital_unattested_50 |
| 0 | guard | 384c3f89-p000205-l0005 / 0 | Ἡ → Ἦ | L2 | excluded:all_caps |
| 0 | constraint | 384c3f89-p000068-l0028 / 7 | ἂσσον → ἆσσον | D1 | target proposal: shape_predicts_psili+acute |
| 0 | real_word | 384c3f89-p000182-l0027 / 2 | ὡς → ὧς | L2 | target proposal: shape_predicts_dasia+acute |
| 0 | real_word | 384c3f89-p000182-l0027 / 6 | οἷος → οἶος | L2 | target proposal: shape_predicts_psili+acute |
| 0 | real_word | 384c3f89-p000182-l0031 / 1 | ἢ → ἦ | L2 | target proposal: shape_predicts_psili+acute |
| 0 | real_word | 384c3f89-p000121-l0035 / 1 | ρ → ῥ | L2 | no_attested_mark_alternative |
| 0 | guard | 177b717d-p000017-l0012 / 8 | Στυγός → Στυγὸς | D2 | excluded:proper_name |
| 0 | constraint | 384c3f89-p000142-l0014 / 1 | εύρρηνός → ἐύρρηνός | D1 | constraint_no_unique_supported_minimal_repair |
| 0 | real_word | 384c3f89-p000142-l0030 / 3 | ἣν → ἥν | L2 | shape_predicts_dasia+acute; target absent from proposals |
| 0 | real_word | 384c3f89-p000059-l0027 / 0 | ὣς → ὧς | L2 | target proposal: shape_predicts_dasia |
| 0 | guard | 9c1dca9b-p000005-l0017 / 1 | Ιουλίου → Ἰουλίου | D1 | excluded:proper_name |
| 0 | guard | 9c1dca9b-p000005-l0017 / 2 | Κλαρετή → Κλαρετῆ | D2 | excluded:proper_name |
| 0 | lex_compete | 384c3f89-p000091-l0014 / 1 | εὔτ → εὖτ | L1 | target proposal: abstain:clipped_band; D2 slope-only attempt: abstain:clipped_band |
| 1 | real_word | 8b6b0de9-p000013-l0011 / 1 | λαίλαψ → λαῖλαψ | L2 | target proposal: shape_predicts_acute; contradiction=classifier_reads_google |
| 1 | grave | 8b6b0de9-p000021-l0012 / 0 | Τί → Τὶ | D2 | excluded:known_name |
| 1 | lex_compete | 8b6b0de9-p000008-l0002 / 1 | ἄδου → ᾅδου | L1 | target proposal: shape_predicts_circumflex+subscript |
| 1 | real_word | 9c1dca9b-p000015-l0063 / 0 | ἂν → ἄν | L2 | abstain:clipped_band; target absent from proposals |
| 1 | grave_line_end | 8b6b0de9-p000004-l0029 / 2 | χοροί → χοροὶ | L2 | no_attested_mark_alternative; D2 slope-only attempt: abstain:grave_accent_not_isolated |
| 1 | lex_miss | 8b6b0de9-p000008-l0019 / 2 | διακαή → διακαῆ | L1 | no_attested_one_cluster_variant; D2 slope-only attempt: abstain:grave_accent_not_isolated |
| 1 | human_unatt | 8b6b0de9-p000011-l0008 / 1 | ἐραστοῦ → ἑραστοῦ | L2 | no_attested_mark_alternative |
| 1 | real_word | 8b6b0de9-p000004-l0005 / 2 | βουνόν → βουνὸν | L2 | no_attested_mark_alternative; D2 slope-only attempt: abstain:grave_accent_not_isolated |
| 1 | real_word | 8b6b0de9-p000003-l0016 / 1 | ἂν → ἄν | L2 | shape_predicts_psili+grave; target absent from proposals; contradiction=classifier_reads_google |
| 1 | grave | 02a3a2a6-p000302-l0004 / 0 | Σφραγίς → Σφραγὶς | D2 | excluded:initial_capital_unattested_50 |
| 1 | real_word | 8b6b0de9-p000006-l0013 / 2 | χιών → χιὼν | L2 | no_attested_mark_alternative; D2 slope-only attempt: abstain:neighbouring_marks |
| 1 | real_word | 8b6b0de9-p000016-l0012 / 3 | σκιὰ → σκιά | L2 | shape_predicts_grave; target absent from proposals; contradiction=no_blob_below |
| 1 | lex_miss | 2793d64c-p000048-l0004 / 3 | ἡσυχάση → ἠσυχάσῃ | L1 | decided_other_form: ἡσυχάσῃ,; ambiguous_image;abstain:clipped_band; target absent from proposals |
| 1 | lex_miss | 02a3a2a6-p000046-l0018 / 0 | μοῦρθε → μοὖρθε | L1 | no_attested_one_cluster_variant |
| 1 | real_word | 8b6b0de9-p000008-l0020 / 0 | τίς → τις | D2 | abstain:acute_slope; target absent from proposals; contradiction=classifier_reads_google |
| 1 | lex_miss | 8b6b0de9-p000013-l0029 / 4 | ὠχριᾶς → ὠχριᾷς | L1 | no_attested_one_cluster_variant |
| 1 | real_word | 02a3a2a6-p000022-l0008 / 1 | ἡ → ᾑ | L2 | target proposal: shape_predicts_subscript |
| 1 | real_word | 8b6b0de9-p000021-l0016 / 4 | γλυκὺς → γλυκύς | L2 | no_attested_mark_alternative |
| 1 | real_word | 8b6b0de9-p000009-l0004 / 1 | εἰς → εἷς | L2 | target proposal: shape_predicts_none; contradiction=too_few_above_blobs |
| 1 | grave_line_end | 9c1dca9b-p000015-l0062 / 3 | βουλή → βουλὴ | L2 | shape_predicts_grave; target absent from proposals; D2 slope-only attempt: abstain:grave_slope_required; contradiction=no_blob_below |
| 1 | lex_miss | 2793d64c-p000070-l0014 / 2 | θρηνωδός → θρηνῳδός | L1 | no_attested_one_cluster_variant; D2 slope-only attempt: abstain:acute_slope |
| 1 | lex_miss | 9c1dca9b-p000015-l0066 / 3 | φελᾷ → φελᾳ | L1 | no_attested_one_cluster_variant |
| 1 | real_word | 2793d64c-p000068-l0011 / 0 | καί → καὶ | L2 | shape_predicts_acute; target absent from proposals; D2 slope-only attempt: abstain:acute_slope; contradiction=classifier_reads_google |
| 1 | real_word | 2793d64c-p000068-l0011 / 3 | των → τῶν | L2 | target proposal: shape_predicts_none; contradiction=too_few_above_blobs |
| 1 | lex_miss | 9c1dca9b-p000015-l0065 / 1 | μαγκούρες → μαγκοῦρες | L1 | no_attested_one_cluster_variant |
| 1 | lex_miss | 8b6b0de9-p000011-l0012 / 2 | σπινθηροβολεί → σπινθηροβολεῖ | L1 | no_attested_one_cluster_variant; D2 slope-only attempt: abstain:grave_slope_required |
| 1 | human_unatt | 8b6b0de9-p000021-l0007 / 3 | δύσης → δύσῃς | L2 | no_attested_mark_alternative |
| 1 | lex_miss | 02a3a2a6-p000318-l0017 / 1 | οἰκονόμησες → οἱκονόμησες | L1 | no_attested_one_cluster_variant |
| 1 | guard | 602cc72e-p000143-l0013 / 2 | Ζεὺς → Ζεύς | L2 | excluded:proper_name |
| 1 | real_word | 2793d64c-p000026-l0013 / 0 | Ὅπως → Ὄπως | L2 | excluded:known_name |
| 1 | grave | 602cc72e-p000353-l0006 / 0 | Χελιδών → Χελιδὼν | D2 | excluded:known_name |
| 1 | real_word | 8b6b0de9-p000004-l0026 / 3 | εὐρύ → εὐρὺ | L2 | no_attested_mark_alternative; D2 slope-only attempt: abstain:grave_accent_not_isolated |
| 1 | grave_line_end | 8b6b0de9-p000012-l0006 / 2 | νυκτός → νυκτὸς | L2 | no_attested_mark_alternative; D2 slope-only attempt: abstain:neighbouring_marks |
| 1 | real_word | 8b6b0de9-p000011-l0030 / 3 | θρασύς → θρασὺς | L2 | no_attested_mark_alternative; D2 slope-only attempt: abstain:grave_accent_not_isolated |
| 1 | human_unatt | 8b6b0de9-p000016-l0013 / 4 | φωλεά → φωλέα | D2 | decided_other_form: φωλεὰ; decisive_grave_slope; target absent from proposals; D2 slope-only attempt: decisive_grave_slope |
| 1 | real_word | 8b6b0de9-p000009-l0024 / 3 | τὸν → τον | L2 | target proposal: shape_predicts_grave; contradiction=classifier_reads_google |
| 1 | real_word | 02a3a2a6-p000022-l0011 / 0 | ἢ → ἤ | L2 | shape_predicts_psili+grave; target absent from proposals |
| 1 | real_word | 2793d64c-p000021-l0017 / 4 | γνωρίση → γνωρίσῃ | L2 | target proposal: abstain:clipped_band |
| 1 | human_unatt | 9c1dca9b-p000015-l0052 / 2 | ὄντες → ὅντες | L2 | no_attested_mark_alternative |
| 1 | real_word | 2793d64c-p000047-l0009 / 0 | οὕτως → οὔτως | L2 | target proposal: shape_predicts_dasia+acute |
| 1 | guard | 8b6b0de9-p000007-l0021 / 5 | Κλωθώ → Κλωθὼ | D2 | excluded:proper_name |
| 1 | real_word | 2793d64c-p000048-l0010 / 5 | φύγη → φύγῃ | L2 | target proposal: abstain:clipped_band |
| 1 | real_word | 2793d64c-p000070-l0021 / 0 | μόνῳ → μόνω | L2 | target proposal: abstain:shape_below_tau |
| 1 | real_word | 8b6b0de9-p000008-l0001 / 4 | ἄδην → ᾅδην | L2 | target proposal: abstain:neighbouring_marks |
| 1 | constraint | 02a3a2a6-p000318-l0020 / 0 | Άγι-Νικόλας → Ἁγι-Νικόλας | D1 | excluded:initial_capital_unattested_50 |
| 1 | lex_miss | 2793d64c-p000033-l0017 / 4 | ὑποκύπτη → ὑποκύπτῃ | L1 | no_attested_one_cluster_variant |
| 1 | human_unatt | 2793d64c-p000031-l0009 / 1 | ἠκολούθησεν → ἡκολούθησεν | L2 | no_attested_mark_alternative |
| 1 | grave | 02a3a2a6-p000178-l0014 / 2 | ἐγώ → ἐγὼ | D2 | target proposal: abstain:acute_slope; contradiction=classifier_reads_google |
| 1 | real_word | 8b6b0de9-p000012-l0005 / 3 | φρικτός → φρικτὸς | L2 | no_attested_mark_alternative; D2 slope-only attempt: abstain:grave_accent_not_isolated |
| 1 | lex_miss | 602cc72e-p000155-l0009 / 0 | Εὔνουχος → Εὐνοῦχος | L1 | excluded:initial_capital_unattested_50 |
| 1 | guard | 2793d64c-p000033-l0022 / 0 | Ω → Ὤ | L2 | excluded:all_caps |
| 1 | lex_miss | 8b6b0de9-p000016-l0023 / 0 | ἐλίσσ → ἑλίσσ | L1 | no_attested_one_cluster_variant; D2 slope-only attempt: abstain:acute_slope |
| 1 | human_unatt | 8b6b0de9-p000018-l0014 / 3 | λῃστὰς → ληστὰς | L2 | no_attested_mark_alternative |
| 1 | grave_line_end | 02a3a2a6-p000318-l0014 / 3 | φειδωλοί → φειδωλοὶ | L2 | no_attested_mark_alternative; D2 slope-only attempt: abstain:grave_accent_not_isolated |
| 1 | lex_miss | 02a3a2a6-p000168-l0005 / 2 | ῥωτήσουν → ρωτήσουν | L1 | no_attested_one_cluster_variant |
| 1 | real_word | 02a3a2a6-p000133-l0015 / 0 | Εἰν → Εἶν | L2 | excluded:initial_capital_unattested_50 |
| 1 | real_word | 22fda82b-p000063-l0039 / 4 | πῆς → πῇς | L2 | target proposal: abstain:shape_below_tau |
| 1 | real_word | 02a3a2a6-p000307-l0003 / 3 | ἁψηλὰ → ἀψηλὰ | L2 | target proposal: shape_predicts_dasia; contradiction=classifier_reads_google |
| 1 | guard | 602cc72e-p000167-l0027 / 2 | Πλούτος → Πλοῦτος | L1 | excluded:proper_name |
| 1 | lex_miss | 384c3f89-p000050-l0016 / 0 | Νηλείδαι → Νηλεΐδαι | L1 | excluded:initial_capital_unattested_50 |
| 1 | real_word | 177b717d-p000013-l0009 / 0 | Ἦταν → Ἤταν | L2 | excluded:known_name |
| 1 | real_word | 02a3a2a6-p000046-l0014 / 0 | Ὡς → Ὠς | L2 | excluded:known_name |
| 1 | real_word | 22fda82b-p000063-l0022 / 6 | σιγὰ → σιγά | L2 | abstain:neighbouring_marks; target absent from proposals |
| 1 | lex_miss | 177b717d-p000067-l0009 / 3 | ἀλληλογραφία → ἀλληλογραφίᾳ | L1 | no_attested_one_cluster_variant |
| 1 | real_word | 384c3f89-p000096-l0005 / 1 | δὲ → δέ | L2 | abstain:neighbouring_marks; target absent from proposals |
| 1 | guard | 177b717d-p000097-l0010 / 0 | Ω → Ὤ | L2 | excluded:all_caps |
| 1 | real_word | 177b717d-p000041-l0008 / 1 | πιο → πιὸ | L2 | target proposal: shape_predicts_psili+acute |
| 1 | lex_miss | 177b717d-p000104-l0012 / 4 | τἄλλοτινά → τἀλλοτινά | L1 | no_attested_one_cluster_variant |
| 1 | real_word | 177b717d-p000041-l0009 / 5 | ἔρμα → ἕρμα | L2 | target proposal: shape_predicts_circumflex |
| 1 | lex_unique | 384c3f89-p000096-l0004 / 3 | ᾖσι → ᾗσι | L1 | target proposal: shape_predicts_dasia; contradiction=no_blob_below |
| 1 | real_word | 177b717d-p000045-l0013 / 3 | ἢ → ἡ | L2 | target proposal: shape_predicts_circumflex |
| 1 | real_word | 384c3f89-p000096-l0006 / 0 | ὡς → ὧς | L2 | target proposal: shape_predicts_dasia+acute |
| 1 | real_word | 384c3f89-p000068-l0036 / 0 | αὕτως → αὔτως | L2 | target proposal: abstain:shape_below_tau |
| 1 | guard | 02a3a2a6-p000041-l0005 / 1 | Καλοκαίρι → Καλοκαῖρι | L2 | excluded:proper_name |
| 1 | real_word | 51fe7386-p000024-l0012 / 2 | βουνά → βουνὰ | L2 | no_attested_mark_alternative; D2 slope-only attempt: abstain:clipped_band |
| 1 | lex_miss | 51fe7386-p000024-l0012 / 3 | ὁλονυχτῆς → ὁλονυχτῇς | L1 | no_attested_one_cluster_variant |
| 1 | lex_miss | 51fe7386-p000024-l0012 / 4 | ῥωτιῶνται → ρωτιῶνται | L1 | no_attested_one_cluster_variant |
| 1 | lex_unique | 384c3f89-p000182-l0008 / 0 | Σειρήνες → Σειρῆνες | L1 | excluded:initial_capital_unattested_50 |
| 1 | lex_miss | 384c3f89-p000182-l0008 / 3 | ἡδείησιν → ἡδείῃσιν | L1 | no_attested_one_cluster_variant |
| 1 | real_word | 384c3f89-p000091-l0017 / 0 | ἢ → ἦ | L2 | target proposal: abstain:shape_below_tau |
| 1 | lex_miss | 384c3f89-p000183-l0022 / 0 | Ἀργώῃ → Ἀργῴῃ | L1 | excluded:initial_capital_unattested_50 |
| 1 | lex_miss | 384c3f89-p000050-l0041 / 1 | ἔδνοισιν → ἕδνοισιν | L1 | no_attested_one_cluster_variant |
| 1 | real_word | 384c3f89-p000142-l0003 / 1 | ἢ → ἣ | L2 | target proposal: shape_predicts_psili+grave |
| 1 | lex_miss | 384c3f89-p000091-l0027 / 0 | ἠρί → ἦρί | L1 | no_attested_one_cluster_variant |
| 1 | lex_miss | 384c3f89-p000170-l0024 / 2 | δήοισιν → δῄοισιν | L1 | no_attested_one_cluster_variant |
| 1 | lex_miss | 384c3f89-p000183-l0005 / 1 | μιξοδίησιν → μιξοδίῃσιν | L1 | no_attested_one_cluster_variant |
| 1 | lex_unique | 22fda82b-p000118-l0008 / 6 | συγχωρήσης → συγχωρήσῃς | L1 | target proposal: shape_predicts_none; contradiction=no_blob_below |
| 1 | real_word | 384c3f89-p000183-l0021 / 0 | ὡς → ὧς | L2 | target proposal: shape_predicts_dasia |
| 1 | guard | 51fe7386-p000024-l0015 / 1 | Ὅλυμπος → Ὄλυμπος | L1 | excluded:proper_name |
| 1 | guard | 51fe7386-p000024-l0015 / 6 | Ὅσσα → Ὄσσα | L2 | excluded:proper_name |
| 1 | real_word | 384c3f89-p000068-l0008 / 2 | οἱ → οἷ | L2 | target proposal: shape_predicts_dasia+acute |
| 1 | real_word | 384c3f89-p000068-l0037 / 2 | κορύνη → κορύνῃ | L2 | target proposal: abstain:clipped_band |
| 1 | real_word | 384c3f89-p000091-l0039 / 1 | οἷος → οἶος | L2 | target proposal: shape_predicts_psili+acute |
| 1 | lex_miss | 384c3f89-p000091-l0039 / 6 | τίφος → τῖφος | L1 | no_attested_one_cluster_variant |
| 1 | real_word | 384c3f89-p000182-l0016 / 0 | ἢ → ἦ | L2 | target proposal: abstain:shape_below_tau |
| 1 | lex_miss | 384c3f89-p000142-l0010 / 1 | προβάλησι → προβάλῃσι | L1 | no_attested_one_cluster_variant |
| 1 | constraint | 384c3f89-p000030-l0029 / 0 | Ἑἰ → Εἰ | D1 | abstain:neighbouring_marks; target absent from proposals; contradiction=classifier_reads_google |
| 1 | lex_compete | 384c3f89-p000059-l0013 / 6 | ἤγε → ἥγε | L1 | target proposal: abstain:shape_below_tau |
| 1 | human_unatt | 384c3f89-p000182-l0014 / 2 | παρθενικῆς → παρθενικῇς | L2 | no_attested_mark_alternative |
| 1 | real_word | 384c3f89-p000183-l0029 / 0 | αἳ → αἵ | L2 | shape_predicts_none; target absent from proposals |
| 1 | lex_miss | 384c3f89-p000205-l0011 / 0 | ἔσπεται → ἕσπεται | L1 | no_attested_one_cluster_variant |
| 1 | lex_miss | 384c3f89-p000050-l0027 / 1 | εἰσάμενοι → εἱσάμενοι | L1 | no_attested_one_cluster_variant |
| 1 | lex_unique | 384c3f89-p000182-l0023 / 1 | ἀμυδις → ἄμυδις | L1 | target proposal: shape_predicts_psili; contradiction=classifier_reads_google |
| 1 | lex_compete | 384c3f89-p000096-l0031 / 5 | ἔθεν → ἕθεν | L1 | target proposal: abstain:shape_below_tau |
| 1 | real_word | 384c3f89-p000205-l0013 / 0 | ὡς → ὧς | L2 | target proposal: shape_predicts_dasia+acute |
| 1 | constraint | 384c3f89-p000050-l0040 / 1 | ευπλόκαμος → ἐυπλόκαμος | D1 | decided_other_form: ἐϋπλόκαμος,; ambiguous_image;abstain:neighbouring_marks; target absent from proposals |
| 1 | real_word | 384c3f89-p000179-l0019 / 0 | εὐτ → εὖτ | L2 | target proposal: abstain:localisation_uncertain |
| 1 | real_word | 384c3f89-p000121-l0024 / 0 | οἷος → οἶος | L2 | target proposal: abstain:shape_below_tau |
| 1 | real_word | 384c3f89-p000053-l0028 / 0 | ἢ → ἣ | L2 | target proposal: shape_predicts_psili+grave |
| 1 | lex_compete | 384c3f89-p000183-l0009 / 1 | ἦχι → ᾗχι | L1 | target proposal: abstain:clipped_band |
| 1 | constraint | 384c3f89-p000030-l0010 / 0 | Αλλα → Ἄλλα | D1 | excluded:initial_capital_unattested_50 |
| 1 | guard | 384c3f89-p000205-l0005 / 0 | Ἡ → Ἦ | L2 | excluded:all_caps |
| 1 | constraint | 384c3f89-p000068-l0028 / 7 | ἂσσον → ἆσσον | D1 | target proposal: shape_predicts_psili+acute |
| 1 | real_word | 384c3f89-p000182-l0027 / 2 | ὡς → ὧς | L2 | target proposal: shape_predicts_dasia+acute |
| 1 | real_word | 384c3f89-p000182-l0027 / 6 | οἷος → οἶος | L2 | target proposal: shape_predicts_psili+acute |
| 1 | real_word | 384c3f89-p000182-l0031 / 1 | ἢ → ἦ | L2 | target proposal: shape_predicts_psili+acute |
| 1 | real_word | 384c3f89-p000121-l0035 / 1 | ρ → ῥ | L2 | no_attested_mark_alternative |
| 1 | guard | 177b717d-p000017-l0012 / 8 | Στυγός → Στυγὸς | D2 | excluded:proper_name |
| 1 | constraint | 384c3f89-p000142-l0014 / 1 | εύρρηνός → ἐύρρηνός | D1 | constraint_no_unique_supported_minimal_repair |
| 1 | real_word | 384c3f89-p000142-l0030 / 3 | ἣν → ἥν | L2 | abstain:localisation_uncertain; target absent from proposals |
| 1 | real_word | 384c3f89-p000059-l0027 / 0 | ὣς → ὧς | L2 | target proposal: shape_predicts_dasia |
| 1 | guard | 9c1dca9b-p000005-l0017 / 1 | Ιουλίου → Ἰουλίου | D1 | excluded:proper_name |
| 1 | guard | 9c1dca9b-p000005-l0017 / 2 | Κλαρετή → Κλαρετῆ | D2 | excluded:proper_name |
| 1 | lex_compete | 384c3f89-p000091-l0014 / 1 | εὔτ → εὖτ | L1 | target proposal: abstain:localisation_uncertain; D2 slope-only attempt: abstain:localisation_uncertain |

## Artifacts and verification

Per-word records (including guards and no-proposal words): `words_s0.jsonl`, `words_s1.jsonl`. Every strict decision, true or false: `sheets/{D1,D2,L1,L2}.rows.jsonl` and self-contained v4 HTML. Reference CSS is copied verbatim. Each card contains the full crop, enlarged detector-mark raster, caption, Google / Human (test reference) / Tool table with the word highlighted, and stage / column / outcome pills. For unknown one-to-one human references the display-only aligned span is highlighted and labelled; scoring stays unknown. Ratio decisions are diagnostic columns in per-word rows and report tables; they are not folded into strict sheets.

The 185-error instruments, Google labels, cached alignments and old rules are unchanged. The 4 known human-text errors are excluded from T1 recall only; precision tables retain the literal human-reference outcome, so a physically justified change can still be both-wrong against that reference. `run_receipt.json` records input hashes and timing. New thresholds use only DEV_BOOKS. Exact old decisions are read from the existing validation_candidates_s{seed}_strict.jsonl; no old-rule output is rewritten.

S1 RESULT: ACCEPT p=93.1% (LB95 84.9%) recall 14.6% (model-wrong 11.6%); HOLD p=81.2% (LB95 72.8%) +18.6% recall; L2 7 ACCEPT/6 TP/1 FP; D2 47 ACCEPT/44 TP/1 FP
