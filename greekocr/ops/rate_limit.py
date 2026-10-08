"""Preserved cross-process O4c rate state, budgets and body-hash ledger."""
from greekocr.types import PathLike, DiscoveryHTTP
from greekocr.real.sources.discovery import http_client
__all__ = ['rate_limited_client']

def rate_limited_client(source: str, root: PathLike, *, offline: bool = True,
                        interval: float = 2, budget: int = 2_000_000_000) -> DiscoveryHTTP:
    return http_client(source, root, offline=offline, interval=interval, budget=budget)
