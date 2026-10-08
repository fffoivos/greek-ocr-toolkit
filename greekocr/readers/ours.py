"""Evaluation-native own recognizer; raw NFD decoding and uint8 halo padding."""
from greekocr.types import PathLike, Reader
__all__ = ['load_ours']

def load_ours(checkpoint: PathLike, codec: PathLike) -> Reader:
    from greekocr._vendor.bench.e2_reader_parity import E1Reader
    return E1Reader(checkpoint, codec, 'cpu')
