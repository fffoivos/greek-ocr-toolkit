"""Run every Sol-reading regression and B4 final-artifact check offline."""
import contextlib,io,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'));sys.path.insert(0,str(ROOT/'validation'))
import test_b1,test_b2,test_b3,test_b4
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(m) for m in (test_b1,test_b2,test_b3,test_b4)])
buffer=io.StringIO()
with contextlib.redirect_stdout(buffer),contextlib.redirect_stderr(buffer):
 result=unittest.TextTestRunner(stream=buffer,verbosity=2).run(suite)
passed=result.testsRun-len(result.failures)-len(result.errors)
text=buffer.getvalue()+f'\nSR-B4 tests={passed}/{result.testsRun}\n'
(ROOT/'TEST_RESULTS_B4.txt').write_text(text);print(text);sys.exit(not result.wasSuccessful())
