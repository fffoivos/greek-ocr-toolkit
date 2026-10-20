# R0 whole-line population CER (recogniser vs Google), 17 Oct 2026

The sample is 100 seeded lines: 50 from stratum (i-b), the clean locked Wikisource set; 25 from (ii), which is mark-enriched and not a population estimate; and 25 from the 666 continuity instrument.

Two blind Opus readers each transcribed every full printed line, all marks included, never guessing. Lines where they disagreed went to a third reader.
- 84 lines: both readers agreed.
- 13 lines: settled by majority of three.
- 3 lines: unresolved, so excluded.

Most disagreements were single marks, such as ῳ/ω, ἂ/ἀ and ἥ/ἡ. The four elision apostrophe codepoints ’ ᾽ ᾿ ' were treated as the same sign.

CER is Levenshtein distance divided by the number of truth characters, on 97 lines.

| Stratum | Recogniser letters | Google letters | Recogniser letters+marks | Google letters+marks |
|---|---:|---:|---:|---:|
| 666 continuity | 0/656 = 0.00% | 0/656 = 0.00% | 6/820 = 0.73% | 6/820 = 0.73% |
| (i-b) clean locked Wikisource | 2/1265 = 0.16% | 2/1265 = 0.16% | **5/1584 = 0.32%** | **12/1584 = 0.76%** |
| (ii) mark-enriched new sources | **17/927 = 1.83%** | 3/927 = 0.32% | **30/1140 = 2.63%** | 6/1140 = 0.53% |

How to read these:
- The samples are small, 25–50 lines per stratum, so the confidence intervals are wide.
- On Wikisource-type books, the recogniser matches Google on letters and beats it on marks.
- On the new sources, the recogniser is about 5× worse than Google on letters and marks. This is a domain gap (R0: mixed Greek/Latin, new fonts), and wave 2 targets it.

Files: wl_key.json (strata; private), wl_r1/r2/r3.jsonl (reader transcriptions), wl_scored.json (truth and hypotheses per line), and scripts/labelfix/r0_wholeline_score.py.
