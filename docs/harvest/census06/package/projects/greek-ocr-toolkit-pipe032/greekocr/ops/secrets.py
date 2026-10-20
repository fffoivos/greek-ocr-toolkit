"""Secrets are read from the caller environment and never written into receipts."""
from __future__ import annotations
import os
from typing import Mapping, Sequence
__all__ = ['require_env']

def require_env(names: Sequence[str], *, env: Mapping[str, str] | None = None) -> dict[str, str]:
    source = os.environ if env is None else env
    missing = [key for key in names if not source.get(key)]
    if missing: raise ValueError('missing environment variables: ' + ', '.join(missing))
    return {key: source[key] for key in names}
