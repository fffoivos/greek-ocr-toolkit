"""Extract body text from TEI XML tarballs (Perseus canonical-greekLit, First1KGreek) to jsonl lines.

    python -m greekocr.labelfix.tei_extract --tarball <repo-SHA>.tar.gz --key perseus_greeklit \
        --license CC-BY-SA-4.0 --out /tmp/labelfix-raw/perseus_greeklit_lines.jsonl

Policy (recorded in every output record as `tei_policy`):
  - Greek files only: path contains `grc` (Perseus/First1K name files `*.grc1.xml`, `*.grc2.xml`).
  - text = the TEI `<body>` only (no teiHeader, no front/back matter).
  - `<choice>` resolves to the ORIGINAL branch: `<sic>` / `<orig>` / `<abbr>` kept, `<corr>` /
    `<reg>` / `<expan>` dropped — the lexicon must attest what editions print, not editors' fixes.
  - `<note>`, `<bibl>`, `<ref>`, `<foreign>`, `<app>`'s readings other than `<lem>`, `<del>`, `<gap>`,
    `<pb>/<lb>/<milestone>` content are dropped; `<lem>` of an apparatus is kept.
  - One output line per text-bearing block (`<p>`, `<l>`, `<ab>`, `<s>`, `<head>`, `<cit>`, `<q>`,
    `<said>`, `<sp>`, `<div>` leaf text), whitespace collapsed, lines < 3 characters skipped.
"""
from __future__ import annotations

import argparse
import json
import re
import tarfile
import time
import xml.etree.ElementTree as ET

TEI = '{http://www.tei-c.org/ns/1.0}'
DROP = {'note', 'bibl', 'ref', 'foreign', 'del', 'gap', 'corr', 'reg', 'expan', 'rdg', 'teiHeader', 'front', 'back',
        'figDesc', 'fw', 'speaker', 'label', 'index', 'interp', 'supplied'}
BLOCKS = {'p', 'l', 'ab', 's', 'head', 'cit', 'q', 'said', 'sp', 'item', 'quote', 'lg', 'div'}
POLICY = 'body-only; choice->sic/orig/abbr (corr/reg/expan dropped); app->lem; notes/refs/foreign/del/gap dropped; supplied dropped'


def _strip_ns(tag: str) -> str:
    return tag.split('}', 1)[1] if '}' in tag else tag


def text_of(el) -> str:
    """Recursive text with the policy above."""
    tag = _strip_ns(el.tag)
    if tag in DROP:
        return (el.tail or '')
    if tag == 'choice':
        keep = None
        for child in el:
            if _strip_ns(child.tag) in ('sic', 'orig', 'abbr'):
                keep = child
                break
        return ((text_of(keep) if keep is not None else '') + (el.tail or ''))
    out = [el.text or '']
    for child in el:
        out.append(text_of(child))
    out.append(el.tail or '')
    return ''.join(out)


def blocks(body):
    """Yield text of leaf-most block elements."""
    for el in body.iter():
        tag = _strip_ns(el.tag)
        if tag not in BLOCKS:
            continue
        if any(_strip_ns(c.tag) in BLOCKS for c in el.iter() if c is not el):
            continue
        t = text_of(el)
        t = re.sub(r'\s+', ' ', t).strip()
        if len(t) >= 3:
            yield t


def extract(tarball: str, key: str, license_: str, out: str, log=print) -> dict:
    n_files = n_lines = n_err = 0
    t0 = time.time()
    with tarfile.open(tarball, 'r:gz') as tf, open(out, 'w', encoding='utf-8') as fh:
        for m in tf:
            if not m.isfile() or not m.name.endswith('.xml') or 'grc' not in m.name.rsplit('/', 1)[-1]:
                continue
            if '__cts__' in m.name:
                continue
            f = tf.extractfile(m)
            if f is None:
                continue
            try:
                root = ET.parse(f).getroot()
            except ET.ParseError:
                n_err += 1
                continue
            body = root.find(f'.//{TEI}body')
            if body is None:
                body = root.find('.//body')
            if body is None:
                continue
            n_files += 1
            doc = m.name.split('/', 1)[-1]
            for t in blocks(body):
                fh.write(json.dumps(dict(text=t, source_dataset=key, source_doc_id=doc, license=license_,
                                         provenance='born_digital', tei_policy=POLICY), ensure_ascii=False) + '\n')
                n_lines += 1
            if n_files % 500 == 0:
                log(f'[tei:{key}] {n_files} files, {n_lines} lines ({time.time() - t0:.0f}s)')
    meta = dict(key=key, tarball=tarball, files=n_files, lines=n_lines, parse_errors=n_err, policy=POLICY,
                seconds=round(time.time() - t0))
    log(f'[tei:{key}] done: {meta}')
    return meta


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--tarball', required=True)
    ap.add_argument('--key', required=True)
    ap.add_argument('--license', default='CC-BY-SA-4.0')
    ap.add_argument('--out', required=True)
    a = ap.parse_args(argv)
    meta = extract(a.tarball, a.key, a.license, a.out, log=lambda s: print(s, flush=True))
    with open(a.out + '.meta.json', 'w') as fh:
        json.dump(meta, fh, indent=1)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
