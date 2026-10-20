"""CP7 helper binding, independent of unrelated top-level ``common`` imports.

Keep common.py intact because historical freezes refer to its bytes.
"""
import importlib.util as _util
from pathlib import Path as _Path

_spec = _util.spec_from_file_location("_cp7_common_impl", _Path(__file__).with_name("common.py"))
_module = _util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
globals().update({k: v for k, v in vars(_module).items() if not k.startswith("_")})
