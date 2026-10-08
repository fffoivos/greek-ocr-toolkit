# T1 — greek-ocr-toolkit: one private repo, high-level APIs, tests (gpt-6.1-sol, xhigh). Workspace = this repo (empty, git-initialised).
No `.git` writes (the coordinator commits). No network except `pip`/`uv` for the venv. No GPU. Do not modify any other repo.

Owner mandate (8 Oct 2026): "create a new private repo with all the tools we use including synthetic lines + how to get real lines,
any annotators, all the deployments you learned how to do, organized in high-level APIs with tests; set this as the standard moving
forward." Phase 1 (this job) = vendor + wrap + test; NO behaviour changes to vendored logic (byte-identical functions where possible,
import paths rewritten). Record every vendored file's origin path + commit in `docs/INVENTORY.md`.

Sources to read and vendor (read-only; absolute paths):
- Synthetic lines: `~/Projects/greek-page-ocr/factory/` (Rust linefactory; recipes `factory/recipe.v5.json`, `v7`, `v8`; `factory/src/import_real.rs`,
  `custody.rs`), `~/Projects/greek-page-ocr/train/mix.py` + `train/mix.schema.json` (mix manifests, provenance rule: recipe sha256 = the
  distribution; trainer fails closed), `docs/ocr_program_2026-10-06/data_contracts.md`. The Rust stays where it is for now: wrap it
  (`greekocr.synth`: recipe registry with sha256, `build_shards(recipe, binary, out)`, `build_mix(...)`, `verify_recipe_sha(...)`).
- Real lines: `bench/o4b_textlayer_lines.py` (text-layer line extraction from PDFs), `bench/o4b_adjudicate.py` (two-reader adjudication →
  admitted/flagged tiers), `bench/o4b_common.py` (Partition, resolve_exclusions, canonical works), `bench/o4b_import_datasets.py`
  (Polyton-DB / GRPOLY importers, BOM strip, image_suffix), `bench/o4b_partition.py`, `scripts/fetch/parliament_pdf_cache.py`,
  `seed/node_scripts/fetch_parliament_s2.py` (ranked candidate staging with md5/sha receipts), `scripts/fetch/o4c_*.py` (discovery crawls:
  parliament API, Internet Archive, Anemi authenticated client, wikimedia; rate state, transfer ledger), `scripts/fetch/o4b_*.sh`.
- Annotators: `bench/line_categories.py` (rule-based line category / script tagger), word tags (`bench/e1_*` → `real/word_tags.jsonl` producer;
  find it), per-line script-class rules in the factory recipes.
- Readers / teachers: `bench/e2_teachers.py` (Kalchas native adapter incl. the MPS→cpu map_location, CLLG kraken-native adapter, service
  stubs), `bench/e2_native.py` (persistent CLLG `--serve` worker client; Paddle R01 native reference; R03), `scripts/fetch/r2_cllg_worker.py`,
  `scripts/fetch/r2_cllg_env.sh`, `bench/e2_cllg_contract.py`, `bench/e2_reader_parity.py`, our own recogniser inference (`bench/e1_*` eval
  reader / `train/model.py` loader).
- Scoring: the bake-off scorer in `bench/e2_bakeoff.py` (strict NFD CER, mark precision/recall/F1 per diacritic, Greek→Latin homoglyphs),
  `bench/e1_*` evaluation summaries (by_category readouts).
- Warm-start: `bench/e2_warmstart.py` (R01/R03 converters), `bench/e2_models.py` (donor modules + `preprocess` incl. `paddle_dynamic`
  pad rule), `bench/e2_parity.py` (scale-normalised parity gate), `docs/ocr_program_2026-10-06/R01_native_preprocess_review.md`.
- Deployment: Docling OCR plugin `~/Projects/glossapi-development/src/glossapi/ocr/plugin/` (options/model/docling_plugin/recognizer; entry
  point `docling` kind `glossapi`), tests `tests/test_docling_plugin_c1.py`; node environment recipes (from `seed/node_scripts/*.sh` and
  `docs/ocr_program_2026-10-06/E2_NOTES.md`): venvs `ocr` (torch cu126, safetensors 0.7 pinned for kraken 7.1.1 conflicts), `cllg-gpu`
  (py3.11, torch cu126, kraken 7.1.1 wheel sha 82faba07…), `e2ws` (torch cpu, transformers, paddlepaddle 3.1.0 + PaddleOCR requirements),
  `kraken`; pod ops `~/Projects/glossapi-ocr-local/experiments/ocr_program_review_20261006/pod_e2/pi_pod.py` (Prime Intellect create/
  terminate with A100/A6000 fallbacks); the Monitor/ssh lessons in `~/.claude/skills/checkpoint/SKILL.md` Part B (bounded ssh, liveness lines).

Deliverable layout (Python ≥3.11, `pyproject.toml`, package `greekocr`, CLI `greekocr`):
  greekocr/synth, greekocr/real (sources/, extract, adjudicate, partition, importers), greekocr/annotate, greekocr/readers (ours, kalchas,
  cllg, paddle_r01, services), greekocr/score, greekocr/warmstart, greekocr/deploy (docling_plugin, node_envs, pods), greekocr/ops (watch,
  receipts, rate limiting, secrets-from-env), tests/ (pytest; fixtures recorded, no network, no GPU; mocks for subprocess workers),
  docs/STANDARD.md (the rule: new tooling = API + test here; vendored logic carries origin), docs/INVENTORY.md, docs/API.md (every
  public function with a 2-line example), README.md. Keep each public API small and typed; keep provenance/receipt semantics intact.
Run the full test suite; report counts. Last line exactly: `T1: done | tests: <n> passed | modules: <n>`.
