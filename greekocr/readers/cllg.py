"""Published CLLG teacher and isolated persistent Kraken worker."""
from pathlib import Path
from greekocr.types import PathLike, Record, Reader, BatchReader
__all__ = ['load_cllg', 'load_cllg_worker', 'build_cllg_contract']

def load_cllg(spec: Record) -> Reader:
    from greekocr._vendor.bench.e2_teachers import CLLG, validate_files
    validate_files(spec)
    return CLLG(spec)


def load_cllg_worker(checkpoint: PathLike, contract: Record | None = None, *,
                     python: PathLike | None = None, timeout: float = 300) -> BatchReader:
    from greekocr._vendor.bench.e2_native import cllg_kraken
    return cllg_kraken(checkpoint, contract, python=python, timeout=timeout)


def build_cllg_contract(readme: PathLike, checkpoint: PathLike, out: PathLike) -> Record:
    from greekocr._vendor.bench.e2_cllg_contract import build_contract
    return build_contract(Path(readme), Path(checkpoint), Path(out))
