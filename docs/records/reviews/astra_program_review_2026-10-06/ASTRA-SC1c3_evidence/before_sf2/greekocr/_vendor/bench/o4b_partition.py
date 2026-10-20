"""Build the reviewed O4b work partition from O5 custody, C1 and a work map."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from greekocr._vendor.bench.common import read_rows, sha256, write_json
from greekocr._vendor.bench.o4b_common import resolve_exclusions


def build(o5, c1, document_map, out, reviewed=False):
    o5 = Path(o5); c1 = Path(c1); document_map = Path(document_map)
    info = json.loads(o5.read_text())
    reserved = info['document_assignment']['reserved']
    rows = list(read_rows(c1)) if c1.suffix == '.jsonl' else json.loads(c1.read_text())['documents']
    documents = json.loads(document_map.read_text())['documents']
    c1set = {r if isinstance(r, str) else r.get('source_doc_id', r.get('doc')) for r in rows}
    if not reserved or not c1set or None in c1set: raise ValueError('O5 and C1 documents must be explicit/nonempty')
    c1docs = sorted(c1set)
    resolve_exclusions(documents, set(reserved) | c1set)
    canonical = lambda docs: resolve_exclusions(documents, docs)
    hashes = sorted({r[k] for r in rows if isinstance(r, dict)
                     for k in ('document_sha256', 'pdf_sha256') if r.get(k)})
    result = dict(schema='o4b-documents-v1', reviewed=reviewed, documents=documents,
        cohorts={'O5_E1_test': dict(documents=canonical(reserved), evidence=str(o5.resolve()), source_sha256=sha256(o5)),
                 'C1': dict(documents=canonical(c1docs), sha256=hashes, evidence=str(c1.resolve()), source_sha256=sha256(c1))},
        work_map_sha256=sha256(document_map),
        identity_review='coordinator must group mirrors/serial volumes/editions of the same held-out work before --reviewed')
    write_json(out, result)
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--o5-info', type=Path, required=True); p.add_argument('--c1', type=Path, required=True)
    p.add_argument('--document-map', type=Path, required=True); p.add_argument('--out', type=Path, required=True)
    p.add_argument('--reviewed', action='store_true', help='coordinator attests canonical identities and exclusion evidence')
    a = p.parse_args(argv); build(a.o5_info, a.c1, a.document_map, a.out, a.reviewed)


if __name__ == '__main__': main()
