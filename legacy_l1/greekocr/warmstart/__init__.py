"""Exact donor conversion and independent native preprocessing/logit parity."""
from __future__ import annotations
from typing import Any, Mapping
from pathlib import Path
from PIL import Image
from greekocr.types import PathLike, Record
__all__ = ['map_donor_state', 'map_paddle_state', 'preprocess', 'compare_endpoints', 'convert_donor', 'verify_init', 'qualify_parity']

def map_donor_state(family: str, state: Mapping[str, Any]) -> tuple[Record, Record, list[str]]:
    from greekocr._vendor.bench.e2_warmstart import mapping
    return mapping(family, state)


def map_paddle_state(state: Mapping[str, Any], layer_map: Record, expected: Mapping[str, Any]) -> Record:
    from greekocr._vendor.bench.e2_warmstart import paddle_map
    return paddle_map(state, layer_map, expected)


def preprocess(image: Image.Image, contract: Record) -> Any:
    from greekocr._vendor.bench.e2_models import preprocess as native
    return native(image, contract)


def compare_endpoints(native: Mapping[str, Any], converted: Mapping[str, Any]) -> Record:
    from greekocr._vendor.bench.e2_parity import compare
    return compare(native, converted)


def convert_donor(family: str, checkpoint: PathLike, config: PathLike, out: PathLike,
                  revision: str, *, codec: PathLike, seed: int = 0) -> Record:
    from greekocr._vendor.bench.e2_warmstart import convert
    return convert(family, Path(checkpoint), Path(config), Path(out), revision, seed=seed, codec=Path(codec))


def verify_init(path: PathLike) -> Record:
    from greekocr._vendor.bench.e2_warmstart import verify_init as verify
    return verify(Path(path))


def qualify_parity(spec: Record, converted: PathLike, crops: PathLike, out: PathLike) -> Record:
    from greekocr._vendor.bench.e2_parity import parity
    return parity(spec, Path(converted), Path(crops), Path(out))
