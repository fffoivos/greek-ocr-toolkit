# O4b — real scan-line supply, offline implementation (7 October 2026)

Code is implemented; external acquisition and worker OCR remain coordinator work.
No network, training, new external dataset admission, or `.git` mutation was performed.
`O4b_HANDOFF.json` records edited files, tests and outstanding evidence. Existing
unrelated untracked files were left alone. `sources: 3` means S1/S2/S3 implemented,
not three downloaded or release-qualified datasets.

The E1 run4 pain map motivates this supply: 104 real polytonic train lines,
11 Cyrillic, 20–70% polytonic mark errors, 12–27% Cyrillic CER, and the all-real
arm's failure on unseen fonts. S1 offers the cheapest existing pairs; S2 broadens
historical type/editions; S3 retains human page transcriptions without relying on
O4a's width/paragraph reflow (59 admitted lines in the cited 85-minute run).

## Custody, labels and partitions

All source tools emit JSONL plus crop PNGs, rejected inventories and receipts.
They never write training shards. Every admitted line carries `label_tier`,
`licence` (also factory spelling `license`), `source_dataset`, `source_doc_id`,
`line_id`, `crop_path`, NFC `text`, codec version, crop hash, source/rights evidence
and a document split. Native source IDs and raw labels remain available.
NFC and whitespace normalization preserve diacritics and case. Encoding eligibility
uses **the frozen Rust codec-v1 inventory and enumerated folds**, not codec v2.
Unknown atoms reject the whole line and have per-codepoint occurrence counts;
no replacement/UNK. Serbian Ђ/Ј/Љ/Њ/Ћ/Џ and pre-reform Russian letters may sharply
reduce supply under v1; Bulgarian/Ukrainian/Serbian quotas cannot be assumed.
Script/word tagging follows factory `corpus::classify`; factory writes word tags.

`bench.o4b_partition` combines the authoritative O5 `document_assignment.reserved`
and C1 cohort into a reviewed exclusion manifest. A canonical **work** mapping
must group mirrors, serial volumes, alternate editions and all pages of a book,
including overlaps across S1/S2/S3. Source-native document IDs cannot be inferred
from line filenames. Missing identities, missing/empty O5 or C1 exclusions and
unreviewed rights fail closed. Book hashes also block known C1/O5 bytes when supplied.
Review remains essential for different scans of the same work; hashes cannot
detect them. C1's entire cohort is excluded, irrespective of its train/test role.

Split: `sha256(seed/canonical-work) mod 1000`, seed `20261007`; <900 train,
900–949 val, >=950 reserved. Excluded works have zero admitted lines. Reserved
is never trainable; this is a source-document partition, separate from the
synthetic text-band rule. No legacy evaluation data is promoted into training
or used to calibrate a new gate. `legacy_eval` remains disclosed evaluation-only.

`linefactory import-real` retains the frozen Parquet schema. Its quality metadata
and licence/source identity survive in `word_tags.jsonl`; `build_info.json` records
the sidecar hash and tier counts. Source JSONL remains the evidence of record.
The importer still reports appearance/length issues rather than silently removing
real crops. `gold_aligned` and `silver_agreed` describe machine evidence, not a human seal.

## S1 — published pairs

| Source | Evidence read locally | Intended tier | Expected gross supply / unresolved items |
|---|---|---|---|
| Polyton-DB, via [Kalchas](https://github.com/kperi/Kalchas) | Astra R08; [Logios, r17](https://arxiv.org/abs/2506.21474) | gold only with release ground-truth evidence; otherwise silver | Thousands of polytonic lines. The reported extra 6,796 lines are not a verified downloadable pair count. Native files, book IDs and data licence need review. Apache-2.0 is established for the code/model survey, not blanket scan permission. |
| GRPOLY-DB | [Gatos et al., r16](https://www.cs.uoi.gr/~sfikas/2015GatosICDAR.pdf); local literature review | gold for manually transcribed printed subset | MachinePrinted-B has 33 pages and 2,835 recognition lines in cropped blocks. Do not mix its handwriting task into printed OCR. Dataset download endpoint, segmentation/label format and redistribution rights remain unverified. |
| CLLG, [Zenodo 22232579](https://zenodo.org/records/22232579) | Astra R23, September 2026 | silver aligned corpus; human-reviewed test subset only can be gold | 794,564 Greek/Latin aligned training lines reported. User identifies CC-BY; survey explicitly verifies CC-BY-4.0 **weights**. Check that released files include images/annotations and that corpus lineage has the same rights. Record authors, title, version, DOI and scan attribution. A weights-only release supplies zero pairs. |

[Patrologia Graeca, r18](https://arxiv.org/html/2603.09470v1) reports specialised
adaptation (445 annotated images, 30 manually transcribed Greek test pages) and
a larger silver corpus. It is contextual evidence, not a fourth silently admitted
source. Keep its mixed Greek/Latin scope and Unicode-sensitive scores explicit.

`scripts/fetch/o4b_datasets.sh discover` snapshots Kalchas HEAD/tree/code licence,
immutable README/licence files and Zenodo metadata/file checksums. The reviewed
download manifest supplies exact URLs, licences and pinned SHA-256 or publisher
MD5 (a local SHA-256 is always recorded). Tar/ZIP path escapes, links and special
files reject. Existing downloads resume only after checksum verification.
GRPOLY's reviewed endpoint is supplied explicitly; there is no invented URL.

Native adapters: `.gt.txt`/image pairs (or explicit `.txt` suffix), column-mapped
TSV line manifests with optional page rectangles, PAGE XML polygons/text,
ALTO pixel rectangles/explicit spaces, OCR LMDB `image-N/label-N/num-samples`,
and Kraken Arrow IPC binary-image/text columns. PAGE requires one reviewed
line-level TextEquiv; polygons mask neighbouring ink. Arrow/LMDB require a
line-to-book map. Native format support is fixture-tested; **actual upstream
payload schemas were not inspectable offline**. The example manifests are inert
and must be adapted to inventoried release files. No assertion that all three
sources natively use the example formats.

Planning yields (not measured): Polyton thousands; GRPOLY up to 2,835 before
codec/geometry/identity filtering; CLLG 0 if unavailable, otherwise up to the
reported 794,564 before filtering. Every run reports actual admitted/rejected
counts, classes, tiers and documents. No duplication to meet a yield target.

## S2 — text-layer books

`data/sources/o4b_archive_ids.txt` is TSV with 30 Greek and 30 Cyrillic proposals
(Russian 12, Ukrainian 6, Bulgarian 6, Serbian 6). **These are proposed IA slugs,
not verified accessions.** No online lookup was possible. Every row is `verified=no`,
`licence=pending`; none can download in the normal fetch mode. Inventory mode
queries IA metadata and, for missing slugs, records search-query alternatives.
Coordinator chooses the actual identifier and searchable derivative, verifies
the edition/PD or licence evidence, records attribution, and marks `verified=yes`.
The exact chosen filename is compulsory and IA's MD5 is checked. A metadata
public-domain claim is evidence for review, not an automatic licence grant.
The candidate tables below describe bibliographic targets; all edition/scan/layer
rights remain pending. The 1800–1930 window targets 19th/early-20th-century print;
old underlying authors alone do not establish rights in an edition or scan.

`bench.o4b_textlayer_lines` reuses O1 `native_rows`, PDFium character boxes,
column/baseline assembly and ink ownership guards at 200 dpi. Layer text starts
as `silver_ocr_layer`; raw layer labels and all geometric rejects remain in
`all.jsonl`. Textless PDFs have explicit page failures. Reviewed Anemi PDFs work
through the same book manifest (`source_dataset=anemi`, stable accession ID,
edition/scan/text-layer rights evidence); no Anemi accession is invented here.
DjVuLibre `djvutoxml`/`ddjvu` are optional worker tools. DjVu supports real
CHAR/CHARACTER geometry; common WORD-only layers are reported as
`djvu_no_character_boxes`. It never synthesizes char boxes. Prefer an IA
searchable PDF derivative when DjVu has word geometry only.

`bench.o4b_adjudicate` rereads **every crop in all.jsonl** blind with E1 and, when
available for its script, Kalchas. Exact NFC/whitespace-normalized equality
with layer text is necessary for `silver_agreed`; different breathing/accent
marks still disagree. Geometric rejects never become admitted through agreement.
Missing teachers, failures, unsupported scripts or disagreement are `flagged`.
Kalchas alone is not a Cyrillic teacher: with E1 only, Cyrillic stays flagged.
The same offline adapter interface permits a separately reviewed independent
Cyrillic teacher, with supported scripts and model hash recorded.

Teacher interface: local `module:factory(model_path)` returns `reader(crop_path)`;
native Kalchas inference may be wrapped without changing its preprocessing.
The supplied `bench.o4b_teacher:load` handles a parity-verified ONNX export plus
`model.onnx.json` containing `model_sha256`, `parity_verified:true`,
`parity_evidence`, `height`, `width`, `mean`, `std`, optional
`binarize_threshold`, `layout` (BTC/TBC/TC), `input_name`, `output_name`, `atoms`
(native ordered strings, blank index 0). Inspect native Kalchas before filling
this configuration; the survey's 80×760 resize/binarisation is insufficient to
guess tensor names, normalisation, token order or export parity. The factory
receives the exact pinned model path and the config hash survives in the receipt.

Scenario yield: 30 candidates/script × 100–250 useful pages × 20–35 lines =
60k–262.5k gross lines/script if all books resolve. Assuming half have usable
layers gives 30k–131k before codec/geometry checks. Agreement retention is unknown;
do not promise it, particularly for Cyrillic with no independent teacher. Serial
volumes and alternate editions reduce the number of independent work groups.

## S3 — fast acquisition, DBNet and CTC alignment

`bench/source_wikisource.py --fast-plan` uses explicit reviewed proofread-page
plans. Page revisions and explicit Index queries batch in <=50 titles; allpages
discovery already batches revisions. Media bodies download with 1–8 bounded
threads (default 4). One shared start limiter covers APIs/media at >=1 second;
per-URL locks deduplicate concurrent requests and serialize cache writes.
Downloads overlap without increasing request starts. PDF/DjVu thumbnails avoid
PDFium in threads. Resume verifies page-image hashes and immutable plan/code/
resolution bindings. Old O4a entrypoints and cache replay remain supported.
Quality levels 3/4, scan PD metadata and transcription rights are required.
Record physical page width or usable DPI metadata; unknown/below-200 resolution
remains a blocker. Fast acquisition itself admits **zero lines**.

Line detection uses the existing **local docTR DBNet `db_mobilenet_v3_large`**
checkpoint with two-pass detection, ink gating and DT8 reading order.
`onnxruntime` is installed here; `rapidocr` is absent and no PP-OCRv5 detector
weights were identified, so no RapidOCR fallback/download is claimed. Detector
and E1 paths are explicit worker arguments. They are never loaded in fixture tests.

`bench.o4b_align` concatenates line CTC logits in detector reading order, inserts
virtual blank/space boundary frames and Viterbi-aligns the full page transcription.
The CTC topology handles repeated characters correctly. Every atom must be
consumed; letters cannot cross line boundaries; every box must get text; joined
line labels must reconstruct page text exactly. Unknown atoms, malformed markup,
printed references, failed alignment, uncalibrated scripts and memory-budget
overflow are flagged. There is no projection/length heuristic fallback. Greedy E1
text must also equal each aligned label. Confidence is minimum atom emission
confidence, not a calibrated probability of truth.

Calibration uses document-balanced **S1 gold val only**, >=3 documents per
stratum, >=100 positive and >=100 different-document similar-length negative
pairs (default cap 1,000 lines/class). Threshold is just above the highest
negative confidence and must retain positives. Zero observed false accepts needs
a 95% binomial upper bound <=3%, conditional on independent pairs. Shuffled
negatives are artificial; document correlation, detector omissions and natural
page alignment errors still need manual audit. Thresholds bind exact E1/codec/
adapter/alignment code hashes; absent Cyrillic gold calibration flags Cyrillic.
**No production threshold was calibrated here: S1 payloads and E1 weights are
not available in this sandbox.** Tests prove the calibration logic and admission
gate on offline fixtures; they do not measure source precision or live speed.

Expected speed: 50 page revisions/request instead of one/title; up to four slow
media bodies overlap at unchanged polite request rate. Real throughput depends
on thumbnail availability, retry/DPI rates and worker inference. Conditional
yield: 100 usable pages/work × 20–35 lines gives 2k–3.5k candidates/work. Measure
actual `gold_aligned` yield and manual alignment error before mixing into E2.

## Exact coordinator commands (network/processing worker only)

Set paths on the worker; E1 must be the selected, codec-bound **weights-only**
checkpoint (safetensors/native serving export), not an arbitrary unpickled resume
file. Select the polytonic/font-OOD teacher using E1's per-stratum report; the
all-real arm is inappropriate for these weak/OOD strata. Record the selected
checkpoint identity in the run evidence. This handoff does not pick a missing
checkpoint by filename.

```bash
cd /path/to/greek-page-ocr
export PYTHON=/path/to/worker/venv/bin/python
export RAW_ROOT=data/raw
RUN=out/o4b_worker
mkdir -p "$RUN"
E1=/path/to/selected_e1/best.safetensors
DET=/path/to/local_dbnet/best.pt
KALCHAS=/path/to/parity_verified_kalchas/model.onnx
```

Discover/review metadata, then copy/edit the inert examples to real, reviewed
manifests. Preserve download/rights snapshots and native document mappings.

```bash
scripts/fetch/o4b_datasets.sh discover --out "$RUN/dataset_inventory"
scripts/fetch/o4b_archive.sh data/sources/o4b_archive_ids.txt --inventory-only
# Review inventory, resolve proposals, fill licence/attribution/evidence/filename;
# set verified=yes only for chosen archive rows in o4b_archive_reviewed.txt.
scripts/fetch/o4b_archive.sh data/sources/o4b_archive_reviewed.txt
# o4b_downloads.reviewed.json contains pinned URLs/checksums and reviewed rights.
scripts/fetch/o4b_datasets.sh datasets --manifest data/sources/o4b_downloads.reviewed.json --out data/raw/o4b_datasets
```

Build the work map from the actual dataset/native books/Wikisource editions,
including O5/C1 aliases. C1 JSONL rows need `doc` or `source_doc_id`, optionally
book `pdf_sha256`/`document_sha256`; JSON can instead contain `documents`.
`o4b_work_map.reviewed.json` is `{ "documents": { "native-doc": "canonical-work", ... } }`.

```bash
"$PYTHON" -m bench.o4b_partition --o5-info out/o5_node_20261007/build_info.json \
  --c1 /path/to/frozen_c1_cohort.jsonl --document-map data/sources/o4b_work_map.reviewed.json \
  --reviewed --out "$RUN/partition.json"
"$PYTHON" -m bench.o4b_import_datasets --manifest data/sources/o4b_datasets.reviewed.json \
  --partition "$RUN/partition.json" --out "$RUN/s1"
# S2 books manifest can be assembled from verified archive source.json files;
# include reviewed Anemi files explicitly if available.
"$PYTHON" -m bench.o4b_textlayer_lines --sources data/sources/o4b_books.reviewed.json \
  --partition "$RUN/partition.json" --out "$RUN/s2"
"$PYTHON" -m bench.o4b_adjudicate --records "$RUN/s2/all.jsonl" --out "$RUN/s2_agreed" \
  --e1 "$E1" --codec codec/v1.json --device cuda \
  --kalchas bench.o4b_teacher:load --kalchas-model "$KALCHAS"
```

Without Kalchas, omit both teacher arguments; all affected crops remain flagged.
For an independent Cyrillic export, run a separate adjudication with its model
and `--kalchas-scripts cyrillic` (the field name is historical; record true model
identity). Keep each teacher's records/receipt, and deduplicate line IDs when
combining agreed subsets. Do not import `s2/all.jsonl` as agreed supervision.

```bash
# Reuse existing O4a discovery snapshots, or refresh discovery on the coordinator:
"$PYTHON" -m bench.source_wikisource --scale --discover-only --out "$RUN/ws_discovery"
# rights-review.json maps work_id to reviewed licence/source/attribution/evidence;
# it may additionally attest page_width_inches for the exact edition.
"$PYTHON" -m bench.o4b_wikisource --discoveries "$RUN/ws_discovery/el/discovery.json" \
  "$RUN/ws_discovery/ru/discovery.json" "$RUN/ws_discovery/uk/discovery.json" \
  "$RUN/ws_discovery/bg/discovery.json" "$RUN/ws_discovery/sr/discovery.json" \
  --rights-review data/sources/o4b_wikisource_rights.reviewed.json --out "$RUN/ws_plan.json"
"$PYTHON" -m bench.source_wikisource --fast-plan "$RUN/ws_plan.json" --download-workers 4 \
  --request-interval 1 --user-agent 'GreekPageOCR-O4b/1.0 (coordinator contact: REPLACE)' \
  --out "$RUN/ws_pages"
# Repeat the preceding command unchanged to resume; add --offline for cache-only use.
"$PYTHON" -m bench.o4b_align calibrate --records "$RUN/s1/records.jsonl" \
  --e1 "$E1" --codec codec/v1.json --device cuda --out "$RUN/ctc_calibration.json"
"$PYTHON" -m bench.o4b_align align --pages "$RUN/ws_pages/pages.jsonl" --partition "$RUN/partition.json" \
  --e1 "$E1" --codec codec/v1.json --device cuda --detector "$DET" \
  --calibration "$RUN/ctc_calibration.json" --out "$RUN/s3"
```

A new discovery may add work identities: update/review the work map before any
source conversion, freeze the resulting partition, and use fresh outputs.
Never change identities under existing admitted records. Copy the same partition
manifest across sources, including its seed/hash.

Factory import is the only shard-writing step. Use a newly built importer so
quality sidecars are retained; do not use an old binary. Inspect per-source
rejection/atom counts and manually audit aligned/agreed samples before E2.
No training command is part of O4b.

```bash
cargo build --locked --release --manifest-path factory/Cargo.toml
for SOURCE in s1 s2_agreed s3; do
  factory/target/release/linefactory import-real --records "$RUN/$SOURCE/records.jsonl" \
    --crops "$RUN" --out "$RUN/import_$SOURCE" --partition o4b-documents-v1
done
```

The coordinator must commit/review code separately before P3 training receipts
are established. This implementer leaves edits and never writes `.git`.

## Offline validation

New tests cover native pair/TSV/PAGE/ALTO conversion, rights failures, document
and byte exclusions, NFC and unknown atom counts, blind teacher agreement,
missing/ineligible teachers, O1 PDF extraction, full S2 crop accounting, CTC
repeats/impossible paths/page reconstruction, calibration refusal/binding,
fast-page resume, batch limits, concurrent cache writers, overlapping bodies with
polite starts, download checksums/resume, safe archives and teacher parity gates.
Factory tests verify actual crop/shard round trips and persistent quality/licence
sidecars without changing the shard schema.

```bash
.venv/bin/python -m pytest bench/tests/test_o4b.py \
  bench/tests/test_source_wikisource.py bench/tests/test_source_wikisource_scale.py -q
CARGO_HOME=/private/tmp/o4b-cargo-home cargo test --offline --manifest-path factory/Cargo.toml import_real -- --nocapture
bash -n scripts/fetch/o4b_datasets.sh scripts/fetch/o4b_archive.sh
```

The existing PDF fixture test now uses the already-required PDFium writer instead
of missing optional `pypdf`. Cargo's normal cache path was read-only; a temporary
Cargo home used symlinks to existing cached sources/index/crate blobs and unpacked
missing cached crates only under `/private/tmp`. No network or dependency install.
Executed test counts are in the handoff; no fixture result is a production OCR,
native upstream payload, live-speed, licence or human-precision validation.

## Candidate identifier tables (all unverified)

### Greek — 30 proposed identifiers

| Identifier (unverified) | Language | Intended edition/type | Proposed rights status |
|---|---|---|---|
| `homeriilias01home` | el | Homer, Iliad, Greek critical edition | PD candidate; verify 1800–1930 edition, scan and layer |
| `homeriilias02home` | el | Homer, Iliad, alternate type and commentary | PD candidate; verify 1800–1930 edition, scan and layer |
| `homeriodyssea01home` | el | Homer, Odyssey, Greek critical edition | PD candidate; verify 1800–1930 edition, scan and layer |
| `homeriodyssea02home` | el | Homer, Odyssey, commentary and apparatus | PD candidate; verify 1800–1930 edition, scan and layer |
| `hesiodicarmina00hesi` | el | Hesiod, Carmina, 1908 family | PD candidate; verify 1800–1930 edition, scan and layer |
| `pindaricarmina00pind` | el | Pindar, Carmina | PD candidate; verify 1800–1930 edition, scan and layer |
| `aeschylitragoed00aesc` | el | Aeschylus, Greek tragedies | PD candidate; verify 1800–1930 edition, scan and layer |
| `sophoclistragoed00soph` | el | Sophocles, Greek tragedies | PD candidate; verify 1800–1930 edition, scan and layer |
| `euripidistragoed01euri` | el | Euripides, Greek tragedies | PD candidate; verify 1800–1930 edition, scan and layer |
| `aristophaniscomo01aris` | el | Aristophanes, Greek comedies | PD candidate; verify 1800–1930 edition, scan and layer |
| `herodotihistoria01hero` | el | Herodotus, Histories | PD candidate; verify 1800–1930 edition, scan and layer |
| `thucydidishistor01thuc` | el | Thucydides, Histories | PD candidate; verify 1800–1930 edition, scan and layer |
| `xenophontisanab00xeno` | el | Xenophon, Anabasis | PD candidate; verify 1800–1930 edition, scan and layer |
| `xenophontishell00xeno` | el | Xenophon, Hellenica | PD candidate; verify 1800–1930 edition, scan and layer |
| `platonisopera01plat` | el | Plato, Greek Opera | PD candidate; verify 1800–1930 edition, scan and layer |
| `aristotelisopera01aris` | el | Aristotle, Greek Opera | PD candidate; verify 1800–1930 edition, scan and layer |
| `demosthenisora01demo` | el | Demosthenes, Greek speeches | PD candidate; verify 1800–1930 edition, scan and layer |
| `isocratisopera00isoc` | el | Isocrates, Greek Opera | PD candidate; verify 1800–1930 edition, scan and layer |
| `plutarchivitae01plut` | el | Plutarch, Greek Lives | PD candidate; verify 1800–1930 edition, scan and layer |
| `lucianiopera01luci` | el | Lucian, Greek Opera | PD candidate; verify 1800–1930 edition, scan and layer |
| `geographicastra01stra` | el | Strabo, Greek Geography | PD candidate; verify 1800–1930 edition, scan and layer |
| `pausaniaegraeci01paus` | el | Pausanias, Greek Description of Greece | PD candidate; verify 1800–1930 edition, scan and layer |
| `theocritusmosch00theo` | el | Theocritus, Greek idylls | PD candidate; verify 1800–1930 edition, scan and layer |
| `anthologiagraec01anth` | el | Greek Anthology | PD candidate; verify 1800–1930 edition, scan and layer |
| `dionysiihalica01dion` | el | Dionysius of Halicarnassus, Greek | PD candidate; verify 1800–1930 edition, scan and layer |
| `hellenikabible00bibl` | el | Greek Bible, historical edition | PD candidate; verify 1800–1930 edition, scan and layer |
| `athidesaurai00pala` | el | Palamas, Athides Aurai, 1889 family | PD candidate; verify 1800–1930 edition, scan and layer |
| `poiemata00solo` | el | Solomos, Greek poems, historical edition | PD candidate; verify 1800–1930 edition, scan and layer |
| `poiemata00vala` | el | Valaoritis, Greek poems, historical edition | PD candidate; verify 1800–1930 edition, scan and layer |
| `diegemata00vizy` | el | Vizyinos, Greek stories, 19th-century printing | PD candidate; verify 1800–1930 edition, scan and layer |

### Cyrillic — 30 proposed identifiers

| Identifier (unverified) | Language | Intended edition/type | Proposed rights status |
|---|---|---|---|
| `voinaimir01tols` | ru | Tolstoy, War and Peace, pre-reform Russian | PD candidate; verify 1800–1930 edition, scan and layer |
| `voinaimir02tols` | ru | Tolstoy, War and Peace, alternate volume/type | PD candidate; verify 1800–1930 edition, scan and layer |
| `annakarenina01tols` | ru | Tolstoy, Anna Karenina | PD candidate; verify 1800–1930 edition, scan and layer |
| `prestuplenienak00dost` | ru | Dostoevsky, Crime and Punishment | PD candidate; verify 1800–1930 edition, scan and layer |
| `bratiakaramazo01dost` | ru | Dostoevsky, Brothers Karamazov | PD candidate; verify 1800–1930 edition, scan and layer |
| `idiot01dost` | ru | Dostoevsky, The Idiot | PD candidate; verify 1800–1930 edition, scan and layer |
| `mertvyedushi00gogo` | ru | Gogol, Dead Souls | PD candidate; verify 1800–1930 edition, scan and layer |
| `vecheranakhuto00gogo` | ru | Gogol, Evenings near Dikanka | PD candidate; verify 1800–1930 edition, scan and layer |
| `evgeniioniegin00push` | ru | Pushkin, Eugene Onegin | PD candidate; verify 1800–1930 edition, scan and layer |
| `polnoesobranie01push` | ru | Pushkin, Collected Works | PD candidate; verify 1800–1930 edition, scan and layer |
| `ottsyideti00turg` | ru | Turgenev, Fathers and Sons | PD candidate; verify 1800–1930 edition, scan and layer |
| `geroinashegovr00lerm` | ru | Lermontov, Hero of Our Time | PD candidate; verify 1800–1930 edition, scan and layer |
| `kobzar00shev` | uk | Shevchenko, Kobzar | PD candidate; verify 1800–1930 edition, scan and layer |
| `kobzar01shev` | uk | Shevchenko, Kobzar, alternate historical edition | PD candidate; verify 1800–1930 edition, scan and layer |
| `eneida00kotl` | uk | Kotliarevsky, Eneida | PD candidate; verify 1800–1930 edition, scan and layer |
| `chornaradaroma00kuli` | uk | Kulish, Chorna Rada | PD candidate; verify 1800–1930 edition, scan and layer |
| `zvershyninyzyn00fran` | uk | Franko, Z vershyn i nyzyn | PD candidate; verify 1800–1930 edition, scan and layer |
| `lisovapisnia00ukra` | uk | Lesia Ukrainka, Lisova pisnia | PD candidate; verify 1800–1930 edition, scan and layer |
| `podigoto00vazo` | bg | Vazov, Pod igoto | PD candidate; verify 1800–1930 edition, scan and layer |
| `epopeianazabr00vazo` | bg | Vazov, Epopeya na zabravenite | PD candidate; verify 1800–1930 edition, scan and layer |
| `baiganiu00kons` | bg | Aleko Konstantinov, Bay Ganyo | PD candidate; verify 1800–1930 edition, scan and layer |
| `stihotvoreniia00bote` | bg | Hristo Botev, poems | PD candidate; verify 1800–1930 edition, scan and layer |
| `nedelnik00sofr` | bg | Sophronius, Nedelnik, later historical edition | PD candidate; verify 1800–1930 edition, scan and layer |
| `ribniibukvar00bero` | bg | Petar Beron, Riben bukvar | PD candidate; verify 1800–1930 edition, scan and layer |
| `gorskivijenac00njeg` | sr | Njegos, Gorski vijenac | PD candidate; verify 1800–1930 edition, scan and layer |
| `lucamikrokozma00njeg` | sr | Njegos, Luca mikrokozma | PD candidate; verify 1800–1930 edition, scan and layer |
| `srpskinarodnip01kara` | sr | Vuk Karadzic, Serbian folk songs | PD candidate; verify 1800–1930 edition, scan and layer |
| `srpskinarodnep00kara` | sr | Vuk Karadzic, Serbian folk tales | PD candidate; verify 1800–1930 edition, scan and layer |
| `pesme00radi` | sr | Branko Radicevic, Serbian poems | PD candidate; verify 1800–1930 edition, scan and layer |
| `pesme00zmaj` | sr | Jovan Jovanovic Zmaj, Serbian poems | PD candidate; verify 1800–1930 edition, scan and layer |

