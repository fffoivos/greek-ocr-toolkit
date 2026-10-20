# SR-G4 provenance scans

| Context | v4 result | Violations | Returned images |
| --- | --- | --- | --- |
| p1c1 | VOID | 1 | 28 |
| p1c2 | OK | 0 | 23 |
| p1c3 | OK | 0 | 21 |
| p1c4 | OK | 0 | 11 |

The original v3 scans are preserved beside each v4 scan as `p1cN.scan.v3.json`.

p1c1 record 42: the original manifest-verified `items.jsonl` and 200 PNGs were copied into a fresh temporary directory. The five preceding literal commands were replayed in order; the final command produced `zoom/batch1.png` at 982×1110. Its decoded RGB pixels are exactly equal to the recorded image. The PNG date:create, date:modify and date:timestamp metadata differ. Raw file bytes therefore differ, and the image is too small for the existing 2048-long-side downscale rule. The violation remains under the requested bytes/downscale policy. No same-size pixel or metadata-normalization acceptance was introduced.

The synthetic overwrite regression recovers a byte-identical earlier PNG and records `match: "reproduced"`. A metadata-only mismatch regression remains a violation.

Replay uses no shell evaluation. A conservative command/Python API allowlist, confined Python IO, and parsed ImageMagick options reject unsupported operations and network requests. No OS sandbox isolation is claimed: sandbox-exec was unavailable. Failed or skipped replay commands are recorded in the v4 scan.
