# glossAPI improvement plan v3 (7 Oct 2026, after the Astra consistency review and the Astra literature review)

Frame (owner): the current glossAPI pipeline with Docling upstream; the owner's line generator (`greek-page-ocr/factory`) is built on,
not replaced; standard = Apple Live Text on English; all tracks move together. Inputs: `STOCKTAKE_20261007.md`,
`reviews/ASTRA-consistency_review_1.md` (REVISE: 1 BLOCKER, 5 HIGH), the literature review (`greek-page-ocr/docs/ocr_program_2026-10-06/
LITERATURE_REVIEW_ASTRA_20261007.md`, 9 recommendations, 3 experiments), `REPORT_MORNING.md` with the errata below.

## Errata to the morning report (from the Astra review; recomputed by the coordinator where marked ✓)
- Batching is not output-preserving on the campaign sample: B2 markdown byte-equal 192/242 ✓, full fidelity 18/242; the −35% run (8 workers)
  changed markdown on 2/11; the 11/11 was the 4-worker run ✓. The "fidelity gate only tripped on timing fields" claim was wrong.
- Batched B2 = +23.2% time, −18.9% throughput; sequential timing is censored by one crash.
- pypdfium2 pin is a mitigation (one crash remained with 4.30), not a root-cause proof.
- DeepSeek 0.83 = document-level, accent-folded word-multiset recall (median 0.829, mean 0.804), not page recall or CER.
- O6-prep's 12.2% is the layout-first alternative, not the plugin ceiling; "another 13.7% partly covered" was 1.48%.
- O5: Latin contributes 74.5% of the base's errors; on modern-Greek lines the base is 1.33%, so 12.7% → 1.1% is not a tenfold gain on Greek.
- O2 minus O5-train documents leaves 228 lines with no polytonic or Cyrillic.
- No Docling OCR plugin integration exists today: `Corpus.ocr` is DeepSeek-only, Docling options set `do_ocr=False`, the batching
  adapter rejects OCR-enabled pipelines, native cells suppress OCR cells unless full-page replacement is set (BLOCKER F01).

## Tracks, steps and gates (reviews: Sol per checkpoint, Astra per track result; results certified, not plans)

### Track A — text-layer extraction (keep improving the path that handles most pages)
A0 Diverse-sample gate for the ToUnicode repair (owner condition, 6 Oct; unmet): draw a second OA sample disjoint from the 242 docs
   (other hosts incl. slow ones, producers other than Word, page counts outside 10–250, negative controls), run the Rust repair + routing
   on the home server (CPU), report decision-equivalence and projection; until it passes the repair stays "an experiment", not merged.
A1 REMOVED (owner, 7 Oct evening): no DeepSeek runs. glossAPI is a codebase, not a running service; DeepSeek is one pluggable
   engine, not a baseline. Comparators are Live Text on English twins and the exact text layer on Greek pages.
A2 Routing revalidation under the plugin (after C2): which selected pages improve, which unselected pages hide problems, clean pages intact.
A3 Label-quality rules from the tagger: wrong-codepoint Latin letters inside Greek words audited contextually (not folded by majority),
   polytonic class by tagger, provenance kept; feeds C3 and the benchmark.
A4 Repair/extraction stays as certified; 768-doc routing numbers stand as historical observations.
   A3b (owner, 7 Oct evening) Line-category tagger, rule-based, no human: dotted leaders/TOC, numeric/table cells, all-caps headings,
   footnote-size type and italic/bold (from PDF font name/size), hyphenated line ends, punctuation-heavy, mixed-script, very long lines;
   categories become an axis of the E1 readout and galleries; each weak category maps to a generator change (new content class, like
   `furniture`) or a pipeline change (crop padding, cell policy). Fallback for undecidable lines: O2 two-model adjudication.

### Track B — Docling parallelism, within one GPU and across GPUs
B1 Resolve the 50 B2 markdown differences and 83 JSON-tolerance failures (what differs, why; batch composition effects); reconcile the
   instrument's censored timing; only then rerun matched configurations (workers 4 vs 8, batch 8, pypdfium2 4.30) on the same node.
   Until then the auto-CUDA batching default is OFF (explicit opt-in stays). Gate: Sol (instrument fix2 + results), Astra scoped.
B2 Multi-GPU arm (owner standing test case) on a 2-GPU pod with the instrument's `--use-gpus multi`; per-GPU failures, recovery, break-even.
B3 Crash class: keep `--crash-loop` accounting, keep the pypdfium2 pin as mitigation, add a periodic sequential crash soak to CI-like runs.
B4 Later: OCR-enabled pipeline batching (not before C2 exists; the T1.5 certification does not cover it).

### Track C — lightweight OCR as a Docling engine plugin (Astra's revised P0–P5)
C0 Inventory + custody: bind source/recipe/codec/checkpoint hashes; selective commits of the July generator and detector work; correct
   `DOCLING_PLUGIN_CONTRACT.md` (callable yields updated Page objects after installing cells; plugin scale explicit, bundled engines use
   scale 3 = 216 dpi; no claimed routing integration; detector = first candidate, not mandatory architecture).
C1 Vertical slice through the REAL glossAPI entry point: external plugin registration (`OcrOptions.kind`), existing DBNet + recogniser,
   cell installation, native-text replacement policy (bitmap supplementation vs full replacement of corrupt native text), Docling export;
   ordinary Docling execution, `batched=False`; frozen diagnostic page cohort with its source partition. Gate: executable test that
   proves invocation, geometry, replacement and page preservation (Sol), then Astra. **This is the gate before any new training.**
   **STATUS 7 Oct 19:35: CP-C1 PASSED (Sol cycle 2 + Astra scoped verification). Mode A plugin certified on the 32-page cohort: 18 replaced pages, mean CER 7.53%, 6/6 clean byte-identical, 663/663 rects; 55 ms/line CPU (latency gap logged). Open MEDIUM: extreme-width crop branch, codec-hash in .pt loader.**
C2 Measure the existing models end to end through C1: the exact text layer on Greek pages as the reference (no Live Text here; the English-twin Live Text comparison is a benchmark claim in D2, made once the model is ready); attribute detector,
   recogniser and downstream-layout errors; unsupported cases recorded. Latency on the Mac: cold/warm, per stage, total page, memory.
C3 Data: one shared source-document/family partition for everything (lines, pages, silver, calibration, eval); codec v2 bridged through
   generation, shards, training, checkpoints, inference; complete vs partial detector labels (O1 pages with unlabelled regions = ignore
   regions, 268 scan pages unlabelled); appearance band re-measured on plugin crops by domain; crop augmentation fitted to measured
   detector residuals; ink transfer as a measured arm; per-word script tags with provenance; polytonic/Cyrillic supply from the generator's
   sources and from O4a sourcing; composer extended to hand Docling-rendered pages at the plugin scale with transformed GT.
C3b Verified text-layer lines as a real training component (owner, 7 Oct evening): on documents whose text layer is present and
   verified good (ToUnicode repaired or never broken; cleaner clean; tagger script tags consistent; render-vs-text consistency check
   on a sample of lines), take Docling's own line cells at the plugin scale, cut the crops with the plugin's crop/resize code, and
   ingest them through the factory as a real component with document partition id and shard hashes (rule P1/P2). This is the
   O1 extractor moved to the exact plugin crop distribution (Mode A crops); O1's char-box crops remain the gold for geometry.
   Admission is a gate, not a heuristic: a verified-good document is one that passes all four checks; failures are logged with reason.
O4b (owner, 7 Oct 23:20; from the E1 map) Real line supply for the weakest strata — image+text pairs: S1 published datasets
   (Polyton-DB, GRPOLY-DB, CLLG Zenodo corpus CC-BY); S2 archive.org/Anemi books with text layers via the O1 extractor (silver, two-model
   agreement); S3 Wikisource proofread pages with detector + CTC forced alignment (gold text). Label tiers recorded; document-disjoint
   partition. Feeds E2 (next sweep) and D2 (benchmark redraw with polytonic/Cyrillic). Brief: greek-page-ocr briefs/O4b_image_text_sourcing_brief.md.
O4d (owner, 8 Oct 12:30; OPEN PROBLEM) Line geometry on bound scans. Evidence: the owner's check of CLLG readings on parliament lines
   (artifact AJRarJ26UPVQwY73pEQLHX; notes in greek-page-ocr docs/evidence/cllg_check/) found that most "recognition" disagreements are crop
   geometry: (i) lines curl toward the gutter, so the straight text-layer box clips the top/bottom of the words at one end and the neighbouring
   line intrudes there; (ii) a text-layer box spanning two lines; (iii) the final glyph clipped at the right edge; (iv) line-end hyphenation conventions differ: the
   text layer writes '-', '¬' (U+00AC) or nothing, CLLG writes '-' or nothing (measured on 400 lines, 8 Oct 13:40: layer ends with a mark on 33,
   CLLG on 31; of 24 ink-hyphen lines the label lacks, CLLG emits it on 9) — exact agreement counts these as disagreements. Test solutions, in cost order, all built in the toolkit:
   G1 ink-refined extraction: ink components inside each box → quadratic baseline fit → strip extracted along the curve → box extended to ink
   extents → two-baseline boxes split. G2 baseline+polygon segmentation (Kraken blla, CLLG's native pipeline) with per-line rectification as
   the Mode B detector candidate. G3 page-level curl dewarp (Leptonica-style) before boxing. H1 line-end hyphenation: the text layer's '¬' (U+00AC) is an artefact of its OCR engine (owner, 8 Oct 13:45), never mapped to a hyphen;
   the ink check (component with hyphen geometry after the last glyph) decides whether a hyphen exists; admitted labels keep the ink hyphen
   as '-'. The text layer is just another OCR: silver = agreement of two OCRs, shared errors survive; independent signals (ink checks,
   lexicon/edition alignment, human checks) are the only way to do better. Measurement: a geometry-stratified set (trailing ends,
   two-line, clipped-edge; the 44 checked lines + ≥300 sampled) scored by CLLG CER vs the layer and by exact-agreement yield (silver lines
   admitted per 1,000); G1 is adopted if yield rises and CER falls; G2 is compared head to head on the same pages; the winner reruns the O4b
   S2 extraction (parliament + Anemi) and sets C4 Experiment 1's detector targets to baseline/polygon labels. D2 gets a geometry stratum.
   Order: after the E2 sweep readout, before the S2 adjudication round.
   G4 (owner question, 8 Oct 13:35: "doesn't this imply an issue with ground truth for training?") Training-side arm: scan-derived lines are
   NOT admitted until the geometry fix + label-convention checks (end-of-line hyphen, line-end punctuation) pass; the born-digital O1d real
   lines are unaffected (exact glyph geometry). Synthetic labels are exact but the renders are too clean: add to the recipe (v9, eval + train
   arms) baseline curl, neighbouring-line fragments at the top/bottom, edge-clipped glyphs, and two-line / empty boxes as reject cases, so the
   recogniser is trained on what the extractor delivers at inference; measure on a geometry stratum of the v8/v9 held-out set.
O4e (owner, 8 Oct 13:50; "we can still render html of pages, social media, newspapers and parse it as an image — an untapped resource")
   G5 EVIDENCE (QC-agent calibration, 8 Oct 17:20; files glossapi-ocr-local/experiments/glyphs_calib/strips_v2{,_straight}): on 40
   synthetic polytonic lines x skew 0-6 deg (240 strips), our E1 f50_s0 median CER by skew bin BEFORE straightening = clean (renderer's
   random +-2 deg) 0.193 / 0-1 deg 0.028 / 1-2 deg 0.188 / 2-3 deg 0.514 / 3-4 deg 0.678 / 5-6 deg 0.86; AFTER straightening with
   greekocr.glyphs.lines_api.separate_lines = 0.061 / 0.069 / 0.069 / 0.071 / 0.078 / 0.071 (flat). CLLG 0.000 in every bin either
   way. Reading: recipe v5 skew augmentation did not buy invariance at this model size; a ms-cost straightener in front of E1-type
   readers and in the training-crop path recovers it. Real-page deployment still goes through the decision rule (stratified
   held-out, reference-free signals, cost < 1/5 recogniser; hybrid training with the fixer stochastically off).
   G5 cost: on exactly level tight crops E1 goes 0.033 -> 0.083 after straightening (height-normalised output with 1.9/1.0 x-height
   margins and paper-tone padding is not E1's tight crop); a tight post-straighten crop is being tested and must recover <= 0.04 before
   the straightener is deployable in front of E1. Real crops (444, calibrated CLLG limits): 195 readable / 241 partly / 8 unreadable;
   247 have the accent/tall-letter zone cut by the text-layer box; 81 have an ambiguous target (several lines or columns). Text-layer
   boxes are therefore the wrong crop source for training lines (QC agent, docs/GLYPHS_CALIBRATION.md in greek-ocr-toolkit).
   G5 tight variant (8 Oct 17:45; CORRECTED 17:55): separate_lines(tight=True) (crop to ink +-0.3 x-heights after straightening)
   gives E1 median CER (NFD, canonical) clean(random +-2 deg) 0.033 / 0 deg 0.041 / 1 deg 0.041 / 2 deg 0.041 / 3 deg 0.039 /
   5 deg 0.043, mean 0.051 (original 0.411, padded-straight 0.109); CLLG 0.000 every bin. Level lines DO regress slightly:
   rotated 0 deg original 0.033 -> tight 0.041 NFD (0.033 -> 0.051 NFC), so the no-regression bar (<= +0.005 median NFD) is NOT
   yet cleared; a margin sweep (0.2/0.3/0.5 x-heights) and a no-resample path for |skew| < 0.3 deg are under test. Scorer: NFD
   both sides + mark F1 is canonical; NFC kept in the table. Real-page check (stratified held-out, reference-free) still required.
   G5 margin sweep (8 Oct 18:05, E1 median NFD CER clean/0/1/2/3/5 deg | mean): tight m0.2 = 0.041/0.028/0.029/0.028/0.037/0.042 |
   0.046; m0.3 = 0.033/0.041/0.041/0.041/0.039/0.043 | 0.051; m0.5 = 0.052/0.066/0.061/0.056/0.061/0.065 | 0.075; m0.3 with shift-only
   under 0.3 deg identical to m0.3. Level lines at m0.2: 0.028 = original 0.028 -> bar cleared; the regression was the margin, not the
   resampling. DECISION: separate_lines(tight=True, margin=0.2 x-heights) is the recogniser-facing default (QC agent commits after
   CP-G3c2; paired bootstrap on the level bin to follow in GLYPHS_CALIBRATION.md). Real-page check still required before the plugin
   ships it.
   Rendered web pages as exact-label page data: headless Chromium prints pages to PDF with embedded fonts → the existing born-digital
   extractor (O1 path) yields exact line records with exact boxes; the DOM text is the page-level reference for the Docling-downstream
   measurement (C2) at scale; degraded twins (page_degrade) give scan-like pages with intact labels for the detector and the recogniser.
   Sources (licence recorded per record; internal use): el.wikipedia / el.wikisource (polytonic in real web fonts), gov.gr and eur-lex el,
   Greek news sites, Mastodon public timelines (informal Greek, emoji, mixed script), Gutenberg el. Built in the toolkit (greekocr.real.sources.web_render).
   Wave 1 = a few thousand pages on the node; records enter the environment at tier "exact-rendered".
**E1 run4 DONE 7 Oct 23:10 (results docs/ocr_program_2026-10-06/E1_REPORT_run4.md; CP-E1 Sol review pending):** observed means over 3 seeds:
   real test f75 1.84% vs f100 1.94% (gap within seed range); v7 synthetic held-out f25 6.56% (f100 72.8%); legacy transfer (unprovenanced,
   disclosed) f25 4.91%; f0 seed 1 did not converge (79.7%); mark errors on v7 for mixed arms: rough breathing 62–84%, smooth 41–59%, iota
   subscript 100%, circumflex 26–52%, grave 39–74%, dialytika 88–92%; Cyrillic 12–27%; real test has no polytonic/Cyrillic (NA).
   Interventions below are proposals; E1 does not establish their effects. Next round E2 = warm-start arms (C4b) × mixture .25/.5 × O4b supply + 64 px.
C4 Train only what C2 implicates: lit-review Experiment 1 (detector with PDF geometry + degraded twins + small real-scan set; targets:
   halve omitted characters, ≥95% glyph coverage on scans, ≥25% page CER reduction, ≤10% p95 latency cost) and Experiment 2 (real
   fraction sweep {0,.25,.5,.75,1}, crop/ink ablations, three seeds; targets: modern-Greek ≤1.20%, font-OOD ≤2.50%, no script worse by
   >0.2 pt); then Experiment 3 (48 vs 64 px × training-only guidance; Core ML export parity ≤0.05 pt, ≤10% p95). Compact/Core ML
   qualification and release lineage are gates, not afterthoughts.
C4b Warm-start arm (owner, 7 Oct evening): in Experiment 2 add arm P = encoder of PaddleOCR `el_PP-OCRv5_mobile_rec` (Greek+English,
   354-char dictionary, no polytonic/Cyrillic → head replaced by our codec) converted to PyTorch, same mix/budget/seeds as the
   from-scratch arm; conversion verified by reproducing the original model's logits on 100 crops before training; licence
   (Apache-2.0) and framework drift recorded in the run's provenance. Decision rule: held-out CER on polytonic and on unseen fonts,
   no script worse by >0.2 pt. Further candidates (recognisers and detectors) come from the Astra warm-start survey R1; any
   candidate added becomes an arm under the same rule, never a replacement by argument.
R1 Research (Astra, web-enabled, launched 7 Oct ~18:40): survey of pretrained lightweight recognisers/detectors as warm-start or
   teacher candidates (dictionary coverage incl. polytonic checked, licence, framework, conversion cost, head-swap recipe).
   Output: `WARMSTART_SURVEY.md` → copied to docs; its top candidates feed C4b arms and the Mode B detector choice in C1/C2.
   DONE 18:35 (asserted gpt-6-astra): `WARMSTART_SURVEY_ASTRA_20261007.md`. Recogniser warm-start arms adopted: R01 el_PP-OCRv5_mobile
   (1.93M, official safetensors + PyTorch mapping), R02 PP-OCRv6_small (5.27M, 2026), R03 SVTRv2-T/OpenOCR (5.13M, native PyTorch);
   teachers only: Kalchas/Logios polytonic (8.0M, permissive) and CLLG Sept-2026 polytonic Greek (15.9M, NFD codec with all seven Greek
   marks, 794k aligned lines, CC-BY → attribution, not a deployable arm). Detector Mode-B candidates: PP-OCRv6_small_det (2.45M),
   PP-OCRv5_mobile_det (1.17M). Screening rule: one seed per arm first, three seeds for the best two. Parity proof before any swap:
   converted encoder reproduces native pre-softmax logits (max abs ≤1e-4) on short/long/blank/padded crops.
C5 Script-aware decoding as an ablation on the unified recogniser; tags never become oracle inputs at inference.

### Binding rule — synthetic data provenance (owner, 7 Oct 2026; applies from C0 onwards, no exceptions)
The generator of record is `linefactory` (`~/Projects/greek-page-ocr/factory`, Rust). All synthetic line and page data used for any
training, calibration or evaluation set is produced by it from a **committed recipe file**, and the recipe IS the predefined
distribution: `content_marginals` (script classes, incl. polytonic), `severity_weights`, `bg_weights`, `polarity_light_fraction`,
`fonts` (+ held-out), `lengths`, `crop`, `ink_transfer`, `exclusion_manifests`. The generator end already enforces this:
`audit.rs` hard-gates realised-vs-recipe marginals and `build.rs` writes `build_info.json` with `recipe_sha256`, the full recipe,
`audit_ok` and font hashes. What was missing is the consumer end, and that is what this rule adds:
P1 **No ad-hoc shard writers.** `o5_prepare.py`-style scripts stop writing training shards directly. Real crops enter through the
   factory's ingest path so they get the same schema, `script_class` and word tags, and appear in the same audit.
P2 **Every mix is a manifest.** A training/eval set is defined by `mix.json`: components = {factory build dir with `build_info.json`
   (synthetic) | real shard set with sha256 and source-partition id}, fraction per component, seed, codec version, recipe_sha256 per
   synthetic component. Training reads `mix.json` only; `--train-dir` on a loose directory is removed.
P3 **The trainer refuses unprovenanced data.** `train.py` (and the detector trainer) fail closed unless every synthetic component's
   `recipe_sha256` equals the sha256 of a recipe file that is **git-tracked at a committed revision** and `audit_ok` is true; the
   realised marginals of the assembled mix are recomputed from the rows and written next to the checkpoint (`data_provenance.json`).
P4 **Recipes are versioned, never edited in place.** A new distribution = `recipe.vN+1.json` + a one-paragraph change note in
   `docs/data_contracts.md`; the disclose-recipe-changes rule applies to every training launch (table recipe vs previous run).
P5 **Reviews check it.** Every checkpoint brief that gates training (CP-C1, CP-C4) lists P1–P4 as acceptance criteria; a run whose
   checkpoint lacks `data_provenance.json` is not reportable.
**STATUS 7 Oct 21:41: CP-C0 CERTIFIED (Sol c1 HOLD → 4 fixes → Astra c4 PASS under the stated threat model). Gate live on main.**
C0 gains two concrete items: C0.3 commit `recipe.v5.json` and the July factory sources (the recipe of record becomes v5 after its own
audit run); C0.4 implement P2–P3 (manifest + trainer gate) with tests, before C1. The O5 synthetic arm is grandfathered as a measured
experiment only; it is not a provenanced set and is not reused.

### Operating principle — the data environment (owner, 8 Oct 2026 13:50)
We are building a stochastic reward function from the verifications we can get and a stochastic estimate of the next best prediction; we
never have clear insight of the ground truth. Therefore: every label carries a tier and an error model (synthetic exact/off-distribution;
born-digital text layer near-exact; scan text layer + reader = two-OCR agreement with shared errors; owner spot checks = calibration tier);
admission is a weight or an abstain, not only a gate (hard gates only for known-wrong image–text pairs, e.g. geometry); provenance stays
binary; verifications are the reward signal and must be cheap, numerous and independent (ink checks, reader agreement, lexicon/edition
alignment, human checks); verified self-reads feed the next round; readouts report by tier and stratum with uncertainty.

### Track D — benchmark and verification
D1 Fix the O5 evaluation cache identity (device/dtype) and label the saved table as the CUDA evaluation (Sol HOLD F06).
D2 Benchmark redraw on the shared partition: human-verifiable site stays; machine adjudication is provisional and biased towards easy
   lines; Cyrillic needs real supply (one Word-error phrase dominates today); Live Text runner fixed for the Latin/English column.
D3 Every set ships with a gallery (crops, class, word tags) and a coverage denominator.

### Backbone v4 (owner, 8 Oct 2026 14:00) — supersedes the "Order of execution" below for everything after the running E2 sweep
(1) Diverse sources of data, properly annotated: parliament (S2 staged, extend toward ~200 documents), Internet Archive polytonic +
    Cyrillic, Anemi (image-only; wave 1 running), rendered web pages (O4e), born-digital OpenArchives; annotation from catalogue metadata
    (year, collection, document type), image features (contrast, ink coverage, background cast, stroke, curl, blur), a font estimate from
    the synthetic-trained classifier, text features (script, polytonic density, lexicon validity), and a small-model annotator (Luna) for
    text-level judgements; per-source distribution reports (toolkit T5).
(2) Find and fix the ground-truth problems: line geometry (G1 v3 judged by reference-free signals + owner blind A/B; G2 Kraken segmenter;
    geometry diagnostics as features), text-layer quality measured per source (agreement with CLLG; artefact classes such as '¬'); the
    verification stack (CLLG, Luna, lexicon/edition alignment, ink checks, owner spot checks as calibration) combined into a calibrated
    confidence per candidate reading. The text layer is NEVER a reference for any gate. Output: per-source quality report + calibration curve.
(3) Only then test the data mixes: E3 weighted, stratum-aware mixes (real share up to 0.75 of DISTINCT lines per epoch, per-stratum floors),
    synthetic recipe fitted to the real feature distributions, readouts by tier and stratum with uncertainty. The running E2 sweep stays as
    the warm-start baseline; no new sweeps before (1) and (2).

### Order of execution and first checkpoint
C0 → C1 (the executable plugin test) → A1 ∥ B1 → C2 → C3 → C4 → C5; B2 after B1; A2 after C2. First checkpoint = CP-C1: the vertical
slice runs on the frozen cohort from `Corpus.extract/ocr`, produces Docling markdown with the plugin's cells, and the test proves the
replacement boundary. Nothing trains before CP-C1 passes.

### H1 — Harvest real lines with the fast line finder + SOTA OCR labels (owner idea, 11 Oct; PROPOSAL, no go yet)
Owner: the page-line detector, though unfinished, may be good enough to cut real lines; pass the crops through SOTA OCR systems and
keep the labels as training ground truth for our recogniser. Caveats from the line-finding session (round-7 stack, commit 52cee3b,
prototypes/fast_lines/stack, docs/research/FAST_LINES_STACK.md): (1) 159 owner-marked two-line segments, 88 unfixed → crops with a
neighbour's descenders/accents or two whole lines; (2) curled edges truncate last words (s2-8686, 3229, 4959); (3) crops are polygon cuts,
not straightened; (4) faint front text sometimes dropped (no noise), ghost/show-through lines sometimes kept (garbage labels);
(5) tables fused/split; (6) drop caps dropped or split; (7) some ornaments/stamps still boxed; (8) orientation parked; (9) column and
rule boundaries good.
Proposed pipeline (pilot first): pages → stack@52cee3b (provenance on every line) → page gates (skip rotated pages, table pages, pages
where the bend scout fires; keep single-column/two-column body pages) → crop gates (height ≤ 1.5 × body pitch; not touching a curled
edge; not much taller than neighbours; inside a column band) → straighten + tight 0.2 x-height crop (G5) → readers: CLLG (local GPU,
free) + Google Document AI (R3; ~USD 1.5 per 1,000 calls; montage several crops per call with separators to cut cost 20–40×) + PDF text
layer where present as a weak third vote → labels: exact NFD agreement = tier 1; one-engine-only = tier 2 with confidence; engines
disagree / multi-line output / empty / low confidence = rejected; → per-line metadata (T5: length, x-height, faintness, inkiness,
contrast, column, page class) → records with weighted labels (stochastic-reward principle). Sources: Vouli (1,126 pages), parliament S2
(191 docs), Internet Archive (39 items) are public-domain scans and may go to an external API; Anemi (CC BY-NC-ND, internal) gets
CLLG + our readers only unless the owner authorises the external call. Compute: a CPU-only pod suffices for the stack (0.35 s/page);
CLLG needs the GPU pod (42 ms/line); the Mac does nothing but coordination. Pilot: 50 pages, review page of crops with both labels and
the gate decisions, owner checks by eye; then scale to the 250k-line target with the sampling rule above.

Owner (11 Oct): "source matters a lot; if it is mainly new polytonic lines you are looking for, some use unusual Greek chars that
not even Google might know about." Checked 11 Oct: our codec v1 (247 atoms) LACKS ϗ (kai abbreviation), ȣ (ou ligature), ϲ/Ϲ (lunate
sigma), ϐ ϑ ϰ ϱ ϖ (symbol variants), ϟ; it HAS ϛ ϝ ϙ ϡ, iota subscript, dialytika, numeral signs. CLLG's codec has ȣ ϛ ϲ ϝ ϙ ϡ but not
ϗ. The Anemi early prints (e.g. an-1436, 1815) use ϗ and ȣ on every page. Consequences (owner correction 11 Oct: Google MIGHT not know them; it is unknown until measured): whether Google
arbitrates those glyphs is a pilot measurement, not an assumption; if it does not, an agreement filter would silently drop exactly the
rare-glyph lines; the pilot must be stratified by source (Vouli 1850s / IA / Anemi
early prints) and tabulate per engine which characters it ever emits; lines with rare glyphs (per CLLG) get their own tier
("rare-glyph, CLLG-labelled, Google disagreement expected") and a visual review page rather than rejection; the codec policy (add
ϗ ȣ ϲ as classes vs map to κ/ου/σ,ς) is an owner decision before any such lines enter training (cf. the I9 lunate-sigma rule).

MEASURED 11 Oct 23:40 (T10 with Anemi included, owner go; 396 calls, USD 0.59): Google Document AI emitted NONE of ϗ ȣ ϛ ϲ Ϲ ϝ ϙ ϡ in
396 crops (160 Anemi early-print crops). On crops that visibly contain them it SUBSTITUTES look-alikes: the στ ligature (ϛ-shape) →
'ς' or 'σ' mid-word (an-3352…p29 mark4: printed χείριϛον → "χείριςον"; an-b9d6…p162 mark81: μάϛιγες → "μάσιγες"), the kai sign ϗ →
"κὶ" (same crop: ϗ ἐγὼ → "κὶ ἐγω"), with normal confidence — i.e. silent label errors on exactly those glyphs. Consequence: for early
prints Google is a weak vote on rare-glyph lines; CLLG (codec has ȣ ϛ ϲ ϝ ϙ ϡ, not ϗ) or a dedicated glyph pass must supply those
characters, and the agreement rule must treat Google's substitutes as expected disagreements, not as rejections. Anemi treatment
otherwise: 174 crops, 78 returned one line, 82 two to five lines, 5 empty (two-line crops dominate the catalogue sample).

Owner rule (12 Oct 00:05): a multi-line (list) return means the crop is likely tricky and the output unreliable. Calibration: 60 of 181
owner-verified single-line controls also returned 2–6 lines (Google fragments long/bent rows horizontally), so the list is a FLAG, not a
rejection. Harvest rule for list returns, from Google's per-line boxes: pieces side by side in one vertical band → one split line, join in
reading order and keep; pieces stacked in different vertical bands → genuine two-line crop or neighbour sliver, reject (or keep only the
piece on the crop's main row); any piece with garbage/foreign script (stamp lettering, Cyrillic ghosts) → drop the piece, and if it lies
inside the line the crop is obstructed and goes out. Single-line returns remain subject to the silent-failure filters (curl end, height).

T11 (12 Oct 00:35, owner "use the google model here"): Cloud Vision DOCUMENT_TEXT_DETECTION with hints el+grc on the same 469 crops
(396 calls, USD 0.59; report docs/harvest/VISION_VS_DOCAI_v1.md @ 72afb43; page [review artifact URL withheld from public evidence]).
Vision emits none of ϗ ȣ ϛ ϲ ϝ ϙ ϡ either, BUT expands the kai sign to "καὶ" (6 of the 8 crops where DocAI wrote "κὶ"), i.e. a
correct reading at the word level. Vision produces far fewer foreign-script garbage letters (Vouli 1 vs 11 crops, Anemi 0 vs 5), slightly
fewer diacritics per letter on Anemi (17.6 vs 21.4 per 100 letters), slightly lower symbol confidence (0.875 vs 0.928 Vouli), and more
fragments per crop. The two engines disagree strongly: strict NFD agreement on the 181 controls 2/181 (48/181 ignoring line breaks),
between-engine CER median 0.107 on Vouli and 0.298 on Anemi — so at least one is far from right on early prints; neither is a reference.
Next: a third independent reader (CLLG) on the same crops to triangulate, plus the owner's eye on the side-by-side page.

T12 (12 Oct 00:42, owner's Transkribus account, 101 credits of 200): public model "19th-century Greek 8.0" (148525) on all 469 crops.
Report docs/harvest/THREE_ENGINES_v1.md @ b07db74. Transkribus disagrees most with both Google engines (Anemi: DocAI–Vision 0.347,
DocAI–Transkribus 0.484, Vision–Transkribus 0.527; Vouli 0.175 / 0.296 / 0.296); three-way exact agreement is rare on these failure-case
crops (Anemi 21/174, Vouli 74/295 ignoring line breaks). Transkribus is the only engine emitting ϛ (1 crop) and it keeps the ligature
shape ("μάςιγες"), but by eye it garbles letters on early prints (χείριϛον → "χείξιζςεν", ὁπλιτῶν → "ὀπλίφων", ἐτάθη → "ἐφάβη"), so
the public model does not help on Anemi. By eye on the same crops Vision reads early prints best (ἀσπράδες, κατεντάρω, καὶ for ϗ),
Document AI second (it sits in the middle of the pairwise table, hence "best by agreement"), Transkribus last. Decision input: harvest
labels from Vision + Document AI (two models, one vendor) + CLLG; start with the easier books (Vouli/parliament) per the owner; Anemi
lines only where two readers agree or via the rare-glyph tier. Owner's eye on ~10 Anemi cards of the three-engine page still wanted.

OWNER DECISION 12 Oct 01:00 (after viewing the three-engine page): "it's not very good, the google models are better" → Transkribus dropped as a
harvest reader; readers = Cloud Vision + Document AI (+ CLLG as the independent third / rare-glyph supplier).

### Line supply for E2 (owner, 10 Oct, relayed): the page-line detector is basically done
Owner: "line recognizer [the page-line detector] is basically done; they can figure out sampling strategies to see if the lines are
what they need: they should be careful about (a) line length to get good lines, and (b) per char faintness so that the chars are
actually readable." Consequence for E2 real-line supply: sample training/eval lines from the page-line output by line length
(prefer full-width lines; short fragments only as a labelled stratum) and by per-character faintness/readability (the toolkit's
readability profile + calibrated CLLG limits), not by text-layer agreement alone; record both as line metadata (T5) so mixes can
be stratified on them. Fast line finding research (charter 10 Oct) runs separately; coordinator's dreams in
greek-ocr-toolkit-astra-lines4/.astra/fast_lines/dreams_coordinator.md.

### Line-set repair before recognition — Mode A+ (owner, 8–9 Oct 2026 ~00:00; from the glyphs/geometry session handoff)
KEY FINDING: the pipeline's LINE SET is the problem, not only the crop geometry. C1 plugin Mode A re-reads the PDF's native textline
cells (all 107 Vouli PDFs: Producer InDigital / InVision OCR 1.0.1), and the plugin's detector mode is a stub
(greekocr/deploy/docling_plugin/model.py:115 reason="no_textlayer_lines"). Consequences: (a) every printed line InVision did not
segment, or merged across columns/rows, is never seen by our recogniser; (b) scans with no text layer (all Anemi pages) get no lines.
Vouli p00001: 71 InVision segments for ~120 printed lines (many boxes span both columns; ~14 lines have no box). Text-layer boxes
overlap neighbours in 79% of 20,496 adjacent pairs (median 13% of box height).
NEXT STEP (owner agreed in principle): repair the line set before recognition with the owner's page-lines procedure
(greek-ocr-toolkit docs/PAGE_LINES_ALGORITHM.md, 7 steps): find every line from pixels starting from the segments; split segments
holding two columns/rows; add lines with no segment; dedupe; hand the complete set to Docling as our cells (Mode A+). The same
procedure from a simple segmenter (scripts/glyphs/segment_page_lines.py) or a small detector = the detector mode for scans.
FIRST MEASUREMENT: on the six Vouli review pages, count printed lines with no segment and segments holding >1 line; then a
before/after page. Switch the review from our extractor's boxes (bench/o4b_textlayer_lines grouping) to Docling's own native cells
(what the plugin actually sees).
Owner decisions: table STRUCTURE is Docling's job; ours is only that lines never cross vertical rules / wide gaps (step 7) and that
tiny segments borrow geometry from neighbours (shared geometry). Owner review material: artifacts C8cT9HrvLJc7PdZ7ghoDnJ (12 pages,
per-segment ratings) and SffUsxC7hEwWiaCP5fCGoY (Vouli p00001); notes in toolkit docs/reviews/OWNER_PAGE_REVIEW_NOTES.md.
Code state (toolkit main 89dd3bd): curl fix (Astra, a4a1421; end curls only), line_glyphs(focus), regression set of the owner's first
40 crops (tests/glyphs/test_initial_batches.py), fix_page + page_lines.py first versions; CP-G4 (Astra) still HOLD (F2/F3 superseded).
Relation to E2: the sweep's real-line supply and the Vouli test both come from InVision boxes; E2 relaunch should wait for the Mode A+
line set or run explicitly as the 'InVision-box control'.

### Open problems (owner-registered)
- O4d line geometry on bound scans (8 Oct): curled baselines, two-line boxes, edge clipping, dropped hyphens; test arms G1/G2/G3/H1 above.
