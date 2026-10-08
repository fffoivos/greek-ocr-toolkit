#!/usr/bin/env bash
# Text source for the rendered validation lines: the first 1500 polytonic lines of two public-domain corpora in
# greek-page-ocr's corpus_v4 (Gutenberg Greek, 1000 πρῶτα χρόνια). Text only: no image, no OCR, no text layer.
# Usage: extract_poly_lines.sh OUT_DIR   (writes OUT_DIR/poly_lines.jsonl; the eval scripts take OUT_DIR as argv[1])
set -eu
C=~/Projects/greek-page-ocr/data/raw/corpus_v4
for f in gutenberg_el_lines.jsonl nc_1000_prwta_xronia_ellhnikhs.jsonl; do grep -m 1500 '"is_polytonic": true' "$C/$f"; done > "$1/poly_lines.jsonl"
wc -l "$1/poly_lines.jsonl"
