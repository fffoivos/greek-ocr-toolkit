# Public snapshot preparation — REL0-S2c

The working-tree inventory is a review aid. The materialisation root is a **resolved commit**, exported with `git archive`, never the index or working tree. No staging, commit, checkout, ref update, merge or push is performed. The builder makes only read-only `rev-parse` and `archive` queries; evidence enumeration makes a read-only `ls-tree` query. The coordinator constructs the publication commit on the public parent under PLAN rev 2 §2 and verifies ancestry/reachable objects separately.

From the checkout root, using the existing test environment:

```sh
python -B -m scripts.release_v0_publish.prepare_evidence --commit HEAD
python -B scripts/release_v0_publish/receipt_manifest.py
python -B scripts/release_v0_publish/inventory.py
python -B scripts/release_v0_publish/build_public_tree.py HEAD /private/tmp/rel0-public-tree
```

`out_dir` must be absent. The builder exports the given commit into temporary scratch, applies the current scanner policy to those archived bytes, copies included files with their executable modes, then runs from the assembled tree:

```sh
PYTHONPATH=<out_dir> python -B -c 'import greekocr, greekocr.train, greekocr.deploy.docling_plugin'
PYTHONPATH=<out_dir> python -B -m pytest tests/train tests/deploy tests/release_v0 tests/test_montage.py tests/test_provenance_cli_api.py -q -p no:cacheprovider --basetemp=<temporary scratch>
```

Imports must resolve inside the assembled tree. The initial import check runs without pytest/conftest. Test basetemp and archive scratch are removed automatically. The output tree is retained for review; the caller removes it after retaining receipts. A build from current HEAD does **not** acquire uncommitted fixes or evidence. Rebuild against the coordinator's new commit before publication.

`PUBLIC_TREE_MANIFEST.tsv` binds payload paths/bytes/SHA256. If a complete manifest would exceed 5 MB, this TSV instead indexes `PUBLIC_TREE_MANIFEST.parts/part-*.tsv`, each containing complete payload rows; the receipt declares the layout and binds the parts. Generated validation metadata is outside the payload manifest to avoid circular hashes. `PUBLIC_TREE_RECEIPT.json` records the resolved commit, tooling hashes, import/test exits, evidence problems and exact-byte recheck. `PUBLIC_TREE_VALIDATION/` retains logs/JUnit, excluded paths, and review queues. Any test mutation is reported as a failure and original commit bytes are restored. Missing sealed members/cited model records fail the build even when imports succeed.

## Inventory rules

- No payload file may exceed **5,000,000 bytes**. Symlinks and linked ancestors are excluded without dereferencing them. Cache directories and operational namespaces (`.aws`, `.ssh`, `.codex`, `.agents`, `.env`, `.netrc`, `.npmrc`) are excluded.
- Exclude directory components named `private` or ending `_private`, audit `opus_keys` trees, `items_key*.json` (also gzip), and `key.jsonl` in audit/adjudication/cards trees. `PRIVATE_REVIEW.tsv` lists excluded candidates as path/bytes/SHA256/rule, including otherwise ignored private candidates. Private archive members also exclude their containing archive. `INCLUDED_NAME_REVIEW.tsv` lists included paths containing private/key/secret/token/password for coordinator review.
- Raw Google exclusions require structured JSON/JSONL response content: Document AI text/pages with response anchors, Vision annotation objects, response/document wrappers or arrays. Gzip/TAR/ZIP members are inspected with a 50 MB expanded budget. A raw-looking filename, source field-name literal, or documentation mention alone is not a response. Unreadable/oversized archives require review.
- Credential exclusion requires value-shaped HF (at least 30 alphanumeric suffix characters), GitHub/OpenAI keys, AWS access-key ids, private-key headers, or a quoted long high-entropy literal assigned to a credential name. Environment lookups, variables, parser code, ordinary examples and tokenizer/digest fields stay included. Diagnostics contain **path and line only**, never matched values; archive line numbers refer to expanded content. This defined scanner does not establish absence of arbitrary secret formats or private prose.
- All `receipts_*smoke*` directory trees are excluded. `out/` contains run outputs: only the exact `EVIDENCE_PATHS.txt` members are retained. Under `artifacts/`, pytest/mock/test/output run trees are excluded; ordinary small method/evaluation evidence remains eligible. `OUTPUT_REVIEW.tsv` lists every candidate under out/artifacts with its decision/rule. Large review lists use a small TSV index binding complete parts, keeping every published file below 5 MB.

`EVIDENCE_PATHS.txt` enumerates existing repository files cited by MODELS/VERSIONS/PLAN plus the public evidence-redaction receipt and each sealed PAYLOAD and its exact members (93 Stage C, 95 h14). Evidence exceptions do not override private/content/size rules. The h14 package includes only its PAYLOAD and bound members, never sibling smoke/test outputs. `.gitignore` has exact member exceptions, without package wildcards. Small attempt013 config-bearing CLAIM/PLAN records and attempt014 expected config/PLAN records are retained by exact path. The final attempt014 remote CLAIM/RUN_BINDING is still a documented gap; smoke/pytest fixtures are not substitutes.

`REQUIRED_EVIDENCE.txt` lists cited files absent from HEAD, and the mutable TRAIN_FULL execution ledger that must also be committed. The coordinator commits these plus the scoped fixes. The ledger SHA follows **hash recorded at publication**; fill `MODELS.json.execution_evidence.publication_sha256` from the final committed bytes, never invent a value. Version chronology uncertainties remain in GAPS.md.

The full local `PUBLIC_INVENTORY.tsv` uses working-tree bytes: tracked existing paths (read from the index) union rg nonignored files and ignored private candidates. It is **not** the commit inventory. Its Git-sized parts and receipt bind the review snapshot; the oversized full TSV stays local. Generated review metadata omits itself to avoid circular hashes. Re-run after writers settle. `BULK_RECEIPT_MANIFEST.tsv` covers ignored smoke receipts too; it does not certify a Clariden copy. The coordinator still reviews private prose, verifies remote custody and publication history, and reads back the public commit.

Two PAGE evidence copies withhold private or unverified-sharing review-artifact URLs. `PUBLIC_EVIDENCE_RECEIPT.json` binds original source SHA256, public SHA256/bytes and redacted line numbers, without retaining the private links. VERSIONS pins the public copies; result text is unchanged.
