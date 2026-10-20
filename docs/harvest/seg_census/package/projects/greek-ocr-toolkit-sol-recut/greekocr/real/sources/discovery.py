"""O4c metadata crawls retain robots, rate state and transfer-ledger semantics."""
from __future__ import annotations
import importlib
from pathlib import Path
import subprocess
import sys
from typing import Sequence
from greekocr.types import PathLike, Record, DiscoveryHTTP
__all__ = ['parse_source', 'discovery_command', 'run_discovery', 'http_client']
_MODULES = {name: f'greekocr._vendor.scripts.fetch.o4c_discover_{name}'
            for name in ('parliament', 'archive', 'anemi', 'wikimedia', 'other')}


def parse_source(source: str, metadata: Record, *, identifier: str = '', language: str = 'el') -> Record:
    """Parse recorded metadata only; never infer confirmed rights or gold labels."""
    module = importlib.import_module(_MODULES[source])
    if source == 'parliament': return module.parse_record(metadata)
    if source == 'archive': return module.parse_item(identifier, metadata)
    if source == 'wikimedia': return module.parse_file(metadata, language)
    raise ValueError('Anemi/other require the native catalogue parser; use http_client or run_discovery')


def discovery_command(source: str, out: PathLike, *, offline: bool = True,
                      args: Sequence[str] = (), python: PathLike = sys.executable,
                      evidence_root: PathLike | None = None, timeout: float = 1800) -> list[str]:
    if source not in _MODULES: raise ValueError('unknown discovery source: '+source)
    output = Path(out).resolve()
    return [str(python), '-m', 'greekocr.real.sources._runner', source, '--evidence-root',
            str(Path(evidence_root).resolve() if evidence_root is not None else output.parent),
            '--timeout', str(timeout), '--', '--out', str(output),
            *(['--offline'] if offline else []), *args]


def run_discovery(source: str, out: PathLike, *, offline: bool = True,
                  args: Sequence[str] = (), timeout: float = 1800,
                  evidence_root: PathLike | None = None) -> subprocess.CompletedProcess[str]:
    """Run native CLI on a worker; arguments include original bounded crawl controls."""
    return subprocess.run(discovery_command(source, out, offline=offline, args=args,
                          evidence_root=evidence_root, timeout=timeout),
                          text=True, capture_output=True, check=True, timeout=timeout+5)


def http_client(source: str, root: PathLike, *, offline: bool = True, interval: float = 2,
                budget: int = 2_000_000_000) -> DiscoveryHTTP:
    """Expose the preserved rate-lock/cache/ledger transport with an explicit root."""
    if source == 'anemi':
        from greekocr._vendor.scripts.fetch.o4c_discover_anemi import AnemiHTTP
        if budget != 2_000_000_000 and budget != 1_500_000_000:
            raise ValueError('Anemi fixes its budget at 1.5 GB')
        return AnemiHTTP(offline=offline, interval=interval, root=Path(root))
    from greekocr._vendor.scripts.fetch.o4c_common import HTTP
    return HTTP(source, offline, interval, budget, Path(root))
