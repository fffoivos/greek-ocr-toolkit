# M1 matched born-digital replay

For each epoch, replace exactly round(0.10*N) scanned draws. Allocate that quota proportionally across supported class x ceil(width/128)*128 strata (largest remainder); unsupported strata remain scanned. Sample positions without replacement; born-digital pool cycles shuffled independently within stratum. No pixel/label changes. Synthetic positions identical.

Born-digital: 19,657 train rows; excluded TEST: 3,600, document and ID disjoint.
Epoch budget 428,872; synthetic 214,436; born-digital 42,887; scanned 171,549. Integer rounding: born-digital = 9.999953%.
31 unavailable strata stay scanned; the replacement quota is redistributed across supported strata. Exact overall class x width marginals match control each epoch.
E3 data seed 20261015 is retained for all three model seeds. Draw entries use zero-based base-assembly position and born-digital pool index in sorted-shard/physical-row order. Each epoch binds ordered base and final (component,pool_index,line_id) SHA256. All unchanged draws are reconstructed by train.mix.assemble with the bound base fractions and 428872 exact rows. The compressed draw plan, mix, shard inventories, build receipts, validation mix, codec and data release must all be bound by the M1 arm.
The trainer uses matched_replay for train only; shared val is concatenated once. Packed sampler seed = mix seed and set_epoch(epoch). Width marginals match, so its 6702-step horizon stays fixed. Test rows never enter the replay component.

| Epoch | Synthetic | Scanned | Born-digital | Distinct replay rows |
|---:|---:|---:|---:|---:|
| 1 | 214436 | 171549 | 42887 | 9291 |
| 2 | 214436 | 171549 | 42887 | 9283 |
| 3 | 214436 | 171549 | 42887 | 9288 |
| 4 | 214436 | 171549 | 42887 | 9292 |
| 5 | 214436 | 171549 | 42887 | 9272 |
| 6 | 214436 | 171549 | 42887 | 9288 |
| 7 | 214436 | 171549 | 42887 | 9287 |
| 8 | 214436 | 171549 | 42887 | 9286 |

Full per-epoch class, width, appearance and per-stratum removed/inserted/still-scanned counts are in m1_verification.json. Repetition is intentional and explicit.

| Class | Width bucket |
|---|---:|
| cyrillic | 256 |
| cyrillic | 384 |
| cyrillic | 640 |
| cyrillic | 768 |
| cyrillic | 896 |
| cyrillic | 1024 |
| cyrillic | 1152 |
| cyrillic | 1280 |
| cyrillic | 1536 |
| cyrillic | 1664 |
| cyrillic | 1792 |
| cyrillic | 1920 |
| cyrillic | 2048 |
| cyrillic | 2176 |
| cyrillic | 2432 |
| greek_latin_cs | 2176 |
| greek_latin_cs | 2560 |
| greek_mono | 2304 |
| greek_mono | 2432 |
| greek_mono | 2560 |
| greek_poly | 512 |
| greek_poly | 1152 |
| greek_poly | 2048 |
| greek_poly | 2176 |
| greek_poly | 2304 |
| greek_poly | 2432 |
| greek_poly | 2560 |
| latin | 2176 |
| latin | 2304 |
| latin | 2432 |
| latin | 2560 |

This is an E3-based preparation receipt. F1 has not been frozen; regenerate and validate the exact draw plan against the repaired release before campaign submission.

Actual Clariden validation: **verified**, all eight epochs; `m1_shard_validation.json` binds the final mix and compressed draw manifest. No M1 training arm was launched.
