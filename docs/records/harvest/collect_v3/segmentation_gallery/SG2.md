# SG2 provenance and page strips

The original result is in `0dc29bf2163d26ce9ff6788b0861e70eb77d7150:docs/records/labelfix/geometry/REPORT.md:398`, supported by 50 page judgments. It was introduced in G1c on 16 Oct and retained in G1d. 501/2624 = 19.09%; 2123/2624 = 80.91%.

The pilot overlays contain admitted boxes. P002 is a concrete counterexample to reading the 19% as absence of a raw Google detection: both short final rows and the page number have raw boxes. The strips preserve this distinction visibly: blue admitted, cyan other raw boxes, red no admitted box. Two merged pairs are also shown. The later G1d census uses all raw boxes, detector rows rather than printed rows, and permits partial coverage; its 8.55% is a separate measurement. No OCR, detector, checkout, network access or input mutation.

The original ignored sealed page index was unavailable. Membership was reconstructed with the archived sampler and seed, using frozen measured test-page census records. The complete reconstructed sealed page index matches the archived FILES.tsv SHA-256 and size exactly (78,707 bytes). The selected source rasters match their archived SHA-256 hashes. JSON records retain native coordinates and box lists. `sg2_validation.json` records custody and limitations.

Rebuild offline with the existing workspace Python: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python docs/records/harvest/collect_v3/segmentation_gallery/build_sg2.py`. Run after the SG1 builder, which rebuilds its own files.
