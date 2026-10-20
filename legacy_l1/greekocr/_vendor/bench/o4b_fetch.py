"""Coordinator-only HTTPS fetch, metadata inventory, checksums and safe unpacking."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tarfile
import zipfile
from pathlib import Path
from urllib.parse import quote, urlparse
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from greekocr._vendor.bench.common import sha256, write_json
from greekocr._vendor.bench.o4b_common import rights

AGENT = 'GreekPageOCR-O4b/1.0 (research dataset acquisition; coordinator controlled)'


def fetch(url, dest, checksum=None):
    if urlparse(url).scheme != 'https': raise ValueError('HTTPS required')
    dest = Path(dest); dest.parent.mkdir(parents=True, exist_ok=True)
    algorithm, expected = checksum.split(':', 1) if checksum else ('sha256', None)
    if algorithm not in ('sha256', 'md5'): raise ValueError('checksum must be sha256: or md5:')
    if expected and not re.fullmatch('[0-9a-fA-F]{'+str(64 if algorithm == 'sha256' else 32)+'}', expected):
        raise ValueError('checksum must be a complete hexadecimal digest')
    if expected: expected = expected.lower()
    if dest.exists():
        digest = hashlib.new(algorithm)
        with dest.open('rb') as f:
            for block in iter(lambda: f.read(1024*1024), b''): digest.update(block)
        actual = digest.hexdigest()
        if expected and actual != expected: raise ValueError('existing file checksum mismatch: '+str(dest))
        if not expected: raise ValueError('existing download needs a bound checksum')
        return dict(url=url, path=str(dest.resolve()), sha256=sha256(dest), upstream_checksum=checksum, resumed=True)
    temp = dest.with_name(dest.name+'.partial')
    digest = hashlib.new(algorithm)
    with urlopen(Request(url, headers={'User-Agent': AGENT}), timeout=90) as response, temp.open('wb') as output:
        for block in iter(lambda: response.read(1024*1024), b''):
            output.write(block); digest.update(block)
    if expected and digest.hexdigest() != expected:
        raise ValueError('download checksum mismatch; partial retained: '+str(temp))
    temp.replace(dest)
    return dict(url=url, path=str(dest.resolve()), sha256=sha256(dest), upstream_checksum=checksum, resumed=False)


def metadata(url, dest):
    # A metadata snapshot is refreshed explicitly, while payloads are immutable.
    with urlopen(Request(url, headers={'User-Agent': AGENT}), timeout=90) as response:
        data = json.load(response)
    write_json(dest, data)
    return data


def unpack(path, out):
    out = Path(out).resolve(); out.mkdir(parents=True, exist_ok=True)
    def check(name):
        p = (out/name).resolve()
        if not p.is_relative_to(out): raise ValueError('archive path escape: '+name)
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            for member in archive.infolist():
                check(member.filename)
                if (member.external_attr >> 16) & 0o170000 == 0o120000: raise ValueError('archive symlink')
            archive.extractall(out)
    elif tarfile.is_tarfile(path):
        with tarfile.open(path) as archive:
            members = archive.getmembers()
            for member in members:
                check(member.name)
                if not (member.isfile() or member.isdir()): raise ValueError('archive link or special file')
            archive.extractall(out, members=members)
    else:
        raise ValueError('not a supported archive; keep native file for conversion')


def discover(out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    commit = metadata('https://api.github.com/repos/kperi/Kalchas/commits/HEAD', out/'kalchas_commit.json')['sha']
    repo = metadata('https://api.github.com/repos/kperi/Kalchas/git/trees/'+commit+'?recursive=1', out/'kalchas_tree.json')
    licence = metadata('https://api.github.com/repos/kperi/Kalchas/license', out/'kalchas_code_licence.json')
    # README/data links must be reviewed: Apache code licence does not license external scans.
    for item in repo.get('tree', []):
        if item['path'].lower() in ('readme.md', 'license', 'license.txt'):
            dest = out/'kalchas'/commit/item['path']
            receipt_path = dest.with_name(dest.name+'.receipt.json')
            checksum = 'sha256:'+json.loads(receipt_path.read_text())['sha256'] if receipt_path.exists() else None
            receipt = fetch('https://raw.githubusercontent.com/kperi/Kalchas/'+commit+'/'+item['path'], dest, checksum)
            write_json(receipt_path, receipt)
    zenodo = metadata('https://zenodo.org/api/records/22232579', out/'cllg_zenodo.json')
    inventory = dict(kalchas_commit=commit, kalchas_code_licence=licence.get('license'),
                     kalchas_archive_url='https://codeload.github.com/kperi/Kalchas/tar.gz/'+commit,
                     cllg_metadata=zenodo.get('metadata'), cllg_files=zenodo.get('files', []),
                     grpoly_reference='https://www.cs.uoi.gr/~sfikas/2015GatosICDAR.pdf',
                     status='review image/transcription licences, corpus availability and formats before download')
    write_json(out/'inventory.json', inventory)
    return inventory


def datasets(manifest, out):
    rows = json.loads(Path(manifest).read_text())['downloads']
    receipts = []
    for row in rows:
        rights(row)
        if not row.get('checksum'): raise ValueError('published payload needs a pinned checksum')
        if not re.fullmatch(r'[A-Za-z0-9_.-]+', row['filename']): raise ValueError('unsafe filename')
        dest = Path(out)/row['source_dataset']/row['filename']
        receipt = fetch(row['url'], dest, row['checksum'])
        if row.get('unpack'): unpack(dest, dest.parent/'unpacked')
        receipt.update({k: row[k] for k in ('source_dataset', 'licence', 'attribution', 'licence_evidence', 'source_url')})
        receipts.append(receipt)
        write_json(dest.parent/'download_receipt.json', receipts)
    write_json(Path(out)/'fetch_receipt.json', dict(manifest_sha256=sha256(manifest), downloads=receipts))


def archive(ids, out, inventory_only=False):
    """Candidate TSV is inert until verified=yes with rights evidence and attribution."""
    import csv
    results = []
    for row in csv.DictReader(Path(ids).open(encoding='utf-8'), delimiter='\t'):
        ident = row['identifier']
        if not re.fullmatch(r'[A-Za-z0-9_.-]+', ident): raise ValueError('unsafe IA identifier')
        if row.get('verified') != 'yes' and not inventory_only:
            results.append(dict(identifier=ident, status='skipped_unverified')); continue
        dest = Path(out)/ident
        try:
            data = metadata('https://archive.org/metadata/'+quote(ident), dest/'ia_metadata.json')
        except (HTTPError, URLError, OSError, ValueError) as error:
            data = {}; results.append(dict(identifier=ident, status='metadata_error', error=str(error)))
        if data.get('is_dark') or not data.get('files'):
            candidate = dict(identifier=ident, status='unavailable')
            if inventory_only and row.get('search_query'):
                url = 'https://archive.org/advancedsearch.php?'+urlencode(dict(q=row['search_query'], output='json', rows=10,
                    **{'fl[]': 'identifier,title,date,language'}))
                try:
                    search = metadata(url, dest/'search_results.json')
                    candidate['search_matches'] = search.get('response', {}).get('docs', [])
                except (HTTPError, URLError, OSError, ValueError) as error:
                    candidate['search_error'] = str(error)
            results.append(candidate); continue
        files = [f for f in data['files'] if f.get('name', '').lower().endswith(('.pdf', '.djvu'))]
        if inventory_only:
            results.append(dict(identifier=ident, status='inventory_only', metadata=data.get('metadata'), files=files)); continue
        review = dict(rights_reviewed=True, licence=row['licence'], source_url='https://archive.org/details/'+ident,
                      attribution=row['attribution'], licence_evidence=row['licence_evidence'])
        rights(review)
        # Coordinator selects an exact derivative; prefer searchable PDFs, never infer a text layer from extension.
        wanted = row.get('filename')
        if not wanted: raise ValueError('verified archive row needs exact filename: '+ident)
        selected = [f for f in files if f['name'] == wanted]
        if len(selected) != 1 or not selected[0].get('md5'): raise ValueError('missing selected file/IA checksum')
        target = dest/Path(wanted).name
        receipt = fetch('https://archive.org/download/'+quote(ident)+'/'+quote(wanted, safe=''), target, 'md5:'+selected[0]['md5'])
        receipt.update(review, source_dataset='internet_archive', source_doc_id='ia:'+ident, identifier=ident,
                       script=row['script'], input_path=str(target.resolve()), metadata_sha256=sha256(dest/'ia_metadata.json'))
        write_json(dest/'source.json', receipt); results.append(receipt)
    write_json(Path(out)/'archive_receipt.json', dict(ids_sha256=sha256(ids), items=results))
    return results


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='action', required=True)
    d = sub.add_parser('discover'); d.add_argument('--out', type=Path, required=True)
    d = sub.add_parser('datasets'); d.add_argument('--manifest', type=Path, required=True); d.add_argument('--out', type=Path, required=True)
    d = sub.add_parser('archive'); d.add_argument('--ids', type=Path, required=True); d.add_argument('--out', type=Path, required=True)
    d.add_argument('--inventory-only', action='store_true')
    a = p.parse_args(argv)
    if a.action == 'discover': discover(a.out)
    elif a.action == 'datasets': datasets(a.manifest, a.out)
    else: archive(a.ids, a.out, a.inventory_only)


if __name__ == '__main__': main()
