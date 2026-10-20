"""Run every SR-B1/B1b/B2/B3 regression offline."""
import contextlib,io,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'validation'))
import test_b1,test_b2,test_b3
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(m) for m in (test_b1,test_b2,test_b3)])
buffer=io.StringIO()
with contextlib.redirect_stdout(buffer),contextlib.redirect_stderr(buffer):
 result=unittest.TextTestRunner(stream=buffer,verbosity=2).run(suite)
passed=result.testsRun-len(result.failures)-len(result.errors)
text=buffer.getvalue()+f'\nSR-B3 tests={passed}/{result.testsRun}\n'
(ROOT/'TEST_RESULTS_B3.txt').write_text(text);print(text);sys.exit(not result.wasSuccessful())
