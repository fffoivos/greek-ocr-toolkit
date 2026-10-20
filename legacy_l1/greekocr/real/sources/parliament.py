"""Byte-identical Parliament fetch scripts, staged with explicit input/output paths."""
from __future__ import annotations
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from greekocr.types import PathLike, Record
from greekocr._vendor.train.mix import sha256
__all__ = ['refetch_pdf_cache', 'stage_parliament']
_VENDOR = Path(__file__).resolve().parents[2] / '_vendor'


def refetch_pdf_cache(manifest: PathLike, out: PathLike, *, timeout: float = 1800) -> list[Record]:
    """Preserve three attempts and hash-before-publication; return verified file receipts."""
    directory = Path(out).resolve()
    records = [json.loads(s) for s in Path(manifest).read_text().splitlines() if s.strip()]
    with tempfile.TemporaryDirectory(prefix='greekocr-refetch-') as stage:
        root = Path(stage)
        script = root/'scripts/fetch/parliament_pdf_cache.py'
        script.parent.mkdir(parents=True)
        shutil.copyfile(_VENDOR/'scripts/fetch/parliament_pdf_cache.py', script)
        evidence = root/'docs/evidence/s17/pdf_cache_refetch.jsonl'
        evidence.parent.mkdir(parents=True)
        shutil.copyfile(manifest, evidence)
        subprocess.run([sys.executable, str(script), str(directory)], check=True, timeout=timeout)
    result = []
    for record in records:
        path = directory/(record['pdf_cache_sha256']+'.pdf')
        if sha256(path) != record['pdf_cache_sha256']: raise ValueError('PDF cache checksum mismatch')
        result.append(dict(record, local_path=str(path), bytes=path.stat().st_size, sha256=sha256(path)))
    return result


def stage_parliament(candidate_root: PathLike, out: PathLike, *, timeout: float = 1800) -> list[Record]:
    """Ranked S2 staging, with original MD5-match flags and SHA-256 receipts."""
    subprocess.run([sys.executable, str(_VENDOR/'seed/node_scripts/fetch_parliament_s2.py'),
                    str(Path(candidate_root).resolve()), str(Path(out).resolve())], check=True, timeout=timeout)
    return [json.loads(s) for s in (Path(out)/'receipts.jsonl').read_text().splitlines() if s.strip()]
