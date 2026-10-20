#!/usr/bin/env python3
"""Stage the O4c-ranked parliament candidates (CC-BY-4.0, verified text layers) under /opt/e2-assets/parliament_s2.
Reads docs/evidence/o4c/candidates.jsonl (source == parliament), downloads each scan file, verifies md5 against scan_md5
when present, writes receipts.jsonl. Polite: one request at a time, 1 s between files, O4c user agent."""
import json, hashlib, time, pathlib, sys, urllib.request, ast
ROOT = pathlib.Path(sys.argv[1]); DEST = pathlib.Path(sys.argv[2]); DEST.mkdir(parents=True, exist_ok=True)
UA = 'GreekPageOCR-O4b/1.0 (noncommercial OCR research; bounded candidate acquisition)'
rows = [json.loads(l) for l in open(ROOT/'docs/evidence/o4c/candidates.jsonl') if l.strip()]
rows = [r for r in rows if r.get('source') == 'parliament']
rows.sort(key=lambda r: int(r.get('rank') or 999))
receipts = DEST/'receipts.jsonl'; done = {json.loads(l)['document_id'] for l in open(receipts)} if receipts.exists() else set()
print(f'{len(rows)} parliament candidates; {len(done)} already staged', flush=True)
for r in rows:
    doc = r['document_id']
    if doc in done: continue
    files = r.get('scan_files') or []
    if isinstance(files, str): files = ast.literal_eval(files)
    out_dir = DEST/doc; out_dir.mkdir(exist_ok=True); got = []
    for f in files:
        url = f['url']; name = f.get('name') or url.rsplit('/',1)[-1]; out = out_dir/name
        if not out.exists():
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=600) as resp, open(out, 'wb') as fh:
                while True:
                    chunk = resp.read(1 << 20)
                    if not chunk: break
                    fh.write(chunk)
            time.sleep(1.0)
        h = hashlib.md5(out.read_bytes()).hexdigest(); s = hashlib.sha256(out.read_bytes()).hexdigest()
        got.append(dict(name=name, url=url, bytes=out.stat().st_size, md5=h, sha256=s,
                        md5_matches_manifest=(h == r.get('scan_md5')) if r.get('scan_md5') and len(files) == 1 else None))
    rec = dict(document_id=doc, rank=r.get('rank'), title=r.get('title'), record_url=r.get('record_url'), year=r.get('year'),
               pages=r.get('pages'), rights=r.get('rights'), estimated_polytonic_lines=r.get('estimated_polytonic_lines'),
               text_layer=r.get('text_layer'), files=got, fetched_at=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    with open(receipts, 'a') as fh: fh.write(json.dumps(rec, ensure_ascii=False) + '\n')
    print(f"staged rank {r.get('rank')} {doc} {sum(g['bytes'] for g in got)/1e6:.1f} MB md5ok={[g['md5_matches_manifest'] for g in got]}", flush=True)
print('PARLIAMENT_S2_DONE', flush=True)
