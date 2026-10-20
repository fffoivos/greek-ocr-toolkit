#!/usr/bin/env python3
"""Re-fetch the S17 Parliament pdf_cache (107 PDFs) from the PUBLIC digital library.

home-ts-INDEPENDENT. Source = digitallibrary.parliament.gr (InvenioRDM, CC-BY-4.0). Each PDF is
downloaded from its manifest `download_url` and VERIFIED byte-exact against `pdf_cache_sha256`
(the content-addressed pdf_cache filename), so the result is provably identical to what home-ts holds.

Manifest: docs/evidence/s17/pdf_cache_refetch.jsonl  (built by joining the 107 pdf_cache sha256s to
home-ts:.../parliament_digital_library/manifests/records_manifest.jsonl via content MD5; 107/107, 0 miss).

Usage:  python3 scripts/fetch/parliament_pdf_cache.py [DEST_DIR]   (default: data/raw/pdf_cache)
"""
import json, sys, hashlib, urllib.request, pathlib, time

ROOT = pathlib.Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "docs/evidence/s17/pdf_cache_refetch.jsonl"
DEST = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data/raw/pdf_cache"
DEST.mkdir(parents=True, exist_ok=True)

recs = [json.loads(l) for l in open(MANIFEST) if l.strip()]
print(f"re-fetching {len(recs)} Parliament PDFs -> {DEST}")
ok = skip = bad = 0
for i, r in enumerate(recs, 1):
    sha = r["pdf_cache_sha256"]
    out = DEST / f"{sha}.pdf"
    if out.exists() and hashlib.sha256(out.read_bytes()).hexdigest() == sha:
        skip += 1; continue
    for attempt in range(3):
        try:
            with urllib.request.urlopen(r["download_url"], timeout=120) as resp:
                data = resp.read()
            got = hashlib.sha256(data).hexdigest()
            if got == sha:
                out.write_bytes(data); ok += 1
                print(f"[{i}/{len(recs)}] OK {sha[:12]} ({len(data)//1024}KB) {r.get('title','')[:40]}")
            else:
                bad += 1; print(f"[{i}/{len(recs)}] ✗ HASH MISMATCH {sha[:12]} got {got[:12]}")
            break
        except Exception as e:
            if attempt == 2:
                bad += 1; print(f"[{i}/{len(recs)}] ✗ FAILED {sha[:12]}: {e}")
            else:
                time.sleep(2 * (attempt + 1))
print(f"\ndone: {ok} fetched, {skip} already-present, {bad} failed  (total present = {ok+skip}/{len(recs)})")
sys.exit(1 if bad else 0)
