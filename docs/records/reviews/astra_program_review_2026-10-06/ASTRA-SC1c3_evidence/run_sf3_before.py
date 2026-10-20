import sys,importlib.util,pytest
from pathlib import Path
root=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck')
spec=importlib.util.spec_from_file_location('greekocr.labelfix.release_gate',root/'artifacts/labelfix_sf3/baseline/release_gate.py')
module=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=module
spec.loader.exec_module(module)
raise SystemExit(pytest.main(['tests/labelfix/test_sf3.py','-p','no:cacheprovider','-q','--tb=short']))
