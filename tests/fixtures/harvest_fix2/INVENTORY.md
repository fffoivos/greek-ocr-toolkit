# CP-H1 Fix 2 regression fixture inventory

Source: the read-only supplied `pilot_t13c` archive. Anemi CC BY-NC-ND; internal regression use only. Full pages are byte-identical archived renders. Raw crops are polygon-masked extractions from those same page pixels. No new render, detector run, reader call or network acquisition.

Source records SHA-256: `108c3635a5ffc3a424f5810b9491639fdee047fcd926c7423a731ed415b6cbe4`. The manifest binds each raw crop to its original page SHA and polygon, and records every page polygon for the region/table cases. All tests use repository-relative fixture paths.

| Case | Source / required outcome |
| --- | --- |
| `anemi-ffe26907d1e3e9c1f75337e2-v7b51b63d-p000159-l0024.raw.png` | `anemi-ffe26907d1e3e9c1f75337e2-v7b51b63d-p000159-l0024`: clean own diacritics pass |
| `anemi-e28081a0d8ed58a169d0b77d-v7c521382-p000093-l0038.raw.png` | `anemi-e28081a0d8ed58a169d0b77d-v7c521382-p000093-l0038`: clean own diacritics pass |
| `anemi-d163abb4ab37b39eee28ab58-v1aa60884-p000112.png` | `anemi-d163abb4ab37b39eee28ab58-v1aa60884-p000112-l0001`: upper l30-l37 remain intact and pass; lower fused l5/l8/l14/l16 split without ink loss |
| `anemi-d80c7cca7455ce4d6261baa6-v3f6fd847-p000049.png` | `anemi-d80c7cca7455ce4d6261baa6-v3f6fd847-p000049-l0001`: at least two closed rule cells; page excluded as table |
| `anemi-8e3c482e1f6c81bb67f24395-v3e1ce3ec-p000024.png` | `anemi-8e3c482e1f6c81bb67f24395-v3e1ce3ec-p000024-l0001`: no invented gutter; l26/l27 remain intact and pass |
| `anemi-0907df739607faca673d2169-vdb56fe97-p000023-l0067.raw.png` | `anemi-0907df739607faca673d2169-vdb56fe97-p000023-l0067`: clean own diacritics pass |
| `anemi-c6f5e826036e0b6764099523-vd599e2de-p000045-l0057.raw.png` | `anemi-c6f5e826036e0b6764099523-vd599e2de-p000045-l0057`: clean scan-grain row passes |
| `anemi-043b454a8c255b6690fd3777-v410b5b9f-p000038.png` | `anemi-043b454a8c255b6690fd3777-v410b5b9f-p000038-l0001`: short paragraph endings and ornaments retain the established facing-page columns; l4/l6/l19/l21/l25 pass |
| `anemi-928e34aaaa78469aacd6c7ef-vdcf1df66-p000029.png` | `anemi-928e34aaaa78469aacd6c7ef-vdcf1df66-p000029-l0001`: vertical gaps separate title and stanza bands; l2/l4 pass |
| `anemi-6df192e72b10d13c5fc1374a-v5410521e-p000085.png` | `anemi-6df192e72b10d13c5fc1374a-v5410521e-p000085-l0001`: illustration fragments do not widen the prose band; l12 passes |

The original cycle-1 sliver page/polygon and border-prose control are reused from `../harvest_fix1/manifest.json` and its existing custody inventory. The sliver must still reject; the frame must still pass. Synthetic tests cover exact 12% AND 20% union thresholds, centroids inside/outside the zone, the inclusive 25% overlap limit, actual ink contact with the zone, an empty bounding-box corner grazing the guide, and closed cells without any box lattice, including large cells divided horizontally or vertically.

| File | SHA-256 | Bytes |
| --- | --- | ---: |
| `anemi-043b454a8c255b6690fd3777-v410b5b9f-p000038.png` | `aba32592356989b0e75a50e223545f8805dd6cbfb767d2beff972fd012099f1c` | 1275638 |
| `anemi-0907df739607faca673d2169-vdb56fe97-p000023-l0067.raw.png` | `d6c8c4e350363189e9b23c2b72d7db0affc51cf260e1758b842c15b0391df669` | 6687 |
| `anemi-6df192e72b10d13c5fc1374a-v5410521e-p000085.png` | `d270e08844446890b8bf05851016b3fb4236fe60486a7a64639a3eb68161956b` | 310901 |
| `anemi-8e3c482e1f6c81bb67f24395-v3e1ce3ec-p000024.png` | `d97deccaf16362d1d1f28679f33c574e662f779c34bd7208571aa69b5eaab5d7` | 808988 |
| `anemi-928e34aaaa78469aacd6c7ef-vdcf1df66-p000029.png` | `60a20ad3f06a1551960e8b7651d0320e9065d03c18d06a69b5daf8174643f112` | 111886 |
| `anemi-c6f5e826036e0b6764099523-vd599e2de-p000045-l0057.raw.png` | `6c04af987192cf44c89dfe731ea336b02a68d3faa2249512889fd0c4c81d59b0` | 6934 |
| `anemi-d163abb4ab37b39eee28ab58-v1aa60884-p000112.png` | `60908f30d0e8d9c24ccde5b5b56febb717293dc7252136aefec976efa603b556` | 208646 |
| `anemi-d80c7cca7455ce4d6261baa6-v3f6fd847-p000049.png` | `466372f43394e5031ee5b79b4a0b1f3507a61d66963f4b4e16229b320374eb37` | 344507 |
| `anemi-e28081a0d8ed58a169d0b77d-v7c521382-p000093-l0038.raw.png` | `101287bdf2717de2d846d80852cedc9e2a003837338328a734a83386304aa642` | 6463 |
| `anemi-ffe26907d1e3e9c1f75337e2-v7b51b63d-p000159-l0024.raw.png` | `0b7579ec900eb5bf88cb677478d58de47e29d14e445f9f4f5954e58ecb192212` | 5015 |
| `manifest.json` | `705b679ed07a54310eda2008b975a5dddebccd011ca97b2cec4a65da9aee0f45` | 132287 |
