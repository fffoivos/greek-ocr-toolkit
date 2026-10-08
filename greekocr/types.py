"""Shared small contracts for public APIs."""
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol, Sequence, TypeAlias

PathLike: TypeAlias = str | Path
Record: TypeAlias = dict[str, Any]
CropReader: TypeAlias = Callable[[Path], str]

class Reader(Protocol):
    binding: Mapping[str, Any]
    def read(self, path: PathLike) -> str: ...

class BatchReader(Reader, Protocol):
    last_batch_ms: float | None
    def read_batch(self, paths: Sequence[PathLike]) -> list[str]: ...
    def close(self) -> None: ...

class NativeReference(Protocol):
    binding: Mapping[str, Any]
    def preprocess(self, path: PathLike) -> Any: ...
    def endpoints(self, tensor: Any) -> Mapping[str, Any]: ...

class DiscoveryHTTP(Protocol):
    root: Path
    offline: bool
    interval: float
    budget: int
    ledger: Path
    transferred: int
    requests: int
    def get(self, url: str, limit: int = 8_000_000, range_header: str | None = None) -> tuple[Record, bytes]: ...
    def json(self, url: str) -> Any: ...
