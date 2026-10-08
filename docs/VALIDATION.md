# Phase 1 validation — 8 October 2026

**367 passed, 0 failed, 0 errors, 0 skipped.** Full offline pytest suite on Python 3.11.3, CPU only. The 15 warnings come from the preserved Docling `force_full_page_ocr` API, now deprecated in the installed runtime.

Command: `.venv/bin/python -m pytest -q --junitxml=docs/pytest-results.xml`.

Evidence: [JUnit results](pytest-results.xml), [machine-readable validation](validation.json), [exact test environment](test-environment.txt).

The suite covers every vendored file hash and logic receipt, HEAD-based recipe custody, shard/receipt tampering, legacy role refusal, deterministic sampling, document-family exclusions, dataset BOM/suffix and geometry, blind adjudication and rejected crops, missing text layers, word-tag bindings, strict and bake-off scoring, mark and category readouts, CLLG worker restart/timeout/protocol handling, recorded O4c/Anemi transport replay, real CPU fixture-model loading and R01/R03 conversion, checkpoint digests, Kalchas CPU map-location restoration, Docling registration/routing/replacement geometry, environment plans, mocked pod operations and every watcher terminal state.

The built wheel contains all 123 vendored package files with inventory-matching hashes. An isolated install outside the checkout successfully loaded recipes, exclusion resources, upstream licence, tags and scoring, then loaded a fixture checkpoint and read a crop with the real CPU recognizer. No source checkout was on that process's import path.

Counts: 172 vendored files; 71 public callable API entries; 40 package modules. Module count includes Python package initializers and the deployed Docling plugin, excludes `_vendor` archival implementations and `__main__.py`. The module path list and wheel hash are in `validation.json`.

These are fixture/API qualifications. Released reader weights, production datasets, real native-framework parity, the original full Corpus C1 cohort, Linux/CUDA node execution and live deployments remain separate evidence. Rust was preserved as reference source and wrapped; it was not built or moved. No training, remote data acquisition, service call, pod creation, Git write or other-repository modification was performed. Repository visibility and commits remain with the coordinator.
