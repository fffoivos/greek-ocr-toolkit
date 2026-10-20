# After the clean-up: filtering rerun, recipe retest, benchmark, scaling (19 Oct 2026, coordinator review and plan)

Owner brief (19 Oct, 22:30): after the repo clean-up, (1) relaunch filtering and corrections on CSCS with the new tools; (2) test the new tools by rerunning the latest model's recipe on the corrected and filtered data, with an "as close as possible" criterion since lines are removed as well as corrected; (3) start the scaling experiments as designed; (4) compile a benchmark first, because evaluation needs it: considerable size but only newly sourced lines so the first experiment is barely affected; good lines, filtered and corrected and agent-verified; every class of segment and output (short/long, vertical/horizontal, numeric or not, mixed script, Greek modern/polytonic, Latin, Cyrillic, fonts, capitals, and every other class met so far); within each class, lines from as many books and sources as possible.

## 1. Review of the existing benchmark attempt (benchmark 0.1, 19 Oct)

What exists (CSCS `benchmark_20261019/attempts/build_01`, guide `benchmark_v01/README.md`):
- A scorer and builder with a fair-comparison contract (same IDs, literal references, exact pixels; strict NFD CER plus NFC, diacritic-insensitive, WER, exact lines, script confusion, per class/facet/book; failed reads score as empty; per-model manifest with training-audit evidence; `diagnostic_only` when exposure is unknown). This part is sound and reusable.
- Four historical panels (Google-labelled test 43,883; proofread-aligned 1,527; born-digital 3,600; synthetic 2,399) reproducing the wave-1b scores exactly. Continuity instruments, not an independent holdout.
- New candidates: 2,479 test / 647 dev, drawn from the whole 592,466-row inventory, target 1,200/300, with class quotas (monotonic 220, polytonic 420, Russian historical 100, modern 60, Serbian 40, Bulgarian 40, Ukrainian 40, Latin 60, Greek–Latin 100, numeric 120) and overlapping facets (accents, iota subscript, dialytika, capitals vs quotes, historical Cyrillic, script confusion, dots, dashes, leaders, short numbers, headings, long lines, rotation, font size, footnotes, verse, symbols, degraded scans).
- Status: NOT_READY, zero certified rows. Cyrillic quotas unfilled (0 assigned; 156 Cyrillic candidates of unknown language). Fonts, degradation, genre, edition and date facets have no tags. Candidate labels are Google proposals, not verified references.

Gaps against the owner's requirements:
1. Candidates were drawn from the whole inventory, including the original v2 train/dev/test. The owner wants only newly sourced lines (collect-v3 W1/W2), so the first experiment's pool is not disturbed → redraw from W1/W2 only.
2. Candidates predate the frozen filter (segmentation 0.9-s4, content gate 0.3, band 0.30–2.00) and the correction tools; the owner wants lines that passed filtering and carry the corrected labels → draw after the census rerun, from admitted rows only.
3. No verification path was executed (alignment queue empty, blind batches unused). The owner wants agent-verified references → the two-reader pixel adjudication (Sol first reader, Opus second on disagreement, owner sheet for the residual) with the literal-print rule.
4. Vertical/rotated lines, fonts and capitals are not quota classes → add them as quota classes with physical tags from the segmentation evidence (turned crops, letter-spaced caps, x-height, line length) rather than annotation by eye.
5. Book diversity is counted but not enforced → a per-book cap and a per-source spread inside every class.
6. Edition identity: the SPLIT1 edition map (1,359 editions) exists for W1/W2; the benchmark must reserve whole editions, not rows, so no training row shares an edition with a test row.

## 2. Sequence after the clean-up

| Step | What | Depends on | Executes | Owner gate |
|---|---|---|---|---|
| S0 | SPLIT1 edition split decision (owner sheet TNwtj25y…); sf7 audit closed (OC1/OC2 cards, TR2 test/dev inference) | — | spell-check lead (Sol), owner marks | sf7 TR2 job spend; split decision |
| S1 | Census rerun = pipeline 0.3 + seg 0.9-s4 + gate 0.3 + band 0.30–2.00 + sf7 + RU1 0.3 + N1 0.2 on W1/W2 (+ v2 for continuity), with the split map as pinned input; VERIFY_OK then smoke then full (census kind: 1 node, ≤4 h) | S0; clean-up merged (tools at their final paths) | segmentation lead (Sol); I submit | Clariden spend |
| S2 | Benchmark draw (§3): candidate pool = admitted W1/W2 rows; stratified draw with book cap; edition reservation written to the split map | S1 | sourcing lead (Sol) | benchmark size |
| S3 | Verification (§3.4): Sol first read on every candidate; Opus second read on disagreements and on a 10% control; owner sheet for the residual; seal 1 version with sha256 receipts | S2 | spell-check lead (readers), me (sheets) | Opus reader budget |
| S4 | Release v3 train = admitted rows minus reserved editions; corrected labels bound as edits-only overlays; admission receipts; exposure audit for every checkpoint to be compared | S3 | sourcing lead (Sol) | — |
| S5 | Recipe retest (§4): control = latest recipe on the previous release; arm = same recipe on release v3; three seeds each; instruments = benchmark panels + v2_test + wikisource_human | S4 | training lead (Sol); I verify deploy, submit | Clariden spend (≈ 6 × 3 GPU-h) |
| S6 | Scaling experiments (§5) on release v3 with the benchmark as primary instrument | S5 control exists | training lead (Sol) | per-wave budget ≤150 GPU-h |

## 3. Benchmark design (benchmark 0.2)

### 3.1 Scope and size
- Source: collect-v3 W1 + W2 admitted rows only (after S1). The original v2 train/dev/test are untouched, so experiment S5's control pool is unchanged except for the rows filtering removes.
- Size (as planned; sealed numbers in §3.3a below): **test 2,400 lines, dev 600 lines** (3,000 of ≈300k admitted W1/W2 rows ≈ 1%). Reasoning: ≥100 lines per quota class gives ≈4,500 reference atoms per class, enough to resolve 0.2 pp CER differences between arms at the seed ranges we observe (0.01–0.07 pp on 2.5 M atoms; ≈0.1 pp at 4,500); 2,400 lets the 15 classes below hold 100–300 lines each; removing 1% of W1/W2 changes no class share by more than 1 pp. Larger is not better here because every line costs two reads and owner time.
- Rows removed from training: NONE beyond the SPLIT1 split itself. The benchmark is drawn only from editions that SPLIT1 already assigns to TEST (60,070 rows in 10% of editions, plus the 99 editions forced to test), so the training pool is exactly the SPLIT1 train set whatever the benchmark size; dev lines come from the SPLIT1 DEV editions (7,007 rows). Owner, 19 Oct 23:00: size approved on the condition that it does not subtract from the experiment; this method subtracts nothing.

### 3.2 Quota classes (test lines; dev = ¼) — every class filled from ≥10 books and ≥3 sources where the supply allows
| Class | Test | Physical tag source |
|---|---:|---|
| Greek monotonic, ordinary lines | 240 | script class + orthography (gate expectations) |
| Greek polytonic, ordinary lines | 360 | orthography = polytonic |
| Greek polytonic, dictionary/journal mixed (bsb/ia poly1850) | 160 | source + class |
| Latin-script lines | 160 | script inventory |
| Legitimate Greek–Latin lines | 160 | gate inventory: two expected scripts, no mixed word |
| Cyrillic: historical Russian | 120 | orthography = historical (RU1 gate) |
| Cyrillic: modern Russian / Serbian / Bulgarian / Ukrainian | 160 (40 each; fill from supply, report deficits) | document metadata (CENSUS3) |
| Numeric and table cells (>1 alnum) | 200 | numeric grammar + cell flag (A ≤ 6) |
| Short lines (≤ 12 letters, non-cell: headings, labels, catchwords) | 120 | letter count |
| Long lines (≥ 60 characters) | 160 | character count |
| Vertical / turned crops (h > w, turned 90°) | 100 | segmentation 0.9-s2 turn flag |
| All-caps and letter-spaced headings | 120 | headings_caps class + inventory |
| Dotted leaders, dashes, punctuation-heavy | 100 | N1/dash tags + punctuation share |
| Small fonts (x-height ≤ 10 px) and large fonts (≥ 30 px) | 100 (50/50) | segmentation x-height |
| Degraded / faint / show-through (low ink density, low DocAI confidence) | 100 | ink density + confidence |
| Curved or skewed baselines (|angle| ≥ 2° or curve deviation ≥ 8 px) | 100 | segmentation 0.9-s3 evidence |
Total 2,400 (classes overlap; a line counts toward its primary class only; secondary facets are tagged and reported). Open: Serbian/Bulgarian/Ukrainian supply is unknown until S1; deficits are reported, never filled with easier lines.

### 3.3 Draw rule (authorised revision, coordinator under the owner mandate, 20 Oct 2026 00:33–05:31; Astra ASTRA-CENSUS05R H1 asked for this to be recorded)
The original rule (cap 4 lines per edition, forced editions excluded) was infeasible on split2: 49 non-forced TEST editions × 4 = 196 lines against 2,460. Authorised revision, applied by BENCH02I–L on census_05: (1) the non-locked rows of the 99 forced editions are drawable (those editions are already out of training; the exact LQB-truth and N1-locked rows stay undrawable — 0 drawn); (2) the cap is 50 lines per class × edition (sweep BENCH02H: the smallest of {12, 25, 50} at which every supplied class reaches ≥ 90% of its quota on the upper bound), allocated fairly (round-robin over classes in precedence order, one line per class per pass); (3) the series cap is 3× (unverifiable without series identity, reported); (4) classes without supply are reported as deficits, never substituted: test modern Cyrillic is Serbian-only (48 of 160; Serbian subgroup quota 40), dev greek_latin 15/40, latin 3/40, historical Russian 0/30, polytonic dictionary 0/40; (5) "degraded" is relative (bottom 5% DocAI confidence within source among admitted rows) because admission removes every line below 0.89. Result on census_05 (candidates v3, sha 0432c56f…): in-quota test 2,340 / dev 453, reserve 468 / 80, 15/16 and 11/16 classes filled, 0 locked rows. The original rule text follows for the record.
### 3.3a Sealed instrument (benchmark 0.2, 20 Oct 2026; Astra CP3 M2 fix)
The 16-class quota table sums to **2,460 test / 615 dev** (not 2,400/600; "15 classes" above is stale). The candidate-stage figures (15/16 test, 11/16 dev classes filled) are NOT sealed coverage. seal03 (superseded by seal04, which drops one dev row that is pixel-identical to a test crop): **test 2,253 rows, 16/16 classes non-empty but only 2/16 at full quota; dev 438 → 437 rows, 14/16 non-empty, 6/16 at full quota**; dev historical Russian and dictionary/journal are empty; modern Cyrillic is Serbian only (40 test / 8 dev), so the suite does not evaluate Russian/Bulgarian/Ukrainian. Deficit = initial supply deficit + LF1 loss (UNFILLED), reported separately per class × split in the seal record (docs/harvest/collect_v3_admission/seal02/seal03_record/, seal04_record/). Size power: read it from the sealed per-class counts, not from the planned 100-per-class figure.
#### 3.3 (original)
Within each class: group by source, then by edition; round-robin across sources, then across editions, taking at most 4 lines per edition and at most 12 per book series (gazette issue = edition), seeded. Exclude any row whose edition appears in the original v2 train/dev/test or in a locked evaluation set. Record the draw plan (seed, order, caps) and the per-class × source × edition counts.

### 3.4 Verification protocol (owner, 19 Oct 23:20)
The reference of every benchmark line is the pipeline's filtered and corrected label; it is accepted as the mix stands. **Qualification (Astra CP3 M1, 20 Oct):** the reference is a pipeline reference, filtered on letters and crop geometry; diacritics are NOT qualified by the last filter (its prompt and mapper exclude marks by design), so the suite is `diagnostic_only` for mark-level claims and the 97 diagnostic mark flags (83 TEST / 14 DEV) stay in the evidence; any mark-qualified claim needs a separate authorised audit. Sol is a LAST FILTER on the drawn lines, not a label producer: for each candidate it checks (a) that the crop obeys the segmentation rules (one central line; the text is the visible line exactly; no other complete line; at most two whole neighbour words at 100% visibility; nothing turned or clipped) and (b) that the text is what the image shows. It answers per line: OK / crop violates rule <which> / text differs <where>. A flagged line is removed from the benchmark and replaced from the same class and source by the draw rule; flagged lines are kept as evidence for the filter and the tools. Sol may write what it reads when it flags a text difference, but that reading is evidence, not the reference. No second reader is required; the owner sees a sample of the flags on one sheet if he wants to calibrate Sol's strictness. Cost ≈ 3,000 Sol card-checks (≈ 6 Codex points).
Sealing: references = the corrected labels of the unflagged lines; images (sha256), tags, draw plan, Sol check receipts; one `suite.json` version.

### 3.5 Exposure rule
Every compared checkpoint must have a training audit against the reserved editions (rows, synthetic text sources, corrector training data). Unknown exposure = `diagnostic_only`. The LQB truth set and the 888/150/417 review sets stay separate instruments.

## 4. Recipe retest = E4 wave 2 (H7), as preregistered on 17 Oct
The retest the owner asks for is the wave-2 package already prepared (greek-page-ocr branch sol/e4-wave2 a707a36, brief `briefs/E4_wave2_scale_brief.md`, readback brief, registry rows in TRAINING_DIRECTIONS §E4 wave 2): three arms, three seeds each, one recipe.
- **ctrl = v_c**: the wave-1b recipe (codec v2 + recovered rows, width ×2, 50% synthetic v5, eight epochs × 428,872 draws, batch 64, AdamW 1e-4/0.05, OneCycle, data seed 20261015); existing checkpoints reused if hash-verified on Clariden.
- **add**: v_c's real rows PLUS every row of release v3 (the admitted, filtered W1/W2 rows after S1, minus the benchmark editions) at natural frequency; synthetic recomputed to stay 50%; same draws per epoch; parliament cap 25% re-applied.
- **add_corr**: add + the registered label corrections applied by row id to old and new rows (ru1_v3_edits, n1_v1_w1, sf7 release if audited).
"As close as possible" is therefore already the design: identical architecture, schedule, draws and synthetic positions; the only change is the real row set (and labels in add_corr). What filtering removes shows up as a smaller `add` set; the MIX_TABLE receipt (previous vs new unique rows and draw shares per class) is mandatory and reports the removed share per class. Preregistered H7: add lowers v2_test CER overall and on the weak categories beyond v_c's three-seed range; add_corr lowers it further on the corrected classes; refuted otherwise. Instruments: wave-1b set + E3 per-class/line-type slices + the locked new-source strata + benchmark 0.2 panels.
Remaining inputs: release v3 admission file (S4), corrections registered at bind time, W1/W2 original crops on Clariden (W1 uploaded 18 Oct, 28,798 rows; W2 pending), deploy + smoke on debug, then the three-arm campaign (≈ 9 × 3 GPU-h).

## 5. Scaling experiments = Stream S (data plan §4) with the width ladder (Track C1)
- **Reference stratum** (§4.1): the E3 real-half sampling frame frozen (class proportions, wave/source policy, parliament cap 25%, length and date distributions); new rows enter it only under the same source policy; targeted rows are a separate stratum.
- **Design** (§4.2): unique real rows U ∈ {208k, 420k} × {reference only, reference + targeted at equal U}, equal optimizer draws, synthetic recipe and fraction frozen within the series, repeats and effective distinct support disclosed per arm; crossed with **C1** widths ×1 / ×1.5 / ×2 (timing probe done 16 Oct: ≤ 17% more GPU time at ×2, CPU latency ×1.7); three seeds; ≈ 20–30 runs after sharing arms; primary instruments as in §4 plus benchmark 0.2 per class.
- **Order** (TRAINING_DIRECTIONS §3): C1 width × size at the 420k reference point → M3 class reweighting then M4 source temperature → P1 in-domain pretraining after C1, P2 donor isolation on demand → G generator ablations rolling → C2 only after C1.
- **Caps and stop rule:** ≤ 150 GPU-h per wave without further gating; the cumulative scaling series ≤ 120 GPU-h; no 840k before the 420k result; no change to the test books; no parliament by default beyond the cap.
- **Dependency:** the 420k reference-stratum collection is sized from release v3; if release v3 holds fewer than 420k reference-stratum rows after filtering, the upper size point is the actual count and is reported as such, not padded.

## 5b. Novelties (not scaling) — from TRAINING_DIRECTIONS rev 2.4 and the 7 Oct literature review
Stream S + C1 is pure scaling (data size × width). The new ideas are separate one-variable arms, each against the same pinned control, run broad in the same waves once release v3 and benchmark 0.2 exist:
| Idea | Source | State | Where it goes |
|---|---|---|---|
| S2 label correction by lexicon + ink (sf7/RU1/N1) | directions S2; owner decision | built; sf7 audit open | add_corr arm of wave 2 (§4) |
| S3 calibrated confidence weighting of CTC loss | directions S3 | not started; after S2 validated | wave 3 arm |
| C2 training-only semantic guidance (SVTRv2-style auxiliary head, inference unchanged) | directions C2; lit review Experiment 3 (diacritics within the native Mac budget) | not started; after C1 | wave 3 arm |
| C3 mark head with forced alignment | directions C3 | only if S2 shows marks learnable yet lagging | conditional |
| P1 in-domain masked pretraining on unlabelled train-only crops, compute-matched control | directions P1; lit review §4 real adaptation | not started; after C1 | wave 3 |
| P2 donor initialisation isolated | directions P2 | low priority | on demand |
| M1 born-digital replay 10%; M2 synthetic fraction 40/50/60 + curriculum; M3 class reweighting (Cyrillic 3→6%); M4 source temperature | directions M | M1/M2 preregistered earlier; M3/M4 after V | wave 3 rolling |
| G generator v6 bundle: capital-mark policy, display faces for caps, old-style numerals, light-on-dark 5%, per-mark visibility gate; real-statistics matching (x-height, stroke, contrast, blur, leading, skew, padding) and raster-only degraded twins | directions G; lit review §3 | bundle declared; twins not built. G-AUDIT 20 Oct (sol-recut f65fe2696, metadata evidence only): coverage 0 yes / 920 partial / 368 no over 1,288 cells, 7 gap groups. **Prerequisite (coordinator, 20 Oct):** the renderer's text path must move to codec v2.1 before any G ablation, because codec v1 rejects ѣ (111 occurrences) and ј (87) in the seal04 references, which matters for the Cyrillic classes (G-AUDIT gap 7). A8 shards and A9 twins wait for S1 | wave 3 ablations |
| Conservative script-aware candidate rescoring, then conditional CTC–LM fusion (log P_CTC + λ log P_LM + β length + γ script) | lit review rec. 7 / §5 | not started; only if wrong-script substitutions are an appreciable residual (E3: ≈120 swaps in 62k mixed atoms → low priority) | parked until benchmark 0.2 shows a mixed-script residual |
| PARSeq small challenger (encoder–decoder comparator) | lit review §1 | after data/crop controls | parked |
| Page supervision for detection from the PDF text layer (lit review Experiment 1) | lit review §2 | aspect A, not B | A track, separate |
| Masked-crop training (wave 1d H4) and weak-category upsampling (wave 1e H5) | directions registry | 1e refuted; 1d result in the registry | closed/recorded |
Rule: every novelty is one preregistered hypothesis with the decision it settles, three seeds, the pinned control of its wave, benchmark 0.2 per class as primary instrument; negative results recorded with the same care.

## 6. Decisions for the owner before S1
1. Benchmark size 2,400/600 and the quota table (§3.2).
2. Opus as second reader for ≈1,000 cards (spend).
3. SPLIT1 edition split (review sheet) — required for admission of W1/W2 and for edition reservation.
4. Census rerun spend on Clariden (one census job, ≤4 h, after the clean-up lands the tools at their final paths).

## 7. Review checkpoints for the experiments (owner, 20 Oct 2026 00:57)
Before the launch of each experiment family (wave 2 H7; the C1 width × size series; each novelty family C2, P1, S3, G, M), Astra at xhigh reviews the deployment-ready code as it will run: the deployed bundle and its hash manifest, VERIFY_OK, the package tests, a smoke run on the debug partition, the preregistered hypotheses and driver decision rules, and the exposure/leakage audit of the training rows against the benchmark editions. BLOCKER/HIGH are fixed and re-reviewed; nothing is submitted before PASS. Each family's results get a second Astra review before the next family starts.
