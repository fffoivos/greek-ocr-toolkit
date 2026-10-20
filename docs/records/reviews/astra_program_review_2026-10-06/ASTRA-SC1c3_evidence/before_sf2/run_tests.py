import sys,pytest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
raise SystemExit(pytest.main([str(Path(__file__).parent/'tests/labelfix/test_sf2.py'),'-p','no:cacheprovider','-q','--tb=short']))
