"""Isolated independent-reader batches, public-only copies and hash receipts."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from importlib.resources import files
from ._files import contained, dump, hashes, sha
from .deck import leak_scan
from .protocol import deal, INSTRUCTIONS, ANSWER_SCHEMA

__all__ = ['deal_batches']
_PUBLIC = {'id','img','line_img','mark_img','options','other_options','A','B','C','anchor_index','target_head'}


def deal_batches(deck: str | Path, output: str | Path, *, batch_size: int = 110, readers: tuple[int, ...] = (1,2)) -> dict:
    """Copy public cards/images into independent new folders; reader 2 reverses.

    A folder contains only assigned cards and referenced images, no key, absolute
    path, symlink or link to another batch. Hash receipts bind every file.
    Isolation is the assigned-tree boundary; filesystem confinement must be set
    by the reader launcher (a tool cannot revoke a process's existing access).
    Split first, reverse each matching batch for reader 2, preserving coverage.
    """
    source, output = Path(deck).resolve(), Path(output).absolute()
    if type(batch_size) is not int or batch_size<=0 or not readers or len(set(readers))!=len(readers) or set(readers)-{1,2,3}:
        raise ValueError('positive batch size and distinct readers 1/2/3 required')
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    if output.is_relative_to(source) or source.is_relative_to(output):
        raise ValueError('assignments must be separate from source tree')
    manifest = contained(source,'items_blind.json')
    cards = json.loads(manifest.read_text())
    if not cards or len({c['id'] for c in cards})!=len(cards):
        raise ValueError('empty/duplicate deck identities')
    for c in cards:
        if set(c)-_PUBLIC:
            raise ValueError('private or unsupported public card fields')
        for field in ('img','line_img','mark_img'):
            if field in c:
                p = contained(source,c[field])
                if p.suffix!='.png' or p.stem!=sha(p):
                    raise ValueError('image must be a content-hashed PNG')
    output.parent.mkdir(parents=True,exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.deal-',dir=output.parent))
    receipt = dict(version=1, source_manifest_sha256=sha(manifest), batch_size=batch_size, batches=[])
    try:
        for offset in range(0,len(cards),batch_size):
            batch = cards[offset:offset+batch_size]
            for reader in readers:
                name = f'b{offset//batch_size:03d}/r{reader}'
                folder = stage/name
                folder.mkdir(parents=True)
                assigned = deal(batch,reader)
                for c in assigned:
                    for field in ('img','line_img','mark_img'):
                        if field in c:
                            dst = contained(folder,c[field]);dst.parent.mkdir(parents=True,exist_ok=True)
                            shutil.copyfile(contained(source,c[field]),dst)
                dump(folder/'items_blind.json',assigned)
                dump(folder/'answer_schema.json',ANSWER_SCHEMA)
                # Each folder's manifest is already in its assigned reader order.
                instructions = INSTRUCTIONS.split('Reader 1 follows')[0]+'Follow items_blind.json in its assigned order.\n'
                (folder/'README.md').write_text(instructions)
                js = files('greekocr.adjudicate').joinpath('deck.js').read_text().replace("const reader = new URLSearchParams(location.search).get('reader') === '2' ? 2 : 1;",f'const reader = {reader};').replace("const cards = reader === 2 ? [...manifest].reverse() : manifest;",'const cards = manifest;')
                payload = json.dumps(assigned,ensure_ascii=False).replace('</','<\\/')
                digest = hashlib.sha256(payload.encode()).hexdigest()
                (folder/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Independent reading</title><body data-deck="'+digest+'"><h1 id="assignment"></h1><button id="export">Export answers</button><main id="cards"></main><script id="manifest" type="application/json">'+payload+'</script><script>'+js+'</script>')
                scan = leak_scan(folder)
                if not scan['passed']:
                    raise ValueError('assignment leak scan failed: '+str(scan))
                receipt['batches'].append(dict(folder=name,reader=reader,ids=[c['id'] for c in assigned],files=hashes(folder),leak_scan=scan))
        dump(stage/'deal_receipt.json',receipt)
        if output.exists():
            raise FileExistsError(output)
        stage.rename(output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return receipt
