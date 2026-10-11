# CP-H1 Fix 1 regression fixture inventory

Source: the explicitly supplied `pilot_t13c` archive. `manifest.json` binds the
14,200-record source JSONL by SHA-256 and includes all page polygons, reviewer
IDs, expected split polygons and stored reader-piece geometry. Page renders are
byte-identical copies, not new renders. Anemi CC BY-NC-ND; internal regression
use only. No network acquisition or OCR calls are needed by these fixtures.

| Fixture | Origin / regression |
| --- | --- |
| `anemi-39efef08912bdefa01efa90d-v5c05ae52-p000023.png` | `anemi-39efef08912bdefa01efa90d-v5c05ae52-p000023-l0038`: cross_column |
| `anemi-39efef08912bdefa01efa90d-v5c05ae52-p000024.png` | `anemi-39efef08912bdefa01efa90d-v5c05ae52-p000024-l0012`: cross_column |
| `anemi-1697d5cc21fa26717b97e073-v1d3645ab-p000106.png` | `anemi-1697d5cc21fa26717b97e073-v1d3645ab-p000106-l0041`: neighbour_sliver |
| `anemi-0cb3f67240837f77ee728005-v02def8a2-p000020.png` | `anemi-0cb3f67240837f77ee728005-v02def8a2-p000020-l0001`: page_border |
| `clean_polytonic.raw.png` | `00c322b3… p87 l4`: polygon-masked clean control; own accents must survive. |
| `fetch_selection.py` | Verbatim `selected_indices` and `select_records` from archived `pilot/_fetch/o4b_anemi_pages.py`, with offline imports. Original module hash and extraction are in the manifest. |
| `manifest.json` | Geometry and custody metadata; no absolute fixture dependency. |

The column regressions preserve **6,196 / 5,846** original dark pixels respectively
(threshold <200) across the two split crops. Page 24's right split starts at x=562,
not the page's median band edge x=565; this preserves the first German letter.
The neighbour regression measures 5/32 occupied rows and x-span 572/796 above
the fitted main body. The bordered prose page has long rules but no box lattice.

| File | SHA-256 | Bytes |
| --- | --- | ---: |
| `anemi-0cb3f67240837f77ee728005-v02def8a2-p000020.png` | `1f13118446f62f190f738419559d111b04b46f4edf91cb49aad975dd67726d2c` | 522869 |
| `anemi-1697d5cc21fa26717b97e073-v1d3645ab-p000106.png` | `3385fe1e522e340df1b075dc3eda88c9add8780912e02b60270bfe88d8a3007e` | 618585 |
| `anemi-39efef08912bdefa01efa90d-v5c05ae52-p000023.png` | `6af6c920ef4c4b54d91544e9131c6f6ce0837737cced5a1e0b6858c184a9e6df` | 281770 |
| `anemi-39efef08912bdefa01efa90d-v5c05ae52-p000024.png` | `4ebe6488b93a4c5bb4e2b2cbb9be156e49ba5916091f3149fa4fbbe31cc2ea3a` | 250796 |
| `clean_polytonic.raw.png` | `cc38a789cc64756ca690a956c32c558c0e775485b92947dde3ae87b3f2201787` | 7606 |
| `fetch_selection.py` | `33251f244408d013657d3cdfb20b6a697c27b3ee2898f4c30cf38d8e48cc532b` | 1325 |
| `manifest.json` | `e968f504d4e76ce1cee1aa0be68806c9f36aeeabbb4e3e31f2f9cd0e2ba82bc0` | 141970 |
