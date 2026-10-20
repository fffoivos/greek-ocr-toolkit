"""Dataset import and the sole real-training shard writer: linefactory import-real."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
from typing import Iterator
from greekocr.types import PathLike, Record
from greekocr._vendor.bench.o4b_import_datasets import convert, native_rows as _native_rows
from greekocr._vendor.train.mix import sha256, shard_inventory
__all__ = ['import_dataset', 'native_rows', 'import_real_shards']

def native_rows(spec: Record, root: PathLike) -> Iterator[Record]:
    """Parse reviewed dataset formats, retaining native paths and labels."""
    return _native_rows(spec, Path(root))


def import_dataset(manifest: PathLike, partition: PathLike, out: PathLike, *, seed: int = 20261007) -> Record:
    return convert(Path(manifest), Path(partition), Path(out), seed)


def import_real_shards(records: PathLike, crops: PathLike, binary: PathLike, out: PathLike, *,
                       partition: str, timeout: float = 3600) -> Record:
    directory = Path(out).resolve()
    if directory.exists() and any(directory.iterdir()): raise ValueError('use a fresh output directory')
    subprocess.run([str(Path(binary).expanduser().absolute()), 'import-real', '--records',
                    str(Path(records).resolve()), '--crops', str(Path(crops).resolve()), '--out',
                    str(directory), '--partition', partition], check=True, timeout=timeout)
    info = json.loads((directory/'build_info.json').read_text())
    if info.get('kind') != 'real' or info.get('partition_id') != partition:
        raise ValueError('real import kind/partition receipt mismatch')
    if not info.get('shard_sha256') or info['shard_sha256'] != shard_inventory(directory):
        raise ValueError('real shard inventory mismatch')
    if info.get('word_tags_sha256') != sha256(directory/'word_tags.jsonl'):
        raise ValueError('real word-tag sidecar mismatch')
    return info
