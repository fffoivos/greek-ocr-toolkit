#!/usr/bin/env python3
"""Run SR-B1/B1b regressions plus labelled synthetic SR-B2 tests."""
import contextlib,io,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'validation'))
import test_b1,test_b2
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(module) for module in (test_b1,test_b2)])
buffer=io.StringIO()
with contextlib.redirect_stdout(buffer),contextlib.redirect_stderr(buffer):
 result=unittest.TextTestRunner(stream=buffer,verbosity=2).run(suite)
passed=result.testsRun-len(result.failures)-len(result.errors)
text=buffer.getvalue()+f'\nSR-B2 READY: tests={passed}/{result.testsRun}\n' if result.wasSuccessful() else buffer.getvalue()+f'\nSR-B2 BLOCKED: tests={passed}/{result.testsRun}\n'
(ROOT/'TEST_RESULTS_B2.txt').write_text(text);print(text);sys.exit(not result.wasSuccessful())
