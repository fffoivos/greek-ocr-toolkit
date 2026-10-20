# CLEAN3B receipts

One row per MOVE entry, including 19 symlinks whose size/hash describe link text. Producing commits are inherited from CLEAN3A and later custody corrections. CP5's full producing SHA identifies the historical gzip source; decompression reproduces the uncompressed receipted bytes exactly. HEAD bytes have custody; no lead-receipt replacement.

| Shard | Entries | Payload bytes | TSV bytes | SHA256 |
|---|---:|---:|---:|---|
| [receipt_01.tsv](receipt_01.tsv) | 16,888 | 9,984,555,912 | 2,890,365 | `7c538a608f33601dde77d82bebb0fb5af03d6c1c8873d924e087e08cf7aae6b9` |
| [receipt_02.tsv](receipt_02.tsv) | 8 | 389,751,892 | 1,340 | `49d6cb51d117b92aeb1edc06853cc443c3c4717af21c44b32d0b5c7035d17890` |
| [receipt_03.tsv](receipt_03.tsv) | 1 | 119,720,892 | 238 | `724f5cbf78a2ad68d679c148f2b90237fef515e2839f9c229e3737f80ff1c3a2` |
| [receipt_04.tsv](receipt_04.tsv) | 1 | 42,991,967 | 194 | `cb497f533d260f0d437563ede42bcb64971688447999ff8a00158145fa41206e` |

Total: **16,898 entries / 10,537,020,663 payload bytes**. Each TSV is <=4,000,000 bytes. All four shards are included in `../MOVE_MANIFEST.tsv`. Later manifest rows use their receipt file's UTC mtime at this correction; this is filesystem provenance, not an inferred original movement time.

SEGEVAL1.bundle is preserved as a file (147,025,055 bytes; sha256 `25c38794aacb89d083b461175471735575551f0acc4d1f612214b3e43fee1e1a`). Its header names bundled head `b3b5aaa19835ac626af6576da37e008386b26879 refs/heads/segeval1-artifacts`. Custody is the bundle bytes, not assumed availability in local history.

`candidate_order_KEEP.jsonl` and `SEGEVAL1.bundle` are referenced by historical scope guards s1–s4 / gate_rereport / gate03. Those records and scripts under docs/ remain unchanged. Historical replay needs a new receipt-backed adapter or a deliberate restored mirror; current scope-guard execution is not qualified by this plan.


## receipt_02.tsv (19 Oct 23:50)
8 restored test fixtures > 5 MB moved to the data root after the size guard flagged them (tests reading them are records).


## receipt_03.tsv (20 Oct 00:05)
1 files > 5 MB that re-entered via lead merges, moved to the data root.


## receipt_04.tsv (20 Oct 00:58)
1 files > 5 MB re-added by the ignore-pattern fix, moved to the data root.


## CP5 producing source

`dc47b8bb757a902aa180314527d2d0907b3da61c`, found with `git log ac1c38cf6 -- docs/harvest/collect_v3_admission/seg/CP5_verification.json.gz`, is the producing-phase commit. The old base path is the **gzip** file; the restored 119,720,892-byte JSON is its decompressed payload (SHA256 `cc5131461ce6fa43a5f5be67fe74a5638b5d7226145dee2883ab1632c6a26731`). This is a transformed-source binding, not a claim that an uncompressed blob existed at that old path.
