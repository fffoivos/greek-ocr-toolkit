"""Lazy local readers and explicitly enabled service hooks."""
from .ours import load_ours
from .kalchas import load_kalchas
from .cllg import load_cllg, load_cllg_worker, build_cllg_contract
from .paddle_r01 import load_paddle_r01, load_r03
from .services import load_service
__all__ = ['load_ours', 'load_kalchas', 'load_cllg', 'load_cllg_worker', 'build_cllg_contract',
           'load_paddle_r01', 'load_r03', 'load_service']
