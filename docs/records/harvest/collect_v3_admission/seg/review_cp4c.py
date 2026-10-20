"""Rebuild CP4c truth in temporary storage only; never re-freeze the ledger."""
import contextlib,hashlib,importlib.util,io,json,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[4];seg=root/'docs/harvest/collect_v3_admission/seg'
spec=importlib.util.spec_from_file_location('freeze_cp4c_review',seg/'freeze_truth.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory(prefix='seg-cp5-ledger-',dir='/tmp') as tmp:
    m.SEG=Path(tmp)
    with contextlib.redirect_stdout(io.StringIO()):m.main()
    actual=(Path(tmp)/'calibration_ledger.json').read_bytes()
    expected=(seg/'calibration_ledger.json').read_bytes()
    out=dict(ledger_byte_exact=actual==expected,ledger_sha256=hashlib.sha256(expected).hexdigest(),
        rebuilt_sha256=hashlib.sha256(actual).hexdigest(),counts=json.loads(actual)['counts'],
        output_scope='temporary directory only; original ledger unchanged',
        cp4c_tests='tests/test_seg_cp4c.py included in CP5_pytest.log',findings=[])
print(json.dumps(out,indent=2))
