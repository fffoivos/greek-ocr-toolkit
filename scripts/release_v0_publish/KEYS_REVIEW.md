# REL0-S2e: coordinator decision on historical review keys

Decision (28 Oct 2026): past blind-review deblinding keys stay out of the public snapshot, kept locally and retrievable later. The path policy now applies anywhere: directories named `keys` (except `*.py` files), `*_key.json`, `*_key.jsonl`, `key_SEALED.json`, `blind_key.json`, `blind_pages_key.json`, `wl_key.json` (including gzip forms), and `*.mapped.jsonl` below an `answers/` directory. Rules are respectively `review deck key tree`, `review deck key file`, and `review answer join`. Leads matched only by content remain included: of the old 76 `card/row content` leads, ten now match the requested `answers/*.mapped.jsonl` path rule and 66 remain content-only. No local key payload is deleted.

Source-scope check: **zero rule hits under `greekocr/`, `scripts/`, or `tests/`** in the refreshed candidate set, including non-code files; there are no such hits to list. The `*.py` directory-rule exemption preserves `docs/records/harvest/sol_reading/grave_full/keys/synthetic/pipeline/packs/p1c1/zoom/add.py`; no other discovered Python file has a `keys` directory component. Fixtures cover source roots and directory-rule exemptions.

The following is the retained REL0-S2d search evidence, before this decision; its old inclusion claims and hashes are historical, not fresh-policy classification. REL0_S2e_RECEIPT.json binds current exclusions, source-scope checks, content-only inclusion and refreshed outputs. Exact paths, snapshot hashes and search signals are in [KEYS_REVIEW.tsv](KEYS_REVIEW.tsv) (338 search leads, including support files, code and fixtures; not 338 confirmed keys).

Confirmed mapping examples and related candidate families:

| Included path/family | Evidence / review scope |
| --- | --- |
| `docs/records/harvest/blind_checks_v1/{c0,t4c}/*_key.json` | `c001`-style cards map to `line_id`; 13 key files. |
| `docs/records/harvest/collect_v3/c1/efficiency/keys/` | `input_mapping.json` maps card ids to line/source crops; also review permutations, truth and support files (28 paths). |
| `docs/records/harvest/collect_v3_admission/{seg,segeval1}/` | Key trees plus `segeval1/keys/crop_custody.json` (`card_id` → `row_id`); `seg/cp7/**/answers/*.mapped.jsonl` directly pairs `card_id` and `line_id`. Also review controls, scored rows, diagnostics and small-segment answer joins. |
| `docs/records/harvest/recut_v1/w1_masked/` | `*/keys/*.json` contains opaque-card/source mappings and control truth (54 key-tree paths); results/review queues/scored cards and `control_swap.json` may duplicate joins. `recut_v1/{dev,f2}/**/records.jsonl` embeds review card and row/source ids. |
| `docs/records/harvest/sol_reading/{keys,grave,grave_full,validation}/` | `keys/*.json` includes opaque `items` → `line_id`/`source_id`, controls and slot permutations; synthetic validation copies are separately flagged by their paths. Support receipts are search leads only. |
| `docs/records/harvest/sample_v1/gr/{label_cards/*_key.json,blind_pages_key.json}`; `docs/records/harvest/page_reads_v1/blind_key.json` | Label cards map `card` to `line_id`; page keys map anonymised filenames/cards to source/page ids. |
| `docs/records/labelfix/spellcheck/{R0_wholeline/wl_key.json,print_truth/key_SEALED.json}` | `wl000` / `P000` map to `line_id`, image/source or answer alternatives. Related R0/SF3 manifests and scoring records are content-search leads. |

Method: searched 39,282 included text/structured/code files outside `artifacts/` from the pre-refresh inventory, including gzip expansion (50 MB cap). Signals: a `keys` directory/key-shaped filename, or quoted card/opaque/blind identifiers (including opaque dictionary keys) together with row/line/source fields. 262 path leads and 76 additional content-only leads. Confirmed examples above were read; co-occurrence alone does not establish a key, and code, fixtures, templates and receipts need coordinator classification. Binary/archive internals and arbitrary identifier encodings were not exhaustively reviewed. That historical fresh-inventory membership and SHA readback are recorded in REL0_S2d_RECEIPT.json. No mapping values are reproduced here.
