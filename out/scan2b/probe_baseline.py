import importlib.util,subprocess,sys,types,unittest
from pathlib import Path
root=Path.cwd();tools=root/'docs/harvest/sol_reading/tools';sys.path.insert(0,str(tools))
spec=importlib.util.spec_from_file_location('scan2b_tests',root/'tests/test_scan_rollout.py')
tests=importlib.util.module_from_spec(spec);spec.loader.exec_module(tests)
old=types.ModuleType('baseline_scanner');old.__file__=str(tools/'scan_rollout.py')
source=subprocess.check_output(['git','show','HEAD:docs/harvest/sol_reading/tools/scan_rollout.py'],text=True)
exec(compile(source,old.__file__,'exec'),old.__dict__)
assert old.VERSION=='4.5';tests.s=old
suite=unittest.defaultTestLoader.loadTestsFromTestCase(tests.Scan2BProbes)
result=unittest.TextTestRunner(verbosity=2).run(suite)
assert result.testsRun==3 and len(result.failures)==5 and not result.errors
print('Confirmed: unchanged v4.5 incorrectly returns VALID for all five concrete probes across three fixture tests.')
