"""Provenance, bounded liveness, rate locking and environment secrets."""
from importlib import import_module
from .secrets import require_env
from .watch import Observation, WatchResult, watch, bounded_ssh

__all__ = ['file_sha256', 'verify_files', 'write_receipt', 'require_env', 'rate_limited_client',
           'Observation', 'WatchResult', 'watch', 'bounded_ssh']


def __getattr__(name):
    # data_root must import without a receipt/vendor cycle or optional OCR
    # dependencies. Preserve the existing public helpers on first access.
    modules = {'file_sha256': 'receipts', 'verify_files': 'receipts',
               'write_receipt': 'receipts', 'rate_limited_client': 'rate_limit'}
    if name not in modules:
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}')
    module = import_module(f'{__name__}.{modules[name]}')
    for public, source in modules.items():
        if source == modules[name]:
            globals()[public] = getattr(module, public)
    return globals()[name]
