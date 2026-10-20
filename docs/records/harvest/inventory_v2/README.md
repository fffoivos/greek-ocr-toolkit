S1 source inventory evidence and build tools.

The deliverables are `INVENTORY.md`, `RIGHTS.md`, `sources.jsonl`, and `receipts/`.
Source code, existing harvests, other worktrees, and the main checkout are read-only inputs.

The `jobs-*.json` files are a record of bounded catalogue, terms, front-matter and page checks, including failed attempts. They are not a bulk acquisition manifest. Do not rerun all jobs as an acquisition task. `fetch_inventory.py` reuses the unchanged O4c robots/rate transport and User-Agent with worktree-local caches. No Anemi images, Google OCR reads, source-book PDFs, paid APIs, gate acceptance or credential persistence are part of this inventory. Individual raster probes are capped per source.

Offline rebuild and validation:

```sh
python3.14 build_inventory.py
python3.14 validate_inventory.py
```

Run from this directory with the repository's page-probe dependencies available if reproducing image counts. The completed run used an isolated temporary environment, not a repository/runtime dependency change. `probe_lines.py` uses `greekocr.pages.lines.page_line_segments`; its rows are descriptive detector output, not admitted target-class yield. `assessments.py` contains human source assessments and ranked recommendations. `audit_local_metadata.py` only reads existing metadata/link tables. `hf_metadata_check.py` accepts an HF token only through its command environment; no token value is stored. All token-bearing requests omit authorization headers from receipts.

`sanitize_receipts.py` removes unneeded response session headers and embedded public website API keys. Its redaction log preserves original response byte counts/hashes and stored-body hashes. It must run after collection and before the final offline build. The delivered raw HTTP bodies are sanitised accordingly.

The validation receipt checks schema, source coverage, body/image hashes, decoded raster sizes, detector-input binding, cap compliance, source/summary arithmetic, report links and the exact footer. Numerical report claims link to the specific census, plan-input, page or source-assessment receipts. Blocking or unavailable facts remain unknown; inventory completion is not source qualification.

The requested local commit could not be created in the managed sandbox: Git was denied creation of the worktree index lock. No alternate index, other worktree, or push was used. The source-bound handoff below verifies branch, HEAD, every delivered input hash, validation and staged-file scope. Run it from a normal shell with Git metadata write access:

```sh
python3 docs/records/harvest/inventory_v2/commit_inventory.py --check
python3 docs/records/harvest/inventory_v2/commit_inventory.py
```

The first command is read-only. The second performs the already-requested local commit and never pushes. The pre-existing untracked S1 brief is outside the commit scope.
