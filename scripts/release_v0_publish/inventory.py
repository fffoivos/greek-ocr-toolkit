"""Reviewable public working-tree inventory; no git command or metadata writes.

Candidates = rg's nonignored files (including hidden files, local .gitignore rules)
UNION existing tracked paths read directly from the index and ignored private candidates. Metadata is never walked.
Default output is PUBLIC_INVENTORY.tsv beside this script. No files are deleted.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import math
from collections import Counter
import json
import os
from pathlib import Path, PurePosixPath
import re
import struct
import subprocess
import tarfile
import zipfile

MAX_BYTES = 5_000_000
# Any receipt tree whose directory name starts receipts_ and contains smoke.
BULK = re.compile(r'^receipts_.*smoke', re.I)
# Only value-shaped credentials; source expressions and field names are not secrets.
SECRETS = re.compile(
    rb'(?<![A-Za-z0-9_])(?:hf_[A-Za-z0-9]{30,}|gh[pousr]_[A-Za-z0-9]{30,}|'
    rb'github_pat_[A-Za-z0-9_]{30,}|sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}|'
    rb'(?:AKIA|ASIA)[A-Z0-9]{16})(?![A-Za-z0-9_])|'
    rb'-----BEGIN (?:[A-Z0-9]+ )*PRIVATE KEY-----'
)
ASSIGNMENT = re.compile(
    rb'''(?i:["']?\b(?:(?:[a-z0-9]{1,24}_){0,4}(?:token|password|passwd|secret|api_key|apikey)(?:_value)?)["']?\s*[:=]\s*)(["'])([^"'\r\n]{24,})\1'''
)


def scan_bytes(data):
    """Report locations only, never matched literal values."""
    markers = (b'hf_', b'ghp_', b'gho_', b'ghu_', b'ghs_', b'ghr_', b'github_pat_',
               b'sk-', b'private key', b'akia', b'asia', b'token', b'password',
               b'passwd', b'secret', b'api_key', b'apikey')
    lower = data.lower()
    if not any(marker in lower for marker in markers):
        return []
    lines = []
    for n, line in enumerate(data.split(b'\n'), 1):
        lowline = line.lower()
        if not any(marker in lowline for marker in markers):
            continue
        literal = any(len(set(m[2])) >= 12 and
                      -sum((v/len(m[2])) * math.log2(v/len(m[2]))
                           for v in Counter(m[2]).values()) >= 3.5
                      and not any(x in m[2] for x in (b' ', b'${', b'\\', b'(', b')'))
                      for m in ASSIGNMENT.finditer(line))
        if SECRETS.search(line) or literal:
            lines.append(n)
    return lines


def google_object(value):
    """A decoded Document AI/Vision response, including batch/REST wrappers."""
    if isinstance(value, list):
        return bool(value) and any(google_object(x) for x in value)
    if not isinstance(value, dict):
        return False
    if isinstance(value.get('fullTextAnnotation'), dict) or isinstance(value.get('textAnnotations'), list):
        return True
    pages = value.get('pages')
    if isinstance(value.get('text'), str) and isinstance(pages, list):
        def anchored(x):
            if isinstance(x, dict):
                return any(k in x for k in ('textAnchor', 'textSegments', 'detectedLanguages')) or any(anchored(v) for v in x.values())
            return isinstance(x, list) and any(anchored(v) for v in x)
        if any(anchored(page) for page in pages):
            return True
    return any(google_object(value[k]) for k in ('document', 'responses', 'response', 'documents') if k in value)


def google_content(data):
    try:
        return google_object(json.loads(data))
    except (ValueError, UnicodeError):
        for line in data.splitlines():
            try:
                if google_object(json.loads(line)):
                    return True
            except (ValueError, UnicodeError):
                continue
    return False


def private_rule(path):
    parts = PurePosixPath(path.lower().removesuffix('.gz')).parts
    if any(x == 'private' or x.endswith('_private') for x in parts[:-1]):
        return 'private directory component'
    if 'opus_keys' in parts and any('audit' in x for x in parts):
        return 'audit answer/deblinding tree opus_keys'
    if re.fullmatch(r'items_key.*\.json', parts[-1]):
        return 'audit answer/deblinding items_key JSON'
    if parts[-1] == 'key.jsonl' and any(any(x in p for x in ('audit', 'adjudication', 'cards')) for p in parts[:-1]):
        return 'audit/adjudication/cards key.jsonl'
    # Review mappings remain local wherever historical decks were stored.
    # Python source in a keys namespace is implementation, not a deck key.
    if 'keys' in parts[:-1] and PurePosixPath(path.lower()).suffix != '.py':
        return 'review deck key tree'
    if (parts[-1].endswith(('_key.json', '_key.jsonl')) or
            parts[-1] in ('key_sealed.json', 'blind_key.json', 'blind_pages_key.json', 'wl_key.json')):
        return 'review deck key file'
    if 'answers' in parts[:-1] and parts[-1].endswith('.mapped.jsonl'):
        return 'review answer join'
    return ''


def evidence_paths(root):
    path = Path(root)/'scripts/release_v0_publish/EVIDENCE_PATHS.txt'
    return set(path.read_text().splitlines()) if path.exists() else set()


def index_paths(root):
    """Read SHA-1 index v2/v3/v4 without invoking git; reject unknown/split formats."""
    dotgit = root/'.git'
    if not dotgit.exists():
        return set()
    gitdir = dotgit if dotgit.is_dir() else (root/dotgit.read_text().strip().removeprefix('gitdir: ')).resolve()
    index = gitdir/'index'
    if not index.exists():
        return set()
    data = index.read_bytes()
    signature, version, count = struct.unpack('>4sII', data[:12])
    if signature != b'DIRC' or version not in (2, 3, 4):
        raise ValueError('unsupported git index; explicit candidate list required')
    if hashlib.sha1(data[:-20]).digest() != data[-20:]:
        raise ValueError('index checksum mismatch')
    pos = 12; previous = b''; paths = set()
    for _ in range(count):
        start = pos
        flags = struct.unpack('>H', data[pos+60:pos+62])[0]
        mode = struct.unpack('>I', data[pos+24:pos+28])[0]
        if mode == 0o160000 or mode == 0o040000:
            raise ValueError('submodule/sparse index needs explicit public inventory review')
        pos += 62
        if flags & 0x4000:
            pos += 2
        if version == 4:
            strip = data[pos] & 0x7f
            while data[pos] & 0x80:
                pos += 1
                strip = ((strip+1) << 7) + (data[pos] & 0x7f)
            pos += 1
            end = data.index(b'\0', pos)
            name = previous[:len(previous)-strip] + data[pos:end]
            pos = end+1
        else:
            end = data.index(b'\0', pos)
            name = data[pos:end]
            pos = start + ((end+1-start+7)//8)*8
        previous = name
        path = os.fsdecode(name)
        if not path or '..' in PurePosixPath(path).parts or path.startswith('/'):
            raise ValueError('unsafe index path')
        paths.add(path)
    # Split indexes would hide entries in a shared index: fail instead of omitting.
    while pos < len(data)-20:
        key, size = struct.unpack('>4sI', data[pos:pos+8]); pos += 8
        if key == b'link':
            raise ValueError('split index unsupported; explicit candidates required')
        pos += size
    return paths


def candidates(root):
    found = subprocess.run(['rg', '--files', '--hidden', '--null', '--no-ignore-global',
                            '--no-ignore-parent', '-g', '!.git', '-g', '!**/.git/**'],
                           cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if found.returncode not in (0, 1):
        raise RuntimeError('rg candidate discovery failed')
    # Private review is complete even when a local ignore hides an answer-key tree.
    hidden = subprocess.run(['rg', '--files', '--hidden', '--null', '--no-ignore',
                             '-g', '!.git', '-g', '!**/.git/**'], cwd=root,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if hidden.returncode not in (0, 1):
        raise RuntimeError('private candidate discovery failed')
    private = {os.fsdecode(p) for p in hidden.stdout.split(b'\0') if p and private_rule(os.fsdecode(p))}
    return sorted(index_paths(root) | private | {os.fsdecode(p) for p in found.stdout.split(b'\0') if p})



def is_bulk(path):
    return any(BULK.match(part) for part in PurePosixPath(path).parts[:-1])


def content_checks(path, data):
    # Structured formats only for Google responses; code/docs may mention fields.
    matches = set(); google = False; review = ''
    budget = 50_000_000

    def inspect(name, payload, structured=False, depth=0):
        nonlocal budget, google, review
        budget -= len(payload)
        if budget < 0 or depth > 8:
            review = 'compressed payload exceeds review budget'; return
        matches.update(scan_bytes(payload))
        low = name.lower()
        if payload.startswith(b'\x1f\x8b'):
            with gzip.GzipFile(fileobj=io.BytesIO(payload)) as f:
                expanded = f.read(budget+1)
            inspect(name.removesuffix('.gz'), expanded, True, depth+1)
        elif low.endswith(('.tar', '.tar.gz', '.tgz')) or zipfile.is_zipfile(io.BytesIO(payload)):
            if zipfile.is_zipfile(io.BytesIO(payload)):
                with zipfile.ZipFile(io.BytesIO(payload)) as z:
                    for m in z.infolist():
                        if m.is_dir(): continue
                        if m.file_size > budget:
                            review = 'archive exceeds review budget'; return
                        if private_rule(m.filename): review = 'private archive member'
                        inspect(m.filename, z.read(m), depth=depth+1)
            else:
                with tarfile.open(fileobj=io.BytesIO(payload), mode='r:*') as t:
                    for m in t:
                        if not m.isfile(): continue
                        if m.size > budget:
                            review = 'archive exceeds review budget'; return
                        if private_rule(m.name): review = 'private archive member'
                        inspect(m.name, t.extractfile(m).read(), depth=depth+1)
        elif structured or low.endswith(('.json', '.jsonl', '.ndjson')):
            google = google or google_content(payload)
    try:
        inspect(path, data)
    except (OSError, EOFError, ValueError, tarfile.TarError, zipfile.BadZipFile):
        review = 'unreadable compressed payload'
    return sorted(matches), google, review


def output_rule(path, keep=()):
    parts = PurePosixPath(path).parts
    if not parts or parts[0] not in ('out', 'artifacts') or path in keep:
        return ''
    # out is run output by definition; only enumerated evidence travels publicly.
    if parts[0] == 'out':
        return 'bulk/test-run output under out; not enumerated release evidence'
    if any(re.match(r'(?:pytest(?:_|$)|pytest_tmp|mock(?:_|$)|test[_-]|output[_-])', p) or p.endswith('_test')
           for p in parts[1:-1]):
        return 'bulk/test-run output under artifacts'
    return ''


def inventory(root, *, paths=None, omit=(), progress=None):
    root = Path(root).resolve(); rows = []; matches = []
    keep = evidence_paths(root)
    for name in (candidates(root) if paths is None else sorted(set(paths))):
        if name in omit:
            continue  # generated inventories cannot hash themselves
        relative = PurePosixPath(name)
        if relative.is_absolute() or '..' in relative.parts or '.git' in relative.parts:
            raise ValueError('unsafe candidate path')
        p = root/name
        if not p.exists() and not p.is_symlink():
            continue  # tracked deletion is absent from the working snapshot
        reasons = []
        # Never dereference a link, including a linked ancestor, to private files.
        if any(x.is_symlink() for x in [p, *list(p.parents)[:len(relative.parts)-1]]):
            data = os.fsencode(os.readlink(p)) if p.is_symlink() else b''
            reasons.append('symlink; requires explicit public review')
            sha = hashlib.sha256(data).hexdigest(); size = len(data)
        else:
            if not p.is_file():
                continue
            before = p.stat()
            size = before.st_size
            h = hashlib.sha256()
            blocks = []; previous = b''; newlines = 0
            with p.open('rb') as f:
                for block in iter(lambda: f.read(1 << 20), b''):
                    h.update(block)
                    if size <= MAX_BYTES:
                        blocks.append(block)
                    else:
                        combined = previous + block
                        offset = newlines - previous.count(b'\n')
                        secret_lines = scan_bytes(combined)
                        matches.extend((name, offset+n) for n in secret_lines)
                        if secret_lines:
                            reasons.append('credential pattern')
                        previous = combined[-512:]
                        newlines += block.count(b'\n')
            after = p.stat()
            if (before.st_size, before.st_mtime_ns, before.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
                raise RuntimeError('working-tree file changed during inventory: '+name)
            sha = h.hexdigest()
            if size <= MAX_BYTES:
                data = b''.join(blocks)
                secret_lines, google, review = content_checks(name, data)
                if secret_lines:
                    reasons.append('credential pattern (content/member line)')
                    matches.extend((name, n) for n in secret_lines)
                if google:
                    reasons.append('raw Google response content')
                if review:
                    reasons.append(review)
        if size > MAX_BYTES:
            reasons.append('over 5000000 bytes')
        if is_bulk(name):
            reasons.append('bulk smoke receipt tree: receipts_*smoke* directory')
        for rule in (private_rule(name), output_rule(name, keep)):
            if rule:
                reasons.append(rule)
        if any(x in relative.parts for x in ('__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache')):
            reasons.append('cache')
        if any(x in relative.parts for x in ('.aws', '.ssh', '.codex', '.agents')) or p.name in ('.env', '.netrc', '.npmrc'):
            reasons.append('private operational material')
        rows.append(dict(path=name, bytes=size, sha256=sha, decision='exclude' if reasons else 'include',
                         reason='; '.join(dict.fromkeys(reasons)) or 'eligible working-tree file; review before publication'))
        if progress is not None and len(rows) % 5000 == 0:
            progress(len(rows))
    return rows, sorted(set(matches))


def write_tsv(path, rows, fields):
    with Path(path).open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter='\t', extrasaction='ignore')
        writer.writeheader(); writer.writerows(rows)


def write_inventory_outputs(output, rows, *, part_bytes=4_000_000):
    """Keep the complete local review TSV plus Git-sized review parts and receipt."""
    output = Path(output)
    fields = ['path', 'bytes', 'sha256', 'decision', 'reason']
    write_tsv(output, rows, fields)
    if output.stat().st_size <= MAX_BYTES:
        return
    directory = output.with_suffix('.parts')
    directory.mkdir(exist_ok=True)
    header_buffer = io.StringIO(newline='')
    csv.writer(header_buffer, delimiter='\t').writerow(fields)
    header = header_buffer.getvalue().encode('utf-8')
    parts = []; payload = bytearray(header)
    def flush():
        path = directory / ('part-%04d.tsv' % len(parts))
        path.write_bytes(payload)
        parts.append(dict(path=str(path.relative_to(output.parent)), bytes=len(payload),
                          sha256=hashlib.sha256(payload).hexdigest()))
    for row in rows:
        buffer = io.StringIO(newline='')
        csv.writer(buffer, delimiter='\t').writerow([row[key] for key in fields])
        encoded = buffer.getvalue().encode('utf-8')
        if len(header)+len(encoded) > part_bytes:
            raise ValueError('single inventory row exceeds part cap')
        if len(payload)+len(encoded) > part_bytes:
            flush(); payload = bytearray(header)
        payload.extend(encoded)
    if len(payload) > len(header):
        flush()
    receipt = dict(schema='greekocr-public-inventory-v1', rows=len(rows),
                   full_local_review=dict(path=output.name, bytes=output.stat().st_size,
                                          sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                                          public_git='excluded: over 5000000 bytes'),
                   parts=parts, part_byte_cap=part_bytes,
                   note='Rows cover payload; generated inventory metadata omits itself to avoid circular hashes. Only listed parts belong to this receipt; older surplus parts are not selected.')
    output.with_suffix('.receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')


def write_sharded_tsv(path, rows, fields):
    """An oversized review queue becomes a small index of complete TSV parts."""
    path = Path(path)
    write_tsv(path, rows, fields)
    if path.stat().st_size <= MAX_BYTES:
        return
    directory = path.with_suffix('.parts'); directory.mkdir(exist_ok=True)
    batch = []; size = 100; parts = []
    def flush():
        member = directory/f'part-{len(parts):04d}.tsv'
        write_tsv(member, batch, fields)
        payload = member.read_bytes()
        parts.append(dict(path=str(member.relative_to(path.parent)), bytes=len(payload),
                          sha256=hashlib.sha256(payload).hexdigest()))
    for row in rows:
        buffer = io.StringIO(newline='')
        csv.DictWriter(buffer, fieldnames=fields, delimiter='\t', extrasaction='ignore').writerow(row)
        length = len(buffer.getvalue().encode())
        if batch and size+length > 4_000_000:
            flush(); batch = []; size = 100
        batch.append(row); size += length
    if batch: flush()
    write_tsv(path, parts, ['path', 'bytes', 'sha256'])


def write_review_outputs(directory, rows):
    write_tsv(Path(directory)/'PRIVATE_REVIEW.tsv',
              [dict(r, rule=private_rule(r['path']) or r['reason']) for r in rows
               if r['decision'] == 'exclude' and (private_rule(r['path']) or 'private' in r['reason'])],
              ['path', 'bytes', 'sha256', 'rule'])
    write_tsv(Path(directory)/'INCLUDED_NAME_REVIEW.tsv',
              [r for r in rows if r['decision'] == 'include' and
               re.search(r'private|key|secret|token|password', r['path'], re.I)],
              ['path', 'bytes', 'sha256'])
    write_sharded_tsv(Path(directory)/'OUTPUT_REVIEW.tsv',
              [r for r in rows if PurePosixPath(r['path']).parts[0] in ('out', 'artifacts')],
              ['path', 'bytes', 'sha256', 'decision', 'reason'])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('PUBLIC_INVENTORY.tsv'))
    args = parser.parse_args(argv)
    output = args.output.resolve()
    omit = []
    if output.is_relative_to(args.root.resolve()):
        omit.append(output.relative_to(args.root.resolve()).as_posix())
        omit.append(output.with_suffix('.receipt.json').relative_to(args.root.resolve()).as_posix())
        omit.append(output.with_suffix('.credentials.tsv').relative_to(args.root.resolve()).as_posix())
        parts = output.with_suffix('.parts')
        if parts.exists():
            omit.extend(p.relative_to(args.root.resolve()).as_posix() for p in parts.rglob('*') if p.is_file())
    omit.extend(p.relative_to(args.root.resolve()).as_posix() for p in output.parent.glob('*REVIEW*') if p.is_file() and p.is_relative_to(args.root.resolve()))
    omit.extend(p.relative_to(args.root.resolve()).as_posix() for p in output.parent.glob('*REVIEW.parts/*') if p.is_file() and p.is_relative_to(args.root.resolve()))
    import sys
    rows, matches = inventory(args.root, omit=omit, progress=lambda n: print(f'inventoried={n}', file=sys.stderr, flush=True))
    write_inventory_outputs(output, rows)
    write_review_outputs(output.parent, rows)
    locations = output.with_suffix('.credentials.tsv')
    write_tsv(locations, [dict(path=path, line=line) for path, line in matches], ['path', 'line'])
    receipt_path = output.with_suffix('.receipt.json')
    if receipt_path.exists():
        receipt = json.loads(receipt_path.read_text())
        receipt['credential_locations'] = dict(path=locations.name, bytes=locations.stat().st_size,
                                              sha256=hashlib.sha256(locations.read_bytes()).hexdigest(),
                                              matches=len(matches))
        receipt_path.write_text(json.dumps(receipt, indent=2)+'\n')
    for path, line in matches:
        print(f'{path}:{line}')
    print(f'files={len(rows)} included={sum(r["decision"] == "include" for r in rows)} excluded={sum(r["decision"] == "exclude" for r in rows)} credential_locations={len(matches)}')


if __name__ == '__main__':
    main()
